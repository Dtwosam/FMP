from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from .model_successor_fit_temporal_residual_regime_floor_utility_post_result_diagnostics import (
    POST_RESULT_DIAGNOSTIC_DECISION,
    build_fit_temporal_residual_regime_floor_post_result_diagnostic_gate,
)
from .model_successor_fit_temporal_residual_regime_floor_utility_protocol import (
    FIT_TEMPORAL_RESIDUAL_REGIME_COUNT,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_BOUND_COUNT_PER_ROW,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_PROTOCOL_VERSION,
    FIT_TEMPORAL_RESIDUAL_WINDOWS_PER_REGIME,
    fit_temporal_residual_regime_floor_utility_protocol_fingerprint,
    fit_temporal_residual_regime_floor_utility_protocol_payload,
)


FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_EXPERIMENT_ID = (
    "EXP-20260926-059"
)
FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_PROTOCOL_VERSION = (
    "fmp-exp059-fit-temporal-residual-regime-balance-utility-protocol-v1"
)
FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_PROTOCOL_DECISION = "DEC-242"

DEC241_MERGED_COMMIT = "761696ac8619841efde494ff4c827c4c91e8895c"
DEC241_DIAGNOSTIC_BLOB_SHA = (
    "c0717252dabd625bd6a65b78f9acb5217ed44c84"
)
DEC240_RESULT_DECISION_BLOB_SHA = (
    "f5a5f7e49b7088f4af9b35a9143e486c3fba3d1a"
)
PREDECESSOR_PROTOCOL_BLOB_SHA = (
    "8e10cc3760a4a7dd019ea1ecc7c60189fe1770e2"
)
PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT = (
    "7e5019f0e00ada90a8f9c111d2b6fdb"
    "4ba41908f86a47203258b333439c8c8ee"
)
PREDECESSOR_DIAGNOSTIC_CLASSIFICATION = (
    "REGIME_FLOOR_RANKING_CHANGED_CANDIDATE_MIX_AND_FINANCIALS_"
    "BUT_DID_NOT_CREATE_TEMPORAL_STABILITY"
)

PRIOR_RESULT_INFORMED = True
UNTOUCHED_OOS = False

FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_AUTHORIZED = True
FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_REGIME_COUNT = (
    FIT_TEMPORAL_RESIDUAL_REGIME_COUNT
)
FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_SOURCE_BOUND_COUNT_PER_ROW = (
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_BOUND_COUNT_PER_ROW
)
FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_PENALTY_MULTIPLIER = 1.0

FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_RULE = (
    "for each EXP-058-eligible row and its unchanged unanimous LONG or SHORT "
    "direction, reuse the exact three finite fit-regime means already derived "
    "by EXP-058 from the same twelve frozen downside-adjusted residual lower "
    "bounds; compute the arithmetic mean of the three regime means, compute "
    "their spread as maximum minus minimum, and define fit-temporal residual "
    "regime-balance utility as arithmetic_mean(regime_means) minus exactly "
    "1.0 times regime_spread; do not rebuild residual references, change the "
    "three frozen fit regimes, use selection/validation/holdout outcomes, tune "
    "the penalty multiplier, normalize by selection-window behavior, or add "
    "any new reference vector"
)
RESIDUAL_REGIME_BALANCE_ELIGIBILITY_RULE = (
    "EXP-059 does not change EXP-058 row eligibility; regime-balance utility "
    "is a fit-only ranking score computed after unchanged unanimous positive-"
    "utility LONG/SHORT eligibility and uses only the three frozen fit-regime "
    "means derived from frozen jackknife predictions and residual references"
)

