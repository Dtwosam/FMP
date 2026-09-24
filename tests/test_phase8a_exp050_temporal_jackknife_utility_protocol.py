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
from fmp.market_learning.model_successor_temporal_jackknife_utility_protocol import (
    AUTHORIZED_MODEL_FAMILIES,
    EXCLUDED_MODEL_FAMILIES,
    FINANCIAL_TARGET_COLUMNS,
    FINANCIAL_TARGET_SLIPPAGE_PIPS,
    FIT_JACKKNIFE_VIEWS,
    HIST_GRADIENT_BOOSTING_REGRESSION_CONFIG,
    PREDECESSOR_REGIME_NAMES,
    REQUIRED_JACKKNIFE_VIEW_COUNT,
    REQUIRED_REGRESSORS_PER_VIEW,
    TEMPORAL_JACKKNIFE_DIRECTION_RULE,
    TEMPORAL_JACKKNIFE_SCORE_RULE,
    TEMPORAL_JACKKNIFE_UTILITY_EXPERIMENT_ID,
    TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_DECISION,
    TOTAL_REGRESSORS_PER_CELL,
    temporal_jackknife_utility_protocol_fingerprint,
    temporal_jackknife_utility_protocol_payload,
    validate_temporal_jackknife_utility_predecessor_identity,
)


