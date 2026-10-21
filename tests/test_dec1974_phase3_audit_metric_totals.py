"""Source-defined tests for opt-in Phase3 stored-economic metric reconciliation."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fmp.backtest import BACKTEST_ENGINE_VERSION
from fmp.backtest.costs import apply_adverse_slippage
from fmp.risk import pnl_usd
from fmp.contracts import (
    BacktestRun, Direction, EquityCheckpoint, ExitReason, OrderSide, RejectionCode,
    RejectionRecord, TradeRecord,
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


def _forge_rejection_field(
    folder: Path, manifest: dict[str, object], name: str, value: object,
) -> None:
    path = folder / "rejections.jsonl"
    row = json.loads(path.read_text("utf-8"))
    row[name] = value
    payload = (json.dumps(row, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(payload)
    for entry in manifest["artifacts"]:
        if entry["path"] == "rejections.jsonl":
            entry["size_bytes"] = len(payload)
            entry["sha256"] = hashlib.sha256(payload).hexdigest()
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def _one_rejection_run() -> BacktestRun:
    rejection = RejectionRecord(
        decision_id="DEC-REJECT",
        symbol="EURUSD",
        decision_timestamp_utc=STAMP,
        evaluated_timestamp_utc=STAMP,
        code=RejectionCode.NO_TRADE,
        explanation="synthetic",
    )
    return BacktestRun(
        run_identity={}, trades=(), rejections=(rejection,),
        equity_checkpoints=(), metrics={"trade_count": 0},
    )


class Phase3AuditRejectionContractTests(unittest.TestCase):
    def test_audit_refuses_rehashed_unknown_rejection_symbol_or_code(self):
        for field, value in (("symbol", "BTCUSD"), ("code", "NOT_SUPPORTED")):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as home:
                folder = Path(home) / "evidence"
                manifest = write_backtest_artifacts(_one_rejection_run(), folder)
                _forge_rejection_field(folder, manifest, field, value)
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, "rejection (symbol|code) is unsupported"):
                    audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_rejection_explanation_aliases(self):
        for explanation in ("", False, "x" * 4097):
            with self.subTest(kind=type(explanation).__name__), tempfile.TemporaryDirectory() as home:
                folder = Path(home) / "evidence"
                manifest = write_backtest_artifacts(_one_rejection_run(), folder)
                _forge_rejection_field(folder, manifest, "explanation", explanation)
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, "explanation must be bounded"):
                    audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_invalid_decision_identifier(self):
        for identifier in ("", "INVALID\nID", "x" * 513):
            with self.subTest(length=len(identifier)), tempfile.TemporaryDirectory() as home:
                folder = Path(home) / "evidence"
                manifest = write_backtest_artifacts(_one_rejection_run(), folder)
                _forge_rejection_field(folder, manifest, "decision_id", identifier)
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, "decision_id must be bounded"):
                    audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_invalid_trade_identifier(self):
        for identifier in ("T\nINVALID", "x" * 513):
            with self.subTest(length=len(identifier)), tempfile.TemporaryDirectory() as home:
                folder = Path(home) / "evidence"
                manifest = write_backtest_artifacts(
                    _run({"trade_count": 1}), folder
                )
                _forge_trade_field(folder, manifest, "trade_id", identifier)
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, "trade_id must be bounded"):
                    audit_backtest_artifact_structure(folder)


def _forge_raw_metric_payload(
    folder: Path, manifest: dict[str, object], payload: bytes,
) -> None:
    path = folder / "metrics.json"
    path.write_bytes(payload)
    for entry in manifest["artifacts"]:
        if entry["path"] == "metrics.json":
            entry["size_bytes"] = len(payload)
            entry["sha256"] = hashlib.sha256(payload).hexdigest()
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


class Phase3AuditBoundedNumericJsonTests(unittest.TestCase):
    def test_audit_refuses_rehashed_exponent_float_overflow_in_optional_metric(self):
        run = BacktestRun(
            run_identity={}, trades=(), rejections=(),
            equity_checkpoints=(), metrics={"trade_count": 0},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            _forge_raw_metric_payload(
                folder, manifest, b'{"trade_count":0,"unknown_metric":1e309}\n'
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "non-finite numeric"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_oversized_integer_in_optional_metric(self):
        run = BacktestRun(
            run_identity={}, trades=(), rejections=(),
            equity_checkpoints=(), metrics={"trade_count": 0},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            payload = b'{"trade_count":0,"unknown_metric":' + b"9" * 200 + b"}\n"
            _forge_raw_metric_payload(folder, manifest, payload)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "integer exceeds safe width"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_deeply_nested_rehashed_metric_json_without_recursion_escape(self):
        run = BacktestRun(
            run_identity={}, trades=(), rejections=(),
            equity_checkpoints=(), metrics={"trade_count": 0},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            payload = b'{"trade_count":0,"unknown_metric":' + (
                b"[" * 2000 + b"0" + b"]" * 2000
            ) + b"}\n"
            _forge_raw_metric_payload(folder, manifest, payload)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "nesting limit"):
                audit_backtest_artifact_structure(folder)


def _forge_summary_checkpoint(
    folder: Path, manifest: dict[str, object], timestamp: str,
) -> None:
    path = folder / "summary.json"
    summary = json.loads(path.read_text("utf-8"))
    summary["equity_checkpoints"][0]["timestamp_utc"] = timestamp
    payload = (json.dumps(summary, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(payload)
    for entry in manifest["artifacts"]:
        if entry["path"] == "summary.json":
            entry["size_bytes"] = len(payload)
            entry["sha256"] = hashlib.sha256(payload).hexdigest()
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


class Phase3AuditCanonicalUTCStringTests(unittest.TestCase):
    def test_audit_refuses_rehashed_space_separated_trade_timestamp(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_run({"trade_count": 1}), folder)
            _forge_trade_field(
                folder, manifest, "entry_timestamp_utc",
                "2026-10-20 00:00:00Z",
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "canonical UTC"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_short_precision_rejection_timestamp(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_one_rejection_run(), folder)
            _forge_rejection_field(
                folder, manifest, "evaluated_timestamp_utc",
                "2026-10-20T00:00Z",
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "canonical UTC"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_noncanonical_checkpoint_fraction(self):
        run = BacktestRun(
            run_identity={}, trades=(), rejections=(),
            equity_checkpoints=(EquityCheckpoint(STAMP, 10000.0),),
            metrics={"trade_count": 0},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            _forge_summary_checkpoint(
                folder, manifest, "2026-10-20T00:00:00.000Z",
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "canonical UTC"):
                audit_backtest_artifact_structure(folder)


class Phase3AuditJSONTreeWriterParityTests(unittest.TestCase):
    def test_audit_refuses_rehashed_control_character_object_key(self):
        run = BacktestRun(
            run_identity={}, trades=(), rejections=(),
            equity_checkpoints=(), metrics={"trade_count": 0},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            _forge_raw_metric_payload(
                folder, manifest, b'{"trade_count":0,"bad\\nkey":1}\n'
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "JSON key must be printable"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_unicode_surrogate_string(self):
        run = BacktestRun(
            run_identity={}, trades=(), rejections=(),
            equity_checkpoints=(), metrics={"trade_count": 0},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            _forge_raw_metric_payload(
                folder, manifest, b'{"trade_count":0,"description":"\\ud800"}\n'
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "Unicode surrogates"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_nested_json_deeper_than_writer(self):
        run = BacktestRun(
            run_identity={}, trades=(), rejections=(),
            equity_checkpoints=(), metrics={"trade_count": 0},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            payload = b'{"trade_count":0,"extra":' + (
                b"[" * 70 + b"0" + b"]" * 70
            ) + b"}\n"
            _forge_raw_metric_payload(folder, manifest, payload)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "JSON nesting limit"):
                audit_backtest_artifact_structure(folder)


class Phase3AuditCanonicalJSONLBytesTests(unittest.TestCase):
    def test_audit_reports_semantic_tamper_before_noncanonical_row_format(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_run({"trade_count": 1}), folder)
            # The existing forge helper emits spaced/noncanonical JSON.
            _forge_trade_field(folder, manifest, "symbol", "INVALIDFX")
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "trade symbol is unsupported"):
                audit_backtest_artifact_structure(folder)

    def test_audit_accepts_canonical_writer_jsonl_bytes(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_run({"trade_count": 1}), folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 1)

    def test_audit_refuses_rehashed_unterminated_trade_row(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_run({"trade_count": 1}), folder)
            path = folder / "trades.jsonl"
            payload = path.read_bytes()
            self.assertTrue(payload.endswith(b"\n"))
            altered = payload[:-1]
            path.write_bytes(altered)
            for entry in manifest["artifacts"]:
                if entry["path"] == "trades.jsonl":
                    entry["size_bytes"] = len(altered)
                    entry["sha256"] = hashlib.sha256(altered).hexdigest()
            (folder / "manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "JSONL row is not canonical"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_pretty_rejection_row(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_one_rejection_run(), folder)
            path = folder / "rejections.jsonl"
            parsed = json.loads(path.read_text("utf-8"))
            altered = (json.dumps(parsed, sort_keys=True, separators=(", ", ": ")) + "\n").encode("utf-8")
            path.write_bytes(altered)
            for entry in manifest["artifacts"]:
                if entry["path"] == "rejections.jsonl":
                    entry["size_bytes"] = len(altered)
                    entry["sha256"] = hashlib.sha256(altered).hexdigest()
            (folder / "manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "JSONL row is not canonical"):
                audit_backtest_artifact_structure(folder)


class Phase3AuditCanonicalSummaryMetricsBytesTests(unittest.TestCase):
    def test_audit_accepts_writer_summary_metrics_canonical_bytes(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_run({"trade_count": 1}), folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 1)

    def test_audit_refuses_rehashed_compact_summary_json(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_run({"trade_count": 1}), folder)
            path = folder / "summary.json"
            source = json.loads(path.read_text("utf-8"))
            data = (json.dumps(source, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
            self.assertNotEqual(path.read_bytes(), data)
            path.write_bytes(data)
            for entry in manifest["artifacts"]:
                if entry["path"] == "summary.json":
                    entry["size_bytes"] = len(data)
                    entry["sha256"] = hashlib.sha256(data).hexdigest()
            (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "summary.json is not canonical JSON"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_metrics_with_different_key_order(self):
        metrics = {
            "trade_count": 1,
            "net_pnl_usd": 11.0,
            "commission_cost_usd": 0.5,
        }
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_run(metrics), folder)
            path = folder / "metrics.json"
            source = json.loads(path.read_text("utf-8"))
            reverse = dict(reversed(list(source.items())))
            data = (json.dumps(reverse, indent=2, sort_keys=False) + "\n").encode("utf-8")
            self.assertNotEqual(path.read_bytes(), data)
            path.write_bytes(data)
            for entry in manifest["artifacts"]:
                if entry["path"] == "metrics.json":
                    entry["size_bytes"] = len(data)
                    entry["sha256"] = hashlib.sha256(data).hexdigest()
            (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "metrics.json is not canonical JSON"):
                audit_backtest_artifact_structure(folder)


class Phase3AuditSourceEquityNetReturnTests(unittest.TestCase):
    def test_audit_accepts_writer_consistent_net_return_with_start_equity(self):
        run = replace(
            _run({"trade_count": 1, "net_return": 0.0011}),
            run_identity={"starting_equity_usd": 10000.0},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 1)

    def test_audit_refuses_rehashed_false_net_return_with_valid_identity(self):
        run = replace(
            _run({"trade_count": 1, "net_return": 0.0011}),
            run_identity={"starting_equity_usd": 10000.0},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            _forge_metrics(folder, manifest, "net_return", 0.5)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "net_return conflicts"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_nonpositive_or_boolean_start_equity_in_identity(self):
        for start in (0, False, -100):
            with self.subTest(start=start), tempfile.TemporaryDirectory() as home:
                run = replace(
                    _run({"trade_count": 1}),
                    run_identity={"starting_equity_usd": start},
                )
                folder = Path(home) / "evidence"
                write_backtest_artifacts(run, folder)
                with self.assertRaisesRegex(ValueError, "starting equity must be finite positive"):
                    audit_backtest_artifact_structure(folder)


def _drawdown_run() -> BacktestRun:
    curve = (
        EquityCheckpoint(STAMP, 10000.0),
        EquityCheckpoint(STAMP + timedelta(minutes=1), 9900.0),
        EquityCheckpoint(STAMP + timedelta(minutes=2), 10100.0),
        EquityCheckpoint(STAMP + timedelta(minutes=3), 9800.0),
    )
    return BacktestRun(
        run_identity={"starting_equity_usd": 10000.0},
        trades=(), rejections=(), equity_checkpoints=curve,
        metrics={
            "trade_count": 0,
            "max_drawdown_usd": 300.0,
            "max_drawdown_fraction": 300 / 10100,
            "recovery_factor": 0.0,
        },
    )


class Phase3AuditCheckpointDrawdownMetricTests(unittest.TestCase):
    def test_audit_accepts_checkpoint_curve_maximum_drawdown(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_drawdown_run(), folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 0)

    def test_audit_refuses_rehashed_false_dollar_drawdown(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_drawdown_run(), folder)
            _forge_metrics(folder, manifest, "max_drawdown_usd", 10.0)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "max_drawdown_usd conflicts"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_false_drawdown_fraction_and_recovery(self):
        for field, value in (
            ("max_drawdown_fraction", 0.8),
            ("recovery_factor", 8.0),
        ):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as home:
                folder = Path(home) / "evidence"
                manifest = write_backtest_artifacts(_drawdown_run(), folder)
                _forge_metrics(folder, manifest, field, value)
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, f"{field} conflicts"):
                    audit_backtest_artifact_structure(folder)

    def test_audit_accepts_null_recovery_when_curve_never_draws_down(self):
        run = BacktestRun(
            run_identity={"starting_equity_usd": 10000.0},
            trades=(), rejections=(),
            equity_checkpoints=(EquityCheckpoint(STAMP, 10000.0),),
            metrics={
                "trade_count": 0,
                "max_drawdown_usd": 0.0,
                "max_drawdown_fraction": 0.0,
                "recovery_factor": None,
            },
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 0)


def _requested_window_run() -> BacktestRun:
    return replace(
        _run({"trade_count": 1}),
        run_identity={
            "requested_start_utc": STAMP,
            "requested_end_utc": STAMP + timedelta(minutes=5),
        },
    )


def _forge_run_identity_window(
    folder: Path, manifest: dict[str, object], key: str,
    value: object, *, drop: bool = False,
) -> None:
    path = folder / "summary.json"
    summary = json.loads(path.read_text("utf-8"))
    if drop:
        summary["run_identity"].pop(key)
    else:
        summary["run_identity"][key] = value
    payload = (json.dumps(summary, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(payload)
    for entry in manifest["artifacts"]:
        if entry["path"] == "summary.json":
            entry["size_bytes"] = len(payload)
            entry["sha256"] = hashlib.sha256(payload).hexdigest()
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


class Phase3AuditRequestedWindowContractTests(unittest.TestCase):
    def test_audit_accepts_canonical_source_requested_interval(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_requested_window_run(), folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 1)

    def test_audit_refuses_rehashed_backdated_requested_end(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_requested_window_run(), folder)
            _forge_run_identity_window(
                folder, manifest, "requested_end_utc", "2026-10-19T00:00:00Z"
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "requested end precedes"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_noncanonical_requested_end_timestamp(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_requested_window_run(), folder)
            _forge_run_identity_window(
                folder, manifest, "requested_end_utc", "2026-10-20 00:05:00Z"
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "requested end.*canonical UTC"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_missing_requested_window_endpoint(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_requested_window_run(), folder)
            _forge_run_identity_window(
                folder, manifest, "requested_start_utc", None, drop=True
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "both UTC endpoints"):
                audit_backtest_artifact_structure(folder)


class Phase3AuditSourceIdentityScalarTests(unittest.TestCase):
    def test_audit_accepts_source_scalar_metadata_domains(self):
        run = replace(_run({"trade_count": 1}), run_identity={
            "backtest_engine_version": "v1",
            "code_commit": "abc123",
            "processed_data_manifest_id": "manifest-ref",
            "schema_version": "schema-v1",
            "timeframe": "1m",
            "slippage_pips": 0.4,
            "execution_timing_mode": "DECLARED_EARLIEST_BAR",
        })
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 1)

    def test_audit_refuses_rehashed_bool_or_negative_source_slippage(self):
        run = replace(_run({"trade_count": 1}), run_identity={"slippage_pips": 0.4})
        for value in (True, -0.1):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as home:
                folder = Path(home) / "evidence"
                manifest = write_backtest_artifacts(run, folder)
                _forge_run_identity_window(folder, manifest, "slippage_pips", value)
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, "slippage_pips must be finite nonnegative"):
                    audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_empty_or_control_source_commit(self):
        run = replace(_run({"trade_count": 1}), run_identity={"code_commit": "abc123"})
        for value in ("", "commit\nfake"):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as home:
                folder = Path(home) / "evidence"
                manifest = write_backtest_artifacts(run, folder)
                _forge_run_identity_window(folder, manifest, "code_commit", value)
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, "code_commit must be printable nonempty"):
                    audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_unknown_execution_timing_mode(self):
        run = replace(_run({"trade_count": 1}), run_identity={
            "execution_timing_mode": "DECLARED_EARLIEST_BAR"
        })
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            _forge_run_identity_window(
                folder, manifest, "execution_timing_mode", "BEFORE_DECISION"
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "execution_timing_mode is unsupported"):
                audit_backtest_artifact_structure(folder)


def _scheduled_exits_run() -> BacktestRun:
    return replace(
        _run({"trade_count": 1}),
        run_identity={
            "scheduled_exits": [
                {
                    "decision_id": "DEC-A",
                    "symbol": "EURUSD",
                    "timestamp_utc": STAMP + timedelta(minutes=1),
                },
                {
                    "decision_id": "DEC-B",
                    "symbol": "GBPUSD",
                    "timestamp_utc": STAMP + timedelta(minutes=2),
                },
            ],
        },
    )


class Phase3AuditScheduledExitIdentityTests(unittest.TestCase):
    def test_audit_accepts_canonical_source_scheduled_exits(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_scheduled_exits_run(), folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 1)

    def test_audit_refuses_rehashed_scheduled_exit_unsupported_symbol(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_scheduled_exits_run(), folder)
            scheduled = [
                {"decision_id": "DEC-A", "symbol": "BTCUSD",
                 "timestamp_utc": "2026-10-20T00:01:00Z"},
            ]
            _forge_run_identity_window(folder, manifest, "scheduled_exits", scheduled)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "scheduled exit symbol is unsupported"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_scheduled_exit_noncanonical_order(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_scheduled_exits_run(), folder)
            scheduled = list(reversed(json.loads(
                (folder / "summary.json").read_text("utf-8")
            )["run_identity"]["scheduled_exits"]))
            _forge_run_identity_window(folder, manifest, "scheduled_exits", scheduled)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "scheduled exits are not in canonical order"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_duplicate_scheduled_exit_decision(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_scheduled_exits_run(), folder)
            scheduled = json.loads(
                (folder / "summary.json").read_text("utf-8")
            )["run_identity"]["scheduled_exits"]
            scheduled[1]["decision_id"] = scheduled[0]["decision_id"]
            _forge_run_identity_window(folder, manifest, "scheduled_exits", scheduled)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "duplicate scheduled exit decision_id"):
                audit_backtest_artifact_structure(folder)


def _source_risk_config() -> dict[str, float]:
    return {
        "default_risk_fraction": 0.0025,
        "max_risk_fraction": 0.005,
        "max_simultaneous_risk_fraction": 0.01,
        "daily_loss_halt_fraction": 0.015,
    }


class Phase3AuditRiskConfigSourceContractTests(unittest.TestCase):
    def test_audit_accepts_source_defined_positive_bounded_risk_config(self):
        run = replace(
            _run({"trade_count": 1}),
            run_identity={"risk_config": _source_risk_config()},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 1)

    def test_audit_refuses_rehashed_zero_or_boolean_risk_fraction(self):
        run = replace(
            _run({"trade_count": 1}),
            run_identity={"risk_config": _source_risk_config()},
        )
        for bad in (0, True):
            with self.subTest(bad=bad), tempfile.TemporaryDirectory() as home:
                folder = Path(home) / "evidence"
                manifest = write_backtest_artifacts(run, folder)
                risk = _source_risk_config()
                risk["default_risk_fraction"] = bad
                _forge_run_identity_window(folder, manifest, "risk_config", risk)
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, "default_risk_fraction must be positive bounded"):
                    audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_risk_hierarchy_inversion(self):
        run = replace(
            _run({"trade_count": 1}),
            run_identity={"risk_config": _source_risk_config()},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            risk = _source_risk_config()
            risk["max_risk_fraction"] = 0.001
            _forge_run_identity_window(folder, manifest, "risk_config", risk)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "fractions violate risk hierarchy"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_missing_risk_config_field(self):
        run = replace(
            _run({"trade_count": 1}),
            run_identity={"risk_config": _source_risk_config()},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            risk = _source_risk_config()
            risk.pop("daily_loss_halt_fraction")
            _forge_run_identity_window(folder, manifest, "risk_config", risk)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "risk_config fields mismatch"):
                audit_backtest_artifact_structure(folder)


class Phase3AuditBuiltinCostModelContractTests(unittest.TestCase):
    def test_audit_accepts_builtin_zero_and_fixed_cost_source_models(self):
        for commission in (
            {"model": "zero_commission"},
            {"model": "fixed_per_million_per_side",
             "usd_per_million_per_side": 2.25},
        ):
            with self.subTest(model=commission["model"]), tempfile.TemporaryDirectory() as home:
                folder = Path(home) / "evidence"
                run = replace(
                    _run({"trade_count": 1}),
                    run_identity={
                        "commission_model": commission,
                        "financing_model": {"model": "zero_financing"},
                    },
                )
                write_backtest_artifacts(run, folder)
                self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 1)

    def test_audit_refuses_rehashed_negative_or_boolean_fixed_commission_rate(self):
        for rate in (-1.0, True):
            with self.subTest(rate=rate), tempfile.TemporaryDirectory() as home:
                folder = Path(home) / "evidence"
                run = replace(
                    _run({"trade_count": 1}),
                    run_identity={
                        "commission_model": {
                            "model": "fixed_per_million_per_side",
                            "usd_per_million_per_side": 2.25,
                        }
                    },
                )
                manifest = write_backtest_artifacts(run, folder)
                _forge_run_identity_window(
                    folder, manifest, "commission_model", {
                        "model": "fixed_per_million_per_side",
                        "usd_per_million_per_side": rate,
                    }
                )
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, "fixed commission rate must be finite"):
                    audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_extra_zero_financing_claim(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            run = replace(
                _run({"trade_count": 1}),
                run_identity={"financing_model": {"model": "zero_financing"}},
            )
            manifest = write_backtest_artifacts(run, folder)
            _forge_run_identity_window(
                folder, manifest, "financing_model",
                {"model": "zero_financing", "charge_usd": 100},
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "zero model fields mismatch"):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_custom_model_source_identity(self):
        run = replace(
            _run({"trade_count": 1}),
            run_identity={"commission_model": {"model": "custom", "rate": 1.25}},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 1)


class Phase3AuditCostModelFamilyIdentityTests(unittest.TestCase):
    def test_audit_refuses_rehashed_financing_model_in_commission_slot(self):
        run = replace(
            _run({"trade_count": 1}),
            run_identity={"commission_model": {"model": "zero_commission"}},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            _forge_run_identity_window(
                folder, manifest, "commission_model",
                {"model": "zero_financing"},
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "commission_model model type is incompatible"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_commission_model_in_financing_slot(self):
        run = replace(
            _run({"trade_count": 1}),
            run_identity={"financing_model": {"model": "zero_financing"}},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            _forge_run_identity_window(
                folder, manifest, "financing_model",
                {"model": "zero_commission"},
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "financing_model model type is incompatible"):
                audit_backtest_artifact_structure(folder)


class Phase3AuditDecisionMetadataContractTests(unittest.TestCase):
    def test_audit_accepts_engine_compatible_decision_metadata(self):
        run = replace(
            _run({"trade_count": 1}),
            run_identity={"decision_config": {
                "signal": ["trend", 1, 0.25, None, True],
                "thresholds": {"low": -2, "high": 3.5},
            }},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 1)

    def test_audit_refuses_rehashed_control_character_metadata_value(self):
        run = replace(_run({"trade_count": 1}), run_identity={"decision_config": {"signal": "trend"}})
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            _forge_run_identity_window(
                folder, manifest, "decision_config", {"signal": "bad\nvalue"}
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "decision_config strings must be printable"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_empty_nested_metadata_key(self):
        run = replace(_run({"trade_count": 1}), run_identity={"decision_config": {"signal": 1}})
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            _forge_run_identity_window(folder, manifest, "decision_config", {"signal": {"": 1}})
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "decision_config keys must be printable nonempty"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_metadata_deeper_than_engine_budget(self):
        run = replace(_run({"trade_count": 1}), run_identity={"decision_config": {"signal": 1}})
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            nested = 1
            for _ in range(34):
                nested = [nested]
            _forge_run_identity_window(folder, manifest, "decision_config", {"signal": nested})
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "decision_config exceeds nesting depth"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_oversized_serialized_metadata(self):
        run = replace(_run({"trade_count": 1}), run_identity={"decision_config": {"signal": 1}})
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            _forge_run_identity_window(
                folder, manifest, "decision_config", {"signal": "x" * 66000}
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "decision_config exceeds 64 KiB"):
                audit_backtest_artifact_structure(folder)


def _sequential_equity_run() -> BacktestRun:
    first = _sample_trade()
    second = replace(
        first, trade_id="AUDIT-T2", decision_id="AUDIT-D2",
        exit_timestamp_utc=STAMP + timedelta(minutes=2),
        risk_equity_before_usd=10011.0, risk_equity_after_usd=10022.0,
    )
    return BacktestRun(
        run_identity={"starting_equity_usd": 10000.0},
        trades=(first, second), rejections=(), equity_checkpoints=(),
        metrics={"trade_count": 2},
    )


def _forge_second_trade_equity(
    folder: Path, manifest: dict[str, object], before: float, after: float,
) -> None:
    path = folder / "trades.jsonl"
    records = [json.loads(line) for line in path.read_text("utf-8").splitlines()]
    records[1]["risk_equity_before_usd"] = before
    records[1]["risk_equity_after_usd"] = after
    payload = (
        "\n".join(json.dumps(item, sort_keys=True, separators=(",", ":"))
                  for item in records) + "\n"
    ).encode("utf-8")
    path.write_bytes(payload)
    for entry in manifest["artifacts"]:
        if entry["path"] == "trades.jsonl":
            entry["size_bytes"] = len(payload)
            entry["sha256"] = hashlib.sha256(payload).hexdigest()
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


class Phase3AuditRealizedEquityContinuityTests(unittest.TestCase):
    def test_audit_accepts_source_realized_equity_trade_sequence(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_sequential_equity_run(), folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 2)

    def test_audit_refuses_rehashed_disconnected_second_trade_equity(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_sequential_equity_run(), folder)
            _forge_second_trade_equity(folder, manifest, 12011.0, 12022.0)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "risk equity continuity"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_first_trade_equity_not_starting_equity(self):
        with tempfile.TemporaryDirectory() as home:
            run = _sequential_equity_run()
            wrong_first = replace(
                run.trades[0],
                risk_equity_before_usd=11000.0,
                risk_equity_after_usd=11011.0,
            )
            run = replace(run, trades=(wrong_first, run.trades[1]))
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            with self.assertRaisesRegex(ValueError, "risk equity continuity"):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_older_synthetic_trade_without_source_starting_equity(self):
        run = replace(_sequential_equity_run(), run_identity={})
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 2)


class Phase3AuditDecisionMetadataBudgetEdgesTests(unittest.TestCase):
    def test_audit_accepts_exact_8192_node_decision_budget(self):
        # Root dict + list + 8190 leaves matches BacktestConfig's limit.
        run = replace(
            _run({"trade_count": 1}),
            run_identity={"decision_config": {"values": [0] * 8190}},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 1)

    def test_audit_refuses_8193_node_decision_metadata(self):
        run = replace(
            _run({"trade_count": 1}),
            run_identity={"decision_config": {"values": [0] * 8191}},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "decision_config exceeds node budget"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_ascii_escaped_unicode_size_bypass(self):
        # Writer/BacktestConfig size is computed with ensure_ascii=True.
        # This escaped Unicode content is >64KiB, despite short UTF-8 text.
        run = replace(
            _run({"trade_count": 1}),
            run_identity={"decision_config": {"signal": "é" * 11000}},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "decision_config exceeds 64 KiB"):
                audit_backtest_artifact_structure(folder)


class Phase3AuditAdverseExecutionPriceTests(unittest.TestCase):
    def test_audit_accepts_source_compatible_equal_execution_references(self):
        for direction in (Direction.LONG, Direction.SHORT):
            with self.subTest(direction=direction), tempfile.TemporaryDirectory() as home:
                record = replace(
                    _sample_trade(), direction=direction,
                    stop_price=(1.099 if direction is Direction.LONG else 1.102),
                    target_price=(1.101 if direction is Direction.LONG else 1.099),
                )
                run = replace(_run({"trade_count": 1}), trades=(record,))
                folder = Path(home) / "evidence"
                write_backtest_artifacts(run, folder)
                self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 1)

    def test_audit_refuses_rehashed_long_favorable_entry_or_exit(self):
        for field, value in (
            ("entry_price", 1.099),
            ("exit_price", 1.102),
        ):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as home:
                folder = Path(home) / "evidence"
                manifest = write_backtest_artifacts(_run({"trade_count": 1}), folder)
                _forge_trade_field(folder, manifest, field, value)
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, "favorable slippage"):
                    audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_short_favorable_entry_or_exit(self):
        for field, value in (
            ("entry_price", 1.102),
            ("exit_price", 1.099),
        ):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as home:
                record = replace(
                    _sample_trade(), direction=Direction.SHORT,
                    stop_price=1.102, target_price=1.099,
                )
                run = replace(_run({"trade_count": 1}), trades=(record,))
                folder = Path(home) / "evidence"
                manifest = write_backtest_artifacts(run, folder)
                _forge_trade_field(folder, manifest, field, value)
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, "favorable slippage"):
                    audit_backtest_artifact_structure(folder)


class Phase3AuditStopTargetGeometryTests(unittest.TestCase):
    def test_audit_accepts_source_long_and_short_trade_geometry(self):
        for direction in (Direction.LONG, Direction.SHORT):
            with self.subTest(direction=direction), tempfile.TemporaryDirectory() as home:
                record = replace(
                    _sample_trade(), direction=direction,
                    stop_price=(1.099 if direction is Direction.LONG else 1.102),
                    target_price=(1.101 if direction is Direction.LONG else 1.099),
                )
                run = replace(_run({"trade_count": 1}), trades=(record,))
                folder = Path(home) / "evidence"
                write_backtest_artifacts(run, folder)
                self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 1)

    def test_audit_refuses_rehashed_long_invalid_stop_or_target(self):
        for field, price in (("stop_price", 1.101), ("target_price", 1.099)):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as home:
                folder = Path(home) / "evidence"
                manifest = write_backtest_artifacts(_run({"trade_count": 1}), folder)
                _forge_trade_field(folder, manifest, field, price)
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, "stop/target geometry"):
                    audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_short_invalid_stop_or_target(self):
        for field, price in (("stop_price", 1.099), ("target_price", 1.101)):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as home:
                record = replace(
                    _sample_trade(), direction=Direction.SHORT,
                    stop_price=1.102, target_price=1.099,
                )
                run = replace(_run({"trade_count": 1}), trades=(record,))
                folder = Path(home) / "evidence"
                manifest = write_backtest_artifacts(run, folder)
                _forge_trade_field(folder, manifest, field, price)
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, "stop/target geometry"):
                    audit_backtest_artifact_structure(folder)

    def test_audit_preserves_optional_null_target_when_stop_valid(self):
        for direction in (Direction.LONG, Direction.SHORT):
            with self.subTest(direction=direction), tempfile.TemporaryDirectory() as home:
                record = replace(
                    _sample_trade(), direction=direction,
                    stop_price=(1.099 if direction is Direction.LONG else 1.102),
                    target_price=None,
                )
                run = replace(_run({"trade_count": 1}), trades=(record,))
                folder = Path(home) / "evidence"
                write_backtest_artifacts(run, folder)
                self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 1)


def _source_engine_checkpoint_run() -> BacktestRun:
    source = _sequential_equity_run()
    # The real engine uses position_id == decision_id for each close.
    source = replace(
        source, trades=tuple(
            replace(
                item, trade_id=item.decision_id,
                exit_reference_price=1.10125, exit_price=1.1011,
            ) for item in source.trades
        ),
    )
    return replace(
        source,
        run_identity={
            "backtest_engine_version": BACKTEST_ENGINE_VERSION,
            "starting_equity_usd": 10000.0,
        },
        equity_checkpoints=(
            EquityCheckpoint(STAMP, 10000.0),
            EquityCheckpoint(STAMP + timedelta(minutes=1), 10011.0),
            EquityCheckpoint(STAMP + timedelta(minutes=2), 10022.0),
        ),
    )


def _forge_checkpoint_summary(
    folder: Path, manifest: dict[str, object], index: int,
    field: str, value: object,
) -> None:
    path = folder / "summary.json"
    summary = json.loads(path.read_text("utf-8"))
    if field == "remove":
        summary["equity_checkpoints"].pop(index)
        summary["equity_checkpoint_count"] -= 1
    else:
        summary["equity_checkpoints"][index][field] = value
    payload = (json.dumps(summary, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(payload)
    for entry in manifest["artifacts"]:
        if entry["path"] == "summary.json":
            entry["size_bytes"] = len(payload)
            entry["sha256"] = hashlib.sha256(payload).hexdigest()
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


class Phase3AuditSourceEngineCheckpointParityTests(unittest.TestCase):
    def test_audit_accepts_engine_checkpoint_close_parity(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_source_engine_checkpoint_run(), folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 2)

    def test_audit_refuses_rehashed_missing_close_checkpoint(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_source_engine_checkpoint_run(), folder)
            _forge_checkpoint_summary(folder, manifest, 2, "remove", None)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "checkpoint count conflicts"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_wrong_initial_source_checkpoint(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_source_engine_checkpoint_run(), folder)
            _forge_checkpoint_summary(
                folder, manifest, 0, "realized_risk_equity_usd", 10001.0
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "initial checkpoint equity conflicts"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_wrong_close_equity_or_time(self):
        for field, value in (
            ("realized_risk_equity_usd", 10015.0),
            ("timestamp_utc", "2026-10-20T00:01:30Z"),
        ):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as home:
                folder = Path(home) / "evidence"
                manifest = write_backtest_artifacts(
                    _source_engine_checkpoint_run(), folder
                )
                _forge_checkpoint_summary(folder, manifest, 1, field, value)
                self.assertEqual(verify_backtest_artifacts(folder), manifest)
                with self.assertRaisesRegex(ValueError, "checkpoint conflicts with trade close"):
                    audit_backtest_artifact_structure(folder)


class Phase3AuditSourceEngineTradeIdentifierParityTests(unittest.TestCase):
    def test_audit_accepts_source_engine_matching_trade_and_decision_ids(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_source_engine_checkpoint_run(), folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 2)

    def test_audit_refuses_rehashed_false_source_trade_position_id(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_source_engine_checkpoint_run(), folder)
            path = folder / "trades.jsonl"
            records = [json.loads(row) for row in path.read_text("utf-8").splitlines()]
            records[0]["trade_id"] = "UNRELATED-POSITION"
            payload = (
                "\n".join(
                    json.dumps(row, sort_keys=True, separators=(",", ":"))
                    for row in records
                ) + "\n"
            ).encode("utf-8")
            path.write_bytes(payload)
            for entry in manifest["artifacts"]:
                if entry["path"] == "trades.jsonl":
                    entry["size_bytes"] = len(payload)
                    entry["sha256"] = hashlib.sha256(payload).hexdigest()
            (folder / "manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "trade_id conflicts with decision_id"):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_generic_synthetic_trade_identifier_distinction(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_sequential_equity_run(), folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 2)


class Phase3AuditSourceEngineReferencePnLTests(unittest.TestCase):
    def test_audit_accepts_source_reference_pnl_calculation(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_source_engine_checkpoint_run(), folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 2)

    def test_audit_refuses_rehashed_false_reference_price_gross_pnl(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_source_engine_checkpoint_run(), folder)
            path = folder / "trades.jsonl"
            rows = [json.loads(value) for value in path.read_text("utf-8").splitlines()]
            rows[0]["exit_reference_price"] = 1.1013
            payload = (
                "\n".join(
                    json.dumps(value, sort_keys=True, separators=(",", ":"))
                    for value in rows
                ) + "\n"
            ).encode("utf-8")
            path.write_bytes(payload)
            for entry in manifest["artifacts"]:
                if entry["path"] == "trades.jsonl":
                    entry["size_bytes"] = len(payload)
                    entry["sha256"] = hashlib.sha256(payload).hexdigest()
            (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "gross PnL conflicts with reference-price"):
                audit_backtest_artifact_structure(folder)

    def test_audit_accepts_source_jpy_quote_conversion(self):
        gross = pnl_usd(
            symbol="USDJPY", direction=Direction.LONG, units=10000,
            entry_price=150.0, exit_price=150.1,
        )
        item = replace(
            _sample_trade(), trade_id="JPY-CLOSE", decision_id="JPY-CLOSE",
            symbol="USDJPY", entry_reference_price=150.0,
            exit_reference_price=150.1, entry_price=150.0,
            exit_price=150.1, stop_price=149.9, target_price=150.1,
            gross_pnl_usd=gross, slippage_cost_usd=0.0,
            commission_cost_usd=0.0, financing_cost_usd=0.0,
            net_pnl_usd=gross, risk_equity_after_usd=10000.0 + gross,
        )
        run = BacktestRun(
            run_identity={
                "backtest_engine_version": BACKTEST_ENGINE_VERSION,
                "starting_equity_usd": 10000.0,
            },
            trades=(item,), rejections=(),
            equity_checkpoints=(
                EquityCheckpoint(STAMP, 10000.0),
                EquityCheckpoint(STAMP + timedelta(minutes=1), 10000.0 + gross),
            ),
            metrics={"trade_count": 1},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 1)


def _forge_versioned_trade_execution(
    folder: Path, manifest: dict[str, object], key: str, value: float,
) -> None:
    path = folder / "trades.jsonl"
    rows = [json.loads(line) for line in path.read_text("utf-8").splitlines()]
    rows[0][key] = value
    payload = ("\n".join(
        json.dumps(line, sort_keys=True, separators=(",", ":")) for line in rows
    ) + "\n").encode("utf-8")
    path.write_bytes(payload)
    for entry in manifest["artifacts"]:
        if entry["path"] == "trades.jsonl":
            entry["size_bytes"] = len(payload)
            entry["sha256"] = hashlib.sha256(payload).hexdigest()
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


class Phase3AuditSourceSlippageCostReconciliationTests(unittest.TestCase):
    def test_audit_accepts_source_engine_adverse_slippage_economics(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_source_engine_checkpoint_run(), folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 2)

    def test_audit_refuses_rehashed_forged_exit_execution_slippage(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_source_engine_checkpoint_run(), folder)
            _forge_versioned_trade_execution(
                folder, manifest, "exit_price", 1.10112,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "slippage cost conflicts with execution"):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_forged_entry_execution_slippage(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_source_engine_checkpoint_run(), folder)
            _forge_versioned_trade_execution(
                folder, manifest, "entry_price", 1.10003,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "slippage cost conflicts with execution"):
                audit_backtest_artifact_structure(folder)


def _same_exit_source_engine_run() -> BacktestRun:
    original = _source_engine_checkpoint_run()
    first, second = original.trades
    # Engine closes Z before A but writer sorts equal-exit rows by A then Z.
    first = replace(first, trade_id="Z-CLOSE", decision_id="Z-CLOSE")
    second = replace(
        second, trade_id="A-CLOSE", decision_id="A-CLOSE",
        exit_timestamp_utc=STAMP + timedelta(minutes=1),
    )
    return replace(
        original, trades=(first, second),
        equity_checkpoints=(
            EquityCheckpoint(STAMP, 10000.0),
            EquityCheckpoint(STAMP + timedelta(minutes=1), 10011.0),
            EquityCheckpoint(STAMP + timedelta(minutes=1), 10022.0),
        ),
    )


class Phase3AuditEqualExitTimeSourceCheckpointTests(unittest.TestCase):
    def test_audit_accepts_close_order_different_from_same_time_id_order(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_same_exit_source_engine_run(), folder)
            rows = [
                json.loads(line)
                for line in (folder / "trades.jsonl").read_text("utf-8").splitlines()
            ]
            self.assertEqual(
                [row["trade_id"] for row in rows], ["A-CLOSE", "Z-CLOSE"]
            )
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 2)

    def test_audit_refuses_rehashed_same_time_checkpoint_without_transition(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_same_exit_source_engine_run(), folder)
            _forge_checkpoint_summary(
                folder, manifest, 1, "realized_risk_equity_usd", 10022.0
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "checkpoint conflicts with trade close"):
                audit_backtest_artifact_structure(folder)


def _versioned_builtin_zero_cost_run() -> BacktestRun:
    source = _source_engine_checkpoint_run()
    return replace(
        source,
        run_identity={
            "backtest_engine_version": BACKTEST_ENGINE_VERSION,
            "starting_equity_usd": 10000.0,
            "commission_model": {"model": "zero_commission"},
            "financing_model": {"model": "zero_financing"},
        },
        trades=tuple(
            replace(item, commission_cost_usd=0.0, financing_cost_usd=0.0)
            for item in source.trades
        ),
    )


def _forge_versioned_trade_costs(
    folder: Path, manifest: dict[str, object], commission: float,
    financing: float,
) -> None:
    path = folder / "trades.jsonl"
    records = [json.loads(line) for line in path.read_text("utf-8").splitlines()]
    records[0]["commission_cost_usd"] = commission
    records[0]["financing_cost_usd"] = financing
    payload = ("\n".join(
        json.dumps(row, sort_keys=True, separators=(",", ":")) for row in records
    ) + "\n").encode("utf-8")
    path.write_bytes(payload)
    for entry in manifest["artifacts"]:
        if entry["path"] == "trades.jsonl":
            entry["size_bytes"] = len(payload)
            entry["sha256"] = hashlib.sha256(payload).hexdigest()
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


class Phase3AuditSourceBuiltinCostEconomicsTests(unittest.TestCase):
    def test_audit_accepts_source_zero_commission_and_financing_trades(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_versioned_builtin_zero_cost_run(), folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 2)

    def test_audit_refuses_rehashed_hidden_nonzero_commission_under_zero_model(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_versioned_builtin_zero_cost_run(), folder)
            # Preserve net= gross - slippage - commission - financing,
            # but the declared source models cannot charge these costs.
            _forge_versioned_trade_costs(folder, manifest, 1.0, -1.0)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "zero commission conflicts"):
                audit_backtest_artifact_structure(folder)

    def test_audit_accepts_source_fixed_per_million_commission_rate(self):
        original = _source_engine_checkpoint_run()
        run = replace(
            original,
            run_identity={
                "backtest_engine_version": BACKTEST_ENGINE_VERSION,
                "starting_equity_usd": 10000.0,
                "commission_model": {
                    "model": "fixed_per_million_per_side",
                    "usd_per_million_per_side": 25.0,
                },
            },
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 2)

    def test_audit_refuses_rehashed_false_zero_financing_model(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_source_engine_checkpoint_run(), folder)
            _forge_run_identity_window(
                folder, manifest, "financing_model", {"model": "zero_financing"}
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "zero financing conflicts"):
                audit_backtest_artifact_structure(folder)


def _zero_trade_source_engine_run() -> BacktestRun:
    return BacktestRun(
        run_identity={
            "backtest_engine_version": BACKTEST_ENGINE_VERSION,
            "starting_equity_usd": 10000.0,
        },
        trades=(), rejections=(),
        equity_checkpoints=(EquityCheckpoint(STAMP, 10000.0),),
        metrics={"trade_count": 0},
    )


class Phase3AuditSourceCheckpointCountBoundaryTests(unittest.TestCase):
    def test_audit_accepts_zero_trade_source_with_initial_checkpoint(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_zero_trade_source_engine_run(), folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 0)

    def test_audit_refuses_rehashed_absent_zero_trade_initial_checkpoint(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(_zero_trade_source_engine_run(), folder)
            _forge_checkpoint_summary(folder, manifest, 0, "remove", None)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(ValueError, "checkpoint count conflicts"):
                audit_backtest_artifact_structure(folder)

    def test_audit_accepts_repeated_zero_pnl_equal_timestamp_closes(self):
        source = _same_exit_source_engine_run()
        zero_trades = tuple(
            replace(
                item, entry_reference_price=1.1, exit_reference_price=1.1,
                entry_price=1.1, exit_price=1.1, gross_pnl_usd=0.0,
                slippage_cost_usd=0.0, commission_cost_usd=0.0,
                financing_cost_usd=0.0, net_pnl_usd=0.0,
                risk_equity_before_usd=10000.0,
                risk_equity_after_usd=10000.0,
            ) for item in source.trades
        )
        run = replace(
            source, trades=zero_trades,
            equity_checkpoints=(
                EquityCheckpoint(STAMP, 10000.0),
                EquityCheckpoint(STAMP + timedelta(minutes=1), 10000.0),
                EquityCheckpoint(STAMP + timedelta(minutes=1), 10000.0),
            ),
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            self.assertEqual(audit_backtest_artifact_structure(folder)["trade_count"], 2)


def _declared_source_slippage_run(
    direction: Direction, symbol: str,
) -> BacktestRun:
    reference_entry = 150.0 if symbol == "USDJPY" else 1.1
    reference_exit = (
        (150.2 if direction is Direction.LONG else 149.8)
        if symbol == "USDJPY"
        else (1.10125 if direction is Direction.LONG else 1.09875)
    )
    entry_side = OrderSide.BUY if direction is Direction.LONG else OrderSide.SELL
    exit_side = OrderSide.SELL if direction is Direction.LONG else OrderSide.BUY
    entry_fill = apply_adverse_slippage(
        reference_entry, side=entry_side, pips=1.5, symbol=symbol,
    )
    exit_fill = apply_adverse_slippage(
        reference_exit, side=exit_side, pips=1.5, symbol=symbol,
    )
    gross = pnl_usd(
        symbol=symbol, direction=direction, units=10000,
        entry_price=reference_entry, exit_price=reference_exit,
    )
    slipped = pnl_usd(
        symbol=symbol, direction=direction, units=10000,
        entry_price=entry_fill, exit_price=exit_fill,
    )
    slippage_cost = max(0.0, gross - slipped)
    net_pnl = gross - slippage_cost
    stop = (
        (149.9 if direction is Direction.LONG else 150.1)
        if symbol == "USDJPY"
        else (1.099 if direction is Direction.LONG else 1.101)
    )
    target = (
        (150.3 if direction is Direction.LONG else 149.7)
        if symbol == "USDJPY"
        else (1.102 if direction is Direction.LONG else 1.098)
    )
    item = replace(
        _sample_trade(), trade_id="SOURCE-SLIP-1",
        decision_id="SOURCE-SLIP-1", symbol=symbol, direction=direction,
        entry_reference_price=reference_entry,
        exit_reference_price=reference_exit,
        entry_price=entry_fill, exit_price=exit_fill,
        stop_price=stop, target_price=target,
        gross_pnl_usd=gross, slippage_cost_usd=slippage_cost,
        commission_cost_usd=0.0, financing_cost_usd=0.0,
        net_pnl_usd=net_pnl, risk_equity_before_usd=10000.0,
        risk_equity_after_usd=10000.0 + net_pnl,
    )
    return BacktestRun(
        run_identity={
            "backtest_engine_version": BACKTEST_ENGINE_VERSION,
            "starting_equity_usd": 10000.0,
            "slippage_pips": 1.5,
        },
        trades=(item,), rejections=(),
        equity_checkpoints=(
            EquityCheckpoint(STAMP, 10000.0),
            EquityCheckpoint(STAMP + timedelta(minutes=1), 10000.0 + net_pnl),
        ),
        metrics={"trade_count": 1},
    )


class Phase3AuditDeclaredSourceSlippagePipsTests(unittest.TestCase):
    def test_audit_accepts_declared_long_short_and_jpy_fill_prices(self):
        for direction, symbol in (
            (Direction.LONG, "EURUSD"),
            (Direction.SHORT, "GBPUSD"),
            (Direction.LONG, "USDJPY"),
        ):
            with self.subTest(direction=direction, symbol=symbol):
                with tempfile.TemporaryDirectory() as home:
                    folder = Path(home) / "evidence"
                    write_backtest_artifacts(
                        _declared_source_slippage_run(direction, symbol), folder,
                    )
                    self.assertEqual(
                        audit_backtest_artifact_structure(folder)["trade_count"], 1,
                    )

    def test_audit_refuses_rehashed_false_declared_pip_displacement(self):
        for direction, symbol in (
            (Direction.LONG, "EURUSD"),
            (Direction.SHORT, "GBPUSD"),
        ):
            with self.subTest(direction=direction, symbol=symbol):
                with tempfile.TemporaryDirectory() as home:
                    folder = Path(home) / "evidence"
                    manifest = write_backtest_artifacts(
                        _declared_source_slippage_run(direction, symbol), folder,
                    )
                    _forge_run_identity_window(
                        folder, manifest, "slippage_pips", 0.0,
                    )
                    self.assertEqual(verify_backtest_artifacts(folder), manifest)
                    with self.assertRaisesRegex(
                        ValueError, "conflict with declared slippage_pips",
                    ):
                        audit_backtest_artifact_structure(folder)

    def test_audit_preserves_generic_synthetic_slippage_identity_flexibility(self):
        source = _declared_source_slippage_run(Direction.LONG, "EURUSD")
        synthetic = replace(
            source, run_identity={
                "starting_equity_usd": 10000.0,
                "slippage_pips": 0.0,
            },
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(synthetic, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )


class Phase3AuditSourceInitialCheckpointTradeEntryChronologyTests(unittest.TestCase):
    def test_audit_accepts_initial_checkpoint_before_first_trade_entry(self):
        source = _declared_source_slippage_run(Direction.LONG, "EURUSD")
        run = replace(
            source, equity_checkpoints=(
                replace(
                    source.equity_checkpoints[0],
                    timestamp_utc=STAMP - timedelta(minutes=1),
                ),
                source.equity_checkpoints[1],
            ),
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )

    def test_audit_refuses_rehashed_initial_checkpoint_after_trade_entry(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _declared_source_slippage_run(Direction.LONG, "EURUSD"), folder,
            )
            forged_initial = (
                (STAMP + timedelta(seconds=30)).isoformat()
                .replace("+00:00", "Z")
            )
            _forge_checkpoint_summary(
                folder, manifest, 0, "timestamp_utc", forged_initial,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "initial checkpoint follows trade entry",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_generic_initial_checkpoint_timing_flexibility(self):
        source = _declared_source_slippage_run(Direction.LONG, "EURUSD")
        generic = replace(
            source,
            run_identity={"starting_equity_usd": 10000.0},
            equity_checkpoints=(
                replace(
                    source.equity_checkpoints[0],
                    timestamp_utc=STAMP + timedelta(seconds=30),
                ),
                source.equity_checkpoints[1],
            ),
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(generic, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )


def _zero_declared_source_slippage_run(direction: Direction) -> BacktestRun:
    source = _declared_source_slippage_run(direction, "EURUSD")
    trade = source.trades[0]
    zero_slippage_trade = replace(
        trade,
        entry_price=trade.entry_reference_price,
        exit_price=trade.exit_reference_price,
        slippage_cost_usd=0.0,
        net_pnl_usd=trade.gross_pnl_usd,
        risk_equity_after_usd=10000.0 + trade.gross_pnl_usd,
    )
    return replace(
        source,
        run_identity={**source.run_identity, "slippage_pips": 0.0},
        trades=(zero_slippage_trade,),
        equity_checkpoints=(
            source.equity_checkpoints[0],
            EquityCheckpoint(
                STAMP + timedelta(minutes=1),
                10000.0 + trade.gross_pnl_usd,
            ),
        ),
    )


class Phase3AuditSourceSlippageBoundaryWitnessTests(unittest.TestCase):
    def test_audit_accepts_zero_pips_both_direction_execution_fills(self):
        for direction in (Direction.LONG, Direction.SHORT):
            with self.subTest(direction=direction):
                with tempfile.TemporaryDirectory() as home:
                    folder = Path(home) / "evidence"
                    write_backtest_artifacts(
                        _zero_declared_source_slippage_run(direction), folder,
                    )
                    self.assertEqual(
                        audit_backtest_artifact_structure(folder)["trade_count"], 1,
                    )

    def test_audit_refuses_rehashed_nonzero_setting_for_zero_slip_fill(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _zero_declared_source_slippage_run(Direction.SHORT), folder,
            )
            _forge_run_identity_window(
                folder, manifest, "slippage_pips", 1.5,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "execution prices conflict with declared slippage_pips",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_accepts_jpy_short_declared_pip_size_and_execution_side(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(
                _declared_source_slippage_run(Direction.SHORT, "USDJPY"),
                folder,
            )
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )

    def test_audit_accepts_source_version_without_optional_pip_identity(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_source_engine_checkpoint_run(), folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 2,
            )


def _ambiguous_stop_source_run() -> BacktestRun:
    source = _zero_declared_source_slippage_run(Direction.LONG)
    original = source.trades[0]
    # A source-engine LONG stop exits at the declared stop; when both
    # stop and target are touched the result is still a STOP.
    reference_exit = original.stop_price
    gross = pnl_usd(
        symbol=original.symbol, direction=original.direction,
        units=original.units, entry_price=original.entry_reference_price,
        exit_price=reference_exit,
    )
    stop_trade = replace(
        original, exit_reason=ExitReason.STOP,
        intrabar_ambiguous=True, exit_reference_price=reference_exit,
        exit_price=reference_exit, gross_pnl_usd=gross,
        net_pnl_usd=gross, slippage_cost_usd=0.0,
        risk_equity_after_usd=10000.0 + gross,
    )
    return replace(
        source, trades=(stop_trade,),
        equity_checkpoints=(
            source.equity_checkpoints[0],
            EquityCheckpoint(
                STAMP + timedelta(minutes=1), 10000.0 + gross,
            ),
        ),
    )


class Phase3AuditSourceIntrabarAmbiguityWitnessTests(unittest.TestCase):
    def test_audit_accepts_ambiguous_stop_with_target_present(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_ambiguous_stop_source_run(), folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )

    def test_audit_refuses_rehashed_ambiguous_target_exit(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _zero_declared_source_slippage_run(Direction.LONG), folder,
            )
            _forge_versioned_trade_execution(
                folder, manifest, "intrabar_ambiguous", True,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "ambiguous stop/target exit witness conflicts",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_source_ambiguous_stop_without_target(self):
        source = _ambiguous_stop_source_run()
        forged = replace(
            source, trades=(replace(source.trades[0], target_price=None),),
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(forged, folder)
            with self.assertRaisesRegex(
                ValueError, "ambiguous stop/target exit witness conflicts",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_generic_ambiguous_target_record_compatibility(self):
        source = _zero_declared_source_slippage_run(Direction.LONG)
        generic = replace(
            source, run_identity={"starting_equity_usd": 10000.0},
            trades=(replace(source.trades[0], intrabar_ambiguous=True),),
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(generic, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )


def _source_scheduled_time_exit_run() -> BacktestRun:
    source = _declared_source_slippage_run(Direction.LONG, "EURUSD")
    exit_timestamp = source.trades[0].exit_timestamp_utc
    descriptor = {
        "decision_id": source.trades[0].decision_id,
        "symbol": source.trades[0].symbol,
        "timestamp_utc": exit_timestamp.isoformat().replace("+00:00", "Z"),
    }
    return replace(
        source,
        run_identity={
            **source.run_identity,
            "scheduled_exits": [descriptor],
        },
        trades=(replace(
            source.trades[0], exit_reason=ExitReason.TIME_EXIT,
        ),),
    )


class Phase3AuditSourceScheduledTimeExitParityTests(unittest.TestCase):
    def test_audit_accepts_matching_declared_source_time_exit(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_source_scheduled_time_exit_run(), folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )

    def test_audit_refuses_rehashed_changed_source_exit_schedule_timestamp(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_scheduled_time_exit_run(), folder,
            )
            wrong_timestamp = (
                (STAMP + timedelta(minutes=2)).isoformat()
                .replace("+00:00", "Z")
            )
            _forge_run_identity_window(
                folder, manifest, "scheduled_exits", [{
                    "decision_id": "SOURCE-SLIP-1",
                    "symbol": "EURUSD",
                    "timestamp_utc": wrong_timestamp,
                }],
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "source time exit conflicts with scheduled exit",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_source_time_exit_without_schedule(self):
        source = _source_scheduled_time_exit_run()
        forged = replace(
            source, run_identity={
                key: val for key, val in source.run_identity.items()
                if key != "scheduled_exits"
            },
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(forged, folder)
            with self.assertRaisesRegex(
                ValueError, "source time exit conflicts with scheduled exit",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_generic_unscheduled_time_exit_envelopes(self):
        source = _source_scheduled_time_exit_run()
        generic = replace(
            source, run_identity={"starting_equity_usd": 10000.0},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(generic, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )


if __name__ == "__main__":
    unittest.main()
