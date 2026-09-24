from __future__ import annotations

import unittest

from fmp.market_learning.model_successor_temporal_calibrated_utility_post_result_diagnostics import (
    AGGREGATE_SELECTION_PASS_VARIANT_DELTA,
    AVAILABLE_VARIANT_COUNT_DELTA,
    BUDGET1000_TOTAL_NET_PIPS_DELTA,
    BUDGET250_MEAN_NET_PIPS_DELTA,
    BUDGET250_TOTAL_NET_PIPS_DELTA,
    BUDGET500_TOTAL_NET_PIPS_DELTA,
    COMMON_AGGREGATE_PASS_CELL,
    EXP050_AGGREGATE_PASS_BUDGETS,
    EXP050_AGGREGATE_SELECTION_PASS_VARIANT_COUNT,
    EXP050_AVAILABLE_VARIANT_COUNT,
    EXP050_STABLE_SELECTION_PASS_VARIANT_COUNT,
    EXP050_UNAVAILABLE_BUDGET_VARIANT_COUNT,
    EXP050_UTILITY_ELIGIBLE_SELECTION_ROW_COUNT,
    EXP051_AGGREGATE_PASS_BUDGETS,
    EXP051_AGGREGATE_SELECTION_PASS_VARIANT_COUNT,
    EXP051_AVAILABLE_VARIANT_COUNT,
    EXP051_STABLE_SELECTION_PASS_VARIANT_COUNT,
    EXP051_UNAVAILABLE_BUDGET_VARIANT_COUNT,
    EXP051_UTILITY_ELIGIBLE_SELECTION_ROW_COUNT,
    POST_RESULT_DIAGNOSTIC_DECISION,
    STABLE_SELECTION_PASS_VARIANT_DELTA,
    TOTAL_VARIANT_COUNT,
    UNAVAILABLE_BUDGET_VARIANT_COUNT_DELTA,
    UTILITY_ELIGIBLE_SELECTION_ROW_DELTA,
    build_temporal_calibrated_utility_post_result_diagnostic_gate,
)


