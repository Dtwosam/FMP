from __future__ import annotations

import unittest

from fmp.market_learning.model_successor_density_post_result_diagnostics import (
    ACCEPTED_MODEL_CANDIDATE_COUNT,
    AGGREGATE_SELECTION_PASS_VARIANT_COUNT,
    AGGREGATE_SELECTION_REJECT_VARIANT_COUNT,
    CANDIDATE_SHARE_ONLY_REJECT_VARIANT_COUNT,
    CANDIDATE_SHARE_REJECT_VARIANT_COUNT,
    EVALUATED_DENSITY_VARIANT_COUNT,
    POST_RESULT_DIAGNOSTIC_DECISION,
    STABILITY_REJECT_VARIANT_COUNT,
    STABLE_SELECTION_PASS_VARIANT_COUNT,
    WINDOW_FINANCIAL_REJECT_VARIANT_COUNT,
    ZERO_2021_CANDIDATE_VARIANT_COUNT,
    build_density_post_result_diagnostic_gate,
)


class Exp047PostResultDiagnosticsTests(unittest.TestCase):
    def test_gate_opens_successor_protocol_source_only(
        self,
    ) -> None:
        report = build_density_post_result_diagnostic_gate()

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
            "TEMPORAL_REGIME_CONCENTRATION_DOMINANT",
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
            "remove_2021_stability_windows_authorized",
            "add_wider_density_anchors_authorized",
            "exp047_rerun_authorized",
            "exp047_replacement_run_authorized",
        ):
            with self.subTest(field=field):
                self.assertIs(guardrails[field], False)

    def test_variant_accounting_is_exact(self) -> None:
        report = build_density_post_result_diagnostic_gate()

        self.assertEqual(
            EVALUATED_DENSITY_VARIANT_COUNT,
            54,
        )
        self.assertEqual(
            AGGREGATE_SELECTION_PASS_VARIANT_COUNT,
            12,
        )
        self.assertEqual(
            AGGREGATE_SELECTION_REJECT_VARIANT_COUNT,
            42,
        )
        self.assertEqual(
            STABLE_SELECTION_PASS_VARIANT_COUNT,
            0,
        )
        self.assertEqual(
            STABILITY_REJECT_VARIANT_COUNT,
            12,
        )
        self.assertEqual(
            CANDIDATE_SHARE_REJECT_VARIANT_COUNT,
            12,
        )
        self.assertEqual(
            WINDOW_FINANCIAL_REJECT_VARIANT_COUNT,
            10,
        )
        self.assertEqual(
            CANDIDATE_SHARE_ONLY_REJECT_VARIANT_COUNT,
            2,
        )
        self.assertEqual(
            ZERO_2021_CANDIDATE_VARIANT_COUNT,
            6,
        )
        self.assertEqual(
            ACCEPTED_MODEL_CANDIDATE_COUNT,
            0,
        )

        self.assertEqual(
            report["evaluated_density_variant_count"],
            54,
        )
        self.assertEqual(
            report["aggregate_selection_pass_variant_count"],
            12,
        )
        self.assertEqual(
            report["stability_reject_variant_count"],
            12,
        )

    def test_all_aggregate_passes_fail_candidate_share(
        self,
    ) -> None:
        report = build_density_post_result_diagnostic_gate()

        self.assertEqual(
            report["candidate_share_reject_variant_count"],
            report["stability_reject_variant_count"],
        )
        self.assertEqual(
            len(report["aggregate_pass_variants"]),
            12,
        )
        self.assertEqual(
            len(report["zero_2021_candidate_variants"]),
            6,
        )
        self.assertEqual(
            len(
                report[
                    "candidate_share_only_reject_variants"
                ]
            ),
            2,
        )


if __name__ == "__main__":
    unittest.main()
