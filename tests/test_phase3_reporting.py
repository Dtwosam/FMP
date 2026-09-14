from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fmp.contracts import (
    BacktestRun,
    Direction,
    EquityCheckpoint,
    ExitReason,
    RejectionCode,
    RejectionRecord,
    TradeRecord,
)
from fmp.reporting.backtest import compute_backtest_metrics, write_backtest_artifacts


BASE_TS = datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc)


def trade(
    *,
    trade_id: str,
    minutes: int,
    net_pnl_usd: float,
    slippage_cost_usd: float = 0.0,
    commission_cost_usd: float = 0.0,
    financing_cost_usd: float = 0.0,
) -> TradeRecord:
    before = 10_000.0
    return TradeRecord(
        trade_id=trade_id,
        decision_id=f"D-{trade_id}",
        symbol="EURUSD",
        direction=Direction.LONG,
        units=10_000,
        entry_timestamp_utc=BASE_TS + timedelta(minutes=minutes),
        exit_timestamp_utc=BASE_TS + timedelta(minutes=minutes + 1),
        entry_reference_price=1.1000,
        exit_reference_price=1.1010,
        entry_price=1.1000,
        exit_price=1.1010,
        stop_price=1.0990,
        target_price=1.1010,
        exit_reason=ExitReason.TARGET if net_pnl_usd >= 0 else ExitReason.STOP,
        intrabar_ambiguous=False,
        gross_pnl_usd=net_pnl_usd
        + slippage_cost_usd
        + commission_cost_usd
        + financing_cost_usd,
        slippage_cost_usd=slippage_cost_usd,
        commission_cost_usd=commission_cost_usd,
        financing_cost_usd=financing_cost_usd,
        net_pnl_usd=net_pnl_usd,
        risk_equity_before_usd=before,
        risk_equity_after_usd=before + net_pnl_usd,
    )


