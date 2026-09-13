from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

import polars as pl

from fmp.data.phase2.normalize import normalize_decoded_sides
from fmp.data.phase2.schema import CANONICAL_SCHEMA_VERSION


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


class Phase2NormalizeTests(unittest.TestCase):
    def test_outer_join_preserves_one_sided_minute(self) -> None:
        out = normalize_decoded_sides(decoded_side("BID", [0, 1]), decoded_side("ASK", [0]))
        self.assertEqual(out.height, 2)
        second = out.filter(pl.col("timestamp_utc") == datetime(2024, 1, 2, 0, 1, tzinfo=timezone.utc))
        self.assertEqual(second.height, 1)
        self.assertIsNone(second["ask_open"][0])
        self.assertEqual(second["bid_open"][0], 1.1001)
        self.assertEqual(out["schema_version"].unique().to_list(), [CANONICAL_SCHEMA_VERSION])


if __name__ == "__main__":
    unittest.main()
