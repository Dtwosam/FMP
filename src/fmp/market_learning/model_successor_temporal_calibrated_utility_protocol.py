from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from .model_protocol import (
    GATE_REQUIREMENTS,
    MIN_DIRECTIONAL_CANDIDATES,
    MODEL_CELLS,
    MODEL_HORIZONS_MINUTES,
    MODEL_SYMBOLS,
    MODEL_TIMEFRAMES,
)
from .model_successor_density_protocol import (
    CANDIDATE_BUDGET_ANCHORS,
)
from .model_successor_stability_protocol import (
    MIN_STABILITY_WINDOW_CANDIDATE_SHARE,
    STABILITY_WINDOW_REQUIREMENTS,
    TEMPORAL_STABILITY_WINDOWS,
)
from .model_successor_temporal_jackknife_utility_post_result_diagnostics import (
    ACCEPTED_MODEL_CANDIDATE_COUNT,
    AGGREGATE_SELECTION_PASS_VARIANT_COUNT,
    ALTER_TEMPORAL_JACKKNIFE_VIEWS_AUTHORIZED,
    ALTER_UNANIMOUS_UTILITY_CONSENSUS_AUTHORIZED,
    AVAILABLE_VARIANT_COUNT,
    LOWER_UTILITY_POSITIVITY_REQUIREMENT_AUTHORIZED,
    POST_RESULT_DIAGNOSTIC_DECISION,
    RELAX_STABILITY_FINANCIAL_AUTHORIZED,
    RELAX_STABILITY_SHARE_AUTHORIZED,
    REMOVE_2021_STABILITY_WINDOWS_AUTHORIZED,
    SELECTION_2021_H1_ZERO_CANDIDATE_VARIANT_COUNT,
    SOURCE_EVIDENCE_FINGERPRINT,
    SOURCE_EXPERIMENT_ID,
    SOURCE_MODEL_RUN_ID,
    SOURCE_RESULT_DECISION,
    STABLE_SELECTION_PASS_VARIANT_COUNT,
    SUCCESSOR_MODEL_FIT_AUTHORIZED,
    SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED,
    SUCCESSOR_RESULT_EXECUTION_AUTHORIZED,
    TOTAL_VARIANT_COUNT,
    UNAVAILABLE_BUDGET_VARIANT_COUNT,
    UTILITY_ELIGIBLE_SELECTION_ROW_COUNT,
    build_temporal_jackknife_utility_post_result_diagnostic_gate,
)
from .model_successor_temporal_jackknife_utility_protocol import (
    AUTHORIZED_MODEL_FAMILIES,
    EXCLUDED_MODEL_FAMILIES,
    FINANCIAL_TARGET_COLUMNS,
    FINANCIAL_TARGET_SLIPPAGE_PIPS,
    FIT_JACKKNIFE_VIEWS,
    HIST_GRADIENT_BOOSTING_REGRESSION_CONFIG,
    REQUIRED_JACKKNIFE_VIEW_COUNT,
    REQUIRED_REGRESSORS_PER_VIEW,
    TEMPORAL_JACKKNIFE_DIRECTION_RULE,
    TEMPORAL_JACKKNIFE_DISAGREEMENT_POLICY,
    TEMPORAL_JACKKNIFE_SCORE_RULE,
    TEMPORAL_JACKKNIFE_SELECTION_TIE_BREAK,
    TEMPORAL_JACKKNIFE_UTILITY_EXPERIMENT_ID,
    TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_DECISION,
    TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_VERSION,
    TOTAL_REGRESSORS_PER_CELL,
    temporal_jackknife_utility_protocol_fingerprint,
    temporal_jackknife_utility_protocol_payload,
    validate_temporal_jackknife_utility_predecessor_identity,
)


TEMPORAL_CALIBRATED_UTILITY_EXPERIMENT_ID = "EXP-20260924-051"
TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_VERSION = (
    "fmp-exp051-temporal-calibrated-utility-protocol-v1"
)
TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_DECISION = "DEC-150"

