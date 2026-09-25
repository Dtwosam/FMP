from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

from fmp.market_learning.model_successor_fit_temporal_support_utility_training import (
    DEC163_MERGED_COMMIT,
    DEC163_PROTOCOL_BLOB_SHA,
    FIT_TEMPORAL_SUPPORT_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_DECISION,
    MODEL_FIT_AUTHORIZED,
    PREDECESSOR_TRAINING_CORE_BLOB_SHA,
    REQUIRED_SUPPORT_COMPARISON_COUNT,
    _candidate_directions_support,
    _derive_support_cutoff,
    _passes_support_cutoff,
    _support_reference_digest,
    validate_fit_temporal_support_utility_training_sources,
)


ROOT = Path(__file__).resolve().parents[1]


class Exp052FitTemporalSupportUtilityTrainingCoreTests(
    unittest.TestCase
):
    def test_source_binds_exact_protocol_and_predecessor_core(
        self,
    ) -> None:
        report = (
            validate_fit_temporal_support_utility_training_sources(
                repository_root=ROOT,
            )
        )

        self.assertEqual(
            report["dec163_merged_commit"],
            DEC163_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC163_MERGED_COMMIT,
            "9108cd170b2eccf73bddb6cbf8d6d7118dbd9cd1",
        )
        self.assertEqual(
            report["dec163_protocol_blob_sha"],
            DEC163_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            DEC163_PROTOCOL_BLOB_SHA,
            "01d5080560ec5d41653694b4df086ff2f10e770d",
        )
        self.assertEqual(
            report["predecessor_training_core_blob_sha"],
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
            "959fbfd52f41c08de3c1a26769e0e7fd2545b92a",
        )
        self.assertEqual(
            report[
                "fit_temporal_support_utility_training_core_decision"
            ],
            FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_DECISION,
        )
        self.assertEqual(
            FIT_TEMPORAL_SUPPORT_UTILITY_TRAINING_CORE_DECISION,
            "DEC-164",
        )
        self.assertFalse(
            report[
                "fit_temporal_support_utility_result_execution_authorized"
            ]
        )
        self.assertFalse(report["model_fit_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["shadow_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_required_support_comparison_count_is_twelve(
        self,
    ) -> None:
        self.assertEqual(
            REQUIRED_SUPPORT_COMPARISON_COUNT,
            12,
        )

    def test_support_reference_digest_is_deterministic(
        self,
    ) -> None:
        values = np.asarray(
            [-1.0, 0.0, 0.5, 2.0],
            dtype=np.float64,
        )
        first = _support_reference_digest(values)
        second = _support_reference_digest(
            values.copy()
        )

        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)
        int(first, 16)

        with self.assertRaisesRegex(
            ValueError,
            "support reference must be sorted",
        ):
            _support_reference_digest(
                np.asarray([1.0, 0.0])
            )

    def test_support_cutoff_uses_support_then_pooled_then_raw(
        self,
    ) -> None:
        directions = np.asarray(
            ["LONG"] * 300,
            dtype=object,
        )
        support = np.asarray(
            [0.9] * 260 + [0.8] * 40,
            dtype=np.float64,
        )
        pooled = np.linspace(
            1.0,
            0.01,
            300,
            dtype=np.float64,
        )
        raw = np.linspace(
            3.0,
            0.1,
            300,
            dtype=np.float64,
        )
        row_ids = tuple(
            f"row-{index:04d}"
            for index in range(300)
        )

        report = _derive_support_cutoff(
            directions=directions,
            raw_utility=raw,
            pooled_calibrated_utility=pooled,
            fit_temporal_support=support,
            row_ids=row_ids,
            budget=250,
        )

        self.assertEqual(report["status"], "AVAILABLE")
        self.assertEqual(
            report["selection_derived_support_cutoff"],
            0.9,
        )
        self.assertGreater(
            float(
                report[
                    "selection_derived_pooled_calibrated_cutoff"
                ]
            ),
            0.0,
        )
        self.assertGreater(
            float(
                report["selection_derived_raw_cutoff"]
            ),
            0.0,
        )
        self.assertEqual(
            report["selection_candidate_count_at_cutoff"],
            250,
        )

        candidates = _candidate_directions_support(
            directions=directions,
            raw_utility=raw,
            pooled_calibrated_utility=pooled,
            fit_temporal_support=support,
            support_cutoff=float(
                report[
                    "selection_derived_support_cutoff"
                ]
            ),
            pooled_cutoff=float(
                report[
                    "selection_derived_pooled_calibrated_cutoff"
                ]
            ),
            raw_cutoff=float(
                report["selection_derived_raw_cutoff"]
            ),
        )
        self.assertEqual(
            sum(
                value != "NO_TRADE"
                for value in candidates.tolist()
            ),
            250,
        )

    def test_exact_cutoff_triple_ties_may_exceed_budget(
        self,
    ) -> None:
        directions = np.asarray(
            ["LONG"] * 260,
            dtype=object,
        )
        support = np.asarray(
            [0.75] * 260,
            dtype=np.float64,
        )
        pooled = np.asarray(
            [0.8] * 260,
            dtype=np.float64,
        )
        raw = np.asarray(
            [1.2] * 260,
            dtype=np.float64,
        )
        row_ids = tuple(
            f"row-{index:04d}"
            for index in range(260)
        )

        report = _derive_support_cutoff(
            directions=directions,
            raw_utility=raw,
            pooled_calibrated_utility=pooled,
            fit_temporal_support=support,
            row_ids=row_ids,
            budget=250,
        )

        self.assertEqual(report["status"], "AVAILABLE")
        self.assertEqual(
            report["selection_candidate_count_at_cutoff"],
            260,
        )

    def test_budget_unavailable_preserves_raw_eligibility(
        self,
    ) -> None:
        directions = np.asarray(
            ["SHORT"] * 249,
            dtype=object,
        )
        support = np.linspace(
            0.1,
            1.0,
            249,
            dtype=np.float64,
        )
        pooled = np.linspace(
            0.2,
            0.9,
            249,
            dtype=np.float64,
        )
        raw = np.linspace(
            0.1,
            2.0,
            249,
            dtype=np.float64,
        )
        row_ids = tuple(
            f"row-{index:04d}"
            for index in range(249)
        )

        report = _derive_support_cutoff(
            directions=directions,
            raw_utility=raw,
            pooled_calibrated_utility=pooled,
            fit_temporal_support=support,
            row_ids=row_ids,
            budget=250,
        )

        self.assertEqual(
            report["status"],
            "UNAVAILABLE_INSUFFICIENT_UTILITY_ROWS",
        )
        self.assertEqual(
            report["eligible_utility_row_count"],
            249,
        )
        self.assertIsNone(
            report["selection_derived_support_cutoff"]
        )
        self.assertIsNone(
            report[
                "selection_derived_pooled_calibrated_cutoff"
            ]
        )
        self.assertIsNone(
            report["selection_derived_raw_cutoff"]
        )

    def test_candidate_rule_preserves_direction(
        self,
    ) -> None:
        directions = np.asarray(
            ["LONG", "SHORT", "NO_TRADE", "LONG"],
            dtype=object,
        )
        raw = np.asarray(
            [1.0, 1.1, float("-inf"), 0.6],
            dtype=np.float64,
        )
        pooled = np.asarray(
            [0.8, 0.9, float("-inf"), 0.8],
            dtype=np.float64,
        )
        support = np.asarray(
            [0.7, 0.8, float("-inf"), 0.7],
            dtype=np.float64,
        )

        candidates = _candidate_directions_support(
            directions=directions,
            raw_utility=raw,
            pooled_calibrated_utility=pooled,
            fit_temporal_support=support,
            support_cutoff=0.7,
            pooled_cutoff=0.8,
            raw_cutoff=0.8,
        )
        self.assertEqual(
            candidates.tolist(),
            ["LONG", "SHORT", "NO_TRADE", "NO_TRADE"],
        )

    def test_cutoff_lexicographic_predicate_is_exact(
        self,
    ) -> None:
        self.assertTrue(
            _passes_support_cutoff(
                support=0.8,
                pooled=0.1,
                raw=0.1,
                support_cutoff=0.7,
                pooled_cutoff=0.9,
                raw_cutoff=2.0,
            )
        )
        self.assertTrue(
            _passes_support_cutoff(
                support=0.7,
                pooled=0.9,
                raw=2.0,
                support_cutoff=0.7,
                pooled_cutoff=0.8,
                raw_cutoff=3.0,
            )
        )
        self.assertTrue(
            _passes_support_cutoff(
                support=0.7,
                pooled=0.8,
                raw=3.0,
                support_cutoff=0.7,
                pooled_cutoff=0.8,
                raw_cutoff=3.0,
            )
        )
        self.assertFalse(
            _passes_support_cutoff(
                support=0.7,
                pooled=0.8,
                raw=2.9,
                support_cutoff=0.7,
                pooled_cutoff=0.8,
                raw_cutoff=3.0,
            )
        )

    def test_source_remains_non_executable(
        self,
    ) -> None:
        self.assertFalse(
            FIT_TEMPORAL_SUPPORT_UTILITY_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(MODEL_FIT_AUTHORIZED)

        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_support_utility_training.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("broker_send", source)


if __name__ == "__main__":
    unittest.main()
