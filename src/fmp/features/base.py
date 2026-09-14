from __future__ import annotations

import math

import polars as pl

from .contracts import FEATURE_SET_VERSION, pip_size, timeframe_delta, validate_symbol, validate_timeframe

_REQUIRED_COLUMNS = (
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
    "source_minutes",
    "expected_open_minutes",
    "is_complete",
    "timeframe",
    "schema_version",
)


def prepare_base_frame(
    frame: pl.DataFrame,
    *,
    symbol: str,
    timeframe: str,
    processed_manifest_sha256: str,
) -> pl.DataFrame:
    validate_symbol(symbol)
    validate_timeframe(timeframe)
    if len(processed_manifest_sha256) != 64:
        raise ValueError("processed manifest sha256 must be 64 hex characters")
    try:
        int(processed_manifest_sha256, 16)
    except ValueError as exc:
        raise ValueError("processed manifest sha256 must be hexadecimal") from exc
    missing = [name for name in _REQUIRED_COLUMNS if name not in frame.columns]
    if missing:
        raise ValueError(f"Phase 5 source frame missing required columns: {missing}")
    if frame.is_empty():
        raise ValueError("Phase 5 source frame is empty")
    symbols = set(frame["symbol"].to_list())
    if symbols != {symbol}:
        raise ValueError(f"Phase 5 source symbol mismatch: {sorted(symbols)} != {symbol}")
    timeframes = set(frame["timeframe"].to_list())
    if timeframes != {timeframe}:
        raise ValueError(f"Phase 5 source timeframe mismatch: {sorted(timeframes)} != {timeframe}")
    if frame.select(pl.col("timestamp_utc").is_duplicated().any()).item():
        raise ValueError("duplicate Phase 5 source timestamp")

    delta = timeframe_delta(timeframe)
    pip = pip_size(symbol)
    out = frame.sort("timestamp_utc").rename({"timestamp_utc": "bar_start_utc"})
    out = out.with_columns(
        ((pl.col("bid_open") + pl.col("ask_open")) / 2.0).alias("mid_open"),
        ((pl.col("bid_high") + pl.col("ask_high")) / 2.0).alias("mid_high"),
        ((pl.col("bid_low") + pl.col("ask_low")) / 2.0).alias("mid_low"),
        ((pl.col("bid_close") + pl.col("ask_close")) / 2.0).alias("mid_close"),
        (pl.col("bar_start_utc") + pl.duration(minutes=int(delta.total_seconds() // 60))).alias("bar_end_utc"),
        pl.lit(pip).alias("pip_size"),
        pl.lit(FEATURE_SET_VERSION).alias("feature_set_version"),
        pl.lit(processed_manifest_sha256).alias("processed_manifest_sha256"),
    ).with_columns(pl.col("bar_end_utc").alias("available_at_utc"))
    return out
