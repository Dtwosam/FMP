from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fmp.contracts import BacktestRun, Direction, ExitReason, QuoteBar, TradeRecord
from fmp.shadow.cli import build_parser, main
from fmp.shadow.reference import build_spread_reference, write_spread_reference
from fmp.walkforward.contracts import STAGE2_WINDOWS
from fmp.walkforward.data import LoadedPhase7Bars


UTC = timezone.utc
CODE_COMMIT = "c" * 40


def bar(when: datetime, *, bid: float, spread_pips: float) -> QuoteBar:
    ask = bid + spread_pips * 0.01
    return QuoteBar(
        timestamp_utc=when,
        symbol="USDJPY",
        bid_open=bid,
        bid_high=bid,
        bid_low=bid,
        bid_close=bid,
        ask_open=ask,
        ask_high=ask,
        ask_low=ask,
        ask_close=ask,
    )


def loaded_for(index: int) -> LoadedPhase7Bars:
    window = STAGE2_WINDOWS[index]
    entry = datetime(window.start.year, window.start.month, window.start.day, 8, 15, tzinfo=UTC)
    exit_at = entry + timedelta(minutes=45)
    bars = (
        bar(entry, bid=140.00 + index, spread_pips=float(index + 1)),
        bar(entry + timedelta(minutes=15), bid=140.10 + index, spread_pips=9.0),
        bar(exit_at, bid=140.20 + index, spread_pips=float(index) + 1.5),
    )
    scored_start = datetime(window.start.year, window.start.month, window.start.day, tzinfo=UTC)
    return LoadedPhase7Bars(
        bars=bars,
        scored_bars=bars,
        eligible_scored_dates=(entry.date(),),
        opened_partition_keys=(f"15m:{window.start.year:04d}-{window.start.month:02d}",),
        warmup_range=(scored_start - timedelta(days=7), scored_start),
    )


def run_for(index: int) -> BacktestRun:
    loaded = loaded_for(index)
    entry_bar = loaded.scored_bars[0]
    exit_bar = loaded.scored_bars[-1]
    trade = TradeRecord(
        trade_id=f"trade-{index}",
        decision_id=f"decision-{index}",
        symbol="USDJPY",
        direction=Direction.LONG,
        units=1000,
        entry_timestamp_utc=entry_bar.timestamp_utc,
        exit_timestamp_utc=exit_bar.timestamp_utc + timedelta(minutes=5),
        entry_reference_price=entry_bar.ask_open,
        exit_reference_price=exit_bar.bid_open,
        entry_price=entry_bar.ask_open,
        exit_price=exit_bar.bid_open,
        stop_price=entry_bar.bid_open - 0.50,
        target_price=entry_bar.ask_open + 0.50,
        exit_reason=ExitReason.TIME_EXIT,
        intrabar_ambiguous=False,
        gross_pnl_usd=1.0,
        slippage_cost_usd=0.0,
        commission_cost_usd=0.0,
        financing_cost_usd=0.0,
        net_pnl_usd=1.0,
        risk_equity_before_usd=100_000.0,
        risk_equity_after_usd=100_001.0,
    )
    return BacktestRun(
        run_identity={"window": STAGE2_WINDOWS[index].name},
        trades=(trade,),
        rejections=(),
        equity_checkpoints=(),
        metrics={},
    )


