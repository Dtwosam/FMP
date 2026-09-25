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
from .model_successor_fit_temporal_support_utility_protocol import (
    CUTOFF_TIE_POLICY,
    FIT_TEMPORAL_SUPPORT_PERCENTILE_RULE,
    FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL,
    FIT_TEMPORAL_SUPPORT_REFERENCE_RULE,
    FIT_TEMPORAL_SUPPORT_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_VERSION,
    FIT_TEMPORAL_SUPPORT_WINDOWS,
    FORWARD_APPLICATION_RULE,
    PRIOR_RESULT_INFORMED,
    RANKING_RULE,
    ROBUST_FIT_TEMPORAL_SUPPORT_SCORE_RULE,
    SELECTION_CUTOFF_RULE,
    SUPPORT_REFERENCE_WINDOWS_PER_EXCLUDED_REGIME,
    UNTOUCHED_OOS,
    fit_temporal_support_utility_protocol_fingerprint,
)
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
    MODEL_FIT_AUTHORIZED as PREDECESSOR_MODEL_FIT_AUTHORIZED,
    TEMPORAL_CALIBRATED_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    TEMPORAL_CALIBRATED_UTILITY_TRAINING_CORE_DECISION,
    TEMPORAL_CALIBRATED_UTILITY_TRAINING_CORE_VERSION,
    _build_calibration_references,
    _empirical_percentiles,
    _reference_digest,
    _score_raw_view_matrices,
    validate_temporal_calibrated_utility_training_sources,
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
    _selection_key,
    _temporal_jackknife_utility_direction_score,
)


FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_VERSION = (
    "fmp-exp052-fit-temporal-support-utility-training-core-v1"
)
FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_DECISION = "DEC-164"

DEC163_MERGED_COMMIT = (
    "9108cd170b2eccf73bddb6cbf8d6d7118dbd9cd1"
)
DEC163_PROTOCOL_BLOB_SHA = (
    "01d5080560ec5d41653694b4df086ff2f10e770d"
)
PREDECESSOR_TRAINING_CORE_BLOB_SHA = (
    "959fbfd52f41c08de3c1a26769e0e7fd2545b92a"
)

FIT_TEMPORAL_SUPPORT_UTILITY_RESULT_EXECUTION_AUTHORIZED = False
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


def validate_fit_temporal_support_utility_training_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "dec163_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_support_utility_protocol.py",
            DEC163_PROTOCOL_BLOB_SHA,
        ),
        "predecessor_training_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_temporal_calibrated_utility_training.py",
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(
                f"missing EXP-052 training dependency: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-052 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    predecessor = (
        validate_temporal_calibrated_utility_training_sources(
            repository_root=root,
        )
    )
    if predecessor[
        "temporal_calibrated_utility_training_core_decision"
    ] != TEMPORAL_CALIBRATED_UTILITY_TRAINING_CORE_DECISION:
        raise ValueError(
            "EXP-052 predecessor training decision drift"
        )
    if predecessor["model_fit_authorized"] is not False:
        raise ValueError(
            "EXP-052 predecessor model fit must remain closed"
        )
    if predecessor[
        "temporal_calibrated_utility_result_execution_authorized"
    ] is not False:
        raise ValueError(
            "EXP-052 predecessor result execution must remain closed"
        )
    if PREDECESSOR_MODEL_FIT_AUTHORIZED is not False:
        raise ValueError(
            "EXP-052 predecessor source fit authorization drift"
        )
    if (
        TEMPORAL_CALIBRATED_UTILITY_RESULT_EXECUTION_AUTHORIZED
        is not False
    ):
        raise ValueError(
            "EXP-052 predecessor source execution authorization drift"
        )

    fingerprint = (
        fit_temporal_support_utility_protocol_fingerprint()
    )
    if len(fingerprint) != 64:
        raise ValueError(
            "EXP-052 protocol fingerprint is invalid"
        )

    return {
        "fit_temporal_support_utility_training_core_version": (
            FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_VERSION
        ),
        "fit_temporal_support_utility_training_core_decision": (
            FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_DECISION
        ),
        "dec163_merged_commit": DEC163_MERGED_COMMIT,
        "dec163_protocol_blob_sha": actual[
            "dec163_protocol"
        ],
        "predecessor_training_core_blob_sha": actual[
            "predecessor_training_core"
        ],
        "predecessor_training_core_decision": (
            TEMPORAL_CALIBRATED_UTILITY_TRAINING_CORE_DECISION
        ),
        "predecessor_training_core_version": (
            TEMPORAL_CALIBRATED_UTILITY_TRAINING_CORE_VERSION
        ),
        "fit_temporal_support_utility_protocol_fingerprint": (
            fingerprint
        ),
        "fit_temporal_support_utility_result_execution_authorized": (
            False
        ),
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
    }


