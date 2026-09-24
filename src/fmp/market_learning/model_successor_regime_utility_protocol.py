from __future__ import annotations

import hashlib
import json
from types import MappingProxyType

from .model_protocol import (
    DIAGNOSTIC_SCENARIOS,
    FIT_SPLIT,
    GATE_REQUIREMENTS,
    HIST_GRADIENT_BOOSTING_CONFIG,
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
    TARGET_COLUMN,
    TARGET_SLIPPAGE_PIPS,
    VALIDATION_GATE_SCENARIOS,
    VALIDATION_SPLIT,
)
from .model_successor_density_protocol import (
    CANDIDATE_BUDGET_ANCHORS,
)
from .model_successor_regime_consensus_post_result_diagnostics import (
    ACCEPTED_MODEL_CANDIDATE_COUNT,
    AGGREGATE_SELECTION_PASS_VARIANT_COUNT,
    CANDIDATE_SHARE_REJECT_VARIANT_COUNT,
    FINANCIAL_ONLY_REJECT_VARIANT_COUNT,
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
    WINDOW_FINANCIAL_REJECT_VARIANT_COUNT,
)
from .model_successor_regime_consensus_protocol import (
    FIT_REGIME_WINDOWS as PREDECESSOR_FIT_REGIME_WINDOWS,
)
from .model_successor_stability_protocol import (
    MIN_STABILITY_WINDOW_CANDIDATE_SHARE,
    STABILITY_WINDOW_REQUIREMENTS,
    TEMPORAL_STABILITY_WINDOWS,
)
from .outcomes import OUTCOME_COLUMNS


REGIME_UTILITY_EXPERIMENT_ID = "EXP-20260924-049"
REGIME_UTILITY_PROTOCOL_VERSION = (
    "fmp-exp049-regime-utility-protocol-v1"
)
REGIME_UTILITY_PROTOCOL_DECISION = "DEC-132"

DEC131_MERGED_COMMIT = (
    "c07127c9651818b3dea817976a0e87ea76765f38"
)
DEC131_DIAGNOSTIC_BLOB_SHA = (
    "165ab1e0e10a9fb6453ad0880ea1df97d0a35fa8"
)
PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT = (
    "acd3a9d7708c345b05082026de9eecc5"
    "15abb9090a901126034e91173eb30647"
)
PREDECESSOR_DIAGNOSTIC_CLASSIFICATION = (
    "WINDOW_FINANCIAL_INSTABILITY_DOMINANT"
)

PRIOR_RESULT_INFORMED = True
UNTOUCHED_OOS = False

AUTHORIZED_MODEL_FAMILIES = (
    "hist_gradient_boosting_regression",
)
EXCLUDED_MODEL_FAMILIES = (
    "logistic_regression",
    "hist_gradient_boosting_classifier",
)

FINANCIAL_TARGET_COLUMNS = (
    "long_net_pips_0p5",
    "short_net_pips_0p5",
)
FINANCIAL_TARGET_SLIPPAGE_PIPS = 0.5
PREDECESSOR_CLASS_TARGET = TARGET_COLUMN
PREDECESSOR_CLASS_TARGET_REPLACED = True
FURTHER_TARGET_CHANGE_AUTHORIZED = False

FIT_REGIME_WINDOWS = tuple(
    MappingProxyType(dict(window))
    for window in PREDECESSOR_FIT_REGIME_WINDOWS
)
REQUIRED_REGIME_MODEL_COUNT = 3
REQUIRED_REGRESSORS_PER_REGIME = 2
TOTAL_REGRESSORS_PER_CELL = (
    REQUIRED_REGIME_MODEL_COUNT
    * REQUIRED_REGRESSORS_PER_REGIME
)

