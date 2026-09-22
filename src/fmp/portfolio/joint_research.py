from __future__ import annotations

import hashlib
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping, Sequence

from fmp.backtest.costs import ZeroCommission, ZeroFinancing
from fmp.backtest.engine import (
    DECLARED_EARLIEST_BAR,
    BacktestConfig,
    run_backtest,
)
from fmp.contracts import Direction, QuoteBar, TradeRecord
from fmp.data.phase2.schema import CANONICAL_SCHEMA_VERSION
from fmp.research.adapter import candidate_to_decision
from fmp.research.reporting import compute_research_metrics
from fmp.risk import RiskConfig
from fmp.strategies.contracts import SignalCandidate

from .contracts import PortfolioCandidate, StrategyVersion
from .research_data import (
    LoadedRetrospectiveBars,
    PHASE8A_RETROSPECTIVE_LABEL,
    RetrospectiveRange,
    load_phase8a_retrospective_bars,
)
from .research_runner import (
    REQUESTED_RISK_FRACTION,
    SLIPPAGE_SCENARIOS,
    STARTING_EQUITY_USD,
    generate_strategy_candidates,
    summarize_daily_returns,
)
from .router import partition_direction_conflicts, summarize_candidate_exposure

JOINT_PORTFOLIO_PROTOCOL = "fmp-phase8a-joint-portfolio-v1"
EXECUTION_TIMEFRAME = "1m"
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True, slots=True)
class Phase8AJointPortfolioPlan:
    experiment_id: str
    strategies: tuple[StrategyVersion, ...]
    research_range: RetrospectiveRange
    slippage_pips: float
    runner_code_commit: str
    evidence_label: str = PHASE8A_RETROSPECTIVE_LABEL
    untouched_oos: bool = False
    starting_equity_usd: float = STARTING_EQUITY_USD
    requested_risk_fraction: float = REQUESTED_RISK_FRACTION

    def __post_init__(self) -> None:
        if not isinstance(self.experiment_id, str) or not self.experiment_id.strip():
            raise ValueError("experiment_id must be non-empty")
        if not isinstance(self.research_range, RetrospectiveRange):
            raise TypeError("research_range must be RetrospectiveRange")
        if self.slippage_pips not in SLIPPAGE_SCENARIOS:
            raise ValueError("slippage_pips must be exactly 0.2, 0.5, or 1.0")
        if not _COMMIT_RE.fullmatch(self.runner_code_commit):
            raise ValueError("runner_code_commit must be a 40-character lowercase hexadecimal SHA")
        if self.evidence_label != PHASE8A_RETROSPECTIVE_LABEL:
            raise ValueError("joint portfolio evidence label is immutable")
        if self.untouched_oos is not False:
            raise ValueError("joint retrospective evidence cannot be marked untouched OOS")
        if self.starting_equity_usd != STARTING_EQUITY_USD:
            raise ValueError("joint portfolio starting equity is frozen at $100,000")
        if self.requested_risk_fraction != REQUESTED_RISK_FRACTION:
            raise ValueError("joint portfolio requested risk is frozen at 0.25%")
        if not self.strategies:
            raise ValueError("joint portfolio requires at least one strategy")
        if any(not isinstance(item, StrategyVersion) for item in self.strategies):
            raise TypeError("strategies must contain StrategyVersion")
        ordered = tuple(sorted(self.strategies, key=lambda item: item.fingerprint))
        fingerprints = tuple(item.fingerprint for item in ordered)
        if len(set(fingerprints)) != len(fingerprints):
            raise ValueError("joint portfolio contains duplicate strategy identities")
        object.__setattr__(self, "strategies", ordered)


