from __future__ import annotations

import hashlib
from pathlib import Path
import struct
from typing import Mapping, Sequence

import numpy as np
import polars as pl

from . import model_training as _base
from .contracts import EVIDENCE_LABEL
from .model_protocol import (
    DIAGNOSTIC_SCENARIOS,
    HOLDOUT_GATE_SCENARIOS,
    PROTOCOL_SPLITS,
    RETROSPECTIVE_HOLDOUT_SPLIT,
    SELECTION_GATE_SCENARIOS,
    SELECTION_SPLIT,
    VALIDATION_GATE_SCENARIOS,
    VALIDATION_SPLIT,
    ModelCell,
)
from .model_successor_density_protocol import (
    CANDIDATE_BUDGET_ANCHORS,
)
from .model_successor_density_training import (
    _canonical_json,
    _git_blob_sha,
    _parse_utc_date,
    _window_gate,
    _window_indices,
)
from .model_successor_stability_protocol import (
    MIN_STABILITY_WINDOW_CANDIDATE_SHARE,
    TEMPORAL_STABILITY_WINDOWS,
)
from .model_successor_temporal_calibrated_utility_protocol import (
    CALIBRATED_PERCENTILE_RULE,
    CALIBRATION_REFERENCE_RULE,
    CUTOFF_TIE_POLICY,
    FINANCIAL_TARGET_COLUMNS,
    FORWARD_APPLICATION_RULE,
    PRIOR_RESULT_INFORMED,
    ROBUST_CALIBRATED_SCORE_RULE,
    SELECTION_CUTOFF_RULE,
    TEMPORAL_CALIBRATED_UTILITY_EXPERIMENT_ID,
    TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_DECISION,
    TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_VERSION,
    UNTOUCHED_OOS,
    temporal_calibrated_utility_protocol_fingerprint,
)
from .model_successor_temporal_jackknife_utility_protocol import (
    PREDECESSOR_REGIME_NAMES,
)
from .model_successor_temporal_jackknife_utility_training import (
    MODEL_FIT_AUTHORIZED as PREDECESSOR_MODEL_FIT_AUTHORIZED,
    TEMPORAL_JACKKNIFE_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_DECISION,
    TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_VERSION,
    _build_jackknife_view_frames,
    _jackknife_view_regime_names,
    _predecessor_fit_regime_splits,
    _predecessor_fit_regressor,
    _predecessor_score_regressor,
    _predecessor_target_summary,
    _selection_key,
    _temporal_jackknife_utility_direction_score,
    validate_temporal_jackknife_utility_training_sources,
)


TEMPORAL_CALIBRATED_UTILITY_TRAINING_CORE_VERSION = (
    "fmp-exp051-temporal-calibrated-utility-training-core-v1"
)
TEMPORAL_CALIBRATED_UTILITY_TRAINING_CORE_DECISION = "DEC-151"

DEC150_MERGED_COMMIT = (
    "b80a1f688afe8f5056aa31c1a2ff5b4ebbc11833"
)
DEC150_PROTOCOL_BLOB_SHA = (
    "c39309c4115cae1ea058e56f30cae4af6407e36e"
)
PREDECESSOR_TRAINING_CORE_BLOB_SHA = (
    "ec97a9941af052d6e223e4bafab9a9989ec57ff0"
)

TEMPORAL_CALIBRATED_UTILITY_RESULT_EXECUTION_AUTHORIZED = False
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


