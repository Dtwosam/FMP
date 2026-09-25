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
from .model_successor_density_protocol import CANDIDATE_BUDGET_ANCHORS
from .model_successor_density_training import (
    _canonical_json,
    _git_blob_sha,
    _parse_utc_date,
    _window_gate,
    _window_indices,
)
from .model_successor_fit_temporal_feature_support_utility_protocol import (
    FIT_TEMPORAL_FEATURE_DISTANCE_RULE,
    FIT_TEMPORAL_FEATURE_REFERENCE_RULE,
    FIT_TEMPORAL_FEATURE_SUPPORT_PERCENTILE_RULE,
    FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL,
    ROBUST_FIT_TEMPORAL_FEATURE_SUPPORT_SCORE_RULE,
)
from .model_successor_fit_temporal_feature_support_utility_training import (
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_DECISION,
    MODEL_FIT_AUTHORIZED as PREDECESSOR_MODEL_FIT_AUTHORIZED,
    _build_fit_temporal_feature_support_references,
    _score_fit_temporal_feature_support_consensus,
    validate_fit_temporal_feature_support_utility_training_sources,
)
from .model_successor_fit_temporal_residual_bound_utility_protocol import (
    CUTOFF_TIE_POLICY,
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_PROTOCOL_VERSION,
    FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL,
    FIT_TEMPORAL_RESIDUAL_REFERENCE_RULE,
    FORWARD_APPLICATION_RULE,
    PRIOR_RESULT_INFORMED,
    RANKING_RULE,
    RESIDUAL_BOUND_ELIGIBILITY_RULE,
    RESIDUAL_DOWNSIDE_QUANTILE,
    RESIDUAL_DOWNSIDE_QUANTILE_RULE,
    RESIDUAL_REFERENCE_WINDOWS_PER_VIEW,
    ROBUST_RESIDUAL_BOUND_UTILITY_RULE,
    SELECTION_CUTOFF_RULE,
    UNTOUCHED_OOS,
    fit_temporal_residual_bound_utility_protocol_fingerprint,
)
from .model_successor_fit_temporal_support_utility_protocol import (
    FIT_TEMPORAL_SUPPORT_PERCENTILE_RULE,
    FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL,
    FIT_TEMPORAL_SUPPORT_REFERENCE_RULE,
    FIT_TEMPORAL_SUPPORT_WINDOWS,
    ROBUST_FIT_TEMPORAL_SUPPORT_SCORE_RULE,
)
from .model_successor_fit_temporal_support_utility_training import (
    _build_fit_temporal_support_references,
)
from .model_successor_regime_utility_training import _selection_key
from .model_successor_stability_protocol import (
    MIN_STABILITY_WINDOW_CANDIDATE_SHARE,
    TEMPORAL_STABILITY_WINDOWS,
)
from .model_successor_temporal_calibrated_utility_protocol import (
    CALIBRATED_PERCENTILE_RULE,
    CALIBRATION_REFERENCE_RULE,
    FINANCIAL_TARGET_COLUMNS,
    ROBUST_CALIBRATED_SCORE_RULE,
)
from .model_successor_temporal_calibrated_utility_training import (
    _build_calibration_references,
)
from .model_successor_temporal_jackknife_utility_protocol import (
    PREDECESSOR_REGIME_NAMES,
)
from .model_successor_temporal_jackknife_utility_training import (
    _build_jackknife_view_frames,
    _jackknife_view_regime_names,
    _predecessor_fit_regime_splits,
    _predecessor_fit_regressor,
    _predecessor_score_regressor,
    _predecessor_target_summary,
)


FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_VERSION = (
    "fmp-exp054-fit-temporal-residual-bound-utility-training-core-v2"
)
FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_DECISION = "DEC-188"

DEC185_MERGED_COMMIT = "3578491ab24b3fa6209ea674e02e1bce5dd99895"
DEC185_PROTOCOL_BLOB_SHA = "3ffac844f9ed5308512dc3313e850cc84fb6d144"
PREDECESSOR_TRAINING_CORE_BLOB_SHA = (
    "4fd0e48302f97e188a8124e1543bde0ffdb43b6f"
)

FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_RESULT_EXECUTION_AUTHORIZED = False
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


def _float_array_digest(values: np.ndarray) -> str:
    array = np.asarray(values, dtype=np.float64)
    if not np.isfinite(array).all():
        raise ValueError("EXP-054 residual values must be finite")
    digest = hashlib.sha256()
    digest.update(len(array.shape).to_bytes(8, "big", signed=False))
    for size in array.shape:
        digest.update(int(size).to_bytes(8, "big", signed=False))
    for value in array.ravel(order="C").tolist():
        digest.update(struct.pack(">d", float(value)))
    return digest.hexdigest()


def validate_fit_temporal_residual_bound_utility_training_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "dec185_protocol": (
            root / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_bound_utility_protocol.py",
            DEC185_PROTOCOL_BLOB_SHA,
        ),
        "predecessor_training_core": (
            root / "src/fmp/market_learning/"
            "model_successor_fit_temporal_feature_support_utility_training.py",
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing EXP-054 training dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-054 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    predecessor = (
        validate_fit_temporal_feature_support_utility_training_sources(
            repository_root=root,
        )
    )
    if predecessor[
        "fit_temporal_feature_support_utility_training_core_decision"
    ] != FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_DECISION:
        raise ValueError("EXP-054 predecessor training decision drift")
    if PREDECESSOR_MODEL_FIT_AUTHORIZED is not False:
        raise ValueError("EXP-054 predecessor model fit must remain closed")
    if FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_RESULT_EXECUTION_AUTHORIZED is not False:
        raise ValueError("EXP-054 predecessor result execution must remain closed")

    fingerprint = fit_temporal_residual_bound_utility_protocol_fingerprint()
    if len(fingerprint) != 64:
        raise ValueError("EXP-054 protocol fingerprint is invalid")

    return {
        "fit_temporal_residual_bound_utility_training_core_version": (
            FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_VERSION
        ),
        "fit_temporal_residual_bound_utility_training_core_decision": (
            FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_DECISION
        ),
        "dec185_merged_commit": DEC185_MERGED_COMMIT,
        "dec185_protocol_blob_sha": actual["dec185_protocol"],
        "predecessor_training_core_blob_sha": actual[
            "predecessor_training_core"
        ],
        "predecessor_training_core_decision": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_DECISION
        ),
        "fit_temporal_residual_bound_utility_protocol_fingerprint": fingerprint,
        "fit_temporal_residual_bound_utility_result_execution_authorized": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
    }


