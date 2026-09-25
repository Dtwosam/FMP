from __future__ import annotations


POST_RESULT_DIAGNOSTIC_DECISION = "DEC-197"

DEC196_MERGED_COMMIT = "fe84544b7acd3ce3a2e322b68b1ca723c216ce45"
DEC196_RESULT_DECISION_BLOB_SHA = (
    "17235435604bc5c0bd8950037bd8c49a0c6fb81a"
)
DEC184_DIAGNOSTIC_BLOB_SHA = (
    "a2fce33c15422abeb8323a6e3014ebf5a3a52794"
)

TOTAL_VARIANT_COUNT = 54
AVAILABLE_VARIANT_COUNT = 28
UNAVAILABLE_VARIANT_COUNT = 26
UTILITY_ELIGIBLE_SELECTION_ROW_COUNT = 26392

EXP050_AGGREGATE_PASS_COUNT = 3
EXP051_AGGREGATE_PASS_COUNT = 1
EXP052_AGGREGATE_PASS_COUNT = 1
EXP053_AGGREGATE_PASS_COUNT = 10
EXP054_AGGREGATE_PASS_COUNT = 2

EXP050_STABLE_PASS_COUNT = 0
EXP051_STABLE_PASS_COUNT = 0
EXP052_STABLE_PASS_COUNT = 0
EXP053_STABLE_PASS_COUNT = 0
EXP054_STABLE_PASS_COUNT = 0

EXP053_EVIDENCE_FINGERPRINT = (
    "cb32abc0e4ecd3df8b639d77b6770e25"
    "5aa87701eb19180dfdfb25c37dfe48e1"
)
EXP054_EVIDENCE_FINGERPRINT = (
    "307b576f06c6aa2fb01a267232a0de55"
    "3bfa79c1bdbe6bf5d55b2bfc3b40787c"
)

EXP054_AGGREGATE_PASS_VARIANTS = (
    ("USDJPY", "5m", 60, 250),
    ("USDJPY", "5m", 60, 1000),
)
EXP054_CELLS_WITH_AGGREGATE_PASS_COUNT = 1
EXP054_HORIZON_60_PASS_COUNT = 2
EXP054_HORIZON_240_PASS_COUNT = 0
EXP054_USDJPY_PASS_COUNT = 2
EXP054_GBPUSD_PASS_COUNT = 0
EXP054_EURUSD_PASS_COUNT = 0

EXP052_COMMON_PASS_VARIANT = ("USDJPY", "5m", 60, 250)
EXP053_COMMON_PASS_VARIANT = ("USDJPY", "5m", 60, 1000)
EXP054_RESTORES_EXP052_COMMON_PASS = True
EXP054_RETAINS_EXP053_COMMON_PASS = True

EXP053_USDJPY_5M_60_AGGREGATE_NET_PIPS = {
    250: -352.00000000002524,
    500: -108.60000000003674,
    1000: 485.19999999998333,
}
EXP054_USDJPY_5M_60_AGGREGATE_NET_PIPS = {
    250: 644.3000000000043,
    500: -7.7000000000080036,
    1000: 302.2999999999838,
}

EXP053_USDJPY_5M_60_BUDGET1000_WINDOW_COUNTS = (
    0, 3, 130, 867
)
EXP053_USDJPY_5M_60_BUDGET1000_WINDOW_NET_PIPS = (
    0.0,
    21.199999999999022,
    -67.19999999999004,
    531.1999999999744,
)
EXP054_USDJPY_5M_60_BUDGET250_WINDOW_COUNTS = (
    0, 0, 0, 250
)
EXP054_USDJPY_5M_60_BUDGET250_WINDOW_NET_PIPS = (
    0.0,
    0.0,
    0.0,
    644.3000000000043,
)
EXP054_USDJPY_5M_60_BUDGET1000_WINDOW_COUNTS = (
    0, 3, 72, 925
)
EXP054_USDJPY_5M_60_BUDGET1000_WINDOW_NET_PIPS = (
    0.0,
    21.199999999999022,
    510.5000000000031,
    -229.40000000001828,
)

ACCEPTED_MODEL_CANDIDATE_COUNT = 0

EXP054_RERUN_AUTHORIZED = False
EXP054_REPLACEMENT_RUN_AUTHORIZED = False
RELAX_STABILITY_SHARE_AUTHORIZED = False
RELAX_STABILITY_FINANCIAL_AUTHORIZED = False
REMOVE_EARLY_STABILITY_WINDOWS_AUTHORIZED = False
USE_SELECTION_OUTCOMES_IN_RANKING_AUTHORIZED = False
RECALIBRATE_ON_SELECTION_WINDOWS_AUTHORIZED = False
ADD_SELECTION_WINDOW_QUOTAS_AUTHORIZED = False

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


