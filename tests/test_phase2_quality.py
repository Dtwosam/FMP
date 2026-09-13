from __future__ import annotations

import math
import unittest
from datetime import datetime, timedelta, timezone

import polars as pl

from fmp.data.phase2.market_hours import is_market_open_minute
from fmp.data.phase2.quality import analyze_quality
from fmp.data.phase2.schema import CANONICAL_SCHEMA_VERSION, INGESTION_VERSION


def canonical_frame(timestamps: list[datetime]) -> pl.DataFrame:
    count = len(timestamps)
    return pl.DataFrame(
        {
            "timestamp_utc": timestamps,
            "symbol": ["EURUSD"] * count,
            "bid_open": [1.10] * count,
            "bid_high": [1.11] * count,
            "bid_low": [1.09] * count,
            "bid_close": [1.10] * count,
            "ask_open": [1.1002] * count,
            "ask_high": [1.1102] * count,
            "ask_low": [1.0902] * count,
            "ask_close": [1.1002] * count,
            "bid_volume": [1.0] * count,
            "ask_volume": [1.0] * count,
            "source": ["dukascopy"] * count,
            "ingestion_version": [INGESTION_VERSION] * count,
            "schema_version": [CANONICAL_SCHEMA_VERSION] * count,
        }
    ).with_columns(pl.col("timestamp_utc").dt.replace_time_zone("UTC"))


def frame_from_closes(timestamps: list[datetime], bid_closes: list[float], spreads: list[float]) -> pl.DataFrame:
    ask_closes = [bid + spread for bid, spread in zip(bid_closes, spreads)]
    count = len(timestamps)
    return pl.DataFrame(
        {
            "timestamp_utc": timestamps,
            "symbol": ["EURUSD"] * count,
            "bid_open": bid_closes,
            "bid_high": [value + 0.001 for value in bid_closes],
            "bid_low": [value - 0.001 for value in bid_closes],
            "bid_close": bid_closes,
            "ask_open": ask_closes,
            "ask_high": [value + 0.001 for value in ask_closes],
            "ask_low": [value - 0.001 for value in ask_closes],
            "ask_close": ask_closes,
            "bid_volume": [1.0] * count,
            "ask_volume": [1.0] * count,
            "source": ["dukascopy"] * count,
            "ingestion_version": [INGESTION_VERSION] * count,
            "schema_version": [CANONICAL_SCHEMA_VERSION] * count,
        }
    ).with_columns(pl.col("timestamp_utc").dt.replace_time_zone("UTC"))


class Phase2MarketHoursTests(unittest.TestCase):
    def test_new_york_week_boundaries(self) -> None:
        self.assertFalse(is_market_open_minute(datetime(2026, 9, 13, 20, 59, tzinfo=timezone.utc)))
        self.assertTrue(is_market_open_minute(datetime(2026, 9, 13, 21, 0, tzinfo=timezone.utc)))
        self.assertTrue(is_market_open_minute(datetime(2026, 9, 18, 20, 59, tzinfo=timezone.utc)))
        self.assertFalse(is_market_open_minute(datetime(2026, 9, 18, 21, 0, tzinfo=timezone.utc)))

    def test_dst_changes_utc_open_hour(self) -> None:
        self.assertTrue(is_market_open_minute(datetime(2026, 1, 4, 22, 0, tzinfo=timezone.utc)))
        self.assertFalse(is_market_open_minute(datetime(2026, 1, 4, 21, 0, tzinfo=timezone.utc)))
        self.assertTrue(is_market_open_minute(datetime(2026, 7, 5, 21, 0, tzinfo=timezone.utc)))


