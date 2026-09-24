from __future__ import annotations

import unittest

from fmp.market_learning.model_successor_temporal_jackknife_utility_post_result_diagnostics import (
    ACCEPTED_MODEL_CANDIDATE_COUNT,
    AGGREGATE_SELECTION_PASS_VARIANT_COUNT,
    AGGREGATE_SELECTION_REJECT_AVAILABLE_VARIANT_COUNT,
    AVAILABLE_VARIANT_COUNT,
    AVAILABLE_VARIANT_COUNT_DELTA,
    POST_RESULT_DIAGNOSTIC_DECISION,
    PREDECESSOR_AVAILABLE_VARIANT_COUNT,
    PREDECESSOR_UNAVAILABLE_BUDGET_VARIANT_COUNT,
    PREDECESSOR_UTILITY_ELIGIBLE_SELECTION_ROW_COUNT,
    SELECTION_2021_H1_ZERO_CANDIDATE_VARIANT_COUNT,
    SELECTION_2021_H2_SINGLE_CANDIDATE_VARIANT_COUNT,
    SELECTION_2021_H2_ZERO_CANDIDATE_VARIANT_COUNT,
    SELECTION_2022_H1_FINANCIAL_POSITIVE_SHARE_REJECT_VARIANT_COUNT,
    SELECTION_2022_H2_PASS_VARIANT_COUNT,
    STABILITY_REJECT_VARIANT_COUNT,
    STABLE_SELECTION_PASS_VARIANT_COUNT,
    TOTAL_VARIANT_COUNT,
    UNAVAILABLE_BUDGET_VARIANT_COUNT,
    UNAVAILABLE_BUDGET_VARIANT_COUNT_DELTA,
    UTILITY_ELIGIBLE_SELECTION_ROW_COUNT,
    UTILITY_ELIGIBLE_SELECTION_ROW_DELTA,
    build_temporal_jackknife_utility_post_result_diagnostic_gate,
)


class Exp050PostResultDiagnosticsTests(unittest.TestCase):
    def test_gate_opens_successor_protocol_source_only(
        self,
    ) -> None:
        report = (
            build_temporal_jackknife_utility_post_result_diagnostic_gate()
        )

        self.assertEqual(
            report["post_result_diagnostic_decision"],
            POST_RESULT_DIAGNOSTIC_DECISION,
        )
        self.assertEqual(
            report["stage"],
            "SUCCESSOR_PROTOCOL_SOURCE_OPEN",
        )
        self.assertEqual(
            report["diagnostic_classification"],
            (
                "UTILITY_COVERAGE_INCREASED_BUT_"
                "EARLY_TEMPORAL_COVERAGE_LIMITED"
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
            "alter_temporal_jackknife_views_authorized",
            "alter_unanimous_utility_consensus_authorized",
            "lower_utility_positivity_requirement_authorized",
            "add_smaller_budget_anchors_authorized",
            "exp050_rerun_authorized",
            "exp050_replacement_run_authorized",
        ):
            with self.subTest(field=field):
                self.assertIs(guardrails[field], False)

    def test_variant_accounting_is_exact(self) -> None:
        report = (
            build_temporal_jackknife_utility_post_result_diagnostic_gate()
        )

        self.assertEqual(TOTAL_VARIANT_COUNT, 54)
        self.assertEqual(AVAILABLE_VARIANT_COUNT, 28)
        self.assertEqual(UNAVAILABLE_BUDGET_VARIANT_COUNT, 26)
        self.assertEqual(
            AGGREGATE_SELECTION_PASS_VARIANT_COUNT,
            3,
        )
        self.assertEqual(
            AGGREGATE_SELECTION_REJECT_AVAILABLE_VARIANT_COUNT,
            25,
        )
        self.assertEqual(
            STABLE_SELECTION_PASS_VARIANT_COUNT,
            0,
        )
        self.assertEqual(
            STABILITY_REJECT_VARIANT_COUNT,
            3,
        )
        self.assertEqual(
            ACCEPTED_MODEL_CANDIDATE_COUNT,
            0,
        )

        self.assertEqual(
            report["available_variant_count"]
            + report["unavailable_budget_variant_count"],
            report["total_variant_count"],
        )
        self.assertEqual(
            report["aggregate_selection_pass_variant_count"]
            + report[
                "aggregate_selection_reject_available_variant_count"
            ],
            report["available_variant_count"],
        )

    def test_all_aggregate_passes_are_one_cell_and_fail_early_windows(
        self,
    ) -> None:
        report = (
            build_temporal_jackknife_utility_post_result_diagnostic_gate()
        )

        self.assertEqual(
            report["cells_with_aggregate_pass_count"],
            1,
        )
        self.assertEqual(
            report["horizon_60_aggregate_pass_variant_count"],
            3,
        )
        self.assertEqual(
            report["horizon_240_aggregate_pass_variant_count"],
            0,
        )
        self.assertEqual(
            SELECTION_2021_H1_ZERO_CANDIDATE_VARIANT_COUNT,
            3,
        )
        self.assertEqual(
            SELECTION_2021_H2_ZERO_CANDIDATE_VARIANT_COUNT,
            2,
        )
        self.assertEqual(
            SELECTION_2021_H2_SINGLE_CANDIDATE_VARIANT_COUNT,
            1,
        )
        self.assertEqual(
            SELECTION_2022_H1_FINANCIAL_POSITIVE_SHARE_REJECT_VARIANT_COUNT,
            2,
        )
        self.assertEqual(
            SELECTION_2022_H2_PASS_VARIANT_COUNT,
            3,
        )

        pass_rows = report["aggregate_pass_variants"]
        assert isinstance(pass_rows, list)
        self.assertEqual(
            {
                tuple(row[:4])
                for row in pass_rows
            },
            {
                ("USDJPY", "5m", 60, 250),
                ("USDJPY", "5m", 60, 500),
                ("USDJPY", "5m", 60, 1000),
            },
        )

    def test_coverage_change_is_descriptive_only(self) -> None:
        report = (
            build_temporal_jackknife_utility_post_result_diagnostic_gate()
        )

        self.assertEqual(
            PREDECESSOR_AVAILABLE_VARIANT_COUNT,
            23,
        )
        self.assertEqual(
            PREDECESSOR_UNAVAILABLE_BUDGET_VARIANT_COUNT,
            31,
        )
        self.assertEqual(
            PREDECESSOR_UTILITY_ELIGIBLE_SELECTION_ROW_COUNT,
            14158,
        )
        self.assertEqual(
            UTILITY_ELIGIBLE_SELECTION_ROW_COUNT,
            26392,
        )
        self.assertEqual(
            UTILITY_ELIGIBLE_SELECTION_ROW_DELTA,
            12234,
        )
        self.assertEqual(
            AVAILABLE_VARIANT_COUNT_DELTA,
            5,
        )
        self.assertEqual(
            UNAVAILABLE_BUDGET_VARIANT_COUNT_DELTA,
            -5,
        )
        self.assertEqual(
            report["stable_selection_pass_variant_count"],
            0,
        )
        self.assertEqual(
            report["accepted_model_candidate_count"],
            0,
        )


if __name__ == "__main__":
    unittest.main()
