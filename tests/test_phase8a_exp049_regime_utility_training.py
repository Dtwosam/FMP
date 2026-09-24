from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

from fmp.market_learning.model_successor_regime_utility_training import (
    BASE_TRAINING_CORE_BLOB_SHA,
    DEC132_MERGED_COMMIT,
    DEC132_PROTOCOL_BLOB_SHA,
    DENSITY_HELPER_CORE_BLOB_SHA,
    MODEL_FIT_AUTHORIZED,
    REGIME_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    REGIME_UTILITY_TRAINING_CORE_DECISION,
    _candidate_directions,
    _derive_utility_cutoff,
    _fit_regime_splits,
    _regime_utility_direction_score,
    _selection_key,
    validate_regime_utility_training_sources,
)


ROOT = Path(__file__).resolve().parents[1]


class Exp049RegimeUtilityTrainingCoreTests(
    unittest.TestCase
):
    def test_source_binds_exact_merged_protocol_and_helpers(
        self,
    ) -> None:
        report = validate_regime_utility_training_sources(
            repository_root=ROOT,
        )

        self.assertEqual(
            report["dec132_merged_commit"],
            DEC132_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC132_MERGED_COMMIT,
            "d17326eebf6b456211225d7bad3a182a0307b707",
        )
        self.assertEqual(
            report["dec132_protocol_blob_sha"],
            DEC132_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            DEC132_PROTOCOL_BLOB_SHA,
            "ad2fcb22656fc7a1490f4cdf87fb25c62895a1ac",
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
                "regime_utility_training_core_decision"
            ],
            REGIME_UTILITY_TRAINING_CORE_DECISION,
        )
        self.assertEqual(
            REGIME_UTILITY_TRAINING_CORE_DECISION,
            "DEC-133",
        )
        self.assertFalse(
            report[
                "regime_utility_result_execution_authorized"
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

    def test_utility_consensus_requires_positive_unanimity(
        self,
    ) -> None:
        first = np.asarray(
            [
                [2.0, -1.0],
                [-0.5, 1.5],
                [2.0, -1.0],
                [-0.2, -0.1],
                [1.0, 1.0],
            ],
            dtype=np.float64,
        )
        second = np.asarray(
            [
                [1.4, -0.7],
                [-0.4, 1.2],
                [-0.5, 1.3],
                [-0.5, 0.2],
                [1.5, 0.5],
            ],
            dtype=np.float64,
        )
        third = np.asarray(
            [
                [1.1, -0.3],
                [-0.2, 1.0],
                [1.7, -0.8],
                [-0.6, 0.3],
                [1.2, 0.4],
            ],
            dtype=np.float64,
        )

        directions, score = (
            _regime_utility_direction_score(
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
                "NO_TRADE",
            ],
        )
        self.assertAlmostEqual(score[0], 1.1)
        self.assertAlmostEqual(score[1], 1.0)
        self.assertTrue(np.isneginf(score[2]))
        self.assertTrue(np.isneginf(score[3]))
        self.assertTrue(np.isneginf(score[4]))

    def test_robust_utility_is_minimum_agreed_prediction(
        self,
    ) -> None:
        matrices = (
            np.asarray([[3.2, -1.0]], dtype=np.float64),
            np.asarray([[1.7, -0.8]], dtype=np.float64),
            np.asarray([[2.4, -0.5]], dtype=np.float64),
        )
        directions, score = (
            _regime_utility_direction_score(matrices)
        )

        self.assertEqual(directions.tolist(), ["LONG"])
        self.assertAlmostEqual(score[0], 1.7)

    def test_nonfinite_predictions_fail_closed(self) -> None:
        matrices = (
            np.asarray([[1.0, -1.0]], dtype=np.float64),
            np.asarray([[float("nan"), -1.0]]),
            np.asarray([[1.0, -1.0]], dtype=np.float64),
        )
        with self.assertRaisesRegex(
            ValueError,
            "finite",
        ):
            _regime_utility_direction_score(matrices)

    def test_budget_cutoff_uses_robust_utility_rank(
        self,
    ) -> None:
        directions = np.asarray(
            ["LONG"] * 300,
            dtype=object,
        )
        utility = np.linspace(
            3.0,
            0.1,
            300,
            dtype=np.float64,
        )
        row_ids = tuple(
            f"row-{index:04d}"
            for index in range(300)
        )

        report = _derive_utility_cutoff(
            directions=directions,
            utility=utility,
            row_ids=row_ids,
            budget=250,
        )

        self.assertEqual(report["status"], "AVAILABLE")
        self.assertEqual(
            report["eligible_utility_row_count"],
            300,
        )
        self.assertEqual(
            report["selection_candidate_count_at_cutoff"],
            250,
        )
        self.assertAlmostEqual(
            report["selection_derived_cutoff"],
            utility[249],
        )

    def test_cutoff_ties_expand_candidate_count(self) -> None:
        directions = np.asarray(
            ["LONG"] * 300,
            dtype=object,
        )
        utility = np.linspace(
            3.0,
            0.1,
            300,
            dtype=np.float64,
        )
        utility[249] = utility[248]
        utility[250] = utility[248]
        row_ids = tuple(
            f"row-{index:04d}"
            for index in range(300)
        )

        report = _derive_utility_cutoff(
            directions=directions,
            utility=utility,
            row_ids=row_ids,
            budget=250,
        )
        self.assertGreater(
            report["selection_candidate_count_at_cutoff"],
            250,
        )

    def test_insufficient_utility_rows_make_budget_unavailable(
        self,
    ) -> None:
        directions = np.asarray(
            ["LONG"] * 249 + ["NO_TRADE"] * 10,
            dtype=object,
        )
        utility = np.asarray(
            [0.8] * 249 + [float("-inf")] * 10,
            dtype=np.float64,
        )
        row_ids = tuple(
            f"row-{index:04d}"
            for index in range(len(directions))
        )

        report = _derive_utility_cutoff(
            directions=directions,
            utility=utility,
            row_ids=row_ids,
            budget=250,
        )
        self.assertEqual(
            report["status"],
            "UNAVAILABLE_INSUFFICIENT_UTILITY_ROWS",
        )
        self.assertIsNone(
            report["selection_derived_cutoff"]
        )

    def test_forward_candidate_rule_uses_exact_utility_cutoff(
        self,
    ) -> None:
        directions = np.asarray(
            ["LONG", "SHORT", "LONG", "NO_TRADE"],
            dtype=object,
        )
        utility = np.asarray(
            [1.2, 0.8, 0.59, float("-inf")],
            dtype=np.float64,
        )
        candidates = _candidate_directions(
            directions=directions,
            utility=utility,
            cutoff=0.60,
        )
        self.assertEqual(
            candidates.tolist(),
            ["LONG", "SHORT", "NO_TRADE", "NO_TRADE"],
        )

    def test_nonpositive_forward_cutoff_fails_closed(self) -> None:
        directions = np.asarray(["LONG"], dtype=object)
        utility = np.asarray([0.1], dtype=np.float64)
        with self.assertRaisesRegex(
            ValueError,
            "cutoff",
        ):
            _candidate_directions(
                directions=directions,
                utility=utility,
                cutoff=0.0,
            )

    def test_selection_tie_break_prefers_smaller_budget(
        self,
    ) -> None:
        def row(budget: int) -> dict[str, object]:
            return {
                "candidate_budget_anchor": budget,
                "scenarios": {
                    "0.5": {
                        "metrics": {
                            "total_net_pips": 123.0,
                            "directional_candidate_count": 500,
                        }
                    }
                },
            }

        selected = max(
            [row(1000), row(250), row(500)],
            key=_selection_key,
        )
        self.assertEqual(
            selected["candidate_budget_anchor"],
            250,
        )

    def test_source_is_non_executable_and_has_no_dispatch(
        self,
    ) -> None:
        self.assertFalse(
            REGIME_UTILITY_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(MODEL_FIT_AUTHORIZED)

        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_regime_utility_training.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("broker_send", source)
        self.assertNotIn("HistGradientBoostingClassifier(", source)
        self.assertNotIn("LogisticRegression(", source)


if __name__ == "__main__":
    unittest.main()
