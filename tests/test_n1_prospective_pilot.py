from __future__ import annotations

import ast
import subprocess
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

from fmp.contracts import ExitReason, QuoteBar, RejectionCode
from fmp.research.n1_news_shock import ReleaseKind, ReleaseStatus
from fmp.research.n1_prospective_pilot import (
    AUTHORIZATION_COMMIT,
    AUTHORIZATION_EFFECTIVE_UTC,
    EVIDENCE_CLASS,
    FROZEN_SIGNAL_COMMIT,
    PilotWindowClosed,
    assert_frozen_signal_blob,
    record_labeled_slippage_runs,
    record_pilot,
    record_pilot_observation,
)
from tests.test_n1_news_shock import _release, _session, _utc

EMPSIT_DAY = date(2026, 12, 4)
CPI_DAY = date(2026, 12, 10)
REPO_ROOT = Path(__file__).resolve().parents[1]


def _empsit(**kwargs):
    return _release(
        EMPSIT_DAY,
        release_id="bls-empsit-2026-12-04",
        kind=ReleaseKind.EMPLOYMENT_SITUATION,
        **kwargs,
    )


def _cpi(**kwargs):
    return _release(
        CPI_DAY,
        release_id="bls-cpi-2026-12-10",
        kind=ReleaseKind.CPI,
        **kwargs,
    )


