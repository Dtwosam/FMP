from __future__ import annotations

from copy import deepcopy
import hashlib
import json

from .model_successor_temporal_calibrated_utility_post_result_diagnostics import (
    ACCEPTED_MODEL_CANDIDATE_COUNT,
    ADD_SMALLER_BUDGET_ANCHORS_AUTHORIZED,
    EXP051_AVAILABLE_VARIANT_COUNT,
    EXP051_REPLACEMENT_RUN_AUTHORIZED,
    EXP051_RERUN_AUTHORIZED,
    EXP051_STABLE_SELECTION_PASS_VARIANT_COUNT,
    EXP051_UNAVAILABLE_BUDGET_VARIANT_COUNT,
    EXP051_UTILITY_ELIGIBLE_SELECTION_ROW_COUNT,
    LOWER_AGGREGATE_CANDIDATE_FLOOR_AUTHORIZED,
    LOWER_DIRECTIONAL_UTILITY_POSITIVITY_AUTHORIZED,
    POST_RESULT_DIAGNOSTIC_DECISION,
    RECALIBRATE_ON_SELECTION_WINDOWS_AUTHORIZED,
    REMOVE_2021_STABILITY_WINDOWS_AUTHORIZED,
    RELAX_STABILITY_FINANCIAL_AUTHORIZED,
    RELAX_STABILITY_SHARE_AUTHORIZED,
    SOURCE_EVIDENCE_FINGERPRINT,
    SOURCE_EXPERIMENT_ID,
    SOURCE_MODEL_RUN_ID,
    SOURCE_RESULT_DECISION,
    SUCCESSOR_MODEL_FIT_AUTHORIZED,
    SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED,
    SUCCESSOR_RESULT_EXECUTION_AUTHORIZED,
    USE_SELECTION_OUTCOMES_IN_RANKING_AUTHORIZED,
    build_temporal_calibrated_utility_post_result_diagnostic_gate,
)
from .model_successor_temporal_calibrated_utility_protocol import (
    FINANCIAL_TARGET_COLUMNS,
    REQUIRED_JACKKNIFE_VIEW_COUNT,
    REQUIRED_REGRESSORS_PER_VIEW,
    TEMPORAL_CALIBRATED_UTILITY_EXPERIMENT_ID,
    TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_DECISION,
    TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_VERSION,
    TOTAL_REGRESSORS_PER_CELL,
    temporal_calibrated_utility_protocol_fingerprint,
    temporal_calibrated_utility_protocol_payload,
)


FIT_TEMPORAL_SUPPORT_UTILITY_EXPERIMENT_ID = "EXP-20260925-052"
FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_VERSION = (
    "fmp-exp052-fit-temporal-support-utility-protocol-v1"
)
FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_DECISION = "DEC-163"

DEC162_MERGED_COMMIT = (
    "3d8453c544fc4b06c691d1068828ec6da9fc7110"
)
DEC162_DIAGNOSTIC_BLOB_SHA = (
    "00b9cbb5b0c95bd161d429d1f973d1e807f02a48"
)
DEC161_RESULT_DECISION_BLOB_SHA = (
    "14bc6f2e9172aa325aeb556b7abeacf2c756c475"
)
PREDECESSOR_PROTOCOL_BLOB_SHA = (
    "c39309c4115cae1ea058e56f30cae4af6407e36e"
)
PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT = (
    "7dd836ed1c76c8eefd09b2b75e1eef9e"
    "875f5c6261c6fbb2cac8e3209781aaea"
)
PREDECESSOR_DIAGNOSTIC_CLASSIFICATION = (
    "TOP_250_FINANCIAL_QUALITY_IMPROVED_BUT_"
    "EARLY_TEMPORAL_COVERAGE_UNCHANGED_AND_"
    "BROAD_BUDGETS_DEGRADED"
)

PRIOR_RESULT_INFORMED = True
UNTOUCHED_OOS = False

