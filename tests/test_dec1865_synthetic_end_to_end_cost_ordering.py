"""DEC-1865: invented bars only; higher costs may never inflate net P&L."""
from __future__ import annotations

import unittest
from unittest import mock
from datetime import datetime, timedelta, timezone

from fmp.backtest.costs import FixedCommissionPerMillion, ZeroCommission, ZeroFinancing
from fmp.backtest.engine import BacktestConfig, run_backtest
from fmp.contracts import Decision, Direction, ExitReason, QuoteBar
from fmp.risk import RiskConfig

DAY = datetime(2026, 9, 14, tzinfo=timezone.utc)


def synthetic_bars():
    rows = []
    for minute in range(3):
        rows.append(QuoteBar(
            timestamp_utc=DAY + timedelta(minutes=minute),
            symbol="EURUSD",
            bid_open=1.1000,
            bid_high=1.1008,
            bid_low=1.0995,
            bid_close=1.1006 if minute == 2 else 1.1003,
            ask_open=1.1002,
            ask_high=1.1010,
            ask_low=1.0997,
            ask_close=1.1008 if minute == 2 else 1.1005,
        ))
    return rows


def synthetic_trade(*, slippage_pips=0.0, commission_rate=None):
    commission = (
        ZeroCommission()
        if commission_rate is None
        else FixedCommissionPerMillion(
            usd_per_million_per_side=commission_rate)
    )
    config = BacktestConfig(
        starting_equity_usd=10_000.0,
        slippage_pips=slippage_pips,
        risk_config=RiskConfig(),
        commission_model=commission,
        financing_model=ZeroFinancing(),
        processed_data_manifest_id="DEC-1865-INVENTED-CONSTANTS-NOT-MARKET-DATA",
        schema_version="fmp-canonical-1m-v1",
        timeframe="1m",
        requested_start_utc=DAY,
        requested_end_utc=DAY + timedelta(days=1),
        code_commit="sourceonly-synthetic-dec1865-not-a-release",
        decision_config={"synthetic_fixture": "not_strategy_v1"},
    )
    decision = Decision(
        decision_id="SYNTHETIC-COST-ONLY",
        symbol="EURUSD",
        decision_timestamp_utc=DAY,
        direction=Direction.LONG,
        earliest_executable_timestamp_utc=DAY + timedelta(minutes=1),
        requested_risk_fraction=None,
        stop_price=1.0900,
        target_price=None,
    )
    run = run_backtest(bars=synthetic_bars(), decisions=[decision], config=config)
    if len(run.trades) != 1:
        raise AssertionError("synthetic cost contract requires exactly one closed trade")
    return run, run.trades[0]