DEC149_MERGED_COMMIT = (
    "d8874bf213c420fb506cc9ee8c4dfb2caffbb9e1"
)
DEC149_DIAGNOSTIC_BLOB_SHA = (
    "f23465ca30249ce8abab3c9fdf07ce39a8679a9a"
)
DEC148_RESULT_DECISION_BLOB_SHA = (
    "70402f6c21f4ed22b4991025c98e6c1664215215"
)
PREDECESSOR_PROTOCOL_BLOB_SHA = (
    "b41b817b03aa0cc03a9d893227caa399b46d3cf8"
)
PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT = (
    "866b4a8f26553bad8c80a7b2e0e68aed"
    "b50bfa42b3c767ce91478c9dfd720023"
)
PREDECESSOR_DIAGNOSTIC_CLASSIFICATION = (
    "UTILITY_COVERAGE_INCREASED_BUT_"
    "EARLY_TEMPORAL_COVERAGE_LIMITED"
)

PRIOR_RESULT_INFORMED = True
UNTOUCHED_OOS = False

CALIBRATION_REFERENCE_RULE = (
    "for each frozen jackknife view and each LONG/SHORT utility target, "
    "score exactly the two-year fit regime excluded from that view with "
    "the already-fitted view regressor; sort all finite predicted utilities "
    "ascending and freeze that vector as the view/target out-of-fit "
    "calibration reference; realized outcomes, selection rows, validation "
    "rows, and holdout rows do not enter calibration"
)
CALIBRATED_PERCENTILE_RULE = (
    "for a scored row and agreed direction, each view's calibrated utility "
    "percentile is count(reference_prediction <= raw_predicted_utility) "
    "divided by the frozen reference count for that view and direction"
)
ROBUST_CALIBRATED_SCORE_RULE = (
    "for an EXP-050-eligible row, robust calibrated utility is the minimum "
    "agreed-direction calibrated percentile across all three frozen "
    "jackknife views; the predecessor minimum raw predicted utility is "
    "retained unchanged as robust raw utility"
)
CALIBRATION_EMPTY_REFERENCE_POLICY = "FAIL_CLOSED"
CALIBRATION_NONFINITE_PREDICTION_POLICY = "FAIL_CLOSED"

SELECTION_CUTOFF_RULE = (
    "for each candidate budget, sort eligible selection rows by robust "
    "calibrated utility descending, robust raw utility descending, and row "
    "identity ascending; freeze the budget-th row's "
    "(robust_calibrated_utility, robust_raw_utility) pair as the cutoff"
)
CUTOFF_TIE_POLICY = (
    "a scored row passes the frozen cutoff when its robust calibrated "
    "utility is greater than the cutoff percentile, or when equal and its "
    "robust raw utility is greater than or equal to the cutoff raw utility; "
    "exact score-pair ties may exceed the nominal budget"
)
FORWARD_APPLICATION_RULE = (
    "validation and retrospective holdout reuse the exact six frozen "
    "jackknife regressors, the exact six frozen excluded-regime calibration "
    "references, the unchanged unanimous positive-utility direction rule, "
    "and the exact selection-derived calibrated/raw cutoff pair; do not "
    "refit, rebuild calibration references, recompute a budget, tune by "
    "window, or recalibrate on selection, validation, or holdout rows"
)

FEATURE_CHANGE_AUTHORIZED = False
FINANCIAL_TARGET_CHANGE_AUTHORIZED = False
OUTER_CHRONOLOGY_CHANGE_AUTHORIZED = False
HGB_STRUCTURAL_CONFIG_CHANGE_AUTHORIZED = False
JACKKNIFE_VIEW_CHANGE_AUTHORIZED = False
UNANIMOUS_UTILITY_CONSENSUS_CHANGE_AUTHORIZED = False
POSITIVE_UTILITY_REQUIREMENT_CHANGE_AUTHORIZED = False
OUT_OF_FIT_UTILITY_CALIBRATION_AUTHORIZED = True
SELECTION_WINDOW_CALIBRATION_AUTHORIZED = False
VALIDATION_CALIBRATION_AUTHORIZED = False
HOLDOUT_CALIBRATION_AUTHORIZED = False
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


