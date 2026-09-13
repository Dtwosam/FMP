from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

import polars as pl

from fmp.data.phase2.resample import resample_canonical
from fmp.data.phase2.schema import CANONICAL_SCHEMA_VERSION, DERIVED_SCHEMA_VERSION, INGESTION_VERSION


def canonical_minutes(count: int) -> pl.DataFrame:
    start = datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc)
    timestamps = [start + timedelta(minutes=i) for i in range(count)]
    bid_open = [1.1000 + i * 0.0001 for i in range(count)]
    return pl.DataFrame(
        {
            "timestamp_utc": timestamps,
            "symbol": ["EURUSD"] * count,
            "bid_open": bid_open,
            "bid_high": [value + 0.0003 for value in bid_open],
            "bid_low": [value - 0.0002 for value in bid_open],
            "bid_close": [value + 0.0001 for value in bid_open],
            "ask_open": [value + 0.0002 for value in bid_open],
            "ask_high": [value + 0.0005 for value in bid_open],
            "ask_low": [value for value in bid_open],
            "ask_close": [value + 0.0003 for value in bid_open],
            "bid_volume": [1.0] * count,
            "ask_volume": [2.0] * count,
            "source": ["dukascopy"] * count,
            "ingestion_version": [INGESTION_VERSION] * count,
            "schema_version": [CANONICAL_SCHEMA_VERSION] * count,
        }
    ).with_columns(pl.col("timestamp_utc").dt.replace_time_zone("UTC"))


class Phase2ResampleTests(unittest.TestCase):
    def test_five_minute_buckets_are_closed_left_and_mark_incomplete_tail(self) -> None:
        frame = canonical_minutes(6)
        out = resample_canonical(frame, "5m")
        self.assertEqual(out.height, 2)

        first = out.row(0, named=True)
        self.assertEqual(first["timestamp_utc"], datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc))
        self.assertEqual(first["bid_open"], frame["bid_open"][0])
        self.assertEqual(first["bid_high"], max(frame["bid_high"][:5]))
        self.assertEqual(first["bid_low"], min(frame["bid_low"][:5]))
        self.assertEqual(first["bid_close"], frame["bid_close"][4])
        self.assertEqual(first["ask_open"], frame["ask_open"][0])
        self.assertEqual(first["ask_close"], frame["ask_close"][4])
        self.assertEqual(first["bid_volume"], 5.0)
        self.assertEqual(first["ask_volume"], 10.0)
        self.assertEqual(first["source_minutes"], 5)
        self.assertEqual(first["expected_open_minutes"], 5)
        self.assertTrue(first["is_complete"])
        self.assertEqual(first["timeframe"], "5m")
        self.assertEqual(first["schema_version"], DERIVED_SCHEMA_VERSION)

        second = out.row(1, named=True)
        self.assertEqual(second["timestamp_utc"], datetime(2026, 9, 14, 0, 5, tzinfo=timezone.utc))
        self.assertEqual(second["source_minutes"], 1)
        self.assertEqual(second["expected_open_minutes"], 5)
        self.assertFalse(second["is_complete"])


if __name__ == "__main__":
    unittest.main()
