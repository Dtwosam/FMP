from __future__ import annotations

import unittest

from fmp.market_learning.model_successor_fit_temporal_residual_lower_tail_utility_repair_protocol import (
    fit_temporal_residual_lower_tail_utility_repair_protocol_payload,
)
from fmp.market_learning.model_successor_fit_temporal_residual_regime_floor_utility_protocol import (
    FIT_TEMPORAL_RESIDUAL_REGIME_COUNT,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_BOUND_COUNT_PER_ROW,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_PROTOCOL_VERSION,
    FIT_TEMPORAL_RESIDUAL_WINDOWS_PER_REGIME,
    HISTORICAL_RESULT_EXECUTION_AUTHORIZED,
    MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED,
    TRADING_AUTHORIZED,
    fit_temporal_residual_regime_floor_utility_protocol_fingerprint,
    fit_temporal_residual_regime_floor_utility_protocol_payload,
    validate_fit_temporal_residual_regime_floor_predecessor_identity,
)


class Exp058FitRegimeFloorProtocolTests(unittest.TestCase):
    def test_identity_and_fingerprint_are_frozen(self) -> None:
        validate_fit_temporal_residual_regime_floor_predecessor_identity()
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_EXPERIMENT_ID,
            "EXP-20260925-058",
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_PROTOCOL_DECISION,
            "DEC-231",
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_PROTOCOL_VERSION,
            "fmp-exp058-fit-temporal-residual-regime-floor-utility-protocol-v1",
        )
        first = fit_temporal_residual_regime_floor_utility_protocol_fingerprint()
        second = fit_temporal_residual_regime_floor_utility_protocol_fingerprint()
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)
        int(first, 16)

    def test_exact_fit_only_regime_floor_definition(self) -> None:
        payload = fit_temporal_residual_regime_floor_utility_protocol_payload()
        floor = payload["fit_temporal_residual_regime_floor"]

        self.assertTrue(FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_AUTHORIZED)
        self.assertEqual(FIT_TEMPORAL_RESIDUAL_REGIME_COUNT, 3)
        self.assertEqual(FIT_TEMPORAL_RESIDUAL_WINDOWS_PER_REGIME, 4)
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_BOUND_COUNT_PER_ROW,
            12,
        )
        self.assertTrue(floor["authorized_protocol_change"])
        self.assertEqual(floor["source_bound_count_per_row"], 12)
        self.assertEqual(floor["fit_regime_count"], 3)
        self.assertEqual(floor["residual_windows_per_regime"], 4)
        self.assertEqual(floor["within_regime_aggregation"], "arithmetic_mean")
        self.assertEqual(floor["across_regime_aggregation"], "minimum")
        self.assertTrue(floor["uses_existing_exp057_lower_bounds"])
        self.assertFalse(floor["creates_new_reference_vectors"])
        self.assertFalse(floor["uses_realized_selection_outcomes"])
        self.assertFalse(floor["selection_window_identity_enters_ranking"])
        self.assertFalse(floor["selection_window_quota_used"])
        self.assertFalse(floor["stability_gate_changed"])
        self.assertIn(
            "three frozen jackknife views and four residual half-year references per view",
            floor["regime_rule"],
        )
        self.assertIn(
            "minimum of those three regime means",
            floor["regime_rule"],
        )

    def test_predecessor_semantics_are_preserved_except_new_score(self) -> None:
        predecessor = (
            fit_temporal_residual_lower_tail_utility_repair_protocol_payload()
        )
        payload = fit_temporal_residual_regime_floor_utility_protocol_payload()

        for field in (
            "chronology",
            "model_family",
            "temporal_jackknife",
            "out_of_fit_utility_calibration",
            "fit_temporal_support_calibration",
            "fit_temporal_feature_support",
            "fit_temporal_residual_bound",
            "fit_temporal_residual_breadth",
            "fit_temporal_residual_lower_tail",
        ):
            with self.subTest(field=field):
                self.assertEqual(payload[field], predecessor[field])

        predecessor_selection = dict(predecessor["selection"])
        successor_selection = dict(payload["selection"])
        for field in (
            "selection_cutoff_rule",
            "cutoff_tie_policy",
            "forward_application_rule",
            "ranking_order",
            "cutoff_components",
        ):
            predecessor_selection.pop(field)
            successor_selection.pop(field)
        self.assertEqual(successor_selection, predecessor_selection)

        predecessor_validation = dict(predecessor["validation"])
        successor_validation = dict(payload["validation"])
        successor_validation.pop("fit_temporal_residual_regime_floor_source")
        successor_validation.pop(
            "rebuild_fit_temporal_residual_regime_floor_on_validation"
        )
        successor_validation.pop(
            "selection_derived_residual_regime_floor_cutoff_reused"
        )
        self.assertEqual(successor_validation, predecessor_validation)

        predecessor_holdout = dict(predecessor["retrospective_holdout"])
        successor_holdout = dict(payload["retrospective_holdout"])
        successor_holdout.pop("fit_temporal_residual_regime_floor_source")
        successor_holdout.pop(
            "rebuild_fit_temporal_residual_regime_floor_on_holdout"
        )
        successor_holdout.pop(
            "selection_derived_residual_regime_floor_cutoff_reused"
        )
        self.assertEqual(successor_holdout, predecessor_holdout)

    def test_ranking_and_cutoff_add_regime_floor_first(self) -> None:
        payload = fit_temporal_residual_regime_floor_utility_protocol_payload()
        selection = payload["selection"]
        self.assertEqual(
            selection["ranking_order"],
            [
                "fit_temporal_residual_regime_floor_utility_desc",
                "fit_temporal_residual_lower_tail_mean_desc",
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
                "fit_temporal_residual_regime_floor_utility",
                "fit_temporal_residual_lower_tail_mean",
                "fit_temporal_residual_breadth",
                "robust_fit_temporal_residual_bound_utility",
                "robust_fit_temporal_feature_support",
                "robust_fit_temporal_support",
                "robust_pooled_calibrated_utility",
                "robust_raw_utility",
            ],
        )
        self.assertEqual(selection["candidate_budget_anchors"], [250, 500, 1000])
        self.assertEqual(
            selection["temporal_stability"][
                "minimum_directional_candidate_share_per_window"
            ],
            0.10,
        )

    def test_all_other_changes_and_execution_remain_closed(self) -> None:
        payload = fit_temporal_residual_regime_floor_utility_protocol_payload()
        auth = payload["authorization"]
        self.assertTrue(
            auth["fit_temporal_residual_regime_floor_authorized"]
        )
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
            "pooled_out_of_fit_calibration_change_authorized",
            "fit_temporal_utility_support_change_authorized",
            "fit_temporal_feature_support_change_authorized",
            "fit_temporal_residual_bound_change_authorized",
            "fit_temporal_residual_breadth_change_authorized",
            "fit_temporal_residual_lower_tail_change_authorized",
            "fit_temporal_residual_reference_change_authorized",
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

    def test_predecessor_result_and_diagnostic_are_explicit(self) -> None:
        payload = fit_temporal_residual_regime_floor_utility_protocol_payload()
        self.assertEqual(
            payload["predecessor_experiment_id"],
            "EXP-20260925-057",
        )
        self.assertEqual(
            payload["predecessor_result_decision"],
            "DEC-229",
        )
        self.assertEqual(
            payload["predecessor_post_result_diagnostic_decision"],
            "DEC-230",
        )
        self.assertEqual(
            payload["predecessor_diagnostic_classification"],
            (
                "LOWER_TAIL_RANKING_CHANGED_CANDIDATE_FINANCIAL_MIX_"
                "AND_ADDED_AGGREGATE_PASS_BUT_DID_NOT_CREATE_TEMPORAL_STABILITY"
            ),
        )


if __name__ == "__main__":
    unittest.main()
