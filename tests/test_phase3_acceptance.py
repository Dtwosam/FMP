from __future__ import annotations

import json
import math
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fmp.backtest.costs import FixedCommissionPerMillion, ZeroCommission, ZeroFinancing
from fmp.backtest.engine import BacktestConfig, run_backtest
from fmp.contracts import Decision, Direction, ExitReason, QuoteBar, RejectionCode
from fmp.reporting.backtest import write_backtest_artifacts
from fmp.risk import RiskConfig


DAY = datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc)


def quote(
    minute: int,
    *,
    symbol: str = "EURUSD",
    bid_open: float = 1.1000,
    bid_high: float = 1.1008,
    bid_low: float = 1.0995,
    bid_close: float = 1.1003,
    ask_open: float = 1.1002,
    ask_high: float = 1.1010,
    ask_low: float = 1.0997,
    ask_close: float = 1.1005,
    day: datetime = DAY,
) -> QuoteBar:
    return QuoteBar(
        timestamp_utc=day + timedelta(minutes=minute),
        symbol=symbol,
        bid_open=bid_open,
        bid_high=bid_high,
        bid_low=bid_low,
        bid_close=bid_close,
        ask_open=ask_open,
        ask_high=ask_high,
        ask_low=ask_low,
        ask_close=ask_close,
    )


def decision(
    decision_id: str,
    *,
    symbol: str = "EURUSD",
    direction: Direction = Direction.LONG,
    decision_minute: int = 0,
    executable_minute: int = 1,
    stop_price: float = 1.0992,
    target_price: float | None = None,
    requested_risk_fraction: float | None = None,
    day: datetime = DAY,
) -> Decision:
    return Decision(
        decision_id=decision_id,
        symbol=symbol,
        decision_timestamp_utc=day + timedelta(minutes=decision_minute),
        direction=direction,
        earliest_executable_timestamp_utc=day + timedelta(minutes=executable_minute),
        requested_risk_fraction=requested_risk_fraction,
        stop_price=stop_price,
        target_price=target_price,
    )


def config(
    *,
    slippage_pips: float = 0.0,
    commission_model: ZeroCommission | FixedCommissionPerMillion | None = None,
) -> BacktestConfig:
    return BacktestConfig(
        starting_equity_usd=10_000.0,
        slippage_pips=slippage_pips,
        risk_config=RiskConfig(),
        commission_model=commission_model or ZeroCommission(),
        financing_model=ZeroFinancing(),
        processed_data_manifest_id="phase2-frozen-manifest",
        schema_version="fmp-canonical-1m-v1",
        timeframe="1m",
        requested_start_utc=DAY,
        requested_end_utc=DAY + timedelta(days=1),
        code_commit="phase3-golden-fixture",
        decision_config={"fixture": "phase3-golden-v1"},
    )