HIST_GRADIENT_BOOSTING_REGRESSION_CONFIG = MappingProxyType(
    {
        "loss": "squared_error",
        "learning_rate": HIST_GRADIENT_BOOSTING_CONFIG[
            "learning_rate"
        ],
        "max_iter": HIST_GRADIENT_BOOSTING_CONFIG["max_iter"],
        "max_leaf_nodes": HIST_GRADIENT_BOOSTING_CONFIG[
            "max_leaf_nodes"
        ],
        "max_depth": HIST_GRADIENT_BOOSTING_CONFIG["max_depth"],
        "min_samples_leaf": HIST_GRADIENT_BOOSTING_CONFIG[
            "min_samples_leaf"
        ],
        "l2_regularization": HIST_GRADIENT_BOOSTING_CONFIG[
            "l2_regularization"
        ],
        "max_features": HIST_GRADIENT_BOOSTING_CONFIG[
            "max_features"
        ],
        "max_bins": HIST_GRADIENT_BOOSTING_CONFIG["max_bins"],
        "early_stopping": HIST_GRADIENT_BOOSTING_CONFIG[
            "early_stopping"
        ],
        "warm_start": HIST_GRADIENT_BOOSTING_CONFIG[
            "warm_start"
        ],
        "random_state": HIST_GRADIENT_BOOSTING_CONFIG[
            "random_state"
        ],
    }
)

REGIME_UTILITY_DIRECTION_RULE = (
    "within each fit regime, choose LONG or SHORT only when that "
    "direction has the unique higher predicted 0.5-pip net utility "
    "and the predicted utility is greater than zero; a row is eligible "
    "only when all three fit regimes choose the same direction"
)
REGIME_UTILITY_SCORE_RULE = (
    "for an eligible row, robust utility is the minimum predicted net pips "
    "for the agreed direction across the three fit regimes"
)
REGIME_UTILITY_DISAGREEMENT_POLICY = "NO_TRADE"

SELECTION_CUTOFF_RULE = (
    "for each candidate budget, sort regime-utility-eligible selection "
    "rows by robust utility descending and row identity ascending; use "
    "the robust utility of the budget-th ranked row as the frozen cutoff"
)
CUTOFF_TIE_POLICY = (
    "all regime-utility-eligible rows whose robust utility is greater "
    "than or equal to the frozen cutoff are candidates; ties may exceed "
    "the nominal budget"
)
FORWARD_APPLICATION_RULE = (
    "apply the exact selection-derived robust-utility cutoff unchanged "
    "to validation and retrospective holdout using the same six frozen "
    "regressors; do not recompute a quantile, budget, window cutoff, or "
    "utility calibration"
)
REGIME_UTILITY_SELECTION_TIE_BREAK = (
    "higher_total_net_pips_0p5",
    "higher_directional_candidate_count",
    "smaller_candidate_budget_anchor",
)

FEATURE_CHANGE_AUTHORIZED = False
OUTER_CHRONOLOGY_CHANGE_AUTHORIZED = False
HGB_STRUCTURAL_CONFIG_CHANGE_AUTHORIZED = False
DENSITY_ANCHOR_CHANGE_AUTHORIZED = False
MIN_DIRECTIONAL_CANDIDATE_COUNT_CHANGE_AUTHORIZED = False
STABILITY_SCREEN_CHANGE_AUTHORIZED = False
PER_WINDOW_FINANCIAL_GATE_CHANGE_AUTHORIZED = False
LOGISTIC_REINTRODUCTION_AUTHORIZED = False
CLASSIFIER_FALLBACK_AUTHORIZED = False
PER_WINDOW_CUTOFF_TUNING_AUTHORIZED = False
PER_WINDOW_UTILITY_RECALIBRATION_AUTHORIZED = False

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


