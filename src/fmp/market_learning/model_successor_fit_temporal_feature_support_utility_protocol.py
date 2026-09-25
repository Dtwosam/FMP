from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from .model_successor_fit_temporal_support_utility_post_result_diagnostics import (
    ACCEPTED_MODEL_CANDIDATE_COUNT,
    ADD_SELECTION_WINDOW_QUOTAS_AUTHORIZED,
    EXP052_EVIDENCE_FINGERPRINT,
    EXP052_REPLACEMENT_RUN_AUTHORIZED,
    EXP052_RERUN_AUTHORIZED,
    POST_RESULT_DIAGNOSTIC_DECISION,
    RECALIBRATE_ON_SELECTION_WINDOWS_AUTHORIZED,
    RELAX_STABILITY_FINANCIAL_AUTHORIZED,
    RELAX_STABILITY_SHARE_AUTHORIZED,
    REMOVE_EARLY_STABILITY_WINDOWS_AUTHORIZED,
    SUCCESSOR_MODEL_FIT_AUTHORIZED,
    SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED,
    SUCCESSOR_RESULT_EXECUTION_AUTHORIZED,
    USE_SELECTION_OUTCOMES_IN_RANKING_AUTHORIZED,
    build_fit_temporal_support_post_result_diagnostic_gate,
)
from .model_successor_fit_temporal_support_utility_protocol import (
    FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL,
    FIT_TEMPORAL_SUPPORT_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_VERSION,
    FIT_TEMPORAL_SUPPORT_WINDOWS,
    fit_temporal_support_utility_protocol_fingerprint,
    fit_temporal_support_utility_protocol_payload,
)
from .model_successor_temporal_calibrated_utility_protocol import (
    REQUIRED_JACKKNIFE_VIEW_COUNT,
)


FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_EXPERIMENT_ID = "EXP-20260925-053"
FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_VERSION = (
    "fmp-exp053-fit-temporal-feature-support-utility-protocol-v1"
)
FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_DECISION = "DEC-174"

DEC173_MERGED_COMMIT = "da3eb522f4178b635a261fe9ec6022d3cf94cbc8"
DEC173_DIAGNOSTIC_BLOB_SHA = (
    "af57f0eb6c00e18bb587203dc81530702e657e87"
)
DEC172_RESULT_DECISION_BLOB_SHA = (
    "c9983c33792a8b143989b928a9c2af0c4ecda1e5"
)
PREDECESSOR_PROTOCOL_BLOB_SHA = (
    "01d5080560ec5d41653694b4df086ff2f10e770d"
)
PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT = (
    "34e397e027a069db9344d56546b654f00"
    "bd34aff73240e5bca1d55e7b3dab7eb"
)
PREDECESSOR_DIAGNOSTIC_CLASSIFICATION = (
    "FIT_TEMPORAL_SUPPORT_DID_NOT_TRANSFER_TO_SELECTION_TIME_"
    "AND_TOP250_FINANCIAL_QUALITY_SLIGHTLY_DECLINED"
)

PRIOR_RESULT_INFORMED = True
UNTOUCHED_OOS = False

FEATURE_SUPPORT_WINDOWS_PER_VIEW = 4
FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL = (
    REQUIRED_JACKKNIFE_VIEW_COUNT * FEATURE_SUPPORT_WINDOWS_PER_VIEW
)

FIT_TEMPORAL_FEATURE_REFERENCE_RULE = (
    "for each frozen jackknife view and each of its four excluded-regime "
    "fit half-years, transform that half-year's model-input feature rows "
    "through the already-fitted view preprocessor; compute a finite per-"
    "dimension mean and population standard deviation, discard only zero-"
    "variance dimensions from distance calculation, compute each reference "
    "row's mean squared standardized distance from that half-year center, "
    "sort all finite reference distances ascending, and freeze one feature-"
    "support reference per view and half-year; no realized outcome and no "
    "selection, validation, or holdout row enters any reference"
)

FIT_TEMPORAL_FEATURE_DISTANCE_RULE = (
    "for a scored row, transform its model-input features through each "
    "frozen jackknife view preprocessor; for each of that view's four "
    "excluded-regime half-year references compute the mean squared "
    "standardized distance using only dimensions with positive frozen "
    "half-year scale"
)

