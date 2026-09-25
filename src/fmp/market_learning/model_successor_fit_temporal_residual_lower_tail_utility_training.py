from __future__ import annotations

import hashlib
from pathlib import Path
import struct
from typing import Mapping, Sequence

import numpy as np
import polars as pl

from . import model_successor_fit_temporal_residual_breadth_utility_training as _predecessor
from .contracts import EVIDENCE_LABEL
from .model_protocol import ModelCell
from .model_successor_fit_temporal_residual_lower_tail_utility_protocol import (
    CUTOFF_TIE_POLICY,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_BOUND_COUNT_PER_ROW,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_COUNT,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_FRACTION,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_RULE,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_PROTOCOL_VERSION,
    FORWARD_APPLICATION_RULE,
    PRIOR_RESULT_INFORMED,
    RANKING_RULE,
    RESIDUAL_LOWER_TAIL_ELIGIBILITY_RULE,
    SELECTION_CUTOFF_RULE,
    UNTOUCHED_OOS,
    fit_temporal_residual_lower_tail_utility_protocol_fingerprint,
)

_base = _predecessor._predecessor

FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_TRAINING_CORE_VERSION = (
    "fmp-exp056-fit-temporal-residual-lower-tail-utility-training-core-v1"
)
FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_TRAINING_CORE_DECISION = "DEC-210"

DEC209_MERGED_COMMIT = "d2e1aabba6c0f283da6802fe315a5a29b22b503c"
DEC209_PROTOCOL_BLOB_SHA = "14d8fe5d0530f44acaa7084c6d78d1c19bd21d8d"
PREDECESSOR_TRAINING_CORE_BLOB_SHA = (
    "c9517b7516940c78621448088c3933aa1c57e281"
)

FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_RESULT_EXECUTION_AUTHORIZED = False
MODEL_FIT_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
SHADOW_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _sha256(value: object) -> str:
    return hashlib.sha256(_base._canonical_json(value)).hexdigest()


def validate_fit_temporal_residual_lower_tail_utility_training_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "dec209_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_lower_tail_utility_protocol.py",
            DEC209_PROTOCOL_BLOB_SHA,
        ),
        "predecessor_training_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_breadth_utility_training.py",
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing EXP-056 training dependency: {path}")
        actual_sha = _base._git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-056 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    predecessor = (
        _predecessor
        .validate_fit_temporal_residual_breadth_utility_training_sources(
            repository_root=root,
        )
    )
    if predecessor[
        "fit_temporal_residual_breadth_utility_training_core_decision"
    ] != _predecessor.FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_TRAINING_CORE_DECISION:
        raise ValueError("EXP-056 predecessor training decision drift")
    if _predecessor.MODEL_FIT_AUTHORIZED is not False:
        raise ValueError("EXP-056 predecessor model fit must remain closed")
    if (
        _predecessor
        .FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_RESULT_EXECUTION_AUTHORIZED
        is not False
    ):
        raise ValueError(
            "EXP-056 predecessor result execution must remain closed"
        )

    fingerprint = fit_temporal_residual_lower_tail_utility_protocol_fingerprint()
    if len(fingerprint) != 64:
        raise ValueError("EXP-056 protocol fingerprint is invalid")

    return {
        "fit_temporal_residual_lower_tail_utility_training_core_version": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_TRAINING_CORE_VERSION
        ),
        "fit_temporal_residual_lower_tail_utility_training_core_decision": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_TRAINING_CORE_DECISION
        ),
        "dec209_merged_commit": DEC209_MERGED_COMMIT,
        "dec209_protocol_blob_sha": actual["dec209_protocol"],
        "predecessor_training_core_blob_sha": actual[
            "predecessor_training_core"
        ],
        "predecessor_training_core_decision": (
            _predecessor
            .FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_TRAINING_CORE_DECISION
        ),
        "fit_temporal_residual_lower_tail_utility_protocol_fingerprint": (
            fingerprint
        ),
        "fit_temporal_residual_lower_tail_utility_result_execution_authorized": (
            False
        ),
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
    }


def _fit_temporal_residual_lower_tail_mean(
    *,
    directions: np.ndarray,
    view_predictions: Mapping[str, Mapping[str, np.ndarray]],
    residual_references: Mapping[str, Mapping[str, Mapping[str, float]]],
) -> np.ndarray:
    directions = np.asarray(directions, dtype=object)
    result = np.full(len(directions), -np.inf, dtype=np.float64)
    eligible = np.isin(
        directions,
        np.asarray(["LONG", "SHORT"], dtype=object),
    )
    for index in np.flatnonzero(eligible):
        target = (
            _base.FINANCIAL_TARGET_COLUMNS[0]
            if directions[index] == "LONG"
            else _base.FINANCIAL_TARGET_COLUMNS[1]
        )
        bounds: list[float] = []
        for view_name in sorted(view_predictions):
            prediction = float(view_predictions[view_name][target][index])
            for residual in residual_references[view_name][target].values():
                bounds.append(prediction + float(residual))
        values = np.asarray(bounds, dtype=np.float64)
        if (
            len(values)
            != FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_BOUND_COUNT_PER_ROW
            or not np.isfinite(values).all()
        ):
            raise ValueError(
                "EXP-056 residual lower-tail bound inventory invalid"
            )
        ordered = np.sort(values)
        tail = ordered[:FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_COUNT]
        result[index] = float(np.mean(tail))
    return result


