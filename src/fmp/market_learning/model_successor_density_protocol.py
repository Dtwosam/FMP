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
    SELECTION_TIE_BREAK,
    TARGET_CLASSES,
    TARGET_COLUMN,
    TARGET_SLIPPAGE_PIPS,
    VALIDATION_GATE_SCENARIOS,
    VALIDATION_SPLIT,
)
from .model_successor_cross_run_reproducibility import (
    CROSS_RUN_REPRODUCIBILITY_DECISION,
    EXP046_ACCEPTED_MODEL_CANDIDATE_COUNT,
    EXP046_EVIDENCE_FINGERPRINT,
    LOGISTIC_FAMILY_REUSE_FOR_RESULT_EXECUTION_AUTHORIZED,
)
from .model_successor_stability_protocol import (
    MIN_STABILITY_WINDOW_CANDIDATE_SHARE,
    STABILITY_WINDOW_REQUIREMENTS,
    TEMPORAL_STABILITY_WINDOWS,
)


DENSITY_SUCCESSOR_EXPERIMENT_ID = "EXP-20260924-047"
DENSITY_PROTOCOL_VERSION = "fmp-exp047-hgb-density-protocol-v1"
DENSITY_PROTOCOL_DECISION = "DEC-113"

DEC111_MERGED_COMMIT = (
    "0fca0ec79f75c07a9cbabaae57ddaee6cafac651"
)
DEC112_MERGED_COMMIT = (
    "42c6a20388a406a0c350d9ea9e0cfdb64b6d7fbc"
)
DEC112_REPRODUCIBILITY_BLOB_SHA = (
    "cf4f6ee1a7d387c3a48269a9f6aea8212dd56b1b"
)
PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT = (
    "499c91e4508f07bf8a637657969175fb"
    "ba8e93d07236b94ded06ae884b386214"
)

PREDECESSOR_HGB_VARIANT_COUNT = 54
PREDECESSOR_HGB_COUNT_GATE_PASS_COUNT = 23
PREDECESSOR_HGB_POSITIVE_FINANCIAL_SIGN_COUNT = 13
PREDECESSOR_HGB_AGGREGATE_GATE_PASS_COUNT = 1
PREDECESSOR_HGB_POSITIVE_BUT_LOW_COUNT = 12

PRIOR_RESULT_INFORMED = True
UNTOUCHED_OOS = False

AUTHORIZED_MODEL_FAMILIES = ("hist_gradient_boosting",)
EXCLUDED_MODEL_FAMILIES = ("logistic_regression",)
LOGISTIC_EXCLUSION_REASON = (
    "DEC-112 family-availability reproducibility failure"
)

CANDIDATE_BUDGET_ANCHORS = (250, 500, 1000)
DIRECTIONAL_CONFIDENCE_DEFINITION = (
    "probability of the unique top class when that class is LONG or SHORT"
)
SELECTION_CUTOFF_RULE = (
    "for each candidate budget, sort selection rows with a unique "
    "directional top class by directional confidence descending and "
    "row identity ascending; use the directional confidence of the "
    "budget-th ranked row as the frozen cutoff"
)
CUTOFF_TIE_POLICY = (
    "all rows whose directional confidence is greater than or equal "
    "to the frozen cutoff are candidates; ties may therefore produce "
    "more candidates than the budget anchor"
)
FORWARD_APPLICATION_RULE = (
    "apply the exact selection-derived numeric cutoff unchanged to "
    "validation and retrospective holdout; do not recompute a quantile "
    "or budget on later splits"
)

TEMPORAL_STABILITY_WINDOWS = tuple(
    MappingProxyType(dict(window))
    for window in TEMPORAL_STABILITY_WINDOWS
)

DENSITY_SELECTION_TIE_BREAK = (
    *SELECTION_TIE_BREAK,
    "candidate_budget_anchor_ascending",
)

MODEL_CONFIG_CHANGE_AUTHORIZED = False
FEATURE_CHANGE_AUTHORIZED = False
TARGET_CHANGE_AUTHORIZED = False
DATA_SPLIT_CHANGE_AUTHORIZED = False
MIN_DIRECTIONAL_CANDIDATE_COUNT_CHANGE_AUTHORIZED = False
STABILITY_SCREEN_CHANGE_AUTHORIZED = False
LOGISTIC_REINTRODUCTION_AUTHORIZED = False

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