def _residual_windows_by_parent(
) -> dict[str, tuple[dict[str, object], ...]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for raw in FIT_TEMPORAL_SUPPORT_WINDOWS:
        window = dict(raw)
        grouped.setdefault(str(window["parent_regime"]), []).append(window)
    result = {
        parent: tuple(
            sorted(windows, key=lambda item: str(item["start"]))
        )
        for parent, windows in grouped.items()
    }
    if any(
        len(windows) != RESIDUAL_REFERENCE_WINDOWS_PER_VIEW
        for windows in result.values()
    ):
        raise ValueError("EXP-054 residual reference window count mismatch")
    return result


def _downside_residual(sorted_residuals: np.ndarray) -> float:
    residuals = np.asarray(sorted_residuals, dtype=np.float64)
    if (
        residuals.ndim != 1
        or residuals.size == 0
        or not np.isfinite(residuals).all()
    ):
        raise ValueError("EXP-054 residual reference must be finite and non-empty")
    if bool((residuals[1:] < residuals[:-1]).any()):
        raise ValueError("EXP-054 residual reference must be sorted")
    index = int(np.floor(RESIDUAL_DOWNSIDE_QUANTILE * (residuals.size - 1)))
    return float(residuals[index])


def _build_fit_temporal_residual_references(
    *,
    fitted_models: Mapping[str, Mapping[str, object]],
    regime_frames: Mapping[str, pl.DataFrame],
    cell: ModelCell,
) -> tuple[dict[str, dict[str, dict[str, float]]], dict[str, object]]:
    view_regimes = _jackknife_view_regime_names()
    windows_by_parent = _residual_windows_by_parent()
    if set(fitted_models) != set(view_regimes):
        raise ValueError("EXP-054 fitted view inventory mismatch")

    references: dict[str, dict[str, dict[str, float]]] = {}
    evidence: dict[str, object] = {}

    for view_name in sorted(fitted_models):
        included = tuple(view_regimes[view_name])
        excluded = tuple(
            regime for regime in regime_frames if regime not in included
        )
        if len(excluded) != 1:
            raise ValueError("EXP-054 excluded fit-regime count drift")
        excluded_regime = excluded[0]
        parent_frame = regime_frames[excluded_regime]
        target_refs: dict[str, dict[str, float]] = {}
        target_evidence: dict[str, object] = {}

        for target_column in FINANCIAL_TARGET_COLUMNS:
            model = fitted_models[view_name][target_column]
            window_refs: dict[str, float] = {}
            window_evidence: dict[str, object] = {}
            for raw_window in windows_by_parent[excluded_regime]:
                window = dict(raw_window)
                indices = _window_indices(
                    parent_frame,
                    start=_parse_utc_date(str(window["start"])),
                    end_exclusive=_parse_utc_date(str(window["end_exclusive"])),
                )
                window_frame = parent_frame[indices]
                if window_frame.is_empty():
                    raise ValueError("EXP-054 residual reference window is empty")
                predictions, prediction_digest, row_ids = (
                    _predecessor_score_regressor(
                        model,
                        window_frame,
                        cell=cell,
                    )
                )
                realized = np.asarray(
                    window_frame[target_column].to_numpy(),
                    dtype=np.float64,
                )
                predicted = np.asarray(predictions, dtype=np.float64)
                if (
                    realized.shape != predicted.shape
                    or len(row_ids) != window_frame.height
                    or not np.isfinite(realized).all()
                    or not np.isfinite(predicted).all()
                ):
                    raise ValueError("EXP-054 residual reference inputs invalid")
                residuals = np.sort(realized - predicted)
                downside = _downside_residual(residuals)
                name = str(window["name"])
                window_refs[name] = downside
                window_evidence[name] = {
                    "status": "FROZEN",
                    "name": name,
                    "parent_regime": excluded_regime,
                    "start": str(window["start"]),
                    "end_exclusive": str(window["end_exclusive"]),
                    "target_column": target_column,
                    "row_count": window_frame.height,
                    "prediction_digest": prediction_digest,
                    "sorted_residual_digest": _float_array_digest(residuals),
                    "downside_residual": downside,
                }
            target_refs[target_column] = window_refs
            target_evidence[target_column] = window_evidence
        references[view_name] = target_refs
        evidence[view_name] = {
            "status": "FROZEN",
            "included_regimes": list(included),
            "excluded_regime": excluded_regime,
            "targets": target_evidence,
        }

    count = sum(
        len(windows)
        for targets in references.values()
        for windows in targets.values()
    )
    if count != FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL:
        raise ValueError("EXP-054 total residual reference count drift")
    return references, evidence


def _robust_residual_bound_utility(
    *,
    directions: np.ndarray,
    view_predictions: Mapping[str, Mapping[str, np.ndarray]],
    residual_references: Mapping[str, Mapping[str, Mapping[str, float]]],
) -> np.ndarray:
    directions = np.asarray(directions, dtype=object)
    result = np.full(len(directions), -np.inf, dtype=np.float64)
    eligible = np.isin(directions, np.asarray(["LONG", "SHORT"], dtype=object))
    for index in np.flatnonzero(eligible):
        target = (
            FINANCIAL_TARGET_COLUMNS[0]
            if directions[index] == "LONG"
            else FINANCIAL_TARGET_COLUMNS[1]
        )
        bounds: list[float] = []
        for view_name in sorted(view_predictions):
            prediction = float(view_predictions[view_name][target][index])
            for residual in residual_references[view_name][target].values():
                bounds.append(prediction + float(residual))
        if len(bounds) != 12 or not np.isfinite(bounds).all():
            raise ValueError("EXP-054 residual-bound utility inventory invalid")
        result[index] = min(bounds)
    return result


def _derive_residual_bound_cutoff(
    *,
    directions: np.ndarray,
    residual_bound_utility: np.ndarray,
    feature_support: np.ndarray,
    fit_temporal_support: np.ndarray,
    pooled_calibrated_utility: np.ndarray,
    raw_utility: np.ndarray,
    row_ids: Sequence[str],
    budget: int,
) -> dict[str, object]:
    if budget not in CANDIDATE_BUDGET_ANCHORS:
        raise ValueError("unsupported EXP-054 candidate budget")
    directions = np.asarray(directions, dtype=object)
    arrays = [
        np.asarray(residual_bound_utility, dtype=np.float64),
        np.asarray(feature_support, dtype=np.float64),
        np.asarray(fit_temporal_support, dtype=np.float64),
        np.asarray(pooled_calibrated_utility, dtype=np.float64),
        np.asarray(raw_utility, dtype=np.float64),
    ]
    if any(len(value) != len(directions) for value in arrays) or len(row_ids) != len(directions):
        raise ValueError("EXP-054 cutoff row mismatch")
    eligible = np.isin(directions, np.asarray(["LONG", "SHORT"], dtype=object))
    indices = np.flatnonzero(eligible)
    for index in indices.tolist():
        if not np.isfinite(arrays[0][index]):
            raise ValueError("EXP-054 residual-bound utility must be finite")
        for label, value in (
            ("feature support", arrays[1][index]),
            ("fit-temporal utility support", arrays[2][index]),
            ("pooled calibrated utility", arrays[3][index]),
        ):
            if not np.isfinite(value) or value < 0.0 or value > 1.0:
                raise ValueError(f"EXP-054 {label} must be within [0, 1]")
        if not np.isfinite(arrays[4][index]) or arrays[4][index] <= 0.0:
            raise ValueError("EXP-054 directional raw utility must be positive")
    if len(indices) < budget:
        return {
            "status": "BUDGET_UNAVAILABLE",
            "candidate_budget_anchor": budget,
            "eligible_selection_row_count": int(len(indices)),
            "selection_derived_residual_bound_cutoff": None,
            "selection_derived_feature_support_cutoff": None,
            "selection_derived_support_cutoff": None,
            "selection_derived_pooled_calibrated_cutoff": None,
            "selection_derived_raw_cutoff": None,
        }
    ranked = sorted(
        indices.tolist(),
        key=lambda i: (
            -float(arrays[0][i]),
            -float(arrays[1][i]),
            -float(arrays[2][i]),
            -float(arrays[3][i]),
            -float(arrays[4][i]),
            str(row_ids[i]),
        ),
    )
    cutoff_index = ranked[budget - 1]
    cutoff = tuple(float(array[cutoff_index]) for array in arrays)
    passing = _candidate_directions_residual_bound(
        directions=directions,
        residual_bound_utility=arrays[0],
        feature_support=arrays[1],
        fit_temporal_support=arrays[2],
        pooled_calibrated_utility=arrays[3],
        raw_utility=arrays[4],
        residual_bound_cutoff=cutoff[0],
        feature_cutoff=cutoff[1],
        utility_cutoff=cutoff[2],
        pooled_cutoff=cutoff[3],
        raw_cutoff=cutoff[4],
    )
    return {
        "status": "AVAILABLE",
        "candidate_budget_anchor": budget,
        "eligible_selection_row_count": int(len(indices)),
        "selection_derived_residual_bound_cutoff": cutoff[0],
        "selection_derived_feature_support_cutoff": cutoff[1],
        "selection_derived_support_cutoff": cutoff[2],
        "selection_derived_pooled_calibrated_cutoff": cutoff[3],
        "selection_derived_raw_cutoff": cutoff[4],
        "selection_candidate_count_at_cutoff": int(
            np.count_nonzero(passing != "NO_TRADE")
        ),
    }


def _candidate_directions_residual_bound(
    *,
    directions: np.ndarray,
    residual_bound_utility: np.ndarray,
    feature_support: np.ndarray,
    fit_temporal_support: np.ndarray,
    pooled_calibrated_utility: np.ndarray,
    raw_utility: np.ndarray,
    residual_bound_cutoff: float,
    feature_cutoff: float,
    utility_cutoff: float,
    pooled_cutoff: float,
    raw_cutoff: float,
) -> np.ndarray:
    directions = np.asarray(directions, dtype=object)
    values = [
        np.asarray(residual_bound_utility, dtype=np.float64),
        np.asarray(feature_support, dtype=np.float64),
        np.asarray(fit_temporal_support, dtype=np.float64),
        np.asarray(pooled_calibrated_utility, dtype=np.float64),
        np.asarray(raw_utility, dtype=np.float64),
    ]
    cutoffs = [
        residual_bound_cutoff,
        feature_cutoff,
        utility_cutoff,
        pooled_cutoff,
        raw_cutoff,
    ]
    if any(len(value) != len(directions) for value in values):
        raise ValueError("EXP-054 cutoff input length mismatch")
    eligible = np.isin(directions, np.asarray(["LONG", "SHORT"], dtype=object))
    greater = np.zeros(len(directions), dtype=np.bool_)
    equal_prefix = np.ones(len(directions), dtype=np.bool_)
    for value, cutoff in zip(values[:-1], cutoffs[:-1]):
        greater |= equal_prefix & (value > cutoff)
        equal_prefix &= value == cutoff
    greater |= equal_prefix & (values[-1] >= cutoffs[-1])
    return np.where(eligible & greater, directions, "NO_TRADE")


def _view_prediction_matrices(
    *,
    fitted_models: Mapping[str, Mapping[str, object]],
    frame: pl.DataFrame,
    cell: ModelCell,
) -> tuple[
    dict[str, dict[str, np.ndarray]],
    dict[str, dict[str, str]],
    tuple[str, ...],
]:
    predictions: dict[str, dict[str, np.ndarray]] = {}
    digests: dict[str, dict[str, str]] = {}
    expected_row_ids: tuple[str, ...] | None = None
    for view_name in sorted(fitted_models):
        predictions[view_name] = {}
        digests[view_name] = {}
        for target in FINANCIAL_TARGET_COLUMNS:
            values, digest, row_ids = _predecessor_score_regressor(
                fitted_models[view_name][target],
                frame,
                cell=cell,
            )
            current_ids = tuple(str(value) for value in row_ids)
            if expected_row_ids is None:
                expected_row_ids = current_ids
            elif current_ids != expected_row_ids:
                raise ValueError("EXP-054 scored row identity drift")
            array = np.asarray(values, dtype=np.float64)
            if array.shape != (frame.height,) or not np.isfinite(array).all():
                raise ValueError("EXP-054 view predictions are invalid")
            predictions[view_name][target] = array
            digests[view_name][target] = str(digest)
    if expected_row_ids is None or len(expected_row_ids) != frame.height:
        raise ValueError("EXP-054 scored row inventory mismatch")
    return predictions, digests, expected_row_ids


def _residual_bound_consensus_digest(
    *,
    predecessor_digest: str,
    row_ids: Sequence[str],
    directions: np.ndarray,
    residual_bound_utility: np.ndarray,
) -> str:
    if not (
        len(row_ids)
        == len(directions)
        == len(residual_bound_utility)
    ):
        raise ValueError("EXP-054 consensus digest row mismatch")
    digest = hashlib.sha256()
    digest.update(str(predecessor_digest).encode("utf-8"))
    for row_id, direction, residual_bound in zip(
        row_ids,
        directions.tolist(),
        residual_bound_utility.tolist(),
        strict=True,
    ):
        for value in (str(row_id), str(direction)):
            encoded = value.encode("utf-8")
            digest.update(len(encoded).to_bytes(8, "big", signed=False))
            digest.update(encoded)
        digest.update(struct.pack(">d", float(residual_bound)))
    return digest.hexdigest()


def _score_fit_temporal_residual_bound_consensus(
    *,
    fitted_models: Mapping[str, Mapping[str, object]],
    pooled_calibration_references: Mapping[str, Mapping[str, np.ndarray]],
    support_references: Mapping[str, Mapping[str, Mapping[str, np.ndarray]]],
    feature_references: Mapping[str, Mapping[str, Mapping[str, np.ndarray]]],
    residual_references: Mapping[str, Mapping[str, Mapping[str, float]]],
    frame: pl.DataFrame,
    cell: ModelCell,
) -> tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    dict[str, object],
    tuple[str, ...],
    str,
]:
    (
        directions,
        raw_utility,
        pooled_calibrated_utility,
        fit_temporal_support,
        feature_support,
        predecessor_diagnostics,
        row_ids,
        predecessor_digest,
    ) = _score_fit_temporal_feature_support_consensus(
        fitted_models=fitted_models,
        pooled_calibration_references=pooled_calibration_references,
        support_references=support_references,
        feature_references=feature_references,
        frame=frame,
        cell=cell,
    )
    view_predictions, view_prediction_digests, scored_row_ids = (
        _view_prediction_matrices(
            fitted_models=fitted_models,
            frame=frame,
            cell=cell,
        )
    )
    if tuple(row_ids) != tuple(scored_row_ids):
        raise ValueError("EXP-054 predecessor/scored row identity drift")
    residual_bound = _robust_residual_bound_utility(
        directions=directions,
        view_predictions=view_predictions,
        residual_references=residual_references,
    )
    eligible = np.isin(
        directions,
        np.asarray(["LONG", "SHORT"], dtype=object),
    )
    values = residual_bound[eligible]
    if bool(eligible.any()) and (
        not np.isfinite(values).all()
    ):
        raise ValueError("EXP-054 eligible residual-bound utility is invalid")
    diagnostics = {
        **dict(predecessor_diagnostics),
        "minimum_robust_fit_temporal_residual_bound_utility": (
            float(values.min()) if len(values) else None
        ),
        "maximum_robust_fit_temporal_residual_bound_utility": (
            float(values.max()) if len(values) else None
        ),
        "fit_temporal_residual_reference_count": (
            FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL
        ),
        "residual_bound_view_prediction_digests": view_prediction_digests,
    }
    digest = _residual_bound_consensus_digest(
        predecessor_digest=predecessor_digest,
        row_ids=row_ids,
        directions=directions,
        residual_bound_utility=residual_bound,
    )
    return (
        directions,
        raw_utility,
        pooled_calibrated_utility,
        fit_temporal_support,
        feature_support,
        residual_bound,
        diagnostics,
        tuple(row_ids),
        digest,
    )


