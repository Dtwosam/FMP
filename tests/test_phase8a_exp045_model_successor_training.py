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
    ModelCell,
)
from fmp.market_learning.model_successor_protocol import (
    SUCCESSOR_EXPERIMENT_ID,
    SUCCESSOR_PROTOCOL_DECISION,
    SUCCESSOR_PROTOCOL_VERSION,
    successor_protocol_fingerprint,
)
from fmp.market_learning.model_successor_training import (
    BASE_TRAINING_CORE_BLOB_SHA,
    MODEL_FIT_AUTHORIZED,
    SUCCESSOR_PROTOCOL_BLOB_SHA,
    SUCCESSOR_TRAINING_CORE_DECISION,
    SUCCESSOR_TRAINING_CORE_VERSION,
    SUCCESSOR_TRAINING_RESULT_EXECUTION_AUTHORIZED,
    run_successor_model_cell_core,
    validate_successor_training_sources,
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

    for base in split_bases:
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
            for column_index, name in enumerate(
                FEATURE_VALUE_COLUMNS
            ):
                feature[name] = (
                    signal[target]
                    + float(column_index) / 1000.0
                    + float(index % 5) / 10000.0
                )
            feature_rows.append(feature)

            long_02, short_02, direction_02 = (
                _scenario_values(
                    target,
                    magnitude=8.0,
                )
            )
            long_05, short_05, direction_05 = (
                _scenario_values(
                    target,
                    magnitude=7.0,
                )
            )
            long_10, short_10, direction_10 = (
                _scenario_values(
                    target,
                    magnitude=6.0,
                )
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
                    "feature_set_version": (
                        MARKET_FEATURE_SET_VERSION
                    ),
                    "outcome_set_version": (
                        MARKET_OUTCOME_SET_VERSION
                    ),
                    "evidence_label": EVIDENCE_LABEL,
                    "processed_manifest_sha256": MANIFEST,
                }
            )

    return (
        pl.DataFrame(feature_rows),
        pl.DataFrame(outcome_rows),
    )


