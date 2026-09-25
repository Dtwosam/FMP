from __future__ import annotations

import unittest

from fmp.market_learning.model_successor_fit_temporal_support_utility_protocol import (
    FIT_TEMPORAL_SUPPORT_CALIBRATION_AUTHORIZED,
    FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL,
    FIT_TEMPORAL_SUPPORT_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_VERSION,
    FIT_TEMPORAL_SUPPORT_WINDOWS,
    HISTORICAL_RESULT_EXECUTION_AUTHORIZED,
    MODEL_FIT_AUTHORIZED,
    MODEL_PROTOCOL_RESULT_AUTHORIZED,
    POOLED_OUT_OF_FIT_CALIBRATION_CHANGE_AUTHORIZED,
    PRIOR_RESULT_INFORMED,
    RANKING_RULE,
    REALIZED_SELECTION_OUTCOME_RANKING_AUTHORIZED,
    SELECTION_WINDOW_CALIBRATION_AUTHORIZED,
    SUPPORT_REFERENCE_WINDOWS_PER_EXCLUDED_REGIME,
    TRADING_AUTHORIZED,
    UNTOUCHED_OOS,
    fit_temporal_support_utility_protocol_fingerprint,
    fit_temporal_support_utility_protocol_payload,
    validate_fit_temporal_support_utility_predecessor_identity,
)


