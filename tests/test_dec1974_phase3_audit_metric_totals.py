"""Source-defined tests for opt-in Phase3 stored-economic metric reconciliation."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fmp.contracts import (
    BacktestRun, Direction, ExitReason, RejectionCode, RejectionRecord, TradeRecord,
)
from fmp.reporting.backtest import (
    audit_backtest_artifact_structure,
    verify_backtest_artifacts,
    write_backtest_artifacts,
)


STAMP = datetime(2026, 10, 20, 0, 0, tzinfo=timezone.utc)


def _sample_trade() -> TradeRecord:
    return TradeRecord(
        trade_id="AUDIT-T1",
        decision_id="AUDIT-D1",
        symbol="EURUSD",
        direction=Direction.LONG,
        units=10_000,
        entry_timestamp_utc=STAMP,
        exit_timestamp_utc=STAMP + timedelta(minutes=1),
        entry_reference_price=1.1000,
        exit_reference_price=1.1010,
        entry_price=1.1000,
        exit_price=1.1010,
        stop_price=1.0990,
        target_price=1.1010,
        exit_reason=ExitReason.TARGET,
        intrabar_ambiguous=False,
        gross_pnl_usd=12.5,
        slippage_cost_usd=1.5,
        commission_cost_usd=0.5,
        financing_cost_usd=-0.5,
        net_pnl_usd=11.0,
        risk_equity_before_usd=10_000.0,
        risk_equity_after_usd=10_011.0,
    )


def _run(metrics: dict[str, object]) -> BacktestRun:
    return BacktestRun(
        run_identity={},
        trades=(_sample_trade(),),
        rejections=(),
        equity_checkpoints=(),
        metrics=metrics,
    )


def _forge_metrics(folder: Path, manifest: dict[str, object], name: str, value: object) -> None:
    path = folder / "metrics.json"
    record = json.loads(path.read_text("utf-8"))
    record[name] = value
    payload = (json.dumps(record, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(payload)
    for entry in manifest["artifacts"]:
        if entry["path"] == "metrics.json":
            entry["size_bytes"] = len(payload)
            entry["sha256"] = hashlib.sha256(payload).hexdigest()
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


class Phase3AuditLedgerMetricTotalsTests(unittest.TestCase):
    def test_audit_accepts_writer_consistent_optional_economics(self):
        metrics = {
            "trade_count": 1,
            "net_pnl_usd": 11.0,
            "slippage_cost_usd": 1.5,
            "commission_cost_usd": 0.5,
            "financing_cost_usd": -0.5,
            "total_explicit_cost_usd": 1.5,
        }
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_run(metrics), folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )

    def test_audit_refuses_rehashed_metric_net_pnl_conflicting_with_ledger(self):
        metrics = {"trade_count": 1, "net_pnl_usd": 11.0}
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_run(metrics), folder)
            _forge_metrics(folder, manifest, "net_pnl_usd", 42.0)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "metric net_pnl_usd conflicts"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_cost_subtotal_or_total(self):
        metrics = {
            "trade_count": 1,
            "slippage_cost_usd": 1.5,
            "commission_cost_usd": 0.5,
            "financing_cost_usd": -0.5,
            "total_explicit_cost_usd": 1.5,
        }
        for name in ("slippage_cost_usd", "total_explicit_cost_usd"):
            with self.subTest(field=name), tempfile.TemporaryDirectory() as home:
                folder = Path(home) / "evidence"
                manifest = write_backtest_artifacts(_run(metrics), folder)
                _forge_metrics(folder, manifest, name, 8.5)
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, "conflicts with trade ledger"):
                    audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_boolean_economics_alias(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _run({"trade_count": 1, "net_pnl_usd": 11.0}), folder
            )
            _forge_metrics(folder, manifest, "net_pnl_usd", True)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "metric net_pnl_usd must be finite"):
                audit_backtest_artifact_structure(folder)


def _run_winning_and_losing(metrics: dict[str, object]) -> BacktestRun:
    winner = _sample_trade()
    loser = replace(
        winner,
        trade_id="AUDIT-T2",
        decision_id="AUDIT-D2",
        entry_timestamp_utc=STAMP + timedelta(minutes=5),
        exit_timestamp_utc=STAMP + timedelta(minutes=6),
        gross_pnl_usd=-4.0,
        slippage_cost_usd=0.0,
        commission_cost_usd=0.0,
        financing_cost_usd=0.0,
        net_pnl_usd=-4.0,
        risk_equity_before_usd=10_011.0,
        risk_equity_after_usd=10_007.0,
    )
    return BacktestRun(
        run_identity={},
        trades=(winner, loser),
        rejections=(),
        equity_checkpoints=(),
        metrics=metrics,
    )


class Phase3AuditProfitabilityMetricTests(unittest.TestCase):
    def test_audit_accepts_valid_gross_profit_loss_factor(self):
        metrics = {
            "trade_count": 2,
            "net_pnl_usd": 7.0,
            "gross_profit_usd": 11.0,
            "gross_loss_usd": 4.0,
            "profit_factor": 2.75,
        }
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_run_winning_and_losing(metrics), folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 2,
            )

    def test_audit_accepts_null_profit_factor_without_losses(self):
        metrics = {
            "trade_count": 1,
            "gross_profit_usd": 11.0,
            "gross_loss_usd": 0.0,
            "profit_factor": None,
        }
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_run(metrics), folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )

    def test_audit_refuses_rehashed_gross_profit_or_profit_factor(self):
        metrics = {
            "trade_count": 2,
            "gross_profit_usd": 11.0,
            "gross_loss_usd": 4.0,
            "profit_factor": 2.75,
        }
        for name in ("gross_profit_usd", "profit_factor"):
            with self.subTest(metric=name), tempfile.TemporaryDirectory() as home:
                folder = Path(home) / "evidence"
                manifest = write_backtest_artifacts(
                    _run_winning_and_losing(metrics), folder
                )
                _forge_metrics(folder, manifest, name, 88.0)
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, "conflicts with trade ledger"):
                    audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_nonnull_profit_factor_without_loss(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _run({"trade_count": 1, "profit_factor": None}), folder
            )
            _forge_metrics(folder, manifest, "profit_factor", 9.0)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "metric profit_factor conflicts"):
                audit_backtest_artifact_structure(folder)


def _forge_trade_field(
    folder: Path, manifest: dict[str, object], name: str, value: object,
) -> None:
    path = folder / "trades.jsonl"
    row = json.loads(path.read_text("utf-8"))
    row[name] = value
    payload = (json.dumps(row, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(payload)
    for entry in manifest["artifacts"]:
        if entry["path"] == "trades.jsonl":
            entry["size_bytes"] = len(payload)
            entry["sha256"] = hashlib.sha256(payload).hexdigest()
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


class Phase3AuditRealizedEquityArithmeticTests(unittest.TestCase):
    def test_audit_accepts_writer_trade_realized_equity(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_run({"trade_count": 1}), folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1
            )

    def test_audit_refuses_rehashed_trade_equity_after_not_matching_net_pnl(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_run({"trade_count": 1}), folder)
            _forge_trade_field(folder, manifest, "risk_equity_after_usd", 10009.0)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "realized equity conflicts"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_boolean_equity_alias(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_run({"trade_count": 1}), folder)
            _forge_trade_field(folder, manifest, "risk_equity_before_usd", True)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "risk_equity_before_usd.*numeric"):
                audit_backtest_artifact_structure(folder)


def _forge_jsonl_order(
    folder: Path, manifest: dict[str, object], name: str,
) -> None:
    target = folder / name
    rows = target.read_text("utf-8").splitlines()
    assert len(rows) >= 2
    payload = ("\n".join(reversed(rows)) + "\n").encode("utf-8")
    target.write_bytes(payload)
    for entry in manifest["artifacts"]:
        if entry["path"] == name:
            entry["size_bytes"] = len(payload)
            entry["sha256"] = hashlib.sha256(payload).hexdigest()
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


class Phase3AuditCanonicalJSONLOrderTests(unittest.TestCase):
    def test_audit_refuses_rehashed_reverse_exit_trade_order(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _run_winning_and_losing({"trade_count": 2}), folder
            )
            _forge_jsonl_order(folder, manifest, "trades.jsonl")
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "canonical exit order"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_reverse_rejection_evaluation_order(self):
        first = RejectionRecord(
            decision_id="R1",
            symbol="EURUSD",
            decision_timestamp_utc=STAMP,
            evaluated_timestamp_utc=STAMP,
            code=RejectionCode.NO_TRADE,
            explanation="synthetic",
        )
        second = RejectionRecord(
            decision_id="R2",
            symbol="EURUSD",
            decision_timestamp_utc=STAMP + timedelta(minutes=1),
            evaluated_timestamp_utc=STAMP + timedelta(minutes=1),
            code=RejectionCode.NO_TRADE,
            explanation="synthetic",
        )
        run = BacktestRun(
            run_identity={}, trades=(), rejections=(first, second),
            equity_checkpoints=(), metrics={},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            _forge_jsonl_order(folder, manifest, "rejections.jsonl")
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "canonical evaluation order"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_same_exit_time_noncanonical_trade_id_tiebreak(self):
        first = _sample_trade()
        other = replace(
            first, trade_id="AUDIT-Z", decision_id="AUDIT-DZ"
        )
        run = BacktestRun(
            run_identity={}, trades=(other, first), rejections=(),
            equity_checkpoints=(), metrics={"trade_count": 2},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 2)
            _forge_jsonl_order(folder, manifest, "trades.jsonl")
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "canonical exit order"):
                audit_backtest_artifact_structure(folder)


class Phase3AuditDistributionMetricTests(unittest.TestCase):
    def test_audit_accepts_writer_win_loss_distribution(self):
        metrics = {
            "trade_count": 2,
            "win_rate": 0.5,
            "average_win_usd": 11.0,
            "average_loss_usd": -4.0,
            "expectancy_usd": 3.5,
            "longest_winning_streak": 1,
            "longest_losing_streak": 1,
        }
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_run_winning_and_losing(metrics), folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 2)

    def test_audit_refuses_rehashed_win_rate_or_expectancy(self):
        metrics = {
            "trade_count": 2,
            "win_rate": 0.5,
            "expectancy_usd": 3.5,
        }
        for name, forged in (("win_rate", 0.9), ("expectancy_usd", 9.0)):
            with self.subTest(field=name), tempfile.TemporaryDirectory() as home:
                folder = Path(home) / "evidence"
                manifest = write_backtest_artifacts(
                    _run_winning_and_losing(metrics), folder
                )
                _forge_metrics(folder, manifest, name, forged)
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, "conflicts with trade ledger"):
                    audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_winning_streak_and_boolean_alias(self):
        metrics = {
            "trade_count": 2,
            "longest_winning_streak": 1,
        }
        for forged in (2, True):
            with self.subTest(forged=forged), tempfile.TemporaryDirectory() as home:
                folder = Path(home) / "evidence"
                manifest = write_backtest_artifacts(
                    _run_winning_and_losing(metrics), folder
                )
                _forge_metrics(folder, manifest, "longest_winning_streak", forged)
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, "conflicts with trade ledger"):
                    audit_backtest_artifact_structure(folder)

    def test_audit_accepts_empty_trade_null_win_rate_and_expectancy(self):
        run = BacktestRun(
            run_identity={}, trades=(), rejections=(),
            equity_checkpoints=(),
            metrics={
                "trade_count": 0,
                "win_rate": None,
                "expectancy_usd": None,
                "longest_winning_streak": 0,
                "longest_losing_streak": 0,
            },
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 0)


class Phase3AuditStoredTradeContractTests(unittest.TestCase):
    def test_audit_refuses_rehashed_unsupported_fx_symbol_or_direction(self):
        for field, value in (("symbol", "BTCUSD"), ("direction", "NO_TRADE")):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as home:
                folder = Path(home) / "evidence"
                manifest = write_backtest_artifacts(_run({"trade_count": 1}), folder)
                _forge_trade_field(folder, manifest, field, value)
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, "trade (symbol|direction) is unsupported"):
                    audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_boolean_or_zero_trade_units(self):
        for units in (True, 0):
            with self.subTest(units=units), tempfile.TemporaryDirectory() as home:
                folder = Path(home) / "evidence"
                manifest = write_backtest_artifacts(_run({"trade_count": 1}), folder)
                _forge_trade_field(folder, manifest, "units", units)
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, "trade units must be positive"):
                    audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_negative_or_boolean_price(self):
        for price in (-1.0, False):
            with self.subTest(price=price), tempfile.TemporaryDirectory() as home:
                folder = Path(home) / "evidence"
                manifest = write_backtest_artifacts(_run({"trade_count": 1}), folder)
                _forge_trade_field(folder, manifest, "entry_price", price)
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, "entry_price must be finite positive"):
                    audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_exit_reason_or_intrabar_ambiguity(self):
        for field, value in (
            ("exit_reason", "UNKNOWN"),
            ("intrabar_ambiguous", "false"),
        ):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as home:
                folder = Path(home) / "evidence"
                manifest = write_backtest_artifacts(_run({"trade_count": 1}), folder)
                _forge_trade_field(folder, manifest, field, value)
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, "trade (exit reason|ambiguity)"):
                    audit_backtest_artifact_structure(folder)


if __name__ == "__main__":
    unittest.main()
