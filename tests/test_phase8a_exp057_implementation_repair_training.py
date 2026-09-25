from __future__ import annotations

from pathlib import Path
import re
import unittest

from fmp.market_learning.model_successor_fit_temporal_residual_lower_tail_utility_repair_training import (
    DEC220_MERGED_COMMIT,
    DEC220_PROTOCOL_BLOB_SHA,
    EXP055_PREDECESSOR_TRAINING_CORE_BLOB_SHA,
    FAILED_EXP056_TRAINING_CORE_BLOB_SHA,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_TRAINING_CORE_DECISION,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    MODEL_FIT_AUTHORIZED,
    build_fit_temporal_residual_lower_tail_training_core_gate,
    run_fit_temporal_residual_lower_tail_utility_model_cell_core,
    validate_fit_temporal_residual_lower_tail_utility_repair_training_sources,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "src/fmp/market_learning/"
    "model_successor_fit_temporal_residual_lower_tail_utility_repair_training.py"
)

REPAIRED_NAMES = (
    "FIT_TEMPORAL_FEATURE_SUPPORT_PERCENTILE_RULE",
    "FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL",
    "FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL",
    "FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL",
    "MIN_STABILITY_WINDOW_CANDIDATE_SHARE",
    "ROBUST_FIT_TEMPORAL_FEATURE_SUPPORT_SCORE_RULE",
    "ROBUST_FIT_TEMPORAL_SUPPORT_SCORE_RULE",
)


class Exp057ImplementationRepairTrainingTests(unittest.TestCase):
    def test_source_binding_and_authorization_are_exact(self) -> None:
        report = (
            validate_fit_temporal_residual_lower_tail_utility_repair_training_sources(
                repository_root=ROOT,
            )
        )
        self.assertEqual(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_REPAIR_TRAINING_CORE_DECISION,
            "DEC-221",
        )
        self.assertEqual(
            DEC220_MERGED_COMMIT,
            "865ab1569a0765078ed099008a5722f8a6d310b4",
        )
        self.assertEqual(
            DEC220_PROTOCOL_BLOB_SHA,
            "2f355526476a4d41967bb46e1bfad6aa525cbfa9",
        )
        self.assertEqual(
            FAILED_EXP056_TRAINING_CORE_BLOB_SHA,
            "c472ed48e7b79d22056d43deb0fe09166ccf34c9",
        )
        self.assertEqual(
            EXP055_PREDECESSOR_TRAINING_CORE_BLOB_SHA,
            "c9517b7516940c78621448088c3933aa1c57e281",
        )
        self.assertEqual(
            report["failed_exp056_training_core_blob_sha"],
            FAILED_EXP056_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            report["exp055_predecessor_training_core_blob_sha"],
            EXP055_PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        )
        self.assertTrue(
            report["implementation_dependency_repair_authorized"]
        )
        self.assertFalse(
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_UTILITY_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(MODEL_FIT_AUTHORIZED)
        self.assertFalse(report["model_fit_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["shadow_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_exact_seven_invalid_predecessor_accesses_are_repaired(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        for name in REPAIRED_NAMES:
            with self.subTest(name=name):
                predecessor = re.compile(
                    rf"_predecessor\s*\.\s*{name}"
                )
                base = re.compile(rf"_base\s*\.\s*{name}")
                self.assertIsNone(predecessor.search(source))
                self.assertIsNotNone(base.search(source))

    def test_legitimate_breadth_predecessor_accesses_remain(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        for name in (
            "FIT_TEMPORAL_RESIDUAL_BREADTH_BOUND_COUNT_PER_ROW",
            "FIT_TEMPORAL_RESIDUAL_BREADTH_RULE",
            "RESIDUAL_BREADTH_ELIGIBILITY_RULE",
            "RESIDUAL_BREADTH_POSITIVITY_RULE",
            "_score_fit_temporal_residual_breadth_consensus",
        ):
            with self.subTest(name=name):
                self.assertRegex(
                    source,
                    rf"_predecessor\s*\.\s*{name}",
                )

    def test_no_stale_exp056_or_dec209_identity_remains(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        for value in (
            "DEC209_MERGED_COMMIT",
            "DEC209_PROTOCOL_BLOB_SHA",
            "EXP-056",
            "fmp-exp056-fit-temporal-residual-lower-tail-utility-"
            "training-core-v1",
        ):
            with self.subTest(value=value):
                self.assertNotIn(value, source)

        self.assertIn("EXP-20260925-057", source)
        self.assertIn("DEC-220", source)
        self.assertIn("DEC-221", source)

    def test_completed_core_exposes_full_cell_runner(self) -> None:
        self.assertTrue(
            callable(
                run_fit_temporal_residual_lower_tail_utility_model_cell_core
            )
        )
        source = SOURCE.read_text(encoding="utf-8")
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
        self.assertIn(
            "fit_temporal_residual_lower_tail_mean",
            source,
        )

    def test_training_gate_marks_tail_retained_and_repair_only(self) -> None:
        gate = build_fit_temporal_residual_lower_tail_training_core_gate()
        self.assertEqual(gate["experiment_id"], "EXP-20260925-057")
        self.assertEqual(gate["training_core_decision"], "DEC-221")
        self.assertEqual(gate["protocol_decision"], "DEC-220")
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
        self.assertEqual(gate["residual_lower_tail_fraction"], 0.25)
        self.assertTrue(gate["residual_lower_tail_retained"])
        self.assertFalse(
            gate["residual_lower_tail_change_authorized"]
        )
        self.assertTrue(
            gate["implementation_dependency_repair_authorized"]
        )

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
