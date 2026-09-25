from __future__ import annotations

import unittest

from fmp.market_learning.model_successor_fit_temporal_residual_bound_utility_protocol import (
    FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL,
    fit_temporal_residual_bound_utility_protocol_payload,
)
from fmp.market_learning.model_successor_fit_temporal_residual_breadth_utility_protocol import (
    FIT_TEMPORAL_RESIDUAL_BREADTH_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_BREADTH_BOUND_COUNT_PER_ROW,
    FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_PROTOCOL_VERSION,
    HISTORICAL_RESULT_EXECUTION_AUTHORIZED,
    MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED,
    PRIOR_RESULT_INFORMED,
    RANKING_RULE,
    TRADING_AUTHORIZED,
    UNTOUCHED_OOS,
    fit_temporal_residual_breadth_utility_protocol_fingerprint,
    fit_temporal_residual_breadth_utility_protocol_payload,
    validate_fit_temporal_residual_breadth_predecessor_identity,
)


class Exp055FitTemporalResidualBreadthProtocolTests(unittest.TestCase):
    def test_identity_and_fingerprint_are_frozen(self) -> None:
        validate_fit_temporal_residual_breadth_predecessor_identity()
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_EXPERIMENT_ID,
            "EXP-20260925-055",
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_PROTOCOL_DECISION,
            "DEC-198",
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_PROTOCOL_VERSION,
            "fmp-exp055-fit-temporal-residual-breadth-utility-protocol-v1",
        )
        first = fit_temporal_residual_breadth_utility_protocol_fingerprint()
        second = fit_temporal_residual_breadth_utility_protocol_fingerprint()
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)
        int(first, 16)

    def test_breadth_reuses_exp054_residual_bounds_only(self) -> None:
        payload = fit_temporal_residual_breadth_utility_protocol_payload()
        breadth = payload["fit_temporal_residual_breadth"]
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL,
            24,
        )
        self.assertEqual(
            breadth["source_residual_reference_count_per_cell"],
            24,
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_BREADTH_BOUND_COUNT_PER_ROW,
            12,
        )
        self.assertEqual(
            breadth["source_lower_bound_count_per_row"],
            12,
        )
        self.assertTrue(
            breadth["uses_existing_exp054_residual_references"]
        )
        self.assertFalse(breadth["creates_new_reference_vectors"])
        self.assertTrue(
            breadth["uses_realized_fit_outcomes_via_frozen_residuals"]
        )
        self.assertFalse(breadth["uses_realized_selection_outcomes"])
        self.assertFalse(
            breadth["uses_realized_validation_outcomes_for_ranking"]
        )
        self.assertFalse(
            breadth["uses_realized_holdout_outcomes_for_ranking"]
        )
        self.assertFalse(
            breadth["selection_window_identity_enters_ranking"]
        )
        self.assertFalse(breadth["selection_window_quota_used"])
        self.assertFalse(breadth["stability_gate_changed"])
        self.assertEqual(breadth["score_minimum"], 0.0)
        self.assertEqual(breadth["score_maximum"], 1.0)
        self.assertAlmostEqual(breadth["score_increment"], 1.0 / 12.0)

    def test_exp054_residual_bound_block_is_retained_exactly(self) -> None:
        predecessor = fit_temporal_residual_bound_utility_protocol_payload()
        payload = fit_temporal_residual_breadth_utility_protocol_payload()
        self.assertEqual(
            payload["fit_temporal_residual_bound"],
            predecessor["fit_temporal_residual_bound"],
        )
        utility = payload["utility_consensus"]
        self.assertTrue(
            utility["fit_temporal_residual_bound_retained"]
        )
        self.assertTrue(
            utility["fit_temporal_residual_breadth_added"]
        )
        self.assertEqual(utility["ranking_score_rule"], RANKING_RULE)

    def test_ranking_and_cutoff_are_breadth_first(self) -> None:
        payload = fit_temporal_residual_breadth_utility_protocol_payload()
        selection = payload["selection"]
        self.assertEqual(
            selection["candidate_budget_anchors"],
            [250, 500, 1000],
        )
        self.assertEqual(
            selection["ranking_order"],
            [
                "fit_temporal_residual_breadth_desc",
                "robust_fit_temporal_residual_bound_utility_desc",
                "robust_fit_temporal_feature_support_desc",
                "robust_fit_temporal_support_desc",
                "robust_pooled_calibrated_utility_desc",
                "robust_raw_utility_desc",
                "row_identity_asc",
            ],
        )
        self.assertEqual(
            selection["cutoff_components"],
            [
                "fit_temporal_residual_breadth",
                "robust_fit_temporal_residual_bound_utility",
                "robust_fit_temporal_feature_support",
                "robust_fit_temporal_support",
                "robust_pooled_calibrated_utility",
                "robust_raw_utility",
            ],
        )

    def test_existing_stability_gate_is_unchanged(self) -> None:
        predecessor = fit_temporal_residual_bound_utility_protocol_payload()
        payload = fit_temporal_residual_breadth_utility_protocol_payload()
        stability = payload["selection"]["temporal_stability"]
        self.assertEqual(
            stability,
            predecessor["selection"]["temporal_stability"],
        )
        self.assertEqual(len(stability["windows"]), 4)
        self.assertEqual(
            stability["minimum_directional_candidate_share_per_window"],
            0.10,
        )
        self.assertTrue(stability["all_windows_must_pass"])
        self.assertFalse(stability["stability_screen_change_authorized"])
        self.assertFalse(
            stability["per_window_financial_gate_change_authorized"]
        )

    def test_forward_stages_reuse_frozen_breadth_cutoff(self) -> None:
        payload = fit_temporal_residual_breadth_utility_protocol_payload()
        validation = payload["validation"]
        holdout = payload["retrospective_holdout"]
        expected = "frozen_exp054_fit_half_year_residual_bounds"
        self.assertEqual(
            validation["fit_temporal_residual_breadth_source"],
            expected,
        )
        self.assertFalse(
            validation[
                "rebuild_fit_temporal_residual_breadth_on_validation"
            ]
        )
        self.assertTrue(
            validation[
                "selection_derived_residual_breadth_cutoff_reused"
            ]
        )
        self.assertEqual(
            holdout["fit_temporal_residual_breadth_source"],
            expected,
        )
        self.assertFalse(
            holdout[
                "rebuild_fit_temporal_residual_breadth_on_holdout"
            ]
        )
        self.assertTrue(
            holdout[
                "selection_derived_residual_breadth_cutoff_reused"
            ]
        )

    def test_only_residual_breadth_protocol_change_is_open(self) -> None:
        payload = fit_temporal_residual_breadth_utility_protocol_payload()
        auth = payload["authorization"]
        self.assertTrue(FIT_TEMPORAL_RESIDUAL_BREADTH_AUTHORIZED)
        self.assertTrue(
            auth["fit_temporal_residual_breadth_authorized"]
        )

        for field in (
            "feature_change_authorized",
            "financial_target_change_authorized",
            "outer_chronology_change_authorized",
            "hgb_structural_config_change_authorized",
            "jackknife_view_change_authorized",
            "unanimous_utility_consensus_change_authorized",
            "positive_utility_requirement_change_authorized",
            "pooled_out_of_fit_calibration_change_authorized",
            "fit_temporal_utility_support_change_authorized",
            "fit_temporal_feature_support_change_authorized",
            "fit_temporal_residual_bound_change_authorized",
            "selection_window_calibration_authorized",
            "selection_window_quota_authorized",
            "validation_calibration_authorized",
            "holdout_calibration_authorized",
            "realized_selection_outcome_ranking_authorized",
            "density_anchor_change_authorized",
            "minimum_directional_candidate_count_change_authorized",
            "stability_screen_change_authorized",
            "per_window_financial_gate_change_authorized",
            "per_window_cutoff_tuning_authorized",
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
                self.assertIs(auth[field], False)

        self.assertFalse(MODEL_PROTOCOL_RESULT_AUTHORIZED)
        self.assertFalse(MODEL_FIT_AUTHORIZED)
        self.assertFalse(HISTORICAL_RESULT_EXECUTION_AUTHORIZED)
        self.assertFalse(TRADING_AUTHORIZED)

    def test_result_informed_not_untouched_oos(self) -> None:
        self.assertTrue(PRIOR_RESULT_INFORMED)
        self.assertFalse(UNTOUCHED_OOS)


if __name__ == "__main__":
    unittest.main()
