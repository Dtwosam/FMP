from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from statistics import median
from typing import Mapping, Sequence

import numpy as np
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

from fmp.backtest.costs import ZeroCommission, ZeroFinancing
from fmp.backtest.engine import BacktestConfig, run_backtest
from fmp.contracts import Direction, QuoteBar
from fmp.data.phase2.schema import CANONICAL_SCHEMA_VERSION
from fmp.research.adapter import candidate_to_decision
from fmp.research.reporting import compute_research_metrics
from fmp.risk import RiskConfig
from fmp.strategies.contracts import SignalCandidate

from .contracts import (
    EXPERIMENT_ID,
    FINAL_START,
    FROZEN_STRATEGIES,
    ModelFamily,
    Phase6Split,
    USDJPY_PROCESSED_MANIFEST_SHA256,
)


STARTING_EQUITY_USD = 100_000.0
REQUESTED_RISK_FRACTION = 0.0025


@dataclass(frozen=True, slots=True)
class FinancialResult:
    slippage_pips: float
    candidate_count: int
    directional_candidate_count: int
    metrics: Mapping[str, object]
    run_identity: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class GateResult:
    passed: bool
    criteria: Mapping[str, bool]


@dataclass(frozen=True, slots=True)
class SelectedVariant:
    model_family: str
    retained_fraction: float
    selection_row: Mapping[str, object]


def _validated_classification_inputs(
    labels: Sequence[int],
    scores: Sequence[float],
    candidate_ids: Sequence[str],
) -> tuple[np.ndarray, np.ndarray, tuple[str, ...]]:
    y = np.asarray(tuple(labels), dtype=np.int64)
    s = np.asarray(tuple(scores), dtype=np.float64)
    ids = tuple(candidate_ids)

    if y.ndim != 1 or s.ndim != 1 or len(y) != len(s) or len(y) != len(ids):
        raise ValueError("Phase 6 diagnostic labels, scores, and candidate_ids must align")
    if len(y) == 0:
        raise ValueError("Phase 6 diagnostics require non-empty inputs")
    if len(set(ids)) != len(ids):
        raise ValueError("Phase 6 diagnostic candidate_ids must be unique")
    if any(not isinstance(candidate_id, str) or not candidate_id for candidate_id in ids):
        raise ValueError("Phase 6 diagnostic candidate_ids must be non-empty strings")
    if not np.isfinite(s).all():
        raise ValueError("Phase 6 diagnostic scores must be finite")
    if np.any(s < 0.0) or np.any(s > 1.0):
        raise ValueError("Phase 6 diagnostic scores must be in [0, 1]")
    classes = set(np.unique(y).tolist())
    if classes != {0, 1}:
        raise ValueError("Phase 6 diagnostics require both label classes; one class is invalid")
    return y, s, ids


def _reliability_bins(
    labels: np.ndarray,
    scores: np.ndarray,
    candidate_ids: tuple[str, ...],
) -> tuple[dict[str, object], ...]:
    ordered = sorted(
        zip(scores.tolist(), candidate_ids, labels.tolist(), strict=True),
        key=lambda item: (item[0], item[1]),
    )
    bin_count = min(10, len(ordered))
    base, extra = divmod(len(ordered), bin_count)
    out: list[dict[str, object]] = []
    offset = 0
    for index in range(bin_count):
        size = base + (1 if index < extra else 0)
        chunk = ordered[offset : offset + size]
        offset += size
        chunk_scores = [float(item[0]) for item in chunk]
        chunk_labels = [int(item[2]) for item in chunk]
        out.append(
            {
                "row_count": size,
                "mean_model_score": float(sum(chunk_scores) / size),
                "observed_positive_rate": float(sum(chunk_labels) / size),
            }
        )
    return tuple(out)