FIT_TEMPORAL_FEATURE_SUPPORT_PERCENTILE_RULE = (
    "for each view-by-half-year distance, feature support is "
    "count(reference_distance >= scored_row_distance) divided by the "
    "half-year reference count, with ties included; smaller distance "
    "therefore maps to higher support"
)

ROBUST_FIT_TEMPORAL_FEATURE_SUPPORT_SCORE_RULE = (
    "for an EXP-052-eligible row, robust fit-temporal feature support is "
    "the minimum feature-support percentile across all twelve view-by-half-"
    "year references; EXP-052 robust fit-temporal utility support, pooled "
    "calibrated utility, and robust raw utility remain unchanged as "
    "secondary, tertiary, and quaternary ranking scores"
)

FIT_TEMPORAL_FEATURE_SUPPORT_EMPTY_REFERENCE_POLICY = "FAIL_CLOSED"
FIT_TEMPORAL_FEATURE_SUPPORT_ZERO_ACTIVE_DIMENSION_POLICY = "FAIL_CLOSED"
FIT_TEMPORAL_FEATURE_SUPPORT_NONFINITE_VALUE_POLICY = "FAIL_CLOSED"

RANKING_RULE = (
    "sort eligible selection rows by robust fit-temporal feature support "
    "descending, EXP-052 robust fit-temporal utility support descending, "
    "robust pooled calibrated utility descending, robust raw utility "
    "descending, and row identity ascending"
)

SELECTION_CUTOFF_RULE = (
    "for each unchanged candidate budget, freeze the budget-th selection "
    "row's (robust_fit_temporal_feature_support, robust_fit_temporal_support, "
    "robust_pooled_calibrated_utility, robust_raw_utility) quadruple after "
    "applying the frozen ranking order"
)

CUTOFF_TIE_POLICY = (
    "a scored row passes the frozen quadruple lexicographically: feature "
    "support above cutoff passes; when equal, fit-temporal utility support "
    "above cutoff passes; when both equal, pooled calibrated utility above "
    "cutoff passes; when all three equal, robust raw utility greater than "
    "or equal to the raw cutoff passes; exact quadruple ties may exceed "
    "the nominal budget"
)

FORWARD_APPLICATION_RULE = (
    "validation and retrospective holdout reuse the exact six frozen "
    "jackknife regressors, six pooled excluded-regime utility references, "
    "twenty-four fit-half-year utility-support references, twelve frozen "
    "fit-half-year feature-support references, unchanged unanimous positive-"
    "utility direction eligibility, and the exact selection-derived feature/"
    "utility-support/pooled/raw cutoff quadruple; do not refit, rebuild any "
    "reference, recompute a budget, tune by window, or use selection, "
    "validation, or holdout outcomes to change ranking"
)

FEATURE_CHANGE_AUTHORIZED = False
FINANCIAL_TARGET_CHANGE_AUTHORIZED = False
OUTER_CHRONOLOGY_CHANGE_AUTHORIZED = False
HGB_STRUCTURAL_CONFIG_CHANGE_AUTHORIZED = False
JACKKNIFE_VIEW_CHANGE_AUTHORIZED = False
UNANIMOUS_UTILITY_CONSENSUS_CHANGE_AUTHORIZED = False
POSITIVE_UTILITY_REQUIREMENT_CHANGE_AUTHORIZED = False
POOLED_OUT_OF_FIT_CALIBRATION_CHANGE_AUTHORIZED = False
FIT_TEMPORAL_UTILITY_SUPPORT_CHANGE_AUTHORIZED = False
FIT_TEMPORAL_FEATURE_SUPPORT_AUTHORIZED = True
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


