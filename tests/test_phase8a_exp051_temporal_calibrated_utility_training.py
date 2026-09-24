from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

from fmp.market_learning.model_successor_temporal_calibrated_utility_training import (
    DEC150_MERGED_COMMIT,
    DEC150_PROTOCOL_BLOB_SHA,
    MODEL_FIT_AUTHORIZED,
    PREDECESSOR_TRAINING_CORE_BLOB_SHA,
    TEMPORAL_CALIBRATED_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    TEMPORAL_CALIBRATED_UTILITY_TRAINING_CORE_DECISION,
    _candidate_directions_calibrated,
    _derive_calibrated_cutoff,
    _empirical_percentiles,
    _reference_digest,
    validate_temporal_calibrated_utility_training_sources,
)


ROOT = Path(__file__).resolve().parents[1]


class Exp051TemporalCalibratedUtilityTrainingCoreTests(
    unittest.TestCase
):
    def test_source_binds_exact_protocol_and_predecessor_core(
        self,
    ) -> None:
        report = (
            validate_temporal_calibrated_utility_training_sources(
                repository_root=ROOT,
            )
        )

        self.assertEqual(
            report["dec150_merged_commit"],
            DEC150_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC150_MERGED_COMMIT,
            "b80a1f688afe8f5056aa31c1a2ff5b4ebbc11833",
        )
        self.assertEqual(
            report["dec150_protocol_blob_sha"],
            DEC150_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            DEC150_PROTOCOL_BLOB_SHA,
            "c39309c4115cae1ea058e56f30cae4af6407e36e",
        )
        self.assertEqual(
            report["predecessor_training_core_blob_sha"],
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
            "ec97a9941af052d6e223e4bafab9a9989ec57ff0",
        )
        self.assertEqual(
            report[
                "temporal_calibrated_utility_training_core_decision"
            ],
            TEMPORAL_CALIBRATED_UTILITY_TRAINING_CORE_DECISION,
        )
        self.assertEqual(
            TEMPORAL_CALIBRATED_UTILITY_TRAINING_CORE_DECISION,
            "DEC-151",
        )
        self.assertFalse(
            report[
                "temporal_calibrated_utility_result_execution_authorized"
            ]
        )
        self.assertFalse(report["model_fit_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["shadow_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_empirical_percentiles_use_right_cdf(self) -> None:
        reference = np.asarray(
            [-2.0, 0.0, 1.0, 1.0, 3.0],
            dtype=np.float64,
        )
        values = np.asarray(
            [-3.0, 0.0, 1.0, 2.0, 4.0],
            dtype=np.float64,
        )

        result = _empirical_percentiles(
            reference,
            values,
        )

        np.testing.assert_allclose(
            result,
            np.asarray(
                [0.0, 0.4, 0.8, 0.8, 1.0],
                dtype=np.float64,
            ),
        )

    def test_empirical_percentiles_require_sorted_finite_reference(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "reference must be sorted",
        ):
            _empirical_percentiles(
                np.asarray([1.0, 0.0]),
                np.asarray([0.5]),
            )

        with self.assertRaisesRegex(
            ValueError,
            "inputs must be finite",
        ):
            _empirical_percentiles(
                np.asarray([0.0, 1.0]),
                np.asarray([float("nan")]),
            )

    def test_reference_digest_is_deterministic(self) -> None:
        values = np.asarray(
            [-1.0, 0.5, 2.0],
            dtype=np.float64,
        )
        first = _reference_digest(values)
        second = _reference_digest(values.copy())

        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)
        int(first, 16)

    def test_calibrated_cutoff_uses_percentile_then_raw_utility(
        self,
    ) -> None:
        directions = np.asarray(
            ["LONG"] * 300,
            dtype=object,
        )
        calibrated = np.asarray(
            [0.9] * 260 + [0.8] * 40,
            dtype=np.float64,
        )
        raw = np.linspace(
            3.0,
            0.01,
            300,
            dtype=np.float64,
        )
        row_ids = tuple(
            f"row-{index:04d}"
            for index in range(300)
        )

        report = _derive_calibrated_cutoff(
            directions=directions,
            raw_utility=raw,
            calibrated_utility=calibrated,
            row_ids=row_ids,
            budget=250,
        )

        self.assertEqual(report["status"], "AVAILABLE")
        self.assertEqual(
            report["selection_derived_calibrated_cutoff"],
            0.9,
        )
        raw_cutoff = float(
            report["selection_derived_raw_cutoff"]
        )
        self.assertGreater(raw_cutoff, 0.0)
        self.assertEqual(
            report["selection_candidate_count_at_cutoff"],
            250,
        )

        candidates = _candidate_directions_calibrated(
            directions=directions,
            raw_utility=raw,
            calibrated_utility=calibrated,
            calibrated_cutoff=0.9,
            raw_cutoff=raw_cutoff,
        )
        self.assertEqual(
            int(
                sum(
                    value != "NO_TRADE"
                    for value in candidates.tolist()
                )
            ),
            250,
        )

    def test_exact_score_pair_ties_may_exceed_budget(
        self,
    ) -> None:
        directions = np.asarray(
            ["LONG"] * 260,
            dtype=object,
        )
        calibrated = np.asarray(
            [0.75] * 260,
            dtype=np.float64,
        )
        raw = np.asarray(
            [1.0] * 260,
            dtype=np.float64,
        )
        row_ids = tuple(
            f"row-{index:04d}"
            for index in range(260)
        )

        report = _derive_calibrated_cutoff(
            directions=directions,
            raw_utility=raw,
            calibrated_utility=calibrated,
            row_ids=row_ids,
            budget=250,
        )

        self.assertEqual(report["status"], "AVAILABLE")
        self.assertEqual(
            report["selection_candidate_count_at_cutoff"],
            260,
        )

    def test_budget_unavailable_uses_unchanged_eligible_rows(
        self,
    ) -> None:
        directions = np.asarray(
            ["LONG"] * 249,
            dtype=object,
        )
        calibrated = np.linspace(
            0.1,
            1.0,
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

        report = _derive_calibrated_cutoff(
            directions=directions,
            raw_utility=raw,
            calibrated_utility=calibrated,
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
            report["selection_derived_calibrated_cutoff"]
        )
        self.assertIsNone(
            report["selection_derived_raw_cutoff"]
        )

    def test_candidate_rule_preserves_direction_and_raw_positive_gate(
        self,
    ) -> None:
        directions = np.asarray(
            ["LONG", "SHORT", "NO_TRADE", "LONG"],
            dtype=object,
        )
        raw = np.asarray(
            [1.2, 0.8, float("-inf"), 0.4],
            dtype=np.float64,
        )
        calibrated = np.asarray(
            [0.7, 0.8, float("-inf"), 0.7],
            dtype=np.float64,
        )

        candidates = _candidate_directions_calibrated(
            directions=directions,
            raw_utility=raw,
            calibrated_utility=calibrated,
            calibrated_cutoff=0.7,
            raw_cutoff=0.5,
        )
        self.assertEqual(
            candidates.tolist(),
            ["LONG", "SHORT", "NO_TRADE", "NO_TRADE"],
        )

    def test_source_is_non_executable_and_has_no_dispatch(
        self,
    ) -> None:
        self.assertFalse(
            TEMPORAL_CALIBRATED_UTILITY_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(MODEL_FIT_AUTHORIZED)

        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_temporal_calibrated_utility_training.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("broker_send", source)
        self.assertNotIn(
            "HistGradientBoostingClassifier(",
            source,
        )
        self.assertNotIn("LogisticRegression(", source)


if __name__ == "__main__":
    unittest.main()
