from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest

import numpy as np
import polars as pl

import fmp.market_learning.model_successor_stability_training as stability
from fmp.market_learning.model_protocol import ModelCell
from fmp.market_learning.model_successor_stability_protocol import (
    MIN_STABILITY_WINDOW_CANDIDATE_SHARE,
    STABILITY_PROTOCOL_DECISION,
    STABILITY_SUCCESSOR_EXPERIMENT_ID,
    stability_protocol_fingerprint,
)
from fmp.market_learning.model_successor_stability_training import (
    DEC096_SUCCESSOR_TRAINING_BLOB_SHA,
    DEC104_MERGED_COMMIT,
    DEC104_PROTOCOL_BLOB_SHA,
    MODEL_FIT_AUTHORIZED,
    STABILITY_TRAINING_CORE_DECISION,
    STABILITY_TRAINING_RESULT_EXECUTION_AUTHORIZED,
    _evaluate_temporal_stability,
    _window_gate,
    _window_indices,
    validate_stability_training_sources,
)


ROOT = Path(__file__).resolve().parents[1]
UTC = timezone.utc
CELL = ModelCell("EURUSD", "5m", 60)


def _window_frame(
    *,
    negative_window: str | None = None,
) -> tuple[pl.DataFrame, np.ndarray]:
    windows = (
        ("selection_2021_h1", datetime(2021, 2, 1, tzinfo=UTC)),
        ("selection_2021_h2", datetime(2021, 8, 1, tzinfo=UTC)),
        ("selection_2022_h1", datetime(2022, 2, 1, tzinfo=UTC)),
        ("selection_2022_h2", datetime(2022, 8, 1, tzinfo=UTC)),
    )
    rows: list[dict[str, object]] = []
    probabilities: list[list[float]] = []

    for name, base in windows:
        for index in range(2):
            bar_start = base + timedelta(hours=index)
            available = bar_start + timedelta(minutes=5)
            exit_timestamp = available + timedelta(minutes=60)
            long_net = (
                -5.0
                if name == negative_window
                else 5.0
            )
            rows.append(
                {
                    "symbol": "EURUSD",
                    "timeframe": "5m",
                    "bar_start_utc": bar_start,
                    "available_at_utc": available,
                    "exit_timestamp_utc": exit_timestamp,
                    "long_net_pips_0p5": long_net,
                    "short_net_pips_0p5": -7.0,
                }
            )
            probabilities.append([0.90, 0.05, 0.05])

    return (
        pl.DataFrame(rows),
        np.asarray(probabilities, dtype=np.float64),
    )


