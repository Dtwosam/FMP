from __future__ import annotations

from datetime import datetime, timedelta

import polars as pl

CANONICAL_SCHEMA_VERSION = "fmp-canonical-1m-v1"
DERIVED_SCHEMA_VERSION = "fmp-derived-bars-v1"
INGESTION_VERSION = "dukascopy-bi5-candles-v1"
SOURCE = "dukascopy"

PRICE_DIVISORS = {
    "EURUSD": 100_000,
    "GBPUSD": 100_000,
    "USDJPY": 1_000,
}

DECODED_SIDE_COLUMNS = (
    "timestamp_utc",
    "symbol",
    "side",
    "open",
    "high",
    "low",
    "close",
    "volume",
)

CANONICAL_COLUMNS = (
    "timestamp_utc",
    "symbol",
    "bid_open",
    "bid_high",
    "bid_low",
    "bid_close",
    "ask_open",
    "ask_high",
    "ask_low",
    "ask_close",
    "bid_volume",
    "ask_volume",
    "source",
    "ingestion_version",
    "schema_version",
)

_CANONICAL_FLOAT_COLUMNS = (
    "bid_open",
    "bid_high",
    "bid_low",
    "bid_close",
    "ask_open",
    "ask_high",
    "ask_low",
    "ask_close",
    "bid_volume",
    "ask_volume",
)


def validate_canonical_frame(frame: pl.DataFrame) -> None:
    if tuple(frame.columns) != CANONICAL_COLUMNS:
        raise ValueError("canonical frame columns do not match fmp-canonical-1m-v1")

    for column in _CANONICAL_FLOAT_COLUMNS:
        if frame.schema[column] != pl.Float64:
            raise ValueError(f"canonical frame {column} must be Float64")

    for timestamp in frame["timestamp_utc"].to_list():
        if (
            not isinstance(timestamp, datetime)
            or timestamp.tzinfo is None
            or timestamp.utcoffset() != timedelta(0)
        ):
            raise ValueError("canonical frame timestamp_utc must use UTC")

    identities = {
        "source": SOURCE,
        "ingestion_version": INGESTION_VERSION,
        "schema_version": CANONICAL_SCHEMA_VERSION,
    }
    for column, expected in identities.items():
        if frame[column].null_count() != 0:
            raise ValueError(f"canonical frame {column} must not contain nulls")
        values = set(frame[column].cast(pl.String).unique().to_list())
        if values and values != {expected}:
            raise ValueError(
                f"canonical frame {column} must be {expected!r}, got {sorted(values)!r}"
            )

    if frame["symbol"].null_count() != 0:
        raise ValueError("canonical frame symbol must not contain nulls")
    symbols = set(frame["symbol"].cast(pl.String).unique().to_list())
    unsupported = symbols.difference(PRICE_DIVISORS)
    if unsupported:
        raise ValueError(f"canonical frame contains unsupported symbols: {sorted(unsupported)}")