class Exp052FitTemporalSupportUtilityProtocolTests(
    unittest.TestCase
):
    def test_protocol_identity_and_fingerprint_are_frozen(
        self,
    ) -> None:
        validate_fit_temporal_support_utility_predecessor_identity()

        self.assertEqual(
            FIT_TEMPORAL_SUPPORT_UTILITY_EXPERIMENT_ID,
            "EXP-20260925-052",
        )
        self.assertEqual(
            FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_DECISION,
            "DEC-163",
        )
        self.assertEqual(
            FIT_TEMPORAL_SUPPORT_UTILITY_PROTOCOL_VERSION,
            "fmp-exp052-fit-temporal-support-utility-protocol-v1",
        )

        first = fit_temporal_support_utility_protocol_fingerprint()
        second = fit_temporal_support_utility_protocol_fingerprint()
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)
        int(first, 16)

    def test_support_windows_are_exact_fit_half_years(
        self,
    ) -> None:
        self.assertEqual(len(FIT_TEMPORAL_SUPPORT_WINDOWS), 12)
        self.assertEqual(
            SUPPORT_REFERENCE_WINDOWS_PER_EXCLUDED_REGIME,
            4,
        )
        self.assertEqual(
            FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL,
            24,
        )

        names = [
            str(window["name"])
            for window in FIT_TEMPORAL_SUPPORT_WINDOWS
        ]
        self.assertEqual(
            names,
            [
                "fit_2015_h1",
                "fit_2015_h2",
                "fit_2016_h1",
                "fit_2016_h2",
                "fit_2017_h1",
                "fit_2017_h2",
                "fit_2018_h1",
                "fit_2018_h2",
                "fit_2019_h1",
                "fit_2019_h2",
                "fit_2020_h1",
                "fit_2020_h2",
            ],
        )

        grouped: dict[str, list[dict[str, object]]] = {}
        for raw in FIT_TEMPORAL_SUPPORT_WINDOWS:
            window = dict(raw)
            grouped.setdefault(
                str(window["parent_regime"]),
                [],
            ).append(window)

        self.assertEqual(
            set(grouped),
            {
                "fit_2015_2016",
                "fit_2017_2018",
                "fit_2019_2020",
            },
        )
        self.assertTrue(
            all(len(value) == 4 for value in grouped.values())
        )
        self.assertEqual(
            FIT_TEMPORAL_SUPPORT_WINDOWS[0]["start"],
            "2015-01-01",
        )
        self.assertEqual(
            FIT_TEMPORAL_SUPPORT_WINDOWS[-1]["end_exclusive"],
            "2021-01-01",
        )
        self.assertTrue(
            all(
                str(window["end_exclusive"])
                <= "2021-01-01"
                for window in FIT_TEMPORAL_SUPPORT_WINDOWS
            )
        )

    def test_payload_retains_exp051_pooled_calibration(
        self,
    ) -> None:
        payload = fit_temporal_support_utility_protocol_payload()

        pooled = payload["out_of_fit_utility_calibration"]
        assert isinstance(pooled, dict)
        self.assertEqual(
            pooled["reference_count_per_cell"],
            6,
        )
        self.assertFalse(
            pooled["selection_rows_enter_calibration"]
        )
        self.assertFalse(
            pooled["validation_rows_enter_calibration"]
        )
        self.assertFalse(
            pooled["holdout_rows_enter_calibration"]
        )

        support = payload[
            "fit_temporal_support_calibration"
        ]
        assert isinstance(support, dict)
        self.assertTrue(
            support["authorized_protocol_change"]
        )
        self.assertEqual(
            support["reference_count_per_cell"],
            24,
        )
        self.assertEqual(
            support["support_windows_per_excluded_regime"],
            4,
        )
        self.assertEqual(
            len(support["support_windows"]),
            12,
        )
        self.assertTrue(
            support["pooled_exp051_calibration_retained"]
        )
        self.assertFalse(support["uses_realized_outcomes"])
        self.assertFalse(
            support["selection_rows_enter_support_references"]
        )
        self.assertFalse(
            support["validation_rows_enter_support_references"]
        )
        self.assertFalse(
            support["holdout_rows_enter_support_references"]
        )
        self.assertEqual(
            support["aggregation"],
            "minimum",
        )

    def test_ranking_and_cutoff_are_support_first(
        self,
    ) -> None:
        payload = fit_temporal_support_utility_protocol_payload()

        utility = payload["utility_consensus"]
        assert isinstance(utility, dict)
        self.assertEqual(
            utility["ranking_score_rule"],
            RANKING_RULE,
        )
        self.assertTrue(
            utility["raw_direction_eligibility_unchanged"]
        )
        self.assertTrue(
            utility["pooled_calibrated_score_retained"]
        )

        selection = payload["selection"]
        assert isinstance(selection, dict)
        self.assertEqual(
            selection["candidate_budget_anchors"],
            [250, 500, 1000],
        )
        self.assertEqual(
            selection["ranking_order"],
            [
                "robust_fit_temporal_support_desc",
                "robust_pooled_calibrated_utility_desc",
                "robust_raw_utility_desc",
                "row_identity_asc",
            ],
        )
        self.assertEqual(
            selection["cutoff_components"],
            [
                "robust_fit_temporal_support",
                "robust_pooled_calibrated_utility",
                "robust_raw_utility",
            ],
        )

    def test_existing_stability_gate_is_unchanged(
        self,
    ) -> None:
        payload = fit_temporal_support_utility_protocol_payload()
        selection = payload["selection"]
        assert isinstance(selection, dict)
        stability = selection["temporal_stability"]
        assert isinstance(stability, dict)

        self.assertEqual(len(stability["windows"]), 4)
        self.assertEqual(
            stability[
                "minimum_directional_candidate_share_per_window"
            ],
            0.10,
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

    def test_forward_stages_reuse_frozen_support_references(
        self,
    ) -> None:
        payload = fit_temporal_support_utility_protocol_payload()

        validation = payload["validation"]
        holdout = payload["retrospective_holdout"]
        assert isinstance(validation, dict)
        assert isinstance(holdout, dict)

        self.assertEqual(
            validation["fit_temporal_support_reference_source"],
            "frozen_excluded_fit_regime_half_years",
        )
        self.assertFalse(
            validation[
                "rebuild_fit_temporal_support_reference_on_validation"
            ]
        )
        self.assertTrue(
            validation["selection_derived_support_cutoff_reused"]
        )

        self.assertEqual(
            holdout["fit_temporal_support_reference_source"],
            "frozen_excluded_fit_regime_half_years",
        )
        self.assertFalse(
            holdout[
                "rebuild_fit_temporal_support_reference_on_holdout"
            ]
        )
        self.assertTrue(
            holdout["selection_derived_support_cutoff_reused"]
        )

    def test_only_fit_temporal_support_protocol_change_is_open(
        self,
    ) -> None:
        payload = fit_temporal_support_utility_protocol_payload()
        auth = payload["authorization"]
        assert isinstance(auth, dict)

        self.assertTrue(
            FIT_TEMPORAL_SUPPORT_CALIBRATION_AUTHORIZED
        )
        self.assertTrue(
            auth["fit_temporal_support_calibration_authorized"]
        )
        self.assertFalse(
            POOLED_OUT_OF_FIT_CALIBRATION_CHANGE_AUTHORIZED
        )
        self.assertFalse(
            auth[
                "pooled_out_of_fit_calibration_change_authorized"
            ]
        )
        self.assertFalse(
            SELECTION_WINDOW_CALIBRATION_AUTHORIZED
        )
        self.assertFalse(
            REALIZED_SELECTION_OUTCOME_RANKING_AUTHORIZED
        )

        for field in (
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

    def test_protocol_remains_result_informed_not_untouched_oos(
        self,
    ) -> None:
        self.assertTrue(PRIOR_RESULT_INFORMED)
        self.assertFalse(UNTOUCHED_OOS)


if __name__ == "__main__":
    unittest.main()
