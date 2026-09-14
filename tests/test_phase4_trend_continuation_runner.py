from __future__ import annotations

import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from fmp.contracts import Direction, QuoteBar
from fmp.research.data import LoadedResearchBars
from fmp.research.trend_continuation import (
    SLIPPAGE_SCENARIOS,
    TREND_CONTINUATION_GRID,
    run_trend_continuation_grid,
)
from fmp.strategies.contracts import SignalCandidate

BASE = datetime(2020, 1, 2, 11, 0, tzinfo=timezone.utc)


def bars() -> tuple[QuoteBar, ...]:
    return tuple(
        QuoteBar(
            timestamp_utc=BASE + timedelta(hours=i), symbol="EURUSD",
            bid_open=1.1000, bid_high=1.1005, bid_low=1.0995, bid_close=1.1002,
            ask_open=1.1002, ask_high=1.1007, ask_low=1.0997, ask_close=1.1004,
        )
        for i in range(3)
    )


def no_trade(config) -> tuple[SignalCandidate, ...]:
    return (
        SignalCandidate(
            candidate_id=f"NT-{config.timeframe}-{config.trend_window_id}-{config.target_r_multiple}",
            symbol="EURUSD",
            observation_bar_timestamp_utc=BASE,
            signal_known_timestamp_utc=BASE + timedelta(hours=1),
            direction=Direction.NO_TRADE,
            stop_price=None,
            target_price=None,
            latest_exit_timestamp_utc=None,
            reason_code="NO_CONTINUATION",
            metadata={"session_date": "2020-01-02"},
        ),
    )


class Phase4TrendContinuationRunnerTests(unittest.TestCase):
    def test_runner_reuses_candidates_and_preserves_all_18_rows(self) -> None:
        loaded = LoadedResearchBars(
            bars=bars(), excluded_incomplete_count=4, eligible_utc_dates=(date(2020, 1, 2),)
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "manifest.json"
            manifest.write_text('{"fixture":true}\n', encoding="utf-8")
            generated: list[tuple[str, float, str]] = []

            def fake_generate(_bars, *, config):
                generated.append((config.trend_window_id, config.target_r_multiple, config.timeframe))
                return no_trade(config)

            with patch("fmp.research.trend_continuation.load_processed_bars", return_value=loaded) as load_mock, patch(
                "fmp.research.trend_continuation.generate_trend_continuation_candidates",
                side_effect=fake_generate,
            ) as generate_mock:
                result = run_trend_continuation_grid(
                    dataset_root=root, manifest_path=manifest, symbol="EURUSD", timeframe="1h",
                    split_name="development", code_commit="trend-test-commit",
                )

        self.assertEqual(load_mock.call_count, 1)
        self.assertEqual(generate_mock.call_count, 6)
        self.assertEqual(generated, [(window, target, "1h") for window, target in TREND_CONTINUATION_GRID])
        rows = result["configuration_rows"]
        self.assertEqual(len(rows), 18)
        self.assertEqual(
            [(row["trend_window_id"], row["target_r_multiple"], row["slippage_pips"]) for row in rows],
            [(window, target, slip) for window, target in TREND_CONTINUATION_GRID for slip in SLIPPAGE_SCENARIOS],
        )
        self.assertEqual(result["excluded_incomplete_bar_count"], 4)
        self.assertEqual(result["code_commit"], "trend-test-commit")
        digests: dict[tuple[str, float], set[str]] = {}
        for row in rows:
            key = (row["trend_window_id"], row["target_r_multiple"])
            digests.setdefault(key, set()).add(row["candidate_sha256"])
            self.assertEqual(row["requested_risk_fraction"], 0.0025)
            self.assertEqual(row["run_identity"]["commission_model"], {"model": "zero_commission"})
            self.assertEqual(row["run_identity"]["financing_model"], {"model": "zero_financing"})
        self.assertTrue(all(len(values) == 1 for values in digests.values()))

    def test_final_split_fails_before_loader_is_called(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, patch(
            "fmp.research.trend_continuation.load_processed_bars"
        ) as load_mock:
            root = Path(tmp)
            manifest = root / "manifest.json"
            manifest.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "final test"):
                run_trend_continuation_grid(
                    dataset_root=root, manifest_path=manifest, symbol="EURUSD", timeframe="1h",
                    split_name="final", code_commit="trend-test-commit",
                )
            load_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