def validate_temporal_calibrated_utility_predecessor_identity(
) -> None:
    validate_temporal_jackknife_utility_predecessor_identity()

    diagnostic = (
        build_temporal_jackknife_utility_post_result_diagnostic_gate()
    )
    if SOURCE_EXPERIMENT_ID != "EXP-20260924-050":
        raise ValueError(
            "EXP-051 predecessor experiment identity drift"
        )
    if SOURCE_RESULT_DECISION != "DEC-148":
        raise ValueError(
            "EXP-051 predecessor result decision drift"
        )
    if POST_RESULT_DIAGNOSTIC_DECISION != "DEC-149":
        raise ValueError(
            "EXP-051 predecessor diagnostic decision drift"
        )
    if SOURCE_MODEL_RUN_ID != 36049824739:
        raise ValueError(
            "EXP-051 predecessor model run id drift"
        )
    if SOURCE_EVIDENCE_FINGERPRINT != (
        PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT
    ):
        raise ValueError(
            "EXP-051 predecessor evidence fingerprint drift"
        )
    if diagnostic.get("diagnostic_classification") != (
        PREDECESSOR_DIAGNOSTIC_CLASSIFICATION
    ):
        raise ValueError(
            "EXP-051 predecessor diagnostic classification drift"
        )
    if ACCEPTED_MODEL_CANDIDATE_COUNT != 0:
        raise ValueError(
            "EXP-051 requires zero accepted predecessor candidates"
        )
    if TOTAL_VARIANT_COUNT != 54:
        raise ValueError(
            "EXP-051 predecessor total-variant count drift"
        )
    if AVAILABLE_VARIANT_COUNT != 28:
        raise ValueError(
            "EXP-051 predecessor available-variant count drift"
        )
    if UNAVAILABLE_BUDGET_VARIANT_COUNT != 26:
        raise ValueError(
            "EXP-051 predecessor unavailable-budget count drift"
        )
    if AGGREGATE_SELECTION_PASS_VARIANT_COUNT != 3:
        raise ValueError(
            "EXP-051 predecessor aggregate-pass count drift"
        )
    if STABLE_SELECTION_PASS_VARIANT_COUNT != 0:
        raise ValueError(
            "EXP-051 predecessor stable-pass count drift"
        )
    if SELECTION_2021_H1_ZERO_CANDIDATE_VARIANT_COUNT != 3:
        raise ValueError(
            "EXP-051 predecessor 2021-H1 coverage count drift"
        )
    if UTILITY_ELIGIBLE_SELECTION_ROW_COUNT != 26392:
        raise ValueError(
            "EXP-051 predecessor utility-eligible row count drift"
        )
    if SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED is not True:
        raise ValueError(
            "EXP-051 successor protocol source is not open"
        )
    if SUCCESSOR_RESULT_EXECUTION_AUTHORIZED is not False:
        raise ValueError(
            "EXP-051 requires predecessor successor execution closed"
        )
    if SUCCESSOR_MODEL_FIT_AUTHORIZED is not False:
        raise ValueError(
            "EXP-051 requires predecessor successor fit closed"
        )

    for name, value in (
        (
            "alter temporal jackknife views",
            ALTER_TEMPORAL_JACKKNIFE_VIEWS_AUTHORIZED,
        ),
        (
            "alter unanimous utility consensus",
            ALTER_UNANIMOUS_UTILITY_CONSENSUS_AUTHORIZED,
        ),
        (
            "lower positive utility requirement",
            LOWER_UTILITY_POSITIVITY_REQUIREMENT_AUTHORIZED,
        ),
        (
            "relax stability share",
            RELAX_STABILITY_SHARE_AUTHORIZED,
        ),
        (
            "relax stability financial",
            RELAX_STABILITY_FINANCIAL_AUTHORIZED,
        ),
        (
            "remove 2021 stability windows",
            REMOVE_2021_STABILITY_WINDOWS_AUTHORIZED,
        ),
    ):
        if value is not False:
            raise ValueError(
                f"EXP-051 predecessor unexpectedly authorizes {name}"
            )

    if TEMPORAL_JACKKNIFE_UTILITY_EXPERIMENT_ID != (
        "EXP-20260924-050"
    ):
        raise ValueError(
            "EXP-051 predecessor protocol experiment drift"
        )
    if TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_DECISION != "DEC-141":
        raise ValueError(
            "EXP-051 predecessor protocol decision drift"
        )
    if TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_VERSION != (
        "fmp-exp050-temporal-jackknife-utility-protocol-v1"
    ):
        raise ValueError(
            "EXP-051 predecessor protocol version drift"
        )
    if len(FIT_JACKKNIFE_VIEWS) != 3:
        raise ValueError(
            "EXP-051 jackknife view count drift"
        )
    if REQUIRED_JACKKNIFE_VIEW_COUNT != 3:
        raise ValueError(
            "EXP-051 required jackknife view count drift"
        )
    if REQUIRED_REGRESSORS_PER_VIEW != 2:
        raise ValueError(
            "EXP-051 regressors-per-view drift"
        )
    if TOTAL_REGRESSORS_PER_CELL != 6:
        raise ValueError(
            "EXP-051 total regressor count drift"
        )
    if tuple(AUTHORIZED_MODEL_FAMILIES) != (
        "hist_gradient_boosting_regression",
    ):
        raise ValueError(
            "EXP-051 authorized model family drift"
        )
    if tuple(EXCLUDED_MODEL_FAMILIES) != (
        "logistic_regression",
        "hist_gradient_boosting_classifier",
    ):
        raise ValueError(
            "EXP-051 excluded model family drift"
        )
    if FINANCIAL_TARGET_COLUMNS != (
        "long_net_pips_0p5",
        "short_net_pips_0p5",
    ):
        raise ValueError(
            "EXP-051 financial target identity drift"
        )
    if FINANCIAL_TARGET_SLIPPAGE_PIPS != 0.5:
        raise ValueError(
            "EXP-051 financial target cost drift"
        )
    if tuple(CANDIDATE_BUDGET_ANCHORS) != (250, 500, 1000):
        raise ValueError(
            "EXP-051 candidate budget identity drift"
        )
    if MIN_DIRECTIONAL_CANDIDATES != 250:
        raise ValueError(
            "EXP-051 minimum directional candidate count drift"
        )
    if MIN_STABILITY_WINDOW_CANDIDATE_SHARE != 0.10:
        raise ValueError(
            "EXP-051 temporal stability share drift"
        )
    if tuple(STABILITY_WINDOW_REQUIREMENTS) != (
        "directional_candidate_share>=0.10",
        "total_net_pips>0",
        "mean_net_pips>0",
        "gross_positive_pips>absolute_gross_negative_pips",
    ):
        raise ValueError(
            "EXP-051 temporal stability requirements drift"
        )
    if "greater than zero" not in TEMPORAL_JACKKNIFE_DIRECTION_RULE:
        raise ValueError(
            "EXP-051 predecessor positive-utility rule drift"
        )
    if "minimum predicted net pips" not in (
        TEMPORAL_JACKKNIFE_SCORE_RULE
    ):
        raise ValueError(
            "EXP-051 predecessor raw utility score drift"
        )


