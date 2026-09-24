from __future__ import annotations


POST_RESULT_DIAGNOSTIC_DECISION = "DEC-122"
SOURCE_RESULT_DECISION = "DEC-121"
SOURCE_EXPERIMENT_ID = "EXP-20260924-047"
SOURCE_MODEL_RUN_ID = 35993400007
SOURCE_MODEL_HEAD_SHA = (
    "5c4d81c0ebc9f930b2361d54cb0245a3d8c886d2"
)
SOURCE_EVIDENCE_FINGERPRINT = (
    "f047310749a2742d75d2e448243080d3"
    "68b6a5cdf66bc119ec33e59cc192352f"
)
DEC121_MERGED_COMMIT = (
    "1c9dec9ea6025b45a35097c4d9c2eda11aaaad00"
)
DEC121_RESULT_DECISION_BLOB_SHA = (
    "1c1cffc360949609b2d4ae404a165154f3ce7b0f"
)

EVALUATED_DENSITY_VARIANT_COUNT = 54
UNAVAILABLE_BUDGET_VARIANT_COUNT = 0
AGGREGATE_SELECTION_PASS_VARIANT_COUNT = 12
AGGREGATE_SELECTION_REJECT_VARIANT_COUNT = 42
STABLE_SELECTION_PASS_VARIANT_COUNT = 0
STABILITY_REJECT_VARIANT_COUNT = 12
CANDIDATE_SHARE_REJECT_VARIANT_COUNT = 12
WINDOW_FINANCIAL_REJECT_VARIANT_COUNT = 10
CANDIDATE_SHARE_ONLY_REJECT_VARIANT_COUNT = 2
ZERO_2021_CANDIDATE_VARIANT_COUNT = 6
CELLS_WITH_AGGREGATE_PASS_COUNT = 6
ACCEPTED_MODEL_CANDIDATE_COUNT = 0

AGGREGATE_PASS_VARIANTS = (
    ("GBPUSD", "1h", 60, 250),
    ("GBPUSD", "5m", 240, 250),
    ("GBPUSD", "5m", 240, 500),
    ("USDJPY", "15m", 60, 250),
    ("USDJPY", "15m", 240, 250),
    ("USDJPY", "15m", 240, 500),
    ("USDJPY", "5m", 60, 250),
    ("USDJPY", "5m", 60, 500),
    ("USDJPY", "5m", 60, 1000),
    ("USDJPY", "5m", 240, 250),
    ("USDJPY", "5m", 240, 500),
    ("USDJPY", "5m", 240, 1000),
)

CANDIDATE_SHARE_ONLY_REJECT_VARIANTS = (
    ("GBPUSD", "1h", 60, 250),
    ("GBPUSD", "5m", 240, 500),
)

ZERO_2021_CANDIDATE_VARIANTS = (
    ("USDJPY", "15m", 240, 250),
    ("USDJPY", "15m", 240, 500),
    ("USDJPY", "5m", 60, 250),
    ("USDJPY", "5m", 240, 250),
    ("USDJPY", "5m", 240, 500),
    ("USDJPY", "5m", 240, 1000),
)

RELAX_STABILITY_SHARE_AUTHORIZED = False
REMOVE_2021_STABILITY_WINDOWS_AUTHORIZED = False
ADD_WIDER_DENSITY_ANCHORS_AUTHORIZED = False
EXP047_RERUN_AUTHORIZED = False
EXP047_REPLACEMENT_RUN_AUTHORIZED = False

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


