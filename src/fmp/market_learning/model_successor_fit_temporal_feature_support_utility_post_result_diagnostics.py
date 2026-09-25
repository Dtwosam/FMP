from __future__ import annotations


POST_RESULT_DIAGNOSTIC_DECISION = "DEC-184"

DEC183_MERGED_COMMIT = "6635c874973576b5acac7ec46ee2bf4fd2bbe1ba"
DEC183_RESULT_DECISION_BLOB_SHA = (
    "7001c2b7944bd7b75a0c70e6fb1a775ff50ba6b5"
)
DEC173_DIAGNOSTIC_BLOB_SHA = (
    "af57f0eb6c00e18bb587203dc81530702e657e87"
)

TOTAL_VARIANT_COUNT = 54
AVAILABLE_VARIANT_COUNT = 28
UNAVAILABLE_VARIANT_COUNT = 26
UTILITY_ELIGIBLE_SELECTION_ROW_COUNT = 26392

EXP050_EVIDENCE_FINGERPRINT = (
    "866b4a8f26553bad8c80a7b2e0e68aed"
    "b50bfa42b3c767ce91478c9dfd720023"
)
EXP051_EVIDENCE_FINGERPRINT = (
    "7dd836ed1c76c8eefd09b2b75e1eef9e"
    "875f5c6261c6fbb2cac8e3209781aaea"
)
EXP052_EVIDENCE_FINGERPRINT = (
    "34e397e027a069db9344d56546b654f0"
    "0bd34aff73240e5bca1d55e7b3dab7eb"
)
EXP053_EVIDENCE_FINGERPRINT = (
    "cb32abc0e4ecd3df8b639d77b6770e25"
    "5aa87701eb19180dfdfb25c37dfe48e1"
)

EXP050_AGGREGATE_PASS_COUNT = 3
EXP051_AGGREGATE_PASS_COUNT = 1
EXP052_AGGREGATE_PASS_COUNT = 1
EXP053_AGGREGATE_PASS_COUNT = 10

EXP050_STABLE_PASS_COUNT = 0
EXP051_STABLE_PASS_COUNT = 0
EXP052_STABLE_PASS_COUNT = 0
EXP053_STABLE_PASS_COUNT = 0

EXP053_CELLS_WITH_AGGREGATE_PASS_COUNT = 6
EXP053_HORIZON_60_PASS_COUNT = 2
EXP053_HORIZON_240_PASS_COUNT = 8
EXP053_GBPUSD_PASS_COUNT = 4
EXP053_USDJPY_PASS_COUNT = 6
EXP053_EURUSD_PASS_COUNT = 0

EXP053_AGGREGATE_PASS_VARIANTS = (
    ("GBPUSD", "15m", 240, 250),
    ("GBPUSD", "5m", 240, 250),
    ("GBPUSD", "5m", 240, 500),
    ("GBPUSD", "5m", 240, 1000),
    ("USDJPY", "15m", 60, 250),
    ("USDJPY", "15m", 240, 250),
    ("USDJPY", "15m", 240, 500),
    ("USDJPY", "15m", 240, 1000),
    ("USDJPY", "1h", 240, 250),
    ("USDJPY", "5m", 60, 1000),
)

EXP052_AGGREGATE_PASS_VARIANT = ("USDJPY", "5m", 60, 250)
EXP053_RETAINS_EXP052_PASS_VARIANT = False

EXP053_ZERO_2021_H1_PASS_VARIANT_COUNT = 5
EXP053_2021_SHARE_REJECT_VARIANT_COUNT = 9
EXP053_2022_H1_FINANCIAL_REJECT_VARIANT_COUNT = 9
EXP053_ANY_2022_H1_FINANCIAL_PASS_VARIANT_COUNT = 1

EXP053_GBPUSD_5M_240_BUDGET500_WINDOW_COUNTS = (
    57, 33, 131, 279
)
EXP053_GBPUSD_5M_240_BUDGET500_WINDOW_NET_PIPS = (
    1043.7000000000012,
    323.7999999999927,
    -875.1000000000075,
    646.200000000002,
)

EXP053_USDJPY_15M_240_BUDGET250_WINDOW_COUNTS = (
    0, 27, 88, 135
)
EXP053_USDJPY_15M_240_BUDGET250_WINDOW_NET_PIPS = (
    0.0,
    395.69999999999897,
    -558.1999999999983,
    1078.6999999999916,
)

EXP053_USDJPY_5M_60_BUDGET1000_WINDOW_COUNTS = (
    0, 3, 130, 867
)
EXP053_USDJPY_5M_60_BUDGET1000_TOTAL_NET_PIPS = (
    485.19999999998333
)

EXP052_USDJPY_5M_60_BUDGET250_TOTAL_NET_PIPS = (
    1247.500000000025
)
EXP052_USDJPY_5M_60_BUDGET500_TOTAL_NET_PIPS = (
    -31.50000000000273
)
EXP052_USDJPY_5M_60_BUDGET1000_TOTAL_NET_PIPS = (
    -3.200000000010732
)

