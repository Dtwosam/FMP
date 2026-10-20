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

    def test_adverse_slippage_rejects_string_buy_instead_of_treating_as_sell(self):
        with self.assertRaisesRegex(ValueError, "side"):
            apply_adverse_slippage(
                1.2000, side="BUY", pips=1.0, symbol="EURUSD"
            )

    def test_adverse_slippage_rejects_non_enum_side_variants(self):
        for side in ("SELL", None, True, 0, Direction.LONG, Direction.SHORT):
            with self.subTest(side=repr(side)):
                with self.assertRaisesRegex(ValueError, "side"):
                    apply_adverse_slippage(
                        1.2000, side=side, pips=1.0, symbol="EURUSD"
                    )

    def test_adverse_slippage_rejects_bad_side_even_with_zero_pips(self):
        for side in ("BUY", "SELL", None):
            with self.subTest(side=repr(side)):
                with self.assertRaisesRegex(ValueError, "side"):
                    apply_adverse_slippage(
                        1.2000, side=side, pips=0.0, symbol="EURUSD"
                    )

    def test_slippage_enum_side_still_adverse_for_all_supported_pairs(self):
        for symbol, price in (("EURUSD", 1.2), ("GBPUSD", 1.35),
                              ("USDJPY", 150.0)):
            with self.subTest(symbol=symbol):
                buy = apply_adverse_slippage(
                    price, side=OrderSide.BUY, pips=1.0, symbol=symbol)
                sell = apply_adverse_slippage(
                    price, side=OrderSide.SELL, pips=1.0, symbol=symbol)
                self.assertGreater(buy, price)
                self.assertLess(sell, price)

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

    def test_fixed_commission_rejects_fractional_units(self):
        model = FixedCommissionPerMillion(usd_per_million_per_side=30.0)
        for units in (0.5, -0.5, 1.0, 100_000.5, -100_000.25):
            with self.subTest(units=units):
                with self.assertRaisesRegex(ValueError, "whole integer"):
                    model.cost_usd(units=units)

    def test_fixed_commission_rejects_boolean_or_nonnumeric_units(self):
        model = FixedCommissionPerMillion(usd_per_million_per_side=30.0)
        for units in (True, False, None, "100000", float("nan"), float("inf")):
            with self.subTest(units=repr(units)):
                with self.assertRaisesRegex(ValueError, "whole integer"):
                    model.cost_usd(units=units)

    def test_fixed_commission_retains_signed_integer_symmetry(self):
        model = FixedCommissionPerMillion(usd_per_million_per_side=30.0)
        for units, expected in ((0, 0.0), (1, 0.00003), (-1, 0.00003),
                                (100_000, 3.0), (-200_000, 6.0)):
            with self.subTest(units=units):
                self.assertAlmostEqual(model.cost_usd(units=units), expected)

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