def temporal_calibrated_utility_protocol_payload(
) -> dict[str, object]:
    validate_temporal_calibrated_utility_predecessor_identity()

    predecessor = temporal_jackknife_utility_protocol_payload()
    chronology = deepcopy(predecessor["chronology"])
    model_family = deepcopy(predecessor["model_family"])
    temporal_jackknife = deepcopy(
        predecessor["temporal_jackknife"]
    )
    utility_consensus = deepcopy(
        predecessor["utility_consensus"]
    )
    validation = deepcopy(predecessor["validation"])
    holdout = deepcopy(predecessor["retrospective_holdout"])

    utility_consensus["raw_score_rule"] = (
        TEMPORAL_JACKKNIFE_SCORE_RULE
    )
    utility_consensus["ranking_score_rule"] = (
        ROBUST_CALIBRATED_SCORE_RULE
    )
    utility_consensus["direction_rule_change_authorized"] = (
        UNANIMOUS_UTILITY_CONSENSUS_CHANGE_AUTHORIZED
    )

    validation.update(
        {
            "calibration_reference_source": (
                "frozen_excluded_fit_regimes"
            ),
            "rebuild_calibration_reference_on_validation": False,
        }
    )
    holdout.update(
        {
            "calibration_reference_source": (
                "frozen_excluded_fit_regimes"
            ),
            "rebuild_calibration_reference_on_holdout": False,
        }
    )

    return {
        "experiment_id": TEMPORAL_CALIBRATED_UTILITY_EXPERIMENT_ID,
        "protocol_version": (
            TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_VERSION
        ),
        "protocol_decision": (
            TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_DECISION
        ),
        "predecessor": {
            "experiment_id": SOURCE_EXPERIMENT_ID,
            "result_decision": SOURCE_RESULT_DECISION,
            "diagnostic_decision": POST_RESULT_DIAGNOSTIC_DECISION,
            "diagnostic_classification": (
                PREDECESSOR_DIAGNOSTIC_CLASSIFICATION
            ),
            "diagnostic_merged_commit": DEC149_MERGED_COMMIT,
            "diagnostic_blob_sha": DEC149_DIAGNOSTIC_BLOB_SHA,
            "result_decision_blob_sha": (
                DEC148_RESULT_DECISION_BLOB_SHA
            ),
            "protocol_experiment_id": (
                TEMPORAL_JACKKNIFE_UTILITY_EXPERIMENT_ID
            ),
            "protocol_decision": (
                TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_DECISION
            ),
            "protocol_version": (
                TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_VERSION
            ),
            "protocol_blob_sha": PREDECESSOR_PROTOCOL_BLOB_SHA,
            "protocol_fingerprint": (
                temporal_jackknife_utility_protocol_fingerprint()
            ),
            "model_run_id": SOURCE_MODEL_RUN_ID,
            "result_evidence_fingerprint": (
                PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT
            ),
            "total_variant_count": TOTAL_VARIANT_COUNT,
            "available_variant_count": AVAILABLE_VARIANT_COUNT,
            "unavailable_budget_variant_count": (
                UNAVAILABLE_BUDGET_VARIANT_COUNT
            ),
            "aggregate_selection_pass_variant_count": (
                AGGREGATE_SELECTION_PASS_VARIANT_COUNT
            ),
            "stable_selection_pass_variant_count": (
                STABLE_SELECTION_PASS_VARIANT_COUNT
            ),
            "selection_2021_h1_zero_candidate_variant_count": (
                SELECTION_2021_H1_ZERO_CANDIDATE_VARIANT_COUNT
            ),
            "utility_eligible_selection_row_count": (
                UTILITY_ELIGIBLE_SELECTION_ROW_COUNT
            ),
            "accepted_model_candidate_count": 0,
            "prior_result_informed": PRIOR_RESULT_INFORMED,
            "untouched_oos": UNTOUCHED_OOS,
        },
        "universe": {
            "symbols": list(MODEL_SYMBOLS),
            "timeframes": list(MODEL_TIMEFRAMES),
            "horizons_minutes": list(MODEL_HORIZONS_MINUTES),
            "cell_count": len(MODEL_CELLS),
        },
        "inputs": deepcopy(predecessor["inputs"]),
        "financial_targets": deepcopy(
            predecessor["financial_targets"]
        ),
        "chronology": chronology,
        "model_family": model_family,
        "temporal_jackknife": {
            **temporal_jackknife,
            "view_change_authorized": (
                JACKKNIFE_VIEW_CHANGE_AUTHORIZED
            ),
        },
        "utility_consensus": utility_consensus,
        "out_of_fit_utility_calibration": {
            "authorized_protocol_change": (
                OUT_OF_FIT_UTILITY_CALIBRATION_AUTHORIZED
            ),
            "reference_rule": CALIBRATION_REFERENCE_RULE,
            "percentile_rule": CALIBRATED_PERCENTILE_RULE,
            "robust_score_rule": ROBUST_CALIBRATED_SCORE_RULE,
            "reference_count_per_cell": (
                REQUIRED_JACKKNIFE_VIEW_COUNT
                * REQUIRED_REGRESSORS_PER_VIEW
            ),
            "reference_scope": (
                "one excluded fit-regime prediction vector per "
                "jackknife view and utility target"
            ),
            "uses_realized_outcomes": False,
            "selection_rows_enter_calibration": False,
            "validation_rows_enter_calibration": False,
            "holdout_rows_enter_calibration": False,
            "empty_reference_policy": (
                CALIBRATION_EMPTY_REFERENCE_POLICY
            ),
            "nonfinite_prediction_policy": (
                CALIBRATION_NONFINITE_PREDICTION_POLICY
            ),
        },
        "selection": {
            "candidate_budget_anchors": list(
                CANDIDATE_BUDGET_ANCHORS
            ),
            "density_anchor_change_authorized": (
                DENSITY_ANCHOR_CHANGE_AUTHORIZED
            ),
            "selection_cutoff_rule": SELECTION_CUTOFF_RULE,
            "cutoff_tie_policy": CUTOFF_TIE_POLICY,
            "forward_application_rule": FORWARD_APPLICATION_RULE,
            "minimum_directional_candidates": (
                MIN_DIRECTIONAL_CANDIDATES
            ),
            "minimum_directional_candidate_count_change_authorized": (
                MIN_DIRECTIONAL_CANDIDATE_COUNT_CHANGE_AUTHORIZED
            ),
            "gate_scenarios": deepcopy(
                predecessor["selection"]["gate_scenarios"]
            ),
            "aggregate_gate_requirements": list(
                GATE_REQUIREMENTS
            ),
            "temporal_stability": {
                "windows": [
                    dict(window)
                    for window in TEMPORAL_STABILITY_WINDOWS
                ],
                "minimum_directional_candidate_share_per_window": (
                    MIN_STABILITY_WINDOW_CANDIDATE_SHARE
                ),
                "requirements_per_window": list(
                    STABILITY_WINDOW_REQUIREMENTS
                ),
                "all_windows_must_pass": True,
                "stability_screen_change_authorized": (
                    STABILITY_SCREEN_CHANGE_AUTHORIZED
                ),
                "per_window_financial_gate_change_authorized": (
                    PER_WINDOW_FINANCIAL_GATE_CHANGE_AUTHORIZED
                ),
            },
            "selection_window_calibration_authorized": (
                SELECTION_WINDOW_CALIBRATION_AUTHORIZED
            ),
            "per_window_cutoff_tuning_authorized": (
                PER_WINDOW_CUTOFF_TUNING_AUTHORIZED
            ),
            "tie_break": list(
                TEMPORAL_JACKKNIFE_SELECTION_TIE_BREAK
            ),
        },
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
            "selection_window_calibration_authorized": (
                SELECTION_WINDOW_CALIBRATION_AUTHORIZED
            ),
            "validation_calibration_authorized": (
                VALIDATION_CALIBRATION_AUTHORIZED
            ),
            "holdout_calibration_authorized": (
                HOLDOUT_CALIBRATION_AUTHORIZED
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
            "broker_mutation_authorized": (
                BROKER_MUTATION_AUTHORIZED
            ),
            "live_order_authorized": LIVE_ORDER_AUTHORIZED,
            "real_money_authorized": REAL_MONEY_AUTHORIZED,
            "trading_authorized": TRADING_AUTHORIZED,
        },
    }