def validate_regime_utility_predecessor_identity() -> None:
    if SOURCE_EXPERIMENT_ID != "EXP-20260924-048":
        raise ValueError(
            "EXP-049 predecessor experiment identity drift"
        )
    if SOURCE_RESULT_DECISION != "DEC-130":
        raise ValueError(
            "EXP-049 predecessor result decision drift"
        )
    if POST_RESULT_DIAGNOSTIC_DECISION != "DEC-131":
        raise ValueError(
            "EXP-049 predecessor diagnostic decision drift"
        )
    if SOURCE_MODEL_RUN_ID != 36006524422:
        raise ValueError(
            "EXP-049 predecessor model run id drift"
        )
    if SOURCE_EVIDENCE_FINGERPRINT != (
        PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT
    ):
        raise ValueError(
            "EXP-049 predecessor evidence fingerprint drift"
        )
    if ACCEPTED_MODEL_CANDIDATE_COUNT != 0:
        raise ValueError(
            "EXP-049 requires zero accepted predecessor candidates"
        )
    if AGGREGATE_SELECTION_PASS_VARIANT_COUNT != 17:
        raise ValueError(
            "EXP-049 predecessor aggregate-pass count drift"
        )
    if WINDOW_FINANCIAL_REJECT_VARIANT_COUNT != 17:
        raise ValueError(
            "EXP-049 predecessor financial-window count drift"
        )
    if CANDIDATE_SHARE_REJECT_VARIANT_COUNT != 13:
        raise ValueError(
            "EXP-049 predecessor share-reject count drift"
        )
    if FINANCIAL_ONLY_REJECT_VARIANT_COUNT != 4:
        raise ValueError(
            "EXP-049 predecessor financial-only count drift"
        )
    if SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED is not True:
        raise ValueError(
            "EXP-049 successor protocol source is not open"
        )
    if SUCCESSOR_RESULT_EXECUTION_AUTHORIZED is not False:
        raise ValueError(
            "EXP-049 requires predecessor successor execution closed"
        )
    if SUCCESSOR_MODEL_FIT_AUTHORIZED is not False:
        raise ValueError(
            "EXP-049 requires predecessor successor fit closed"
        )

    if RELAX_STABILITY_SHARE_AUTHORIZED is not False:
        raise ValueError(
            "EXP-049 forbids candidate-share relaxation"
        )
    if RELAX_STABILITY_FINANCIAL_AUTHORIZED is not False:
        raise ValueError(
            "EXP-049 forbids financial stability relaxation"
        )
    if REMOVE_2021_STABILITY_WINDOWS_AUTHORIZED is not False:
        raise ValueError(
            "EXP-049 forbids removal of 2021 stability windows"
        )

    if FIT_SPLIT.start.isoformat() != "2015-01-01":
        raise ValueError("EXP-049 fit split start drift")
    if FIT_SPLIT.end_exclusive.isoformat() != "2021-01-01":
        raise ValueError("EXP-049 fit split end drift")

    windows = [dict(window) for window in FIT_REGIME_WINDOWS]
    if len(windows) != REQUIRED_REGIME_MODEL_COUNT:
        raise ValueError("EXP-049 fit-regime window count drift")
    if windows[0]["start"] != FIT_SPLIT.start.isoformat():
        raise ValueError("EXP-049 first fit-regime start drift")
    if (
        windows[-1]["end_exclusive"]
        != FIT_SPLIT.end_exclusive.isoformat()
    ):
        raise ValueError("EXP-049 final fit-regime end drift")
    for previous, current in zip(windows, windows[1:]):
        if previous["end_exclusive"] != current["start"]:
            raise ValueError(
                "EXP-049 fit-regime windows must be contiguous"
            )

    if tuple(CANDIDATE_BUDGET_ANCHORS) != (250, 500, 1000):
        raise ValueError("EXP-049 density-anchor identity drift")
    if MIN_DIRECTIONAL_CANDIDATES != 250:
        raise ValueError(
            "EXP-049 minimum directional candidate count drift"
        )
    if MIN_STABILITY_WINDOW_CANDIDATE_SHARE != 0.10:
        raise ValueError(
            "EXP-049 temporal stability share drift"
        )
    if tuple(STABILITY_WINDOW_REQUIREMENTS) != (
        "directional_candidate_share>=0.10",
        "total_net_pips>0",
        "mean_net_pips>0",
        "gross_positive_pips>absolute_gross_negative_pips",
    ):
        raise ValueError(
            "EXP-049 temporal financial stability requirements drift"
        )

    if TARGET_SLIPPAGE_PIPS != FINANCIAL_TARGET_SLIPPAGE_PIPS:
        raise ValueError("EXP-049 target slippage identity drift")
    if any(
        column not in OUTCOME_COLUMNS
        for column in FINANCIAL_TARGET_COLUMNS
    ):
        raise ValueError(
            "EXP-049 financial target column identity drift"
        )

    structural_keys = (
        "learning_rate",
        "max_iter",
        "max_leaf_nodes",
        "max_depth",
        "min_samples_leaf",
        "l2_regularization",
        "max_features",
        "max_bins",
        "early_stopping",
        "warm_start",
        "random_state",
    )
    for key in structural_keys:
        if (
            HIST_GRADIENT_BOOSTING_REGRESSION_CONFIG[key]
            != HIST_GRADIENT_BOOSTING_CONFIG[key]
        ):
            raise ValueError(
                "EXP-049 HGB structural configuration drift"
            )


