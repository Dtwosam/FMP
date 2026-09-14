from __future__ import annotations

import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from fmp.contracts import Direction, QuoteBar
from fmp.research.data import LoadedResearchBars
from fmp.research.session_breakout import (
    SESSION_BREAKOUT_GRID,
    SLIPPAGE_SCENARIOS,
    run_session_breakout_grid,
)
from fmp.strategies.contracts import SignalCandidate


BASE = datetime(2020, 1, 2, 11, 0, tzinfo=timezone.utc)


def bars() -> tuple[QuoteBar, ...]:
    out: list[QuoteBar] = []
    for offset in range(3):
        timestamp = BASE + timedelta(hours=offset)
        out.append(
            QuoteBar(
                timestamp_utc=timestamp,
                symbol="EURUSD",
                bid_open=1.1000,
                bid_high=1.1005,
                bid_low=1.0995,
                bid_close=1.1002,
                ask_open=1.1002,
                ask_high=1.1007,
                ask_low=1.0997,
                ask_close=1.1004,
            )
        )
    return tuple(out)


def no_trade_candidate(config) -> tuple[SignalCandidate, ...]:
    return (
        SignalCandidate(
            candidate_id=(
                f"NT-{config.timeframe}-{config.buffer_pips}-"
                f"{config.target_range_multiple}"
            ),
            symbol="EURUSD",
            observation_bar_timestamp_utc=BASE,
            signal_known_timestamp_utc=BASE + timedelta(hours=1),
            direction=Direction.NO_TRADE,
            stop_price=None,
            target_price=None,
            latest_exit_timestamp_utc=None,
            reason_code="NO_BREAKOUT",
            metadata={"session_date": "2020-01-02", "session_name": "london"},
        ),
    )


class Phase4SessionBreakoutResearchTests(unittest.TestCase):
    def test_grid_and_slippage_scenarios_are_exactly_predeclared(self) -> None:
        self.assertEqual(
            SESSION_BREAKOUT_GRID,
            (
                (0, 0.5), (0, 1.0), (0, 1.5),
                (2, 0.5), (2, 1.0), (2, 1.5),
                (5, 0.5), (5, 1.0), (5, 1.5),
            ),
        )
        self.assertEqual(SLIPPAGE_SCENARIOS, (0.2, 0.5, 1.0))

    def test_runner_reuses_candidates_across_cost_scenarios_and_preserves_all_rows(self) -> None:
        loaded = LoadedResearchBars(
            bars=bars(),
            excluded_incomplete_count=7,
            eligible_utc_dates=(date(2020, 1, 2),),
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "manifest.json"
            manifest.write_text('{"fixture":true}\n', encoding="utf-8")
            generated_configs: list[tuple[int, float, str]] = []

            def fake_generate(_bars, *, config):
                generated_configs.append(
                    (config.buffer_pips, config.target_range_multiple, config.timeframe)
                )
                return no_trade_candidate(config)

            with patch(
                "fmp.research.session_breakout.load_processed_bars",
                return_value=loaded,
            ) as load_mock, patch(
                "fmp.research.session_breakout.generate_session_breakout_candidates",
                side_effect=fake_generate,
            ) as generate_mock:
                result = run_session_breakout_grid(
                    dataset_root=root,
                    manifest_path=manifest,
                    symbol="EURUSD",
                    timeframe="1h",
                    split_name="development",
                    code_commit="phase4-test-commit",
                )

        self.assertEqual(load_mock.call_count, 1)
        self.assertEqual(generate_mock.call_count, 9)
        self.assertEqual(
            generated_configs,
            [(buffer, target, "1h") for buffer, target in SESSION_BREAKOUT_GRID],
        )
        rows = result["configuration_rows"]
        self.assertEqual(len(rows), 27)
        self.assertEqual(
            [
                (row["buffer_pips"], row["target_range_multiple"], row["slippage_pips"])
                for row in rows
            ],
            [
                (buffer, target, slippage)
                for buffer, target in SESSION_BREAKOUT_GRID
                for slippage in SLIPPAGE_SCENARIOS
            ],
        )
        self.assertEqual(result["excluded_incomplete_bar_count"], 7)
        self.assertEqual(result["split_name"], "development")
        self.assertEqual(result["code_commit"], "phase4-test-commit")

        candidate_digests: dict[tuple[int, float], set[str]] = {}
        for row in rows:
            key = (row["buffer_pips"], row["target_range_multiple"])
            candidate_digests.setdefault(key, set()).add(row["candidate_sha256"])
            self.assertEqual(row["requested_risk_fraction"], 0.0025)
            identity = row["run_identity"]
            self.assertEqual(identity["code_commit"], "phase4-test-commit")
            self.assertEqual(identity["timeframe"], "1h")
            self.assertEqual(identity["commission_model"], {"model": "zero_commission"})
            self.assertEqual(identity["financing_model"], {"model": "zero_financing"})
            self.assertEqual(
                identity["risk_config"],
                {
                    "default_risk_fraction": 0.0025,
                    "max_risk_fraction": 0.005,
                    "max_simultaneous_risk_fraction": 0.01,
                    "daily_loss_halt_fraction": 0.015,
                },
            )
            self.assertEqual(row["metrics"]["no_trade_count"], 1)
        self.assertTrue(all(len(digests) == 1 for digests in candidate_digests.values()))

    def test_final_split_fails_before_data_loader_is_called(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, patch(
            "fmp.research.session_breakout.load_processed_bars"
        ) as load_mock:
            root = Path(tmp)
            manifest = root / "manifest.json"
            manifest.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "final test"):
                run_session_breakout_grid(
                    dataset_root=root,
                    manifest_path=manifest,
                    symbol="EURUSD",
                    timeframe="1h",
                    split_name="final",
                    code_commit="phase4-test-commit",
                )
            load_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