def validate_fit_temporal_feature_support_predecessor_identity() -> None:
    diagnostic = build_fit_temporal_support_post_result_diagnostic_gate()

    if POST_RESULT_DIAGNOSTIC_DECISION != "DEC-173":
        raise ValueError("EXP-053 predecessor diagnostic decision drift")
    if diagnostic.get("diagnostic_classification") != (
        PREDECESSOR_DIAGNOSTIC_CLASSIFICATION
    ):
        raise ValueError("EXP-053 predecessor diagnostic classification drift")
    if diagnostic.get("successor_protocol_source_open_authorized") is not True:
        raise ValueError("EXP-053 successor protocol source is not open")
    if diagnostic.get("successor_result_execution_authorized") is not False:
        raise ValueError("EXP-053 predecessor successor execution must be closed")
    if diagnostic.get("successor_model_fit_authorized") is not False:
        raise ValueError("EXP-053 predecessor successor fit must be closed")
    if ACCEPTED_MODEL_CANDIDATE_COUNT != 0:
        raise ValueError("EXP-053 requires zero accepted predecessor candidates")
    if EXP052_EVIDENCE_FINGERPRINT != PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT:
        raise ValueError("EXP-053 predecessor evidence fingerprint drift")

    for name, value in (
        ("EXP-052 rerun", EXP052_RERUN_AUTHORIZED),
        ("EXP-052 replacement run", EXP052_REPLACEMENT_RUN_AUTHORIZED),
        ("relax stability share", RELAX_STABILITY_SHARE_AUTHORIZED),
        ("relax stability financial", RELAX_STABILITY_FINANCIAL_AUTHORIZED),
        ("remove early stability windows", REMOVE_EARLY_STABILITY_WINDOWS_AUTHORIZED),
        ("selection-window recalibration", RECALIBRATE_ON_SELECTION_WINDOWS_AUTHORIZED),
        ("selection-outcome ranking", USE_SELECTION_OUTCOMES_IN_RANKING_AUTHORIZED),
        ("selection-window quotas", ADD_SELECTION_WINDOW_QUOTAS_AUTHORIZED),
    ):
        if value is not False:
            raise ValueError(
                f"EXP-053 predecessor unexpectedly authorizes {name}"
            )

    if FIT_TEMPORAL_SUPPORT_UTILITY_EXPERIMENT_ID != "EXP-20260925-052":
        raise ValueError("EXP-053 predecessor experiment identity drift")
    if FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_DECISION != "DEC-163":
        raise ValueError("EXP-053 predecessor protocol decision drift")
    if FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_VERSION != (
        "fmp-exp052-fit-temporal-support-utility-protocol-v1"
    ):
        raise ValueError("EXP-053 predecessor protocol version drift")
    if FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL != 24:
        raise ValueError("EXP-053 predecessor utility-support count drift")
    if len(FIT_TEMPORAL_SUPPORT_WINDOWS) != 12:
        raise ValueError("EXP-053 predecessor support-window inventory drift")

    predecessor = fit_temporal_support_utility_protocol_payload()
    if predecessor["experiment_id"] != FIT_TEMPORAL_SUPPORT_UTILITY_EXPERIMENT_ID:
        raise ValueError("EXP-053 predecessor payload experiment drift")
    if predecessor["protocol_decision"] != FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_DECISION:
        raise ValueError("EXP-053 predecessor payload decision drift")

    selection = predecessor.get("selection")
    if not isinstance(selection, dict):
        raise ValueError("EXP-053 predecessor selection payload missing")
    if selection.get("candidate_budget_anchors") != [250, 500, 1000]:
        raise ValueError("EXP-053 predecessor budget identity drift")
    stability = selection.get("temporal_stability")
    if not isinstance(stability, dict):
        raise ValueError("EXP-053 predecessor stability payload missing")
    if len(stability.get("windows", [])) != 4:
        raise ValueError("EXP-053 predecessor stability-window count drift")
    if (
        stability.get("minimum_directional_candidate_share_per_window")
        != 0.10
    ):
        raise ValueError("EXP-053 predecessor stability-share drift")


