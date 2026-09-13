from __future__ import annotations

import unittest
from datetime import datetime, timezone

import polars as pl

from fmp.data.phase2.market_hours import is_market_open_minute
from fmp.data.phase2.quality import analyze_quality
from fmp.data.phase2.schema import CANONICAL_SCHEMA_VERSION, INGESTION_VERSION


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
        timestamp = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
        frame = pl.DataFrame(
            {
                "timestamp_utc": [timestamp],
                "symbol": ["EURUSD"],
                "bid_open": [1.10], "bid_high": [1.09], "bid_low": [1.08], "bid_close": [1.10],
                "ask_open": [1.09], "ask_high": [1.11], "ask_low": [1.08], "ask_close": [1.09],
                "bid_volume": [1.0], "ask_volume": [None],
                "source": ["dukascopy"],
                "ingestion_version": [INGESTION_VERSION],
                "schema_version": [CANONICAL_SCHEMA_VERSION],
            }
        ).with_columns(pl.col("timestamp_utc").dt.replace_time_zone("UTC"))
        before = frame.clone()
        report = analyze_quality(frame)
        codes = [item["code"] for item in report["findings"]]
        self.assertIn("bid_ohlc_invalid", codes)
        self.assertIn("ask_below_bid", codes)
        self.assertIn("missing_ask_side", codes)
        self.assertTrue(frame.equals(before))


if __name__ == "__main__":
    unittest.main()
