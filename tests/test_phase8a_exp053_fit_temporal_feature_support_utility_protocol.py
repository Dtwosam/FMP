from __future__ import annotations

import unittest

from fmp.market_learning.model_successor_fit_temporal_feature_support_utility_protocol import (
    FIT_TEMPORAL_FEATURE_SUPPORT_AUTHORIZED,
    FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_VERSION,
    HISTORICAL_RESULT_EXECUTION_AUTHORIZED,
    MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED,
    PRIOR_RESULT_INFORMED,
    RANKING_RULE,
    TRADING_AUTHORIZED,
    UNTOUCHED_OOS,
    fit_temporal_feature_support_utility_protocol_fingerprint,
    fit_temporal_feature_support_utility_protocol_payload,
    validate_fit_temporal_feature_support_predecessor_identity,
)


class Exp053FitTemporalFeatureSupportProtocolTests(unittest.TestCase):
    def test_identity_and_fingerprint_are_frozen(self) -> None:
        validate_fit_temporal_feature_support_predecessor_identity()
        self.assertEqual(
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_EXPERIMENT_ID,
            "EXP-20260925-053",
        )
        self.assertEqual(
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_DECISION,
            "DEC-174",
        )
        self.assertEqual(
            FIT_TEMPORAL_FEATURE_SUPPORT_UTILITY_PROTOCOL_VERSION,
            "fmp-exp053-fit-temporal-feature-support-utility-protocol-v1",
        )
        first = fit_temporal_feature_support_utility_protocol_fingerprint()
        second = fit_temporal_feature_support_utility_protocol_fingerprint()
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)
        int(first, 16)

    def test_feature_support_references_are_fit_only(self) -> None:
        payload = fit_temporal_feature_support_utility_protocol_payload()
        support = payload["fit_temporal_feature_support"]
        self.assertEqual(
            support["reference_count_per_cell"],
            FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL,
        )
        self.assertEqual(
            FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL,
            12,
        )
        self.assertEqual(len(support["reference_windows"]), 12)
        self.assertEqual(support["reference_windows_per_view"], 4)
        self.assertTrue(support["view_preprocessor_reused"])
        self.assertFalse(support["uses_realized_outcomes"])
        self.assertFalse(support["selection_rows_enter_references"])
        self.assertFalse(support["validation_rows_enter_references"])
        self.assertFalse(support["holdout_rows_enter_references"])
        self.assertFalse(
            support["selection_window_identity_enters_ranking"]
        )
        self.assertEqual(support["aggregation"], "minimum")

    def test_exp052_utility_support_is_retained(self) -> None:
        payload = fit_temporal_feature_support_utility_protocol_payload()
        utility_support = payload["fit_temporal_support_calibration"]
        self.assertEqual(utility_support["reference_count_per_cell"], 24)
        self.assertFalse(utility_support["uses_realized_outcomes"])
        utility = payload["utility_consensus"]
        self.assertTrue(utility["fit_temporal_utility_support_retained"])
        self.assertTrue(utility["fit_temporal_feature_support_added"])
        self.assertEqual(utility["ranking_score_rule"], RANKING_RULE)

    def test_ranking_and_cutoff_are_feature_support_first(self) -> None:
        payload = fit_temporal_feature_support_utility_protocol_payload()
        selection = payload["selection"]
        self.assertEqual(
            selection["candidate_budget_anchors"],
            [250, 500, 1000],
        )
        self.assertEqual(
            selection["ranking_order"],
            [
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
                "robust_fit_temporal_feature_support",
                "robust_fit_temporal_support",
                "robust_pooled_calibrated_utility",
                "robust_raw_utility",
            ],
        )

    def test_existing_stability_gate_is_unchanged(self) -> None:
        payload = fit_temporal_feature_support_utility_protocol_payload()
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

    def test_forward_stages_reuse_feature_support(self) -> None:
        payload = fit_temporal_feature_support_utility_protocol_payload()
        validation = payload["validation"]
        holdout = payload["retrospective_holdout"]
        self.assertEqual(
            validation["fit_temporal_feature_support_reference_source"],
            "frozen_excluded_fit_regime_half_year_features",
        )
        self.assertFalse(
            validation[
                "rebuild_fit_temporal_feature_support_on_validation"
            ]
        )
        self.assertTrue(
            validation["selection_derived_feature_support_cutoff_reused"]
        )
        self.assertEqual(
            holdout["fit_temporal_feature_support_reference_source"],
            "frozen_excluded_fit_regime_half_year_features",
        )
        self.assertFalse(
            holdout[
                "rebuild_fit_temporal_feature_support_on_holdout"
            ]
        )
        self.assertTrue(
            holdout["selection_derived_feature_support_cutoff_reused"]
        )

    def test_only_feature_support_protocol_change_is_open(self) -> None:
        payload = fit_temporal_feature_support_utility_protocol_payload()
        auth = payload["authorization"]
        self.assertTrue(FIT_TEMPORAL_FEATURE_SUPPORT_AUTHORIZED)
        self.assertTrue(auth["fit_temporal_feature_support_authorized"])
        self.assertFalse(
            auth["fit_temporal_utility_support_change_authorized"]
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