def classification_diagnostics(
    labels: Sequence[int],
    scores: Sequence[float],
    candidate_ids: Sequence[str],
) -> dict[str, object]:
    y, s, ids = _validated_classification_inputs(labels, scores, candidate_ids)
    score_values = tuple(float(value) for value in s.tolist())
    result = {
        "roc_auc": float(roc_auc_score(y, s)),
        "average_precision": float(average_precision_score(y, s)),
        "brier_score": float(brier_score_loss(y, s)),
        "prevalence": float(np.mean(y)),
        "score_min": min(score_values),
        "score_max": max(score_values),
        "score_mean": float(sum(score_values) / len(score_values)),
        "score_median": float(median(score_values)),
        "reliability_bins": _reliability_bins(y, s, ids),
    }
    numeric_values = tuple(
        float(result[key])
        for key in (
            "roc_auc",
            "average_precision",
            "brier_score",
            "prevalence",
            "score_min",
            "score_max",
            "score_mean",
            "score_median",
        )
    )
    if any(not math.isfinite(value) for value in numeric_values):
        raise ValueError("Phase 6 classification diagnostics produced non-finite metrics")
    return result


def _utc_start(value) -> datetime:
    return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)


def run_candidate_backtest(
    *,
    bars: Sequence[QuoteBar],
    candidates: Sequence[SignalCandidate],
    strategy_id: str,
    split: Phase6Split,
    code_commit: str,
    slippage_pips: float,
) -> FinancialResult:
    try:
        strategy = FROZEN_STRATEGIES[strategy_id]
    except KeyError as exc:
        raise ValueError(f"unsupported frozen Phase 6 strategy: {strategy_id!r}") from exc
    if not code_commit.strip():
        raise ValueError("code_commit must be non-empty")
    if split.end_exclusive > FINAL_START:
        raise ValueError("Phase 6 final-test lock: backtest split may not reach beyond 2024-01-01")
    if not math.isfinite(slippage_pips) or slippage_pips < 0:
        raise ValueError("slippage_pips must be finite and non-negative")
    if not bars:
        raise ValueError("Phase 6 candidate backtest requires quote bars")
    boundary = _utc_start(FINAL_START)
    if any(bar.timestamp_utc >= boundary for bar in bars):
        raise ValueError("Phase 6 final-test lock: backtest bars may not reach 2024-01-01")

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

    config = BacktestConfig(
        starting_equity_usd=STARTING_EQUITY_USD,
        slippage_pips=slippage_pips,
        risk_config=RiskConfig(),
        commission_model=ZeroCommission(),
        financing_model=ZeroFinancing(),
        processed_data_manifest_id=USDJPY_PROCESSED_MANIFEST_SHA256,
        schema_version=CANONICAL_SCHEMA_VERSION,
        timeframe=strategy.timeframe,
        requested_start_utc=_utc_start(split.start),
        requested_end_utc=_utc_start(split.end_exclusive),
        code_commit=code_commit,
        decision_config={
            "experiment_id": EXPERIMENT_ID,
            "strategy_id": strategy_id,
            "split_name": split.name,
        },
    )
    run = run_backtest(
        bars=tuple(bars),
        decisions=tuple(decisions),
        config=config,
        scheduled_exits=tuple(scheduled_exits),
    )
    candidate_metadata = {
        candidate.candidate_id: dict(candidate.metadata) for candidate in candidates
    }
    eligible_dates = tuple(sorted({bar.timestamp_utc.date() for bar in bars}))
    metrics = compute_research_metrics(
        run,
        starting_equity_usd=STARTING_EQUITY_USD,
        requested_risk_fraction=REQUESTED_RISK_FRACTION,
        candidate_metadata=candidate_metadata,
        eligible_utc_dates=eligible_dates,
    )
    raw_identity = getattr(run, "run_identity", None)
    run_identity = (
        dict(raw_identity)
        if isinstance(raw_identity, Mapping)
        else {
            "experiment_id": EXPERIMENT_ID,
            "strategy_id": strategy_id,
            "split_name": split.name,
            "slippage_pips": slippage_pips,
            "code_commit": code_commit,
        }
    )
    return FinancialResult(
        slippage_pips=slippage_pips,
        candidate_count=len(candidates),
        directional_candidate_count=sum(
            candidate.direction in {Direction.LONG, Direction.SHORT}
            for candidate in candidates
        ),
        metrics=metrics,
        run_identity=run_identity,
    )


