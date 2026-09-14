from __future__ import annotations

import hashlib
import json
import math
import tempfile
import unittest
from datetime import date, datetime, timezone
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
from fmp.research.reporting import compute_research_metrics, write_benchmark_artifacts


def trade(
    decision_id: str,
    *,
    symbol: str,
    exit_time: datetime,
    pnl: float,
    equity_before: float,
    exit_reason: ExitReason = ExitReason.TARGET,
) -> TradeRecord:
    return TradeRecord(
        trade_id=decision_id,
        decision_id=decision_id,
        symbol=symbol,
        direction=Direction.LONG,
        units=10_000,
        entry_timestamp_utc=exit_time.replace(hour=8),
        exit_timestamp_utc=exit_time,
        entry_reference_price=1.1000,
        exit_reference_price=1.1010,
        entry_price=1.1000,
        exit_price=1.1010,
        stop_price=1.0950,
        target_price=1.1010,
        exit_reason=exit_reason,
        intrabar_ambiguous=False,
        gross_pnl_usd=pnl,
        slippage_cost_usd=0.0,
        commission_cost_usd=0.0,
        financing_cost_usd=0.0,
        net_pnl_usd=pnl,
        risk_equity_before_usd=equity_before,
        risk_equity_after_usd=equity_before + pnl,
    )