def temporal_calibrated_utility_protocol_fingerprint() -> str:
    return hashlib.sha256(
        _canonical_json(
            temporal_calibrated_utility_protocol_payload()
        )
    ).hexdigest()


__all__ = [
    "BROKER_MUTATION_AUTHORIZED",
    "CALIBRATED_PERCENTILE_RULE",
    "CALIBRATION_EMPTY_REFERENCE_POLICY",
    "CALIBRATION_NONFINITE_PREDICTION_POLICY",
    "CALIBRATION_REFERENCE_RULE",
    "CLASSIFIER_FALLBACK_AUTHORIZED",
    "CUTOFF_TIE_POLICY",
    "DEC148_RESULT_DECISION_BLOB_SHA",
    "DEC149_DIAGNOSTIC_BLOB_SHA",
    "DEC149_MERGED_COMMIT",
    "DEMO_ORDER_AUTHORIZED",
    "DENSITY_ANCHOR_CHANGE_AUTHORIZED",
    "FEATURE_CHANGE_AUTHORIZED",
    "FINANCIAL_TARGET_CHANGE_AUTHORIZED",
    "FORWARD_APPLICATION_RULE",
    "HGB_STRUCTURAL_CONFIG_CHANGE_AUTHORIZED",
    "HISTORICAL_RESULT_EXECUTION_AUTHORIZED",
    "HOLDOUT_CALIBRATION_AUTHORIZED",
    "JACKKNIFE_VIEW_CHANGE_AUTHORIZED",
    "LIVE_ORDER_AUTHORIZED",
    "LOGISTIC_REINTRODUCTION_AUTHORIZED",
    "MIN_DIRECTIONAL_CANDIDATE_COUNT_CHANGE_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "OUTER_CHRONOLOGY_CHANGE_AUTHORIZED",
    "OUT_OF_FIT_UTILITY_CALIBRATION_AUTHORIZED",
    "PER_WINDOW_CUTOFF_TUNING_AUTHORIZED",
    "PER_WINDOW_FINANCIAL_GATE_CHANGE_AUTHORIZED",
    "POSITIVE_UTILITY_REQUIREMENT_CHANGE_AUTHORIZED",
    "PREDECESSOR_DIAGNOSTIC_CLASSIFICATION",
    "PREDECESSOR_PROTOCOL_BLOB_SHA",
    "PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT",
    "PRIOR_RESULT_INFORMED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "ROBUST_CALIBRATED_SCORE_RULE",
    "SELECTION_CUTOFF_RULE",
    "SELECTION_WINDOW_CALIBRATION_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "STABILITY_SCREEN_CHANGE_AUTHORIZED",
    "TEMPORAL_CALIBRATED_UTILITY_EXPERIMENT_ID",
    "TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_DECISION",
    "TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_VERSION",
    "TRADING_AUTHORIZED",
    "UNANIMOUS_UTILITY_CONSENSUS_CHANGE_AUTHORIZED",
    "UNTOUCHED_OOS",
    "VALIDATION_CALIBRATION_AUTHORIZED",
    "temporal_calibrated_utility_protocol_fingerprint",
    "temporal_calibrated_utility_protocol_payload",
    "validate_temporal_calibrated_utility_predecessor_identity",
]
