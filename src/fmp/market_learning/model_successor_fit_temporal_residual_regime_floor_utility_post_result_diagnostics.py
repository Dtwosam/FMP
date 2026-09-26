from __future__ import annotations

from .model_successor_fit_temporal_residual_lower_tail_utility_repair_result_decision import (
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_RESULT_DECISION,
    REVIEWED_EVIDENCE_FINGERPRINT as EXP057_EVIDENCE_FINGERPRINT,
)
from .model_successor_fit_temporal_residual_regime_floor_utility_result_decision import (
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RESULT_DECISION,
    REVIEWED_EVIDENCE_FINGERPRINT as EXP058_EVIDENCE_FINGERPRINT,
)


POST_RESULT_DIAGNOSTIC_DECISION = "DEC-241"

DEC240_MERGED_COMMIT = "d691c8e12f40cf4baf3fc93f598b24d23b8435f4"
DEC240_RESULT_DECISION_BLOB_SHA = (
    "f5a5f7e49b7088f4af9b35a9143e486c3fba3d1a"
)
DEC229_RESULT_DECISION_BLOB_SHA = (
    "185e2cdf089cb6f1a12619af58fd32860366498f"
)
DEC230_DIAGNOSTIC_BLOB_SHA = (
    "09e88b85a51b858296a3af7d146251606f1d5533"
)

TOTAL_VARIANT_COUNT = 54
AVAILABLE_VARIANT_COUNT = 28
UNAVAILABLE_VARIANT_COUNT = 26
UTILITY_ELIGIBLE_SELECTION_ROW_COUNT = 26392

EXP057_AGGREGATE_PASS_COUNT = 3
EXP058_AGGREGATE_PASS_COUNT = 3
EXP057_STABLE_PASS_COUNT = 0
EXP058_STABLE_PASS_COUNT = 0

EXP057_AGGREGATE_PASS_VARIANTS = (
    ("USDJPY", "5m", 60, 250),
    ("USDJPY", "5m", 60, 500),
    ("USDJPY", "5m", 60, 1000),
)
EXP058_AGGREGATE_PASS_VARIANTS = (
    ("USDJPY", "5m", 60, 250),
    ("USDJPY", "5m", 60, 500),
    ("USDJPY", "5m", 60, 1000),
)

EXP057_USDJPY_5M_60_AGGREGATE_NET_PIPS = {
    250: 301.40000000000646,
    500: 88.99999999999636,
    1000: 362.0999999999858,
}
EXP058_USDJPY_5M_60_AGGREGATE_NET_PIPS = {
    250: 819.2000000000007,
    500: 179.49999999999773,
    1000: 296.99999999998136,
}

EXP057_BUDGET250_WINDOW_COUNTS = (0, 0, 0, 250)
EXP058_BUDGET250_WINDOW_COUNTS = (0, 0, 0, 250)
EXP057_BUDGET500_WINDOW_COUNTS = (0, 0, 3, 497)
EXP058_BUDGET500_WINDOW_COUNTS = (0, 0, 7, 493)
EXP057_BUDGET1000_WINDOW_COUNTS = (0, 1, 73, 926)
EXP058_BUDGET1000_WINDOW_COUNTS = (0, 3, 72, 925)

EXP057_BUDGET250_WINDOW_NET_PIPS = (
    0.0,
    0.0,
    0.0,
    301.40000000000646,
)
EXP058_BUDGET250_WINDOW_NET_PIPS = (
    0.0,
    0.0,
    0.0,
    819.2000000000007,
)
EXP057_BUDGET500_WINDOW_NET_PIPS = (
    0.0,
    0.0,
    27.099999999998772,
    61.89999999999691,
)
EXP058_BUDGET500_WINDOW_NET_PIPS = (
    0.0,
    0.0,
    84.8999999999997,
    94.59999999999764,
)
EXP057_BUDGET1000_WINDOW_NET_PIPS = (
    0.0,
    -2.800000000000068,
    522.6000000000031,
    -157.700000000018,
)
EXP058_BUDGET1000_WINDOW_NET_PIPS = (
    0.0,
    21.199999999999022,
    510.5000000000031,
    -234.70000000002074,
)

EXP058_BUDGET250_REGIME_FLOOR_CUTOFF = -0.11335128369382375
EXP058_BUDGET500_REGIME_FLOOR_CUTOFF = -2.042678526565064
EXP058_BUDGET1000_REGIME_FLOOR_CUTOFF = -4.659644720399596

AVAILABLE_VARIANT_CANDIDATE_IDENTITY_CHANGED_COUNT = 27
AVAILABLE_VARIANT_CANDIDATE_IDENTITY_UNCHANGED_COUNT = 1
AVAILABLE_VARIANT_NET_PIPS_IMPROVED_COUNT = 14
AVAILABLE_VARIANT_NET_PIPS_WORSENED_COUNT = 13
AVAILABLE_VARIANT_NET_PIPS_UNCHANGED_COUNT = 1

