from __future__ import annotations

import unittest

from fmp.market_learning.model_successor_cross_run_reproducibility import (
    CROSS_RUN_REPRODUCIBILITY_DECISION,
    EXP046_ACCEPTED_MODEL_CANDIDATE_COUNT,
    EXP046_STABLE_SELECTION_PASS_VARIANT_COUNT,
    HGB_CANDIDATE_IDENTITY_MATCH_COUNT,
    HGB_CANDIDATE_VARIANT_COUNT,
    HGB_MODEL_FINGERPRINT_MATCH_COUNT,
    HGB_PROBABILITY_DIGEST_MATCH_COUNT,
    LOGISTIC_CANDIDATE_IDENTITY_MATCH_COUNT,
    LOGISTIC_CANDIDATE_VARIANT_COUNT,
    LOGISTIC_FAMILY_AVAILABILITY_CHANGED_CELL_COUNT,
    LOGISTIC_MODEL_FINGERPRINT_MATCH_COUNT,
    LOGISTIC_PROBABILITY_DIGEST_MATCH_COUNT,
    build_cross_run_reproducibility_gate,
)


class ModelCrossRunReproducibilityTests(unittest.TestCase):
    def test_gate_opens_protocol_source_only(self) -> None:
        report = build_cross_run_reproducibility_gate()

        self.assertEqual(
            report["cross_run_reproducibility_decision"],
            CROSS_RUN_REPRODUCIBILITY_DECISION,
        )
        self.assertEqual(
            report["stage"],
            "SUCCESSOR_PROTOCOL_SOURCE_OPEN",
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
            "logistic_family_reuse_for_result_execution_authorized",
            "logistic_numerical_remedy_result_execution_authorized",
            "relax_stability_screen_authorized",
            "exp046_rerun_authorized",
            "exp046_replacement_run_authorized",
        ):
            with self.subTest(field=field):
                self.assertIs(guardrails[field], False)

    def test_hgb_material_decisions_are_reproducible(self) -> None:
        report = build_cross_run_reproducibility_gate()
        hgb = report["hgb"]
        assert isinstance(hgb, dict)

        self.assertEqual(
            hgb["classification"],
            "MATERIAL_DECISION_REPRODUCIBILITY_ESTABLISHED",
        )
        self.assertEqual(
            HGB_MODEL_FINGERPRINT_MATCH_COUNT,
            18,
        )
        self.assertEqual(
            HGB_CANDIDATE_IDENTITY_MATCH_COUNT,
            HGB_CANDIDATE_VARIANT_COUNT,
        )
        self.assertEqual(
            HGB_CANDIDATE_VARIANT_COUNT,
            54,
        )
        self.assertEqual(
            HGB_PROBABILITY_DIGEST_MATCH_COUNT,
            4,
        )
        self.assertLess(
            HGB_PROBABILITY_DIGEST_MATCH_COUNT,
            HGB_MODEL_FINGERPRINT_MATCH_COUNT,
        )

    def test_logistic_family_availability_is_not_reproducible(
        self,
    ) -> None:
        report = build_cross_run_reproducibility_gate()
        logistic = report["logistic_regression"]
        assert isinstance(logistic, dict)

        self.assertEqual(
            logistic["classification"],
            "FAMILY_AVAILABILITY_REPRODUCIBILITY_FAILED",
        )
        self.assertEqual(
            LOGISTIC_FAMILY_AVAILABILITY_CHANGED_CELL_COUNT,
            5,
        )
        self.assertEqual(
            LOGISTIC_MODEL_FINGERPRINT_MATCH_COUNT,
            4,
        )
        self.assertEqual(
            LOGISTIC_PROBABILITY_DIGEST_MATCH_COUNT,
            4,
        )
        self.assertEqual(
            LOGISTIC_CANDIDATE_IDENTITY_MATCH_COUNT,
            29,
        )
        self.assertEqual(
            LOGISTIC_CANDIDATE_VARIANT_COUNT,
            30,
        )

    def test_cross_run_effects_do_not_change_exp046_final_result(
        self,
    ) -> None:
        report = build_cross_run_reproducibility_gate()
        effects = report["cross_run_effects"]
        assert isinstance(effects, dict)

        self.assertEqual(
            effects["aggregate_gate_outcome_change_count"],
            1,
        )
        aggregate_change = effects[
            "aggregate_gate_outcome_change"
        ]
        assert isinstance(aggregate_change, dict)
        self.assertEqual(
            aggregate_change["symbol"],
            "EURUSD",
        )
        self.assertEqual(
            aggregate_change["timeframe"],
            "5m",
        )
        self.assertEqual(
            aggregate_change["horizon_minutes"],
            60,
        )
        self.assertEqual(
            aggregate_change["confidence_threshold"],
            0.6,
        )
        self.assertEqual(
            aggregate_change["exp046_status"],
            "AGGREGATE_GATE_PASS_STABILITY_REJECT",
        )

        self.assertEqual(
            EXP046_STABLE_SELECTION_PASS_VARIANT_COUNT,
            0,
        )
        self.assertEqual(
            EXP046_ACCEPTED_MODEL_CANDIDATE_COUNT,
            0,
        )


if __name__ == "__main__":
    unittest.main()
