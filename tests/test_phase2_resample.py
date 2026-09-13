from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

import polars as pl

from fmp.data.phase2.resample import resample_canonical
from fmp.data.phase2.schema import CANONICAL_SCHEMA_VERSION, DERIVED_SCHEMA_VERSION, INGESTION_VERSION


def canonical_minutes(count: int, start: datetime | None = None) -> pl.DataFrame:
    start = start or datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc)
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

    def test_one_sided_minute_keeps_bar_but_marks_it_incomplete(self) -> None:
        start = datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc)
        frame = canonical_minutes(5, start).with_columns(
            pl.when(pl.col("timestamp_utc") == start + timedelta(minutes=2))
            .then(pl.lit(None, dtype=pl.Float64))
            .otherwise(pl.col("ask_open"))
            .alias("ask_open"),
            pl.when(pl.col("timestamp_utc") == start + timedelta(minutes=2))
            .then(pl.lit(None, dtype=pl.Float64))
            .otherwise(pl.col("ask_high"))
            .alias("ask_high"),
            pl.when(pl.col("timestamp_utc") == start + timedelta(minutes=2))
            .then(pl.lit(None, dtype=pl.Float64))
            .otherwise(pl.col("ask_low"))
            .alias("ask_low"),
            pl.when(pl.col("timestamp_utc") == start + timedelta(minutes=2))
            .then(pl.lit(None, dtype=pl.Float64))
            .otherwise(pl.col("ask_close"))
            .alias("ask_close"),
        )
        row = resample_canonical(frame, "5m").row(0, named=True)
        self.assertEqual(row["source_minutes"], 5)
        self.assertEqual(row["expected_open_minutes"], 5)
        self.assertFalse(row["is_complete"])
        self.assertEqual(row["ask_open"], frame["ask_open"][0])
        self.assertEqual(row["ask_close"], frame["ask_close"][4])

    def test_all_null_volume_stays_null(self) -> None:
        frame = canonical_minutes(5).with_columns(pl.lit(None, dtype=pl.Float64).alias("bid_volume"))
        row = resample_canonical(frame, "5m").row(0, named=True)
        self.assertIsNone(row["bid_volume"])
        self.assertEqual(row["ask_volume"], 10.0)

    def test_fifteen_minute_and_hour_labels_are_utc_aligned(self) -> None:
        frame = canonical_minutes(61)
        fifteen = resample_canonical(frame, "15m")
        self.assertEqual(
            fifteen["timestamp_utc"].to_list(),
            [
                datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc),
                datetime(2026, 9, 14, 0, 15, tzinfo=timezone.utc),
                datetime(2026, 9, 14, 0, 30, tzinfo=timezone.utc),
                datetime(2026, 9, 14, 0, 45, tzinfo=timezone.utc),
                datetime(2026, 9, 14, 1, 0, tzinfo=timezone.utc),
            ],
        )
        hourly = resample_canonical(frame, "1h")
        self.assertEqual(
            hourly["timestamp_utc"].to_list(),
            [
                datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc),
                datetime(2026, 9, 14, 1, 0, tzinfo=timezone.utc),
            ],
        )

    def test_expected_open_minutes_follow_new_york_dst(self) -> None:
        winter_open = canonical_minutes(1, datetime(2026, 1, 4, 22, 0, tzinfo=timezone.utc))
        summer_open = canonical_minutes(1, datetime(2026, 7, 5, 21, 0, tzinfo=timezone.utc))
        self.assertEqual(resample_canonical(winter_open, "5m")["expected_open_minutes"][0], 5)
        self.assertEqual(resample_canonical(summer_open, "5m")["expected_open_minutes"][0], 5)

    def test_friday_close_and_sunday_open_boundaries_drive_completeness(self) -> None:
        friday_open = resample_canonical(
            canonical_minutes(5, datetime(2026, 9, 18, 20, 55, tzinfo=timezone.utc)),
            "5m",
        ).row(0, named=True)
        self.assertEqual(friday_open["expected_open_minutes"], 5)
        self.assertTrue(friday_open["is_complete"])

        friday_closed = resample_canonical(
            canonical_minutes(1, datetime(2026, 9, 18, 21, 0, tzinfo=timezone.utc)),
            "5m",
        ).row(0, named=True)
        self.assertEqual(friday_closed["expected_open_minutes"], 0)
        self.assertFalse(friday_closed["is_complete"])

        sunday_closed = resample_canonical(
            canonical_minutes(1, datetime(2026, 9, 20, 20, 55, tzinfo=timezone.utc)),
            "5m",
        ).row(0, named=True)
        self.assertEqual(sunday_closed["expected_open_minutes"], 0)
        self.assertFalse(sunday_closed["is_complete"])

        sunday_open = resample_canonical(
            canonical_minutes(5, datetime(2026, 9, 20, 21, 0, tzinfo=timezone.utc)),
            "5m",
        ).row(0, named=True)
        self.assertEqual(sunday_open["expected_open_minutes"], 5)
        self.assertTrue(sunday_open["is_complete"])


if __name__ == "__main__":
    unittest.main()
