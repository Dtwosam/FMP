from __future__ import annotations


POST_RESULT_DIAGNOSTIC_DECISION = "DEC-230"

DEC229_MERGED_COMMIT = "7a2c53712a85f69e106a707dc1245e664c68bcbb"
DEC229_RESULT_DECISION_BLOB_SHA = (
    "185e2cdf089cb6f1a12619af58fd32860366498f"
)
DEC208_DIAGNOSTIC_BLOB_SHA = (
    "5ff61be317b225d9d7ec656b4789c4561d52b522"
)
DEC207_RESULT_DECISION_BLOB_SHA = (
    "e2226117ebf10b762557d43549390c46c243bbae"
)

TOTAL_VARIANT_COUNT = 54
AVAILABLE_VARIANT_COUNT = 28
UNAVAILABLE_VARIANT_COUNT = 26
UTILITY_ELIGIBLE_SELECTION_ROW_COUNT = 26392

EXP055_EVIDENCE_FINGERPRINT = (
    "f3a386dad7f23ac9d6867d030ac90e08"
    "84f3ab658c9ffecce8647048037d2510"
)
EXP057_EVIDENCE_FINGERPRINT = (
    "4bf67108e0df38d4f213d08898fadd33"
    "8285ac7a2ce56920b61e4dba0f3eec4c"
)

EXP055_AGGREGATE_PASS_COUNT = 2
EXP057_AGGREGATE_PASS_COUNT = 3
EXP055_STABLE_PASS_COUNT = 0
EXP057_STABLE_PASS_COUNT = 0

EXP055_AGGREGATE_PASS_VARIANTS = (
    ("USDJPY", "5m", 60, 250),
    ("USDJPY", "5m", 60, 1000),
)
EXP057_AGGREGATE_PASS_VARIANTS = (
    ("USDJPY", "5m", 60, 250),
    ("USDJPY", "5m", 60, 500),
    ("USDJPY", "5m", 60, 1000),
)

EXP055_USDJPY_5M_60_AGGREGATE_NET_PIPS = {
    250: 576.6000000000067,
    500: -470.799999999977,
    1000: 40.50000000001137,
}
EXP057_USDJPY_5M_60_AGGREGATE_NET_PIPS = {
    250: 301.40000000000646,
    500: 88.99999999999636,
    1000: 362.0999999999858,
}

EXP055_BUDGET250_WINDOW_COUNTS = (0, 0, 0, 251)
EXP057_BUDGET250_WINDOW_COUNTS = (0, 0, 0, 250)
EXP055_BUDGET250_WINDOW_NET_PIPS = (
    0.0,
    0.0,
    0.0,
    576.6000000000067,
)
EXP057_BUDGET250_WINDOW_NET_PIPS = (
    0.0,
    0.0,
    0.0,
    301.40000000000646,
)

EXP057_BUDGET500_WINDOW_COUNTS = (0, 0, 3, 497)
EXP057_BUDGET500_WINDOW_NET_PIPS = (
    0.0,
    0.0,
    27.099999999998772,
    61.89999999999691,
)

EXP055_BUDGET1000_WINDOW_COUNTS = (0, 1, 83, 916)
EXP057_BUDGET1000_WINDOW_COUNTS = (0, 1, 73, 926)
EXP055_BUDGET1000_WINDOW_NET_PIPS = (
    0.0,
    -2.800000000000068,
    464.30000000001553,
    -421.0000000000041,
)
EXP057_BUDGET1000_WINDOW_NET_PIPS = (
    0.0,
    -2.800000000000068,
    522.6000000000031,
    -157.700000000018,
)

EXP057_BUDGET250_LOWER_TAIL_CUTOFF = -0.6255004829563466
EXP057_BUDGET500_LOWER_TAIL_CUTOFF = -2.6367081864599355
EXP057_BUDGET1000_LOWER_TAIL_CUTOFF = -4.902851329338788

