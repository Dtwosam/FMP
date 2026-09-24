from __future__ import annotations

import unittest

from fmp.market_learning.model_protocol import (
    MIN_DIRECTIONAL_CANDIDATES,
)
from fmp.market_learning.model_successor_density_protocol import (
    AUTHORIZED_MODEL_FAMILIES,
    CANDIDATE_BUDGET_ANCHORS,
    DENSITY_PROTOCOL_DECISION,
    DENSITY_SUCCESSOR_EXPERIMENT_ID,
    EXCLUDED_MODEL_FAMILIES,
    PREDECESSOR_HGB_AGGREGATE_GATE_PASS_COUNT,
    PREDECESSOR_HGB_COUNT_GATE_PASS_COUNT,
    PREDECESSOR_HGB_POSITIVE_BUT_LOW_COUNT,
    PREDECESSOR_HGB_POSITIVE_FINANCIAL_SIGN_COUNT,
    PREDECESSOR_HGB_VARIANT_COUNT,
    density_protocol_fingerprint,
    density_protocol_payload,
    validate_density_predecessor_identity,
)


class Exp047DensityProtocolTests(unittest.TestCase):
    def test_predecessor_identity_is_exact(self) -> None:
        validate_density_predecessor_identity()

    def test_protocol_is_post_result_informed_and_closed(
        self,
    ) -> None:
        payload = density_protocol_payload()

        self.assertEqual(
            payload["experiment_id"],
            DENSITY_SUCCESSOR_EXPERIMENT_ID,
        )
        self.assertEqual(
            payload["protocol_decision"],
            DENSITY_PROTOCOL_DECISION,
        )

        predecessor = payload["predecessor"]
        assert isinstance(predecessor, dict)
        self.assertEqual(
            predecessor["experiment_id"],
            "EXP-20260923-046",
        )
        self.assertEqual(
            predecessor["result_decision"],
            "DEC-111",
        )
        self.assertEqual(
            predecessor["reproducibility_decision"],
            "DEC-112",
        )
        self.assertTrue(
            predecessor["prior_result_informed"]
        )
        self.assertFalse(predecessor["untouched_oos"])
        self.assertEqual(
            predecessor["accepted_model_candidate_count"],
            0,
        )

        authorization = payload["authorization"]
        assert isinstance(authorization, dict)
        for field in (
            "model_protocol_result_authorized",
            "model_fit_authorized",
            "historical_result_execution_authorized",
            "promotion_authorized",
            "shadow_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            with self.subTest(field=field):
                self.assertIs(
                    authorization[field],
                    False,
                )

    def test_predecessor_hgb_density_diagnostic_is_bound(
        self,
    ) -> None:
        payload = density_protocol_payload()
        predecessor = payload["predecessor"]
        assert isinstance(predecessor, dict)
        diagnostic = predecessor["hgb_density_diagnostic"]
        assert isinstance(diagnostic, dict)

        self.assertEqual(
            PREDECESSOR_HGB_VARIANT_COUNT,
            54,
        )
        self.assertEqual(
            PREDECESSOR_HGB_COUNT_GATE_PASS_COUNT,
            23,
        )
        self.assertEqual(
            PREDECESSOR_HGB_POSITIVE_FINANCIAL_SIGN_COUNT,
            13,
        )
        self.assertEqual(
            PREDECESSOR_HGB_AGGREGATE_GATE_PASS_COUNT,
            1,
        )
        self.assertEqual(
            PREDECESSOR_HGB_POSITIVE_BUT_LOW_COUNT,
            12,
        )
        self.assertEqual(
            diagnostic["evaluated_variant_count"],
            54,
        )
        self.assertEqual(
            diagnostic["positive_but_low_count_count"],
            12,
        )

    def test_logistic_is_excluded_and_hgb_is_unchanged(
        self,
    ) -> None:
        payload = density_protocol_payload()
        families = payload["model_families"]
        assert isinstance(families, dict)

        self.assertEqual(
            AUTHORIZED_MODEL_FAMILIES,
            ("hist_gradient_boosting",),
        )
        self.assertEqual(
            EXCLUDED_MODEL_FAMILIES,
            ("logistic_regression",),
        )
        self.assertEqual(
            families["authorized"],
            ["hist_gradient_boosting"],
        )
        self.assertEqual(
            families["excluded"],
            ["logistic_regression"],
        )
        self.assertFalse(
            families["model_config_change_authorized"]
        )
        self.assertFalse(
            families["logistic_reintroduction_authorized"]
        )

    def test_density_rule_preserves_existing_gates(
        self,
    ) -> None:
        payload = density_protocol_payload()
        selection = payload["selection"]
        assert isinstance(selection, dict)

        self.assertEqual(
            CANDIDATE_BUDGET_ANCHORS,
            (250, 500, 1000),
        )
        self.assertEqual(
            selection["candidate_budget_anchors"],
            [250, 500, 1000],
        )
        self.assertEqual(
            selection["minimum_directional_candidates"],
            MIN_DIRECTIONAL_CANDIDATES,
        )
        self.assertEqual(
            MIN_DIRECTIONAL_CANDIDATES,
            250,
        )
        self.assertFalse(
            selection[
                "minimum_directional_candidate_count_change_authorized"
            ]
        )

        stability = selection["temporal_stability"]
        assert isinstance(stability, dict)
        self.assertEqual(
            stability[
                "minimum_directional_candidate_share_per_window"
            ],
            0.10,
        )
        self.assertTrue(
            stability["all_windows_must_pass"]
        )
        self.assertFalse(
            stability["stability_screen_change_authorized"]
        )
        self.assertEqual(
            len(stability["windows"]),
            4,
        )

    def test_forward_splits_reuse_selection_cutoff(
        self,
    ) -> None:
        payload = density_protocol_payload()
        validation = payload["validation"]
        holdout = payload["retrospective_holdout"]
        assert isinstance(validation, dict)
        assert isinstance(holdout, dict)

        self.assertEqual(
            validation["cutoff_source"],
            "selection",
        )
        self.assertFalse(
            validation["recompute_cutoff_on_validation"]
        )
        self.assertEqual(
            holdout["cutoff_source"],
            "selection",
        )
        self.assertFalse(
            holdout["recompute_cutoff_on_holdout"]
        )

    def test_protocol_fingerprint_is_deterministic(
        self,
    ) -> None:
        first = density_protocol_fingerprint()
        second = density_protocol_fingerprint()

        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)
        int(first, 16)


if __name__ == "__main__":
    unittest.main()
