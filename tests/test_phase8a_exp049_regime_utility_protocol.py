from __future__ import annotations

import unittest

from fmp.market_learning.model_protocol import (
    GATE_REQUIREMENTS,
    HIST_GRADIENT_BOOSTING_CONFIG,
    MIN_DIRECTIONAL_CANDIDATES,
)
from fmp.market_learning.model_successor_regime_utility_protocol import (
    AUTHORIZED_MODEL_FAMILIES,
    CANDIDATE_BUDGET_ANCHORS,
    EXCLUDED_MODEL_FAMILIES,
    FINANCIAL_TARGET_COLUMNS,
    FINANCIAL_TARGET_SLIPPAGE_PIPS,
    FIT_REGIME_WINDOWS,
    HIST_GRADIENT_BOOSTING_REGRESSION_CONFIG,
    REGIME_UTILITY_DIRECTION_RULE,
    REGIME_UTILITY_EXPERIMENT_ID,
    REGIME_UTILITY_PROTOCOL_DECISION,
    REGIME_UTILITY_SCORE_RULE,
    REQUIRED_REGIME_MODEL_COUNT,
    REQUIRED_REGRESSORS_PER_REGIME,
    TOTAL_REGRESSORS_PER_CELL,
    regime_utility_protocol_fingerprint,
    regime_utility_protocol_payload,
    validate_regime_utility_predecessor_identity,
)
from fmp.market_learning.model_successor_stability_protocol import (
    STABILITY_WINDOW_REQUIREMENTS,
)


