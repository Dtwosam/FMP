from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import pickle
import struct
import warnings
from typing import Mapping, Sequence

import numpy as np
import polars as pl
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression

from fmp.features.schema import FEATURE_COLUMNS
from fmp.models.preprocessing import (
    PreprocessorState,
    fit_preprocessor,
    transform_features,
)

from .contracts import EVIDENCE_LABEL, MARKET_FEATURE_SET_VERSION
from .model_protocol import (
    CONFIDENCE_THRESHOLDS,
    DIAGNOSTIC_SCENARIOS,
    FIT_SPLIT,
    GATE_REQUIREMENTS,
    HIST_GRADIENT_BOOSTING_CONFIG,
    HOLDOUT_GATE_SCENARIOS,
    LOGISTIC_REGRESSION_CONFIG,
    MIN_DIRECTIONAL_CANDIDATES,
    MODEL_FAMILIES,
    MODEL_INPUT_COLUMNS,
    MODEL_PROTOCOL_DECISION,
    MODEL_PROTOCOL_VERSION,
    PROTOCOL_SPLITS,
    RETROSPECTIVE_HOLDOUT_SPLIT,
    SELECTION_GATE_SCENARIOS,
    SELECTION_SPLIT,
    TARGET_CLASSES,
    TARGET_COLUMN,
    VALIDATION_GATE_SCENARIOS,
    VALIDATION_SPLIT,
    ModelCell,
    ModelProtocolSplit,
    directional_candidate,
    protocol_fingerprint,
)
from .outcomes import (
    MARKET_OUTCOME_SET_VERSION,
    OUTCOME_COLUMNS,
    OUTCOME_FEATURE_IDENTITY_COLUMNS,
)


MODEL_TRAINING_CORE_VERSION = "fmp-exp044-model-training-core-v1"
MODEL_TRAINING_CORE_DECISION = "DEC-090"
MODEL_TRAINING_REPAIR_VERSION = "fmp-exp044-model-training-repair-v1"
MODEL_TRAINING_REPAIR_DECISION = "DEC-094"
MODEL_TRAINING_RESULT_EXECUTION_AUTHORIZED = False

_SCENARIO_COLUMNS = {
    0.2: ("long_net_pips_0p2", "short_net_pips_0p2"),
    0.5: ("long_net_pips_0p5", "short_net_pips_0p5"),
    1.0: ("long_net_pips_1p0", "short_net_pips_1p0"),
}


@dataclass(frozen=True, slots=True)
class FittedMarketModel:
    family: str
    preprocessor: PreprocessorState
    estimator: object
    preprocessor_fingerprint: str
    model_fingerprint: str


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _split_bounds(split: ModelProtocolSplit) -> tuple[datetime, datetime]:
    return (
        datetime(
            split.start.year,
            split.start.month,
            split.start.day,
            tzinfo=timezone.utc,
        ),
        datetime(
            split.end_exclusive.year,
            split.end_exclusive.month,
            split.end_exclusive.day,
            tzinfo=timezone.utc,
        ),
    )


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value


def _expected_direction(long_pips: float, short_pips: float) -> str:
    if long_pips > 0.0 and long_pips > short_pips:
        return "LONG"
    if short_pips > 0.0 and short_pips > long_pips:
        return "SHORT"
    return "NO_TRADE"