class Exp045SuccessorTrainingCoreTests(unittest.TestCase):
    def test_source_binds_exact_base_core_and_successor_protocol(self) -> None:
        report = validate_successor_training_sources(
            repository_root=ROOT,
        )
        self.assertEqual(
            report["base_training_core_blob_sha"],
            BASE_TRAINING_CORE_BLOB_SHA,
        )
        self.assertEqual(
            report["successor_protocol_blob_sha"],
            SUCCESSOR_PROTOCOL_BLOB_SHA,
        )
        self.assertEqual(
            report["successor_training_core_decision"],
            "DEC-096",
        )
        self.assertFalse(
            report[
                "successor_training_result_execution_authorized"
            ]
        )
        self.assertFalse(report["model_fit_authorized"])
        self.assertFalse(report["promotion_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_normal_synthetic_cell_uses_successor_identity(self) -> None:
        features, outcomes = _frames()
        result = run_successor_model_cell_core(
            features=features,
            outcomes=outcomes,
            cell=CELL,
        )
        self.assertEqual(
            result["experiment_id"],
            SUCCESSOR_EXPERIMENT_ID,
        )
        self.assertEqual(
            result["training_core_version"],
            SUCCESSOR_TRAINING_CORE_VERSION,
        )
        self.assertEqual(
            result["training_core_decision"],
            SUCCESSOR_TRAINING_CORE_DECISION,
        )
        self.assertEqual(
            result["protocol_decision"],
            SUCCESSOR_PROTOCOL_DECISION,
        )
        self.assertEqual(
            result["protocol_version"],
            SUCCESSOR_PROTOCOL_VERSION,
        )
        self.assertEqual(
            result["protocol_fingerprint"],
            successor_protocol_fingerprint(),
        )
        self.assertTrue(result["prior_result_informed"])
        self.assertFalse(result["untouched_oos"])
        self.assertEqual(
            result["fit"]["families"][
                "logistic_regression"
            ]["status"],
            "FITTED",
        )
        self.assertEqual(
            result["fit"]["families"][
                "hist_gradient_boosting"
            ]["status"],
            "FITTED",
        )
        self.assertEqual(
            len(result["selection"]["variants"]),
            6,
        )
        self.assertFalse(result["model_fit_authorized"])
        self.assertFalse(result["promotion_authorized"])
        self.assertFalse(result["trading_authorized"])
        self.assertEqual(len(result["result_fingerprint"]), 64)

    def test_logistic_nonconvergence_is_preserved_without_retry(self) -> None:
        import fmp.market_learning.model_successor_training as successor

        features, outcomes = _frames()
        original = successor._base._fit_family
        calls: list[str] = []

        def fit_with_logistic_failure(
            family: str,
            fit_frame: pl.DataFrame,
        ):
            calls.append(family)
            if family == "logistic_regression":
                raise RuntimeError(
                    "EXP-044 logistic regression failed to converge"
                )
            return original(family, fit_frame)

        with patch.object(
            successor._base,
            "_fit_family",
            side_effect=fit_with_logistic_failure,
        ):
            result = run_successor_model_cell_core(
                features=features,
                outcomes=outcomes,
                cell=CELL,
            )

        self.assertEqual(
            calls,
            [
                "logistic_regression",
                "hist_gradient_boosting",
            ],
        )
        logistic = result["fit"]["families"][
            "logistic_regression"
        ]
        self.assertEqual(
            logistic["status"],
            "FAILED_NON_CONVERGENCE",
        )
        self.assertEqual(
            logistic["failure_reason"],
            "LBFGS_MAX_ITER_REACHED",
        )
        self.assertEqual(logistic["fit_attempt_count"], 1)
        self.assertFalse(logistic["retry_authorized"])

        variants = result["selection"]["variants"]
        self.assertEqual(len(variants), 6)
        unavailable = [
            row
            for row in variants
            if row["model_family"]
            == "logistic_regression"
        ]
        self.assertEqual(
            [row["confidence_threshold"] for row in unavailable],
            list(CONFIDENCE_THRESHOLDS),
        )
        self.assertTrue(
            all(
                row["evaluation_status"]
                == "FAMILY_UNAVAILABLE"
                and row["selection_gate_passed"] is False
                for row in unavailable
            )
        )
        selected = result["selection"]["selected_variant"]
        if selected is not None:
            self.assertEqual(
                selected["model_family"],
                "hist_gradient_boosting",
            )

    def test_other_family_fit_failure_still_fails_closed(self) -> None:
        import fmp.market_learning.model_successor_training as successor

        features, outcomes = _frames()
        original = successor._base._fit_family

        def fail_hgb(
            family: str,
            fit_frame: pl.DataFrame,
        ):
            if family == "hist_gradient_boosting":
                raise RuntimeError("synthetic HGB failure")
            return original(family, fit_frame)

        with patch.object(
            successor._base,
            "_fit_family",
            side_effect=fail_hgb,
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "synthetic HGB failure",
            ):
                run_successor_model_cell_core(
                    features=features,
                    outcomes=outcomes,
                    cell=CELL,
                )

    def test_successor_result_is_deterministic_for_identical_inputs(self) -> None:
        features, outcomes = _frames()
        first = run_successor_model_cell_core(
            features=features,
            outcomes=outcomes,
            cell=CELL,
        )
        second = run_successor_model_cell_core(
            features=features,
            outcomes=outcomes,
            cell=CELL,
        )
        self.assertEqual(first, second)
        self.assertEqual(
            first["result_fingerprint"],
            second["result_fingerprint"],
        )

    def test_execution_authorization_remains_false_and_no_workflow_exists(self) -> None:
        self.assertFalse(
            SUCCESSOR_TRAINING_RESULT_EXECUTION_AUTHORIZED
        )
        self.assertFalse(MODEL_FIT_AUTHORIZED)
        workflow = (
            ROOT
            / ".github/workflows/"
            "phase8a-exp045-model-training.yml"
        )
        self.assertFalse(workflow.exists())

    def test_source_has_no_dispatch_or_workflow_side_effect(self) -> None:
        source = (
            ROOT
            / "src/fmp/market_learning/"
            "model_successor_training.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("workflow_dispatch", source)
        self.assertNotIn("gh workflow run", source)


if __name__ == "__main__":
    unittest.main()
