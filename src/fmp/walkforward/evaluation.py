from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Mapping

from fmp.backtest.costs import ZeroCommission, ZeroFinancing
from fmp.backtest.engine import BacktestConfig, run_backtest
from fmp.contracts import Direction
from fmp.data.phase2.schema import CANONICAL_SCHEMA_VERSION
from fmp.research.adapter import candidate_to_decision
from fmp.research.reporting import compute_research_metrics
from fmp.risk import RiskConfig
from fmp.strategies.contracts import SignalCandidate
from fmp.strategies.session_breakout import (
    SessionBreakoutConfig,
    generate_session_breakout_candidates,
)
from fmp.strategies.volatility_breakout import (
    VolatilityBreakoutConfig,
    generate_volatility_breakout_candidates,
)

from .contracts import (
    EXPERIMENT_ID,
    FROZEN_CANDIDATES,
    MAX_WARMUP_DAYS,
    REQUESTED_RISK_FRACTION,
    SLIPPAGE_SCENARIOS,
    STARTING_EQUITY_USD,
    USDJPY_PROCESSED_MANIFEST_SHA256,
    FrozenPhase7Candidate,
    Phase7Window,
    allowed_phase7_window,
)
from .data import LoadedPhase7Bars


REFIT_STATUS = "NOT_APPLICABLE_FIXED_RULE"


@dataclass(frozen=True, slots=True)
class WindowFinancialResult:
    candidate_id: str
    window_name: str
    slippage_pips: float
    candidate_count: int
    scored_candidate_count: int
    directional_candidate_count: int
    trade_count: int
    net_pnl_usd: float
    net_return: float
    expectancy_usd: float | None
    gross_profit_usd: float
    gross_loss_usd: float
    profit_factor: float | None
    max_drawdown_fraction: float
    metrics: Mapping[str, object]
    run_identity: Mapping[str, object]
    warmup_range: tuple[datetime, datetime]
    opened_partition_keys: tuple[str, ...]
    scored_start_utc: datetime
    scored_end_utc: datetime
    refit_status: str


def _utc_start(value: date) -> datetime:
    return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)


def _resolve_candidate(candidate_id: str) -> FrozenPhase7Candidate:
    try:
        return FROZEN_CANDIDATES[candidate_id]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"unsupported frozen Phase 7 candidate: {candidate_id!r}") from exc


def _validate_loaded_contract(
    *, loaded: LoadedPhase7Bars, candidate: FrozenPhase7Candidate, window: Phase7Window
) -> tuple[datetime, datetime]:
    scored_start = _utc_start(window.start)
    scored_end = _utc_start(window.end_exclusive)
    expected_warmup = (scored_start - timedelta(days=MAX_WARMUP_DAYS), scored_start)
    if loaded.warmup_range != expected_warmup:
        raise ValueError("Phase 7 loaded warm-up range does not match the frozen window")

    prefix = f"{candidate.timeframe}:"
    if not loaded.opened_partition_keys or any(
        not key.startswith(prefix) for key in loaded.opened_partition_keys
    ):
        raise ValueError("Phase 7 loaded partition identity does not match the frozen candidate/window")
    if not loaded.scored_bars:
        raise ValueError("Phase 7 evaluation requires scored quote bars")

    if any(bar.symbol != candidate.symbol for bar in loaded.bars):
        raise ValueError("Phase 7 loaded bars do not match the frozen candidate symbol")
    if any(
        bar.timestamp_utc < expected_warmup[0] or bar.timestamp_utc >= scored_end
        for bar in loaded.bars
    ):
        raise ValueError("Phase 7 loaded bars fall outside the approved warm-up/scored range")

    expected_scored = tuple(
        bar for bar in loaded.bars if scored_start <= bar.timestamp_utc < scored_end
    )
    if loaded.scored_bars != expected_scored:
        raise ValueError("Phase 7 scored bars do not match the approved window")
    expected_dates = tuple(sorted({bar.timestamp_utc.date() for bar in expected_scored}))
    if loaded.eligible_scored_dates != expected_dates:
        raise ValueError("Phase 7 scored-date accounting does not match scored bars")
    return scored_start, scored_end


def _generate_candidates(
    candidate: FrozenPhase7Candidate, loaded: LoadedPhase7Bars
) -> tuple[SignalCandidate, ...]:
    if candidate.candidate_id == "session_breakout":
        config = SessionBreakoutConfig(
            buffer_pips=int(candidate.parameters["buffer_pips"]),
            target_range_multiple=float(candidate.parameters["target_range_multiple"]),
            timeframe=candidate.timeframe,
        )
        return generate_session_breakout_candidates(loaded.bars, config=config)
    if candidate.candidate_id == "volatility_breakout":
        if float(candidate.parameters["target_r"]) != 1.0:
            raise ValueError("frozen Phase 7 volatility target must remain exactly 1.0R")
        config = VolatilityBreakoutConfig(
            range_multiplier=float(candidate.parameters["range_multiplier"]),
            timeframe=candidate.timeframe,
        )
        return generate_volatility_breakout_candidates(loaded.bars, config=config)
    raise ValueError(f"unsupported frozen Phase 7 candidate: {candidate.candidate_id!r}")


def _is_scored_candidate(
    candidate: SignalCandidate, *, scored_start: datetime, scored_end: datetime
) -> bool:
    if not (scored_start <= candidate.observation_bar_timestamp_utc < scored_end):
        return False
    if not (scored_start <= candidate.signal_known_timestamp_utc < scored_end):
        return False
    if candidate.latest_exit_timestamp_utc is not None and not (
        scored_start < candidate.latest_exit_timestamp_utc < scored_end
    ):
        return False
    return True