def _evaluate_residual_bound_cutoff(
    frame: pl.DataFrame,
    *,
    directions: np.ndarray,
    residual_bound_utility: np.ndarray,
    feature_support: np.ndarray,
    fit_temporal_support: np.ndarray,
    pooled_calibrated_utility: np.ndarray,
    raw_utility: np.ndarray,
    residual_bound_cutoff: float,
    feature_cutoff: float,
    utility_cutoff: float,
    pooled_cutoff: float,
    raw_cutoff: float,
    budget: int,
    scenarios: Sequence[float],
    row_ids: Sequence[str],
) -> dict[str, object]:
    candidates = _candidate_directions_residual_bound(
        directions=directions,
        residual_bound_utility=residual_bound_utility,
        feature_support=feature_support,
        fit_temporal_support=fit_temporal_support,
        pooled_calibrated_utility=pooled_calibrated_utility,
        raw_utility=raw_utility,
        residual_bound_cutoff=residual_bound_cutoff,
        feature_cutoff=feature_cutoff,
        utility_cutoff=utility_cutoff,
        pooled_cutoff=pooled_cutoff,
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
        "selection_derived_residual_bound_cutoff": residual_bound_cutoff,
        "selection_derived_feature_support_cutoff": feature_cutoff,
        "selection_derived_support_cutoff": utility_cutoff,
        "selection_derived_pooled_calibrated_cutoff": pooled_cutoff,
        "selection_derived_raw_cutoff": raw_cutoff,
        "scenarios": scenario_results,
    }


