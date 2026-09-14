from __future__ import annotations

import unittest
from datetime import datetime, timezone

import polars as pl

from tests.phase5_helpers import make_bars


class Phase5SessionFeatureTests(unittest.TestCase):
    def _one(self, ts: datetime):
        from fmp.features.base import prepare_base_frame
        from fmp.features.sessions import add_session_features

        base = prepare_base_frame(
            make_bars(timeframe="1h", start=ts, count=1),
            symbol="EURUSD", timeframe="1h", processed_manifest_sha256="a" * 64,
        )
        return add_session_features(base).row(0, named=True)

    def test_london_uses_named_zone_across_dst(self) -> None:
        winter = self._one(datetime(2023, 1, 10, 8, tzinfo=timezone.utc))
        summer = self._one(datetime(2023, 7, 10, 7, tzinfo=timezone.utc))
        self.assertTrue(winter["is_london_session"])
        self.assertTrue(summer["is_london_session"])
        self.assertEqual(winter["minutes_since_london_open"], 0)
        self.assertEqual(summer["minutes_since_london_open"], 0)

    def test_new_york_uses_named_zone_across_dst(self) -> None:
        winter = self._one(datetime(2023, 1, 10, 13, tzinfo=timezone.utc))
        summer = self._one(datetime(2023, 7, 10, 12, tzinfo=timezone.utc))
        self.assertTrue(winter["is_new_york_session"])
        self.assertTrue(summer["is_new_york_session"])
        self.assertEqual(winter["minutes_since_new_york_open"], 0)
        self.assertEqual(summer["minutes_since_new_york_open"], 0)

    def test_us_uk_dst_mismatch_week_overlap_is_computed_from_both_zones(self) -> None:
        # 2023-03-20: US is on DST, UK is not yet on DST.
        row = self._one(datetime(2023, 3, 20, 12, tzinfo=timezone.utc))
        self.assertTrue(row["is_london_session"])
        self.assertTrue(row["is_new_york_session"])
        self.assertTrue(row["is_london_new_york_overlap"])

    def test_complete_bar_interval_must_fit_session(self) -> None:
        inside = self._one(datetime(2023, 1, 10, 15, tzinfo=timezone.utc))
        outside = self._one(datetime(2023, 1, 10, 16, tzinfo=timezone.utc))
        self.assertTrue(inside["is_london_session"])
        self.assertFalse(outside["is_london_session"])
        self.assertIsNone(outside["minutes_since_london_open"])

    def test_tokyo_session_and_utc_clock_fields(self) -> None:
        row = self._one(datetime(2023, 1, 10, 0, tzinfo=timezone.utc))  # 09:00 Tokyo
        self.assertTrue(row["is_asia_session"])
        self.assertEqual(row["minutes_since_asia_open"], 0)
        self.assertEqual(row["hour_utc"], 0)
        self.assertEqual(row["minute_utc"], 0)
        self.assertEqual(row["day_of_week_utc"], 1)


if __name__ == "__main__":
    unittest.main()