def _validate_frames(
    features: pl.DataFrame,
    outcomes: pl.DataFrame,
    *,
    cell: ModelCell,
) -> tuple[pl.DataFrame, str]:
    if cell.symbol not in {"EURUSD", "GBPUSD", "USDJPY"}:
        raise ValueError("unsupported EXP-044 model symbol")
    if cell.timeframe not in {"5m", "15m", "1h"}:
        raise ValueError("unsupported EXP-044 model timeframe")
    if cell.horizon_minutes not in {60, 240}:
        raise ValueError("unsupported EXP-044 model horizon")

    missing_features = [
        name for name in FEATURE_COLUMNS if name not in features.columns
    ]
    if missing_features:
        raise ValueError(
            f"EXP-044 model features are missing columns: {missing_features}"
        )
    missing_outcomes = [
        name for name in OUTCOME_COLUMNS if name not in outcomes.columns
    ]
    if missing_outcomes:
        raise ValueError(
            f"EXP-044 model outcomes are missing columns: {missing_outcomes}"
        )
    if features.is_empty() or outcomes.is_empty():
        raise ValueError("EXP-044 model cell inputs must be non-empty")

    if set(features["symbol"].to_list()) != {cell.symbol}:
        raise ValueError("EXP-044 model feature symbol mismatch")
    if set(features["timeframe"].to_list()) != {cell.timeframe}:
        raise ValueError("EXP-044 model feature timeframe mismatch")
    if set(features["feature_set_version"].to_list()) != {
        MARKET_FEATURE_SET_VERSION
    }:
        raise ValueError("EXP-044 model feature-set identity mismatch")

    cell_outcomes = outcomes.filter(
        (pl.col("symbol") == cell.symbol)
        & (pl.col("timeframe") == cell.timeframe)
        & (pl.col("horizon_minutes") == cell.horizon_minutes)
    )
    if cell_outcomes.is_empty():
        raise ValueError("EXP-044 model outcome cell is empty")
    if set(cell_outcomes["feature_set_version"].to_list()) != {
        MARKET_FEATURE_SET_VERSION
    }:
        raise ValueError("EXP-044 model outcome feature-set identity mismatch")
    if set(cell_outcomes["outcome_set_version"].to_list()) != {
        MARKET_OUTCOME_SET_VERSION
    }:
        raise ValueError("EXP-044 model outcome-set identity mismatch")
    if set(cell_outcomes["evidence_label"].to_list()) != {EVIDENCE_LABEL}:
        raise ValueError("EXP-044 model outcome evidence label mismatch")

    feature_manifests = set(
        features["processed_manifest_sha256"].to_list()
    )
    outcome_manifests = set(
        cell_outcomes["processed_manifest_sha256"].to_list()
    )
    if len(feature_manifests) != 1 or len(outcome_manifests) != 1:
        raise ValueError(
            "EXP-044 model source manifest identity is not singular"
        )
    processed_manifest_sha256 = _validate_sha256(
        next(iter(feature_manifests)),
        field="EXP-044 processed manifest sha256",
    )
    if outcome_manifests != {processed_manifest_sha256}:
        raise ValueError("EXP-044 feature/outcome source manifest mismatch")

    feature_unique = features.select(
        pl.struct(
            [
                "symbol",
                "timeframe",
                "bar_start_utc",
                "available_at_utc",
                "feature_set_version",
                "processed_manifest_sha256",
            ]
        ).n_unique()
    ).item()
    if feature_unique != features.height:
        raise ValueError("duplicate EXP-044 model feature identity")

    outcome_unique = cell_outcomes.select(
        pl.struct(
            [
                "symbol",
                "timeframe",
                "bar_start_utc",
                "horizon_minutes",
            ]
        ).n_unique()
    ).item()
    if outcome_unique != cell_outcomes.height:
        raise ValueError("duplicate EXP-044 model outcome identity")

    scenario_columns = [
        "available_at_utc",
        "exit_timestamp_utc",
        "long_net_pips_0p2",
        "short_net_pips_0p2",
        "best_direction_0p2",
        "long_net_pips_0p5",
        "short_net_pips_0p5",
        "best_direction_0p5",
        "long_net_pips_1p0",
        "short_net_pips_1p0",
        "best_direction_1p0",
    ]
    for row in cell_outcomes.select(scenario_columns).iter_rows(named=True):
        available = row["available_at_utc"]
        exit_timestamp = row["exit_timestamp_utc"]
        if (
            not isinstance(available, datetime)
            or not isinstance(exit_timestamp, datetime)
            or exit_timestamp <= available
        ):
            raise ValueError("EXP-044 model outcome timestamps are invalid")
        if (
            exit_timestamp - available
        ).total_seconds() != cell.horizon_minutes * 60:
            raise ValueError(
                "EXP-044 model outcome horizon timestamp mismatch"
            )

        for suffix in ("0p2", "0p5", "1p0"):
            long_value = float(row[f"long_net_pips_{suffix}"])
            short_value = float(row[f"short_net_pips_{suffix}"])
            if not math.isfinite(long_value) or not math.isfinite(
                short_value
            ):
                raise ValueError(
                    "EXP-044 model outcome pips must be finite"
                )
            expected = _expected_direction(long_value, short_value)
            if row[f"best_direction_{suffix}"] != expected:
                raise ValueError(
                    "EXP-044 model outcome direction does not match "
                    "frozen pips"
                )

    joined = features.join(
        cell_outcomes.select(
            [
                *OUTCOME_FEATURE_IDENTITY_COLUMNS,
                "exit_timestamp_utc",
                "horizon_minutes",
                "future_mid_move_pips",
                "long_net_pips_0p2",
                "short_net_pips_0p2",
                "best_direction_0p2",
                "long_net_pips_0p5",
                "short_net_pips_0p5",
                "best_direction_0p5",
                "long_net_pips_1p0",
                "short_net_pips_1p0",
                "best_direction_1p0",
                "outcome_set_version",
                "evidence_label",
            ]
        ),
        on=list(OUTCOME_FEATURE_IDENTITY_COLUMNS),
        how="inner",
        validate="1:1",
    ).sort(["bar_start_utc"])

    if joined.is_empty():
        raise ValueError("EXP-044 model feature/outcome join is empty")
    return joined, processed_manifest_sha256


