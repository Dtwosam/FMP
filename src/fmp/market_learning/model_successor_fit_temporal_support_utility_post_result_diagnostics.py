from __future__ import annotations


POST_RESULT_DIAGNOSTIC_DECISION = "DEC-173"

DEC172_MERGED_COMMIT = "c06eb90953d1e38bd4db11ec6d7fc0d49ad0310c"
DEC172_RESULT_DECISION_BLOB_SHA = (
    "c9983c33792a8b143989b928a9c2af0c4ecda1e5"
)
DEC162_MERGED_COMMIT = "3d8453c544fc4b06c691d1068828ec6da9fc7110"
DEC162_DIAGNOSTIC_BLOB_SHA = (
    "00b9cbb5b0c95bd161d429d1f973d1e807f02a48"
)

EXP050_EXPERIMENT_ID = "EXP-20260924-050"
EXP051_EXPERIMENT_ID = "EXP-20260924-051"
EXP052_EXPERIMENT_ID = "EXP-20260925-052"

EXP050_EVIDENCE_FINGERPRINT = (
    "866b4a8f26553bad8c80a7b2e0e68aed"
    "b50bfa42b3c767ce91478c9dfd720023"
)
EXP051_EVIDENCE_FINGERPRINT = (
    "7dd836ed1c76c8eefd09b2b75e1eef9e"
    "875f5c6261c6fbb2cac8e3209781aaea"
)
EXP052_EVIDENCE_FINGERPRINT = (
    "34e397e027a069db9344d56546b654f00"
    "bd34aff73240e5bca1d55e7b3dab7eb"
)

TOTAL_VARIANT_COUNT = 54
AVAILABLE_VARIANT_COUNT = 28
UNAVAILABLE_VARIANT_COUNT = 26
UTILITY_ELIGIBLE_SELECTION_ROW_COUNT = 26392

EXP050_AGGREGATE_PASS_COUNT = 3
EXP051_AGGREGATE_PASS_COUNT = 1
EXP052_AGGREGATE_PASS_COUNT = 1
EXP050_STABLE_PASS_COUNT = 0
EXP051_STABLE_PASS_COUNT = 0
EXP052_STABLE_PASS_COUNT = 0

COMMON_AGGREGATE_PASS_CELL = ("USDJPY", "5m", 60)
EXP050_AGGREGATE_PASS_BUDGETS = (250, 500, 1000)
EXP051_AGGREGATE_PASS_BUDGETS = (250,)
EXP052_AGGREGATE_PASS_BUDGETS = (250,)

EXP050_BUDGET250_TOTAL_NET_PIPS = 612.8999999999933
EXP051_BUDGET250_TOTAL_NET_PIPS = 1288.1000000000117
EXP052_BUDGET250_TOTAL_NET_PIPS = 1247.500000000025

EXP050_BUDGET250_MEAN_NET_PIPS = 2.451599999999973
EXP051_BUDGET250_MEAN_NET_PIPS = 5.152400000000047
EXP052_BUDGET250_MEAN_NET_PIPS = 4.9900000000001

EXP050_BUDGET250_LONG_COUNT = 249
EXP051_BUDGET250_LONG_COUNT = 239
EXP052_BUDGET250_LONG_COUNT = 248
EXP050_BUDGET250_SHORT_COUNT = 1
EXP051_BUDGET250_SHORT_COUNT = 11
EXP052_BUDGET250_SHORT_COUNT = 2

EXP050_BUDGET250_IDENTITY_DIGEST = (
    "63b8b9d3c451df82724d55878f00cf16888060e1358724bb2d7846580cf3879c"
)
EXP051_BUDGET250_IDENTITY_DIGEST = (
    "e3d0dd4e6881726ba015b6e35d39c5ba0e08642c566adb0eeaef5dbf0e6da5cd"
)
EXP052_BUDGET250_IDENTITY_DIGEST = (
    "385770dab4c6f54900b9ebd77228e51f3fa8a48209b75e136475d145998a29cd"
)

EXP050_BUDGET250_WINDOW_COUNTS = (0, 0, 0, 250)
EXP051_BUDGET250_WINDOW_COUNTS = (0, 0, 3, 247)
EXP052_BUDGET250_WINDOW_COUNTS = (0, 0, 0, 250)

