from __future__ import annotations

import math
import unittest
from datetime import datetime, timedelta, timezone

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

    def test_pip_size_rejects_unhashable_and_nonstr_symbol_types(self):
        for symbol in ([], {}, ["EURUSD"], None, True, 1, b"EURUSD"):
            with self.subTest(symbol=repr(symbol)):
                with self.assertRaisesRegex(ValueError, "unsupported symbol"):
                    pip_size(symbol)

    def test_adverse_slippage_rejects_unhashable_symbol_with_value_error(self):
        for symbol in ([], {}, ["USDJPY"]):
            with self.subTest(symbol=repr(symbol)):
                with self.assertRaisesRegex(ValueError, "unsupported symbol"):
                    apply_adverse_slippage(
                        1.2, side=OrderSide.BUY, pips=1.0, symbol=symbol,
                    )

    def test_exact_supported_symbol_lookups_keep_frozen_pip_sizes(self):
        for symbol, expected in (
            ("EURUSD", 0.0001), ("GBPUSD", 0.0001),
            ("USDJPY", 0.01),
        ):
            with self.subTest(symbol=symbol):
                self.assertEqual(pip_size(symbol), expected)
                self.assertAlmostEqual(
                    apply_adverse_slippage(
                        2.0, side=OrderSide.BUY, pips=2.0, symbol=symbol
                    ),
                    2.0 + 2.0 * expected,
                )

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

    def test_slippage_rejects_boolean_or_nonnumeric_quote_price(self):
        for price in (True, False, "1.200", None, 10 ** 400):
            with self.subTest(price=repr(price)):
                with self.assertRaisesRegex(ValueError, "price"):
                    apply_adverse_slippage(
                        price, side=OrderSide.BUY, pips=1.0,
                        symbol="EURUSD",
                    )

    def test_slippage_rejects_boolean_or_nonnumeric_pip_amount(self):
        for pips in (True, False, "1.0", None, 10 ** 400):
            with self.subTest(pips=repr(pips)):
                with self.assertRaisesRegex(ValueError, "pips|finite"):
                    apply_adverse_slippage(
                        1.2, side=OrderSide.SELL, pips=pips,
                        symbol="EURUSD",
                    )

    def test_fixed_commission_rate_rejects_boolean_or_untyped_input(self):
        for rate in (True, False, "30.0", None, 10 ** 400):
            with self.subTest(rate=repr(rate)):
                with self.assertRaisesRegex(ValueError, "commission rate"):
                    FixedCommissionPerMillion(usd_per_million_per_side=rate)

    def test_valid_int_and_float_slippage_inputs_still_adverse(self):
        for price in (1, 1.2):
            for pips in (0, 1, 1.0):
                with self.subTest(price=price, pips=pips):
                    out = apply_adverse_slippage(
                        price, side=OrderSide.BUY, pips=pips,
                        symbol="EURUSD",
                    )
                    self.assertGreaterEqual(out, price)

    def test_zero_commission_is_exact_and_serializable(self) -> None:
        model = ZeroCommission()
        self.assertEqual(model.cost_usd(units=100_000), 0.0)
        self.assertEqual(model.to_config(), {"model": "zero_commission"})

    def test_zero_commission_rejects_fractional_and_boolean_units(self):
        model = ZeroCommission()
        for units in (0.5, -1.5, 1.0, True, False):
            with self.subTest(units=repr(units)):
                with self.assertRaisesRegex(ValueError, "whole integer"):
                    model.cost_usd(units=units)

    def test_zero_commission_rejects_nonfinite_and_nonnumeric_units(self):
        model = ZeroCommission()
        for units in (None, "100000", float("nan"), float("inf")):
            with self.subTest(units=repr(units)):
                with self.assertRaisesRegex(ValueError, "whole integer"):
                    model.cost_usd(units=units)

    def test_zero_commission_remains_exact_for_signed_whole_units(self):
        model = ZeroCommission()
        for units in (0, 1, -1, 100_000, -200_000):
            with self.subTest(units=units):
                self.assertEqual(model.cost_usd(units=units), 0.0)
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

    def test_fixed_commission_rejects_huge_units_that_overflow(self):
        model = FixedCommissionPerMillion(usd_per_million_per_side=30.0)
        for units in (10 ** 400, -(10 ** 400)):
            with self.subTest(negative=units < 0):
                with self.assertRaisesRegex(ValueError, "finite"):
                    model.cost_usd(units=units)

    def test_fixed_commission_rejects_infinite_derived_cost(self):
        model = FixedCommissionPerMillion(usd_per_million_per_side=1e308)
        self.assertTrue(math.isfinite(model.cost_usd(units=1_000_000)))
        for units in (2_000_000, -2_000_000, 10 ** 320):
            with self.subTest(units=units):
                with self.assertRaisesRegex(ValueError, "finite"):
                    model.cost_usd(units=units)

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


    def test_zero_financing_rejects_bad_symbol_and_direction(self):
        model = ZeroFinancing()
        entry = datetime(2026, 9, 14, 20, tzinfo=timezone.utc)
        exit_ = datetime(2026, 9, 15, 8, tzinfo=timezone.utc)
        for symbol in ("AUDUSD", "eurusd", None):
            with self.subTest(symbol=symbol):
                with self.assertRaisesRegex(ValueError, "symbol"):
                    model.cost_usd(
                        symbol=symbol, direction=Direction.LONG, units=100,
                        entry_timestamp_utc=entry, exit_timestamp_utc=exit_,
                    )
        for direction in ("LONG", Direction.NO_TRADE, None, True):
            with self.subTest(direction=direction):
                with self.assertRaisesRegex(ValueError, "direction"):
                    model.cost_usd(
                        symbol="EURUSD", direction=direction, units=100,
                        entry_timestamp_utc=entry, exit_timestamp_utc=exit_,
                    )

    def test_zero_financing_rejects_noninteger_units(self):
        model = ZeroFinancing()
        entry = datetime(2026, 9, 14, 20, tzinfo=timezone.utc)
        for units in (True, False, 1.0, -0.5, None, "100000"):
            with self.subTest(units=repr(units)):
                with self.assertRaisesRegex(ValueError, "units"):
                    model.cost_usd(
                        symbol="EURUSD", direction=Direction.SHORT,
                        units=units, entry_timestamp_utc=entry,
                        exit_timestamp_utc=entry,
                    )

    def test_zero_financing_rejects_naive_or_non_utc_timestamps(self):
        model = ZeroFinancing()
        good = datetime(2026, 9, 14, 20, tzinfo=timezone.utc)
        bad = (
            datetime(2026, 9, 14, 20),
            datetime(2026, 9, 14, 20,
                     tzinfo=timezone(timedelta(hours=1))),
            None, "2026-09-14T20:00:00",
        )
        for invalid in bad:
            for field in ("entry_timestamp_utc", "exit_timestamp_utc"):
                with self.subTest(value=repr(invalid), field=field):
                    params = dict(
                        symbol="EURUSD", direction=Direction.LONG, units=1,
                        entry_timestamp_utc=good, exit_timestamp_utc=good,
                    )
                    params[field] = invalid
                    with self.assertRaisesRegex(ValueError, "UTC"):
                        model.cost_usd(**params)

    def test_zero_financing_rejects_exit_preceding_entry(self):
        model = ZeroFinancing()
        entry = datetime(2026, 9, 14, 20, tzinfo=timezone.utc)
        exit_ = entry - timedelta(minutes=1)
        with self.assertRaisesRegex(ValueError, "precede"):
            model.cost_usd(
                symbol="USDJPY", direction=Direction.SHORT, units=100,
                entry_timestamp_utc=entry, exit_timestamp_utc=exit_,
            )

    def test_zero_financing_still_returns_zero_for_valid_signed_positions(self):
        model = ZeroFinancing()
        when = datetime(2026, 9, 14, 20, tzinfo=timezone.utc)
        later = when + timedelta(hours=4)
        for symbol in ("EURUSD", "GBPUSD", "USDJPY"):
            for direction in (Direction.LONG, Direction.SHORT):
                for units in (-100, 0, 100):
                    with self.subTest(symbol=symbol, direction=direction,
                                      units=units):
                        self.assertEqual(
                            model.cost_usd(
                                symbol=symbol, direction=direction, units=units,
                                entry_timestamp_utc=when,
                                exit_timestamp_utc=later,
                            ), 0.0,
                        )
        self.assertEqual(model.to_config(), {"model": "zero_financing"})


if __name__ == "__main__":
    unittest.main()
