from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

from fmp.market_learning.model_successor_regime_consensus_training import (
    BASE_TRAINING_CORE_BLOB_SHA,
    DEC123_MERGED_COMMIT,
    DEC123_PROTOCOL_BLOB_SHA,
    DENSITY_HELPER_CORE_BLOB_SHA,
    MODEL_FIT_AUTHORIZED,
    REGIME_CONSENSUS_RESULT_EXECUTION_AUTHORIZED,
    REGIME_CONSENSUS_TRAINING_CORE_DECISION,
    _candidate_directions,
    _consensus_direction_confidence,
    _derive_consensus_cutoff,
    _fit_regime_splits,
    validate_regime_consensus_training_sources,
)


ROOT = Path(__file__).resolve().parents[1]


class Exp048RegimeConsensusTrainingCoreTests(
    unittest.TestCase
):
    def test_source_binds_exact_merged_protocol_and_helpers(
        self,
    ) -> None:
        report = validate_regime_consensus_training_sources(
            repository_root=ROOT,
        )

        self.assertEqual(
            report["dec123_merged_commit"],
            DEC123_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC123_MERGED_COMMIT,
            "39674f482e57922ac61fb0a6dff15a5ef621efd3",
        )
        self.assertEqual(
            report["dec123_protocol_blob_sha"],
            DEC123_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            report["base_training_core_blob_sha"],
            BASE_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            report["density_helper_core_blob_sha"],
            DENSITY_HELPER_CORE_BLOB_SHA,
        )
        self.assertEqual(
            report[
                "regime_consensus_training_core_decision"
            ],
            REGIME_CONSENSUS_TRAINING_CORE_DECISION,
        )
        self.assertEqual(
            REGIME_CONSENSUS_TRAINING_CORE_DECISION,
            "DEC-124",
        )
        self.assertFalse(
            report[
                "regime_consensus_result_execution_authorized"
            ]
        )
        self.assertFalse(report["model_fit_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["shadow_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_fit_regime_splits_are_exact_and_contiguous(
        self,
    ) -> None:
        splits = _fit_regime_splits()
        self.assertEqual(
            [
                (
                    split.name,
                    split.start.isoformat(),
                    split.end_exclusive.isoformat(),
                )
                for split in splits
            ],
            [
                (
                    "fit_2015_2016",
                    "2015-01-01",
                    "2017-01-01",
                ),
                (
                    "fit_2017_2018",
                    "2017-01-01",
                    "2019-01-01",
                ),
                (
                    "fit_2019_2020",
                    "2019-01-01",
                    "2021-01-01",
                ),
            ],
        )

    def test_consensus_requires_unanimous_direction(
        self,
    ) -> None:
        first = np.asarray(
            [
                [0.80, 0.10, 0.10],
                [0.10, 0.80, 0.10],
                [0.80, 0.10, 0.10],
                [0.50, 0.50, 0.00],
            ],
            dtype=np.float64,
        )
        second = np.asarray(
            [
                [0.70, 0.20, 0.10],
                [0.10, 0.75, 0.15],
                [0.10, 0.80, 0.10],
                [0.70, 0.20, 0.10],
            ],
            dtype=np.float64,
        )
        third = np.asarray(
            [
                [0.65, 0.20, 0.15],
                [0.20, 0.70, 0.10],
                [0.75, 0.15, 0.10],
                [0.80, 0.10, 0.10],
            ],
            dtype=np.float64,
        )

        directions, confidence = (
            _consensus_direction_confidence(
                (first, second, third)
            )
        )

        self.assertEqual(
            directions.tolist(),
            [
                "LONG",
                "SHORT",
                "NO_TRADE",
                "NO_TRADE",
            ],
        )
        self.assertAlmostEqual(confidence[0], 0.65)
        self.assertAlmostEqual(confidence[1], 0.70)
        self.assertTrue(np.isneginf(confidence[2]))
        self.assertTrue(np.isneginf(confidence[3]))

    def test_consensus_confidence_is_minimum_support(
        self,
    ) -> None:
        matrices = (
            np.asarray([[0.91, 0.05, 0.04]]),
            np.asarray([[0.73, 0.12, 0.15]]),
            np.asarray([[0.84, 0.08, 0.08]]),
        )
        directions, confidence = (
            _consensus_direction_confidence(matrices)
        )
        self.assertEqual(directions.tolist(), ["LONG"])
        self.assertAlmostEqual(confidence[0], 0.73)

    def test_budget_cutoff_uses_consensus_rank(
        self,
    ) -> None:
        directions = np.asarray(
            ["LONG"] * 300,
            dtype=object,
        )
        confidence = np.linspace(
            0.99,
            0.51,
            300,
            dtype=np.float64,
        )
        row_ids = tuple(
            f"row-{index:04d}"
            for index in range(300)
        )

        report = _derive_consensus_cutoff(
            directions=directions,
            confidence=confidence,
            row_ids=row_ids,
            budget=250,
        )

        self.assertEqual(report["status"], "AVAILABLE")
        self.assertEqual(
            report["eligible_consensus_row_count"],
            300,
        )
        self.assertEqual(
            report["selection_candidate_count_at_cutoff"],
            250,
        )
        self.assertAlmostEqual(
            report["selection_derived_cutoff"],
            confidence[249],
        )

    def test_cutoff_ties_expand_candidate_count(self) -> None:
        directions = np.asarray(
            ["LONG"] * 300,
            dtype=object,
        )
        confidence = np.linspace(
            0.99,
            0.51,
            300,
            dtype=np.float64,
        )
        confidence[249] = confidence[248]
        confidence[250] = confidence[248]
        row_ids = tuple(
            f"row-{index:04d}"
            for index in range(300)
        )

        report = _derive_consensus_cutoff(
            directions=directions,
            confidence=confidence,
            row_ids=row_ids,
            budget=250,
        )
        self.assertGreater(
            report["selection_candidate_count_at_cutoff"],
            250,
        )

    def test_insufficient_consensus_rows_make_budget_unavailable(
        self,
    ) -> None:
        directions = np.asarray(
            ["LONG"] * 249 + ["NO_TRADE"] * 10,
            dtype=object,
        )
        confidence = np.asarray(
            [0.80] * 249 + [float("-inf")] * 10,
            dtype=np.float64,
        )
        row_ids = tuple(
            f"row-{index:04d}"
            for index in range(len(directions))
        )

        report = _derive_consensus_cutoff(
            directions=directions,
            confidence=confidence,
            row_ids=row_ids,
            budget=250,
        )
        self.assertEqual(
            report["status"],
            "UNAVAILABLE_INSUFFICIENT_CONSENSUS_ROWS",
        )
        self.assertIsNone(
            report["selection_derived_cutoff"]
        )

    def test_forward_candidate_rule_uses_exact_consensus_cutoff(
        self,
    ) -> None:
        directions = np.asarray(
            ["LONG", "SHORT", "LONG", "NO_TRADE"],
            dtype=object,
        )
        confidence = np.asarray(
            [0.80, 0.70, 0.59, float("-inf")],
            dtype=np.float64,
        )
        candidates = _candidate_directions(
            directions=directions,
            confidence=confidence,
            cutoff=0.60,
        )
        self.assertEqual(
            candidates.tolist(),
            ["LONG", "SHORT", "NO_TRADE", "NO_TRADE"],
        )

    def test_source_is_non_executable_and_has_no_dispatch(
        self,
    ) -> None:
        self.assertFalse(
            REGIME_CONSENSUS_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(MODEL_FIT_AUTHORIZED)

        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_regime_consensus_training.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("broker_send", source)
        self.assertNotIn(
            '_fit_family(\n            "logistic_regression"',
            source,
        )


if __name__ == "__main__":
    unittest.main()