def fit_temporal_feature_support_utility_protocol_payload(
) -> dict[str, object]:
    validate_fit_temporal_feature_support_predecessor_identity()
    predecessor = fit_temporal_support_utility_protocol_payload()

    chronology = deepcopy(predecessor["chronology"])
    model_family = deepcopy(predecessor["model_family"])
    temporal_jackknife = deepcopy(predecessor["temporal_jackknife"])
    utility_consensus = deepcopy(predecessor["utility_consensus"])
    pooled_calibration = deepcopy(predecessor["out_of_fit_utility_calibration"])
    utility_support = deepcopy(predecessor["fit_temporal_support_calibration"])
    selection = deepcopy(predecessor["selection"])
    validation = deepcopy(predecessor["validation"])
    holdout = deepcopy(predecessor["retrospective_holdout"])

    utility_consensus["ranking_score_rule"] = RANKING_RULE
    utility_consensus["fit_temporal_utility_support_retained"] = True
    utility_consensus["fit_temporal_feature_support_added"] = True

    selection.update(
        {
            "selection_cutoff_rule": SELECTION_CUTOFF_RULE,
            "cutoff_tie_policy": CUTOFF_TIE_POLICY,
            "forward_application_rule": FORWARD_APPLICATION_RULE,
            "ranking_order": [
                "robust_fit_temporal_feature_support_desc",
                "robust_fit_temporal_support_desc",
                "robust_pooled_calibrated_utility_desc",
                "robust_raw_utility_desc",
                "row_identity_asc",
            ],
            "cutoff_components": [
                "robust_fit_temporal_feature_support",
                "robust_fit_temporal_support",
                "robust_pooled_calibrated_utility",
                "robust_raw_utility",
            ],
        }
    )

    validation.update(
        {
            "fit_temporal_feature_support_reference_source": (
                "frozen_excluded_fit_regime_half_year_features"
            ),
            "rebuild_fit_temporal_feature_support_on_validation": False,
            "selection_derived_feature_support_cutoff_reused": True,
        }
    )
    holdout.update(
        {
            "fit_temporal_feature_support_reference_source": (
                "frozen_excluded_fit_regime_half_year_features"
            ),
            "rebuild_fit_temporal_feature_support_on_holdout": False,
            "selection_derived_feature_support_cutoff_reused": True,
        }
    )

    return {
        "protocol_version": FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_VERSION,
        "protocol_decision": FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_DECISION,
        "experiment_id": FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_EXPERIMENT_ID,
        "predecessor_experiment_id": FIT_TEMPORAL_SUPPORT_UTILITY_EXPERIMENT_ID,
        "predecessor_protocol_decision": FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_DECISION,
        "predecessor_protocol_fingerprint": (
            fit_temporal_support_utility_protocol_fingerprint()
        ),
        "predecessor_result_evidence_fingerprint": (
            PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT
        ),
        "predecessor_post_result_diagnostic_decision": (
            POST_RESULT_DIAGNOSTIC_DECISION
        ),
        "predecessor_diagnostic_classification": (
            PREDECESSOR_DIAGNOSTIC_CLASSIFICATION
        ),
        "prior_result_informed": PRIOR_RESULT_INFORMED,
        "untouched_oos": UNTOUCHED_OOS,
        "chronology": chronology,
        "model_family": model_family,
        "temporal_jackknife": temporal_jackknife,
        "utility_consensus": utility_consensus,
        "out_of_fit_utility_calibration": pooled_calibration,
        "fit_temporal_support_calibration": utility_support,
        "fit_temporal_feature_support": {
            "authorized_protocol_change": FIT_TEMPORAL_FEATURE_SUPPORT_AUTHORIZED,
            "reference_windows": [
                dict(window) for window in FIT_TEMPORAL_SUPPORT_WINDOWS
            ],
            "reference_windows_per_view": FEATURE_SUPPORT_WINDOWS_PER_VIEW,
            "reference_count_per_cell": (
                FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL
            ),
            "reference_rule": FIT_TEMPORAL_FEATURE_REFERENCE_RULE,
            "distance_rule": FIT_TEMPORAL_FEATURE_DISTANCE_RULE,
            "support_percentile_rule": (
                FIT_TEMPORAL_FEATURE_SUPPORT_PERCENTILE_RULE
            ),
            "robust_support_score_rule": (
                ROBUST_FIT_TEMPORAL_FEATURE_SUPPORT_SCORE_RULE
            ),
            "aggregation": "minimum",
            "view_preprocessor_reused": True,
            "uses_realized_outcomes": False,
            "selection_rows_enter_references": False,
            "validation_rows_enter_references": False,
            "holdout_rows_enter_references": False,
            "selection_window_identity_enters_ranking": False,
            "empty_reference_policy": (
                FIT_TEMPORAL_FEATURE_SUPPORT_EMPTY_REFERENCE_POLICY
            ),
            "zero_active_dimension_policy": (
                FIT_TEMPORAL_FEATURE_SUPPORT_ZERO_ACTIVE_DIMENSION_POLICY
            ),
            "nonfinite_value_policy": (
                FIT_TEMPORAL_FEATURE_SUPPORT_NONFINITE_VALUE_POLICY
            ),
        },
        "selection": selection,
        "validation": validation,
        "retrospective_holdout": holdout,
        "authorization": {
            "model_protocol_result_authorized": MODEL_PROTOCOL_RESULT_AUTHORIZED,
            "model_fit_authorized": MODEL_FIT_AUTHORIZED,
            "historical_result_execution_authorized": (
                HISTORICAL_RESULT_EXECUTION_AUTHORIZED
            ),
            "feature_change_authorized": FEATURE_CHANGE_AUTHORIZED,
            "financial_target_change_authorized": FINANCIAL_TARGET_CHANGE_AUTHORIZED,
            "outer_chronology_change_authorized": OUTER_CHRONOLOGY_CHANGE_AUTHORIZED,
            "hgb_structural_config_change_authorized": (
                HGB_STRUCTURAL_CONFIG_CHANGE_AUTHORIZED
            ),
            "jackknife_view_change_authorized": JACKKNIFE_VIEW_CHANGE_AUTHORIZED,
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
            "fit_temporal_feature_support_authorized": (
                FIT_TEMPORAL_FEATURE_SUPPORT_AUTHORIZED
            ),
            "selection_window_calibration_authorized": (
                SELECTION_WINDOW_CALIBRATION_AUTHORIZED
            ),
            "selection_window_quota_authorized": (
                SELECTION_WINDOW_QUOTA_AUTHORIZED
            ),
            "validation_calibration_authorized": VALIDATION_CALIBRATION_AUTHORIZED,
            "holdout_calibration_authorized": HOLDOUT_CALIBRATION_AUTHORIZED,
            "realized_selection_outcome_ranking_authorized": (
                REALIZED_SELECTION_OUTCOME_RANKING_AUTHORIZED
            ),
            "density_anchor_change_authorized": DENSITY_ANCHOR_CHANGE_AUTHORIZED,
            "minimum_directional_candidate_count_change_authorized": (
                MIN_DIRECTIONAL_CANDIDATE_COUNT_CHANGE_AUTHORIZED
            ),
            "stability_screen_change_authorized": STABILITY_SCREEN_CHANGE_AUTHORIZED,
            "per_window_financial_gate_change_authorized": (
                PER_WINDOW_FINANCIAL_GATE_CHANGE_AUTHORIZED
            ),
            "per_window_cutoff_tuning_authorized": (
                PER_WINDOW_CUTOFF_TUNING_AUTHORIZED
            ),
            "logistic_reintroduction_authorized": LOGISTIC_REINTRODUCTION_AUTHORIZED,
            "classifier_fallback_authorized": CLASSIFIER_FALLBACK_AUTHORIZED,
            "promotion_authorized": PROMOTION_AUTHORIZED,
            "shadow_authorized": SHADOW_AUTHORIZED,
            "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
            "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
            "live_order_authorized": LIVE_ORDER_AUTHORIZED,
            "real_money_authorized": REAL_MONEY_AUTHORIZED,
            "trading_authorized": TRADING_AUTHORIZED,
        },
    }


