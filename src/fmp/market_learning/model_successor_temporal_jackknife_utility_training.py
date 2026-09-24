from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
import polars as pl

from . import model_training as _base
from .contracts import EVIDENCE_LABEL
from .model_protocol import (
    DIAGNOSTIC_SCENARIOS,
    HOLDOUT_GATE_SCENARIOS,
    MODEL_CELLS,
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
)
from .model_successor_regime_utility_training import (
    REGIME_UTILITY_TRAINING_CORE_DECISION,
    REGIME_UTILITY_TRAINING_CORE_VERSION,
    _candidate_directions as _predecessor_candidate_directions,
    _derive_utility_cutoff as _predecessor_derive_utility_cutoff,
    _evaluate_temporal_stability as _predecessor_evaluate_temporal_stability,
    _evaluate_utility_cutoff as _predecessor_evaluate_utility_cutoff,
    _fit_regime_splits as _predecessor_fit_regime_splits,
    _fit_regressor as _predecessor_fit_regressor,
    _regime_utility_direction_score as _predecessor_direction_score,
    _score_regressor as _predecessor_score_regressor,
    _selection_key as _predecessor_selection_key,
    _target_summary as _predecessor_target_summary,
    _utility_consensus_digest as _predecessor_consensus_digest,
    validate_regime_utility_training_sources,
)
from .model_successor_stability_protocol import (
    MIN_STABILITY_WINDOW_CANDIDATE_SHARE,
)
from .model_successor_temporal_jackknife_utility_protocol import (
    FINANCIAL_TARGET_COLUMNS,
    FIT_JACKKNIFE_VIEWS,
    PREDECESSOR_REGIME_NAMES,
    PRIOR_RESULT_INFORMED,
    TEMPORAL_JACKKNIFE_UTILITY_EXPERIMENT_ID,
    TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_DECISION,
    TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_VERSION,
    UNTOUCHED_OOS,
    temporal_jackknife_utility_protocol_fingerprint,
)


TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_VERSION = (
    "fmp-exp050-temporal-jackknife-utility-training-core-v1"
)
TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_DECISION = "DEC-142"

DEC141_MERGED_COMMIT = (
    "4729da0e769f76f44b97ff6349ee25c5b7c0f5c7"
)
DEC141_PROTOCOL_BLOB_SHA = (
    "b41b817b03aa0cc03a9d893227caa399b46d3cf8"
)
PREDECESSOR_TRAINING_CORE_BLOB_SHA = (
    "e1018b20210b7bb8d666071d8eb878aba5899111"
)

TEMPORAL_JACKKNIFE_UTILITY_RESULT_EXECUTION_AUTHORIZED = False
MODEL_FIT_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
SHADOW_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False

_candidate_directions = _predecessor_candidate_directions
_derive_utility_cutoff = _predecessor_derive_utility_cutoff
_selection_key = _predecessor_selection_key
_temporal_jackknife_utility_direction_score = (
    _predecessor_direction_score
)


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def validate_temporal_jackknife_utility_training_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "dec141_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_temporal_jackknife_utility_protocol.py",
            DEC141_PROTOCOL_BLOB_SHA,
        ),
        "predecessor_training_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_regime_utility_training.py",
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(
                f"missing EXP-050 training dependency: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-050 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    predecessor = validate_regime_utility_training_sources(
        repository_root=root,
    )
    if predecessor[
        "regime_utility_training_core_decision"
    ] != REGIME_UTILITY_TRAINING_CORE_DECISION:
        raise ValueError(
            "EXP-050 predecessor training decision drift"
        )
    if predecessor["model_fit_authorized"] is not False:
        raise ValueError(
            "EXP-050 predecessor model fit must remain closed"
        )
    if predecessor[
        "regime_utility_result_execution_authorized"
    ] is not False:
        raise ValueError(
            "EXP-050 predecessor result execution must remain closed"
        )

    protocol_fingerprint = (
        temporal_jackknife_utility_protocol_fingerprint()
    )
    if len(protocol_fingerprint) != 64:
        raise ValueError(
            "EXP-050 temporal-jackknife protocol fingerprint is invalid"
        )

    return {
        "temporal_jackknife_utility_training_core_version": (
            TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_VERSION
        ),
        "temporal_jackknife_utility_training_core_decision": (
            TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_DECISION
        ),
        "dec141_merged_commit": DEC141_MERGED_COMMIT,
        "dec141_protocol_blob_sha": actual[
            "dec141_protocol"
        ],
        "predecessor_training_core_blob_sha": actual[
            "predecessor_training_core"
        ],
        "predecessor_training_core_decision": (
            REGIME_UTILITY_TRAINING_CORE_DECISION
        ),
        "predecessor_training_core_version": (
            REGIME_UTILITY_TRAINING_CORE_VERSION
        ),
        "temporal_jackknife_utility_protocol_fingerprint": (
            protocol_fingerprint
        ),
        "temporal_jackknife_utility_result_execution_authorized": (
            False
        ),
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
    }


