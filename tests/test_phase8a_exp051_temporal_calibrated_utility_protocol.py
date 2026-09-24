from __future__ import annotations

import unittest

from fmp.market_learning.model_protocol import (
    GATE_REQUIREMENTS,
    MIN_DIRECTIONAL_CANDIDATES,
)
from fmp.market_learning.model_successor_density_protocol import (
    CANDIDATE_BUDGET_ANCHORS,
)
from fmp.market_learning.model_successor_stability_protocol import (
    STABILITY_WINDOW_REQUIREMENTS,
)
from fmp.market_learning.model_successor_temporal_calibrated_utility_protocol import (
    CALIBRATED_PERCENTILE_RULE,
    CALIBRATION_REFERENCE_RULE,
    OUT_OF_FIT_UTILITY_CALIBRATION_AUTHORIZED,
    PREDECESSOR_DIAGNOSTIC_CLASSIFICATION,
    ROBUST_CALIBRATED_SCORE_RULE,
    SELECTION_CUTOFF_RULE,
    TEMPORAL_CALIBRATED_UTILITY_EXPERIMENT_ID,
    TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_DECISION,
    temporal_calibrated_utility_protocol_fingerprint,
    temporal_calibrated_utility_protocol_payload,
    validate_temporal_calibrated_utility_predecessor_identity,
)


