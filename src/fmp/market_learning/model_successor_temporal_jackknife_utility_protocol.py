from __future__ import annotations

import hashlib
import json
from types import MappingProxyType

from .model_protocol import (
    DIAGNOSTIC_SCENARIOS,
    FIT_SPLIT,
    GATE_REQUIREMENTS,
    HOLDOUT_GATE_SCENARIOS,
    MIN_DIRECTIONAL_CANDIDATES,
    MODEL_CELLS,
    MODEL_HORIZONS_MINUTES,
    MODEL_INPUT_COLUMNS,
    MODEL_SYMBOLS,
    MODEL_TIMEFRAMES,
    PROTOCOL_SPLITS,
    RETROSPECTIVE_HOLDOUT_SPLIT,
    SCIKIT_LEARN_VERSION,
    SELECTION_GATE_SCENARIOS,
    SELECTION_SPLIT,
    VALIDATION_GATE_SCENARIOS,
    VALIDATION_SPLIT,
)
from .model_successor_density_protocol import (
    CANDIDATE_BUDGET_ANCHORS,
)
from .model_successor_regime_utility_post_result_diagnostics import (
    ACCEPTED_MODEL_CANDIDATE_COUNT,
    AGGREGATE_SELECTION_PASS_VARIANT_COUNT,
    BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT,
    LOWER_UTILITY_POSITIVITY_REQUIREMENT_AUTHORIZED,
    POST_RESULT_DIAGNOSTIC_DECISION,
    RELAX_STABILITY_FINANCIAL_AUTHORIZED,
    RELAX_STABILITY_SHARE_AUTHORIZED,
    REMOVE_2021_STABILITY_WINDOWS_AUTHORIZED,
    SOURCE_EVIDENCE_FINGERPRINT,
    SOURCE_EXPERIMENT_ID,
    SOURCE_MODEL_RUN_ID,
    SOURCE_RESULT_DECISION,
    SUCCESSOR_MODEL_FIT_AUTHORIZED,
    SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED,
    SUCCESSOR_RESULT_EXECUTION_AUTHORIZED,
    TOTAL_VARIANT_COUNT,
    UNAVAILABLE_BUDGET_VARIANT_COUNT,
)
from .model_successor_regime_utility_protocol import (
    AUTHORIZED_MODEL_FAMILIES as PREDECESSOR_AUTHORIZED_MODEL_FAMILIES,
    EXCLUDED_MODEL_FAMILIES as PREDECESSOR_EXCLUDED_MODEL_FAMILIES,
    FINANCIAL_TARGET_COLUMNS as PREDECESSOR_FINANCIAL_TARGET_COLUMNS,
    FINANCIAL_TARGET_SLIPPAGE_PIPS as PREDECESSOR_FINANCIAL_TARGET_SLIPPAGE_PIPS,
    FIT_REGIME_WINDOWS as PREDECESSOR_FIT_REGIME_WINDOWS,
    HIST_GRADIENT_BOOSTING_REGRESSION_CONFIG as PREDECESSOR_HGB_REGRESSION_CONFIG,
    REGIME_UTILITY_DIRECTION_RULE as PREDECESSOR_DIRECTION_RULE,
    REGIME_UTILITY_SCORE_RULE as PREDECESSOR_SCORE_RULE,
    REGIME_UTILITY_SELECTION_TIE_BREAK as PREDECESSOR_SELECTION_TIE_BREAK,
)
from .model_successor_stability_protocol import (
    MIN_STABILITY_WINDOW_CANDIDATE_SHARE,
    STABILITY_WINDOW_REQUIREMENTS,
    TEMPORAL_STABILITY_WINDOWS,
)


TEMPORAL_JACKKNIFE_UTILITY_EXPERIMENT_ID = "EXP-20260924-050"
TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_VERSION = (
    "fmp-exp050-temporal-jackknife-utility-protocol-v1"
)
TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_DECISION = "DEC-141"

