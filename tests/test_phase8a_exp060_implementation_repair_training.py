from __future__ import annotations

import ast
from pathlib import Path
import unittest

import numpy as np

from fmp.market_learning.model_successor_fit_temporal_residual_regime_balance_utility_repair_training import (
    DEC253_MERGED_COMMIT,
    DEC253_PROTOCOL_BLOB_SHA,
    FAILED_EXP059_TRAINING_CORE_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_RESULT_EXECUTION_AUTHORIZED,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_TRAINING_CORE_DECISION,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_TRAINING_CORE_VERSION,
    MODEL_FIT_AUTHORIZED,
    PREDECESSOR_TRAINING_CORE_BLOB_SHA,
    _candidate_directions_residual_regime_balance,
    _derive_residual_regime_balance_cutoff,
    _fit_temporal_residual_regime_balance_utility,
    build_fit_temporal_residual_regime_balance_repair_training_core_gate,
    run_fit_temporal_residual_regime_balance_utility_model_cell_core,
    validate_fit_temporal_residual_regime_balance_utility_repair_training_sources,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "src/fmp/market_learning/"
    "model_successor_fit_temporal_residual_regime_balance_utility_repair_training.py"
)
BREADTH_NAMES = {
    "FIT_TEMPORAL_RESIDUAL_BREADTH_BOUND_COUNT_PER_ROW",
    "FIT_TEMPORAL_RESIDUAL_BREADTH_RULE",
    "RESIDUAL_BREADTH_ELIGIBILITY_RULE",
    "RESIDUAL_BREADTH_POSITIVITY_RULE",
}


def _attribute_chain(node: ast.Attribute) -> tuple[str, ...] | None:
    parts: list[str] = [node.attr]
    value: ast.expr = node.value
    while isinstance(value, ast.Attribute):
        parts.append(value.attr)
        value = value.value
    if not isinstance(value, ast.Name):
        return None
    parts.append(value.id)
    return tuple(reversed(parts))