def validate_temporal_calibrated_utility_training_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "dec150_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_temporal_calibrated_utility_protocol.py",
            DEC150_PROTOCOL_BLOB_SHA,
        ),
        "predecessor_training_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_temporal_jackknife_utility_training.py",
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(
                f"missing EXP-051 training dependency: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-051 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    predecessor = validate_temporal_jackknife_utility_training_sources(
        repository_root=root,
    )
    if predecessor[
        "temporal_jackknife_utility_training_core_decision"
    ] != TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_DECISION:
        raise ValueError(
            "EXP-051 predecessor training decision drift"
        )
    if predecessor["model_fit_authorized"] is not False:
        raise ValueError(
            "EXP-051 predecessor model fit must remain closed"
        )
    if predecessor[
        "temporal_jackknife_utility_result_execution_authorized"
    ] is not False:
        raise ValueError(
            "EXP-051 predecessor result execution must remain closed"
        )
    if PREDECESSOR_MODEL_FIT_AUTHORIZED is not False:
        raise ValueError(
            "EXP-051 predecessor source fit authorization drift"
        )
    if (
        TEMPORAL_JACKKNIFE_UTILITY_RESULT_EXECUTION_AUTHORIZED
        is not False
    ):
        raise ValueError(
            "EXP-051 predecessor source execution authorization drift"
        )

    protocol_fingerprint = (
        temporal_calibrated_utility_protocol_fingerprint()
    )
    if len(protocol_fingerprint) != 64:
        raise ValueError(
            "EXP-051 calibrated-utility protocol fingerprint is invalid"
        )

    return {
        "temporal_calibrated_utility_training_core_version": (
            TEMPORAL_CALIBRATED_UTILITY_TRAINING_CORE_VERSION
        ),
        "temporal_calibrated_utility_training_core_decision": (
            TEMPORAL_CALIBRATED_UTILITY_TRAINING_CORE_DECISION
        ),
        "dec150_merged_commit": DEC150_MERGED_COMMIT,
        "dec150_protocol_blob_sha": actual[
            "dec150_protocol"
        ],
        "predecessor_training_core_blob_sha": actual[
            "predecessor_training_core"
        ],
        "predecessor_training_core_decision": (
            TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_DECISION
        ),
        "predecessor_training_core_version": (
            TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_VERSION
        ),
        "temporal_calibrated_utility_protocol_fingerprint": (
            protocol_fingerprint
        ),
        "temporal_calibrated_utility_result_execution_authorized": (
            False
        ),
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
    }


def _reference_digest(values: np.ndarray) -> str:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1 or array.size == 0:
        raise ValueError(
            "EXP-051 calibration reference must be non-empty 1D"
        )
    if not np.isfinite(array).all():
        raise ValueError(
            "EXP-051 calibration reference must be finite"
        )
    if np.any(array[1:] < array[:-1]):
        raise ValueError(
            "EXP-051 calibration reference must be sorted"
        )

    digest = hashlib.sha256()
    digest.update(
        int(array.size).to_bytes(8, "big", signed=False)
    )
    for value in array.tolist():
        digest.update(struct.pack(">d", float(value)))
    return digest.hexdigest()


def _empirical_percentiles(
    reference: np.ndarray,
    values: np.ndarray,
) -> np.ndarray:
    reference_array = np.asarray(
        reference,
        dtype=np.float64,
    )
    scored = np.asarray(
        values,
        dtype=np.float64,
    )
    if (
        reference_array.ndim != 1
        or reference_array.size == 0
    ):
        raise ValueError(
            "EXP-051 empirical CDF reference must be non-empty 1D"
        )
    if scored.ndim != 1:
        raise ValueError(
            "EXP-051 empirical CDF values must be 1D"
        )
    if (
        not np.isfinite(reference_array).all()
        or not np.isfinite(scored).all()
    ):
        raise ValueError(
            "EXP-051 empirical CDF inputs must be finite"
        )
    if np.any(
        reference_array[1:] < reference_array[:-1]
    ):
        raise ValueError(
            "EXP-051 empirical CDF reference must be sorted"
        )

    ranks = np.searchsorted(
        reference_array,
        scored,
        side="right",
    ).astype(np.float64)
    return ranks / float(reference_array.size)