def _evaluate_temporal_stability_residual_bound(
    *,
    selection_frame: pl.DataFrame,
    directions: np.ndarray,
    residual_bound_utility: np.ndarray,
    feature_support: np.ndarray,
    fit_temporal_support: np.ndarray,
    pooled_calibrated_utility: np.ndarray,
    raw_utility: np.ndarray,
    residual_bound_cutoff: float,
    feature_cutoff: float,
    utility_cutoff: float,
    pooled_cutoff: float,
    raw_cutoff: float,
    budget: int,
    cell: ModelCell,
    full_selection_candidate_count: int,
) -> dict[str, object]:
    arrays = (
        directions,
        residual_bound_utility,
        feature_support,
        fit_temporal_support,
        pooled_calibrated_utility,
        raw_utility,
    )
    if any(len(value) != selection_frame.height for value in arrays):
        raise ValueError("EXP-054 stability row mismatch")
    windows: list[dict[str, object]] = []
    for raw_window in TEMPORAL_STABILITY_WINDOWS:
        window = dict(raw_window)
        indices = _window_indices(
            selection_frame,
            start=_parse_utc_date(str(window["start"])),
            end_exclusive=_parse_utc_date(str(window["end_exclusive"])),
        )
        frame = selection_frame[indices]
        index_array = np.asarray(indices, dtype=np.int64)
        row_ids = _base._row_identity(frame, cell=cell)
        evaluated = _evaluate_residual_bound_cutoff(
            frame,
            directions=directions[index_array],
            residual_bound_utility=residual_bound_utility[index_array],
            feature_support=feature_support[index_array],
            fit_temporal_support=fit_temporal_support[index_array],
            pooled_calibrated_utility=pooled_calibrated_utility[index_array],
            raw_utility=raw_utility[index_array],
            residual_bound_cutoff=residual_bound_cutoff,
            feature_cutoff=feature_cutoff,
            utility_cutoff=utility_cutoff,
            pooled_cutoff=pooled_cutoff,
            raw_cutoff=raw_cutoff,
            budget=budget,
            scenarios=SELECTION_GATE_SCENARIOS,
            row_ids=row_ids,
        )
        metrics = evaluated["scenarios"]["0.5"]["metrics"]
        gate = _window_gate(
            metrics,
            full_selection_candidate_count=full_selection_candidate_count,
        )
        windows.append(
            {
                "name": str(window["name"]),
                "start": str(window["start"]),
                "end_exclusive": str(window["end_exclusive"]),
                "row_count": frame.height,
                "metrics": metrics,
                "gate": gate,
            }
        )
    return {
        "status": (
            "PASS"
            if all(bool(row["gate"]["passed"]) for row in windows)
            else "REJECT"
        ),
        "minimum_directional_candidate_share_per_window": (
            MIN_STABILITY_WINDOW_CANDIDATE_SHARE
        ),
        "windows": windows,
    }


