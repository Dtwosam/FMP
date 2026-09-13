from __future__ import annotations

import hashlib
import json
import lzma
import struct
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import polars as pl

from fmp.data.cli import main
from fmp.data.dukascopy import DukascopySource
from fmp.data.phase2.artifacts import (
    PARQUET_WRITER_CONFIG,
    PHASE1_FROZEN_PLAN_SHA256,
    PHASE1_SOURCE_CHECKPOINT,
    build_processed_manifest,
    sha256_file,
    write_parquet_partition,
    write_processed_manifest,
)
from fmp.data.phase2.schema import CANONICAL_COLUMNS, CANONICAL_SCHEMA_VERSION, INGESTION_VERSION
from fmp.data.types import RawChunkKey


def canonical_frame() -> pl.DataFrame:
    start = datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc)
    frame = pl.DataFrame(
        {
            "timestamp_utc": [start + timedelta(minutes=1), start],
            "symbol": ["EURUSD", "EURUSD"],
            "bid_open": [1.1001, 1.1000],
            "bid_high": [1.1004, 1.1003],
            "bid_low": [1.0999, 1.0998],
            "bid_close": [1.1002, 1.1001],
            "ask_open": [1.1003, 1.1002],
            "ask_high": [1.1006, 1.1005],
            "ask_low": [1.1001, 1.1000],
            "ask_close": [1.1004, 1.1003],
            "bid_volume": [2.0, 1.0],
            "ask_volume": [4.0, 3.0],
            "source": ["dukascopy", "dukascopy"],
            "ingestion_version": [INGESTION_VERSION, INGESTION_VERSION],
            "schema_version": [CANONICAL_SCHEMA_VERSION, CANONICAL_SCHEMA_VERSION],
        }
    ).with_columns(pl.col("timestamp_utc").dt.replace_time_zone("UTC"))
    return frame.select(list(CANONICAL_COLUMNS))


def _bi5(rows: list[tuple[int, int, int, int, int, float]]) -> bytes:
    return lzma.compress(b"".join(struct.pack(">IIIIIf", *row) for row in rows))


def _complete_manifest(key: RawChunkKey, body: bytes, records: int) -> dict[str, object]:
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
        "records": records,
        "retrieved_at_utc": "2026-09-13T12:00:00+00:00",
    }


def _write_phase1_day(root: Path, pair: str, day: date) -> dict[str, str]:
    rows_by_side = {
        "BID": [(0, 110000, 110010, 109990, 110020, 1.0), (60, 110010, 110020, 110000, 110030, 2.0)],
        "ASK": [(0, 110020, 110030, 110010, 110040, 3.0), (60, 110030, 110040, 110020, 110050, 4.0)],
    }
    checksums: dict[str, str] = {}
    for side, rows in rows_by_side.items():
        key = RawChunkKey(pair, side, day)  # type: ignore[arg-type]
        body = _bi5(rows)
        raw_path = root / "raw" / key.relative_raw_path
        manifest_path = root / "manifests" / key.relative_manifest_path
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_bytes(body)
        manifest_path.write_text(json.dumps(_complete_manifest(key, body, len(rows))), encoding="utf-8")
        checksums[side] = hashlib.sha256(body).hexdigest()
    return checksums


