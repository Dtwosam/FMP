import unittest

from fmp.portfolio import StrategyLifecycle
from fmp.portfolio.research_batch import (
    PHASE8A_BATCH_PROTOCOL,
    select_historical_inventory,
)


class Phase8ARetrospectiveBatchTests(unittest.TestCase):
    def test_each_pair_timeframe_cell_contains_the_exact_30_historical_configs(self) -> None:
        rows = select_historical_inventory(symbol="EURUSD", timeframe="15m")
        self.assertEqual(len(rows), 30)
        counts = {}
        for row in rows:
            counts[row.strategy.family] = counts.get(row.strategy.family, 0) + 1
        self.assertEqual(
            counts,
            {
                "mean_reversion": 6,
                "previous_day_rejection": 3,
                "session_breakout": 9,
                "session_sweep_rejection": 3,
                "trend_continuation": 6,
                "volatility_breakout": 3,
            },
        )
        self.assertEqual(PHASE8A_BATCH_PROTOCOL, "fmp-phase8a-retrospective-batch-v1")

    def test_family_filter_is_exact_and_deterministic(self) -> None:
        first = select_historical_inventory(
            symbol="GBPUSD",
            timeframe="5m",
            families=("volatility_breakout", "session_breakout"),
        )
        second = select_historical_inventory(
            symbol="GBPUSD",
            timeframe="5m",
            families=("session_breakout", "volatility_breakout"),
        )
        self.assertEqual(
            tuple(item.strategy.fingerprint for item in first),
            tuple(item.strategy.fingerprint for item in second),
        )
        self.assertEqual(len(first), 12)
        self.assertEqual(
            {item.strategy.family for item in first},
            {"session_breakout", "volatility_breakout"},
        )

    def test_old_rejections_are_not_reclassified_by_batch_selection(self) -> None:
        eurusd = select_historical_inventory(symbol="EURUSD", timeframe="1h")
        self.assertTrue(eurusd)
        self.assertTrue(
            all(item.lifecycle is StrategyLifecycle.RETIRED for item in eurusd)
        )

        usdjpy_15m = select_historical_inventory(symbol="USDJPY", timeframe="15m")
        qualified = [
            item
            for item in usdjpy_15m
            if item.lifecycle is StrategyLifecycle.HISTORICAL_QUALIFIED
        ]
        self.assertEqual(len(qualified), 1)
        self.assertEqual(
            qualified[0].strategy.parameters_json,
            '{"buffer_pips":5,"target_range_multiple":1.5}',
        )

    def test_invalid_pair_timeframe_or_family_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            select_historical_inventory(symbol="AUDUSD", timeframe="15m")
        with self.assertRaises(ValueError):
            select_historical_inventory(symbol="EURUSD", timeframe="4h")
        with self.assertRaises(ValueError):
            select_historical_inventory(
                symbol="EURUSD",
                timeframe="15m",
                families=("invented_after_results",),
            )


if __name__ == "__main__":
    unittest.main()
