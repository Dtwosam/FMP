from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np
import polars as pl

from fmp.market_learning.model_successor_temporal_jackknife_utility_training import (
    DEC141_MERGED_COMMIT,
    DEC141_PROTOCOL_BLOB_SHA,
    MODEL_FIT_AUTHORIZED,
    PREDECESSOR_TRAINING_CORE_BLOB_SHA,
    TEMPORAL_JACKKNIFE_UTILITY_RESULT_EXECUTION_AUTHORIZED,
    TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_DECISION,
    _build_jackknife_view_frames,
    _candidate_directions,
    _derive_utility_cutoff,
    _jackknife_view_regime_names,
    _selection_key,
    _temporal_jackknife_utility_direction_score,
    validate_temporal_jackknife_utility_training_sources,
)


ROOT = Path(__file__).resolve().parents[1]


class Exp050TemporalJackknifeUtilityTrainingCoreTests(
    unittest.TestCase
):
    def test_source_binds_exact_protocol_and_predecessor_core(
        self,
    ) -> None:
        report = (
            validate_temporal_jackknife_utility_training_sources(
                repository_root=ROOT,
            )
        )

        self.assertEqual(
            report["dec141_merged_commit"],
            DEC141_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC141_MERGED_COMMIT,
            "4729da0e769f76f44b97ff6349ee25c5b7c0f5c7",
        )
        self.assertEqual(
            report["dec141_protocol_blob_sha"],
            DEC141_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            DEC141_PROTOCOL_BLOB_SHA,
            "b41b817b03aa0cc03a9d893227caa399b46d3cf8",
        )
        self.assertEqual(
            report["predecessor_training_core_blob_sha"],
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            PREDECESSOR_TRAINING_CORE_BLOB_SHA,
            "e1018b20210b7bb8d666071d8eb878aba5899111",
        )
        self.assertEqual(
            report[
                "temporal_jackknife_utility_training_core_decision"
            ],
            TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_DECISION,
        )
        self.assertEqual(
            TEMPORAL_JACKKNIFE_UTILITY_TRAINING_CORE_DECISION,
            "DEC-142",
        )
        self.assertFalse(
            report[
                "temporal_jackknife_utility_result_execution_authorized"
            ]
        )
        self.assertFalse(report["model_fit_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["shadow_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_jackknife_view_regime_names_are_exact(self) -> None:
        views = _jackknife_view_regime_names()
        self.assertEqual(
            views,
            {
                "leave_out_fit_2015_2016": (
                    "fit_2017_2018",
                    "fit_2019_2020",
                ),
                "leave_out_fit_2017_2018": (
                    "fit_2015_2016",
                    "fit_2019_2020",
                ),
                "leave_out_fit_2019_2020": (
                    "fit_2015_2016",
                    "fit_2017_2018",
                ),
            },
        )

    def test_jackknife_view_frames_exclude_exact_regime(
        self,
    ) -> None:
        regimes = {
            "fit_2015_2016": pl.DataFrame(
                {"tag": ["a1", "a2"]}
            ),
            "fit_2017_2018": pl.DataFrame(
                {"tag": ["b1", "b2", "b3"]}
            ),
            "fit_2019_2020": pl.DataFrame(
                {"tag": ["c1", "c2"]}
            ),
        }

        views = _build_jackknife_view_frames(regimes)

        self.assertEqual(
            views[
                "leave_out_fit_2015_2016"
            ]["tag"].to_list(),
            ["b1", "b2", "b3", "c1", "c2"],
        )
        self.assertEqual(
            views[
                "leave_out_fit_2017_2018"
            ]["tag"].to_list(),
            ["a1", "a2", "c1", "c2"],
        )
        self.assertEqual(
            views[
                "leave_out_fit_2019_2020"
            ]["tag"].to_list(),
            ["a1", "a2", "b1", "b2", "b3"],
        )

    def test_jackknife_view_frames_require_all_regimes(
        self,
    ) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "frame set mismatch",
        ):
            _build_jackknife_view_frames(
                {
                    "fit_2015_2016": pl.DataFrame(
                        {"tag": ["a"]}
                    ),
                    "fit_2017_2018": pl.DataFrame(
                        {"tag": ["b"]}
                    ),
                }
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
            _temporal_jackknife_utility_direction_score(
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

    def test_robust_utility_is_minimum_view_prediction(
        self,
    ) -> None:
        matrices = (
            np.asarray([[3.2, -1.0]], dtype=np.float64),
            np.asarray([[1.7, -0.8]], dtype=np.float64),
            np.asarray([[2.4, -0.5]], dtype=np.float64),
        )
        directions, score = (
            _temporal_jackknife_utility_direction_score(
                matrices
            )
        )

        self.assertEqual(directions.tolist(), ["LONG"])
        self.assertAlmostEqual(score[0], 1.7)

    def test_budget_cutoff_and_forward_rule_remain_exact(
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
        cutoff = float(
            report["selection_derived_cutoff"]
        )
        candidates = _candidate_directions(
            directions=directions,
            utility=utility,
            cutoff=cutoff,
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
            TEMPORAL_JACKKNIFE_UTILITY_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(MODEL_FIT_AUTHORIZED)

        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_temporal_jackknife_utility_training.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("broker_send", source)
        self.assertNotIn("HistGradientBoostingClassifier(", source)
        self.assertNotIn("LogisticRegression(", source)


if __name__ == "__main__":
    unittest.main()
