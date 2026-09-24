from __future__ import annotations


POST_RESULT_DIAGNOSTIC_DECISION = "DEC-131"
SOURCE_RESULT_DECISION = "DEC-130"
SOURCE_EXPERIMENT_ID = "EXP-20260924-048"
SOURCE_MODEL_RUN_ID = 36006524422
SOURCE_MODEL_HEAD_SHA = (
    "60b2796a64f0a4f7f95660d45ef7ab7fac519e9c"
)
SOURCE_EVIDENCE_FINGERPRINT = (
    "acd3a9d7708c345b05082026de9eecc5"
    "15abb9090a901126034e91173eb30647"
)
DEC130_MERGED_COMMIT = (
    "39f7934896b83fdbd7f57dda75acded433419f92"
)
DEC130_RESULT_DECISION_BLOB_SHA = (
    "0556da8c036a55ba3b94d933f67f439eb306f9c2"
)

EVALUATED_VARIANT_COUNT = 54
UNAVAILABLE_BUDGET_VARIANT_COUNT = 0
AGGREGATE_SELECTION_PASS_VARIANT_COUNT = 17
AGGREGATE_SELECTION_REJECT_VARIANT_COUNT = 37
STABLE_SELECTION_PASS_VARIANT_COUNT = 0
STABILITY_REJECT_VARIANT_COUNT = 17
CANDIDATE_SHARE_REJECT_VARIANT_COUNT = 13
WINDOW_FINANCIAL_REJECT_VARIANT_COUNT = 17
BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT = 13
FINANCIAL_ONLY_REJECT_VARIANT_COUNT = 4
SHARE_ONLY_REJECT_VARIANT_COUNT = 0
ZERO_BOTH_2021_HALVES_VARIANT_COUNT = 0
ZERO_ANY_2021_HALF_VARIANT_COUNT = 5
ACCEPTED_MODEL_CANDIDATE_COUNT = 0

FINANCIAL_ONLY_REJECT_VARIANTS = (
    ("EURUSD", "15m", 240, 1000),
    ("EURUSD", "1h", 240, 250),
    ("EURUSD", "1h", 240, 500),
    ("EURUSD", "1h", 240, 1000),
)

ZERO_ANY_2021_HALF_VARIANTS = (
    ("GBPUSD", "5m", 60, 250),
    ("GBPUSD", "5m", 60, 500),
    ("USDJPY", "5m", 240, 250),
    ("USDJPY", "5m", 60, 250),
    ("USDJPY", "5m", 60, 500),
)

RELAX_STABILITY_SHARE_AUTHORIZED = False
RELAX_STABILITY_FINANCIAL_AUTHORIZED = False
REMOVE_2021_STABILITY_WINDOWS_AUTHORIZED = False
EXP048_RERUN_AUTHORIZED = False
EXP048_REPLACEMENT_RUN_AUTHORIZED = False

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