DEC140_MERGED_COMMIT = (
    "04f06deb4d68f9936438eec20dbb9610683bbc2e"
)
DEC140_DIAGNOSTIC_BLOB_SHA = (
    "e286be2574d4cee60322a4b65213af76ab34b381"
)
DEC139_RESULT_DECISION_BLOB_SHA = (
    "dce13838f32fbb8aa0e403c550b669f778dd0742"
)
PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT = (
    "29ecbb5bf3ce00f35c825e977d9b3fff"
    "1777e165ce9bef311fefcb7bfbdb091e"
)
PREDECESSOR_DIAGNOSTIC_CLASSIFICATION = (
    "UTILITY_COVERAGE_AND_DUAL_TEMPORAL_STABILITY_LIMITED"
)

PRIOR_RESULT_INFORMED = True
UNTOUCHED_OOS = False

AUTHORIZED_MODEL_FAMILIES = tuple(
    PREDECESSOR_AUTHORIZED_MODEL_FAMILIES
)
EXCLUDED_MODEL_FAMILIES = tuple(
    PREDECESSOR_EXCLUDED_MODEL_FAMILIES
)
FINANCIAL_TARGET_COLUMNS = tuple(
    PREDECESSOR_FINANCIAL_TARGET_COLUMNS
)
FINANCIAL_TARGET_SLIPPAGE_PIPS = (
    PREDECESSOR_FINANCIAL_TARGET_SLIPPAGE_PIPS
)
HIST_GRADIENT_BOOSTING_REGRESSION_CONFIG = MappingProxyType(
    dict(PREDECESSOR_HGB_REGRESSION_CONFIG)
)

PREDECESSOR_REGIME_NAMES = tuple(
    str(window["name"])
    for window in PREDECESSOR_FIT_REGIME_WINDOWS
)

FIT_JACKKNIFE_VIEWS = (
    MappingProxyType(
        {
            "name": "leave_out_fit_2015_2016",
            "excluded_regime": "fit_2015_2016",
            "included_regimes": (
                "fit_2017_2018",
                "fit_2019_2020",
            ),
        }
    ),
    MappingProxyType(
        {
            "name": "leave_out_fit_2017_2018",
            "excluded_regime": "fit_2017_2018",
            "included_regimes": (
                "fit_2015_2016",
                "fit_2019_2020",
            ),
        }
    ),
    MappingProxyType(
        {
            "name": "leave_out_fit_2019_2020",
            "excluded_regime": "fit_2019_2020",
            "included_regimes": (
                "fit_2015_2016",
                "fit_2017_2018",
            ),
        }
    ),
)
REQUIRED_JACKKNIFE_VIEW_COUNT = 3
REQUIRED_REGRESSORS_PER_VIEW = 2
TOTAL_REGRESSORS_PER_CELL = (
    REQUIRED_JACKKNIFE_VIEW_COUNT
    * REQUIRED_REGRESSORS_PER_VIEW
)

TEMPORAL_JACKKNIFE_DIRECTION_RULE = (
    "within each leave-one-regime-out fit view, choose LONG or SHORT only "
    "when that direction has the unique higher predicted 0.5-pip net "
    "utility and the predicted utility is greater than zero; a row is "
    "eligible only when all three jackknife views choose the same direction"
)
TEMPORAL_JACKKNIFE_SCORE_RULE = (
    "for an eligible row, robust utility is the minimum predicted net pips "
    "for the agreed direction across the three leave-one-regime-out views"
)
TEMPORAL_JACKKNIFE_DISAGREEMENT_POLICY = "NO_TRADE"

SELECTION_CUTOFF_RULE = (
    "for each candidate budget, sort temporal-jackknife-utility-eligible "
    "selection rows by robust utility descending and row identity ascending; "
    "use the robust utility of the budget-th ranked row as the frozen cutoff"
)
CUTOFF_TIE_POLICY = (
    "all temporal-jackknife-utility-eligible rows whose robust utility is "
    "greater than or equal to the frozen cutoff are candidates; ties may "
    "exceed the nominal budget"
)
FORWARD_APPLICATION_RULE = (
    "apply the exact selection-derived robust-utility cutoff unchanged to "
    "validation and retrospective holdout using the same six frozen "
    "jackknife-view regressors; do not recompute a quantile, budget, view, "
    "window cutoff, or utility calibration"
)
TEMPORAL_JACKKNIFE_SELECTION_TIE_BREAK = tuple(
    PREDECESSOR_SELECTION_TIE_BREAK
)

