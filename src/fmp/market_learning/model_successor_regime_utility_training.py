from __future__ import annotations

from datetime import date
import hashlib
from pathlib import Path
import struct
from typing import Mapping, Sequence

import numpy as np
import polars as pl
from sklearn.ensemble import HistGradientBoostingRegressor

from . import model_training as _base
from .contracts import EVIDENCE_LABEL
from .model_protocol import (
    DIAGNOSTIC_SCENARIOS,
    HOLDOUT_GATE_SCENARIOS,
    MODEL_INPUT_COLUMNS,
    PROTOCOL_SPLITS,
    RETROSPECTIVE_HOLDOUT_SPLIT,
    SELECTION_GATE_SCENARIOS,
    SELECTION_SPLIT,
    VALIDATION_GATE_SCENARIOS,
    VALIDATION_SPLIT,
    ModelCell,
    ModelProtocolSplit,
)
from .model_successor_density_training import (
    _canonical_json,
    _git_blob_sha,
    _parse_utc_date,
    _window_gate,
    _window_indices,
)
from .model_successor_regime_utility_protocol import (
    CANDIDATE_BUDGET_ANCHORS,
    FINANCIAL_TARGET_COLUMNS,
    FIT_REGIME_WINDOWS,
    HIST_GRADIENT_BOOSTING_REGRESSION_CONFIG,
    MIN_STABILITY_WINDOW_CANDIDATE_SHARE,
    PRIOR_RESULT_INFORMED,
    REGIME_UTILITY_EXPERIMENT_ID,
    REGIME_UTILITY_PROTOCOL_DECISION,
    REGIME_UTILITY_PROTOCOL_VERSION,
    TEMPORAL_STABILITY_WINDOWS,
    UNTOUCHED_OOS,
    regime_utility_protocol_fingerprint,
)


REGIME_UTILITY_TRAINING_CORE_VERSION = (
    "fmp-exp049-regime-utility-training-core-v1"
)
REGIME_UTILITY_TRAINING_CORE_DECISION = "DEC-133"

DEC132_MERGED_COMMIT = (
    "d17326eebf6b456211225d7bad3a182a0307b707"
)
DEC132_PROTOCOL_BLOB_SHA = (
    "ad2fcb22656fc7a1490f4cdf87fb25c62895a1ac"
)
BASE_TRAINING_CORE_BLOB_SHA = (
    "34b50a3f907d26b1c5ec50a0a0b444a3417d04f7"
)
DENSITY_HELPER_CORE_BLOB_SHA = (
    "8ed51edc12c8d7d23cf9cc362e6b0ea7564d4945"
)