def validate_density_predecessor_identity() -> None:
    if CROSS_RUN_REPRODUCIBILITY_DECISION != "DEC-112":
        raise ValueError(
            "EXP-047 predecessor reproducibility decision drift"
        )
    if EXP046_EVIDENCE_FINGERPRINT != (
        PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT
    ):
        raise ValueError(
            "EXP-047 predecessor evidence fingerprint drift"
        )
    if EXP046_ACCEPTED_MODEL_CANDIDATE_COUNT != 0:
        raise ValueError(
            "EXP-047 requires zero accepted predecessor candidates"
        )
    if (
        LOGISTIC_FAMILY_REUSE_FOR_RESULT_EXECUTION_AUTHORIZED
        is not False
    ):
        raise ValueError(
            "EXP-047 requires logistic result-producing reuse closed"
        )
    if (
        PREDECESSOR_HGB_VARIANT_COUNT != 54
        or PREDECESSOR_HGB_COUNT_GATE_PASS_COUNT != 23
        or PREDECESSOR_HGB_POSITIVE_FINANCIAL_SIGN_COUNT != 13
        or PREDECESSOR_HGB_AGGREGATE_GATE_PASS_COUNT != 1
        or PREDECESSOR_HGB_POSITIVE_BUT_LOW_COUNT != 12
    ):
        raise ValueError(
            "EXP-047 predecessor HGB diagnostic accounting drift"
        )
    if MIN_DIRECTIONAL_CANDIDATES != 250:
        raise ValueError(
            "EXP-047 minimum directional candidate count drift"
        )
    if MIN_STABILITY_WINDOW_CANDIDATE_SHARE != 0.10:
        raise ValueError(
            "EXP-047 temporal stability share drift"
        )


