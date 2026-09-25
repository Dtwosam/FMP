from __future__ import annotations


POST_RESULT_DIAGNOSTIC_DECISION = "DEC-208"

DEC207_MERGED_COMMIT = "78b1081aec39f8b79fe751ba2935ef49a1cb5ad1"
DEC207_RESULT_DECISION_BLOB_SHA = (
    "e2226117ebf10b762557d43549390c46c243bbae"
)
DEC197_DIAGNOSTIC_BLOB_SHA = (
    "3f53e79b52d3a2e4de1e7f61e142ecc55197aa87"
)

TOTAL_VARIANT_COUNT = 54
AVAILABLE_VARIANT_COUNT = 28
UNAVAILABLE_VARIANT_COUNT = 26
UTILITY_ELIGIBLE_SELECTION_ROW_COUNT = 26392

EXP054_EVIDENCE_FINGERPRINT = (
    "307b576f06c6aa2fb01a267232a0de55"
    "3bfa79c1bdbe6bf5d55b2bfc3b40787c"
)
EXP055_EVIDENCE_FINGERPRINT = (
    "f3a386dad7f23ac9d6867d030ac90e08"
    "84f3ab658c9ffecce8647048037d2510"
)

EXP054_AGGREGATE_PASS_COUNT = 2
EXP055_AGGREGATE_PASS_COUNT = 2
EXP054_STABLE_PASS_COUNT = 0
EXP055_STABLE_PASS_COUNT = 0

EXP054_AGGREGATE_PASS_VARIANTS = (
    ("USDJPY", "5m", 60, 250),
    ("USDJPY", "5m", 60, 1000),
)
EXP055_AGGREGATE_PASS_VARIANTS = (
    ("USDJPY", "5m", 60, 250),
    ("USDJPY", "5m", 60, 1000),
)

EXP054_USDJPY_5M_60_AGGREGATE_NET_PIPS = {
    250: 644.3000000000043,
    500: -7.7000000000080036,
    1000: 302.2999999999838,
}
EXP055_USDJPY_5M_60_AGGREGATE_NET_PIPS = {
    250: 576.6000000000067,
    500: -470.799999999977,
    1000: 40.50000000001137,
}

EXP054_BUDGET250_WINDOW_COUNTS = (0, 0, 0, 250)
EXP055_BUDGET250_WINDOW_COUNTS = (0, 0, 0, 251)
EXP054_BUDGET250_WINDOW_NET_PIPS = (
    0.0,
    0.0,
    0.0,
    644.3000000000043,
)
EXP055_BUDGET250_WINDOW_NET_PIPS = (
    0.0,
    0.0,
    0.0,
    576.6000000000067,
)

EXP054_BUDGET1000_WINDOW_COUNTS = (0, 3, 72, 925)
EXP055_BUDGET1000_WINDOW_COUNTS = (0, 1, 83, 916)
EXP054_BUDGET1000_WINDOW_NET_PIPS = (
    0.0,
    21.199999999999022,
    510.5000000000031,
    -229.40000000001828,
)
EXP055_BUDGET1000_WINDOW_NET_PIPS = (
    0.0,
    -2.800000000000068,
    464.30000000001553,
    -421.0000000000041,
)

EXP055_BUDGET250_RESIDUAL_BREADTH_CUTOFF = 10.0 / 12.0
EXP055_BUDGET1000_RESIDUAL_BREADTH_CUTOFF = 0.0

AVAILABLE_VARIANT_NET_PIPS_IMPROVED_COUNT = 7
AVAILABLE_VARIANT_NET_PIPS_WORSENED_COUNT = 16
AVAILABLE_VARIANT_NET_PIPS_UNCHANGED_COUNT = 5

ACCEPTED_MODEL_CANDIDATE_COUNT = 0

