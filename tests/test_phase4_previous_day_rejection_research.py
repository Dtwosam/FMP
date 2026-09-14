from __future__ import annotations

import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from fmp.contracts import Direction, QuoteBar
from fmp.research.data import LoadedResearchBars
from fmp.research.previous_day_rejection import (
    PREVIOUS_DAY_REJECTION_GRID,
    SLIPPAGE_SCENARIOS,
    run_previous_day_rejection_grid,
)
from fmp.strategies.contracts import SignalCandidate


BASE = datetime(2020, 1, 2, 11, 0, tzinfo=timezone.utc)


def bars() -> tuple[QuoteBar, ...]:
    return tuple(
        QuoteBar(
            timestamp_utc=BASE + timedelta(hours=i),
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
        for i in range(3)
    )


def no_trade(config) -> tuple[SignalCandidate, ...]:
    return (
        SignalCandidate(
            candidate_id=f"PDR-NT-{config.timeframe}-{config.buffer_pips}",
            symbol="EURUSD",
            observation_bar_timestamp_utc=BASE,
            signal_known_timestamp_utc=BASE + timedelta(hours=1),
            direction=Direction.NO_TRADE,
            stop_price=None,
            target_price=None,
            latest_exit_timestamp_utc=None,
            reason_code="NO_REJECTION",
            metadata={"session_date": "2020-01-02"},
        ),
    )


class Phase4PreviousDayRejectionResearchTests(unittest.TestCase):
    def test_grid_and_slippage_are_exactly_frozen(self) -> None:
        self.assertEqual(PREVIOUS_DAY_REJECTION_GRID, (0, 2, 5))
        self.assertEqual(SLIPPAGE_SCENARIOS, (0.2, 0.5, 1.0))

    def test_runner_reuses_candidates_and_preserves_all_9_rows(self) -> None:
        loaded = LoadedResearchBars(
            bars=bars(),
            excluded_incomplete_count=4,
            eligible_utc_dates=(date(2020, 1, 2),),
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "manifest.json"
            manifest.write_text('{"fixture":true}\n', encoding="utf-8")
            generated: list[tuple[int, str]] = []

            def fake_generate(_bars, *, config):
                generated.append((config.buffer_pips, config.timeframe))
                return no_trade(config)

            with patch(
                "fmp.research.previous_day_rejection.load_processed_bars",
                return_value=loaded,
            ) as load_mock, patch(
                "fmp.research.previous_day_rejection.generate_previous_day_rejection_candidates",
                side_effect=fake_generate,
            ) as generate_mock:
                result = run_previous_day_rejection_grid(
                    dataset_root=root,
                    manifest_path=manifest,
                    symbol="EURUSD",
                    timeframe="1h",
                    split_name="development",
                    code_commit="previous-day-test-commit",
                )

        self.assertEqual(load_mock.call_count, 1)
        self.assertEqual(generate_mock.call_count, 3)
        self.assertEqual(generated, [(buffer_pips, "1h") for buffer_pips in PREVIOUS_DAY_REJECTION_GRID])
        rows = result["configuration_rows"]
        self.assertEqual(len(rows), 9)
        self.assertEqual(
            [(row["buffer_pips"], row["slippage_pips"]) for row in rows],
            [(buffer_pips, slip) for buffer_pips in PREVIOUS_DAY_REJECTION_GRID for slip in SLIPPAGE_SCENARIOS],
        )
        self.assertEqual(result["protocol"], "fmp-phase4-previous-day-rejection-grid-v1")
        self.assertEqual(result["excluded_incomplete_bar_count"], 4)
        self.assertEqual(result["code_commit"], "previous-day-test-commit")
        digests: dict[int, set[str]] = {}
        for row in rows:
            digests.setdefault(row["buffer_pips"], set()).add(row["candidate_sha256"])
            self.assertEqual(row["requested_risk_fraction"], 0.0025)
            self.assertEqual(row["run_identity"]["commission_model"], {"model": "zero_commission"})
            self.assertEqual(row["run_identity"]["financing_model"], {"model": "zero_financing"})
        self.assertTrue(all(len(values) == 1 for values in digests.values()))

    def test_final_split_fails_before_loader_is_called(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, patch(
            "fmp.research.previous_day_rejection.load_processed_bars"
        ) as load_mock:
            root = Path(tmp)
            manifest = root / "manifest.json"
            manifest.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "final test"):
                run_previous_day_rejection_grid(
                    dataset_root=root,
                    manifest_path=manifest,
                    symbol="EURUSD",
                    timeframe="1h",
                    split_name="final",
                    code_commit="previous-day-test-commit",
                )
            load_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
