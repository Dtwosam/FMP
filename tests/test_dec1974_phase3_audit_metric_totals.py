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
                target_price=1.10125,
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
            # TARGET parity must remain true so this isolates source gross
            # PnL reconstruction instead of tripping the newer exit guard.
            rows[0]["exit_reference_price"] = 1.1013
            rows[0]["target_price"] = 1.1013
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
                exit_reason=ExitReason.END_OF_DATA,
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
    target = reference_exit
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


def _source_adverse_gap_stop_run(direction: Direction) -> BacktestRun:
    source = _zero_declared_source_slippage_run(direction)
    original = source.trades[0]
    adverse_gap = (
        original.stop_price - 0.0002
        if direction is Direction.LONG
        else original.stop_price + 0.0002
    )
    gross = pnl_usd(
        symbol=original.symbol, direction=direction,
        units=original.units, entry_price=original.entry_reference_price,
        exit_price=adverse_gap,
    )
    gap_trade = replace(
        original, exit_reason=ExitReason.STOP,
        intrabar_ambiguous=False,
        exit_reference_price=adverse_gap, exit_price=adverse_gap,
        gross_pnl_usd=gross, slippage_cost_usd=0.0,
        net_pnl_usd=gross,
        risk_equity_after_usd=10000.0 + gross,
    )
    return replace(
        source, trades=(gap_trade,),
        equity_checkpoints=(
            source.equity_checkpoints[0],
            EquityCheckpoint(
                STAMP + timedelta(minutes=1), 10000.0 + gross,
            ),
        ),
    )


