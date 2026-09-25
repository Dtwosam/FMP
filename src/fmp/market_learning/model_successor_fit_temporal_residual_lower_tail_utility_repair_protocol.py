from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from .model_successor_fit_temporal_residual_lower_tail_utility_failure_diagnostics import (
    EXPECTED_STATIC_MISSING_PREDECESSOR_EXPORTS,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_IMPLEMENTATION_DIAGNOSTIC_DECISION,
    IMPLEMENTATION_DIAGNOSTIC_CLASSIFICATION,
    IMPLEMENTATION_REPAIR_RULE,
    SUCCESSOR_HISTORICAL_RESULT_EXECUTION_AUTHORIZED,
    SUCCESSOR_MODEL_FIT_AUTHORIZED,
    SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED,
)
from .model_successor_fit_temporal_residual_lower_tail_utility_protocol import (
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_BOUND_COUNT_PER_ROW,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_COUNT,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_FRACTION,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_RULE,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_PROTOCOL_VERSION,
    RESIDUAL_LOWER_TAIL_ELIGIBILITY_RULE,
    fit_temporal_residual_lower_tail_utility_protocol_fingerprint,
    fit_temporal_residual_lower_tail_utility_protocol_payload,
)


FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_EXPERIMENT_ID = (
    "EXP-20260925-057"
)
FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_PROTOCOL_VERSION = (
    "fmp-exp057-fit-temporal-residual-lower-tail-utility-"
    "implementation-repair-protocol-v1"
)
FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_PROTOCOL_DECISION = (
    "DEC-220"
)

DEC219_MERGED_COMMIT = "acc0fab2219b76af061d602863c257b335a32d05"
DEC219_DIAGNOSTIC_BLOB_SHA = (
    "d94fb02c5037aec4c2cd2a1b020aa1317193d862"
)
DEC218_RESULT_DECISION_BLOB_SHA = (
    "75fc25ae97c03730ab75a3036059f761d8234630"
)
EXP056_PROTOCOL_BLOB_SHA = "14d8fe5d0530f44acaa7084c6d78d1c19bd21d8d"
EXP056_TRAINING_CORE_BLOB_SHA = (
    "c472ed48e7b79d22056d43deb0fe09166ccf34c9"
)

PRIOR_RESULT_INFORMED = True
UNTOUCHED_OOS = False

IMPLEMENTATION_DEPENDENCY_REPAIR_AUTHORIZED = True
PROTOCOL_SEMANTICS_CHANGE_AUTHORIZED = False

FEATURE_CHANGE_AUTHORIZED = False
FINANCIAL_TARGET_CHANGE_AUTHORIZED = False
OUTER_CHRONOLOGY_CHANGE_AUTHORIZED = False
HGB_STRUCTURAL_CONFIG_CHANGE_AUTHORIZED = False
JACKKNIFE_VIEW_CHANGE_AUTHORIZED = False
UNANIMOUS_UTILITY_CONSENSUS_CHANGE_AUTHORIZED = False
POSITIVE_UTILITY_REQUIREMENT_CHANGE_AUTHORIZED = False
POOLED_OUT_OF_FIT_CALIBRATION_CHANGE_AUTHORIZED = False
FIT_TEMPORAL_UTILITY_SUPPORT_CHANGE_AUTHORIZED = False
FIT_TEMPORAL_FEATURE_SUPPORT_CHANGE_AUTHORIZED = False
FIT_TEMPORAL_RESIDUAL_BOUND_CHANGE_AUTHORIZED = False
FIT_TEMPORAL_RESIDUAL_BREADTH_CHANGE_AUTHORIZED = False
FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_CHANGE_AUTHORIZED = False
SELECTION_WINDOW_CALIBRATION_AUTHORIZED = False
SELECTION_WINDOW_QUOTA_AUTHORIZED = False
VALIDATION_CALIBRATION_AUTHORIZED = False
HOLDOUT_CALIBRATION_AUTHORIZED = False
REALIZED_SELECTION_OUTCOME_RANKING_AUTHORIZED = False
DENSITY_ANCHOR_CHANGE_AUTHORIZED = False
MIN_DIRECTIONAL_CANDIDATE_COUNT_CHANGE_AUTHORIZED = False
STABILITY_SCREEN_CHANGE_AUTHORIZED = False
PER_WINDOW_FINANCIAL_GATE_CHANGE_AUTHORIZED = False
PER_WINDOW_CUTOFF_TUNING_AUTHORIZED = False
LOGISTIC_REINTRODUCTION_AUTHORIZED = False
CLASSIFIER_FALLBACK_AUTHORIZED = False

