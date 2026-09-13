from __future__ import annotations

import polars as pl

from .schema import (
    CANONICAL_COLUMNS,
    CANONICAL_SCHEMA_VERSION,
    INGESTION_VERSION,
    SOURCE,
)

_SIDE_VALUE_COLUMNS = ("open", "high", "low", "close", "volume")


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
