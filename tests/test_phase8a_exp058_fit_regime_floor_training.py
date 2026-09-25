from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

from fmp.market_learning.model_successor_fit_temporal_residual_regime_floor_utility_training import (
    DEC231_MERGED_COMMIT,
    DEC231_PROTOCOL_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_TRAINING_CORE_DECISION,
    MODEL_FIT_AUTHORIZED,
    PREDECESSOR_TRAINING_CORE_BLOB_SHA,
    _candidate_directions_residual_regime_floor,
    _derive_residual_regime_floor_cutoff,
    _fit_temporal_residual_regime_floor_utility,
    build_fit_temporal_residual_regime_floor_training_core_gate,
    run_fit_temporal_residual_regime_floor_utility_model_cell_core,
    validate_fit_temporal_residual_regime_floor_utility_training_sources,
)


ROOT = Path(__file__).resolve().parents[1]


class Exp058FitTemporalResidualRegimeFloorTrainingTests(unittest.TestCase):
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
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
            "ef0ffc46b130d5cfe5b1a19f86bea6a2d41d0cbd",
        )
        self.assertEqual(
            report["dec231_protocol_blob_sha"],
            DEC231_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            report["predecessor_training_core_blob_sha"],
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        )
        self.assertTrue(report["residual_regime_floor_authorized"])
        self.assertFalse(
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_UTILITY_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(MODEL_FIT_AUTHORIZED)
        self.assertFalse(report["result_execution_authorized"])
        self.assertFalse(report["model_fit_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["shadow_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_regime_floor_is_minimum_of_three_four_bound_means(self) -> None:
        directions = np.asarray(
            ["LONG", "SHORT", "NO_TRADE"],
            dtype=object,
        )
        view_predictions = {}
        residual_references = {}
        residuals = {
            "a": (-3.0, -1.0, 0.0, 1.0),
            "b": (-4.0, -2.0, 0.0, 2.0),
            "c": (-5.0, -1.0, 0.0, 1.0),
        }
        for view_name, values in residuals.items():
            view_predictions[view_name] = {
                "long_net_pips_0p5": np.asarray(
                    [2.0, 99.0, 99.0],
                    dtype=np.float64,
                ),
                "short_net_pips_0p5": np.asarray(
                    [99.0, 1.0, 99.0],
                    dtype=np.float64,
                ),
            }
            residual_references[view_name] = {
                "long_net_pips_0p5": {
                    f"w{index}": value
                    for index, value in enumerate(values)
                },
                "short_net_pips_0p5": {
                    f"w{index}": value
                    for index, value in enumerate(values)
                },
            }

        result = _fit_temporal_residual_regime_floor_utility(
            directions=directions,
            view_predictions=view_predictions,
            residual_references=residual_references,
        )

        expected_long = min(
            np.mean([2.0 + value for value in residuals[name]])
            for name in ("a", "b", "c")
        )
        expected_short = min(
            np.mean([1.0 + value for value in residuals[name]])
            for name in ("a", "b", "c")
        )
        self.assertAlmostEqual(result[0], expected_long)
        self.assertAlmostEqual(result[1], expected_short)
        self.assertTrue(np.isneginf(result[2]))

    def test_regime_floor_requires_three_views_and_four_windows_each(self) -> None:
        directions = np.asarray(["LONG"], dtype=object)
        predictions = {
            "a": {
                "long_net_pips_0p5": np.asarray([1.0]),
                "short_net_pips_0p5": np.asarray([1.0]),
            },
            "b": {
                "long_net_pips_0p5": np.asarray([1.0]),
                "short_net_pips_0p5": np.asarray([1.0]),
            },
        }
        refs = {
            name: {
                target: {"w0": 0.0, "w1": 0.0, "w2": 0.0, "w3": 0.0}
                for target in (
                    "long_net_pips_0p5",
                    "short_net_pips_0p5",
                )
            }
            for name in predictions
        }
        with self.assertRaisesRegex(ValueError, "view count drift"):
            _fit_temporal_residual_regime_floor_utility(
                directions=directions,
                view_predictions=predictions,
                residual_references=refs,
            )

    def test_regime_floor_cutoff_is_primary_and_eight_part(self) -> None:
        row_count = 251
        directions = np.full(row_count, "LONG", dtype=object)
        floor = np.ones(row_count, dtype=np.float64)
        tail = np.full(row_count, 0.8, dtype=np.float64)
        breadth = np.full(row_count, 0.75, dtype=np.float64)
        residual = np.full(row_count, 1.0, dtype=np.float64)
        feature = np.full(row_count, 0.9, dtype=np.float64)
        utility = np.full(row_count, 0.8, dtype=np.float64)
        pooled = np.full(row_count, 0.7, dtype=np.float64)
        raw = np.full(row_count, 5.0, dtype=np.float64)

        floor[248] = 0.75
        tail[248] = -10.0
        floor[249] = 0.50
        tail[249] = 0.99
        breadth[249] = 0.99
        feature[249] = 0.99
        utility[249] = 0.99
        pooled[249] = 0.99
        raw[249] = 50.0

        floor[250] = 5.0 / 12.0
        tail[250] = 100.0
        breadth[250] = 1.0
        residual[250] = 100.0
        feature[250] = 1.0
        utility[250] = 1.0
        pooled[250] = 1.0
        raw[250] = 100.0

        row_ids = tuple(
            f"row-{index:03d}"
            for index in range(row_count)
        )
        record = _derive_residual_regime_floor_cutoff(
            directions=directions,
            residual_regime_floor=floor,
            residual_lower_tail=tail,
            residual_breadth=breadth,
            residual_bound_utility=residual,
            feature_support=feature,
            fit_temporal_support=utility,
            pooled_calibrated_utility=pooled,
            raw_utility=raw,
            row_ids=row_ids,
            budget=250,
        )
        self.assertEqual(record["status"], "AVAILABLE")
        self.assertEqual(
            record["selection_derived_residual_regime_floor_cutoff"],
            0.50,
        )
        self.assertEqual(
            record["selection_derived_residual_lower_tail_cutoff"],
            0.99,
        )
        self.assertEqual(
            record["selection_candidate_count_at_cutoff"],
            250,
        )

        candidates = _candidate_directions_residual_regime_floor(
            directions=directions,
            residual_regime_floor=floor,
            residual_lower_tail=tail,
            residual_breadth=breadth,
            residual_bound_utility=residual,
            feature_support=feature,
            fit_temporal_support=utility,
            pooled_calibrated_utility=pooled,
            raw_utility=raw,
            residual_regime_floor_cutoff=0.50,
            residual_lower_tail_cutoff=0.99,
            residual_breadth_cutoff=0.99,
            residual_bound_cutoff=1.0,
            feature_cutoff=0.99,
            utility_cutoff=0.99,
            pooled_cutoff=0.99,
            raw_cutoff=50.0,
        )
        self.assertEqual(
            int(np.count_nonzero(candidates != "NO_TRADE")),
            250,
        )
        self.assertEqual(candidates[248], "LONG")
        self.assertEqual(candidates[249], "LONG")
        self.assertEqual(candidates[250], "NO_TRADE")

    def test_completed_core_exposes_full_forward_and_stability_paths(self) -> None:
        self.assertTrue(
            callable(
                run_fit_temporal_residual_regime_floor_utility_model_cell_core
            )
        )
        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_regime_floor_utility_training.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "def _evaluate_forward_split_residual_regime_floor(",
            source,
        )
        self.assertIn(
            "def _evaluate_temporal_stability_residual_regime_floor(",
            source,
        )
        self.assertIn(
            "selection_derived_residual_regime_floor_cutoff",
            source,
        )
        self.assertIn(
            "_predecessor._score_fit_temporal_residual_lower_tail_consensus",
            source,
        )
        self.assertIn('"dec231_merged_commit"', source)
        self.assertIn('"dec231_protocol_blob_sha"', source)
        self.assertNotIn('"dec220_merged_commit"', source)
        self.assertNotIn('"dec220_protocol_blob_sha"', source)
        self.assertIn(
            "fit_temporal_residual_breadth",
            source,
        )

    def test_training_gate_keeps_execution_locked(self) -> None:
        gate = build_fit_temporal_residual_regime_floor_training_core_gate()
        self.assertEqual(gate["experiment_id"], "EXP-20260925-058")
        self.assertEqual(gate["training_core_decision"], "DEC-232")
        self.assertEqual(gate["protocol_decision"], "DEC-231")
        self.assertEqual(gate["residual_reference_count_per_cell"], 24)
        self.assertEqual(
            gate["residual_breadth_bound_count_per_row"],
            12,
        )
        self.assertEqual(
            gate["residual_lower_tail_bound_count_per_row"],
            12,
        )
        self.assertEqual(gate["residual_lower_tail_count"], 3)
        self.assertEqual(gate["residual_regime_floor_bound_count_per_row"], 12)
        self.assertEqual(gate["residual_regime_count"], 3)
        self.assertEqual(gate["residual_windows_per_regime"], 4)
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
        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_regime_floor_utility_training.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn(
            "load_authoritative_cell_artifacts",
            source,
        )
        self.assertNotIn(
            "validate_authoritative_readiness",
            source,
        )
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("broker_send", source)


if __name__ == "__main__":
    unittest.main()
