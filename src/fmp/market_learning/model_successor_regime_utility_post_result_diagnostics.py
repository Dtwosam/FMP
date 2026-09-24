from __future__ import annotations


POST_RESULT_DIAGNOSTIC_DECISION = "DEC-140"
SOURCE_RESULT_DECISION = "DEC-139"
SOURCE_EXPERIMENT_ID = "EXP-20260924-049"
SOURCE_MODEL_RUN_ID = 36029925264
SOURCE_MODEL_HEAD_SHA = (
    "eeb735bca7d38c3246f22a9606dfafe9c3df8279"
)
SOURCE_EVIDENCE_FINGERPRINT = (
    "29ecbb5bf3ce00f35c825e977d9b3fff"
    "1777e165ce9bef311fefcb7bfbdb091e"
)
DEC139_MERGED_COMMIT = (
    "3535e47d2224802eadf154330ef57519c8ea674c"
)
DEC139_RESULT_DECISION_BLOB_SHA = (
    "dce13838f32fbb8aa0e403c550b669f778dd0742"
)

TOTAL_VARIANT_COUNT = 54
AVAILABLE_VARIANT_COUNT = 23
UNAVAILABLE_BUDGET_VARIANT_COUNT = 31
FULLY_UNAVAILABLE_CELL_COUNT = 7
CELLS_WITH_ANY_UNAVAILABLE_BUDGET_COUNT = 13

AGGREGATE_SELECTION_PASS_VARIANT_COUNT = 8
AGGREGATE_SELECTION_REJECT_AVAILABLE_VARIANT_COUNT = 15
CELLS_WITH_AGGREGATE_PASS_COUNT = 4
HORIZON_240_AGGREGATE_PASS_VARIANT_COUNT = 8
HORIZON_60_AGGREGATE_PASS_VARIANT_COUNT = 0

STABLE_SELECTION_PASS_VARIANT_COUNT = 0
STABILITY_REJECT_VARIANT_COUNT = 8
CANDIDATE_SHARE_REJECT_VARIANT_COUNT = 8
WINDOW_FINANCIAL_REJECT_VARIANT_COUNT = 8
BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT = 8
FINANCIAL_ONLY_REJECT_VARIANT_COUNT = 0
SHARE_ONLY_REJECT_VARIANT_COUNT = 0

SELECTION_2021_H1_SHARE_REJECT_VARIANT_COUNT = 8
SELECTION_2021_H2_SHARE_REJECT_VARIANT_COUNT = 8
SELECTION_2022_H2_FINANCIAL_REJECT_VARIANT_COUNT = 6

ZERO_ANY_2021_HALF_VARIANT_COUNT = 2
ZERO_BOTH_2021_HALVES_VARIANT_COUNT = 1
ACCEPTED_MODEL_CANDIDATE_COUNT = 0

AGGREGATE_PASS_VARIANTS = (
    ("EURUSD", "1h", 240, 250),
    ("GBPUSD", "5m", 240, 1000),
    ("USDJPY", "15m", 240, 250),
    ("USDJPY", "15m", 240, 500),
    ("USDJPY", "15m", 240, 1000),
    ("USDJPY", "5m", 240, 250),
    ("USDJPY", "5m", 240, 500),
    ("USDJPY", "5m", 240, 1000),
)

ZERO_ANY_2021_HALF_VARIANTS = (
    ("USDJPY", "15m", 240, 250),
    ("USDJPY", "5m", 240, 250),
)

ZERO_BOTH_2021_HALVES_VARIANTS = (
    ("USDJPY", "5m", 240, 250),
)

SELECTION_2022_H2_FINANCIAL_REJECT_VARIANTS = (
    ("EURUSD", "1h", 240, 250),
    ("GBPUSD", "5m", 240, 1000),
    ("USDJPY", "15m", 240, 250),
    ("USDJPY", "15m", 240, 500),
    ("USDJPY", "15m", 240, 1000),
    ("USDJPY", "5m", 240, 250),
)

RELAX_STABILITY_SHARE_AUTHORIZED = False
RELAX_STABILITY_FINANCIAL_AUTHORIZED = False
REMOVE_2021_STABILITY_WINDOWS_AUTHORIZED = False
LOWER_UTILITY_POSITIVITY_REQUIREMENT_AUTHORIZED = False
ADD_SMALLER_BUDGET_ANCHORS_AUTHORIZED = False
EXP049_RERUN_AUTHORIZED = False
EXP049_REPLACEMENT_RUN_AUTHORIZED = False

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