def _split_frame(
    frame: pl.DataFrame,
    split: ModelProtocolSplit,
) -> pl.DataFrame:
    start, end = _split_bounds(split)
    return frame.filter(
        (pl.col("available_at_utc") >= start)
        & (pl.col("available_at_utc") < end)
        & (pl.col("exit_timestamp_utc") < end)
    ).sort(["bar_start_utc"])


def _row_identity(
    frame: pl.DataFrame,
    *,
    cell: ModelCell,
) -> tuple[str, ...]:
    values: list[str] = []
    for row in frame.select(
        ["symbol", "timeframe", "bar_start_utc"]
    ).iter_rows(named=True):
        timestamp = row["bar_start_utc"]
        if not isinstance(timestamp, datetime):
            raise ValueError(
                "EXP-044 model bar_start_utc must be datetime"
            )
        values.append(
            "|".join(
                (
                    str(row["symbol"]),
                    str(row["timeframe"]),
                    timestamp.isoformat(),
                    str(cell.horizon_minutes),
                )
            )
        )
    if len(set(values)) != len(values):
        raise ValueError("duplicate EXP-044 model row identity")
    return tuple(values)


def _target_counts(frame: pl.DataFrame) -> dict[str, int]:
    counts = {name: 0 for name in TARGET_CLASSES}
    for value in frame[TARGET_COLUMN].to_list():
        if value not in counts:
            raise ValueError(
                f"unexpected EXP-044 model target class: {value!r}"
            )
        counts[str(value)] += 1
    return counts


def _preprocessor_fingerprint(state: PreprocessorState) -> str:
    return _sha256(_canonical_json(asdict(state)))


def _model_fingerprint(estimator: object) -> str:
    return _sha256(pickle.dumps(estimator, protocol=5))


