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
from fmp.data.phase2.raw_reader import LocalRawChunkReader, RawReadError
from fmp.data.phase2.schema import CANONICAL_COLUMNS, CANONICAL_SCHEMA_VERSION
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


def manifest_base(key: RawChunkKey) -> dict[str, object]:
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
        "retrieved_at_utc": "2026-09-13T12:00:00+00:00",
    }


def complete_manifest(key: RawChunkKey, body: bytes) -> dict[str, object]:
    return manifest_base(key) | {
        "status": "complete",
        "http_status": 200,
        "sha256": hashlib.sha256(body).hexdigest(),
        "compressed_size_bytes": len(body),
        "records": 1,
    }


def not_found_manifest(key: RawChunkKey) -> dict[str, object]:
    return manifest_base(key) | {
        "status": "not_found",
        "http_status": 404,
        "sha256": None,
        "compressed_size_bytes": None,
        "records": None,
    }


def paths(root: Path, key: RawChunkKey) -> tuple[Path, Path]:
    return root / "raw" / key.relative_raw_path, root / "manifests" / key.relative_manifest_path


def write_manifest(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class Phase2NormalizeTests(unittest.TestCase):
    def test_outer_join_preserves_one_sided_minute(self) -> None:
        out = normalize_decoded_sides(decoded_side("BID", [0, 1]), decoded_side("ASK", [0]))
        self.assertEqual(out.height, 2)
        self.assertEqual(out.columns, list(CANONICAL_COLUMNS))
        second = out.filter(pl.col("timestamp_utc") == datetime(2024, 1, 2, 0, 1, tzinfo=timezone.utc))
        self.assertEqual(second.height, 1)
        self.assertIsNone(second["ask_open"][0])
        self.assertEqual(second["bid_open"][0], 1.1001)
        self.assertEqual(out["schema_version"].unique().to_list(), [CANONICAL_SCHEMA_VERSION])

    def test_rejects_duplicate_timestamp_within_side(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate"):
            normalize_decoded_sides(decoded_side("BID", [0, 0]), decoded_side("ASK", [0]))

    def test_local_raw_reader_returns_only_manifest_verified_bytes(self) -> None:
        key = RawChunkKey("EURUSD", "BID", date(2024, 1, 2))
        body = b"verified-raw-bytes"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_path, manifest_path = paths(root, key)
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path.write_bytes(body)
            write_manifest(manifest_path, complete_manifest(key, body))
            self.assertEqual(LocalRawChunkReader(root).read(key), body)

    def test_local_raw_reader_returns_none_for_verified_not_found(self) -> None:
        key = RawChunkKey("EURUSD", "ASK", date(2024, 1, 2))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, manifest_path = paths(root, key)
            write_manifest(manifest_path, not_found_manifest(key))
            self.assertIsNone(LocalRawChunkReader(root).read(key))

    def test_local_raw_reader_rejects_checksum_mismatch(self) -> None:
        key = RawChunkKey("EURUSD", "BID", date(2024, 1, 2))
        body = b"verified-raw-bytes"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_path, manifest_path = paths(root, key)
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path.write_bytes(b"tampered-raw-bytes")
            manifest = complete_manifest(key, body)
            manifest["compressed_size_bytes"] = len(b"tampered-raw-bytes")
            write_manifest(manifest_path, manifest)
            with self.assertRaisesRegex(RawReadError, "checksum mismatch"):
                LocalRawChunkReader(root).read(key)

    def test_local_raw_reader_rejects_size_mismatch(self) -> None:
        key = RawChunkKey("EURUSD", "BID", date(2024, 1, 2))
        body = b"verified-raw-bytes"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_path, manifest_path = paths(root, key)
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path.write_bytes(body + b"x")
            write_manifest(manifest_path, complete_manifest(key, body))
            with self.assertRaisesRegex(RawReadError, "size mismatch"):
                LocalRawChunkReader(root).read(key)

    def test_local_raw_reader_rejects_missing_manifest(self) -> None:
        key = RawChunkKey("EURUSD", "BID", date(2024, 1, 2))
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RawReadError, "missing Phase 1 manifest"):
                LocalRawChunkReader(Path(tmp)).read(key)

    def test_local_raw_reader_rejects_raw_beside_not_found(self) -> None:
        key = RawChunkKey("EURUSD", "ASK", date(2024, 1, 2))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_path, manifest_path = paths(root, key)
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path.write_bytes(b"illegal")
            write_manifest(manifest_path, not_found_manifest(key))
            with self.assertRaisesRegex(RawReadError, "raw object present beside not_found"):
                LocalRawChunkReader(root).read(key)


if __name__ == "__main__":
    unittest.main()
