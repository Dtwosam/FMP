from __future__ import annotations

import unittest

from fmp.market_learning.model_successor_regime_consensus_post_result_diagnostics import (
    ACCEPTED_MODEL_CANDIDATE_COUNT,
    AGGREGATE_SELECTION_PASS_VARIANT_COUNT,
    AGGREGATE_SELECTION_REJECT_VARIANT_COUNT,
    BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT,
    CANDIDATE_SHARE_REJECT_VARIANT_COUNT,
    EVALUATED_VARIANT_COUNT,
    FINANCIAL_ONLY_REJECT_VARIANT_COUNT,
    POST_RESULT_DIAGNOSTIC_DECISION,
    SHARE_ONLY_REJECT_VARIANT_COUNT,
    STABILITY_REJECT_VARIANT_COUNT,
    STABLE_SELECTION_PASS_VARIANT_COUNT,
    WINDOW_FINANCIAL_REJECT_VARIANT_COUNT,
    ZERO_ANY_2021_HALF_VARIANT_COUNT,
    ZERO_BOTH_2021_HALVES_VARIANT_COUNT,
    build_regime_consensus_post_result_diagnostic_gate,
)


class Exp048PostResultDiagnosticsTests(unittest.TestCase):
    def test_gate_opens_successor_protocol_source_only(
        self,
    ) -> None:
        report = build_regime_consensus_post_result_diagnostic_gate()

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
            "WINDOW_FINANCIAL_INSTABILITY_DOMINANT",
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
            "exp048_rerun_authorized",
            "exp048_replacement_run_authorized",
        ):
            with self.subTest(field=field):
                self.assertIs(guardrails[field], False)

    def test_variant_accounting_is_exact(self) -> None:
        report = build_regime_consensus_post_result_diagnostic_gate()

        self.assertEqual(EVALUATED_VARIANT_COUNT, 54)
        self.assertEqual(
            AGGREGATE_SELECTION_PASS_VARIANT_COUNT,
            17,
        )
        self.assertEqual(
            AGGREGATE_SELECTION_REJECT_VARIANT_COUNT,
            37,
        )
        self.assertEqual(
            STABLE_SELECTION_PASS_VARIANT_COUNT,
            0,
        )
        self.assertEqual(
            STABILITY_REJECT_VARIANT_COUNT,
            17,
        )
        self.assertEqual(
            CANDIDATE_SHARE_REJECT_VARIANT_COUNT,
            13,
        )
        self.assertEqual(
            WINDOW_FINANCIAL_REJECT_VARIANT_COUNT,
            17,
        )
        self.assertEqual(
            BOTH_SHARE_AND_FINANCIAL_REJECT_VARIANT_COUNT,
            13,
        )
        self.assertEqual(
            FINANCIAL_ONLY_REJECT_VARIANT_COUNT,
            4,
        )
        self.assertEqual(
            SHARE_ONLY_REJECT_VARIANT_COUNT,
            0,
        )
        self.assertEqual(
            ZERO_BOTH_2021_HALVES_VARIANT_COUNT,
            0,
        )
        self.assertEqual(
            ZERO_ANY_2021_HALF_VARIANT_COUNT,
            5,
        )
        self.assertEqual(
            ACCEPTED_MODEL_CANDIDATE_COUNT,
            0,
        )

        self.assertEqual(
            report["window_financial_reject_variant_count"],
            report["stability_reject_variant_count"],
        )
        self.assertEqual(
            len(report["financial_only_reject_variants"]),
            4,
        )
        self.assertEqual(
            len(report["zero_any_2021_half_variants"]),
            5,
        )


if __name__ == "__main__":
    unittest.main()