def regime_utility_protocol_payload() -> dict[str, object]:
    validate_regime_utility_predecessor_identity()

    return {
        "experiment_id": REGIME_UTILITY_EXPERIMENT_ID,
        "protocol_version": REGIME_UTILITY_PROTOCOL_VERSION,
        "protocol_decision": REGIME_UTILITY_PROTOCOL_DECISION,
        "predecessor": {
            "experiment_id": SOURCE_EXPERIMENT_ID,
            "result_decision": SOURCE_RESULT_DECISION,
            "diagnostic_decision": (
                POST_RESULT_DIAGNOSTIC_DECISION
            ),
            "diagnostic_classification": (
                PREDECESSOR_DIAGNOSTIC_CLASSIFICATION
            ),
            "diagnostic_merged_commit": DEC131_MERGED_COMMIT,
            "diagnostic_blob_sha": DEC131_DIAGNOSTIC_BLOB_SHA,
            "model_run_id": SOURCE_MODEL_RUN_ID,
            "result_evidence_fingerprint": (
                PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT
            ),
            "aggregate_selection_pass_variant_count": (
                AGGREGATE_SELECTION_PASS_VARIANT_COUNT
            ),
            "window_financial_reject_variant_count": (
                WINDOW_FINANCIAL_REJECT_VARIANT_COUNT
            ),
            "candidate_share_reject_variant_count": (
                CANDIDATE_SHARE_REJECT_VARIANT_COUNT
            ),
            "financial_only_reject_variant_count": (
                FINANCIAL_ONLY_REJECT_VARIANT_COUNT
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
            "predecessor_class_target": PREDECESSOR_CLASS_TARGET,
            "predecessor_class_target_replaced": (
                PREDECESSOR_CLASS_TARGET_REPLACED
            ),
            "change_rationale": (
                "DEC-131 found per-window financial-sign instability "
                "in every aggregate-passing EXP-048 variant"
            ),
            "further_target_change_authorized": (
                FURTHER_TARGET_CHANGE_AUTHORIZED
            ),
        },
        "chronology": {
            "splits": [
                _split_payload(split)
                for split in PROTOCOL_SPLITS
            ],
            "outer_fit_split": _split_payload(FIT_SPLIT),
            "fit_regime_windows": [
                dict(window)
                for window in FIT_REGIME_WINDOWS
            ],
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
            "required_fit_regime_count": (
                REQUIRED_REGIME_MODEL_COUNT
            ),
            "regressors_per_regime": (
                REQUIRED_REGRESSORS_PER_REGIME
            ),
            "total_regressors_per_cell": (
                TOTAL_REGRESSORS_PER_CELL
            ),
            "preprocessing": (
                "fit each regime/target median imputer only on its "
                "own fit-regime rows; no standardization"
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
        "regime_utility_consensus": {
            "required_regime_model_count": (
                REQUIRED_REGIME_MODEL_COUNT
            ),
            "required_regressors_per_regime": (
                REQUIRED_REGRESSORS_PER_REGIME
            ),
            "direction_rule": REGIME_UTILITY_DIRECTION_RULE,
            "score_rule": REGIME_UTILITY_SCORE_RULE,
            "disagreement_policy": (
                REGIME_UTILITY_DISAGREEMENT_POLICY
            ),
            "all_regimes_required": True,
            "positive_predicted_utility_required": True,
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
            "forward_application_rule": (
                FORWARD_APPLICATION_RULE
            ),
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
                REGIME_UTILITY_SELECTION_TIE_BREAK
            ),
        },
        "validation": {
            "models_source": "fit_regime_windows",
            "cutoff_source": "selection",
            "recompute_cutoff_on_validation": False,
            "gate_scenarios": list(
                VALIDATION_GATE_SCENARIOS
            ),
            "diagnostic_scenarios": list(
                DIAGNOSTIC_SCENARIOS
            ),
        },
        "retrospective_holdout": {
            "models_source": "fit_regime_windows",
            "cutoff_source": "selection",
            "recompute_cutoff_on_holdout": False,
            "gate_scenarios": list(
                HOLDOUT_GATE_SCENARIOS
            ),
            "diagnostic_scenarios": list(
                DIAGNOSTIC_SCENARIOS
            ),
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


def regime_utility_protocol_fingerprint() -> str:
    return hashlib.sha256(
        _canonical_json(regime_utility_protocol_payload())
    ).hexdigest()


__all__ = [
    "AUTHORIZED_MODEL_FAMILIES",
    "BROKER_MUTATION_AUTHORIZED",
    "CANDIDATE_BUDGET_ANCHORS",
    "CLASSIFIER_FALLBACK_AUTHORIZED",
    "CUTOFF_TIE_POLICY",
    "DEC131_DIAGNOSTIC_BLOB_SHA",
    "DEC131_MERGED_COMMIT",
    "DEMO_ORDER_AUTHORIZED",
    "DENSITY_ANCHOR_CHANGE_AUTHORIZED",
    "EXCLUDED_MODEL_FAMILIES",
    "FEATURE_CHANGE_AUTHORIZED",
    "FINANCIAL_TARGET_COLUMNS",
    "FINANCIAL_TARGET_SLIPPAGE_PIPS",
    "FIT_REGIME_WINDOWS",
    "FORWARD_APPLICATION_RULE",
    "FURTHER_TARGET_CHANGE_AUTHORIZED",
    "HGB_STRUCTURAL_CONFIG_CHANGE_AUTHORIZED",
    "HISTORICAL_RESULT_EXECUTION_AUTHORIZED",
    "HIST_GRADIENT_BOOSTING_REGRESSION_CONFIG",
    "LIVE_ORDER_AUTHORIZED",
    "LOGISTIC_REINTRODUCTION_AUTHORIZED",
    "MIN_DIRECTIONAL_CANDIDATE_COUNT_CHANGE_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "OUTER_CHRONOLOGY_CHANGE_AUTHORIZED",
    "PER_WINDOW_CUTOFF_TUNING_AUTHORIZED",
    "PER_WINDOW_FINANCIAL_GATE_CHANGE_AUTHORIZED",
    "PER_WINDOW_UTILITY_RECALIBRATION_AUTHORIZED",
    "PREDECESSOR_CLASS_TARGET",
    "PREDECESSOR_CLASS_TARGET_REPLACED",
    "PREDECESSOR_DIAGNOSTIC_CLASSIFICATION",
    "PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT",
    "PRIOR_RESULT_INFORMED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "REGIME_UTILITY_DIRECTION_RULE",
    "REGIME_UTILITY_DISAGREEMENT_POLICY",
    "REGIME_UTILITY_EXPERIMENT_ID",
    "REGIME_UTILITY_PROTOCOL_DECISION",
    "REGIME_UTILITY_PROTOCOL_VERSION",
    "REGIME_UTILITY_SCORE_RULE",
    "REGIME_UTILITY_SELECTION_TIE_BREAK",
    "REQUIRED_REGIME_MODEL_COUNT",
    "REQUIRED_REGRESSORS_PER_REGIME",
    "SELECTION_CUTOFF_RULE",
    "SHADOW_AUTHORIZED",
    "STABILITY_SCREEN_CHANGE_AUTHORIZED",
    "TOTAL_REGRESSORS_PER_CELL",
    "TRADING_AUTHORIZED",
    "UNTOUCHED_OOS",
    "regime_utility_protocol_fingerprint",
    "regime_utility_protocol_payload",
    "validate_regime_utility_predecessor_identity",
]
