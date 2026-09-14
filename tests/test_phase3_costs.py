from __future__ import annotations

import math
import unittest
from datetime import datetime, timezone

from fmp.backtest import BACKTEST_ENGINE_VERSION
from fmp.backtest.costs import (
    FixedCommissionPerMillion,
    ZeroCommission,
    ZeroFinancing,
    apply_adverse_slippage,
    pip_size,
)
from fmp.contracts import Direction, OrderSide


class Phase3CostTests(unittest.TestCase):
    def test_backtest_engine_version_is_frozen(self) -> None:
        self.assertEqual(BACKTEST_ENGINE_VERSION, "fmp-backtest-v1")

    def test_pip_sizes_cover_both_price_conventions(self) -> None:
        self.assertEqual(pip_size("EURUSD"), 0.0001)
        self.assertEqual(pip_size("GBPUSD"), 0.0001)
        self.assertEqual(pip_size("USDJPY"), 0.01)

    def test_pip_size_rejects_unsupported_symbol(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported symbol"):
            pip_size("AUDUSD")

    def test_adverse_slippage_moves_buy_up(self) -> None:
        self.assertAlmostEqual(
            apply_adverse_slippage(
                1.1000,
                side=OrderSide.BUY,
                pips=1.5,
                symbol="EURUSD",
            ),
            1.10015,
        )

    def test_adverse_slippage_moves_sell_down_for_jpy(self) -> None:
        self.assertAlmostEqual(
            apply_adverse_slippage(
                150.00,
                side=OrderSide.SELL,
                pips=2.0,
                symbol="USDJPY",
            ),
            149.98,
        )

    def test_adverse_slippage_rejects_negative_pips(self) -> None:
        with self.assertRaisesRegex(ValueError, "slippage"):
            apply_adverse_slippage(
                1.1000,
                side=OrderSide.BUY,
                pips=-0.1,
                symbol="EURUSD",
            )

    def test_adverse_slippage_rejects_non_finite_price(self) -> None:
        with self.assertRaisesRegex(ValueError, "price"):
            apply_adverse_slippage(
                math.inf,
                side=OrderSide.BUY,
                pips=1.0,
                symbol="EURUSD",
            )

    def test_zero_commission_is_exact_and_serializable(self) -> None:
        model = ZeroCommission()
        self.assertEqual(model.cost_usd(units=100_000), 0.0)
        self.assertEqual(model.to_config(), {"model": "zero_commission"})

    def test_fixed_commission_is_per_million_per_execution_side(self) -> None:
        model = FixedCommissionPerMillion(usd_per_million_per_side=30.0)
        self.assertAlmostEqual(model.cost_usd(units=100_000), 3.0)
        self.assertEqual(
            model.to_config(),
            {
                "model": "fixed_per_million_per_side",
                "usd_per_million_per_side": 30.0,
            },
        )

    def test_fixed_commission_uses_absolute_units(self) -> None:
        model = FixedCommissionPerMillion(usd_per_million_per_side=25.0)
        self.assertAlmostEqual(model.cost_usd(units=-200_000), 5.0)

    def test_fixed_commission_rejects_negative_or_non_finite_rate(self) -> None:
        with self.assertRaisesRegex(ValueError, "commission"):
            FixedCommissionPerMillion(usd_per_million_per_side=-1.0)
        with self.assertRaisesRegex(ValueError, "commission"):
            FixedCommissionPerMillion(usd_per_million_per_side=math.inf)

    def test_zero_financing_is_exact_and_serializable(self) -> None:
        model = ZeroFinancing()
        cost = model.cost_usd(
            symbol="EURUSD",
            direction=Direction.LONG,
            units=100_000,
            entry_timestamp_utc=datetime(2026, 9, 14, 20, 0, tzinfo=timezone.utc),
            exit_timestamp_utc=datetime(2026, 9, 15, 8, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(cost, 0.0)
        self.assertEqual(model.to_config(), {"model": "zero_financing"})


if __name__ == "__main__":
    unittest.main()
