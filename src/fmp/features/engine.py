from __future__ import annotations

import polars as pl

from .base import prepare_base_frame
from .location import add_location_features
from .numeric import add_numeric_features
from .schema import FEATURE_COLUMNS
from .sessions import add_session_features
from .spread import add_spread_features


def build_feature_frame(
    source: pl.DataFrame,
    *,
    symbol: str,
    timeframe: str,
    processed_manifest_sha256: str,
) -> pl.DataFrame:
    frame = prepare_base_frame(
        source,
        symbol=symbol,
        timeframe=timeframe,
        processed_manifest_sha256=processed_manifest_sha256,
    )
    frame = add_numeric_features(frame)
    frame = add_session_features(frame)
    frame = add_location_features(frame)
    frame = add_spread_features(frame)
    out = frame.select(list(FEATURE_COLUMNS)).sort(["symbol", "timeframe", "bar_start_utc"])
    unique = out.select(pl.struct(["symbol", "timeframe", "bar_start_utc"]).n_unique()).item()
    if unique != out.height:
        raise ValueError("duplicate Phase 5 feature identity")
    return out
