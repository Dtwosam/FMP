from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping, Sequence

from fmp.backtest.costs import ZeroCommission, ZeroFinancing
from fmp.backtest.engine import BacktestConfig, run_backtest
from fmp.data.phase2.schema import CANONICAL_SCHEMA_VERSION
from fmp.research.adapter import candidate_to_decision
from fmp.research.reporting import compute_research_metrics
from fmp.risk import RiskConfig
from fmp.strategies.contracts import SignalCandidate
from fmp.strategies.mean_reversion import (
    MeanReversionConfig,
    generate_mean_reversion_candidates,
)
from fmp.strategies.previous_day_rejection import (
    PreviousDayRejectionConfig,
    generate_previous_day_rejection_candidates,
)
from fmp.strategies.session_breakout import (
    SessionBreakoutConfig,
    generate_session_breakout_candidates,
)
from fmp.strategies.session_sweep_rejection import (
    SessionSweepRejectionConfig,
    generate_session_sweep_rejection_candidates,
)
from fmp.strategies.trend_continuation import (
    TrendContinuationConfig,
    generate_trend_continuation_candidates,
)
from fmp.strategies.volatility_breakout import (
    VolatilityBreakoutConfig,
    generate_volatility_breakout_candidates,
)

from .contracts import StrategyVersion
from .research_data import (
    LoadedRetrospectiveBars,
    PHASE8A_RETROSPECTIVE_LABEL,
    RetrospectiveRange,
    load_phase8a_retrospective_bars,
)

RESULT_PROTOCOL = "fmp-phase8a-retrospective-strategy-v1"
SLIPPAGE_SCENARIOS = (0.2, 0.5, 1.0)
STARTING_EQUITY_USD = 100_000.0
REQUESTED_RISK_FRACTION = 0.0025
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

_EXPECTED_PARAMETERS = {
    "session_breakout": frozenset({"buffer_pips", "target_range_multiple"}),
    "trend_continuation": frozenset({"trend_window_id", "target_r_multiple"}),
    "mean_reversion": frozenset({"lookback_hours", "threshold_sigma"}),
    "previous_day_rejection": frozenset({"buffer_pips"}),
    "volatility_breakout": frozenset({"range_multiplier"}),
    "session_sweep_rejection": frozenset({"buffer_pips"}),
}


@dataclass(frozen=True, slots=True)
class Phase8ARetrospectivePlan:
    experiment_id: str
    strategy: StrategyVersion
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
        if not isinstance(self.strategy, StrategyVersion):
            raise TypeError("strategy must be StrategyVersion")
        if not isinstance(self.research_range, RetrospectiveRange):
            raise TypeError("research_range must be RetrospectiveRange")
        if self.slippage_pips not in SLIPPAGE_SCENARIOS:
            raise ValueError("slippage_pips must be exactly 0.2, 0.5, or 1.0")
        if not _COMMIT_RE.fullmatch(self.runner_code_commit):
            raise ValueError("runner_code_commit must be a 40-character lowercase hexadecimal SHA")
        if self.evidence_label != PHASE8A_RETROSPECTIVE_LABEL:
            raise ValueError("Phase 8A evidence label is immutable")
        if self.untouched_oos is not False:
            raise ValueError("Phase 8A retrospective evidence cannot be marked untouched OOS")
        if self.starting_equity_usd != STARTING_EQUITY_USD:
            raise ValueError("Phase 8A retrospective starting equity is frozen at $100,000")
        if self.requested_risk_fraction != REQUESTED_RISK_FRACTION:
            raise ValueError("Phase 8A retrospective requested risk is frozen at 0.25%")


def _parameters(strategy: StrategyVersion) -> dict[str, object]:
    value = json.loads(strategy.parameters_json)
    if not isinstance(value, dict):
        raise ValueError("strategy parameters must decode to an object")
    expected = _EXPECTED_PARAMETERS.get(strategy.family)
    if expected is None:
        raise ValueError(f"unsupported Phase 8A strategy family: {strategy.family!r}")
    actual = frozenset(value)
    if actual != expected:
        raise ValueError(
            f"{strategy.family} parameters must be exactly {sorted(expected)}; "
            f"got {sorted(actual)}"
        )
    return value