SUPPORT_REFERENCE_WINDOWS_PER_EXCLUDED_REGIME = 4
FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL = (
    REQUIRED_JACKKNIFE_VIEW_COUNT
    * REQUIRED_REGRESSORS_PER_VIEW
    * SUPPORT_REFERENCE_WINDOWS_PER_EXCLUDED_REGIME
)

FIT_TEMPORAL_SUPPORT_WINDOWS = (
    {
        "name": "fit_2015_h1",
        "parent_regime": "fit_2015_2016",
        "start": "2015-01-01",
        "end_exclusive": "2015-07-01",
    },
    {
        "name": "fit_2015_h2",
        "parent_regime": "fit_2015_2016",
        "start": "2015-07-01",
        "end_exclusive": "2016-01-01",
    },
    {
        "name": "fit_2016_h1",
        "parent_regime": "fit_2015_2016",
        "start": "2016-01-01",
        "end_exclusive": "2016-07-01",
    },
    {
        "name": "fit_2016_h2",
        "parent_regime": "fit_2015_2016",
        "start": "2016-07-01",
        "end_exclusive": "2017-01-01",
    },
    {
        "name": "fit_2017_h1",
        "parent_regime": "fit_2017_2018",
        "start": "2017-01-01",
        "end_exclusive": "2017-07-01",
    },
    {
        "name": "fit_2017_h2",
        "parent_regime": "fit_2017_2018",
        "start": "2017-07-01",
        "end_exclusive": "2018-01-01",
    },
    {
        "name": "fit_2018_h1",
        "parent_regime": "fit_2017_2018",
        "start": "2018-01-01",
        "end_exclusive": "2018-07-01",
    },
    {
        "name": "fit_2018_h2",
        "parent_regime": "fit_2017_2018",
        "start": "2018-07-01",
        "end_exclusive": "2019-01-01",
    },
    {
        "name": "fit_2019_h1",
        "parent_regime": "fit_2019_2020",
        "start": "2019-01-01",
        "end_exclusive": "2019-07-01",
    },
    {
        "name": "fit_2019_h2",
        "parent_regime": "fit_2019_2020",
        "start": "2019-07-01",
        "end_exclusive": "2020-01-01",
    },
    {
        "name": "fit_2020_h1",
        "parent_regime": "fit_2019_2020",
        "start": "2020-01-01",
        "end_exclusive": "2020-07-01",
    },
    {
        "name": "fit_2020_h2",
        "parent_regime": "fit_2019_2020",
        "start": "2020-07-01",
        "end_exclusive": "2021-01-01",
    },
)

FIT_TEMPORAL_SUPPORT_REFERENCE_RULE = (
    "for each frozen jackknife view and each LONG/SHORT utility target, "
    "split exactly the two-year fit regime excluded from that view into "
    "its four frozen half-year support windows; score every row in each "
    "half-year with the already-fitted view regressor, sort all finite "
    "predictions ascending, and freeze one out-of-fit support-reference "
    "vector per view, target, and half-year; no selection, validation, "
    "holdout, or realized outcome value enters any support reference"
)
FIT_TEMPORAL_SUPPORT_PERCENTILE_RULE = (
    "for a scored row and agreed direction, compare each view's raw "
    "predicted utility separately with each of the four frozen half-year "
    "support references belonging to that view and direction; each support "
    "percentile is count(reference_prediction <= raw_predicted_utility) "
    "divided by that half-year reference count"
)
ROBUST_FIT_TEMPORAL_SUPPORT_SCORE_RULE = (
    "for an EXP-051-eligible row, robust fit-temporal support is the "
    "minimum agreed-direction support percentile across all twelve "
    "view-by-half-year comparisons; EXP-051 robust pooled calibrated "
    "utility and robust raw utility are retained unchanged as secondary "
    "and tertiary ranking scores"
)
FIT_TEMPORAL_SUPPORT_EMPTY_REFERENCE_POLICY = "FAIL_CLOSED"
FIT_TEMPORAL_SUPPORT_NONFINITE_PREDICTION_POLICY = "FAIL_CLOSED"