class Exp060ImplementationRepairTrainingTests(unittest.TestCase):
    def test_source_binding_and_authorization_are_exact(self) -> None:
        report = (
            validate_fit_temporal_residual_regime_balance_utility_repair_training_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_TRAINING_CORE_DECISION,
            "DEC-254",
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_TRAINING_CORE_VERSION,
            (
                "fmp-exp060-fit-temporal-residual-regime-balance-utility-"
                "implementation-repair-training-core-v1"
            ),
        )
        self.assertEqual(
            DEC253_MERGED_COMMIT,
            "7e5b399cb7960d385d956b33e5d96cea85bb2c28",
        )
        self.assertEqual(
            DEC253_PROTOCOL_BLOB_SHA,
            "82d336250e2cdd9894afa5554c6b422e0de6b1fe",
        )
        self.assertEqual(
            FAILED_EXP059_TRAINING_CORE_BLOB_SHA,
            "4f99c1d0cb18551b67cc89357ad4a3940c190cd2",
        )
        self.assertEqual(
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
            "77f2010574b3d8ecc958930d5bfadf7ddb4f2231",
        )
        self.assertEqual(
            report["failed_exp059_training_core_blob_sha"],
            FAILED_EXP059_TRAINING_CORE_BLOB_SHA,
        )
        self.assertTrue(
            report["implementation_dependency_repair_authorized"]
        )
        self.assertFalse(report["protocol_semantics_change_authorized"])
        self.assertFalse(
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_REPAIR_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(MODEL_FIT_AUTHORIZED)
        self.assertFalse(report["model_fit_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["shadow_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_exact_four_breadth_accesses_are_three_levels_deep(self) -> None:
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        chains: set[tuple[str, ...]] = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Attribute):
                continue
            chain = _attribute_chain(node)
            if (
                chain is not None
                and chain[0] == "_predecessor"
                and chain[-1] in BREADTH_NAMES
            ):
                chains.add(chain)

        expected = {
            (
                "_predecessor",
                "_predecessor",
                "_predecessor",
                name,
            )
            for name in BREADTH_NAMES
        }
        self.assertEqual(chains, expected)

    def test_regime_balance_math_is_unchanged(self) -> None:
        directions = np.asarray(
            ["LONG", "NO_TRADE"],
            dtype=object,
        )
        view_predictions = {
            "view_a": {
                "long_net_pips_0p5": np.asarray([10.0, 99.0]),
                "short_net_pips_0p5": np.asarray([99.0, 99.0]),
            },
            "view_b": {
                "long_net_pips_0p5": np.asarray([10.0, 99.0]),
                "short_net_pips_0p5": np.asarray([99.0, 99.0]),
            },
            "view_c": {
                "long_net_pips_0p5": np.asarray([10.0, 99.0]),
                "short_net_pips_0p5": np.asarray([99.0, 99.0]),
            },
        }
        residual_references = {
            "view_a": {
                "long_net_pips_0p5": {
                    "w0": -9.0,
                    "w1": -9.0,
                    "w2": -9.0,
                    "w3": -9.0,
                },
                "short_net_pips_0p5": {
                    "w0": 0.0,
                    "w1": 0.0,
                    "w2": 0.0,
                    "w3": 0.0,
                },
            },
            "view_b": {
                "long_net_pips_0p5": {
                    "w0": -7.0,
                    "w1": -7.0,
                    "w2": -7.0,
                    "w3": -7.0,
                },
                "short_net_pips_0p5": {
                    "w0": 0.0,
                    "w1": 0.0,
                    "w2": 0.0,
                    "w3": 0.0,
                },
            },
            "view_c": {
                "long_net_pips_0p5": {
                    "w0": -5.0,
                    "w1": -5.0,
                    "w2": -5.0,
                    "w3": -5.0,
                },
                "short_net_pips_0p5": {
                    "w0": 0.0,
                    "w1": 0.0,
                    "w2": 0.0,
                    "w3": 0.0,
                },
            },
        }
        balance, floor = _fit_temporal_residual_regime_balance_utility(
            directions=directions,
            view_predictions=view_predictions,
            residual_references=residual_references,
        )
        self.assertEqual(floor[0], 1.0)
        self.assertEqual(balance[0], -1.0)
        self.assertTrue(np.isneginf(floor[1]))
        self.assertTrue(np.isneginf(balance[1]))

    def test_nine_part_cutoff_remains_balance_first(self) -> None:
        row_count = 251
        directions = np.full(row_count, "LONG", dtype=object)
        balance = np.ones(row_count, dtype=np.float64)
        floor = np.full(row_count, 0.9, dtype=np.float64)
        lower_tail = np.full(row_count, 0.8, dtype=np.float64)
        breadth = np.full(row_count, 0.75, dtype=np.float64)
        bound = np.full(row_count, 0.7, dtype=np.float64)
        feature = np.full(row_count, 0.6, dtype=np.float64)
        support = np.full(row_count, 0.5, dtype=np.float64)
        pooled = np.full(row_count, 0.4, dtype=np.float64)
        raw = np.full(row_count, 5.0, dtype=np.float64)

        balance[249] = 0.50
        floor[249] = 0.99
        lower_tail[249] = 0.99
        breadth[249] = 0.99
        bound[249] = 0.99
        feature[249] = 0.99
        support[249] = 0.99
        pooled[249] = 0.99
        raw[249] = 50.0

        balance[250] = 0.49
        floor[250] = 100.0
        lower_tail[250] = 100.0
        breadth[250] = 1.0
        bound[250] = 100.0
        feature[250] = 1.0
        support[250] = 1.0
        pooled[250] = 1.0
        raw[250] = 100.0

        row_ids = tuple(
            f"row-{index:03d}"
            for index in range(row_count)
        )
        record = _derive_residual_regime_balance_cutoff(
            directions=directions,
            residual_regime_balance=balance,
            residual_regime_floor=floor,
            residual_lower_tail=lower_tail,
            residual_breadth=breadth,
            residual_bound_utility=bound,
            feature_support=feature,
            fit_temporal_support=support,
            pooled_calibrated_utility=pooled,
            raw_utility=raw,
            row_ids=row_ids,
            budget=250,
        )
        self.assertEqual(record["status"], "AVAILABLE")
        self.assertEqual(
            record["selection_derived_residual_regime_balance_cutoff"],
            0.50,
        )
        self.assertEqual(
            record["selection_candidate_count_at_cutoff"],
            250,
        )

        candidates = _candidate_directions_residual_regime_balance(
            directions=directions,
            residual_regime_balance=balance,
            residual_regime_floor=floor,
            residual_lower_tail=lower_tail,
            residual_breadth=breadth,
            residual_bound_utility=bound,
            feature_support=feature,
            fit_temporal_support=support,
            pooled_calibrated_utility=pooled,
            raw_utility=raw,
            residual_regime_balance_cutoff=0.50,
            residual_regime_floor_cutoff=0.99,
            residual_lower_tail_cutoff=0.99,
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
        self.assertEqual(candidates[249], "LONG")
        self.assertEqual(candidates[250], "NO_TRADE")

    def test_completed_core_exposes_full_cell_runner(self) -> None:
        self.assertTrue(
            callable(
                run_fit_temporal_residual_regime_balance_utility_model_cell_core
            )
        )
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn(
            "def _evaluate_forward_split_residual_regime_balance(",
            source,
        )
        self.assertIn(
            "def _evaluate_temporal_stability_residual_regime_balance(",
            source,
        )
        self.assertIn(
            "selection_derived_residual_regime_balance_cutoff",
            source,
        )
        self.assertIn(
            "NO_FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_",
            source,
        )

    def test_training_gate_keeps_execution_locked(self) -> None:
        gate = (
            build_fit_temporal_residual_regime_balance_repair_training_core_gate()
        )
        self.assertEqual(
            gate["experiment_id"],
            "EXP-20260926-060",
        )
        self.assertEqual(
            gate["training_core_decision"],
            "DEC-254",
        )
        self.assertEqual(gate["residual_regime_balance_regime_count"], 3)
        self.assertEqual(
            gate["residual_regime_balance_source_bound_count_per_row"],
            12,
        )
        self.assertEqual(
            gate["residual_regime_balance_penalty_multiplier"],
            1.0,
        )
        self.assertTrue(
            gate["implementation_dependency_repair_authorized"]
        )
        self.assertFalse(
            gate["protocol_semantics_change_authorized"]
        )
        self.assertTrue(gate["residual_regime_balance_retained"])
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
