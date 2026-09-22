from collections import Counter
import json
import unittest

from fmp.portfolio import StrategyLifecycle
from fmp.portfolio.challenger_discovery import (
    EXP015_ID,
    EXP015_STRATEGY_VERSION,
    build_exp015_challengers,
)
from fmp.portfolio.historical_inventory import build_phase4_baseline_inventory
from fmp.strategies.mean_reversion import MeanReversionConfig, duration_to_bars
from fmp.strategies.previous_day_rejection import PreviousDayRejectionConfig
from fmp.strategies.session_breakout import SessionBreakoutConfig
from fmp.strategies.session_sweep_rejection import SessionSweepRejectionConfig
from fmp.strategies.trend_continuation import TrendContinuationConfig
from fmp.strategies.volatility_breakout import VolatilityBreakoutConfig


COMMIT = "a" * 40


class Phase8AExp015CatalogTests(unittest.TestCase):
    def test_catalog_contains_exactly_567_new_predeclared_challengers(self) -> None:
        records = build_exp015_challengers(code_commit=COMMIT)

        self.assertEqual(len(records), 567)
        self.assertEqual(len({item.strategy.fingerprint for item in records}), 567)
        self.assertTrue(
            all(item.lifecycle is StrategyLifecycle.CHALLENGER for item in records)
        )
        self.assertTrue(
            all(item.evidence_id == f"{EXP015_ID}:PREDECLARED" for item in records)
        )
        self.assertTrue(
            all(item.strategy.version == EXP015_STRATEGY_VERSION for item in records)
        )

        by_family = Counter(item.strategy.family for item in records)
        self.assertEqual(
            by_family,
            {
                "session_breakout": 180,
                "trend_continuation": 108,
                "mean_reversion": 144,
                "previous_day_rejection": 45,
                "volatility_breakout": 45,
                "session_sweep_rejection": 45,
            },
        )
        by_cell = Counter(
            (item.strategy.symbol, item.strategy.timeframe)
            for item in records
        )
        self.assertEqual(set(by_cell.values()), {63})
        self.assertEqual(len(by_cell), 9)

    def test_exp015_parameter_grid_does_not_overlap_phase4_grid(self) -> None:
        old = {
            (
                item.strategy.family,
                item.strategy.symbol,
                item.strategy.timeframe,
                item.strategy.parameters_json,
            )
            for item in build_phase4_baseline_inventory()
        }
        new = {
            (
                item.strategy.family,
                item.strategy.symbol,
                item.strategy.timeframe,
                item.strategy.parameters_json,
            )
            for item in build_exp015_challengers(code_commit=COMMIT)
        }
        self.assertTrue(old.isdisjoint(new))

    def test_catalog_uses_exact_frozen_parameter_regions(self) -> None:
        records = build_exp015_challengers(code_commit=COMMIT)
        grids: dict[str, set[tuple[tuple[str, object], ...]]] = {}
        for item in records:
            if item.strategy.symbol != "EURUSD" or item.strategy.timeframe != "15m":
                continue
            grids.setdefault(item.strategy.family, set()).add(
                tuple(sorted(json.loads(item.strategy.parameters_json).items()))
            )

        self.assertEqual(
            grids["session_breakout"],
            {
                (("buffer_pips", b), ("target_range_multiple", t))
                for b in (1, 3, 4, 6, 8)
                for t in (0.75, 1.25, 1.75, 2.0)
            },
        )
        self.assertEqual(
            grids["trend_continuation"],
            {
                (("target_r_multiple", t), ("trend_window_id", w))
                for w in ("A", "B", "C")
                for t in (0.75, 1.25, 1.75, 2.0)
            },
        )
        self.assertEqual(
            grids["mean_reversion"],
            {
                (("lookback_hours", h), ("threshold_sigma", s))
                for h in (2, 6, 12, 24)
                for s in (1.25, 1.75, 2.25, 2.5)
            },
        )
        single = {(1,), (3,), (4,), (6,), (8,)}
        for family in ("previous_day_rejection", "session_sweep_rejection"):
            self.assertEqual(
                {tuple(value for _, value in row) for row in grids[family]},
                single,
            )
        self.assertEqual(
            {
                tuple(value for _, value in row)
                for row in grids["volatility_breakout"]
            },
            {(0.75,), (1.25,), (1.75,), (2.25,), (2.5,)},
        )

    def test_strategy_validators_accept_old_and_exp015_values_but_reject_unlisted_values(self) -> None:
        SessionBreakoutConfig(1, 0.75, "15m", parameter_region="exp015")
        SessionBreakoutConfig(5, 1.5, "15m")
        TrendContinuationConfig("A", 0.75, "15m", parameter_region="exp015")
        TrendContinuationConfig("C", 1.5, "15m")
        MeanReversionConfig(2, 1.25, "15m", parameter_region="exp015")
        MeanReversionConfig(16, 2.0, "15m")
        PreviousDayRejectionConfig(8, "15m", parameter_region="exp015")
        PreviousDayRejectionConfig(5, "15m")
        VolatilityBreakoutConfig(2.25, "15m", parameter_region="exp015")
        VolatilityBreakoutConfig(2.0, "15m")
        SessionSweepRejectionConfig(6, "15m", parameter_region="exp015")
        SessionSweepRejectionConfig(2, "15m")
        self.assertEqual(duration_to_bars("15m", 24, parameter_region="exp015"), 96)


        # New EXP-015 values remain invalid under the default Phase 4 region.
        with self.assertRaises(ValueError):
            SessionBreakoutConfig(1, 0.75, "15m")
        with self.assertRaises(ValueError):
            MeanReversionConfig(24, 2.25, "15m")
        with self.assertRaises(ValueError):
            SessionBreakoutConfig(7, 0.75, "15m", parameter_region="exp015")
        with self.assertRaises(ValueError):
            TrendContinuationConfig("A", 2.5, "15m", parameter_region="exp015")
        with self.assertRaises(ValueError):
            MeanReversionConfig(10, 1.25, "15m", parameter_region="exp015")
        with self.assertRaises(ValueError):
            PreviousDayRejectionConfig(7, "15m", parameter_region="exp015")
        with self.assertRaises(ValueError):
            VolatilityBreakoutConfig(3.0, "15m", parameter_region="exp015")
        with self.assertRaises(ValueError):
            SessionSweepRejectionConfig(7, "15m", parameter_region="exp015")

    def test_catalog_rejects_invalid_code_commit(self) -> None:
        with self.assertRaises(ValueError):
            build_exp015_challengers(code_commit="not-a-sha")


if __name__ == "__main__":
    unittest.main()