def _phase3_metrics(result: FinancialResult) -> Mapping[str, object]:
    value = result.metrics.get("phase3_metrics")
    if not isinstance(value, Mapping):
        raise ValueError("Phase 6 financial result is missing phase3_metrics")
    return value


def _numeric_metric(result: FinancialResult, key: str) -> float:
    value = _phase3_metrics(result).get(key)
    if value is None:
        raise ValueError(f"Phase 6 financial metric {key!r} is null")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Phase 6 financial metric {key!r} is not numeric")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"Phase 6 financial metric {key!r} is non-finite")
    return numeric


def _trade_count(result: FinancialResult) -> int:
    value = _phase3_metrics(result).get("trade_count")
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("Phase 6 trade_count must be a non-negative integer")
    return value


def _base_gate_criteria(
    filtered: FinancialResult,
    baseline: FinancialResult,
) -> dict[str, bool]:
    filtered_trades = _trade_count(filtered)
    baseline_trades = _trade_count(baseline)
    filtered_return = _numeric_metric(filtered, "net_return")
    baseline_return = _numeric_metric(baseline, "net_return")
    filtered_expectancy = _numeric_metric(filtered, "expectancy_usd")
    baseline_expectancy = _numeric_metric(baseline, "expectancy_usd")
    filtered_pf = _numeric_metric(filtered, "profit_factor")
    baseline_pf = _numeric_metric(baseline, "profit_factor")
    filtered_dd = _numeric_metric(filtered, "max_drawdown_fraction")
    baseline_dd = _numeric_metric(baseline, "max_drawdown_fraction")
    return {
        "trade_count_at_least_40pct_baseline": filtered_trades >= 0.40 * baseline_trades,
        "net_return_positive": filtered_return > 0.0,
        "expectancy_positive": filtered_expectancy > 0.0,
        "profit_factor_gt_one": filtered_pf > 1.0,
        "net_return_beats_baseline": filtered_return > baseline_return,
        "expectancy_beats_baseline": filtered_expectancy > baseline_expectancy,
        "profit_factor_beats_baseline": filtered_pf > baseline_pf,
        "max_drawdown_no_worse": filtered_dd <= baseline_dd,
    }


def selection_gate(filtered: FinancialResult, baseline: FinancialResult) -> GateResult:
    if filtered.slippage_pips != 0.2 or baseline.slippage_pips != 0.2:
        raise ValueError("Phase 6 selection gate requires the frozen 0.2-pip scenario")
    criteria = _base_gate_criteria(filtered, baseline)
    return GateResult(passed=all(criteria.values()), criteria=criteria)


def _yearly_net_pnl(result: FinancialResult, year: int) -> float:
    breakdown = result.metrics.get("calendar_year_breakdown")
    if not isinstance(breakdown, Mapping):
        raise ValueError("Phase 6 validation result is missing calendar_year_breakdown")
    row = breakdown.get(str(year))
    if not isinstance(row, Mapping):
        raise ValueError(f"Phase 6 validation result is missing calendar year {year}")
    value = row.get("net_pnl_usd")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Phase 6 calendar year {year} net_pnl_usd is invalid")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"Phase 6 calendar year {year} net_pnl_usd is non-finite")
    return numeric


