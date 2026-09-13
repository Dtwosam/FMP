from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import polars as pl

from fmp.data.dukascopy import DukascopySource
from fmp.data.phase2.normalize import normalize_decoded_sides
from fmp.data.phase2.raw_reader import LocalRawChunkReader
from fmp.data.phase2.schema import CANONICAL_SCHEMA_VERSION
from fmp.data.types import RawChunkKey


def decoded_side(side: str, minutes: list[int]) -> pl.DataFrame:
    start = datetime(2024, 1, 2, tzinfo=timezone.utc)
    return pl.DataFrame(
        {
            "timestamp_utc": [start + timedelta(minutes=m) for m in minutes],
            "symbol": ["EURUSD"] * len(minutes),
            "side": [side] * len(minutes),
            "open": [1.1000 + m * 0.0001 for m in minutes],
            "high": [1.1002 + m * 0.0001 for m in minutes],
            "low": [1.0998 + m * 0.0001 for m in minutes],
            "close": [1.1001 + m * 0.0001 for m in minutes],
            "volume": [1.0] * len(minutes),
        }
    ).with_columns(pl.col("timestamp_utc").dt.replace_time_zone("UTC"))


def complete_manifest(key: RawChunkKey, body: bytes) -> dict[str, object]:
    return {
        "manifest_version": 1,
        "retrieval_method": "dukascopy-public-daily-m1-bi5-v1",
        "source": "dukascopy",
        "source_url": DukascopySource().url_for(key),
        "pair": key.pair,
        "side": key.side,
        "date_utc": key.day.isoformat(),
        "granularity": "1m",
        "source_format": "bi5-lzma-daily-candles",
        "record_size_bytes": 24,
        "month_indexing": "zero_based_in_source_url",
        "status": "complete",
        "http_status": 200,
        "sha256": hashlib.sha256(body).hexdigest(),
        "compressed_size_bytes": len(body),
        "records": 1,
        "retrieved_at_utc": "2026-09-13T12:00:00+00:00",
    }


class Phase2NormalizeTests(unittest.TestCase):
    def test_outer_join_preserves_one_sided_minute(self) -> None:
        out = normalize_decoded_sides(decoded_side("BID", [0, 1]), decoded_side("ASK", [0]))
        self.assertEqual(out.height, 2)
        second = out.filter(pl.col("timestamp_utc") == datetime(2024, 1, 2, 0, 1, tzinfo=timezone.utc))
        self.assertEqual(second.height, 1)
        self.assertIsNone(second["ask_open"][0])
        self.assertEqual(second["bid_open"][0], 1.1001)
        self.assertEqual(out["schema_version"].unique().to_list(), [CANONICAL_SCHEMA_VERSION])

    def test_local_raw_reader_returns_only_manifest_verified_bytes(self) -> None:
        key = RawChunkKey("EURUSD", "BID", date(2024, 1, 2))
        body = b"verified-raw-bytes"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_path = root / "raw" / key.relative_raw_path
            manifest_path = root / "manifests" / key.relative_manifest_path
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path.write_bytes(body)
            manifest_path.write_text(json.dumps(complete_manifest(key, body)), encoding="utf-8")
            self.assertEqual(LocalRawChunkReader(root).read(key), body)


if __name__ == "__main__":
    unittest.main()