def _candidate_directions_residual_lower_tail(
    *,
    directions: np.ndarray,
    residual_lower_tail: np.ndarray,
    residual_breadth: np.ndarray,
    residual_bound_utility: np.ndarray,
    feature_support: np.ndarray,
    fit_temporal_support: np.ndarray,
    pooled_calibrated_utility: np.ndarray,
    raw_utility: np.ndarray,
    residual_lower_tail_cutoff: float,
    residual_breadth_cutoff: float,
    residual_bound_cutoff: float,
    feature_cutoff: float,
    utility_cutoff: float,
    pooled_cutoff: float,
    raw_cutoff: float,
) -> np.ndarray:
    directions = np.asarray(directions, dtype=object)
    values = [
        np.asarray(residual_lower_tail, dtype=np.float64),
        np.asarray(residual_breadth, dtype=np.float64),
        np.asarray(residual_bound_utility, dtype=np.float64),
        np.asarray(feature_support, dtype=np.float64),
        np.asarray(fit_temporal_support, dtype=np.float64),
        np.asarray(pooled_calibrated_utility, dtype=np.float64),
        np.asarray(raw_utility, dtype=np.float64),
    ]
    cutoffs = [
        residual_lower_tail_cutoff,
        residual_breadth_cutoff,
        residual_bound_cutoff,
        feature_cutoff,
        utility_cutoff,
        pooled_cutoff,
        raw_cutoff,
    ]
    if any(len(value) != len(directions) for value in values):
        raise ValueError("EXP-056 cutoff input length mismatch")

    eligible = np.isin(
        directions,
        np.asarray(["LONG", "SHORT"], dtype=object),
    )
    greater = np.zeros(len(directions), dtype=np.bool_)
    equal_prefix = np.ones(len(directions), dtype=np.bool_)
    for value, cutoff in zip(values[:-1], cutoffs[:-1], strict=True):
        greater |= equal_prefix & (value > cutoff)
        equal_prefix &= value == cutoff
    greater |= equal_prefix & (values[-1] >= cutoffs[-1])
    return np.where(eligible & greater, directions, "NO_TRADE")


def _derive_residual_lower_tail_cutoff(
    *,
    directions: np.ndarray,
    residual_lower_tail: np.ndarray,
    residual_breadth: np.ndarray,
    residual_bound_utility: np.ndarray,
    feature_support: np.ndarray,
    fit_temporal_support: np.ndarray,
    pooled_calibrated_utility: np.ndarray,
    raw_utility: np.ndarray,
    row_ids: Sequence[str],
    budget: int,
) -> dict[str, object]:
    if budget not in _base.CANDIDATE_BUDGET_ANCHORS:
        raise ValueError("unsupported EXP-056 candidate budget")
    directions = np.asarray(directions, dtype=object)
    arrays = [
        np.asarray(residual_lower_tail, dtype=np.float64),
        np.asarray(residual_breadth, dtype=np.float64),
        np.asarray(residual_bound_utility, dtype=np.float64),
        np.asarray(feature_support, dtype=np.float64),
        np.asarray(fit_temporal_support, dtype=np.float64),
        np.asarray(pooled_calibrated_utility, dtype=np.float64),
        np.asarray(raw_utility, dtype=np.float64),
    ]
    if (
        any(len(value) != len(directions) for value in arrays)
        or len(row_ids) != len(directions)
    ):
        raise ValueError("EXP-056 cutoff row mismatch")

    eligible = np.isin(
        directions,
        np.asarray(["LONG", "SHORT"], dtype=object),
    )
    indices = np.flatnonzero(eligible)
    for index in indices.tolist():
        if not np.isfinite(arrays[0][index]):
            raise ValueError(
                "EXP-056 residual lower-tail mean must be finite"
            )
        breadth = arrays[1][index]
        if not np.isfinite(breadth) or breadth < 0.0 or breadth > 1.0:
            raise ValueError(
                "EXP-056 residual breadth must be within [0, 1]"
            )
        if not np.isfinite(arrays[2][index]):
            raise ValueError(
                "EXP-056 residual-bound utility must be finite"
            )
        for label, value in (
            ("feature support", arrays[3][index]),
            ("fit-temporal utility support", arrays[4][index]),
            ("pooled calibrated utility", arrays[5][index]),
        ):
            if not np.isfinite(value) or value < 0.0 or value > 1.0:
                raise ValueError(
                    f"EXP-056 {label} must be within [0, 1]"
                )
        if not np.isfinite(arrays[6][index]) or arrays[6][index] <= 0.0:
            raise ValueError(
                "EXP-056 directional raw utility must be positive"
            )

    if len(indices) < budget:
        return {
            "status": "BUDGET_UNAVAILABLE",
            "candidate_budget_anchor": budget,
            "eligible_selection_row_count": int(len(indices)),
            "selection_derived_residual_lower_tail_cutoff": None,
            "selection_derived_residual_breadth_cutoff": None,
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
            -float(arrays[5][i]),
            -float(arrays[6][i]),
            str(row_ids[i]),
        ),
    )
    cutoff_index = ranked[budget - 1]
    cutoff = tuple(float(array[cutoff_index]) for array in arrays)
    passing = _candidate_directions_residual_lower_tail(
        directions=directions,
        residual_lower_tail=arrays[0],
        residual_breadth=arrays[1],
        residual_bound_utility=arrays[2],
        feature_support=arrays[3],
        fit_temporal_support=arrays[4],
        pooled_calibrated_utility=arrays[5],
        raw_utility=arrays[6],
        residual_lower_tail_cutoff=cutoff[0],
        residual_breadth_cutoff=cutoff[1],
        residual_bound_cutoff=cutoff[2],
        feature_cutoff=cutoff[3],
        utility_cutoff=cutoff[4],
        pooled_cutoff=cutoff[5],
        raw_cutoff=cutoff[6],
    )
    return {
        "status": "AVAILABLE",
        "candidate_budget_anchor": budget,
        "eligible_selection_row_count": int(len(indices)),
        "selection_derived_residual_lower_tail_cutoff": cutoff[0],
        "selection_derived_residual_breadth_cutoff": cutoff[1],
        "selection_derived_residual_bound_cutoff": cutoff[2],
        "selection_derived_feature_support_cutoff": cutoff[3],
        "selection_derived_support_cutoff": cutoff[4],
        "selection_derived_pooled_calibrated_cutoff": cutoff[5],
        "selection_derived_raw_cutoff": cutoff[6],
        "selection_candidate_count_at_cutoff": int(
            np.count_nonzero(passing != "NO_TRADE")
        ),
    }


