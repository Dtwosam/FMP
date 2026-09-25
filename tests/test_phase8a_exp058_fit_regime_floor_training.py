from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

from fmp.market_learning.model_successor_fit_temporal_residual_regime_floor_utility_training import (
    DEC231_MERGED_COMMIT,
    DEC231_PROTOCOL_BLOB_SHA,
    EXP057_PREDECESSOR_TRAINING_CORE_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_TRAINING_CORE_DECISION,
    MODEL_FIT_AUTHORIZED,
    _derive_residual_regime_floor_cutoff,
    _fit_temporal_residual_regime_floor_utility,
    build_fit_temporal_residual_regime_floor_training_core_gate,
    run_fit_temporal_residual_regime_floor_utility_model_cell_core,
    validate_fit_temporal_residual_regime_floor_utility_training_sources,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "src/fmp/market_learning/"
    "model_successor_fit_temporal_residual_regime_floor_utility_training.py"
)
LONG = "long_net_pips_0p5"
SHORT = "short_net_pips_0p5"


class Exp058FitRegimeFloorTrainingTests(unittest.TestCase):
    def test_source_binding_and_authorization_are_exact(self) -> None:
        report = (
            validate_fit_temporal_residual_regime_floor_utility_training_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_TRAINING_CORE_DECISION,
            "DEC-232",
        )
        self.assertEqual(
            DEC231_MERGED_COMMIT,
            "a6926703d787a7fe0e2ba34261d14c4c4d362df2",
        )
        self.assertEqual(
            DEC231_PROTOCOL_BLOB_SHA,
            "8e10cc3760a4a7dd019ea1ecc7c60189fe1770e2",
        )
        self.assertEqual(
            EXP057_PREDECESSOR_TRAINING_CORE_BLOB_SHA,
            "ef0ffc46b130d5cfe5b1a19f86bea6a2d41d0cbd",
        )
        self.assertEqual(
            report["exp057_predecessor_training_core_blob_sha"],
            EXP057_PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        )
        self.assertFalse(
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(MODEL_FIT_AUTHORIZED)
        self.assertFalse(report["model_fit_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["shadow_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_regime_floor_is_minimum_of_three_four_bound_means(self) -> None:
        directions = np.asarray(["LONG", "SHORT", "NO_TRADE"], dtype=object)
        view_predictions = {
            "view_a": {
                LONG: np.asarray([10.0, 100.0, 0.0]),
                SHORT: np.asarray([50.0, 20.0, 0.0]),
            },
            "view_b": {
                LONG: np.asarray([12.0, 100.0, 0.0]),
                SHORT: np.asarray([50.0, 22.0, 0.0]),
            },
            "view_c": {
                LONG: np.asarray([11.0, 100.0, 0.0]),
                SHORT: np.asarray([50.0, 18.0, 0.0]),
            },
        }
        residual_references = {
            "view_a": {
                LONG: {
                    "a1": -4.0,
                    "a2": -2.0,
                    "a3": 0.0,
                    "a4": 2.0,
                },
                SHORT: {
                    "a1": -3.0,
                    "a2": -1.0,
                    "a3": 1.0,
                    "a4": 3.0,
                },
            },
            "view_b": {
                LONG: {
                    "b1": -8.0,
                    "b2": -8.0,
                    "b3": -8.0,
                    "b4": -8.0,
                },
                SHORT: {
                    "b1": -4.0,
                    "b2": -2.0,
                    "b3": 0.0,
                    "b4": 2.0,
                },
            },
            "view_c": {
                LONG: {
                    "c1": -1.0,
                    "c2": -1.0,
                    "c3": -1.0,
                    "c4": -1.0,
                },
                SHORT: {
                    "c1": -10.0,
                    "c2": -6.0,
                    "c3": -2.0,
                    "c4": 2.0,
                },
            },
        }

        values = _fit_temporal_residual_regime_floor_utility(
            directions=directions,
            view_predictions=view_predictions,
            residual_references=residual_references,
        )
        # LONG regime means: 9, 4, 10 -> floor 4.
        self.assertEqual(values[0], 4.0)
        # SHORT regime means: 20, 21, 14 -> floor 14.
        self.assertEqual(values[1], 14.0)
        self.assertTrue(np.isneginf(values[2]))

    def test_regime_floor_requires_three_views_and_four_windows_each(self) -> None:
        directions = np.asarray(["LONG"], dtype=object)
        predictions = {
            "view_a": {LONG: np.asarray([1.0]), SHORT: np.asarray([1.0])},
            "view_b": {LONG: np.asarray([1.0]), SHORT: np.asarray([1.0])},
        }
        references = {
            view: {
                LONG: {f"{view}-{i}": 0.0 for i in range(4)},
                SHORT: {f"{view}-{i}": 0.0 for i in range(4)},
            }
            for view in predictions
        }
        with self.assertRaisesRegex(ValueError, "view count drift"):
            _fit_temporal_residual_regime_floor_utility(
                directions=directions,
                view_predictions=predictions,
                residual_references=references,
            )

    def test_eight_part_cutoff_starts_with_regime_floor(self) -> None:
        count = 250
        directions = np.asarray(["LONG"] * count, dtype=object)
        regime_floor = np.arange(count, dtype=np.float64)
        lower_tail = regime_floor + 1000.0
        breadth = np.full(count, 1.0, dtype=np.float64)
        residual_bound = regime_floor + 2000.0
        feature = np.full(count, 0.8, dtype=np.float64)
        support = np.full(count, 0.7, dtype=np.float64)
        pooled = np.full(count, 0.6, dtype=np.float64)
        raw = np.full(count, 1.0, dtype=np.float64)
        row_ids = tuple(f"row-{i:03d}" for i in range(count))

        cutoff = _derive_residual_regime_floor_cutoff(
            directions=directions,
            residual_regime_floor=regime_floor,
            residual_lower_tail=lower_tail,
            residual_breadth=breadth,
            residual_bound_utility=residual_bound,
            feature_support=feature,
            fit_temporal_support=support,
            pooled_calibrated_utility=pooled,
            raw_utility=raw,
            row_ids=row_ids,
            budget=250,
        )
        self.assertEqual(cutoff["status"], "AVAILABLE")
        self.assertEqual(
            cutoff["selection_derived_residual_regime_floor_cutoff"],
            0.0,
        )
        self.assertEqual(cutoff["selection_candidate_count_at_cutoff"], 250)
        for field in (
            "selection_derived_residual_regime_floor_cutoff",
            "selection_derived_residual_lower_tail_cutoff",
            "selection_derived_residual_breadth_cutoff",
            "selection_derived_residual_bound_cutoff",
            "selection_derived_feature_support_cutoff",
            "selection_derived_support_cutoff",
            "selection_derived_pooled_calibrated_cutoff",
            "selection_derived_raw_cutoff",
        ):
            with self.subTest(field=field):
                self.assertIn(field, cutoff)

    def test_completed_core_exposes_full_forward_pipeline(self) -> None:
        self.assertTrue(
            callable(
                run_fit_temporal_residual_regime_floor_utility_model_cell_core
            )
        )
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn(
            "def _evaluate_temporal_stability_residual_regime_floor(",
            source,
        )
        self.assertIn(
            "def _evaluate_forward_split_residual_regime_floor(",
            source,
        )
        self.assertIn(
            "fit_temporal_residual_regime_floor_utility_consensus",
            source,
        )
        self.assertIn(
            "selection_derived_residual_regime_floor_cutoff",
            source,
        )
        self.assertNotIn(
            "residual_regime_floor_cutoff=residual_regime_floor_cutoff,\n"
            "            residual_regime_floor_cutoff=",
            source,
        )

    def test_training_gate_is_non_executable(self) -> None:
        gate = build_fit_temporal_residual_regime_floor_training_core_gate()
        self.assertEqual(gate["experiment_id"], "EXP-20260925-058")
        self.assertEqual(gate["training_core_decision"], "DEC-232")
        self.assertEqual(gate["protocol_decision"], "DEC-231")
        self.assertEqual(gate["residual_reference_count_per_cell"], 24)
        self.assertEqual(gate["residual_breadth_bound_count_per_row"], 12)
        self.assertEqual(gate["residual_lower_tail_bound_count_per_row"], 12)
        self.assertEqual(gate["residual_lower_tail_count"], 3)
        self.assertEqual(
            gate["residual_regime_floor_bound_count_per_row"],
            12,
        )
        self.assertEqual(gate["residual_regime_count"], 3)
        self.assertEqual(gate["residual_windows_per_regime"], 4)
        self.assertTrue(gate["residual_regime_floor_added"])
        self.assertTrue(gate["residual_regime_floor_authorized"])

        for field in (
            "result_execution_authorized",
            "model_fit_authorized",
            "promotion_authorized",
            "shadow_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            with self.subTest(field=field):
                self.assertFalse(gate[field])

    def test_source_has_no_artifact_loading_or_dispatch_path(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("load_authoritative_cell_artifacts", source)
        self.assertNotIn("validate_authoritative_readiness", source)
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("broker_send", source)


if __name__ == "__main__":
    unittest.main()