class Exp051TemporalCalibratedUtilityProtocolTests(
    unittest.TestCase
):
    def test_predecessor_identity_is_exact(self) -> None:
        validate_temporal_calibrated_utility_predecessor_identity()

    def test_protocol_is_post_result_informed_and_closed(self) -> None:
        payload = temporal_calibrated_utility_protocol_payload()

        self.assertEqual(
            payload["experiment_id"],
            TEMPORAL_CALIBRATED_UTILITY_EXPERIMENT_ID,
        )
        self.assertEqual(
            TEMPORAL_CALIBRATED_UTILITY_EXPERIMENT_ID,
            "EXP-20260924-051",
        )
        self.assertEqual(
            payload["protocol_decision"],
            TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_DECISION,
        )
        self.assertEqual(
            TEMPORAL_CALIBRATED_UTILITY_PROTOCOL_DECISION,
            "DEC-150",
        )

        predecessor = payload["predecessor"]
        assert isinstance(predecessor, dict)
        self.assertEqual(
            predecessor["experiment_id"],
            "EXP-20260924-050",
        )
        self.assertEqual(
            predecessor["result_decision"],
            "DEC-148",
        )
        self.assertEqual(
            predecessor["diagnostic_decision"],
            "DEC-149",
        )
        self.assertEqual(
            predecessor["diagnostic_classification"],
            PREDECESSOR_DIAGNOSTIC_CLASSIFICATION,
        )
        self.assertEqual(
            predecessor["diagnostic_classification"],
            (
                "UTILITY_COVERAGE_INCREASED_BUT_"
                "EARLY_TEMPORAL_COVERAGE_LIMITED"
            ),
        )
        self.assertEqual(
            predecessor["available_variant_count"],
            28,
        )
        self.assertEqual(
            predecessor["unavailable_budget_variant_count"],
            26,
        )
        self.assertEqual(
            predecessor["aggregate_selection_pass_variant_count"],
            3,
        )
        self.assertEqual(
            predecessor["stable_selection_pass_variant_count"],
            0,
        )
        self.assertEqual(
            predecessor[
                "selection_2021_h1_zero_candidate_variant_count"
            ],
            3,
        )
        self.assertTrue(predecessor["prior_result_informed"])
        self.assertFalse(predecessor["untouched_oos"])

        authorization = payload["authorization"]
        assert isinstance(authorization, dict)
        for field in (
            "model_protocol_result_authorized",
            "model_fit_authorized",
            "historical_result_execution_authorized",
            "feature_change_authorized",
            "financial_target_change_authorized",
            "outer_chronology_change_authorized",
            "hgb_structural_config_change_authorized",
            "jackknife_view_change_authorized",
            "unanimous_utility_consensus_change_authorized",
            "positive_utility_requirement_change_authorized",
            "selection_window_calibration_authorized",
            "validation_calibration_authorized",
            "holdout_calibration_authorized",
            "logistic_reintroduction_authorized",
            "classifier_fallback_authorized",
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

    def test_only_ranking_scale_changes_from_exp050(self) -> None:
        payload = temporal_calibrated_utility_protocol_payload()

        jackknife = payload["temporal_jackknife"]
        consensus = payload["utility_consensus"]
        calibration = payload["out_of_fit_utility_calibration"]
        assert isinstance(jackknife, dict)
        assert isinstance(consensus, dict)
        assert isinstance(calibration, dict)

        self.assertFalse(jackknife["view_change_authorized"])
        self.assertIn(
            "greater than zero",
            consensus["direction_rule"],
        )
        self.assertEqual(
            consensus["disagreement_policy"],
            "NO_TRADE",
        )
        self.assertTrue(
            consensus["positive_predicted_utility_required"]
        )
        self.assertFalse(
            consensus[
                "positive_utility_requirement_change_authorized"
            ]
        )
        self.assertIn(
            "minimum predicted net pips",
            consensus["raw_score_rule"],
        )
        self.assertEqual(
            consensus["ranking_score_rule"],
            ROBUST_CALIBRATED_SCORE_RULE,
        )

        self.assertIs(
            OUT_OF_FIT_UTILITY_CALIBRATION_AUTHORIZED,
            True,
        )
        self.assertIs(
            calibration["authorized_protocol_change"],
            True,
        )
        self.assertEqual(
            calibration["reference_count_per_cell"],
            6,
        )
        self.assertFalse(
            calibration["uses_realized_outcomes"]
        )
        self.assertFalse(
            calibration["selection_rows_enter_calibration"]
        )
        self.assertFalse(
            calibration["validation_rows_enter_calibration"]
        )
        self.assertFalse(
            calibration["holdout_rows_enter_calibration"]
        )

    def test_calibration_uses_only_excluded_fit_regime_predictions(
        self,
    ) -> None:
        payload = temporal_calibrated_utility_protocol_payload()
        calibration = payload["out_of_fit_utility_calibration"]
        assert isinstance(calibration, dict)

        self.assertEqual(
            calibration["reference_rule"],
            CALIBRATION_REFERENCE_RULE,
        )
        self.assertIn(
            "excluded from that view",
            CALIBRATION_REFERENCE_RULE,
        )
        self.assertIn(
            "selection rows",
            CALIBRATION_REFERENCE_RULE,
        )
        self.assertEqual(
            calibration["percentile_rule"],
            CALIBRATED_PERCENTILE_RULE,
        )
        self.assertIn(
            "count(reference_prediction <= raw_predicted_utility)",
            CALIBRATED_PERCENTILE_RULE,
        )
        self.assertEqual(
            calibration["robust_score_rule"],
            ROBUST_CALIBRATED_SCORE_RULE,
        )
        self.assertIn(
            "minimum",
            ROBUST_CALIBRATED_SCORE_RULE,
        )

    def test_selection_and_stability_gates_are_not_weakened(
        self,
    ) -> None:
        payload = temporal_calibrated_utility_protocol_payload()
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
        self.assertEqual(
            selection["selection_cutoff_rule"],
            SELECTION_CUTOFF_RULE,
        )
        self.assertIn(
            "robust calibrated utility descending",
            SELECTION_CUTOFF_RULE,
        )
        self.assertFalse(
            selection["selection_window_calibration_authorized"]
        )
        self.assertFalse(
            selection["per_window_cutoff_tuning_authorized"]
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

    def test_forward_calibration_and_cutoff_are_frozen(self) -> None:
        payload = temporal_calibrated_utility_protocol_payload()
        selection = payload["selection"]
        validation = payload["validation"]
        holdout = payload["retrospective_holdout"]
        assert isinstance(selection, dict)
        assert isinstance(validation, dict)
        assert isinstance(holdout, dict)

        self.assertIn(
            "exact six frozen excluded-regime calibration references",
            selection["forward_application_rule"],
        )
        self.assertEqual(
            validation["calibration_reference_source"],
            "frozen_excluded_fit_regimes",
        )
        self.assertFalse(
            validation[
                "rebuild_calibration_reference_on_validation"
            ]
        )
        self.assertFalse(validation["refit_on_validation"])
        self.assertEqual(
            holdout["calibration_reference_source"],
            "frozen_excluded_fit_regimes",
        )
        self.assertFalse(
            holdout[
                "rebuild_calibration_reference_on_holdout"
            ]
        )
        self.assertFalse(holdout["refit_on_holdout"])

    def test_protocol_fingerprint_is_deterministic(self) -> None:
        first = temporal_calibrated_utility_protocol_fingerprint()
        second = temporal_calibrated_utility_protocol_fingerprint()

        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)
        int(first, 16)


if __name__ == "__main__":
    unittest.main()