def _residual_lower_tail_consensus_digest(
    *,
    predecessor_digest: str,
    row_ids: Sequence[str],
    directions: np.ndarray,
    residual_lower_tail: np.ndarray,
) -> str:
    if not (
        len(row_ids)
        == len(directions)
        == len(residual_lower_tail)
    ):
        raise ValueError("EXP-056 consensus digest row mismatch")
    digest = hashlib.sha256()
    digest.update(str(predecessor_digest).encode("utf-8"))
    for row_id, direction, value in zip(
        row_ids,
        directions.tolist(),
        residual_lower_tail.tolist(),
        strict=True,
    ):
        for text_value in (str(row_id), str(direction)):
            encoded = text_value.encode("utf-8")
            digest.update(len(encoded).to_bytes(8, "big", signed=False))
            digest.update(encoded)
        digest.update(struct.pack(">d", float(value)))
    return digest.hexdigest()


def _score_fit_temporal_residual_lower_tail_consensus(
    *,
    fitted_models: Mapping[str, Mapping[str, object]],
    pooled_calibration_references: Mapping[str, Mapping[str, np.ndarray]],
    support_references: Mapping[
        str, Mapping[str, Mapping[str, np.ndarray]]
    ],
    feature_references: Mapping[
        str, Mapping[str, Mapping[str, np.ndarray]]
    ],
    residual_references: Mapping[
        str, Mapping[str, Mapping[str, float]]
    ],
    frame: pl.DataFrame,
    cell: ModelCell,
) -> tuple[
    np.ndarray,
    np.ndarray,
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
        residual_bound_utility,
        residual_breadth,
        predecessor_diagnostics,
        row_ids,
        predecessor_digest,
    ) = _predecessor._score_fit_temporal_residual_breadth_consensus(
        fitted_models=fitted_models,
        pooled_calibration_references=pooled_calibration_references,
        support_references=support_references,
        feature_references=feature_references,
        residual_references=residual_references,
        frame=frame,
        cell=cell,
    )
    view_predictions, view_prediction_digests, scored_row_ids = (
        _base._view_prediction_matrices(
            fitted_models=fitted_models,
            frame=frame,
            cell=cell,
        )
    )
    if tuple(row_ids) != tuple(scored_row_ids):
        raise ValueError(
            "EXP-056 predecessor/scored row identity drift"
        )
    residual_lower_tail = _fit_temporal_residual_lower_tail_mean(
        directions=directions,
        view_predictions=view_predictions,
        residual_references=residual_references,
    )
    eligible = np.isin(
        directions,
        np.asarray(["LONG", "SHORT"], dtype=object),
    )
    values = residual_lower_tail[eligible]
    if bool(eligible.any()) and not np.isfinite(values).all():
        raise ValueError(
            "EXP-056 eligible residual lower-tail mean is invalid"
        )
    diagnostics = {
        **dict(predecessor_diagnostics),
        "minimum_fit_temporal_residual_lower_tail_mean": (
            float(values.min()) if len(values) else None
        ),
        "maximum_fit_temporal_residual_lower_tail_mean": (
            float(values.max()) if len(values) else None
        ),
        "fit_temporal_residual_lower_tail_bound_count_per_row": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_BOUND_COUNT_PER_ROW
        ),
        "fit_temporal_residual_lower_tail_count": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_COUNT
        ),
        "residual_lower_tail_view_prediction_digests": (
            view_prediction_digests
        ),
    }
    digest = _residual_lower_tail_consensus_digest(
        predecessor_digest=predecessor_digest,
        row_ids=row_ids,
        directions=directions,
        residual_lower_tail=residual_lower_tail,
    )
    return (
        directions,
        raw_utility,
        pooled_calibrated_utility,
        fit_temporal_support,
        feature_support,
        residual_bound_utility,
        residual_breadth,
        residual_lower_tail,
        diagnostics,
        tuple(row_ids),
        digest,
    )