class Phase2ArtifactTests(unittest.TestCase):
    def test_parquet_write_is_deterministic_and_round_trips_canonical_schema(self) -> None:
        frame = canonical_frame()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "first.parquet"
            second = root / "second.parquet"
            digest_a = write_parquet_partition(frame, first)
            digest_b = write_parquet_partition(frame, second)

            self.assertEqual(digest_a.sha256, digest_b.sha256)
            self.assertEqual(digest_a.size_bytes, digest_b.size_bytes)
            self.assertEqual(digest_a.row_count, 2)
            self.assertEqual(digest_a.sha256, sha256_file(first))

            round_trip = pl.read_parquet(first)
            self.assertEqual(round_trip.columns, list(CANONICAL_COLUMNS))
            self.assertEqual(round_trip["timestamp_utc"].to_list(), sorted(frame["timestamp_utc"].to_list()))
            self.assertEqual(PARQUET_WRITER_CONFIG["compression"], "zstd")
            self.assertEqual(PARQUET_WRITER_CONFIG["compression_level"], 3)
            self.assertTrue(PARQUET_WRITER_CONFIG["statistics"])

    def test_parquet_write_is_idempotent_but_rejects_conflicting_existing_partition(self) -> None:
        frame = canonical_frame()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "partition.parquet"
            first = write_parquet_partition(frame, path)
            repeated = write_parquet_partition(frame, path)
            self.assertEqual(repeated.sha256, first.sha256)

            conflicting = frame.with_columns(
                pl.when(pl.col("timestamp_utc") == frame["timestamp_utc"][0])
                .then(pl.lit(9.9))
                .otherwise(pl.col("bid_close"))
                .alias("bid_close")
            )
            with self.assertRaisesRegex(ValueError, "conflicting existing Parquet partition"):
                write_parquet_partition(conflicting, path)
            self.assertEqual(sha256_file(path), first.sha256)

    def test_processed_manifest_records_source_identity_artifacts_and_writer(self) -> None:
        generated_at = datetime(2026, 9, 13, 19, 0, tzinfo=timezone.utc)
        artifacts = {
            "1m": {"path": "1m/EURUSD/2026/09.parquet", "sha256": "a" * 64, "size_bytes": 123, "row_count": 2},
            "quality": {"path": "quality/EURUSD.json", "sha256": "b" * 64, "size_bytes": 456, "row_count": None},
        }
        quality_summary = {"finding_counts": {"spread_outlier": 1}, "row_count": 2}
        manifest = build_processed_manifest(
            symbol="EURUSD",
            actual_start_utc=datetime(2026, 9, 1, tzinfo=timezone.utc),
            actual_end_utc=datetime(2026, 9, 30, 23, 59, tzinfo=timezone.utc),
            artifacts=artifacts,
            row_counts={"1m": 2, "5m": 1, "15m": 1, "1h": 1},
            quality_summary=quality_summary,
            generated_at_utc=generated_at,
            code_commit="deadbeef",
        )
        self.assertEqual(manifest["manifest_version"], 1)
        self.assertEqual(manifest["schema_version"], CANONICAL_SCHEMA_VERSION)
        self.assertEqual(manifest["ingestion_version"], INGESTION_VERSION)
        self.assertEqual(manifest["source_snapshot"]["checkpoint"], PHASE1_SOURCE_CHECKPOINT)
        self.assertEqual(manifest["source_snapshot"]["frozen_plan_sha256"], PHASE1_FROZEN_PLAN_SHA256)
        self.assertEqual(manifest["artifacts"], artifacts)
        self.assertEqual(manifest["row_counts"]["1m"], 2)
        self.assertEqual(manifest["quality_summary"], quality_summary)
        self.assertEqual(manifest["parquet_writer"], PARQUET_WRITER_CONFIG)
        self.assertEqual(manifest["generated_at_utc"], "2026-09-13T19:00:00Z")
        self.assertEqual(manifest["code_commit"], "deadbeef")
        self.assertEqual(manifest["polars_version"], pl.__version__)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "EURUSD.json"
            write_processed_manifest(path, manifest)
            loaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(loaded, manifest)
            self.assertTrue(path.read_text(encoding="utf-8").endswith("\n"))

    def test_bounded_cli_commands_and_process_phase2_leave_raw_bytes_unchanged(self) -> None:
        day = date(2024, 1, 2)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "data"
            raw_hashes = _write_phase1_day(root, "EURUSD", day)

            decoded = Path(tmp) / "decoded.parquet"
            self.assertEqual(main(["decode-day", "--root", str(root), "--pair", "EURUSD", "--side", "BID", "--date", day.isoformat(), "--out", str(decoded)]), 0)
            self.assertEqual(pl.read_parquet(decoded).height, 2)

            canonical = Path(tmp) / "canonical.parquet"
            self.assertEqual(main(["normalize", "--root", str(root), "--pair", "EURUSD", "--start", day.isoformat(), "--end", "2024-01-03", "--out", str(canonical)]), 0)
            self.assertEqual(pl.read_parquet(canonical).height, 2)

            quality = Path(tmp) / "quality.json"
            self.assertEqual(main(["quality", "--input", str(canonical), "--out", str(quality)]), 0)
            quality_payload = json.loads(quality.read_text(encoding="utf-8"))
            self.assertEqual(quality_payload["row_count"], 2)

            five = Path(tmp) / "five.parquet"
            self.assertEqual(main(["resample", "--input", str(canonical), "--timeframe", "5m", "--out", str(five)]), 0)
            self.assertEqual(pl.read_parquet(five).height, 1)

            self.assertEqual(main(["process-phase2", "--root", str(root), "--pair", "EURUSD", "--start", day.isoformat(), "--end", "2024-01-03", "--code-commit", "testcommit"]), 0)
            expected = [
                root / "processed" / CANONICAL_SCHEMA_VERSION / "1m" / "EURUSD" / "2024" / "01.parquet",
                root / "processed" / CANONICAL_SCHEMA_VERSION / "5m" / "EURUSD" / "2024" / "01.parquet",
                root / "processed" / CANONICAL_SCHEMA_VERSION / "15m" / "EURUSD" / "2024" / "01.parquet",
                root / "processed" / CANONICAL_SCHEMA_VERSION / "1h" / "EURUSD" / "2024" / "01.parquet",
                root / "processed" / CANONICAL_SCHEMA_VERSION / "quality" / "EURUSD.json",
                root / "manifests" / "processed" / CANONICAL_SCHEMA_VERSION / "EURUSD.json",
            ]
            for path in expected:
                self.assertTrue(path.exists(), path)

            manifest = json.loads(expected[-1].read_text(encoding="utf-8"))
            self.assertEqual(manifest["code_commit"], "testcommit")
            self.assertEqual(manifest["row_counts"]["1m"], 2)

            for side in ("BID", "ASK"):
                key = RawChunkKey("EURUSD", side, day)  # type: ignore[arg-type]
                raw_path = root / "raw" / key.relative_raw_path
                self.assertEqual(hashlib.sha256(raw_path.read_bytes()).hexdigest(), raw_hashes[side])


if __name__ == "__main__":
    unittest.main()