class Phase8SpreadReferenceTests(unittest.TestCase):
    def test_builder_uses_exact_stage2_windows_and_bar_level_trade_spreads(self) -> None:
        loaded_calls: list[dict[str, object]] = []
        run_calls: list[dict[str, object]] = []

        def loader(**kwargs):  # type: ignore[no-untyped-def]
            loaded_calls.append(kwargs)
            index = [item.name for item in STAGE2_WINDOWS].index(kwargs["window_name"])
            return loaded_for(index)

        def runner(**kwargs):  # type: ignore[no-untyped-def]
            run_calls.append(kwargs)
            index = [item.name for item in STAGE2_WINDOWS].index(kwargs["window_name"])
            return run_for(index)

        reference = build_spread_reference(
            dataset_root=Path("dataset"),
            manifest_path=Path("processed.json"),
            code_commit=CODE_COMMIT,
            load_window=loader,
            run_window=runner,
        )

        expected_windows = [item.name for item in STAGE2_WINDOWS]
        self.assertEqual([call["window_name"] for call in loaded_calls], expected_windows)
        self.assertEqual([call["window_name"] for call in run_calls], expected_windows)
        self.assertTrue(all(call["candidate_id"] == "session_breakout" for call in loaded_calls))
        self.assertTrue(all(call["slippage_pips"] == 0.2 for call in run_calls))
        self.assertEqual(reference["trade_count"], 7)
        self.assertAlmostEqual(reference["entry_spread_pips"]["median"], 4.0)
        self.assertAlmostEqual(reference["entry_spread_pips"]["p95"], 7.0)
        self.assertAlmostEqual(reference["exit_spread_pips"]["median"], 4.5)
        self.assertAlmostEqual(reference["exit_spread_pips"]["p95"], 7.5)
        self.assertEqual(reference["method_version"], "fmp-phase8-spread-reference-v1")
        self.assertEqual(len(reference["trades"]), 7)
        self.assertEqual(reference["trades"][0]["exit_bar_timestamp_utc"], "2025-01-01T09:00:00Z")

    def test_reference_binds_exact_accepted_phase7_and_phase2_identity(self) -> None:
        def loader(**kwargs):  # type: ignore[no-untyped-def]
            index = [item.name for item in STAGE2_WINDOWS].index(kwargs["window_name"])
            return loaded_for(index)

        def runner(**kwargs):  # type: ignore[no-untyped-def]
            index = [item.name for item in STAGE2_WINDOWS].index(kwargs["window_name"])
            return run_for(index)

        reference = build_spread_reference(
            dataset_root=Path("dataset"),
            manifest_path=Path("processed.json"),
            code_commit=CODE_COMMIT,
            load_window=loader,
            run_window=runner,
        )
        self.assertEqual(reference["phase7_checkpoint_sha"], "b6fb0176555b071fef6d1070edf3407b03cd60c9")
        self.assertEqual(reference["phase7_experiment"], "EXP-20260915-008")
        self.assertEqual(reference["phase7_outcome"], "PASS / PROMOTE")
        self.assertEqual(reference["phase7_stage2_run_id"], 35015277625)
        self.assertEqual(reference["phase2_artifact_id"], 10327600628)
        self.assertEqual(reference["phase2_zip_sha256"], "6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72")
        self.assertEqual(reference["processed_manifest_sha256"], "e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d")
        self.assertEqual(reference["code_commit"], CODE_COMMIT)
        self.assertEqual(
            reference["strategy"],
            {
                "id": "session_breakout",
                "symbol": "USDJPY",
                "timeframe": "15m",
                "buffer_pips": 5,
                "target_range_multiple": 1.5,
            },
        )
        self.assertEqual(reference["historical_slippage_pips"], 0.2)

    def test_writer_is_deterministic_and_companion_sha_binds_reference_bytes(self) -> None:
        def loader(**kwargs):  # type: ignore[no-untyped-def]
            index = [item.name for item in STAGE2_WINDOWS].index(kwargs["window_name"])
            return loaded_for(index)

        def runner(**kwargs):  # type: ignore[no-untyped-def]
            index = [item.name for item in STAGE2_WINDOWS].index(kwargs["window_name"])
            return run_for(index)

        reference = build_spread_reference(
            dataset_root=Path("dataset"),
            manifest_path=Path("processed.json"),
            code_commit=CODE_COMMIT,
            load_window=loader,
            run_window=runner,
        )
        with TemporaryDirectory() as left_tmp, TemporaryDirectory() as right_tmp:
            left = Path(left_tmp)
            right = Path(right_tmp)
            left_digest = write_spread_reference(left, reference)
            right_digest = write_spread_reference(right, reference)
            self.assertEqual(left_digest, right_digest)
            self.assertEqual((left / "reference.json").read_bytes(), (right / "reference.json").read_bytes())
            self.assertEqual((left / "reference.sha256").read_bytes(), (right / "reference.sha256").read_bytes())
            self.assertEqual(
                left_digest,
                hashlib.sha256((left / "reference.json").read_bytes()).hexdigest(),
            )
            self.assertEqual((left / "reference.sha256").read_text(encoding="utf-8"), left_digest + "\n")

    def test_missing_trade_bar_fails_closed_instead_of_inferring_spread(self) -> None:
        def loader(**kwargs):  # type: ignore[no-untyped-def]
            index = [item.name for item in STAGE2_WINDOWS].index(kwargs["window_name"])
            loaded = loaded_for(index)
            if index == 0:
                return LoadedPhase7Bars(
                    bars=loaded.bars[:-1],
                    scored_bars=loaded.scored_bars[:-1],
                    eligible_scored_dates=loaded.eligible_scored_dates,
                    opened_partition_keys=loaded.opened_partition_keys,
                    warmup_range=loaded.warmup_range,
                )
            return loaded

        def runner(**kwargs):  # type: ignore[no-untyped-def]
            index = [item.name for item in STAGE2_WINDOWS].index(kwargs["window_name"])
            return run_for(index)

        with self.assertRaisesRegex(ValueError, "exit bar"):
            build_spread_reference(
                dataset_root=Path("dataset"),
                manifest_path=Path("processed.json"),
                code_commit=CODE_COMMIT,
                load_window=loader,
                run_window=runner,
            )

    def test_reference_source_reuses_phase7_loader_strategy_adapter_and_backtest(self) -> None:
        source = Path("src/fmp/shadow/reference.py").read_text(encoding="utf-8")
        for required in (
            "load_phase7_bars",
            "generate_session_breakout_candidates",
            "candidate_to_decision",
            "run_backtest",
            "pip_size",
            "STAGE2_WINDOWS",
        ):
            self.assertIn(required, source)
        self.assertNotIn("aggregate_profit_factor", source)
        self.assertNotIn("stage2 aggregate", source.lower())

    def test_build_reference_cli_is_source_free_and_has_no_strategy_or_window_override(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "build-reference",
                "--dataset-root",
                "dataset",
                "--processed-manifest",
                "processed.json",
                "--out",
                "reference-out",
            ]
        )
        self.assertEqual(args.command, "build-reference")
        for forbidden in ("candidate", "window", "slippage_pips", "symbol", "timeframe"):
            self.assertFalse(hasattr(args, forbidden))

        calls: list[dict[str, object]] = []
        rc = main(
            [
                "build-reference",
                "--dataset-root",
                "dataset",
                "--processed-manifest",
                "processed.json",
                "--out",
                "reference-out",
            ],
            environ={},
            reference_command=lambda **kwargs: calls.append(kwargs) or "d" * 64,
            code_commit_resolver=lambda: CODE_COMMIT,
        )
        self.assertEqual(rc, 0)
        self.assertEqual(calls[0]["dataset_root"], Path("dataset"))
        self.assertEqual(calls[0]["manifest_path"], Path("processed.json"))
        self.assertEqual(calls[0]["out_dir"], Path("reference-out"))
        self.assertEqual(calls[0]["code_commit"], CODE_COMMIT)


if __name__ == "__main__":
    unittest.main()
