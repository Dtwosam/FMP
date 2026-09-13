from __future__ import annotations

import lzma
import math
import struct
import unittest
from datetime import date, datetime, timezone

from fmp.data.phase2.bi5 import Phase2DecodeError, decode_bi5_day
from fmp.data.phase2.schema import DECODED_SIDE_COLUMNS
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
        self.assertEqual(frame.columns, list(DECODED_SIDE_COLUMNS))
        self.assertEqual(frame["open"].to_list(), [1.1])
        self.assertEqual(frame["close"].to_list(), [1.1001])
        self.assertEqual(frame["low"].to_list(), [1.0999])
        self.assertEqual(frame["high"].to_list(), [1.1002])
        self.assertEqual(
            frame["timestamp_utc"].to_list(),
            [datetime(2024, 1, 2, tzinfo=timezone.utc)],
        )

    def test_decodes_usdjpy_with_frozen_1000_divisor(self) -> None:
        frame = decode_bi5_day(
            RawChunkKey("USDJPY", "ASK", date(2024, 1, 2)),
            make_bi5([(60, 145123, 145130, 145100, 145150, 2.0)]),
        )
        self.assertAlmostEqual(frame["open"][0], 145.123)
        self.assertAlmostEqual(frame["close"][0], 145.130)

    def test_preserves_abnormal_quote_values_for_quality_layer(self) -> None:
        frame = decode_bi5_day(
            RawChunkKey("EURUSD", "BID", date(2024, 1, 2)),
            make_bi5([(0, 0, 1, 0, 2, math.inf)]),
        )
        self.assertEqual(frame["open"][0], 0.0)
        self.assertTrue(math.isinf(frame["volume"][0]))

    def test_rejects_invalid_lzma(self) -> None:
        with self.assertRaisesRegex(Phase2DecodeError, "LZMA"):
            decode_bi5_day(
                RawChunkKey("EURUSD", "BID", date(2024, 1, 2)),
                b"not-lzma",
            )

    def test_rejects_non_record_aligned_payload(self) -> None:
        with self.assertRaisesRegex(Phase2DecodeError, "24 bytes"):
            decode_bi5_day(
                RawChunkKey("EURUSD", "BID", date(2024, 1, 2)),
                lzma.compress(b"x" * 25),
            )

    def test_rejects_duplicate_or_non_increasing_offsets(self) -> None:
        rows = [
            (60, 110000, 110010, 109990, 110020, 1.0),
            (60, 110010, 110020, 110000, 110030, 1.0),
        ]
        with self.assertRaisesRegex(Phase2DecodeError, "strictly increasing"):
            decode_bi5_day(
                RawChunkKey("EURUSD", "BID", date(2024, 1, 2)),
                make_bi5(rows),
            )

    def test_rejects_out_of_day_offset(self) -> None:
        with self.assertRaisesRegex(Phase2DecodeError, "strictly increasing"):
            decode_bi5_day(
                RawChunkKey("EURUSD", "BID", date(2024, 1, 2)),
                make_bi5([(86_400, 110000, 110010, 109990, 110020, 1.0)]),
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
