from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest

import numpy as np
import polars as pl

from fmp.market_learning.model_protocol import ModelCell
from fmp.market_learning.model_successor_density_protocol import (
    CANDIDATE_BUDGET_ANCHORS,
    DENSITY_PROTOCOL_DECISION,
    DENSITY_SUCCESSOR_EXPERIMENT_ID,
    density_protocol_fingerprint,
)
from fmp.market_learning.model_successor_density_training import (
    BASE_TRAINING_CORE_BLOB_SHA,
    DEC113_MERGED_COMMIT,
    DEC113_PROTOCOL_BLOB_SHA,
    DENSITY_TRAINING_CORE_DECISION,
    DENSITY_TRAINING_RESULT_EXECUTION_AUTHORIZED,
    MODEL_FIT_AUTHORIZED,
    _density_candidate_directions,
    _derive_density_cutoff,
    _evaluate_temporal_stability,
    _window_gate,
    validate_density_training_sources,
)


ROOT = Path(__file__).resolve().parents[1]
UTC = timezone.utc
CELL = ModelCell("EURUSD", "5m", 60)


def _directional_probabilities(
    count: int,
) -> np.ndarray:
    scores = np.linspace(
        0.99,
        0.51,
        count,
        dtype=np.float64,
    )
    return np.column_stack(
        [
            scores,
            (1.0 - scores) * 0.4,
            (1.0 - scores) * 0.6,
        ]
    )


def _window_frame() -> tuple[pl.DataFrame, np.ndarray]:
    windows = (
        datetime(2021, 2, 1, tzinfo=UTC),
        datetime(2021, 8, 1, tzinfo=UTC),
        datetime(2022, 2, 1, tzinfo=UTC),
        datetime(2022, 8, 1, tzinfo=UTC),
    )
    rows: list[dict[str, object]] = []
    probabilities: list[list[float]] = []

    for base in windows:
        for index in range(2):
            bar_start = base + timedelta(hours=index)
            available = bar_start + timedelta(minutes=5)
            rows.append(
                {
                    "symbol": "EURUSD",
                    "timeframe": "5m",
                    "bar_start_utc": bar_start,
                    "available_at_utc": available,
                    "exit_timestamp_utc": (
                        available + timedelta(minutes=60)
                    ),
                    "long_net_pips_0p5": 5.0,
                    "short_net_pips_0p5": -7.0,
                }
            )
            probabilities.append([0.90, 0.05, 0.05])

    return (
        pl.DataFrame(rows),
        np.asarray(probabilities, dtype=np.float64),
    )


class Exp047DensityTrainingCoreTests(unittest.TestCase):
    def test_source_binds_exact_merged_protocol_and_base_core(
        self,
    ) -> None:
        report = validate_density_training_sources(
            repository_root=ROOT,
        )
        self.assertEqual(
            report["dec113_merged_commit"],
            DEC113_MERGED_COMMIT,
        )
        self.assertEqual(
            DEC113_MERGED_COMMIT,
            "060bde94835158d62d47640aaf1a77ec56b483ff",
        )
        self.assertEqual(
            report["dec113_protocol_blob_sha"],
            DEC113_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            report["base_training_core_blob_sha"],
            BASE_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            report["density_protocol_fingerprint"],
            density_protocol_fingerprint(),
        )
        self.assertEqual(
            report["density_training_core_decision"],
            DENSITY_TRAINING_CORE_DECISION,
        )
        self.assertEqual(
            DENSITY_TRAINING_CORE_DECISION,
            "DEC-114",
        )
        self.assertFalse(
            report[
                "density_training_result_execution_authorized"
            ]
        )
        self.assertFalse(report["model_fit_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["shadow_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_budget_anchors_are_exact(self) -> None:
        self.assertEqual(
            CANDIDATE_BUDGET_ANCHORS,
            (250, 500, 1000),
        )

    def test_derive_cutoff_uses_budget_rank(self) -> None:
        probabilities = _directional_probabilities(1000)
        row_ids = tuple(
            f"row-{index:04d}"
            for index in range(1000)
        )

        report = _derive_density_cutoff(
            probabilities=probabilities,
            row_ids=row_ids,
            budget=250,
        )

        self.assertEqual(report["status"], "AVAILABLE")
        self.assertEqual(
            report["candidate_budget_anchor"],
            250,
        )
        self.assertEqual(
            report["eligible_directional_row_count"],
            1000,
        )
        self.assertEqual(
            report["selection_candidate_count_at_cutoff"],
            250,
        )
        self.assertAlmostEqual(
            report["selection_derived_cutoff"],
            probabilities[249, 0],
        )

    def test_cutoff_ties_expand_candidate_count(self) -> None:
        probabilities = _directional_probabilities(500)
        probabilities[249, :] = probabilities[248, :]
        probabilities[250, :] = probabilities[248, :]
        row_ids = tuple(
            f"row-{index:04d}"
            for index in range(500)
        )

        report = _derive_density_cutoff(
            probabilities=probabilities,
            row_ids=row_ids,
            budget=250,
        )

        self.assertEqual(report["status"], "AVAILABLE")
        self.assertGreater(
            report["selection_candidate_count_at_cutoff"],
            250,
        )

    def test_insufficient_directional_rows_make_budget_unavailable(
        self,
    ) -> None:
        probabilities = _directional_probabilities(249)
        row_ids = tuple(
            f"row-{index:04d}"
            for index in range(249)
        )

        report = _derive_density_cutoff(
            probabilities=probabilities,
            row_ids=row_ids,
            budget=250,
        )

        self.assertEqual(
            report["status"],
            "UNAVAILABLE_INSUFFICIENT_DIRECTIONAL_ROWS",
        )
        self.assertIsNone(
            report["selection_derived_cutoff"]
        )

    def test_forward_candidate_rule_uses_exact_cutoff(
        self,
    ) -> None:
        probabilities = np.asarray(
            [
                [0.80, 0.10, 0.10],
                [0.60, 0.20, 0.20],
                [0.59, 0.21, 0.20],
                [0.10, 0.80, 0.10],
                [0.20, 0.20, 0.60],
            ],
            dtype=np.float64,
        )
        directions = _density_candidate_directions(
            probabilities,
            cutoff=0.60,
        )
        self.assertEqual(
            directions.tolist(),
            [
                "LONG",
                "LONG",
                "NO_TRADE",
                "SHORT",
                "NO_TRADE",
            ],
        )

    def test_window_gate_preserves_share_not_250_subwindow_floor(
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

    def test_all_four_windows_pass_with_same_frozen_cutoff(
        self,
    ) -> None:
        frame, probabilities = _window_frame()
        report = _evaluate_temporal_stability(
            selection_frame=frame,
            probabilities=probabilities,
            cutoff=0.60,
            budget=250,
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

    def test_source_is_source_only_and_logistic_free(
        self,
    ) -> None:
        self.assertEqual(
            DENSITY_SUCCESSOR_EXPERIMENT_ID,
            "EXP-20260924-047",
        )
        self.assertEqual(
            DENSITY_PROTOCOL_DECISION,
            "DEC-113",
        )
        self.assertFalse(
            DENSITY_TRAINING_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(MODEL_FIT_AUTHORIZED)

        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_density_training.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn(
            '_fit_family(\n        "logistic_regression"',
            source,
        )
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)
        self.assertNotIn("broker_send", source)


if __name__ == "__main__":
    unittest.main()