def build_density_post_result_diagnostic_gate() -> dict[str, object]:
    if (
        AGGREGATE_SELECTION_PASS_VARIANT_COUNT
        + AGGREGATE_SELECTION_REJECT_VARIANT_COUNT
        != EVALUATED_DENSITY_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-122 aggregate-selection accounting drift"
        )
    if (
        STABLE_SELECTION_PASS_VARIANT_COUNT
        + STABILITY_REJECT_VARIANT_COUNT
        != AGGREGATE_SELECTION_PASS_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-122 stability accounting drift"
        )
    if (
        CANDIDATE_SHARE_ONLY_REJECT_VARIANT_COUNT
        + WINDOW_FINANCIAL_REJECT_VARIANT_COUNT
        != STABILITY_REJECT_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-122 rejection accounting drift"
        )
    if (
        CANDIDATE_SHARE_REJECT_VARIANT_COUNT
        != STABILITY_REJECT_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-122 candidate-share rejection drift"
        )
    if (
        len(AGGREGATE_PASS_VARIANTS)
        != AGGREGATE_SELECTION_PASS_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-122 aggregate-pass identity count drift"
        )
    if (
        len(CANDIDATE_SHARE_ONLY_REJECT_VARIANTS)
        != CANDIDATE_SHARE_ONLY_REJECT_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-122 share-only identity count drift"
        )
    if (
        len(ZERO_2021_CANDIDATE_VARIANTS)
        != ZERO_2021_CANDIDATE_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-122 zero-2021 identity count drift"
        )
    if UNAVAILABLE_BUDGET_VARIANT_COUNT != 0:
        raise ValueError(
            "DEC-122 unavailable-budget count drift"
        )
    if ACCEPTED_MODEL_CANDIDATE_COUNT != 0:
        raise ValueError(
            "DEC-122 accepted-candidate count drift"
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
        "dec121_merged_commit": DEC121_MERGED_COMMIT,
        "dec121_result_decision_blob_sha": (
            DEC121_RESULT_DECISION_BLOB_SHA
        ),
        "stage": "SUCCESSOR_PROTOCOL_SOURCE_OPEN",
        "diagnostic_classification": (
            "TEMPORAL_REGIME_CONCENTRATION_DOMINANT"
        ),
        "evaluated_density_variant_count": (
            EVALUATED_DENSITY_VARIANT_COUNT
        ),
        "unavailable_budget_variant_count": (
            UNAVAILABLE_BUDGET_VARIANT_COUNT
        ),
        "aggregate_selection_pass_variant_count": (
            AGGREGATE_SELECTION_PASS_VARIANT_COUNT
        ),
        "aggregate_selection_reject_variant_count": (
            AGGREGATE_SELECTION_REJECT_VARIANT_COUNT
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
        "candidate_share_only_reject_variant_count": (
            CANDIDATE_SHARE_ONLY_REJECT_VARIANT_COUNT
        ),
        "zero_2021_candidate_variant_count": (
            ZERO_2021_CANDIDATE_VARIANT_COUNT
        ),
        "cells_with_aggregate_pass_count": (
            CELLS_WITH_AGGREGATE_PASS_COUNT
        ),
        "aggregate_pass_variants": [
            list(value)
            for value in AGGREGATE_PASS_VARIANTS
        ],
        "candidate_share_only_reject_variants": [
            list(value)
            for value in (
                CANDIDATE_SHARE_ONLY_REJECT_VARIANTS
            )
        ],
        "zero_2021_candidate_variants": [
            list(value)
            for value in ZERO_2021_CANDIDATE_VARIANTS
        ],
        "accepted_model_candidate_count": (
            ACCEPTED_MODEL_CANDIDATE_COUNT
        ),
        "guardrails": {
            "relax_stability_share_authorized": (
                RELAX_STABILITY_SHARE_AUTHORIZED
            ),
            "remove_2021_stability_windows_authorized": (
                REMOVE_2021_STABILITY_WINDOWS_AUTHORIZED
            ),
            "add_wider_density_anchors_authorized": (
                ADD_WIDER_DENSITY_ANCHORS_AUTHORIZED
            ),
            "exp047_rerun_authorized": (
                EXP047_RERUN_AUTHORIZED
            ),
            "exp047_replacement_run_authorized": (
                EXP047_REPLACEMENT_RUN_AUTHORIZED
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
    "ADD_WIDER_DENSITY_ANCHORS_AUTHORIZED",
    "AGGREGATE_PASS_VARIANTS",
    "AGGREGATE_SELECTION_PASS_VARIANT_COUNT",
    "AGGREGATE_SELECTION_REJECT_VARIANT_COUNT",
    "BROKER_MUTATION_AUTHORIZED",
    "CANDIDATE_SHARE_ONLY_REJECT_VARIANT_COUNT",
    "CANDIDATE_SHARE_ONLY_REJECT_VARIANTS",
    "CANDIDATE_SHARE_REJECT_VARIANT_COUNT",
    "CELLS_WITH_AGGREGATE_PASS_COUNT",
    "DEC121_MERGED_COMMIT",
    "DEC121_RESULT_DECISION_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "EVALUATED_DENSITY_VARIANT_COUNT",
    "EXP047_REPLACEMENT_RUN_AUTHORIZED",
    "EXP047_RERUN_AUTHORIZED",
    "LIVE_ORDER_AUTHORIZED",
    "POST_RESULT_DIAGNOSTIC_DECISION",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "RELAX_STABILITY_SHARE_AUTHORIZED",
    "REMOVE_2021_STABILITY_WINDOWS_AUTHORIZED",
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
    "TRADING_AUTHORIZED",
    "UNAVAILABLE_BUDGET_VARIANT_COUNT",
    "WINDOW_FINANCIAL_REJECT_VARIANT_COUNT",
    "ZERO_2021_CANDIDATE_VARIANT_COUNT",
    "ZERO_2021_CANDIDATE_VARIANTS",
    "build_density_post_result_diagnostic_gate",
]