def _fit_family(
    family: str,
    fit_frame: pl.DataFrame,
) -> FittedMarketModel:
    if family not in MODEL_FAMILIES:
        raise ValueError(
            f"unsupported EXP-044 model family: {family!r}"
        )

    counts = _target_counts(fit_frame)
    if any(counts[name] <= 0 for name in TARGET_CLASSES):
        raise ValueError(
            "EXP-044 fit split must contain all three target classes"
        )

    preprocessor = fit_preprocessor(
        fit_frame.select(list(MODEL_INPUT_COLUMNS)),
        standardize=family == "logistic_regression",
    )
    X = transform_features(
        fit_frame.select(list(MODEL_INPUT_COLUMNS)),
        preprocessor,
    )
    y = np.asarray(fit_frame[TARGET_COLUMN].to_list())

    if family == "logistic_regression":
        estimator = LogisticRegression(
            **dict(LOGISTIC_REGRESSION_CONFIG)
        )
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", ConvergenceWarning)
                estimator.fit(X, y)
        except ConvergenceWarning as exc:
            raise RuntimeError(
                "EXP-044 logistic regression failed to converge"
            ) from exc
    else:
        estimator = HistGradientBoostingClassifier(
            **dict(HIST_GRADIENT_BOOSTING_CONFIG)
        )
        estimator.fit(X, y)

    return FittedMarketModel(
        family=family,
        preprocessor=preprocessor,
        estimator=estimator,
        preprocessor_fingerprint=_preprocessor_fingerprint(
            preprocessor
        ),
        model_fingerprint=_model_fingerprint(estimator),
    )


def _score_probabilities(
    fitted: FittedMarketModel,
    frame: pl.DataFrame,
) -> np.ndarray:
    X = transform_features(
        frame.select(list(MODEL_INPUT_COLUMNS)),
        fitted.preprocessor,
    )
    raw = np.asarray(
        fitted.estimator.predict_proba(X),
        dtype=np.float64,
    )
    classes = tuple(
        str(value) for value in fitted.estimator.classes_
    )
    if set(classes) != set(TARGET_CLASSES):
        raise ValueError("EXP-044 estimator class identity mismatch")
    if raw.shape != (frame.height, len(TARGET_CLASSES)):
        raise ValueError(
            "EXP-044 estimator probability shape mismatch"
        )
    canonical = np.column_stack(
        [raw[:, classes.index(name)] for name in TARGET_CLASSES]
    )
    if (
        not np.isfinite(canonical).all()
        or np.any(canonical < 0.0)
        or np.any(canonical > 1.0)
    ):
        raise ValueError(
            "EXP-044 estimator emitted invalid probabilities"
        )
    if not np.allclose(
        canonical.sum(axis=1),
        np.ones(frame.height),
        rtol=0.0,
        atol=1e-9,
    ):
        raise ValueError(
            "EXP-044 estimator probabilities do not sum to one"
        )
    return canonical


def _probability_digest(
    row_ids: Sequence[str],
    probabilities: np.ndarray,
) -> str:
    if len(row_ids) != probabilities.shape[0]:
        raise ValueError(
            "EXP-044 probability digest row mismatch"
        )
    digest = hashlib.sha256()
    for row_id, row in zip(
        row_ids,
        probabilities,
        strict=True,
    ):
        encoded = row_id.encode("utf-8")
        digest.update(
            len(encoded).to_bytes(8, "big", signed=False)
        )
        digest.update(encoded)
        for value in row.tolist():
            digest.update(struct.pack(">d", float(value)))
    return digest.hexdigest()


def _top_classes(probabilities: np.ndarray) -> np.ndarray:
    out = np.empty(probabilities.shape[0], dtype=object)
    for index, row in enumerate(probabilities):
        maximum = float(np.max(row))
        winners = np.flatnonzero(row == maximum)
        if len(winners) != 1:
            out[index] = "NO_TRADE"
        else:
            out[index] = TARGET_CLASSES[int(winners[0])]
    return out


def _candidate_directions(
    probabilities: np.ndarray,
    *,
    threshold: float,
) -> np.ndarray:
    if threshold not in CONFIDENCE_THRESHOLDS:
        raise ValueError(
            "unsupported EXP-044 confidence threshold"
        )
    out = np.empty(probabilities.shape[0], dtype=object)
    for index, row in enumerate(probabilities):
        mapping = {
            name: float(row[class_index])
            for class_index, name in enumerate(TARGET_CLASSES)
        }
        out[index] = directional_candidate(
            mapping,
            threshold=threshold,
        )
    return out