MODEL_PROTOCOL_RESULT_AUTHORIZED = False
MODEL_FIT_AUTHORIZED = False
HISTORICAL_RESULT_EXECUTION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
SHADOW_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


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


def validate_fit_temporal_residual_lower_tail_utility_repair_predecessor_identity(
) -> None:
    if (
        FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_IMPLEMENTATION_DIAGNOSTIC_DECISION
        != "DEC-219"
    ):
        raise ValueError("EXP-057 predecessor diagnostic decision drift")
    if IMPLEMENTATION_DIAGNOSTIC_CLASSIFICATION != (
        "EXP056_IMPLEMENTATION_FAILED_BEFORE_EVIDENCE_DUE_INTERMEDIATE_"
        "PREDECESSOR_EXPORT_DRIFT"
    ):
        raise ValueError("EXP-057 predecessor diagnostic classification drift")
    if SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED is not True:
        raise ValueError("EXP-057 successor protocol source is not open")
    if SUCCESSOR_MODEL_FIT_AUTHORIZED is not False:
        raise ValueError("EXP-057 predecessor successor fit must be closed")
    if SUCCESSOR_HISTORICAL_RESULT_EXECUTION_AUTHORIZED is not False:
        raise ValueError(
            "EXP-057 predecessor successor execution must be closed"
        )
    if tuple(sorted(EXPECTED_STATIC_MISSING_PREDECESSOR_EXPORTS)) != (
        "FIT_TEMPORAL_FEATURE_SUPPORT_PERCENTILE_RULE",
        "FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL",
        "FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL",
        "FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL",
        "MIN_STABILITY_WINDOW_CANDIDATE_SHARE",
        "ROBUST_FIT_TEMPORAL_FEATURE_SUPPORT_SCORE_RULE",
        "ROBUST_FIT_TEMPORAL_SUPPORT_SCORE_RULE",
    ):
        raise ValueError("EXP-057 repair export inventory drift")

    if FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_EXPERIMENT_ID != (
        "EXP-20260925-056"
    ):
        raise ValueError("EXP-057 semantic predecessor experiment drift")
    if FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_PROTOCOL_DECISION != "DEC-209":
        raise ValueError("EXP-057 semantic predecessor decision drift")
    if FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_PROTOCOL_VERSION != (
        "fmp-exp056-fit-temporal-residual-lower-tail-utility-protocol-v1"
    ):
        raise ValueError("EXP-057 semantic predecessor version drift")
    if FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_BOUND_COUNT_PER_ROW != 12:
        raise ValueError("EXP-057 lower-bound inventory drift")
    if FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_COUNT != 3:
        raise ValueError("EXP-057 lower-tail count drift")
    if FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_FRACTION != 0.25:
        raise ValueError("EXP-057 lower-tail fraction drift")

    predecessor = fit_temporal_residual_lower_tail_utility_protocol_payload()
    if predecessor["experiment_id"] != (
        FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_EXPERIMENT_ID
    ):
        raise ValueError("EXP-057 predecessor payload experiment drift")

    selection = predecessor.get("selection")
    if not isinstance(selection, dict):
        raise ValueError("EXP-057 predecessor selection payload missing")
    if selection.get("candidate_budget_anchors") != [250, 500, 1000]:
        raise ValueError("EXP-057 predecessor budget identity drift")
    if selection.get("ranking_order") != [
        "fit_temporal_residual_lower_tail_mean_desc",
        "fit_temporal_residual_breadth_desc",
        "robust_fit_temporal_residual_bound_utility_desc",
        "robust_fit_temporal_feature_support_desc",
        "robust_fit_temporal_support_desc",
        "robust_pooled_calibrated_utility_desc",
        "robust_raw_utility_desc",
        "row_identity_asc",
    ]:
        raise ValueError("EXP-057 predecessor ranking identity drift")

    stability = selection.get("temporal_stability")
    if not isinstance(stability, dict):
        raise ValueError("EXP-057 predecessor stability payload missing")
    if len(stability.get("windows", [])) != 4:
        raise ValueError("EXP-057 predecessor stability-window count drift")
    if (
        stability.get("minimum_directional_candidate_share_per_window")
        != 0.10
    ):
        raise ValueError("EXP-057 predecessor stability-share drift")


