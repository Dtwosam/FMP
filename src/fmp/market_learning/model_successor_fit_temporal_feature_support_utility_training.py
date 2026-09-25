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
    MODEL_INPUT_COLUMNS,
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
    CUTOFF_TIE_POLICY,
    FEATURE_SUPPORT_WINDOWS_PER_VIEW,
    FIT_TEMPORAL_FEATURE_DISTANCE_RULE,
    FIT_TEMPORAL_FEATURE_REFERENCE_RULE,
    FIT_TEMPORAL_FEATURE_SUPPORT_PERCENTILE_RULE,
    FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_VERSION,
    FORWARD_APPLICATION_RULE,
    PRIOR_RESULT_INFORMED,
    RANKING_RULE,
    ROBUST_FIT_TEMPORAL_FEATURE_SUPPORT_SCORE_RULE,
    SELECTION_CUTOFF_RULE,
    UNTOUCHED_OOS,
    fit_temporal_feature_support_utility_protocol_fingerprint,
)
from .model_successor_fit_temporal_support_utility_protocol import (
    FIT_TEMPORAL_SUPPORT_PERCENTILE_RULE,
    FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL,
    FIT_TEMPORAL_SUPPORT_REFERENCE_RULE,
    FIT_TEMPORAL_SUPPORT_WINDOWS,
    ROBUST_FIT_TEMPORAL_SUPPORT_SCORE_RULE,
)
from .model_successor_fit_temporal_support_utility_training import (
    FIT_TEMPORAL_SUPPORT_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_DECISION,
    FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_VERSION,
    MODEL_FIT_AUTHORIZED as PREDECESSOR_MODEL_FIT_AUTHORIZED,
    _build_fit_temporal_support_references,
    _score_fit_temporal_support_consensus,
    validate_fit_temporal_support_utility_training_sources,
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
    _predecessor_target_summary,
)
from .model_successor_regime_utility_training import _selection_key


FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_VERSION = (
    "fmp-exp053-fit-temporal-feature-support-utility-training-core-v1"
)
FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_DECISION = "DEC-175"

DEC174_MERGED_COMMIT = "9687eb8ea3920e87d6681adf7366a3ce0bba7154"
DEC174_PROTOCOL_BLOB_SHA = (
    "11ae3fc8e68687cc04957ed9243d8c5969227fb8"
)
PREDECESSOR_TRAINING_CORE_BLOB_SHA = (
    "fe5664438752a161134bbed6f55d9985f1c1470a"
)

FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_RESULT_EXECUTION_AUTHORIZED = False
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


def validate_fit_temporal_feature_support_utility_training_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "dec174_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_feature_support_utility_protocol.py",
            DEC174_PROTOCOL_BLOB_SHA,
        ),
        "predecessor_training_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_support_utility_training.py",
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(
                f"missing EXP-053 training dependency: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-053 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    predecessor = validate_fit_temporal_support_utility_training_sources(
        repository_root=root,
    )
    if predecessor[
        "fit_temporal_support_utility_training_core_decision"
    ] != FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_DECISION:
        raise ValueError("EXP-053 predecessor training decision drift")
    if predecessor["model_fit_authorized"] is not False:
        raise ValueError("EXP-053 predecessor model fit must remain closed")
    if predecessor[
        "fit_temporal_support_utility_result_execution_authorized"
    ] is not False:
        raise ValueError(
            "EXP-053 predecessor result execution must remain closed"
        )
    if PREDECESSOR_MODEL_FIT_AUTHORIZED is not False:
        raise ValueError(
            "EXP-053 predecessor source fit authorization drift"
        )
    if FIT_TEMPORAL_SUPPORT_UTILITY_RESULT_EXECUTION_AUTHORIZED is not False:
        raise ValueError(
            "EXP-053 predecessor source execution authorization drift"
        )

    fingerprint = fit_temporal_feature_support_utility_protocol_fingerprint()
    if len(fingerprint) != 64:
        raise ValueError("EXP-053 protocol fingerprint is invalid")

    return {
        "fit_temporal_feature_support_utility_training_core_version": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_VERSION
        ),
        "fit_temporal_feature_support_utility_training_core_decision": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_DECISION
        ),
        "dec174_merged_commit": DEC174_MERGED_COMMIT,
        "dec174_protocol_blob_sha": actual["dec174_protocol"],
        "predecessor_training_core_blob_sha": actual[
            "predecessor_training_core"
        ],
        "predecessor_training_core_decision": (
            FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_DECISION
        ),
        "predecessor_training_core_version": (
            FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_VERSION
        ),
        "fit_temporal_feature_support_utility_protocol_fingerprint": (
            fingerprint
        ),
        "fit_temporal_feature_support_utility_result_execution_authorized": (
            False
        ),
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
    }


