from __future__ import annotations

import unittest

from fmp.market_learning.model_successor_fit_temporal_residual_bound_utility_protocol import (
    FIT_TEMPORAL_RESIDUAL_BOUND_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_PROTOCOL_VERSION,
    FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL,
    HISTORICAL_RESULT_EXECUTION_AUTHORIZED,
    MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED,
    PRIOR_RESULT_INFORMED,
    RANKING_RULE,
    RESIDUAL_DOWNSIDE_QUANTILE,
    TRADING_AUTHORIZED,
    UNTOUCHED_OOS,
    fit_temporal_residual_bound_utility_protocol_fingerprint,
    fit_temporal_residual_bound_utility_protocol_payload,
    validate_fit_temporal_residual_bound_predecessor_identity,
)


class Exp054FitTemporalResidualBoundProtocolTests(unittest.TestCase):
    def test_identity_and_fingerprint_are_frozen(self) -> None:
        validate_fit_temporal_residual_bound_predecessor_identity()
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_EXPERIMENT_ID,
            "EXP-20260925-054",
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_PROTOCOL_DECISION,
            "DEC-185",
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_PROTOCOL_VERSION,
            "fmp-exp054-fit-temporal-residual-bound-utility-protocol-v1",
        )
        first = fit_temporal_residual_bound_utility_protocol_fingerprint()
        second = fit_temporal_residual_bound_utility_protocol_fingerprint()
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)
        int(first, 16)

    def test_residual_references_are_out_of_fit_and_fit_only(self) -> None:
        payload = fit_temporal_residual_bound_utility_protocol_payload()
        residual = payload["fit_temporal_residual_bound"]
        self.assertEqual(
            residual["reference_count_per_cell"],
            FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL,
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL,
            24,
        )
        self.assertEqual(len(residual["reference_windows"]), 12)
        self.assertEqual(
            residual["reference_windows_per_view"],
            4,
        )
        self.assertEqual(
            residual["downside_quantile"],
            RESIDUAL_DOWNSIDE_QUANTILE,
        )
        self.assertEqual(RESIDUAL_DOWNSIDE_QUANTILE, 0.25)
        self.assertTrue(
            residual["reference_model_is_out_of_fit_for_reference_window"]
        )
        self.assertTrue(residual["uses_realized_fit_outcomes"])
        self.assertFalse(
            residual["uses_realized_selection_outcomes"]
        )
        self.assertFalse(
            residual["uses_realized_validation_outcomes_for_ranking"]
        )
        self.assertFalse(
            residual["uses_realized_holdout_outcomes_for_ranking"]
        )
        self.assertFalse(residual["selection_rows_enter_references"])
        self.assertFalse(residual["validation_rows_enter_references"])
        self.assertFalse(residual["holdout_rows_enter_references"])
        self.assertFalse(
            residual["selection_window_identity_enters_ranking"]
        )

    def test_exp053_eligibility_and_support_layers_are_retained(self) -> None:
        payload = fit_temporal_residual_bound_utility_protocol_payload()
        self.assertEqual(
            payload["fit_temporal_support_calibration"][
                "reference_count_per_cell"
            ],
            24,
        )
        self.assertEqual(
            payload["fit_temporal_feature_support"][
                "reference_count_per_cell"
            ],
            12,
        )
        utility = payload["utility_consensus"]
        self.assertTrue(
            utility["fit_temporal_feature_support_retained"]
        )
        self.assertTrue(
            utility["fit_temporal_residual_bound_added"]
        )
        self.assertEqual(utility["ranking_score_rule"], RANKING_RULE)

    def test_ranking_and_cutoff_are_residual_bound_first(self) -> None:
        payload = fit_temporal_residual_bound_utility_protocol_payload()
        selection = payload["selection"]
        self.assertEqual(
            selection["candidate_budget_anchors"],
            [250, 500, 1000],
        )
        self.assertEqual(
            selection["ranking_order"],
            [
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
                "robust_fit_temporal_residual_bound_utility",
                "robust_fit_temporal_feature_support",
                "robust_fit_temporal_support",
                "robust_pooled_calibrated_utility",
                "robust_raw_utility",
            ],
        )

    def test_existing_stability_gate_is_unchanged(self) -> None:
        payload = fit_temporal_residual_bound_utility_protocol_payload()
        stability = payload["selection"]["temporal_stability"]
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

    def test_forward_stages_reuse_frozen_residual_references(self) -> None:
        payload = fit_temporal_residual_bound_utility_protocol_payload()
        validation = payload["validation"]
        holdout = payload["retrospective_holdout"]
        expected = (
            "frozen_excluded_fit_regime_half_year_out_of_fit_residuals"
        )
        self.assertEqual(
            validation["fit_temporal_residual_reference_source"],
            expected,
        )
        self.assertFalse(
            validation["rebuild_fit_temporal_residuals_on_validation"]
        )
        self.assertTrue(
            validation[
                "selection_derived_residual_bound_cutoff_reused"
            ]
        )
        self.assertEqual(
            holdout["fit_temporal_residual_reference_source"],
            expected,
        )
        self.assertFalse(
            holdout["rebuild_fit_temporal_residuals_on_holdout"]
        )
        self.assertTrue(
            holdout["selection_derived_residual_bound_cutoff_reused"]
        )

    def test_only_residual_bound_protocol_change_is_open(self) -> None:
        payload = fit_temporal_residual_bound_utility_protocol_payload()
        auth = payload["authorization"]
        self.assertTrue(FIT_TEMPORAL_RESIDUAL_BOUND_AUTHORIZED)
        self.assertTrue(
            auth["fit_temporal_residual_bound_authorized"]
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
