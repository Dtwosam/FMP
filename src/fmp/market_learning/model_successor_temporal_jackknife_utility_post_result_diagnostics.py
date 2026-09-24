from __future__ import annotations


POST_RESULT_DIAGNOSTIC_DECISION = "DEC-149"
SOURCE_RESULT_DECISION = "DEC-148"
SOURCE_EXPERIMENT_ID = "EXP-20260924-050"
SOURCE_MODEL_RUN_ID = 36049824739
SOURCE_MODEL_HEAD_SHA = (
    "25d48828b981c4309f4a859d2a33a56094638f21"
)
SOURCE_EVIDENCE_FINGERPRINT = (
    "866b4a8f26553bad8c80a7b2e0e68aed"
    "b50bfa42b3c767ce91478c9dfd720023"
)
DEC148_MERGED_COMMIT = (
    "50ae34098ece275959d52ca9d104a07374a7ff6a"
)
DEC148_RESULT_DECISION_BLOB_SHA = (
    "70402f6c21f4ed22b4991025c98e6c1664215215"
)

TOTAL_VARIANT_COUNT = 54
AVAILABLE_VARIANT_COUNT = 28
UNAVAILABLE_BUDGET_VARIANT_COUNT = 26

AGGREGATE_SELECTION_PASS_VARIANT_COUNT = 3
AGGREGATE_SELECTION_REJECT_AVAILABLE_VARIANT_COUNT = 25
CELLS_WITH_AGGREGATE_PASS_COUNT = 1
HORIZON_60_AGGREGATE_PASS_VARIANT_COUNT = 3
HORIZON_240_AGGREGATE_PASS_VARIANT_COUNT = 0

STABLE_SELECTION_PASS_VARIANT_COUNT = 0
STABILITY_REJECT_VARIANT_COUNT = 3

SELECTION_2021_H1_ZERO_CANDIDATE_VARIANT_COUNT = 3
SELECTION_2021_H2_ZERO_CANDIDATE_VARIANT_COUNT = 2
SELECTION_2021_H2_SINGLE_CANDIDATE_VARIANT_COUNT = 1
SELECTION_2021_H2_BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT = 1
SELECTION_2022_H1_FINANCIAL_POSITIVE_SHARE_REJECT_VARIANT_COUNT = 2
SELECTION_2022_H2_PASS_VARIANT_COUNT = 3

PREDECESSOR_AVAILABLE_VARIANT_COUNT = 23
PREDECESSOR_UNAVAILABLE_BUDGET_VARIANT_COUNT = 31
PREDECESSOR_UTILITY_ELIGIBLE_SELECTION_ROW_COUNT = 14158
UTILITY_ELIGIBLE_SELECTION_ROW_COUNT = 26392
UTILITY_ELIGIBLE_SELECTION_ROW_DELTA = 12234
AVAILABLE_VARIANT_COUNT_DELTA = 5
UNAVAILABLE_BUDGET_VARIANT_COUNT_DELTA = -5

ACCEPTED_MODEL_CANDIDATE_COUNT = 0

AGGREGATE_PASS_VARIANTS = (
    ("USDJPY", "5m", 60, 250, 250, 612.9),
    ("USDJPY", "5m", 60, 500, 501, 247.4),
    ("USDJPY", "5m", 60, 1000, 1000, 504.3),
)

SELECTION_2021_H2_ZERO_CANDIDATE_VARIANTS = (
    ("USDJPY", "5m", 60, 250),
    ("USDJPY", "5m", 60, 500),
)

SELECTION_2021_H2_SINGLE_CANDIDATE_VARIANTS = (
    ("USDJPY", "5m", 60, 1000),
)

SELECTION_2022_H1_FINANCIAL_POSITIVE_SHARE_REJECT_VARIANTS = (
    ("USDJPY", "5m", 60, 500),
    ("USDJPY", "5m", 60, 1000),
)

RELAX_STABILITY_SHARE_AUTHORIZED = False
RELAX_STABILITY_FINANCIAL_AUTHORIZED = False
REMOVE_2021_STABILITY_WINDOWS_AUTHORIZED = False
ALTER_TEMPORAL_JACKKNIFE_VIEWS_AUTHORIZED = False
ALTER_UNANIMOUS_UTILITY_CONSENSUS_AUTHORIZED = False
LOWER_UTILITY_POSITIVITY_REQUIREMENT_AUTHORIZED = False
ADD_SMALLER_BUDGET_ANCHORS_AUTHORIZED = False
EXP050_RERUN_AUTHORIZED = False
EXP050_REPLACEMENT_RUN_AUTHORIZED = False

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