def _evaluate_forward_split_residual_bound(
    *,
    fitted_models: Mapping[str, Mapping[str, object]],
    pooled_calibration_references: Mapping[str, Mapping[str, np.ndarray]],
    support_references: Mapping[str, Mapping[str, Mapping[str, np.ndarray]]],
    feature_references: Mapping[str, Mapping[str, Mapping[str, np.ndarray]]],
    residual_references: Mapping[str, Mapping[str, Mapping[str, float]]],
    frame: pl.DataFrame,
    cell: ModelCell,
    residual_bound_cutoff: float,
    feature_cutoff: float,
    utility_cutoff: float,
    pooled_cutoff: float,
    raw_cutoff: float,
    budget: int,
    gate_scenarios: Sequence[float],
) -> dict[str, object]:
    (
        directions,
        raw_utility,
        pooled_calibrated_utility,
        fit_temporal_support,
        feature_support,
        residual_bound_utility,
        diagnostics,
        row_ids,
        digest,
    ) = _score_fit_temporal_residual_bound_consensus(
        fitted_models=fitted_models,
        pooled_calibration_references=pooled_calibration_references,
        support_references=support_references,
        feature_references=feature_references,
        residual_references=residual_references,
        frame=frame,
        cell=cell,
    )
    all_scenarios = tuple(
        sorted(
            {
                *(float(v) for v in DIAGNOSTIC_SCENARIOS),
                *(float(v) for v in gate_scenarios),
            }
        )
    )
    evaluated = _evaluate_residual_bound_cutoff(
        frame,
        directions=directions,
        residual_bound_utility=residual_bound_utility,
        feature_support=feature_support,
        fit_temporal_support=fit_temporal_support,
        pooled_calibrated_utility=pooled_calibrated_utility,
        raw_utility=raw_utility,
        residual_bound_cutoff=residual_bound_cutoff,
        feature_cutoff=feature_cutoff,
        utility_cutoff=utility_cutoff,
        pooled_cutoff=pooled_cutoff,
        raw_cutoff=raw_cutoff,
        budget=budget,
        scenarios=all_scenarios,
        row_ids=row_ids,
    )
    gating = [
        bool(evaluated["scenarios"][str(float(value))]["gate"]["passed"])
        for value in gate_scenarios
    ]
    return {
        "status": "PASS" if all(gating) else "REJECT",
        "row_count": frame.height,
        "fit_temporal_residual_bound_utility_consensus": diagnostics,
        "fit_temporal_residual_bound_utility_consensus_digest": digest,
        **evaluated,
    }