FEATURE_CHANGE_AUTHORIZED = False
FINANCIAL_TARGET_CHANGE_AUTHORIZED = False
OUTER_CHRONOLOGY_CHANGE_AUTHORIZED = False
HGB_STRUCTURAL_CONFIG_CHANGE_AUTHORIZED = False
POSITIVE_UTILITY_REQUIREMENT_CHANGE_AUTHORIZED = False
JACKKNIFE_VIEW_WEIGHT_SEARCH_AUTHORIZED = False
JACKKNIFE_VIEW_FALLBACK_AUTHORIZED = False
DENSITY_ANCHOR_CHANGE_AUTHORIZED = False
MIN_DIRECTIONAL_CANDIDATE_COUNT_CHANGE_AUTHORIZED = False
STABILITY_SCREEN_CHANGE_AUTHORIZED = False
PER_WINDOW_FINANCIAL_GATE_CHANGE_AUTHORIZED = False
PER_WINDOW_CUTOFF_TUNING_AUTHORIZED = False
PER_WINDOW_UTILITY_RECALIBRATION_AUTHORIZED = False
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


def _split_payload(split: object) -> dict[str, object]:
    return {
        "name": str(getattr(split, "name")),
        "start": getattr(split, "start").isoformat(),
        "end_exclusive": (
            getattr(split, "end_exclusive").isoformat()
        ),
    }


def _fit_regime_payloads() -> list[dict[str, object]]:
    return [
        dict(window)
        for window in PREDECESSOR_FIT_REGIME_WINDOWS
    ]


def _jackknife_view_payloads() -> list[dict[str, object]]:
    return [
        {
            "name": str(view["name"]),
            "excluded_regime": str(view["excluded_regime"]),
            "included_regimes": list(view["included_regimes"]),
            "included_regime_count": 2,
            "excluded_regime_count": 1,
            "fit_year_count": 4,
        }
        for view in FIT_JACKKNIFE_VIEWS
    ]