def _build_calibration_references(
    *,
    fitted_models: Mapping[
        str,
        Mapping[str, _base.FittedMarketModel],
    ],
    regime_frames: Mapping[str, pl.DataFrame],
    cell: ModelCell,
) -> tuple[
    dict[str, dict[str, np.ndarray]],
    dict[str, object],
]:
    view_regimes = _jackknife_view_regime_names()
    if set(fitted_models) != set(view_regimes):
        raise ValueError(
            "EXP-051 fitted jackknife model set mismatch"
        )
    if set(regime_frames) != set(PREDECESSOR_REGIME_NAMES):
        raise ValueError(
            "EXP-051 calibration regime frame set mismatch"
        )

    references: dict[
        str,
        dict[str, np.ndarray],
    ] = {}
    evidence: dict[str, object] = {}

    for view_name, included in view_regimes.items():
        excluded = tuple(
            regime
            for regime in PREDECESSOR_REGIME_NAMES
            if regime not in included
        )
        if len(excluded) != 1:
            raise ValueError(
                "EXP-051 calibration excluded-regime count drift"
            )
        excluded_name = excluded[0]
        frame = regime_frames[excluded_name]
        if frame.is_empty():
            raise ValueError(
                "EXP-051 calibration excluded regime is empty"
            )

        target_models = fitted_models[view_name]
        if set(target_models) != set(FINANCIAL_TARGET_COLUMNS):
            raise ValueError(
                "EXP-051 calibration target model set mismatch"
            )

        target_references: dict[str, np.ndarray] = {}
        target_evidence: dict[str, object] = {}
        row_ids_reference: tuple[str, ...] | None = None

        for target_column in FINANCIAL_TARGET_COLUMNS:
            predictions, prediction_digest, row_ids = (
                _predecessor_score_regressor(
                    target_models[target_column],
                    frame,
                    cell=cell,
                )
            )
            if row_ids_reference is None:
                row_ids_reference = tuple(row_ids)
            elif tuple(row_ids) != row_ids_reference:
                raise ValueError(
                    "EXP-051 calibration row identity mismatch"
                )

            sorted_reference = np.sort(
                np.asarray(
                    predictions,
                    dtype=np.float64,
                )
            )
            if sorted_reference.size == 0:
                raise ValueError(
                    "EXP-051 calibration reference is empty"
                )
            if not np.isfinite(sorted_reference).all():
                raise ValueError(
                    "EXP-051 calibration reference is non-finite"
                )

            target_references[target_column] = (
                sorted_reference
            )
            target_evidence[target_column] = {
                "status": "FROZEN",
                "excluded_regime": excluded_name,
                "row_count": int(
                    sorted_reference.size
                ),
                "minimum_prediction": float(
                    sorted_reference[0]
                ),
                "maximum_prediction": float(
                    sorted_reference[-1]
                ),
                "mean_prediction": float(
                    sorted_reference.mean()
                ),
                "row_bound_prediction_digest": (
                    prediction_digest
                ),
                "sorted_reference_digest": (
                    _reference_digest(
                        sorted_reference
                    )
                ),
            }

        references[view_name] = target_references
        evidence[view_name] = {
            "status": "FROZEN",
            "included_regimes": list(included),
            "excluded_regime": excluded_name,
            "row_count": frame.height,
            "target_count": len(target_references),
            "targets": target_evidence,
        }

    return references, evidence


def _score_raw_view_matrices(
    *,
    fitted_models: Mapping[
        str,
        Mapping[str, _base.FittedMarketModel],
    ],
    frame: pl.DataFrame,
    cell: ModelCell,
) -> tuple[
    tuple[str, ...],
    list[np.ndarray],
    dict[str, dict[str, str]],
    tuple[str, ...],
]:
    view_names = tuple(
        _jackknife_view_regime_names()
    )
    if set(fitted_models) != set(view_names):
        raise ValueError(
            "EXP-051 fitted jackknife model set mismatch"
        )

    matrices: list[np.ndarray] = []
    digests: dict[str, dict[str, str]] = {}
    row_ids_reference: tuple[str, ...] | None = None

    for view_name in view_names:
        target_models = fitted_models[view_name]
        if set(target_models) != set(
            FINANCIAL_TARGET_COLUMNS
        ):
            raise ValueError(
                "EXP-051 fitted target model set mismatch"
            )

        target_predictions: list[np.ndarray] = []
        target_digests: dict[str, str] = {}
        for target_column in FINANCIAL_TARGET_COLUMNS:
            predictions, digest, row_ids = (
                _predecessor_score_regressor(
                    target_models[target_column],
                    frame,
                    cell=cell,
                )
            )
            if row_ids_reference is None:
                row_ids_reference = tuple(row_ids)
            elif tuple(row_ids) != row_ids_reference:
                raise ValueError(
                    "EXP-051 score row identity mismatch"
                )
            target_predictions.append(
                np.asarray(
                    predictions,
                    dtype=np.float64,
                )
            )
            target_digests[target_column] = digest

        matrices.append(
            np.column_stack(target_predictions)
        )
        digests[view_name] = target_digests

    if row_ids_reference is None:
        raise ValueError(
            "EXP-051 scoring produced no row identity"
        )

    return (
        view_names,
        matrices,
        digests,
        row_ids_reference,
    )


