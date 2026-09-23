from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest
from unittest.mock import patch

import polars as pl

from fmp.features.schema import FEATURE_VALUE_COLUMNS
from fmp.market_learning.contracts import (
    EVIDENCE_LABEL,
    MARKET_FEATURE_SET_VERSION,
)
from fmp.market_learning.model_protocol import (
    CONFIDENCE_THRESHOLDS,
    MODEL_FAMILIES,
    ModelCell,
)
from fmp.market_learning.model_training import (
    MODEL_TRAINING_RESULT_EXECUTION_AUTHORIZED,
    run_model_cell_core,
)
from fmp.market_learning.outcomes import (
    MARKET_OUTCOME_SET_VERSION,
)


ROOT = Path(__file__).resolve().parents[1]
UTC = timezone.utc
MANIFEST = "a" * 64
CELL = ModelCell("EURUSD", "5m", 60)


def _scenario_values(
    target: str,
    *,
    magnitude: float,
) -> tuple[float, float, str]:
    if target == "LONG":
        return magnitude, -(magnitude + 2.0), "LONG"
    if target == "SHORT":
        return -(magnitude + 2.0), magnitude, "SHORT"
    return -2.0, -2.0, "NO_TRADE"


def _frames(
    *,
    rows_per_split: int = 450,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    split_bases = (
        datetime(2018, 1, 2, tzinfo=UTC),
        datetime(2021, 1, 2, tzinfo=UTC),
        datetime(2023, 1, 2, tzinfo=UTC),
        datetime(2025, 1, 2, tzinfo=UTC),
    )
    classes = ("LONG", "SHORT", "NO_TRADE")
    signal = {
        "LONG": 10.0,
        "SHORT": -10.0,
        "NO_TRADE": 0.0,
    }

    feature_rows: list[dict[str, object]] = []
    outcome_rows: list[dict[str, object]] = []

    for split_index, base in enumerate(split_bases):
        for index in range(rows_per_split):
            target = classes[index % len(classes)]
            bar_start = base + timedelta(minutes=5 * index)
            available = bar_start + timedelta(minutes=5)
            exit_timestamp = available + timedelta(minutes=60)

            feature: dict[str, object] = {
                "symbol": "EURUSD",
                "timeframe": "5m",
                "bar_start_utc": bar_start,
                "bar_end_utc": available,
                "available_at_utc": available,
                "feature_set_version": MARKET_FEATURE_SET_VERSION,
                "processed_manifest_sha256": MANIFEST,
            }
            for column_index, name in enumerate(FEATURE_VALUE_COLUMNS):
                feature[name] = (
                    signal[target]
                    + float(column_index) / 1000.0
                    + float(index % 5) / 10000.0
                )
            feature_rows.append(feature)

            long_02, short_02, direction_02 = _scenario_values(
                target,
                magnitude=8.0,
            )
            long_05, short_05, direction_05 = _scenario_values(
                target,
                magnitude=7.0,
            )
            long_10, short_10, direction_10 = _scenario_values(
                target,
                magnitude=6.0,
            )
            outcome_rows.append(
                {
                    "symbol": "EURUSD",
                    "timeframe": "5m",
                    "bar_start_utc": bar_start,
                    "available_at_utc": available,
                    "exit_timestamp_utc": exit_timestamp,
                    "horizon_minutes": 60,
                    "future_mid_move_pips": (
                        10.0
                        if target == "LONG"
                        else -10.0
                        if target == "SHORT"
                        else 0.0
                    ),
                    "long_net_pips_0p2": long_02,
                    "short_net_pips_0p2": short_02,
                    "best_direction_0p2": direction_02,
                    "long_net_pips_0p5": long_05,
                    "short_net_pips_0p5": short_05,
                    "best_direction_0p5": direction_05,
                    "long_net_pips_1p0": long_10,
                    "short_net_pips_1p0": short_10,
                    "best_direction_1p0": direction_10,
                    "feature_set_version": MARKET_FEATURE_SET_VERSION,
                    "outcome_set_version": MARKET_OUTCOME_SET_VERSION,
                    "evidence_label": EVIDENCE_LABEL,
                    "processed_manifest_sha256": MANIFEST,
                }
            )

    return pl.DataFrame(feature_rows), pl.DataFrame(outcome_rows)


class Exp044ModelTrainingCoreTests(unittest.TestCase):
    def test_source_exists_but_historical_result_execution_remains_locked(self) -> None:
        self.assertIs(MODEL_TRAINING_RESULT_EXECUTION_AUTHORIZED, False)
        self.assertFalse(
            (
                ROOT
                / ".github/workflows/"
                "phase8a-exp044-model-training.yml"
            ).exists()
        )

    def test_core_fits_each_family_once_and_never_refits_after_selection(self) -> None:
        import fmp.market_learning.model_training as training

        features, outcomes = _frames()
        with patch.object(
            training,
            "_fit_family",
            wraps=training._fit_family,
        ) as fit_spy:
            result = run_model_cell_core(
                features=features,
                outcomes=outcomes,
                cell=CELL,
            )

        self.assertEqual(fit_spy.call_count, len(MODEL_FAMILIES))
        self.assertEqual(result["selection"]["status"], "SELECTED")
        selected = result["selection"]["selected_variant"]
        self.assertIn(selected["model_family"], MODEL_FAMILIES)
        self.assertIn(
            selected["confidence_threshold"],
            CONFIDENCE_THRESHOLDS,
        )
        self.assertEqual(result["validation"]["status"], "PASS")
        self.assertEqual(
            result["retrospective_holdout"]["status"],
            "PASS",
        )
        self.assertFalse(result["promotion_authorized"])
        self.assertFalse(result["shadow_authorized"])
        self.assertFalse(result["demo_order_authorized"])
        self.assertFalse(result["broker_mutation_authorized"])
        self.assertFalse(result["live_order_authorized"])
        self.assertFalse(result["real_money_authorized"])
        self.assertEqual(len(result["result_fingerprint"]), 64)

    def test_core_is_deterministic_for_identical_synthetic_inputs(self) -> None:
        features, outcomes = _frames()
        first = run_model_cell_core(
            features=features,
            outcomes=outcomes,
            cell=CELL,
        )
        second = run_model_cell_core(
            features=features,
            outcomes=outcomes,
            cell=CELL,
        )
        self.assertEqual(
            first["result_fingerprint"],
            second["result_fingerprint"],
        )
        self.assertEqual(
            first["selection"]["probability_digest_by_family"],
            second["selection"]["probability_digest_by_family"],
        )
        self.assertEqual(first, second)

    def test_financial_gate_uses_fixed_minimum_candidate_count(self) -> None:
        features, outcomes = _frames(rows_per_split=180)
        result = run_model_cell_core(
            features=features,
            outcomes=outcomes,
            cell=CELL,
        )
        self.assertEqual(
            result["selection"]["status"],
            "NO_MODEL_CHALLENGER",
        )
        self.assertEqual(
            result["validation"]["status"],
            "LOCKED_NO_SELECTION",
        )
        self.assertEqual(
            result["retrospective_holdout"]["status"],
            "LOCKED_NO_SELECTION",
        )

    def test_inconsistent_frozen_outcome_direction_fails_closed(self) -> None:
        features, outcomes = _frames()
        rows = outcomes.to_dicts()
        rows[0]["best_direction_0p5"] = "SHORT"
        with self.assertRaisesRegex(
            ValueError,
            "direction does not match frozen pips",
        ):
            run_model_cell_core(
                features=features,
                outcomes=pl.DataFrame(rows),
                cell=CELL,
            )


if __name__ == "__main__":
    unittest.main()