def build_regime_utility_post_result_diagnostic_gate() -> dict[str, object]:
    if (
        AVAILABLE_VARIANT_COUNT
        + UNAVAILABLE_BUDGET_VARIANT_COUNT
        != TOTAL_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-140 total-variant accounting drift"
        )
    if (
        AGGREGATE_SELECTION_PASS_VARIANT_COUNT
        + AGGREGATE_SELECTION_REJECT_AVAILABLE_VARIANT_COUNT
        != AVAILABLE_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-140 available-variant aggregate accounting drift"
        )
    if (
        STABLE_SELECTION_PASS_VARIANT_COUNT
        + STABILITY_REJECT_VARIANT_COUNT
        != AGGREGATE_SELECTION_PASS_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-140 stability accounting drift"
        )
    if (
        BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT
        + FINANCIAL_ONLY_REJECT_VARIANT_COUNT
        + SHARE_ONLY_REJECT_VARIANT_COUNT
        != STABILITY_REJECT_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-140 rejection partition drift"
        )
    if (
        CANDIDATE_SHARE_REJECT_VARIANT_COUNT
        != BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT
        + SHARE_ONLY_REJECT_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-140 candidate-share rejection drift"
        )
    if (
        WINDOW_FINANCIAL_REJECT_VARIANT_COUNT
        != BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT
        + FINANCIAL_ONLY_REJECT_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-140 financial-window rejection drift"
        )
    if (
        SELECTION_2021_H1_SHARE_REJECT_VARIANT_COUNT
        != AGGREGATE_SELECTION_PASS_VARIANT_COUNT
        or SELECTION_2021_H2_SHARE_REJECT_VARIANT_COUNT
        != AGGREGATE_SELECTION_PASS_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-140 2021 share-rejection accounting drift"
        )
    if (
        len(AGGREGATE_PASS_VARIANTS)
        != AGGREGATE_SELECTION_PASS_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-140 aggregate-pass identity count drift"
        )
    if (
        len(ZERO_ANY_2021_HALF_VARIANTS)
        != ZERO_ANY_2021_HALF_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-140 zero-any-2021 identity count drift"
        )
    if (
        len(ZERO_BOTH_2021_HALVES_VARIANTS)
        != ZERO_BOTH_2021_HALVES_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-140 zero-both-2021 identity count drift"
        )
    if (
        len(SELECTION_2022_H2_FINANCIAL_REJECT_VARIANTS)
        != SELECTION_2022_H2_FINANCIAL_REJECT_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-140 2022-H2 financial identity count drift"
        )
    if (
        HORIZON_240_AGGREGATE_PASS_VARIANT_COUNT
        + HORIZON_60_AGGREGATE_PASS_VARIANT_COUNT
        != AGGREGATE_SELECTION_PASS_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-140 horizon aggregate-pass accounting drift"
        )
    if ACCEPTED_MODEL_CANDIDATE_COUNT != 0:
        raise ValueError(
            "DEC-140 accepted-candidate count drift"
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
        "dec139_merged_commit": DEC139_MERGED_COMMIT,
        "dec139_result_decision_blob_sha": (
            DEC139_RESULT_DECISION_BLOB_SHA
        ),
        "stage": "SUCCESSOR_PROTOCOL_SOURCE_OPEN",
        "diagnostic_classification": (
            "UTILITY_COVERAGE_AND_DUAL_TEMPORAL_STABILITY_LIMITED"
        ),
        "total_variant_count": TOTAL_VARIANT_COUNT,
        "available_variant_count": AVAILABLE_VARIANT_COUNT,
        "unavailable_budget_variant_count": (
            UNAVAILABLE_BUDGET_VARIANT_COUNT
        ),
        "fully_unavailable_cell_count": (
            FULLY_UNAVAILABLE_CELL_COUNT
        ),
        "cells_with_any_unavailable_budget_count": (
            CELLS_WITH_ANY_UNAVAILABLE_BUDGET_COUNT
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
        "horizon_240_aggregate_pass_variant_count": (
            HORIZON_240_AGGREGATE_PASS_VARIANT_COUNT
        ),
        "horizon_60_aggregate_pass_variant_count": (
            HORIZON_60_AGGREGATE_PASS_VARIANT_COUNT
        ),
        "stable_selection_pass_variant_count": (
            STABLE_SELECTION_PASS_VARIANT_COUNT
        ),
        "stability_reject_variant_count": (
            STABILITY_REJECT_VARIANT_COUNT
        ),
        "candidate_share_reject_variant_count": (
            CANDIDATE_SHARE_REJECT_VARIANT_COUNT
        ),
        "window_financial_reject_variant_count": (
            WINDOW_FINANCIAL_REJECT_VARIANT_COUNT
        ),
        "both_share_and_financial_reject_variant_count": (
            BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT
        ),
        "financial_only_reject_variant_count": (
            FINANCIAL_ONLY_REJECT_VARIANT_COUNT
        ),
        "share_only_reject_variant_count": (
            SHARE_ONLY_REJECT_VARIANT_COUNT
        ),
        "selection_2021_h1_share_reject_variant_count": (
            SELECTION_2021_H1_SHARE_REJECT_VARIANT_COUNT
        ),
        "selection_2021_h2_share_reject_variant_count": (
            SELECTION_2021_H2_SHARE_REJECT_VARIANT_COUNT
        ),
        "selection_2022_h2_financial_reject_variant_count": (
            SELECTION_2022_H2_FINANCIAL_REJECT_VARIANT_COUNT
        ),
        "zero_any_2021_half_variant_count": (
            ZERO_ANY_2021_HALF_VARIANT_COUNT
        ),
        "zero_both_2021_halves_variant_count": (
            ZERO_BOTH_2021_HALVES_VARIANT_COUNT
        ),
        "aggregate_pass_variants": [
            list(value)
            for value in AGGREGATE_PASS_VARIANTS
        ],
        "zero_any_2021_half_variants": [
            list(value)
            for value in ZERO_ANY_2021_HALF_VARIANTS
        ],
        "zero_both_2021_halves_variants": [
            list(value)
            for value in ZERO_BOTH_2021_HALVES_VARIANTS
        ],
        "selection_2022_h2_financial_reject_variants": [
            list(value)
            for value in (
                SELECTION_2022_H2_FINANCIAL_REJECT_VARIANTS
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
            "lower_utility_positivity_requirement_authorized": (
                LOWER_UTILITY_POSITIVITY_REQUIREMENT_AUTHORIZED
            ),
            "add_smaller_budget_anchors_authorized": (
                ADD_SMALLER_BUDGET_ANCHORS_AUTHORIZED
            ),
            "exp049_rerun_authorized": EXP049_RERUN_AUTHORIZED,
            "exp049_replacement_run_authorized": (
                EXP049_REPLACEMENT_RUN_AUTHORIZED
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
    "AVAILABLE_VARIANT_COUNT",
    "BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT",
    "BROKER_MUTATION_AUTHORIZED",
    "CANDIDATE_SHARE_REJECT_VARIANT_COUNT",
    "CELLS_WITH_AGGREGATE_PASS_COUNT",
    "CELLS_WITH_ANY_UNAVAILABLE_BUDGET_COUNT",
    "DEC139_MERGED_COMMIT",
    "DEC139_RESULT_DECISION_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "EXP049_REPLACEMENT_RUN_AUTHORIZED",
    "EXP049_RERUN_AUTHORIZED",
    "FINANCIAL_ONLY_REJECT_VARIANT_COUNT",
    "FULLY_UNAVAILABLE_CELL_COUNT",
    "HORIZON_240_AGGREGATE_PASS_VARIANT_COUNT",
    "HORIZON_60_AGGREGATE_PASS_VARIANT_COUNT",
    "LIVE_ORDER_AUTHORIZED",
    "LOWER_UTILITY_POSITIVITY_REQUIREMENT_AUTHORIZED",
    "POST_RESULT_DIAGNOSTIC_DECISION",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "RELAX_STABILITY_FINANCIAL_AUTHORIZED",
    "RELAX_STABILITY_SHARE_AUTHORIZED",
    "REMOVE_2021_STABILITY_WINDOWS_AUTHORIZED",
    "SELECTION_2021_H1_SHARE_REJECT_VARIANT_COUNT",
    "SELECTION_2021_H2_SHARE_REJECT_VARIANT_COUNT",
    "SELECTION_2022_H2_FINANCIAL_REJECT_VARIANT_COUNT",
    "SELECTION_2022_H2_FINANCIAL_REJECT_VARIANTS",
    "SHADOW_AUTHORIZED",
    "SHARE_ONLY_REJECT_VARIANT_COUNT",
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
    "WINDOW_FINANCIAL_REJECT_VARIANT_COUNT",
    "ZERO_ANY_2021_HALF_VARIANT_COUNT",
    "ZERO_ANY_2021_HALF_VARIANTS",
    "ZERO_BOTH_2021_HALVES_VARIANT_COUNT",
    "ZERO_BOTH_2021_HALVES_VARIANTS",
    "build_regime_utility_post_result_diagnostic_gate",
]