def density_protocol_payload() -> dict[str, object]:
    validate_density_predecessor_identity()

    return {
        "experiment_id": DENSITY_SUCCESSOR_EXPERIMENT_ID,
        "protocol_version": DENSITY_PROTOCOL_VERSION,
        "protocol_decision": DENSITY_PROTOCOL_DECISION,
        "predecessor": {
            "experiment_id": "EXP-20260923-046",
            "result_decision": "DEC-111",
            "reproducibility_decision": (
                CROSS_RUN_REPRODUCIBILITY_DECISION
            ),
            "dec111_merged_commit": DEC111_MERGED_COMMIT,
            "dec112_merged_commit": DEC112_MERGED_COMMIT,
            "dec112_reproducibility_blob_sha": (
                DEC112_REPRODUCIBILITY_BLOB_SHA
            ),
            "result_evidence_fingerprint": (
                PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT
            ),
            "accepted_model_candidate_count": 0,
            "hgb_density_diagnostic": {
                "evaluated_variant_count": (
                    PREDECESSOR_HGB_VARIANT_COUNT
                ),
                "count_gate_pass_count": (
                    PREDECESSOR_HGB_COUNT_GATE_PASS_COUNT
                ),
                "positive_financial_sign_count": (
                    PREDECESSOR_HGB_POSITIVE_FINANCIAL_SIGN_COUNT
                ),
                "aggregate_gate_pass_count": (
                    PREDECESSOR_HGB_AGGREGATE_GATE_PASS_COUNT
                ),
                "positive_but_low_count_count": (
                    PREDECESSOR_HGB_POSITIVE_BUT_LOW_COUNT
                ),
            },
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
        "target": {
            "column": TARGET_COLUMN,
            "slippage_pips": TARGET_SLIPPAGE_PIPS,
            "classes": list(TARGET_CLASSES),
            "target_change_authorized": TARGET_CHANGE_AUTHORIZED,
        },
        "chronology": {
            "splits": [
                _split_payload(split)
                for split in PROTOCOL_SPLITS
            ],
            "fit_split": _split_payload(FIT_SPLIT),
            "selection_split": _split_payload(SELECTION_SPLIT),
            "validation_split": _split_payload(VALIDATION_SPLIT),
            "retrospective_holdout_split": _split_payload(
                RETROSPECTIVE_HOLDOUT_SPLIT
            ),
            "data_split_change_authorized": (
                DATA_SPLIT_CHANGE_AUTHORIZED
            ),
            "no_refit_after_fit": True,
            "untouched_oos": False,
        },
        "model_families": {
            "authorized": list(AUTHORIZED_MODEL_FAMILIES),
            "excluded": list(EXCLUDED_MODEL_FAMILIES),
            "logistic_exclusion_reason": (
                LOGISTIC_EXCLUSION_REASON
            ),
            "scikit_learn_version": SCIKIT_LEARN_VERSION,
            "hist_gradient_boosting": dict(
                HIST_GRADIENT_BOOSTING_CONFIG
            ),
            "model_config_change_authorized": (
                MODEL_CONFIG_CHANGE_AUTHORIZED
            ),
            "logistic_reintroduction_authorized": (
                LOGISTIC_REINTRODUCTION_AUTHORIZED
            ),
        },
        "selection": {
            "candidate_budget_anchors": list(
                CANDIDATE_BUDGET_ANCHORS
            ),
            "directional_confidence_definition": (
                DIRECTIONAL_CONFIDENCE_DEFINITION
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
            "gate_scenarios": list(
                SELECTION_GATE_SCENARIOS
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
            },
            "tie_break": list(
                DENSITY_SELECTION_TIE_BREAK
            ),
        },
        "validation": {
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


def density_protocol_fingerprint() -> str:
    return hashlib.sha256(
        _canonical_json(density_protocol_payload())
    ).hexdigest()


__all__ = [
    "AUTHORIZED_MODEL_FAMILIES",
    "BROKER_MUTATION_AUTHORIZED",
    "CANDIDATE_BUDGET_ANCHORS",
    "CUTOFF_TIE_POLICY",
    "DATA_SPLIT_CHANGE_AUTHORIZED",
    "DEMO_ORDER_AUTHORIZED",
    "DENSITY_PROTOCOL_DECISION",
    "DENSITY_PROTOCOL_VERSION",
    "DENSITY_SELECTION_TIE_BREAK",
    "DENSITY_SUCCESSOR_EXPERIMENT_ID",
    "DIRECTIONAL_CONFIDENCE_DEFINITION",
    "EXCLUDED_MODEL_FAMILIES",
    "FEATURE_CHANGE_AUTHORIZED",
    "FORWARD_APPLICATION_RULE",
    "HISTORICAL_RESULT_EXECUTION_AUTHORIZED",
    "LIVE_ORDER_AUTHORIZED",
    "LOGISTIC_EXCLUSION_REASON",
    "LOGISTIC_REINTRODUCTION_AUTHORIZED",
    "MIN_DIRECTIONAL_CANDIDATE_COUNT_CHANGE_AUTHORIZED",
    "MODEL_CONFIG_CHANGE_AUTHORIZED",
    "MODEL_FIT_AUTHORIZED",
    "MODEL_PROTOCOL_RESULT_AUTHORIZED",
    "PREDECESSOR_HGB_AGGREGATE_GATE_PASS_COUNT",
    "PREDECESSOR_HGB_COUNT_GATE_PASS_COUNT",
    "PREDECESSOR_HGB_POSITIVE_BUT_LOW_COUNT",
    "PREDECESSOR_HGB_POSITIVE_FINANCIAL_SIGN_COUNT",
    "PREDECESSOR_HGB_VARIANT_COUNT",
    "PREDECESSOR_RESULT_EVIDENCE_FINGERPRINT",
    "PRIOR_RESULT_INFORMED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "SELECTION_CUTOFF_RULE",
    "SHADOW_AUTHORIZED",
    "STABILITY_SCREEN_CHANGE_AUTHORIZED",
    "TARGET_CHANGE_AUTHORIZED",
    "TEMPORAL_STABILITY_WINDOWS",
    "TRADING_AUTHORIZED",
    "UNTOUCHED_OOS",
    "density_protocol_fingerprint",
    "density_protocol_payload",
    "validate_density_predecessor_identity",
]
