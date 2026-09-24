from __future__ import annotations

import unittest

from fmp.market_learning.model_successor_regime_utility_post_result_diagnostics import (
    ACCEPTED_MODEL_CANDIDATE_COUNT,
    AGGREGATE_SELECTION_PASS_VARIANT_COUNT,
    AGGREGATE_SELECTION_REJECT_AVAILABLE_VARIANT_COUNT,
    AVAILABLE_VARIANT_COUNT,
    BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT,
    CANDIDATE_SHARE_REJECT_VARIANT_COUNT,
    FINANCIAL_ONLY_REJECT_VARIANT_COUNT,
    POST_RESULT_DIAGNOSTIC_DECISION,
    SELECTION_2021_H1_SHARE_REJECT_VARIANT_COUNT,
    SELECTION_2021_H2_SHARE_REJECT_VARIANT_COUNT,
    SELECTION_2022_H2_FINANCIAL_REJECT_VARIANT_COUNT,
    SHARE_ONLY_REJECT_VARIANT_COUNT,
    STABILITY_REJECT_VARIANT_COUNT,
    STABLE_SELECTION_PASS_VARIANT_COUNT,
    TOTAL_VARIANT_COUNT,
    UNAVAILABLE_BUDGET_VARIANT_COUNT,
    WINDOW_FINANCIAL_REJECT_VARIANT_COUNT,
    ZERO_ANY_2021_HALF_VARIANT_COUNT,
    ZERO_BOTH_2021_HALVES_VARIANT_COUNT,
    build_regime_utility_post_result_diagnostic_gate,
)


class Exp049PostResultDiagnosticsTests(unittest.TestCase):
    def test_gate_opens_successor_protocol_source_only(
        self,
    ) -> None:
        report = build_regime_utility_post_result_diagnostic_gate()

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
            "UTILITY_COVERAGE_AND_DUAL_TEMPORAL_STABILITY_LIMITED",
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
            "lower_utility_positivity_requirement_authorized",
            "add_smaller_budget_anchors_authorized",
            "exp049_rerun_authorized",
            "exp049_replacement_run_authorized",
        ):
            with self.subTest(field=field):
                self.assertIs(guardrails[field], False)

    def test_variant_accounting_is_exact(self) -> None:
        report = build_regime_utility_post_result_diagnostic_gate()

        self.assertEqual(TOTAL_VARIANT_COUNT, 54)
        self.assertEqual(AVAILABLE_VARIANT_COUNT, 23)
        self.assertEqual(UNAVAILABLE_BUDGET_VARIANT_COUNT, 31)
        self.assertEqual(
            AGGREGATE_SELECTION_PASS_VARIANT_COUNT,
            8,
        )
        self.assertEqual(
            AGGREGATE_SELECTION_REJECT_AVAILABLE_VARIANT_COUNT,
            15,
        )
        self.assertEqual(
            STABLE_SELECTION_PASS_VARIANT_COUNT,
            0,
        )
        self.assertEqual(
            STABILITY_REJECT_VARIANT_COUNT,
            8,
        )
        self.assertEqual(
            CANDIDATE_SHARE_REJECT_VARIANT_COUNT,
            8,
        )
        self.assertEqual(
            WINDOW_FINANCIAL_REJECT_VARIANT_COUNT,
            8,
        )
        self.assertEqual(
            BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT,
            8,
        )
        self.assertEqual(
            FINANCIAL_ONLY_REJECT_VARIANT_COUNT,
            0,
        )
        self.assertEqual(
            SHARE_ONLY_REJECT_VARIANT_COUNT,
            0,
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

    def test_all_aggregate_passes_fail_both_stability_dimensions(
        self,
    ) -> None:
        report = build_regime_utility_post_result_diagnostic_gate()

        self.assertEqual(
            CANDIDATE_SHARE_REJECT_VARIANT_COUNT,
            STABILITY_REJECT_VARIANT_COUNT,
        )
        self.assertEqual(
            WINDOW_FINANCIAL_REJECT_VARIANT_COUNT,
            STABILITY_REJECT_VARIANT_COUNT,
        )
        self.assertEqual(
            BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT,
            STABILITY_REJECT_VARIANT_COUNT,
        )
        self.assertEqual(
            SELECTION_2021_H1_SHARE_REJECT_VARIANT_COUNT,
            8,
        )
        self.assertEqual(
            SELECTION_2021_H2_SHARE_REJECT_VARIANT_COUNT,
            8,
        )
        self.assertEqual(
            SELECTION_2022_H2_FINANCIAL_REJECT_VARIANT_COUNT,
            6,
        )
        self.assertEqual(
            ZERO_ANY_2021_HALF_VARIANT_COUNT,
            2,
        )
        self.assertEqual(
            ZERO_BOTH_2021_HALVES_VARIANT_COUNT,
            1,
        )
        self.assertEqual(
            len(report["aggregate_pass_variants"]),
            8,
        )
        self.assertEqual(
            len(report["selection_2022_h2_financial_reject_variants"]),
            6,
        )


if __name__ == "__main__":
    unittest.main()
