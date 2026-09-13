from __future__ import annotations

import lzma
import struct
from datetime import datetime, time, timedelta, timezone

import polars as pl

from fmp.data.types import RawChunkKey

from .schema import DECODED_SIDE_COLUMNS, PRICE_DIVISORS

_RECORD = struct.Struct(">IIIIIf")


class Phase2DecodeError(ValueError):
    pass


def decode_bi5_day(key: RawChunkKey, body: bytes) -> pl.DataFrame:
    try:
        payload = lzma.decompress(body)
    except lzma.LZMAError as exc:
        raise Phase2DecodeError("invalid BI5 LZMA payload") from exc

    if not payload or len(payload) % _RECORD.size != 0:
        raise Phase2DecodeError("BI5 payload is not a non-zero multiple of 24 bytes")

    divisor = PRICE_DIVISORS[key.pair]
    day_start = datetime.combine(key.day, time.min, tzinfo=timezone.utc)
    rows: list[tuple[object, ...]] = []
    previous_seconds = -1

    for offset in range(0, len(payload), _RECORD.size):
        seconds, open_i, close_i, low_i, high_i, volume = _RECORD.unpack_from(payload, offset)
        if seconds >= 86_400 or seconds <= previous_seconds:
            raise Phase2DecodeError(
                "BI5 second offsets must be strictly increasing within the UTC day"
            )
        previous_seconds = seconds
        rows.append(
            (
                day_start + timedelta(seconds=seconds),
                key.pair,
                key.side,
                open_i / divisor,
                high_i / divisor,
                low_i / divisor,
                close_i / divisor,
                float(volume),
            )
        )

    schema = {
        "timestamp_utc": pl.Datetime(time_unit="us", time_zone="UTC"),
        "symbol": pl.String,
        "side": pl.String,
        "open": pl.Float64,
        "high": pl.Float64,
        "low": pl.Float64,
        "close": pl.Float64,
        "volume": pl.Float64,
    }
    frame = pl.DataFrame(rows, schema=schema, orient="row")
    return frame.select(list(DECODED_SIDE_COLUMNS))