def _jackknife_view_regime_names() -> dict[str, tuple[str, ...]]:
    expected_regimes = set(PREDECESSOR_REGIME_NAMES)
    views: dict[str, tuple[str, ...]] = {}
    excluded_seen: set[str] = set()

    for raw in FIT_JACKKNIFE_VIEWS:
        name = str(raw["name"])
        excluded = str(raw["excluded_regime"])
        included = tuple(
            str(value)
            for value in raw["included_regimes"]
        )
        if name in views:
            raise ValueError(
                "EXP-050 duplicate jackknife view name"
            )
        if excluded not in expected_regimes:
            raise ValueError(
                "EXP-050 jackknife excluded regime drift"
            )
        if (
            len(included) != 2
            or len(set(included)) != 2
            or excluded in included
            or set(included)
            != expected_regimes - {excluded}
        ):
            raise ValueError(
                "EXP-050 jackknife included-regime drift"
            )
        views[name] = included
        excluded_seen.add(excluded)

    if (
        len(views) != 3
        or excluded_seen != expected_regimes
    ):
        raise ValueError(
            "EXP-050 jackknife view coverage drift"
        )
    return views


def _build_jackknife_view_frames(
    regime_frames: Mapping[str, pl.DataFrame],
) -> dict[str, pl.DataFrame]:
    if set(regime_frames) != set(PREDECESSOR_REGIME_NAMES):
        raise ValueError(
            "EXP-050 fit-regime frame set mismatch"
        )
    if any(
        frame.is_empty()
        for frame in regime_frames.values()
    ):
        raise ValueError(
            "EXP-050 jackknife source regime must be non-empty"
        )

    views: dict[str, pl.DataFrame] = {}
    for view_name, included in (
        _jackknife_view_regime_names().items()
    ):
        pieces = [
            regime_frames[regime_name]
            for regime_name in included
        ]
        combined = pl.concat(
            pieces,
            how="vertical",
        )
        expected_height = sum(
            frame.height
            for frame in pieces
        )
        if (
            combined.is_empty()
            or combined.height != expected_height
        ):
            raise ValueError(
                "EXP-050 jackknife view row accounting drift"
            )
        views[view_name] = combined

    return views


def _jackknife_utility_diagnostics(
    *,
    directions: np.ndarray,
    utility: np.ndarray,
    view_prediction_digests: Mapping[
        str,
        Mapping[str, str],
    ],
) -> dict[str, object]:
    if len(directions) != len(utility):
        raise ValueError(
            "EXP-050 utility diagnostic row mismatch"
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
        "view_prediction_digests": {
            view: dict(values)
            for view, values in (
                view_prediction_digests.items()
            )
        },
    }