def _classification_diagnostics(
    frame: pl.DataFrame,
    probabilities: np.ndarray,
) -> dict[str, object]:
    labels = np.asarray(
        frame[TARGET_COLUMN].to_list(),
        dtype=object,
    )
    top = _top_classes(probabilities)

    confusion = {
        actual: {predicted: 0 for predicted in TARGET_CLASSES}
        for actual in TARGET_CLASSES
    }
    for actual, predicted in zip(
        labels.tolist(),
        top.tolist(),
        strict=True,
    ):
        confusion[str(actual)][str(predicted)] += 1

    class_index = {
        name: index
        for index, name in enumerate(TARGET_CLASSES)
    }
    selected_probability = np.asarray(
        [
            probabilities[row_index, class_index[str(label)]]
            for row_index, label in enumerate(labels.tolist())
        ],
        dtype=np.float64,
    )
    epsilon = np.finfo(np.float64).eps
    multiclass_log_loss = float(
        -np.mean(
            np.log(
                np.clip(
                    selected_probability,
                    epsilon,
                    1.0,
                )
            )
        )
    )

    counts = _target_counts(frame)
    return {
        "row_count": frame.height,
        "class_counts": counts,
        "class_prevalence": {
            name: float(counts[name] / frame.height)
            for name in TARGET_CLASSES
        },
        "multiclass_log_loss": multiclass_log_loss,
        "confusion_matrix": confusion,
    }


def _candidate_digest(
    row_ids: Sequence[str],
    directions: Sequence[str],
) -> str:
    if len(row_ids) != len(directions):
        raise ValueError(
            "EXP-044 candidate digest row mismatch"
        )
    digest = hashlib.sha256()
    for row_id, direction in zip(
        row_ids,
        directions,
        strict=True,
    ):
        if direction == "NO_TRADE":
            continue
        payload = f"{row_id}|{direction}".encode("utf-8")
        digest.update(
            len(payload).to_bytes(8, "big", signed=False)
        )
        digest.update(payload)
    return digest.hexdigest()


def _financial_metrics(
    frame: pl.DataFrame,
    directions: np.ndarray,
    *,
    scenario: float,
    row_ids: Sequence[str],
) -> dict[str, object]:
    try:
        long_column, short_column = _SCENARIO_COLUMNS[scenario]
    except KeyError as exc:
        raise ValueError(
            "unsupported EXP-044 financial scenario"
        ) from exc

    long_values = np.asarray(
        frame[long_column].to_list(),
        dtype=np.float64,
    )
    short_values = np.asarray(
        frame[short_column].to_list(),
        dtype=np.float64,
    )
    if (
        not np.isfinite(long_values).all()
        or not np.isfinite(short_values).all()
    ):
        raise ValueError(
            "EXP-044 financial outcome pips must be finite"
        )

    long_mask = directions == "LONG"
    short_mask = directions == "SHORT"
    directional_mask = long_mask | short_mask
    selected = np.where(
        long_mask,
        long_values,
        short_values,
    )[directional_mask]

    count = int(directional_mask.sum())
    total = float(selected.sum()) if count else 0.0
    mean = float(selected.mean()) if count else None
    positive = selected[selected > 0.0]
    negative = selected[selected < 0.0]
    zero = selected[selected == 0.0]

    return {
        "slippage_pips_per_fill": scenario,
        "row_count": frame.height,
        "directional_candidate_count": count,
        "directional_candidate_rate": float(
            count / frame.height
        ),
        "long_candidate_count": int(long_mask.sum()),
        "short_candidate_count": int(short_mask.sum()),
        "total_net_pips": total,
        "mean_net_pips": mean,
        "gross_positive_pips": (
            float(positive.sum()) if positive.size else 0.0
        ),
        "absolute_gross_negative_pips": (
            float(abs(negative.sum()))
            if negative.size
            else 0.0
        ),
        "positive_candidate_count": int(positive.size),
        "negative_candidate_count": int(negative.size),
        "zero_candidate_count": int(zero.size),
        "candidate_identity_digest": _candidate_digest(
            row_ids,
            directions.tolist(),
        ),
    }


