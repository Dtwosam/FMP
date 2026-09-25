from __future__ import annotations

import unittest

from fmp.market_learning.model_successor_fit_temporal_residual_breadth_utility_post_result_diagnostics import (
    POST_RESULT_DIAGNOSTIC_DECISION,
    build_fit_temporal_residual_breadth_post_result_diagnostic_gate,
)


class Exp055PostResultDiagnosticTests(unittest.TestCase):
    def test_diagnostic_identity_and_classification_are_frozen(self) -> None:
        gate = build_fit_temporal_residual_breadth_post_result_diagnostic_gate()
        self.assertEqual(POST_RESULT_DIAGNOSTIC_DECISION, "DEC-208")
        self.assertEqual(
            gate["diagnostic_classification"],
            (
                "FIT_RESIDUAL_BREADTH_DID_NOT_TRANSFER_TO_SELECTION_"
                "TEMPORAL_BREADTH_AND_WEAKENED_PASS_VARIANT_FINANCIALS"
            ),
        )
        self.assertEqual(
            gate["dec207_merged_commit"],
            "78b1081aec39f8b79fe751ba2935ef49a1cb5ad1",
        )
        self.assertEqual(
            gate["dec207_result_decision_blob_sha"],
            "e2226117ebf10b762557d43549390c46c243bbae",
        )

    def test_variant_accounting_and_pass_identity_are_unchanged(self) -> None:
        gate = build_fit_temporal_residual_breadth_post_result_diagnostic_gate()
        self.assertEqual(
            gate["variant_accounting"],
            {
                "total_variant_count": 54,
                "available_variant_count_each_experiment": 28,
                "unavailable_variant_count_each_experiment": 26,
                "utility_eligible_selection_row_count_each_experiment": 26392,
            },
        )
        self.assertEqual(
            gate["aggregate_pass_identity"],
            {
                "unchanged_vs_exp054": True,
                "variants": [
                    ["USDJPY", "5m", 60, 250],
                    ["USDJPY", "5m", 60, 1000],
                ],
            },
        )
        self.assertEqual(gate["experiments"]["exp054"]["stable_pass_count"], 0)
        self.assertEqual(gate["experiments"]["exp055"]["stable_pass_count"], 0)
        self.assertEqual(
            gate["experiments"]["exp055"]["accepted_model_candidate_count"],
            0,
        )

    def test_common_cell_proves_no_selection_time_breadth_transfer(self) -> None:
        gate = build_fit_temporal_residual_breadth_post_result_diagnostic_gate()
        common = gate["common_cell_comparison"]
        self.assertEqual(common["cell"], ["USDJPY", "5m", 60])
        self.assertEqual(
            common["exp054_budget250_window_candidate_counts"],
            [0, 0, 0, 250],
        )
        self.assertEqual(
            common["exp055_budget250_window_candidate_counts"],
            [0, 0, 0, 251],
        )
        self.assertAlmostEqual(
            common["exp055_budget250_residual_breadth_cutoff"],
            10.0 / 12.0,
        )
        self.assertEqual(
            common["exp054_budget1000_window_candidate_counts"],
            [0, 3, 72, 925],
        )
        self.assertEqual(
            common["exp055_budget1000_window_candidate_counts"],
            [0, 1, 83, 916],
        )
        self.assertEqual(
            common["exp055_budget1000_residual_breadth_cutoff"],
            0.0,
        )

    def test_pass_variant_financial_quality_weakened(self) -> None:
        gate = build_fit_temporal_residual_breadth_post_result_diagnostic_gate()
        common = gate["common_cell_comparison"]
        self.assertGreater(
            common["exp054_aggregate_total_net_pips"]["250"],
            common["exp055_aggregate_total_net_pips"]["250"],
        )
        self.assertGreater(
            common["exp054_aggregate_total_net_pips"]["1000"],
            common["exp055_aggregate_total_net_pips"]["1000"],
        )
        self.assertEqual(
            gate["available_variant_financial_comparison"],
            {
                "aggregate_0p5_net_pips_improved_count": 7,
                "aggregate_0p5_net_pips_worsened_count": 16,
                "aggregate_0p5_net_pips_unchanged_count": 5,
            },
        )

    def test_interpretation_is_fail_closed(self) -> None:
        gate = build_fit_temporal_residual_breadth_post_result_diagnostic_gate()
        interpretation = gate["interpretation"]
        self.assertFalse(interpretation["eligibility_changed"])
        self.assertFalse(interpretation["budget_availability_changed"])
        self.assertFalse(
            interpretation["aggregate_pass_identity_changed_vs_exp054"]
        )
        self.assertFalse(
            interpretation["stable_pass_count_improved_vs_exp054"]
        )
        self.assertFalse(
            interpretation["top250_fit_breadth_high_but_selection_breadth_created"]
        )
        self.assertTrue(
            interpretation["budget1000_2022_h1_candidate_share_increased"]
        )
        self.assertFalse(
            interpretation["budget1000_2022_h1_candidate_share_cleared_floor"]
        )
        self.assertFalse(
            interpretation[
                "residual_breadth_created_selection_time_temporal_stability"
            ]
        )
        self.assertFalse(
            interpretation["binary_fit_breadth_is_sufficient_successor_signal"]
        )
        self.assertFalse(interpretation["accepted_model_candidate_created"])

    def test_only_successor_protocol_source_is_open(self) -> None:
        gate = build_fit_temporal_residual_breadth_post_result_diagnostic_gate()
        self.assertTrue(gate["successor_protocol_source_open_authorized"])
        for field in (
            "exp055_rerun_authorized",
            "exp055_replacement_run_authorized",
            "relax_stability_share_authorized",
            "relax_stability_financial_authorized",
            "remove_early_stability_windows_authorized",
            "use_selection_outcomes_in_ranking_authorized",
            "recalibrate_on_selection_windows_authorized",
            "add_selection_window_quotas_authorized",
            "retune_residual_breadth_on_selection_authorized",
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
