from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

from fmp.market_learning.model_successor_fit_temporal_residual_breadth_utility_training import (
    DEC198_MERGED_COMMIT,
    DEC198_PROTOCOL_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_TRAINING_CORE_DECISION,
    MODEL_FIT_AUTHORIZED,
    PREDECESSOR_TRAINING_CORE_BLOB_SHA,
    _candidate_directions_residual_breadth,
    _derive_residual_breadth_cutoff,
    _fit_temporal_residual_breadth,
    build_fit_temporal_residual_breadth_training_core_gate,
    run_fit_temporal_residual_breadth_utility_model_cell_core,
    validate_fit_temporal_residual_breadth_utility_training_sources,
)


ROOT = Path(__file__).resolve().parents[1]


class Exp055FitTemporalResidualBreadthTrainingTests(unittest.TestCase):
    def test_source_binding_and_authorization_are_exact(self) -> None:
        report = (
            validate_fit_temporal_residual_breadth_utility_training_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_TRAINING_CORE_DECISION,
            "DEC-199",
        )
        self.assertEqual(
            DEC198_MERGED_COMMIT,
            "670f5d615b837b9268f8fb807aa198e7d14d0f1a",
        )
        self.assertEqual(
            report["dec198_protocol_blob_sha"],
            DEC198_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            DEC198_PROTOCOL_BLOB_SHA,
            "0ef3f932cade1a62e1faf946e9a9b87cf9c98744",
        )
        self.assertEqual(
            report["predecessor_training_core_blob_sha"],
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
            "4f3f189c104d41352433397421f021896c03a5e9",
        )
        self.assertFalse(
            FIT_TEMPORAL_RESIDUAL_BREADTH_UTILITY_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(MODEL_FIT_AUTHORIZED)
        self.assertFalse(report["model_fit_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["shadow_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_residual_breadth_counts_positive_twelve_bounds(self) -> None:
        directions = np.asarray(
            ["LONG", "SHORT", "NO_TRADE"],
            dtype=object,
        )
        view_predictions = {}
        residual_references = {}
        for view_name in ("a", "b", "c"):
            view_predictions[view_name] = {
                "long_net_pips_0p5": np.asarray(
                    [2.0, 99.0, 99.0],
                    dtype=np.float64,
                ),
                "short_net_pips_0p5": np.asarray(
                    [99.0, 0.5, 99.0],
                    dtype=np.float64,
                ),
            }
            residual_references[view_name] = {
                "long_net_pips_0p5": {
                    "w0": -3.0,
                    "w1": -1.0,
                    "w2": 0.0,
                    "w3": 1.0,
                },
                "short_net_pips_0p5": {
                    "w0": -2.0,
                    "w1": -1.0,
                    "w2": 0.0,
                    "w3": 1.0,
                },
            }

        result = _fit_temporal_residual_breadth(
            directions=directions,
            view_predictions=view_predictions,
            residual_references=residual_references,
        )
        self.assertEqual(result[0], 0.75)
        self.assertEqual(result[1], 0.50)
        self.assertTrue(np.isneginf(result[2]))

    def test_breadth_cutoff_is_primary_and_lexicographic(self) -> None:
        row_count = 251
        directions = np.full(row_count, "LONG", dtype=object)
        breadth = np.ones(row_count, dtype=np.float64)
        residual = np.full(row_count, 1.0, dtype=np.float64)
        feature = np.full(row_count, 0.9, dtype=np.float64)
        utility = np.full(row_count, 0.8, dtype=np.float64)
        pooled = np.full(row_count, 0.7, dtype=np.float64)
        raw = np.full(row_count, 5.0, dtype=np.float64)

        breadth[248] = 0.75
        residual[248] = -10.0
        feature[248] = 0.10

        breadth[249] = 0.50
        residual[249] = 0.99
        feature[249] = 0.99
        utility[249] = 0.99
        pooled[249] = 0.99
        raw[249] = 50.0

        breadth[250] = 5.0 / 12.0
        residual[250] = 100.0
        feature[250] = 1.00
        utility[250] = 1.00
        pooled[250] = 1.00
        raw[250] = 100.0

        row_ids = tuple(
            f"row-{index:03d}"
            for index in range(row_count)
        )
        record = _derive_residual_breadth_cutoff(
            directions=directions,
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
            record["selection_derived_residual_breadth_cutoff"],
            0.50,
        )
        self.assertEqual(
            record["selection_derived_residual_bound_cutoff"],
            0.99,
        )
        self.assertEqual(
            record["selection_candidate_count_at_cutoff"],
            250,
        )

        candidates = _candidate_directions_residual_breadth(
            directions=directions,
            residual_breadth=breadth,
            residual_bound_utility=residual,
            feature_support=feature,
            fit_temporal_support=utility,
            pooled_calibrated_utility=pooled,
            raw_utility=raw,
            residual_breadth_cutoff=0.50,
            residual_bound_cutoff=0.99,
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

    def test_completed_core_exposes_full_cell_runner(self) -> None:
        self.assertTrue(
            callable(
                run_fit_temporal_residual_breadth_utility_model_cell_core
            )
        )
        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_breadth_utility_training.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "def _evaluate_forward_split_residual_breadth(",
            source,
        )
        self.assertIn(
            "def _evaluate_temporal_stability_residual_breadth(",
            source,
        )
        self.assertIn(
            "selection_derived_residual_breadth_cutoff",
            source,
        )
        self.assertNotIn(
            "def _build_fit_temporal_residual_breadth_references(",
            source,
        )

    def test_training_gate_keeps_execution_locked(self) -> None:
        gate = build_fit_temporal_residual_breadth_training_core_gate()
        self.assertEqual(
            gate["experiment_id"],
            "EXP-20260925-055",
        )
        self.assertEqual(
            gate["residual_reference_count_per_cell"],
            24,
        )
        self.assertEqual(
            gate["residual_breadth_bound_count_per_row"],
            12,
        )
        self.assertTrue(gate["residual_breadth_authorized"])
        for name in (
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
            self.assertFalse(gate[name])

    def test_source_has_no_artifact_loading_or_dispatch_path(self) -> None:
        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_breadth_utility_training.py"
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