class Exp050TemporalJackknifeUtilityProtocolTests(unittest.TestCase):
    def test_predecessor_identity_is_exact(self) -> None:
        validate_temporal_jackknife_utility_predecessor_identity()

    def test_protocol_is_post_result_informed_and_closed(self) -> None:
        payload = temporal_jackknife_utility_protocol_payload()

        self.assertEqual(
            payload["experiment_id"],
            TEMPORAL_JACKKNIFE_UTILITY_EXPERIMENT_ID,
        )
        self.assertEqual(
            TEMPORAL_JACKKNIFE_UTILITY_EXPERIMENT_ID,
            "EXP-20260924-050",
        )
        self.assertEqual(
            payload["protocol_decision"],
            TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_DECISION,
        )
        self.assertEqual(
            TEMPORAL_JACKKNIFE_UTILITY_PROTOCOL_DECISION,
            "DEC-141",
        )

        predecessor = payload["predecessor"]
        assert isinstance(predecessor, dict)
        self.assertEqual(
            predecessor["experiment_id"],
            "EXP-20260924-049",
        )
        self.assertEqual(
            predecessor["result_decision"],
            "DEC-139",
        )
        self.assertEqual(
            predecessor["diagnostic_decision"],
            "DEC-140",
        )
        self.assertEqual(
            predecessor["diagnostic_classification"],
            "UTILITY_COVERAGE_AND_DUAL_TEMPORAL_STABILITY_LIMITED",
        )
        self.assertTrue(predecessor["prior_result_informed"])
        self.assertFalse(predecessor["untouched_oos"])
        self.assertEqual(
            predecessor["unavailable_budget_variant_count"],
            31,
        )
        self.assertEqual(
            predecessor["aggregate_selection_pass_variant_count"],
            8,
        )
        self.assertEqual(
            predecessor[
                "both_share_and_financial_reject_variant_count"
            ],
            8,
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

    def test_jackknife_views_cover_exact_leave_one_regime_out_sets(
        self,
    ) -> None:
        payload = temporal_jackknife_utility_protocol_payload()
        chronology = payload["chronology"]
        jackknife = payload["temporal_jackknife"]
        assert isinstance(chronology, dict)
        assert isinstance(jackknife, dict)

        self.assertEqual(
            REQUIRED_JACKKNIFE_VIEW_COUNT,
            3,
        )
        self.assertEqual(
            REQUIRED_REGRESSORS_PER_VIEW,
            2,
        )
        self.assertEqual(
            TOTAL_REGRESSORS_PER_CELL,
            6,
        )
        self.assertEqual(
            tuple(PREDECESSOR_REGIME_NAMES),
            (
                "fit_2015_2016",
                "fit_2017_2018",
                "fit_2019_2020",
            ),
        )
        self.assertEqual(len(FIT_JACKKNIFE_VIEWS), 3)

        views = chronology["jackknife_fit_views"]
        assert isinstance(views, list)
        self.assertEqual(len(views), 3)
        self.assertEqual(
            {
                row["excluded_regime"]
                for row in views
            },
            set(PREDECESSOR_REGIME_NAMES),
        )
        for row in views:
            with self.subTest(view=row["name"]):
                self.assertEqual(
                    row["included_regime_count"],
                    2,
                )
                self.assertEqual(
                    row["excluded_regime_count"],
                    1,
                )
                self.assertEqual(
                    row["fit_year_count"],
                    4,
                )
                self.assertNotIn(
                    row["excluded_regime"],
                    row["included_regimes"],
                )
                self.assertEqual(
                    set(row["included_regimes"]),
                    set(PREDECESSOR_REGIME_NAMES)
                    - {row["excluded_regime"]},
                )

        self.assertTrue(jackknife["all_views_required"])
        self.assertFalse(
            jackknife["view_weight_search_authorized"]
        )
        self.assertFalse(
            jackknife["view_fallback_authorized"]
        )

    def test_targets_and_model_structure_are_unchanged(self) -> None:
        payload = temporal_jackknife_utility_protocol_payload()
        targets = payload["financial_targets"]
        models = payload["model_family"]
        assert isinstance(targets, dict)
        assert isinstance(models, dict)

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
        self.assertFalse(
            targets["target_change_authorized"]
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
        self.assertEqual(
            models["total_regressors_per_cell"],
            6,
        )
        config = dict(
            HIST_GRADIENT_BOOSTING_REGRESSION_CONFIG
        )
        self.assertEqual(config["loss"], "squared_error")
        self.assertEqual(
            models["regressor_config"],
            config,
        )

    def test_positive_unanimous_utility_rule_is_not_relaxed(
        self,
    ) -> None:
        payload = temporal_jackknife_utility_protocol_payload()
        consensus = payload["utility_consensus"]
        assert isinstance(consensus, dict)

        self.assertEqual(
            consensus["direction_rule"],
            TEMPORAL_JACKKNIFE_DIRECTION_RULE,
        )
        self.assertIn(
            "greater than zero",
            TEMPORAL_JACKKNIFE_DIRECTION_RULE,
        )
        self.assertIn(
            "all three jackknife views",
            TEMPORAL_JACKKNIFE_DIRECTION_RULE,
        )
        self.assertEqual(
            consensus["score_rule"],
            TEMPORAL_JACKKNIFE_SCORE_RULE,
        )
        self.assertIn(
            "minimum predicted net pips",
            TEMPORAL_JACKKNIFE_SCORE_RULE,
        )
        self.assertTrue(
            consensus["positive_predicted_utility_required"]
        )
        self.assertFalse(
            consensus[
                "positive_utility_requirement_change_authorized"
            ]
        )
        self.assertEqual(
            consensus["disagreement_policy"],
            "NO_TRADE",
        )

    def test_density_and_stability_gates_are_not_weakened(self) -> None:
        payload = temporal_jackknife_utility_protocol_payload()
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
        self.assertEqual(
            MIN_DIRECTIONAL_CANDIDATES,
            250,
        )
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
        self.assertEqual(
            len(stability["windows"]),
            4,
        )
        self.assertEqual(
            tuple(stability["requirements_per_window"]),
            tuple(STABILITY_WINDOW_REQUIREMENTS),
        )
        self.assertTrue(
            stability["all_windows_must_pass"]
        )
        self.assertFalse(
            stability["stability_screen_change_authorized"]
        )
        self.assertFalse(
            stability[
                "per_window_financial_gate_change_authorized"
            ]
        )

    def test_forward_cutoff_is_selection_derived_and_frozen(
        self,
    ) -> None:
        payload = temporal_jackknife_utility_protocol_payload()
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
        self.assertFalse(
            validation["refit_on_validation"]
        )
        self.assertEqual(
            holdout["cutoff_source"],
            "selection",
        )
        self.assertFalse(
            holdout["recompute_cutoff_on_holdout"]
        )
        self.assertFalse(
            holdout["refit_on_holdout"]
        )

    def test_protocol_fingerprint_is_deterministic(self) -> None:
        first = temporal_jackknife_utility_protocol_fingerprint()
        second = temporal_jackknife_utility_protocol_fingerprint()

        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)
        int(first, 16)


if __name__ == "__main__":
    unittest.main()
