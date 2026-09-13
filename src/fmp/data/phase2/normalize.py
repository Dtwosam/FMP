from __future__ import annotations

from datetime import date

import polars as pl

from fmp.data.types import Pair, RawChunkKey

from .bi5 import decode_bi5_day
from .raw_reader import RawChunkReader
from .schema import (
    CANONICAL_COLUMNS,
    CANONICAL_SCHEMA_VERSION,
    INGESTION_VERSION,
    SOURCE,
)

_SIDE_VALUE_COLUMNS = ("open", "high", "low", "close", "volume")


def _empty_canonical_frame() -> pl.DataFrame:
    return pl.DataFrame(
        schema={
            "timestamp_utc": pl.Datetime(time_unit="us", time_zone="UTC"),
            "symbol": pl.String,
            "bid_open": pl.Float64,
            "bid_high": pl.Float64,
            "bid_low": pl.Float64,
            "bid_close": pl.Float64,
            "ask_open": pl.Float64,
            "ask_high": pl.Float64,
            "ask_low": pl.Float64,
            "ask_close": pl.Float64,
            "bid_volume": pl.Float64,
            "ask_volume": pl.Float64,
            "source": pl.String,
            "ingestion_version": pl.String,
            "schema_version": pl.String,
        }
    ).select(list(CANONICAL_COLUMNS))


def _prepare_side(frame: pl.DataFrame | None, side: str) -> pl.DataFrame | None:
    if frame is None:
        return None
    expected_side = side.upper()
    if frame.is_empty():
        return frame.select(["timestamp_utc", "symbol"]).with_columns(
            *[pl.lit(None, dtype=pl.Float64).alias(f"{side.lower()}_{name}") for name in _SIDE_VALUE_COLUMNS]
        )
    sides = frame["side"].unique().to_list()
    if sides != [expected_side]:
        raise ValueError(f"decoded frame must contain only {expected_side} rows")
    identity = frame.select(["symbol", "timestamp_utc"])
    if identity.unique().height != identity.height:
        raise ValueError(
            f"decoded {expected_side} frame contains duplicate symbol/timestamp rows"
        )
    rename = {name: f"{side.lower()}_{name}" for name in _SIDE_VALUE_COLUMNS}
    return frame.drop("side").rename(rename)


def normalize_decoded_sides(
    bid: pl.DataFrame | None,
    ask: pl.DataFrame | None,
) -> pl.DataFrame:
    bid_frame = _prepare_side(bid, "BID")
    ask_frame = _prepare_side(ask, "ASK")
    if bid_frame is None and ask_frame is None:
        raise ValueError("at least one decoded side is required")

    if bid_frame is None:
        joined = ask_frame
        assert joined is not None
        for name in _SIDE_VALUE_COLUMNS:
            joined = joined.with_columns(pl.lit(None, dtype=pl.Float64).alias(f"bid_{name}"))
    elif ask_frame is None:
        joined = bid_frame
        for name in _SIDE_VALUE_COLUMNS:
            joined = joined.with_columns(pl.lit(None, dtype=pl.Float64).alias(f"ask_{name}"))
    else:
        joined = bid_frame.join(
            ask_frame,
            on=["timestamp_utc", "symbol"],
            how="full",
            coalesce=True,
        )

    joined = joined.with_columns(
        pl.lit(SOURCE).alias("source"),
        pl.lit(INGESTION_VERSION).alias("ingestion_version"),
        pl.lit(CANONICAL_SCHEMA_VERSION).alias("schema_version"),
    )
    return joined.select(list(CANONICAL_COLUMNS)).sort(["symbol", "timestamp_utc"])


def normalize_day(reader: RawChunkReader, pair: Pair, day: date) -> pl.DataFrame:
    bid_key = RawChunkKey(pair, "BID", day)
    ask_key = RawChunkKey(pair, "ASK", day)
    bid_body = reader.read(bid_key)
    ask_body = reader.read(ask_key)

    if bid_body is None and ask_body is None:
        return _empty_canonical_frame()

    bid = None if bid_body is None else decode_bi5_day(bid_key, bid_body)
    ask = None if ask_body is None else decode_bi5_day(ask_key, ask_body)
    return normalize_decoded_sides(bid, ask)
