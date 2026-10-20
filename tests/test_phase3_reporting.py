from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from dataclasses import dataclass
from unittest import mock
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import MappingProxyType

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

    def test_metrics_reject_invalid_starting_equity_without_bool_alias(self):
        for value in (True, False, None, [], "10000", 10 ** 400):
            with self.subTest(equity_type=type(value).__name__):
                with self.assertRaisesRegex(ValueError, "starting equity"):
                    compute_backtest_metrics(
                        starting_equity_usd=value, trades=(),
                        equity_checkpoints=(),
                    )

    def test_metrics_reject_finite_trade_pnl_aggregate_overflow(self):
        trades = (
            trade(trade_id="EXTREME-1", minutes=1, net_pnl_usd=1e308),
            trade(trade_id="EXTREME-2", minutes=3, net_pnl_usd=1e308),
        )
        with self.assertRaisesRegex(ValueError, "metric.*finite"):
            compute_backtest_metrics(
                starting_equity_usd=10_000.0, trades=trades,
                equity_checkpoints=(EquityCheckpoint(BASE_TS, 10_000.0),),
            )

    def test_metrics_reject_nonfinite_derived_cost_ratio_and_drawdown(self):
        cases = (
            (
                (
                    trade(trade_id="C1", minutes=1, net_pnl_usd=0.0,
                          slippage_cost_usd=1e308),
                    trade(trade_id="C2", minutes=3, net_pnl_usd=0.0,
                          slippage_cost_usd=1e308),
                ),
                (EquityCheckpoint(BASE_TS, 10_000.0),),
            ),
            (
                (
                    trade(trade_id="P1", minutes=1, net_pnl_usd=1e308),
                    trade(trade_id="L1", minutes=3, net_pnl_usd=-1e-308),
                ),
                (EquityCheckpoint(BASE_TS, 10_000.0),),
            ),
            (
                (),
                (
                    EquityCheckpoint(BASE_TS, 1e308),
                    EquityCheckpoint(BASE_TS + timedelta(minutes=1), -1e308),
                ),
            ),
        )
        for trades, checkpoints in cases:
            with self.subTest(trade_count=len(trades),
                              checkpoint_count=len(checkpoints)):
                with self.assertRaisesRegex(ValueError, "metric.*finite"):
                    compute_backtest_metrics(
                        starting_equity_usd=10_000.0, trades=trades,
                        equity_checkpoints=checkpoints,
                    )

    def test_metrics_deny_malformed_trade_and_checkpoint_collections(self):
        class HostileTrade:
            @property
            def net_pnl_usd(self):
                raise AssertionError("hostile trade getter invoked")

        for invalid in (None, True, "trades", {}, [None],
                        [{}], [HostileTrade()]):
            with self.subTest(trades=type(invalid).__name__):
                with self.assertRaisesRegex(ValueError, "TradeRecord"):
                    compute_backtest_metrics(
                        starting_equity_usd=10_000.0, trades=invalid,
                        equity_checkpoints=(),
                    )
        for invalid in (None, False, "checkpoints", {}, [None], [{}]):
            with self.subTest(checkpoints=type(invalid).__name__):
                with self.assertRaisesRegex(ValueError, "EquityCheckpoint"):
                    compute_backtest_metrics(
                        starting_equity_usd=10_000.0, trades=(),
                        equity_checkpoints=invalid,
                    )

    def test_metrics_deny_untyped_nonfinite_and_negative_trade_costs(self):
        good = trade(trade_id="CANONICAL", minutes=1, net_pnl_usd=10.0)
        for field in ("net_pnl_usd", "slippage_cost_usd",
                      "commission_cost_usd", "financing_cost_usd"):
            for invalid in (True, "10", None, float("nan"), 10 ** 400):
                with self.subTest(field=field, value=repr(invalid)):
                    with self.assertRaisesRegex(ValueError, field):
                        compute_backtest_metrics(
                            starting_equity_usd=10_000.0,
                            trades=(replace(good, **{field: invalid}),),
                            equity_checkpoints=(),
                        )
        for field in ("slippage_cost_usd", "commission_cost_usd"):
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, field):
                    compute_backtest_metrics(
                        starting_equity_usd=10_000.0,
                        trades=(replace(good, **{field: -1.0}),),
                        equity_checkpoints=(),
                    )
        credit = replace(good, financing_cost_usd=-2.0)
        self.assertEqual(compute_backtest_metrics(
            starting_equity_usd=10_000.0,
            trades=(credit,), equity_checkpoints=(),
        )["financing_cost_usd"], -2.0)

    def test_metrics_reject_bad_checkpoint_timestamps_and_equity_values(self):
        good = EquityCheckpoint(BASE_TS, 10_000.0)
        for invalid in (None, "2026-09-14", datetime(2026, 9, 14),
                        42):
            with self.subTest(timestamp=repr(invalid)):
                with self.assertRaisesRegex(ValueError, "timestamp"):
                    compute_backtest_metrics(
                        starting_equity_usd=10_000.0, trades=(),
                        equity_checkpoints=(replace(
                            good, timestamp_utc=invalid
                        ),),
                    )
        for invalid in (None, True, "10000", float("nan"), 10 ** 400):
            with self.subTest(equity=repr(invalid)):
                with self.assertRaisesRegex(ValueError, "equity checkpoint"):
                    compute_backtest_metrics(
                        starting_equity_usd=10_000.0, trades=(),
                        equity_checkpoints=(replace(
                            good, realized_risk_equity_usd=invalid
                        ),),
                    )

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

    def test_artifact_writer_rejects_untyped_run_without_any_io(self):
        class HostileRun:
            @property
            def run_identity(self):
                raise AssertionError("unexpected hostile run getter")

        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "missing"
            for invalid in (None, True, {}, "BacktestRun", HostileRun()):
                with self.subTest(value_type=type(invalid).__name__):
                    with mock.patch("pathlib.Path.mkdir", side_effect=AssertionError(
                        "malformed run must not create artifact directory"
                    )):
                        with self.assertRaisesRegex(ValueError, "BacktestRun"):
                            write_backtest_artifacts(invalid, target)
                    self.assertFalse(target.exists())

    def test_artifact_writer_rejects_nonfinite_metrics_before_directory_creation(self):
        base = BacktestRun(
            run_identity={"code_commit": "synthetic"},
            trades=(), rejections=(), equity_checkpoints=(), metrics={},
        )
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "missing"
            for invalid in (float("nan"), float("inf")):
                with self.subTest(metric=repr(invalid)):
                    with mock.patch("pathlib.Path.mkdir", side_effect=AssertionError(
                        "invalid evidence must not touch filesystem"
                    )):
                        with self.assertRaisesRegex(ValueError, "non-finite"):
                            write_backtest_artifacts(
                                replace(base, metrics={"net_pnl_usd": invalid}),
                                target,
                            )
                    self.assertFalse(target.exists())

    def test_artifact_writer_rejects_unserializable_identity_before_directory(self):
        base = BacktestRun(
            run_identity={"code_commit": object()},
            trades=(), rejections=(), equity_checkpoints=(), metrics={},
        )
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "missing"
            with mock.patch("pathlib.Path.mkdir", side_effect=AssertionError(
                "unserializable run must not touch filesystem"
            )):
                with self.assertRaises(TypeError):
                    write_backtest_artifacts(base, target)
            self.assertFalse(target.exists())

    def test_artifact_writer_rejects_untyped_collections_before_any_io(self):
        base = BacktestRun(
            run_identity={"code_commit": "synthetic"},
            trades=(), rejections=(), equity_checkpoints=(), metrics={},
        )
        for field in ("trades", "rejections", "equity_checkpoints"):
            for invalid in (None, "bad", {}, [None], [object()]):
                with self.subTest(field=field, collection=repr(invalid)[:50]):
                    malformed = replace(base, **{field: invalid})
                    with tempfile.TemporaryDirectory() as root:
                        target = Path(root) / "not-created"
                        with mock.patch("pathlib.Path.mkdir", side_effect=AssertionError(
                            "malformed collections must not reach filesystem"
                        )):
                            with self.assertRaisesRegex(ValueError, field):
                                write_backtest_artifacts(malformed, target)
                        self.assertFalse(target.exists())

    def test_artifact_writer_does_not_read_hostile_record_getters(self):
        class HostileTrade:
            @property
            def exit_timestamp_utc(self):
                raise AssertionError("hostile trade getter accessed")

        base = BacktestRun(
            run_identity={"code_commit": "synthetic"},
            trades=(HostileTrade(),), rejections=(),
            equity_checkpoints=(), metrics={},
        )
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "not-created"
            with mock.patch("pathlib.Path.mkdir", side_effect=AssertionError(
                "hostile record must not create files"
            )):
                with self.assertRaisesRegex(ValueError, "TradeRecord"):
                    write_backtest_artifacts(base, target)
            self.assertFalse(target.exists())

    def test_artifact_writer_keeps_valid_empty_list_sequence_controls(self):
        run = BacktestRun(
            run_identity={"code_commit": "synthetic"},
            trades=[], rejections=[], equity_checkpoints=[], metrics={},
        )
        with tempfile.TemporaryDirectory() as root:
            manifest = write_backtest_artifacts(run, Path(root) / "valid")
            self.assertEqual(manifest["protocol"], "fmp-phase3-backtest-artifacts-v1")
            self.assertEqual((Path(root) / "valid/trades.jsonl").read_bytes(), b"")
            self.assertEqual((Path(root) / "valid/rejections.jsonl").read_bytes(), b"")

    def test_artifact_identity_rejects_nonstr_keys_without_file_creation(self):
        base = BacktestRun(
            run_identity={"1": "canonical", 1: "coercion-collision"},
            trades=(), rejections=(), equity_checkpoints=(), metrics={},
        )
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "bad"
            with mock.patch("pathlib.Path.mkdir", side_effect=AssertionError(
                "invalid identity keys must fail without I/O"
            )):
                with self.assertRaisesRegex(ValueError, "mapping keys"):
                    write_backtest_artifacts(base, target)
            self.assertFalse(target.exists())

    def test_artifact_identity_rejects_control_and_surrogate_keys(self):
        for bad in ("bad\nline", "bad\x00nul", "bad\ud800surrogate"):
            with self.subTest(value=ascii(bad)):
                base = BacktestRun(
                    run_identity={bad: "value"},
                    trades=(), rejections=(), equity_checkpoints=(), metrics={},
                )
                with tempfile.TemporaryDirectory() as root:
                    target = Path(root) / "bad"
                    with mock.patch("pathlib.Path.mkdir", side_effect=AssertionError(
                        "unprintable evidence key must not make artifacts"
                    )):
                        with self.assertRaisesRegex(ValueError, "mapping keys"):
                            write_backtest_artifacts(base, target)
                    self.assertFalse(target.exists())

    def test_artifact_identity_preserves_nested_unicode_keys(self):
        run = BacktestRun(
            run_identity={"café": {"日本語": "synthetic"}, "": "allowed"},
            trades=(), rejections=(), equity_checkpoints=(), metrics={},
        )
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "valid"
            write_backtest_artifacts(run, target)
            payload = json.loads((target / "summary.json").read_text("utf-8"))
            self.assertEqual(payload["run_identity"], run.run_identity)

    def test_artifact_writer_refuses_opaque_dataclasses_before_io(self):
        @dataclass(frozen=True)
        class HostileMetadata:
            key: str = "synthetic"

            def __getattribute__(self, name):
                if name == "key":
                    raise AssertionError("user dataclass getter ran")
                return object.__getattribute__(self, name)

        run = BacktestRun(
            run_identity={"opaque": HostileMetadata()},
            trades=(), rejections=(), equity_checkpoints=(), metrics={},
        )
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "should-not-exist"
            with mock.patch("pathlib.Path.mkdir", side_effect=AssertionError(
                "untrusted dataclass must not access filesystem"
            )):
                with self.assertRaisesRegex(ValueError, "dataclass"):
                    write_backtest_artifacts(run, target)
            self.assertFalse(target.exists())

    def test_artifact_writer_refuses_nested_backtest_run_as_identity_value(self):
        nested = BacktestRun(
            run_identity={}, trades=(), rejections=(),
            equity_checkpoints=(), metrics={},
        )
        wrapper = replace(nested, run_identity={"nested": nested})
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "blocked"
            with self.assertRaisesRegex(ValueError, "dataclass"):
                write_backtest_artifacts(wrapper, target)
            self.assertFalse(target.exists())

    def test_artifact_writer_keeps_source_record_dataclass_serialization(self):
        checkpoint = EquityCheckpoint(BASE_TS, 10_000.0)
        record = RejectionRecord(
            decision_id="NO", symbol="EURUSD",
            decision_timestamp_utc=BASE_TS,
            evaluated_timestamp_utc=BASE_TS,
            code=RejectionCode.NO_TRADE, explanation="synthetic",
        )
        run = BacktestRun(
            run_identity={"code_commit": "synthetic"},
            trades=(), rejections=(record,),
            equity_checkpoints=(checkpoint,), metrics={},
        )
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "ok"
            write_backtest_artifacts(run, target)
            summary = json.loads((target / "summary.json").read_text("utf-8"))
            rejection = json.loads((target / "rejections.jsonl").read_text("utf-8"))
            self.assertEqual(summary["equity_checkpoints"][0]["realized_risk_equity_usd"], 10_000.0)
            self.assertEqual(rejection["code"], "NO_TRADE")

    def test_artifact_writer_rejects_surrogate_text_before_io(self):
        for string in ("bad\ud800text", "\udfff", "before\ud812after"):
            with self.subTest(value=ascii(string)):
                run = BacktestRun(
                    run_identity={"reason": string}, trades=(), rejections=(),
                    equity_checkpoints=(), metrics={},
                )
                with tempfile.TemporaryDirectory() as root:
                    target = Path(root) / "missing"
                    with mock.patch("pathlib.Path.mkdir", side_effect=AssertionError(
                        "invalid unicode cannot write output"
                    )):
                        with self.assertRaisesRegex(ValueError, "surrogate"):
                            write_backtest_artifacts(run, target)
                    self.assertFalse(target.exists())

    def test_artifact_writer_rejects_giant_integer_metadata_before_io(self):
        for value in (2 ** 512, -(2 ** 512), 10 ** 400):
            with self.subTest(bits=value.bit_length()):
                run = BacktestRun(
                    run_identity={"unsafe_counter": value}, trades=(),
                    rejections=(), equity_checkpoints=(), metrics={},
                )
                with tempfile.TemporaryDirectory() as root:
                    target = Path(root) / "missing"
                    with mock.patch("pathlib.Path.mkdir", side_effect=AssertionError(
                        "giant integer cannot write output"
                    )):
                        with self.assertRaisesRegex(ValueError, "safe width"):
                            write_backtest_artifacts(run, target)
                    self.assertFalse(target.exists())

    def test_artifact_writer_keeps_valid_unicode_and_integer_boundaries(self):
        run = BacktestRun(
            run_identity={
                "message": "Café 日本語 - synthetic",
                "count": 2 ** 511,
                "line": "regular text",
            }, trades=(), rejections=(), equity_checkpoints=(), metrics={},
        )
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "valid"
            write_backtest_artifacts(run, target)
            saved = json.loads((target / "summary.json").read_text("utf-8"))
            self.assertEqual(saved["run_identity"], run.run_identity)

    def test_artifact_writer_rejects_invalid_run_identity_mapping(self):
        base = BacktestRun(
            run_identity={}, trades=(), rejections=(),
            equity_checkpoints=(), metrics={},
        )
        for invalid in (None, True, "identity", [], [("key", "value")]):
            with self.subTest(value=repr(invalid)[:50]):
                with tempfile.TemporaryDirectory() as root:
                    target = Path(root) / "invalid"
                    with mock.patch("pathlib.Path.mkdir", side_effect=AssertionError(
                        "identity mismatch must not touch files"
                    )):
                        with self.assertRaisesRegex(ValueError, "run_identity"):
                            write_backtest_artifacts(
                                replace(base, run_identity=invalid), target,
                            )
                    self.assertFalse(target.exists())

    def test_artifact_writer_rejects_invalid_metrics_mapping(self):
        base = BacktestRun(
            run_identity={}, trades=(), rejections=(),
            equity_checkpoints=(), metrics={},
        )
        for invalid in (None, "metrics", False, [], object()):
            with self.subTest(value_type=type(invalid).__name__):
                with tempfile.TemporaryDirectory() as root:
                    target = Path(root) / "invalid"
                    with mock.patch("pathlib.Path.mkdir", side_effect=AssertionError(
                        "untyped metrics cannot create artifacts"
                    )):
                        with self.assertRaisesRegex(ValueError, "metrics"):
                            write_backtest_artifacts(
                                replace(base, metrics=invalid), target,
                            )
                    self.assertFalse(target.exists())

    def test_artifact_writer_preserves_immutable_mapping_inputs(self):
        run = BacktestRun(
            run_identity=MappingProxyType({"code_commit": "synthetic"}),
            trades=(), rejections=(), equity_checkpoints=(),
            metrics=MappingProxyType({"trade_count": 0}),
        )
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "valid"
            write_backtest_artifacts(run, target)
            saved = json.loads((target / "metrics.json").read_text("utf-8"))
            self.assertEqual(saved, {"trade_count": 0})
            self.assertEqual(
                json.loads((target / "summary.json").read_text("utf-8"))["run_identity"],
                {"code_commit": "synthetic"},
            )

    def test_rejection_evidence_rejects_invalid_enum_and_identity_before_io(self):
        good = RejectionRecord(
            decision_id="SYNTHETIC", symbol="EURUSD",
            decision_timestamp_utc=BASE_TS,
            evaluated_timestamp_utc=BASE_TS,
            code=RejectionCode.NO_TRADE, explanation="filtered",
        )
        for field, invalid in (
            ("code", "NO_TRADE"), ("code", None),
            ("symbol", "eurusd"), ("symbol", None),
            ("decision_id", None), ("decision_id", "bad\nline"),
        ):
            with self.subTest(field=field, value=repr(invalid)):
                run = BacktestRun(
                    run_identity={}, trades=(),
                    rejections=(replace(good, **{field: invalid}),),
                    equity_checkpoints=(), metrics={},
                )
                with tempfile.TemporaryDirectory() as root:
                    target = Path(root) / "invalid"
                    with mock.patch("pathlib.Path.mkdir", side_effect=AssertionError(
                        "invalid rejection cannot publish artifacts"
                    )):
                        with self.assertRaisesRegex(ValueError, "rejection"):
                            write_backtest_artifacts(run, target)
                    self.assertFalse(target.exists())

    def test_rejection_evidence_rejects_invalid_explanation_before_io(self):
        good = RejectionRecord(
            decision_id="SYNTHETIC", symbol="EURUSD",
            decision_timestamp_utc=BASE_TS,
            evaluated_timestamp_utc=BASE_TS,
            code=RejectionCode.NO_TRADE, explanation="filtered",
        )
        for invalid in (None, 17, "", "\x00bad", "bad\nline",
                        "x" * 4097):
            with self.subTest(value=repr(invalid)[:50]):
                run = BacktestRun(
                    run_identity={}, trades=(),
                    rejections=(replace(good, explanation=invalid),),
                    equity_checkpoints=(), metrics={},
                )
                with tempfile.TemporaryDirectory() as root:
                    target = Path(root) / "invalid"
                    with mock.patch("pathlib.Path.mkdir", side_effect=AssertionError(
                        "invalid explanation cannot publish"
                    )):
                        with self.assertRaisesRegex(ValueError, "explanation"):
                            write_backtest_artifacts(run, target)
                    self.assertFalse(target.exists())

    def test_rejection_evidence_rejects_backdated_or_non_utc_times(self):
        good = RejectionRecord(
            decision_id="SYNTHETIC", symbol="EURUSD",
            decision_timestamp_utc=BASE_TS,
            evaluated_timestamp_utc=BASE_TS + timedelta(minutes=1),
            code=RejectionCode.NO_TRADE, explanation="filtered",
        )
        for field, invalid in (
            ("decision_timestamp_utc", "2026-09-14"),
            ("evaluated_timestamp_utc", datetime(2026, 9, 14)),
            ("evaluated_timestamp_utc", BASE_TS - timedelta(minutes=1)),
        ):
            run = BacktestRun(
                run_identity={}, trades=(),
                rejections=(replace(good, **{field: invalid}),),
                equity_checkpoints=(), metrics={},
            )
            with self.subTest(field=field, value=repr(invalid)):
                with tempfile.TemporaryDirectory() as root:
                    target = Path(root) / "invalid"
                    with self.assertRaisesRegex(ValueError, "rejection"):
                        write_backtest_artifacts(run, target)
                    self.assertFalse(target.exists())

    def test_trade_evidence_rejects_malformed_identity_enums_and_size(self):
        good = trade(trade_id="SYNTHETIC", minutes=1, net_pnl_usd=10.0)
        for field, invalid in (
            ("trade_id", None), ("trade_id", "bad\nline"),
            ("decision_id", True), ("symbol", "AUDUSD"),
            ("direction", "LONG"), ("exit_reason", "TARGET"),
            ("units", True), ("units", 0), ("units", 2 ** 63),
        ):
            with self.subTest(field=field, value=repr(invalid)):
                run = BacktestRun(
                    run_identity={}, trades=(replace(good, **{field: invalid}),),
                    rejections=(), equity_checkpoints=(), metrics={},
                )
                with tempfile.TemporaryDirectory() as root:
                    target = Path(root) / "invalid"
                    with mock.patch("pathlib.Path.mkdir", side_effect=AssertionError(
                        "malformed trade must fail before publication"
                    )):
                        with self.assertRaisesRegex(ValueError, "trade"):
                            write_backtest_artifacts(run, target)
                    self.assertFalse(target.exists())

    def test_trade_evidence_rejects_non_utc_and_backdated_exit(self):
        good = trade(trade_id="SYNTHETIC", minutes=1, net_pnl_usd=10.0)
        for field, invalid in (
            ("entry_timestamp_utc", "2026-09-14"),
            ("exit_timestamp_utc", datetime(2026, 9, 14)),
            ("exit_timestamp_utc", good.entry_timestamp_utc - timedelta(minutes=1)),
        ):
            with self.subTest(field=field, value=repr(invalid)):
                run = BacktestRun(
                    run_identity={}, trades=(replace(good, **{field: invalid}),),
                    rejections=(), equity_checkpoints=(), metrics={},
                )
                with tempfile.TemporaryDirectory() as root:
                    target = Path(root) / "invalid"
                    with self.assertRaisesRegex(ValueError, "trade"):
                        write_backtest_artifacts(run, target)
                    self.assertFalse(target.exists())

    def test_trade_evidence_keeps_same_bar_exit_allowed(self):
        good = trade(trade_id="SYNTHETIC", minutes=1, net_pnl_usd=10.0)
        same_bar = replace(good, exit_timestamp_utc=good.entry_timestamp_utc)
        run = BacktestRun(
            run_identity={}, trades=(same_bar,), rejections=(),
            equity_checkpoints=(), metrics={},
        )
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "valid"
            write_backtest_artifacts(run, target)
            rows = (target / "trades.jsonl").read_text("utf-8").splitlines()
            self.assertEqual(len(rows), 1)
            record = json.loads(rows[0])
            self.assertEqual(record["direction"], "LONG")
            self.assertEqual(record["entry_timestamp_utc"],
                             record["exit_timestamp_utc"])

    def test_trade_artifacts_reject_malformed_prices_before_io(self):
        good = trade(trade_id="VALID", minutes=1, net_pnl_usd=10.0)
        for field in ("entry_reference_price", "exit_reference_price",
                      "entry_price", "exit_price", "stop_price", "target_price"):
            for invalid in (None, True, "1.1", float("nan"), float("inf"),
                            10 ** 400, 0.0, -1.0):
                if field == "target_price" and invalid is None:
                    continue
                with self.subTest(field=field, value=repr(invalid)[:32]):
                    run = BacktestRun(
                        run_identity={}, trades=(replace(good, **{field: invalid}),),
                        rejections=(), equity_checkpoints=(), metrics={},
                    )
                    with tempfile.TemporaryDirectory() as root:
                        target = Path(root) / "blocked"
                        with mock.patch("pathlib.Path.mkdir", side_effect=AssertionError(
                            "invalid trade price must not create files"
                        )):
                            with self.assertRaisesRegex(ValueError, field):
                                write_backtest_artifacts(run, target)
                        self.assertFalse(target.exists())

    def test_trade_artifacts_reject_invalid_pnl_costs_and_equity(self):
        good = trade(trade_id="VALID", minutes=1, net_pnl_usd=10.0)
        fields = ("gross_pnl_usd", "slippage_cost_usd",
                  "commission_cost_usd", "financing_cost_usd",
                  "net_pnl_usd", "risk_equity_before_usd",
                  "risk_equity_after_usd")
        for field in fields:
            for invalid in (None, True, "10", float("nan"), 10 ** 400):
                with self.subTest(field=field, value=repr(invalid)[:32]):
                    run = BacktestRun(
                        run_identity={}, trades=(replace(good, **{field: invalid}),),
                        rejections=(), equity_checkpoints=(), metrics={},
                    )
                    with tempfile.TemporaryDirectory() as root:
                        target = Path(root) / "blocked"
                        with mock.patch("pathlib.Path.mkdir", side_effect=AssertionError(
                            "invalid trade financials must not create files"
                        )):
                            with self.assertRaisesRegex(ValueError, field):
                                write_backtest_artifacts(run, target)
                        self.assertFalse(target.exists())
        for field in ("slippage_cost_usd", "commission_cost_usd"):
            with self.subTest(field=field, value=-1.0):
                run = BacktestRun(
                    run_identity={}, trades=(replace(good, **{field: -1.0}),),
                    rejections=(), equity_checkpoints=(), metrics={},
                )
                with self.assertRaisesRegex(ValueError, field):
                    write_backtest_artifacts(run, Path("never-created"))

    def test_trade_artifacts_preserve_valid_financing_credit_and_no_target(self):
        original = trade(trade_id="VALID", minutes=1, net_pnl_usd=10.0)
        valid = replace(original, target_price=None, financing_cost_usd=-2.0,
                        intrabar_ambiguous=True)
        run = BacktestRun(
            run_identity={}, trades=(valid,), rejections=(),
            equity_checkpoints=(), metrics={},
        )
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "valid"
            write_backtest_artifacts(run, path)
            row = json.loads((path / "trades.jsonl").read_text("utf-8"))
            self.assertIsNone(row["target_price"])
            self.assertEqual(row["financing_cost_usd"], -2.0)
            self.assertTrue(row["intrabar_ambiguous"])

    def test_trade_artifacts_reject_non_boolean_ambiguity_flag(self):
        original = trade(trade_id="VALID", minutes=1, net_pnl_usd=10.0)
        for invalid in (0, 1, None, "False"):
            with self.subTest(value=repr(invalid)):
                run = BacktestRun(
                    run_identity={}, trades=(replace(
                        original, intrabar_ambiguous=invalid,
                    ),), rejections=(), equity_checkpoints=(), metrics={},
                )
                with self.assertRaisesRegex(ValueError, "intrabar_ambiguous"):
                    write_backtest_artifacts(run, Path("never-created"))

    def test_artifact_writer_rejects_invalid_checkpoint_times_before_io(self):
        checkpoint = EquityCheckpoint(BASE_TS, 10_000.0)
        for invalid in (None, "2026-09-14", datetime(2026, 9, 14), 7):
            with self.subTest(timestamp=repr(invalid)):
                run = BacktestRun(
                    run_identity={}, trades=(), rejections=(),
                    equity_checkpoints=(replace(
                        checkpoint, timestamp_utc=invalid,
                    ),), metrics={},
                )
                with tempfile.TemporaryDirectory() as root:
                    target = Path(root) / "blocked"
                    with mock.patch("pathlib.Path.mkdir", side_effect=AssertionError(
                        "malformed checkpoint must not create files"
                    )):
                        with self.assertRaisesRegex(ValueError, "checkpoint timestamp"):
                            write_backtest_artifacts(run, target)
                    self.assertFalse(target.exists())

    def test_artifact_writer_rejects_invalid_checkpoint_equity_before_io(self):
        checkpoint = EquityCheckpoint(BASE_TS, 10_000.0)
        for invalid in (None, True, "10000", float("nan"),
                        float("inf"), 10 ** 400):
            with self.subTest(value=repr(invalid)):
                run = BacktestRun(
                    run_identity={}, trades=(), rejections=(),
                    equity_checkpoints=(replace(
                        checkpoint, realized_risk_equity_usd=invalid,
                    ),), metrics={},
                )
                with tempfile.TemporaryDirectory() as root:
                    target = Path(root) / "blocked"
                    with mock.patch("pathlib.Path.mkdir", side_effect=AssertionError(
                        "malformed equity must not create files"
                    )):
                        with self.assertRaisesRegex(ValueError, "equity checkpoint"):
                            write_backtest_artifacts(run, target)
                    self.assertFalse(target.exists())

    def test_artifact_writer_rejects_backdated_checkpoint_sequence(self):
        run = BacktestRun(
            run_identity={}, trades=(), rejections=(),
            equity_checkpoints=(
                EquityCheckpoint(BASE_TS + timedelta(minutes=1), 10_100.0),
                EquityCheckpoint(BASE_TS, 10_000.0),
            ), metrics={},
        )
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "blocked"
            with mock.patch("pathlib.Path.mkdir", side_effect=AssertionError(
                "backdated equity checkpoint must not publish"
            )):
                with self.assertRaisesRegex(ValueError, "chronological"):
                    write_backtest_artifacts(run, target)
            self.assertFalse(target.exists())

    def test_artifact_writer_preserves_equal_time_checkpoints(self):
        run = BacktestRun(
            run_identity={}, trades=(), rejections=(),
            equity_checkpoints=(
                EquityCheckpoint(BASE_TS, 10_000.0),
                EquityCheckpoint(BASE_TS, 10_025.0),
            ), metrics={},
        )
        with tempfile.TemporaryDirectory() as root:
            target = Path(root) / "valid"
            write_backtest_artifacts(run, target)
            summary = json.loads((target / "summary.json").read_text("utf-8"))
            self.assertEqual(len(summary["equity_checkpoints"]), 2)

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
