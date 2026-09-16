from __future__ import annotations

import json
import math
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from .campaign import (
    MAXIMUM_DRAWDOWN_FRACTION,
    MAXIMUM_PROCESSING_LATENCY_P99_MS,
    MAXIMUM_QUOTE_DELAY_SECONDS,
    MAXIMUM_SPREAD_PARITY_DELTA_PIPS,
    MINIMUM_COMPLETED_SCORABLE_TRADES_0P2,
    MINIMUM_FULLY_OBSERVED_LONDON_DATES,
    MINIMUM_VALID_DATE_COVERAGE_FRACTION,
)


class Phase8ReviewOutcome(str, Enum):
    PASS = "PHASE8_PASS_ELIGIBLE_FOR_DEMO_DESIGN"
    NEED_MORE_DATA = "PHASE8_NEED_MORE_DATA"
    REJECT_OPERATIONAL = "PHASE8_REJECT_OPERATIONAL_MISMATCH"
    REJECT_MARKET = "PHASE8_REJECT_MARKET_MISMATCH"
    REJECT_FINANCIAL = "PHASE8_REJECT_FINANCIAL_MISMATCH"
    REJECT_SAFETY = "PHASE8_REJECT_SAFETY_FAILURE"


def _finite_nonnegative(value: float, *, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 0:
        raise ValueError(f"{field} must be finite and non-negative")
    return numeric


def _finite(value: float, *, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"{field} must be finite")
    return numeric


@dataclass(frozen=True, slots=True)
class SpreadSummary:
    median_pips: float
    p95_pips: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "median_pips",
            _finite_nonnegative(self.median_pips, field="median_pips"),
        )
        object.__setattr__(
            self,
            "p95_pips",
            _finite_nonnegative(self.p95_pips, field="p95_pips"),
        )
        if self.p95_pips < self.median_pips:
            raise ValueError("p95_pips must not be below median_pips")


@dataclass(frozen=True, slots=True)
class FinancialScenarioMetrics:
    trade_count: int
    net_return: float
    expectancy_usd: float
    profit_factor: float
    max_drawdown_fraction: float

    def __post_init__(self) -> None:
        if (
            isinstance(self.trade_count, bool)
            or not isinstance(self.trade_count, int)
            or self.trade_count < 0
        ):
            raise ValueError("trade_count must be a non-negative integer")
        object.__setattr__(self, "net_return", _finite(self.net_return, field="net_return"))
        object.__setattr__(
            self,
            "expectancy_usd",
            _finite(self.expectancy_usd, field="expectancy_usd"),
        )
        object.__setattr__(
            self,
            "profit_factor",
            _finite_nonnegative(self.profit_factor, field="profit_factor"),
        )
        object.__setattr__(
            self,
            "max_drawdown_fraction",
            _finite_nonnegative(
                self.max_drawdown_fraction, field="max_drawdown_fraction"
            ),
        )


