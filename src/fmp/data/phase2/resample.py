from __future__ import annotations

from datetime import datetime, timedelta
from typing import Literal

import polars as pl

from .market_hours import is_market_open_minute
from .schema import DERIVED_SCHEMA_VERSION

Timeframe = Literal["5m", "15m", "1h"]

_TIMEFRAME_MINUTES: dict[str, int] = {
    "5m": 5,
    "15m": 15,
    "1h": 60,
}

_DERIVED_COLUMNS = (
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
    "source_minutes",
    "expected_open_minutes",
    "is_complete",
    "timeframe",
    "schema_version",
)


def _expected_open_minutes(bucket_start: datetime, width_minutes: int) -> int:
    return sum(
        1
        for offset in range(width_minutes)
        if is_market_open_minute(bucket_start + timedelta(minutes=offset))
    )


def _volume_sum(column: str) -> pl.Expr:
    return (
        pl.when(pl.col(column).count() > 0)
        .then(pl.col(column).sum())
        .otherwise(pl.lit(None, dtype=pl.Float64))
        .alias(column)
    )


def resample_canonical(frame: pl.DataFrame, timeframe: Timeframe) -> pl.DataFrame:
    width_minutes = _TIMEFRAME_MINUTES.get(timeframe)
    if width_minutes is None:
        raise ValueError(f"unsupported Phase 2 timeframe: {timeframe}")

    both_sides = pl.all_horizontal(
        [
            pl.col(f"{side}_{field}").is_not_null()
            for side in ("bid", "ask")
            for field in ("open", "high", "low", "close")
        ]
    ).alias("_both_sides")

    source = frame.sort("symbol", "timestamp_utc").with_columns(both_sides)
    grouped = (
        source.group_by_dynamic(
            "timestamp_utc",
            every=timeframe,
            period=timeframe,
            closed="left",
            label="left",
            group_by="symbol",
        )
        .agg(
            pl.col("bid_open").drop_nulls().first().alias("bid_open"),
            pl.col("bid_high").drop_nulls().max().alias("bid_high"),
            pl.col("bid_low").drop_nulls().min().alias("bid_low"),
            pl.col("bid_close").drop_nulls().last().alias("bid_close"),
            pl.col("ask_open").drop_nulls().first().alias("ask_open"),
            pl.col("ask_high").drop_nulls().max().alias("ask_high"),
            pl.col("ask_low").drop_nulls().min().alias("ask_low"),
            pl.col("ask_close").drop_nulls().last().alias("ask_close"),
            _volume_sum("bid_volume"),
            _volume_sum("ask_volume"),
            pl.col("timestamp_utc").n_unique().alias("source_minutes"),
            pl.col("_both_sides").sum().alias("_both_sides_minutes"),
        )
        .sort("symbol", "timestamp_utc")
    )

    out = grouped.with_columns(
        pl.col("timestamp_utc")
        .map_elements(
            lambda value: _expected_open_minutes(value, width_minutes),
            return_dtype=pl.Int64,
        )
        .alias("expected_open_minutes"),
        pl.lit(timeframe).alias("timeframe"),
        pl.lit(DERIVED_SCHEMA_VERSION).alias("schema_version"),
    ).with_columns(
        (
            (pl.col("source_minutes") == pl.col("expected_open_minutes"))
            & (pl.col("_both_sides_minutes") == pl.col("source_minutes"))
        ).alias("is_complete")
    )

    return out.select(list(_DERIVED_COLUMNS))
