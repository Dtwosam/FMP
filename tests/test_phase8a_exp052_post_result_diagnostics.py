from __future__ import annotations

import unittest

from fmp.market_learning.model_successor_fit_temporal_support_utility_post_result_diagnostics import (
    POST_RESULT_DIAGNOSTIC_DECISION,
    build_fit_temporal_support_post_result_diagnostic_gate,
)


class Exp052PostResultDiagnosticsTests(unittest.TestCase):
    def test_three_experiment_accounting_and_classification(self) -> None:
        report = build_fit_temporal_support_post_result_diagnostic_gate()
        self.assertEqual(
            report["post_result_diagnostic_decision"],
            POST_RESULT_DIAGNOSTIC_DECISION,
        )
        self.assertEqual(
            POST_RESULT_DIAGNOSTIC_DECISION,
            "DEC-173",
        )
        self.assertEqual(
            report["diagnostic_classification"],
            (
                "FIT_TEMPORAL_SUPPORT_DID_NOT_TRANSFER_TO_SELECTION_TIME_"
                "AND_TOP250_FINANCIAL_QUALITY_SLIGHTLY_DECLINED"
            ),
        )
        accounting = report["variant_accounting"]
        self.assertEqual(accounting["total_variant_count"], 54)
        self.assertEqual(
            accounting["available_variant_count_each_experiment"],
            28,
        )
        self.assertEqual(
            accounting["unavailable_variant_count_each_experiment"],
            26,
        )
        self.assertEqual(
            accounting[
                "utility_eligible_selection_row_count_each_experiment"
            ],
            26392,
        )

    def test_fit_support_changes_identity_but_not_temporal_coverage(
        self,
    ) -> None:
        report = build_fit_temporal_support_post_result_diagnostic_gate()
        comparison = report["budget250_comparison"]
        self.assertEqual(
            comparison["selection_window_candidate_counts"]["exp050"],
            [0, 0, 0, 250],
        )
        self.assertEqual(
            comparison["selection_window_candidate_counts"]["exp051"],
            [0, 0, 3, 247],
        )
        self.assertEqual(
            comparison["selection_window_candidate_counts"]["exp052"],
            [0, 0, 0, 250],
        )
        digests = comparison["candidate_identity_digests"]
        self.assertEqual(len(set(digests.values())), 3)
        interpretation = report["interpretation"]
        self.assertTrue(
            interpretation["fit_support_changed_candidate_identity"]
        )
        self.assertFalse(
            interpretation["fit_support_created_2021_candidates"]
        )
        self.assertFalse(
            interpretation["fit_support_created_2022_h1_candidates"]
        )
        self.assertFalse(
            interpretation["selection_time_transfer_demonstrated"]
        )

    def test_financial_comparison_is_exact(self) -> None:
        report = build_fit_temporal_support_post_result_diagnostic_gate()
        top = report["budget250_comparison"]["total_net_pips"]
        self.assertAlmostEqual(top["exp050"], 612.8999999999933)
        self.assertAlmostEqual(top["exp051"], 1288.1000000000117)
        self.assertAlmostEqual(top["exp052"], 1247.500000000025)
        self.assertAlmostEqual(
            top["exp052_minus_exp051"],
            -40.59999999998672,
        )
        broad = report["broad_budget_comparison"]
        self.assertAlmostEqual(
            broad["budget_500"]["exp052_total_net_pips"],
            -31.50000000000273,
        )
        self.assertEqual(
            broad["budget_500"]["aggregate_gate_passed"],
            [True, False, False],
        )
        self.assertEqual(
            broad["budget_1000"]["aggregate_gate_passed"],
            [True, False, False],
        )

    def test_only_successor_source_design_opens(self) -> None:
        report = build_fit_temporal_support_post_result_diagnostic_gate()
        self.assertEqual(
            report["stage"],
            "SUCCESSOR_PROTOCOL_SOURCE_OPEN",
        )
        self.assertTrue(
            report["successor_protocol_source_open_authorized"]
        )
        for field in (
            "exp052_rerun_authorized",
            "exp052_replacement_run_authorized",
            "relax_stability_share_authorized",
            "relax_stability_financial_authorized",
            "remove_early_stability_windows_authorized",
            "use_selection_outcomes_in_ranking_authorized",
            "recalibrate_on_selection_windows_authorized",
            "add_selection_window_quotas_authorized",
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


if __name__ == "__main__":
    unittest.main()
