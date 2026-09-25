from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

from fmp.market_learning.model_successor_fit_temporal_residual_lower_tail_utility_training import (
    DEC209_MERGED_COMMIT,
    DEC209_PROTOCOL_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_TRAINING_CORE_DECISION,
    MODEL_FIT_AUTHORIZED,
    PREDECESSOR_TRAINING_CORE_BLOB_SHA,
    _candidate_directions_residual_lower_tail,
    _derive_residual_lower_tail_cutoff,
    _fit_temporal_residual_lower_tail_mean,
    build_fit_temporal_residual_lower_tail_training_core_gate,
    run_fit_temporal_residual_lower_tail_utility_model_cell_core,
    validate_fit_temporal_residual_lower_tail_utility_training_sources,
)


ROOT = Path(__file__).resolve().parents[1]


class Exp056ResidualLowerTailTrainingTests(unittest.TestCase):
    def test_source_binding_and_authorization_are_exact(self) -> None:
        report = (
            validate_fit_temporal_residual_lower_tail_utility_training_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_TRAINING_CORE_DECISION,
            "DEC-210",
        )
        self.assertEqual(
            DEC209_MERGED_COMMIT,
            "d2e1aabba6c0f283da6802fe315a5a29b22b503c",
        )
        self.assertEqual(
            report["dec209_protocol_blob_sha"],
            DEC209_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            DEC209_PROTOCOL_BLOB_SHA,
            "14d8fe5d0530f44acaa7084c6d78d1c19bd21d8d",
        )
        self.assertEqual(
            report["predecessor_training_core_blob_sha"],
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
            "c9517b7516940c78621448088c3933aa1c57e281",
        )
        self.assertFalse(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(MODEL_FIT_AUTHORIZED)
        self.assertFalse(report["model_fit_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["shadow_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_lower_tail_is_mean_of_exact_worst_three_bounds(self) -> None:
        directions = np.asarray(
            ["LONG", "SHORT", "NO_TRADE"],
            dtype=object,
        )
        view_predictions: dict[str, dict[str, np.ndarray]] = {}
        residual_references: dict[
            str,
            dict[str, dict[str, float]],
        ] = {}
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

        result = _fit_temporal_residual_lower_tail_mean(
            directions=directions,
            view_predictions=view_predictions,
            residual_references=residual_references,
        )

        self.assertEqual(result[0], -1.0)
        self.assertEqual(result[1], -1.5)
        self.assertTrue(np.isneginf(result[2]))

    def test_lower_tail_cutoff_is_primary_and_lexicographic(self) -> None:
        row_count = 251
        directions = np.full(row_count, "LONG", dtype=object)
        lower_tail = np.ones(row_count, dtype=np.float64)
        breadth = np.ones(row_count, dtype=np.float64)
        residual = np.full(row_count, 1.0, dtype=np.float64)
        feature = np.full(row_count, 0.9, dtype=np.float64)
        utility = np.full(row_count, 0.8, dtype=np.float64)
        pooled = np.full(row_count, 0.7, dtype=np.float64)
        raw = np.full(row_count, 5.0, dtype=np.float64)

        lower_tail[248] = 0.75
        breadth[248] = 0.0
        residual[248] = -10.0

        lower_tail[249] = 0.50
        breadth[249] = 0.99
        residual[249] = 0.99
        feature[249] = 0.99
        utility[249] = 0.99
        pooled[249] = 0.99
        raw[249] = 50.0

        lower_tail[250] = 0.49
        breadth[250] = 1.00
        residual[250] = 100.0
        feature[250] = 1.00
        utility[250] = 1.00
        pooled[250] = 1.00
        raw[250] = 100.0

        row_ids = tuple(
            f"row-{index:03d}"
            for index in range(row_count)
        )
        record = _derive_residual_lower_tail_cutoff(
            directions=directions,
            residual_lower_tail=lower_tail,
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
            record["selection_derived_residual_lower_tail_cutoff"],
            0.50,
        )
        self.assertEqual(
            record["selection_derived_residual_breadth_cutoff"],
            0.99,
        )
        self.assertEqual(
            record["selection_candidate_count_at_cutoff"],
            250,
        )

        candidates = _candidate_directions_residual_lower_tail(
            directions=directions,
            residual_lower_tail=lower_tail,
            residual_breadth=breadth,
            residual_bound_utility=residual,
            feature_support=feature,
            fit_temporal_support=utility,
            pooled_calibrated_utility=pooled,
            raw_utility=raw,
            residual_lower_tail_cutoff=0.50,
            residual_breadth_cutoff=0.99,
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
                run_fit_temporal_residual_lower_tail_utility_model_cell_core
            )
        )
        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_lower_tail_utility_training.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "def _evaluate_forward_split_residual_lower_tail(",
            source,
        )
        self.assertIn(
            "def _evaluate_temporal_stability_residual_lower_tail(",
            source,
        )
        self.assertIn(
            "selection_derived_residual_lower_tail_cutoff",
            source,
        )
        self.assertNotIn(
            "def _build_fit_temporal_residual_lower_tail_references(",
            source,
        )

    def test_training_gate_keeps_execution_locked(self) -> None:
        gate = build_fit_temporal_residual_lower_tail_training_core_gate()
        self.assertEqual(
            gate["experiment_id"],
            "EXP-20260925-056",
        )
        self.assertEqual(gate["residual_reference_count_per_cell"], 24)
        self.assertEqual(gate["residual_breadth_bound_count_per_row"], 12)
        self.assertEqual(
            gate["residual_lower_tail_bound_count_per_row"],
            12,
        )
        self.assertEqual(gate["residual_lower_tail_count"], 3)
        self.assertEqual(gate["residual_lower_tail_fraction"], 0.25)
        self.assertTrue(gate["residual_lower_tail_authorized"])
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
            "model_successor_fit_temporal_residual_lower_tail_utility_training.py"
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