EXP055_RERUN_AUTHORIZED = False
EXP055_REPLACEMENT_RUN_AUTHORIZED = False
RELAX_STABILITY_SHARE_AUTHORIZED = False
RELAX_STABILITY_FINANCIAL_AUTHORIZED = False
REMOVE_EARLY_STABILITY_WINDOWS_AUTHORIZED = False
USE_SELECTION_OUTCOMES_IN_RANKING_AUTHORIZED = False
RECALIBRATE_ON_SELECTION_WINDOWS_AUTHORIZED = False
ADD_SELECTION_WINDOW_QUOTAS_AUTHORIZED = False
RETUNE_RESIDUAL_BREADTH_ON_SELECTION_AUTHORIZED = False

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


def build_fit_temporal_residual_breadth_post_result_diagnostic_gate(
) -> dict[str, object]:
    if AVAILABLE_VARIANT_COUNT + UNAVAILABLE_VARIANT_COUNT != TOTAL_VARIANT_COUNT:
        raise ValueError("DEC-208 total-variant accounting drift")
    if UTILITY_ELIGIBLE_SELECTION_ROW_COUNT != 26392:
        raise ValueError("DEC-208 eligible-row accounting drift")
    if EXP054_AGGREGATE_PASS_VARIANTS != EXP055_AGGREGATE_PASS_VARIANTS:
        raise ValueError("DEC-208 aggregate-pass identity drift")
    if len(EXP055_AGGREGATE_PASS_VARIANTS) != EXP055_AGGREGATE_PASS_COUNT:
        raise ValueError("DEC-208 aggregate-pass count drift")
    if EXP054_STABLE_PASS_COUNT != 0 or EXP055_STABLE_PASS_COUNT != 0:
        raise ValueError("DEC-208 stable-pass count drift")
    if (
        AVAILABLE_VARIANT_NET_PIPS_IMPROVED_COUNT
        + AVAILABLE_VARIANT_NET_PIPS_WORSENED_COUNT
        + AVAILABLE_VARIANT_NET_PIPS_UNCHANGED_COUNT
        != AVAILABLE_VARIANT_COUNT
    ):
        raise ValueError("DEC-208 available-variant comparison drift")
    if EXP055_BUDGET250_WINDOW_COUNTS[:3] != (0, 0, 0):
        raise ValueError("DEC-208 top-250 early-window concentration drift")
    if EXP055_BUDGET250_RESIDUAL_BREADTH_CUTOFF != 10.0 / 12.0:
        raise ValueError("DEC-208 top-250 breadth cutoff drift")
    if EXP055_BUDGET1000_RESIDUAL_BREADTH_CUTOFF != 0.0:
        raise ValueError("DEC-208 budget-1000 breadth cutoff drift")
    if EXP055_BUDGET1000_WINDOW_COUNTS[2] >= 100:
        raise ValueError("DEC-208 budget-1000 2022-H1 share unexpectedly clears floor")
    if ACCEPTED_MODEL_CANDIDATE_COUNT != 0:
        raise ValueError("DEC-208 accepted-candidate count drift")

    return {
        "post_result_diagnostic_decision": POST_RESULT_DIAGNOSTIC_DECISION,
        "stage": "SUCCESSOR_PROTOCOL_SOURCE_OPEN",
        "diagnostic_classification": (
            "FIT_RESIDUAL_BREADTH_DID_NOT_TRANSFER_TO_SELECTION_"
            "TEMPORAL_BREADTH_AND_WEAKENED_PASS_VARIANT_FINANCIALS"
        ),
        "dec207_merged_commit": DEC207_MERGED_COMMIT,
        "dec207_result_decision_blob_sha": DEC207_RESULT_DECISION_BLOB_SHA,
        "dec197_diagnostic_blob_sha": DEC197_DIAGNOSTIC_BLOB_SHA,
        "variant_accounting": {
            "total_variant_count": TOTAL_VARIANT_COUNT,
            "available_variant_count_each_experiment": AVAILABLE_VARIANT_COUNT,
            "unavailable_variant_count_each_experiment": UNAVAILABLE_VARIANT_COUNT,
            "utility_eligible_selection_row_count_each_experiment": (
                UTILITY_ELIGIBLE_SELECTION_ROW_COUNT
            ),
        },
        "experiments": {
            "exp054": {
                "evidence_fingerprint": EXP054_EVIDENCE_FINGERPRINT,
                "aggregate_pass_count": EXP054_AGGREGATE_PASS_COUNT,
                "stable_pass_count": EXP054_STABLE_PASS_COUNT,
            },
            "exp055": {
                "evidence_fingerprint": EXP055_EVIDENCE_FINGERPRINT,
                "aggregate_pass_count": EXP055_AGGREGATE_PASS_COUNT,
                "stable_pass_count": EXP055_STABLE_PASS_COUNT,
                "accepted_model_candidate_count": (
                    ACCEPTED_MODEL_CANDIDATE_COUNT
                ),
            },
        },
        "aggregate_pass_identity": {
            "unchanged_vs_exp054": True,
            "variants": [
                list(value) for value in EXP055_AGGREGATE_PASS_VARIANTS
            ],
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
            "exp054_aggregate_total_net_pips": {
                str(key): value
                for key, value in EXP054_USDJPY_5M_60_AGGREGATE_NET_PIPS.items()
            },
            "exp055_aggregate_total_net_pips": {
                str(key): value
                for key, value in EXP055_USDJPY_5M_60_AGGREGATE_NET_PIPS.items()
            },
            "exp054_budget250_window_candidate_counts": list(
                EXP054_BUDGET250_WINDOW_COUNTS
            ),
            "exp055_budget250_window_candidate_counts": list(
                EXP055_BUDGET250_WINDOW_COUNTS
            ),
            "exp054_budget250_window_total_net_pips": list(
                EXP054_BUDGET250_WINDOW_NET_PIPS
            ),
            "exp055_budget250_window_total_net_pips": list(
                EXP055_BUDGET250_WINDOW_NET_PIPS
            ),
            "exp054_budget1000_window_candidate_counts": list(
                EXP054_BUDGET1000_WINDOW_COUNTS
            ),
            "exp055_budget1000_window_candidate_counts": list(
                EXP055_BUDGET1000_WINDOW_COUNTS
            ),
            "exp054_budget1000_window_total_net_pips": list(
                EXP054_BUDGET1000_WINDOW_NET_PIPS
            ),
            "exp055_budget1000_window_total_net_pips": list(
                EXP055_BUDGET1000_WINDOW_NET_PIPS
            ),
            "exp055_budget250_residual_breadth_cutoff": (
                EXP055_BUDGET250_RESIDUAL_BREADTH_CUTOFF
            ),
            "exp055_budget1000_residual_breadth_cutoff": (
                EXP055_BUDGET1000_RESIDUAL_BREADTH_CUTOFF
            ),
        },
        "interpretation": {
            "eligibility_changed": False,
            "budget_availability_changed": False,
            "aggregate_pass_identity_changed_vs_exp054": False,
            "stable_pass_count_improved_vs_exp054": False,
            "top250_fit_breadth_high_but_selection_breadth_created": False,
            "budget1000_2022_h1_candidate_share_increased": True,
            "budget1000_2022_h1_candidate_share_cleared_floor": False,
            "budget1000_2021_h2_candidate_count_improved": False,
            "budget1000_2021_h2_financial_sign_improved": False,
            "budget1000_2022_h2_financial_quality_improved": False,
            "pass_variant_aggregate_financial_quality_improved": False,
            "residual_breadth_created_selection_time_temporal_stability": False,
            "accepted_model_candidate_created": False,
            "binary_fit_breadth_is_sufficient_successor_signal": False,
        },
        "accepted_model_candidate_count": ACCEPTED_MODEL_CANDIDATE_COUNT,
        "exp055_rerun_authorized": EXP055_RERUN_AUTHORIZED,
        "exp055_replacement_run_authorized": (
            EXP055_REPLACEMENT_RUN_AUTHORIZED
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
        "retune_residual_breadth_on_selection_authorized": (
            RETUNE_RESIDUAL_BREADTH_ON_SELECTION_AUTHORIZED
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
    "build_fit_temporal_residual_breadth_post_result_diagnostic_gate",
]