RANKING_RULE = (
    "sort eligible selection rows by robust fit-temporal support descending, "
    "EXP-051 robust pooled calibrated utility descending, robust raw utility "
    "descending, and row identity ascending"
)
SELECTION_CUTOFF_RULE = (
    "for each unchanged candidate budget, freeze the budget-th selection "
    "row's (robust_fit_temporal_support, robust_pooled_calibrated_utility, "
    "robust_raw_utility) triple after applying the frozen ranking order"
)
CUTOFF_TIE_POLICY = (
    "a scored row passes the frozen triple when its fit-temporal support is "
    "greater than the support cutoff; or when equal and its pooled calibrated "
    "utility is greater than the pooled cutoff; or when both are equal and "
    "its robust raw utility is greater than or equal to the raw cutoff; exact "
    "triple ties may exceed the nominal budget"
)
FORWARD_APPLICATION_RULE = (
    "validation and retrospective holdout reuse the exact six frozen "
    "jackknife regressors, six EXP-051 pooled excluded-regime references, "
    "twenty-four frozen fit-half-year support references, unchanged unanimous "
    "positive-utility direction eligibility, and the exact selection-derived "
    "support/pooled/raw cutoff triple; do not refit, rebuild any reference, "
    "recompute a budget, tune by window, or use selection, validation, or "
    "holdout outcomes to change ranking"
)

FEATURE_CHANGE_AUTHORIZED = False
FINANCIAL_TARGET_CHANGE_AUTHORIZED = False
OUTER_CHRONOLOGY_CHANGE_AUTHORIZED = False
HGB_STRUCTURAL_CONFIG_CHANGE_AUTHORIZED = False
JACKKNIFE_VIEW_CHANGE_AUTHORIZED = False
UNANIMOUS_UTILITY_CONSENSUS_CHANGE_AUTHORIZED = False
POSITIVE_UTILITY_REQUIREMENT_CHANGE_AUTHORIZED = False
POOLED_OUT_OF_FIT_CALIBRATION_CHANGE_AUTHORIZED = False
FIT_TEMPORAL_SUPPORT_CALIBRATION_AUTHORIZED = True
SELECTION_WINDOW_CALIBRATION_AUTHORIZED = False
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


def _support_windows_by_parent() -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for raw in FIT_TEMPORAL_SUPPORT_WINDOWS:
        window = dict(raw)
        parent = str(window["parent_regime"])
        grouped.setdefault(parent, []).append(window)
    return grouped