class N1ProspectivePilotTests(unittest.TestCase):
    def test_effective_timestamp_is_the_decision_commit(self) -> None:
        shown = subprocess.check_output(
            ["git", "show", "-s", "--format=%cI", AUTHORIZATION_COMMIT],
            cwd=REPO_ROOT,
            text=True,
        ).strip()
        self.assertEqual(shown, AUTHORIZATION_EFFECTIVE_UTC)
        self.assertEqual(FROZEN_SIGNAL_COMMIT, "78185a1aded7f5d97c296c16fdfd615f46934353")
        assert_frozen_signal_blob(REPO_ROOT)

    def test_module_does_not_fetch_market_data(self) -> None:
        source = (REPO_ROOT / "src/fmp/research/n1_prospective_pilot.py").read_text()
        tree = ast.parse(source)
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".", 1)[0])
        self.assertTrue(imported.isdisjoint({"urllib", "requests", "http", "socket", "ftplib"}))
        self.assertNotIn("def fetch_", source)

    def test_complete_window_keeps_time_exit_and_hypothetical_cost(self) -> None:
        bars = _session(CPI_DAY, direction="strength", stop_bar_extreme=1.10150)
        record = record_pilot_observation(_cpi(), bars, slippage_pips=0.5)
        self.assertEqual(record.raw_exit_reason, ExitReason.TIME_EXIT.value)
        self.assertEqual(record.quality, "COMPLETE")
        self.assertTrue(record.ordinary_n1_time_exit)
        self.assertEqual(record.missing_labels, ())
        self.assertEqual(record.raw_commission_usd, 7.0)
        self.assertEqual(record.evidence_class, EVIDENCE_CLASS)
        self.assertTrue(record.qualifying_publication)
        self.assertTrue(record.engine_ran)
        self.assertFalse(record.quality_replaces_raw_result)

    def test_missing_bars_after_a_stop_do_not_erase_the_stop(self) -> None:
        bars = _session(
            EMPSIT_DAY,
            direction="strength",
            stop_bar_extreme=1.10150,
            gap_at=(8, 40, 1.10300, 1.10320),
        )
        cutoff = _utc(EMPSIT_DAY, 8, 40)
        truncated = [bar for bar in bars if bar.timestamp_utc <= cutoff]
        record = record_pilot_observation(_empsit(), truncated, slippage_pips=0.5)
        self.assertEqual(record.raw_exit_reason, ExitReason.STOP.value)
        self.assertEqual(record.raw_stop_price, 1.10150)
        self.assertIsNone(record.raw_rejection_code)
        self.assertEqual(record.quality, "INCOMPLETE")
        self.assertFalse(record.ordinary_n1_time_exit)
        self.assertIn("EURUSD 09:30 America/New_York", record.missing_labels)
        self.assertFalse(record.quality_replaces_raw_result)

    def test_unpublished_release_is_kept_without_a_download(self) -> None:
        release = _empsit(status=ReleaseStatus.NOT_PUBLISHED, actual=None)
        record = record_pilot_observation(release, (), slippage_pips=0.5)
        self.assertFalse(record.engine_ran)
        self.assertFalse(record.qualifying_publication)
        self.assertEqual(record.direction, "NO_TRADE")
        self.assertEqual(record.reason_code, "RELEASE_NOT_PUBLISHED")
        self.assertIsNone(record.raw_exit_reason)
        self.assertIsNone(record.raw_rejection_code)
        self.assertEqual(record.quality, "INCOMPLETE")

    def test_mistimed_publication_stays_a_rejection_and_does_not_count(self) -> None:
        release = _empsit(actual=_utc(EMPSIT_DAY, 8, 31))
        bars = _session(EMPSIT_DAY, direction="strength", stop_bar_extreme=1.10150)
        record = record_pilot_observation(release, bars, slippage_pips=0.2)
        self.assertEqual(record.raw_rejection_code, RejectionCode.NO_TRADE.value)
        self.assertIsNone(record.raw_exit_reason)
        self.assertFalse(record.qualifying_publication)
        self.assertEqual(record.quality, "COMPLETE")
        self.assertFalse(record.ordinary_n1_time_exit)

    def test_january_backfill_and_a_third_date_are_refused(self) -> None:
        winter = date(2026, 1, 13)
        bars = _session(winter, direction="strength", stop_bar_extreme=1.10150)
        with self.assertRaises(PilotWindowClosed):
            record_pilot_observation(_release(winter), bars, slippage_pips=0.5)
        later = _release(
            date(2027, 1, 8),
            release_id="bls-empsit-2027-01-08",
            kind=ReleaseKind.EMPLOYMENT_SITUATION,
        )
        with self.assertRaises(PilotWindowClosed):
            record_pilot_observation(
                later,
                _session(date(2027, 1, 8), direction="strength", stop_bar_extreme=1.10150),
                slippage_pips=0.5,
            )

    def test_bar_at_the_authorization_instant_is_refused(self) -> None:
        stamp = datetime.fromisoformat(AUTHORIZATION_EFFECTIVE_UTC).astimezone(timezone.utc)
        bar = QuoteBar(
            timestamp_utc=stamp,
            symbol="EURUSD",
            bid_open=1.1,
            bid_high=1.1,
            bid_low=1.1,
            bid_close=1.1,
            ask_open=1.1002,
            ask_high=1.1002,
            ask_low=1.1002,
            ask_close=1.1002,
        )
        with self.assertRaises(ValueError):
            record_pilot_observation(_empsit(), (bar,), slippage_pips=0.5)

    def test_labeled_slippage_runs_stay_separate(self) -> None:
        bars = _session(CPI_DAY, direction="strength", stop_bar_extreme=1.10150)
        records = record_labeled_slippage_runs(_cpi(), bars)
        self.assertEqual([record.slippage_pips for record in records], [0.5, 0.2, 1.0])
        self.assertEqual(records[0].raw_stop_price, records[2].raw_stop_price)
        self.assertNotEqual(records[0].raw_entry_price, records[2].raw_entry_price)
        self.assertEqual({record.release_id for record in records}, {"bls-cpi-2026-12-10"})

    def test_two_windows_are_kept_and_a_duplicate_is_refused(self) -> None:
        first = (
            _empsit(status=ReleaseStatus.DELAYED, actual=None),
            (),
            0.5,
        )
        second_bars = _session(CPI_DAY, direction="weakness", stop_bar_extreme=1.09800)
        second = (_cpi(), second_bars, 1.0)
        records = record_pilot((first, second))
        self.assertEqual(len(records), 2)
        self.assertFalse(records[0].qualifying_publication)
        self.assertTrue(records[1].qualifying_publication)
        self.assertEqual(records[1].raw_exit_reason, ExitReason.TIME_EXIT.value)
        with self.assertRaises(ValueError):
            record_pilot((second, second))

    def test_unlabeled_slippage_is_refused(self) -> None:
        bars = _session(CPI_DAY, direction="strength", stop_bar_extreme=1.10150)
        with self.assertRaises(ValueError):
            record_pilot_observation(_cpi(), bars, slippage_pips=0.7)


if __name__ == "__main__":
    unittest.main()