def _evaluate_residual_lower_tail_cutoff(
    frame: pl.DataFrame,
    *,
    directions: np.ndarray,
    residual_lower_tail: np.ndarray,
    residual_breadth: np.ndarray,
    residual_bound_utility: np.ndarray,
    feature_support: np.ndarray,
    fit_temporal_support: np.ndarray,
    pooled_calibrated_utility: np.ndarray,
    raw_utility: np.ndarray,
    residual_lower_tail_cutoff: float,
    residual_breadth_cutoff: float,
    residual_bound_cutoff: float,
    feature_cutoff: float,
    utility_cutoff: float,
    pooled_cutoff: float,
    raw_cutoff: float,
    budget: int,
    scenarios: Sequence[float],
    row_ids: Sequence[str],
) -> dict[str, object]:
    candidates = _candidate_directions_residual_lower_tail(
        directions=directions,
        residual_lower_tail=residual_lower_tail,
        residual_breadth=residual_breadth,
        residual_bound_utility=residual_bound_utility,
        feature_support=feature_support,
        fit_temporal_support=fit_temporal_support,
        pooled_calibrated_utility=pooled_calibrated_utility,
        raw_utility=raw_utility,
        residual_lower_tail_cutoff=residual_lower_tail_cutoff,
        residual_breadth_cutoff=residual_breadth_cutoff,
        residual_bound_cutoff=residual_bound_cutoff,
        feature_cutoff=feature_cutoff,
        utility_cutoff=utility_cutoff,
        pooled_cutoff=pooled_cutoff,
        raw_cutoff=raw_cutoff,
    )
    scenario_results: dict[str, object] = {}
    for scenario in scenarios:
        metrics = _base._base._financial_metrics(
            frame,
            candidates,
            scenario=float(scenario),
            row_ids=row_ids,
        )
        scenario_results[str(float(scenario))] = {
            "metrics": metrics,
            "gate": _base._base._financial_gate(metrics),
        }
    return {
        "candidate_budget_anchor": budget,
        "selection_derived_residual_lower_tail_cutoff": (
            residual_lower_tail_cutoff
        ),
        "selection_derived_residual_breadth_cutoff": residual_breadth_cutoff,
        "selection_derived_residual_bound_cutoff": residual_bound_cutoff,
        "selection_derived_feature_support_cutoff": feature_cutoff,
        "selection_derived_support_cutoff": utility_cutoff,
        "selection_derived_pooled_calibrated_cutoff": pooled_cutoff,
        "selection_derived_raw_cutoff": raw_cutoff,
        "scenarios": scenario_results,
    }


def _evaluate_temporal_stability_residual_lower_tail(
    *,
    selection_frame: pl.DataFrame,
    directions: np.ndarray,
    residual_lower_tail: np.ndarray,
    residual_breadth: np.ndarray,
    residual_bound_utility: np.ndarray,
    feature_support: np.ndarray,
    fit_temporal_support: np.ndarray,
    pooled_calibrated_utility: np.ndarray,
    raw_utility: np.ndarray,
    residual_lower_tail_cutoff: float,
    residual_breadth_cutoff: float,
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
        residual_lower_tail,
        residual_breadth,
        residual_bound_utility,
        feature_support,
        fit_temporal_support,
        pooled_calibrated_utility,
        raw_utility,
    )
    if any(len(value) != selection_frame.height for value in arrays):
        raise ValueError("EXP-056 stability row mismatch")
    windows: list[dict[str, object]] = []
    for raw_window in _base.TEMPORAL_STABILITY_WINDOWS:
        window = dict(raw_window)
        indices = _base._window_indices(
            selection_frame,
            start=_base._parse_utc_date(str(window["start"])),
            end_exclusive=_base._parse_utc_date(
                str(window["end_exclusive"])
            ),
        )
        frame = selection_frame[indices]
        index_array = np.asarray(indices, dtype=np.int64)
        row_ids = _base._base._row_identity(frame, cell=cell)
        evaluated = _evaluate_residual_lower_tail_cutoff(
            frame,
            directions=directions[index_array],
            residual_lower_tail=residual_lower_tail[index_array],
            residual_breadth=residual_breadth[index_array],
            residual_bound_utility=residual_bound_utility[index_array],
            feature_support=feature_support[index_array],
            fit_temporal_support=fit_temporal_support[index_array],
            pooled_calibrated_utility=pooled_calibrated_utility[index_array],
            raw_utility=raw_utility[index_array],
            residual_lower_tail_cutoff=residual_lower_tail_cutoff,
            residual_breadth_cutoff=residual_breadth_cutoff,
            residual_bound_cutoff=residual_bound_cutoff,
            feature_cutoff=feature_cutoff,
            utility_cutoff=utility_cutoff,
            pooled_cutoff=pooled_cutoff,
            raw_cutoff=raw_cutoff,
            budget=budget,
            scenarios=_base.SELECTION_GATE_SCENARIOS,
            row_ids=row_ids,
        )
        metrics = evaluated["scenarios"]["0.5"]["metrics"]
        gate = _base._window_gate(
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
            _base.MIN_STABILITY_WINDOW_CANDIDATE_SHARE
        ),
        "windows": windows,
    }


def _evaluate_forward_split_residual_lower_tail(
    *,
    fitted_models: Mapping[str, Mapping[str, object]],
    pooled_calibration_references: Mapping[str, Mapping[str, np.ndarray]],
    support_references: Mapping[
        str, Mapping[str, Mapping[str, np.ndarray]]
    ],
    feature_references: Mapping[
        str, Mapping[str, Mapping[str, np.ndarray]]
    ],
    residual_references: Mapping[
        str, Mapping[str, Mapping[str, float]]
    ],
    frame: pl.DataFrame,
    cell: ModelCell,
    residual_lower_tail_cutoff: float,
    residual_breadth_cutoff: float,
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
        residual_breadth,
        residual_lower_tail,
        diagnostics,
        row_ids,
        digest,
    ) = _score_fit_temporal_residual_lower_tail_consensus(
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
                *(float(value) for value in _base.DIAGNOSTIC_SCENARIOS),
                *(float(value) for value in gate_scenarios),
            }
        )
    )
    evaluated = _evaluate_residual_lower_tail_cutoff(
        frame,
        directions=directions,
        residual_lower_tail=residual_lower_tail,
        residual_breadth=residual_breadth,
        residual_bound_utility=residual_bound_utility,
        feature_support=feature_support,
        fit_temporal_support=fit_temporal_support,
        pooled_calibrated_utility=pooled_calibrated_utility,
        raw_utility=raw_utility,
        residual_lower_tail_cutoff=residual_lower_tail_cutoff,
        residual_breadth_cutoff=residual_breadth_cutoff,
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
        bool(
            evaluated["scenarios"][str(float(value))]["gate"]["passed"]
        )
        for value in gate_scenarios
    ]
    return {
        "status": "PASS" if all(gating) else "REJECT",
        "row_count": frame.height,
        "fit_temporal_residual_lower_tail_utility_consensus": diagnostics,
        "fit_temporal_residual_lower_tail_utility_consensus_digest": digest,
        **evaluated,
    }


