from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Mapping, Sequence

import numpy as np
import polars as pl
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

from fmp.backtest.costs import ZeroCommission, ZeroFinancing
from fmp.backtest.engine import BacktestConfig, run_backtest
from fmp.contracts import Direction, QuoteBar
from fmp.data.phase2.schema import CANONICAL_SCHEMA_VERSION
from fmp.research.adapter import candidate_to_decision
from fmp.research.contracts import ResearchSplit
from fmp.research.data import load_processed_bars_for_split
from fmp.research.reporting import compute_research_metrics
from fmp.risk import RiskConfig
from fmp.strategies.contracts import SignalCandidate

from .contracts import (
    EXPERIMENT_ID,
    FINAL_START,
    FIT_SPLIT,
    FROZEN_STRATEGIES,
    PHASE5_CHECKPOINT_SHA,
    SELECTION_SPLIT,
    VALIDATION_SPLIT,
    ModelFamily,
    Phase6Split,
    USDJPY_PROCESSED_MANIFEST_SHA256,
)
from .data import (
    MODEL_INPUT_COLUMNS,
    generate_frozen_candidates,
    join_directional_candidates_to_features,
    load_phase6_feature_frame,
)
from .estimators import FittedEstimator, fit_estimator, score_digest, score_estimator
from .filtering import filter_candidates
from .labels import LabelResult, label_candidates
from .preprocessing import PreprocessorState, fit_preprocessor, transform_features
from .thresholds import ScoreCutoff, derive_fit_cutoffs


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


def _research_split(split: Phase6Split) -> ResearchSplit:
    return ResearchSplit(split.name, split.start, split.end_exclusive)


def _jsonable(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, datetime):
        if value.tzinfo is None:
            raise ValueError("Phase 6 evidence timestamp must be timezone-aware")
        utc = value.astimezone(timezone.utc)
        return utc.isoformat().replace("+00:00", "Z")
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, (np.integer, np.floating, np.bool_)):
        return _jsonable(value.item())
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Phase 6 evidence cannot contain non-finite floats")
        return value
    raise TypeError(f"unsupported Phase 6 evidence value: {type(value).__name__}")


