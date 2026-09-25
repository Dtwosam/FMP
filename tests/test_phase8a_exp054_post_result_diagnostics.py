from __future__ import annotations

import unittest

from fmp.market_learning.model_successor_fit_temporal_residual_bound_utility_post_result_diagnostics import (
    POST_RESULT_DIAGNOSTIC_DECISION,
    build_fit_temporal_residual_bound_post_result_diagnostic_gate,
)


class Exp054PostResultDiagnosticsTests(unittest.TestCase):
    def test_five_experiment_accounting_and_classification(self) -> None:
        report = build_fit_temporal_residual_bound_post_result_diagnostic_gate()
        self.assertEqual(
            report["post_result_diagnostic_decision"],
            POST_RESULT_DIAGNOSTIC_DECISION,
        )
        self.assertEqual(POST_RESULT_DIAGNOSTIC_DECISION, "DEC-197")
        self.assertEqual(
            report["diagnostic_classification"],
            (
                "RESIDUAL_BOUND_NARROWED_AGGREGATE_PASSES_AND_IMPROVED_"
                "SOME_DOWNSIDE_WINDOWS_BUT_DID_NOT_CREATE_TEMPORAL_BREADTH"
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

    def test_residual_bound_narrows_passes_without_stability(self) -> None:
        report = build_fit_temporal_residual_bound_post_result_diagnostic_gate()
        experiments = report["experiments"]
        self.assertEqual(
            [
                experiments[name]["aggregate_pass_count"]
                for name in (
                    "exp050",
                    "exp051",
                    "exp052",
                    "exp053",
                    "exp054",
                )
            ],
            [3, 1, 1, 10, 2],
        )
        self.assertEqual(
            [
                experiments[name]["stable_pass_count"]
                for name in (
                    "exp050",
                    "exp051",
                    "exp052",
                    "exp053",
                    "exp054",
                )
            ],
            [0, 0, 0, 0, 0],
        )
        exp054 = report["exp054_aggregate_pass_distribution"]
        self.assertEqual(
            exp054["variants"],
            [
                ["USDJPY", "5m", 60, 250],
                ["USDJPY", "5m", 60, 1000],
            ],
        )
        self.assertEqual(exp054["horizon_60_count"], 2)
        self.assertEqual(exp054["horizon_240_count"], 0)
        self.assertEqual(exp054["usdjpy_count"], 2)
        self.assertEqual(exp054["gbpusd_count"], 0)
        self.assertEqual(exp054["eurusd_count"], 0)
        self.assertTrue(exp054["restores_exact_exp052_common_pass"])
        self.assertTrue(exp054["retains_exact_exp053_common_pass"])

    def test_common_cell_shift_is_exact(self) -> None:
        report = build_fit_temporal_residual_bound_post_result_diagnostic_gate()
        common = report["common_cell_comparison"]
        self.assertEqual(common["cell"], ["USDJPY", "5m", 60])
        self.assertEqual(
            common["exp053_aggregate_total_net_pips"]["250"],
            -352.00000000002524,
        )
        self.assertEqual(
            common["exp054_aggregate_total_net_pips"]["250"],
            644.3000000000043,
        )
        self.assertEqual(
            common["exp053_budget1000_window_candidate_counts"],
            [0, 3, 130, 867],
        )
        self.assertEqual(
            common["exp054_budget250_window_candidate_counts"],
            [0, 0, 0, 250],
        )
        self.assertEqual(
            common["exp054_budget1000_window_candidate_counts"],
            [0, 3, 72, 925],
        )
        self.assertEqual(
            common["exp053_budget1000_window_total_net_pips"],
            [0.0, 21.199999999999022, -67.19999999999004, 531.1999999999744],
        )
        self.assertEqual(
            common["exp054_budget1000_window_total_net_pips"],
            [0.0, 21.199999999999022, 510.5000000000031, -229.40000000001828],
        )

    def test_interpretation_keeps_temporal_problem_open(self) -> None:
        report = build_fit_temporal_residual_bound_post_result_diagnostic_gate()
        interpretation = report["interpretation"]
        self.assertFalse(
            interpretation["aggregate_pass_breadth_improved_vs_exp053"]
        )
        self.assertTrue(
            interpretation[
                "top250_aggregate_financial_quality_improved_vs_exp053"
            ]
        )
        self.assertFalse(
            interpretation["top250_temporal_breadth_created"]
        )
        self.assertTrue(
            interpretation["budget1000_2022_h1_financial_sign_improved"]
        )
        self.assertFalse(
            interpretation["budget1000_2022_h1_candidate_share_improved"]
        )
        self.assertFalse(
            interpretation["budget1000_2022_h2_financial_quality_improved"]
        )
        self.assertFalse(
            interpretation[
                "residual_bound_created_selection_time_temporal_stability"
            ]
        )
        self.assertFalse(
            interpretation["accepted_model_candidate_created"]
        )

    def test_only_successor_source_design_opens(self) -> None:
        report = build_fit_temporal_residual_bound_post_result_diagnostic_gate()
        self.assertEqual(report["stage"], "SUCCESSOR_PROTOCOL_SOURCE_OPEN")
        self.assertTrue(
            report["successor_protocol_source_open_authorized"]
        )
        for field in (
            "exp054_rerun_authorized",
            "exp054_replacement_run_authorized",
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
