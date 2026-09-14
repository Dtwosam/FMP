from __future__ import annotations

import hashlib
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from fmp.contracts import Direction, QuoteBar
from fmp.research.data import LoadedResearchBars
from fmp.research.session_sweep_rejection import (
    REQUESTED_RISK_FRACTION,
    SESSION_SWEEP_REJECTION_GRID,
    SLIPPAGE_SCENARIOS,
    STARTING_EQUITY_USD,
    run_session_sweep_rejection_grid,
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
            candidate_id=f"SSR-NT-{config.timeframe}-{config.buffer_pips}",
            symbol="EURUSD",
            observation_bar_timestamp_utc=BASE,
            signal_known_timestamp_utc=BASE + timedelta(hours=1),
            direction=Direction.NO_TRADE,
            stop_price=None,
            target_price=None,
            latest_exit_timestamp_utc=None,
            reason_code="NO_SESSION_SWEEP_REJECTION",
            metadata={"session_date": "2020-01-02"},
        ),
    )


class Phase4SessionSweepRejectionResearchTests(unittest.TestCase):
    def test_grid_cost_equity_and_risk_are_exactly_frozen(self) -> None:
        self.assertEqual(SESSION_SWEEP_REJECTION_GRID, (0, 2, 5))
        self.assertEqual(SLIPPAGE_SCENARIOS, (0.2, 0.5, 1.0))
        self.assertEqual(STARTING_EQUITY_USD, 100_000.0)
        self.assertEqual(REQUESTED_RISK_FRACTION, 0.0025)

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
            manifest_sha = hashlib.sha256(manifest.read_bytes()).hexdigest()
            generated: list[tuple[int, str]] = []

            def fake_generate(_bars, *, config):
                generated.append((config.buffer_pips, config.timeframe))
                return no_trade(config)

            with patch(
                "fmp.research.session_sweep_rejection.load_processed_bars",
                return_value=loaded,
            ) as load_mock, patch(
                "fmp.research.session_sweep_rejection.generate_session_sweep_rejection_candidates",
                side_effect=fake_generate,
            ) as generate_mock:
                result = run_session_sweep_rejection_grid(
                    dataset_root=root,
                    manifest_path=manifest,
                    symbol="EURUSD",
                    timeframe="1h",
                    split_name="development",
                    code_commit="session-sweep-test-commit",
                )

        self.assertEqual(load_mock.call_count, 1)
        self.assertEqual(generate_mock.call_count, 3)
        self.assertEqual(
            generated,
            [(buffer_pips, "1h") for buffer_pips in SESSION_SWEEP_REJECTION_GRID],
        )
        self.assertEqual(result["protocol"], "fmp-phase4-session-sweep-rejection-grid-v1")
        self.assertEqual(result["family_id"], "session_sweep_rejection")
        self.assertEqual(result["code_commit"], "session-sweep-test-commit")
        self.assertEqual(result["processed_manifest_sha256"], manifest_sha)
        self.assertEqual(result["excluded_incomplete_bar_count"], 4)
        rows = result["configuration_rows"]
        self.assertEqual(len(rows), 9)
        self.assertEqual(
            [(row["buffer_pips"], row["slippage_pips"]) for row in rows],
            [
                (buffer_pips, slippage)
                for buffer_pips in SESSION_SWEEP_REJECTION_GRID
                for slippage in SLIPPAGE_SCENARIOS
            ],
        )

        digests: dict[int, set[str]] = {}
        counts: dict[int, set[int]] = {}
        reasons: dict[int, set[tuple[tuple[str, int], ...]]] = {}
        for row in rows:
            buffer_pips = row["buffer_pips"]
            digests.setdefault(buffer_pips, set()).add(row["candidate_sha256"])
            counts.setdefault(buffer_pips, set()).add(row["candidate_count"])
            reasons.setdefault(buffer_pips, set()).add(
                tuple(sorted(row["candidate_reason_counts"].items()))
            )
            self.assertEqual(row["requested_risk_fraction"], 0.0025)
            identity = row["run_identity"]
            self.assertEqual(identity["code_commit"], "session-sweep-test-commit")
            self.assertEqual(identity["processed_data_manifest_id"], manifest_sha)
            self.assertEqual(identity["timeframe"], "1h")
            self.assertEqual(identity["commission_model"], {"model": "zero_commission"})
            self.assertEqual(identity["financing_model"], {"model": "zero_financing"})
            self.assertEqual(identity["decision_config"]["family_id"], "session_sweep_rejection")
            self.assertEqual(identity["decision_config"]["buffer_pips"], buffer_pips)
            self.assertEqual(identity["decision_config"]["candidate_sha256"], row["candidate_sha256"])
        self.assertTrue(all(len(values) == 1 for values in digests.values()))
        self.assertTrue(all(len(values) == 1 for values in counts.values()))
        self.assertTrue(all(len(values) == 1 for values in reasons.values()))

    def test_final_split_fails_before_manifest_or_loader_access(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, patch(
            "fmp.research.session_sweep_rejection.load_processed_bars"
        ) as load_mock:
            root = Path(tmp)
            missing_manifest = root / "does-not-exist.json"
            with self.assertRaisesRegex(ValueError, "final test"):
                run_session_sweep_rejection_grid(
                    dataset_root=root,
                    manifest_path=missing_manifest,
                    symbol="EURUSD",
                    timeframe="1h",
                    split_name="final",
                    code_commit="session-sweep-test-commit",
                )
            load_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
