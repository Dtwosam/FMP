from __future__ import annotations

import unittest

from fmp.market_learning.model_protocol import (
    MIN_DIRECTIONAL_CANDIDATES,
)
from fmp.market_learning.model_successor_regime_consensus_protocol import (
    ALL_REGIME_MODELS_REQUIRED,
    AUTHORIZED_MODEL_FAMILIES,
    CANDIDATE_BUDGET_ANCHORS,
    CONSENSUS_CONFIDENCE_RULE,
    CONSENSUS_DIRECTION_RULE,
    EXCLUDED_MODEL_FAMILIES,
    FIT_REGIME_WINDOWS,
    REGIME_CONSENSUS_EXPERIMENT_ID,
    REGIME_CONSENSUS_PROTOCOL_DECISION,
    REGIME_FALLBACK_AUTHORIZED,
    REQUIRED_REGIME_MODEL_COUNT,
    regime_consensus_protocol_fingerprint,
    regime_consensus_protocol_payload,
    validate_regime_consensus_predecessor_identity,
)


class Exp048RegimeConsensusProtocolTests(unittest.TestCase):
    def test_predecessor_identity_is_exact(self) -> None:
        validate_regime_consensus_predecessor_identity()

    def test_protocol_is_post_result_informed_and_closed(
        self,
    ) -> None:
        payload = regime_consensus_protocol_payload()

        self.assertEqual(
            payload["experiment_id"],
            REGIME_CONSENSUS_EXPERIMENT_ID,
        )
        self.assertEqual(
            payload["protocol_decision"],
            REGIME_CONSENSUS_PROTOCOL_DECISION,
        )
        self.assertEqual(
            REGIME_CONSENSUS_EXPERIMENT_ID,
            "EXP-20260924-048",
        )
        self.assertEqual(
            REGIME_CONSENSUS_PROTOCOL_DECISION,
            "DEC-123",
        )

        predecessor = payload["predecessor"]
        assert isinstance(predecessor, dict)
        self.assertEqual(
            predecessor["result_decision"],
            "DEC-121",
        )
        self.assertEqual(
            predecessor["diagnostic_decision"],
            "DEC-122",
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

    def test_three_disjoint_regime_windows_cover_fit_split(
        self,
    ) -> None:
        payload = regime_consensus_protocol_payload()
        chronology = payload["chronology"]
        assert isinstance(chronology, dict)

        expected = [
            {
                "name": "fit_2015_2016",
                "start": "2015-01-01",
                "end_exclusive": "2017-01-01",
            },
            {
                "name": "fit_2017_2018",
                "start": "2017-01-01",
                "end_exclusive": "2019-01-01",
            },
            {
                "name": "fit_2019_2020",
                "start": "2019-01-01",
                "end_exclusive": "2021-01-01",
            },
        ]
        self.assertEqual(
            chronology["fit_regime_windows"],
            expected,
        )
        self.assertEqual(
            len(FIT_REGIME_WINDOWS),
            REQUIRED_REGIME_MODEL_COUNT,
        )
        self.assertEqual(
            REQUIRED_REGIME_MODEL_COUNT,
            3,
        )
        self.assertTrue(ALL_REGIME_MODELS_REQUIRED)
        self.assertFalse(REGIME_FALLBACK_AUTHORIZED)

    def test_consensus_rule_is_unanimous_and_conservative(
        self,
    ) -> None:
        payload = regime_consensus_protocol_payload()
        consensus = payload["regime_consensus"]
        assert isinstance(consensus, dict)

        self.assertEqual(
            consensus["direction_rule"],
            CONSENSUS_DIRECTION_RULE,
        )
        self.assertIn(
            "all three regime models",
            CONSENSUS_DIRECTION_RULE,
        )
        self.assertIn(
            "same unique top class",
            CONSENSUS_DIRECTION_RULE,
        )
        self.assertEqual(
            consensus["confidence_rule"],
            CONSENSUS_CONFIDENCE_RULE,
        )
        self.assertIn(
            "minimum across the three regime models",
            CONSENSUS_CONFIDENCE_RULE,
        )
        self.assertEqual(
            consensus["disagreement_policy"],
            "NO_TRADE",
        )

    def test_density_and_stability_gates_remain_frozen(
        self,
    ) -> None:
        payload = regime_consensus_protocol_payload()
        selection = payload["selection"]
        assert isinstance(selection, dict)

        self.assertEqual(
            tuple(selection["candidate_budget_anchors"]),
            tuple(CANDIDATE_BUDGET_ANCHORS),
        )
        self.assertEqual(
            tuple(CANDIDATE_BUDGET_ANCHORS),
            (250, 500, 1000),
        )
        self.assertFalse(
            selection["density_anchor_change_authorized"]
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
        self.assertEqual(len(stability["windows"]), 4)
        self.assertTrue(stability["all_windows_must_pass"])
        self.assertFalse(
            stability["stability_screen_change_authorized"]
        )

    def test_hgb_only_without_full_fit_fallback(self) -> None:
        payload = regime_consensus_protocol_payload()
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
            families["hgb_model_config_change_authorized"]
        )
        self.assertFalse(
            families["logistic_reintroduction_authorized"]
        )
        self.assertFalse(
            families["full_fit_single_model_authorized"]
        )

    def test_forward_splits_reuse_selection_cutoff(
        self,
    ) -> None:
        payload = regime_consensus_protocol_payload()
        validation = payload["validation"]
        holdout = payload["retrospective_holdout"]
        assert isinstance(validation, dict)
        assert isinstance(holdout, dict)

        self.assertEqual(
            validation["consensus_models_source"],
            "fit_regime_windows",
        )
        self.assertEqual(
            validation["cutoff_source"],
            "selection",
        )
        self.assertFalse(
            validation["recompute_cutoff_on_validation"]
        )
        self.assertEqual(
            holdout["consensus_models_source"],
            "fit_regime_windows",
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
        first = regime_consensus_protocol_fingerprint()
        second = regime_consensus_protocol_fingerprint()

        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)
        int(first, 16)


if __name__ == "__main__":
    unittest.main()