def run_fit_temporal_residual_bound_utility_model_cell_core(
    *,
    features: pl.DataFrame,
    outcomes: pl.DataFrame,
    cell: ModelCell,
) -> dict[str, object]:
    joined, processed_manifest_sha256 = _base._validate_frames(
        features,
        outcomes,
        cell=cell,
    )
    split_frames = {
        split.name: _base._split_frame(joined, split)
        for split in PROTOCOL_SPLITS
    }
    if any(frame.is_empty() for frame in split_frames.values()):
        empty = [name for name, frame in split_frames.items() if frame.is_empty()]
        raise ValueError(f"EXP-054 model cell has empty required split(s): {empty}")

    regime_frames = {
        split.name: _base._split_frame(joined, split)
        for split in _predecessor_fit_regime_splits()
    }
    if set(regime_frames) != set(PREDECESSOR_REGIME_NAMES):
        raise ValueError("EXP-054 predecessor fit-regime identity drift")
    if any(frame.is_empty() for frame in regime_frames.values()):
        empty = [name for name, frame in regime_frames.items() if frame.is_empty()]
        raise ValueError(f"EXP-054 model cell has empty fit regime(s): {empty}")

    view_frames = _build_jackknife_view_frames(regime_frames)
    fitted_models: dict[str, dict[str, _base.FittedMarketModel]] = {}
    fit_evidence: dict[str, object] = {}
    view_regimes = _jackknife_view_regime_names()
    for view_name, fit_frame in view_frames.items():
        target_models: dict[str, _base.FittedMarketModel] = {}
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
                "target_summary": _predecessor_target_summary(
                    fit_frame,
                    target_column=target_column,
                ),
                "preprocessor_fingerprint": fitted.preprocessor_fingerprint,
                "model_fingerprint": fitted.model_fingerprint,
            }
        included = view_regimes[view_name]
        excluded = tuple(
            value for value in PREDECESSOR_REGIME_NAMES if value not in included
        )
        if len(excluded) != 1:
            raise ValueError("EXP-054 jackknife excluded-regime count drift")
        fitted_models[view_name] = target_models
        fit_evidence[view_name] = {
            "status": "FITTED",
            "included_regimes": list(included),
            "excluded_regime": excluded[0],
            "row_count": fit_frame.height,
            "regressor_count": len(target_models),
            "regressors": target_evidence,
        }

    pooled_calibration_references, pooled_calibration_evidence = (
        _build_calibration_references(
            fitted_models=fitted_models,
            regime_frames=regime_frames,
            cell=cell,
        )
    )
    support_references, support_evidence = _build_fit_temporal_support_references(
        fitted_models=fitted_models,
        regime_frames=regime_frames,
        cell=cell,
    )
    feature_references, feature_evidence = (
        _build_fit_temporal_feature_support_references(
            fitted_models=fitted_models,
            regime_frames=regime_frames,
        )
    )
    residual_references, residual_evidence = _build_fit_temporal_residual_references(
        fitted_models=fitted_models,
        regime_frames=regime_frames,
        cell=cell,
    )

    selection_frame = split_frames[SELECTION_SPLIT.name]
    (
        selection_directions,
        selection_raw_utility,
        selection_pooled_calibrated_utility,
        selection_fit_temporal_support,
        selection_feature_support,
        selection_residual_bound_utility,
        selection_diagnostics,
        selection_row_ids,
        selection_consensus_digest,
    ) = _score_fit_temporal_residual_bound_consensus(
        fitted_models=fitted_models,
        pooled_calibration_references=pooled_calibration_references,
        support_references=support_references,
        feature_references=feature_references,
        residual_references=residual_references,
        frame=selection_frame,
        cell=cell,
    )

    variants: list[dict[str, object]] = []
    for budget in CANDIDATE_BUDGET_ANCHORS:
        cutoff_record = _derive_residual_bound_cutoff(
            directions=selection_directions,
            residual_bound_utility=selection_residual_bound_utility,
            feature_support=selection_feature_support,
            fit_temporal_support=selection_fit_temporal_support,
            pooled_calibrated_utility=selection_pooled_calibrated_utility,
            raw_utility=selection_raw_utility,
            row_ids=selection_row_ids,
            budget=budget,
        )
        if cutoff_record["status"] != "AVAILABLE":
            variants.append(
                {
                    "model_family": "hist_gradient_boosting_regression",
                    "candidate_budget_anchor": budget,
                    "evaluation_status": "BUDGET_UNAVAILABLE",
                    **cutoff_record,
                    "aggregate_selection_gate_passed": False,
                    "temporal_stability": {
                        "status": "BUDGET_UNAVAILABLE",
                        "minimum_directional_candidate_share_per_window": (
                            MIN_STABILITY_WINDOW_CANDIDATE_SHARE
                        ),
                        "windows": [],
                    },
                    "selection_gate_passed": False,
                }
            )
            continue
        residual_bound_cutoff = float(
            cutoff_record["selection_derived_residual_bound_cutoff"]
        )
        feature_cutoff = float(
            cutoff_record["selection_derived_feature_support_cutoff"]
        )
        utility_cutoff = float(cutoff_record["selection_derived_support_cutoff"])
        pooled_cutoff = float(
            cutoff_record["selection_derived_pooled_calibrated_cutoff"]
        )
        raw_cutoff = float(cutoff_record["selection_derived_raw_cutoff"])
        evaluated = _evaluate_residual_bound_cutoff(
            selection_frame,
            directions=selection_directions,
            residual_bound_utility=selection_residual_bound_utility,
            feature_support=selection_feature_support,
            fit_temporal_support=selection_fit_temporal_support,
            pooled_calibrated_utility=selection_pooled_calibrated_utility,
            raw_utility=selection_raw_utility,
            residual_bound_cutoff=residual_bound_cutoff,
            feature_cutoff=feature_cutoff,
            utility_cutoff=utility_cutoff,
            pooled_cutoff=pooled_cutoff,
            raw_cutoff=raw_cutoff,
            budget=budget,
            scenarios=SELECTION_GATE_SCENARIOS,
            row_ids=selection_row_ids,
        )
        scenario = evaluated["scenarios"]["0.5"]
        aggregate_passed = bool(scenario["gate"]["passed"])
        full_count = int(scenario["metrics"]["directional_candidate_count"])
        if aggregate_passed:
            stability = _evaluate_temporal_stability_residual_bound(
                selection_frame=selection_frame,
                directions=selection_directions,
                residual_bound_utility=selection_residual_bound_utility,
                feature_support=selection_feature_support,
                fit_temporal_support=selection_fit_temporal_support,
                pooled_calibrated_utility=selection_pooled_calibrated_utility,
                raw_utility=selection_raw_utility,
                residual_bound_cutoff=residual_bound_cutoff,
                feature_cutoff=feature_cutoff,
                utility_cutoff=utility_cutoff,
                pooled_cutoff=pooled_cutoff,
                raw_cutoff=raw_cutoff,
                budget=budget,
                cell=cell,
                full_selection_candidate_count=full_count,
            )
            stability_passed = stability["status"] == "PASS"
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
                "model_family": "hist_gradient_boosting_regression",
                "evaluation_status": "EVALUATED",
                **cutoff_record,
                **evaluated,
                "aggregate_selection_gate_passed": aggregate_passed,
                "temporal_stability": stability,
                "selection_gate_passed": bool(
                    aggregate_passed and stability_passed
                ),
            }
        )

    passing = [row for row in variants if row["selection_gate_passed"]]
    selected = max(passing, key=_selection_key) if passing else None
    result: dict[str, object] = {
        "experiment_id": FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_EXPERIMENT_ID,
        "training_core_version": FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_VERSION,
        "training_core_decision": FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_DECISION,
        "dec185_merged_commit": DEC185_MERGED_COMMIT,
        "dec185_protocol_blob_sha": DEC185_PROTOCOL_BLOB_SHA,
        "predecessor_training_core_blob_sha": PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        "predecessor_training_core_decision": FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_DECISION,
        "protocol_decision": FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_PROTOCOL_DECISION,
        "protocol_version": FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_PROTOCOL_VERSION,
        "protocol_fingerprint": fit_temporal_residual_bound_utility_protocol_fingerprint(),
        "prior_result_informed": PRIOR_RESULT_INFORMED,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": UNTOUCHED_OOS,
        "cell": {
            "symbol": cell.symbol,
            "timeframe": cell.timeframe,
            "horizon_minutes": cell.horizon_minutes,
        },
        "processed_manifest_sha256": processed_manifest_sha256,
        "joined_row_count": joined.height,
        "split_row_counts": {name: frame.height for name, frame in split_frames.items()},
        "fit": {
            "jackknife_models": fit_evidence,
            "jackknife_view_count": len(fitted_models),
            "regressor_count": sum(len(value) for value in fitted_models.values()),
            "out_of_fit_calibration_references": pooled_calibration_evidence,
            "calibration_reference_count": sum(
                len(value) for value in pooled_calibration_references.values()
            ),
            "calibration_reference_rule": CALIBRATION_REFERENCE_RULE,
            "calibrated_percentile_rule": CALIBRATED_PERCENTILE_RULE,
            "robust_calibrated_score_rule": ROBUST_CALIBRATED_SCORE_RULE,
            "fit_temporal_support_references": support_evidence,
            "fit_temporal_support_reference_count": FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL,
            "fit_temporal_support_reference_rule": FIT_TEMPORAL_SUPPORT_REFERENCE_RULE,
            "fit_temporal_support_percentile_rule": FIT_TEMPORAL_SUPPORT_PERCENTILE_RULE,
            "robust_fit_temporal_support_score_rule": ROBUST_FIT_TEMPORAL_SUPPORT_SCORE_RULE,
            "fit_temporal_feature_support_references": feature_evidence,
            "fit_temporal_feature_support_reference_count": FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL,
            "fit_temporal_feature_reference_rule": FIT_TEMPORAL_FEATURE_REFERENCE_RULE,
            "fit_temporal_feature_distance_rule": FIT_TEMPORAL_FEATURE_DISTANCE_RULE,
            "fit_temporal_feature_support_percentile_rule": FIT_TEMPORAL_FEATURE_SUPPORT_PERCENTILE_RULE,
            "robust_fit_temporal_feature_support_score_rule": ROBUST_FIT_TEMPORAL_FEATURE_SUPPORT_SCORE_RULE,
            "fit_temporal_residual_references": residual_evidence,
            "fit_temporal_residual_reference_count": FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL,
            "fit_temporal_residual_reference_rule": FIT_TEMPORAL_RESIDUAL_REFERENCE_RULE,
            "residual_downside_quantile_rule": RESIDUAL_DOWNSIDE_QUANTILE_RULE,
            "robust_residual_bound_utility_rule": ROBUST_RESIDUAL_BOUND_UTILITY_RULE,
            "residual_bound_eligibility_rule": RESIDUAL_BOUND_ELIGIBILITY_RULE,
            "full_fit_single_model": {"status": "FORBIDDEN_BY_DEC150_DEC163_DEC174_DEC185", "fit_attempt_count": 0},
            "view_weight_search": {"status": "FORBIDDEN_BY_DEC150_DEC163_DEC174_DEC185", "fit_attempt_count": 0},
            "view_fallback": {"status": "FORBIDDEN_BY_DEC150_DEC163_DEC174_DEC185", "fit_attempt_count": 0},
            "selection_window_calibration": {"status": "FORBIDDEN_BY_DEC150_DEC163_DEC174_DEC185", "fit_attempt_count": 0},
            "hist_gradient_boosting_classifier": {"status": "EXCLUDED_BY_DEC150_DEC163_DEC174_DEC185", "fit_attempt_count": 0},
            "logistic_regression": {"status": "EXCLUDED_BY_DEC112_DEC150_DEC163_DEC174_DEC185", "fit_attempt_count": 0},
        },
        "selection": {
            "status": (
                "SELECTED"
                if selected is not None
                else "NO_FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_STABLE_MODEL_CHALLENGER"
            ),
            "row_count": selection_frame.height,
            "fit_temporal_residual_bound_utility_consensus": selection_diagnostics,
            "fit_temporal_residual_bound_utility_consensus_digest": selection_consensus_digest,
            "ranking_rule": RANKING_RULE,
            "selection_cutoff_rule": SELECTION_CUTOFF_RULE,
            "cutoff_tie_policy": CUTOFF_TIE_POLICY,
            "forward_application_rule": FORWARD_APPLICATION_RULE,
            "variants": variants,
            "selected_variant": (
                {
                    "model_family": "hist_gradient_boosting_regression",
                    "candidate_budget_anchor": int(selected["candidate_budget_anchor"]),
                    "selection_derived_residual_bound_cutoff": float(
                        selected["selection_derived_residual_bound_cutoff"]
                    ),
                    "selection_derived_feature_support_cutoff": float(
                        selected["selection_derived_feature_support_cutoff"]
                    ),
                    "selection_derived_support_cutoff": float(
                        selected["selection_derived_support_cutoff"]
                    ),
                    "selection_derived_pooled_calibrated_cutoff": float(
                        selected["selection_derived_pooled_calibrated_cutoff"]
                    ),
                    "selection_derived_raw_cutoff": float(
                        selected["selection_derived_raw_cutoff"]
                    ),
                }
                if selected is not None
                else None
            ),
        },
        "validation": {"status": "LOCKED_NO_SELECTION"},
        "retrospective_holdout": {"status": "LOCKED_NO_SELECTION"},
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
        result["result_fingerprint"] = _sha256(result)
        return result

    residual_bound_cutoff = float(selected["selection_derived_residual_bound_cutoff"])
    feature_cutoff = float(selected["selection_derived_feature_support_cutoff"])
    utility_cutoff = float(selected["selection_derived_support_cutoff"])
    pooled_cutoff = float(selected["selection_derived_pooled_calibrated_cutoff"])
    raw_cutoff = float(selected["selection_derived_raw_cutoff"])
    budget = int(selected["candidate_budget_anchor"])

    validation = _evaluate_forward_split_residual_bound(
        fitted_models=fitted_models,
        pooled_calibration_references=pooled_calibration_references,
        support_references=support_references,
        feature_references=feature_references,
        residual_references=residual_references,
        frame=split_frames[VALIDATION_SPLIT.name],
        cell=cell,
        residual_bound_cutoff=residual_bound_cutoff,
        feature_cutoff=feature_cutoff,
        utility_cutoff=utility_cutoff,
        pooled_cutoff=pooled_cutoff,
        raw_cutoff=raw_cutoff,
        budget=budget,
        gate_scenarios=VALIDATION_GATE_SCENARIOS,
    )
    result["validation"] = validation
    if validation["status"] != "PASS":
        result["retrospective_holdout"] = {"status": "LOCKED_VALIDATION_REJECT"}
        result["result_fingerprint"] = _sha256(result)
        return result

    result["retrospective_holdout"] = _evaluate_forward_split_residual_bound(
        fitted_models=fitted_models,
        pooled_calibration_references=pooled_calibration_references,
        support_references=support_references,
        feature_references=feature_references,
        residual_references=residual_references,
        frame=split_frames[RETROSPECTIVE_HOLDOUT_SPLIT.name],
        cell=cell,
        residual_bound_cutoff=residual_bound_cutoff,
        feature_cutoff=feature_cutoff,
        utility_cutoff=utility_cutoff,
        pooled_cutoff=pooled_cutoff,
        raw_cutoff=raw_cutoff,
        budget=budget,
        gate_scenarios=HOLDOUT_GATE_SCENARIOS,
    )
    result["result_fingerprint"] = _sha256(result)
    return result


def build_fit_temporal_residual_bound_training_core_gate() -> dict[str, object]:
    return {
        "experiment_id": FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_EXPERIMENT_ID,
        "training_core_version": (
            FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_DECISION
        ),
        "protocol_decision": FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_PROTOCOL_DECISION,
        "protocol_version": FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_PROTOCOL_VERSION,
        "protocol_fingerprint": (
            fit_temporal_residual_bound_utility_protocol_fingerprint()
        ),
        "ranking_rule": RANKING_RULE,
        "selection_cutoff_rule": SELECTION_CUTOFF_RULE,
        "cutoff_tie_policy": CUTOFF_TIE_POLICY,
        "forward_application_rule": FORWARD_APPLICATION_RULE,
        "residual_reference_count_per_cell": (
            FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL
        ),
        "result_execution_authorized": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }


__all__ = [
    "BROKER_MUTATION_AUTHORIZED",
    "DEC185_MERGED_COMMIT",
    "DEC185_PROTOCOL_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_RESULT_EXECUTION_AUTHORIZED",
    "FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_DECISION",
    "FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_VERSION",
    "LIVE_ORDER_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "PREDECESSOR_TRAINING_CORE_BLOB_SHA",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "_build_fit_temporal_residual_references",
    "_candidate_directions_residual_bound",
    "_derive_residual_bound_cutoff",
    "_downside_residual",
    "_robust_residual_bound_utility",
    "_score_fit_temporal_residual_bound_consensus",
    "run_fit_temporal_residual_bound_utility_model_cell_core",
    "build_fit_temporal_residual_bound_training_core_gate",
    "validate_fit_temporal_residual_bound_utility_training_sources",
]