def _feature_windows_by_parent(
) -> dict[str, tuple[dict[str, object], ...]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for raw in FIT_TEMPORAL_SUPPORT_WINDOWS:
        window = dict(raw)
        grouped.setdefault(
            str(window["parent_regime"]),
            [],
        ).append(window)
    result = {
        parent: tuple(
            sorted(
                windows,
                key=lambda item: str(item["start"]),
            )
        )
        for parent, windows in grouped.items()
    }
    if set(result) != set(PREDECESSOR_REGIME_NAMES):
        raise ValueError(
            "EXP-053 feature-support parent-regime inventory mismatch"
        )
    if any(
        len(windows) != FEATURE_SUPPORT_WINDOWS_PER_VIEW
        for windows in result.values()
    ):
        raise ValueError(
            "EXP-053 feature-support window count mismatch"
        )
    return result


def _float_array_digest(values: np.ndarray) -> str:
    array = np.asarray(values, dtype=np.float64)
    if not np.isfinite(array).all():
        raise ValueError(
            "EXP-053 feature-support digest values must be finite"
        )
    digest = hashlib.sha256()
    digest.update(
        len(array.shape).to_bytes(8, "big", signed=False)
    )
    for size in array.shape:
        digest.update(int(size).to_bytes(8, "big", signed=False))
    for value in array.ravel(order="C").tolist():
        digest.update(struct.pack(">d", float(value)))
    return digest.hexdigest()


def _bool_array_digest(values: np.ndarray) -> str:
    array = np.asarray(values, dtype=np.bool_)
    digest = hashlib.sha256()
    digest.update(len(array).to_bytes(8, "big", signed=False))
    digest.update(bytes(int(value) for value in array.tolist()))
    return digest.hexdigest()


def _view_preprocessor(
    target_models: Mapping[str, _base.FittedMarketModel],
) -> _base.FittedMarketModel:
    if set(target_models) != set(FINANCIAL_TARGET_COLUMNS):
        raise ValueError(
            "EXP-053 fitted target-model inventory mismatch"
        )
    first = target_models[FINANCIAL_TARGET_COLUMNS[0]]
    second = target_models[FINANCIAL_TARGET_COLUMNS[1]]
    if first.preprocessor_fingerprint != second.preprocessor_fingerprint:
        raise ValueError(
            "EXP-053 view target preprocessors must be identical"
        )
    return first


def _reference_distances(
    transformed: np.ndarray,
    *,
    center: np.ndarray,
    scale: np.ndarray,
    active_mask: np.ndarray,
) -> np.ndarray:
    matrix = np.asarray(transformed, dtype=np.float64)
    center = np.asarray(center, dtype=np.float64)
    scale = np.asarray(scale, dtype=np.float64)
    active = np.asarray(active_mask, dtype=np.bool_)
    if matrix.ndim != 2:
        raise ValueError("EXP-053 transformed feature matrix must be 2-D")
    if (
        center.shape != (matrix.shape[1],)
        or scale.shape != (matrix.shape[1],)
        or active.shape != (matrix.shape[1],)
    ):
        raise ValueError("EXP-053 feature-reference dimension mismatch")
    if not np.isfinite(matrix).all():
        raise ValueError(
            "EXP-053 transformed feature values must be finite"
        )
    if not np.isfinite(center).all() or not np.isfinite(scale).all():
        raise ValueError(
            "EXP-053 feature-reference center/scale must be finite"
        )
    if not bool(active.any()):
        raise ValueError(
            "EXP-053 feature reference has zero active dimensions"
        )
    if (scale[active] <= 0.0).any():
        raise ValueError(
            "EXP-053 active feature-reference scales must be positive"
        )
    standardized = (
        matrix[:, active] - center[active]
    ) / scale[active]
    distances = np.mean(
        np.square(standardized),
        axis=1,
        dtype=np.float64,
    )
    if (
        distances.shape != (matrix.shape[0],)
        or not np.isfinite(distances).all()
        or (distances < 0.0).any()
    ):
        raise ValueError(
            "EXP-053 feature-reference distances are invalid"
        )
    return distances


def _build_fit_temporal_feature_support_references(
    *,
    fitted_models: Mapping[
        str,
        Mapping[str, _base.FittedMarketModel],
    ],
    regime_frames: Mapping[str, pl.DataFrame],
) -> tuple[
    dict[str, dict[str, dict[str, np.ndarray]]],
    dict[str, object],
]:
    view_regimes = _jackknife_view_regime_names()
    windows_by_parent = _feature_windows_by_parent()
    if set(fitted_models) != set(view_regimes):
        raise ValueError(
            "EXP-053 fitted view inventory mismatch"
        )
    if set(regime_frames) != set(PREDECESSOR_REGIME_NAMES):
        raise ValueError(
            "EXP-053 fit-regime inventory mismatch"
        )

    references: dict[
        str,
        dict[str, dict[str, np.ndarray]],
    ] = {}
    evidence: dict[str, object] = {}

    for view_name in sorted(fitted_models):
        included = tuple(view_regimes[view_name])
        excluded = tuple(
            regime
            for regime in PREDECESSOR_REGIME_NAMES
            if regime not in included
        )
        if len(excluded) != 1:
            raise ValueError(
                "EXP-053 excluded fit-regime count drift"
            )
        excluded_regime = excluded[0]
        fitted = _view_preprocessor(
            fitted_models[view_name]
        )
        parent_frame = regime_frames[excluded_regime]
        window_refs: dict[str, dict[str, np.ndarray]] = {}
        window_evidence: dict[str, object] = {}

        for raw_window in windows_by_parent[excluded_regime]:
            window = dict(raw_window)
            start = _parse_utc_date(str(window["start"]))
            end_exclusive = _parse_utc_date(
                str(window["end_exclusive"])
            )
            indices = _window_indices(
                parent_frame,
                start=start,
                end_exclusive=end_exclusive,
            )
            window_frame = parent_frame[indices]
            if window_frame.is_empty():
                raise ValueError(
                    "EXP-053 feature-support reference window is empty"
                )
            transformed = _base.transform_features(
                window_frame.select(list(MODEL_INPUT_COLUMNS)),
                fitted.preprocessor,
            )
            transformed = np.asarray(
                transformed,
                dtype=np.float64,
            )
            if (
                transformed.ndim != 2
                or transformed.shape[0] != window_frame.height
                or transformed.shape[1] == 0
                or not np.isfinite(transformed).all()
            ):
                raise ValueError(
                    "EXP-053 transformed reference features are invalid"
                )
            center = np.mean(
                transformed,
                axis=0,
                dtype=np.float64,
            )
            scale = np.std(
                transformed,
                axis=0,
                ddof=0,
                dtype=np.float64,
            )
            active = scale > 0.0
            if not bool(active.any()):
                raise ValueError(
                    "EXP-053 feature-support reference has zero "
                    "positive-scale dimensions"
                )
            distances = _reference_distances(
                transformed,
                center=center,
                scale=scale,
                active_mask=active,
            )
            sorted_distances = np.sort(
                distances.astype(np.float64, copy=True)
            )
            window_name = str(window["name"])
            window_refs[window_name] = {
                "center": center,
                "scale": scale,
                "active_mask": active,
                "sorted_distances": sorted_distances,
            }
            window_evidence[window_name] = {
                "status": "FROZEN",
                "name": window_name,
                "parent_regime": excluded_regime,
                "start": str(window["start"]),
                "end_exclusive": str(window["end_exclusive"]),
                "row_count": window_frame.height,
                "transformed_dimension_count": int(
                    transformed.shape[1]
                ),
                "active_dimension_count": int(active.sum()),
                "preprocessor_fingerprint": (
                    fitted.preprocessor_fingerprint
                ),
                "center_digest": _float_array_digest(center),
                "scale_digest": _float_array_digest(scale),
                "active_dimension_mask_digest": (
                    _bool_array_digest(active)
                ),
                "minimum_reference_distance": float(
                    sorted_distances[0]
                ),
                "maximum_reference_distance": float(
                    sorted_distances[-1]
                ),
                "mean_reference_distance": float(
                    sorted_distances.mean()
                ),
                "sorted_reference_distance_digest": (
                    _float_array_digest(sorted_distances)
                ),
            }

        if len(window_refs) != FEATURE_SUPPORT_WINDOWS_PER_VIEW:
            raise ValueError(
                "EXP-053 feature-support reference count drift"
            )
        references[view_name] = window_refs
        evidence[view_name] = {
            "status": "FROZEN",
            "included_regimes": list(included),
            "excluded_regime": excluded_regime,
            "reference_count": len(window_refs),
            "windows": window_evidence,
        }

    count = sum(len(value) for value in references.values())
    if count != FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL:
        raise ValueError(
            "EXP-053 total feature-support reference count drift"
        )
    return references, evidence


def _survival_percentiles(
    sorted_reference: np.ndarray,
    values: np.ndarray,
) -> np.ndarray:
    reference = np.asarray(
        sorted_reference,
        dtype=np.float64,
    )
    scored = np.asarray(values, dtype=np.float64)
    if (
        reference.ndim != 1
        or scored.ndim != 1
        or len(reference) == 0
        or not np.isfinite(reference).all()
        or not np.isfinite(scored).all()
    ):
        raise ValueError(
            "EXP-053 feature-support percentile inputs are invalid"
        )
    if bool((reference[1:] < reference[:-1]).any()):
        raise ValueError(
            "EXP-053 feature-support reference must be sorted"
        )
    left = np.searchsorted(
        reference,
        scored,
        side="left",
    )
    result = (
        len(reference) - left
    ).astype(np.float64) / float(len(reference))
    if (
        not np.isfinite(result).all()
        or (result < 0.0).any()
        or (result > 1.0).any()
    ):
        raise ValueError(
            "EXP-053 feature-support percentiles are invalid"
        )
    return result


def _score_fit_temporal_feature_support(
    *,
    fitted_models: Mapping[
        str,
        Mapping[str, _base.FittedMarketModel],
    ],
    feature_references: Mapping[
        str,
        Mapping[str, Mapping[str, np.ndarray]],
    ],
    frame: pl.DataFrame,
) -> np.ndarray:
    if frame.is_empty():
        raise ValueError(
            "EXP-053 feature-support scored frame must be non-empty"
        )
    if set(feature_references) != set(fitted_models):
        raise ValueError(
            "EXP-053 feature-support view inventory mismatch"
        )

    columns: list[np.ndarray] = []
    for view_name in sorted(fitted_models):
        fitted = _view_preprocessor(
            fitted_models[view_name]
        )
        transformed = _base.transform_features(
            frame.select(list(MODEL_INPUT_COLUMNS)),
            fitted.preprocessor,
        )
        transformed = np.asarray(
            transformed,
            dtype=np.float64,
        )
        if (
            transformed.ndim != 2
            or transformed.shape[0] != frame.height
            or not np.isfinite(transformed).all()
        ):
            raise ValueError(
                "EXP-053 scored transformed features are invalid"
            )
        refs = feature_references[view_name]
        if len(refs) != FEATURE_SUPPORT_WINDOWS_PER_VIEW:
            raise ValueError(
                "EXP-053 scored feature-reference count drift"
            )
        for window_name in sorted(refs):
            ref = refs[window_name]
            distances = _reference_distances(
                transformed,
                center=ref["center"],
                scale=ref["scale"],
                active_mask=ref["active_mask"],
            )
            columns.append(
                _survival_percentiles(
                    ref["sorted_distances"],
                    distances,
                )
            )

    if len(columns) != FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL:
        raise ValueError(
            "EXP-053 feature-support comparison count drift"
        )
    stacked = np.column_stack(columns)
    support = np.min(
        stacked,
        axis=1,
    )
    if (
        support.shape != (frame.height,)
        or not np.isfinite(support).all()
        or (support < 0.0).any()
        or (support > 1.0).any()
    ):
        raise ValueError(
            "EXP-053 robust feature support is invalid"
        )
    return support


def _feature_support_consensus_digest(
    *,
    row_ids: Sequence[str],
    directions: np.ndarray,
    raw_utility: np.ndarray,
    pooled_calibrated_utility: np.ndarray,
    fit_temporal_support: np.ndarray,
    feature_support: np.ndarray,
) -> str:
    if not (
        len(row_ids)
        == len(directions)
        == len(raw_utility)
        == len(pooled_calibrated_utility)
        == len(fit_temporal_support)
        == len(feature_support)
    ):
        raise ValueError(
            "EXP-053 consensus digest row mismatch"
        )
    digest = hashlib.sha256()
    for values in zip(
        row_ids,
        directions.tolist(),
        raw_utility.tolist(),
        pooled_calibrated_utility.tolist(),
        fit_temporal_support.tolist(),
        feature_support.tolist(),
        strict=True,
    ):
        row_id, direction, raw, pooled, utility_support, feature = values
        for text_value in (str(row_id), str(direction)):
            encoded = text_value.encode("utf-8")
            digest.update(
                len(encoded).to_bytes(8, "big", signed=False)
            )
            digest.update(encoded)
        for number in (raw, pooled, utility_support, feature):
            digest.update(struct.pack(">d", float(number)))
    return digest.hexdigest()


def _feature_support_diagnostics(
    *,
    predecessor: Mapping[str, object],
    directions: np.ndarray,
    feature_support: np.ndarray,
) -> dict[str, object]:
    eligible_indices = [
        index
        for index, direction in enumerate(
            directions.tolist()
        )
        if direction in {"LONG", "SHORT"}
    ]
    values = [
        float(feature_support[index])
        for index in eligible_indices
    ]
    if values and (
        not all(np.isfinite(value) for value in values)
        or min(values) < 0.0
        or max(values) > 1.0
    ):
        raise ValueError(
            "EXP-053 eligible feature support must be within [0, 1]"
        )
    return {
        **dict(predecessor),
        "minimum_robust_fit_temporal_feature_support": (
            min(values) if values else None
        ),
        "maximum_robust_fit_temporal_feature_support": (
            max(values) if values else None
        ),
        "fit_temporal_feature_support_reference_count": (
            FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL
        ),
    }


def _score_fit_temporal_feature_support_consensus(
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
        Mapping[str, Mapping[str, np.ndarray]],
    ],
    feature_references: Mapping[
        str,
        Mapping[str, Mapping[str, np.ndarray]],
    ],
    frame: pl.DataFrame,
    cell: ModelCell,
) -> tuple[
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
        predecessor_diagnostics,
        row_ids,
        _,
    ) = _score_fit_temporal_support_consensus(
        fitted_models=fitted_models,
        pooled_calibration_references=pooled_calibration_references,
        support_references=support_references,
        frame=frame,
        cell=cell,
    )
    feature_support = _score_fit_temporal_feature_support(
        fitted_models=fitted_models,
        feature_references=feature_references,
        frame=frame,
    )
    eligible = np.isin(
        directions,
        np.asarray(["LONG", "SHORT"], dtype=object),
    )
    if bool(eligible.any()):
        values = feature_support[eligible]
        if (
            not np.isfinite(values).all()
            or (values < 0.0).any()
            or (values > 1.0).any()
        ):
            raise ValueError(
                "EXP-053 eligible feature support is invalid"
            )
    diagnostics = _feature_support_diagnostics(
        predecessor=predecessor_diagnostics,
        directions=directions,
        feature_support=feature_support,
    )
    digest = _feature_support_consensus_digest(
        row_ids=row_ids,
        directions=directions,
        raw_utility=raw_utility,
        pooled_calibrated_utility=pooled_calibrated_utility,
        fit_temporal_support=fit_temporal_support,
        feature_support=feature_support,
    )
    return (
        directions,
        raw_utility,
        pooled_calibrated_utility,
        fit_temporal_support,
        feature_support,
        diagnostics,
        row_ids,
        digest,
    )