EXP050_BUDGET250_WINDOW_NET_PIPS = (
    0.0,
    0.0,
    0.0,
    612.8999999999933,
)
EXP051_BUDGET250_WINDOW_NET_PIPS = (
    0.0,
    0.0,
    -28.100000000000477,
    1316.2000000000123,
)
EXP052_BUDGET250_WINDOW_NET_PIPS = (
    0.0,
    0.0,
    0.0,
    1247.500000000025,
)

EXP050_BUDGET500_TOTAL_NET_PIPS = 247.4000000000135
EXP051_BUDGET500_TOTAL_NET_PIPS = -766.5999999999894
EXP052_BUDGET500_TOTAL_NET_PIPS = -31.50000000000273

EXP050_BUDGET1000_TOTAL_NET_PIPS = 504.3000000000052
EXP051_BUDGET1000_TOTAL_NET_PIPS = -3.200000000010732
EXP052_BUDGET1000_TOTAL_NET_PIPS = -3.200000000010732

EXP050_BUDGET500_AGGREGATE_GATE_PASSED = True
EXP051_BUDGET500_AGGREGATE_GATE_PASSED = False
EXP052_BUDGET500_AGGREGATE_GATE_PASSED = False
EXP050_BUDGET1000_AGGREGATE_GATE_PASSED = True
EXP051_BUDGET1000_AGGREGATE_GATE_PASSED = False
EXP052_BUDGET1000_AGGREGATE_GATE_PASSED = False

EXP051_BUDGET250_CALIBRATED_CUTOFF = 0.9971023442510035
EXP051_BUDGET250_RAW_CUTOFF = 1.852905399735933
EXP052_BUDGET250_SUPPORT_CUTOFF = 0.9924051599114572
EXP052_BUDGET250_POOLED_CUTOFF = 0.9967413248462105
EXP052_BUDGET250_RAW_CUTOFF = 6.412340537481511

ACCEPTED_MODEL_CANDIDATE_COUNT = 0

EXP052_RERUN_AUTHORIZED = False
EXP052_REPLACEMENT_RUN_AUTHORIZED = False
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


