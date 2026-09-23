from datetime import datetime, timezone
from pathlib import Path
import unittest

from fmp.features.schema import FEATURE_VALUE_COLUMNS
from fmp.market_learning.model_protocol import (
    CONFIDENCE_THRESHOLDS,
    FIT_SPLIT,
    HIST_GRADIENT_BOOSTING_CONFIG,
    LOGISTIC_REGRESSION_CONFIG,
    MODEL_CELLS,
    MODEL_FAMILIES,
    MODEL_FIT_AUTHORIZED,
    MODEL_INPUT_COLUMNS,
    MODEL_PROTOCOL_RESULT_AUTHORIZED,
    PROMOTION_AUTHORIZED,
    PROTOCOL_SPLITS,
    REAL_MONEY_AUTHORIZED,
    RETROSPECTIVE_HOLDOUT_SPLIT,
    SCIKIT_LEARN_VERSION,
    SELECTION_SPLIT,
    TARGET_CLASSES,
    TARGET_COLUMN,
    TARGET_SLIPPAGE_PIPS,
    VALIDATION_SPLIT,
    directional_candidate,
    protocol_fingerprint,
    protocol_payload,
    split_accepts_observation,
)


ROOT = Path(__file__).resolve().parents[1]


class Exp044ModelProtocolTests(unittest.TestCase):
    def test_protocol_freezes_exact_eighteen_direct_market_cells(self) -> None:
        self.assertEqual(len(MODEL_CELLS), 18)
        self.assertEqual(
            {
                (cell.symbol, cell.timeframe, cell.horizon_minutes)
                for cell in MODEL_CELLS
            },
            {
                (symbol, timeframe, horizon)
                for symbol in ("EURUSD", "GBPUSD", "USDJPY")
                for timeframe in ("5m", "15m", "1h")
                for horizon in (60, 240)
            },
        )

    def test_protocol_uses_exact_frozen_feature_values_and_direct_target(self) -> None:
        self.assertEqual(MODEL_INPUT_COLUMNS, FEATURE_VALUE_COLUMNS)
        self.assertEqual(len(MODEL_INPUT_COLUMNS), 48)
        self.assertEqual(TARGET_COLUMN, "best_direction_0p5")
        self.assertEqual(TARGET_SLIPPAGE_PIPS, 0.5)
        self.assertEqual(TARGET_CLASSES, ("LONG", "SHORT", "NO_TRADE"))

    def test_protocol_freezes_chronology_and_boundary_purge(self) -> None:
        self.assertEqual(
            [(split.name, split.start.isoformat(), split.end_exclusive.isoformat())
             for split in PROTOCOL_SPLITS],
            [
                ("fit", "2015-01-01", "2021-01-01"),
                ("selection", "2021-01-01", "2023-01-01"),
                ("validation", "2023-01-01", "2025-01-01"),
                ("retrospective_holdout", "2025-01-01", "2026-08-21"),
            ],
        )
        self.assertEqual(FIT_SPLIT.end_exclusive, SELECTION_SPLIT.start)
        self.assertEqual(SELECTION_SPLIT.end_exclusive, VALIDATION_SPLIT.start)
        self.assertEqual(
            VALIDATION_SPLIT.end_exclusive,
            RETROSPECTIVE_HOLDOUT_SPLIT.start,
        )

        self.assertTrue(
            split_accepts_observation(
                FIT_SPLIT,
                available_at_utc=datetime(
                    2020, 12, 31, 18, 0, tzinfo=timezone.utc
                ),
                exit_timestamp_utc=datetime(
                    2020, 12, 31, 22, 0, tzinfo=timezone.utc
                ),
            )
        )
        self.assertFalse(
            split_accepts_observation(
                FIT_SPLIT,
                available_at_utc=datetime(
                    2020, 12, 31, 23, 0, tzinfo=timezone.utc
                ),
                exit_timestamp_utc=datetime(
                    2021, 1, 1, 3, 0, tzinfo=timezone.utc
                ),
            )
        )

    def test_model_families_and_configs_are_exact_and_no_search_exists(self) -> None:
        self.assertEqual(
            MODEL_FAMILIES,
            ("logistic_regression", "hist_gradient_boosting"),
        )
        self.assertEqual(SCIKIT_LEARN_VERSION, "1.9.1")
        self.assertEqual(
            dict(LOGISTIC_REGRESSION_CONFIG),
            {
                "penalty": "l2",
                "C": 1.0,
                "solver": "lbfgs",
                "tol": 1e-8,
                "fit_intercept": True,
                "class_weight": None,
                "max_iter": 2000,
                "warm_start": False,
            },
        )
        self.assertEqual(HIST_GRADIENT_BOOSTING_CONFIG["early_stopping"], False)
        self.assertEqual(HIST_GRADIENT_BOOSTING_CONFIG["random_state"], 20260923)
        self.assertEqual(CONFIDENCE_THRESHOLDS, (0.50, 0.60, 0.70))

    def test_directional_candidate_is_conservative_and_deterministic(self) -> None:
        self.assertEqual(
            directional_candidate(
                {"LONG": 0.65, "SHORT": 0.15, "NO_TRADE": 0.20},
                threshold=0.60,
            ),
            "LONG",
        )
        self.assertEqual(
            directional_candidate(
                {"LONG": 0.10, "SHORT": 0.70, "NO_TRADE": 0.20},
                threshold=0.70,
            ),
            "SHORT",
        )
        self.assertEqual(
            directional_candidate(
                {"LONG": 0.55, "SHORT": 0.10, "NO_TRADE": 0.35},
                threshold=0.60,
            ),
            "NO_TRADE",
        )
        self.assertEqual(
            directional_candidate(
                {"LONG": 0.45, "SHORT": 0.45, "NO_TRADE": 0.10},
                threshold=0.50,
            ),
            "NO_TRADE",
        )
        self.assertEqual(
            directional_candidate(
                {"LONG": 0.40, "SHORT": 0.20, "NO_TRADE": 0.40},
                threshold=0.50,
            ),
            "NO_TRADE",
        )

    def test_protocol_payload_keeps_all_result_and_trading_locks_false(self) -> None:
        payload = protocol_payload()
        self.assertIs(MODEL_PROTOCOL_RESULT_AUTHORIZED, False)
        self.assertIs(MODEL_FIT_AUTHORIZED, False)
        self.assertIs(PROMOTION_AUTHORIZED, False)
        self.assertIs(REAL_MONEY_AUTHORIZED, False)
        self.assertIs(payload["model_protocol_result_authorized"], False)
        self.assertIs(payload["model_fit_authorized"], False)
        self.assertIs(payload["promotion_authorized"], False)
        self.assertIs(payload["shadow_authorized"], False)
        self.assertIs(payload["demo_order_authorized"], False)
        self.assertIs(payload["broker_mutation_authorized"], False)
        self.assertIs(payload["live_order_authorized"], False)
        self.assertIs(payload["real_money_authorized"], False)
        self.assertIs(payload["no_refit_after_fit"], True)
        self.assertEqual(len(protocol_fingerprint()), 64)
        self.assertEqual(protocol_fingerprint(), protocol_fingerprint())

    def test_dec088_documents_source_only_protocol_and_next_gate(self) -> None:
        decision = (ROOT / "docs/decision-log.md").read_text(encoding="utf-8")
        spec = (
            ROOT
            / "docs/superpowers/specs/"
            "2026-09-23-phase8a-exp044-model-training-protocol.md"
        ).read_text(encoding="utf-8")
        state = (ROOT / "docs/project-state.md").read_text(encoding="utf-8")

        self.assertIn(
            "## DEC-088 — Phase 8A EXP-044 predeclared model-training protocol",
            decision,
        )
        self.assertIn("result-producing fit remains locked", decision)
        self.assertIn("best_direction_0p5", spec)
        self.assertIn("exactly 18 model cells", spec)
        self.assertIn("There is no refit after the fit split.", spec)
        self.assertIn("model_fit_authorized", spec)
        self.assertIn("RESULT RUN STILL LOCKED", spec)
        self.assertIn("EXP-044 V1 CLOSED", state)


if __name__ == "__main__":
    unittest.main()
