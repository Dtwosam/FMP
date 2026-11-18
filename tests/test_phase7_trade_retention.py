"""Synthetic checks for opt-in Phase 7 trade retention.

These tests build quote bars in memory. They do not read historical market
data, download artifacts, or dispatch a workflow.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fmp.contracts import Direction, QuoteBar, RejectionCode
from fmp.research.trade_level_evidence import (
    REQUESTED_RISK_R_DEFINITION,
    validate_trade_submission,
)
from fmp.strategies.contracts import SignalCandidate
from fmp.walkforward.contracts import (
    EXPERIMENT_ID,
    PHASE6_CHECKPOINT_SHA,
    STAGE2_WINDOWS,
    USDJPY_PROCESSED_MANIFEST_SHA256,
)
from fmp.walkforward.data import LoadedPhase7Bars
from fmp.walkforward.gates import stage2_gate


UTC = timezone.utc
CODE = "dec636-synthetic-source"
WINDOW = "stage1-2024"
ORIGINAL_ARTIFACT = "10414817824"


def _bar(
    timestamp: datetime,
    bid_open: float,
    bid_high: float,
    bid_low: float,
    bid_close: float,
) -> QuoteBar:
    spread = 0.02
    return QuoteBar(
        timestamp_utc=timestamp,
        symbol="USDJPY",
        bid_open=bid_open,
        bid_high=bid_high,
        bid_low=bid_low,
        bid_close=bid_close,
        ask_open=bid_open + spread,
        ask_high=bid_high + spread,
        ask_low=bid_low + spread,
        ask_close=bid_close + spread,
    )


def _loaded() -> LoadedPhase7Bars:
    warmup = _bar(datetime(2023, 12, 31, 23, 45, tzinfo=UTC), 150.00, 150.10, 149.90, 150.04)
    scored = (
        _bar(datetime(2024, 1, 1, 0, 0, tzinfo=UTC), 150.00, 150.10, 149.90, 150.04),
        _bar(datetime(2024, 1, 1, 0, 15, tzinfo=UTC), 150.00, 150.20, 149.95, 150.05),
        _bar(datetime(2024, 1, 1, 0, 30, tzinfo=UTC), 150.10, 150.45, 150.00, 150.30),
        _bar(datetime(2024, 1, 1, 0, 45, tzinfo=UTC), 150.00, 150.15, 149.85, 150.02),
        _bar(datetime(2024, 1, 1, 1, 0, tzinfo=UTC), 149.85, 149.95, 149.60, 149.70),
    )
    return LoadedPhase7Bars(
        bars=(warmup, *scored),
        scored_bars=scored,
        eligible_scored_dates=(date(2024, 1, 1),),
        opened_partition_keys=("15m:2023-12", "15m:2024-01"),
        warmup_range=(
            datetime(2023, 12, 25, tzinfo=UTC),
            datetime(2024, 1, 1, tzinfo=UTC),
        ),
    )


def _candidate(
    candidate_id: str,
    observation: datetime,
    known: datetime,
    *,
    direction: Direction = Direction.LONG,
    stop: float | None = None,
    target: float | None = None,
) -> SignalCandidate:
    return SignalCandidate(
        candidate_id=candidate_id,
        symbol="USDJPY",
        observation_bar_timestamp_utc=observation,
        signal_known_timestamp_utc=known,
        direction=direction,
        stop_price=stop,
        target_price=target,
        latest_exit_timestamp_utc=None,
        reason_code="SYNTHETIC_SESSION_BREAKOUT",
        metadata={"session_name": "tokyo"},
    )


def _candidates() -> tuple[SignalCandidate, ...]:
    t0 = datetime(2024, 1, 1, 0, 0, tzinfo=UTC)
    t15 = datetime(2024, 1, 1, 0, 15, tzinfo=UTC)
    t30 = datetime(2024, 1, 1, 0, 30, tzinfo=UTC)
    t45 = datetime(2024, 1, 1, 0, 45, tzinfo=UTC)
    return (
        _candidate("syn-win", t0, t15, stop=149.90, target=150.40),
        _candidate("syn-no-trade", t0, t15, direction=Direction.NO_TRADE),
        _candidate("syn-lose", t30, t45, stop=149.70, target=151.00),
    )


def _retain(loaded: LoadedPhase7Bars, slippage: float):
    from fmp.walkforward.retention import retain_phase7_window

    with patch(
        "fmp.walkforward.evaluation.generate_session_breakout_candidates",
        return_value=_candidates(),
    ):
        return retain_phase7_window(
            loaded,
            candidate_id="session_breakout",
            window_name=WINDOW,
            code_commit=CODE,
            slippage_pips=slippage,
        )


def _rewrite_checksums(root: Path) -> None:
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for record in manifest["artifacts"]:
        data = (root / record["path"]).read_bytes()
        record["sha256"] = hashlib.sha256(data).hexdigest()
        record["size_bytes"] = len(data)
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def _stage2_rows():
    pnls = (100.0, 100.0, 100.0, 100.0, -10.0, -10.0, -10.0)
    out = {}
    for slippage in (0.2, 0.5, 1.0):
        rows = []
        for window, pnl in zip(STAGE2_WINDOWS, pnls, strict=True):
            start = datetime(window.start.year, window.start.month, window.start.day, tzinfo=UTC)
            end = datetime(
                window.end_exclusive.year,
                window.end_exclusive.month,
                window.end_exclusive.day,
                tzinfo=UTC,
            )
            gross_profit = max(pnl, 0.0) + 200.0
            gross_loss = gross_profit - pnl
            rows.append(
                SimpleNamespace(
                    candidate_id="session_breakout",
                    window_name=window.name,
                    slippage_pips=slippage,
                    candidate_count=50,
                    scored_candidate_count=45,
                    directional_candidate_count=40,
                    trade_count=15,
                    net_pnl_usd=pnl,
                    net_return=pnl / 100_000.0,
                    expectancy_usd=pnl / 15,
                    gross_profit_usd=gross_profit,
                    gross_loss_usd=gross_loss,
                    profit_factor=gross_profit / gross_loss,
                    max_drawdown_fraction=0.04,
                    warmup_range=(start - timedelta(days=7), start),
                    opened_partition_keys=("15m:2024-12", "15m:2025-01"),
                    scored_start_utc=start,
                    scored_end_utc=end,
                    refit_status="NOT_APPLICABLE_FIXED_RULE",
                )
            )
        out[slippage] = tuple(rows)
    return out


class Phase7TradeRetentionTests(unittest.TestCase):
    def test_export_uses_the_same_execution_without_changing_economics(self) -> None:
        from fmp.backtest.engine import run_backtest as real_run
        from fmp.walkforward.evaluation import evaluate_window
        from fmp.walkforward.retention import retain_phase7_window

        loaded = _loaded()
        with patch(
            "fmp.walkforward.evaluation.generate_session_breakout_candidates",
            return_value=_candidates(),
        ), patch(
            "fmp.walkforward.evaluation.run_backtest",
            wraps=real_run,
        ) as engine, patch(
            "fmp.walkforward.artifacts.write_stage2_evidence",
        ) as aggregate_writer:
            financial = evaluate_window(
                loaded,
                candidate_id="session_breakout",
                window_name=WINDOW,
                code_commit=CODE,
                slippage_pips=0.2,
            )
            retained = retain_phase7_window(
                loaded,
                candidate_id="session_breakout",
                window_name=WINDOW,
                code_commit=CODE,
                slippage_pips=0.2,
            )

        self.assertEqual(engine.call_count, 2)
        first, second = engine.call_args_list
        self.assertEqual(first.kwargs["bars"], loaded.scored_bars)
        self.assertEqual(first.kwargs["bars"], second.kwargs["bars"])
        self.assertEqual(first.kwargs["decisions"], second.kwargs["decisions"])
        self.assertEqual(first.kwargs["scheduled_exits"], second.kwargs["scheduled_exits"])
        self.assertEqual(first.kwargs["config"], second.kwargs["config"])
        aggregate_writer.assert_not_called()

        self.assertEqual(financial, retained.financial)
        self.assertEqual(financial.trade_count, 2)
        self.assertEqual(financial.candidate_count, 3)
        self.assertEqual(financial.scored_candidate_count, 3)
        self.assertEqual(financial.directional_candidate_count, 2)
        self.assertGreater(financial.gross_profit_usd, 0.0)
        self.assertGreater(financial.gross_loss_usd, 0.0)
        self.assertAlmostEqual(
            financial.net_pnl_usd,
            financial.gross_profit_usd - financial.gross_loss_usd,
            places=6,
        )
        self.assertEqual(financial.scored_start_utc, datetime(2024, 1, 1, tzinfo=UTC))
        self.assertEqual(financial.scored_end_utc, datetime(2025, 1, 1, tzinfo=UTC))
        self.assertEqual(
            financial.warmup_range,
            (datetime(2023, 12, 25, tzinfo=UTC), datetime(2024, 1, 1, tzinfo=UTC)),
        )
        self.assertEqual(financial.refit_status, "NOT_APPLICABLE_FIXED_RULE")
        self.assertEqual(financial.run_identity["code_commit"], CODE)
        self.assertEqual(financial.run_identity["starting_equity_usd"], 100_000.0)
        self.assertEqual(financial.run_identity["slippage_pips"], 0.2)
        self.assertEqual(
            financial.run_identity["decision_config"]["parameters"],
            {"buffer_pips": 5, "target_range_multiple": 1.5},
        )
        self.assertEqual(financial.run_identity["decision_config"]["experiment_id"], EXPERIMENT_ID)

        trades = {trade.trade_id: trade for trade in retained.trades}
        self.assertEqual(set(trades), {"syn-win", "syn-lose"})
        winner = trades["syn-win"]
        loser = trades["syn-lose"]
        self.assertEqual(winner.decision_id, "syn-win")
        self.assertEqual(winner.entry_reference_price, 150.02)
        self.assertEqual(winner.exit_reference_price, 150.40)
        self.assertGreater(winner.entry_price, winner.entry_reference_price)
        self.assertLess(winner.exit_price, winner.exit_reference_price)
        self.assertGreater(winner.gross_pnl_usd, 0.0)
        self.assertGreater(winner.net_pnl_usd, 0.0)
        self.assertEqual(winner.commission_cost_usd, 0.0)
        self.assertEqual(winner.financing_cost_usd, 0.0)
        self.assertGreater(winner.slippage_cost_usd, 0.0)
        self.assertEqual(loser.entry_reference_price, 150.02)
        self.assertEqual(loser.exit_reference_price, 149.70)
        self.assertLess(loser.net_pnl_usd, 0.0)
        self.assertEqual(loser.commission_cost_usd, 0.0)
        self.assertEqual(loser.financing_cost_usd, 0.0)
        self.assertEqual(winner.risk_equity_before_usd, 100_000.0)
        self.assertAlmostEqual(
            winner.risk_equity_after_usd,
            winner.risk_equity_before_usd + winner.net_pnl_usd,
            places=6,
        )
        self.assertAlmostEqual(loser.risk_equity_before_usd, winner.risk_equity_after_usd, places=6)
        self.assertAlmostEqual(
            loser.risk_equity_after_usd,
            loser.risk_equity_before_usd + loser.net_pnl_usd,
            places=6,
        )
        self.assertEqual(
            [trade.trade_id for trade in retained.trades],
            ["syn-win", "syn-lose"],
        )
        self.assertEqual(
            [(row.decision_id, row.code) for row in retained.rejections],
            [("syn-no-trade", RejectionCode.NO_TRADE)],
        )
        self.assertNotIn("syn-no-trade", trades)

    def test_slippage_changes_fills_without_changing_decisions_or_bounds(self) -> None:
        loaded = _loaded()
        low = _retain(loaded, 0.2)
        high = _retain(loaded, 0.5)
        self.assertEqual(
            [trade.decision_id for trade in low.trades],
            [trade.decision_id for trade in high.trades],
        )
        self.assertEqual(low.financial.scored_start_utc, high.financial.scored_start_utc)
        self.assertEqual(low.financial.scored_end_utc, high.financial.scored_end_utc)
        self.assertEqual(low.financial.warmup_range, high.financial.warmup_range)
        self.assertEqual(low.financial.trade_count, high.financial.trade_count)
        for left, right in zip(low.trades, high.trades, strict=True):
            self.assertEqual(left.entry_reference_price, right.entry_reference_price)
            self.assertEqual(left.exit_reference_price, right.exit_reference_price)
            self.assertGreater(right.entry_price, left.entry_price)
            self.assertLess(right.exit_price, left.exit_price)
            self.assertGreater(right.slippage_cost_usd, left.slippage_cost_usd)
        winner_low, loser_low = low.trades
        winner_high, loser_high = high.trades
        self.assertEqual(winner_low.units, winner_high.units)
        self.assertEqual(winner_low.gross_pnl_usd, winner_high.gross_pnl_usd)
        self.assertLess(winner_high.net_pnl_usd, winner_low.net_pnl_usd)
        self.assertNotEqual(loser_low.units, loser_high.units)
        self.assertLess(high.financial.gross_profit_usd, low.financial.gross_profit_usd)
        self.assertNotEqual(high.financial.net_pnl_usd, low.financial.net_pnl_usd)

    def test_retention_preserves_existing_stage2_aggregate_bytes(self) -> None:
        from fmp.walkforward.artifacts import write_stage2_evidence
        from fmp.walkforward.retention import write_phase7_trade_retention

        loaded = _loaded()
        retained = tuple(_retain(loaded, slippage) for slippage in (0.2, 0.5, 1.0))
        rows = _stage2_rows()
        gate = stage2_gate(rows)
        identity = {
            "experiment_id": EXPERIMENT_ID,
            "candidate_id": "session_breakout",
            "status": "STAGE1_PASS",
            "code_commit": "stage1abc",
            "phase6_checkpoint_sha": PHASE6_CHECKPOINT_SHA,
            "processed_manifest_sha256": USDJPY_PROCESSED_MANIFEST_SHA256,
            "manifest_sha256": "a" * 64,
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            aggregate = root / "stage2"
            retention = root / "trades"
            write_stage2_evidence(
                out_dir=aggregate,
                candidate_id="session_breakout",
                code_commit=CODE,
                results_by_slippage=rows,
                gate=gate,
                stage1_identity=identity,
            )
            before = {path.name: path.read_bytes() for path in aggregate.iterdir()}
            self.assertEqual(set(before), {"result.json", "windows.json", "manifest.json"})
            first = write_phase7_trade_retention(
                retention_dir=retention,
                windows=retained,
                code_commit=CODE,
                aggregate_dir=aggregate,
            )
            after = {path.name: path.read_bytes() for path in aggregate.iterdir()}
            self.assertEqual(before, after)
            self.assertFalse((root / ORIGINAL_ARTIFACT).exists())
            self.assertNotIn(ORIGINAL_ARTIFACT, {path.name for path in retention.iterdir()})
            names = {path.name for path in retention.iterdir()}
            self.assertEqual(
                names,
                {"trades.jsonl", "rejections.jsonl", "window-index.json", "manifest.json"},
            )
            first_bytes = {name: (retention / name).read_bytes() for name in names}
            second = write_phase7_trade_retention(
                retention_dir=retention,
                windows=tuple(reversed(retained)),
                code_commit=CODE,
                aggregate_dir=aggregate,
            )
            second_bytes = {name: (retention / name).read_bytes() for name in names}
            self.assertEqual(first_bytes, second_bytes)
            self.assertEqual(first, second)
            self.assertFalse(first["authentic_stage2_series_recovered"])
            self.assertFalse(first["original_artifact_modified"])
            self.assertFalse(first["reproduction_authorized"])
            self.assertFalse(first["owner_authorization_recorded"])
            self.assertEqual(first["original_artifact_id"], ORIGINAL_ARTIFACT)
            trade_line = json.loads(first_bytes["trades.jsonl"].splitlines()[0])
            self.assertEqual(trade_line["code_commit"], CODE)
            self.assertEqual(trade_line["experiment_id"], EXPERIMENT_ID)
            self.assertEqual(trade_line["candidate_id"], "session_breakout")
            self.assertEqual(trade_line["window_name"], WINDOW)
            self.assertIn(trade_line["slippage_pips"], (0.2, 0.5, 1.0))
            self.assertEqual(trade_line["reproduction_target_artifact_id"], ORIGINAL_ARTIFACT)
            self.assertFalse(trade_line["authentic_stage2_series_recovered"])
            self.assertEqual(trade_line["spread_basis"], "included_in_bid_ask_reference")
            self.assertEqual(trade_line["spread_cost_usd"], 0.0)
            self.assertEqual(trade_line["r_definition"], REQUESTED_RISK_R_DEFINITION)

    def test_loaded_rows_pass_the_dec634_validator_per_slippage(self) -> None:
        from fmp.walkforward.retention import (
            load_phase7_trade_retention,
            write_phase7_trade_retention,
        )

        loaded = _loaded()
        retained = tuple(_retain(loaded, slippage) for slippage in (0.2, 0.5, 1.0))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "trades"
            write_phase7_trade_retention(
                retention_dir=root,
                windows=retained,
                code_commit=CODE,
            )
            loaded_retention = load_phase7_trade_retention(root)

        self.assertFalse(loaded_retention.authentic_stage2_series_recovered)
        self.assertEqual(loaded_retention.r_definition, REQUESTED_RISK_R_DEFINITION)
        self.assertEqual(len(loaded_retention.submissions), 3)
        decision_ids = []
        for submission in loaded_retention.submissions:
            self.assertFalse(submission.claims_trades_from_stage2_zip)
            self.assertEqual(submission.provenance.role, "synthetic_fixture")
            self.assertIsNone(submission.provenance.source_run_id)
            self.assertIsNone(submission.provenance.source_artifact_id)
            self.assertIsNone(submission.provenance.source_commit)
            validation = validate_trade_submission(submission)
            self.assertTrue(validation.accepted, validation.findings)
            self.assertFalse(validation.original_phase7_trade_ledger_verified)
            self.assertFalse(validation.probabilities_computed)
            self.assertEqual(validation.r_definition, REQUESTED_RISK_R_DEFINITION)
            self.assertEqual(validation.sample_size, 2)
            self.assertGreater(submission.windows[0].gross_loss_usd, 0.0)
            self.assertEqual(submission.windows[0].overlap_role, "none")
            self.assertEqual(
                [trade.trade_id for trade in submission.trades],
                ["syn-win", "syn-lose"],
            )
            decision_ids.append(tuple(trade.decision_id for trade in submission.trades))
        self.assertEqual(len(set(decision_ids)), 1)

    def test_missing_duplicate_malformed_and_inconsistent_records_fail(self) -> None:
        from fmp.walkforward.retention import (
            load_phase7_trade_retention,
            write_phase7_trade_retention,
        )

        loaded = _loaded()
        retained = _retain(loaded, 0.2)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "good"
            write_phase7_trade_retention(
                retention_dir=source,
                windows=(retained,),
                code_commit=CODE,
            )

            missing = root / "missing-file"
            missing.mkdir()
            for path in source.iterdir():
                (missing / path.name).write_bytes(path.read_bytes())
            (missing / "trades.jsonl").unlink()
            with self.assertRaisesRegex(ValueError, "missing retention file: trades.jsonl"):
                load_phase7_trade_retention(missing)
            with self.assertRaisesRegex(ValueError, "missing retention file: manifest.json"):
                load_phase7_trade_retention(root / "absent")

            def copy_case(name: str) -> Path:
                destination = root / name
                destination.mkdir()
                for path in source.iterdir():
                    (destination / path.name).write_bytes(path.read_bytes())
                return destination

            dropped = copy_case("dropped")
            lines = (dropped / "trades.jsonl").read_text(encoding="utf-8").splitlines()
            (dropped / "trades.jsonl").write_text(lines[1] + "\n", encoding="utf-8")
            _rewrite_checksums(dropped)
            with self.assertRaisesRegex(ValueError, "missing trade record"):
                load_phase7_trade_retention(dropped)

            duplicated = copy_case("duplicated")
            text = (duplicated / "trades.jsonl").read_text(encoding="utf-8")
            (duplicated / "trades.jsonl").write_text(text + text.splitlines()[0] + "\n", encoding="utf-8")
            _rewrite_checksums(duplicated)
            with self.assertRaisesRegex(ValueError, "duplicate trade record"):
                load_phase7_trade_retention(duplicated)

            malformed = copy_case("malformed")
            (malformed / "trades.jsonl").write_bytes(b"{not-json\n")
            _rewrite_checksums(malformed)
            with self.assertRaisesRegex(ValueError, "malformed retention file: trades.jsonl"):
                load_phase7_trade_retention(malformed)

            inconsistent = copy_case("inconsistent")
            rows = [
                json.loads(line)
                for line in (inconsistent / "trades.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            rows[0]["record"]["net_pnl_usd"] = float(rows[0]["record"]["net_pnl_usd"]) + 1.0
            (inconsistent / "trades.jsonl").write_text(
                "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows),
                encoding="utf-8",
            )
            _rewrite_checksums(inconsistent)
            with self.assertRaisesRegex(ValueError, "net PnL does not match the prices"):
                load_phase7_trade_retention(inconsistent)

            negative = copy_case("negative-gross-loss")
            index = json.loads((negative / "window-index.json").read_text(encoding="utf-8"))
            index["windows"][0]["gross_loss_usd"] = -abs(float(index["windows"][0]["gross_loss_usd"]))
            (negative / "window-index.json").write_text(
                json.dumps(index, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
            _rewrite_checksums(negative)
            with self.assertRaisesRegex(
                ValueError,
                "gross loss must be the positive Phase 3 magnitude",
            ):
                load_phase7_trade_retention(negative)

            claimed = copy_case("claims-zip")
            manifest = json.loads((claimed / "manifest.json").read_text(encoding="utf-8"))
            manifest["claims_trades_from_stage2_zip"] = True
            (claimed / "manifest.json").write_text(json.dumps(manifest) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Stage 2 ZIP has no trade ledger"):
                load_phase7_trade_retention(claimed)

            winner, loser = retained.trades
            with self.assertRaisesRegex(ValueError, "duplicate trade record"):
                write_phase7_trade_retention(
                    retention_dir=root / "writer-duplicate",
                    windows=(
                        replace(
                            retained,
                            trades=(
                                winner,
                                replace(loser, trade_id=winner.trade_id, decision_id=winner.decision_id),
                            ),
                        ),
                    ),
                    code_commit=CODE,
                )
            with self.assertRaisesRegex(ValueError, "trade records are not chronological"):
                write_phase7_trade_retention(
                    retention_dir=root / "writer-order",
                    windows=(
                        replace(
                            retained,
                            trades=(
                                replace(winner, exit_timestamp_utc=loser.exit_timestamp_utc),
                                replace(loser, exit_timestamp_utc=winner.exit_timestamp_utc),
                            ),
                        ),
                    ),
                    code_commit=CODE,
                )
            with self.assertRaisesRegex(ValueError, "gross loss must be the positive Phase 3 magnitude"):
                write_phase7_trade_retention(
                    retention_dir=root / "writer-negative",
                    windows=(
                        replace(
                            retained,
                            financial=replace(retained.financial, gross_loss_usd=-10.0),
                        ),
                    ),
                    code_commit=CODE,
                )
            with self.assertRaisesRegex(ValueError, "code commit does not match the engine"):
                write_phase7_trade_retention(
                    retention_dir=root / "writer-commit",
                    windows=(retained,),
                    code_commit="different-commit",
                )

    def test_retention_directory_must_stay_separate(self) -> None:
        from fmp.walkforward.retention import write_phase7_trade_retention

        retained = _retain(_loaded(), 0.2)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            aggregate = root / "aggregates"
            aggregate.mkdir()
            (aggregate / "result.json").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must be separate from the Phase 7 aggregate directory"):
                write_phase7_trade_retention(
                    retention_dir=aggregate,
                    windows=(retained,),
                    code_commit=CODE,
                    aggregate_dir=aggregate,
                )
            with self.assertRaisesRegex(ValueError, "must be separate from the Phase 7 aggregate directory"):
                write_phase7_trade_retention(
                    retention_dir=aggregate / "nested",
                    windows=(retained,),
                    code_commit=CODE,
                    aggregate_dir=aggregate,
                )
            with self.assertRaisesRegex(ValueError, "must be separate from the Phase 7 aggregate directory"):
                write_phase7_trade_retention(
                    retention_dir=root,
                    windows=(retained,),
                    code_commit=CODE,
                    aggregate_dir=aggregate,
                )
            self.assertEqual(list(aggregate.iterdir()), [aggregate / "result.json"])
            self.assertFalse((root / ORIGINAL_ARTIFACT).exists())

    def test_source_citation_does_not_mark_the_stage2_series_recovered(self) -> None:
        from fmp.walkforward.retention import (
            ORIGINAL_STAGE2_CODE,
            ORIGINAL_STAGE2_RUN_ID,
            load_phase7_trade_retention,
            write_phase7_trade_retention,
        )

        retained = _retain(_loaded(), 0.2)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "trades"
            write_phase7_trade_retention(
                retention_dir=root,
                windows=(retained,),
                code_commit=CODE,
                provenance_role="separately_authorized_submission",
                provenance_label="separately-authorized-reproduction-review",
                source_run_id=ORIGINAL_STAGE2_RUN_ID,
                source_artifact_id=ORIGINAL_ARTIFACT,
                source_commit=ORIGINAL_STAGE2_CODE,
            )
            loaded_retention = load_phase7_trade_retention(root)
        self.assertFalse(loaded_retention.authentic_stage2_series_recovered)
        self.assertFalse(loaded_retention.manifest["reproduction_authorized"])
        self.assertFalse(loaded_retention.manifest["owner_authorization_recorded"])
        submission = loaded_retention.submissions[0]
        self.assertEqual(submission.provenance.role, "separately_authorized_submission")
        self.assertEqual(submission.provenance.source_run_id, ORIGINAL_STAGE2_RUN_ID)
        validation = validate_trade_submission(submission)
        self.assertTrue(validation.accepted, validation.findings)
        self.assertFalse(validation.original_phase7_trade_ledger_verified)

        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "cannot carry a historical source identity"):
                write_phase7_trade_retention(
                    retention_dir=Path(tmp) / "synthetic",
                    windows=(retained,),
                    code_commit=CODE,
                    source_run_id=ORIGINAL_STAGE2_RUN_ID,
                )