def fit_temporal_residual_lower_tail_utility_repair_protocol_payload(
) -> dict[str, object]:
    validate_fit_temporal_residual_lower_tail_utility_repair_predecessor_identity()
    predecessor = fit_temporal_residual_lower_tail_utility_protocol_payload()

    chronology = deepcopy(predecessor["chronology"])
    model_family = deepcopy(predecessor["model_family"])
    temporal_jackknife = deepcopy(predecessor["temporal_jackknife"])
    utility_consensus = deepcopy(predecessor["utility_consensus"])
    pooled_calibration = deepcopy(
        predecessor["out_of_fit_utility_calibration"]
    )
    utility_support = deepcopy(
        predecessor["fit_temporal_support_calibration"]
    )
    feature_support = deepcopy(
        predecessor["fit_temporal_feature_support"]
    )
    residual_bound = deepcopy(
        predecessor["fit_temporal_residual_bound"]
    )
    residual_breadth = deepcopy(
        predecessor["fit_temporal_residual_breadth"]
    )
    residual_lower_tail = deepcopy(
        predecessor["fit_temporal_residual_lower_tail"]
    )
    selection = deepcopy(predecessor["selection"])
    validation = deepcopy(predecessor["validation"])
    holdout = deepcopy(predecessor["retrospective_holdout"])

    utility_consensus["fit_temporal_residual_lower_tail_added"] = False
    utility_consensus["fit_temporal_residual_lower_tail_retained"] = True

    residual_lower_tail["authorized_protocol_change"] = False
    residual_lower_tail["retained_from_exp056"] = True

    return {
        "protocol_version": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_PROTOCOL_VERSION
        ),
        "protocol_decision": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_PROTOCOL_DECISION
        ),
        "experiment_id": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_EXPERIMENT_ID
        ),
        "semantic_predecessor_experiment_id": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_EXPERIMENT_ID
        ),
        "semantic_predecessor_protocol_decision": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_PROTOCOL_DECISION
        ),
        "semantic_predecessor_protocol_fingerprint": (
            fit_temporal_residual_lower_tail_utility_protocol_fingerprint()
        ),
        "failed_predecessor_result_decision": "DEC-218",
        "failure_diagnostic_decision": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_IMPLEMENTATION_DIAGNOSTIC_DECISION
        ),
        "failure_diagnostic_classification": (
            IMPLEMENTATION_DIAGNOSTIC_CLASSIFICATION
        ),
        "prior_result_informed": PRIOR_RESULT_INFORMED,
        "untouched_oos": UNTOUCHED_OOS,
        "chronology": chronology,
        "model_family": model_family,
        "temporal_jackknife": temporal_jackknife,
        "utility_consensus": utility_consensus,
        "out_of_fit_utility_calibration": pooled_calibration,
        "fit_temporal_support_calibration": utility_support,
        "fit_temporal_feature_support": feature_support,
        "fit_temporal_residual_bound": residual_bound,
        "fit_temporal_residual_breadth": residual_breadth,
        "fit_temporal_residual_lower_tail": residual_lower_tail,
        "selection": selection,
        "validation": validation,
        "retrospective_holdout": holdout,
        "implementation_repair": {
            "authorized": IMPLEMENTATION_DEPENDENCY_REPAIR_AUTHORIZED,
            "protocol_semantics_change_authorized": (
                PROTOCOL_SEMANTICS_CHANGE_AUTHORIZED
            ),
            "source_training_core_blob_sha": (
                EXP056_TRAINING_CORE_BLOB_SHA
            ),
            "from_module_role": "exp055_intermediate_predecessor",
            "to_module_role": "exp054_base_predecessor",
            "from_attribute_root": "_predecessor",
            "to_attribute_root": "_base",
            "exact_attribute_names": list(
                sorted(EXPECTED_STATIC_MISSING_PREDECESSOR_EXPORTS)
            ),
            "exact_attribute_count": 7,
            "repair_rule": IMPLEMENTATION_REPAIR_RULE,
        },
        "authorization": {
            "implementation_dependency_repair_authorized": (
                IMPLEMENTATION_DEPENDENCY_REPAIR_AUTHORIZED
            ),
            "protocol_semantics_change_authorized": (
                PROTOCOL_SEMANTICS_CHANGE_AUTHORIZED
            ),
            "model_protocol_result_authorized": (
                MODEL_PROTOCOL_RESULT_AUTHORIZED
            ),
            "model_fit_authorized": MODEL_FIT_AUTHORIZED,
            "historical_result_execution_authorized": (
                HISTORICAL_RESULT_EXECUTION_AUTHORIZED
            ),
            "feature_change_authorized": FEATURE_CHANGE_AUTHORIZED,
            "financial_target_change_authorized": (
                FINANCIAL_TARGET_CHANGE_AUTHORIZED
            ),
            "outer_chronology_change_authorized": (
                OUTER_CHRONOLOGY_CHANGE_AUTHORIZED
            ),
            "hgb_structural_config_change_authorized": (
                HGB_STRUCTURAL_CONFIG_CHANGE_AUTHORIZED
            ),
            "jackknife_view_change_authorized": (
                JACKKNIFE_VIEW_CHANGE_AUTHORIZED
            ),
            "unanimous_utility_consensus_change_authorized": (
                UNANIMOUS_UTILITY_CONSENSUS_CHANGE_AUTHORIZED
            ),
            "positive_utility_requirement_change_authorized": (
                POSITIVE_UTILITY_REQUIREMENT_CHANGE_AUTHORIZED
            ),
            "pooled_out_of_fit_calibration_change_authorized": (
                POOLED_OUT_OF_FIT_CALIBRATION_CHANGE_AUTHORIZED
            ),
            "fit_temporal_utility_support_change_authorized": (
                FIT_TEMPORAL_UTILITY_SUPPORT_CHANGE_AUTHORIZED
            ),
            "fit_temporal_feature_support_change_authorized": (
                FIT_TEMPORAL_FEATURE_SUPPORT_CHANGE_AUTHORIZED
            ),
            "fit_temporal_residual_bound_change_authorized": (
                FIT_TEMPORAL_RESIDUAL_BOUND_CHANGE_AUTHORIZED
            ),
            "fit_temporal_residual_breadth_change_authorized": (
                FIT_TEMPORAL_RESIDUAL_BREADTH_CHANGE_AUTHORIZED
            ),
            "fit_temporal_residual_lower_tail_change_authorized": (
                FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_CHANGE_AUTHORIZED
            ),
            "selection_window_calibration_authorized": (
                SELECTION_WINDOW_CALIBRATION_AUTHORIZED
            ),
            "selection_window_quota_authorized": (
                SELECTION_WINDOW_QUOTA_AUTHORIZED
            ),
            "validation_calibration_authorized": (
                VALIDATION_CALIBRATION_AUTHORIZED
            ),
            "holdout_calibration_authorized": (
                HOLDOUT_CALIBRATION_AUTHORIZED
            ),
            "realized_selection_outcome_ranking_authorized": (
                REALIZED_SELECTION_OUTCOME_RANKING_AUTHORIZED
            ),
            "density_anchor_change_authorized": (
                DENSITY_ANCHOR_CHANGE_AUTHORIZED
            ),
            "minimum_directional_candidate_count_change_authorized": (
                MIN_DIRECTIONAL_CANDIDATE_COUNT_CHANGE_AUTHORIZED
            ),
            "stability_screen_change_authorized": (
                STABILITY_SCREEN_CHANGE_AUTHORIZED
            ),
            "per_window_financial_gate_change_authorized": (
                PER_WINDOW_FINANCIAL_GATE_CHANGE_AUTHORIZED
            ),
            "per_window_cutoff_tuning_authorized": (
                PER_WINDOW_CUTOFF_TUNING_AUTHORIZED
            ),
            "logistic_reintroduction_authorized": (
                LOGISTIC_REINTRODUCTION_AUTHORIZED
            ),
            "classifier_fallback_authorized": (
                CLASSIFIER_FALLBACK_AUTHORIZED
            ),
            "promotion_authorized": PROMOTION_AUTHORIZED,
            "shadow_authorized": SHADOW_AUTHORIZED,
            "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
            "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
            "live_order_authorized": LIVE_ORDER_AUTHORIZED,
            "real_money_authorized": REAL_MONEY_AUTHORIZED,
            "trading_authorized": TRADING_AUTHORIZED,
        },
    }


def fit_temporal_residual_lower_tail_utility_repair_protocol_fingerprint(
) -> str:
    return hashlib.sha256(
        _canonical_json(
            fit_temporal_residual_lower_tail_utility_repair_protocol_payload()
        )
    ).hexdigest()


__all__ = [
    "DEC218_RESULT_DECISION_BLOB_SHA",
    "DEC219_DIAGNOSTIC_BLOB_SHA",
    "DEC219_MERGED_COMMIT",
    "EXP056_PROTOCOL_BLOB_SHA",
    "EXP056_TRAINING_CORE_BLOB_SHA",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_EXPERIMENT_ID",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_PROTOCOL_DECISION",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_PROTOCOL_VERSION",
    "HISTORICAL_RESULT_EXECUTION_AUTHORIZED",
    "IMPLEMENTATION_DEPENDENCY_REPAIR_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "PROTOCOL_SEMANTICS_CHANGE_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "fit_temporal_residual_lower_tail_utility_repair_protocol_fingerprint",
    "fit_temporal_residual_lower_tail_utility_repair_protocol_payload",
    "validate_fit_temporal_residual_lower_tail_utility_repair_predecessor_identity",
]