def build_strategy_config(strategy: StrategyVersion) -> object:
    params = _parameters(strategy)
    try:
        if strategy.family == "session_breakout":
            return SessionBreakoutConfig(timeframe=strategy.timeframe, **params)
        if strategy.family == "trend_continuation":
            return TrendContinuationConfig(timeframe=strategy.timeframe, **params)
        if strategy.family == "mean_reversion":
            return MeanReversionConfig(timeframe=strategy.timeframe, **params)
        if strategy.family == "previous_day_rejection":
            return PreviousDayRejectionConfig(timeframe=strategy.timeframe, **params)
        if strategy.family == "volatility_breakout":
            return VolatilityBreakoutConfig(timeframe=strategy.timeframe, **params)
        if strategy.family == "session_sweep_rejection":
            return SessionSweepRejectionConfig(timeframe=strategy.timeframe, **params)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid frozen parameters for {strategy.family}: {exc}") from exc
    raise ValueError(f"unsupported Phase 8A strategy family: {strategy.family!r}")


def _generate_candidates(
    strategy: StrategyVersion,
    bars: Sequence[object],
) -> tuple[SignalCandidate, ...]:
    config = build_strategy_config(strategy)
    if strategy.family == "session_breakout":
        return tuple(generate_session_breakout_candidates(bars, config=config))
    if strategy.family == "trend_continuation":
        return tuple(generate_trend_continuation_candidates(bars, config=config))
    if strategy.family == "mean_reversion":
        return tuple(generate_mean_reversion_candidates(bars, config=config))
    if strategy.family == "previous_day_rejection":
        return tuple(generate_previous_day_rejection_candidates(bars, config=config))
    if strategy.family == "volatility_breakout":
        return tuple(generate_volatility_breakout_candidates(bars, config=config))
    if strategy.family == "session_sweep_rejection":
        return tuple(generate_session_sweep_rejection_candidates(bars, config=config))
    raise ValueError(f"unsupported Phase 8A strategy family: {strategy.family!r}")


def _candidate_sha256(candidates: Sequence[SignalCandidate]) -> str:
    digest = hashlib.sha256()
    for candidate in candidates:
        payload = candidate.stable_json_bytes()
        digest.update(len(payload).to_bytes(8, byteorder="big", signed=False))
        digest.update(payload)
    return digest.hexdigest()


def _adapt_candidates(
    candidates: Sequence[SignalCandidate],
) -> tuple[tuple[object, ...], tuple[object, ...]]:
    decisions = []
    scheduled_exits = []
    for candidate in candidates:
        decision, scheduled_exit = candidate_to_decision(
            candidate,
            next_bar_timestamp_utc=candidate.signal_known_timestamp_utc,
            requested_risk_fraction=REQUESTED_RISK_FRACTION,
        )
        decisions.append(decision)
        if scheduled_exit is not None:
            scheduled_exits.append(scheduled_exit)
    return tuple(decisions), tuple(scheduled_exits)


