"""DEC-1855: deterministic synthetic cost diagnostic cannot approve trading."""
import contextlib
import io
import json
import unittest
from pathlib import Path
import runpy
from unittest import mock

from fmp.backtest.costs import (
    FixedCommissionPerMillion, apply_adverse_slippage, pip_size,
)
from fmp.contracts import OrderSide

ROOT = Path(__file__).resolve().parents[1]
MOD = runpy.run_path(
    str(ROOT / "scripts" / "dec1855_synthetic_cost_boundary_diagnostic.py")
)
BUILD = MOD["inspect_synthetic_cost_boundaries"]


class SyntheticCostBoundaryDiagnosticTests(unittest.TestCase):
    def test_exact_enum_side_moves_worsen_fill_in_both_directions(self):
        result = BUILD()
        self.assertTrue(result["enum_buy_moves_up"])
        self.assertTrue(result["enum_sell_moves_down"])
        self.assertEqual(result["symbol"], "EURUSD")
        self.assertEqual(result["synthetic_pips"], 1.0)

    def test_current_untyped_side_and_fractional_units_exposure_is_visible(self):
        result = BUILD()
        self.assertIs(result["untyped_buy_string_interpreted_as_sell"], True)
        self.assertIs(result["fractional_commission_units_currently_accepted"], True)
        self.assertTrue(result["known_issues_require_separate_backtester_review"])

    def test_diagnostic_is_blocked_and_cannot_be_trading_evidence(self):
        result = BUILD()
        self.assertEqual(result["disposition"],
                         "BLOCKED_NO_STRATEGY_OR_TRADING_PERMISSION")
        self.assertEqual(result["source_material"], "constants_only_no_market_data")
        self.assertFalse(result["economic_expectancy_or_profitable_strategy_verified"])
        self.assertFalse(result["protected_2023_run385_attempt1_authorized"])
        self.assertFalse(result["broker_demo_live_or_real_money_authorized"])
        self.assertEqual(result["allowed_actions"], [])

    def test_synthetic_adverse_slippage_monotone_on_each_supported_fx_pair(self):
        for symbol, reference in (
            ("EURUSD", 1.20), ("GBPUSD", 1.35), ("USDJPY", 150.00)
        ):
            with self.subTest(symbol=symbol):
                buys, sells = [], []
                for pips in (0.0, 0.25, 0.5, 1.0, 3.0):
                    bought = apply_adverse_slippage(
                        reference, side=OrderSide.BUY, pips=pips, symbol=symbol)
                    sold = apply_adverse_slippage(
                        reference, side=OrderSide.SELL, pips=pips, symbol=symbol)
                    self.assertGreaterEqual(bought, reference)
                    self.assertLessEqual(sold, reference)
                    self.assertAlmostEqual(
                        bought - reference, pips * pip_size(symbol), places=9)
                    self.assertAlmostEqual(
                        reference - sold, pips * pip_size(symbol), places=9)
                    buys.append(bought)
                    sells.append(sold)
                self.assertEqual(buys, sorted(buys))
                self.assertEqual(sells, sorted(sells, reverse=True))

    def test_synthetic_commission_symmetry_and_monotone_size(self):
        for rate in (0.0, 10.0, 30.0):
            with self.subTest(rate=rate):
                cost = FixedCommissionPerMillion(
                    usd_per_million_per_side=rate)
                measurements = [
                    cost.cost_usd(units=n)
                    for n in (0, 100_000, 200_000, 1_000_000)
                ]
                self.assertEqual(measurements, sorted(measurements))
                self.assertEqual(measurements[0], 0.0)
                for units in (100_000, 200_000, 1_000_000):
                    self.assertAlmostEqual(
                        cost.cost_usd(units=units),
                        cost.cost_usd(units=-units),
                    )

    def test_synthetic_invalid_slippage_magnitudes_reject(self):
        for pips in (-1.0, float("nan"), float("inf")):
            with self.subTest(pips=repr(pips)):
                with self.assertRaises(ValueError):
                    apply_adverse_slippage(
                        1.20, side=OrderSide.BUY, pips=pips, symbol="EURUSD")
        with self.assertRaisesRegex(ValueError, "slipped price"):
            apply_adverse_slippage(
                1.20, side=OrderSide.SELL, pips=20_000.0, symbol="EURUSD")

    def test_synthetic_matrix_is_not_a_return_or_strategy_claim(self):
        report = BUILD()
        self.assertEqual(
            report["disposition"], "BLOCKED_NO_STRATEGY_OR_TRADING_PERMISSION")
        self.assertEqual(report["source_material"], "constants_only_no_market_data")
        self.assertFalse(report["economic_expectancy_or_profitable_strategy_verified"])
        self.assertFalse(report["broker_demo_live_or_real_money_authorized"])
        self.assertEqual(report["allowed_actions"], [])

    def test_synthetic_cli_exits_nonzero_and_does_not_use_network_or_process(self):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch("subprocess.Popen",
                        side_effect=AssertionError("unexpected subprocess")):
            with mock.patch("socket.socket",
                            side_effect=AssertionError("unexpected network")):
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    status = MOD["main"]([])
        self.assertEqual(status, 3)
        self.assertEqual(err.getvalue(), "")
        self.assertEqual(json.loads(out.getvalue())["allowed_actions"], [])


if __name__ == "__main__":
    unittest.main()