class Phase4ResearchReportingTests(unittest.TestCase):
    def sample_run(self) -> BacktestRun:
        trades = (
            trade(
                "D1",
                symbol="EURUSD",
                exit_time=datetime(2020, 12, 30, 16, tzinfo=timezone.utc),
                pnl=100.0,
                equity_before=10_000.0,
            ),
            trade(
                "D2",
                symbol="EURUSD",
                exit_time=datetime(2020, 12, 31, 16, tzinfo=timezone.utc),
                pnl=-50.0,
                equity_before=10_100.0,
                exit_reason=ExitReason.TIME_EXIT,
            ),
            trade(
                "D3",
                symbol="EURUSD",
                exit_time=datetime(2021, 1, 4, 16, tzinfo=timezone.utc),
                pnl=-25.0,
                equity_before=10_050.0,
                exit_reason=ExitReason.STOP,
            ),
        )
        rejections = (
            RejectionRecord(
                decision_id="NT",
                symbol="EURUSD",
                decision_timestamp_utc=datetime(2020, 12, 31, 11, tzinfo=timezone.utc),
                evaluated_timestamp_utc=datetime(2020, 12, 31, 11, tzinfo=timezone.utc),
                code=RejectionCode.NO_TRADE,
                explanation="NO_BREAKOUT",
            ),
            RejectionRecord(
                decision_id="RISK",
                symbol="EURUSD",
                decision_timestamp_utc=datetime(2021, 1, 4, 8, tzinfo=timezone.utc),
                evaluated_timestamp_utc=datetime(2021, 1, 4, 9, tzinfo=timezone.utc),
                code=RejectionCode.INVALID_STOP_TARGET,
                explanation="gap invalidated target geometry",
            ),
        )
        checkpoints = (
            EquityCheckpoint(datetime(2020, 12, 30, 0, tzinfo=timezone.utc), 10_000.0),
            EquityCheckpoint(datetime(2020, 12, 30, 16, tzinfo=timezone.utc), 10_100.0),
            EquityCheckpoint(datetime(2020, 12, 31, 16, tzinfo=timezone.utc), 10_050.0),
            EquityCheckpoint(datetime(2021, 1, 4, 16, tzinfo=timezone.utc), 10_025.0),
        )
        return BacktestRun(
            run_identity={"timeframe": "15m", "starting_equity_usd": 10_000.0},
            trades=trades,
            rejections=rejections,
            equity_checkpoints=checkpoints,
            metrics={
                "net_pnl_usd": 25.0,
                "net_return": 0.0025,
                "trade_count": 3,
                "expectancy_usd": 25.0 / 3.0,
                "profit_factor": 2.0,
            },
        )

    def test_hand_calculated_reward_risk_daily_returns_and_breakdowns(self) -> None:
        run = self.sample_run()
        metadata = {
            "D1": {"session_date": "2020-12-30", "session_name": "london"},
            "D2": {"session_date": "2020-12-31", "session_name": "london"},
            "D3": {"session_date": "2021-01-04", "session_name": "london"},
        }
        eligible = (
            date(2020, 12, 30),
            date(2020, 12, 31),
            date(2021, 1, 1),
            date(2021, 1, 4),
        )
        metrics = compute_research_metrics(
            run,
            starting_equity_usd=10_000.0,
            requested_risk_fraction=0.0025,
            candidate_metadata=metadata,
            eligible_utc_dates=eligible,
        )

        self.assertEqual(metrics["phase3_metrics"], dict(run.metrics))
        self.assertEqual(metrics["trade_count"], 3)
        self.assertEqual(metrics["rejection_count"], 2)
        self.assertEqual(metrics["no_trade_count"], 1)
        self.assertEqual(metrics["time_exit_count"], 1)
        self.assertEqual(metrics["rejection_reason_counts"], {"INVALID_STOP_TARGET": 1, "NO_TRADE": 1})

        reward_risk = metrics["reward_risk_values"]
        assert isinstance(reward_risk, list)
        self.assertAlmostEqual(reward_risk[0], 100.0 / 25.0)
        self.assertAlmostEqual(reward_risk[1], -50.0 / (10_100.0 * 0.0025))
        self.assertAlmostEqual(reward_risk[2], -25.0 / (10_050.0 * 0.0025))

        daily = metrics["daily_realized_returns"]
        assert isinstance(daily, list)
        expected = [
            100.0 / 10_000.0,
            -50.0 / 10_100.0,
            0.0,
            -25.0 / 10_050.0,
        ]
        self.assertEqual([row["date"] for row in daily], [d.isoformat() for d in eligible])
        for row, expected_return in zip(daily, expected, strict=True):
            self.assertAlmostEqual(row["return"], expected_return)

        self.assertEqual(metrics["calendar_year_breakdown"]["2020"]["trade_count"], 2)
        self.assertAlmostEqual(metrics["calendar_year_breakdown"]["2020"]["net_pnl_usd"], 50.0)
        self.assertEqual(metrics["calendar_year_breakdown"]["2021"]["trade_count"], 1)
        self.assertEqual(metrics["pair_breakdown"]["EURUSD"]["trade_count"], 3)
        self.assertEqual(metrics["timeframe_breakdown"]["15m"]["trade_count"], 3)
        self.assertEqual(metrics["session_breakdown"]["london"]["trade_count"], 3)
        self.assertIsNotNone(metrics["sharpe"])
        self.assertIsNotNone(metrics["sortino"])

    def test_sharpe_and_sortino_null_rules_are_explicit(self) -> None:
        run = BacktestRun(
            run_identity={"timeframe": "1h"},
            trades=(),
            rejections=(),
            equity_checkpoints=(
                EquityCheckpoint(datetime(2020, 1, 2, tzinfo=timezone.utc), 10_000.0),
            ),
            metrics={"trade_count": 0, "net_pnl_usd": 0.0},
        )
        metrics = compute_research_metrics(
            run,
            starting_equity_usd=10_000.0,
            requested_risk_fraction=0.0025,
            candidate_metadata={},
            eligible_utc_dates=(date(2020, 1, 2), date(2020, 1, 3)),
        )
        self.assertIsNone(metrics["sharpe"])
        self.assertIsNone(metrics["sortino"])
        self.assertEqual([item["return"] for item in metrics["daily_realized_returns"]], [0.0, 0.0])

    def test_benchmark_artifacts_are_byte_deterministic_and_manifested(self) -> None:
        result = {
            "protocol": "fmp-phase4-session-breakout-benchmark-v1",
            "experiment_id": "EXP-20260914-001",
            "metrics": {"net_pnl_usd": 25.0, "sharpe": None},
            "cost_sensitivity": [
                {"slippage_pips": 0.2, "net_pnl_usd": 25.0},
                {"slippage_pips": 0.5, "net_pnl_usd": 10.0},
            ],
        }
        with tempfile.TemporaryDirectory() as first_tmp, tempfile.TemporaryDirectory() as second_tmp:
            first = Path(first_tmp)
            second = Path(second_tmp)
            manifest_a = write_benchmark_artifacts(result, first)
            manifest_b = write_benchmark_artifacts(result, second)
            self.assertEqual(manifest_a, manifest_b)
            self.assertEqual((first / "benchmark.json").read_bytes(), (second / "benchmark.json").read_bytes())
            self.assertEqual((first / "manifest.json").read_bytes(), (second / "manifest.json").read_bytes())

            benchmark_bytes = (first / "benchmark.json").read_bytes()
            record = manifest_a["artifacts"][0]
            self.assertEqual(record["path"], "benchmark.json")
            self.assertEqual(record["size_bytes"], len(benchmark_bytes))
            self.assertEqual(record["sha256"], hashlib.sha256(benchmark_bytes).hexdigest())
            parsed = json.loads(benchmark_bytes)
            self.assertIsNone(parsed["metrics"]["sharpe"])
            self.assertTrue(benchmark_bytes.endswith(b"\n"))


if __name__ == "__main__":
    unittest.main()