REGIME_UTILITY_RESULT_EXECUTION_AUTHORIZED = False
MODEL_FIT_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
SHADOW_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def validate_regime_utility_training_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "dec132_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_regime_utility_protocol.py",
            DEC132_PROTOCOL_BLOB_SHA,
        ),
        "base_training_core": (
            root
            / "src/fmp/market_learning/model_training.py",
            BASE_TRAINING_CORE_BLOB_SHA,
        ),
        "density_helper_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_density_training.py",
            DENSITY_HELPER_CORE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(
                f"missing EXP-049 training dependency: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-049 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    protocol_fingerprint = regime_utility_protocol_fingerprint()
    if len(protocol_fingerprint) != 64:
        raise ValueError(
            "EXP-049 regime-utility protocol fingerprint is invalid"
        )

    return {
        "regime_utility_training_core_version": (
            REGIME_UTILITY_TRAINING_CORE_VERSION
        ),
        "regime_utility_training_core_decision": (
            REGIME_UTILITY_TRAINING_CORE_DECISION
        ),
        "dec132_merged_commit": DEC132_MERGED_COMMIT,
        "dec132_protocol_blob_sha": actual[
            "dec132_protocol"
        ],
        "base_training_core_blob_sha": actual[
            "base_training_core"
        ],
        "density_helper_core_blob_sha": actual[
            "density_helper_core"
        ],
        "regime_utility_protocol_fingerprint": (
            protocol_fingerprint
        ),
        "regime_utility_result_execution_authorized": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
    }


def _fit_regime_splits() -> tuple[ModelProtocolSplit, ...]:
    return tuple(
        ModelProtocolSplit(
            name=str(window["name"]),
            start=date.fromisoformat(str(window["start"])),
            end_exclusive=date.fromisoformat(
                str(window["end_exclusive"])
            ),
        )
        for window in FIT_REGIME_WINDOWS
    )


def _target_summary(
    frame: pl.DataFrame,
    *,
    target_column: str,
) -> dict[str, object]:
    if target_column not in FINANCIAL_TARGET_COLUMNS:
        raise ValueError(
            "unsupported EXP-049 financial regression target"
        )
    values = np.asarray(
        frame[target_column].to_list(),
        dtype=np.float64,
    )
    if values.shape != (frame.height,):
        raise ValueError(
            "EXP-049 regression target shape mismatch"
        )
    if not np.isfinite(values).all():
        raise ValueError(
            "EXP-049 regression target values must be finite"
        )
    return {
        "row_count": frame.height,
        "minimum_net_pips": float(values.min()),
        "maximum_net_pips": float(values.max()),
        "mean_net_pips": float(values.mean()),
        "positive_count": int((values > 0.0).sum()),
        "negative_count": int((values < 0.0).sum()),
        "zero_count": int((values == 0.0).sum()),
    }


def _fit_regressor(
    frame: pl.DataFrame,
    *,
    target_column: str,
) -> _base.FittedMarketModel:
    _target_summary(
        frame,
        target_column=target_column,
    )
    preprocessor = _base.fit_preprocessor(
        frame.select(list(MODEL_INPUT_COLUMNS)),
        standardize=False,
    )
    X = _base.transform_features(
        frame.select(list(MODEL_INPUT_COLUMNS)),
        preprocessor,
    )
    y = np.asarray(
        frame[target_column].to_list(),
        dtype=np.float64,
    )

    estimator = HistGradientBoostingRegressor(
        **dict(HIST_GRADIENT_BOOSTING_REGRESSION_CONFIG)
    )
    estimator.fit(X, y)

    return _base.FittedMarketModel(
        family="hist_gradient_boosting_regression",
        preprocessor=preprocessor,
        estimator=estimator,
        preprocessor_fingerprint=(
            _base._preprocessor_fingerprint(
                preprocessor
            )
        ),
        model_fingerprint=_base._model_fingerprint(
            estimator
        ),
    )


def _prediction_digest(
    *,
    row_ids: Sequence[str],
    predictions: np.ndarray,
) -> str:
    if len(row_ids) != len(predictions):
        raise ValueError(
            "EXP-049 prediction digest row mismatch"
        )
    digest = hashlib.sha256()
    for row_id, value in zip(
        row_ids,
        predictions.tolist(),
        strict=True,
    ):
        encoded = str(row_id).encode("utf-8")
        digest.update(
            len(encoded).to_bytes(8, "big", signed=False)
        )
        digest.update(encoded)
        digest.update(struct.pack(">d", float(value)))
    return digest.hexdigest()


def _score_regressor(
    fitted: _base.FittedMarketModel,
    frame: pl.DataFrame,
    *,
    cell: ModelCell,
) -> tuple[np.ndarray, str, tuple[str, ...]]:
    if frame.is_empty():
        raise ValueError(
            "EXP-049 scored split must be non-empty"
        )
    if fitted.family != "hist_gradient_boosting_regression":
        raise ValueError(
            "EXP-049 fitted model family mismatch"
        )
    X = _base.transform_features(
        frame.select(list(MODEL_INPUT_COLUMNS)),
        fitted.preprocessor,
    )
    predictions = np.asarray(
        fitted.estimator.predict(X),
        dtype=np.float64,
    )
    if predictions.shape != (frame.height,):
        raise ValueError(
            "EXP-049 estimator prediction shape mismatch"
        )
    if not np.isfinite(predictions).all():
        raise ValueError(
            "EXP-049 estimator predictions must be finite"
        )
    row_ids = _base._row_identity(
        frame,
        cell=cell,
    )
    return (
        predictions,
        _prediction_digest(
            row_ids=row_ids,
            predictions=predictions,
        ),
        row_ids,
    )


def _regime_utility_direction_score(
    utility_matrices: Sequence[np.ndarray],
) -> tuple[np.ndarray, np.ndarray]:
    if len(utility_matrices) != 3:
        raise ValueError(
            "EXP-049 utility consensus requires exactly "
            "three regime matrices"
        )
    first = utility_matrices[0]
    if first.ndim != 2 or first.shape[1] != 2:
        raise ValueError(
            "EXP-049 utility matrix shape is invalid"
        )
    if not np.isfinite(first).all():
        raise ValueError(
            "EXP-049 utility predictions must be finite"
        )
    for value in utility_matrices[1:]:
        if value.shape != first.shape:
            raise ValueError(
                "EXP-049 regime utility shape mismatch"
            )
        if not np.isfinite(value).all():
            raise ValueError(
                "EXP-049 utility predictions must be finite"
            )

    directions = np.full(
        first.shape[0],
        "NO_TRADE",
        dtype=object,
    )
    robust_utility = np.full(
        first.shape[0],
        float("-inf"),
        dtype=np.float64,
    )

    for row_index in range(first.shape[0]):
        votes: list[str] = []
        voted_utilities: list[float] = []
        for matrix in utility_matrices:
            long_value = float(matrix[row_index, 0])
            short_value = float(matrix[row_index, 1])
            if long_value > short_value and long_value > 0.0:
                votes.append("LONG")
                voted_utilities.append(long_value)
            elif short_value > long_value and short_value > 0.0:
                votes.append("SHORT")
                voted_utilities.append(short_value)
            else:
                votes.append("NO_TRADE")
                voted_utilities.append(float("-inf"))

        if len(set(votes)) != 1:
            continue
        agreed = votes[0]
        if agreed not in {"LONG", "SHORT"}:
            continue
        directions[row_index] = agreed
        robust_utility[row_index] = min(voted_utilities)

    return directions, robust_utility


def _utility_consensus_digest(
    *,
    row_ids: Sequence[str],
    directions: np.ndarray,
    utility: np.ndarray,
) -> str:
    if (
        len(row_ids) != len(directions)
        or len(row_ids) != len(utility)
    ):
        raise ValueError(
            "EXP-049 utility consensus digest row mismatch"
        )
    digest = hashlib.sha256()
    for row_id, direction, value in zip(
        row_ids,
        directions.tolist(),
        utility.tolist(),
        strict=True,
    ):
        encoded = str(row_id).encode("utf-8")
        digest.update(
            len(encoded).to_bytes(8, "big", signed=False)
        )
        digest.update(encoded)
        label = str(direction).encode("ascii")
        digest.update(
            len(label).to_bytes(8, "big", signed=False)
        )
        digest.update(label)
        if direction in {"LONG", "SHORT"}:
            digest.update(struct.pack(">d", float(value)))
        else:
            digest.update(b"NO_UTILITY")
    return digest.hexdigest()


def _derive_utility_cutoff(
    *,
    directions: np.ndarray,
    utility: np.ndarray,
    row_ids: Sequence[str],
    budget: int,
) -> dict[str, object]:
    if budget not in CANDIDATE_BUDGET_ANCHORS:
        raise ValueError(
            "unsupported EXP-049 candidate budget"
        )
    if (
        len(row_ids) != len(directions)
        or len(row_ids) != len(utility)
    ):
        raise ValueError(
            "EXP-049 utility cutoff row mismatch"
        )

    eligible = [
        index
        for index, direction in enumerate(
            directions.tolist()
        )
        if direction in {"LONG", "SHORT"}
    ]
    for index in eligible:
        value = float(utility[index])
        if not np.isfinite(value) or value <= 0.0:
            raise ValueError(
                "EXP-049 directional utility must be "
                "finite and positive"
            )

    if len(eligible) < budget:
        return {
            "status": (
                "UNAVAILABLE_INSUFFICIENT_UTILITY_ROWS"
            ),
            "candidate_budget_anchor": budget,
            "eligible_utility_row_count": len(eligible),
            "selection_derived_cutoff": None,
        }

    ranked = sorted(
        eligible,
        key=lambda index: (
            -float(utility[index]),
            str(row_ids[index]),
        ),
    )
    cutoff = float(utility[ranked[budget - 1]])
    selected_count = sum(
        1
        for index in eligible
        if float(utility[index]) >= cutoff
    )
    return {
        "status": "AVAILABLE",
        "candidate_budget_anchor": budget,
        "eligible_utility_row_count": len(eligible),
        "selection_derived_cutoff": cutoff,
        "selection_candidate_count_at_cutoff": (
            selected_count
        ),
    }


def _candidate_directions(
    *,
    directions: np.ndarray,
    utility: np.ndarray,
    cutoff: float,
) -> np.ndarray:
    if not np.isfinite(cutoff) or cutoff <= 0.0:
        raise ValueError(
            "EXP-049 robust-utility cutoff is invalid"
        )
    if len(directions) != len(utility):
        raise ValueError(
            "EXP-049 candidate row mismatch"
        )

    out = np.full(
        len(directions),
        "NO_TRADE",
        dtype=object,
    )
    for index, direction in enumerate(
        directions.tolist()
    ):
        if direction not in {"LONG", "SHORT"}:
            continue
        value = float(utility[index])
        if not np.isfinite(value) or value <= 0.0:
            raise ValueError(
                "EXP-049 directional utility must be "
                "finite and positive"
            )
        if value >= cutoff:
            out[index] = direction
    return out


def _evaluate_utility_cutoff(
    frame: pl.DataFrame,
    *,
    directions: np.ndarray,
    utility: np.ndarray,
    cutoff: float,
    budget: int,
    scenarios: Sequence[float],
    row_ids: Sequence[str],
) -> dict[str, object]:
    candidates = _candidate_directions(
        directions=directions,
        utility=utility,
        cutoff=cutoff,
    )
    scenario_results: dict[str, object] = {}
    for scenario in scenarios:
        metrics = _base._financial_metrics(
            frame,
            candidates,
            scenario=float(scenario),
            row_ids=row_ids,
        )
        scenario_results[str(float(scenario))] = {
            "metrics": metrics,
            "gate": _base._financial_gate(metrics),
        }

    return {
        "candidate_budget_anchor": budget,
        "selection_derived_cutoff": cutoff,
        "scenarios": scenario_results,
    }


def _utility_diagnostics(
    *,
    directions: np.ndarray,
    utility: np.ndarray,
    regime_prediction_digests: Mapping[
        str,
        Mapping[str, str],
    ],
) -> dict[str, object]:
    counts = {
        name: int(
            sum(
                direction == name
                for direction in directions.tolist()
            )
        )
        for name in ("LONG", "SHORT", "NO_TRADE")
    }
    eligible = counts["LONG"] + counts["SHORT"]
    finite = [
        float(value)
        for direction, value in zip(
            directions.tolist(),
            utility.tolist(),
            strict=True,
        )
        if direction in {"LONG", "SHORT"}
    ]
    return {
        "row_count": len(directions),
        "consensus_direction_counts": counts,
        "consensus_eligible_row_count": eligible,
        "consensus_eligible_rate": (
            float(eligible / len(directions))
            if len(directions)
            else 0.0
        ),
        "minimum_robust_utility": (
            min(finite) if finite else None
        ),
        "maximum_robust_utility": (
            max(finite) if finite else None
        ),
        "regime_prediction_digests": {
            regime: dict(values)
            for regime, values in (
                regime_prediction_digests.items()
            )
        },
    }


def _score_utility_consensus(
    *,
    fitted_models: Mapping[
        str,
        Mapping[str, _base.FittedMarketModel],
    ],
    frame: pl.DataFrame,
    cell: ModelCell,
) -> tuple[
    np.ndarray,
    np.ndarray,
    dict[str, object],
    tuple[str, ...],
    str,
]:
    expected_regimes = {
        str(window["name"])
        for window in FIT_REGIME_WINDOWS
    }
    if set(fitted_models) != expected_regimes:
        raise ValueError(
            "EXP-049 fitted regime model set mismatch"
        )

    matrices: list[np.ndarray] = []
    digests: dict[str, dict[str, str]] = {}
    row_ids_reference: tuple[str, ...] | None = None

    for regime_name in (
        str(window["name"])
        for window in FIT_REGIME_WINDOWS
    ):
        target_models = fitted_models[regime_name]
        if set(target_models) != set(
            FINANCIAL_TARGET_COLUMNS
        ):
            raise ValueError(
                "EXP-049 fitted target model set mismatch"
            )

        target_predictions: list[np.ndarray] = []
        target_digests: dict[str, str] = {}
        for target_column in FINANCIAL_TARGET_COLUMNS:
            (
                predictions,
                digest,
                row_ids,
            ) = _score_regressor(
                target_models[target_column],
                frame,
                cell=cell,
            )
            if row_ids_reference is None:
                row_ids_reference = tuple(row_ids)
            elif tuple(row_ids) != row_ids_reference:
                raise ValueError(
                    "EXP-049 regime score row identity mismatch"
                )
            target_predictions.append(predictions)
            target_digests[target_column] = digest

        matrices.append(
            np.column_stack(target_predictions)
        )
        digests[regime_name] = target_digests

    if row_ids_reference is None:
        raise ValueError(
            "EXP-049 regime scoring produced no row identity"
        )

    directions, utility = (
        _regime_utility_direction_score(matrices)
    )
    diagnostics = _utility_diagnostics(
        directions=directions,
        utility=utility,
        regime_prediction_digests=digests,
    )
    consensus_digest = _utility_consensus_digest(
        row_ids=row_ids_reference,
        directions=directions,
        utility=utility,
    )
    return (
        directions,
        utility,
        diagnostics,
        row_ids_reference,
        consensus_digest,
    )


def _evaluate_temporal_stability(
    *,
    selection_frame: pl.DataFrame,
    directions: np.ndarray,
    utility: np.ndarray,
    cutoff: float,
    budget: int,
    cell: ModelCell,
    full_selection_candidate_count: int,
) -> dict[str, object]:
    if (
        len(directions) != selection_frame.height
        or len(utility) != selection_frame.height
    ):
        raise ValueError(
            "EXP-049 stability row mismatch"
        )

    windows: list[dict[str, object]] = []
    for raw_window in TEMPORAL_STABILITY_WINDOWS:
        window = dict(raw_window)
        start = _parse_utc_date(str(window["start"]))
        end_exclusive = _parse_utc_date(
            str(window["end_exclusive"])
        )
        indices = _window_indices(
            selection_frame,
            start=start,
            end_exclusive=end_exclusive,
        )
        window_frame = selection_frame[indices]
        index_array = np.asarray(
            indices,
            dtype=np.int64,
        )
        window_directions = directions[index_array]
        window_utility = utility[index_array]
        row_ids = _base._row_identity(
            window_frame,
            cell=cell,
        )
        evaluated = _evaluate_utility_cutoff(
            window_frame,
            directions=window_directions,
            utility=window_utility,
            cutoff=cutoff,
            budget=budget,
            scenarios=SELECTION_GATE_SCENARIOS,
            row_ids=row_ids,
        )
        scenario = evaluated["scenarios"]["0.5"]
        metrics = scenario["metrics"]
        gate = _window_gate(
            metrics,
            full_selection_candidate_count=(
                full_selection_candidate_count
            ),
        )
        windows.append(
            {
                "name": str(window["name"]),
                "start": str(window["start"]),
                "end_exclusive": str(
                    window["end_exclusive"]
                ),
                "row_count": window_frame.height,
                "metrics": metrics,
                "gate": gate,
            }
        )

    return {
        "status": (
            "PASS"
            if all(
                bool(window["gate"]["passed"])
                for window in windows
            )
            else "REJECT"
        ),
        "minimum_directional_candidate_share_per_window": (
            MIN_STABILITY_WINDOW_CANDIDATE_SHARE
        ),
        "windows": windows,
    }


def _selection_key(
    row: Mapping[str, object],
) -> tuple[float, int, int]:
    scenario = row["scenarios"]["0.5"]
    metrics = scenario["metrics"]
    return (
        float(metrics["total_net_pips"]),
        int(metrics["directional_candidate_count"]),
        -int(row["candidate_budget_anchor"]),
    )


def _evaluate_forward_split(
    *,
    fitted_models: Mapping[
        str,
        Mapping[str, _base.FittedMarketModel],
    ],
    frame: pl.DataFrame,
    cell: ModelCell,
    cutoff: float,
    budget: int,
    gate_scenarios: Sequence[float],
) -> dict[str, object]:
    (
        directions,
        utility,
        diagnostics,
        row_ids,
        consensus_digest,
    ) = _score_utility_consensus(
        fitted_models=fitted_models,
        frame=frame,
        cell=cell,
    )
    all_scenarios = tuple(
        sorted(
            {
                *(
                    float(value)
                    for value in DIAGNOSTIC_SCENARIOS
                ),
                *(
                    float(value)
                    for value in gate_scenarios
                ),
            }
        )
    )
    evaluated = _evaluate_utility_cutoff(
        frame,
        directions=directions,
        utility=utility,
        cutoff=cutoff,
        budget=budget,
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
        "regime_utility_consensus": diagnostics,
        "regime_utility_consensus_digest": (
            consensus_digest
        ),
        **evaluated,
    }


def run_regime_utility_model_cell_core(
    *,
    features: pl.DataFrame,
    outcomes: pl.DataFrame,
    cell: ModelCell,
) -> dict[str, object]:
    joined, processed_manifest_sha256 = (
        _base._validate_frames(
            features,
            outcomes,
            cell=cell,
        )
    )
    split_frames = {
        split.name: _base._split_frame(joined, split)
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
            "EXP-049 model cell has empty required "
            f"split(s): {empty}"
        )

    regime_frames = {
        split.name: _base._split_frame(
            joined,
            split,
        )
        for split in _fit_regime_splits()
    }
    if any(
        frame.is_empty()
        for frame in regime_frames.values()
    ):
        empty = [
            name
            for name, frame in regime_frames.items()
            if frame.is_empty()
        ]
        raise ValueError(
            "EXP-049 model cell has empty fit "
            f"regime(s): {empty}"
        )

    fitted_models: dict[
        str,
        dict[str, _base.FittedMarketModel],
    ] = {}
    fit_evidence: dict[str, object] = {}

    for regime_name, fit_frame in regime_frames.items():
        target_models: dict[
            str,
            _base.FittedMarketModel,
        ] = {}
        target_evidence: dict[str, object] = {}
        for target_column in FINANCIAL_TARGET_COLUMNS:
            fitted = _fit_regressor(
                fit_frame,
                target_column=target_column,
            )
            target_models[target_column] = fitted
            target_evidence[target_column] = {
                "status": "FITTED",
                "fit_attempt_count": 1,
                "target_summary": _target_summary(
                    fit_frame,
                    target_column=target_column,
                ),
                "preprocessor_fingerprint": (
                    fitted.preprocessor_fingerprint
                ),
                "model_fingerprint": (
                    fitted.model_fingerprint
                ),
            }

        fitted_models[regime_name] = target_models
        fit_evidence[regime_name] = {
            "status": "FITTED",
            "row_count": fit_frame.height,
            "regressor_count": len(target_models),
            "regressors": target_evidence,
        }

    selection_frame = split_frames[
        SELECTION_SPLIT.name
    ]
    (
        selection_directions,
        selection_utility,
        selection_diagnostics,
        selection_row_ids,
        selection_consensus_digest,
    ) = _score_utility_consensus(
        fitted_models=fitted_models,
        frame=selection_frame,
        cell=cell,
    )

    variants: list[dict[str, object]] = []
    for budget in CANDIDATE_BUDGET_ANCHORS:
        cutoff_record = _derive_utility_cutoff(
            directions=selection_directions,
            utility=selection_utility,
            row_ids=selection_row_ids,
            budget=budget,
        )
        if cutoff_record["status"] != "AVAILABLE":
            variants.append(
                {
                    "model_family": (
                        "hist_gradient_boosting_regression"
                    ),
                    "candidate_budget_anchor": budget,
                    "evaluation_status": (
                        "BUDGET_UNAVAILABLE"
                    ),
                    **cutoff_record,
                    "aggregate_selection_gate_passed": False,
                    "temporal_stability": {
                        "status": (
                            "BUDGET_UNAVAILABLE"
                        ),
                        "minimum_directional_candidate_share_per_window": (
                            MIN_STABILITY_WINDOW_CANDIDATE_SHARE
                        ),
                        "windows": [],
                    },
                    "selection_gate_passed": False,
                }
            )
            continue

        cutoff = float(
            cutoff_record[
                "selection_derived_cutoff"
            ]
        )
        evaluated = _evaluate_utility_cutoff(
            selection_frame,
            directions=selection_directions,
            utility=selection_utility,
            cutoff=cutoff,
            budget=budget,
            scenarios=SELECTION_GATE_SCENARIOS,
            row_ids=selection_row_ids,
        )
        scenario = evaluated["scenarios"]["0.5"]
        aggregate_passed = bool(
            scenario["gate"]["passed"]
        )
        full_count = int(
            scenario["metrics"][
                "directional_candidate_count"
            ]
        )

        if aggregate_passed:
            stability = _evaluate_temporal_stability(
                selection_frame=selection_frame,
                directions=selection_directions,
                utility=selection_utility,
                cutoff=cutoff,
                budget=budget,
                cell=cell,
                full_selection_candidate_count=full_count,
            )
            stability_passed = (
                stability["status"] == "PASS"
            )
        else:
            stability = {
                "status": "LOCKED_AGGREGATE_REJECT",
                "minimum_directional_candidate_share_per_window": (
                    MIN_STABILITY_WINDOW_CANDIDATE_SHARE
                ),
                "windows": [],
            }
            stability_passed = False

        variants.append(
            {
                "model_family": (
                    "hist_gradient_boosting_regression"
                ),
                "evaluation_status": "EVALUATED",
                **cutoff_record,
                **evaluated,
                "aggregate_selection_gate_passed": (
                    aggregate_passed
                ),
                "temporal_stability": stability,
                "selection_gate_passed": bool(
                    aggregate_passed
                    and stability_passed
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
        "experiment_id": REGIME_UTILITY_EXPERIMENT_ID,
        "training_core_version": (
            REGIME_UTILITY_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            REGIME_UTILITY_TRAINING_CORE_DECISION
        ),
        "dec132_merged_commit": DEC132_MERGED_COMMIT,
        "dec132_protocol_blob_sha": (
            DEC132_PROTOCOL_BLOB_SHA
        ),
        "base_training_core_blob_sha": (
            BASE_TRAINING_CORE_BLOB_SHA
        ),
        "density_helper_core_blob_sha": (
            DENSITY_HELPER_CORE_BLOB_SHA
        ),
        "protocol_decision": (
            REGIME_UTILITY_PROTOCOL_DECISION
        ),
        "protocol_version": (
            REGIME_UTILITY_PROTOCOL_VERSION
        ),
        "protocol_fingerprint": (
            regime_utility_protocol_fingerprint()
        ),
        "prior_result_informed": PRIOR_RESULT_INFORMED,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": UNTOUCHED_OOS,
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
            "regime_models": fit_evidence,
            "regime_model_count": len(
                fitted_models
            ),
            "regressor_count": sum(
                len(value)
                for value in fitted_models.values()
            ),
            "full_fit_single_model": {
                "status": "FORBIDDEN_BY_DEC132",
                "fit_attempt_count": 0,
            },
            "hist_gradient_boosting_classifier": {
                "status": "EXCLUDED_BY_DEC132",
                "fit_attempt_count": 0,
            },
            "logistic_regression": {
                "status": "EXCLUDED_BY_DEC112_DEC132",
                "fit_attempt_count": 0,
            },
        },
        "selection": {
            "status": (
                "SELECTED"
                if selected is not None
                else (
                    "NO_REGIME_UTILITY_"
                    "STABLE_MODEL_CHALLENGER"
                )
            ),
            "row_count": selection_frame.height,
            "regime_utility_consensus": (
                selection_diagnostics
            ),
            "regime_utility_consensus_digest": (
                selection_consensus_digest
            ),
            "variants": variants,
            "selected_variant": (
                {
                    "model_family": (
                        "hist_gradient_boosting_regression"
                    ),
                    "candidate_budget_anchor": int(
                        selected[
                            "candidate_budget_anchor"
                        ]
                    ),
                    "selection_derived_cutoff": float(
                        selected[
                            "selection_derived_cutoff"
                        ]
                    ),
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
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }

    if selected is None:
        result["result_fingerprint"] = _sha256(
            result
        )
        return result

    selected_cutoff = float(
        selected["selection_derived_cutoff"]
    )
    selected_budget = int(
        selected["candidate_budget_anchor"]
    )

    validation = _evaluate_forward_split(
        fitted_models=fitted_models,
        frame=split_frames[
            VALIDATION_SPLIT.name
        ],
        cell=cell,
        cutoff=selected_cutoff,
        budget=selected_budget,
        gate_scenarios=VALIDATION_GATE_SCENARIOS,
    )
    result["validation"] = validation

    if validation["status"] != "PASS":
        result["retrospective_holdout"] = {
            "status": "LOCKED_VALIDATION_REJECT",
        }
        result["result_fingerprint"] = _sha256(
            result
        )
        return result

    holdout = _evaluate_forward_split(
        fitted_models=fitted_models,
        frame=split_frames[
            RETROSPECTIVE_HOLDOUT_SPLIT.name
        ],
        cell=cell,
        cutoff=selected_cutoff,
        budget=selected_budget,
        gate_scenarios=HOLDOUT_GATE_SCENARIOS,
    )
    result["retrospective_holdout"] = holdout
    result["result_fingerprint"] = _sha256(result)
    return result


__all__ = [
    "BASE_TRAINING_CORE_BLOB_SHA",
    "BROKER_MUTATION_AUTHORIZED",
    "DEC132_MERGED_COMMIT",
    "DEC132_PROTOCOL_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "DENSITY_HELPER_CORE_BLOB_SHA",
    "LIVE_ORDER_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "REGIME_UTILITY_RESULT_EXECUTION_AUTHORIZED",
    "REGIME_UTILITY_TRAINING_CORE_DECISION",
    "REGIME_UTILITY_TRAINING_CORE_VERSION",
    "SHADOW_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "_candidate_directions",
    "_derive_utility_cutoff",
    "_fit_regime_splits",
    "_regime_utility_direction_score",
    "_selection_key",
    "run_regime_utility_model_cell_core",
    "validate_regime_utility_training_sources",
]