ACCEPTED_MODEL_CANDIDATE_COUNT = 0

EXP058_RERUN_AUTHORIZED = False
EXP058_REPLACEMENT_RUN_AUTHORIZED = False
RELAX_STABILITY_SHARE_AUTHORIZED = False
RELAX_STABILITY_FINANCIAL_AUTHORIZED = False
REMOVE_EARLY_STABILITY_WINDOWS_AUTHORIZED = False
USE_SELECTION_OUTCOMES_IN_RANKING_AUTHORIZED = False
RECALIBRATE_ON_SELECTION_WINDOWS_AUTHORIZED = False
ADD_SELECTION_WINDOW_QUOTAS_AUTHORIZED = False
RETUNE_REGIME_FLOOR_ON_SELECTION_AUTHORIZED = False

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


def build_fit_temporal_residual_regime_floor_post_result_diagnostic_gate(
) -> dict[str, object]:
    if FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_MODEL_RESULT_DECISION != "DEC-229":
        raise ValueError("DEC-241 EXP-057 result decision drift")
    if FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_MODEL_RESULT_DECISION != "DEC-240":
        raise ValueError("DEC-241 EXP-058 result decision drift")
    if AVAILABLE_VARIANT_COUNT + UNAVAILABLE_VARIANT_COUNT != TOTAL_VARIANT_COUNT:
        raise ValueError("DEC-241 total-variant accounting drift")
    if UTILITY_ELIGIBLE_SELECTION_ROW_COUNT != 26392:
        raise ValueError("DEC-241 eligible-row accounting drift")
    if EXP057_AGGREGATE_PASS_VARIANTS != EXP058_AGGREGATE_PASS_VARIANTS:
        raise ValueError("DEC-241 aggregate-pass identity drift")
    if EXP057_STABLE_PASS_COUNT != 0 or EXP058_STABLE_PASS_COUNT != 0:
        raise ValueError("DEC-241 stable-pass count drift")
    if (
        AVAILABLE_VARIANT_CANDIDATE_IDENTITY_CHANGED_COUNT
        + AVAILABLE_VARIANT_CANDIDATE_IDENTITY_UNCHANGED_COUNT
        != AVAILABLE_VARIANT_COUNT
    ):
        raise ValueError("DEC-241 candidate-identity accounting drift")
    if (
        AVAILABLE_VARIANT_NET_PIPS_IMPROVED_COUNT
        + AVAILABLE_VARIANT_NET_PIPS_WORSENED_COUNT
        + AVAILABLE_VARIANT_NET_PIPS_UNCHANGED_COUNT
        != AVAILABLE_VARIANT_COUNT
    ):
        raise ValueError("DEC-241 financial comparison accounting drift")
    if EXP058_BUDGET250_WINDOW_COUNTS[:3] != (0, 0, 0):
        raise ValueError("DEC-241 budget-250 chronology drift")
    if EXP058_BUDGET500_WINDOW_COUNTS[:2] != (0, 0):
        raise ValueError("DEC-241 budget-500 early-window chronology drift")
    if EXP058_BUDGET500_WINDOW_COUNTS[2] >= 50:
        raise ValueError("DEC-241 budget-500 2022-H1 share unexpectedly clears floor")
    if EXP058_BUDGET1000_WINDOW_COUNTS[2] >= 100:
        raise ValueError("DEC-241 budget-1000 2022-H1 share unexpectedly clears floor")
    if ACCEPTED_MODEL_CANDIDATE_COUNT != 0:
        raise ValueError("DEC-241 accepted-candidate count drift")

    return {
        "post_result_diagnostic_decision": POST_RESULT_DIAGNOSTIC_DECISION,
        "stage": "SUCCESSOR_PROTOCOL_SOURCE_OPEN",
        "diagnostic_classification": (
            "REGIME_FLOOR_RANKING_CHANGED_CANDIDATE_MIX_AND_FINANCIALS_"
            "BUT_DID_NOT_CREATE_TEMPORAL_STABILITY"
        ),
        "dec240_merged_commit": DEC240_MERGED_COMMIT,
        "dec240_result_decision_blob_sha": DEC240_RESULT_DECISION_BLOB_SHA,
        "dec229_result_decision_blob_sha": DEC229_RESULT_DECISION_BLOB_SHA,
        "dec230_diagnostic_blob_sha": DEC230_DIAGNOSTIC_BLOB_SHA,
        "comparison_basis": (
            "EXP-057 is the nearest successful predecessor historical result. "
            "EXP-058 changes only the fit-derived regime-floor ranking layer "
            "ahead of the frozen lower-tail/breadth/residual-bound/support stack."
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
            "exp057": {
                "evidence_fingerprint": EXP057_EVIDENCE_FINGERPRINT,
                "aggregate_pass_count": EXP057_AGGREGATE_PASS_COUNT,
                "stable_pass_count": EXP057_STABLE_PASS_COUNT,
            },
            "exp058": {
                "evidence_fingerprint": EXP058_EVIDENCE_FINGERPRINT,
                "aggregate_pass_count": EXP058_AGGREGATE_PASS_COUNT,
                "stable_pass_count": EXP058_STABLE_PASS_COUNT,
                "accepted_model_candidate_count": (
                    ACCEPTED_MODEL_CANDIDATE_COUNT
                ),
            },
        },
        "aggregate_pass_identity": {
            "retained_from_exp057": [
                list(value) for value in EXP058_AGGREGATE_PASS_VARIANTS
            ],
            "added_vs_exp057": [],
            "lost_vs_exp057": [],
        },
        "available_variant_candidate_identity_comparison": {
            "changed_count": (
                AVAILABLE_VARIANT_CANDIDATE_IDENTITY_CHANGED_COUNT
            ),
            "unchanged_count": (
                AVAILABLE_VARIANT_CANDIDATE_IDENTITY_UNCHANGED_COUNT
            ),
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
            "exp057_aggregate_total_net_pips": {
                str(key): value
                for key, value in EXP057_USDJPY_5M_60_AGGREGATE_NET_PIPS.items()
            },
            "exp058_aggregate_total_net_pips": {
                str(key): value
                for key, value in EXP058_USDJPY_5M_60_AGGREGATE_NET_PIPS.items()
            },
            "exp057_budget250_window_candidate_counts": list(
                EXP057_BUDGET250_WINDOW_COUNTS
            ),
            "exp058_budget250_window_candidate_counts": list(
                EXP058_BUDGET250_WINDOW_COUNTS
            ),
            "exp057_budget500_window_candidate_counts": list(
                EXP057_BUDGET500_WINDOW_COUNTS
            ),
            "exp058_budget500_window_candidate_counts": list(
                EXP058_BUDGET500_WINDOW_COUNTS
            ),
            "exp057_budget1000_window_candidate_counts": list(
                EXP057_BUDGET1000_WINDOW_COUNTS
            ),
            "exp058_budget1000_window_candidate_counts": list(
                EXP058_BUDGET1000_WINDOW_COUNTS
            ),
            "exp057_budget250_window_total_net_pips": list(
                EXP057_BUDGET250_WINDOW_NET_PIPS
            ),
            "exp058_budget250_window_total_net_pips": list(
                EXP058_BUDGET250_WINDOW_NET_PIPS
            ),
            "exp057_budget500_window_total_net_pips": list(
                EXP057_BUDGET500_WINDOW_NET_PIPS
            ),
            "exp058_budget500_window_total_net_pips": list(
                EXP058_BUDGET500_WINDOW_NET_PIPS
            ),
            "exp057_budget1000_window_total_net_pips": list(
                EXP057_BUDGET1000_WINDOW_NET_PIPS
            ),
            "exp058_budget1000_window_total_net_pips": list(
                EXP058_BUDGET1000_WINDOW_NET_PIPS
            ),
            "exp058_regime_floor_cutoffs": {
                "250": EXP058_BUDGET250_REGIME_FLOOR_CUTOFF,
                "500": EXP058_BUDGET500_REGIME_FLOOR_CUTOFF,
                "1000": EXP058_BUDGET1000_REGIME_FLOOR_CUTOFF,
            },
        },
        "interpretation": {
            "eligibility_changed": False,
            "budget_availability_changed": False,
            "aggregate_pass_identity_changed": False,
            "stable_pass_count_improved": False,
            "candidate_identity_changed_for_most_available_variants": True,
            "available_variant_net_pips_improved_majority": True,
            "budget250_financial_quality_improved": True,
            "budget500_financial_quality_improved": True,
            "budget1000_financial_quality_improved": False,
            "budget250_selection_time_temporal_breadth_created": False,
            "budget500_selection_time_temporal_breadth_created": False,
            "budget1000_2022_h1_candidate_share_improved_vs_exp057": False,
            "budget1000_2022_h1_candidate_share_cleared_floor": False,
            "regime_floor_ranking_created_selection_time_temporal_stability": False,
            "accepted_model_candidate_created": False,
        },
        "accepted_model_candidate_count": ACCEPTED_MODEL_CANDIDATE_COUNT,
        "exp058_rerun_authorized": EXP058_RERUN_AUTHORIZED,
        "exp058_replacement_run_authorized": (
            EXP058_REPLACEMENT_RUN_AUTHORIZED
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
        "retune_regime_floor_on_selection_authorized": (
            RETUNE_REGIME_FLOOR_ON_SELECTION_AUTHORIZED
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
    "build_fit_temporal_residual_regime_floor_post_result_diagnostic_gate",
]