def build_temporal_jackknife_utility_post_result_diagnostic_gate(
) -> dict[str, object]:
    if (
        AVAILABLE_VARIANT_COUNT
        + UNAVAILABLE_BUDGET_VARIANT_COUNT
        != TOTAL_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-149 total-variant accounting drift"
        )
    if (
        AGGREGATE_SELECTION_PASS_VARIANT_COUNT
        + AGGREGATE_SELECTION_REJECT_AVAILABLE_VARIANT_COUNT
        != AVAILABLE_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-149 available-variant aggregate accounting drift"
        )
    if (
        STABLE_SELECTION_PASS_VARIANT_COUNT
        + STABILITY_REJECT_VARIANT_COUNT
        != AGGREGATE_SELECTION_PASS_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-149 stability accounting drift"
        )
    if (
        HORIZON_60_AGGREGATE_PASS_VARIANT_COUNT
        + HORIZON_240_AGGREGATE_PASS_VARIANT_COUNT
        != AGGREGATE_SELECTION_PASS_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-149 horizon aggregate-pass accounting drift"
        )
    if (
        len(AGGREGATE_PASS_VARIANTS)
        != AGGREGATE_SELECTION_PASS_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-149 aggregate-pass identity count drift"
        )
    if (
        len(SELECTION_2021_H2_ZERO_CANDIDATE_VARIANTS)
        != SELECTION_2021_H2_ZERO_CANDIDATE_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-149 2021-H2 zero-candidate identity count drift"
        )
    if (
        len(SELECTION_2021_H2_SINGLE_CANDIDATE_VARIANTS)
        != SELECTION_2021_H2_SINGLE_CANDIDATE_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-149 2021-H2 single-candidate identity count drift"
        )
    if (
        len(
            SELECTION_2022_H1_FINANCIAL_POSITIVE_SHARE_REJECT_VARIANTS
        )
        != SELECTION_2022_H1_FINANCIAL_POSITIVE_SHARE_REJECT_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-149 2022-H1 positive-financial identity count drift"
        )
    if (
        SELECTION_2021_H1_ZERO_CANDIDATE_VARIANT_COUNT
        != AGGREGATE_SELECTION_PASS_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-149 2021-H1 zero-candidate accounting drift"
        )
    if (
        SELECTION_2021_H2_ZERO_CANDIDATE_VARIANT_COUNT
        + SELECTION_2021_H2_SINGLE_CANDIDATE_VARIANT_COUNT
        != AGGREGATE_SELECTION_PASS_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-149 2021-H2 candidate accounting drift"
        )
    if (
        SELECTION_2022_H2_PASS_VARIANT_COUNT
        != AGGREGATE_SELECTION_PASS_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-149 2022-H2 pass accounting drift"
        )
    if (
        UTILITY_ELIGIBLE_SELECTION_ROW_COUNT
        - PREDECESSOR_UTILITY_ELIGIBLE_SELECTION_ROW_COUNT
        != UTILITY_ELIGIBLE_SELECTION_ROW_DELTA
    ):
        raise ValueError(
            "DEC-149 utility-row delta drift"
        )
    if (
        AVAILABLE_VARIANT_COUNT
        - PREDECESSOR_AVAILABLE_VARIANT_COUNT
        != AVAILABLE_VARIANT_COUNT_DELTA
    ):
        raise ValueError(
            "DEC-149 available-variant delta drift"
        )
    if (
        UNAVAILABLE_BUDGET_VARIANT_COUNT
        - PREDECESSOR_UNAVAILABLE_BUDGET_VARIANT_COUNT
        != UNAVAILABLE_BUDGET_VARIANT_COUNT_DELTA
    ):
        raise ValueError(
            "DEC-149 unavailable-variant delta drift"
        )
    if ACCEPTED_MODEL_CANDIDATE_COUNT != 0:
        raise ValueError(
            "DEC-149 accepted-candidate count drift"
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
        "dec148_merged_commit": DEC148_MERGED_COMMIT,
        "dec148_result_decision_blob_sha": (
            DEC148_RESULT_DECISION_BLOB_SHA
        ),
        "stage": "SUCCESSOR_PROTOCOL_SOURCE_OPEN",
        "diagnostic_classification": (
            "UTILITY_COVERAGE_INCREASED_BUT_"
            "EARLY_TEMPORAL_COVERAGE_LIMITED"
        ),
        "total_variant_count": TOTAL_VARIANT_COUNT,
        "available_variant_count": AVAILABLE_VARIANT_COUNT,
        "unavailable_budget_variant_count": (
            UNAVAILABLE_BUDGET_VARIANT_COUNT
        ),
        "aggregate_selection_pass_variant_count": (
            AGGREGATE_SELECTION_PASS_VARIANT_COUNT
        ),
        "aggregate_selection_reject_available_variant_count": (
            AGGREGATE_SELECTION_REJECT_AVAILABLE_VARIANT_COUNT
        ),
        "cells_with_aggregate_pass_count": (
            CELLS_WITH_AGGREGATE_PASS_COUNT
        ),
        "horizon_60_aggregate_pass_variant_count": (
            HORIZON_60_AGGREGATE_PASS_VARIANT_COUNT
        ),
        "horizon_240_aggregate_pass_variant_count": (
            HORIZON_240_AGGREGATE_PASS_VARIANT_COUNT
        ),
        "stable_selection_pass_variant_count": (
            STABLE_SELECTION_PASS_VARIANT_COUNT
        ),
        "stability_reject_variant_count": (
            STABILITY_REJECT_VARIANT_COUNT
        ),
        "selection_2021_h1_zero_candidate_variant_count": (
            SELECTION_2021_H1_ZERO_CANDIDATE_VARIANT_COUNT
        ),
        "selection_2021_h2_zero_candidate_variant_count": (
            SELECTION_2021_H2_ZERO_CANDIDATE_VARIANT_COUNT
        ),
        "selection_2021_h2_single_candidate_variant_count": (
            SELECTION_2021_H2_SINGLE_CANDIDATE_VARIANT_COUNT
        ),
        "selection_2021_h2_both_share_and_financial_reject_variant_count": (
            SELECTION_2021_H2_BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT
        ),
        "selection_2022_h1_financial_positive_share_reject_variant_count": (
            SELECTION_2022_H1_FINANCIAL_POSITIVE_SHARE_REJECT_VARIANT_COUNT
        ),
        "selection_2022_h2_pass_variant_count": (
            SELECTION_2022_H2_PASS_VARIANT_COUNT
        ),
        "predecessor_available_variant_count": (
            PREDECESSOR_AVAILABLE_VARIANT_COUNT
        ),
        "predecessor_unavailable_budget_variant_count": (
            PREDECESSOR_UNAVAILABLE_BUDGET_VARIANT_COUNT
        ),
        "predecessor_utility_eligible_selection_row_count": (
            PREDECESSOR_UTILITY_ELIGIBLE_SELECTION_ROW_COUNT
        ),
        "utility_eligible_selection_row_count": (
            UTILITY_ELIGIBLE_SELECTION_ROW_COUNT
        ),
        "utility_eligible_selection_row_delta": (
            UTILITY_ELIGIBLE_SELECTION_ROW_DELTA
        ),
        "available_variant_count_delta": (
            AVAILABLE_VARIANT_COUNT_DELTA
        ),
        "unavailable_budget_variant_count_delta": (
            UNAVAILABLE_BUDGET_VARIANT_COUNT_DELTA
        ),
        "aggregate_pass_variants": [
            list(value)
            for value in AGGREGATE_PASS_VARIANTS
        ],
        "selection_2021_h2_zero_candidate_variants": [
            list(value)
            for value in SELECTION_2021_H2_ZERO_CANDIDATE_VARIANTS
        ],
        "selection_2021_h2_single_candidate_variants": [
            list(value)
            for value in SELECTION_2021_H2_SINGLE_CANDIDATE_VARIANTS
        ],
        "selection_2022_h1_financial_positive_share_reject_variants": [
            list(value)
            for value in (
                SELECTION_2022_H1_FINANCIAL_POSITIVE_SHARE_REJECT_VARIANTS
            )
        ],
        "accepted_model_candidate_count": (
            ACCEPTED_MODEL_CANDIDATE_COUNT
        ),
        "guardrails": {
            "relax_stability_share_authorized": (
                RELAX_STABILITY_SHARE_AUTHORIZED
            ),
            "relax_stability_financial_authorized": (
                RELAX_STABILITY_FINANCIAL_AUTHORIZED
            ),
            "remove_2021_stability_windows_authorized": (
                REMOVE_2021_STABILITY_WINDOWS_AUTHORIZED
            ),
            "alter_temporal_jackknife_views_authorized": (
                ALTER_TEMPORAL_JACKKNIFE_VIEWS_AUTHORIZED
            ),
            "alter_unanimous_utility_consensus_authorized": (
                ALTER_UNANIMOUS_UTILITY_CONSENSUS_AUTHORIZED
            ),
            "lower_utility_positivity_requirement_authorized": (
                LOWER_UTILITY_POSITIVITY_REQUIREMENT_AUTHORIZED
            ),
            "add_smaller_budget_anchors_authorized": (
                ADD_SMALLER_BUDGET_ANCHORS_AUTHORIZED
            ),
            "exp050_rerun_authorized": EXP050_RERUN_AUTHORIZED,
            "exp050_replacement_run_authorized": (
                EXP050_REPLACEMENT_RUN_AUTHORIZED
            ),
        },
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
    "ADD_SMALLER_BUDGET_ANCHORS_AUTHORIZED",
    "AGGREGATE_PASS_VARIANTS",
    "AGGREGATE_SELECTION_PASS_VARIANT_COUNT",
    "AGGREGATE_SELECTION_REJECT_AVAILABLE_VARIANT_COUNT",
    "ALTER_TEMPORAL_JACKKNIFE_VIEWS_AUTHORIZED",
    "ALTER_UNANIMOUS_UTILITY_CONSENSUS_AUTHORIZED",
    "AVAILABLE_VARIANT_COUNT",
    "AVAILABLE_VARIANT_COUNT_DELTA",
    "BROKER_MUTATION_AUTHORIZED",
    "CELLS_WITH_AGGREGATE_PASS_COUNT",
    "DEC148_MERGED_COMMIT",
    "DEC148_RESULT_DECISION_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "EXP050_REPLACEMENT_RUN_AUTHORIZED",
    "EXP050_RERUN_AUTHORIZED",
    "HORIZON_240_AGGREGATE_PASS_VARIANT_COUNT",
    "HORIZON_60_AGGREGATE_PASS_VARIANT_COUNT",
    "LIVE_ORDER_AUTHORIZED",
    "LOWER_UTILITY_POSITIVITY_REQUIREMENT_AUTHORIZED",
    "POST_RESULT_DIAGNOSTIC_DECISION",
    "PREDECESSOR_AVAILABLE_VARIANT_COUNT",
    "PREDECESSOR_UNAVAILABLE_BUDGET_VARIANT_COUNT",
    "PREDECESSOR_UTILITY_ELIGIBLE_SELECTION_ROW_COUNT",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "RELAX_STABILITY_FINANCIAL_AUTHORIZED",
    "RELAX_STABILITY_SHARE_AUTHORIZED",
    "REMOVE_2021_STABILITY_WINDOWS_AUTHORIZED",
    "SELECTION_2021_H1_ZERO_CANDIDATE_VARIANT_COUNT",
    "SELECTION_2021_H2_BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT",
    "SELECTION_2021_H2_SINGLE_CANDIDATE_VARIANT_COUNT",
    "SELECTION_2021_H2_SINGLE_CANDIDATE_VARIANTS",
    "SELECTION_2021_H2_ZERO_CANDIDATE_VARIANT_COUNT",
    "SELECTION_2021_H2_ZERO_CANDIDATE_VARIANTS",
    "SELECTION_2022_H1_FINANCIAL_POSITIVE_SHARE_REJECT_VARIANT_COUNT",
    "SELECTION_2022_H1_FINANCIAL_POSITIVE_SHARE_REJECT_VARIANTS",
    "SELECTION_2022_H2_PASS_VARIANT_COUNT",
    "SHADOW_AUTHORIZED",
    "SOURCE_EVIDENCE_FINGERPRINT",
    "SOURCE_EXPERIMENT_ID",
    "SOURCE_MODEL_HEAD_SHA",
    "SOURCE_MODEL_RUN_ID",
    "SOURCE_RESULT_DECISION",
    "STABILITY_REJECT_VARIANT_COUNT",
    "STABLE_SELECTION_PASS_VARIANT_COUNT",
    "SUCCESSOR_MODEL_FIT_AUTHORIZED",
    "SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED",
    "SUCCESSOR_RESULT_EXECUTION_AUTHORIZED",
    "TOTAL_VARIANT_COUNT",
    "TRADING_AUTHORIZED",
    "UNAVAILABLE_BUDGET_VARIANT_COUNT",
    "UNAVAILABLE_BUDGET_VARIANT_COUNT_DELTA",
    "UTILITY_ELIGIBLE_SELECTION_ROW_COUNT",
    "UTILITY_ELIGIBLE_SELECTION_ROW_DELTA",
    "build_temporal_jackknife_utility_post_result_diagnostic_gate",
]