def _financial_gate(
    metrics: Mapping[str, object],
) -> dict[str, object]:
    count = int(metrics["directional_candidate_count"])
    total = float(metrics["total_net_pips"])
    mean_raw = metrics["mean_net_pips"]
    mean = (
        float(mean_raw)
        if mean_raw is not None
        else float("-inf")
    )
    gross_positive = float(
        metrics["gross_positive_pips"]
    )
    gross_negative = float(
        metrics["absolute_gross_negative_pips"]
    )
    criteria = {
        GATE_REQUIREMENTS[0]: (
            count >= MIN_DIRECTIONAL_CANDIDATES
        ),
        GATE_REQUIREMENTS[1]: total > 0.0,
        GATE_REQUIREMENTS[2]: mean > 0.0,
        GATE_REQUIREMENTS[3]: (
            gross_positive > gross_negative
        ),
    }
    return {
        "passed": all(criteria.values()),
        "criteria": criteria,
    }


def _score_split(
    fitted: FittedMarketModel,
    frame: pl.DataFrame,
    *,
    cell: ModelCell,
) -> tuple[
    np.ndarray,
    dict[str, object],
    str,
    tuple[str, ...],
]:
    if frame.is_empty():
        raise ValueError(
            "EXP-044 scored split must be non-empty"
        )
    probabilities = _score_probabilities(fitted, frame)
    row_ids = _row_identity(frame, cell=cell)
    return (
        probabilities,
        _classification_diagnostics(
            frame,
            probabilities,
        ),
        _probability_digest(
            row_ids,
            probabilities,
        ),
        row_ids,
    )


def _evaluate_threshold(
    frame: pl.DataFrame,
    probabilities: np.ndarray,
    *,
    threshold: float,
    scenarios: Sequence[float],
    row_ids: Sequence[str],
) -> dict[str, object]:
    directions = _candidate_directions(
        probabilities,
        threshold=threshold,
    )
    scenario_results: dict[str, object] = {}
    for scenario in scenarios:
        metrics = _financial_metrics(
            frame,
            directions,
            scenario=float(scenario),
            row_ids=row_ids,
        )
        scenario_results[str(float(scenario))] = {
            "metrics": metrics,
            "gate": _financial_gate(metrics),
        }
    return {
        "confidence_threshold": threshold,
        "scenarios": scenario_results,
    }


def _selection_key(
    row: Mapping[str, object],
) -> tuple[float, int, int, float]:
    scenario = row["scenarios"]["0.5"]
    metrics = scenario["metrics"]
    return (
        float(metrics["total_net_pips"]),
        int(metrics["directional_candidate_count"]),
        (
            1
            if row["model_family"]
            == "logistic_regression"
            else 0
        ),
        float(row["confidence_threshold"]),
    )


def _evaluate_selected_split(
    *,
    fitted: FittedMarketModel,
    frame: pl.DataFrame,
    cell: ModelCell,
    threshold: float,
    gate_scenarios: Sequence[float],
) -> dict[str, object]:
    (
        probabilities,
        diagnostics,
        probability_digest,
        row_ids,
    ) = _score_split(
        fitted,
        frame,
        cell=cell,
    )
    all_scenarios = tuple(
        sorted(
            set(
                float(value)
                for value in (
                    *DIAGNOSTIC_SCENARIOS,
                    *gate_scenarios,
                )
            )
        )
    )
    evaluated = _evaluate_threshold(
        frame,
        probabilities,
        threshold=threshold,
        scenarios=all_scenarios,
        row_ids=row_ids,
    )
    gating = [
        bool(
            evaluated["scenarios"][
                str(float(value))
            ]["gate"]["passed"]
        )
        for value in gate_scenarios
    ]
    return {
        "status": (
            "PASS" if all(gating) else "REJECT"
        ),
        "row_count": frame.height,
        "classification": diagnostics,
        "probability_digest": probability_digest,
        **evaluated,
    }