class SyntheticIntegratedCostOrderingTests(unittest.TestCase):
    def test_synthetic_engine_cannot_open_sockets_or_launch_subprocesses(self):
        with mock.patch("subprocess.Popen",
                        side_effect=AssertionError("network/process denied")):
            with mock.patch("socket.socket",
                            side_effect=AssertionError("network/process denied")):
                run, trade = synthetic_trade(
                    slippage_pips=0.5, commission_rate=30.0
                )
        self.assertEqual(len(run.trades), 1)
        self.assertGreaterEqual(trade.commission_cost_usd, 0.0)

    def test_synthetic_engine_never_opens_real_or_protected_data_files(self):
        with mock.patch("builtins.open",
                        side_effect=AssertionError("filesystem denied")):
            with mock.patch("os.open",
                            side_effect=AssertionError("filesystem denied")):
                run, trade = synthetic_trade(
                    slippage_pips=1.0, commission_rate=120.0
                )
        self.assertEqual(len(run.trades), 1)
        self.assertEqual(
            trade.decision_id, "SYNTHETIC-COST-ONLY"
        )

    def test_synthetic_engine_manifest_explicitly_excludes_market_data(self):
        for slippage in (0.0, 0.5, 1.0):
            with self.subTest(slippage=slippage):
                run, _ = synthetic_trade(
                    slippage_pips=slippage, commission_rate=30.0
                )
                identity = str(run.run_identity)
                self.assertIn(
                    "DEC-1865-INVENTED-CONSTANTS-NOT-MARKET-DATA", identity
                )
                self.assertIn("not_strategy_v1", identity)
                self.assertNotIn("run385", identity)
                self.assertNotIn("broker_order", identity)

    def test_more_commission_never_improves_synthetic_net_trade(self):
        trades = [
            synthetic_trade(slippage_pips=0.0, commission_rate=rate)[1]
            for rate in (0.0, 30.0, 120.0)
        ]
        self.assertTrue(all(t.exit_reason is ExitReason.END_OF_DATA for t in trades))
        self.assertEqual(
            [t.commission_cost_usd for t in trades],
            sorted(t.commission_cost_usd for t in trades),
        )
        self.assertEqual(
            [t.net_pnl_usd for t in trades],
            sorted((t.net_pnl_usd for t in trades), reverse=True),
        )
        self.assertGreater(trades[2].commission_cost_usd,
                           trades[0].commission_cost_usd)
        self.assertLess(trades[2].net_pnl_usd, trades[0].net_pnl_usd)

    def test_more_adverse_slippage_never_improves_synthetic_net_trade(self):
        trades = [
            synthetic_trade(slippage_pips=pips, commission_rate=30.0)[1]
            for pips in (0.0, 0.5, 1.0)
        ]
        self.assertEqual(
            [t.entry_price for t in trades],
            sorted(t.entry_price for t in trades),
        )
        self.assertEqual(
            [t.exit_price for t in trades],
            sorted((t.exit_price for t in trades), reverse=True),
        )
        self.assertEqual(
            [t.net_pnl_usd for t in trades],
            sorted((t.net_pnl_usd for t in trades), reverse=True),
        )

    def test_invented_backtest_is_deterministic_and_not_real_market_evidence(self):
        first, trade = synthetic_trade(slippage_pips=1.0, commission_rate=30.0)
        second, _ = synthetic_trade(slippage_pips=1.0, commission_rate=30.0)
        self.assertEqual(first.trades, second.trades)
        self.assertEqual(first.rejections, second.rejections)
        self.assertEqual(len(first.trades), 1)
        self.assertIn("DEC-1865-INVENTED-CONSTANTS-NOT-MARKET-DATA",
                      str(first.run_identity))
        self.assertEqual(trade.exit_timestamp_utc, DAY + timedelta(minutes=2))
        self.assertGreaterEqual(trade.commission_cost_usd, 0.0)
        self.assertGreaterEqual(trade.slippage_cost_usd, 0.0)
    def test_every_synthetic_trade_net_equals_gross_less_all_costs(self):
        for pips, rate in ((0.0, 0.0), (0.5, 30.0),
                           (1.0, 120.0)):
            with self.subTest(pips=pips, rate=rate):
                run, trade = synthetic_trade(
                    slippage_pips=pips, commission_rate=rate)
                net = (trade.gross_pnl_usd - trade.slippage_cost_usd
                       - trade.commission_cost_usd
                       - trade.financing_cost_usd)
                self.assertAlmostEqual(trade.net_pnl_usd, net, places=8)
                self.assertEqual(trade.financing_cost_usd, 0.0)
                self.assertEqual(len(run.trades), 1)

    def test_large_synthetic_commission_changes_gross_win_to_net_loss(self):
        _, without_fees = synthetic_trade(
            slippage_pips=0.0, commission_rate=0.0)
        _, expensive = synthetic_trade(
            slippage_pips=0.0, commission_rate=100_000.0)
        self.assertGreater(without_fees.gross_pnl_usd, 0.0)
        self.assertGreater(expensive.gross_pnl_usd, 0.0)
        self.assertLess(expensive.net_pnl_usd, 0.0)
        self.assertGreater(expensive.commission_cost_usd,
                           expensive.gross_pnl_usd)
        self.assertGreater(without_fees.net_pnl_usd,
                           expensive.net_pnl_usd)

    def test_synthetic_realized_equity_uses_net_not_gross_pnl(self):
        for rate in (0.0, 30.0, 100_000.0):
            with self.subTest(commission_rate=rate):
                run, trade = synthetic_trade(
                    slippage_pips=0.0, commission_rate=rate)
                self.assertAlmostEqual(
                    trade.risk_equity_after_usd,
                    trade.risk_equity_before_usd + trade.net_pnl_usd,
                    places=8)
                self.assertAlmostEqual(
                    run.equity_checkpoints[-1].realized_risk_equity_usd,
                    trade.risk_equity_after_usd, places=8)


if __name__ == "__main__":
    unittest.main()