ACCEPTED_MODEL_CANDIDATE_COUNT = 0

EXP053_RERUN_AUTHORIZED = False
EXP053_REPLACEMENT_RUN_AUTHORIZED = False
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


def build_fit_temporal_feature_support_post_result_diagnostic_gate(
) -> dict[str, object]:
    if AVAILABLE_VARIANT_COUNT + UNAVAILABLE_VARIANT_COUNT != TOTAL_VARIANT_COUNT:
        raise ValueError("DEC-184 total-variant accounting drift")
    if UTILITY_ELIGIBLE_SELECTION_ROW_COUNT != 26392:
        raise ValueError("DEC-184 eligible-row accounting drift")
    if len(EXP053_AGGREGATE_PASS_VARIANTS) != EXP053_AGGREGATE_PASS_COUNT:
        raise ValueError("DEC-184 EXP-053 aggregate-pass identity drift")
    if len({value[:3] for value in EXP053_AGGREGATE_PASS_VARIANTS}) != (
        EXP053_CELLS_WITH_AGGREGATE_PASS_COUNT
    ):
        raise ValueError("DEC-184 EXP-053 aggregate-pass cell count drift")
    if sum(value[2] == 60 for value in EXP053_AGGREGATE_PASS_VARIANTS) != (
        EXP053_HORIZON_60_PASS_COUNT
    ):
        raise ValueError("DEC-184 horizon-60 pass count drift")
    if sum(value[2] == 240 for value in EXP053_AGGREGATE_PASS_VARIANTS) != (
        EXP053_HORIZON_240_PASS_COUNT
    ):
        raise ValueError("DEC-184 horizon-240 pass count drift")
    if sum(value[0] == "GBPUSD" for value in EXP053_AGGREGATE_PASS_VARIANTS) != (
        EXP053_GBPUSD_PASS_COUNT
    ):
        raise ValueError("DEC-184 GBPUSD pass count drift")
    if sum(value[0] == "USDJPY" for value in EXP053_AGGREGATE_PASS_VARIANTS) != (
        EXP053_USDJPY_PASS_COUNT
    ):
        raise ValueError("DEC-184 USDJPY pass count drift")
    if sum(value[0] == "EURUSD" for value in EXP053_AGGREGATE_PASS_VARIANTS) != (
        EXP053_EURUSD_PASS_COUNT
    ):
        raise ValueError("DEC-184 EURUSD pass count drift")
    if EXP052_AGGREGATE_PASS_VARIANT in EXP053_AGGREGATE_PASS_VARIANTS:
        raise ValueError(
            "DEC-184 feature-support ranking unexpectedly retained "
            "the exact EXP-052 aggregate-pass variant"
        )
    if EXP053_RETAINS_EXP052_PASS_VARIANT is not False:
        raise ValueError("DEC-184 EXP-052 pass-retention flag drift")
    if any(
        count != 0
        for count in (
            EXP050_STABLE_PASS_COUNT,
            EXP051_STABLE_PASS_COUNT,
            EXP052_STABLE_PASS_COUNT,
            EXP053_STABLE_PASS_COUNT,
        )
    ):
        raise ValueError("DEC-184 stable-pass count drift")
    if EXP053_2021_SHARE_REJECT_VARIANT_COUNT != 9:
        raise ValueError("DEC-184 2021 share-reject count drift")
    if EXP053_2022_H1_FINANCIAL_REJECT_VARIANT_COUNT != 9:
        raise ValueError("DEC-184 2022-H1 financial-reject count drift")
    if EXP053_ANY_2022_H1_FINANCIAL_PASS_VARIANT_COUNT != 1:
        raise ValueError("DEC-184 2022-H1 pass count drift")
    if ACCEPTED_MODEL_CANDIDATE_COUNT != 0:
        raise ValueError("DEC-184 accepted-candidate count drift")

    return {
        "post_result_diagnostic_decision": POST_RESULT_DIAGNOSTIC_DECISION,
        "stage": "SUCCESSOR_PROTOCOL_SOURCE_OPEN",
        "diagnostic_classification": (
            "FEATURE_SUPPORT_BROADENED_AGGREGATE_PASSES_"
            "BUT_DID_NOT_CLEAR_TEMPORAL_STABILITY"
        ),
        "dec183_merged_commit": DEC183_MERGED_COMMIT,
        "dec183_result_decision_blob_sha": DEC183_RESULT_DECISION_BLOB_SHA,
        "dec173_diagnostic_blob_sha": DEC173_DIAGNOSTIC_BLOB_SHA,
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
                "evidence_fingerprint": EXP050_EVIDENCE_FINGERPRINT,
                "aggregate_pass_count": EXP050_AGGREGATE_PASS_COUNT,
                "stable_pass_count": EXP050_STABLE_PASS_COUNT,
            },
            "exp051": {
                "evidence_fingerprint": EXP051_EVIDENCE_FINGERPRINT,
                "aggregate_pass_count": EXP051_AGGREGATE_PASS_COUNT,
                "stable_pass_count": EXP051_STABLE_PASS_COUNT,
            },
            "exp052": {
                "evidence_fingerprint": EXP052_EVIDENCE_FINGERPRINT,
                "aggregate_pass_count": EXP052_AGGREGATE_PASS_COUNT,
                "stable_pass_count": EXP052_STABLE_PASS_COUNT,
            },
            "exp053": {
                "evidence_fingerprint": EXP053_EVIDENCE_FINGERPRINT,
                "aggregate_pass_count": EXP053_AGGREGATE_PASS_COUNT,
                "stable_pass_count": EXP053_STABLE_PASS_COUNT,
                "cells_with_aggregate_pass_count": (
                    EXP053_CELLS_WITH_AGGREGATE_PASS_COUNT
                ),
            },
        },
        "exp053_aggregate_pass_distribution": {
            "variants": [
                list(value)
                for value in EXP053_AGGREGATE_PASS_VARIANTS
            ],
            "horizon_60_count": EXP053_HORIZON_60_PASS_COUNT,
            "horizon_240_count": EXP053_HORIZON_240_PASS_COUNT,
            "gbpusd_count": EXP053_GBPUSD_PASS_COUNT,
            "usdjpy_count": EXP053_USDJPY_PASS_COUNT,
            "eurusd_count": EXP053_EURUSD_PASS_COUNT,
            "retains_exact_exp052_pass_variant": (
                EXP053_RETAINS_EXP052_PASS_VARIANT
            ),
        },
        "temporal_stability_diagnostics": {
            "zero_2021_h1_pass_variant_count": (
                EXP053_ZERO_2021_H1_PASS_VARIANT_COUNT
            ),
            "2021_share_reject_variant_count": (
                EXP053_2021_SHARE_REJECT_VARIANT_COUNT
            ),
            "2022_h1_financial_reject_variant_count": (
                EXP053_2022_H1_FINANCIAL_REJECT_VARIANT_COUNT
            ),
            "2022_h1_financial_pass_variant_count": (
                EXP053_ANY_2022_H1_FINANCIAL_PASS_VARIANT_COUNT
            ),
            "representative_gbpusd_5m_240_budget500": {
                "window_candidate_counts": list(
                    EXP053_GBPUSD_5M_240_BUDGET500_WINDOW_COUNTS
                ),
                "window_total_net_pips": list(
                    EXP053_GBPUSD_5M_240_BUDGET500_WINDOW_NET_PIPS
                ),
            },
            "representative_usdjpy_15m_240_budget250": {
                "window_candidate_counts": list(
                    EXP053_USDJPY_15M_240_BUDGET250_WINDOW_COUNTS
                ),
                "window_total_net_pips": list(
                    EXP053_USDJPY_15M_240_BUDGET250_WINDOW_NET_PIPS
                ),
            },
            "representative_usdjpy_5m_60_budget1000": {
                "window_candidate_counts": list(
                    EXP053_USDJPY_5M_60_BUDGET1000_WINDOW_COUNTS
                ),
                "total_net_pips": (
                    EXP053_USDJPY_5M_60_BUDGET1000_TOTAL_NET_PIPS
                ),
            },
        },
        "common_cell_budget_shift": {
            "cell": ["USDJPY", "5m", 60],
            "exp052_aggregate_pass_budget": 250,
            "exp053_aggregate_pass_budget": 1000,
            "exp052_total_net_pips": {
                "250": EXP052_USDJPY_5M_60_BUDGET250_TOTAL_NET_PIPS,
                "500": EXP052_USDJPY_5M_60_BUDGET500_TOTAL_NET_PIPS,
                "1000": EXP052_USDJPY_5M_60_BUDGET1000_TOTAL_NET_PIPS,
            },
            "exp053_budget1000_total_net_pips": (
                EXP053_USDJPY_5M_60_BUDGET1000_TOTAL_NET_PIPS
            ),
        },
        "interpretation": {
            "eligibility_changed": False,
            "budget_availability_changed": False,
            "feature_support_broadened_aggregate_passes": True,
            "feature_support_broadened_pass_cells": True,
            "feature_support_created_some_2021_candidates": True,
            "feature_support_removed_all_2021_share_failures": False,
            "feature_support_removed_2022_h1_financial_instability": False,
            "selection_time_temporal_stability_demonstrated": False,
            "accepted_model_candidate_created": False,
        },
        "accepted_model_candidate_count": ACCEPTED_MODEL_CANDIDATE_COUNT,
        "exp053_rerun_authorized": EXP053_RERUN_AUTHORIZED,
        "exp053_replacement_run_authorized": EXP053_REPLACEMENT_RUN_AUTHORIZED,
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
    "build_fit_temporal_feature_support_post_result_diagnostic_gate",
]
