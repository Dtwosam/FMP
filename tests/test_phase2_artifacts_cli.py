from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import polars as pl

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
            self.assertEqual(
                round_trip["timestamp_utc"].to_list(),
                sorted(frame["timestamp_utc"].to_list()),
            )
            self.assertEqual(PARQUET_WRITER_CONFIG["compression"], "zstd")
            self.assertEqual(PARQUET_WRITER_CONFIG["compression_level"], 3)
            self.assertTrue(PARQUET_WRITER_CONFIG["statistics"])

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


if __name__ == "__main__":
    unittest.main()