def validate_temporal_jackknife_utility_predecessor_identity() -> None:
    if SOURCE_EXPERIMENT_ID != "EXP-20260924-049":
        raise ValueError(
            "EXP-050 predecessor experiment identity drift"
        )
    if SOURCE_RESULT_DECISION != "DEC-139":
        raise ValueError(
            "EXP-050 predecessor result decision drift"
        )
    if POST_RESULT_DIAGNOSTIC_DECISION != "DEC-140":
        raise ValueError(
            "EXP-050 predecessor diagnostic decision drift"
        )
    if SOURCE_MODEL_RUN_ID != 36029925264:
        raise ValueError(
            "EXP-050 predecessor model run id drift"
        )
    if SOURCE_EVIDENCE_FINGERPRINT != (
        PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT
    ):
        raise ValueError(
            "EXP-050 predecessor evidence fingerprint drift"
        )
    if ACCEPTED_MODEL_CANDIDATE_COUNT != 0:
        raise ValueError(
            "EXP-050 requires zero accepted predecessor candidates"
        )
    if TOTAL_VARIANT_COUNT != 54:
        raise ValueError(
            "EXP-050 predecessor total-variant count drift"
        )
    if UNAVAILABLE_BUDGET_VARIANT_COUNT != 31:
        raise ValueError(
            "EXP-050 predecessor unavailable-budget count drift"
        )
    if AGGREGATE_SELECTION_PASS_VARIANT_COUNT != 8:
        raise ValueError(
            "EXP-050 predecessor aggregate-pass count drift"
        )
    if BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT != 8:
        raise ValueError(
            "EXP-050 predecessor dual-stability count drift"
        )
    if SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED is not True:
        raise ValueError(
            "EXP-050 successor protocol source is not open"
        )
    if SUCCESSOR_RESULT_EXECUTION_AUTHORIZED is not False:
        raise ValueError(
            "EXP-050 requires predecessor successor execution closed"
        )
    if SUCCESSOR_MODEL_FIT_AUTHORIZED is not False:
        raise ValueError(
            "EXP-050 requires predecessor successor fit closed"
        )
    if LOWER_UTILITY_POSITIVITY_REQUIREMENT_AUTHORIZED is not False:
        raise ValueError(
            "EXP-050 forbids predecessor utility-threshold relaxation"
        )
    if RELAX_STABILITY_SHARE_AUTHORIZED is not False:
        raise ValueError(
            "EXP-050 forbids candidate-share relaxation"
        )
    if RELAX_STABILITY_FINANCIAL_AUTHORIZED is not False:
        raise ValueError(
            "EXP-050 forbids financial stability relaxation"
        )
    if REMOVE_2021_STABILITY_WINDOWS_AUTHORIZED is not False:
        raise ValueError(
            "EXP-050 forbids removal of 2021 stability windows"
        )

    if FIT_SPLIT.start.isoformat() != "2015-01-01":
        raise ValueError(
            "EXP-050 outer fit split start drift"
        )
    if FIT_SPLIT.end_exclusive.isoformat() != "2021-01-01":
        raise ValueError(
            "EXP-050 outer fit split end drift"
        )

    regimes = _fit_regime_payloads()
    if len(regimes) != 3:
        raise ValueError(
            "EXP-050 predecessor fit-regime count drift"
        )
    if tuple(str(row["name"]) for row in regimes) != (
        "fit_2015_2016",
        "fit_2017_2018",
        "fit_2019_2020",
    ):
        raise ValueError(
            "EXP-050 predecessor fit-regime names drift"
        )

    if len(FIT_JACKKNIFE_VIEWS) != REQUIRED_JACKKNIFE_VIEW_COUNT:
        raise ValueError(
            "EXP-050 jackknife view count drift"
        )
    seen_excluded: set[str] = set()
    for view in FIT_JACKKNIFE_VIEWS:
        excluded = str(view["excluded_regime"])
        included = tuple(
            str(value)
            for value in view["included_regimes"]
        )
        if excluded not in PREDECESSOR_REGIME_NAMES:
            raise ValueError(
                "EXP-050 excluded regime identity drift"
            )
        if len(included) != 2 or len(set(included)) != 2:
            raise ValueError(
                "EXP-050 jackknife included-regime count drift"
            )
        if excluded in included:
            raise ValueError(
                "EXP-050 jackknife view cannot include excluded regime"
            )
        if set(included) != (
            set(PREDECESSOR_REGIME_NAMES) - {excluded}
        ):
            raise ValueError(
                "EXP-050 jackknife included-regime identity drift"
            )
        seen_excluded.add(excluded)
    if seen_excluded != set(PREDECESSOR_REGIME_NAMES):
        raise ValueError(
            "EXP-050 jackknife exclusion coverage drift"
        )

    if tuple(CANDIDATE_BUDGET_ANCHORS) != (250, 500, 1000):
        raise ValueError(
            "EXP-050 density-anchor identity drift"
        )
    if MIN_DIRECTIONAL_CANDIDATES != 250:
        raise ValueError(
            "EXP-050 minimum directional candidate count drift"
        )
    if MIN_STABILITY_WINDOW_CANDIDATE_SHARE != 0.10:
        raise ValueError(
            "EXP-050 temporal stability share drift"
        )
    if tuple(STABILITY_WINDOW_REQUIREMENTS) != (
        "directional_candidate_share>=0.10",
        "total_net_pips>0",
        "mean_net_pips>0",
        "gross_positive_pips>absolute_gross_negative_pips",
    ):
        raise ValueError(
            "EXP-050 temporal stability requirements drift"
        )
    if FINANCIAL_TARGET_COLUMNS != (
        "long_net_pips_0p5",
        "short_net_pips_0p5",
    ):
        raise ValueError(
            "EXP-050 financial target identity drift"
        )
    if FINANCIAL_TARGET_SLIPPAGE_PIPS != 0.5:
        raise ValueError(
            "EXP-050 financial target cost drift"
        )
    if tuple(AUTHORIZED_MODEL_FAMILIES) != (
        "hist_gradient_boosting_regression",
    ):
        raise ValueError(
            "EXP-050 authorized model family drift"
        )
    if tuple(EXCLUDED_MODEL_FAMILIES) != (
        "logistic_regression",
        "hist_gradient_boosting_classifier",
    ):
        raise ValueError(
            "EXP-050 excluded model family drift"
        )

    if "greater than zero" not in PREDECESSOR_DIRECTION_RULE:
        raise ValueError(
            "EXP-050 predecessor positive-utility rule drift"
        )
    if "minimum predicted net pips" not in PREDECESSOR_SCORE_RULE:
        raise ValueError(
            "EXP-050 predecessor robust-utility rule drift"
        )