def build_fit_temporal_support_post_result_diagnostic_gate(
) -> dict[str, object]:
    if AVAILABLE_VARIANT_COUNT + UNAVAILABLE_VARIANT_COUNT != TOTAL_VARIANT_COUNT:
        raise ValueError("DEC-173 total-variant accounting drift")
    if UTILITY_ELIGIBLE_SELECTION_ROW_COUNT != 26392:
        raise ValueError("DEC-173 eligible-row accounting drift")
    if (
        EXP050_STABLE_PASS_COUNT
        or EXP051_STABLE_PASS_COUNT
        or EXP052_STABLE_PASS_COUNT
    ):
        raise ValueError("DEC-173 stable-pass result drift")
    if (
        EXP050_AGGREGATE_PASS_BUDGETS != (250, 500, 1000)
        or EXP051_AGGREGATE_PASS_BUDGETS != (250,)
        or EXP052_AGGREGATE_PASS_BUDGETS != (250,)
    ):
        raise ValueError("DEC-173 aggregate-pass budget identity drift")
    if len({
        EXP050_BUDGET250_IDENTITY_DIGEST,
        EXP051_BUDGET250_IDENTITY_DIGEST,
        EXP052_BUDGET250_IDENTITY_DIGEST,
    }) != 3:
        raise ValueError("DEC-173 candidate identity did not change")
    if EXP050_BUDGET250_WINDOW_COUNTS != (0, 0, 0, 250):
        raise ValueError("DEC-173 EXP-050 window distribution drift")
    if EXP051_BUDGET250_WINDOW_COUNTS != (0, 0, 3, 247):
        raise ValueError("DEC-173 EXP-051 window distribution drift")
    if EXP052_BUDGET250_WINDOW_COUNTS != (0, 0, 0, 250):
        raise ValueError("DEC-173 EXP-052 window distribution drift")
    if EXP052_BUDGET250_WINDOW_COUNTS == EXP051_BUDGET250_WINDOW_COUNTS:
        raise ValueError("DEC-173 EXP-052 temporal-support comparison drift")
    if (
        EXP052_BUDGET250_TOTAL_NET_PIPS - EXP051_BUDGET250_TOTAL_NET_PIPS
        != -40.59999999998672
    ):
        raise ValueError("DEC-173 top-250 EXP-052/051 net delta drift")
    if (
        EXP052_BUDGET250_TOTAL_NET_PIPS - EXP050_BUDGET250_TOTAL_NET_PIPS
        != 634.6000000000317
    ):
        raise ValueError("DEC-173 top-250 EXP-052/050 net delta drift")
    if (
        EXP052_BUDGET500_TOTAL_NET_PIPS - EXP051_BUDGET500_TOTAL_NET_PIPS
        != 735.0999999999867
    ):
        raise ValueError("DEC-173 budget-500 EXP-052/051 delta drift")
    if (
        EXP052_BUDGET1000_TOTAL_NET_PIPS
        - EXP051_BUDGET1000_TOTAL_NET_PIPS
        != 0.0
    ):
        raise ValueError("DEC-173 budget-1000 EXP-052/051 delta drift")
    if ACCEPTED_MODEL_CANDIDATE_COUNT != 0:
        raise ValueError("DEC-173 accepted-candidate count drift")

    return {
        "post_result_diagnostic_decision": POST_RESULT_DIAGNOSTIC_DECISION,
        "stage": "SUCCESSOR_PROTOCOL_SOURCE_OPEN",
        "diagnostic_classification": (
            "FIT_TEMPORAL_SUPPORT_DID_NOT_TRANSFER_TO_SELECTION_TIME_"
            "AND_TOP250_FINANCIAL_QUALITY_SLIGHTLY_DECLINED"
        ),
        "dec172_merged_commit": DEC172_MERGED_COMMIT,
        "dec172_result_decision_blob_sha": DEC172_RESULT_DECISION_BLOB_SHA,
        "dec162_merged_commit": DEC162_MERGED_COMMIT,
        "dec162_diagnostic_blob_sha": DEC162_DIAGNOSTIC_BLOB_SHA,
        "experiments": {
            "exp050": {
                "experiment_id": EXP050_EXPERIMENT_ID,
                "evidence_fingerprint": EXP050_EVIDENCE_FINGERPRINT,
                "aggregate_pass_count": EXP050_AGGREGATE_PASS_COUNT,
                "stable_pass_count": EXP050_STABLE_PASS_COUNT,
            },
            "exp051": {
                "experiment_id": EXP051_EXPERIMENT_ID,
                "evidence_fingerprint": EXP051_EVIDENCE_FINGERPRINT,
                "aggregate_pass_count": EXP051_AGGREGATE_PASS_COUNT,
                "stable_pass_count": EXP051_STABLE_PASS_COUNT,
            },
            "exp052": {
                "experiment_id": EXP052_EXPERIMENT_ID,
                "evidence_fingerprint": EXP052_EVIDENCE_FINGERPRINT,
                "aggregate_pass_count": EXP052_AGGREGATE_PASS_COUNT,
                "stable_pass_count": EXP052_STABLE_PASS_COUNT,
            },
        },
        "variant_accounting": {
            "total_variant_count": TOTAL_VARIANT_COUNT,
            "available_variant_count_each_experiment": AVAILABLE_VARIANT_COUNT,
            "unavailable_variant_count_each_experiment": UNAVAILABLE_VARIANT_COUNT,
            "utility_eligible_selection_row_count_each_experiment": (
                UTILITY_ELIGIBLE_SELECTION_ROW_COUNT
            ),
        },
        "common_aggregate_pass_cell": list(COMMON_AGGREGATE_PASS_CELL),
        "aggregate_pass_budgets": {
            "exp050": list(EXP050_AGGREGATE_PASS_BUDGETS),
            "exp051": list(EXP051_AGGREGATE_PASS_BUDGETS),
            "exp052": list(EXP052_AGGREGATE_PASS_BUDGETS),
        },
        "budget250_comparison": {
            "total_net_pips": {
                "exp050": EXP050_BUDGET250_TOTAL_NET_PIPS,
                "exp051": EXP051_BUDGET250_TOTAL_NET_PIPS,
                "exp052": EXP052_BUDGET250_TOTAL_NET_PIPS,
                "exp052_minus_exp051": -40.59999999998672,
                "exp052_minus_exp050": 634.6000000000317,
            },
            "mean_net_pips": {
                "exp050": EXP050_BUDGET250_MEAN_NET_PIPS,
                "exp051": EXP051_BUDGET250_MEAN_NET_PIPS,
                "exp052": EXP052_BUDGET250_MEAN_NET_PIPS,
                "exp052_minus_exp051": -0.16239999999994748,
                "exp052_minus_exp050": 2.5384000000001268,
            },
            "direction_counts": {
                "exp050": [EXP050_BUDGET250_LONG_COUNT, EXP050_BUDGET250_SHORT_COUNT],
                "exp051": [EXP051_BUDGET250_LONG_COUNT, EXP051_BUDGET250_SHORT_COUNT],
                "exp052": [EXP052_BUDGET250_LONG_COUNT, EXP052_BUDGET250_SHORT_COUNT],
            },
            "candidate_identity_digests": {
                "exp050": EXP050_BUDGET250_IDENTITY_DIGEST,
                "exp051": EXP051_BUDGET250_IDENTITY_DIGEST,
                "exp052": EXP052_BUDGET250_IDENTITY_DIGEST,
            },
            "selection_window_candidate_counts": {
                "exp050": list(EXP050_BUDGET250_WINDOW_COUNTS),
                "exp051": list(EXP051_BUDGET250_WINDOW_COUNTS),
                "exp052": list(EXP052_BUDGET250_WINDOW_COUNTS),
            },
            "selection_window_total_net_pips": {
                "exp050": list(EXP050_BUDGET250_WINDOW_NET_PIPS),
                "exp051": list(EXP051_BUDGET250_WINDOW_NET_PIPS),
                "exp052": list(EXP052_BUDGET250_WINDOW_NET_PIPS),
            },
            "exp051_cutoffs": {
                "calibrated": EXP051_BUDGET250_CALIBRATED_CUTOFF,
                "raw": EXP051_BUDGET250_RAW_CUTOFF,
            },
            "exp052_cutoffs": {
                "support": EXP052_BUDGET250_SUPPORT_CUTOFF,
                "pooled": EXP052_BUDGET250_POOLED_CUTOFF,
                "raw": EXP052_BUDGET250_RAW_CUTOFF,
            },
        },
        "broad_budget_comparison": {
            "budget_500": {
                "exp050_total_net_pips": EXP050_BUDGET500_TOTAL_NET_PIPS,
                "exp051_total_net_pips": EXP051_BUDGET500_TOTAL_NET_PIPS,
                "exp052_total_net_pips": EXP052_BUDGET500_TOTAL_NET_PIPS,
                "exp052_minus_exp051": 735.0999999999867,
                "exp052_minus_exp050": -278.90000000001623,
                "aggregate_gate_passed": [
                    EXP050_BUDGET500_AGGREGATE_GATE_PASSED,
                    EXP051_BUDGET500_AGGREGATE_GATE_PASSED,
                    EXP052_BUDGET500_AGGREGATE_GATE_PASSED,
                ],
            },
            "budget_1000": {
                "exp050_total_net_pips": EXP050_BUDGET1000_TOTAL_NET_PIPS,
                "exp051_total_net_pips": EXP051_BUDGET1000_TOTAL_NET_PIPS,
                "exp052_total_net_pips": EXP052_BUDGET1000_TOTAL_NET_PIPS,
                "exp052_minus_exp051": 0.0,
                "exp052_minus_exp050": -507.5000000000159,
                "aggregate_gate_passed": [
                    EXP050_BUDGET1000_AGGREGATE_GATE_PASSED,
                    EXP051_BUDGET1000_AGGREGATE_GATE_PASSED,
                    EXP052_BUDGET1000_AGGREGATE_GATE_PASSED,
                ],
            },
        },
        "interpretation": {
            "eligibility_changed": False,
            "budget_availability_changed": False,
            "fit_support_changed_candidate_identity": True,
            "fit_support_created_2021_candidates": False,
            "fit_support_created_2022_h1_candidates": False,
            "fit_support_improved_top250_vs_exp051": False,
            "fit_support_improved_top250_vs_exp050": True,
            "fit_support_improved_budget500_vs_exp051": True,
            "fit_support_restored_budget500_aggregate_pass": False,
            "fit_support_changed_budget1000_vs_exp051": False,
            "selection_time_transfer_demonstrated": False,
        },
        "accepted_model_candidate_count": ACCEPTED_MODEL_CANDIDATE_COUNT,
        "exp052_rerun_authorized": EXP052_RERUN_AUTHORIZED,
        "exp052_replacement_run_authorized": EXP052_REPLACEMENT_RUN_AUTHORIZED,
        "relax_stability_share_authorized": RELAX_STABILITY_SHARE_AUTHORIZED,
        "relax_stability_financial_authorized": RELAX_STABILITY_FINANCIAL_AUTHORIZED,
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
    "build_fit_temporal_support_post_result_diagnostic_gate",
]