class Phase3GoldenAcceptanceTests(unittest.TestCase):
    def test_long_ask_entry_bid_target_exit_matches_hand_calculation(self) -> None:
        bars = [
            quote(0),
            quote(1),
            quote(
                2,
                bid_open=1.1005,
                bid_high=1.1012,
                bid_low=1.1002,
                bid_close=1.1010,
                ask_open=1.1007,
                ask_high=1.1014,
                ask_low=1.1004,
                ask_close=1.1012,
            ),
        ]
        run = run_backtest(
            bars=bars,
            decisions=[decision("LONG", stop_price=1.0992, target_price=1.1010)],
            config=config(),
        )
        self.assertEqual(len(run.trades), 1)
        trade = run.trades[0]
        self.assertEqual(trade.units, 25_000)
        self.assertEqual(trade.entry_reference_price, 1.1002)
        self.assertEqual(trade.exit_reference_price, 1.1010)
        self.assertEqual(trade.entry_timestamp_utc, DAY + timedelta(minutes=1))
        self.assertEqual(trade.exit_timestamp_utc, DAY + timedelta(minutes=2))
        self.assertEqual(trade.exit_reason, ExitReason.TARGET)
        self.assertAlmostEqual(trade.gross_pnl_usd, 20.0)
        self.assertAlmostEqual(trade.net_pnl_usd, 20.0)
        self.assertAlmostEqual(trade.risk_equity_after_usd, 10_020.0)

    def test_short_bid_entry_ask_target_exit_matches_hand_calculation(self) -> None:
        bars = [
            quote(0),
            quote(1),
            quote(
                2,
                bid_open=1.0994,
                bid_high=1.0998,
                bid_low=1.0986,
                bid_close=1.0990,
                ask_open=1.0996,
                ask_high=1.1000,
                ask_low=1.0988,
                ask_close=1.0992,
            ),
        ]
        run = run_backtest(
            bars=bars,
            decisions=[
                decision(
                    "SHORT",
                    direction=Direction.SHORT,
                    stop_price=1.1010,
                    target_price=1.0990,
                )
            ],
            config=config(),
        )
        trade = run.trades[0]
        self.assertEqual(trade.units, 25_000)
        self.assertEqual(trade.entry_reference_price, 1.1000)
        self.assertEqual(trade.exit_reference_price, 1.0990)
        self.assertEqual(trade.exit_reason, ExitReason.TARGET)
        self.assertAlmostEqual(trade.gross_pnl_usd, 25.0)
        self.assertAlmostEqual(trade.net_pnl_usd, 25.0)

    def test_ambiguity_stop_gap_and_target_gap_are_conservative(self) -> None:
        ambiguous = run_backtest(
            bars=[
                quote(0),
                quote(1),
                quote(
                    2,
                    bid_open=1.1000,
                    bid_high=1.1025,
                    bid_low=1.0988,
                    bid_close=1.1000,
                    ask_open=1.1002,
                    ask_high=1.1027,
                    ask_low=1.0990,
                    ask_close=1.1002,
                ),
            ],
            decisions=[decision("AMB", stop_price=1.0992, target_price=1.1020)],
            config=config(),
        ).trades[0]
        self.assertEqual(ambiguous.exit_reason, ExitReason.STOP)
        self.assertTrue(ambiguous.intrabar_ambiguous)
        self.assertEqual(ambiguous.exit_reference_price, 1.0992)

        gap_stop = run_backtest(
            bars=[
                quote(0),
                quote(1),
                quote(
                    2,
                    bid_open=1.0985,
                    bid_high=1.0995,
                    bid_low=1.0980,
                    bid_close=1.0990,
                    ask_open=1.0987,
                    ask_high=1.0997,
                    ask_low=1.0982,
                    ask_close=1.0992,
                ),
            ],
            decisions=[decision("GAP-STOP", stop_price=1.0992, target_price=1.1020)],
            config=config(),
        ).trades[0]
        self.assertEqual(gap_stop.exit_reason, ExitReason.STOP)
        self.assertEqual(gap_stop.exit_reference_price, 1.0985)

        target_gap = run_backtest(
            bars=[
                quote(0),
                quote(1),
                quote(
                    2,
                    bid_open=1.1030,
                    bid_high=1.1035,
                    bid_low=1.1025,
                    bid_close=1.1032,
                    ask_open=1.1032,
                    ask_high=1.1037,
                    ask_low=1.1027,
                    ask_close=1.1034,
                ),
            ],
            decisions=[decision("GAP-TARGET", stop_price=1.0992, target_price=1.1020)],
            config=config(),
        ).trades[0]
        self.assertEqual(target_gap.exit_reason, ExitReason.TARGET)
        self.assertEqual(target_gap.exit_reference_price, 1.1020)

    def test_usdjpy_sizing_and_realized_pnl_use_frozen_conversion_rules(self) -> None:
        bars = [
            quote(
                0,
                symbol="USDJPY",
                bid_open=150.00,
                bid_high=150.08,
                bid_low=149.95,
                bid_close=150.03,
                ask_open=150.02,
                ask_high=150.10,
                ask_low=149.97,
                ask_close=150.05,
            ),
            quote(
                1,
                symbol="USDJPY",
                bid_open=150.00,
                bid_high=150.08,
                bid_low=149.95,
                bid_close=150.03,
                ask_open=150.02,
                ask_high=150.10,
                ask_low=149.97,
                ask_close=150.05,
            ),
            quote(
                2,
                symbol="USDJPY",
                bid_open=150.10,
                bid_high=150.16,
                bid_low=150.05,
                bid_close=150.12,
                ask_open=150.12,
                ask_high=150.18,
                ask_low=150.07,
                ask_close=150.14,
            ),
        ]
        run = run_backtest(
            bars=bars,
            decisions=[
                decision(
                    "JPY",
                    symbol="USDJPY",
                    stop_price=149.92,
                    target_price=None,
                )
            ],
            config=config(),
        )
        trade = run.trades[0]
        expected_units = math.floor(25.0 / (abs(150.02 - 149.92) / 149.92))
        expected_pnl = (150.12 - 150.02) * expected_units / 150.12
        self.assertEqual(trade.units, expected_units)
        self.assertEqual(trade.exit_reason, ExitReason.END_OF_DATA)
        self.assertAlmostEqual(trade.gross_pnl_usd, expected_pnl)
        self.assertAlmostEqual(trade.net_pnl_usd, expected_pnl)

    def test_slippage_and_commission_are_subtracted_exactly_once(self) -> None:
        bars = [
            quote(0),
            quote(1),
            quote(
                2,
                bid_open=1.1008,
                bid_high=1.1014,
                bid_low=1.1005,
                bid_close=1.1012,
                ask_open=1.1010,
                ask_high=1.1016,
                ask_low=1.1007,
                ask_close=1.1014,
            ),
        ]
        run = run_backtest(
            bars=bars,
            decisions=[decision("COST", stop_price=1.0992, target_price=1.1012)],
            config=config(
                slippage_pips=1.0,
                commission_model=FixedCommissionPerMillion(30.0),
            ),
        )
        trade = run.trades[0]
        self.assertEqual(trade.units, 25_000)
        self.assertAlmostEqual(trade.entry_reference_price, 1.1002)
        self.assertAlmostEqual(trade.entry_price, 1.1003)
        self.assertAlmostEqual(trade.exit_reference_price, 1.1012)
        self.assertAlmostEqual(trade.exit_price, 1.1011)
        self.assertAlmostEqual(trade.gross_pnl_usd, 25.0)
        self.assertAlmostEqual(trade.slippage_cost_usd, 5.0)
        self.assertAlmostEqual(trade.commission_cost_usd, 1.5)
        self.assertEqual(trade.financing_cost_usd, 0.0)
        self.assertAlmostEqual(trade.net_pnl_usd, 18.5)
        self.assertAlmostEqual(run.metrics["total_explicit_cost_usd"], 6.5)

    def test_per_trade_and_simultaneous_risk_rejections_are_preserved(self) -> None:
        per_trade = run_backtest(
            bars=[quote(0), quote(1)],
            decisions=[
                decision(
                    "TOO-MUCH",
                    requested_risk_fraction=0.006,
                    stop_price=1.0992,
                )
            ],
            config=config(),
        )
        self.assertEqual(per_trade.rejections[0].code, RejectionCode.PER_TRADE_RISK)

        bars = [
            quote(0),
            quote(1),
            quote(
                1,
                symbol="GBPUSD",
                bid_open=1.3000,
                bid_high=1.3010,
                bid_low=1.2995,
                bid_close=1.3004,
                ask_open=1.3002,
                ask_high=1.3012,
                ask_low=1.2997,
                ask_close=1.3006,
            ),
            quote(
                1,
                symbol="USDJPY",
                bid_open=150.00,
                bid_high=150.08,
                bid_low=149.95,
                bid_close=150.03,
                ask_open=150.02,
                ask_high=150.10,
                ask_low=149.97,
                ask_close=150.05,
            ),
        ]
        decisions = [
            decision("A", requested_risk_fraction=0.005, stop_price=1.0992),
            decision(
                "B",
                symbol="GBPUSD",
                requested_risk_fraction=0.005,
                stop_price=1.2992,
            ),
            decision(
                "C",
                symbol="USDJPY",
                requested_risk_fraction=0.005,
                stop_price=149.92,
            ),
        ]
        run = run_backtest(bars=bars, decisions=decisions, config=config())
        rejected = {item.decision_id: item.code for item in run.rejections}
        self.assertNotIn("A", rejected)
        self.assertNotIn("B", rejected)
        self.assertEqual(rejected["C"], RejectionCode.SIMULTANEOUS_RISK)

    def test_repeated_run_and_persisted_artifacts_are_byte_identical(self) -> None:
        bars = [quote(0), quote(1), quote(2, bid_close=1.1008, ask_close=1.1010)]
        decisions = [decision("DET", stop_price=1.0992, target_price=None)]
        first_run = run_backtest(bars=bars, decisions=decisions, config=config())
        second_run = run_backtest(bars=bars, decisions=decisions, config=config())
        self.assertEqual(first_run, second_run)

        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first_path = Path(first_dir)
            second_path = Path(second_dir)
            first_manifest = write_backtest_artifacts(first_run, first_path)
            second_manifest = write_backtest_artifacts(second_run, second_path)
            self.assertEqual(first_manifest, second_manifest)
            for name in (
                "summary.json",
                "trades.jsonl",
                "rejections.jsonl",
                "metrics.json",
                "manifest.json",
            ):
                self.assertEqual(
                    (first_path / name).read_bytes(),
                    (second_path / name).read_bytes(),
                )

            summary = json.loads((first_path / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(
                summary["equity_checkpoints"],
                [
                    {
                        "realized_risk_equity_usd": checkpoint.realized_risk_equity_usd,
                        "timestamp_utc": checkpoint.timestamp_utc.isoformat().replace("+00:00", "Z"),
                    }
                    for checkpoint in first_run.equity_checkpoints
                ],
            )


if __name__ == "__main__":
    unittest.main()