def validate_fit_temporal_support_utility_predecessor_identity(
) -> None:
    diagnostic = (
        build_temporal_calibrated_utility_post_result_diagnostic_gate()
    )
    if SOURCE_EXPERIMENT_ID != "EXP-20260924-051":
        raise ValueError(
            "EXP-052 predecessor experiment identity drift"
        )
    if SOURCE_RESULT_DECISION != "DEC-161":
        raise ValueError(
            "EXP-052 predecessor result decision drift"
        )
    if POST_RESULT_DIAGNOSTIC_DECISION != "DEC-162":
        raise ValueError(
            "EXP-052 predecessor diagnostic decision drift"
        )
    if SOURCE_MODEL_RUN_ID != 36066217609:
        raise ValueError(
            "EXP-052 predecessor model run id drift"
        )
    if SOURCE_EVIDENCE_FINGERPRINT != (
        PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT
    ):
        raise ValueError(
            "EXP-052 predecessor evidence fingerprint drift"
        )
    if diagnostic.get("diagnostic_classification") != (
        PREDECESSOR_DIAGNOSTIC_CLASSIFICATION
    ):
        raise ValueError(
            "EXP-052 predecessor diagnostic classification drift"
        )
    if ACCEPTED_MODEL_CANDIDATE_COUNT != 0:
        raise ValueError(
            "EXP-052 requires zero accepted predecessor candidates"
        )
    if EXP051_AVAILABLE_VARIANT_COUNT != 28:
        raise ValueError(
            "EXP-052 predecessor available-variant count drift"
        )
    if EXP051_UNAVAILABLE_BUDGET_VARIANT_COUNT != 26:
        raise ValueError(
            "EXP-052 predecessor unavailable-budget count drift"
        )
    if EXP051_STABLE_SELECTION_PASS_VARIANT_COUNT != 0:
        raise ValueError(
            "EXP-052 predecessor stable-pass count drift"
        )
    if EXP051_UTILITY_ELIGIBLE_SELECTION_ROW_COUNT != 26392:
        raise ValueError(
            "EXP-052 predecessor utility-eligible row count drift"
        )
    if SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED is not True:
        raise ValueError(
            "EXP-052 successor protocol source is not open"
        )
    if SUCCESSOR_RESULT_EXECUTION_AUTHORIZED is not False:
        raise ValueError(
            "EXP-052 predecessor successor execution must be closed"
        )
    if SUCCESSOR_MODEL_FIT_AUTHORIZED is not False:
        raise ValueError(
            "EXP-052 predecessor successor fit must be closed"
        )

    for name, value in (
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
        (
            "selection-window recalibration",
            RECALIBRATE_ON_SELECTION_WINDOWS_AUTHORIZED,
        ),
        (
            "selection-outcome ranking",
            USE_SELECTION_OUTCOMES_IN_RANKING_AUTHORIZED,
        ),
        (
            "lower directional positivity",
            LOWER_DIRECTIONAL_UTILITY_POSITIVITY_AUTHORIZED,
        ),
        (
            "lower aggregate candidate floor",
            LOWER_AGGREGATE_CANDIDATE_FLOOR_AUTHORIZED,
        ),
        (
            "add smaller budget anchors",
            ADD_SMALLER_BUDGET_ANCHORS_AUTHORIZED,
        ),
        (
            "rerun EXP-051",
            EXP051_RERUN_AUTHORIZED,
        ),
        (
            "replace EXP-051 run",
            EXP051_REPLACEMENT_RUN_AUTHORIZED,
        ),
    ):
        if value is not False:
            raise ValueError(
                f"EXP-052 predecessor unexpectedly authorizes {name}"
            )

    if TEMPORAL_CALIBRATED_UTILITY_EXPERIMENT_ID != (
        "EXP-20260924-051"
    ):
        raise ValueError(
            "EXP-052 predecessor protocol experiment drift"
        )
    if TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_DECISION != "DEC-150":
        raise ValueError(
            "EXP-052 predecessor protocol decision drift"
        )
    if TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_VERSION != (
        "fmp-exp051-temporal-calibrated-utility-protocol-v1"
    ):
        raise ValueError(
            "EXP-052 predecessor protocol version drift"
        )
    if REQUIRED_JACKKNIFE_VIEW_COUNT != 3:
        raise ValueError(
            "EXP-052 required jackknife view count drift"
        )
    if REQUIRED_REGRESSORS_PER_VIEW != 2:
        raise ValueError(
            "EXP-052 regressors-per-view drift"
        )
    if TOTAL_REGRESSORS_PER_CELL != 6:
        raise ValueError(
            "EXP-052 total regressor count drift"
        )
    if FINANCIAL_TARGET_COLUMNS != (
        "long_net_pips_0p5",
        "short_net_pips_0p5",
    ):
        raise ValueError(
            "EXP-052 financial target identity drift"
        )

    predecessor = temporal_calibrated_utility_protocol_payload()
    if predecessor["experiment_id"] != (
        TEMPORAL_CALIBRATED_UTILITY_EXPERIMENT_ID
    ):
        raise ValueError(
            "EXP-052 predecessor payload experiment drift"
        )
    if predecessor["protocol_decision"] != (
        TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_DECISION
    ):
        raise ValueError(
            "EXP-052 predecessor payload decision drift"
        )
    pooled = predecessor.get(
        "out_of_fit_utility_calibration"
    )
    if not isinstance(pooled, dict):
        raise ValueError(
            "EXP-052 predecessor pooled calibration missing"
        )
    if pooled.get("reference_count_per_cell") != 6:
        raise ValueError(
            "EXP-052 predecessor pooled-reference count drift"
        )
    if pooled.get("selection_rows_enter_calibration") is not False:
        raise ValueError(
            "EXP-052 predecessor selection calibration drift"
        )
    selection = predecessor.get("selection")
    if not isinstance(selection, dict):
        raise ValueError(
            "EXP-052 predecessor selection payload missing"
        )
    if selection.get("candidate_budget_anchors") != [
        250,
        500,
        1000,
    ]:
        raise ValueError(
            "EXP-052 predecessor budget identity drift"
        )
    stability = selection.get("temporal_stability")
    if not isinstance(stability, dict):
        raise ValueError(
            "EXP-052 predecessor stability payload missing"
        )
    windows = stability.get("windows")
    if not isinstance(windows, list) or len(windows) != 4:
        raise ValueError(
            "EXP-052 predecessor stability-window count drift"
        )
    if (
        stability.get(
            "minimum_directional_candidate_share_per_window"
        )
        != 0.10
    ):
        raise ValueError(
            "EXP-052 predecessor stability-share drift"
        )

    grouped = _support_windows_by_parent()
    if set(grouped) != {
        "fit_2015_2016",
        "fit_2017_2018",
        "fit_2019_2020",
    }:
        raise ValueError(
            "EXP-052 support parent-regime inventory drift"
        )
    if any(
        len(value)
        != SUPPORT_REFERENCE_WINDOWS_PER_EXCLUDED_REGIME
        for value in grouped.values()
    ):
        raise ValueError(
            "EXP-052 support half-year count drift"
        )
    if len(FIT_TEMPORAL_SUPPORT_WINDOWS) != 12:
        raise ValueError(
            "EXP-052 support-window total count drift"
        )
    if FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL != 24:
        raise ValueError(
            "EXP-052 support-reference count drift"
        )


