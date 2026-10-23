from __future__ import annotations

from pathlib import Path
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
    _build_fit_temporal_feature_support_references,
    _score_fit_temporal_feature_support_consensus,
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
    RESIDUAL_DOWNSIDE_QUANTILE_RULE,
    ROBUST_RESIDUAL_BOUND_UTILITY_RULE,
    SELECTION_CUTOFF_RULE,
    UNTOUCHED_OOS,
    fit_temporal_residual_bound_utility_protocol_fingerprint,
)
from .model_successor_fit_temporal_residual_bound_utility_training import (
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_DECISION,
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_VERSION,
    _build_fit_temporal_residual_references,
    _candidate_directions_residual_bound,
    _derive_residual_bound_cutoff,
    _robust_residual_bound_utility,
    _sha256,
)
from .model_successor_fit_temporal_support_utility_protocol import (
    FIT_TEMPORAL_SUPPORT_PERCENTILE_RULE,
    FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL,
    FIT_TEMPORAL_SUPPORT_REFERENCE_RULE,
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


FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_EVALUATION_CORE_VERSION = (
    "fmp-exp054-fit-temporal-residual-bound-utility-evaluation-core-v1"
)
FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_EVALUATION_CORE_DECISION = "DEC-188"

DEC186_TRAINING_CORE_BLOB_SHA = "672e5ca6003181c831ab51259dee7176f0962f6e"
DEC187_ARTIFACT_CONTRACT_BLOB_SHA = "399bdea4a86945cbabfbb641c7c21d136b6c0b7d"
DEC187_MERGED_COMMIT = "1c56ec7241d5795791ac83f1b58ac875b74e9645"

RESULT_EXECUTION_AUTHORIZED = False
MODEL_FIT_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
SHADOW_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def validate_fit_temporal_residual_bound_evaluation_sources(
    *, repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "dec186_training_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_bound_utility_training.py",
            DEC186_TRAINING_CORE_BLOB_SHA,
        ),
        "dec187_artifact_contract": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_bound_utility_artifacts.py",
            DEC187_ARTIFACT_CONTRACT_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing EXP-054 evaluation dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-054 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha
    return {
        "evaluation_core_version": (
            FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_EVALUATION_CORE_VERSION
        ),
        "evaluation_core_decision": (
            FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_EVALUATION_CORE_DECISION
        ),
        "dec187_merged_commit": DEC187_MERGED_COMMIT,
        "dec186_training_core_blob_sha": actual["dec186_training_core"],
        "dec187_artifact_contract_blob_sha": actual["dec187_artifact_contract"],
        "result_execution_authorized": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
    }


def _score_view_predictions(
    *,
    fitted_models: Mapping[str, Mapping[str, object]],
    frame: pl.DataFrame,
    cell: ModelCell,
    expected_row_ids: Sequence[str],
) -> tuple[
    dict[str, dict[str, np.ndarray]],
    dict[str, dict[str, str]],
]:
    predictions: dict[str, dict[str, np.ndarray]] = {}
    digests: dict[str, dict[str, str]] = {}
    for view_name in sorted(fitted_models):
        target_predictions: dict[str, np.ndarray] = {}
        target_digests: dict[str, str] = {}
        for target in FINANCIAL_TARGET_COLUMNS:
            values, digest, row_ids = _predecessor_score_regressor(
                fitted_models[view_name][target],
                frame,
                cell=cell,
            )
            if tuple(row_ids) != tuple(expected_row_ids):
                raise ValueError("EXP-054 view prediction row identity drift")
            array = np.asarray(values, dtype=np.float64)
            if array.shape != (frame.height,) or not np.isfinite(array).all():
                raise ValueError("EXP-054 view prediction values invalid")
            target_predictions[target] = array
            target_digests[target] = digest
        predictions[view_name] = target_predictions
        digests[view_name] = target_digests
    return predictions, digests


def _score_residual_bound_consensus(
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
        _,
    ) = _score_fit_temporal_feature_support_consensus(
        fitted_models=fitted_models,
        pooled_calibration_references=pooled_calibration_references,
        support_references=support_references,
        feature_references=feature_references,
        frame=frame,
        cell=cell,
    )
    view_predictions, view_prediction_digests = _score_view_predictions(
        fitted_models=fitted_models,
        frame=frame,
        cell=cell,
        expected_row_ids=row_ids,
    )
    residual_bound_utility = _robust_residual_bound_utility(
        directions=directions,
        view_predictions=view_predictions,
        residual_references=residual_references,
    )
    eligible = np.isin(
        directions,
        np.asarray(["LONG", "SHORT"], dtype=object),
    )
    eligible_values = residual_bound_utility[eligible]
    if bool(eligible.any()) and not np.isfinite(eligible_values).all():
        raise ValueError("EXP-054 eligible residual-bound utility invalid")

    diagnostics = dict(predecessor_diagnostics)
    diagnostics.update(
        {
            "fit_temporal_residual_reference_count": (
                FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL
            ),
            "minimum_robust_fit_temporal_residual_bound_utility": (
                float(np.min(eligible_values))
                if eligible_values.size
                else None
            ),
            "maximum_robust_fit_temporal_residual_bound_utility": (
                float(np.max(eligible_values))
                if eligible_values.size
                else None
            ),
            "view_prediction_digests": view_prediction_digests,
        }
    )
    digest = _sha256(
        {
            "row_ids": list(row_ids),
            "directions": directions.tolist(),
            "raw_utility": raw_utility.tolist(),
            "pooled_calibrated_utility": pooled_calibrated_utility.tolist(),
            "fit_temporal_support": fit_temporal_support.tolist(),
            "feature_support": feature_support.tolist(),
            "residual_bound_utility": residual_bound_utility.tolist(),
            "fit_temporal_residual_reference_count": (
                FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL
            ),
        }
    )
    return (
        directions,
        raw_utility,
        pooled_calibrated_utility,
        fit_temporal_support,
        feature_support,
        residual_bound_utility,
        diagnostics,
        row_ids,
        digest,
    )


def _evaluate_residual_bound_cutoff(
    frame: pl.DataFrame,
    *,
    directions: np.ndarray,
    raw_utility: np.ndarray,
    pooled_calibrated_utility: np.ndarray,
    fit_temporal_support: np.ndarray,
    feature_support: np.ndarray,
    residual_bound_utility: np.ndarray,
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
    raw_utility: np.ndarray,
    pooled_calibrated_utility: np.ndarray,
    fit_temporal_support: np.ndarray,
    feature_support: np.ndarray,
    residual_bound_utility: np.ndarray,
    residual_bound_cutoff: float,
    feature_cutoff: float,
    utility_cutoff: float,
    pooled_cutoff: float,
    raw_cutoff: float,
    budget: int,
    cell: ModelCell,
    full_selection_candidate_count: int,
) -> dict[str, object]:
    lengths = (
        len(directions),
        len(raw_utility),
        len(pooled_calibrated_utility),
        len(fit_temporal_support),
        len(feature_support),
        len(residual_bound_utility),
    )
    if any(value != selection_frame.height for value in lengths):
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
            raw_utility=raw_utility[index_array],
            pooled_calibrated_utility=pooled_calibrated_utility[index_array],
            fit_temporal_support=fit_temporal_support[index_array],
            feature_support=feature_support[index_array],
            residual_bound_utility=residual_bound_utility[index_array],
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
    ) = _score_residual_bound_consensus(
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
        raw_utility=raw_utility,
        pooled_calibrated_utility=pooled_calibrated_utility,
        fit_temporal_support=fit_temporal_support,
        feature_support=feature_support,
        residual_bound_utility=residual_bound_utility,
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
        "fit_temporal_residual_bound_consensus": diagnostics,
        "fit_temporal_residual_bound_consensus_digest": digest,
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
        empty = [
            name for name, frame in split_frames.items() if frame.is_empty()
        ]
        raise ValueError(f"EXP-054 model cell has empty required split(s): {empty}")

    regime_frames = {
        split.name: _base._split_frame(joined, split)
        for split in _predecessor_fit_regime_splits()
    }
    if set(regime_frames) != set(PREDECESSOR_REGIME_NAMES):
        raise ValueError("EXP-054 predecessor fit-regime identity drift")
    if any(frame.is_empty() for frame in regime_frames.values()):
        empty = [
            name for name, frame in regime_frames.items() if frame.is_empty()
        ]
        raise ValueError(f"EXP-054 model cell has empty fit regime(s): {empty}")

    view_frames = _build_jackknife_view_frames(regime_frames)
    fitted_models: dict[str, dict[str, object]] = {}
    fit_evidence: dict[str, object] = {}
    view_regimes = _jackknife_view_regime_names()
    for view_name, fit_frame in view_frames.items():
        target_models: dict[str, object] = {}
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

    (
        pooled_calibration_references,
        pooled_calibration_evidence,
    ) = _build_calibration_references(
        fitted_models=fitted_models,
        regime_frames=regime_frames,
        cell=cell,
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
    residual_references, residual_evidence = (
        _build_fit_temporal_residual_references(
            fitted_models=fitted_models,
            regime_frames=regime_frames,
            cell=cell,
        )
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
    ) = _score_residual_bound_consensus(
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
            raw_utility=selection_raw_utility,
            pooled_calibrated_utility=selection_pooled_calibrated_utility,
            fit_temporal_support=selection_fit_temporal_support,
            feature_support=selection_feature_support,
            residual_bound_utility=selection_residual_bound_utility,
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
                raw_utility=selection_raw_utility,
                pooled_calibrated_utility=selection_pooled_calibrated_utility,
                fit_temporal_support=selection_fit_temporal_support,
                feature_support=selection_feature_support,
                residual_bound_utility=selection_residual_bound_utility,
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
        "training_core_version": (
            FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_DECISION
        ),
        "evaluation_core_version": (
            FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_EVALUATION_CORE_VERSION
        ),
        "evaluation_core_decision": (
            FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_EVALUATION_CORE_DECISION
        ),
        "protocol_decision": FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_PROTOCOL_DECISION,
        "protocol_version": FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_PROTOCOL_VERSION,
        "protocol_fingerprint": (
            fit_temporal_residual_bound_utility_protocol_fingerprint()
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
            name: frame.height for name, frame in split_frames.items()
        },
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
            "fit_temporal_support_reference_count": (
                FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL
            ),
            "fit_temporal_support_reference_rule": FIT_TEMPORAL_SUPPORT_REFERENCE_RULE,
            "fit_temporal_support_percentile_rule": (
                FIT_TEMPORAL_SUPPORT_PERCENTILE_RULE
            ),
            "robust_fit_temporal_support_score_rule": (
                ROBUST_FIT_TEMPORAL_SUPPORT_SCORE_RULE
            ),
            "fit_temporal_feature_support_references": feature_evidence,
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
            "fit_temporal_residual_references": residual_evidence,
            "fit_temporal_residual_reference_count": (
                FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL
            ),
            "fit_temporal_residual_reference_rule": (
                FIT_TEMPORAL_RESIDUAL_REFERENCE_RULE
            ),
            "residual_downside_quantile_rule": RESIDUAL_DOWNSIDE_QUANTILE_RULE,
            "robust_residual_bound_utility_rule": (
                ROBUST_RESIDUAL_BOUND_UTILITY_RULE
            ),
            "full_fit_single_model": {
                "status": "FORBIDDEN_BY_DEC150_DEC163_DEC174_DEC185",
                "fit_attempt_count": 0,
            },
            "view_weight_search": {
                "status": "FORBIDDEN_BY_DEC150_DEC163_DEC174_DEC185",
                "fit_attempt_count": 0,
            },
            "view_fallback": {
                "status": "FORBIDDEN_BY_DEC150_DEC163_DEC174_DEC185",
                "fit_attempt_count": 0,
            },
            "selection_window_calibration": {
                "status": "FORBIDDEN_BY_DEC150_DEC163_DEC174_DEC185",
                "fit_attempt_count": 0,
            },
        },
        "selection": {
            "status": (
                "SELECTED"
                if selected is not None
                else "NO_FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_STABLE_MODEL_CHALLENGER"
            ),
            "row_count": selection_frame.height,
            "fit_temporal_residual_bound_consensus": selection_diagnostics,
            "fit_temporal_residual_bound_consensus_digest": (
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

    residual_bound_cutoff = float(
        selected["selection_derived_residual_bound_cutoff"]
    )
    feature_cutoff = float(
        selected["selection_derived_feature_support_cutoff"]
    )
    utility_cutoff = float(selected["selection_derived_support_cutoff"])
    pooled_cutoff = float(
        selected["selection_derived_pooled_calibrated_cutoff"]
    )
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
        result["retrospective_holdout"] = {
            "status": "LOCKED_VALIDATION_REJECT"
        }
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


__all__ = [
    "BROKER_MUTATION_AUTHORIZED",
    "DEC186_TRAINING_CORE_BLOB_SHA",
    "DEC187_ARTIFACT_CONTRACT_BLOB_SHA",
    "DEC187_MERGED_COMMIT",
    "DEMO_ORDER_AUTHORIZED",
    "FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_EVALUATION_CORE_DECISION",
    "FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_EVALUATION_CORE_VERSION",
    "LIVE_ORDER_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "RESULT_EXECUTION_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "_evaluate_forward_split_residual_bound",
    "_evaluate_residual_bound_cutoff",
    "_evaluate_temporal_stability_residual_bound",
    "_score_residual_bound_consensus",
    "run_fit_temporal_residual_bound_utility_model_cell_core",
    "validate_fit_temporal_residual_bound_evaluation_sources",
]