@dataclass(frozen=True, slots=True)
class Phase8ReviewEvidence:
    structural_safety_ok: bool
    durable_artifacts_secret_free: bool
    qualification_pass: bool
    denominator_date_count: int
    valid_date_count: int
    fully_observed_london_dates: int
    malformed_silently_accepted_count: int
    stale_gap_financial_outcomes_count: int
    operational_events_complete: bool
    processing_latency_p99_ms: float
    max_entry_quote_delay_seconds: float
    max_time_exit_quote_delay_seconds: float
    historical_entry_spread: SpreadSummary
    historical_exit_spread: SpreadSummary
    live_entry_spread: SpreadSummary
    live_exit_spread: SpreadSummary
    scenario_metrics: Mapping[float, FinancialScenarioMetrics]
    campaign_minimums_met: bool
    replay_identical: bool

    def __post_init__(self) -> None:
        for name in (
            "structural_safety_ok",
            "durable_artifacts_secret_free",
            "qualification_pass",
            "operational_events_complete",
            "campaign_minimums_met",
            "replay_identical",
        ):
            if type(getattr(self, name)) is not bool:
                raise TypeError(f"{name} must be bool")
        for name in (
            "denominator_date_count",
            "valid_date_count",
            "fully_observed_london_dates",
            "malformed_silently_accepted_count",
            "stale_gap_financial_outcomes_count",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if self.valid_date_count > self.denominator_date_count:
            raise ValueError("valid_date_count cannot exceed denominator_date_count")
        for name in (
            "processing_latency_p99_ms",
            "max_entry_quote_delay_seconds",
            "max_time_exit_quote_delay_seconds",
        ):
            object.__setattr__(
                self,
                name,
                _finite_nonnegative(getattr(self, name), field=name),
            )
        if not isinstance(self.historical_entry_spread, SpreadSummary):
            raise TypeError("historical_entry_spread must be SpreadSummary")
        if not isinstance(self.historical_exit_spread, SpreadSummary):
            raise TypeError("historical_exit_spread must be SpreadSummary")
        if not isinstance(self.live_entry_spread, SpreadSummary):
            raise TypeError("live_entry_spread must be SpreadSummary")
        if not isinstance(self.live_exit_spread, SpreadSummary):
            raise TypeError("live_exit_spread must be SpreadSummary")
        metrics = dict(self.scenario_metrics)
        if set(metrics) != {0.2, 0.5, 1.0}:
            raise ValueError("scenario_metrics must contain exactly 0.2, 0.5, and 1.0")
        if any(not isinstance(value, FinancialScenarioMetrics) for value in metrics.values()):
            raise TypeError("scenario_metrics values must be FinancialScenarioMetrics")
        object.__setattr__(self, "scenario_metrics", MappingProxyType(metrics))


def evaluate_phase8_review(evidence: Phase8ReviewEvidence) -> Phase8ReviewOutcome:
    if not isinstance(evidence, Phase8ReviewEvidence):
        raise TypeError("evidence must be Phase8ReviewEvidence")

    if (
        not evidence.structural_safety_ok
        or not evidence.durable_artifacts_secret_free
        or not evidence.replay_identical
    ):
        return Phase8ReviewOutcome.REJECT_SAFETY

    if not evidence.qualification_pass:
        return Phase8ReviewOutcome.REJECT_OPERATIONAL
    if evidence.denominator_date_count > 0:
        coverage = evidence.valid_date_count / evidence.denominator_date_count
        if coverage < MINIMUM_VALID_DATE_COVERAGE_FRACTION:
            return Phase8ReviewOutcome.REJECT_OPERATIONAL
    elif evidence.campaign_minimums_met:
        return Phase8ReviewOutcome.REJECT_OPERATIONAL
    if (
        evidence.malformed_silently_accepted_count != 0
        or evidence.stale_gap_financial_outcomes_count != 0
        or not evidence.operational_events_complete
        or evidence.processing_latency_p99_ms > MAXIMUM_PROCESSING_LATENCY_P99_MS
        or evidence.max_entry_quote_delay_seconds > MAXIMUM_QUOTE_DELAY_SECONDS
        or evidence.max_time_exit_quote_delay_seconds > MAXIMUM_QUOTE_DELAY_SECONDS
    ):
        return Phase8ReviewOutcome.REJECT_OPERATIONAL

    baseline = evidence.scenario_metrics[0.2]
    if (
        not evidence.campaign_minimums_met
        or evidence.fully_observed_london_dates < MINIMUM_FULLY_OBSERVED_LONDON_DATES
        or baseline.trade_count < MINIMUM_COMPLETED_SCORABLE_TRADES_0P2
    ):
        return Phase8ReviewOutcome.NEED_MORE_DATA

    for live, historical in (
        (evidence.live_entry_spread, evidence.historical_entry_spread),
        (evidence.live_exit_spread, evidence.historical_exit_spread),
    ):
        if (
            live.median_pips
            > historical.median_pips + MAXIMUM_SPREAD_PARITY_DELTA_PIPS
            or live.p95_pips
            > historical.p95_pips + MAXIMUM_SPREAD_PARITY_DELTA_PIPS
        ):
            return Phase8ReviewOutcome.REJECT_MARKET

    for scenario in (0.2, 0.5):
        metrics = evidence.scenario_metrics[scenario]
        if (
            metrics.net_return <= 0.0
            or metrics.expectancy_usd <= 0.0
            or metrics.profit_factor <= 1.0
            or metrics.max_drawdown_fraction > MAXIMUM_DRAWDOWN_FRACTION
        ):
            return Phase8ReviewOutcome.REJECT_FINANCIAL

    return Phase8ReviewOutcome.PASS


def _require_mapping(value: object, *, field: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be an object")
    return value


def _spread_from_record(value: object, *, field: str) -> SpreadSummary:
    record = _require_mapping(value, field=field)
    return SpreadSummary(
        median_pips=record.get("median_pips"),  # type: ignore[arg-type]
        p95_pips=record.get("p95_pips"),  # type: ignore[arg-type]
    )


def _financial_from_record(value: object, *, field: str) -> FinancialScenarioMetrics:
    record = _require_mapping(value, field=field)
    return FinancialScenarioMetrics(
        trade_count=record.get("trade_count"),  # type: ignore[arg-type]
        net_return=record.get("net_return"),  # type: ignore[arg-type]
        expectancy_usd=record.get("expectancy_usd"),  # type: ignore[arg-type]
        profit_factor=record.get("profit_factor"),  # type: ignore[arg-type]
        max_drawdown_fraction=record.get("max_drawdown_fraction"),  # type: ignore[arg-type]
    )


def load_review_evidence(path: Path) -> Phase8ReviewEvidence:
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError("Phase 8 review evidence is missing") from exc
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("Phase 8 review evidence is not valid JSON") from exc
    record = _require_mapping(value, field="review evidence")
    scenarios = _require_mapping(record.get("scenario_metrics"), field="scenario_metrics")
    if set(scenarios) != {"0.2", "0.5", "1.0"}:
        raise ValueError("scenario_metrics must contain exactly 0.2, 0.5, and 1.0")
    return Phase8ReviewEvidence(
        structural_safety_ok=record.get("structural_safety_ok"),  # type: ignore[arg-type]
        durable_artifacts_secret_free=record.get("durable_artifacts_secret_free"),  # type: ignore[arg-type]
        qualification_pass=record.get("qualification_pass"),  # type: ignore[arg-type]
        denominator_date_count=record.get("denominator_date_count"),  # type: ignore[arg-type]
        valid_date_count=record.get("valid_date_count"),  # type: ignore[arg-type]
        fully_observed_london_dates=record.get("fully_observed_london_dates"),  # type: ignore[arg-type]
        malformed_silently_accepted_count=record.get("malformed_silently_accepted_count"),  # type: ignore[arg-type]
        stale_gap_financial_outcomes_count=record.get("stale_gap_financial_outcomes_count"),  # type: ignore[arg-type]
        operational_events_complete=record.get("operational_events_complete"),  # type: ignore[arg-type]
        processing_latency_p99_ms=record.get("processing_latency_p99_ms"),  # type: ignore[arg-type]
        max_entry_quote_delay_seconds=record.get("max_entry_quote_delay_seconds"),  # type: ignore[arg-type]
        max_time_exit_quote_delay_seconds=record.get("max_time_exit_quote_delay_seconds"),  # type: ignore[arg-type]
        historical_entry_spread=_spread_from_record(
            record.get("historical_entry_spread"), field="historical_entry_spread"
        ),
        historical_exit_spread=_spread_from_record(
            record.get("historical_exit_spread"), field="historical_exit_spread"
        ),
        live_entry_spread=_spread_from_record(
            record.get("live_entry_spread"), field="live_entry_spread"
        ),
        live_exit_spread=_spread_from_record(
            record.get("live_exit_spread"), field="live_exit_spread"
        ),
        scenario_metrics={
            0.2: _financial_from_record(scenarios["0.2"], field="scenario_metrics.0.2"),
            0.5: _financial_from_record(scenarios["0.5"], field="scenario_metrics.0.5"),
            1.0: _financial_from_record(scenarios["1.0"], field="scenario_metrics.1.0"),
        },
        campaign_minimums_met=record.get("campaign_minimums_met"),  # type: ignore[arg-type]
        replay_identical=record.get("replay_identical"),  # type: ignore[arg-type]
    )


def review_campaign(campaign_dir: Path) -> Phase8ReviewOutcome:
    from .review_compiler import compile_review_evidence

    campaign_dir = Path(campaign_dir)
    compile_review_evidence(campaign_dir)
    evidence = load_review_evidence(campaign_dir / "review-evidence.json")
    return evaluate_phase8_review(evidence)


__all__ = [
    "FinancialScenarioMetrics",
    "Phase8ReviewEvidence",
    "Phase8ReviewOutcome",
    "SpreadSummary",
    "evaluate_phase8_review",
    "load_review_evidence",
    "review_campaign",
]