def validation_gate(
    filtered_02: FinancialResult,
    baseline_02: FinancialResult,
    filtered_05: FinancialResult,
    baseline_05: FinancialResult,
) -> GateResult:
    if filtered_02.slippage_pips != 0.2 or baseline_02.slippage_pips != 0.2:
        raise ValueError("Phase 6 validation baseline gate requires 0.2-pip results")
    if filtered_05.slippage_pips != 0.5 or baseline_05.slippage_pips != 0.5:
        raise ValueError("Phase 6 robustness gate requires 0.5-pip results")

    criteria = _base_gate_criteria(filtered_02, baseline_02)
    yearly_improvements = sum(
        _yearly_net_pnl(filtered_02, year) > _yearly_net_pnl(baseline_02, year)
        for year in (2021, 2022, 2023)
    )
    criteria["yearly_net_pnl_improves_at_least_two_of_three"] = yearly_improvements >= 2

    robust_return = _numeric_metric(filtered_05, "net_return")
    robust_expectancy = _numeric_metric(filtered_05, "expectancy_usd")
    robust_pf = _numeric_metric(filtered_05, "profit_factor")
    robust_dd = _numeric_metric(filtered_05, "max_drawdown_fraction")
    robust_baseline_return = _numeric_metric(baseline_05, "net_return")
    robust_baseline_expectancy = _numeric_metric(baseline_05, "expectancy_usd")
    robust_baseline_pf = _numeric_metric(baseline_05, "profit_factor")
    robust_baseline_dd = _numeric_metric(baseline_05, "max_drawdown_fraction")
    robust = {
        "robust_05_net_return_positive": robust_return > 0.0,
        "robust_05_expectancy_positive": robust_expectancy > 0.0,
        "robust_05_profit_factor_gt_one": robust_pf > 1.0,
        "robust_05_net_return_beats_baseline": robust_return > robust_baseline_return,
        "robust_05_expectancy_beats_baseline": robust_expectancy > robust_baseline_expectancy,
        "robust_05_profit_factor_beats_baseline": robust_pf > robust_baseline_pf,
        "robust_05_max_drawdown_no_worse": robust_dd <= robust_baseline_dd,
    }
    criteria.update(robust)
    criteria["robust_05_all"] = all(robust.values())
    required = [
        value
        for key, value in criteria.items()
        if key != "robust_05_all"
    ]
    return GateResult(passed=all(required), criteria=criteria)


def select_one_variant(rows: Sequence[Mapping[str, object]]) -> SelectedVariant | None:
    qualifying: list[tuple[tuple[object, ...], Mapping[str, object]]] = []
    family_rank = {
        ModelFamily.LOGISTIC_REGRESSION.value: 0,
        ModelFamily.HIST_GRADIENT_BOOSTING.value: 1,
    }
    fraction_rank = {0.75: 0, 0.50: 1, 0.25: 2}

    for row in rows:
        gate = row.get("gate")
        if not isinstance(gate, GateResult):
            raise ValueError("Phase 6 selection row must contain GateResult")
        if not gate.passed:
            continue
        filtered = row.get("filtered")
        baseline = row.get("baseline")
        if not isinstance(filtered, FinancialResult) or not isinstance(baseline, FinancialResult):
            raise ValueError("Phase 6 selection row must contain financial results")
        family = row.get("model_family")
        retained_fraction = row.get("retained_fraction")
        if family not in family_rank:
            raise ValueError(f"unsupported Phase 6 selection model family: {family!r}")
        if retained_fraction not in fraction_rank:
            raise ValueError(f"unsupported Phase 6 retained fraction: {retained_fraction!r}")

        net_improvement = _numeric_metric(filtered, "net_return") - _numeric_metric(baseline, "net_return")
        expectancy_improvement = _numeric_metric(filtered, "expectancy_usd") - _numeric_metric(baseline, "expectancy_usd")
        pf_improvement = _numeric_metric(filtered, "profit_factor") - _numeric_metric(baseline, "profit_factor")
        drawdown = _numeric_metric(filtered, "max_drawdown_fraction")
        trades = _trade_count(filtered)
        key: tuple[object, ...] = (
            -net_improvement,
            -expectancy_improvement,
            -pf_improvement,
            drawdown,
            -trades,
            family_rank[str(family)],
            fraction_rank[float(retained_fraction)],
        )
        qualifying.append((key, row))

    if not qualifying:
        return None
    qualifying.sort(key=lambda item: item[0])
    selected_row = qualifying[0][1]
    return SelectedVariant(
        model_family=str(selected_row["model_family"]),
        retained_fraction=float(selected_row["retained_fraction"]),
        selection_row=dict(selected_row),
    )