class Phase2QualityTests(unittest.TestCase):
    def test_reports_quote_anomalies_without_mutating_frame(self) -> None:
        start = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
        frame = canonical_frame([start, start + timedelta(minutes=1)]).with_columns(
            pl.when(pl.col("timestamp_utc") == start)
            .then(pl.lit(1.09))
            .otherwise(pl.col("bid_high"))
            .alias("bid_high"),
            pl.when(pl.col("timestamp_utc") == start)
            .then(pl.lit(1.09))
            .otherwise(pl.col("ask_open"))
            .alias("ask_open"),
            pl.when(pl.col("timestamp_utc") == start)
            .then(pl.lit(1.09))
            .otherwise(pl.col("ask_close"))
            .alias("ask_close"),
        )
        frame = frame.with_columns(
            pl.when(pl.col("timestamp_utc") == start + timedelta(minutes=1))
            .then(pl.lit(None, dtype=pl.Float64))
            .otherwise(pl.col("ask_open"))
            .alias("ask_open"),
            pl.when(pl.col("timestamp_utc") == start + timedelta(minutes=1))
            .then(pl.lit(None, dtype=pl.Float64))
            .otherwise(pl.col("ask_high"))
            .alias("ask_high"),
            pl.when(pl.col("timestamp_utc") == start + timedelta(minutes=1))
            .then(pl.lit(None, dtype=pl.Float64))
            .otherwise(pl.col("ask_low"))
            .alias("ask_low"),
            pl.when(pl.col("timestamp_utc") == start + timedelta(minutes=1))
            .then(pl.lit(None, dtype=pl.Float64))
            .otherwise(pl.col("ask_close"))
            .alias("ask_close"),
        )
        before = frame.clone()
        report = analyze_quality(frame)
        codes = [item["code"] for item in report["findings"]]
        self.assertIn("bid_ohlc_invalid", codes)
        self.assertIn("ask_below_bid", codes)
        self.assertIn("missing_ask_side", codes)
        self.assertTrue(frame.equals(before))

    def test_reports_non_positive_non_finite_and_duplicate_values(self) -> None:
        start = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
        frame = canonical_frame([start, start]).with_columns(
            pl.Series("bid_open", [0.0, 1.10]),
            pl.Series("ask_volume", [math.inf, 1.0]),
        )
        report = analyze_quality(frame)
        codes = [item["code"] for item in report["findings"]]
        self.assertIn("non_positive_price", codes)
        self.assertIn("non_finite_value", codes)
        self.assertIn("duplicate_timestamp", codes)
        self.assertEqual(report["duplicate_count"], 1)

    def test_open_market_gap_of_30_missing_minutes_is_long(self) -> None:
        start = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
        report = analyze_quality(canonical_frame([start, start + timedelta(minutes=31)]))
        codes = [item["code"] for item in report["findings"]]
        self.assertIn("missing_open_market_minute", codes)
        self.assertIn("long_weekday_gap", codes)

    def test_weekend_closure_gap_is_not_suspicious_open_market_loss(self) -> None:
        friday = datetime(2026, 9, 18, 20, 59, tzinfo=timezone.utc)
        sunday = datetime(2026, 9, 20, 21, 0, tzinfo=timezone.utc)
        report = analyze_quality(canonical_frame([friday, sunday]))
        codes = [item["code"] for item in report["findings"]]
        self.assertIn("weekend_closure_gap", codes)
        self.assertNotIn("missing_open_market_minute", codes)

    def test_spread_outlier_uses_frozen_iqr_rule(self) -> None:
        start = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
        timestamps = [start + timedelta(minutes=i) for i in range(12)]
        frame = frame_from_closes(timestamps, [1.10] * 12, [0.0002] * 11 + [0.0100])
        report = analyze_quality(frame)
        codes = [item["code"] for item in report["findings"]]
        self.assertEqual(codes.count("spread_outlier"), 1)
        self.assertEqual(report["spread_summary"]["EURUSD"]["outlier_count"], 1)
        self.assertIsNotNone(report["spread_summary"]["EURUSD"]["threshold"])

    def test_midpoint_jump_outlier_excludes_weekend_reopening_gap(self) -> None:
        start = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
        timestamps = [start + timedelta(minutes=i) for i in range(12)]
        bid_closes = [1.10] * 11 + [1.20]
        frame = frame_from_closes(timestamps, bid_closes, [0.0002] * 12)
        report = analyze_quality(frame)
        codes = [item["code"] for item in report["findings"]]
        self.assertEqual(codes.count("price_jump_outlier"), 1)
        self.assertEqual(report["midpoint_return_summary"]["EURUSD"]["outlier_count"], 1)

        friday = datetime(2026, 9, 18, 20, 59, tzinfo=timezone.utc)
        sunday = datetime(2026, 9, 20, 21, 0, tzinfo=timezone.utc)
        weekend = frame_from_closes([friday, sunday], [1.10, 1.20], [0.0002, 0.0002])
        weekend_report = analyze_quality(weekend)
        weekend_codes = [item["code"] for item in weekend_report["findings"]]
        self.assertNotIn("price_jump_outlier", weekend_codes)

    def test_report_includes_versions_range_and_counts(self) -> None:
        start = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
        report = analyze_quality(canonical_frame([start, start + timedelta(minutes=1)]))
        self.assertEqual(report["schema_version"], CANONICAL_SCHEMA_VERSION)
        self.assertEqual(report["ingestion_version"], INGESTION_VERSION)
        self.assertEqual(report["actual_start_utc"], start)
        self.assertEqual(report["actual_end_utc"], start + timedelta(minutes=1))
        self.assertEqual(report["row_count"], 2)


if __name__ == "__main__":
    unittest.main()