def run_model_cell_core(
    *,
    features: pl.DataFrame,
    outcomes: pl.DataFrame,
    cell: ModelCell,
) -> dict[str, object]:
    joined, processed_manifest_sha256 = _validate_frames(
        features,
        outcomes,
        cell=cell,
    )
    split_frames = {
        split.name: _split_frame(joined, split)
        for split in PROTOCOL_SPLITS
    }
    if any(
        frame.is_empty()
        for frame in split_frames.values()
    ):
        empty = [
            name
            for name, frame in split_frames.items()
            if frame.is_empty()
        ]
        raise ValueError(
            "EXP-044 model cell has empty required "
            f"split(s): {empty}"
        )

    fit_frame = split_frames[FIT_SPLIT.name]
    fit_counts = _target_counts(fit_frame)
    if any(
        fit_counts[name] <= 0
        for name in TARGET_CLASSES
    ):
        raise ValueError(
            "EXP-044 fit split must contain all "
            "three target classes"
        )

    fitted: dict[str, FittedMarketModel] = {}
    family_fit: dict[str, dict[str, object]] = {}
    for family in MODEL_FAMILIES:
        try:
            fitted_model = _fit_family(
                family,
                fit_frame,
            )
        except RuntimeError as exc:
            if (
                family == "logistic_regression"
                and str(exc)
                == "EXP-044 logistic regression failed to converge"
            ):
                family_fit[family] = {
                    "status": "FAILED_NON_CONVERGENCE",
                    "failure_reason": (
                        "LBFGS_MAX_ITER_REACHED"
                    ),
                }
                continue
            raise
        fitted[family] = fitted_model
        family_fit[family] = {
            "status": "FITTED",
            "preprocessor_fingerprint": (
                fitted_model.preprocessor_fingerprint
            ),
            "model_fingerprint": (
                fitted_model.model_fingerprint
            ),
        }

    if not fitted:
        raise RuntimeError(
            "EXP-044 model cell has no successfully fitted family"
        )

    selection_frame = split_frames[SELECTION_SPLIT.name]
    variants: list[dict[str, object]] = []
    selection_diagnostics: dict[str, object] = {}
    selection_probability_digests: dict[str, str] = {}

    for family in MODEL_FAMILIES:
        if family not in fitted:
            selection_diagnostics[family] = {
                "status": "FAMILY_UNAVAILABLE",
                "failure_reason": (
                    family_fit[family]["failure_reason"]
                ),
            }
            selection_probability_digests[family] = None
            for threshold in CONFIDENCE_THRESHOLDS:
                variants.append(
                    {
                        "model_family": family,
                        "confidence_threshold": threshold,
                        "family_fit_status": (
                            family_fit[family]["status"]
                        ),
                        "evaluation_status": (
                            "FAMILY_UNAVAILABLE"
                        ),
                        "selection_gate_passed": False,
                    }
                )
            continue

        (
            probabilities,
            diagnostics,
            probability_digest,
            row_ids,
        ) = _score_split(
            fitted[family],
            selection_frame,
            cell=cell,
        )
        selection_diagnostics[family] = diagnostics
        selection_probability_digests[
            family
        ] = probability_digest

        for threshold in CONFIDENCE_THRESHOLDS:
            evaluated = _evaluate_threshold(
                selection_frame,
                probabilities,
                threshold=threshold,
                scenarios=SELECTION_GATE_SCENARIOS,
                row_ids=row_ids,
            )
            scenario = evaluated["scenarios"]["0.5"]
            variants.append(
                {
                    "model_family": family,
                    "family_fit_status": "FITTED",
                    "evaluation_status": "EVALUATED",
                    **evaluated,
                    "selection_gate_passed": bool(
                        scenario["gate"]["passed"]
                    ),
                }
            )

    passing = [
        row
        for row in variants
        if row["selection_gate_passed"]
    ]
    selected = (
        max(passing, key=_selection_key)
        if passing
        else None
    )

    result: dict[str, object] = {
        "training_core_version": (
            MODEL_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            MODEL_TRAINING_CORE_DECISION
        ),
        "training_repair_version": (
            MODEL_TRAINING_REPAIR_VERSION
        ),
        "training_repair_decision": (
            MODEL_TRAINING_REPAIR_DECISION
        ),
        "protocol_decision": MODEL_PROTOCOL_DECISION,
        "protocol_version": MODEL_PROTOCOL_VERSION,
        "protocol_fingerprint": protocol_fingerprint(),
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "cell": {
            "symbol": cell.symbol,
            "timeframe": cell.timeframe,
            "horizon_minutes": cell.horizon_minutes,
        },
        "processed_manifest_sha256": (
            processed_manifest_sha256
        ),
        "joined_row_count": joined.height,
        "split_row_counts": {
            name: frame.height
            for name, frame in split_frames.items()
        },
        "fit": {
            "row_count": fit_frame.height,
            "target_class_counts": fit_counts,
            "families": family_fit,
        },
        "selection": {
            "status": (
                "SELECTED"
                if selected is not None
                else "NO_MODEL_CHALLENGER"
            ),
            "row_count": selection_frame.height,
            "classification_by_family": (
                selection_diagnostics
            ),
            "probability_digest_by_family": (
                selection_probability_digests
            ),
            "variants": variants,
            "selected_variant": (
                {
                    "model_family": selected[
                        "model_family"
                    ],
                    "confidence_threshold": selected[
                        "confidence_threshold"
                    ],
                }
                if selected is not None
                else None
            ),
        },
        "validation": {
            "status": "LOCKED_NO_SELECTION",
        },
        "retrospective_holdout": {
            "status": "LOCKED_NO_SELECTION",
        },
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
    }

    if selected is None:
        result["result_fingerprint"] = _sha256(
            _canonical_json(result)
        )
        return result

    selected_family = str(
        selected["model_family"]
    )
    selected_threshold = float(
        selected["confidence_threshold"]
    )

    validation = _evaluate_selected_split(
        fitted=fitted[selected_family],
        frame=split_frames[VALIDATION_SPLIT.name],
        cell=cell,
        threshold=selected_threshold,
        gate_scenarios=VALIDATION_GATE_SCENARIOS,
    )
    result["validation"] = validation

    if validation["status"] != "PASS":
        result["retrospective_holdout"] = {
            "status": "LOCKED_VALIDATION_REJECT",
        }
        result["result_fingerprint"] = _sha256(
            _canonical_json(result)
        )
        return result

    result["retrospective_holdout"] = (
        _evaluate_selected_split(
            fitted=fitted[selected_family],
            frame=split_frames[
                RETROSPECTIVE_HOLDOUT_SPLIT.name
            ],
            cell=cell,
            threshold=selected_threshold,
            gate_scenarios=HOLDOUT_GATE_SCENARIOS,
        )
    )
    result["result_fingerprint"] = _sha256(
        _canonical_json(result)
    )
    return result


__all__ = [
    "FittedMarketModel",
    "MODEL_TRAINING_CORE_DECISION",
    "MODEL_TRAINING_CORE_VERSION",
    "MODEL_TRAINING_REPAIR_DECISION",
    "MODEL_TRAINING_REPAIR_VERSION",
    "MODEL_TRAINING_RESULT_EXECUTION_AUTHORIZED",
    "run_model_cell_core",
]
