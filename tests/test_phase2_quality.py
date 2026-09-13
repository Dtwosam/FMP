from __future__ import annotations

import unittest
from datetime import datetime, timezone

from fmp.data.phase2.market_hours import is_market_open_minute


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


if __name__ == "__main__":
    unittest.main()