RANKING_RULE = (
    "sort eligible selection rows by fit-temporal residual regime-balance "
    "utility descending, EXP-058 fit-temporal residual regime-floor utility "
    "descending, fit-temporal residual lower-tail mean descending, residual "
    "breadth descending, robust residual-bound utility descending, robust "
    "fit-temporal feature support descending, robust fit-temporal utility "
    "support descending, robust pooled calibrated utility descending, robust "
    "raw utility descending, and row identity ascending"
)
SELECTION_CUTOFF_RULE = (
    "for each unchanged candidate budget, freeze the budget-th selection row's "
    "(fit_temporal_residual_regime_balance_utility, "
    "fit_temporal_residual_regime_floor_utility, "
    "fit_temporal_residual_lower_tail_mean, fit_temporal_residual_breadth, "
    "robust_fit_temporal_residual_bound_utility, "
    "robust_fit_temporal_feature_support, robust_fit_temporal_support, "
    "robust_pooled_calibrated_utility, robust_raw_utility) nine-part tuple "
    "after applying the frozen ranking order"
)
CUTOFF_TIE_POLICY = (
    "a scored row passes the frozen nine-part cutoff lexicographically in the "
    "same descending component order, with the final robust raw utility "
    "comparison inclusive; exact nine-part ties may exceed the nominal budget"
)
FORWARD_APPLICATION_RULE = (
    "validation and retrospective holdout reuse the exact six frozen jackknife "
    "regressors, six pooled excluded-regime references, twenty-four utility-"
    "support references, twelve feature-support references, twenty-four "
    "residual references, unchanged twelve residual bounds per eligible row, "
    "the same three fit-regime means, regime-floor utility, derived regime-"
    "balance utility, and the exact selection-derived nine-part cutoff; do not "
    "refit, rebuild a reference, recompute a budget, recalibrate, tune by "
    "selection window, or use selection/validation/holdout outcomes to change "
    "ranking"
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
FIT_TEMPORAL_FEATURE_SUPPORT_CHANGE_AUTHORIZED = False
FIT_TEMPORAL_RESIDUAL_BOUND_CHANGE_AUTHORIZED = False
FIT_TEMPORAL_RESIDUAL_BREADTH_CHANGE_AUTHORIZED = False
FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_CHANGE_AUTHORIZED = False
FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_CHANGE_AUTHORIZED = False
FIT_TEMPORAL_RESIDUAL_REFERENCE_CHANGE_AUTHORIZED = False
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


def validate_fit_temporal_residual_regime_balance_predecessor_identity(
) -> None:
    diagnostic = build_fit_temporal_residual_regime_floor_post_result_diagnostic_gate()
    if POST_RESULT_DIAGNOSTIC_DECISION != "DEC-241":
        raise ValueError("EXP-059 predecessor diagnostic decision drift")
    if diagnostic.get("diagnostic_classification") != (
        PREDECESSOR_DIAGNOSTIC_CLASSIFICATION
    ):
        raise ValueError(
            "EXP-059 predecessor diagnostic classification drift"
        )
    if diagnostic.get("accepted_model_candidate_count") != 0:
        raise ValueError("EXP-059 requires zero accepted predecessor candidates")
    if diagnostic.get("successor_protocol_source_open_authorized") is not True:
        raise ValueError("EXP-059 successor protocol source is not open")
    if diagnostic.get("successor_result_execution_authorized") is not False:
        raise ValueError("EXP-059 predecessor successor execution must be closed")
    if diagnostic.get("successor_model_fit_authorized") is not False:
        raise ValueError("EXP-059 predecessor successor fit must be closed")

    for field in (
        "exp058_rerun_authorized",
        "exp058_replacement_run_authorized",
        "relax_stability_share_authorized",
        "relax_stability_financial_authorized",
        "remove_early_stability_windows_authorized",
        "use_selection_outcomes_in_ranking_authorized",
        "recalibrate_on_selection_windows_authorized",
        "add_selection_window_quotas_authorized",
        "retune_regime_floor_on_selection_authorized",
        "promotion_authorized",
        "shadow_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "trading_authorized",
    ):
        if diagnostic.get(field) is not False:
            raise ValueError(
                f"EXP-059 predecessor unexpectedly authorizes {field}"
            )

    if FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_EXPERIMENT_ID != (
        "EXP-20260925-058"
    ):
        raise ValueError("EXP-059 predecessor experiment drift")
    if FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_PROTOCOL_DECISION != (
        "DEC-231"
    ):
        raise ValueError("EXP-059 predecessor protocol decision drift")
    if FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_PROTOCOL_VERSION != (
        "fmp-exp058-fit-temporal-residual-regime-floor-utility-protocol-v1"
    ):
        raise ValueError("EXP-059 predecessor protocol version drift")

    predecessor = fit_temporal_residual_regime_floor_utility_protocol_payload()
    selection = predecessor.get("selection")
    if not isinstance(selection, dict):
        raise ValueError("EXP-059 predecessor selection payload missing")
    if selection.get("candidate_budget_anchors") != [250, 500, 1000]:
        raise ValueError("EXP-059 predecessor budget identity drift")
    if selection.get("ranking_order") != [
        "fit_temporal_residual_regime_floor_utility_desc",
        "fit_temporal_residual_lower_tail_mean_desc",
        "fit_temporal_residual_breadth_desc",
        "robust_fit_temporal_residual_bound_utility_desc",
        "robust_fit_temporal_feature_support_desc",
        "robust_fit_temporal_support_desc",
        "robust_pooled_calibrated_utility_desc",
        "robust_raw_utility_desc",
        "row_identity_asc",
    ]:
        raise ValueError("EXP-059 predecessor ranking identity drift")
    stability = selection.get("temporal_stability")
    if not isinstance(stability, dict):
        raise ValueError("EXP-059 predecessor stability payload missing")
    if len(stability.get("windows", [])) != 4:
        raise ValueError("EXP-059 stability-window count drift")
    if (
        stability.get("minimum_directional_candidate_share_per_window")
        != 0.10
    ):
        raise ValueError("EXP-059 stability-share drift")


def fit_temporal_residual_regime_balance_utility_protocol_payload(
) -> dict[str, object]:
    validate_fit_temporal_residual_regime_balance_predecessor_identity()
    predecessor = fit_temporal_residual_regime_floor_utility_protocol_payload()

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
    residual_bound = deepcopy(predecessor["fit_temporal_residual_bound"])
    residual_breadth = deepcopy(predecessor["fit_temporal_residual_breadth"])
    residual_lower_tail = deepcopy(
        predecessor["fit_temporal_residual_lower_tail"]
    )
    residual_regime_floor = deepcopy(
        predecessor["fit_temporal_residual_regime_floor"]
    )
    selection = deepcopy(predecessor["selection"])
    validation = deepcopy(predecessor["validation"])
    holdout = deepcopy(predecessor["retrospective_holdout"])

    utility_consensus["fit_temporal_residual_regime_balance_added"] = True
    utility_consensus["fit_temporal_residual_regime_floor_retained"] = True
    utility_consensus["ranking_score_rule"] = RANKING_RULE

    selection.update(
        {
            "selection_cutoff_rule": SELECTION_CUTOFF_RULE,
            "cutoff_tie_policy": CUTOFF_TIE_POLICY,
            "forward_application_rule": FORWARD_APPLICATION_RULE,
            "ranking_order": [
                "fit_temporal_residual_regime_balance_utility_desc",
                "fit_temporal_residual_regime_floor_utility_desc",
                "fit_temporal_residual_lower_tail_mean_desc",
                "fit_temporal_residual_breadth_desc",
                "robust_fit_temporal_residual_bound_utility_desc",
                "robust_fit_temporal_feature_support_desc",
                "robust_fit_temporal_support_desc",
                "robust_pooled_calibrated_utility_desc",
                "robust_raw_utility_desc",
                "row_identity_asc",
            ],
            "cutoff_components": [
                "fit_temporal_residual_regime_balance_utility",
                "fit_temporal_residual_regime_floor_utility",
                "fit_temporal_residual_lower_tail_mean",
                "fit_temporal_residual_breadth",
                "robust_fit_temporal_residual_bound_utility",
                "robust_fit_temporal_feature_support",
                "robust_fit_temporal_support",
                "robust_pooled_calibrated_utility",
                "robust_raw_utility",
            ],
        }
    )

    validation.update(
        {
            "fit_temporal_residual_regime_balance_source": (
                "frozen_three_fit_regime_means"
            ),
            "rebuild_fit_temporal_residual_regime_balance_on_validation": False,
            "selection_derived_residual_regime_balance_cutoff_reused": True,
        }
    )
    holdout.update(
        {
            "fit_temporal_residual_regime_balance_source": (
                "frozen_three_fit_regime_means"
            ),
            "rebuild_fit_temporal_residual_regime_balance_on_holdout": False,
            "selection_derived_residual_regime_balance_cutoff_reused": True,
        }
    )

    return {
        "protocol_version": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_PROTOCOL_VERSION
        ),
        "protocol_decision": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_PROTOCOL_DECISION
        ),
        "experiment_id": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_EXPERIMENT_ID
        ),
        "predecessor_experiment_id": (
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_EXPERIMENT_ID
        ),
        "predecessor_protocol_decision": (
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_PROTOCOL_DECISION
        ),
        "predecessor_protocol_fingerprint": (
            fit_temporal_residual_regime_floor_utility_protocol_fingerprint()
        ),
        "predecessor_result_decision": "DEC-240",
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
        "fit_temporal_feature_support": feature_support,
        "fit_temporal_residual_bound": residual_bound,
        "fit_temporal_residual_breadth": residual_breadth,
        "fit_temporal_residual_lower_tail": residual_lower_tail,
        "fit_temporal_residual_regime_floor": residual_regime_floor,
        "fit_temporal_residual_regime_balance": {
            "authorized_protocol_change": (
                FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_AUTHORIZED
            ),
            "source_regime_count": (
                FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_REGIME_COUNT
            ),
            "source_bound_count_per_row": (
                FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_SOURCE_BOUND_COUNT_PER_ROW
            ),
            "penalty_multiplier": (
                FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_PENALTY_MULTIPLIER
            ),
            "balance_rule": FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_RULE,
            "eligibility_rule": RESIDUAL_REGIME_BALANCE_ELIGIBILITY_RULE,
            "center_aggregation": "arithmetic_mean",
            "dispersion_measure": "max_minus_min",
            "score_formula": "mean_minus_1p0_times_range",
            "uses_existing_exp058_regime_means": True,
            "creates_new_reference_vectors": False,
            "uses_realized_fit_outcomes_via_frozen_residuals": True,
            "uses_realized_selection_outcomes": False,
            "uses_realized_validation_outcomes_for_ranking": False,
            "uses_realized_holdout_outcomes_for_ranking": False,
            "selection_window_identity_enters_ranking": False,
            "selection_window_quota_used": False,
            "stability_gate_changed": False,
        },
        "selection": selection,
        "validation": validation,
        "retrospective_holdout": holdout,
        "authorization": {
            "fit_temporal_residual_regime_balance_authorized": (
                FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_AUTHORIZED
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
            "fit_temporal_residual_regime_floor_change_authorized": (
                FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_CHANGE_AUTHORIZED
            ),
            "fit_temporal_residual_reference_change_authorized": (
                FIT_TEMPORAL_RESIDUAL_REFERENCE_CHANGE_AUTHORIZED
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


def fit_temporal_residual_regime_balance_utility_protocol_fingerprint(
) -> str:
    return hashlib.sha256(
        _canonical_json(
            fit_temporal_residual_regime_balance_utility_protocol_payload()
        )
    ).hexdigest()


__all__ = [
    "CUTOFF_TIE_POLICY",
    "DEC240_RESULT_DECISION_BLOB_SHA",
    "DEC241_DIAGNOSTIC_BLOB_SHA",
    "DEC241_MERGED_COMMIT",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_AUTHORIZED",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_PENALTY_MULTIPLIER",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_REGIME_COUNT",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_RULE",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_SOURCE_BOUND_COUNT_PER_ROW",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_EXPERIMENT_ID",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_PROTOCOL_DECISION",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_PROTOCOL_VERSION",
    "FORWARD_APPLICATION_RULE",
    "HISTORICAL_RESULT_EXECUTION_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "PREDECESSOR_PROTOCOL_BLOB_SHA",
    "RANKING_RULE",
    "RESIDUAL_REGIME_BALANCE_ELIGIBILITY_RULE",
    "SELECTION_CUTOFF_RULE",
    "TRADING_AUTHORIZED",
    "fit_temporal_residual_regime_balance_utility_protocol_fingerprint",
    "fit_temporal_residual_regime_balance_utility_protocol_payload",
    "validate_fit_temporal_residual_regime_balance_predecessor_identity",
]
