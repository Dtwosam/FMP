from __future__ import annotations

import unittest

from fmp.market_learning.model_successor_fit_temporal_residual_regime_balance_utility_protocol import (
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_PENALTY_MULTIPLIER,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_REGIME_COUNT,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_SOURCE_BOUND_COUNT_PER_ROW,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_PROTOCOL_VERSION,
    HISTORICAL_RESULT_EXECUTION_AUTHORIZED,
    MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED,
    fit_temporal_residual_regime_balance_utility_protocol_fingerprint,
    fit_temporal_residual_regime_balance_utility_protocol_payload,
)


class Exp059RegimeBalanceProtocolTests(unittest.TestCase):
    def test_identity_and_fingerprint_are_deterministic(self) -> None:
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_EXPERIMENT_ID,
            "EXP-20260926-059",
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_PROTOCOL_DECISION,
            "DEC-242",
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_PROTOCOL_VERSION,
            "fmp-exp059-fit-temporal-residual-regime-balance-utility-protocol-v1",
        )
        first = fit_temporal_residual_regime_balance_utility_protocol_fingerprint()
        second = fit_temporal_residual_regime_balance_utility_protocol_fingerprint()
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)

    def test_regime_balance_uses_only_existing_fit_regime_means(self) -> None:
        payload = fit_temporal_residual_regime_balance_utility_protocol_payload()
        balance = payload["fit_temporal_residual_regime_balance"]
        self.assertTrue(FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_AUTHORIZED)
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_REGIME_COUNT,
            3,
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_SOURCE_BOUND_COUNT_PER_ROW,
            12,
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_PENALTY_MULTIPLIER,
            1.0,
        )
        self.assertTrue(balance["uses_existing_exp058_regime_means"])
        self.assertFalse(balance["creates_new_reference_vectors"])
        self.assertEqual(balance["center_aggregation"], "arithmetic_mean")
        self.assertEqual(balance["dispersion_measure"], "max_minus_min")
        self.assertEqual(
            balance["score_formula"],
            "mean_minus_1p0_times_range",
        )
        self.assertFalse(balance["uses_realized_selection_outcomes"])
        self.assertFalse(balance["selection_window_identity_enters_ranking"])
        self.assertFalse(balance["stability_gate_changed"])

    def test_ranking_and_nine_part_cutoff_are_exact(self) -> None:
        payload = fit_temporal_residual_regime_balance_utility_protocol_payload()
        selection = payload["selection"]
        self.assertEqual(
            selection["ranking_order"],
            [
                "fit_temporal_residual_regime_balance_utility_desc",
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
                "fit_temporal_residual_regime_balance_utility",
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
        stability = selection["temporal_stability"]
        self.assertEqual(len(stability["windows"]), 4)
        self.assertEqual(
            stability["minimum_directional_candidate_share_per_window"],
            0.10,
        )

    def test_forward_reuses_same_score_without_refit(self) -> None:
        payload = fit_temporal_residual_regime_balance_utility_protocol_payload()
        validation = payload["validation"]
        holdout = payload["retrospective_holdout"]
        for block in (validation, holdout):
            self.assertEqual(
                block["fit_temporal_residual_regime_balance_source"],
                "frozen_three_fit_regime_means",
            )
            self.assertTrue(
                block[
                    "selection_derived_residual_regime_balance_cutoff_reused"
                ]
            )
        self.assertFalse(
            validation[
                "rebuild_fit_temporal_residual_regime_balance_on_validation"
            ]
        )
        self.assertFalse(
            holdout[
                "rebuild_fit_temporal_residual_regime_balance_on_holdout"
            ]
        )

    def test_only_protocol_source_change_is_open(self) -> None:
        payload = fit_temporal_residual_regime_balance_utility_protocol_payload()
        auth = payload["authorization"]
        self.assertTrue(
            auth["fit_temporal_residual_regime_balance_authorized"]
        )
        self.assertFalse(MODEL_PROTOCOL_RESULT_AUTHORIZED)
        self.assertFalse(MODEL_FIT_AUTHORIZED)
        self.assertFalse(HISTORICAL_RESULT_EXECUTION_AUTHORIZED)
        for field, value in auth.items():
            if field == "fit_temporal_residual_regime_balance_authorized":
                continue
            with self.subTest(field=field):
                self.assertIs(value, False)


if __name__ == "__main__":
    unittest.main()
