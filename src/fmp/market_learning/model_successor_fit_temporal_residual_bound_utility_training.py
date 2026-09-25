from __future__ import annotations

import hashlib
from pathlib import Path
import struct
from typing import Mapping, Sequence

import numpy as np
import polars as pl

from .model_protocol import ModelCell
from .model_successor_density_training import (
    _canonical_json,
    _git_blob_sha,
    _parse_utc_date,
    _window_indices,
)
from .model_successor_fit_temporal_feature_support_utility_training import (
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_DECISION,
    MODEL_FIT_AUTHORIZED as PREDECESSOR_MODEL_FIT_AUTHORIZED,
    _candidate_directions_feature_support,
    _score_fit_temporal_feature_support_consensus,
    validate_fit_temporal_feature_support_utility_training_sources,
)
from .model_successor_fit_temporal_residual_bound_utility_protocol import (
    CUTOFF_TIE_POLICY,
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_PROTOCOL_VERSION,
    FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL,
    FORWARD_APPLICATION_RULE,
    RANKING_RULE,
    RESIDUAL_DOWNSIDE_QUANTILE,
    RESIDUAL_REFERENCE_WINDOWS_PER_VIEW,
    SELECTION_CUTOFF_RULE,
    fit_temporal_residual_bound_utility_protocol_fingerprint,
)
from .model_successor_fit_temporal_support_utility_protocol import (
    FIT_TEMPORAL_SUPPORT_WINDOWS,
)
from .model_successor_temporal_calibrated_utility_protocol import (
    FINANCIAL_TARGET_COLUMNS,
)
from .model_successor_temporal_jackknife_utility_training import (
    _jackknife_view_regime_names,
    _predecessor_score_regressor,
)


FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_VERSION = (
    "fmp-exp054-fit-temporal-residual-bound-utility-training-core-v1"
)
FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_DECISION = "DEC-186"

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
    arrays = [
        np.asarray(residual_bound_utility, dtype=np.float64),
        np.asarray(feature_support, dtype=np.float64),
        np.asarray(fit_temporal_support, dtype=np.float64),
        np.asarray(pooled_calibrated_utility, dtype=np.float64),
        np.asarray(raw_utility, dtype=np.float64),
    ]
    directions = np.asarray(directions, dtype=object)
    eligible = np.isin(directions, np.asarray(["LONG", "SHORT"], dtype=object))
    indices = np.flatnonzero(eligible)
    if len(indices) < budget:
        return {
            "status": "BUDGET_UNAVAILABLE",
            "candidate_budget_anchor": budget,
            "eligible_selection_row_count": int(len(indices)),
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
    "build_fit_temporal_residual_bound_training_core_gate",
    "validate_fit_temporal_residual_bound_utility_training_sources",
]