EXP055_BUDGET250_RESIDUAL_BREADTH_CUTOFF = 10.0 / 12.0
EXP057_BUDGET250_RESIDUAL_BREADTH_CUTOFF = 10.0 / 12.0
EXP055_BUDGET500_RESIDUAL_BREADTH_CUTOFF = 7.0 / 12.0
EXP057_BUDGET500_RESIDUAL_BREADTH_CUTOFF = 0.5
EXP055_BUDGET1000_RESIDUAL_BREADTH_CUTOFF = 0.0
EXP057_BUDGET1000_RESIDUAL_BREADTH_CUTOFF = 0.0

AVAILABLE_VARIANT_NET_PIPS_IMPROVED_COUNT = 15
AVAILABLE_VARIANT_NET_PIPS_WORSENED_COUNT = 13
AVAILABLE_VARIANT_NET_PIPS_UNCHANGED_COUNT = 0

ACCEPTED_MODEL_CANDIDATE_COUNT = 0

EXP057_RERUN_AUTHORIZED = False
EXP057_REPLACEMENT_RUN_AUTHORIZED = False
RELAX_STABILITY_SHARE_AUTHORIZED = False
RELAX_STABILITY_FINANCIAL_AUTHORIZED = False
REMOVE_EARLY_STABILITY_WINDOWS_AUTHORIZED = False
USE_SELECTION_OUTCOMES_IN_RANKING_AUTHORIZED = False
RECALIBRATE_ON_SELECTION_WINDOWS_AUTHORIZED = False
ADD_SELECTION_WINDOW_QUOTAS_AUTHORIZED = False
RETUNE_LOWER_TAIL_ON_SELECTION_AUTHORIZED = False

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


