from __future__ import annotations


POST_RESULT_DIAGNOSTIC_DECISION = "DEC-103"
SOURCE_RESULT_DECISION = "DEC-102"
SOURCE_EXPERIMENT_ID = "EXP-20260923-045"
SOURCE_MODEL_RUN_ID = 35911916239
SOURCE_MODEL_HEAD_SHA = (
    "6d42a5053c5f2f696071715640dab24973a40517"
)
SOURCE_EVIDENCE_FINGERPRINT = (
    "3e0ebac02dbba690b4c03dd10c3fdd30"
    "c5eb0d6356b881e38f9a3527f0135c55"
)

EVALUATED_VARIANT_COUNT = 90
FULL_SELECTION_GATE_PASS_COUNT = 1
POSITIVE_FINANCIAL_SIGNS_VARIANT_COUNT = 26
POSITIVE_FINANCIAL_SIGNS_LOW_COUNT_VARIANT_COUNT = 25
DIRECTIONAL_COUNT_GATE_PASS_COUNT = 37
DIRECTIONAL_COUNT_PASS_FINANCIAL_FAIL_COUNT = 36

SELECTED_SYMBOL = "GBPUSD"
SELECTED_TIMEFRAME = "5m"
SELECTED_HORIZON_MINUTES = 240
SELECTED_MODEL_FAMILY = "hist_gradient_boosting"
SELECTED_CONFIDENCE_THRESHOLD = 0.6

SELECTION_DIRECTIONAL_CANDIDATE_COUNT = 460
SELECTION_DIRECTIONAL_CANDIDATE_RATE = (
    0.002188475298774454
)
SELECTION_MEAN_NET_PIPS = 5.116739130434755
SELECTION_TOTAL_NET_PIPS = 2353.6999999999875

VALIDATION_DIRECTIONAL_CANDIDATE_COUNT = 83
VALIDATION_DIRECTIONAL_CANDIDATE_RATE = (
    0.0003943367540858989
)
VALIDATION_MEAN_NET_PIPS = -16.83734939759037
VALIDATION_TOTAL_NET_PIPS = -1397.5000000000007

VALIDATION_TO_SELECTION_CANDIDATE_COUNT_RATIO = (
    VALIDATION_DIRECTIONAL_CANDIDATE_COUNT
    / SELECTION_DIRECTIONAL_CANDIDATE_COUNT
)
VALIDATION_TO_SELECTION_CANDIDATE_RATE_RATIO = (
    VALIDATION_DIRECTIONAL_CANDIDATE_RATE
    / SELECTION_DIRECTIONAL_CANDIDATE_RATE
)

LOGISTIC_NONCONVERGENCE_CELL_COUNT = 6
ACCEPTED_MODEL_CANDIDATE_COUNT = 0

MIN_DIRECTIONAL_CANDIDATE_COUNT = 250
RELAX_MIN_DIRECTIONAL_CANDIDATE_COUNT_AUTHORIZED = False
PROMOTE_LOW_COUNT_POSITIVE_VARIANTS_AUTHORIZED = False
EXP045_RERUN_AUTHORIZED = False
EXP045_REPLACEMENT_RUN_AUTHORIZED = False

SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED = True
SUCCESSOR_RESULT_EXECUTION_AUTHORIZED = False
SUCCESSOR_MODEL_FIT_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
SHADOW_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def build_post_result_diagnostic_gate() -> dict[str, object]:
    if FULL_SELECTION_GATE_PASS_COUNT != 1:
        raise ValueError(
            "DEC-103 full selection-gate pass count drift"
        )
    if (
        POSITIVE_FINANCIAL_SIGNS_LOW_COUNT_VARIANT_COUNT
        >= POSITIVE_FINANCIAL_SIGNS_VARIANT_COUNT
        + 1
    ):
        raise ValueError(
            "DEC-103 low-count variant accounting drift"
        )
    if (
        DIRECTIONAL_COUNT_PASS_FINANCIAL_FAIL_COUNT
        + FULL_SELECTION_GATE_PASS_COUNT
        != DIRECTIONAL_COUNT_GATE_PASS_COUNT
    ):
        raise ValueError(
            "DEC-103 directional-count accounting drift"
        )
    if VALIDATION_DIRECTIONAL_CANDIDATE_COUNT >= (
        SELECTION_DIRECTIONAL_CANDIDATE_COUNT
    ):
        raise ValueError(
            "DEC-103 selected-candidate contraction drift"
        )
    if VALIDATION_MEAN_NET_PIPS >= 0:
        raise ValueError(
            "DEC-103 selected validation sign drift"
        )
    if ACCEPTED_MODEL_CANDIDATE_COUNT != 0:
        raise ValueError(
            "DEC-103 accepted-candidate count drift"
        )

    return {
        "post_result_diagnostic_decision": (
            POST_RESULT_DIAGNOSTIC_DECISION
        ),
        "source_result_decision": SOURCE_RESULT_DECISION,
        "source_experiment_id": SOURCE_EXPERIMENT_ID,
        "source_model_run_id": SOURCE_MODEL_RUN_ID,
        "source_model_head_sha": SOURCE_MODEL_HEAD_SHA,
        "source_evidence_fingerprint": (
            SOURCE_EVIDENCE_FINGERPRINT
        ),
        "stage": "SUCCESSOR_PROTOCOL_SOURCE_OPEN",
        "diagnostic_classification": (
            "TEMPORAL_STABILITY_FAILURE_DOMINANT"
        ),
        "evaluated_variant_count": EVALUATED_VARIANT_COUNT,
        "full_selection_gate_pass_count": (
            FULL_SELECTION_GATE_PASS_COUNT
        ),
        "positive_financial_signs_variant_count": (
            POSITIVE_FINANCIAL_SIGNS_VARIANT_COUNT
        ),
        "positive_financial_signs_low_count_variant_count": (
            POSITIVE_FINANCIAL_SIGNS_LOW_COUNT_VARIANT_COUNT
        ),
        "directional_count_gate_pass_count": (
            DIRECTIONAL_COUNT_GATE_PASS_COUNT
        ),
        "directional_count_pass_financial_fail_count": (
            DIRECTIONAL_COUNT_PASS_FINANCIAL_FAIL_COUNT
        ),
        "selected_cell": {
            "symbol": SELECTED_SYMBOL,
            "timeframe": SELECTED_TIMEFRAME,
            "horizon_minutes": SELECTED_HORIZON_MINUTES,
            "model_family": SELECTED_MODEL_FAMILY,
            "confidence_threshold": (
                SELECTED_CONFIDENCE_THRESHOLD
            ),
            "selection_directional_candidate_count": (
                SELECTION_DIRECTIONAL_CANDIDATE_COUNT
            ),
            "selection_directional_candidate_rate": (
                SELECTION_DIRECTIONAL_CANDIDATE_RATE
            ),
            "selection_mean_net_pips": (
                SELECTION_MEAN_NET_PIPS
            ),
            "selection_total_net_pips": (
                SELECTION_TOTAL_NET_PIPS
            ),
            "validation_directional_candidate_count": (
                VALIDATION_DIRECTIONAL_CANDIDATE_COUNT
            ),
            "validation_directional_candidate_rate": (
                VALIDATION_DIRECTIONAL_CANDIDATE_RATE
            ),
            "validation_mean_net_pips": (
                VALIDATION_MEAN_NET_PIPS
            ),
            "validation_total_net_pips": (
                VALIDATION_TOTAL_NET_PIPS
            ),
            "validation_to_selection_candidate_count_ratio": (
                VALIDATION_TO_SELECTION_CANDIDATE_COUNT_RATIO
            ),
            "validation_to_selection_candidate_rate_ratio": (
                VALIDATION_TO_SELECTION_CANDIDATE_RATE_RATIO
            ),
        },
        "logistic_nonconvergence_cell_count": (
            LOGISTIC_NONCONVERGENCE_CELL_COUNT
        ),
        "accepted_model_candidate_count": (
            ACCEPTED_MODEL_CANDIDATE_COUNT
        ),
        "min_directional_candidate_count": (
            MIN_DIRECTIONAL_CANDIDATE_COUNT
        ),
        "relax_min_directional_candidate_count_authorized": (
            RELAX_MIN_DIRECTIONAL_CANDIDATE_COUNT_AUTHORIZED
        ),
        "promote_low_count_positive_variants_authorized": (
            PROMOTE_LOW_COUNT_POSITIVE_VARIANTS_AUTHORIZED
        ),
        "exp045_rerun_authorized": EXP045_RERUN_AUTHORIZED,
        "exp045_replacement_run_authorized": (
            EXP045_REPLACEMENT_RUN_AUTHORIZED
        ),
        "successor_protocol_source_open_authorized": (
            SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED
        ),
        "successor_result_execution_authorized": (
            SUCCESSOR_RESULT_EXECUTION_AUTHORIZED
        ),
        "successor_model_fit_authorized": (
            SUCCESSOR_MODEL_FIT_AUTHORIZED
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
    }


__all__ = [
    "ACCEPTED_MODEL_CANDIDATE_COUNT",
    "BROKER_MUTATION_AUTHORIZED",
    "DEMO_ORDER_AUTHORIZED",
    "DIRECTIONAL_COUNT_GATE_PASS_COUNT",
    "DIRECTIONAL_COUNT_PASS_FINANCIAL_FAIL_COUNT",
    "EVALUATED_VARIANT_COUNT",
    "EXP045_REPLACEMENT_RUN_AUTHORIZED",
    "EXP045_RERUN_AUTHORIZED",
    "FULL_SELECTION_GATE_PASS_COUNT",
    "LIVE_ORDER_AUTHORIZED",
    "LOGISTIC_NONCONVERGENCE_CELL_COUNT",
    "MIN_DIRECTIONAL_CANDIDATE_COUNT",
    "POSITIVE_FINANCIAL_SIGNS_LOW_COUNT_VARIANT_COUNT",
    "POSITIVE_FINANCIAL_SIGNS_VARIANT_COUNT",
    "POST_RESULT_DIAGNOSTIC_DECISION",
    "PROMOTE_LOW_COUNT_POSITIVE_VARIANTS_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "RELAX_MIN_DIRECTIONAL_CANDIDATE_COUNT_AUTHORIZED",
    "SHADOW_AUTHORIZED",
    "SOURCE_EVIDENCE_FINGERPRINT",
    "SOURCE_EXPERIMENT_ID",
    "SOURCE_MODEL_HEAD_SHA",
    "SOURCE_MODEL_RUN_ID",
    "SOURCE_RESULT_DECISION",
    "SUCCESSOR_MODEL_FIT_AUTHORIZED",
    "SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED",
    "SUCCESSOR_RESULT_EXECUTION_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "build_post_result_diagnostic_gate",
]