def fit_temporal_support_utility_protocol_payload(
) -> dict[str, object]:
    validate_fit_temporal_support_utility_predecessor_identity()

    predecessor = temporal_calibrated_utility_protocol_payload()

    chronology = deepcopy(predecessor["chronology"])
    model_family = deepcopy(predecessor["model_family"])
    temporal_jackknife = deepcopy(
        predecessor["temporal_jackknife"]
    )
    utility_consensus = deepcopy(
        predecessor["utility_consensus"]
    )
    pooled_calibration = deepcopy(
        predecessor["out_of_fit_utility_calibration"]
    )
    selection = deepcopy(predecessor["selection"])
    validation = deepcopy(predecessor["validation"])
    holdout = deepcopy(
        predecessor["retrospective_holdout"]
    )

    utility_consensus["ranking_score_rule"] = (
        RANKING_RULE
    )
    utility_consensus["raw_direction_eligibility_unchanged"] = (
        True
    )
    utility_consensus["pooled_calibrated_score_retained"] = (
        True
    )

    selection.update(
        {
            "selection_cutoff_rule": SELECTION_CUTOFF_RULE,
            "cutoff_tie_policy": CUTOFF_TIE_POLICY,
            "forward_application_rule": (
                FORWARD_APPLICATION_RULE
            ),
            "ranking_order": [
                "robust_fit_temporal_support_desc",
                "robust_pooled_calibrated_utility_desc",
                "robust_raw_utility_desc",
                "row_identity_asc",
            ],
            "cutoff_components": [
                "robust_fit_temporal_support",
                "robust_pooled_calibrated_utility",
                "robust_raw_utility",
            ],
        }
    )

    validation.update(
        {
            "fit_temporal_support_reference_source": (
                "frozen_excluded_fit_regime_half_years"
            ),
            "rebuild_fit_temporal_support_reference_on_validation": (
                False
            ),
            "selection_derived_support_cutoff_reused": True,
        }
    )
    holdout.update(
        {
            "fit_temporal_support_reference_source": (
                "frozen_excluded_fit_regime_half_years"
            ),
            "rebuild_fit_temporal_support_reference_on_holdout": (
                False
            ),
            "selection_derived_support_cutoff_reused": True,
        }
    )

    return {
        "experiment_id": (
            FIT_TEMPORAL_SUPPORT_UTILITY_EXPERIMENT_ID
        ),
        "protocol_version": (
            FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_VERSION
        ),
        "protocol_decision": (
            FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_DECISION
        ),
        "predecessor": {
            "experiment_id": SOURCE_EXPERIMENT_ID,
            "result_decision": SOURCE_RESULT_DECISION,
            "diagnostic_decision": POST_RESULT_DIAGNOSTIC_DECISION,
            "diagnostic_classification": (
                PREDECESSOR_DIAGNOSTIC_CLASSIFICATION
            ),
            "diagnostic_merged_commit": (
                DEC162_MERGED_COMMIT
            ),
            "diagnostic_blob_sha": (
                DEC162_DIAGNOSTIC_BLOB_SHA
            ),
            "result_decision_blob_sha": (
                DEC161_RESULT_DECISION_BLOB_SHA
            ),
            "protocol_experiment_id": (
                TEMPORAL_CALIBRATED_UTILITY_EXPERIMENT_ID
            ),
            "protocol_decision": (
                TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_DECISION
            ),
            "protocol_version": (
                TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_VERSION
            ),
            "protocol_blob_sha": (
                PREDECESSOR_PROTOCOL_BLOB_SHA
            ),
            "protocol_fingerprint": (
                temporal_calibrated_utility_protocol_fingerprint()
            ),
            "model_run_id": SOURCE_MODEL_RUN_ID,
            "result_evidence_fingerprint": (
                PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT
            ),
            "available_variant_count": (
                EXP051_AVAILABLE_VARIANT_COUNT
            ),
            "unavailable_budget_variant_count": (
                EXP051_UNAVAILABLE_BUDGET_VARIANT_COUNT
            ),
            "stable_selection_pass_variant_count": (
                EXP051_STABLE_SELECTION_PASS_VARIANT_COUNT
            ),
            "utility_eligible_selection_row_count": (
                EXP051_UTILITY_ELIGIBLE_SELECTION_ROW_COUNT
            ),
            "accepted_model_candidate_count": 0,
            "prior_result_informed": (
                PRIOR_RESULT_INFORMED
            ),
            "untouched_oos": UNTOUCHED_OOS,
        },
        "universe": deepcopy(predecessor["universe"]),
        "inputs": deepcopy(predecessor["inputs"]),
        "financial_targets": deepcopy(
            predecessor["financial_targets"]
        ),
        "chronology": chronology,
        "model_family": model_family,
        "temporal_jackknife": temporal_jackknife,
        "utility_consensus": utility_consensus,
        "out_of_fit_utility_calibration": (
            pooled_calibration
        ),
        "fit_temporal_support_calibration": {
            "authorized_protocol_change": (
                FIT_TEMPORAL_SUPPORT_CALIBRATION_AUTHORIZED
            ),
            "support_windows": [
                dict(window)
                for window in FIT_TEMPORAL_SUPPORT_WINDOWS
            ],
            "support_windows_per_excluded_regime": (
                SUPPORT_REFERENCE_WINDOWS_PER_EXCLUDED_REGIME
            ),
            "reference_count_per_cell": (
                FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL
            ),
            "reference_rule": (
                FIT_TEMPORAL_SUPPORT_REFERENCE_RULE
            ),
            "percentile_rule": (
                FIT_TEMPORAL_SUPPORT_PERCENTILE_RULE
            ),
            "robust_support_score_rule": (
                ROBUST_FIT_TEMPORAL_SUPPORT_SCORE_RULE
            ),
            "aggregation": "minimum",
            "pooled_exp051_calibration_retained": True,
            "uses_realized_outcomes": False,
            "selection_rows_enter_support_references": False,
            "validation_rows_enter_support_references": False,
            "holdout_rows_enter_support_references": False,
            "empty_reference_policy": (
                FIT_TEMPORAL_SUPPORT_EMPTY_REFERENCE_POLICY
            ),
            "nonfinite_prediction_policy": (
                FIT_TEMPORAL_SUPPORT_NONFINITE_PREDICTION_POLICY
            ),
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
            "feature_change_authorized": (
                FEATURE_CHANGE_AUTHORIZED
            ),
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
            "fit_temporal_support_calibration_authorized": (
                FIT_TEMPORAL_SUPPORT_CALIBRATION_AUTHORIZED
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
            "broker_mutation_authorized": (
                BROKER_MUTATION_AUTHORIZED
            ),
            "live_order_authorized": LIVE_ORDER_AUTHORIZED,
            "real_money_authorized": REAL_MONEY_AUTHORIZED,
            "trading_authorized": TRADING_AUTHORIZED,
        },
    }


def fit_temporal_support_utility_protocol_fingerprint() -> str:
    return hashlib.sha256(
        _canonical_json(
            fit_temporal_support_utility_protocol_payload()
        )
    ).hexdigest()


__all__ = [
    "BROKER_MUTATION_AUTHORIZED",
    "CLASSIFIER_FALLBACK_AUTHORIZED",
    "CUTOFF_TIE_POLICY",
    "DEC161_RESULT_DECISION_BLOB_SHA",
    "DEC162_DIAGNOSTIC_BLOB_SHA",
    "DEC162_MERGED_COMMIT",
    "DEMO_ORDER_AUTHORIZED",
    "DENSITY_ANCHOR_CHANGE_AUTHORIZED",
    "FEATURE_CHANGE_AUTHORIZED",
    "FINANCIAL_TARGET_CHANGE_AUTHORIZED",
    "FIT_TEMPORAL_SUPPORT_CALIBRATION_AUTHORIZED",
    "FIT_TEMPORAL_SUPPORT_EMPTY_REFERENCE_POLICY",
    "FIT_TEMPORAL_SUPPORT_NONFINITE_PREDICTION_POLICY",
    "FIT_TEMPORAL_SUPPORT_PERCENTILE_RULE",
    "FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL",
    "FIT_TEMPORAL_SUPPORT_REFERENCE_RULE",
    "FIT_TEMPORAL_SUPPORT_UTILITY_EXPERIMENT_ID",
    "FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_DECISION",
    "FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_VERSION",
    "FIT_TEMPORAL_SUPPORT_WINDOWS",
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
    "PER_WINDOW_CUTOFF_TUNING_AUTHORIZED",
    "PER_WINDOW_FINANCIAL_GATE_CHANGE_AUTHORIZED",
    "POOLED_OUT_OF_FIT_CALIBRATION_CHANGE_AUTHORIZED",
    "POSITIVE_UTILITY_REQUIREMENT_CHANGE_AUTHORIZED",
    "PREDECESSOR_DIAGNOSTIC_CLASSIFICATION",
    "PREDECESSOR_PROTOCOL_BLOB_SHA",
    "PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT",
    "PRIOR_RESULT_INFORMED",
    "PROMOTION_AUTHORIZED",
    "RANKING_RULE",
    "REALIZED_SELECTION_OUTCOME_RANKING_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "ROBUST_FIT_TEMPORAL_SUPPORT_SCORE_RULE",
    "SELECTION_CUTOFF_RULE",
    "SELECTION_WINDOW_CALIBRATION_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "STABILITY_SCREEN_CHANGE_AUTHORIZED",
    "SUPPORT_REFERENCE_WINDOWS_PER_EXCLUDED_REGIME",
    "TRADING_AUTHORIZED",
    "UNANIMOUS_UTILITY_CONSENSUS_CHANGE_AUTHORIZED",
    "UNTOUCHED_OOS",
    "VALIDATION_CALIBRATION_AUTHORIZED",
    "fit_temporal_support_utility_protocol_fingerprint",
    "fit_temporal_support_utility_protocol_payload",
    "validate_fit_temporal_support_utility_predecessor_identity",
]
