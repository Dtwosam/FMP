from __future__ import annotations

import lzma
import struct
import unittest
from datetime import date

from fmp.data.phase2.normalize import normalize_day
from fmp.data.phase2.raw_reader import RawChunkReader
from fmp.data.phase2.schema import CANONICAL_COLUMNS
from fmp.data.types import RawChunkKey


def make_bi5(open_i: int) -> bytes:
    return lzma.compress(struct.pack(">IIIIIf", 0, open_i, open_i + 1, open_i - 1, open_i + 2, 1.0))


class MemoryRawChunkReader:
    def __init__(self, bodies: dict[RawChunkKey, bytes | None]) -> None:
        self._bodies = bodies

    def read(self, key: RawChunkKey) -> bytes | None:
        return self._bodies[key]


class Phase2NormalizeDayTests(unittest.TestCase):
    def test_normalize_day_consumes_raw_chunk_reader_protocol(self) -> None:
        day = date(2024, 1, 2)
        reader: RawChunkReader = MemoryRawChunkReader(
            {
                RawChunkKey("EURUSD", "BID", day): make_bi5(110000),
                RawChunkKey("EURUSD", "ASK", day): make_bi5(110020),
            }
        )
        frame = normalize_day(reader, "EURUSD", day)
        self.assertEqual(frame.height, 1)
        self.assertEqual(frame.columns, list(CANONICAL_COLUMNS))
        self.assertAlmostEqual(frame["bid_open"][0], 1.1)
        self.assertAlmostEqual(frame["ask_open"][0], 1.1002)


if __name__ == "__main__":
    unittest.main()