def build_regime_consensus_post_result_diagnostic_gate() -> dict[str, object]:
    if (
        AGGREGATE_SELECTION_PASS_VARIANT_COUNT
        + AGGREGATE_SELECTION_REJECT_VARIANT_COUNT
        != EVALUATED_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-131 aggregate-selection accounting drift"
        )
    if (
        STABLE_SELECTION_PASS_VARIANT_COUNT
        + STABILITY_REJECT_VARIANT_COUNT
        != AGGREGATE_SELECTION_PASS_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-131 stability accounting drift"
        )
    if (
        BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT
        + FINANCIAL_ONLY_REJECT_VARIANT_COUNT
        + SHARE_ONLY_REJECT_VARIANT_COUNT
        != STABILITY_REJECT_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-131 rejection partition drift"
        )
    if (
        CANDIDATE_SHARE_REJECT_VARIANT_COUNT
        != BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT
        + SHARE_ONLY_REJECT_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-131 candidate-share rejection drift"
        )
    if (
        WINDOW_FINANCIAL_REJECT_VARIANT_COUNT
        != BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT
        + FINANCIAL_ONLY_REJECT_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-131 financial-window rejection drift"
        )
    if (
        len(FINANCIAL_ONLY_REJECT_VARIANTS)
        != FINANCIAL_ONLY_REJECT_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-131 financial-only identity count drift"
        )
    if (
        len(ZERO_ANY_2021_HALF_VARIANTS)
        != ZERO_ANY_2021_HALF_VARIANT_COUNT
    ):
        raise ValueError(
            "DEC-131 zero-2021-half identity count drift"
        )
    if UNAVAILABLE_BUDGET_VARIANT_COUNT != 0:
        raise ValueError(
            "DEC-131 unavailable-budget count drift"
        )
    if ACCEPTED_MODEL_CANDIDATE_COUNT != 0:
        raise ValueError(
            "DEC-131 accepted-candidate count drift"
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
        "dec130_merged_commit": DEC130_MERGED_COMMIT,
        "dec130_result_decision_blob_sha": (
            DEC130_RESULT_DECISION_BLOB_SHA
        ),
        "stage": "SUCCESSOR_PROTOCOL_SOURCE_OPEN",
        "diagnostic_classification": (
            "WINDOW_FINANCIAL_INSTABILITY_DOMINANT"
        ),
        "evaluated_variant_count": EVALUATED_VARIANT_COUNT,
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
        "both_share_and_financial_reject_variant_count": (
            BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT
        ),
        "financial_only_reject_variant_count": (
            FINANCIAL_ONLY_REJECT_VARIANT_COUNT
        ),
        "share_only_reject_variant_count": (
            SHARE_ONLY_REJECT_VARIANT_COUNT
        ),
        "zero_both_2021_halves_variant_count": (
            ZERO_BOTH_2021_HALVES_VARIANT_COUNT
        ),
        "zero_any_2021_half_variant_count": (
            ZERO_ANY_2021_HALF_VARIANT_COUNT
        ),
        "financial_only_reject_variants": [
            list(value)
            for value in FINANCIAL_ONLY_REJECT_VARIANTS
        ],
        "zero_any_2021_half_variants": [
            list(value)
            for value in ZERO_ANY_2021_HALF_VARIANTS
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
            "exp048_rerun_authorized": (
                EXP048_RERUN_AUTHORIZED
            ),
            "exp048_replacement_run_authorized": (
                EXP048_REPLACEMENT_RUN_AUTHORIZED
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
    "AGGREGATE_SELECTION_PASS_VARIANT_COUNT",
    "AGGREGATE_SELECTION_REJECT_VARIANT_COUNT",
    "BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT",
    "BROKER_MUTATION_AUTHORIZED",
    "CANDIDATE_SHARE_REJECT_VARIANT_COUNT",
    "DEC130_MERGED_COMMIT",
    "DEC130_RESULT_DECISION_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "EVALUATED_VARIANT_COUNT",
    "EXP048_REPLACEMENT_RUN_AUTHORIZED",
    "EXP048_RERUN_AUTHORIZED",
    "FINANCIAL_ONLY_REJECT_VARIANT_COUNT",
    "FINANCIAL_ONLY_REJECT_VARIANTS",
    "LIVE_ORDER_AUTHORIZED",
    "POST_RESULT_DIAGNOSTIC_DECISION",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "RELAX_STABILITY_FINANCIAL_AUTHORIZED",
    "RELAX_STABILITY_SHARE_AUTHORIZED",
    "REMOVE_2021_STABILITY_WINDOWS_AUTHORIZED",
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
    "TRADING_AUTHORIZED",
    "UNAVAILABLE_BUDGET_VARIANT_COUNT",
    "WINDOW_FINANCIAL_REJECT_VARIANT_COUNT",
    "ZERO_ANY_2021_HALF_VARIANT_COUNT",
    "ZERO_ANY_2021_HALF_VARIANTS",
    "ZERO_BOTH_2021_HALVES_VARIANT_COUNT",
    "build_regime_consensus_post_result_diagnostic_gate",
]