def run_fit_temporal_residual_lower_tail_utility_model_cell_core(
    *,
    features: pl.DataFrame,
    outcomes: pl.DataFrame,
    cell: ModelCell,
) -> dict[str, object]:
    joined, processed_manifest_sha256 = (
        _base._base._validate_frames(
            features,
            outcomes,
            cell=cell,
        )
    )
    split_frames = {
        split.name: _base._base._split_frame(
            joined,
            split,
        )
        for split in _base.PROTOCOL_SPLITS
    }
    if any(frame.is_empty() for frame in split_frames.values()):
        empty = [
            name
            for name, frame in split_frames.items()
            if frame.is_empty()
        ]
        raise ValueError(
            f"EXP-056 model cell has empty required split(s): {empty}"
        )

    regime_frames = {
        split.name: _base._base._split_frame(
            joined,
            split,
        )
        for split in _base._predecessor_fit_regime_splits()
    }
    if set(regime_frames) != set(_base.PREDECESSOR_REGIME_NAMES):
        raise ValueError(
            "EXP-056 predecessor fit-regime identity drift"
        )
    if any(frame.is_empty() for frame in regime_frames.values()):
        empty = [
            name
            for name, frame in regime_frames.items()
            if frame.is_empty()
        ]
        raise ValueError(
            f"EXP-056 model cell has empty fit regime(s): {empty}"
        )

    view_frames = _base._build_jackknife_view_frames(
        regime_frames
    )
    fitted_models: dict[
        str,
        dict[str, _base._base.FittedMarketModel],
    ] = {}
    fit_evidence: dict[str, object] = {}
    view_regimes = _base._jackknife_view_regime_names()
    for view_name, fit_frame in view_frames.items():
        target_models: dict[
            str,
            _base._base.FittedMarketModel,
        ] = {}
        target_evidence: dict[str, object] = {}
        for target_column in _base.FINANCIAL_TARGET_COLUMNS:
            fitted = _base._predecessor_fit_regressor(
                fit_frame,
                target_column=target_column,
            )
            target_models[target_column] = fitted
            target_evidence[target_column] = {
                "status": "FITTED",
                "fit_attempt_count": 1,
                "target_summary": (
                    _base._predecessor_target_summary(
                        fit_frame,
                        target_column=target_column,
                    )
                ),
                "preprocessor_fingerprint": (
                    fitted.preprocessor_fingerprint
                ),
                "model_fingerprint": fitted.model_fingerprint,
            }

        included = view_regimes[view_name]
        excluded = tuple(
            value
            for value in _base.PREDECESSOR_REGIME_NAMES
            if value not in included
        )
        if len(excluded) != 1:
            raise ValueError(
                "EXP-056 jackknife excluded-regime count drift"
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
        pooled_calibration_references,
        pooled_calibration_evidence,
    ) = _base._build_calibration_references(
        fitted_models=fitted_models,
        regime_frames=regime_frames,
        cell=cell,
    )
    (
        support_references,
        support_evidence,
    ) = _base._build_fit_temporal_support_references(
        fitted_models=fitted_models,
        regime_frames=regime_frames,
        cell=cell,
    )
    (
        feature_references,
        feature_evidence,
    ) = _base._build_fit_temporal_feature_support_references(
        fitted_models=fitted_models,
        regime_frames=regime_frames,
    )
    (
        residual_references,
        residual_evidence,
    ) = _base._build_fit_temporal_residual_references(
        fitted_models=fitted_models,
        regime_frames=regime_frames,
        cell=cell,
    )

    selection_frame = split_frames[
        _base.SELECTION_SPLIT.name
    ]
    (
        selection_directions,
        selection_raw_utility,
        selection_pooled_calibrated_utility,
        selection_fit_temporal_support,
        selection_feature_support,
        selection_residual_bound_utility,
        selection_residual_breadth,
        selection_residual_lower_tail,
        selection_diagnostics,
        selection_row_ids,
        selection_consensus_digest,
    ) = _score_fit_temporal_residual_lower_tail_consensus(
        fitted_models=fitted_models,
        pooled_calibration_references=pooled_calibration_references,
        support_references=support_references,
        feature_references=feature_references,
        residual_references=residual_references,
        frame=selection_frame,
        cell=cell,
    )

    variants: list[dict[str, object]] = []
    for budget in _base.CANDIDATE_BUDGET_ANCHORS:
        cutoff_record = _derive_residual_lower_tail_cutoff(
            directions=selection_directions,
            residual_lower_tail=selection_residual_lower_tail,
            residual_breadth=selection_residual_breadth,
            residual_bound_utility=(
                selection_residual_bound_utility
            ),
            feature_support=selection_feature_support,
            fit_temporal_support=selection_fit_temporal_support,
            pooled_calibrated_utility=(
                selection_pooled_calibrated_utility
            ),
            raw_utility=selection_raw_utility,
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
                    "evaluation_status": "BUDGET_UNAVAILABLE",
                    **cutoff_record,
                    "aggregate_selection_gate_passed": False,
                    "temporal_stability": {
                        "status": "BUDGET_UNAVAILABLE",
                        (
                            "minimum_directional_candidate_"
                            "share_per_window"
                        ): (
                            _predecessor
                            .MIN_STABILITY_WINDOW_CANDIDATE_SHARE
                        ),
                        "windows": [],
                    },
                    "selection_gate_passed": False,
                }
            )
            continue

        residual_lower_tail_cutoff = float(
            cutoff_record[
                "selection_derived_residual_lower_tail_cutoff"
            ]
        )
        residual_breadth_cutoff = float(
            cutoff_record[
                "selection_derived_residual_breadth_cutoff"
            ]
        )
        residual_bound_cutoff = float(
            cutoff_record[
                "selection_derived_residual_bound_cutoff"
            ]
        )
        feature_cutoff = float(
            cutoff_record[
                "selection_derived_feature_support_cutoff"
            ]
        )
        utility_cutoff = float(
            cutoff_record["selection_derived_support_cutoff"]
        )
        pooled_cutoff = float(
            cutoff_record[
                "selection_derived_pooled_calibrated_cutoff"
            ]
        )
        raw_cutoff = float(
            cutoff_record["selection_derived_raw_cutoff"]
        )

        evaluated = _evaluate_residual_lower_tail_cutoff(
            selection_frame,
            directions=selection_directions,
            residual_lower_tail=selection_residual_lower_tail,
            residual_breadth=selection_residual_breadth,
            residual_bound_utility=(
                selection_residual_bound_utility
            ),
            feature_support=selection_feature_support,
            fit_temporal_support=selection_fit_temporal_support,
            pooled_calibrated_utility=(
                selection_pooled_calibrated_utility
            ),
            raw_utility=selection_raw_utility,
            residual_lower_tail_cutoff=residual_lower_tail_cutoff,
            residual_lower_tail_cutoff=residual_lower_tail_cutoff,
        residual_breadth_cutoff=residual_breadth_cutoff,
            residual_bound_cutoff=residual_bound_cutoff,
            feature_cutoff=feature_cutoff,
            utility_cutoff=utility_cutoff,
            pooled_cutoff=pooled_cutoff,
            raw_cutoff=raw_cutoff,
            budget=budget,
            scenarios=_base.SELECTION_GATE_SCENARIOS,
            row_ids=selection_row_ids,
        )
        scenario = evaluated["scenarios"]["0.5"]
        aggregate_passed = bool(
            scenario["gate"]["passed"]
        )
        full_count = int(
            scenario["metrics"]["directional_candidate_count"]
        )
        if aggregate_passed:
            stability = (
                _evaluate_temporal_stability_residual_lower_tail(
                    selection_frame=selection_frame,
                    directions=selection_directions,
                    residual_lower_tail=selection_residual_lower_tail,
                    residual_breadth=selection_residual_breadth,
                    residual_bound_utility=(
                        selection_residual_bound_utility
                    ),
                    feature_support=selection_feature_support,
                    fit_temporal_support=(
                        selection_fit_temporal_support
                    ),
                    pooled_calibrated_utility=(
                        selection_pooled_calibrated_utility
                    ),
                    raw_utility=selection_raw_utility,
                    residual_lower_tail_cutoff=(
                        residual_lower_tail_cutoff
                    ),
                    residual_breadth_cutoff=(
                        residual_breadth_cutoff
                    ),
                    residual_bound_cutoff=residual_bound_cutoff,
                    feature_cutoff=feature_cutoff,
                    utility_cutoff=utility_cutoff,
                    pooled_cutoff=pooled_cutoff,
                    raw_cutoff=raw_cutoff,
                    budget=budget,
                    cell=cell,
                    full_selection_candidate_count=full_count,
                )
            )
            stability_passed = stability["status"] == "PASS"
        else:
            stability = {
                "status": "LOCKED_AGGREGATE_REJECT",
                (
                    "minimum_directional_candidate_share_per_window"
                ): (
                    _predecessor
                    .MIN_STABILITY_WINDOW_CANDIDATE_SHARE
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
                    aggregate_passed and stability_passed
                ),
            }
        )

    passing = [
        row
        for row in variants
        if row["selection_gate_passed"]
    ]
    selected = (
        max(passing, key=_base._selection_key)
        if passing
        else None
    )

    result: dict[str, object] = {
        "experiment_id": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_EXPERIMENT_ID
        ),
        "training_core_version": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_TRAINING_CORE_DECISION
        ),
        "dec198_merged_commit": DEC209_MERGED_COMMIT,
        "dec198_protocol_blob_sha": DEC209_PROTOCOL_BLOB_SHA,
        "predecessor_training_core_blob_sha": (
            PREDECESSOR_TRAINING_CORE_BLOB_SHA
        ),
        "predecessor_training_core_decision": (
            _predecessor
            .FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_DECISION
        ),
        "protocol_decision": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_PROTOCOL_DECISION
        ),
        "protocol_version": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_PROTOCOL_VERSION
        ),
        "protocol_fingerprint": (
            fit_temporal_residual_lower_tail_utility_protocol_fingerprint()
        ),
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
        "split_row_counts": {
            name: frame.height
            for name, frame in split_frames.items()
        },
        "fit": {
            "jackknife_models": fit_evidence,
            "jackknife_view_count": len(fitted_models),
            "regressor_count": sum(
                len(value)
                for value in fitted_models.values()
            ),
            "out_of_fit_calibration_references": (
                pooled_calibration_evidence
            ),
            "calibration_reference_count": sum(
                len(value)
                for value in pooled_calibration_references.values()
            ),
            "calibration_reference_rule": (
                _base.CALIBRATION_REFERENCE_RULE
            ),
            "calibrated_percentile_rule": (
                _base.CALIBRATED_PERCENTILE_RULE
            ),
            "robust_calibrated_score_rule": (
                _base.ROBUST_CALIBRATED_SCORE_RULE
            ),
            "fit_temporal_support_references": support_evidence,
            "fit_temporal_support_reference_count": (
                _predecessor
                .FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL
            ),
            "fit_temporal_support_reference_rule": (
                _base.FIT_TEMPORAL_SUPPORT_REFERENCE_RULE
            ),
            "fit_temporal_support_percentile_rule": (
                _base.FIT_TEMPORAL_SUPPORT_PERCENTILE_RULE
            ),
            "robust_fit_temporal_support_score_rule": (
                _predecessor
                .ROBUST_FIT_TEMPORAL_SUPPORT_SCORE_RULE
            ),
            "fit_temporal_feature_support_references": (
                feature_evidence
            ),
            "fit_temporal_feature_support_reference_count": (
                _predecessor
                .FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL
            ),
            "fit_temporal_feature_reference_rule": (
                _base.FIT_TEMPORAL_FEATURE_REFERENCE_RULE
            ),
            "fit_temporal_feature_distance_rule": (
                _base.FIT_TEMPORAL_FEATURE_DISTANCE_RULE
            ),
            "fit_temporal_feature_support_percentile_rule": (
                _predecessor
                .FIT_TEMPORAL_FEATURE_SUPPORT_PERCENTILE_RULE
            ),
            "robust_fit_temporal_feature_support_score_rule": (
                _predecessor
                .ROBUST_FIT_TEMPORAL_FEATURE_SUPPORT_SCORE_RULE
            ),
            "fit_temporal_residual_references": residual_evidence,
            "fit_temporal_residual_reference_count": (
                _predecessor
                .FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL
            ),
            "fit_temporal_residual_reference_rule": (
                _base.FIT_TEMPORAL_RESIDUAL_REFERENCE_RULE
            ),
            "residual_downside_quantile_rule": (
                _base.RESIDUAL_DOWNSIDE_QUANTILE_RULE
            ),
            "robust_residual_bound_utility_rule": (
                _base.ROBUST_RESIDUAL_BOUND_UTILITY_RULE
            ),
            "residual_bound_eligibility_rule": (
                _base.RESIDUAL_BOUND_ELIGIBILITY_RULE
            ),
            "fit_temporal_residual_breadth_rule": (
                _predecessor.FIT_TEMPORAL_RESIDUAL_BREADTH_RULE
            ),
            "residual_breadth_positivity_rule": (
                _predecessor.RESIDUAL_BREADTH_POSITIVITY_RULE
            ),
            "residual_breadth_eligibility_rule": (
                _predecessor.RESIDUAL_BREADTH_ELIGIBILITY_RULE
            ),
            "fit_temporal_residual_breadth_bound_count_per_row": (
                _predecessor.FIT_TEMPORAL_RESIDUAL_BREADTH_BOUND_COUNT_PER_ROW
            ),
            "fit_temporal_residual_lower_tail_rule": (
                FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_RULE
            ),
            "residual_lower_tail_eligibility_rule": (
                RESIDUAL_LOWER_TAIL_ELIGIBILITY_RULE
            ),
            "fit_temporal_residual_lower_tail_bound_count_per_row": (
                FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_BOUND_COUNT_PER_ROW
            ),
            "fit_temporal_residual_lower_tail_count": (
                FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_COUNT
            ),
            "full_fit_single_model": {
                "status": (
                    "FORBIDDEN_BY_DEC150_DEC163_DEC174_DEC185_DEC198_DEC209"
                ),
                "fit_attempt_count": 0,
            },
            "view_weight_search": {
                "status": (
                    "FORBIDDEN_BY_DEC150_DEC163_DEC174_DEC185_DEC198_DEC209"
                ),
                "fit_attempt_count": 0,
            },
            "view_fallback": {
                "status": (
                    "FORBIDDEN_BY_DEC150_DEC163_DEC174_DEC185_DEC198_DEC209"
                ),
                "fit_attempt_count": 0,
            },
            "selection_window_calibration": {
                "status": (
                    "FORBIDDEN_BY_DEC150_DEC163_DEC174_DEC185_DEC198_DEC209"
                ),
                "fit_attempt_count": 0,
            },
            "hist_gradient_boosting_classifier": {
                "status": (
                    "EXCLUDED_BY_DEC150_DEC163_DEC174_DEC185_DEC198_DEC209"
                ),
                "fit_attempt_count": 0,
            },
            "logistic_regression": {
                "status": (
                    "EXCLUDED_BY_DEC112_DEC150_DEC163_DEC174_DEC185_DEC198_DEC209"
                ),
                "fit_attempt_count": 0,
            },
        },
        "selection": {
            "status": (
                "SELECTED"
                if selected is not None
                else (
                    "NO_FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_"
                    "STABLE_MODEL_CHALLENGER"
                )
            ),
            "row_count": selection_frame.height,
            "fit_temporal_residual_lower_tail_utility_consensus": (
                selection_diagnostics
            ),
            "fit_temporal_residual_lower_tail_utility_consensus_digest": (
                selection_consensus_digest
            ),
            "ranking_rule": RANKING_RULE,
            "selection_cutoff_rule": SELECTION_CUTOFF_RULE,
            "cutoff_tie_policy": CUTOFF_TIE_POLICY,
            "forward_application_rule": FORWARD_APPLICATION_RULE,
            "variants": variants,
            "selected_variant": (
                {
                    "model_family": (
                        "hist_gradient_boosting_regression"
                    ),
                    "candidate_budget_anchor": int(
                        selected["candidate_budget_anchor"]
                    ),
                    "selection_derived_residual_lower_tail_cutoff": float(
                        selected[
                            "selection_derived_residual_lower_tail_cutoff"
                        ]
                    ),
                    "selection_derived_residual_breadth_cutoff": float(
                        selected[
                            "selection_derived_residual_breadth_cutoff"
                        ]
                    ),
                    "selection_derived_residual_bound_cutoff": float(
                        selected[
                            "selection_derived_residual_bound_cutoff"
                        ]
                    ),
                    "selection_derived_feature_support_cutoff": float(
                        selected[
                            "selection_derived_feature_support_cutoff"
                        ]
                    ),
                    "selection_derived_support_cutoff": float(
                        selected["selection_derived_support_cutoff"]
                    ),
                    (
                        "selection_derived_pooled_calibrated_cutoff"
                    ): float(
                        selected[
                            "selection_derived_pooled_calibrated_cutoff"
                        ]
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
        "retrospective_holdout": {
            "status": "LOCKED_NO_SELECTION"
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
        result["result_fingerprint"] = _sha256(result)
        return result

    residual_lower_tail_cutoff = float(
        selected["selection_derived_residual_lower_tail_cutoff"]
    )
    residual_breadth_cutoff = float(
        selected["selection_derived_residual_breadth_cutoff"]
    )
    residual_bound_cutoff = float(
        selected["selection_derived_residual_bound_cutoff"]
    )
    feature_cutoff = float(
        selected["selection_derived_feature_support_cutoff"]
    )
    utility_cutoff = float(
        selected["selection_derived_support_cutoff"]
    )
    pooled_cutoff = float(
        selected["selection_derived_pooled_calibrated_cutoff"]
    )
    raw_cutoff = float(
        selected["selection_derived_raw_cutoff"]
    )
    budget = int(selected["candidate_budget_anchor"])

    validation = _evaluate_forward_split_residual_lower_tail(
        fitted_models=fitted_models,
        pooled_calibration_references=pooled_calibration_references,
        support_references=support_references,
        feature_references=feature_references,
        residual_references=residual_references,
        frame=split_frames[
            _base.VALIDATION_SPLIT.name
        ],
        cell=cell,
        residual_breadth_cutoff=residual_breadth_cutoff,
        residual_bound_cutoff=residual_bound_cutoff,
        feature_cutoff=feature_cutoff,
        utility_cutoff=utility_cutoff,
        pooled_cutoff=pooled_cutoff,
        raw_cutoff=raw_cutoff,
        budget=budget,
        gate_scenarios=(
            _base.VALIDATION_GATE_SCENARIOS
        ),
    )
    result["validation"] = validation
    if validation["status"] != "PASS":
        result["retrospective_holdout"] = {
            "status": "LOCKED_VALIDATION_REJECT"
        }
        result["result_fingerprint"] = _sha256(result)
        return result

    result["retrospective_holdout"] = (
        _evaluate_forward_split_residual_lower_tail(
            fitted_models=fitted_models,
            pooled_calibration_references=(
                pooled_calibration_references
            ),
            support_references=support_references,
            feature_references=feature_references,
            residual_references=residual_references,
            frame=split_frames[
                _base.RETROSPECTIVE_HOLDOUT_SPLIT.name
            ],
            cell=cell,
            residual_breadth_cutoff=residual_breadth_cutoff,
            residual_bound_cutoff=residual_bound_cutoff,
            feature_cutoff=feature_cutoff,
            utility_cutoff=utility_cutoff,
            pooled_cutoff=pooled_cutoff,
            raw_cutoff=raw_cutoff,
            budget=budget,
            gate_scenarios=(
                _base.HOLDOUT_GATE_SCENARIOS
            ),
        )
    )
    result["result_fingerprint"] = _sha256(result)
    return result



def build_fit_temporal_residual_lower_tail_training_core_gate(
) -> dict[str, object]:
    return {
        "experiment_id": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_EXPERIMENT_ID
        ),
        "training_core_version": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_TRAINING_CORE_DECISION
        ),
        "protocol_decision": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_PROTOCOL_DECISION
        ),
        "protocol_version": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_PROTOCOL_VERSION
        ),
        "protocol_fingerprint": (
            fit_temporal_residual_lower_tail_utility_protocol_fingerprint()
        ),
        "residual_reference_count_per_cell": (
            _base.FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL
        ),
        "residual_breadth_bound_count_per_row": (
            _predecessor.FIT_TEMPORAL_RESIDUAL_BREADTH_BOUND_COUNT_PER_ROW
        ),
        "residual_lower_tail_bound_count_per_row": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_BOUND_COUNT_PER_ROW
        ),
        "residual_lower_tail_count": FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_COUNT,
        "residual_lower_tail_fraction": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_FRACTION
        ),
        "residual_lower_tail_authorized": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_AUTHORIZED
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
    "DEC209_MERGED_COMMIT",
    "DEC209_PROTOCOL_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_RESULT_EXECUTION_AUTHORIZED",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_TRAINING_CORE_DECISION",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_TRAINING_CORE_VERSION",
    "LIVE_ORDER_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "PREDECESSOR_TRAINING_CORE_BLOB_SHA",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "_candidate_directions_residual_lower_tail",
    "_derive_residual_lower_tail_cutoff",
    "_fit_temporal_residual_lower_tail_mean",
    "_score_fit_temporal_residual_lower_tail_consensus",
    "run_fit_temporal_residual_lower_tail_utility_model_cell_core",
    "build_fit_temporal_residual_lower_tail_training_core_gate",
    "validate_fit_temporal_residual_lower_tail_utility_training_sources",
]