class Exp049RegimeUtilityProtocolTests(unittest.TestCase):
    def test_predecessor_identity_is_exact(self) -> None:
        validate_regime_utility_predecessor_identity()

    def test_protocol_is_post_result_informed_and_closed(self) -> None:
        payload = regime_utility_protocol_payload()

        self.assertEqual(
            payload["experiment_id"],
            REGIME_UTILITY_EXPERIMENT_ID,
        )
        self.assertEqual(
            REGIME_UTILITY_EXPERIMENT_ID,
            "EXP-20260924-049",
        )
        self.assertEqual(
            payload["protocol_decision"],
            REGIME_UTILITY_PROTOCOL_DECISION,
        )
        self.assertEqual(
            REGIME_UTILITY_PROTOCOL_DECISION,
            "DEC-132",
        )

        predecessor = payload["predecessor"]
        assert isinstance(predecessor, dict)
        self.assertEqual(
            predecessor["experiment_id"],
            "EXP-20260924-048",
        )
        self.assertEqual(
            predecessor["result_decision"],
            "DEC-130",
        )
        self.assertEqual(
            predecessor["diagnostic_decision"],
            "DEC-131",
        )
        self.assertEqual(
            predecessor["diagnostic_classification"],
            "WINDOW_FINANCIAL_INSTABILITY_DOMINANT",
        )
        self.assertTrue(predecessor["prior_result_informed"])
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
                self.assertIs(authorization[field], False)

    def test_financial_targets_are_exact_cost_aware_outcomes(self) -> None:
        payload = regime_utility_protocol_payload()
        targets = payload["financial_targets"]
        assert isinstance(targets, dict)

        self.assertEqual(
            tuple(targets["columns"]),
            FINANCIAL_TARGET_COLUMNS,
        )
        self.assertEqual(
            FINANCIAL_TARGET_COLUMNS,
            (
                "long_net_pips_0p5",
                "short_net_pips_0p5",
            ),
        )
        self.assertEqual(
            targets["slippage_pips_per_fill"],
            FINANCIAL_TARGET_SLIPPAGE_PIPS,
        )
        self.assertEqual(
            FINANCIAL_TARGET_SLIPPAGE_PIPS,
            0.5,
        )
        self.assertEqual(
            targets["predecessor_class_target"],
            "best_direction_0p5",
        )
        self.assertTrue(
            targets["predecessor_class_target_replaced"]
        )
        self.assertFalse(
            targets["further_target_change_authorized"]
        )

    def test_three_regimes_fit_two_hgb_regressors_each(self) -> None:
        payload = regime_utility_protocol_payload()
        chronology = payload["chronology"]
        models = payload["model_family"]
        assert isinstance(chronology, dict)
        assert isinstance(models, dict)

        self.assertEqual(len(FIT_REGIME_WINDOWS), 3)
        self.assertEqual(
            REQUIRED_REGIME_MODEL_COUNT,
            3,
        )
        self.assertEqual(
            REQUIRED_REGRESSORS_PER_REGIME,
            2,
        )
        self.assertEqual(
            TOTAL_REGRESSORS_PER_CELL,
            6,
        )
        self.assertEqual(
            len(chronology["fit_regime_windows"]),
            3,
        )
        self.assertEqual(
            models["total_regressors_per_cell"],
            6,
        )
        self.assertEqual(
            AUTHORIZED_MODEL_FAMILIES,
            ("hist_gradient_boosting_regression",),
        )
        self.assertEqual(
            EXCLUDED_MODEL_FAMILIES,
            (
                "logistic_regression",
                "hist_gradient_boosting_classifier",
            ),
        )

    def test_regression_structure_matches_frozen_hgb_shape(self) -> None:
        config = dict(
            HIST_GRADIENT_BOOSTING_REGRESSION_CONFIG
        )
        self.assertEqual(config["loss"], "squared_error")

        for key in (
            "learning_rate",
            "max_iter",
            "max_leaf_nodes",
            "max_depth",
            "min_samples_leaf",
            "l2_regularization",
            "max_features",
            "max_bins",
            "early_stopping",
            "warm_start",
            "random_state",
        ):
            with self.subTest(key=key):
                self.assertEqual(
                    config[key],
                    HIST_GRADIENT_BOOSTING_CONFIG[key],
                )

    def test_utility_consensus_targets_positive_financial_sign(self) -> None:
        payload = regime_utility_protocol_payload()
        consensus = payload["regime_utility_consensus"]
        assert isinstance(consensus, dict)

        self.assertEqual(
            consensus["direction_rule"],
            REGIME_UTILITY_DIRECTION_RULE,
        )
        self.assertIn(
            "greater than zero",
            REGIME_UTILITY_DIRECTION_RULE,
        )
        self.assertIn(
            "all three fit regimes",
            REGIME_UTILITY_DIRECTION_RULE,
        )
        self.assertEqual(
            consensus["score_rule"],
            REGIME_UTILITY_SCORE_RULE,
        )
        self.assertIn(
            "minimum predicted net pips",
            REGIME_UTILITY_SCORE_RULE,
        )
        self.assertEqual(
            consensus["disagreement_policy"],
            "NO_TRADE",
        )

    def test_density_and_stability_gates_are_not_weakened(self) -> None:
        payload = regime_utility_protocol_payload()
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
        self.assertEqual(
            selection["minimum_directional_candidates"],
            MIN_DIRECTIONAL_CANDIDATES,
        )
        self.assertEqual(MIN_DIRECTIONAL_CANDIDATES, 250)
        self.assertEqual(
            tuple(selection["aggregate_gate_requirements"]),
            tuple(GATE_REQUIREMENTS),
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
        self.assertEqual(
            tuple(stability["requirements_per_window"]),
            tuple(STABILITY_WINDOW_REQUIREMENTS),
        )
        self.assertTrue(stability["all_windows_must_pass"])
        self.assertFalse(
            stability["stability_screen_change_authorized"]
        )
        self.assertFalse(
            stability[
                "per_window_financial_gate_change_authorized"
            ]
        )

    def test_cutoff_is_selection_derived_and_never_window_tuned(self) -> None:
        payload = regime_utility_protocol_payload()
        selection = payload["selection"]
        validation = payload["validation"]
        holdout = payload["retrospective_holdout"]
        assert isinstance(selection, dict)
        assert isinstance(validation, dict)
        assert isinstance(holdout, dict)

        self.assertFalse(
            selection["per_window_cutoff_tuning_authorized"]
        )
        self.assertFalse(
            selection["per_window_utility_recalibration_authorized"]
        )
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

    def test_protocol_fingerprint_is_deterministic(self) -> None:
        first = regime_utility_protocol_fingerprint()
        second = regime_utility_protocol_fingerprint()

        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)
        int(first, 16)


if __name__ == "__main__":
    unittest.main()