def _validate_loaded(
    loaded: LoadedRetrospectiveBars,
    *,
    plan: Phase8AJointPortfolioPlan,
) -> None:
    if loaded.evidence_label != PHASE8A_RETROSPECTIVE_LABEL:
        raise ValueError("loaded bars are not explicitly retrospective")
    if (
        loaded.start != plan.research_range.start
        or loaded.end_exclusive != plan.research_range.end_exclusive
    ):
        raise ValueError("loaded retrospective range does not match joint plan")
    if not loaded.bars:
        raise ValueError("joint portfolio requires non-empty accepted bar data")


def _bind_candidate(
    strategy: StrategyVersion,
    candidate: SignalCandidate,
) -> SignalCandidate:
    if candidate.symbol != strategy.symbol:
        raise ValueError("strategy candidate symbol does not match strategy identity")
    metadata = dict(candidate.metadata)
    metadata.update(
        {
            "original_candidate_id": candidate.candidate_id,
            "strategy_fingerprint": strategy.fingerprint,
            "strategy_family": strategy.family,
            "strategy_version": strategy.version,
            "strategy_timeframe": strategy.timeframe,
        }
    )
    return SignalCandidate(
        candidate_id=f"{strategy.fingerprint[:16]}::{candidate.candidate_id}",
        symbol=candidate.symbol,
        observation_bar_timestamp_utc=candidate.observation_bar_timestamp_utc,
        signal_known_timestamp_utc=candidate.signal_known_timestamp_utc,
        direction=candidate.direction,
        stop_price=candidate.stop_price,
        target_price=candidate.target_price,
        latest_exit_timestamp_utc=candidate.latest_exit_timestamp_utc,
        reason_code=candidate.reason_code,
        metadata=metadata,
    )


def _candidate_sort_key(candidate: SignalCandidate) -> tuple[object, ...]:
    return (
        candidate.signal_known_timestamp_utc,
        candidate.symbol,
        candidate.candidate_id,
    )


def _candidate_sha256(candidates: Sequence[SignalCandidate]) -> str:
    digest = hashlib.sha256()
    for candidate in sorted(candidates, key=_candidate_sort_key):
        payload = candidate.stable_json_bytes()
        digest.update(len(payload).to_bytes(8, byteorder="big", signed=False))
        digest.update(payload)
    return digest.hexdigest()


