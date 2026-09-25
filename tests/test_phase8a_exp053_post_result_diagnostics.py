from __future__ import annotations

import unittest

from fmp.market_learning.model_successor_fit_temporal_feature_support_utility_post_result_diagnostics import (
    POST_RESULT_DIAGNOSTIC_DECISION,
    build_fit_temporal_feature_support_post_result_diagnostic_gate,
)


class Exp053PostResultDiagnosticsTests(unittest.TestCase):
    def test_four_experiment_accounting_and_classification(self) -> None:
        report = build_fit_temporal_feature_support_post_result_diagnostic_gate()
        self.assertEqual(
            report["post_result_diagnostic_decision"],
            POST_RESULT_DIAGNOSTIC_DECISION,
        )
        self.assertEqual(POST_RESULT_DIAGNOSTIC_DECISION, "DEC-184")
        self.assertEqual(
            report["diagnostic_classification"],
            (
                "FEATURE_SUPPORT_BROADENED_AGGREGATE_PASSES_"
                "BUT_DID_NOT_CLEAR_TEMPORAL_STABILITY"
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

    def test_feature_support_broadens_passes_without_stability(
        self,
    ) -> None:
        report = build_fit_temporal_feature_support_post_result_diagnostic_gate()
        experiments = report["experiments"]
        self.assertEqual(
            [
                experiments[name]["aggregate_pass_count"]
                for name in ("exp050", "exp051", "exp052", "exp053")
            ],
            [3, 1, 1, 10],
        )
        self.assertEqual(
            [
                experiments[name]["stable_pass_count"]
                for name in ("exp050", "exp051", "exp052", "exp053")
            ],
            [0, 0, 0, 0],
        )
        exp053 = report["exp053_aggregate_pass_distribution"]
        self.assertEqual(len(exp053["variants"]), 10)
        self.assertEqual(exp053["horizon_60_count"], 2)
        self.assertEqual(exp053["horizon_240_count"], 8)
        self.assertEqual(exp053["gbpusd_count"], 4)
        self.assertEqual(exp053["usdjpy_count"], 6)
        self.assertEqual(exp053["eurusd_count"], 0)
        self.assertFalse(
            exp053["retains_exact_exp052_pass_variant"]
        )

    def test_remaining_failure_modes_are_exact(self) -> None:
        report = build_fit_temporal_feature_support_post_result_diagnostic_gate()
        diagnostics = report["temporal_stability_diagnostics"]
        self.assertEqual(
            diagnostics["2021_share_reject_variant_count"],
            10,
        )
        self.assertEqual(
            diagnostics["2022_h1_financial_reject_variant_count"],
            9,
        )
        self.assertEqual(
            diagnostics["2022_h1_financial_pass_variant_count"],
            1,
        )
        self.assertEqual(
            diagnostics[
                "representative_gbpusd_5m_240_budget500"
            ]["window_candidate_counts"],
            [57, 33, 131, 279],
        )
        self.assertEqual(
            diagnostics[
                "representative_usdjpy_15m_240_budget250"
            ]["window_candidate_counts"],
            [0, 27, 88, 135],
        )
        interpretation = report["interpretation"]
        self.assertTrue(
            interpretation[
                "feature_support_broadened_aggregate_passes"
            ]
        )
        self.assertTrue(
            interpretation[
                "feature_support_created_some_2021_candidates"
            ]
        )
        self.assertFalse(
            interpretation[
                "feature_support_removed_all_2021_share_failures"
            ]
        )
        self.assertFalse(
            interpretation[
                "feature_support_removed_2022_h1_financial_instability"
            ]
        )
        self.assertFalse(
            interpretation[
                "selection_time_temporal_stability_demonstrated"
            ]
        )

    def test_only_successor_source_design_opens(self) -> None:
        report = build_fit_temporal_feature_support_post_result_diagnostic_gate()
        self.assertEqual(
            report["stage"],
            "SUCCESSOR_PROTOCOL_SOURCE_OPEN",
        )
        self.assertTrue(
            report["successor_protocol_source_open_authorized"]
        )
        for field in (
            "exp053_rerun_authorized",
            "exp053_replacement_run_authorized",
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
