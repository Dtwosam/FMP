from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import polars as pl

from fmp.data.phase2.cloud_golden import (
    GOLDEN_DAY,
    GOLDEN_PAIRS,
    RecordingRawChunkReader,
    run_cloud_golden,
)
from fmp.data.phase2.schema import CANONICAL_COLUMNS, CANONICAL_SCHEMA_VERSION, INGESTION_VERSION
from fmp.data.types import RawChunkKey


class FakeReader:
    def __init__(self) -> None:
        self.calls: list[RawChunkKey] = []

    def read(self, key: RawChunkKey) -> bytes:
        self.calls.append(key)
        return f"{key.pair}-{key.side}-{key.day.isoformat()}".encode()


def canonical_frame(pair: str) -> pl.DataFrame:
    start = datetime(2024, 1, 2, 0, 0, tzinfo=timezone.utc)
    frame = pl.DataFrame(
        {
            "timestamp_utc": [start, start + timedelta(minutes=1)],
            "symbol": [pair, pair],
            "bid_open": [1.0, 1.1],
            "bid_high": [1.1, 1.2],
            "bid_low": [0.9, 1.0],
            "bid_close": [1.05, 1.15],
            "ask_open": [1.01, 1.11],
            "ask_high": [1.11, 1.21],
            "ask_low": [0.91, 1.01],
            "ask_close": [1.06, 1.16],
            "bid_volume": [1.0, 2.0],
            "ask_volume": [3.0, 4.0],
            "source": ["dukascopy", "dukascopy"],
            "ingestion_version": [INGESTION_VERSION, INGESTION_VERSION],
            "schema_version": [CANONICAL_SCHEMA_VERSION, CANONICAL_SCHEMA_VERSION],
        }
    ).with_columns(pl.col("timestamp_utc").dt.replace_time_zone("UTC"))
    return frame.select(list(CANONICAL_COLUMNS))


class CloudGoldenTests(unittest.TestCase):
    def test_golden_scope_is_fixed_to_both_divisor_classes(self) -> None:
        self.assertEqual(GOLDEN_DAY, date(2024, 1, 2))
        self.assertEqual(GOLDEN_PAIRS, ("EURUSD", "USDJPY"))

    def test_recording_reader_captures_verified_raw_identity(self) -> None:
        inner = FakeReader()
        reader = RecordingRawChunkReader(inner)
        key = RawChunkKey("EURUSD", "BID", GOLDEN_DAY)
        body = reader.read(key)
        self.assertIsNotNone(body)
        self.assertEqual(len(reader.evidence), 1)
        item = reader.evidence[0]
        self.assertEqual(item["pair"], "EURUSD")
        self.assertEqual(item["side"], "BID")
        self.assertEqual(item["date_utc"], "2024-01-02")
        self.assertEqual(item["size_bytes"], len(body or b""))
        self.assertEqual(len(str(item["sha256"])), 64)

    def test_bounded_run_reads_exactly_four_chunks_and_writes_all_evidence(self) -> None:
        inner = FakeReader()

        def fake_normalize(reader: RecordingRawChunkReader, pair: str, day: date) -> pl.DataFrame:
            self.assertEqual(day, GOLDEN_DAY)
            reader.read(RawChunkKey(pair, "BID", day))  # type: ignore[arg-type]
            reader.read(RawChunkKey(pair, "ASK", day))  # type: ignore[arg-type]
            return canonical_frame(pair)

        with tempfile.TemporaryDirectory() as tmp, patch(
            "fmp.data.phase2.cloud_golden.normalize_day", side_effect=fake_normalize
        ):
            summary = run_cloud_golden(inner, Path(tmp), code_commit="abc123")
            self.assertEqual(
                [(key.pair, key.side, key.day) for key in inner.calls],
                [
                    ("EURUSD", "BID", GOLDEN_DAY),
                    ("EURUSD", "ASK", GOLDEN_DAY),
                    ("USDJPY", "BID", GOLDEN_DAY),
                    ("USDJPY", "ASK", GOLDEN_DAY),
                ],
            )
            self.assertEqual(summary["pairs"], ["EURUSD", "USDJPY"])
            self.assertEqual(len(summary["raw_chunks"]), 4)
            for pair in GOLDEN_PAIRS:
                pair_evidence = summary["evidence"][pair]
                self.assertEqual(set(pair_evidence), {"1m", "quality", "5m", "15m", "1h"})
                for item in pair_evidence.values():
                    self.assertTrue((Path(tmp) / str(item["path"])).is_file())
            summary_path = Path(tmp) / "summary.json"
            self.assertTrue(summary_path.is_file())
            self.assertEqual(json.loads(summary_path.read_text())["code_commit"], "abc123")


if __name__ == "__main__":
    unittest.main()