def _combined_manifest_sha256(manifests: Mapping[str, str]) -> str:
    payload = json.dumps(
        dict(sorted(manifests.items())),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _utc_start(day) -> datetime:
    return datetime(day.year, day.month, day.day, tzinfo=timezone.utc)


def _merge_execution_bars(
    loaded_by_symbol: Mapping[str, LoadedRetrospectiveBars],
) -> tuple[QuoteBar, ...]:
    bars = tuple(
        sorted(
            (
                bar
                for symbol in sorted(loaded_by_symbol)
                for bar in loaded_by_symbol[symbol].bars
            ),
            key=lambda item: (item.timestamp_utc, item.symbol),
        )
    )
    keys = [(bar.timestamp_utc, bar.symbol) for bar in bars]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate joint execution bar identity")
    return bars


def _eligible_date_intersection(
    loaded_by_symbol: Mapping[str, LoadedRetrospectiveBars],
) -> tuple[object, ...]:
    date_sets = [set(item.eligible_utc_dates) for item in loaded_by_symbol.values()]
    if not date_sets:
        raise ValueError("joint portfolio has no execution datasets")
    intersection = set.intersection(*date_sets)
    if not intersection:
        raise ValueError("joint execution datasets have no common eligible UTC dates")
    return tuple(sorted(intersection))


def _trade_group_summary(trades: Sequence[TradeRecord]) -> dict[str, object]:
    pnls = [item.net_pnl_usd for item in trades]
    wins = [value for value in pnls if value > 0]
    losses = [value for value in pnls if value < 0]
    gross_profit = sum(wins)
    gross_loss = -sum(losses)
    return {
        "trade_count": len(trades),
        "net_pnl_usd": sum(pnls),
        "expectancy_usd": (sum(pnls) / len(pnls)) if pnls else None,
        "profit_factor": (gross_profit / gross_loss) if gross_loss > 0 else None,
        "gross_profit_usd": gross_profit,
        "gross_loss_usd": gross_loss,
    }


def _contribution_breakdown(
    trades: Sequence[TradeRecord],
    decision_metadata: Mapping[str, Mapping[str, object]],
    *,
    metadata_key: str,
) -> dict[str, dict[str, object]]:
    grouped: dict[str, list[TradeRecord]] = defaultdict(list)
    total_positive = sum(max(0.0, item.net_pnl_usd) for item in trades)
    for trade in trades:
        metadata = decision_metadata.get(trade.decision_id)
        if metadata is None:
            raise ValueError(f"missing decision metadata for trade {trade.decision_id!r}")
        key = str(metadata[metadata_key])
        grouped[key].append(trade)

    result: dict[str, dict[str, object]] = {}
    for key in sorted(grouped):
        summary = _trade_group_summary(grouped[key])
        positive = sum(max(0.0, item.net_pnl_usd) for item in grouped[key])
        summary["positive_pnl_share"] = (
            positive / total_positive if total_positive > 0 else None
        )
        result[key] = summary
    return result


def _pair_contribution(trades: Sequence[TradeRecord]) -> dict[str, dict[str, object]]:
    grouped: dict[str, list[TradeRecord]] = defaultdict(list)
    total_positive = sum(max(0.0, item.net_pnl_usd) for item in trades)
    for trade in trades:
        grouped[trade.symbol].append(trade)
    result: dict[str, dict[str, object]] = {}
    for symbol in sorted(grouped):
        summary = _trade_group_summary(grouped[symbol])
        positive = sum(max(0.0, item.net_pnl_usd) for item in grouped[symbol])
        summary["positive_pnl_share"] = (
            positive / total_positive if total_positive > 0 else None
        )
        result[symbol] = summary
    return result


def _exposure_buckets(
    candidates: Sequence[PortfolioCandidate],
) -> list[dict[str, object]]:
    grouped: dict[datetime, list[PortfolioCandidate]] = defaultdict(list)
    for candidate in candidates:
        grouped[candidate.observed_at_utc].append(candidate)

    rows: list[dict[str, object]] = []
    for timestamp in sorted(grouped):
        bucket = tuple(
            sorted(
                grouped[timestamp],
                key=lambda item: (item.symbol, item.strategy_fingerprint, item.candidate_id),
            )
        )
        exposure = summarize_candidate_exposure(bucket)
        rows.append(
            {
                "signal_known_timestamp_utc": timestamp.isoformat().replace("+00:00", "Z"),
                "candidate_count": len(bucket),
                "total_requested_risk_fraction": exposure.total_requested_risk_fraction,
                "usd_long_requested_risk_fraction": exposure.usd_long_requested_risk_fraction,
                "usd_short_requested_risk_fraction": exposure.usd_short_requested_risk_fraction,
                "gross_usd_directional_risk_fraction": (
                    exposure.gross_usd_directional_risk_fraction
                ),
                "net_usd_directional_risk_fraction": (
                    exposure.net_usd_directional_risk_fraction
                ),
            }
        )
    return rows


def run_phase8a_joint_portfolio(
    *,
    plan: Phase8AJointPortfolioPlan,
    dataset_sources: Mapping[str, tuple[Path, Path]],
    bars_loader: Callable[..., LoadedRetrospectiveBars] = load_phase8a_retrospective_bars,
    candidate_generator: Callable[
        [StrategyVersion, Sequence[QuoteBar]], Sequence[SignalCandidate]
    ] = generate_strategy_candidates,
) -> dict[str, object]:
    if not isinstance(plan, Phase8AJointPortfolioPlan):
        raise TypeError("plan must be Phase8AJointPortfolioPlan")

    required_symbols = tuple(sorted({item.symbol for item in plan.strategies}))
    for symbol in required_symbols:
        if symbol not in dataset_sources:
            raise ValueError(f"missing joint dataset source for {symbol}")

    execution_loaded: dict[str, LoadedRetrospectiveBars] = {}
    manifests: dict[str, str] = {}
    opened_months: dict[str, list[str]] = {}
    for symbol in required_symbols:
        dataset_root, manifest_path = dataset_sources[symbol]
        loaded = bars_loader(
            dataset_root=dataset_root,
            manifest_path=manifest_path,
            symbol=symbol,
            timeframe=EXECUTION_TIMEFRAME,
            research_range=plan.research_range,
        )
        _validate_loaded(loaded, plan=plan)
        execution_loaded[symbol] = loaded
        manifests[symbol] = loaded.processed_manifest_sha256
        opened_months[symbol] = list(loaded.opened_artifact_months)

    signal_cache: dict[tuple[str, str], LoadedRetrospectiveBars] = {}
    bound_candidates: list[SignalCandidate] = []
    for strategy in plan.strategies:
        key = (strategy.symbol, strategy.timeframe)
        loaded = signal_cache.get(key)
        if loaded is None:
            dataset_root, manifest_path = dataset_sources[strategy.symbol]
            loaded = bars_loader(
                dataset_root=dataset_root,
                manifest_path=manifest_path,
                symbol=strategy.symbol,
                timeframe=strategy.timeframe,
                research_range=plan.research_range,
            )
            _validate_loaded(loaded, plan=plan)
            if loaded.processed_manifest_sha256 != manifests[strategy.symbol]:
                raise ValueError("signal/execution processed-manifest identity mismatch")
            signal_cache[key] = loaded

        generated = candidate_generator(strategy, loaded.bars)
        for candidate in generated:
            if not isinstance(candidate, SignalCandidate):
                raise TypeError("candidate_generator must return SignalCandidate")
            bound_candidates.append(_bind_candidate(strategy, candidate))

    bound_candidates.sort(key=_candidate_sort_key)
    bound_ids = [item.candidate_id for item in bound_candidates]
    if len(bound_ids) != len(set(bound_ids)):
        raise ValueError("duplicate bound joint candidate identity")
    candidate_sha256 = _candidate_sha256(bound_candidates)

    directional = tuple(
        PortfolioCandidate(
            candidate_id=item.candidate_id,
            strategy_fingerprint=str(item.metadata["strategy_fingerprint"]),
            symbol=item.symbol,
            direction=item.direction,
            observed_at_utc=item.signal_known_timestamp_utc,
            requested_risk_fraction=plan.requested_risk_fraction,
            applicability_passed=True,
        )
        for item in bound_candidates
        if item.direction is not Direction.NO_TRADE
    )
    routed_directional, conflict_rejections = partition_direction_conflicts(directional)
    accepted_directional_ids = {item.candidate_id for item in routed_directional}

    decisions = []
    scheduled_exits = []
    decision_metadata: dict[str, Mapping[str, object]] = {}
    for candidate in bound_candidates:
        if (
            candidate.direction is not Direction.NO_TRADE
            and candidate.candidate_id not in accepted_directional_ids
        ):
            continue
        decision, scheduled_exit = candidate_to_decision(
            candidate,
            next_bar_timestamp_utc=candidate.signal_known_timestamp_utc,
            requested_risk_fraction=plan.requested_risk_fraction,
        )
        decisions.append(decision)
        decision_metadata[decision.decision_id] = dict(candidate.metadata)
        if scheduled_exit is not None:
            scheduled_exits.append(scheduled_exit)

    execution_bars = _merge_execution_bars(execution_loaded)
    eligible_dates = _eligible_date_intersection(execution_loaded)
    combined_manifest_sha256 = _combined_manifest_sha256(manifests)

    config = BacktestConfig(
        starting_equity_usd=plan.starting_equity_usd,
        slippage_pips=plan.slippage_pips,
        risk_config=RiskConfig(),
        commission_model=ZeroCommission(),
        financing_model=ZeroFinancing(),
        processed_data_manifest_id=combined_manifest_sha256,
        schema_version=CANONICAL_SCHEMA_VERSION,
        timeframe=EXECUTION_TIMEFRAME,
        requested_start_utc=_utc_start(plan.research_range.start),
        requested_end_utc=_utc_start(plan.research_range.end_exclusive),
        code_commit=plan.runner_code_commit,
        decision_config={
            "protocol": JOINT_PORTFOLIO_PROTOCOL,
            "experiment_id": plan.experiment_id,
            "evidence_label": plan.evidence_label,
            "untouched_oos": plan.untouched_oos,
            "strategy_fingerprints": [item.fingerprint for item in plan.strategies],
            "candidate_sha256": candidate_sha256,
            "signal_timeframes": sorted({item.timeframe for item in plan.strategies}),
            "execution_timeframe": EXECUTION_TIMEFRAME,
        },
        execution_timing_mode=DECLARED_EARLIEST_BAR,
    )
    run = run_backtest(
        bars=execution_bars,
        decisions=decisions,
        config=config,
        scheduled_exits=scheduled_exits,
    )

    metrics = dict(
        compute_research_metrics(
            run,
            starting_equity_usd=plan.starting_equity_usd,
            requested_risk_fraction=plan.requested_risk_fraction,
            candidate_metadata=decision_metadata,
            eligible_utc_dates=eligible_dates,
        )
    )
    metrics["daily_return_summary"] = summarize_daily_returns(metrics["daily_realized_returns"])

    conflict_rows = [
        {
            "candidate_id": item.candidate_id,
            "code": item.code.value,
            "explanation": item.explanation,
        }
        for item in conflict_rejections
    ]

    return {
        "protocol": JOINT_PORTFOLIO_PROTOCOL,
        "experiment_id": plan.experiment_id,
        "evidence_label": plan.evidence_label,
        "untouched_oos": plan.untouched_oos,
        "promotion_authorized": False,
        "shared_account": True,
        "execution_timeframe": EXECUTION_TIMEFRAME,
        "slippage_pips": plan.slippage_pips,
        "starting_equity_usd": plan.starting_equity_usd,
        "requested_risk_fraction": plan.requested_risk_fraction,
        "runner_code_commit": plan.runner_code_commit,
        "range_start": plan.research_range.start.isoformat(),
        "range_end_exclusive": plan.research_range.end_exclusive.isoformat(),
        "strategy_fingerprints": [item.fingerprint for item in plan.strategies],
        "processed_manifest_sha256_by_symbol": dict(sorted(manifests.items())),
        "combined_processed_manifest_sha256": combined_manifest_sha256,
        "opened_execution_artifact_months_by_symbol": dict(sorted(opened_months.items())),
        "signal_bar_count_by_cell": {
            f"{symbol}:{timeframe}": len(loaded.bars)
            for (symbol, timeframe), loaded in sorted(signal_cache.items())
        },
        "execution_bar_count": len(execution_bars),
        "candidate_count": len(bound_candidates),
        "candidate_sha256": candidate_sha256,
        "portfolio_conflict_rejection_count": len(conflict_rejections),
        "portfolio_conflict_rejections": conflict_rows,
        "requested_usd_exposure_by_signal_time": _exposure_buckets(routed_directional),
        "run_identity": dict(run.run_identity),
        "metrics": metrics,
        "pair_contribution": _pair_contribution(run.trades),
        "strategy_contribution": _contribution_breakdown(
            run.trades,
            decision_metadata,
            metadata_key="strategy_fingerprint",
        ),
        "signal_timeframe_contribution": _contribution_breakdown(
            run.trades,
            decision_metadata,
            metadata_key="strategy_timeframe",
        ),
    }
