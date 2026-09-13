from __future__ import annotations

import lzma
import struct
import unittest
from datetime import date, datetime, timezone

from fmp.data.phase2.bi5 import Phase2DecodeError, decode_bi5_day
from fmp.data.types import RawChunkKey


def make_bi5(rows: list[tuple[int, int, int, int, int, float]]) -> bytes:
    raw = b"".join(struct.pack(">IIIIIf", *row) for row in rows)
    return lzma.compress(raw)


class Phase2Bi5Tests(unittest.TestCase):
    def test_decodes_eurusd_field_order_and_scale(self) -> None:
        body = make_bi5([(0, 110000, 110010, 109990, 110020, 1.5)])
        frame = decode_bi5_day(
            RawChunkKey("EURUSD", "BID", date(2024, 1, 2)),
            body,
        )
        self.assertEqual(frame["open"].to_list(), [1.1])
        self.assertEqual(frame["close"].to_list(), [1.1001])
        self.assertEqual(frame["low"].to_list(), [1.0999])
        self.assertEqual(frame["high"].to_list(), [1.1002])
        self.assertEqual(
            frame["timestamp_utc"].to_list(),
            [datetime(2024, 1, 2, tzinfo=timezone.utc)],
        )

    def test_rejects_more_than_1440_records(self) -> None:
        rows = [
            (idx, 110000, 110010, 109990, 110020, 1.0)
            for idx in range(1441)
        ]
        with self.assertRaisesRegex(Phase2DecodeError, "record count"):
            decode_bi5_day(
                RawChunkKey("EURUSD", "BID", date(2024, 1, 2)),
                make_bi5(rows),
            )


if __name__ == "__main__":
    unittest.main()