class Exp046StabilityTrainingCoreTests(unittest.TestCase):
    def test_source_binds_exact_merged_protocol_and_predecessor_core(
        self,
    ) -> None:
        report = validate_stability_training_sources(
            repository_root=ROOT,
        )
        self.assertEqual(
            report["dec104_merged_commit"],
            DEC104_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC104_MERGED_COMMIT,
            "bb2ee82a7d081138e1c0847e8c406d6c3ac68589",
        )
        self.assertEqual(
            report["dec104_protocol_blob_sha"],
            DEC104_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            report["dec096_successor_training_blob_sha"],
            DEC096_SUCCESSOR_TRAINING_BLOB_SHA,
        )
        self.assertEqual(
            report["stability_protocol_fingerprint"],
            stability_protocol_fingerprint(),
        )
        self.assertEqual(
            report["stability_training_core_decision"],
            STABILITY_TRAINING_CORE_DECISION,
        )
        self.assertEqual(
            STABILITY_TRAINING_CORE_DECISION,
            "DEC-105",
        )
        self.assertFalse(
            report[
                "stability_training_result_execution_authorized"
            ]
        )
        self.assertFalse(report["model_fit_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["shadow_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_window_indices_enforce_available_and_exit_boundaries(
        self,
    ) -> None:
        frame = pl.DataFrame(
            {
                "available_at_utc": [
                    datetime(2021, 1, 1, tzinfo=UTC),
                    datetime(
                        2021,
                        6,
                        30,
                        22,
                        0,
                        tzinfo=UTC,
                    ),
                    datetime(
                        2021,
                        6,
                        30,
                        23,
                        30,
                        tzinfo=UTC,
                    ),
                    datetime(2021, 7, 1, tzinfo=UTC),
                ],
                "exit_timestamp_utc": [
                    datetime(
                        2021,
                        1,
                        1,
                        1,
                        tzinfo=UTC,
                    ),
                    datetime(
                        2021,
                        6,
                        30,
                        23,
                        0,
                        tzinfo=UTC,
                    ),
                    datetime(
                        2021,
                        7,
                        1,
                        0,
                        30,
                        tzinfo=UTC,
                    ),
                    datetime(
                        2021,
                        7,
                        1,
                        1,
                        tzinfo=UTC,
                    ),
                ],
            }
        )
        indices = _window_indices(
            frame,
            start=datetime(2021, 1, 1, tzinfo=UTC),
            end_exclusive=datetime(
                2021,
                7,
                1,
                tzinfo=UTC,
            ),
        )
        self.assertEqual(indices, [0, 1])

    def test_window_gate_uses_share_not_250_subwindow_floor(
        self,
    ) -> None:
        metrics = {
            "directional_candidate_count": 40,
            "total_net_pips": 100.0,
            "mean_net_pips": 2.5,
            "gross_positive_pips": 130.0,
            "absolute_gross_negative_pips": 30.0,
        }
        gate = _window_gate(
            metrics,
            full_selection_candidate_count=300,
        )
        self.assertTrue(gate["passed"])
        self.assertAlmostEqual(
            gate["directional_candidate_share"],
            40 / 300,
        )
        self.assertGreaterEqual(
            gate["directional_candidate_share"],
            MIN_STABILITY_WINDOW_CANDIDATE_SHARE,
        )

    def test_all_four_positive_windows_pass_stability(
        self,
    ) -> None:
        frame, probabilities = _window_frame()
        report = _evaluate_temporal_stability(
            selection_frame=frame,
            probabilities=probabilities,
            threshold=0.5,
            cell=CELL,
            full_selection_candidate_count=8,
        )
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(len(report["windows"]), 4)
        self.assertTrue(
            all(
                window["gate"]["passed"]
                for window in report["windows"]
            )
        )
        self.assertTrue(
            all(
                window["gate"][
                    "directional_candidate_share"
                ]
                == 0.25
                for window in report["windows"]
            )
        )

    def test_one_negative_window_rejects_stability(
        self,
    ) -> None:
        frame, probabilities = _window_frame(
            negative_window="selection_2022_h1"
        )
        report = _evaluate_temporal_stability(
            selection_frame=frame,
            probabilities=probabilities,
            threshold=0.5,
            cell=CELL,
            full_selection_candidate_count=8,
        )
        self.assertEqual(report["status"], "REJECT")
        indexed = {
            window["name"]: window
            for window in report["windows"]
        }
        rejected = indexed["selection_2022_h1"]
        self.assertFalse(rejected["gate"]["passed"])
        self.assertFalse(
            rejected["gate"]["criteria"][
                "total_net_pips>0"
            ]
        )
        self.assertFalse(
            rejected["gate"]["criteria"][
                "mean_net_pips>0"
            ]
        )

    def test_source_is_source_only_and_authorization_closed(
        self,
    ) -> None:
        self.assertEqual(
            STABILITY_SUCCESSOR_EXPERIMENT_ID,
            "EXP-20260923-046",
        )
        self.assertEqual(
            STABILITY_PROTOCOL_DECISION,
            "DEC-104",
        )
        self.assertFalse(
            STABILITY_TRAINING_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(MODEL_FIT_AUTHORIZED)

        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_stability_training.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("broker_send", source)


if __name__ == "__main__":
    unittest.main()