def build_fit_temporal_residual_bound_post_result_diagnostic_gate(
) -> dict[str, object]:
    if AVAILABLE_VARIANT_COUNT + UNAVAILABLE_VARIANT_COUNT != TOTAL_VARIANT_COUNT:
        raise ValueError("DEC-197 total-variant accounting drift")
    if UTILITY_ELIGIBLE_SELECTION_ROW_COUNT != 26392:
        raise ValueError("DEC-197 eligible-row accounting drift")
    if len(EXP054_AGGREGATE_PASS_VARIANTS) != EXP054_AGGREGATE_PASS_COUNT:
        raise ValueError("DEC-197 EXP-054 aggregate-pass identity drift")
    if len({value[:3] for value in EXP054_AGGREGATE_PASS_VARIANTS}) != (
        EXP054_CELLS_WITH_AGGREGATE_PASS_COUNT
    ):
        raise ValueError("DEC-197 EXP-054 aggregate-pass cell count drift")
    if sum(value[2] == 60 for value in EXP054_AGGREGATE_PASS_VARIANTS) != (
        EXP054_HORIZON_60_PASS_COUNT
    ):
        raise ValueError("DEC-197 horizon-60 pass count drift")
    if sum(value[2] == 240 for value in EXP054_AGGREGATE_PASS_VARIANTS) != (
        EXP054_HORIZON_240_PASS_COUNT
    ):
        raise ValueError("DEC-197 horizon-240 pass count drift")
    if sum(value[0] == "USDJPY" for value in EXP054_AGGREGATE_PASS_VARIANTS) != (
        EXP054_USDJPY_PASS_COUNT
    ):
        raise ValueError("DEC-197 USDJPY pass count drift")
    if sum(value[0] == "GBPUSD" for value in EXP054_AGGREGATE_PASS_VARIANTS) != (
        EXP054_GBPUSD_PASS_COUNT
    ):
        raise ValueError("DEC-197 GBPUSD pass count drift")
    if sum(value[0] == "EURUSD" for value in EXP054_AGGREGATE_PASS_VARIANTS) != (
        EXP054_EURUSD_PASS_COUNT
    ):
        raise ValueError("DEC-197 EURUSD pass count drift")
    if EXP052_COMMON_PASS_VARIANT not in EXP054_AGGREGATE_PASS_VARIANTS:
        raise ValueError("DEC-197 EXP-052 common pass was not restored")
    if EXP053_COMMON_PASS_VARIANT not in EXP054_AGGREGATE_PASS_VARIANTS:
        raise ValueError("DEC-197 EXP-053 common pass was not retained")
    if any(
        value != 0
        for value in (
            EXP050_STABLE_PASS_COUNT,
            EXP051_STABLE_PASS_COUNT,
            EXP052_STABLE_PASS_COUNT,
            EXP053_STABLE_PASS_COUNT,
            EXP054_STABLE_PASS_COUNT,
        )
    ):
        raise ValueError("DEC-197 stable-pass count drift")
    if ACCEPTED_MODEL_CANDIDATE_COUNT != 0:
        raise ValueError("DEC-197 accepted-candidate count drift")

    return {
        "post_result_diagnostic_decision": POST_RESULT_DIAGNOSTIC_DECISION,
        "stage": "SUCCESSOR_PROTOCOL_SOURCE_OPEN",
        "diagnostic_classification": (
            "RESIDUAL_BOUND_NARROWED_AGGREGATE_PASSES_AND_IMPROVED_"
            "SOME_DOWNSIDE_WINDOWS_BUT_DID_NOT_CREATE_TEMPORAL_BREADTH"
        ),
        "dec196_merged_commit": DEC196_MERGED_COMMIT,
        "dec196_result_decision_blob_sha": DEC196_RESULT_DECISION_BLOB_SHA,
        "dec184_diagnostic_blob_sha": DEC184_DIAGNOSTIC_BLOB_SHA,
        "variant_accounting": {
            "total_variant_count": TOTAL_VARIANT_COUNT,
            "available_variant_count_each_experiment": AVAILABLE_VARIANT_COUNT,
            "unavailable_variant_count_each_experiment": UNAVAILABLE_VARIANT_COUNT,
            "utility_eligible_selection_row_count_each_experiment": (
                UTILITY_ELIGIBLE_SELECTION_ROW_COUNT
            ),
        },
        "experiments": {
            "exp050": {
                "aggregate_pass_count": EXP050_AGGREGATE_PASS_COUNT,
                "stable_pass_count": EXP050_STABLE_PASS_COUNT,
            },
            "exp051": {
                "aggregate_pass_count": EXP051_AGGREGATE_PASS_COUNT,
                "stable_pass_count": EXP051_STABLE_PASS_COUNT,
            },
            "exp052": {
                "aggregate_pass_count": EXP052_AGGREGATE_PASS_COUNT,
                "stable_pass_count": EXP052_STABLE_PASS_COUNT,
            },
            "exp053": {
                "evidence_fingerprint": EXP053_EVIDENCE_FINGERPRINT,
                "aggregate_pass_count": EXP053_AGGREGATE_PASS_COUNT,
                "stable_pass_count": EXP053_STABLE_PASS_COUNT,
            },
            "exp054": {
                "evidence_fingerprint": EXP054_EVIDENCE_FINGERPRINT,
                "aggregate_pass_count": EXP054_AGGREGATE_PASS_COUNT,
                "stable_pass_count": EXP054_STABLE_PASS_COUNT,
                "cells_with_aggregate_pass_count": (
                    EXP054_CELLS_WITH_AGGREGATE_PASS_COUNT
                ),
            },
        },
        "exp054_aggregate_pass_distribution": {
            "variants": [
                list(value) for value in EXP054_AGGREGATE_PASS_VARIANTS
            ],
            "horizon_60_count": EXP054_HORIZON_60_PASS_COUNT,
            "horizon_240_count": EXP054_HORIZON_240_PASS_COUNT,
            "usdjpy_count": EXP054_USDJPY_PASS_COUNT,
            "gbpusd_count": EXP054_GBPUSD_PASS_COUNT,
            "eurusd_count": EXP054_EURUSD_PASS_COUNT,
            "restores_exact_exp052_common_pass": (
                EXP054_RESTORES_EXP052_COMMON_PASS
            ),
            "retains_exact_exp053_common_pass": (
                EXP054_RETAINS_EXP053_COMMON_PASS
            ),
        },
        "common_cell_comparison": {
            "cell": ["USDJPY", "5m", 60],
            "exp053_aggregate_total_net_pips": {
                str(key): value
                for key, value in EXP053_USDJPY_5M_60_AGGREGATE_NET_PIPS.items()
            },
            "exp054_aggregate_total_net_pips": {
                str(key): value
                for key, value in EXP054_USDJPY_5M_60_AGGREGATE_NET_PIPS.items()
            },
            "exp053_budget1000_window_candidate_counts": list(
                EXP053_USDJPY_5M_60_BUDGET1000_WINDOW_COUNTS
            ),
            "exp053_budget1000_window_total_net_pips": list(
                EXP053_USDJPY_5M_60_BUDGET1000_WINDOW_NET_PIPS
            ),
            "exp054_budget250_window_candidate_counts": list(
                EXP054_USDJPY_5M_60_BUDGET250_WINDOW_COUNTS
            ),
            "exp054_budget250_window_total_net_pips": list(
                EXP054_USDJPY_5M_60_BUDGET250_WINDOW_NET_PIPS
            ),
            "exp054_budget1000_window_candidate_counts": list(
                EXP054_USDJPY_5M_60_BUDGET1000_WINDOW_COUNTS
            ),
            "exp054_budget1000_window_total_net_pips": list(
                EXP054_USDJPY_5M_60_BUDGET1000_WINDOW_NET_PIPS
            ),
        },
        "interpretation": {
            "eligibility_changed": False,
            "budget_availability_changed": False,
            "aggregate_pass_breadth_improved_vs_exp053": False,
            "top250_aggregate_financial_quality_improved_vs_exp053": True,
            "top250_temporal_breadth_created": False,
            "budget1000_2022_h1_financial_sign_improved": True,
            "budget1000_2022_h1_candidate_share_improved": False,
            "budget1000_2022_h2_financial_quality_improved": False,
            "residual_bound_created_selection_time_temporal_stability": False,
            "accepted_model_candidate_created": False,
        },
        "accepted_model_candidate_count": ACCEPTED_MODEL_CANDIDATE_COUNT,
        "exp054_rerun_authorized": EXP054_RERUN_AUTHORIZED,
        "exp054_replacement_run_authorized": EXP054_REPLACEMENT_RUN_AUTHORIZED,
        "relax_stability_share_authorized": RELAX_STABILITY_SHARE_AUTHORIZED,
        "relax_stability_financial_authorized": (
            RELAX_STABILITY_FINANCIAL_AUTHORIZED
        ),
        "remove_early_stability_windows_authorized": (
            REMOVE_EARLY_STABILITY_WINDOWS_AUTHORIZED
        ),
        "use_selection_outcomes_in_ranking_authorized": (
            USE_SELECTION_OUTCOMES_IN_RANKING_AUTHORIZED
        ),
        "recalibrate_on_selection_windows_authorized": (
            RECALIBRATE_ON_SELECTION_WINDOWS_AUTHORIZED
        ),
        "add_selection_window_quotas_authorized": (
            ADD_SELECTION_WINDOW_QUOTAS_AUTHORIZED
        ),
        "successor_protocol_source_open_authorized": (
            SUCCESSOR_PROTOCOL_SOURCE_OPEN_AUTHORIZED
        ),
        "successor_result_execution_authorized": (
            SUCCESSOR_RESULT_EXECUTION_AUTHORIZED
        ),
        "successor_model_fit_authorized": SUCCESSOR_MODEL_FIT_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "shadow_authorized": SHADOW_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
    }


__all__ = [
    "POST_RESULT_DIAGNOSTIC_DECISION",
    "build_fit_temporal_residual_bound_post_result_diagnostic_gate",
]
