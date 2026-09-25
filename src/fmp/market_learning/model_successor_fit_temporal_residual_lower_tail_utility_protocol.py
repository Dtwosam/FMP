from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from .model_successor_fit_temporal_residual_breadth_utility_post_result_diagnostics import (
    POST_RESULT_DIAGNOSTIC_DECISION,
    build_fit_temporal_residual_breadth_post_result_diagnostic_gate,
)
from .model_successor_fit_temporal_residual_breadth_utility_protocol import (
    FIT_TEMPORAL_RESIDUAL_BREADTH_BOUND_COUNT_PER_ROW,
    FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_PROTOCOL_VERSION,
    fit_temporal_residual_breadth_utility_protocol_fingerprint,
    fit_temporal_residual_breadth_utility_protocol_payload,
)


FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_EXPERIMENT_ID = "EXP-20260925-056"
FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_PROTOCOL_VERSION = (
    "fmp-exp056-fit-temporal-residual-lower-tail-utility-protocol-v1"
)
FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_PROTOCOL_DECISION = "DEC-209"

DEC208_MERGED_COMMIT = "9efc720149fea77ab60e50ac0222f6ed1c458195"
DEC208_DIAGNOSTIC_BLOB_SHA = (
    "5ff61be317b225d9d7ec656b4789c4561d52b522"
)
DEC207_RESULT_DECISION_BLOB_SHA = (
    "e2226117ebf10b762557d43549390c46c243bbae"
)
PREDECESSOR_PROTOCOL_BLOB_SHA = (
    "0ef3f932cade1a62e1faf946e9a9b87cf9c98744"
)
PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT = (
    "f3a386dad7f23ac9d6867d030ac90e08"
    "84f3ab658c9ffecce8647048037d2510"
)
PREDECESSOR_DIAGNOSTIC_CLASSIFICATION = (
    "FIT_RESIDUAL_BREADTH_DID_NOT_TRANSFER_TO_SELECTION_"
    "TEMPORAL_BREADTH_AND_WEAKENED_PASS_VARIANT_FINANCIALS"
)

PRIOR_RESULT_INFORMED = True
UNTOUCHED_OOS = False

FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_BOUND_COUNT_PER_ROW = (
    FIT_TEMPORAL_RESIDUAL_BREADTH_BOUND_COUNT_PER_ROW
)
FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_COUNT = 3
FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_FRACTION = 0.25

FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_RULE = (
    "for each EXP-055-eligible row and its unchanged unanimous LONG or SHORT "
    "direction, reuse the exact twelve downside-adjusted lower-bound utilities "
    "already computed by EXP-055; sort those twelve finite lower bounds "
    "ascending and take the arithmetic mean of the three smallest values; "
    "three is the exact lower-quartile count because 0.25 times twelve equals "
    "three; do not interpolate, trim, winsorize, or use selection, validation, "
    "or holdout outcomes"
)

RESIDUAL_LOWER_TAIL_ELIGIBILITY_RULE = (
    "EXP-056 does not change EXP-055 row eligibility; residual lower-tail mean "
    "is a ranking score only after the unchanged unanimous positive-utility "
    "direction eligibility has already passed"
)

RANKING_RULE = (
    "sort eligible selection rows by fit-temporal residual lower-tail mean "
    "descending, fit-temporal residual breadth descending, robust fit-temporal "
    "residual-bound utility descending, robust fit-temporal feature support "
    "descending, robust fit-temporal utility support descending, robust pooled "
    "calibrated utility descending, robust raw utility descending, and row "
    "identity ascending"
)

SELECTION_CUTOFF_RULE = (
    "for each unchanged candidate budget, freeze the budget-th selection row's "
    "(fit_temporal_residual_lower_tail_mean, fit_temporal_residual_breadth, "
    "robust_fit_temporal_residual_bound_utility, "
    "robust_fit_temporal_feature_support, robust_fit_temporal_support, "
    "robust_pooled_calibrated_utility, robust_raw_utility) septuple after "
    "applying the frozen ranking order"
)

CUTOFF_TIE_POLICY = (
    "a scored row passes the frozen septuple lexicographically: residual "
    "lower-tail mean above cutoff passes; when equal, residual breadth above "
    "cutoff passes; when equal again, residual-bound utility above cutoff "
    "passes; then feature support, fit-temporal utility support, pooled "
    "calibrated utility, and finally robust raw utility greater than or equal "
    "to the raw cutoff; exact septuple ties may exceed the nominal budget"
)

