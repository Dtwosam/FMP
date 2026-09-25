from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

from fmp.market_learning.model_successor_fit_temporal_residual_bound_utility_training import (
    DEC185_MERGED_COMMIT,
    DEC185_PROTOCOL_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_DECISION,
    MODEL_FIT_AUTHORIZED,
    PREDECESSOR_TRAINING_CORE_BLOB_SHA,
    _candidate_directions_residual_bound,
    _derive_residual_bound_cutoff,
    _downside_residual,
    _robust_residual_bound_utility,
    build_fit_temporal_residual_bound_training_core_gate,
    validate_fit_temporal_residual_bound_utility_training_sources,
)


ROOT = Path(__file__).resolve().parents[1]


class Exp054FitTemporalResidualBoundTrainingTests(unittest.TestCase):
    def test_source_binding_and_authorization_are_exact(self) -> None:
        report = validate_fit_temporal_residual_bound_utility_training_sources(
            repository_root=ROOT,
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_DECISION,
            "DEC-186",
        )
        self.assertEqual(
            DEC185_MERGED_COMMIT,
            "3578491ab24b3fa6209ea674e02e1bce5dd99895",
        )
        self.assertEqual(
            report["dec185_protocol_blob_sha"],
            DEC185_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            DEC185_PROTOCOL_BLOB_SHA,
            "3ffac844f9ed5308512dc3313e850cc84fb6d144",
        )
        self.assertEqual(
            report["predecessor_training_core_blob_sha"],
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
            "4fd0e48302f97e188a8124e1543bde0ffdb43b6f",
        )
        self.assertFalse(
            FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(MODEL_FIT_AUTHORIZED)
        self.assertFalse(report["model_fit_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["shadow_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_downside_residual_uses_exact_lower_quartile_index(self) -> None:
        residuals = np.asarray(
            [-4.0, -2.0, -1.0, 0.0, 3.0],
            dtype=np.float64,
        )
        self.assertEqual(_downside_residual(residuals), -2.0)
        with self.assertRaisesRegex(ValueError, "must be sorted"):
            _downside_residual(residuals[::-1])

    def test_robust_residual_bound_is_minimum_of_twelve_bounds(self) -> None:
        directions = np.asarray(["LONG", "SHORT", "NO_TRADE"], dtype=object)
        view_predictions = {}
        residual_references = {}
        for view_index, view_name in enumerate(("a", "b", "c")):
            view_predictions[view_name] = {
                "long_net_pips_0p5": np.asarray(
                    [10.0 + view_index, 99.0, 99.0],
                    dtype=np.float64,
                ),
                "short_net_pips_0p5": np.asarray(
                    [99.0, 20.0 + view_index, 99.0],
                    dtype=np.float64,
                ),
            }
            residual_references[view_name] = {
                "long_net_pips_0p5": {
                    f"w{i}": float(-i - view_index)
                    for i in range(4)
                },
                "short_net_pips_0p5": {
                    f"w{i}": float(-2 * i - view_index)
                    for i in range(4)
                },
            }
        result = _robust_residual_bound_utility(
            directions=directions,
            view_predictions=view_predictions,
            residual_references=residual_references,
        )
        self.assertEqual(result[0], 7.0)
        self.assertEqual(result[1], 14.0)
        self.assertTrue(np.isneginf(result[2]))

    def test_residual_bound_cutoff_is_primary_and_lexicographic(self) -> None:
        row_count = 251
        directions = np.full(row_count, "LONG", dtype=object)
        residual = np.full(row_count, 1.0, dtype=np.float64)
        feature = np.full(row_count, 0.9, dtype=np.float64)
        utility = np.full(row_count, 0.8, dtype=np.float64)
        pooled = np.full(row_count, 0.7, dtype=np.float64)
        raw = np.full(row_count, 5.0, dtype=np.float64)

        residual[248] = 0.85
        feature[248] = 0.10
        residual[249] = 0.50
        feature[249] = 0.99
        utility[249] = 0.99
        pooled[249] = 0.99
        raw[249] = 50.0
        residual[250] = 0.40
        feature[250] = 1.00
        utility[250] = 1.00
        pooled[250] = 1.00
        raw[250] = 100.0

        row_ids = tuple(f"row-{index:03d}" for index in range(row_count))
        record = _derive_residual_bound_cutoff(
            directions=directions,
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
            record["selection_derived_residual_bound_cutoff"],
            0.50,
        )
        self.assertEqual(record["selection_candidate_count_at_cutoff"], 250)

        candidates = _candidate_directions_residual_bound(
            directions=directions,
            residual_bound_utility=residual,
            feature_support=feature,
            fit_temporal_support=utility,
            pooled_calibrated_utility=pooled,
            raw_utility=raw,
            residual_bound_cutoff=0.50,
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

    def test_training_gate_keeps_execution_locked(self) -> None:
        gate = build_fit_temporal_residual_bound_training_core_gate()
        self.assertEqual(gate["experiment_id"], "EXP-20260925-054")
        self.assertEqual(gate["residual_reference_count_per_cell"], 24)
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
            "model_successor_fit_temporal_residual_bound_utility_training.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("load_authoritative_cell_artifacts", source)
        self.assertNotIn("validate_authoritative_readiness", source)
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("broker_send", source)


if __name__ == "__main__":
    unittest.main()
