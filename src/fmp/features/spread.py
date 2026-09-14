from __future__ import annotations

import bisect
import math
from collections import deque

import polars as pl

from .contracts import timeframe_minutes


def _bars(timeframe: str, hours: int) -> int:
    return hours * 60 // timeframe_minutes(timeframe)


def _finite(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _spread_state(frame: pl.DataFrame) -> tuple[list[float | None], list[int]]:
    timeframe = str(frame["timeframe"][0])
    delta_seconds = timeframe_minutes(timeframe) * 60
    timestamps = frame["bar_start_utc"].to_list()
    complete = frame["is_complete"].to_list()
    bids = frame["bid_close"].to_list()
    asks = frame["ask_close"].to_list()
    pips = frame["pip_size"].to_list()
    spreads: list[float | None] = []
    streak: list[int] = []
    for i, ts in enumerate(timestamps):
        valid = bool(complete[i]) and all(_finite(v) for v in (bids[i], asks[i], pips[i]))
        spread = (float(asks[i]) - float(bids[i])) / float(pips[i]) if valid else None
        spreads.append(spread)
        if not valid:
            streak.append(0)
        elif i > 0 and streak[i - 1] > 0 and (ts - timestamps[i - 1]).total_seconds() == delta_seconds:
            streak.append(streak[i - 1] + 1)
        else:
            streak.append(1)
    return spreads, streak


def _prior_percentile(
    spreads: list[float | None], streak: list[int], *, window: int
) -> list[float | None]:
    ordered: list[float] = []
    queue: deque[float] = deque()
    result: list[float | None] = []
    for i, value in enumerate(spreads):
        if value is None or streak[i] == 0:
            ordered.clear()
            queue.clear()
            result.append(None)
            continue
        if i == 0 or streak[i] == 1:
            ordered.clear()
            queue.clear()
        if len(queue) == window:
            result.append(bisect.bisect_right(ordered, value) / window)
        else:
            result.append(None)
        bisect.insort(ordered, value)
        queue.append(value)
        if len(queue) > window:
            old = queue.popleft()
            pos = bisect.bisect_left(ordered, old)
            ordered.pop(pos)
    return result


def add_spread_features(frame: pl.DataFrame) -> pl.DataFrame:
    if frame.is_empty():
        return frame
    timeframe = str(frame["timeframe"][0])
    n1 = _bars(timeframe, 1)
    n8 = _bars(timeframe, 8)
    n24 = _bars(timeframe, 24)
    spreads, streak = _spread_state(frame)
    percentile = _prior_percentile(spreads, streak, window=n24)
    out = frame.with_columns(
        pl.Series("spread_close_pips", spreads, dtype=pl.Float64),
        pl.Series("_spread_streak", streak, dtype=pl.Int64),
        pl.Series("spread_percentile_prior_24h", percentile, dtype=pl.Float64),
    )
    spread = pl.col("spread_close_pips")
    prior_median = spread.shift(1).rolling_median(window_size=n8)
    out = out.with_columns(
        pl.when(pl.col("_spread_streak") >= n1)
        .then(spread.rolling_mean(window_size=n1))
        .otherwise(None)
        .alias("spread_mean_1h_pips"),
        pl.when(pl.col("_spread_streak") >= n8 + 1)
        .then(prior_median)
        .otherwise(None)
        .alias("spread_median_prior_8h_pips"),
    ).with_columns(
        pl.when(
            (pl.col("_spread_streak") >= n8 + 1)
            & (pl.col("spread_median_prior_8h_pips") > 0)
        )
        .then(spread / pl.col("spread_median_prior_8h_pips"))
        .otherwise(None)
        .alias("spread_vs_prior_median_8h")
    )
    return out.drop("_spread_streak")
