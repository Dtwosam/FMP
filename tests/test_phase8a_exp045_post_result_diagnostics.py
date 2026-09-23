from __future__ import annotations

import unittest

from fmp.market_learning.model_successor_post_result_diagnostics import (
    ACCEPTED_MODEL_CANDIDATE_COUNT,
    FULL_SELECTION_GATE_PASS_COUNT,
    MIN_DIRECTIONAL_CANDIDATE_COUNT,
    POST_RESULT_DIAGNOSTIC_DECISION,
    SOURCE_MODEL_RUN_ID,
    build_post_result_diagnostic_gate,
)


class Exp045PostResultDiagnosticsTests(unittest.TestCase):
    def test_diagnostic_gate_opens_protocol_source_only(
        self,
    ) -> None:
        report = build_post_result_diagnostic_gate()

        self.assertEqual(
            report["post_result_diagnostic_decision"],
            POST_RESULT_DIAGNOSTIC_DECISION,
        )
        self.assertEqual(
            report["source_model_run_id"],
            SOURCE_MODEL_RUN_ID,
        )
        self.assertEqual(
            report["stage"],
            "SUCCESSOR_PROTOCOL_SOURCE_OPEN",
        )
        self.assertEqual(
            report["diagnostic_classification"],
            "TEMPORAL_STABILITY_FAILURE_DOMINANT",
        )
        self.assertEqual(
            report["full_selection_gate_pass_count"],
            FULL_SELECTION_GATE_PASS_COUNT,
        )
        self.assertEqual(
            report["accepted_model_candidate_count"],
            ACCEPTED_MODEL_CANDIDATE_COUNT,
        )

        self.assertEqual(
            report["min_directional_candidate_count"],
            MIN_DIRECTIONAL_CANDIDATE_COUNT,
        )
        self.assertFalse(
            report[
                "relax_min_directional_candidate_count_authorized"
            ]
        )
        self.assertFalse(
            report[
                "promote_low_count_positive_variants_authorized"
            ]
        )
        self.assertFalse(report["exp045_rerun_authorized"])
        self.assertFalse(
            report["exp045_replacement_run_authorized"]
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

    def test_selected_variant_records_validation_collapse(
        self,
    ) -> None:
        report = build_post_result_diagnostic_gate()
        selected = report["selected_cell"]
        assert isinstance(selected, dict)

        self.assertEqual(selected["symbol"], "GBPUSD")
        self.assertEqual(selected["timeframe"], "5m")
        self.assertEqual(
            selected["horizon_minutes"],
            240,
        )
        self.assertEqual(
            selected["model_family"],
            "hist_gradient_boosting",
        )
        self.assertEqual(
            selected["confidence_threshold"],
            0.6,
        )
        self.assertEqual(
            selected["selection_directional_candidate_count"],
            460,
        )
        self.assertEqual(
            selected["validation_directional_candidate_count"],
            83,
        )
        self.assertGreater(
            selected["selection_mean_net_pips"],
            0,
        )
        self.assertLess(
            selected["validation_mean_net_pips"],
            0,
        )
        self.assertLess(
            selected[
                "validation_to_selection_candidate_count_ratio"
            ],
            0.2,
        )
        self.assertLess(
            selected[
                "validation_to_selection_candidate_rate_ratio"
            ],
            0.2,
        )

    def test_variant_accounting_is_exact(self) -> None:
        report = build_post_result_diagnostic_gate()

        self.assertEqual(
            report["evaluated_variant_count"],
            90,
        )
        self.assertEqual(
            report["directional_count_gate_pass_count"],
            37,
        )
        self.assertEqual(
            report[
                "directional_count_pass_financial_fail_count"
            ],
            36,
        )
        self.assertEqual(
            report["positive_financial_signs_variant_count"],
            26,
        )
        self.assertEqual(
            report[
                "positive_financial_signs_low_count_variant_count"
            ],
            25,
        )
        self.assertEqual(
            report["logistic_nonconvergence_cell_count"],
            6,
        )


if __name__ == "__main__":
    unittest.main()