def _support_windows_by_parent(
) -> dict[str, tuple[dict[str, object], ...]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for raw in FIT_TEMPORAL_SUPPORT_WINDOWS:
        window = dict(raw)
        parent = str(window["parent_regime"])
        grouped.setdefault(parent, []).append(window)

    result = {
        parent: tuple(windows)
        for parent, windows in grouped.items()
    }
    if set(result) != set(PREDECESSOR_REGIME_NAMES):
        raise ValueError(
            "EXP-052 support parent-regime inventory mismatch"
        )
    if any(
        len(windows)
        != SUPPORT_REFERENCE_WINDOWS_PER_EXCLUDED_REGIME
        for windows in result.values()
    ):
        raise ValueError(
            "EXP-052 support-window count per regime mismatch"
        )
    return result


def _support_reference_digest(
    values: np.ndarray,
) -> str:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1 or array.size == 0:
        raise ValueError(
            "EXP-052 support reference must be non-empty 1D"
        )
    if not np.isfinite(array).all():
        raise ValueError(
            "EXP-052 support reference must be finite"
        )
    if np.any(array[1:] < array[:-1]):
        raise ValueError(
            "EXP-052 support reference must be sorted"
        )
    return _reference_digest(array)


def _build_fit_temporal_support_references(
    *,
    fitted_models: Mapping[
        str,
        Mapping[str, _base.FittedMarketModel],
    ],
    regime_frames: Mapping[str, pl.DataFrame],
    cell: ModelCell,
) -> tuple[
    dict[
        str,
        dict[
            str,
            dict[str, np.ndarray],
        ],
    ],
    dict[str, object],
]:
    view_regimes = _jackknife_view_regime_names()
    if set(fitted_models) != set(view_regimes):
        raise ValueError(
            "EXP-052 fitted jackknife model set mismatch"
        )
    if set(regime_frames) != set(PREDECESSOR_REGIME_NAMES):
        raise ValueError(
            "EXP-052 support regime frame set mismatch"
        )

    windows_by_parent = _support_windows_by_parent()
    references: dict[
        str,
        dict[
            str,
            dict[str, np.ndarray],
        ],
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
                "EXP-052 support excluded-regime count drift"
            )
        excluded_name = excluded[0]
        frame = regime_frames[excluded_name]
        if frame.is_empty():
            raise ValueError(
                "EXP-052 support excluded regime is empty"
            )

        target_models = fitted_models[view_name]
        if set(target_models) != set(FINANCIAL_TARGET_COLUMNS):
            raise ValueError(
                "EXP-052 support target model set mismatch"
            )

        window_frames: dict[str, pl.DataFrame] = {}
        window_meta: dict[str, dict[str, object]] = {}
        for window in windows_by_parent[excluded_name]:
            name = str(window["name"])
            start = _parse_utc_date(str(window["start"]))
            end_exclusive = _parse_utc_date(
                str(window["end_exclusive"])
            )
            indices = _window_indices(
                frame,
                start=start,
                end_exclusive=end_exclusive,
            )
            window_frame = frame[indices]
            if window_frame.is_empty():
                raise ValueError(
                    "EXP-052 support half-year is empty: "
                    f"{view_name} {name}"
                )
            window_frames[name] = window_frame
            window_meta[name] = {
                "name": name,
                "parent_regime": excluded_name,
                "start": str(window["start"]),
                "end_exclusive": str(
                    window["end_exclusive"]
                ),
                "row_count": window_frame.height,
            }

        target_references: dict[
            str,
            dict[str, np.ndarray],
        ] = {}
        target_evidence: dict[str, object] = {}

        for target_column in FINANCIAL_TARGET_COLUMNS:
            model = target_models[target_column]
            window_references: dict[
                str,
                np.ndarray,
            ] = {}
            window_evidence: dict[str, object] = {}

            for window_name, window_frame in (
                window_frames.items()
            ):
                predictions, prediction_digest, row_ids = (
                    _predecessor_score_regressor(
                        model,
                        window_frame,
                        cell=cell,
                    )
                )
                if len(row_ids) != window_frame.height:
                    raise ValueError(
                        "EXP-052 support row identity count mismatch"
                    )
                sorted_reference = np.sort(
                    np.asarray(
                        predictions,
                        dtype=np.float64,
                    )
                )
                if sorted_reference.size == 0:
                    raise ValueError(
                        "EXP-052 support reference is empty"
                    )
                if not np.isfinite(
                    sorted_reference
                ).all():
                    raise ValueError(
                        "EXP-052 support reference is non-finite"
                    )

                window_references[
                    window_name
                ] = sorted_reference
                meta = window_meta[window_name]
                window_evidence[window_name] = {
                    **meta,
                    "status": "FROZEN",
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
                        _support_reference_digest(
                            sorted_reference
                        )
                    ),
                }

            if len(window_references) != (
                SUPPORT_REFERENCE_WINDOWS_PER_EXCLUDED_REGIME
            ):
                raise ValueError(
                    "EXP-052 support target window count drift"
                )
            target_references[
                target_column
            ] = window_references
            target_evidence[target_column] = {
                "status": "FROZEN",
                "excluded_regime": excluded_name,
                "window_count": len(
                    window_references
                ),
                "windows": window_evidence,
            }

        references[view_name] = target_references
        evidence[view_name] = {
            "status": "FROZEN",
            "included_regimes": list(included),
            "excluded_regime": excluded_name,
            "target_count": len(target_references),
            "support_reference_count": sum(
                len(value)
                for value in target_references.values()
            ),
            "targets": target_evidence,
        }

    total = sum(
        len(window_refs)
        for targets in references.values()
        for window_refs in targets.values()
    )
    if total != FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL:
        raise ValueError(
            "EXP-052 total support-reference count drift"
        )
    return references, evidence


