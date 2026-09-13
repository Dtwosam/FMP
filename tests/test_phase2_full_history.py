from __future__ import annotations

import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from fmp.data.phase2.full_history import (
    DEFAULT_WORKERS,
    FULL_HISTORY_END_EXCLUSIVE,
    FULL_HISTORY_PAIRS,
    FULL_HISTORY_START,
    MAX_WORKERS,
    RecordingCompleteRawChunkReader,
    _iter_month_ranges,
    _validate_workers,
    validate_full_history_ledger,
)
from fmp.data.types import RawChunkKey


class FakeReader:
    def __init__(self, *, not_found: bool = False) -> None:
        self.not_found = not_found
        self.calls: list[RawChunkKey] = []

    def read(self, key: RawChunkKey) -> bytes | None:
        self.calls.append(key)
        if self.not_found:
            return None
        return f"{key.pair}-{key.side}-{key.day.isoformat()}".encode()


def ledger_for(pair: str, start: date, end_exclusive: date) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    day = start
    while day < end_exclusive:
        for side in ("BID", "ASK"):
            records.append(
                {
                    "pair": pair,
                    "side": side,
                    "date_utc": day.isoformat(),
                    "sha256": "a" * 64,
                    "size_bytes": 123,
                    "status": "complete",
                }
            )
        day += timedelta(days=1)
    return records


class FullHistoryPlanTests(unittest.TestCase):
    def test_frozen_scope_has_exact_days_months_pairs_and_workers(self) -> None:
        self.assertEqual(FULL_HISTORY_START, date(2015, 1, 1))
        self.assertEqual(FULL_HISTORY_END_EXCLUSIVE, date(2026, 8, 21))
        self.assertEqual((FULL_HISTORY_END_EXCLUSIVE - FULL_HISTORY_START).days, 4250)
        self.assertEqual(FULL_HISTORY_PAIRS, ("EURUSD", "GBPUSD", "USDJPY"))
        self.assertEqual(DEFAULT_WORKERS, 4)
        self.assertEqual(MAX_WORKERS, 8)

        months = list(_iter_month_ranges(FULL_HISTORY_START, FULL_HISTORY_END_EXCLUSIVE))
        self.assertEqual(len(months), 140)
        self.assertEqual(months[0], (date(2015, 1, 1), date(2015, 2, 1)))
        self.assertEqual(months[-1], (date(2026, 8, 1), date(2026, 8, 21)))
        for left, right in zip(months, months[1:]):
            self.assertEqual(left[1], right[0])

    def test_worker_budget_is_bounded(self) -> None:
        self.assertEqual(_validate_workers(1), 1)
        self.assertEqual(_validate_workers(8), 8)
        for invalid in (0, 9, -1, True, 1.5, "4"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    _validate_workers(invalid)  # type: ignore[arg-type]


class FullHistoryLedgerTests(unittest.TestCase):
    def test_recording_reader_requires_complete_and_writes_stable_ledger(self) -> None:
        start = date(2024, 1, 1)
        inner = FakeReader()
        reader = RecordingCompleteRawChunkReader(inner)
        for side in ("BID", "ASK"):
            body = reader.read(RawChunkKey("EURUSD", side, start))
            self.assertIsInstance(body, bytes)

        self.assertEqual(len(reader.records), 2)
        self.assertEqual({str(item["side"]) for item in reader.records}, {"BID", "ASK"})
        for item in reader.records:
            self.assertEqual(item["pair"], "EURUSD")
            self.assertEqual(item["date_utc"], "2024-01-01")
            self.assertEqual(item["status"], "complete")
            self.assertEqual(len(str(item["sha256"])), 64)
            self.assertGreater(int(item["size_bytes"]), 0)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "raw-ledger.json"
            reader.write_ledger(path)
            first = path.read_bytes()
            reader.write_ledger(path)
            self.assertEqual(path.read_bytes(), first)

        missing = RecordingCompleteRawChunkReader(FakeReader(not_found=True))
        with self.assertRaises(ValueError):
            missing.read(RawChunkKey("EURUSD", "BID", start))

    def test_ledger_validator_requires_exact_cartesian_plan(self) -> None:
        start = date(2024, 1, 1)
        end = date(2024, 1, 4)
        valid = ledger_for("EURUSD", start, end)
        validate_full_history_ledger(valid, "EURUSD", start, end)

        cases: list[list[dict[str, object]]] = []
        cases.append(valid[:-1])
        cases.append(valid + [dict(valid[0])])

        wrong_pair = [dict(item) for item in valid]
        wrong_pair[0]["pair"] = "GBPUSD"
        cases.append(wrong_pair)

        wrong_side = [dict(item) for item in valid]
        wrong_side[0]["side"] = "MID"
        cases.append(wrong_side)

        wrong_date = [dict(item) for item in valid]
        wrong_date[0]["date_utc"] = "2024-01-05"
        cases.append(wrong_date)

        not_complete = [dict(item) for item in valid]
        not_complete[0]["status"] = "not_found"
        cases.append(not_complete)

        malformed_sha = [dict(item) for item in valid]
        malformed_sha[0]["sha256"] = "abc"
        cases.append(malformed_sha)

        zero_size = [dict(item) for item in valid]
        zero_size[0]["size_bytes"] = 0
        cases.append(zero_size)

        for records in cases:
            with self.subTest(records=records[:1]):
                with self.assertRaises(ValueError):
                    validate_full_history_ledger(records, "EURUSD", start, end)


if __name__ == "__main__":
    unittest.main()