def summarize_daily_returns(
    daily_rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    returns: list[float] = []
    for row in daily_rows:
        raw = row.get("return")
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise ValueError("daily return row must contain numeric return")
        value = float(raw)
        if not math.isfinite(value):
            raise ValueError("daily returns must be finite")
        returns.append(value)

    count = len(returns)
    ge_10 = sum(1 for value in returns if value >= 0.10)
    positive = sum(1 for value in returns if value > 0.0)
    negative = sum(1 for value in returns if value < 0.0)
    zero = count - positive - negative
    return {
        "observed_days": count,
        "positive_days": positive,
        "negative_days": negative,
        "zero_days": zero,
        "days_ge_10pct": ge_10,
        "days_ge_10pct_fraction": (ge_10 / count) if count else None,
        "mean_daily_return": (sum(returns) / count) if count else None,
        "best_day_return": max(returns) if returns else None,
        "worst_day_return": min(returns) if returns else None,
    }


def _utc_start(day) -> datetime:
    return datetime(day.year, day.month, day.day, tzinfo=timezone.utc)


def run_phase8a_retrospective_strategy(
    *,
    plan: Phase8ARetrospectivePlan,
    dataset_root: Path | None,
    manifest_path: Path | None,
    bars_loader: Callable[..., LoadedRetrospectiveBars] = load_phase8a_retrospective_bars,
) -> dict[str, object]:
    if not isinstance(plan, Phase8ARetrospectivePlan):
        raise TypeError("plan must be Phase8ARetrospectivePlan")

    loaded = bars_loader(
        dataset_root=dataset_root,
        manifest_path=manifest_path,
        symbol=plan.strategy.symbol,
        timeframe=plan.strategy.timeframe,
        research_range=plan.research_range,
    )
    if loaded.evidence_label != PHASE8A_RETROSPECTIVE_LABEL:
        raise ValueError("loaded bars are not explicitly labeled retrospective")
    if loaded.start != plan.research_range.start or loaded.end_exclusive != plan.research_range.end_exclusive:
        raise ValueError("loaded retrospective range does not match frozen plan")
    if not loaded.bars:
        raise ValueError("Phase 8A retrospective run requires at least one complete quote bar")

    candidates = _generate_candidates(plan.strategy, loaded.bars)
    candidate_sha256 = _candidate_sha256(candidates)
    decisions, scheduled_exits = _adapt_candidates(candidates)
    candidate_metadata = {
        candidate.candidate_id: dict(candidate.metadata)
        for candidate in candidates
    }

    backtest_config = BacktestConfig(
        starting_equity_usd=plan.starting_equity_usd,
        slippage_pips=plan.slippage_pips,
        risk_config=RiskConfig(),
        commission_model=ZeroCommission(),
        financing_model=ZeroFinancing(),
        processed_data_manifest_id=loaded.processed_manifest_sha256,
        schema_version=CANONICAL_SCHEMA_VERSION,
        timeframe=plan.strategy.timeframe,
        requested_start_utc=_utc_start(plan.research_range.start),
        requested_end_utc=_utc_start(plan.research_range.end_exclusive),
        code_commit=plan.runner_code_commit,
        decision_config={
            "experiment_id": plan.experiment_id,
            "evidence_label": plan.evidence_label,
            "untouched_oos": plan.untouched_oos,
            "strategy_fingerprint": plan.strategy.fingerprint,
            "strategy_family": plan.strategy.family,
            "strategy_version": plan.strategy.version,
            "strategy_code_commit": plan.strategy.code_commit,
            "parameters_json": plan.strategy.parameters_json,
            "candidate_sha256": candidate_sha256,
        },
    )
    run = run_backtest(
        bars=loaded.bars,
        decisions=decisions,
        config=backtest_config,
        scheduled_exits=scheduled_exits,
    )
    metrics = compute_research_metrics(
        run,
        starting_equity_usd=plan.starting_equity_usd,
        requested_risk_fraction=plan.requested_risk_fraction,
        candidate_metadata=candidate_metadata,
        eligible_utc_dates=loaded.eligible_utc_dates,
    )
    metrics = dict(metrics)
    metrics["daily_return_summary"] = summarize_daily_returns(metrics["daily_realized_returns"])

    return {
        "protocol": RESULT_PROTOCOL,
        "experiment_id": plan.experiment_id,
        "evidence_label": plan.evidence_label,
        "untouched_oos": plan.untouched_oos,
        "strategy_fingerprint": plan.strategy.fingerprint,
        "strategy_identity_json": plan.strategy.identity_json,
        "runner_code_commit": plan.runner_code_commit,
        "processed_manifest_sha256": loaded.processed_manifest_sha256,
        "schema_version": CANONICAL_SCHEMA_VERSION,
        "range_start": plan.research_range.start.isoformat(),
        "range_end_exclusive": plan.research_range.end_exclusive.isoformat(),
        "opened_artifact_months": list(loaded.opened_artifact_months),
        "excluded_incomplete_bar_count": loaded.excluded_incomplete_count,
        "candidate_count": len(candidates),
        "candidate_sha256": candidate_sha256,
        "candidate_reason_counts": dict(
            sorted(Counter(candidate.reason_code for candidate in candidates).items())
        ),
        "slippage_pips": plan.slippage_pips,
        "starting_equity_usd": plan.starting_equity_usd,
        "requested_risk_fraction": plan.requested_risk_fraction,
        "run_identity": dict(run.run_identity),
        "metrics": metrics,
    }