def _fit_temporal_support_consensus_digest(
    *,
    row_ids: Sequence[str],
    directions: np.ndarray,
    raw_utility: np.ndarray,
    pooled_calibrated_utility: np.ndarray,
    fit_temporal_support: np.ndarray,
) -> str:
    if not (
        len(row_ids)
        == len(directions)
        == len(raw_utility)
        == len(pooled_calibrated_utility)
        == len(fit_temporal_support)
    ):
        raise ValueError(
            "EXP-052 consensus digest row mismatch"
        )

    digest = hashlib.sha256()
    for (
        row_id,
        direction,
        raw_value,
        pooled_value,
        support_value,
    ) in zip(
        row_ids,
        directions.tolist(),
        raw_utility.tolist(),
        pooled_calibrated_utility.tolist(),
        fit_temporal_support.tolist(),
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
                struct.pack(">d", float(pooled_value))
            )
            digest.update(
                struct.pack(">d", float(support_value))
            )
        else:
            digest.update(
                b"NO_FIT_TEMPORAL_SUPPORT_UTILITY"
            )
    return digest.hexdigest()


def _fit_temporal_support_diagnostics(
    *,
    directions: np.ndarray,
    raw_utility: np.ndarray,
    pooled_calibrated_utility: np.ndarray,
    fit_temporal_support: np.ndarray,
    view_prediction_digests: Mapping[
        str,
        Mapping[str, str],
    ],
) -> dict[str, object]:
    if not (
        len(directions)
        == len(raw_utility)
        == len(pooled_calibrated_utility)
        == len(fit_temporal_support)
    ):
        raise ValueError(
            "EXP-052 diagnostic row mismatch"
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
    eligible_indices = [
        index
        for index, direction in enumerate(
            directions.tolist()
        )
        if direction in {"LONG", "SHORT"}
    ]

    def bounds(
        values: np.ndarray,
    ) -> tuple[float | None, float | None]:
        finite = [
            float(values[index])
            for index in eligible_indices
        ]
        return (
            (min(finite), max(finite))
            if finite
            else (None, None)
        )

    raw_min, raw_max = bounds(raw_utility)
    pooled_min, pooled_max = bounds(
        pooled_calibrated_utility
    )
    support_min, support_max = bounds(
        fit_temporal_support
    )

    return {
        "row_count": len(directions),
        "consensus_direction_counts": counts,
        "consensus_eligible_row_count": eligible,
        "consensus_eligible_rate": (
            float(eligible / len(directions))
            if len(directions)
            else 0.0
        ),
        "minimum_robust_raw_utility": raw_min,
        "maximum_robust_raw_utility": raw_max,
        "minimum_robust_pooled_calibrated_utility": (
            pooled_min
        ),
        "maximum_robust_pooled_calibrated_utility": (
            pooled_max
        ),
        "minimum_robust_fit_temporal_support": (
            support_min
        ),
        "maximum_robust_fit_temporal_support": (
            support_max
        ),
        "view_prediction_digests": {
            view: dict(values)
            for view, values in (
                view_prediction_digests.items()
            )
        },
    }


def _score_fit_temporal_support_consensus(
    *,
    fitted_models: Mapping[
        str,
        Mapping[str, _base.FittedMarketModel],
    ],
    pooled_calibration_references: Mapping[
        str,
        Mapping[str, np.ndarray],
    ],
    support_references: Mapping[
        str,
        Mapping[
            str,
            Mapping[str, np.ndarray],
        ],
    ],
    frame: pl.DataFrame,
    cell: ModelCell,
) -> tuple[
    np.ndarray,
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

    if set(pooled_calibration_references) != set(
        view_names
    ):
        raise ValueError(
            "EXP-052 pooled reference view set mismatch"
        )
    if set(support_references) != set(view_names):
        raise ValueError(
            "EXP-052 support reference view set mismatch"
        )

    directions, raw_utility = (
        _temporal_jackknife_utility_direction_score(
            raw_matrices
        )
    )

    pooled_matrices: list[np.ndarray] = []
    support_by_view_target: dict[
        tuple[str, int],
        list[np.ndarray],
    ] = {}

    for view_name, raw_matrix in zip(
        view_names,
        raw_matrices,
        strict=True,
    ):
        pooled_targets = pooled_calibration_references[
            view_name
        ]
        support_targets = support_references[view_name]
        if set(pooled_targets) != set(
            FINANCIAL_TARGET_COLUMNS
        ):
            raise ValueError(
                "EXP-052 pooled target reference set mismatch"
            )
        if set(support_targets) != set(
            FINANCIAL_TARGET_COLUMNS
        ):
            raise ValueError(
                "EXP-052 support target reference set mismatch"
            )

        pooled_columns: list[np.ndarray] = []
        for target_index, target_column in enumerate(
            FINANCIAL_TARGET_COLUMNS
        ):
            pooled_columns.append(
                _empirical_percentiles(
                    pooled_targets[target_column],
                    raw_matrix[:, target_index],
                )
            )

            window_refs = support_targets[
                target_column
            ]
            if len(window_refs) != (
                SUPPORT_REFERENCE_WINDOWS_PER_EXCLUDED_REGIME
            ):
                raise ValueError(
                    "EXP-052 support window reference count mismatch"
                )
            support_by_view_target[
                (view_name, target_index)
            ] = [
                _empirical_percentiles(
                    reference,
                    raw_matrix[:, target_index],
                )
                for _, reference in sorted(
                    window_refs.items()
                )
            ]

        pooled_matrices.append(
            np.column_stack(pooled_columns)
        )

    pooled_calibrated_utility = np.full(
        len(directions),
        float("-inf"),
        dtype=np.float64,
    )
    fit_temporal_support = np.full(
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

        pooled_selected = np.column_stack(
            [
                matrix[mask, target_index]
                for matrix in pooled_matrices
            ]
        )
        pooled_calibrated_utility[mask] = np.min(
            pooled_selected,
            axis=1,
        )

        support_columns: list[np.ndarray] = []
        for view_name in view_names:
            for values in support_by_view_target[
                (view_name, target_index)
            ]:
                support_columns.append(values[mask])
        support_selected = np.column_stack(
            support_columns
        )
        if support_selected.shape[1] != (
            REQUIRED_SUPPORT_COMPARISON_COUNT
        ):
            raise ValueError(
                "EXP-052 support comparison count drift"
            )
        fit_temporal_support[mask] = np.min(
            support_selected,
            axis=1,
        )

    eligible_mask = np.isin(
        directions,
        np.asarray(
            ["LONG", "SHORT"],
            dtype=object,
        ),
    )
    if bool(eligible_mask.any()):
        raw_values = raw_utility[eligible_mask]
        pooled_values = pooled_calibrated_utility[
            eligible_mask
        ]
        support_values = fit_temporal_support[
            eligible_mask
        ]
        if (
            not np.isfinite(raw_values).all()
            or (raw_values <= 0.0).any()
        ):
            raise ValueError(
                "EXP-052 eligible raw utility must be finite and positive"
            )
        for label, values in (
            ("pooled calibrated utility", pooled_values),
            ("fit-temporal support", support_values),
        ):
            if (
                not np.isfinite(values).all()
                or (values < 0.0).any()
                or (values > 1.0).any()
            ):
                raise ValueError(
                    f"EXP-052 eligible {label} must be within [0, 1]"
                )

    diagnostics = _fit_temporal_support_diagnostics(
        directions=directions,
        raw_utility=raw_utility,
        pooled_calibrated_utility=(
            pooled_calibrated_utility
        ),
        fit_temporal_support=fit_temporal_support,
        view_prediction_digests=digests,
    )
    consensus_digest = (
        _fit_temporal_support_consensus_digest(
            row_ids=row_ids,
            directions=directions,
            raw_utility=raw_utility,
            pooled_calibrated_utility=(
                pooled_calibrated_utility
            ),
            fit_temporal_support=fit_temporal_support,
        )
    )
    return (
        directions,
        raw_utility,
        pooled_calibrated_utility,
        fit_temporal_support,
        diagnostics,
        row_ids,
        consensus_digest,
    )


REQUIRED_SUPPORT_COMPARISON_COUNT = (
    3 * SUPPORT_REFERENCE_WINDOWS_PER_EXCLUDED_REGIME
)


def _derive_support_cutoff(
    *,
    directions: np.ndarray,
    raw_utility: np.ndarray,
    pooled_calibrated_utility: np.ndarray,
    fit_temporal_support: np.ndarray,
    row_ids: Sequence[str],
    budget: int,
) -> dict[str, object]:
    if budget not in CANDIDATE_BUDGET_ANCHORS:
        raise ValueError(
            "unsupported EXP-052 candidate budget"
        )
    if not (
        len(row_ids)
        == len(directions)
        == len(raw_utility)
        == len(pooled_calibrated_utility)
        == len(fit_temporal_support)
    ):
        raise ValueError(
            "EXP-052 support cutoff row mismatch"
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
        pooled_value = float(
            pooled_calibrated_utility[index]
        )
        support_value = float(
            fit_temporal_support[index]
        )
        if (
            not np.isfinite(raw_value)
            or raw_value <= 0.0
        ):
            raise ValueError(
                "EXP-052 directional raw utility must be finite and positive"
            )
        for label, value in (
            ("pooled calibrated utility", pooled_value),
            ("fit-temporal support", support_value),
        ):
            if (
                not np.isfinite(value)
                or value < 0.0
                or value > 1.0
            ):
                raise ValueError(
                    f"EXP-052 {label} must be within [0, 1]"
                )

    if len(eligible) < budget:
        return {
            "status": (
                "UNAVAILABLE_INSUFFICIENT_UTILITY_ROWS"
            ),
            "candidate_budget_anchor": budget,
            "eligible_utility_row_count": len(eligible),
            "selection_derived_support_cutoff": None,
            "selection_derived_pooled_calibrated_cutoff": (
                None
            ),
            "selection_derived_raw_cutoff": None,
        }

    ranked = sorted(
        eligible,
        key=lambda index: (
            -float(fit_temporal_support[index]),
            -float(
                pooled_calibrated_utility[index]
            ),
            -float(raw_utility[index]),
            str(row_ids[index]),
        ),
    )
    cutoff_index = ranked[budget - 1]
    support_cutoff = float(
        fit_temporal_support[cutoff_index]
    )
    pooled_cutoff = float(
        pooled_calibrated_utility[cutoff_index]
    )
    raw_cutoff = float(
        raw_utility[cutoff_index]
    )

    selected_count = sum(
        1
        for index in eligible
        if _passes_support_cutoff(
            support=float(
                fit_temporal_support[index]
            ),
            pooled=float(
                pooled_calibrated_utility[index]
            ),
            raw=float(raw_utility[index]),
            support_cutoff=support_cutoff,
            pooled_cutoff=pooled_cutoff,
            raw_cutoff=raw_cutoff,
        )
    )
    return {
        "status": "AVAILABLE",
        "candidate_budget_anchor": budget,
        "eligible_utility_row_count": len(eligible),
        "selection_derived_support_cutoff": (
            support_cutoff
        ),
        "selection_derived_pooled_calibrated_cutoff": (
            pooled_cutoff
        ),
        "selection_derived_raw_cutoff": raw_cutoff,
        "selection_candidate_count_at_cutoff": (
            selected_count
        ),
    }


def _passes_support_cutoff(
    *,
    support: float,
    pooled: float,
    raw: float,
    support_cutoff: float,
    pooled_cutoff: float,
    raw_cutoff: float,
) -> bool:
    return bool(
        support > support_cutoff
        or (
            support == support_cutoff
            and (
                pooled > pooled_cutoff
                or (
                    pooled == pooled_cutoff
                    and raw >= raw_cutoff
                )
            )
        )
    )


def _candidate_directions_support(
    *,
    directions: np.ndarray,
    raw_utility: np.ndarray,
    pooled_calibrated_utility: np.ndarray,
    fit_temporal_support: np.ndarray,
    support_cutoff: float,
    pooled_cutoff: float,
    raw_cutoff: float,
) -> np.ndarray:
    for label, value in (
        ("support cutoff", support_cutoff),
        ("pooled cutoff", pooled_cutoff),
    ):
        if (
            not np.isfinite(value)
            or value < 0.0
            or value > 1.0
        ):
            raise ValueError(
                f"EXP-052 {label} is invalid"
            )
    if (
        not np.isfinite(raw_cutoff)
        or raw_cutoff <= 0.0
    ):
        raise ValueError(
            "EXP-052 raw cutoff is invalid"
        )
    if not (
        len(directions)
        == len(raw_utility)
        == len(pooled_calibrated_utility)
        == len(fit_temporal_support)
    ):
        raise ValueError(
            "EXP-052 candidate row mismatch"
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
        pooled_value = float(
            pooled_calibrated_utility[index]
        )
        support_value = float(
            fit_temporal_support[index]
        )
        if (
            not np.isfinite(raw_value)
            or raw_value <= 0.0
        ):
            raise ValueError(
                "EXP-052 directional raw utility must be finite and positive"
            )
        for label, value in (
            ("pooled calibrated utility", pooled_value),
            ("fit-temporal support", support_value),
        ):
            if (
                not np.isfinite(value)
                or value < 0.0
                or value > 1.0
            ):
                raise ValueError(
                    f"EXP-052 directional {label} is invalid"
                )
        if _passes_support_cutoff(
            support=support_value,
            pooled=pooled_value,
            raw=raw_value,
            support_cutoff=support_cutoff,
            pooled_cutoff=pooled_cutoff,
            raw_cutoff=raw_cutoff,
        ):
            out[index] = direction
    return out


def _evaluate_support_cutoff(
    frame: pl.DataFrame,
    *,
    directions: np.ndarray,
    raw_utility: np.ndarray,
    pooled_calibrated_utility: np.ndarray,
    fit_temporal_support: np.ndarray,
    support_cutoff: float,
    pooled_cutoff: float,
    raw_cutoff: float,
    budget: int,
    scenarios: Sequence[float],
    row_ids: Sequence[str],
) -> dict[str, object]:
    candidates = _candidate_directions_support(
        directions=directions,
        raw_utility=raw_utility,
        pooled_calibrated_utility=(
            pooled_calibrated_utility
        ),
        fit_temporal_support=fit_temporal_support,
        support_cutoff=support_cutoff,
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
        "selection_derived_support_cutoff": (
            support_cutoff
        ),
        "selection_derived_pooled_calibrated_cutoff": (
            pooled_cutoff
        ),
        "selection_derived_raw_cutoff": raw_cutoff,
        "scenarios": scenario_results,
    }


def _evaluate_temporal_stability_support(
    *,
    selection_frame: pl.DataFrame,
    directions: np.ndarray,
    raw_utility: np.ndarray,
    pooled_calibrated_utility: np.ndarray,
    fit_temporal_support: np.ndarray,
    support_cutoff: float,
    pooled_cutoff: float,
    raw_cutoff: float,
    budget: int,
    cell: ModelCell,
    full_selection_candidate_count: int,
) -> dict[str, object]:
    if not (
        len(directions)
        == selection_frame.height
        == len(raw_utility)
        == len(pooled_calibrated_utility)
        == len(fit_temporal_support)
    ):
        raise ValueError(
            "EXP-052 stability row mismatch"
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
        row_ids = _base._row_identity(
            window_frame,
            cell=cell,
        )
        evaluated = _evaluate_support_cutoff(
            window_frame,
            directions=directions[index_array],
            raw_utility=raw_utility[index_array],
            pooled_calibrated_utility=(
                pooled_calibrated_utility[index_array]
            ),
            fit_temporal_support=(
                fit_temporal_support[index_array]
            ),
            support_cutoff=support_cutoff,
            pooled_cutoff=pooled_cutoff,
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


def _evaluate_forward_split_support(
    *,
    fitted_models: Mapping[
        str,
        Mapping[str, _base.FittedMarketModel],
    ],
    pooled_calibration_references: Mapping[
        str,
        Mapping[str, np.ndarray],
    ],
    support_references: Mapping[
        str,
        Mapping[
            str,
            Mapping[str, np.ndarray],
        ],
    ],
    frame: pl.DataFrame,
    cell: ModelCell,
    support_cutoff: float,
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
        diagnostics,
        row_ids,
        consensus_digest,
    ) = _score_fit_temporal_support_consensus(
        fitted_models=fitted_models,
        pooled_calibration_references=(
            pooled_calibration_references
        ),
        support_references=support_references,
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
    evaluated = _evaluate_support_cutoff(
        frame,
        directions=directions,
        raw_utility=raw_utility,
        pooled_calibrated_utility=(
            pooled_calibrated_utility
        ),
        fit_temporal_support=fit_temporal_support,
        support_cutoff=support_cutoff,
        pooled_cutoff=pooled_cutoff,
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
        "fit_temporal_support_consensus": (
            diagnostics
        ),
        "fit_temporal_support_consensus_digest": (
            consensus_digest
        ),
        **evaluated,
    }


def run_fit_temporal_support_utility_model_cell_core(
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
            "EXP-052 model cell has empty required "
            f"split(s): {empty}"
        )

    regime_frames = {
        split.name: _base._split_frame(
            joined,
            split,
        )
        for split in _predecessor_fit_regime_splits()
    }
    if set(regime_frames) != set(
        PREDECESSOR_REGIME_NAMES
    ):
        raise ValueError(
            "EXP-052 predecessor fit-regime identity drift"
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
            "EXP-052 model cell has empty fit regime(s): "
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
                "EXP-052 jackknife excluded-regime count drift"
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
    ) = _build_calibration_references(
        fitted_models=fitted_models,
        regime_frames=regime_frames,
        cell=cell,
    )
    (
        support_references,
        support_evidence,
    ) = _build_fit_temporal_support_references(
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
        selection_pooled_calibrated_utility,
        selection_fit_temporal_support,
        selection_diagnostics,
        selection_row_ids,
        selection_consensus_digest,
    ) = _score_fit_temporal_support_consensus(
        fitted_models=fitted_models,
        pooled_calibration_references=(
            pooled_calibration_references
        ),
        support_references=support_references,
        frame=selection_frame,
        cell=cell,
    )

    variants: list[dict[str, object]] = []
    for budget in CANDIDATE_BUDGET_ANCHORS:
        cutoff_record = _derive_support_cutoff(
            directions=selection_directions,
            raw_utility=selection_raw_utility,
            pooled_calibrated_utility=(
                selection_pooled_calibrated_utility
            ),
            fit_temporal_support=(
                selection_fit_temporal_support
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

        support_cutoff = float(
            cutoff_record[
                "selection_derived_support_cutoff"
            ]
        )
        pooled_cutoff = float(
            cutoff_record[
                "selection_derived_pooled_calibrated_cutoff"
            ]
        )
        raw_cutoff = float(
            cutoff_record[
                "selection_derived_raw_cutoff"
            ]
        )

        evaluated = _evaluate_support_cutoff(
            selection_frame,
            directions=selection_directions,
            raw_utility=selection_raw_utility,
            pooled_calibrated_utility=(
                selection_pooled_calibrated_utility
            ),
            fit_temporal_support=(
                selection_fit_temporal_support
            ),
            support_cutoff=support_cutoff,
            pooled_cutoff=pooled_cutoff,
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
                _evaluate_temporal_stability_support(
                    selection_frame=selection_frame,
                    directions=selection_directions,
                    raw_utility=selection_raw_utility,
                    pooled_calibrated_utility=(
                        selection_pooled_calibrated_utility
                    ),
                    fit_temporal_support=(
                        selection_fit_temporal_support
                    ),
                    support_cutoff=support_cutoff,
                    pooled_cutoff=pooled_cutoff,
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
            FIT_TEMPORAL_SUPPORT_UTILITY_EXPERIMENT_ID
        ),
        "training_core_version": (
            FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_DECISION
        ),
        "dec163_merged_commit": DEC163_MERGED_COMMIT,
        "dec163_protocol_blob_sha": (
            DEC163_PROTOCOL_BLOB_SHA
        ),
        "predecessor_training_core_blob_sha": (
            PREDECESSOR_TRAINING_CORE_BLOB_SHA
        ),
        "predecessor_training_core_decision": (
            TEMPORAL_CALIBRATED_UTILITY_TRAINING_CORE_DECISION
        ),
        "protocol_decision": (
            FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_DECISION
        ),
        "protocol_version": (
            FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_VERSION
        ),
        "protocol_fingerprint": (
            fit_temporal_support_utility_protocol_fingerprint()
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
                pooled_calibration_evidence
            ),
            "calibration_reference_count": sum(
                len(value)
                for value in pooled_calibration_references.values()
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
            "fit_temporal_support_references": (
                support_evidence
            ),
            "fit_temporal_support_reference_count": (
                FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL
            ),
            "fit_temporal_support_reference_rule": (
                FIT_TEMPORAL_SUPPORT_REFERENCE_RULE
            ),
            "fit_temporal_support_percentile_rule": (
                FIT_TEMPORAL_SUPPORT_PERCENTILE_RULE
            ),
            "robust_fit_temporal_support_score_rule": (
                ROBUST_FIT_TEMPORAL_SUPPORT_SCORE_RULE
            ),
            "full_fit_single_model": {
                "status": "FORBIDDEN_BY_DEC150_DEC163",
                "fit_attempt_count": 0,
            },
            "view_weight_search": {
                "status": "FORBIDDEN_BY_DEC150_DEC163",
                "fit_attempt_count": 0,
            },
            "view_fallback": {
                "status": "FORBIDDEN_BY_DEC150_DEC163",
                "fit_attempt_count": 0,
            },
            "selection_window_calibration": {
                "status": "FORBIDDEN_BY_DEC150_DEC163",
                "fit_attempt_count": 0,
            },
            "hist_gradient_boosting_classifier": {
                "status": "EXCLUDED_BY_DEC150_DEC163",
                "fit_attempt_count": 0,
            },
            "logistic_regression": {
                "status": "EXCLUDED_BY_DEC112_DEC150_DEC163",
                "fit_attempt_count": 0,
            },
        },
        "selection": {
            "status": (
                "SELECTED"
                if selected is not None
                else (
                    "NO_FIT_TEMPORAL_SUPPORT_UTILITY_"
                    "STABLE_MODEL_CHALLENGER"
                )
            ),
            "row_count": selection_frame.height,
            "fit_temporal_support_consensus": (
                selection_diagnostics
            ),
            "fit_temporal_support_consensus_digest": (
                selection_consensus_digest
            ),
            "ranking_rule": RANKING_RULE,
            "selection_cutoff_rule": (
                SELECTION_CUTOFF_RULE
            ),
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
                    "selection_derived_support_cutoff": float(
                        selected[
                            "selection_derived_support_cutoff"
                        ]
                    ),
                    "selection_derived_pooled_calibrated_cutoff": float(
                        selected[
                            "selection_derived_pooled_calibrated_cutoff"
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

    selected_support_cutoff = float(
        selected[
            "selection_derived_support_cutoff"
        ]
    )
    selected_pooled_cutoff = float(
        selected[
            "selection_derived_pooled_calibrated_cutoff"
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

    validation = _evaluate_forward_split_support(
        fitted_models=fitted_models,
        pooled_calibration_references=(
            pooled_calibration_references
        ),
        support_references=support_references,
        frame=split_frames[
            VALIDATION_SPLIT.name
        ],
        cell=cell,
        support_cutoff=selected_support_cutoff,
        pooled_cutoff=selected_pooled_cutoff,
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

    holdout = _evaluate_forward_split_support(
        fitted_models=fitted_models,
        pooled_calibration_references=(
            pooled_calibration_references
        ),
        support_references=support_references,
        frame=split_frames[
            RETROSPECTIVE_HOLDOUT_SPLIT.name
        ],
        cell=cell,
        support_cutoff=selected_support_cutoff,
        pooled_cutoff=selected_pooled_cutoff,
        raw_cutoff=selected_raw_cutoff,
        budget=selected_budget,
        gate_scenarios=HOLDOUT_GATE_SCENARIOS,
    )
    result["retrospective_holdout"] = holdout
    result["result_fingerprint"] = _sha256(result)
    return result


__all__ = [
    "BROKER_MUTATION_AUTHORIZED",
    "DEC163_MERGED_COMMIT",
    "DEC163_PROTOCOL_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "FIT_TEMPORAL_SUPPORT_UTILITY_RESULT_EXECUTION_AUTHORIZED",
    "FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_DECISION",
    "FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_VERSION",
    "LIVE_ORDER_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "PREDECESSOR_TRAINING_CORE_BLOB_SHA",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "REQUIRED_SUPPORT_COMPARISON_COUNT",
    "SHADOW_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "_build_fit_temporal_support_references",
    "_candidate_directions_support",
    "_derive_support_cutoff",
    "_fit_temporal_support_consensus_digest",
    "_score_fit_temporal_support_consensus",
    "_support_reference_digest",
    "run_fit_temporal_support_utility_model_cell_core",
    "validate_fit_temporal_support_utility_training_sources",
]
