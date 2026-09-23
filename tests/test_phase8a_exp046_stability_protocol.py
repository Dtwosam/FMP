from __future__ import annotations

import unittest

from fmp.market_learning.model_protocol import (
    CONFIDENCE_THRESHOLDS,
    MIN_DIRECTIONAL_CANDIDATES,
)
from fmp.market_learning.model_successor_stability_protocol import (
    MIN_STABILITY_WINDOW_CANDIDATE_SHARE,
    STABILITY_PROTOCOL_DECISION,
    STABILITY_SUCCESSOR_EXPERIMENT_ID,
    TEMPORAL_STABILITY_WINDOWS,
    stability_protocol_fingerprint,
    stability_protocol_payload,
    validate_predecessor_identity,
)


class Exp046StabilityProtocolTests(unittest.TestCase):
    def test_predecessor_identity_is_exact(self) -> None:
        validate_predecessor_identity()

    def test_protocol_is_post_result_informed_and_closed(
        self,
    ) -> None:
        payload = stability_protocol_payload()

        self.assertEqual(
            payload["experiment_id"],
            STABILITY_SUCCESSOR_EXPERIMENT_ID,
        )
        self.assertEqual(
            payload["protocol_decision"],
            STABILITY_PROTOCOL_DECISION,
        )
        predecessor = payload["predecessor"]
        assert isinstance(predecessor, dict)
        self.assertEqual(
            predecessor["experiment_id"],
            "EXP-20260923-045",
        )
        self.assertEqual(
            predecessor["result_decision"],
            "DEC-102",
        )
        self.assertEqual(
            predecessor["diagnostic_decision"],
            "DEC-103",
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

    def test_only_selection_stability_rule_changes(
        self,
    ) -> None:
        payload = stability_protocol_payload()
        selection = payload["selection"]
        assert isinstance(selection, dict)

        self.assertEqual(
            selection["confidence_thresholds"],
            list(CONFIDENCE_THRESHOLDS),
        )
        self.assertFalse(
            selection[
                "confidence_threshold_change_authorized"
            ]
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
        self.assertTrue(
            selection["aggregate_gate_must_pass"]
        )

        model_families = payload["model_families"]
        assert isinstance(model_families, dict)
        self.assertFalse(
            model_families["family_change_authorized"]
        )
        self.assertFalse(
            model_families["config_change_authorized"]
        )
        self.assertFalse(
            model_families["logistic_rescue_authorized"]
        )

        inputs = payload["inputs"]
        target = payload["target"]
        chronology = payload["chronology"]
        assert isinstance(inputs, dict)
        assert isinstance(target, dict)
        assert isinstance(chronology, dict)
        self.assertFalse(
            inputs["feature_change_authorized"]
        )
        self.assertFalse(
            target["target_change_authorized"]
        )
        self.assertFalse(
            chronology["data_split_change_authorized"]
        )

    def test_temporal_stability_windows_cover_selection(
        self,
    ) -> None:
        payload = stability_protocol_payload()
        selection = payload["selection"]
        assert isinstance(selection, dict)
        stability = selection["temporal_stability"]
        assert isinstance(stability, dict)

        expected = [
            {
                "name": "selection_2021_h1",
                "start": "2021-01-01",
                "end_exclusive": "2021-07-01",
            },
            {
                "name": "selection_2021_h2",
                "start": "2021-07-01",
                "end_exclusive": "2022-01-01",
            },
            {
                "name": "selection_2022_h1",
                "start": "2022-01-01",
                "end_exclusive": "2022-07-01",
            },
            {
                "name": "selection_2022_h2",
                "start": "2022-07-01",
                "end_exclusive": "2023-01-01",
            },
        ]
        self.assertEqual(
            stability["windows"],
            expected,
        )
        self.assertEqual(
            len(TEMPORAL_STABILITY_WINDOWS),
            4,
        )
        self.assertEqual(
            stability[
                "minimum_directional_candidate_share_per_window"
            ],
            MIN_STABILITY_WINDOW_CANDIDATE_SHARE,
        )
        self.assertEqual(
            MIN_STABILITY_WINDOW_CANDIDATE_SHARE,
            0.10,
        )
        self.assertTrue(
            stability["all_windows_must_pass"]
        )
        self.assertEqual(
            stability["requirements_per_window"],
            [
                "directional_candidate_share>=0.10",
                "total_net_pips>0",
                "mean_net_pips>0",
                (
                    "gross_positive_pips>"
                    "absolute_gross_negative_pips"
                ),
            ],
        )

    def test_protocol_fingerprint_is_deterministic(
        self,
    ) -> None:
        first = stability_protocol_fingerprint()
        second = stability_protocol_fingerprint()

        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)
        int(first, 16)


if __name__ == "__main__":
    unittest.main()