def fit_temporal_feature_support_utility_protocol_fingerprint() -> str:
    return hashlib.sha256(
        _canonical_json(
            fit_temporal_feature_support_utility_protocol_payload()
        )
    ).hexdigest()


__all__ = [
    "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_EXPERIMENT_ID",
    "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_VERSION",
    "FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_DECISION",
    "FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL",
    "FIT_TEMPORAL_FEATURE_SUPPORT_AUTHORIZED",
    "FIT_TEMPORAL_FEATURE_REFERENCE_RULE",
    "FIT_TEMPORAL_FEATURE_DISTANCE_RULE",
    "FIT_TEMPORAL_FEATURE_SUPPORT_PERCENTILE_RULE",
    "ROBUST_FIT_TEMPORAL_FEATURE_SUPPORT_SCORE_RULE",
    "RANKING_RULE",
    "SELECTION_CUTOFF_RULE",
    "CUTOFF_TIE_POLICY",
    "FORWARD_APPLICATION_RULE",
    "PRIOR_RESULT_INFORMED",
    "UNTOUCHED_OOS",
    "MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "HISTORICAL_RESULT_EXECUTION_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "fit_temporal_feature_support_utility_protocol_fingerprint",
    "fit_temporal_feature_support_utility_protocol_payload",
    "validate_fit_temporal_feature_support_predecessor_identity",
]