class Exp051PostResultDiagnosticsTests(unittest.TestCase):
    def test_gate_opens_successor_protocol_source_only(
        self,
    ) -> None:
        report = (
            build_temporal_calibrated_utility_post_result_diagnostic_gate()
        )

        self.assertEqual(
            report["post_result_diagnostic_decision"],
            POST_RESULT_DIAGNOSTIC_DECISION,
        )
        self.assertEqual(
            POST_RESULT_DIAGNOSTIC_DECISION,
            "DEC-162",
        )
        self.assertEqual(
            report["stage"],
            "SUCCESSOR_PROTOCOL_SOURCE_OPEN",
        )
        self.assertEqual(
            report["diagnostic_classification"],
            (
                "TOP_250_FINANCIAL_QUALITY_IMPROVED_BUT_"
                "EARLY_TEMPORAL_COVERAGE_UNCHANGED_AND_"
                "BROAD_BUDGETS_DEGRADED"
            ),
        )
        self.assertTrue(
            report["successor_protocol_source_open_authorized"]
        )

        for field in (
            "successor_result_execution_authorized",
            "successor_model_fit_authorized",
            "promotion_authorized",
            "shadow_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            with self.subTest(field=field):
                self.assertIs(report[field], False)

        guardrails = report["guardrails"]
        assert isinstance(guardrails, dict)
        for field in (
            "relax_stability_share_authorized",
            "relax_stability_financial_authorized",
            "remove_2021_stability_windows_authorized",
            "recalibrate_on_selection_windows_authorized",
            "use_selection_outcomes_in_ranking_authorized",
            "lower_directional_utility_positivity_authorized",
            "lower_aggregate_candidate_floor_authorized",
            "add_smaller_budget_anchors_authorized",
            "exp051_rerun_authorized",
            "exp051_replacement_run_authorized",
        ):
            with self.subTest(field=field):
                self.assertIs(guardrails[field], False)

    def test_eligibility_and_budget_availability_are_unchanged(
        self,
    ) -> None:
        self.assertEqual(TOTAL_VARIANT_COUNT, 54)
        self.assertEqual(
            EXP050_AVAILABLE_VARIANT_COUNT,
            28,
        )
        self.assertEqual(
            EXP051_AVAILABLE_VARIANT_COUNT,
            28,
        )
        self.assertEqual(
            AVAILABLE_VARIANT_COUNT_DELTA,
            0,
        )
        self.assertEqual(
            EXP050_UNAVAILABLE_BUDGET_VARIANT_COUNT,
            26,
        )
        self.assertEqual(
            EXP051_UNAVAILABLE_BUDGET_VARIANT_COUNT,
            26,
        )
        self.assertEqual(
            UNAVAILABLE_BUDGET_VARIANT_COUNT_DELTA,
            0,
        )
        self.assertEqual(
            EXP050_UTILITY_ELIGIBLE_SELECTION_ROW_COUNT,
            26392,
        )
        self.assertEqual(
            EXP051_UTILITY_ELIGIBLE_SELECTION_ROW_COUNT,
            26392,
        )
        self.assertEqual(
            UTILITY_ELIGIBLE_SELECTION_ROW_DELTA,
            0,
        )

    def test_aggregate_passes_contract_but_stability_does_not_improve(
        self,
    ) -> None:
        self.assertEqual(
            EXP050_AGGREGATE_SELECTION_PASS_VARIANT_COUNT,
            3,
        )
        self.assertEqual(
            EXP051_AGGREGATE_SELECTION_PASS_VARIANT_COUNT,
            1,
        )
        self.assertEqual(
            AGGREGATE_SELECTION_PASS_VARIANT_DELTA,
            -2,
        )
        self.assertEqual(
            EXP050_STABLE_SELECTION_PASS_VARIANT_COUNT,
            0,
        )
        self.assertEqual(
            EXP051_STABLE_SELECTION_PASS_VARIANT_COUNT,
            0,
        )
        self.assertEqual(
            STABLE_SELECTION_PASS_VARIANT_DELTA,
            0,
        )
        self.assertEqual(
            COMMON_AGGREGATE_PASS_CELL,
            ("USDJPY", "5m", 60),
        )
        self.assertEqual(
            EXP050_AGGREGATE_PASS_BUDGETS,
            (250, 500, 1000),
        )
        self.assertEqual(
            EXP051_AGGREGATE_PASS_BUDGETS,
            (250,),
        )

    def test_budget250_quality_improves_without_early_2021_coverage(
        self,
    ) -> None:
        report = (
            build_temporal_calibrated_utility_post_result_diagnostic_gate()
        )
        comparison = report["budget250_comparison"]
        assert isinstance(comparison, dict)

        self.assertEqual(
            comparison["exp050_selection_candidate_count"],
            250,
        )
        self.assertEqual(
            comparison["exp051_selection_candidate_count"],
            250,
        )
        self.assertEqual(
            comparison["total_net_pips_delta"],
            BUDGET250_TOTAL_NET_PIPS_DELTA,
        )
        self.assertEqual(
            BUDGET250_TOTAL_NET_PIPS_DELTA,
            675.2000000000185,
        )
        self.assertEqual(
            comparison["mean_net_pips_delta"],
            BUDGET250_MEAN_NET_PIPS_DELTA,
        )
        self.assertEqual(
            BUDGET250_MEAN_NET_PIPS_DELTA,
            2.7008000000000743,
        )
        self.assertTrue(
            comparison["candidate_identity_changed"]
        )
        self.assertEqual(
            comparison[
                "selection_2021_h1_candidate_counts"
            ],
            [0, 0],
        )
        self.assertEqual(
            comparison[
                "selection_2021_h2_candidate_counts"
            ],
            [0, 0],
        )
        self.assertEqual(
            comparison[
                "selection_2022_h1_candidate_counts"
            ],
            [0, 3],
        )
        self.assertEqual(
            comparison[
                "selection_2022_h1_total_net_pips"
            ],
            [0.0, -28.100000000000477],
        )
        self.assertEqual(
            comparison[
                "selection_2022_h2_candidate_counts"
            ],
            [250, 247],
        )
        self.assertFalse(
            comparison["stability_passed_in_exp050"]
        )
        self.assertFalse(
            comparison["stability_passed_in_exp051"]
        )

    def test_broad_budget_aggregate_quality_degrades(
        self,
    ) -> None:
        report = (
            build_temporal_calibrated_utility_post_result_diagnostic_gate()
        )
        broad = report["broad_budget_comparison"]
        assert isinstance(broad, dict)
        budget500 = broad["budget_500"]
        budget1000 = broad["budget_1000"]
        assert isinstance(budget500, dict)
        assert isinstance(budget1000, dict)

        self.assertTrue(
            budget500["exp050_aggregate_gate_passed"]
        )
        self.assertFalse(
            budget500["exp051_aggregate_gate_passed"]
        )
        self.assertEqual(
            budget500["total_net_pips_delta"],
            BUDGET500_TOTAL_NET_PIPS_DELTA,
        )
        self.assertEqual(
            BUDGET500_TOTAL_NET_PIPS_DELTA,
            -1014.000000000003,
        )

        self.assertTrue(
            budget1000["exp050_aggregate_gate_passed"]
        )
        self.assertFalse(
            budget1000["exp051_aggregate_gate_passed"]
        )
        self.assertEqual(
            budget1000["total_net_pips_delta"],
            BUDGET1000_TOTAL_NET_PIPS_DELTA,
        )
        self.assertEqual(
            BUDGET1000_TOTAL_NET_PIPS_DELTA,
            -507.5000000000159,
        )


if __name__ == "__main__":
    unittest.main()