class Phase3AuditSourceStopGapPriceBoundTests(unittest.TestCase):
    def test_audit_accepts_source_long_and_short_adverse_stop_gaps(self):
        for direction in (Direction.LONG, Direction.SHORT):
            with self.subTest(direction=direction):
                with tempfile.TemporaryDirectory() as home:
                    folder = Path(home) / "evidence"
                    write_backtest_artifacts(
                        _source_adverse_gap_stop_run(direction), folder,
                    )
                    self.assertEqual(
                        audit_backtest_artifact_structure(folder)["trade_count"], 1,
                    )

    def test_audit_refuses_rehashed_favorable_long_stop_reference(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _zero_declared_source_slippage_run(Direction.LONG), folder,
            )
            _forge_versioned_trade_execution(
                folder, manifest, "exit_reason", ExitReason.STOP.value,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "stop exit reference improves beyond stop",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_favorable_short_stop_reference(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _zero_declared_source_slippage_run(Direction.SHORT), folder,
            )
            _forge_versioned_trade_execution(
                folder, manifest, "exit_reason", ExitReason.STOP.value,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "stop exit reference improves beyond stop",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_generic_favorable_stop_reference_envelope(self):
        source = _zero_declared_source_slippage_run(Direction.LONG)
        generic = replace(
            source, run_identity={"starting_equity_usd": 10000.0},
            trades=(replace(
                source.trades[0], exit_reason=ExitReason.STOP,
            ),),
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(generic, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )


class Phase3AuditSourceTargetReferenceWitnessTests(unittest.TestCase):
    def test_audit_accepts_source_long_short_and_jpy_exact_targets(self):
        for direction, symbol in (
            (Direction.LONG, "EURUSD"),
            (Direction.SHORT, "GBPUSD"),
            (Direction.LONG, "USDJPY"),
        ):
            with self.subTest(direction=direction, symbol=symbol):
                with tempfile.TemporaryDirectory() as home:
                    folder = Path(home) / "evidence"
                    run = _declared_source_slippage_run(direction, symbol)
                    self.assertEqual(
                        run.trades[0].exit_reference_price,
                        run.trades[0].target_price,
                    )
                    write_backtest_artifacts(run, folder)
                    self.assertEqual(
                        audit_backtest_artifact_structure(folder)["trade_count"], 1,
                    )

    def test_audit_refuses_rehashed_false_target_level(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _declared_source_slippage_run(Direction.LONG, "EURUSD"), folder,
            )
            _forge_versioned_trade_execution(
                folder, manifest, "target_price", 1.102,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "target exit reference conflicts with target_price",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_source_target_exit_without_declared_target(self):
        source = _declared_source_slippage_run(Direction.SHORT, "GBPUSD")
        forged = replace(
            source, trades=(replace(source.trades[0], target_price=None),),
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(forged, folder)
            with self.assertRaisesRegex(
                ValueError, "target exit reference conflicts with target_price",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_generic_target_reference_flexibility(self):
        source = _declared_source_slippage_run(Direction.LONG, "EURUSD")
        generic = replace(
            source, run_identity={"starting_equity_usd": 10000.0},
            trades=(replace(source.trades[0], target_price=1.102),),
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(generic, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )


def _source_rejected_scheduled_exit_run() -> BacktestRun:
    source = _zero_trade_source_engine_run()
    scheduled = {
        "decision_id": "REJECTED-SCHEDULE",
        "symbol": "GBPUSD",
        "timestamp_utc": (
            (STAMP + timedelta(minutes=3)).isoformat()
            .replace("+00:00", "Z")
        ),
    }
    rejection = RejectionRecord(
        decision_id="REJECTED-SCHEDULE", symbol="GBPUSD",
        decision_timestamp_utc=STAMP,
        evaluated_timestamp_utc=STAMP,
        code=RejectionCode.TIMING_CONTRACT,
        explanation="synthetic input has no valid execution bar",
    )
    return replace(
        source,
        run_identity={
            **source.run_identity, "scheduled_exits": [scheduled],
        },
        rejections=(rejection,),
    )


class Phase3AuditSourceScheduledExitOutcomeMembershipTests(unittest.TestCase):
    def test_audit_accepts_scheduled_source_decision_rejected_before_entry(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(
                _source_rejected_scheduled_exit_run(), folder,
            )
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["rejection_count"], 1,
            )

    def test_audit_refuses_rehashed_orphan_scheduled_decision(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_scheduled_time_exit_run(), folder,
            )
            source_schedule = json.loads(
                (folder / "summary.json").read_text("utf-8")
            )["run_identity"]["scheduled_exits"]
            source_schedule.append({
                "decision_id": "ORPHAN",
                "symbol": "GBPUSD",
                "timestamp_utc": (
                    (STAMP + timedelta(minutes=2)).isoformat()
                    .replace("+00:00", "Z")
                ),
            })
            _forge_run_identity_window(
                folder, manifest, "scheduled_exits", source_schedule,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "scheduled exit has no matching decision outcome",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_wrong_scheduled_rejection_symbol(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_rejected_scheduled_exit_run(), folder,
            )
            wrong_schedule = json.loads(
                (folder / "summary.json").read_text("utf-8")
            )["run_identity"]["scheduled_exits"]
            wrong_schedule[0]["symbol"] = "EURUSD"
            _forge_run_identity_window(
                folder, manifest, "scheduled_exits", wrong_schedule,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "scheduled exit has no matching decision outcome",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_generic_scheduled_exit_orphan_flexibility(self):
        source = _source_scheduled_time_exit_run()
        schedule = list(source.run_identity["scheduled_exits"])
        schedule.append({
            "decision_id": "GENERIC-ORPHAN",
            "symbol": "GBPUSD",
            "timestamp_utc": (
                (STAMP + timedelta(minutes=2)).isoformat()
                .replace("+00:00", "Z")
            ),
        })
        generic = replace(
            source, run_identity={
                "starting_equity_usd": 10000.0,
                "scheduled_exits": schedule,
            },
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(generic, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )


def _source_target_before_scheduled_exit_run() -> BacktestRun:
    source = _declared_source_slippage_run(Direction.LONG, "EURUSD")
    scheduled = {
        "decision_id": source.trades[0].decision_id,
        "symbol": source.trades[0].symbol,
        "timestamp_utc": (
            (STAMP + timedelta(minutes=2)).isoformat()
            .replace("+00:00", "Z")
        ),
    }
    return replace(
        source, run_identity={
            **source.run_identity, "scheduled_exits": [scheduled],
        },
    )


class Phase3AuditSourceScheduledExitChronologyTests(unittest.TestCase):
    def test_audit_accepts_source_target_before_later_scheduled_time_exit(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(
                _source_target_before_scheduled_exit_run(), folder,
            )
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )

    def test_audit_refuses_rehashed_schedule_at_source_trade_entry(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_target_before_scheduled_exit_run(), folder,
            )
            _forge_run_identity_window(
                folder, manifest, "scheduled_exits", [{
                    "decision_id": "SOURCE-SLIP-1",
                    "symbol": "EURUSD",
                    "timestamp_utc": STAMP.isoformat().replace("+00:00", "Z"),
                }],
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "scheduled exit is not later than decision entry",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_schedule_at_rejection_decision_time(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_rejected_scheduled_exit_run(), folder,
            )
            _forge_run_identity_window(
                folder, manifest, "scheduled_exits", [{
                    "decision_id": "REJECTED-SCHEDULE",
                    "symbol": "GBPUSD",
                    "timestamp_utc": STAMP.isoformat().replace("+00:00", "Z"),
                }],
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "scheduled exit is not later than decision entry",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_generic_same_time_scheduled_exit_metadata(self):
        source = _source_target_before_scheduled_exit_run()
        generic = replace(
            source, run_identity={
                "starting_equity_usd": 10000.0,
                "scheduled_exits": [{
                    "decision_id": "SOURCE-SLIP-1",
                    "symbol": "EURUSD",
                    "timestamp_utc": STAMP.isoformat().replace("+00:00", "Z"),
                }],
            },
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(generic, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )


def _source_no_trade_rejection_run() -> BacktestRun:
    source = _zero_trade_source_engine_run()
    no_trade = RejectionRecord(
        decision_id="SOURCE-NO-TRADE", symbol="EURUSD",
        decision_timestamp_utc=STAMP,
        evaluated_timestamp_utc=STAMP,
        code=RejectionCode.NO_TRADE,
        explanation="directional signal deliberately absent",
    )
    return replace(source, rejections=(no_trade,))


class Phase3AuditSourceNoTradeRejectionContractTests(unittest.TestCase):
    def test_audit_accepts_source_no_trade_at_decision_time(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_source_no_trade_rejection_run(), folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["rejection_count"], 1,
            )

    def test_audit_refuses_rehashed_delayed_source_no_trade_evaluation(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_no_trade_rejection_run(), folder,
            )
            _forge_rejection_field(
                folder, manifest, "evaluated_timestamp_utc",
                (STAMP + timedelta(minutes=1)).isoformat()
                .replace("+00:00", "Z"),
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "NO_TRADE evaluation differs from decision",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_source_no_trade_with_scheduled_exit(self):
        source = _source_no_trade_rejection_run()
        forged = replace(
            source,
            run_identity={
                **source.run_identity,
                "scheduled_exits": [{
                    "decision_id": "SOURCE-NO-TRADE",
                    "symbol": "EURUSD",
                    "timestamp_utc": (
                        (STAMP + timedelta(minutes=2)).isoformat()
                        .replace("+00:00", "Z")
                    ),
                }],
            },
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(forged, folder)
            with self.assertRaisesRegex(
                ValueError, "NO_TRADE decision cannot have scheduled exit",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_generic_delayed_no_trade_and_schedule(self):
        source = _source_no_trade_rejection_run()
        generic = replace(
            source,
            run_identity={
                "starting_equity_usd": 10000.0,
                "scheduled_exits": [{
                    "decision_id": "SOURCE-NO-TRADE",
                    "symbol": "EURUSD",
                    "timestamp_utc": (
                        (STAMP + timedelta(minutes=2)).isoformat()
                        .replace("+00:00", "Z")
                    ),
                }],
            },
            rejections=(replace(
                source.rejections[0],
                evaluated_timestamp_utc=STAMP + timedelta(minutes=1),
            ),),
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(generic, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["rejection_count"], 1,
            )


class Phase3AuditSourceGrossPnLMutationPrecedenceTests(unittest.TestCase):
    def test_audit_refuses_wrong_units_when_target_and_cost_unchanged(self):
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
                    _forge_versioned_trade_execution(
                        folder, manifest, "units", 11000,
                    )
                    self.assertEqual(verify_backtest_artifacts(folder), manifest)
                    with self.assertRaisesRegex(
                        ValueError, "gross PnL conflicts with reference-price",
                    ):
                        audit_backtest_artifact_structure(folder)

    def test_audit_refuses_wrong_usdjpy_units_before_slippage_reconciliation(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _declared_source_slippage_run(Direction.LONG, "USDJPY"), folder,
            )
            _forge_versioned_trade_execution(
                folder, manifest, "units", 11000,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "gross PnL conflicts with reference-price",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_generic_synthetic_gross_pnl_formula_flexibility(self):
        source = _declared_source_slippage_run(Direction.LONG, "EURUSD")
        generic = replace(
            source, run_identity={"starting_equity_usd": 10000.0},
            trades=(replace(source.trades[0], units=11000),),
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(generic, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )


class Phase3AuditSourceScheduledExitClosePrecedenceTests(unittest.TestCase):
    def test_audit_accepts_scheduled_close_or_earlier_target(self):
        for run in (
            _source_scheduled_time_exit_run(),
            _source_target_before_scheduled_exit_run(),
        ):
            with self.subTest(reason=run.trades[0].exit_reason):
                with tempfile.TemporaryDirectory() as home:
                    folder = Path(home) / "evidence"
                    write_backtest_artifacts(run, folder)
                    self.assertEqual(
                        audit_backtest_artifact_structure(folder)["trade_count"], 1,
                    )

    def test_audit_refuses_rehashed_target_at_exact_scheduled_close(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_target_before_scheduled_exit_run(), folder,
            )
            _forge_run_identity_window(
                folder, manifest, "scheduled_exits", [{
                    "decision_id": "SOURCE-SLIP-1",
                    "symbol": "EURUSD",
                    "timestamp_utc": (
                        (STAMP + timedelta(minutes=1)).isoformat()
                        .replace("+00:00", "Z")
                    ),
                }],
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "scheduled close conflicts with exit reason",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_stop_at_exact_scheduled_close(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _ambiguous_stop_source_run(), folder,
            )
            _forge_run_identity_window(
                folder, manifest, "scheduled_exits", [{
                    "decision_id": "SOURCE-SLIP-1",
                    "symbol": "EURUSD",
                    "timestamp_utc": (
                        (STAMP + timedelta(minutes=1)).isoformat()
                        .replace("+00:00", "Z")
                    ),
                }],
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "scheduled close conflicts with exit reason",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_generic_same_time_target_and_schedule(self):
        source = _source_target_before_scheduled_exit_run()
        generic = replace(
            source, run_identity={
                "starting_equity_usd": 10000.0,
                "scheduled_exits": [{
                    "decision_id": "SOURCE-SLIP-1",
                    "symbol": "EURUSD",
                    "timestamp_utc": (
                        (STAMP + timedelta(minutes=1)).isoformat()
                        .replace("+00:00", "Z")
                    ),
                }],
            },
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(generic, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )


def _mixed_same_time_scheduled_source_run() -> BacktestRun:
    source = _same_exit_source_engine_run()
    first, second = source.trades
    # Source realization order: Z TIME_EXIT, then A TARGET; the writer
    # publishes equal-time trade rows in A/Z trade-ID order.
    scheduled = [{
        "decision_id": first.decision_id,
        "symbol": first.symbol,
        "timestamp_utc": first.exit_timestamp_utc.isoformat()
        .replace("+00:00", "Z"),
    }]
    return replace(
        source,
        run_identity={**source.run_identity, "scheduled_exits": scheduled},
        trades=(
            replace(first, exit_reason=ExitReason.TIME_EXIT),
            second,
        ),
    )


class Phase3AuditSameTimeMixedSourceExitWitnessTests(unittest.TestCase):
    def test_audit_accepts_mixed_scheduled_and_target_equal_time_closes(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(
                _mixed_same_time_scheduled_source_run(), folder,
            )
            rows = [
                json.loads(line) for line in
                (folder / "trades.jsonl").read_text("utf-8").splitlines()
            ]
            self.assertEqual(
                [row["trade_id"] for row in rows], ["A-CLOSE", "Z-CLOSE"],
            )
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 2,
            )

    def test_audit_refuses_rehashed_target_with_new_same_time_schedule(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _mixed_same_time_scheduled_source_run(), folder,
            )
            same_time = (
                (STAMP + timedelta(minutes=1)).isoformat()
                .replace("+00:00", "Z")
            )
            _forge_run_identity_window(
                folder, manifest, "scheduled_exits", [
                    {
                        "decision_id": "A-CLOSE",
                        "symbol": "EURUSD",
                        "timestamp_utc": same_time,
                    },
                    {
                        "decision_id": "Z-CLOSE",
                        "symbol": "EURUSD",
                        "timestamp_utc": same_time,
                    },
                ],
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "scheduled close conflicts with exit reason",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_unscheduled_time_exit_in_same_time_group(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _mixed_same_time_scheduled_source_run(), folder,
            )
            # Canonical order places A before Z, despite Z closing first.
            _forge_versioned_trade_execution(
                folder, manifest, "exit_reason", ExitReason.TIME_EXIT.value,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "time exit conflicts with scheduled exit identity",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_keeps_generic_target_same_time_schedule_compatibility(self):
        source = _declared_source_slippage_run(Direction.LONG, "EURUSD")
        generic = replace(
            source, run_identity={
                "starting_equity_usd": 10000.0,
                "scheduled_exits": [{
                    "decision_id": source.trades[0].decision_id,
                    "symbol": source.trades[0].symbol,
                    "timestamp_utc": (
                        source.trades[0].exit_timestamp_utc.isoformat()
                        .replace("+00:00", "Z")
                    ),
                }],
            },
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(generic, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )


class Phase3AuditSourceInitialEquityExactCopyTests(unittest.TestCase):
    def test_audit_accepts_exact_source_initial_checkpoint_copy(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(
                _zero_trade_source_engine_run(), folder,
            )
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 0,
            )

    def test_audit_refuses_rehashed_sub_tolerance_initial_equity_drift(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _zero_trade_source_engine_run(), folder,
            )
            # Former isclose(rel_tol=1e-12, abs_tol=1e-8) admitted this
            # drift even though both source fields copy one numeric value.
            _forge_checkpoint_summary(
                folder, manifest, 0, "realized_risk_equity_usd",
                10000.000000001,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "initial checkpoint equity conflicts with starting equity",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_generic_initial_equity_numeric_tolerance(self):
        source = _zero_trade_source_engine_run()
        generic = replace(
            source,
            run_identity={"starting_equity_usd": 10000.0},
            equity_checkpoints=(
                EquityCheckpoint(STAMP, 10000.000000001),
            ),
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(generic, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 0,
            )


def _source_fixed_commission_run(rate: float) -> BacktestRun:
    source = (
        _versioned_builtin_zero_cost_run()
        if rate == 0.0 else _source_engine_checkpoint_run()
    )
    return replace(
        source, run_identity={
            **source.run_identity,
            "commission_model": {
                "model": "fixed_per_million_per_side",
                "usd_per_million_per_side": rate,
            },
        },
    )


class Phase3AuditSourceExactFixedCommissionTests(unittest.TestCase):
    def test_audit_accepts_exact_fixed_rate_or_zero_rate_source_fees(self):
        for rate in (0.0, 25.0):
            with self.subTest(rate=rate):
                with tempfile.TemporaryDirectory() as home:
                    folder = Path(home) / "evidence"
                    write_backtest_artifacts(
                        _source_fixed_commission_run(rate), folder,
                    )
                    self.assertEqual(
                        audit_backtest_artifact_structure(folder)["trade_count"], 2,
                    )

    def test_audit_refuses_rehashed_near_equal_fixed_commission_credit_swap(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_fixed_commission_run(25.0), folder,
            )
            # Preserve net PnL exactly through an opposite financing change.
            # The old 1e-8 absolute tolerance admitted the false built-in fee.
            _forge_versioned_trade_costs(
                folder, manifest, 0.500000001, -0.500000001,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "source fixed commission conflicts with trade costs",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_near_equal_zero_rate_built_in_fee(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_fixed_commission_run(0.0), folder,
            )
            _forge_versioned_trade_costs(
                folder, manifest, 0.000000001, -0.000000001,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "source fixed commission conflicts with trade costs",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_generic_fee_model_economic_flexibility(self):
        source = _source_fixed_commission_run(25.0)
        trades = tuple(source.trades)
        first = replace(
            trades[0],
            commission_cost_usd=0.500000001,
            financing_cost_usd=-0.500000001,
        )
        generic = replace(
            source,
            run_identity={
                "starting_equity_usd": 10000.0,
                "commission_model": {
                    "model": "fixed_per_million_per_side",
                    "usd_per_million_per_side": 25.0,
                },
            },
            trades=(first, *trades[1:]),
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(generic, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 2,
            )


class Phase3AuditSourceExactModeledSlippageTests(unittest.TestCase):
    def test_audit_accepts_exact_source_slippage_for_pairs_and_zero_pips(self):
        runs = (
            _declared_source_slippage_run(Direction.LONG, "EURUSD"),
            _declared_source_slippage_run(Direction.SHORT, "GBPUSD"),
            _declared_source_slippage_run(Direction.LONG, "USDJPY"),
            _zero_declared_source_slippage_run(Direction.LONG),
        )
        for run in runs:
            with self.subTest(
                symbol=run.trades[0].symbol,
                pips=run.run_identity["slippage_pips"],
            ):
                with tempfile.TemporaryDirectory() as home:
                    folder = Path(home) / "evidence"
                    write_backtest_artifacts(run, folder)
                    self.assertEqual(
                        audit_backtest_artifact_structure(folder)["trade_count"], 1,
                    )

    def test_audit_refuses_rehashed_near_equal_positive_slippage_cost(self):
        source = _declared_source_slippage_run(Direction.LONG, "EURUSD")
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_versioned_trade_execution(
                folder, manifest, "slippage_cost_usd",
                source.trades[0].slippage_cost_usd + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "slippage cost conflicts with execution prices",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_near_zero_modeled_slippage(self):
        source = _zero_declared_source_slippage_run(Direction.SHORT)
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_versioned_trade_execution(
                folder, manifest, "slippage_cost_usd", 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "slippage cost conflicts with execution prices",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_keeps_generic_near_equal_slippage_cost_flexibility(self):
        source = _declared_source_slippage_run(Direction.LONG, "EURUSD")
        generic = replace(
            source,
            run_identity={"starting_equity_usd": 10000.0},
            trades=(replace(
                source.trades[0],
                slippage_cost_usd=source.trades[0].slippage_cost_usd + 1e-9,
            ),),
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(generic, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )


class Phase3AuditSourceExactReferenceGrossPnLTests(unittest.TestCase):
    def test_audit_accepts_source_gross_from_reference_prices(self):
        for direction, symbol in (
            (Direction.LONG, "EURUSD"),
            (Direction.SHORT, "GBPUSD"),
            (Direction.LONG, "USDJPY"),
        ):
            with self.subTest(direction=direction, symbol=symbol):
                with tempfile.TemporaryDirectory() as home:
                    folder = Path(home) / "evidence"
                    write_backtest_artifacts(
                        _declared_source_slippage_run(direction, symbol),
                        folder,
                    )
                    self.assertEqual(
                        audit_backtest_artifact_structure(folder)["trade_count"], 1,
                    )

    def test_audit_refuses_rehashed_near_equal_eurusd_source_gross(self):
        source = _declared_source_slippage_run(Direction.LONG, "EURUSD")
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_versioned_trade_execution(
                folder, manifest, "gross_pnl_usd",
                source.trades[0].gross_pnl_usd + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "gross PnL conflicts with reference-price",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_near_equal_jpy_converted_gross(self):
        source = _declared_source_slippage_run(Direction.LONG, "USDJPY")
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_versioned_trade_execution(
                folder, manifest, "gross_pnl_usd",
                source.trades[0].gross_pnl_usd + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "gross PnL conflicts with reference-price",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_generic_near_equal_gross_pnl_tolerance(self):
        source = _declared_source_slippage_run(Direction.LONG, "EURUSD")
        generic = replace(
            source,
            run_identity={"starting_equity_usd": 10000.0},
            trades=(replace(
                source.trades[0],
                gross_pnl_usd=source.trades[0].gross_pnl_usd + 1e-9,
            ),),
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(generic, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )


def _combined_source_economic_model_run(
    direction: Direction = Direction.LONG,
    symbol: str = "EURUSD",
) -> BacktestRun:
    source = _declared_source_slippage_run(direction, symbol)
    trade = source.trades[0]
    commission = 2 * (trade.units / 1_000_000 * 25.0)
    modeled_net = trade.net_pnl_usd - commission
    return replace(
        source,
        run_identity={
            **source.run_identity,
            "commission_model": {
                "model": "fixed_per_million_per_side",
                "usd_per_million_per_side": 25.0,
            },
            "financing_model": {"model": "zero_financing"},
        },
        trades=(replace(
            trade, commission_cost_usd=commission,
            net_pnl_usd=modeled_net,
            risk_equity_after_usd=10000.0 + modeled_net,
        ),),
        equity_checkpoints=(
            source.equity_checkpoints[0],
            EquityCheckpoint(
                STAMP + timedelta(minutes=1), 10000.0 + modeled_net,
            ),
        ),
    )


class Phase3AuditCombinedSourceEconomicModelWitnessTests(unittest.TestCase):
    def test_audit_accepts_joint_pip_gross_slippage_commission_and_net(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(
                _combined_source_economic_model_run(), folder,
            )
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )

    def test_audit_refuses_joint_model_near_equal_rehashed_gross(self):
        source = _combined_source_economic_model_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_versioned_trade_execution(
                folder, manifest, "gross_pnl_usd",
                source.trades[0].gross_pnl_usd + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "gross PnL conflicts with reference-price",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_joint_model_near_equal_rehashed_slippage(self):
        source = _combined_source_economic_model_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_versioned_trade_execution(
                folder, manifest, "slippage_cost_usd",
                source.trades[0].slippage_cost_usd + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "slippage cost conflicts with execution prices",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_joint_model_near_equal_rehashed_commission(self):
        source = _combined_source_economic_model_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_versioned_trade_execution(
                folder, manifest, "commission_cost_usd",
                source.trades[0].commission_cost_usd + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "source fixed commission conflicts with trade costs",
            ):
                audit_backtest_artifact_structure(folder)


class Phase3AuditCrossPairCombinedSourceEconomicTests(unittest.TestCase):
    def test_audit_accepts_combined_fixed_fee_on_short_jpy_and_gbp_pairs(self):
        for symbol in ("USDJPY", "GBPUSD"):
            with self.subTest(symbol=symbol):
                with tempfile.TemporaryDirectory() as home:
                    folder = Path(home) / "evidence"
                    run = _combined_source_economic_model_run(
                        Direction.SHORT, symbol,
                    )
                    write_backtest_artifacts(run, folder)
                    self.assertEqual(
                        audit_backtest_artifact_structure(folder)["trade_count"], 1,
                    )

    def test_audit_refuses_rehashed_near_equal_fixed_model_rate(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _combined_source_economic_model_run(), folder,
            )
            # The rate shift changes expected aggregate source fees by
            # only 2e-9 for 10,000 units, inside the old 1e-8 tolerance.
            _forge_run_identity_window(
                folder, manifest, "commission_model", {
                    "model": "fixed_per_million_per_side",
                    "usd_per_million_per_side": 25.0000001,
                },
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "source fixed commission conflicts with trade costs",
            ):
                audit_backtest_artifact_structure(folder)


class Phase3AuditSourceCompensatedEconomicTamperTests(unittest.TestCase):
    def test_audit_refuses_compensated_gross_and_slippage_drift(self):
        source = _combined_source_economic_model_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            delta = 0.00001
            _forge_versioned_trade_execution(
                folder, manifest, "gross_pnl_usd",
                source.trades[0].gross_pnl_usd + delta,
            )
            _forge_versioned_trade_execution(
                folder, manifest, "slippage_cost_usd",
                source.trades[0].slippage_cost_usd + delta,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "gross PnL conflicts with reference-price",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_compensated_slippage_and_commission_drift(self):
        source = _combined_source_economic_model_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            delta = 0.00001
            _forge_versioned_trade_execution(
                folder, manifest, "slippage_cost_usd",
                source.trades[0].slippage_cost_usd + delta,
            )
            _forge_versioned_trade_execution(
                folder, manifest, "commission_cost_usd",
                source.trades[0].commission_cost_usd - delta,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "slippage cost conflicts with execution prices",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_compensated_commission_and_financing_drift(self):
        source = _combined_source_economic_model_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            delta = 0.00001
            _forge_versioned_trade_execution(
                folder, manifest, "commission_cost_usd",
                source.trades[0].commission_cost_usd + delta,
            )
            _forge_versioned_trade_execution(
                folder, manifest, "financing_cost_usd",
                -delta,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "source fixed commission conflicts with trade costs",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_generic_compensated_gross_slip_flexibility(self):
        source = _combined_source_economic_model_run()
        item = source.trades[0]
        delta = 0.00001
        generic = replace(
            source,
            run_identity={
                key: value for key, value in source.run_identity.items()
                if key != "backtest_engine_version"
            },
            trades=(replace(
                item, gross_pnl_usd=item.gross_pnl_usd + delta,
                slippage_cost_usd=item.slippage_cost_usd + delta,
            ),),
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(generic, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )


class Phase3AuditExactSourceNetPnLTests(unittest.TestCase):
    def test_audit_accepts_exact_joint_source_net_pnl(self):
        for direction, symbol in (
            (Direction.LONG, "EURUSD"),
            (Direction.SHORT, "GBPUSD"),
            (Direction.SHORT, "USDJPY"),
        ):
            with self.subTest(direction=direction, symbol=symbol):
                with tempfile.TemporaryDirectory() as home:
                    folder = Path(home) / "evidence"
                    write_backtest_artifacts(
                        _combined_source_economic_model_run(direction, symbol),
                        folder,
                    )
                    self.assertEqual(
                        audit_backtest_artifact_structure(folder)["trade_count"], 1,
                    )

    def test_audit_refuses_rehashed_near_equal_source_net_pnl(self):
        source = _combined_source_economic_model_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_versioned_trade_execution(
                folder, manifest, "net_pnl_usd",
                source.trades[0].net_pnl_usd + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "net PnL cost reconciliation mismatch",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_generic_near_equal_net_pnl_tolerance(self):
        source = _combined_source_economic_model_run()
        generic = replace(
            source,
            run_identity={"starting_equity_usd": 10000.0},
            trades=(replace(
                source.trades[0],
                net_pnl_usd=source.trades[0].net_pnl_usd + 1e-9,
            ),),
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(generic, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )


class Phase3AuditExactSourceEquityAdditionTests(unittest.TestCase):
    def test_audit_accepts_exact_source_trade_equity_for_both_sides(self):
        for direction, symbol in (
            (Direction.LONG, "EURUSD"),
            (Direction.SHORT, "USDJPY"),
        ):
            with self.subTest(direction=direction, symbol=symbol):
                with tempfile.TemporaryDirectory() as home:
                    folder = Path(home) / "evidence"
                    write_backtest_artifacts(
                        _combined_source_economic_model_run(direction, symbol),
                        folder,
                    )
                    self.assertEqual(
                        audit_backtest_artifact_structure(folder)["trade_count"], 1,
                    )

    def test_audit_refuses_rehashed_near_equal_source_equity_after(self):
        source = _combined_source_economic_model_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_versioned_trade_execution(
                folder, manifest, "risk_equity_after_usd",
                source.trades[0].risk_equity_after_usd + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "realized equity conflicts with net PnL",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_generic_near_equal_equity_transition_tolerance(self):
        source = _combined_source_economic_model_run()
        generic = replace(
            source,
            run_identity={"starting_equity_usd": 10000.0},
            trades=(replace(
                source.trades[0],
                risk_equity_after_usd=source.trades[0].risk_equity_after_usd + 1e-9,
            ),),
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(generic, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )


def _source_custom_financing_run(financing: float) -> BacktestRun:
    source = _combined_source_economic_model_run()
    prior = source.trades[0]
    # The built-in zero-financing model cannot emit a debit or credit.
    # A valid user-defined source FinancingModel may return signed values.
    adjusted_net = (
        prior.gross_pnl_usd - prior.slippage_cost_usd
        - prior.commission_cost_usd - financing
    )
    adjusted = replace(
        prior, financing_cost_usd=financing,
        net_pnl_usd=adjusted_net,
        risk_equity_after_usd=10000.0 + adjusted_net,
    )
    return replace(
        source,
        run_identity={
            **source.run_identity,
            "financing_model": {"model": "source_custom_signed_financing"},
        },
        trades=(adjusted,),
        equity_checkpoints=(
            source.equity_checkpoints[0],
            EquityCheckpoint(
                STAMP + timedelta(minutes=1), 10000.0 + adjusted_net,
            ),
        ),
    )


class Phase3AuditSignedCustomSourceFinancingTests(unittest.TestCase):
    def test_audit_accepts_source_custom_financing_debit_and_credit(self):
        for financing in (-1.25, 1.25):
            with self.subTest(financing=financing):
                with tempfile.TemporaryDirectory() as home:
                    folder = Path(home) / "evidence"
                    write_backtest_artifacts(
                        _source_custom_financing_run(financing), folder,
                    )
                    self.assertEqual(
                        audit_backtest_artifact_structure(folder)["trade_count"], 1,
                    )

    def test_audit_refuses_rehashed_near_equal_signed_financing_drift(self):
        for financing in (-1.25, 1.25):
            with self.subTest(financing=financing):
                with tempfile.TemporaryDirectory() as home:
                    source = _source_custom_financing_run(financing)
                    folder = Path(home) / "evidence"
                    manifest = write_backtest_artifacts(source, folder)
                    _forge_versioned_trade_execution(
                        folder, manifest, "financing_cost_usd",
                        financing + 1e-9,
                    )
                    self.assertEqual(verify_backtest_artifacts(folder), manifest)
                    with self.assertRaisesRegex(
                        ValueError, "net PnL cost reconciliation mismatch",
                    ):
                        audit_backtest_artifact_structure(folder)

    def test_audit_preserves_generic_financing_near_equal_tolerance(self):
        source = _source_custom_financing_run(-1.25)
        generic = replace(
            source,
            run_identity={"starting_equity_usd": 10000.0},
            trades=(replace(
                source.trades[0], financing_cost_usd=-1.249999999,
            ),),
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(generic, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )


def _source_with_complete_economic_metrics() -> BacktestRun:
    source = _combined_source_economic_model_run()
    trade = source.trades[0]
    explicit_cost = (
        trade.slippage_cost_usd + trade.commission_cost_usd
        + trade.financing_cost_usd
    )
    return replace(
        source, metrics={
            "trade_count": 1,
            "net_pnl_usd": trade.net_pnl_usd,
            "slippage_cost_usd": trade.slippage_cost_usd,
            "commission_cost_usd": trade.commission_cost_usd,
            "financing_cost_usd": trade.financing_cost_usd,
            "total_explicit_cost_usd": explicit_cost,
        },
    )


class Phase3AuditExactSourceAggregateMetricTests(unittest.TestCase):
    def test_audit_accepts_source_aggregate_economic_metrics(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(
                _source_with_complete_economic_metrics(), folder,
            )
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )

    def test_audit_refuses_near_equal_rehashed_source_metric_net(self):
        source = _source_with_complete_economic_metrics()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_metrics(
                folder, manifest, "net_pnl_usd",
                source.metrics["net_pnl_usd"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric net_pnl_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_near_equal_source_total_explicit_cost_metric(self):
        source = _source_with_complete_economic_metrics()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_metrics(
                folder, manifest, "total_explicit_cost_usd",
                source.metrics["total_explicit_cost_usd"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric total_explicit_cost_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_keeps_generic_metric_aggregate_summation_tolerance(self):
        source = _source_with_complete_economic_metrics()
        generic = replace(
            source, run_identity={"starting_equity_usd": 10000.0},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(generic, folder)
            # The writer correctly refuses contradictory claimed metrics.
            # To test the auditor's generic numeric tolerance, mutate and
            # rehash an already-written *canonical* metrics payload.
            payload_path = folder / "metrics.json"
            metrics = json.loads(payload_path.read_text("utf-8"))
            metrics["net_pnl_usd"] += 1e-9
            payload = (
                json.dumps(
                    metrics, sort_keys=True, indent=2,
                    ensure_ascii=False, allow_nan=False,
                ) + "\n"
            ).encode("utf-8")
            payload_path.write_bytes(payload)
            for record in manifest["artifacts"]:
                if record["path"] == "metrics.json":
                    record["size_bytes"] = len(payload)
                    record["sha256"] = hashlib.sha256(payload).hexdigest()
            (folder / "manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8",
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )


def _source_same_time_with_aggregate_economics() -> BacktestRun:
    source = _same_exit_source_engine_run()
    trades = source.trades
    slippage = sum(trade.slippage_cost_usd for trade in trades)
    commission = sum(trade.commission_cost_usd for trade in trades)
    financing = sum(trade.financing_cost_usd for trade in trades)
    return replace(source, metrics={
        "trade_count": len(trades),
        "net_pnl_usd": sum(trade.net_pnl_usd for trade in trades),
        "slippage_cost_usd": slippage,
        "commission_cost_usd": commission,
        "financing_cost_usd": financing,
        "total_explicit_cost_usd": slippage + commission + financing,
    })


class Phase3AuditZeroAndSameTimeSourceMetricTests(unittest.TestCase):
    def test_audit_accepts_same_time_source_metrics_in_publication_order(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            source = _source_same_time_with_aggregate_economics()
            write_backtest_artifacts(source, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 2,
            )

    def test_audit_accepts_zero_trade_source_zero_metric_economics(self):
        source = _zero_trade_source_engine_run()
        zero = replace(source, metrics={
            "trade_count": 0, "net_pnl_usd": 0,
            "slippage_cost_usd": 0, "commission_cost_usd": 0,
            "financing_cost_usd": 0, "total_explicit_cost_usd": 0,
        })
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(zero, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 0,
            )

    def test_audit_refuses_rehashed_near_zero_metric_without_trades(self):
        source = _zero_trade_source_engine_run()
        zero = replace(source, metrics={
            "trade_count": 0, "net_pnl_usd": 0.0,
        })
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(zero, folder)
            _forge_metrics(folder, manifest, "net_pnl_usd", 1e-9)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric net_pnl_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)


def _source_with_exact_net_return_metric() -> BacktestRun:
    source = _source_with_complete_economic_metrics()
    return replace(source, metrics={
        **source.metrics,
        "net_return": source.metrics["net_pnl_usd"] / 10000.0,
    })


class Phase3AuditExactSourceNetReturnTests(unittest.TestCase):
    def test_audit_accepts_source_net_return_from_ledger_and_start(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_source_with_exact_net_return_metric(), folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )

    def test_audit_refuses_rehashed_sub_tolerance_net_return_drift(self):
        source = _source_with_exact_net_return_metric()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_metrics(
                folder, manifest, "net_return",
                source.metrics["net_return"] + 1e-13,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "net_return conflicts with starting equity and trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_generic_net_return_rounding_tolerance(self):
        source = _source_with_exact_net_return_metric()
        generic = replace(
            source, run_identity={"starting_equity_usd": 10000.0},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(generic, folder)
            _forge_canonical_metric(
                folder, manifest, "net_return",
                source.metrics["net_return"] + 1e-13,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )


class Phase3AuditZeroAndSameTimeSourceNetReturnTests(unittest.TestCase):
    def test_audit_accepts_source_same_time_close_net_return(self):
        source = _source_same_time_with_aggregate_economics()
        run = replace(
            source, metrics={
                **source.metrics,
                "net_return": source.metrics["net_pnl_usd"] / 10000.0,
            },
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 2,
            )

    def test_audit_accepts_source_zero_trade_zero_net_return(self):
        source = _zero_trade_source_engine_run()
        run = replace(
            source, metrics={
                "trade_count": 0, "net_pnl_usd": 0.0,
                "net_return": 0.0,
            },
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 0,
            )

    def test_audit_refuses_rehashed_near_zero_empty_source_net_return(self):
        source = _zero_trade_source_engine_run()
        run = replace(
            source, metrics={
                "trade_count": 0, "net_pnl_usd": 0.0,
                "net_return": 0.0,
            },
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            _forge_metrics(folder, manifest, "net_return", 1e-13)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "net_return conflicts with starting equity and trade ledger",
            ):
                audit_backtest_artifact_structure(folder)


def _source_winning_losing_profit_metrics_run() -> BacktestRun:
    winner_source = _combined_source_economic_model_run()
    loser_source = _source_adverse_gap_stop_run(Direction.LONG)
    winner = winner_source.trades[0]
    loser = loser_source.trades[0]
    after_winner = winner.risk_equity_after_usd
    realized_after_loss = after_winner + loser.net_pnl_usd
    loser = replace(
        loser, decision_id="MIXED-LOSS", trade_id="MIXED-LOSS",
        entry_timestamp_utc=STAMP + timedelta(minutes=1),
        exit_timestamp_utc=STAMP + timedelta(minutes=2),
        risk_equity_before_usd=after_winner,
        risk_equity_after_usd=realized_after_loss,
    )
    gross_profit = winner.net_pnl_usd
    gross_loss = -loser.net_pnl_usd
    return BacktestRun(
        run_identity={
            "backtest_engine_version": BACKTEST_ENGINE_VERSION,
            "starting_equity_usd": 10000.0,
        },
        trades=(winner, loser), rejections=(),
        equity_checkpoints=(
            EquityCheckpoint(STAMP, 10000.0),
            EquityCheckpoint(STAMP + timedelta(minutes=1), after_winner),
            EquityCheckpoint(
                STAMP + timedelta(minutes=2), realized_after_loss,
            ),
        ),
        metrics={
            "trade_count": 2,
            "net_pnl_usd": winner.net_pnl_usd + loser.net_pnl_usd,
            "gross_profit_usd": gross_profit,
            "gross_loss_usd": gross_loss,
            "profit_factor": gross_profit / gross_loss,
        },
    )


class Phase3AuditExactSourceProfitabilityMetricsTests(unittest.TestCase):
    def test_audit_accepts_source_winning_and_losing_profit_metrics(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(
                _source_winning_losing_profit_metrics_run(), folder,
            )
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 2,
            )

    def test_audit_refuses_rehashed_source_gross_profit_metric_drift(self):
        source = _source_winning_losing_profit_metrics_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_metrics(
                folder, manifest, "gross_profit_usd",
                source.metrics["gross_profit_usd"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric gross_profit_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_source_profit_factor_metric_drift(self):
        source = _source_winning_losing_profit_metrics_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_metrics(
                folder, manifest, "profit_factor",
                source.metrics["profit_factor"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric profit_factor conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_keeps_generic_near_equal_profitability_tolerance(self):
        source = _source_winning_losing_profit_metrics_run()
        generic = replace(
            source, run_identity={"starting_equity_usd": 10000.0},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(generic, folder)
            _forge_canonical_metric(
                folder, manifest, "gross_profit_usd",
                source.metrics["gross_profit_usd"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 2,
            )


def _source_with_exact_trade_distribution_metrics() -> BacktestRun:
    source = _source_winning_losing_profit_metrics_run()
    winner, loser = source.trades
    return replace(source, metrics={
        **source.metrics,
        "win_rate": 0.5,
        "average_win_usd": winner.net_pnl_usd,
        "average_loss_usd": loser.net_pnl_usd,
        "expectancy_usd": (
            (winner.net_pnl_usd + loser.net_pnl_usd) / 2
        ),
        "longest_winning_streak": 1,
        "longest_losing_streak": 1,
    })


class Phase3AuditExactSourceTradeDistributionMetricsTests(unittest.TestCase):
    def test_audit_accepts_source_winner_loser_average_and_streak_metrics(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(
                _source_with_exact_trade_distribution_metrics(), folder,
            )
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 2,
            )

    def test_audit_refuses_rehashed_near_equal_source_win_rate(self):
        source = _source_with_exact_trade_distribution_metrics()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_metrics(
                folder, manifest, "win_rate",
                source.metrics["win_rate"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric win_rate conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_near_equal_source_expectancy(self):
        source = _source_with_exact_trade_distribution_metrics()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_metrics(
                folder, manifest, "expectancy_usd",
                source.metrics["expectancy_usd"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric expectancy_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_generic_near_equal_trade_win_rate_tolerance(self):
        source = _source_with_exact_trade_distribution_metrics()
        generic = replace(
            source, run_identity={"starting_equity_usd": 10000.0},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(generic, folder)
            _forge_canonical_metric(
                folder, manifest, "win_rate",
                source.metrics["win_rate"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 2,
            )


def _source_with_exact_drawdown_metrics() -> BacktestRun:
    source = _source_winning_losing_profit_metrics_run()
    first_peak = source.equity_checkpoints[1].realized_risk_equity_usd
    final_equity = source.equity_checkpoints[2].realized_risk_equity_usd
    maximum_drawdown = first_peak - final_equity
    return replace(source, metrics={
        **source.metrics,
        "max_drawdown_usd": maximum_drawdown,
        "max_drawdown_fraction": maximum_drawdown / first_peak,
        "recovery_factor": source.metrics["net_pnl_usd"] / maximum_drawdown,
    })


class Phase3AuditExactSourceDrawdownMetricsTests(unittest.TestCase):
    def test_audit_accepts_source_drawdown_fraction_and_recovery_metrics(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(
                _source_with_exact_drawdown_metrics(), folder,
            )
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 2,
            )

    def test_audit_refuses_rehashed_near_equal_source_drawdown_usd(self):
        source = _source_with_exact_drawdown_metrics()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_metrics(
                folder, manifest, "max_drawdown_usd",
                source.metrics["max_drawdown_usd"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric max_drawdown_usd conflicts with checkpoint curve",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_near_equal_source_drawdown_fraction(self):
        source = _source_with_exact_drawdown_metrics()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_metrics(
                folder, manifest, "max_drawdown_fraction",
                source.metrics["max_drawdown_fraction"] + 1e-13,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric max_drawdown_fraction conflicts with checkpoint curve",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_keeps_generic_drawdown_metric_tolerance(self):
        source = _source_with_exact_drawdown_metrics()
        generic = replace(
            source, run_identity={"starting_equity_usd": 10000.0},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(generic, folder)
            _forge_canonical_metric(
                folder, manifest, "max_drawdown_usd",
                source.metrics["max_drawdown_usd"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 2,
            )


def _source_zero_drawdown_run() -> BacktestRun:
    source = _zero_trade_source_engine_run()
    return replace(source, metrics={
        "trade_count": 0,
        "net_pnl_usd": 0.0,
        "net_return": 0.0,
        "max_drawdown_usd": 0.0,
        "max_drawdown_fraction": 0.0,
        "recovery_factor": None,
    })


class Phase3AuditSourceNoDrawdownNullRecoveryTests(unittest.TestCase):
    def test_audit_accepts_zero_trade_null_recovery_and_zero_drawdown(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(_source_zero_drawdown_run(), folder)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 0,
            )

    def test_audit_refuses_rehashed_near_zero_source_drawdown_fraction(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_zero_drawdown_run(), folder,
            )
            _forge_metrics(folder, manifest, "max_drawdown_fraction", 1e-13)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric max_drawdown_fraction conflicts with checkpoint curve",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_nonnull_recovery_without_drawdown(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_zero_drawdown_run(), folder,
            )
            _forge_metrics(folder, manifest, "recovery_factor", 0.0)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric recovery_factor conflicts with checkpoint curve",
            ):
                audit_backtest_artifact_structure(folder)


class Phase3AuditPreciseSourceEconomicErrorOrderingTests(unittest.TestCase):
    def test_audit_identifies_source_gross_before_dependent_net(self):
        source = _combined_source_economic_model_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_versioned_trade_execution(
                folder, manifest, "gross_pnl_usd",
                source.trades[0].gross_pnl_usd + 0.00001,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "gross PnL conflicts with reference-price",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_identifies_source_commission_before_dependent_net(self):
        source = _combined_source_economic_model_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_versioned_trade_execution(
                folder, manifest, "commission_cost_usd",
                source.trades[0].commission_cost_usd + 0.00001,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "source fixed commission conflicts with trade costs",
            ):
                audit_backtest_artifact_structure(folder)


def _forge_canonical_metric(
    folder: Path, manifest: dict[str, object], field: str, value: object,
) -> None:
    # Preserve the writer's canonical small-JSON encoding. This isolates
    # the auditor's intentionally looser generic metric arithmetic from
    # the writer's correctly strict pre-I/O ledger validation.
    file = folder / "metrics.json"
    report = json.loads(file.read_text("utf-8"))
    report[field] = value
    payload = (
        json.dumps(
            report, sort_keys=True, indent=2,
            ensure_ascii=False, allow_nan=False,
        ) + "\n"
    ).encode("utf-8")
    file.write_bytes(payload)
    for record in manifest["artifacts"]:
        if record["path"] == "metrics.json":
            record["size_bytes"] = len(payload)
            record["sha256"] = hashlib.sha256(payload).hexdigest()
    (folder / "manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8",
    )


class Phase3AuditGenericCanonicalMetricCompatibilityTests(unittest.TestCase):
    def test_audit_rejects_rehashed_generic_metric_with_large_drift(self):
        source = _source_with_exact_trade_distribution_metrics()
        generic = replace(
            source, run_identity={"starting_equity_usd": 10000.0},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(generic, folder)
            _forge_canonical_metric(folder, manifest, "win_rate", 0.9)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric win_rate conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_accepts_rehashed_generic_metric_below_legacy_tolerance(self):
        source = _source_with_exact_trade_distribution_metrics()
        generic = replace(
            source, run_identity={"starting_equity_usd": 10000.0},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(generic, folder)
            _forge_canonical_metric(folder, manifest, "win_rate", 0.500000001)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 2,
            )


class Phase3AuditSourceEconomicMultiFaultOrderingTests(unittest.TestCase):
    def test_audit_rejects_only_false_source_net_after_valid_cost_components(self):
        source = _combined_source_economic_model_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_versioned_trade_execution(
                folder, manifest, "net_pnl_usd",
                source.trades[0].net_pnl_usd + 0.00001,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "net PnL cost reconciliation mismatch",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_identifies_source_zero_financing_before_net_mismatch(self):
        source = _combined_source_economic_model_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_versioned_trade_execution(
                folder, manifest, "financing_cost_usd", 0.00001,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "source zero financing conflicts with trade costs",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_preserves_source_equity_check_after_consistent_net(self):
        source = _combined_source_economic_model_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_versioned_trade_execution(
                folder, manifest, "risk_equity_after_usd",
                source.trades[0].risk_equity_after_usd + 0.00001,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "realized equity conflicts with net PnL",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_still_rejects_large_generic_net_pnl_drift(self):
        source = _combined_source_economic_model_run()
        generic = replace(
            source, run_identity={"starting_equity_usd": 10000.0},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(generic, folder)
            _forge_versioned_trade_execution(
                folder, manifest, "net_pnl_usd",
                source.trades[0].net_pnl_usd + 0.00001,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "net PnL cost reconciliation mismatch",
            ):
                audit_backtest_artifact_structure(folder)


class Phase3AuditCanonicalSourceVersusGenericMetricPrecisionTests(unittest.TestCase):
    def test_audit_refuses_near_equal_source_average_loss_in_canonical_metrics(self):
        source = _source_with_exact_trade_distribution_metrics()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_canonical_metric(
                folder, manifest, "average_loss_usd",
                source.metrics["average_loss_usd"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric average_loss_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_accepts_near_equal_generic_average_loss_with_canonical_hash(self):
        source = _source_with_exact_trade_distribution_metrics()
        generic = replace(
            source, run_identity={"starting_equity_usd": 10000.0},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(generic, folder)
            _forge_canonical_metric(
                folder, manifest, "average_loss_usd",
                source.metrics["average_loss_usd"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 2,
            )

    def test_audit_refuses_near_equal_source_recovery_factor_in_canonical_metrics(self):
        source = _source_with_exact_drawdown_metrics()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_canonical_metric(
                folder, manifest, "recovery_factor",
                source.metrics["recovery_factor"] + 1e-13,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric recovery_factor conflicts with checkpoint curve",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_accepts_near_equal_generic_recovery_factor_with_canonical_hash(self):
        source = _source_with_exact_drawdown_metrics()
        generic = replace(
            source, run_identity={"starting_equity_usd": 10000.0},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(generic, folder)
            _forge_canonical_metric(
                folder, manifest, "recovery_factor",
                source.metrics["recovery_factor"] + 1e-13,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 2,
            )


def _source_signed_financing_with_complete_metrics(
    financing: float,
) -> BacktestRun:
    source = _source_custom_financing_run(financing)
    item = source.trades[0]
    total_cost = (
        item.slippage_cost_usd + item.commission_cost_usd
        + item.financing_cost_usd
    )
    return replace(source, metrics={
        "trade_count": 1,
        "net_pnl_usd": item.net_pnl_usd,
        "slippage_cost_usd": item.slippage_cost_usd,
        "commission_cost_usd": item.commission_cost_usd,
        "financing_cost_usd": financing,
        "total_explicit_cost_usd": total_cost,
    })


class Phase3AuditSignedFinancingAggregateWitnessTests(unittest.TestCase):
    def test_audit_accepts_exact_source_credit_and_debit_totals(self):
        for signed_financing in (-1.25, 1.25):
            with self.subTest(signed_financing=signed_financing):
                with tempfile.TemporaryDirectory() as home:
                    folder = Path(home) / "evidence"
                    source = _source_signed_financing_with_complete_metrics(
                        signed_financing,
                    )
                    write_backtest_artifacts(source, folder)
                    self.assertEqual(
                        audit_backtest_artifact_structure(folder)["trade_count"], 1,
                    )

    def test_audit_refuses_rehashed_near_equal_source_financing_metric(self):
        source = _source_signed_financing_with_complete_metrics(-1.25)
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_canonical_metric(
                folder, manifest, "financing_cost_usd",
                source.metrics["financing_cost_usd"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric financing_cost_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_allows_generic_near_equal_credit_metric_after_rehash(self):
        source = _source_signed_financing_with_complete_metrics(-1.25)
        generic = replace(
            source, run_identity={"starting_equity_usd": 10000.0},
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(generic, folder)
            _forge_canonical_metric(
                folder, manifest, "financing_cost_usd",
                source.metrics["financing_cost_usd"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 1,
            )


def _zero_trade_source_with_null_performance_metrics() -> BacktestRun:
    base = _zero_trade_source_engine_run()
    return replace(base, metrics={
        "trade_count": 0,
        "net_pnl_usd": 0.0,
        "gross_profit_usd": 0.0,
        "gross_loss_usd": 0.0,
        "profit_factor": None,
        "win_rate": None,
        "average_win_usd": None,
        "average_loss_usd": None,
        "expectancy_usd": None,
        "longest_winning_streak": 0,
        "longest_losing_streak": 0,
    })


class Phase3AuditSourceZeroTradeNullPerformanceWitnessTests(unittest.TestCase):
    def test_audit_accepts_null_profit_and_distribution_metrics_without_trades(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(
                _zero_trade_source_with_null_performance_metrics(), folder,
            )
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 0,
            )

    def test_audit_refuses_rehashed_zero_win_rate_instead_of_null(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _zero_trade_source_with_null_performance_metrics(), folder,
            )
            _forge_canonical_metric(folder, manifest, "win_rate", 0.0)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric win_rate conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_zero_profit_factor_instead_of_null(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _zero_trade_source_with_null_performance_metrics(), folder,
            )
            _forge_canonical_metric(folder, manifest, "profit_factor", 0.0)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric profit_factor conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_nonzero_winning_streak_without_trades(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _zero_trade_source_with_null_performance_metrics(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "longest_winning_streak", 1,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric longest_winning_streak conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)


def _source_one_sided_performance_metrics_run(*, winning: bool) -> BacktestRun:
    source = (
        _combined_source_economic_model_run()
        if winning else _source_adverse_gap_stop_run(Direction.LONG)
    )
    amount = source.trades[0].net_pnl_usd
    assert (amount > 0) is winning
    return replace(source, metrics={
        "trade_count": 1,
        "net_pnl_usd": amount,
        "gross_profit_usd": amount if winning else 0.0,
        "gross_loss_usd": 0.0 if winning else -amount,
        "profit_factor": None if winning else 0.0,
        "win_rate": 1.0 if winning else 0.0,
        "average_win_usd": amount if winning else None,
        "average_loss_usd": None if winning else amount,
        "expectancy_usd": amount,
        "longest_winning_streak": 1 if winning else 0,
        "longest_losing_streak": 0 if winning else 1,
    })


class Phase3AuditSourceOneSidedPerformanceNullTests(unittest.TestCase):
    def test_audit_accepts_source_only_winner_and_only_loser_metrics(self):
        for winning in (True, False):
            with self.subTest(winning=winning):
                with tempfile.TemporaryDirectory() as home:
                    folder = Path(home) / "evidence"
                    write_backtest_artifacts(
                        _source_one_sided_performance_metrics_run(
                            winning=winning,
                        ), folder,
                    )
                    self.assertEqual(
                        audit_backtest_artifact_structure(folder)["trade_count"], 1,
                    )

    def test_audit_refuses_rehashed_win_only_finite_profit_factor(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_one_sided_performance_metrics_run(winning=True), folder,
            )
            _forge_canonical_metric(folder, manifest, "profit_factor", 0.0)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric profit_factor conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_win_only_zero_average_loss(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_one_sided_performance_metrics_run(winning=True), folder,
            )
            _forge_canonical_metric(folder, manifest, "average_loss_usd", 0.0)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric average_loss_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_loss_only_zero_average_win(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_one_sided_performance_metrics_run(winning=False), folder,
            )
            _forge_canonical_metric(folder, manifest, "average_win_usd", 0.0)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric average_win_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)


def _source_rejected_only_null_performance_run() -> BacktestRun:
    rejected = _source_no_trade_rejection_run()
    baseline = _zero_trade_source_with_null_performance_metrics()
    return replace(rejected, metrics=baseline.metrics)


class Phase3AuditSourceRejectedOnlyPerformanceWitnessTests(unittest.TestCase):
    def test_audit_accepts_no_trade_rejection_with_null_performance_metrics(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(
                _source_rejected_only_null_performance_run(), folder,
            )
            observed = audit_backtest_artifact_structure(folder)
            self.assertEqual(observed["trade_count"], 0)
            self.assertEqual(observed["rejection_count"], 1)
            self.assertEqual(observed["equity_checkpoint_count"], 1)

    def test_audit_refuses_rehashed_rejected_only_win_rate_zero(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_rejected_only_null_performance_run(), folder,
            )
            _forge_canonical_metric(folder, manifest, "win_rate", 0.0)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric win_rate conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_rejected_only_expectancy_zero(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_rejected_only_null_performance_run(), folder,
            )
            _forge_canonical_metric(folder, manifest, "expectancy_usd", 0.0)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric expectancy_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_rejected_only_losing_streak(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_rejected_only_null_performance_run(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "longest_losing_streak", 1,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric longest_losing_streak conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)


def _source_same_time_all_wins_distribution_run() -> BacktestRun:
    source = _same_exit_source_engine_run()
    net = sum(trade.net_pnl_usd for trade in source.trades)
    assert len(source.trades) == 2
    assert all(trade.net_pnl_usd > 0 for trade in source.trades)
    return replace(source, metrics={
        "trade_count": 2,
        "net_pnl_usd": net,
        "gross_profit_usd": net,
        "gross_loss_usd": 0.0,
        "profit_factor": None,
        "win_rate": 1.0,
        "average_win_usd": net / 2,
        "average_loss_usd": None,
        "expectancy_usd": net / 2,
        "longest_winning_streak": 2,
        "longest_losing_streak": 0,
    })


class Phase3AuditSourceSameTimeAllWinDistributionTests(unittest.TestCase):
    def test_audit_accepts_two_wins_with_same_timestamp_reverse_id_order(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(
                _source_same_time_all_wins_distribution_run(), folder,
            )
            trades = [
                json.loads(line) for line in
                (folder / "trades.jsonl").read_text("utf-8").splitlines()
            ]
            self.assertEqual(
                [trade["trade_id"] for trade in trades], ["A-CLOSE", "Z-CLOSE"],
            )
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 2,
            )

    def test_audit_refuses_rehashed_shorter_same_time_winning_streak(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_all_wins_distribution_run(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "longest_winning_streak", 1,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric longest_winning_streak conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_near_equal_same_time_average_win(self):
        run = _source_same_time_all_wins_distribution_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(run, folder)
            _forge_canonical_metric(
                folder, manifest, "average_win_usd",
                run.metrics["average_win_usd"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric average_win_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)


def _source_same_time_all_losses_distribution_run() -> BacktestRun:
    base = _source_adverse_gap_stop_run(Direction.LONG)
    original = base.trades[0]
    assert original.net_pnl_usd < 0
    first_after = original.risk_equity_after_usd
    final_after = first_after + original.net_pnl_usd
    first = replace(
        original, trade_id="Z-LOSS", decision_id="Z-LOSS",
    )
    second = replace(
        original, trade_id="A-LOSS", decision_id="A-LOSS",
        risk_equity_before_usd=first_after,
        risk_equity_after_usd=final_after,
    )
    total = first.net_pnl_usd + second.net_pnl_usd
    return replace(
        base,
        trades=(first, second),
        equity_checkpoints=(
            base.equity_checkpoints[0],
            EquityCheckpoint(
                STAMP + timedelta(minutes=1), first_after,
            ),
            EquityCheckpoint(
                STAMP + timedelta(minutes=1), final_after,
            ),
        ),
        metrics={
            "trade_count": 2,
            "net_pnl_usd": total,
            "gross_profit_usd": 0.0,
            "gross_loss_usd": -total,
            "profit_factor": 0.0,
            "win_rate": 0.0,
            "average_win_usd": None,
            "average_loss_usd": total / 2,
            "expectancy_usd": total / 2,
            "longest_winning_streak": 0,
            "longest_losing_streak": 2,
        },
    )


class Phase3AuditSourceSameTimeAllLossDistributionTests(unittest.TestCase):
    def test_audit_accepts_same_time_loss_streak_with_reverse_id_order(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(
                _source_same_time_all_losses_distribution_run(), folder,
            )
            rows = [
                json.loads(line) for line in
                (folder / "trades.jsonl").read_text("utf-8").splitlines()
            ]
            self.assertEqual(
                [record["trade_id"] for record in rows],
                ["A-LOSS", "Z-LOSS"],
            )
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 2,
            )

    def test_audit_refuses_rehashed_shortened_loss_streak(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_all_losses_distribution_run(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "longest_losing_streak", 1,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric longest_losing_streak conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_null_profit_factor_with_realized_losses(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_all_losses_distribution_run(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "profit_factor", None,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric profit_factor must be finite numeric",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_near_equal_source_average_loss(self):
        source = _source_same_time_all_losses_distribution_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_canonical_metric(
                folder, manifest, "average_loss_usd",
                source.metrics["average_loss_usd"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric average_loss_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)



def _source_same_time_mixed_outcome_distribution_run() -> BacktestRun:
    source = _source_with_exact_trade_distribution_metrics()
    winner, loser = source.trades
    assert winner.net_pnl_usd > 0 and loser.net_pnl_usd < 0
    same_close = winner.exit_timestamp_utc
    # Realized order: winner then loser. Published order: A-LOSS then Z-WIN.
    return replace(
        source,
        trades=(
            replace(winner, trade_id="Z-WIN", decision_id="Z-WIN"),
            replace(
                loser, trade_id="A-LOSS", decision_id="A-LOSS",
                entry_timestamp_utc=STAMP,
                exit_timestamp_utc=same_close,
            ),
        ),
        equity_checkpoints=(
            source.equity_checkpoints[0],
            source.equity_checkpoints[1],
            replace(source.equity_checkpoints[2], timestamp_utc=same_close),
        ),
    )


class Phase3AuditSourceSameTimeMixedOutcomeDistributionTests(unittest.TestCase):
    def test_audit_accepts_same_time_mixed_outcomes_with_reverse_publication(self):
        source = _source_same_time_mixed_outcome_distribution_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(source, folder)
            rows = [
                json.loads(line) for line in
                (folder / "trades.jsonl").read_text("utf-8").splitlines()
            ]
            self.assertEqual(
                [row["trade_id"] for row in rows], ["A-LOSS", "Z-WIN"],
            )
            self.assertEqual(
                [row["net_pnl_usd"] > 0 for row in rows], [False, True],
            )
            self.assertEqual(source.metrics["win_rate"], 0.5)
            self.assertEqual(source.metrics["longest_winning_streak"], 1)
            self.assertEqual(source.metrics["longest_losing_streak"], 1)
            self.assertGreater(source.metrics["profit_factor"], 0.0)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 2,
            )

    def test_audit_refuses_rehashed_all_win_rate_for_mixed_same_time_exits(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_mixed_outcome_distribution_run(), folder,
            )
            _forge_canonical_metric(folder, manifest, "win_rate", 1.0)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric win_rate conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_two_win_streak_across_realized_loss(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_mixed_outcome_distribution_run(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "longest_winning_streak", 2,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError,
                "metric longest_winning_streak conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_null_profit_factor_for_mixed_outcomes(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_mixed_outcome_distribution_run(), folder,
            )
            _forge_canonical_metric(folder, manifest, "profit_factor", None)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric profit_factor must be finite numeric",
            ):
                audit_backtest_artifact_structure(folder)



class Phase3AuditSourceSameTimeMixedOutcomePrecisionTests(unittest.TestCase):
    def test_audit_refuses_near_equal_source_average_win_with_mixed_exits(self):
        source = _source_same_time_mixed_outcome_distribution_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_canonical_metric(
                folder, manifest, "average_win_usd",
                source.metrics["average_win_usd"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric average_win_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_near_equal_source_average_loss_with_mixed_exits(self):
        source = _source_same_time_mixed_outcome_distribution_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_canonical_metric(
                folder, manifest, "average_loss_usd",
                source.metrics["average_loss_usd"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric average_loss_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_near_equal_source_expectancy_with_mixed_exits(self):
        source = _source_same_time_mixed_outcome_distribution_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_canonical_metric(
                folder, manifest, "expectancy_usd",
                source.metrics["expectancy_usd"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric expectancy_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_false_two_loss_streak_in_mixed_source_report(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_mixed_outcome_distribution_run(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "longest_losing_streak", 2,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError,
                "metric longest_losing_streak conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)



def _source_same_time_mixed_streak_publication_run() -> BacktestRun:
    source = _source_with_exact_trade_distribution_metrics()
    winner, loser = source.trades
    gain, loss = winner.net_pnl_usd, loser.net_pnl_usd
    assert gain > 0 and loss < 0
    same_close = winner.exit_timestamp_utc
    after_first_loss = 10000.0 + loss
    after_win = after_first_loss + gain
    after_second_loss = after_win + loss
    # Engine realizes loss, win, loss, but the canonical rows publish
    # A-LOSS, B-LOSS, Z-WIN at the same UTC exit instant.
    return replace(
        source,
        trades=(
            replace(
                loser, trade_id="A-LOSS", decision_id="A-LOSS",
                entry_timestamp_utc=STAMP, exit_timestamp_utc=same_close,
                risk_equity_before_usd=10000.0,
                risk_equity_after_usd=after_first_loss,
            ),
            replace(
                winner, trade_id="Z-WIN", decision_id="Z-WIN",
                risk_equity_before_usd=after_first_loss,
                risk_equity_after_usd=after_win,
            ),
            replace(
                loser, trade_id="B-LOSS", decision_id="B-LOSS",
                entry_timestamp_utc=STAMP, exit_timestamp_utc=same_close,
                risk_equity_before_usd=after_win,
                risk_equity_after_usd=after_second_loss,
            ),
        ),
        equity_checkpoints=(
            EquityCheckpoint(STAMP, 10000.0),
            EquityCheckpoint(same_close, after_first_loss),
            EquityCheckpoint(same_close, after_win),
            EquityCheckpoint(same_close, after_second_loss),
        ),
        metrics={
            "trade_count": 3,
            "gross_profit_usd": gain,
            "gross_loss_usd": -2 * loss,
            "profit_factor": gain / (-2 * loss),
            "win_rate": 1 / 3,
            "average_win_usd": gain,
            "average_loss_usd": loss,
            "longest_winning_streak": 1,
            "longest_losing_streak": 2,
        },
    )


class Phase3AuditSourceSameTimeMixedPublicationStreakTests(unittest.TestCase):
    def test_audit_uses_canonical_trade_order_for_mixed_sign_streaks(self):
        run = _source_same_time_mixed_streak_publication_run()
        self.assertEqual(
            [trade.net_pnl_usd < 0 for trade in run.trades],
            [True, False, True],
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            rows = [
                json.loads(line) for line in
                (folder / "trades.jsonl").read_text("utf-8").splitlines()
            ]
            self.assertEqual(
                [row["trade_id"] for row in rows],
                ["A-LOSS", "B-LOSS", "Z-WIN"],
            )
            self.assertEqual(run.metrics["longest_losing_streak"], 2)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 3,
            )

    def test_audit_refuses_rehashed_realization_order_loss_streak(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_mixed_streak_publication_run(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "longest_losing_streak", 1,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError,
                "metric longest_losing_streak conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_fictitious_two_win_streak(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_mixed_streak_publication_run(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "longest_winning_streak", 2,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError,
                "metric longest_winning_streak conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_two_thirds_win_rate(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_mixed_streak_publication_run(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "win_rate", 2 / 3,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric win_rate conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)



def _source_same_time_mixed_winning_publication_run() -> BacktestRun:
    source = _source_with_exact_trade_distribution_metrics()
    winner, loser = source.trades
    gain, loss = winner.net_pnl_usd, loser.net_pnl_usd
    assert gain > 0 and loss < 0
    same_close = winner.exit_timestamp_utc
    after_first_win = 10000.0 + gain
    after_loss = after_first_win + loss
    after_second_win = after_loss + gain
    # Realization W/L/W, canonical publication A-WIN/B-WIN/Z-LOSS.
    return replace(
        source,
        trades=(
            replace(
                winner, trade_id="A-WIN", decision_id="A-WIN",
                risk_equity_before_usd=10000.0,
                risk_equity_after_usd=after_first_win,
            ),
            replace(
                loser, trade_id="Z-LOSS", decision_id="Z-LOSS",
                entry_timestamp_utc=STAMP, exit_timestamp_utc=same_close,
                risk_equity_before_usd=after_first_win,
                risk_equity_after_usd=after_loss,
            ),
            replace(
                winner, trade_id="B-WIN", decision_id="B-WIN",
                risk_equity_before_usd=after_loss,
                risk_equity_after_usd=after_second_win,
            ),
        ),
        equity_checkpoints=(
            EquityCheckpoint(STAMP, 10000.0),
            EquityCheckpoint(same_close, after_first_win),
            EquityCheckpoint(same_close, after_loss),
            EquityCheckpoint(same_close, after_second_win),
        ),
        metrics={
            "trade_count": 3,
            "gross_profit_usd": 2 * gain,
            "gross_loss_usd": -loss,
            "profit_factor": (2 * gain) / -loss,
            "win_rate": 2 / 3,
            "average_win_usd": gain,
            "average_loss_usd": loss,
            "longest_winning_streak": 2,
            "longest_losing_streak": 1,
        },
    )


class Phase3AuditSourceSameTimeMixedWinningPublicationTests(unittest.TestCase):
    def test_audit_accepts_canonical_two_win_streak_with_reverse_realization(self):
        run = _source_same_time_mixed_winning_publication_run()
        self.assertEqual(
            [trade.net_pnl_usd > 0 for trade in run.trades],
            [True, False, True],
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            rows = [
                json.loads(line) for line in
                (folder / "trades.jsonl").read_text("utf-8").splitlines()
            ]
            self.assertEqual(
                [row["trade_id"] for row in rows],
                ["A-WIN", "B-WIN", "Z-LOSS"],
            )
            self.assertEqual(run.metrics["longest_winning_streak"], 2)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 3,
            )

    def test_audit_refuses_rehashed_realization_order_win_streak(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_mixed_winning_publication_run(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "longest_winning_streak", 1,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError,
                "metric longest_winning_streak conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_fictitious_two_loss_streak(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_mixed_winning_publication_run(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "longest_losing_streak", 2,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError,
                "metric longest_losing_streak conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_one_third_win_rate_in_two_win_report(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_mixed_winning_publication_run(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "win_rate", 1 / 3,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric win_rate conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)



def _source_cross_timestamp_canonical_winning_streak_run() -> BacktestRun:
    seed = _source_with_exact_trade_distribution_metrics()
    winner, loser = seed.trades
    gain, loss = winner.net_pnl_usd, loser.net_pnl_usd
    assert gain > 0 and loss < 0
    later = STAMP + timedelta(minutes=2)
    # The earlier timestamp wins over trade ID. At the later timestamp,
    # A-WIN/B-WIN publish before Z-LOSS despite loss-first realization.
    first_after = 10000.0 + gain
    second_after = first_after + loss
    third_after = second_after + gain
    final_after = third_after + gain
    return replace(
        seed,
        trades=(
            replace(
                winner, trade_id="Z-EARLY-WIN", decision_id="Z-EARLY-WIN",
                risk_equity_before_usd=10000.0,
                risk_equity_after_usd=first_after,
            ),
            replace(
                loser, trade_id="Z-LOSS", decision_id="Z-LOSS",
                exit_timestamp_utc=later,
                risk_equity_before_usd=first_after,
                risk_equity_after_usd=second_after,
            ),
            replace(
                winner, trade_id="A-WIN", decision_id="A-WIN",
                entry_timestamp_utc=STAMP + timedelta(minutes=1),
                exit_timestamp_utc=later,
                risk_equity_before_usd=second_after,
                risk_equity_after_usd=third_after,
            ),
            replace(
                winner, trade_id="B-WIN", decision_id="B-WIN",
                entry_timestamp_utc=STAMP + timedelta(minutes=1),
                exit_timestamp_utc=later,
                risk_equity_before_usd=third_after,
                risk_equity_after_usd=final_after,
            ),
        ),
        equity_checkpoints=(
            EquityCheckpoint(STAMP, 10000.0),
            EquityCheckpoint(STAMP + timedelta(minutes=1), first_after),
            EquityCheckpoint(later, second_after),
            EquityCheckpoint(later, third_after),
            EquityCheckpoint(later, final_after),
        ),
        metrics={
            "trade_count": 4,
            "win_rate": 0.75,
            "longest_winning_streak": 3,
            "longest_losing_streak": 1,
        },
    )


class Phase3AuditSourceCrossTimestampWinningStreakTests(unittest.TestCase):
    def test_audit_accepts_win_streak_crossing_equal_time_boundary(self):
        run = _source_cross_timestamp_canonical_winning_streak_run()
        self.assertEqual(
            [trade.net_pnl_usd > 0 for trade in run.trades],
            [True, False, True, True],
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            rows = [
                json.loads(line) for line in
                (folder / "trades.jsonl").read_text("utf-8").splitlines()
            ]
            self.assertEqual(
                [row["trade_id"] for row in rows],
                ["Z-EARLY-WIN", "A-WIN", "B-WIN", "Z-LOSS"],
            )
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 4,
            )

    def test_audit_refuses_rehashed_shortened_cross_timestamp_winning_streak(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_cross_timestamp_canonical_winning_streak_run(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "longest_winning_streak", 2,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError,
                "metric longest_winning_streak conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_all_win_rate_across_losing_close(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_cross_timestamp_canonical_winning_streak_run(), folder,
            )
            _forge_canonical_metric(folder, manifest, "win_rate", 1.0)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric win_rate conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_fabricated_double_loss_streak(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_cross_timestamp_canonical_winning_streak_run(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "longest_losing_streak", 2,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError,
                "metric longest_losing_streak conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)



def _source_cross_timestamp_canonical_losing_streak_run() -> BacktestRun:
    seed = _source_with_exact_trade_distribution_metrics()
    winner, loser = seed.trades
    gain, loss = winner.net_pnl_usd, loser.net_pnl_usd
    assert gain > 0 and loss < 0
    earlier = STAMP + timedelta(minutes=1)
    later = STAMP + timedelta(minutes=2)
    # Realization: L at T+1, then W/L/L at T+2. Canonical publication:
    # Z-EARLY-LOSS at T+1, then A-LOSS/B-LOSS/Z-WIN at T+2.
    first_after = 10000.0 + loss
    second_after = first_after + gain
    third_after = second_after + loss
    final_after = third_after + loss
    return replace(
        seed,
        trades=(
            replace(
                loser, trade_id="Z-EARLY-LOSS", decision_id="Z-EARLY-LOSS",
                entry_timestamp_utc=STAMP, exit_timestamp_utc=earlier,
                risk_equity_before_usd=10000.0,
                risk_equity_after_usd=first_after,
            ),
            replace(
                winner, trade_id="Z-WIN", decision_id="Z-WIN",
                entry_timestamp_utc=earlier, exit_timestamp_utc=later,
                risk_equity_before_usd=first_after,
                risk_equity_after_usd=second_after,
            ),
            replace(
                loser, trade_id="A-LOSS", decision_id="A-LOSS",
                exit_timestamp_utc=later,
                risk_equity_before_usd=second_after,
                risk_equity_after_usd=third_after,
            ),
            replace(
                loser, trade_id="B-LOSS", decision_id="B-LOSS",
                exit_timestamp_utc=later,
                risk_equity_before_usd=third_after,
                risk_equity_after_usd=final_after,
            ),
        ),
        equity_checkpoints=(
            EquityCheckpoint(STAMP, 10000.0),
            EquityCheckpoint(earlier, first_after),
            EquityCheckpoint(later, second_after),
            EquityCheckpoint(later, third_after),
            EquityCheckpoint(later, final_after),
        ),
        metrics={
            "trade_count": 4,
            "win_rate": 0.25,
            "longest_winning_streak": 1,
            "longest_losing_streak": 3,
        },
    )


class Phase3AuditSourceCrossTimestampLosingStreakTests(unittest.TestCase):
    def test_audit_accepts_loss_streak_crossing_equal_time_boundary(self):
        run = _source_cross_timestamp_canonical_losing_streak_run()
        self.assertEqual(
            [trade.net_pnl_usd < 0 for trade in run.trades],
            [True, False, True, True],
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            rows = [
                json.loads(line) for line in
                (folder / "trades.jsonl").read_text("utf-8").splitlines()
            ]
            self.assertEqual(
                [row["trade_id"] for row in rows],
                ["Z-EARLY-LOSS", "A-LOSS", "B-LOSS", "Z-WIN"],
            )
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 4,
            )

    def test_audit_refuses_rehashed_realization_order_short_loss_streak(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_cross_timestamp_canonical_losing_streak_run(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "longest_losing_streak", 2,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError,
                "metric longest_losing_streak conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_zero_win_rate_with_profitable_close(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_cross_timestamp_canonical_losing_streak_run(), folder,
            )
            _forge_canonical_metric(folder, manifest, "win_rate", 0.0)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric win_rate conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_fabricated_double_winning_streak(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_cross_timestamp_canonical_losing_streak_run(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "longest_winning_streak", 2,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError,
                "metric longest_winning_streak conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)



def _source_cross_timestamp_complete_profit_distribution(
    *, winning_majority: bool,
) -> BacktestRun:
    source = (
        _source_cross_timestamp_canonical_winning_streak_run()
        if winning_majority
        else _source_cross_timestamp_canonical_losing_streak_run()
    )
    wins = [trade.net_pnl_usd for trade in source.trades if trade.net_pnl_usd > 0]
    losses = [trade.net_pnl_usd for trade in source.trades if trade.net_pnl_usd < 0]
    assert len(wins) == (3 if winning_majority else 1)
    assert len(losses) == (1 if winning_majority else 3)
    profit = sum(wins)
    loss = -sum(losses)
    return replace(source, metrics={
        **source.metrics,
        "gross_profit_usd": profit,
        "gross_loss_usd": loss,
        "profit_factor": profit / loss,
        "average_win_usd": profit / len(wins),
        "average_loss_usd": -loss / len(losses),
    })


class Phase3AuditSourceCrossTimestampProfitDistributionTests(unittest.TestCase):
    def test_audit_accepts_complete_cross_time_profit_metrics_for_both_signs(self):
        for majority in (True, False):
            with self.subTest(winning_majority=majority):
                source = _source_cross_timestamp_complete_profit_distribution(
                    winning_majority=majority,
                )
                self.assertGreater(source.metrics["gross_profit_usd"], 0)
                self.assertGreater(source.metrics["gross_loss_usd"], 0)
                self.assertGreater(source.metrics["profit_factor"], 0)
                with tempfile.TemporaryDirectory() as home:
                    folder = Path(home) / "evidence"
                    write_backtest_artifacts(source, folder)
                    self.assertEqual(
                        audit_backtest_artifact_structure(folder)["trade_count"],
                        4,
                    )

    def test_audit_refuses_near_equal_cross_time_gross_profit(self):
        source = _source_cross_timestamp_complete_profit_distribution(
            winning_majority=True,
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_canonical_metric(
                folder, manifest, "gross_profit_usd",
                source.metrics["gross_profit_usd"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric gross_profit_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_near_equal_cross_time_gross_loss(self):
        source = _source_cross_timestamp_complete_profit_distribution(
            winning_majority=False,
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_canonical_metric(
                folder, manifest, "gross_loss_usd",
                source.metrics["gross_loss_usd"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric gross_loss_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_near_equal_cross_time_profit_factor(self):
        source = _source_cross_timestamp_complete_profit_distribution(
            winning_majority=True,
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_canonical_metric(
                folder, manifest, "profit_factor",
                source.metrics["profit_factor"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric profit_factor conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_near_equal_cross_time_average_loss(self):
        source = _source_cross_timestamp_complete_profit_distribution(
            winning_majority=False,
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_canonical_metric(
                folder, manifest, "average_loss_usd",
                source.metrics["average_loss_usd"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric average_loss_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)



def _source_same_time_win_flat_win_distribution_run() -> BacktestRun:
    seed = _same_exit_source_engine_run()
    first, last = seed.trades
    assert first.net_pnl_usd == last.net_pnl_usd == 11.0
    after_first = first.risk_equity_after_usd
    final_after = last.risk_equity_after_usd
    flat = replace(
        first, trade_id="M-FLAT", decision_id="M-FLAT",
        entry_reference_price=1.1, exit_reference_price=1.1,
        entry_price=1.1, exit_price=1.1,
        gross_pnl_usd=0.0, slippage_cost_usd=0.0,
        commission_cost_usd=0.0, financing_cost_usd=0.0,
        net_pnl_usd=0.0, exit_reason=ExitReason.END_OF_DATA,
        risk_equity_before_usd=after_first,
        risk_equity_after_usd=after_first,
    )
    return replace(
        seed,
        trades=(
            replace(first, trade_id="A-WIN", decision_id="A-WIN"),
            flat,
            replace(last, trade_id="Z-WIN", decision_id="Z-WIN"),
        ),
        equity_checkpoints=(
            EquityCheckpoint(STAMP, 10000.0),
            EquityCheckpoint(STAMP + timedelta(minutes=1), after_first),
            EquityCheckpoint(STAMP + timedelta(minutes=1), after_first),
            EquityCheckpoint(STAMP + timedelta(minutes=1), final_after),
        ),
        metrics={
            "trade_count": 3,
            "net_pnl_usd": 22.0,
            "gross_profit_usd": 22.0,
            "gross_loss_usd": 0.0,
            "profit_factor": None,
            "win_rate": 2 / 3,
            "average_win_usd": 11.0,
            "average_loss_usd": None,
            "expectancy_usd": 22 / 3,
            "longest_winning_streak": 1,
            "longest_losing_streak": 0,
        },
    )


class Phase3AuditSourceBreakevenInterruptsWinStreakTests(unittest.TestCase):
    def test_audit_accepts_same_time_win_flat_win_without_merging_wins(self):
        source = _source_same_time_win_flat_win_distribution_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(source, folder)
            rows = [
                json.loads(line) for line in
                (folder / "trades.jsonl").read_text("utf-8").splitlines()
            ]
            self.assertEqual(
                [row["trade_id"] for row in rows],
                ["A-WIN", "M-FLAT", "Z-WIN"],
            )
            self.assertEqual(
                [row["net_pnl_usd"] for row in rows], [11.0, 0.0, 11.0],
            )
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 3,
            )

    def test_audit_refuses_rehashed_two_win_streak_across_flat_close(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_win_flat_win_distribution_run(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "longest_winning_streak", 2,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError,
                "metric longest_winning_streak conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_full_win_rate_with_flat_denominator(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_win_flat_win_distribution_run(), folder,
            )
            _forge_canonical_metric(folder, manifest, "win_rate", 1.0)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric win_rate conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_finite_profit_factor_without_loss(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_win_flat_win_distribution_run(), folder,
            )
            _forge_canonical_metric(folder, manifest, "profit_factor", 0.0)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric profit_factor conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_zero_average_loss_without_losses(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_win_flat_win_distribution_run(), folder,
            )
            _forge_canonical_metric(folder, manifest, "average_loss_usd", 0.0)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric average_loss_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)



def _source_same_time_loss_flat_loss_distribution_run() -> BacktestRun:
    seed = _source_same_time_all_losses_distribution_run()
    first, last = seed.trades
    assert first.net_pnl_usd == last.net_pnl_usd < 0
    after_first = first.risk_equity_after_usd
    final_after = last.risk_equity_after_usd
    flat = replace(
        first, trade_id="M-FLAT", decision_id="M-FLAT",
        entry_reference_price=1.1, exit_reference_price=1.1,
        entry_price=1.1, exit_price=1.1,
        gross_pnl_usd=0.0, slippage_cost_usd=0.0,
        commission_cost_usd=0.0, financing_cost_usd=0.0,
        net_pnl_usd=0.0, exit_reason=ExitReason.END_OF_DATA,
        risk_equity_before_usd=after_first,
        risk_equity_after_usd=after_first,
    )
    net = first.net_pnl_usd + last.net_pnl_usd
    return replace(
        seed,
        trades=(
            replace(first, trade_id="A-LOSS", decision_id="A-LOSS"),
            flat,
            replace(last, trade_id="Z-LOSS", decision_id="Z-LOSS"),
        ),
        equity_checkpoints=(
            EquityCheckpoint(STAMP, 10000.0),
            EquityCheckpoint(STAMP + timedelta(minutes=1), after_first),
            EquityCheckpoint(STAMP + timedelta(minutes=1), after_first),
            EquityCheckpoint(STAMP + timedelta(minutes=1), final_after),
        ),
        metrics={
            "trade_count": 3,
            "net_pnl_usd": net,
            "gross_profit_usd": 0.0,
            "gross_loss_usd": -net,
            "profit_factor": 0.0,
            "win_rate": 0.0,
            "average_win_usd": None,
            "average_loss_usd": net / 2,
            "expectancy_usd": net / 3,
            "longest_winning_streak": 0,
            "longest_losing_streak": 1,
        },
    )


class Phase3AuditSourceBreakevenInterruptsLossStreakTests(unittest.TestCase):
    def test_audit_accepts_same_time_loss_flat_loss_without_merging_losses(self):
        source = _source_same_time_loss_flat_loss_distribution_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(source, folder)
            rows = [
                json.loads(line) for line in
                (folder / "trades.jsonl").read_text("utf-8").splitlines()
            ]
            self.assertEqual(
                [row["trade_id"] for row in rows],
                ["A-LOSS", "M-FLAT", "Z-LOSS"],
            )
            self.assertEqual(
                [row["net_pnl_usd"] < 0 for row in rows],
                [True, False, True],
            )
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 3,
            )

    def test_audit_refuses_rehashed_two_loss_streak_across_flat_close(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_loss_flat_loss_distribution_run(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "longest_losing_streak", 2,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError,
                "metric longest_losing_streak conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_spurious_wins_without_winning_close(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_loss_flat_loss_distribution_run(), folder,
            )
            _forge_canonical_metric(folder, manifest, "win_rate", 1 / 3)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric win_rate conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_null_profit_factor_despite_real_losses(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_loss_flat_loss_distribution_run(), folder,
            )
            _forge_canonical_metric(folder, manifest, "profit_factor", None)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric profit_factor must be finite numeric",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_zero_average_win_without_winners(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_loss_flat_loss_distribution_run(), folder,
            )
            _forge_canonical_metric(folder, manifest, "average_win_usd", 0.0)
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric average_win_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)



def _source_same_time_canonical_win_win_flat_run() -> BacktestRun:
    source = _source_same_time_win_flat_win_distribution_run()
    first, flat, last = source.trades
    # Checkpoint realization is W/FLAT/W but published ID order is W/W/FLAT.
    return replace(
        source,
        trades=(
            first,
            replace(flat, trade_id="Z-FLAT", decision_id="Z-FLAT"),
            replace(last, trade_id="B-WIN", decision_id="B-WIN"),
        ),
        metrics={
            **source.metrics,
            "longest_winning_streak": 2,
        },
    )


class Phase3AuditSourceCanonicalWinFlatReorderingTests(unittest.TestCase):
    def test_audit_accepts_published_two_win_streak_with_realized_flat_gap(self):
        run = _source_same_time_canonical_win_win_flat_run()
        self.assertEqual(
            [trade.net_pnl_usd for trade in run.trades],
            [11.0, 0.0, 11.0],
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            rows = [
                json.loads(line) for line in
                (folder / "trades.jsonl").read_text("utf-8").splitlines()
            ]
            self.assertEqual(
                [row["trade_id"] for row in rows],
                ["A-WIN", "B-WIN", "Z-FLAT"],
            )
            self.assertEqual(
                [row["net_pnl_usd"] for row in rows],
                [11.0, 11.0, 0.0],
            )
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 3,
            )

    def test_audit_refuses_rehashed_realization_order_winning_streak(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_canonical_win_win_flat_run(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "longest_winning_streak", 1,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError,
                "metric longest_winning_streak conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_rehashed_winner_average_in_flat_tie_report(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_canonical_win_win_flat_run(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "average_win_usd", 22.0,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric average_win_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_checkpoint_reordering_that_omits_flat_transition(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_canonical_win_win_flat_run(), folder,
            )
            _forge_checkpoint_summary(
                folder, manifest, 1, "realized_risk_equity_usd", 10022.0,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "checkpoint conflicts with trade close",
            ):
                audit_backtest_artifact_structure(folder)



def _source_same_time_canonical_loss_loss_flat_run() -> BacktestRun:
    source = _source_same_time_loss_flat_loss_distribution_run()
    first, flat, last = source.trades
    # Checkpoint realization L/FLAT/L; same-time trade IDs publish L/L/FLAT.
    return replace(
        source,
        trades=(
            first,
            replace(flat, trade_id="Z-FLAT", decision_id="Z-FLAT"),
            replace(last, trade_id="B-LOSS", decision_id="B-LOSS"),
        ),
        metrics={
            **source.metrics,
            "longest_losing_streak": 2,
        },
    )


class Phase3AuditSourceCanonicalLossFlatReorderingTests(unittest.TestCase):
    def test_audit_accepts_canonical_two_loss_streak_with_realized_flat_gap(self):
        run = _source_same_time_canonical_loss_loss_flat_run()
        self.assertEqual(
            [trade.net_pnl_usd < 0 for trade in run.trades],
            [True, False, True],
        )
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            write_backtest_artifacts(run, folder)
            rows = [
                json.loads(line) for line in
                (folder / "trades.jsonl").read_text("utf-8").splitlines()
            ]
            self.assertEqual(
                [row["trade_id"] for row in rows],
                ["A-LOSS", "B-LOSS", "Z-FLAT"],
            )
            self.assertEqual(
                [row["net_pnl_usd"] < 0 for row in rows],
                [True, True, False],
            )
            self.assertEqual(run.metrics["profit_factor"], 0.0)
            self.assertEqual(
                audit_backtest_artifact_structure(folder)["trade_count"], 3,
            )

    def test_audit_refuses_rehashed_realization_order_losing_streak(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(
                _source_same_time_canonical_loss_loss_flat_run(), folder,
            )
            _forge_canonical_metric(
                folder, manifest, "longest_losing_streak", 1,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError,
                "metric longest_losing_streak conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_near_equal_source_average_loss_in_flat_tie_report(self):
        source = _source_same_time_canonical_loss_loss_flat_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_canonical_metric(
                folder, manifest, "average_loss_usd",
                source.metrics["average_loss_usd"] + 1e-9,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "metric average_loss_usd conflicts with trade ledger",
            ):
                audit_backtest_artifact_structure(folder)

    def test_audit_refuses_checkpoint_jump_that_skips_flat_loss_transition(self):
        source = _source_same_time_canonical_loss_loss_flat_run()
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "evidence"
            manifest = write_backtest_artifacts(source, folder)
            _forge_checkpoint_summary(
                folder, manifest, 1, "realized_risk_equity_usd",
                source.equity_checkpoints[-1].realized_risk_equity_usd,
            )
            self.assertEqual(verify_backtest_artifacts(folder), manifest)
            with self.assertRaisesRegex(
                ValueError, "checkpoint conflicts with trade close",
            ):
                audit_backtest_artifact_structure(folder)


if __name__ == "__main__":
    unittest.main()