def _canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            _jsonable(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _atomic_write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_bytes(
        json.dumps(
            _jsonable(value),
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        + b"\n"
    )
    temp.replace(path)


def _serialize_preprocessor(state: PreprocessorState) -> dict[str, object]:
    return {
        "input_columns": list(state.input_columns),
        "medians": list(state.medians),
        "null_counts": list(state.null_counts),
        "standardize": state.standardize,
        "scaler_mean": None if state.scaler_mean is None else list(state.scaler_mean),
        "scaler_scale": None if state.scaler_scale is None else list(state.scaler_scale),
    }


def _serialize_cutoff(cutoff: ScoreCutoff) -> dict[str, object]:
    return {
        "retained_fraction": cutoff.retained_fraction,
        "fit_index": cutoff.fit_index,
        "score": cutoff.score,
        "fit_row_count": cutoff.fit_row_count,
        "fit_retained_count": cutoff.fit_retained_count,
        "fit_retained_rate": cutoff.fit_retained_rate,
    }


def _serialize_financial(result: FinancialResult) -> dict[str, object]:
    return {
        "slippage_pips": result.slippage_pips,
        "candidate_count": result.candidate_count,
        "directional_candidate_count": result.directional_candidate_count,
        "metrics": _jsonable(result.metrics),
        "run_identity": _jsonable(result.run_identity),
    }


def _serialize_gate(gate: GateResult) -> dict[str, object]:
    return {"passed": gate.passed, "criteria": dict(gate.criteria)}


def _model_config(fitted: FittedEstimator) -> dict[str, object]:
    params = fitted.estimator.get_params(deep=False)
    if fitted.family is ModelFamily.LOGISTIC_REGRESSION:
        keys = (
            "penalty",
            "C",
            "solver",
            "tol",
            "fit_intercept",
            "class_weight",
            "max_iter",
            "warm_start",
        )
    else:
        keys = (
            "loss",
            "learning_rate",
            "max_iter",
            "max_leaf_nodes",
            "max_depth",
            "min_samples_leaf",
            "l2_regularization",
            "max_features",
            "max_bins",
            "early_stopping",
            "warm_start",
            "class_weight",
            "random_state",
        )
    return {key: _jsonable(params[key]) for key in keys}


def _dataset_digest(
    frame: pl.DataFrame,
    labels_by_id: Mapping[str, LabelResult],
) -> str:
    rows: list[dict[str, object]] = []
    for row in frame.to_dicts():
        candidate_id = str(row["candidate_id"])
        label = labels_by_id[candidate_id]
        if label.label is None:
            continue
        rows.append(
            {
                "candidate_id": candidate_id,
                "inputs": {name: row[name] for name in MODEL_INPUT_COLUMNS},
                "label": label.label,
                "label_reason": label.reason_code,
                "resolved_timestamp_utc": label.resolved_timestamp_utc,
            }
        )
    return hashlib.sha256(_canonical_json_bytes(rows)).hexdigest()


def _load_split_dataset(
    *,
    dataset_root: Path,
    processed_manifest_path: Path,
    feature_root: Path,
    feature_manifest_path: Path,
    strategy_id: str,
    split: Phase6Split,
) -> dict[str, object]:
    strategy = FROZEN_STRATEGIES[strategy_id]
    research_split = _research_split(split)
    loaded_bars = load_processed_bars_for_split(
        dataset_root=Path(dataset_root),
        manifest_path=Path(processed_manifest_path),
        symbol=strategy.symbol,
        timeframe=strategy.timeframe,
        split=research_split,
    )
    loaded_features = load_phase6_feature_frame(
        feature_root=Path(feature_root),
        feature_manifest_path=Path(feature_manifest_path),
        strategy=strategy,
        split=research_split,
    )
    candidates = generate_frozen_candidates(strategy_id, loaded_bars.bars)
    labels = label_candidates(candidates, loaded_bars.bars)
    label_by_id = {item.candidate_id: item for item in labels}
    if len(label_by_id) != len(labels):
        raise ValueError("duplicate Phase 6 label candidate identity")
    if set(label_by_id) != {candidate.candidate_id for candidate in candidates}:
        raise ValueError("Phase 6 labels do not cover the exact candidate set")
    model_frame = join_directional_candidates_to_features(candidates, loaded_features)
    if model_frame.is_empty():
        raise ValueError(f"Phase 6 split {split.name!r} has no directional model rows")
    model_ids = tuple(str(value) for value in model_frame["candidate_id"].to_list())
    directional_ids = tuple(
        candidate.candidate_id
        for candidate in candidates
        if candidate.direction in {Direction.LONG, Direction.SHORT}
    )
    if set(model_ids) != set(directional_ids):
        raise ValueError("Phase 6 model rows do not match directional candidates exactly")
    return {
        "split": split,
        "bars": tuple(loaded_bars.bars),
        "candidates": tuple(candidates),
        "labels": tuple(labels),
        "label_by_id": label_by_id,
        "model_frame": model_frame,
        "feature_manifest_sha256": loaded_features.feature_manifest_sha256,
        "processed_manifest_sha256": loaded_features.processed_manifest_sha256,
        "phase5_checkpoint_sha": loaded_features.phase5_checkpoint_sha,
        "phase5_code_commit": loaded_features.phase5_code_commit,
        "opened_artifacts": tuple(loaded_features.opened_artifacts),
    }


def _labeled_model_rows(dataset: Mapping[str, object]) -> tuple[pl.DataFrame, tuple[str, ...], np.ndarray]:
    frame = dataset["model_frame"]
    label_by_id = dataset["label_by_id"]
    if not isinstance(frame, pl.DataFrame) or not isinstance(label_by_id, Mapping):
        raise TypeError("invalid Phase 6 split dataset")
    ids = tuple(
        str(value)
        for value in frame["candidate_id"].to_list()
        if isinstance(label_by_id[str(value)], LabelResult)
        and label_by_id[str(value)].label is not None
    )
    if not ids:
        raise ValueError("Phase 6 fit/evaluation rows contain no label-eligible candidates")
    id_set = set(ids)
    selected = frame.filter(pl.col("candidate_id").is_in(id_set))
    selected_ids = tuple(str(value) for value in selected["candidate_id"].to_list())
    labels = np.asarray(
        [int(label_by_id[candidate_id].label) for candidate_id in selected_ids],
        dtype=np.int64,
    )
    return selected.select(list(MODEL_INPUT_COLUMNS)), selected_ids, labels


def _all_model_rows(dataset: Mapping[str, object]) -> tuple[pl.DataFrame, tuple[str, ...]]:
    frame = dataset["model_frame"]
    if not isinstance(frame, pl.DataFrame):
        raise TypeError("invalid Phase 6 model frame")
    ids = tuple(str(value) for value in frame["candidate_id"].to_list())
    return frame.select(list(MODEL_INPUT_COLUMNS)), ids


def _diagnostics_for_labeled(
    *,
    dataset: Mapping[str, object],
    all_ids: tuple[str, ...],
    all_scores: Sequence[float],
) -> dict[str, object]:
    label_by_id = dataset["label_by_id"]
    if not isinstance(label_by_id, Mapping):
        raise TypeError("invalid Phase 6 label mapping")
    score_by_id = {
        candidate_id: float(score)
        for candidate_id, score in zip(all_ids, all_scores, strict=True)
    }
    labeled_ids = tuple(
        candidate_id
        for candidate_id in all_ids
        if isinstance(label_by_id[candidate_id], LabelResult)
        and label_by_id[candidate_id].label is not None
    )
    labels = tuple(int(label_by_id[candidate_id].label) for candidate_id in labeled_ids)
    scores = tuple(score_by_id[candidate_id] for candidate_id in labeled_ids)
    return classification_diagnostics(labels, scores, labeled_ids)


def _find_cutoff(
    cutoffs: Sequence[ScoreCutoff], retained_fraction: float
) -> ScoreCutoff:
    for cutoff in cutoffs:
        if cutoff.retained_fraction == retained_fraction:
            return cutoff
    raise ValueError("selected Phase 6 retained fraction has no frozen fit cutoff")


def run_phase6_strategy_cell(
    *,
    dataset_root: Path,
    processed_manifest_path: Path,
    feature_root: Path,
    feature_manifest_path: Path,
    strategy_id: str,
    out_dir: Path,
    code_commit: str,
) -> dict[str, object]:
    if strategy_id not in FROZEN_STRATEGIES:
        raise ValueError(f"unsupported frozen Phase 6 strategy: {strategy_id!r}")
    if not code_commit.strip():
        raise ValueError("code_commit must be non-empty")
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)

    fit = _load_split_dataset(
        dataset_root=Path(dataset_root),
        processed_manifest_path=Path(processed_manifest_path),
        feature_root=Path(feature_root),
        feature_manifest_path=Path(feature_manifest_path),
        strategy_id=strategy_id,
        split=FIT_SPLIT,
    )
    selection = _load_split_dataset(
        dataset_root=Path(dataset_root),
        processed_manifest_path=Path(processed_manifest_path),
        feature_root=Path(feature_root),
        feature_manifest_path=Path(feature_manifest_path),
        strategy_id=strategy_id,
        split=SELECTION_SPLIT,
    )

    fit_features, fit_ids, fit_labels = _labeled_model_rows(fit)
    selection_features, selection_ids = _all_model_rows(selection)
    fit_label_by_id = fit["label_by_id"]
    if not isinstance(fit_label_by_id, Mapping):
        raise TypeError("invalid Phase 6 fit label mapping")

    preprocessors: dict[ModelFamily, PreprocessorState] = {}
    fitted_estimators: dict[ModelFamily, FittedEstimator] = {}
    cutoffs_by_family: dict[ModelFamily, tuple[ScoreCutoff, ScoreCutoff, ScoreCutoff]] = {}
    selection_scores_by_family: dict[ModelFamily, dict[str, float]] = {}
    model_evidence: dict[str, object] = {}

    for family in ModelFamily:
        state = fit_preprocessor(
            fit_features,
            standardize=family is ModelFamily.LOGISTIC_REGRESSION,
        )
        X_fit = transform_features(fit_features, state)
        fitted = fit_estimator(family, X_fit, fit_labels)
        fit_scores = score_estimator(fitted, X_fit)
        cutoffs = derive_fit_cutoffs(fit_scores)

        X_selection = transform_features(selection_features, state)
        selection_scores = score_estimator(fitted, X_selection)
        selection_score_map = {
            candidate_id: float(score)
            for candidate_id, score in zip(selection_ids, selection_scores, strict=True)
        }

        preprocessors[family] = state
        fitted_estimators[family] = fitted
        cutoffs_by_family[family] = cutoffs
        selection_scores_by_family[family] = selection_score_map
        model_evidence[family.value] = {
            "preprocessing": _serialize_preprocessor(state),
            "model_config": _model_config(fitted),
            "fit_score_digest": score_digest(fit_ids, fit_scores),
            "selection_score_digest": score_digest(selection_ids, selection_scores),
            "cutoffs": [_serialize_cutoff(cutoff) for cutoff in cutoffs],
            "fit_diagnostics": classification_diagnostics(
                tuple(int(value) for value in fit_labels.tolist()),
                tuple(float(value) for value in fit_scores.tolist()),
                fit_ids,
            ),
            "selection_diagnostics": _diagnostics_for_labeled(
                dataset=selection,
                all_ids=selection_ids,
                all_scores=selection_scores,
            ),
        }

    selection_candidates = selection["candidates"]
    selection_bars = selection["bars"]
    if not isinstance(selection_candidates, tuple) or not isinstance(selection_bars, tuple):
        raise TypeError("invalid Phase 6 selection dataset")
    selection_baseline = run_candidate_backtest(
        bars=selection_bars,
        candidates=selection_candidates,
        strategy_id=strategy_id,
        split=SELECTION_SPLIT,
        code_commit=code_commit,
        slippage_pips=0.2,
    )

    internal_rows: list[dict[str, object]] = []
    evidence_rows: list[dict[str, object]] = []
    for family in ModelFamily:
        for cutoff in cutoffs_by_family[family]:
            filtered_candidates = filter_candidates(
                selection_candidates,
                selection_scores_by_family[family],
                cutoff,
                family.value,
            )
            filtered = run_candidate_backtest(
                bars=selection_bars,
                candidates=filtered_candidates,
                strategy_id=strategy_id,
                split=SELECTION_SPLIT,
                code_commit=code_commit,
                slippage_pips=0.2,
            )
            gate = selection_gate(filtered, selection_baseline)
            internal = {
                "model_family": family.value,
                "retained_fraction": cutoff.retained_fraction,
                "cutoff": cutoff,
                "filtered": filtered,
                "baseline": selection_baseline,
                "gate": gate,
            }
            internal_rows.append(internal)
            evidence_rows.append(
                {
                    "model_family": family.value,
                    "retained_fraction": cutoff.retained_fraction,
                    "cutoff": _serialize_cutoff(cutoff),
                    "filtered": _serialize_financial(filtered),
                    "baseline": _serialize_financial(selection_baseline),
                    "gate": _serialize_gate(gate),
                }
            )

    selected = select_one_variant(internal_rows)
    selected_payload: object = "NO_ML_CHALLENGER"
    if selected is not None:
        family = ModelFamily(selected.model_family)
        cutoff = _find_cutoff(cutoffs_by_family[family], selected.retained_fraction)
        selected_payload = {
            "model_family": family.value,
            "retained_fraction": cutoff.retained_fraction,
            "cutoff": _serialize_cutoff(cutoff),
        }

    selection_artifact: dict[str, object] = {
        "experiment_id": EXPERIMENT_ID,
        "strategy_id": strategy_id,
        "code_commit": code_commit,
        "phase5_checkpoint_sha": PHASE5_CHECKPOINT_SHA,
        "processed_manifest_sha256": USDJPY_PROCESSED_MANIFEST_SHA256,
        "fit_split": {
            "start": FIT_SPLIT.start.isoformat(),
            "end_exclusive": FIT_SPLIT.end_exclusive.isoformat(),
        },
        "selection_split": {
            "start": SELECTION_SPLIT.start.isoformat(),
            "end_exclusive": SELECTION_SPLIT.end_exclusive.isoformat(),
        },
        "fit_dataset_digest": _dataset_digest(fit["model_frame"], fit_label_by_id),
        "fit_feature_manifest_sha256": fit["feature_manifest_sha256"],
        "selection_feature_manifest_sha256": selection["feature_manifest_sha256"],
        "models": model_evidence,
        "baseline_02": _serialize_financial(selection_baseline),
        "variants": evidence_rows,
        "tie_break_order": [
            "net_return_improvement",
            "expectancy_improvement",
            "profit_factor_improvement",
            "lower_max_drawdown",
            "higher_trade_count",
            "logistic_before_histogram",
            "retained_0.75_before_0.50_before_0.25",
        ],
        "selected_variant": selected_payload,
    }
    _atomic_write_json(output / "selection.json", selection_artifact)

    if selected is None:
        validation_artifact: dict[str, object] = {
            "status": "NO_ML_CHALLENGER",
            "validation_loaded": False,
        }
        return {
            "experiment_id": EXPERIMENT_ID,
            "strategy_id": strategy_id,
            "code_commit": code_commit,
            "selection": selection_artifact,
            "validation": validation_artifact,
        }

    selected_family = ModelFamily(selected.model_family)
    selected_cutoff = _find_cutoff(
        cutoffs_by_family[selected_family], selected.retained_fraction
    )
    validation = _load_split_dataset(
        dataset_root=Path(dataset_root),
        processed_manifest_path=Path(processed_manifest_path),
        feature_root=Path(feature_root),
        feature_manifest_path=Path(feature_manifest_path),
        strategy_id=strategy_id,
        split=VALIDATION_SPLIT,
    )
    validation_features, validation_ids = _all_model_rows(validation)
    X_validation = transform_features(
        validation_features, preprocessors[selected_family]
    )
    validation_scores = score_estimator(
        fitted_estimators[selected_family], X_validation
    )
    validation_score_map = {
        candidate_id: float(score)
        for candidate_id, score in zip(validation_ids, validation_scores, strict=True)
    }
    validation_candidates = validation["candidates"]
    validation_bars = validation["bars"]
    if not isinstance(validation_candidates, tuple) or not isinstance(validation_bars, tuple):
        raise TypeError("invalid Phase 6 validation dataset")
    filtered_validation = filter_candidates(
        validation_candidates,
        validation_score_map,
        selected_cutoff,
        selected_family.value,
    )

    baselines: dict[str, FinancialResult] = {}
    filtered_results: dict[str, FinancialResult] = {}
    for slippage in (0.2, 0.5, 1.0):
        key = f"{slippage:.1f}"
        baselines[key] = run_candidate_backtest(
            bars=validation_bars,
            candidates=validation_candidates,
            strategy_id=strategy_id,
            split=VALIDATION_SPLIT,
            code_commit=code_commit,
            slippage_pips=slippage,
        )
        filtered_results[key] = run_candidate_backtest(
            bars=validation_bars,
            candidates=filtered_validation,
            strategy_id=strategy_id,
            split=VALIDATION_SPLIT,
            code_commit=code_commit,
            slippage_pips=slippage,
        )

    gate = validation_gate(
        filtered_results["0.2"],
        baselines["0.2"],
        filtered_results["0.5"],
        baselines["0.5"],
    )
    validation_artifact = {
        "status": "PROMOTE_ML_FILTER" if gate.passed else "REJECT_ML_FILTER",
        "validation_loaded": True,
        "model_family": selected_family.value,
        "retained_fraction": selected_cutoff.retained_fraction,
        "cutoff": _serialize_cutoff(selected_cutoff),
        "score_digest": score_digest(validation_ids, validation_scores),
        "diagnostics": _diagnostics_for_labeled(
            dataset=validation,
            all_ids=validation_ids,
            all_scores=validation_scores,
        ),
        "feature_manifest_sha256": validation["feature_manifest_sha256"],
        "baseline_results": {
            key: _serialize_financial(value) for key, value in baselines.items()
        },
        "filtered_results": {
            key: _serialize_financial(value) for key, value in filtered_results.items()
        },
        "gate": _serialize_gate(gate),
        "refit_count_after_selection": 0,
    }
    return {
        "experiment_id": EXPERIMENT_ID,
        "strategy_id": strategy_id,
        "code_commit": code_commit,
        "selection": selection_artifact,
        "validation": validation_artifact,
    }