def build_fit_temporal_residual_lower_tail_repair_post_result_diagnostic_gate(
) -> dict[str, object]:
    if AVAILABLE_VARIANT_COUNT + UNAVAILABLE_VARIANT_COUNT != TOTAL_VARIANT_COUNT:
        raise ValueError("DEC-230 total-variant accounting drift")
    if UTILITY_ELIGIBLE_SELECTION_ROW_COUNT != 26392:
        raise ValueError("DEC-230 eligible-row accounting drift")
    if len(EXP055_AGGREGATE_PASS_VARIANTS) != EXP055_AGGREGATE_PASS_COUNT:
        raise ValueError("DEC-230 EXP-055 aggregate-pass count drift")
    if len(EXP057_AGGREGATE_PASS_VARIANTS) != EXP057_AGGREGATE_PASS_COUNT:
        raise ValueError("DEC-230 EXP-057 aggregate-pass count drift")
    if EXP055_STABLE_PASS_COUNT != 0 or EXP057_STABLE_PASS_COUNT != 0:
        raise ValueError("DEC-230 stable-pass count drift")
    if (
        AVAILABLE_VARIANT_NET_PIPS_IMPROVED_COUNT
        + AVAILABLE_VARIANT_NET_PIPS_WORSENED_COUNT
        + AVAILABLE_VARIANT_NET_PIPS_UNCHANGED_COUNT
        != AVAILABLE_VARIANT_COUNT
    ):
        raise ValueError("DEC-230 available-variant comparison drift")
    if set(EXP055_AGGREGATE_PASS_VARIANTS) - set(EXP057_AGGREGATE_PASS_VARIANTS):
        raise ValueError("DEC-230 predecessor aggregate pass was lost")
    added = set(EXP057_AGGREGATE_PASS_VARIANTS) - set(
        EXP055_AGGREGATE_PASS_VARIANTS
    )
    if added != {("USDJPY", "5m", 60, 500)}:
        raise ValueError("DEC-230 added aggregate-pass identity drift")
    if EXP057_BUDGET250_WINDOW_COUNTS[:3] != (0, 0, 0):
        raise ValueError("DEC-230 budget-250 concentration drift")
    if EXP057_BUDGET500_WINDOW_COUNTS[:2] != (0, 0):
        raise ValueError("DEC-230 budget-500 early-window concentration drift")
    if EXP057_BUDGET500_WINDOW_COUNTS[2] >= 50:
        raise ValueError("DEC-230 budget-500 2022-H1 share unexpectedly clears floor")
    if EXP057_BUDGET1000_WINDOW_COUNTS[2] >= 100:
        raise ValueError("DEC-230 budget-1000 2022-H1 share unexpectedly clears floor")
    if EXP057_BUDGET1000_WINDOW_COUNTS[3] <= EXP055_BUDGET1000_WINDOW_COUNTS[3]:
        raise ValueError("DEC-230 budget-1000 late-window concentration drift")
    if ACCEPTED_MODEL_CANDIDATE_COUNT != 0:
        raise ValueError("DEC-230 accepted-candidate count drift")

    return {
        "post_result_diagnostic_decision": POST_RESULT_DIAGNOSTIC_DECISION,
        "stage": "SUCCESSOR_PROTOCOL_SOURCE_OPEN",
        "diagnostic_classification": (
            "LOWER_TAIL_RANKING_CHANGED_CANDIDATE_FINANCIAL_MIX_"
            "AND_ADDED_AGGREGATE_PASS_BUT_DID_NOT_CREATE_TEMPORAL_STABILITY"
        ),
        "dec229_merged_commit": DEC229_MERGED_COMMIT,
        "dec229_result_decision_blob_sha": DEC229_RESULT_DECISION_BLOB_SHA,
        "dec208_diagnostic_blob_sha": DEC208_DIAGNOSTIC_BLOB_SHA,
        "dec207_result_decision_blob_sha": DEC207_RESULT_DECISION_BLOB_SHA,
        "comparison_basis": (
            "EXP-055 is the nearest prior successful historical result. "
            "EXP-056 is excluded as a model-outcome baseline because its "
            "sole attempt failed before producing model evidence."
        ),
        "variant_accounting": {
            "total_variant_count": TOTAL_VARIANT_COUNT,
            "available_variant_count_each_experiment": AVAILABLE_VARIANT_COUNT,
            "unavailable_variant_count_each_experiment": UNAVAILABLE_VARIANT_COUNT,
            "utility_eligible_selection_row_count_each_experiment": (
                UTILITY_ELIGIBLE_SELECTION_ROW_COUNT
            ),
        },
        "experiments": {
            "exp055": {
                "evidence_fingerprint": EXP055_EVIDENCE_FINGERPRINT,
                "aggregate_pass_count": EXP055_AGGREGATE_PASS_COUNT,
                "stable_pass_count": EXP055_STABLE_PASS_COUNT,
            },
            "exp057": {
                "evidence_fingerprint": EXP057_EVIDENCE_FINGERPRINT,
                "aggregate_pass_count": EXP057_AGGREGATE_PASS_COUNT,
                "stable_pass_count": EXP057_STABLE_PASS_COUNT,
                "accepted_model_candidate_count": (
                    ACCEPTED_MODEL_CANDIDATE_COUNT
                ),
            },
        },
        "aggregate_pass_identity": {
            "retained_from_exp055": [
                list(value)
                for value in EXP055_AGGREGATE_PASS_VARIANTS
            ],
            "added_vs_exp055": [["USDJPY", "5m", 60, 500]],
            "lost_vs_exp055": [],
        },
        "available_variant_financial_comparison": {
            "aggregate_0p5_net_pips_improved_count": (
                AVAILABLE_VARIANT_NET_PIPS_IMPROVED_COUNT
            ),
            "aggregate_0p5_net_pips_worsened_count": (
                AVAILABLE_VARIANT_NET_PIPS_WORSENED_COUNT
            ),
            "aggregate_0p5_net_pips_unchanged_count": (
                AVAILABLE_VARIANT_NET_PIPS_UNCHANGED_COUNT
            ),
        },
        "common_cell_comparison": {
            "cell": ["USDJPY", "5m", 60],
            "exp055_aggregate_total_net_pips": {
                str(key): value
                for key, value in EXP055_USDJPY_5M_60_AGGREGATE_NET_PIPS.items()
            },
            "exp057_aggregate_total_net_pips": {
                str(key): value
                for key, value in EXP057_USDJPY_5M_60_AGGREGATE_NET_PIPS.items()
            },
            "exp055_budget250_window_candidate_counts": list(
                EXP055_BUDGET250_WINDOW_COUNTS
            ),
            "exp057_budget250_window_candidate_counts": list(
                EXP057_BUDGET250_WINDOW_COUNTS
            ),
            "exp055_budget250_window_total_net_pips": list(
                EXP055_BUDGET250_WINDOW_NET_PIPS
            ),
            "exp057_budget250_window_total_net_pips": list(
                EXP057_BUDGET250_WINDOW_NET_PIPS
            ),
            "exp057_budget500_window_candidate_counts": list(
                EXP057_BUDGET500_WINDOW_COUNTS
            ),
            "exp057_budget500_window_total_net_pips": list(
                EXP057_BUDGET500_WINDOW_NET_PIPS
            ),
            "exp055_budget1000_window_candidate_counts": list(
                EXP055_BUDGET1000_WINDOW_COUNTS
            ),
            "exp057_budget1000_window_candidate_counts": list(
                EXP057_BUDGET1000_WINDOW_COUNTS
            ),
            "exp055_budget1000_window_total_net_pips": list(
                EXP055_BUDGET1000_WINDOW_NET_PIPS
            ),
            "exp057_budget1000_window_total_net_pips": list(
                EXP057_BUDGET1000_WINDOW_NET_PIPS
            ),
            "exp057_lower_tail_cutoffs": {
                "250": EXP057_BUDGET250_LOWER_TAIL_CUTOFF,
                "500": EXP057_BUDGET500_LOWER_TAIL_CUTOFF,
                "1000": EXP057_BUDGET1000_LOWER_TAIL_CUTOFF,
            },
            "exp055_residual_breadth_cutoffs": {
                "250": EXP055_BUDGET250_RESIDUAL_BREADTH_CUTOFF,
                "500": EXP055_BUDGET500_RESIDUAL_BREADTH_CUTOFF,
                "1000": EXP055_BUDGET1000_RESIDUAL_BREADTH_CUTOFF,
            },
            "exp057_residual_breadth_cutoffs": {
                "250": EXP057_BUDGET250_RESIDUAL_BREADTH_CUTOFF,
                "500": EXP057_BUDGET500_RESIDUAL_BREADTH_CUTOFF,
                "1000": EXP057_BUDGET1000_RESIDUAL_BREADTH_CUTOFF,
            },
        },
        "interpretation": {
            "eligibility_changed": False,
            "budget_availability_changed": False,
            "aggregate_pass_count_increased": True,
            "aggregate_pass_added_budget500": True,
            "stable_pass_count_improved": False,
            "available_variant_net_pips_improved_majority": True,
            "budget250_financial_quality_improved": False,
            "budget500_financial_quality_improved": True,
            "budget1000_financial_quality_improved": True,
            "budget250_selection_time_temporal_breadth_created": False,
            "budget500_selection_time_temporal_breadth_created": False,
            "budget1000_2022_h1_candidate_share_improved_vs_exp055": False,
            "budget1000_2022_h1_candidate_share_cleared_floor": False,
            "budget1000_late_window_concentration_increased": True,
            "lower_tail_ranking_created_selection_time_temporal_stability": False,
            "accepted_model_candidate_created": False,
        },
        "accepted_model_candidate_count": ACCEPTED_MODEL_CANDIDATE_COUNT,
        "exp057_rerun_authorized": EXP057_RERUN_AUTHORIZED,
        "exp057_replacement_run_authorized": (
            EXP057_REPLACEMENT_RUN_AUTHORIZED
        ),
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
        "retune_lower_tail_on_selection_authorized": (
            RETUNE_LOWER_TAIL_ON_SELECTION_AUTHORIZED
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
    "build_fit_temporal_residual_lower_tail_repair_post_result_diagnostic_gate",
]
