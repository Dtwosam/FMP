from __future__ import annotations

import unittest

from fmp.market_learning.model_successor_fit_temporal_residual_regime_floor_utility_post_result_diagnostics import (
    POST_RESULT_DIAGNOSTIC_DECISION,
    build_fit_temporal_residual_regime_floor_post_result_diagnostic_gate,
)


class Exp058PostResultDiagnosticTests(unittest.TestCase):
    def test_diagnostic_identity_and_classification_are_frozen(self) -> None:
        gate = build_fit_temporal_residual_regime_floor_post_result_diagnostic_gate()
        self.assertEqual(POST_RESULT_DIAGNOSTIC_DECISION, "DEC-241")
        self.assertEqual(
            gate["diagnostic_classification"],
            (
                "REGIME_FLOOR_RANKING_CHANGED_CANDIDATE_MIX_AND_FINANCIALS_"
                "BUT_DID_NOT_CREATE_TEMPORAL_STABILITY"
            ),
        )
        self.assertEqual(
            gate["dec240_merged_commit"],
            "d691c8e12f40cf4baf3fc93f598b24d23b8435f4",
        )
        self.assertEqual(
            gate["dec240_result_decision_blob_sha"],
            "f5a5f7e49b7088f4af9b35a9143e486c3fba3d1a",
        )

    def test_variant_accounting_and_pass_identity_are_unchanged(self) -> None:
        gate = build_fit_temporal_residual_regime_floor_post_result_diagnostic_gate()
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
                "retained_from_exp057": [
                    ["USDJPY", "5m", 60, 250],
                    ["USDJPY", "5m", 60, 500],
                    ["USDJPY", "5m", 60, 1000],
                ],
                "added_vs_exp057": [],
                "lost_vs_exp057": [],
            },
        )
        self.assertEqual(gate["experiments"]["exp057"]["stable_pass_count"], 0)
        self.assertEqual(gate["experiments"]["exp058"]["stable_pass_count"], 0)

    def test_regime_floor_changes_most_candidate_identities(self) -> None:
        gate = build_fit_temporal_residual_regime_floor_post_result_diagnostic_gate()
        self.assertEqual(
            gate["available_variant_candidate_identity_comparison"],
            {
                "changed_count": 27,
                "unchanged_count": 1,
            },
        )
        self.assertEqual(
            gate["available_variant_financial_comparison"],
            {
                "aggregate_0p5_net_pips_improved_count": 14,
                "aggregate_0p5_net_pips_worsened_count": 13,
                "aggregate_0p5_net_pips_unchanged_count": 1,
            },
        )

    def test_common_cell_financial_mix_changes_without_stability(self) -> None:
        gate = build_fit_temporal_residual_regime_floor_post_result_diagnostic_gate()
        common = gate["common_cell_comparison"]
        self.assertGreater(
            common["exp058_aggregate_total_net_pips"]["250"],
            common["exp057_aggregate_total_net_pips"]["250"],
        )
        self.assertGreater(
            common["exp058_aggregate_total_net_pips"]["500"],
            common["exp057_aggregate_total_net_pips"]["500"],
        )
        self.assertLess(
            common["exp058_aggregate_total_net_pips"]["1000"],
            common["exp057_aggregate_total_net_pips"]["1000"],
        )
        self.assertEqual(
            common["exp058_budget250_window_candidate_counts"],
            [0, 0, 0, 250],
        )
        self.assertEqual(
            common["exp058_budget500_window_candidate_counts"],
            [0, 0, 7, 493],
        )
        self.assertEqual(
            common["exp058_budget1000_window_candidate_counts"],
            [0, 3, 72, 925],
        )
        self.assertEqual(
            common["exp058_regime_floor_cutoffs"],
            {
                "250": -0.11335128369382375,
                "500": -2.042678526565064,
                "1000": -4.659644720399596,
            },
        )

    def test_selection_time_temporal_breadth_still_does_not_transfer(self) -> None:
        gate = build_fit_temporal_residual_regime_floor_post_result_diagnostic_gate()
        interpretation = gate["interpretation"]
        self.assertFalse(
            interpretation[
                "regime_floor_ranking_created_selection_time_temporal_stability"
            ]
        )
        self.assertFalse(
            interpretation["budget250_selection_time_temporal_breadth_created"]
        )
        self.assertFalse(
            interpretation["budget500_selection_time_temporal_breadth_created"]
        )
        self.assertFalse(
            interpretation["budget1000_2022_h1_candidate_share_cleared_floor"]
        )
        self.assertFalse(interpretation["accepted_model_candidate_created"])

    def test_only_successor_protocol_source_is_open(self) -> None:
        gate = build_fit_temporal_residual_regime_floor_post_result_diagnostic_gate()
        self.assertTrue(gate["successor_protocol_source_open_authorized"])
        for field in (
            "exp058_rerun_authorized",
            "exp058_replacement_run_authorized",
            "relax_stability_share_authorized",
            "relax_stability_financial_authorized",
            "remove_early_stability_windows_authorized",
            "use_selection_outcomes_in_ranking_authorized",
            "recalibrate_on_selection_windows_authorized",
            "add_selection_window_quotas_authorized",
            "retune_regime_floor_on_selection_authorized",
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