def temporal_jackknife_utility_protocol_payload() -> dict[str, object]:
    validate_temporal_jackknife_utility_predecessor_identity()

    return {
        "experiment_id": TEMPORAL_JACKKNIFE_UTILITY_EXPERIMENT_ID,
        "protocol_version": (
            TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_VERSION
        ),
        "protocol_decision": (
            TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_DECISION
        ),
        "predecessor": {
            "experiment_id": SOURCE_EXPERIMENT_ID,
            "result_decision": SOURCE_RESULT_DECISION,
            "diagnostic_decision": (
                POST_RESULT_DIAGNOSTIC_DECISION
            ),
            "diagnostic_classification": (
                PREDECESSOR_DIAGNOSTIC_CLASSIFICATION
            ),
            "diagnostic_merged_commit": DEC140_MERGED_COMMIT,
            "diagnostic_blob_sha": DEC140_DIAGNOSTIC_BLOB_SHA,
            "result_decision_blob_sha": (
                DEC139_RESULT_DECISION_BLOB_SHA
            ),
            "model_run_id": SOURCE_MODEL_RUN_ID,
            "result_evidence_fingerprint": (
                PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT
            ),
            "total_variant_count": TOTAL_VARIANT_COUNT,
            "unavailable_budget_variant_count": (
                UNAVAILABLE_BUDGET_VARIANT_COUNT
            ),
            "aggregate_selection_pass_variant_count": (
                AGGREGATE_SELECTION_PASS_VARIANT_COUNT
            ),
            "both_share_and_financial_reject_variant_count": (
                BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT
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
        "inputs": {
            "columns": list(MODEL_INPUT_COLUMNS),
            "column_count": len(MODEL_INPUT_COLUMNS),
            "feature_change_authorized": FEATURE_CHANGE_AUTHORIZED,
        },
        "financial_targets": {
            "columns": list(FINANCIAL_TARGET_COLUMNS),
            "slippage_pips_per_fill": (
                FINANCIAL_TARGET_SLIPPAGE_PIPS
            ),
            "target_change_authorized": (
                FINANCIAL_TARGET_CHANGE_AUTHORIZED
            ),
        },
        "chronology": {
            "splits": [
                _split_payload(split)
                for split in PROTOCOL_SPLITS
            ],
            "outer_fit_split": _split_payload(FIT_SPLIT),
            "predecessor_fit_regime_windows": (
                _fit_regime_payloads()
            ),
            "jackknife_fit_views": _jackknife_view_payloads(),
            "selection_split": _split_payload(SELECTION_SPLIT),
            "validation_split": _split_payload(VALIDATION_SPLIT),
            "retrospective_holdout_split": _split_payload(
                RETROSPECTIVE_HOLDOUT_SPLIT
            ),
            "outer_chronology_change_authorized": (
                OUTER_CHRONOLOGY_CHANGE_AUTHORIZED
            ),
            "no_refit_after_fit": True,
            "untouched_oos": False,
        },
        "model_family": {
            "authorized": list(AUTHORIZED_MODEL_FAMILIES),
            "excluded": list(EXCLUDED_MODEL_FAMILIES),
            "scikit_learn_version": SCIKIT_LEARN_VERSION,
            "estimator": "HistGradientBoostingRegressor",
            "regressor_config": dict(
                HIST_GRADIENT_BOOSTING_REGRESSION_CONFIG
            ),
            "required_jackknife_view_count": (
                REQUIRED_JACKKNIFE_VIEW_COUNT
            ),
            "regressors_per_view": (
                REQUIRED_REGRESSORS_PER_VIEW
            ),
            "total_regressors_per_cell": (
                TOTAL_REGRESSORS_PER_CELL
            ),
            "view_preprocessing": (
                "for each jackknife view and target, fit one median "
                "imputer only on the union of that view's two included "
                "fit-regime row sets; no standardization and no borrowing "
                "from the excluded fit regime"
            ),
            "hgb_structural_config_change_authorized": (
                HGB_STRUCTURAL_CONFIG_CHANGE_AUTHORIZED
            ),
            "logistic_reintroduction_authorized": (
                LOGISTIC_REINTRODUCTION_AUTHORIZED
            ),
            "classifier_fallback_authorized": (
                CLASSIFIER_FALLBACK_AUTHORIZED
            ),
        },
        "temporal_jackknife": {
            "construction": (
                "three deterministic leave-one-regime-out fit views; "
                "each view includes exactly two of the three frozen "
                "2015-2020 two-year fit regimes and excludes the third"
            ),
            "views": _jackknife_view_payloads(),
            "required_view_count": REQUIRED_JACKKNIFE_VIEW_COUNT,
            "all_views_required": True,
            "view_weight_search_authorized": (
                JACKKNIFE_VIEW_WEIGHT_SEARCH_AUTHORIZED
            ),
            "view_fallback_authorized": (
                JACKKNIFE_VIEW_FALLBACK_AUTHORIZED
            ),
        },
        "utility_consensus": {
            "required_view_count": REQUIRED_JACKKNIFE_VIEW_COUNT,
            "required_regressors_per_view": (
                REQUIRED_REGRESSORS_PER_VIEW
            ),
            "direction_rule": TEMPORAL_JACKKNIFE_DIRECTION_RULE,
            "score_rule": TEMPORAL_JACKKNIFE_SCORE_RULE,
            "disagreement_policy": (
                TEMPORAL_JACKKNIFE_DISAGREEMENT_POLICY
            ),
            "all_views_required": True,
            "positive_predicted_utility_required": True,
            "positive_utility_requirement_change_authorized": (
                POSITIVE_UTILITY_REQUIREMENT_CHANGE_AUTHORIZED
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
            "gate_scenarios": list(SELECTION_GATE_SCENARIOS),
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
            "per_window_cutoff_tuning_authorized": (
                PER_WINDOW_CUTOFF_TUNING_AUTHORIZED
            ),
            "per_window_utility_recalibration_authorized": (
                PER_WINDOW_UTILITY_RECALIBRATION_AUTHORIZED
            ),
            "tie_break": list(
                TEMPORAL_JACKKNIFE_SELECTION_TIE_BREAK
            ),
        },
        "validation": {
            "jackknife_views_source": "outer_fit_split",
            "cutoff_source": "selection",
            "recompute_cutoff_on_validation": False,
            "refit_on_validation": False,
            "gate_scenarios": list(VALIDATION_GATE_SCENARIOS),
            "diagnostic_scenarios": list(DIAGNOSTIC_SCENARIOS),
        },
        "retrospective_holdout": {
            "jackknife_views_source": "outer_fit_split",
            "cutoff_source": "selection",
            "recompute_cutoff_on_holdout": False,
            "refit_on_holdout": False,
            "gate_scenarios": list(HOLDOUT_GATE_SCENARIOS),
            "diagnostic_scenarios": list(DIAGNOSTIC_SCENARIOS),
            "evidence_is_retrospective": True,
        },
        "authorization": {
            "model_protocol_result_authorized": (
                MODEL_PROTOCOL_RESULT_AUTHORIZED
            ),
            "model_fit_authorized": MODEL_FIT_AUTHORIZED,
            "historical_result_execution_authorized": (
                HISTORICAL_RESULT_EXECUTION_AUTHORIZED
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


def temporal_jackknife_utility_protocol_fingerprint() -> str:
    return hashlib.sha256(
        _canonical_json(
            temporal_jackknife_utility_protocol_payload()
        )
    ).hexdigest()


__all__ = [
    "AUTHORIZED_MODEL_FAMILIES",
    "BROKER_MUTATION_AUTHORIZED",
    "CLASSIFIER_FALLBACK_AUTHORIZED",
    "CUTOFF_TIE_POLICY",
    "DEC139_RESULT_DECISION_BLOB_SHA",
    "DEC140_DIAGNOSTIC_BLOB_SHA",
    "DEC140_MERGED_COMMIT",
    "DEMO_ORDER_AUTHORIZED",
    "DENSITY_ANCHOR_CHANGE_AUTHORIZED",
    "EXCLUDED_MODEL_FAMILIES",
    "FEATURE_CHANGE_AUTHORIZED",
    "FINANCIAL_TARGET_CHANGE_AUTHORIZED",
    "FINANCIAL_TARGET_COLUMNS",
    "FINANCIAL_TARGET_SLIPPAGE_PIPS",
    "FIT_JACKKNIFE_VIEWS",
    "FORWARD_APPLICATION_RULE",
    "HGB_STRUCTURAL_CONFIG_CHANGE_AUTHORIZED",
    "HISTORICAL_RESULT_EXECUTION_AUTHORIZED",
    "HIST_GRADIENT_BOOSTING_REGRESSION_CONFIG",
    "JACKKNIFE_VIEW_FALLBACK_AUTHORIZED",
    "JACKKNIFE_VIEW_WEIGHT_SEARCH_AUTHORIZED",
    "LIVE_ORDER_AUTHORIZED",
    "LOGISTIC_REINTRODUCTION_AUTHORIZED",
    "MIN_DIRECTIONAL_CANDIDATE_COUNT_CHANGE_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "OUTER_CHRONOLOGY_CHANGE_AUTHORIZED",
    "PER_WINDOW_CUTOFF_TUNING_AUTHORIZED",
    "PER_WINDOW_FINANCIAL_GATE_CHANGE_AUTHORIZED",
    "PER_WINDOW_UTILITY_RECALIBRATION_AUTHORIZED",
    "POSITIVE_UTILITY_REQUIREMENT_CHANGE_AUTHORIZED",
    "PREDECESSOR_REGIME_NAMES",
    "PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT",
    "PRIOR_RESULT_INFORMED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "REQUIRED_JACKKNIFE_VIEW_COUNT",
    "REQUIRED_REGRESSORS_PER_VIEW",
    "SELECTION_CUTOFF_RULE",
    "SHADOW_AUTHORIZED",
    "STABILITY_SCREEN_CHANGE_AUTHORIZED",
    "TEMPORAL_JACKKNIFE_DIRECTION_RULE",
    "TEMPORAL_JACKKNIFE_DISAGREEMENT_POLICY",
    "TEMPORAL_JACKKNIFE_SCORE_RULE",
    "TEMPORAL_JACKKNIFE_SELECTION_TIE_BREAK",
    "TEMPORAL_JACKKNIFE_UTILITY_EXPERIMENT_ID",
    "TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_DECISION",
    "TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_VERSION",
    "TOTAL_REGRESSORS_PER_CELL",
    "TRADING_AUTHORIZED",
    "UNTOUCHED_OOS",
    "temporal_jackknife_utility_protocol_fingerprint",
    "temporal_jackknife_utility_protocol_payload",
    "validate_temporal_jackknife_utility_predecessor_identity",
]