def _phase3_metrics(metrics: Mapping[str, object]) -> Mapping[str, object]:
    value = metrics.get("phase3_metrics")
    if not isinstance(value, Mapping):
        raise ValueError("Phase 7 evaluation is missing Phase 3 metrics")
    return value


def _float_metric(metrics: Mapping[str, object], key: str) -> float:
    value = metrics.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Phase 7 metric {key!r} must be numeric")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"Phase 7 metric {key!r} must be finite")
    return numeric


def _optional_float_metric(metrics: Mapping[str, object], key: str) -> float | None:
    value = metrics.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Phase 7 metric {key!r} must be numeric or null")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"Phase 7 metric {key!r} must be finite")
    return numeric


def evaluate_window(
    loaded: LoadedPhase7Bars,
    *,
    candidate_id: str,
    window_name: str,
    code_commit: str,
    slippage_pips: float,
) -> WindowFinancialResult:
    candidate = _resolve_candidate(candidate_id)
    window = allowed_phase7_window(window_name)
    if isinstance(slippage_pips, bool) or not isinstance(slippage_pips, (int, float)):
        raise ValueError("Phase 7 slippage must be one of the frozen scenarios")
    slippage = float(slippage_pips)
    if not math.isfinite(slippage) or slippage not in SLIPPAGE_SCENARIOS:
        raise ValueError("Phase 7 slippage must be one of the frozen scenarios")
    if not isinstance(code_commit, str) or not code_commit.strip():
        raise ValueError("code_commit must be non-empty")

    scored_start, scored_end = _validate_loaded_contract(
        loaded=loaded,
        candidate=candidate,
        window=window,
    )
    generated = _generate_candidates(candidate, loaded)
    for item in generated:
        if item.symbol != candidate.symbol:
            raise ValueError("Phase 7 strategy generated a candidate for the wrong symbol")
    scored_candidates = tuple(
        item
        for item in generated
        if _is_scored_candidate(item, scored_start=scored_start, scored_end=scored_end)
    )

    decisions = []
    scheduled_exits = []
    for item in scored_candidates:
        decision, scheduled_exit = candidate_to_decision(
            item,
            next_bar_timestamp_utc=item.signal_known_timestamp_utc,
            requested_risk_fraction=REQUESTED_RISK_FRACTION,
        )
        decisions.append(decision)
        if scheduled_exit is not None:
            scheduled_exits.append(scheduled_exit)

    config = BacktestConfig(
        starting_equity_usd=STARTING_EQUITY_USD,
        slippage_pips=slippage,
        risk_config=RiskConfig(),
        commission_model=ZeroCommission(),
        financing_model=ZeroFinancing(),
        processed_data_manifest_id=USDJPY_PROCESSED_MANIFEST_SHA256,
        schema_version=CANONICAL_SCHEMA_VERSION,
        timeframe=candidate.timeframe,
        requested_start_utc=scored_start,
        requested_end_utc=scored_end,
        code_commit=code_commit,
        decision_config={
            "experiment_id": EXPERIMENT_ID,
            "candidate_id": candidate.candidate_id,
            "window_name": window.name,
            "parameters": dict(candidate.parameters),
            "refit_status": REFIT_STATUS,
        },
    )
    run = run_backtest(
        bars=loaded.scored_bars,
        decisions=tuple(decisions),
        config=config,
        scheduled_exits=tuple(scheduled_exits),
    )
    candidate_metadata = {
        item.candidate_id: dict(item.metadata) for item in scored_candidates
    }
    metrics = compute_research_metrics(
        run,
        starting_equity_usd=STARTING_EQUITY_USD,
        requested_risk_fraction=REQUESTED_RISK_FRACTION,
        candidate_metadata=candidate_metadata,
        eligible_utc_dates=loaded.eligible_scored_dates,
    )
    financial = _phase3_metrics(metrics)
    trade_count = financial.get("trade_count")
    if isinstance(trade_count, bool) or not isinstance(trade_count, int) or trade_count < 0:
        raise ValueError("Phase 7 trade_count must be a non-negative integer")

    return WindowFinancialResult(
        candidate_id=candidate.candidate_id,
        window_name=window.name,
        slippage_pips=slippage,
        candidate_count=len(generated),
        scored_candidate_count=len(scored_candidates),
        directional_candidate_count=sum(
            item.direction in {Direction.LONG, Direction.SHORT}
            for item in scored_candidates
        ),
        trade_count=trade_count,
        net_pnl_usd=_float_metric(financial, "net_pnl_usd"),
        net_return=_float_metric(financial, "net_return"),
        expectancy_usd=_optional_float_metric(financial, "expectancy_usd"),
        gross_profit_usd=_float_metric(financial, "gross_profit_usd"),
        gross_loss_usd=_float_metric(financial, "gross_loss_usd"),
        profit_factor=_optional_float_metric(financial, "profit_factor"),
        max_drawdown_fraction=_float_metric(financial, "max_drawdown_fraction"),
        metrics=metrics,
        run_identity=dict(run.run_identity),
        warmup_range=loaded.warmup_range,
        opened_partition_keys=loaded.opened_partition_keys,
        scored_start_utc=scored_start,
        scored_end_utc=scored_end,
        refit_status=REFIT_STATUS,
    )


def evaluate_phase7_window(
    *,
    loaded: LoadedPhase7Bars,
    candidate_id: str,
    window_name: str,
    code_commit: str,
    slippage_pips: float,
) -> WindowFinancialResult:
    return evaluate_window(
        loaded,
        candidate_id=candidate_id,
        window_name=window_name,
        code_commit=code_commit,
        slippage_pips=slippage_pips,
    )