def _calibrated_consensus_digest(
    *,
    row_ids: Sequence[str],
    directions: np.ndarray,
    raw_utility: np.ndarray,
    calibrated_utility: np.ndarray,
) -> str:
    if (
        len(row_ids) != len(directions)
        or len(row_ids) != len(raw_utility)
        or len(row_ids) != len(calibrated_utility)
    ):
        raise ValueError(
            "EXP-051 calibrated consensus digest row mismatch"
        )

    digest = hashlib.sha256()
    for row_id, direction, raw_value, calibrated_value in zip(
        row_ids,
        directions.tolist(),
        raw_utility.tolist(),
        calibrated_utility.tolist(),
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
            digest.update(
                struct.pack(">d", float(raw_value))
            )
            digest.update(
                struct.pack(
                    ">d",
                    float(calibrated_value),
                )
            )
        else:
            digest.update(b"NO_CALIBRATED_UTILITY")

    return digest.hexdigest()


def _calibrated_utility_diagnostics(
    *,
    directions: np.ndarray,
    raw_utility: np.ndarray,
    calibrated_utility: np.ndarray,
    view_prediction_digests: Mapping[
        str,
        Mapping[str, str],
    ],
) -> dict[str, object]:
    if (
        len(directions) != len(raw_utility)
        or len(directions) != len(calibrated_utility)
    ):
        raise ValueError(
            "EXP-051 calibrated diagnostic row mismatch"
        )

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
    finite_raw = [
        float(value)
        for direction, value in zip(
            directions.tolist(),
            raw_utility.tolist(),
            strict=True,
        )
        if direction in {"LONG", "SHORT"}
    ]
    finite_calibrated = [
        float(value)
        for direction, value in zip(
            directions.tolist(),
            calibrated_utility.tolist(),
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
        "minimum_robust_raw_utility": (
            min(finite_raw) if finite_raw else None
        ),
        "maximum_robust_raw_utility": (
            max(finite_raw) if finite_raw else None
        ),
        "minimum_robust_calibrated_utility": (
            min(finite_calibrated)
            if finite_calibrated
            else None
        ),
        "maximum_robust_calibrated_utility": (
            max(finite_calibrated)
            if finite_calibrated
            else None
        ),
        "view_prediction_digests": {
            view: dict(values)
            for view, values in (
                view_prediction_digests.items()
            )
        },
    }


def _score_temporal_calibrated_utility_consensus(
    *,
    fitted_models: Mapping[
        str,
        Mapping[str, _base.FittedMarketModel],
    ],
    calibration_references: Mapping[
        str,
        Mapping[str, np.ndarray],
    ],
    frame: pl.DataFrame,
    cell: ModelCell,
) -> tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    dict[str, object],
    tuple[str, ...],
    str,
]:
    (
        view_names,
        raw_matrices,
        digests,
        row_ids,
    ) = _score_raw_view_matrices(
        fitted_models=fitted_models,
        frame=frame,
        cell=cell,
    )

    if set(calibration_references) != set(view_names):
        raise ValueError(
            "EXP-051 calibration reference view set mismatch"
        )

    directions, raw_utility = (
        _temporal_jackknife_utility_direction_score(
            raw_matrices
        )
    )

    calibrated_matrices: list[np.ndarray] = []
    for view_name, raw_matrix in zip(
        view_names,
        raw_matrices,
        strict=True,
    ):
        target_references = calibration_references[
            view_name
        ]
        if set(target_references) != set(
            FINANCIAL_TARGET_COLUMNS
        ):
            raise ValueError(
                "EXP-051 calibration target reference set mismatch"
            )

        calibrated_columns = [
            _empirical_percentiles(
                target_references[target_column],
                raw_matrix[:, target_index],
            )
            for target_index, target_column in enumerate(
                FINANCIAL_TARGET_COLUMNS
            )
        ]
        calibrated_matrices.append(
            np.column_stack(calibrated_columns)
        )

    calibrated_utility = np.full(
        len(directions),
        float("-inf"),
        dtype=np.float64,
    )
    for direction, target_index in (
        ("LONG", 0),
        ("SHORT", 1),
    ):
        mask = directions == direction
        if not bool(mask.any()):
            continue
        selected = np.column_stack(
            [
                matrix[mask, target_index]
                for matrix in calibrated_matrices
            ]
        )
        calibrated_utility[mask] = np.min(
            selected,
            axis=1,
        )

    eligible_mask = np.isin(
        directions,
        np.asarray(["LONG", "SHORT"], dtype=object),
    )
    if bool(eligible_mask.any()):
        eligible_calibrated = calibrated_utility[
            eligible_mask
        ]
        if not np.isfinite(eligible_calibrated).all():
            raise ValueError(
                "EXP-051 eligible calibrated utility must be finite"
            )
        if (
            (eligible_calibrated < 0.0).any()
            or (eligible_calibrated > 1.0).any()
        ):
            raise ValueError(
                "EXP-051 calibrated utility percentile out of range"
            )

    diagnostics = _calibrated_utility_diagnostics(
        directions=directions,
        raw_utility=raw_utility,
        calibrated_utility=calibrated_utility,
        view_prediction_digests=digests,
    )
    consensus_digest = _calibrated_consensus_digest(
        row_ids=row_ids,
        directions=directions,
        raw_utility=raw_utility,
        calibrated_utility=calibrated_utility,
    )
    return (
        directions,
        raw_utility,
        calibrated_utility,
        diagnostics,
        row_ids,
        consensus_digest,
    )


def _derive_calibrated_cutoff(
    *,
    directions: np.ndarray,
    raw_utility: np.ndarray,
    calibrated_utility: np.ndarray,
    row_ids: Sequence[str],
    budget: int,
) -> dict[str, object]:
    if budget not in CANDIDATE_BUDGET_ANCHORS:
        raise ValueError(
            "unsupported EXP-051 candidate budget"
        )
    if (
        len(row_ids) != len(directions)
        or len(row_ids) != len(raw_utility)
        or len(row_ids) != len(calibrated_utility)
    ):
        raise ValueError(
            "EXP-051 calibrated cutoff row mismatch"
        )

    eligible = [
        index
        for index, direction in enumerate(
            directions.tolist()
        )
        if direction in {"LONG", "SHORT"}
    ]
    for index in eligible:
        raw_value = float(raw_utility[index])
        calibrated_value = float(
            calibrated_utility[index]
        )
        if (
            not np.isfinite(raw_value)
            or raw_value <= 0.0
        ):
            raise ValueError(
                "EXP-051 directional raw utility must be "
                "finite and positive"
            )
        if (
            not np.isfinite(calibrated_value)
            or calibrated_value < 0.0
            or calibrated_value > 1.0
        ):
            raise ValueError(
                "EXP-051 calibrated utility must be finite "
                "and within [0, 1]"
            )

    if len(eligible) < budget:
        return {
            "status": (
                "UNAVAILABLE_INSUFFICIENT_UTILITY_ROWS"
            ),
            "candidate_budget_anchor": budget,
            "eligible_utility_row_count": len(eligible),
            "selection_derived_calibrated_cutoff": None,
            "selection_derived_raw_cutoff": None,
        }

    ranked = sorted(
        eligible,
        key=lambda index: (
            -float(calibrated_utility[index]),
            -float(raw_utility[index]),
            str(row_ids[index]),
        ),
    )
    cutoff_index = ranked[budget - 1]
    calibrated_cutoff = float(
        calibrated_utility[cutoff_index]
    )
    raw_cutoff = float(raw_utility[cutoff_index])

    selected_count = sum(
        1
        for index in eligible
        if (
            float(calibrated_utility[index])
            > calibrated_cutoff
            or (
                float(calibrated_utility[index])
                == calibrated_cutoff
                and float(raw_utility[index])
                >= raw_cutoff
            )
        )
    )
    return {
        "status": "AVAILABLE",
        "candidate_budget_anchor": budget,
        "eligible_utility_row_count": len(eligible),
        "selection_derived_calibrated_cutoff": (
            calibrated_cutoff
        ),
        "selection_derived_raw_cutoff": raw_cutoff,
        "selection_candidate_count_at_cutoff": (
            selected_count
        ),
    }


def _candidate_directions_calibrated(
    *,
    directions: np.ndarray,
    raw_utility: np.ndarray,
    calibrated_utility: np.ndarray,
    calibrated_cutoff: float,
    raw_cutoff: float,
) -> np.ndarray:
    if (
        not np.isfinite(calibrated_cutoff)
        or calibrated_cutoff < 0.0
        or calibrated_cutoff > 1.0
    ):
        raise ValueError(
            "EXP-051 calibrated cutoff is invalid"
        )
    if (
        not np.isfinite(raw_cutoff)
        or raw_cutoff <= 0.0
    ):
        raise ValueError(
            "EXP-051 raw cutoff is invalid"
        )
    if (
        len(directions) != len(raw_utility)
        or len(directions) != len(calibrated_utility)
    ):
        raise ValueError(
            "EXP-051 candidate row mismatch"
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

        raw_value = float(raw_utility[index])
        calibrated_value = float(
            calibrated_utility[index]
        )
        if (
            not np.isfinite(raw_value)
            or raw_value <= 0.0
        ):
            raise ValueError(
                "EXP-051 directional raw utility must be "
                "finite and positive"
            )
        if (
            not np.isfinite(calibrated_value)
            or calibrated_value < 0.0
            or calibrated_value > 1.0
        ):
            raise ValueError(
                "EXP-051 directional calibrated utility is invalid"
            )
        if (
            calibrated_value > calibrated_cutoff
            or (
                calibrated_value == calibrated_cutoff
                and raw_value >= raw_cutoff
            )
        ):
            out[index] = direction
    return out


def _evaluate_calibrated_cutoff(
    frame: pl.DataFrame,
    *,
    directions: np.ndarray,
    raw_utility: np.ndarray,
    calibrated_utility: np.ndarray,
    calibrated_cutoff: float,
    raw_cutoff: float,
    budget: int,
    scenarios: Sequence[float],
    row_ids: Sequence[str],
) -> dict[str, object]:
    candidates = _candidate_directions_calibrated(
        directions=directions,
        raw_utility=raw_utility,
        calibrated_utility=calibrated_utility,
        calibrated_cutoff=calibrated_cutoff,
        raw_cutoff=raw_cutoff,
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
        "selection_derived_calibrated_cutoff": (
            calibrated_cutoff
        ),
        "selection_derived_raw_cutoff": raw_cutoff,
        "scenarios": scenario_results,
    }


def _evaluate_temporal_stability_calibrated(
    *,
    selection_frame: pl.DataFrame,
    directions: np.ndarray,
    raw_utility: np.ndarray,
    calibrated_utility: np.ndarray,
    calibrated_cutoff: float,
    raw_cutoff: float,
    budget: int,
    cell: ModelCell,
    full_selection_candidate_count: int,
) -> dict[str, object]:
    if (
        len(directions) != selection_frame.height
        or len(raw_utility) != selection_frame.height
        or len(calibrated_utility) != selection_frame.height
    ):
        raise ValueError(
            "EXP-051 stability row mismatch"
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
        window_raw = raw_utility[index_array]
        window_calibrated = calibrated_utility[
            index_array
        ]
        row_ids = _base._row_identity(
            window_frame,
            cell=cell,
        )
        evaluated = _evaluate_calibrated_cutoff(
            window_frame,
            directions=window_directions,
            raw_utility=window_raw,
            calibrated_utility=window_calibrated,
            calibrated_cutoff=calibrated_cutoff,
            raw_cutoff=raw_cutoff,
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


def _evaluate_forward_split(
    *,
    fitted_models: Mapping[
        str,
        Mapping[str, _base.FittedMarketModel],
    ],
    calibration_references: Mapping[
        str,
        Mapping[str, np.ndarray],
    ],
    frame: pl.DataFrame,
    cell: ModelCell,
    calibrated_cutoff: float,
    raw_cutoff: float,
    budget: int,
    gate_scenarios: Sequence[float],
) -> dict[str, object]:
    (
        directions,
        raw_utility,
        calibrated_utility,
        diagnostics,
        row_ids,
        consensus_digest,
    ) = _score_temporal_calibrated_utility_consensus(
        fitted_models=fitted_models,
        calibration_references=calibration_references,
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
    evaluated = _evaluate_calibrated_cutoff(
        frame,
        directions=directions,
        raw_utility=raw_utility,
        calibrated_utility=calibrated_utility,
        calibrated_cutoff=calibrated_cutoff,
        raw_cutoff=raw_cutoff,
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
        "temporal_calibrated_utility_consensus": (
            diagnostics
        ),
        "temporal_calibrated_utility_consensus_digest": (
            consensus_digest
        ),
        **evaluated,
    }


def run_temporal_calibrated_utility_model_cell_core(
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
            "EXP-051 model cell has empty required "
            f"split(s): {empty}"
        )

    regime_frames = {
        split.name: _base._split_frame(
            joined,
            split,
        )
        for split in _predecessor_fit_regime_splits()
    }
    if set(regime_frames) != set(PREDECESSOR_REGIME_NAMES):
        raise ValueError(
            "EXP-051 predecessor fit-regime identity drift"
        )
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
            "EXP-051 model cell has empty fit regime(s): "
            f"{empty}"
        )

    view_frames = _build_jackknife_view_frames(
        regime_frames
    )
    fitted_models: dict[
        str,
        dict[str, _base.FittedMarketModel],
    ] = {}
    fit_evidence: dict[str, object] = {}
    view_regimes = _jackknife_view_regime_names()

    for view_name, fit_frame in view_frames.items():
        target_models: dict[
            str,
            _base.FittedMarketModel,
        ] = {}
        target_evidence: dict[str, object] = {}
        for target_column in FINANCIAL_TARGET_COLUMNS:
            fitted = _predecessor_fit_regressor(
                fit_frame,
                target_column=target_column,
            )
            target_models[target_column] = fitted
            target_evidence[target_column] = {
                "status": "FITTED",
                "fit_attempt_count": 1,
                "target_summary": (
                    _predecessor_target_summary(
                        fit_frame,
                        target_column=target_column,
                    )
                ),
                "preprocessor_fingerprint": (
                    fitted.preprocessor_fingerprint
                ),
                "model_fingerprint": (
                    fitted.model_fingerprint
                ),
            }

        included = view_regimes[view_name]
        excluded = tuple(
            value
            for value in PREDECESSOR_REGIME_NAMES
            if value not in included
        )
        if len(excluded) != 1:
            raise ValueError(
                "EXP-051 jackknife excluded-regime count drift"
            )
        fitted_models[view_name] = target_models
        fit_evidence[view_name] = {
            "status": "FITTED",
            "included_regimes": list(included),
            "excluded_regime": excluded[0],
            "row_count": fit_frame.height,
            "regressor_count": len(target_models),
            "regressors": target_evidence,
        }

    (
        calibration_references,
        calibration_evidence,
    ) = _build_calibration_references(
        fitted_models=fitted_models,
        regime_frames=regime_frames,
        cell=cell,
    )

    selection_frame = split_frames[
        SELECTION_SPLIT.name
    ]
    (
        selection_directions,
        selection_raw_utility,
        selection_calibrated_utility,
        selection_diagnostics,
        selection_row_ids,
        selection_consensus_digest,
    ) = _score_temporal_calibrated_utility_consensus(
        fitted_models=fitted_models,
        calibration_references=calibration_references,
        frame=selection_frame,
        cell=cell,
    )

    variants: list[dict[str, object]] = []
    for budget in CANDIDATE_BUDGET_ANCHORS:
        cutoff_record = _derive_calibrated_cutoff(
            directions=selection_directions,
            raw_utility=selection_raw_utility,
            calibrated_utility=(
                selection_calibrated_utility
            ),
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

        calibrated_cutoff = float(
            cutoff_record[
                "selection_derived_calibrated_cutoff"
            ]
        )
        raw_cutoff = float(
            cutoff_record[
                "selection_derived_raw_cutoff"
            ]
        )
        evaluated = _evaluate_calibrated_cutoff(
            selection_frame,
            directions=selection_directions,
            raw_utility=selection_raw_utility,
            calibrated_utility=(
                selection_calibrated_utility
            ),
            calibrated_cutoff=calibrated_cutoff,
            raw_cutoff=raw_cutoff,
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
            stability = (
                _evaluate_temporal_stability_calibrated(
                    selection_frame=selection_frame,
                    directions=selection_directions,
                    raw_utility=selection_raw_utility,
                    calibrated_utility=(
                        selection_calibrated_utility
                    ),
                    calibrated_cutoff=calibrated_cutoff,
                    raw_cutoff=raw_cutoff,
                    budget=budget,
                    cell=cell,
                    full_selection_candidate_count=(
                        full_count
                    ),
                )
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
        "experiment_id": (
            TEMPORAL_CALIBRATED_UTILITY_EXPERIMENT_ID
        ),
        "training_core_version": (
            TEMPORAL_CALIBRATED_UTILITY_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            TEMPORAL_CALIBRATED_UTILITY_TRAINING_CORE_DECISION
        ),
        "dec150_merged_commit": DEC150_MERGED_COMMIT,
        "dec150_protocol_blob_sha": (
            DEC150_PROTOCOL_BLOB_SHA
        ),
        "predecessor_training_core_blob_sha": (
            PREDECESSOR_TRAINING_CORE_BLOB_SHA
        ),
        "predecessor_training_core_decision": (
            TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_DECISION
        ),
        "protocol_decision": (
            TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_DECISION
        ),
        "protocol_version": (
            TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_VERSION
        ),
        "protocol_fingerprint": (
            temporal_calibrated_utility_protocol_fingerprint()
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
            "jackknife_models": fit_evidence,
            "jackknife_view_count": len(
                fitted_models
            ),
            "regressor_count": sum(
                len(value)
                for value in fitted_models.values()
            ),
            "out_of_fit_calibration_references": (
                calibration_evidence
            ),
            "calibration_reference_count": sum(
                len(value)
                for value in calibration_references.values()
            ),
            "calibration_reference_rule": (
                CALIBRATION_REFERENCE_RULE
            ),
            "calibrated_percentile_rule": (
                CALIBRATED_PERCENTILE_RULE
            ),
            "robust_calibrated_score_rule": (
                ROBUST_CALIBRATED_SCORE_RULE
            ),
            "full_fit_single_model": {
                "status": "FORBIDDEN_BY_DEC150",
                "fit_attempt_count": 0,
            },
            "view_weight_search": {
                "status": "FORBIDDEN_BY_DEC150",
                "fit_attempt_count": 0,
            },
            "view_fallback": {
                "status": "FORBIDDEN_BY_DEC150",
                "fit_attempt_count": 0,
            },
            "selection_window_calibration": {
                "status": "FORBIDDEN_BY_DEC150",
                "fit_attempt_count": 0,
            },
            "hist_gradient_boosting_classifier": {
                "status": "EXCLUDED_BY_DEC150",
                "fit_attempt_count": 0,
            },
            "logistic_regression": {
                "status": "EXCLUDED_BY_DEC112_DEC150",
                "fit_attempt_count": 0,
            },
        },
        "selection": {
            "status": (
                "SELECTED"
                if selected is not None
                else (
                    "NO_TEMPORAL_CALIBRATED_UTILITY_"
                    "STABLE_MODEL_CHALLENGER"
                )
            ),
            "row_count": selection_frame.height,
            "temporal_calibrated_utility_consensus": (
                selection_diagnostics
            ),
            "temporal_calibrated_utility_consensus_digest": (
                selection_consensus_digest
            ),
            "selection_cutoff_rule": SELECTION_CUTOFF_RULE,
            "cutoff_tie_policy": CUTOFF_TIE_POLICY,
            "forward_application_rule": (
                FORWARD_APPLICATION_RULE
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
                    "selection_derived_calibrated_cutoff": float(
                        selected[
                            "selection_derived_calibrated_cutoff"
                        ]
                    ),
                    "selection_derived_raw_cutoff": float(
                        selected[
                            "selection_derived_raw_cutoff"
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

    selected_calibrated_cutoff = float(
        selected[
            "selection_derived_calibrated_cutoff"
        ]
    )
    selected_raw_cutoff = float(
        selected[
            "selection_derived_raw_cutoff"
        ]
    )
    selected_budget = int(
        selected["candidate_budget_anchor"]
    )

    validation = _evaluate_forward_split(
        fitted_models=fitted_models,
        calibration_references=calibration_references,
        frame=split_frames[
            VALIDATION_SPLIT.name
        ],
        cell=cell,
        calibrated_cutoff=selected_calibrated_cutoff,
        raw_cutoff=selected_raw_cutoff,
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
        calibration_references=calibration_references,
        frame=split_frames[
            RETROSPECTIVE_HOLDOUT_SPLIT.name
        ],
        cell=cell,
        calibrated_cutoff=selected_calibrated_cutoff,
        raw_cutoff=selected_raw_cutoff,
        budget=selected_budget,
        gate_scenarios=HOLDOUT_GATE_SCENARIOS,
    )
    result["retrospective_holdout"] = holdout
    result["result_fingerprint"] = _sha256(result)
    return result


__all__ = [
    "BROKER_MUTATION_AUTHORIZED",
    "DEC150_MERGED_COMMIT",
    "DEC150_PROTOCOL_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "LIVE_ORDER_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "PREDECESSOR_TRAINING_CORE_BLOB_SHA",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "TEMPORAL_CALIBRATED_UTILITY_RESULT_EXECUTION_AUTHORIZED",
    "TEMPORAL_CALIBRATED_UTILITY_TRAINING_CORE_DECISION",
    "TEMPORAL_CALIBRATED_UTILITY_TRAINING_CORE_VERSION",
    "TRADING_AUTHORIZED",
    "_build_calibration_references",
    "_candidate_directions_calibrated",
    "_derive_calibrated_cutoff",
    "_empirical_percentiles",
    "_evaluate_temporal_stability_calibrated",
    "_reference_digest",
    "_score_temporal_calibrated_utility_consensus",
    "run_temporal_calibrated_utility_model_cell_core",
    "validate_temporal_calibrated_utility_training_sources",
]