class Phase3ReportingTests(unittest.TestCase):
    def test_metrics_match_hand_calculated_trade_sequence(self) -> None:
        trades = (
            trade(trade_id="T-1", minutes=1, net_pnl_usd=100.0, slippage_cost_usd=1.0),
            trade(trade_id="T-2", minutes=3, net_pnl_usd=-50.0, commission_cost_usd=2.0),
            trade(trade_id="T-3", minutes=5, net_pnl_usd=25.0, financing_cost_usd=3.0),
            trade(trade_id="T-4", minutes=7, net_pnl_usd=-25.0),
        )
        checkpoints = (
            EquityCheckpoint(BASE_TS, 10_000.0),
            EquityCheckpoint(BASE_TS + timedelta(minutes=2), 10_100.0),
            EquityCheckpoint(BASE_TS + timedelta(minutes=4), 10_050.0),
            EquityCheckpoint(BASE_TS + timedelta(minutes=6), 10_075.0),
            EquityCheckpoint(BASE_TS + timedelta(minutes=8), 10_050.0),
        )
        metrics = compute_backtest_metrics(
            starting_equity_usd=10_000.0,
            trades=trades,
            equity_checkpoints=checkpoints,
        )
        self.assertEqual(metrics["net_pnl_usd"], 50.0)
        self.assertEqual(metrics["net_return"], 0.005)
        self.assertEqual(metrics["trade_count"], 4)
        self.assertEqual(metrics["win_rate"], 0.5)
        self.assertEqual(metrics["average_win_usd"], 62.5)
        self.assertEqual(metrics["average_loss_usd"], -37.5)
        self.assertEqual(metrics["expectancy_usd"], 12.5)
        self.assertEqual(metrics["gross_profit_usd"], 125.0)
        self.assertEqual(metrics["gross_loss_usd"], 75.0)
        self.assertAlmostEqual(metrics["profit_factor"], 125.0 / 75.0)
        self.assertEqual(metrics["max_drawdown_usd"], 50.0)
        self.assertAlmostEqual(metrics["max_drawdown_fraction"], 50.0 / 10_100.0)
        self.assertEqual(metrics["recovery_factor"], 1.0)
        self.assertEqual(metrics["longest_winning_streak"], 1)
        self.assertEqual(metrics["longest_losing_streak"], 1)
        self.assertEqual(metrics["slippage_cost_usd"], 1.0)
        self.assertEqual(metrics["commission_cost_usd"], 2.0)
        self.assertEqual(metrics["financing_cost_usd"], 3.0)
        self.assertEqual(metrics["total_explicit_cost_usd"], 6.0)

    def test_zero_trade_metrics_are_explicit(self) -> None:
        metrics = compute_backtest_metrics(
            starting_equity_usd=10_000.0,
            trades=(),
            equity_checkpoints=(EquityCheckpoint(BASE_TS, 10_000.0),),
        )
        self.assertEqual(metrics["net_pnl_usd"], 0.0)
        self.assertEqual(metrics["net_return"], 0.0)
        self.assertEqual(metrics["trade_count"], 0)
        self.assertIsNone(metrics["expectancy_usd"])
        self.assertIsNone(metrics["win_rate"])
        self.assertIsNone(metrics["average_win_usd"])
        self.assertIsNone(metrics["average_loss_usd"])
        self.assertIsNone(metrics["profit_factor"])
        self.assertIsNone(metrics["recovery_factor"])

    def test_realized_equity_drawdown_uses_previous_peak(self) -> None:
        metrics = compute_backtest_metrics(
            starting_equity_usd=1_000.0,
            trades=(),
            equity_checkpoints=(
                EquityCheckpoint(BASE_TS, 1_000.0),
                EquityCheckpoint(BASE_TS + timedelta(minutes=1), 1_100.0),
                EquityCheckpoint(BASE_TS + timedelta(minutes=2), 990.0),
            ),
        )
        self.assertEqual(metrics["max_drawdown_usd"], 110.0)
        self.assertEqual(metrics["max_drawdown_fraction"], 0.1)

    def test_artifact_bytes_and_digests_are_deterministic(self) -> None:
        one_trade = trade(trade_id="T-1", minutes=1, net_pnl_usd=10.0)
        rejection = RejectionRecord(
            decision_id="D-NO",
            symbol="EURUSD",
            decision_timestamp_utc=BASE_TS,
            evaluated_timestamp_utc=BASE_TS + timedelta(minutes=1),
            code=RejectionCode.NO_TRADE,
            explanation="fixture says no trade",
        )
        checkpoints = (
            EquityCheckpoint(BASE_TS, 10_000.0),
            EquityCheckpoint(BASE_TS + timedelta(minutes=2), 10_010.0),
        )
        metrics = compute_backtest_metrics(
            starting_equity_usd=10_000.0,
            trades=(one_trade,),
            equity_checkpoints=checkpoints,
        )
        run = BacktestRun(
            run_identity={
                "backtest_engine_version": "fmp-backtest-v1",
                "code_commit": "abc123",
                "processed_data_manifest_id": "manifest-sha",
                "requested_start_utc": BASE_TS,
                "requested_end_utc": BASE_TS + timedelta(minutes=2),
            },
            trades=(one_trade,),
            rejections=(rejection,),
            equity_checkpoints=checkpoints,
            metrics=metrics,
        )

        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first = Path(first_dir)
            second = Path(second_dir)
            first_manifest = write_backtest_artifacts(run, first)
            second_manifest = write_backtest_artifacts(run, second)

            expected_names = {
                "summary.json",
                "trades.jsonl",
                "rejections.jsonl",
                "metrics.json",
                "manifest.json",
            }
            self.assertEqual({path.name for path in first.iterdir()}, expected_names)
            self.assertEqual({path.name for path in second.iterdir()}, expected_names)

            for name in sorted(expected_names):
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())

            self.assertEqual(first_manifest, second_manifest)
            self.assertEqual(first_manifest["protocol"], "fmp-phase3-backtest-artifacts-v1")
            artifacts = first_manifest["artifacts"]
            self.assertEqual(
                {item["path"] for item in artifacts},
                {"summary.json", "trades.jsonl", "rejections.jsonl", "metrics.json"},
            )
            for item in artifacts:
                data = (first / item["path"]).read_bytes()
                self.assertEqual(item["size_bytes"], len(data))
                self.assertEqual(item["sha256"], hashlib.sha256(data).hexdigest())

            loaded = json.loads((first / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(loaded, first_manifest)
            self.assertTrue((first / "summary.json").read_bytes().endswith(b"\n"))


if __name__ == "__main__":
    unittest.main()
