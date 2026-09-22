import unittest
from collections import Counter

from fmp.portfolio import StrategyLifecycle
from fmp.portfolio.historical_inventory import build_phase4_baseline_inventory


class Phase8AHistoricalInventoryTests(unittest.TestCase):
    def test_inventory_contains_every_phase4_pair_timeframe_configuration_once(self) -> None:
        inventory = build_phase4_baseline_inventory()

        self.assertEqual(len(inventory), 270)
        self.assertEqual(len({item.strategy.fingerprint for item in inventory}), 270)
        self.assertEqual(
            Counter(item.strategy.symbol for item in inventory),
            {"EURUSD": 90, "GBPUSD": 90, "USDJPY": 90},
        )
        self.assertEqual(
            Counter(item.strategy.family for item in inventory),
            {
                "session_breakout": 81,
                "trend_continuation": 54,
                "mean_reversion": 54,
                "previous_day_rejection": 27,
                "volatility_breakout": 27,
                "session_sweep_rejection": 27,
            },
        )

    def test_only_phase7_survivor_remains_historically_qualified(self) -> None:
        inventory = build_phase4_baseline_inventory()
        qualified = [
            item
            for item in inventory
            if item.lifecycle is StrategyLifecycle.HISTORICAL_QUALIFIED
        ]

        self.assertEqual(len(qualified), 1)
        survivor = qualified[0]
        self.assertEqual(survivor.strategy.family, "session_breakout")
        self.assertEqual(survivor.strategy.symbol, "USDJPY")
        self.assertEqual(survivor.strategy.timeframe, "15m")
        self.assertEqual(
            survivor.strategy.parameters_json,
            '{"buffer_pips":5,"target_range_multiple":1.5}',
        )
        self.assertEqual(survivor.evidence_id, "EXP-20260915-008:PHASE7_PROMOTE_TO_SHADOW_DESIGN")

    def test_all_non_survivors_are_retired_and_none_is_shadow_eligible(self) -> None:
        inventory = build_phase4_baseline_inventory()
        states = Counter(item.lifecycle for item in inventory)

        self.assertEqual(states[StrategyLifecycle.HISTORICAL_QUALIFIED], 1)
        self.assertEqual(states[StrategyLifecycle.RETIRED], 269)
        self.assertEqual(states[StrategyLifecycle.SHADOW_CANDIDATE], 0)
        self.assertEqual(states[StrategyLifecycle.SHADOW_VALIDATED], 0)
        self.assertEqual(states[StrategyLifecycle.DEMO_ELIGIBLE], 0)

    def test_previous_volatility_candidate_is_retired_by_phase7_stage1(self) -> None:
        inventory = build_phase4_baseline_inventory()
        matched = [
            item
            for item in inventory
            if item.strategy.family == "volatility_breakout"
            and item.strategy.symbol == "USDJPY"
            and item.strategy.timeframe == "1h"
            and item.strategy.parameters_json == '{"range_multiplier":2.0}'
        ]
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched[0].lifecycle, StrategyLifecycle.RETIRED)
        self.assertEqual(
            matched[0].evidence_id,
            "EXP-20260915-008:STAGE1_REJECT",
        )


if __name__ == "__main__":
    unittest.main()