FORWARD_APPLICATION_RULE = (
    "validation and retrospective holdout reuse the exact six frozen jackknife "
    "regressors, six pooled excluded-regime utility references, twenty-four "
    "fit-half-year utility-support references, twelve fit-half-year feature-"
    "support references, twenty-four target-specific out-of-fit residual "
    "references, the same twelve lower-bound utilities used for EXP-055 "
    "residual breadth, the same fixed worst-three arithmetic-mean lower-tail "
    "rule, unchanged unanimous positive-utility eligibility, and the exact "
    "selection-derived lower-tail/breadth/residual-bound/feature-support/"
    "utility-support/pooled/raw cutoff septuple; do not refit, rebuild "
    "references, recompute a budget, tune by window, or use selection, "
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
FIT_TEMPORAL_FEATURE_SUPPORT_CHANGE_AUTHORIZED = False
FIT_TEMPORAL_RESIDUAL_BOUND_CHANGE_AUTHORIZED = False
FIT_TEMPORAL_RESIDUAL_BREADTH_CHANGE_AUTHORIZED = False
FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_AUTHORIZED = True
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


def validate_fit_temporal_residual_lower_tail_predecessor_identity() -> None:
    diagnostic = build_fit_temporal_residual_breadth_post_result_diagnostic_gate()

    if POST_RESULT_DIAGNOSTIC_DECISION != "DEC-208":
        raise ValueError("EXP-056 predecessor diagnostic decision drift")
    if diagnostic.get("diagnostic_classification") != (
        PREDECESSOR_DIAGNOSTIC_CLASSIFICATION
    ):
        raise ValueError(
            "EXP-056 predecessor diagnostic classification drift"
        )
    if diagnostic.get("successor_protocol_source_open_authorized") is not True:
        raise ValueError("EXP-056 successor protocol source is not open")
    if diagnostic.get("successor_result_execution_authorized") is not False:
        raise ValueError(
            "EXP-056 predecessor successor execution must be closed"
        )
    if diagnostic.get("successor_model_fit_authorized") is not False:
        raise ValueError("EXP-056 predecessor successor fit must be closed")
    if diagnostic.get("accepted_model_candidate_count") != 0:
        raise ValueError(
            "EXP-056 requires zero accepted predecessor candidates"
        )

    experiments = diagnostic.get("experiments")
    if not isinstance(experiments, dict):
        raise ValueError("EXP-056 predecessor experiment evidence missing")
    exp055 = experiments.get("exp055")
    if not isinstance(exp055, dict):
        raise ValueError("EXP-056 predecessor EXP-055 evidence missing")
    if exp055.get("evidence_fingerprint") != (
        PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT
    ):
        raise ValueError("EXP-056 predecessor evidence fingerprint drift")
    if exp055.get("stable_pass_count") != 0:
        raise ValueError("EXP-056 predecessor stable-pass count drift")

    for name in (
        "exp055_rerun_authorized",
        "exp055_replacement_run_authorized",
        "relax_stability_share_authorized",
        "relax_stability_financial_authorized",
        "remove_early_stability_windows_authorized",
        "use_selection_outcomes_in_ranking_authorized",
        "recalibrate_on_selection_windows_authorized",
        "add_selection_window_quotas_authorized",
        "retune_residual_breadth_on_selection_authorized",
    ):
        if diagnostic.get(name) is not False:
            raise ValueError(
                f"EXP-056 predecessor unexpectedly authorizes {name}"
            )

    if FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_EXPERIMENT_ID != (
        "EXP-20260925-055"
    ):
        raise ValueError("EXP-056 predecessor experiment identity drift")
    if FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_PROTOCOL_DECISION != "DEC-198":
        raise ValueError("EXP-056 predecessor protocol decision drift")
    if FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_PROTOCOL_VERSION != (
        "fmp-exp055-fit-temporal-residual-breadth-utility-protocol-v1"
    ):
        raise ValueError("EXP-056 predecessor protocol version drift")
    if FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_BOUND_COUNT_PER_ROW != 12:
        raise ValueError("EXP-056 lower-bound inventory drift")
    if FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_COUNT != 3:
        raise ValueError("EXP-056 lower-tail count drift")
    if FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_FRACTION != 0.25:
        raise ValueError("EXP-056 lower-tail fraction drift")

    predecessor = fit_temporal_residual_breadth_utility_protocol_payload()
    if predecessor["experiment_id"] != (
        FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_EXPERIMENT_ID
    ):
        raise ValueError("EXP-056 predecessor payload experiment drift")

    breadth = predecessor.get("fit_temporal_residual_breadth")
    if not isinstance(breadth, dict):
        raise ValueError("EXP-056 predecessor breadth payload missing")
    if breadth.get("source_lower_bound_count_per_row") != 12:
        raise ValueError("EXP-056 predecessor lower-bound count drift")
    if breadth.get("uses_existing_exp054_residual_references") is not True:
        raise ValueError("EXP-056 predecessor residual-source drift")
    if breadth.get("selection_window_identity_enters_ranking") is not False:
        raise ValueError("EXP-056 predecessor ranking leakage drift")

    selection = predecessor.get("selection")
    if not isinstance(selection, dict):
        raise ValueError("EXP-056 predecessor selection payload missing")
    if selection.get("candidate_budget_anchors") != [250, 500, 1000]:
        raise ValueError("EXP-056 predecessor budget identity drift")
    if selection.get("ranking_order") != [
        "fit_temporal_residual_breadth_desc",
        "robust_fit_temporal_residual_bound_utility_desc",
        "robust_fit_temporal_feature_support_desc",
        "robust_fit_temporal_support_desc",
        "robust_pooled_calibrated_utility_desc",
        "robust_raw_utility_desc",
        "row_identity_asc",
    ]:
        raise ValueError("EXP-056 predecessor ranking identity drift")
    stability = selection.get("temporal_stability")
    if not isinstance(stability, dict):
        raise ValueError("EXP-056 predecessor stability payload missing")
    if len(stability.get("windows", [])) != 4:
        raise ValueError("EXP-056 predecessor stability-window count drift")
    if (
        stability.get("minimum_directional_candidate_share_per_window")
        != 0.10
    ):
        raise ValueError("EXP-056 predecessor stability-share drift")


def fit_temporal_residual_lower_tail_utility_protocol_payload(
) -> dict[str, object]:
    validate_fit_temporal_residual_lower_tail_predecessor_identity()
    predecessor = fit_temporal_residual_breadth_utility_protocol_payload()

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
    selection = deepcopy(predecessor["selection"])
    validation = deepcopy(predecessor["validation"])
    holdout = deepcopy(predecessor["retrospective_holdout"])

    utility_consensus["ranking_score_rule"] = RANKING_RULE
    utility_consensus["fit_temporal_residual_bound_retained"] = True
    utility_consensus["fit_temporal_residual_breadth_retained"] = True
    utility_consensus["fit_temporal_residual_lower_tail_added"] = True

    selection.update(
        {
            "selection_cutoff_rule": SELECTION_CUTOFF_RULE,
            "cutoff_tie_policy": CUTOFF_TIE_POLICY,
            "forward_application_rule": FORWARD_APPLICATION_RULE,
            "ranking_order": [
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
            "fit_temporal_residual_lower_tail_source": (
                "frozen_exp055_twelve_fit_half_year_lower_bounds"
            ),
            "rebuild_fit_temporal_residual_lower_tail_on_validation": False,
            "selection_derived_residual_lower_tail_cutoff_reused": True,
        }
    )
    holdout.update(
        {
            "fit_temporal_residual_lower_tail_source": (
                "frozen_exp055_twelve_fit_half_year_lower_bounds"
            ),
            "rebuild_fit_temporal_residual_lower_tail_on_holdout": False,
            "selection_derived_residual_lower_tail_cutoff_reused": True,
        }
    )

    return {
        "protocol_version": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_PROTOCOL_VERSION
        ),
        "protocol_decision": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_PROTOCOL_DECISION
        ),
        "experiment_id": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_EXPERIMENT_ID
        ),
        "predecessor_experiment_id": (
            FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_EXPERIMENT_ID
        ),
        "predecessor_protocol_decision": (
            FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_PROTOCOL_DECISION
        ),
        "predecessor_protocol_fingerprint": (
            fit_temporal_residual_breadth_utility_protocol_fingerprint()
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
        "fit_temporal_feature_support": feature_support,
        "fit_temporal_residual_bound": residual_bound,
        "fit_temporal_residual_breadth": residual_breadth,
        "fit_temporal_residual_lower_tail": {
            "authorized_protocol_change": (
                FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_AUTHORIZED
            ),
            "source_lower_bound_count_per_row": (
                FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_BOUND_COUNT_PER_ROW
            ),
            "lower_tail_fraction": (
                FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_FRACTION
            ),
            "lower_tail_count": FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_COUNT,
            "lower_tail_rule": FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_RULE,
            "eligibility_rule": RESIDUAL_LOWER_TAIL_ELIGIBILITY_RULE,
            "sort_order": "ascending_lower_bounds",
            "aggregation": "arithmetic_mean",
            "interpolation_used": False,
            "trimming_used": False,
            "winsorization_used": False,
            "uses_existing_exp055_lower_bounds": True,
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
            "fit_temporal_residual_lower_tail_authorized": (
                FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_AUTHORIZED
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


def fit_temporal_residual_lower_tail_utility_protocol_fingerprint() -> str:
    return hashlib.sha256(
        _canonical_json(
            fit_temporal_residual_lower_tail_utility_protocol_payload()
        )
    ).hexdigest()


__all__ = [
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_EXPERIMENT_ID",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_PROTOCOL_VERSION",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_PROTOCOL_DECISION",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_BOUND_COUNT_PER_ROW",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_COUNT",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_FRACTION",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_AUTHORIZED",
    "FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_RULE",
    "RESIDUAL_LOWER_TAIL_ELIGIBILITY_RULE",
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
    "fit_temporal_residual_lower_tail_utility_protocol_fingerprint",
    "fit_temporal_residual_lower_tail_utility_protocol_payload",
    "validate_fit_temporal_residual_lower_tail_predecessor_identity",
]
