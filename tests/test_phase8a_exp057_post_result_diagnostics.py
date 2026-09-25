from __future__ import annotations

import unittest

from fmp.market_learning.model_successor_fit_temporal_residual_lower_tail_utility_repair_post_result_diagnostics import (
    POST_RESULT_DIAGNOSTIC_DECISION,
    build_fit_temporal_residual_lower_tail_repair_post_result_diagnostic_gate,
)


class Exp057PostResultDiagnosticTests(unittest.TestCase):
    def test_diagnostic_identity_and_classification_are_frozen(self) -> None:
        gate = build_fit_temporal_residual_lower_tail_repair_post_result_diagnostic_gate()
        self.assertEqual(POST_RESULT_DIAGNOSTIC_DECISION, "DEC-230")
        self.assertEqual(
            gate["diagnostic_classification"],
            (
                "LOWER_TAIL_RANKING_CHANGED_CANDIDATE_FINANCIAL_MIX_"
                "AND_ADDED_AGGREGATE_PASS_BUT_DID_NOT_CREATE_TEMPORAL_STABILITY"
            ),
        )
        self.assertEqual(
            gate["dec229_merged_commit"],
            "7a2c53712a85f69e106a707dc1245e664c68bcbb",
        )
        self.assertEqual(
            gate["dec229_result_decision_blob_sha"],
            "185e2cdf089cb6f1a12619af58fd32860366498f",
        )

    def test_variant_accounting_is_unchanged(self) -> None:
        gate = build_fit_temporal_residual_lower_tail_repair_post_result_diagnostic_gate()
        self.assertEqual(
            gate["variant_accounting"],
            {
                "total_variant_count": 54,
                "available_variant_count_each_experiment": 28,
                "unavailable_variant_count_each_experiment": 26,
                "utility_eligible_selection_row_count_each_experiment": 26392,
            },
        )
        self.assertEqual(gate["experiments"]["exp055"]["stable_pass_count"], 0)
        self.assertEqual(gate["experiments"]["exp057"]["stable_pass_count"], 0)
        self.assertEqual(
            gate["experiments"]["exp057"]["accepted_model_candidate_count"],
            0,
        )

    def test_lower_tail_adds_only_budget500_aggregate_pass(self) -> None:
        gate = build_fit_temporal_residual_lower_tail_repair_post_result_diagnostic_gate()
        self.assertEqual(
            gate["aggregate_pass_identity"],
            {
                "retained_from_exp055": [
                    ["USDJPY", "5m", 60, 250],
                    ["USDJPY", "5m", 60, 1000],
                ],
                "added_vs_exp055": [
                    ["USDJPY", "5m", 60, 500],
                ],
                "lost_vs_exp055": [],
            },
        )
        self.assertEqual(
            gate["experiments"]["exp055"]["aggregate_pass_count"],
            2,
        )
        self.assertEqual(
            gate["experiments"]["exp057"]["aggregate_pass_count"],
            3,
        )

    def test_available_variant_financial_mix_is_mixed_but_more_often_improved(
        self,
    ) -> None:
        gate = build_fit_temporal_residual_lower_tail_repair_post_result_diagnostic_gate()
        self.assertEqual(
            gate["available_variant_financial_comparison"],
            {
                "aggregate_0p5_net_pips_improved_count": 15,
                "aggregate_0p5_net_pips_worsened_count": 13,
                "aggregate_0p5_net_pips_unchanged_count": 0,
            },
        )
        common = gate["common_cell_comparison"]
        self.assertGreater(
            common["exp055_aggregate_total_net_pips"]["250"],
            common["exp057_aggregate_total_net_pips"]["250"],
        )
        self.assertLess(
            common["exp055_aggregate_total_net_pips"]["500"],
            common["exp057_aggregate_total_net_pips"]["500"],
        )
        self.assertLess(
            common["exp055_aggregate_total_net_pips"]["1000"],
            common["exp057_aggregate_total_net_pips"]["1000"],
        )

    def test_selection_time_temporal_breadth_still_does_not_transfer(self) -> None:
        gate = build_fit_temporal_residual_lower_tail_repair_post_result_diagnostic_gate()
        common = gate["common_cell_comparison"]
        self.assertEqual(
            common["exp055_budget250_window_candidate_counts"],
            [0, 0, 0, 251],
        )
        self.assertEqual(
            common["exp057_budget250_window_candidate_counts"],
            [0, 0, 0, 250],
        )
        self.assertEqual(
            common["exp057_budget500_window_candidate_counts"],
            [0, 0, 3, 497],
        )
        self.assertEqual(
            common["exp055_budget1000_window_candidate_counts"],
            [0, 1, 83, 916],
        )
        self.assertEqual(
            common["exp057_budget1000_window_candidate_counts"],
            [0, 1, 73, 926],
        )
        interpretation = gate["interpretation"]
        self.assertFalse(
            interpretation[
                "lower_tail_ranking_created_selection_time_temporal_stability"
            ]
        )
        self.assertTrue(
            interpretation["budget1000_late_window_concentration_increased"]
        )
        self.assertFalse(
            interpretation["budget1000_2022_h1_candidate_share_cleared_floor"]
        )

    def test_comparison_basis_excludes_failed_exp056_model_outcome(self) -> None:
        gate = build_fit_temporal_residual_lower_tail_repair_post_result_diagnostic_gate()
        self.assertIn("EXP-055", gate["comparison_basis"])
        self.assertIn("EXP-056", gate["comparison_basis"])
        self.assertIn("failed before producing model evidence", gate["comparison_basis"])

    def test_only_successor_protocol_source_is_open(self) -> None:
        gate = build_fit_temporal_residual_lower_tail_repair_post_result_diagnostic_gate()
        self.assertTrue(gate["successor_protocol_source_open_authorized"])
        for field in (
            "exp057_rerun_authorized",
            "exp057_replacement_run_authorized",
            "relax_stability_share_authorized",
            "relax_stability_financial_authorized",
            "remove_early_stability_windows_authorized",
            "use_selection_outcomes_in_ranking_authorized",
            "recalibrate_on_selection_windows_authorized",
            "add_selection_window_quotas_authorized",
            "retune_lower_tail_on_selection_authorized",
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
                self.assertFalse(gate[field])


if __name__ == "__main__":
    unittest.main()