def _score_jackknife_utility_consensus(
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
    expected_views = set(
        _jackknife_view_regime_names()
    )
    if set(fitted_models) != expected_views:
        raise ValueError(
            "EXP-050 fitted jackknife model set mismatch"
        )

    matrices: list[np.ndarray] = []
    digests: dict[str, dict[str, str]] = {}
    row_ids_reference: tuple[str, ...] | None = None

    for view_name in _jackknife_view_regime_names():
        target_models = fitted_models[view_name]
        if set(target_models) != set(
            FINANCIAL_TARGET_COLUMNS
        ):
            raise ValueError(
                "EXP-050 fitted target model set mismatch"
            )

        target_predictions: list[np.ndarray] = []
        target_digests: dict[str, str] = {}
        for target_column in FINANCIAL_TARGET_COLUMNS:
            (
                predictions,
                digest,
                row_ids,
            ) = _predecessor_score_regressor(
                target_models[target_column],
                frame,
                cell=cell,
            )
            if row_ids_reference is None:
                row_ids_reference = tuple(row_ids)
            elif tuple(row_ids) != row_ids_reference:
                raise ValueError(
                    "EXP-050 jackknife score row identity mismatch"
                )
            target_predictions.append(predictions)
            target_digests[target_column] = digest

        matrices.append(
            np.column_stack(target_predictions)
        )
        digests[view_name] = target_digests

    if row_ids_reference is None:
        raise ValueError(
            "EXP-050 jackknife scoring produced no row identity"
        )

    directions, utility = (
        _temporal_jackknife_utility_direction_score(
            matrices
        )
    )
    diagnostics = _jackknife_utility_diagnostics(
        directions=directions,
        utility=utility,
        view_prediction_digests=digests,
    )
    consensus_digest = _predecessor_consensus_digest(
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
    ) = _score_jackknife_utility_consensus(
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
    evaluated = _predecessor_evaluate_utility_cutoff(
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
        "temporal_jackknife_utility_consensus": (
            diagnostics
        ),
        "temporal_jackknife_utility_consensus_digest": (
            consensus_digest
        ),
        **evaluated,
    }


def run_temporal_jackknife_utility_model_cell_core(
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
            "EXP-050 model cell has empty required "
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
            "EXP-050 predecessor fit-regime identity drift"
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
                "EXP-050 jackknife excluded-regime count drift"
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

    selection_frame = split_frames[
        SELECTION_SPLIT.name
    ]
    (
        selection_directions,
        selection_utility,
        selection_diagnostics,
        selection_row_ids,
        selection_consensus_digest,
    ) = _score_jackknife_utility_consensus(
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
        evaluated = _predecessor_evaluate_utility_cutoff(
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
            stability = (
                _predecessor_evaluate_temporal_stability(
                    selection_frame=selection_frame,
                    directions=selection_directions,
                    utility=selection_utility,
                    cutoff=cutoff,
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
            TEMPORAL_JACKKNIFE_UTILITY_EXPERIMENT_ID
        ),
        "training_core_version": (
            TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_DECISION
        ),
        "dec141_merged_commit": DEC141_MERGED_COMMIT,
        "dec141_protocol_blob_sha": (
            DEC141_PROTOCOL_BLOB_SHA
        ),
        "predecessor_training_core_blob_sha": (
            PREDECESSOR_TRAINING_CORE_BLOB_SHA
        ),
        "predecessor_training_core_decision": (
            REGIME_UTILITY_TRAINING_CORE_DECISION
        ),
        "protocol_decision": (
            TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_DECISION
        ),
        "protocol_version": (
            TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_VERSION
        ),
        "protocol_fingerprint": (
            temporal_jackknife_utility_protocol_fingerprint()
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
            "full_fit_single_model": {
                "status": "FORBIDDEN_BY_DEC141",
                "fit_attempt_count": 0,
            },
            "view_weight_search": {
                "status": "FORBIDDEN_BY_DEC141",
                "fit_attempt_count": 0,
            },
            "view_fallback": {
                "status": "FORBIDDEN_BY_DEC141",
                "fit_attempt_count": 0,
            },
            "hist_gradient_boosting_classifier": {
                "status": "EXCLUDED_BY_DEC141",
                "fit_attempt_count": 0,
            },
            "logistic_regression": {
                "status": "EXCLUDED_BY_DEC112_DEC141",
                "fit_attempt_count": 0,
            },
        },
        "selection": {
            "status": (
                "SELECTED"
                if selected is not None
                else (
                    "NO_TEMPORAL_JACKKNIFE_UTILITY_"
                    "STABLE_MODEL_CHALLENGER"
                )
            ),
            "row_count": selection_frame.height,
            "temporal_jackknife_utility_consensus": (
                selection_diagnostics
            ),
            "temporal_jackknife_utility_consensus_digest": (
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
    "BROKER_MUTATION_AUTHORIZED",
    "DEC141_MERGED_COMMIT",
    "DEC141_PROTOCOL_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "LIVE_ORDER_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "PREDECESSOR_TRAINING_CORE_BLOB_SHA",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "TEMPORAL_JACKKNIFE_UTILITY_RESULT_EXECUTION_AUTHORIZED",
    "TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_DECISION",
    "TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_VERSION",
    "TRADING_AUTHORIZED",
    "_build_jackknife_view_frames",
    "_candidate_directions",
    "_derive_utility_cutoff",
    "_jackknife_view_regime_names",
    "_selection_key",
    "_temporal_jackknife_utility_direction_score",
    "run_temporal_jackknife_utility_model_cell_core",
    "validate_temporal_jackknife_utility_training_sources",
]