def _passes_feature_support_cutoff(
    *,
    feature_support: float,
    utility_support: float,
    pooled: float,
    raw: float,
    feature_cutoff: float,
    utility_cutoff: float,
    pooled_cutoff: float,
    raw_cutoff: float,
) -> bool:
    return bool(
        feature_support > feature_cutoff
        or (
            feature_support == feature_cutoff
            and (
                utility_support > utility_cutoff
                or (
                    utility_support == utility_cutoff
                    and (
                        pooled > pooled_cutoff
                        or (
                            pooled == pooled_cutoff
                            and raw >= raw_cutoff
                        )
                    )
                )
            )
        )
    )


def _derive_feature_support_cutoff(
    *,
    directions: np.ndarray,
    raw_utility: np.ndarray,
    pooled_calibrated_utility: np.ndarray,
    fit_temporal_support: np.ndarray,
    feature_support: np.ndarray,
    row_ids: Sequence[str],
    budget: int,
) -> dict[str, object]:
    if budget not in CANDIDATE_BUDGET_ANCHORS:
        raise ValueError(
            "unsupported EXP-053 candidate budget"
        )
    if not (
        len(row_ids)
        == len(directions)
        == len(raw_utility)
        == len(pooled_calibrated_utility)
        == len(fit_temporal_support)
        == len(feature_support)
    ):
        raise ValueError(
            "EXP-053 cutoff row mismatch"
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
        if not np.isfinite(raw_value) or raw_value <= 0.0:
            raise ValueError(
                "EXP-053 directional raw utility must be positive"
            )
        for label, value in (
            (
                "feature support",
                float(feature_support[index]),
            ),
            (
                "fit-temporal utility support",
                float(fit_temporal_support[index]),
            ),
            (
                "pooled calibrated utility",
                float(pooled_calibrated_utility[index]),
            ),
        ):
            if (
                not np.isfinite(value)
                or value < 0.0
                or value > 1.0
            ):
                raise ValueError(
                    f"EXP-053 {label} must be within [0, 1]"
                )

    if len(eligible) < budget:
        return {
            "status": "UNAVAILABLE_INSUFFICIENT_UTILITY_ROWS",
            "candidate_budget_anchor": budget,
            "eligible_utility_row_count": len(eligible),
            "selection_derived_feature_support_cutoff": None,
            "selection_derived_support_cutoff": None,
            "selection_derived_pooled_calibrated_cutoff": None,
            "selection_derived_raw_cutoff": None,
        }

    ranked = sorted(
        eligible,
        key=lambda index: (
            -float(feature_support[index]),
            -float(fit_temporal_support[index]),
            -float(pooled_calibrated_utility[index]),
            -float(raw_utility[index]),
            str(row_ids[index]),
        ),
    )
    cutoff_index = ranked[budget - 1]
    feature_cutoff = float(feature_support[cutoff_index])
    utility_cutoff = float(fit_temporal_support[cutoff_index])
    pooled_cutoff = float(
        pooled_calibrated_utility[cutoff_index]
    )
    raw_cutoff = float(raw_utility[cutoff_index])
    selected_count = sum(
        1
        for index in eligible
        if _passes_feature_support_cutoff(
            feature_support=float(feature_support[index]),
            utility_support=float(fit_temporal_support[index]),
            pooled=float(pooled_calibrated_utility[index]),
            raw=float(raw_utility[index]),
            feature_cutoff=feature_cutoff,
            utility_cutoff=utility_cutoff,
            pooled_cutoff=pooled_cutoff,
            raw_cutoff=raw_cutoff,
        )
    )
    return {
        "status": "AVAILABLE",
        "candidate_budget_anchor": budget,
        "eligible_utility_row_count": len(eligible),
        "selection_derived_feature_support_cutoff": feature_cutoff,
        "selection_derived_support_cutoff": utility_cutoff,
        "selection_derived_pooled_calibrated_cutoff": pooled_cutoff,
        "selection_derived_raw_cutoff": raw_cutoff,
        "selection_candidate_count_at_cutoff": selected_count,
    }


def _candidate_directions_feature_support(
    *,
    directions: np.ndarray,
    raw_utility: np.ndarray,
    pooled_calibrated_utility: np.ndarray,
    fit_temporal_support: np.ndarray,
    feature_support: np.ndarray,
    feature_cutoff: float,
    utility_cutoff: float,
    pooled_cutoff: float,
    raw_cutoff: float,
) -> np.ndarray:
    for label, value in (
        ("feature cutoff", feature_cutoff),
        ("utility-support cutoff", utility_cutoff),
        ("pooled cutoff", pooled_cutoff),
    ):
        if (
            not np.isfinite(value)
            or value < 0.0
            or value > 1.0
        ):
            raise ValueError(f"EXP-053 {label} is invalid")
    if not np.isfinite(raw_cutoff) or raw_cutoff <= 0.0:
        raise ValueError("EXP-053 raw cutoff is invalid")
    if not (
        len(directions)
        == len(raw_utility)
        == len(pooled_calibrated_utility)
        == len(fit_temporal_support)
        == len(feature_support)
    ):
        raise ValueError("EXP-053 candidate row mismatch")

    out = np.full(
        len(directions),
        "NO_TRADE",
        dtype=object,
    )
    for index, direction in enumerate(directions.tolist()):
        if direction not in {"LONG", "SHORT"}:
            continue
        raw_value = float(raw_utility[index])
        feature_value = float(feature_support[index])
        utility_value = float(fit_temporal_support[index])
        pooled_value = float(
            pooled_calibrated_utility[index]
        )
        if not np.isfinite(raw_value) or raw_value <= 0.0:
            raise ValueError(
                "EXP-053 directional raw utility must be positive"
            )
        for label, value in (
            ("feature support", feature_value),
            ("utility support", utility_value),
            ("pooled utility", pooled_value),
        ):
            if (
                not np.isfinite(value)
                or value < 0.0
                or value > 1.0
            ):
                raise ValueError(
                    f"EXP-053 directional {label} is invalid"
                )
        if _passes_feature_support_cutoff(
            feature_support=feature_value,
            utility_support=utility_value,
            pooled=pooled_value,
            raw=raw_value,
            feature_cutoff=feature_cutoff,
            utility_cutoff=utility_cutoff,
            pooled_cutoff=pooled_cutoff,
            raw_cutoff=raw_cutoff,
        ):
            out[index] = direction
    return out


def _evaluate_feature_support_cutoff(
    frame: pl.DataFrame,
    *,
    directions: np.ndarray,
    raw_utility: np.ndarray,
    pooled_calibrated_utility: np.ndarray,
    fit_temporal_support: np.ndarray,
    feature_support: np.ndarray,
    feature_cutoff: float,
    utility_cutoff: float,
    pooled_cutoff: float,
    raw_cutoff: float,
    budget: int,
    scenarios: Sequence[float],
    row_ids: Sequence[str],
) -> dict[str, object]:
    candidates = _candidate_directions_feature_support(
        directions=directions,
        raw_utility=raw_utility,
        pooled_calibrated_utility=pooled_calibrated_utility,
        fit_temporal_support=fit_temporal_support,
        feature_support=feature_support,
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
        "selection_derived_feature_support_cutoff": feature_cutoff,
        "selection_derived_support_cutoff": utility_cutoff,
        "selection_derived_pooled_calibrated_cutoff": pooled_cutoff,
        "selection_derived_raw_cutoff": raw_cutoff,
        "scenarios": scenario_results,
    }


def _evaluate_temporal_stability_feature_support(
    *,
    selection_frame: pl.DataFrame,
    directions: np.ndarray,
    raw_utility: np.ndarray,
    pooled_calibrated_utility: np.ndarray,
    fit_temporal_support: np.ndarray,
    feature_support: np.ndarray,
    feature_cutoff: float,
    utility_cutoff: float,
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
        == len(feature_support)
    ):
        raise ValueError("EXP-053 stability row mismatch")

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
        frame = selection_frame[indices]
        index_array = np.asarray(indices, dtype=np.int64)
        row_ids = _base._row_identity(
            frame,
            cell=cell,
        )
        evaluated = _evaluate_feature_support_cutoff(
            frame,
            directions=directions[index_array],
            raw_utility=raw_utility[index_array],
            pooled_calibrated_utility=(
                pooled_calibrated_utility[index_array]
            ),
            fit_temporal_support=(
                fit_temporal_support[index_array]
            ),
            feature_support=feature_support[index_array],
            feature_cutoff=feature_cutoff,
            utility_cutoff=utility_cutoff,
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


def _evaluate_forward_split_feature_support(
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
        Mapping[str, Mapping[str, np.ndarray]],
    ],
    feature_references: Mapping[
        str,
        Mapping[str, Mapping[str, np.ndarray]],
    ],
    frame: pl.DataFrame,
    cell: ModelCell,
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
        diagnostics,
        row_ids,
        digest,
    ) = _score_fit_temporal_feature_support_consensus(
        fitted_models=fitted_models,
        pooled_calibration_references=pooled_calibration_references,
        support_references=support_references,
        feature_references=feature_references,
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
    evaluated = _evaluate_feature_support_cutoff(
        frame,
        directions=directions,
        raw_utility=raw_utility,
        pooled_calibrated_utility=pooled_calibrated_utility,
        fit_temporal_support=fit_temporal_support,
        feature_support=feature_support,
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
            evaluated["scenarios"][str(float(value))][
                "gate"
            ]["passed"]
        )
        for value in gate_scenarios
    ]
    return {
        "status": "PASS" if all(gating) else "REJECT",
        "row_count": frame.height,
        "fit_temporal_feature_support_consensus": diagnostics,
        "fit_temporal_feature_support_consensus_digest": digest,
        **evaluated,
    }


def run_fit_temporal_feature_support_utility_model_cell_core(
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
        empty = [
            name
            for name, frame in split_frames.items()
            if frame.is_empty()
        ]
        raise ValueError(
            "EXP-053 model cell has empty required "
            f"split(s): {empty}"
        )

    regime_frames = {
        split.name: _base._split_frame(joined, split)
        for split in _predecessor_fit_regime_splits()
    }
    if set(regime_frames) != set(PREDECESSOR_REGIME_NAMES):
        raise ValueError(
            "EXP-053 predecessor fit-regime identity drift"
        )
    if any(frame.is_empty() for frame in regime_frames.values()):
        empty = [
            name
            for name, frame in regime_frames.items()
            if frame.is_empty()
        ]
        raise ValueError(
            "EXP-053 model cell has empty fit regime(s): "
            f"{empty}"
        )

    view_frames = _build_jackknife_view_frames(regime_frames)
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
                "target_summary": _predecessor_target_summary(
                    fit_frame,
                    target_column=target_column,
                ),
                "preprocessor_fingerprint": (
                    fitted.preprocessor_fingerprint
                ),
                "model_fingerprint": fitted.model_fingerprint,
            }

        included = view_regimes[view_name]
        excluded = tuple(
            value
            for value in PREDECESSOR_REGIME_NAMES
            if value not in included
        )
        if len(excluded) != 1:
            raise ValueError(
                "EXP-053 jackknife excluded-regime count drift"
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
    (
        feature_references,
        feature_evidence,
    ) = _build_fit_temporal_feature_support_references(
        fitted_models=fitted_models,
        regime_frames=regime_frames,
    )

    selection_frame = split_frames[SELECTION_SPLIT.name]
    (
        selection_directions,
        selection_raw_utility,
        selection_pooled_calibrated_utility,
        selection_fit_temporal_support,
        selection_feature_support,
        selection_diagnostics,
        selection_row_ids,
        selection_consensus_digest,
    ) = _score_fit_temporal_feature_support_consensus(
        fitted_models=fitted_models,
        pooled_calibration_references=pooled_calibration_references,
        support_references=support_references,
        feature_references=feature_references,
        frame=selection_frame,
        cell=cell,
    )

    variants: list[dict[str, object]] = []
    for budget in CANDIDATE_BUDGET_ANCHORS:
        cutoff_record = _derive_feature_support_cutoff(
            directions=selection_directions,
            raw_utility=selection_raw_utility,
            pooled_calibrated_utility=(
                selection_pooled_calibrated_utility
            ),
            fit_temporal_support=selection_fit_temporal_support,
            feature_support=selection_feature_support,
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

        feature_cutoff = float(
            cutoff_record[
                "selection_derived_feature_support_cutoff"
            ]
        )
        utility_cutoff = float(
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
            cutoff_record["selection_derived_raw_cutoff"]
        )
        evaluated = _evaluate_feature_support_cutoff(
            selection_frame,
            directions=selection_directions,
            raw_utility=selection_raw_utility,
            pooled_calibrated_utility=(
                selection_pooled_calibrated_utility
            ),
            fit_temporal_support=selection_fit_temporal_support,
            feature_support=selection_feature_support,
            feature_cutoff=feature_cutoff,
            utility_cutoff=utility_cutoff,
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
                _evaluate_temporal_stability_feature_support(
                    selection_frame=selection_frame,
                    directions=selection_directions,
                    raw_utility=selection_raw_utility,
                    pooled_calibrated_utility=(
                        selection_pooled_calibrated_utility
                    ),
                    fit_temporal_support=(
                        selection_fit_temporal_support
                    ),
                    feature_support=selection_feature_support,
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

    passing = [
        row for row in variants
        if row["selection_gate_passed"]
    ]
    selected = max(passing, key=_selection_key) if passing else None

    result: dict[str, object] = {
        "experiment_id": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_EXPERIMENT_ID
        ),
        "training_core_version": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_DECISION
        ),
        "dec174_merged_commit": DEC174_MERGED_COMMIT,
        "dec174_protocol_blob_sha": DEC174_PROTOCOL_BLOB_SHA,
        "predecessor_training_core_blob_sha": (
            PREDECESSOR_TRAINING_CORE_BLOB_SHA
        ),
        "predecessor_training_core_decision": (
            FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_DECISION
        ),
        "protocol_decision": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_DECISION
        ),
        "protocol_version": (
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_VERSION
        ),
        "protocol_fingerprint": (
            fit_temporal_feature_support_utility_protocol_fingerprint()
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
                CALIBRATION_REFERENCE_RULE
            ),
            "calibrated_percentile_rule": (
                CALIBRATED_PERCENTILE_RULE
            ),
            "robust_calibrated_score_rule": (
                ROBUST_CALIBRATED_SCORE_RULE
            ),
            "fit_temporal_support_references": support_evidence,
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
            "fit_temporal_feature_support_references": (
                feature_evidence
            ),
            "fit_temporal_feature_support_reference_count": (
                FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL
            ),
            "fit_temporal_feature_reference_rule": (
                FIT_TEMPORAL_FEATURE_REFERENCE_RULE
            ),
            "fit_temporal_feature_distance_rule": (
                FIT_TEMPORAL_FEATURE_DISTANCE_RULE
            ),
            "fit_temporal_feature_support_percentile_rule": (
                FIT_TEMPORAL_FEATURE_SUPPORT_PERCENTILE_RULE
            ),
            "robust_fit_temporal_feature_support_score_rule": (
                ROBUST_FIT_TEMPORAL_FEATURE_SUPPORT_SCORE_RULE
            ),
            "full_fit_single_model": {
                "status": "FORBIDDEN_BY_DEC150_DEC163_DEC174",
                "fit_attempt_count": 0,
            },
            "view_weight_search": {
                "status": "FORBIDDEN_BY_DEC150_DEC163_DEC174",
                "fit_attempt_count": 0,
            },
            "view_fallback": {
                "status": "FORBIDDEN_BY_DEC150_DEC163_DEC174",
                "fit_attempt_count": 0,
            },
            "selection_window_calibration": {
                "status": "FORBIDDEN_BY_DEC150_DEC163_DEC174",
                "fit_attempt_count": 0,
            },
            "hist_gradient_boosting_classifier": {
                "status": "EXCLUDED_BY_DEC150_DEC163_DEC174",
                "fit_attempt_count": 0,
            },
            "logistic_regression": {
                "status": "EXCLUDED_BY_DEC112_DEC150_DEC163_DEC174",
                "fit_attempt_count": 0,
            },
        },
        "selection": {
            "status": (
                "SELECTED"
                if selected is not None
                else (
                    "NO_FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_"
                    "STABLE_MODEL_CHALLENGER"
                )
            ),
            "row_count": selection_frame.height,
            "fit_temporal_feature_support_consensus": (
                selection_diagnostics
            ),
            "fit_temporal_feature_support_consensus_digest": (
                selection_consensus_digest
            ),
            "ranking_rule": RANKING_RULE,
            "selection_cutoff_rule": SELECTION_CUTOFF_RULE,
            "cutoff_tie_policy": CUTOFF_TIE_POLICY,
            "forward_application_rule": FORWARD_APPLICATION_RULE,
            "variants": variants,
            "selected_variant": (
                {
                    "model_family": "hist_gradient_boosting_regression",
                    "candidate_budget_anchor": int(
                        selected["candidate_budget_anchor"]
                    ),
                    "selection_derived_feature_support_cutoff": float(
                        selected[
                            "selection_derived_feature_support_cutoff"
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

    feature_cutoff = float(
        selected[
            "selection_derived_feature_support_cutoff"
        ]
    )
    utility_cutoff = float(
        selected["selection_derived_support_cutoff"]
    )
    pooled_cutoff = float(
        selected[
            "selection_derived_pooled_calibrated_cutoff"
        ]
    )
    raw_cutoff = float(
        selected["selection_derived_raw_cutoff"]
    )
    budget = int(selected["candidate_budget_anchor"])

    validation = _evaluate_forward_split_feature_support(
        fitted_models=fitted_models,
        pooled_calibration_references=pooled_calibration_references,
        support_references=support_references,
        feature_references=feature_references,
        frame=split_frames[VALIDATION_SPLIT.name],
        cell=cell,
        feature_cutoff=feature_cutoff,
        utility_cutoff=utility_cutoff,
        pooled_cutoff=pooled_cutoff,
        raw_cutoff=raw_cutoff,
        budget=budget,
        gate_scenarios=VALIDATION_GATE_SCENARIOS,
    )
    result["validation"] = validation
    if validation["status"] != "PASS":
        result["retrospective_holdout"] = {
            "status": "LOCKED_VALIDATION_REJECT"
        }
        result["result_fingerprint"] = _sha256(result)
        return result

    result["retrospective_holdout"] = (
        _evaluate_forward_split_feature_support(
            fitted_models=fitted_models,
            pooled_calibration_references=pooled_calibration_references,
            support_references=support_references,
            feature_references=feature_references,
            frame=split_frames[
                RETROSPECTIVE_HOLDOUT_SPLIT.name
            ],
            cell=cell,
            feature_cutoff=feature_cutoff,
            utility_cutoff=utility_cutoff,
            pooled_cutoff=pooled_cutoff,
            raw_cutoff=raw_cutoff,
            budget=budget,
            gate_scenarios=HOLDOUT_GATE_SCENARIOS,
        )
    )
    result["result_fingerprint"] = _sha256(result)
    return result


__all__ = [
    "BROKER_MUTATION_AUTHORIZED",
    "DEC174_MERGED_COMMIT",
    "DEC174_PROTOCOL_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_RESULT_EXECUTION_AUTHORIZED",
    "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_DECISION",
    "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_TRAINING_CORE_VERSION",
    "LIVE_ORDER_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "PREDECESSOR_TRAINING_CORE_BLOB_SHA",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "_build_fit_temporal_feature_support_references",
    "_candidate_directions_feature_support",
    "_derive_feature_support_cutoff",
    "_score_fit_temporal_feature_support",
    "_score_fit_temporal_feature_support_consensus",
    "_survival_percentiles",
    "run_fit_temporal_feature_support_utility_model_cell_core",
    "validate_fit_temporal_feature_support_utility_training_sources",
]
