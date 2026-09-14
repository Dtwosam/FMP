from __future__ import annotations

import math

import polars as pl

from .contracts import timeframe_minutes


def _bars(timeframe: str, hours: int) -> int:
    minutes = timeframe_minutes(timeframe)
    total = hours * 60
    if total % minutes:
        raise ValueError(f"duration {hours}h is not divisible by {timeframe}")
    return total // minutes


def _finite(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _cadence_streak(frame: pl.DataFrame, *, timeframe: str) -> list[int]:
    delta_seconds = timeframe_minutes(timeframe) * 60
    timestamps = frame["bar_start_utc"].to_list()
    complete = frame["is_complete"].to_list()
    opens = frame["mid_open"].to_list()
    highs = frame["mid_high"].to_list()
    lows = frame["mid_low"].to_list()
    closes = frame["mid_close"].to_list()
    streak: list[int] = []
    for i, ts in enumerate(timestamps):
        valid = bool(complete[i]) and all(
            _finite(value) for value in (opens[i], highs[i], lows[i], closes[i])
        )
        if not valid:
            streak.append(0)
            continue
        if i == 0 or streak[i - 1] == 0:
            streak.append(1)
            continue
        gap = (ts - timestamps[i - 1]).total_seconds()
        streak.append(streak[i - 1] + 1 if gap == delta_seconds else 1)
    return streak


def _directional_streak(frame: pl.DataFrame, valid_streak: list[int]) -> tuple[list[int | None], list[int | None]]:
    opens = frame["mid_open"].to_list()
    closes = frame["mid_close"].to_list()
    directions: list[int | None] = []
    streaks: list[int | None] = []
    previous_direction: int | None = None
    previous_streak = 0
    for i, (open_, close) in enumerate(zip(opens, closes)):
        if valid_streak[i] == 0:
            directions.append(None)
            streaks.append(None)
            previous_direction = None
            previous_streak = 0
            continue
        direction = 1 if close > open_ else (-1 if close < open_ else 0)
        directions.append(direction)
        if direction == 0:
            streaks.append(0)
            previous_direction = None
            previous_streak = 0
        else:
            current = previous_streak + 1 if direction == previous_direction else 1
            current = min(current, 20)
            streaks.append(current)
            previous_direction = direction
            previous_streak = current
    return directions, streaks


def add_numeric_features(frame: pl.DataFrame) -> pl.DataFrame:
    if frame.is_empty():
        return frame
    timeframes = set(frame["timeframe"].to_list())
    if len(timeframes) != 1:
        raise ValueError("numeric features require exactly one timeframe")
    timeframe = next(iter(timeframes))
    streak = _cadence_streak(frame, timeframe=timeframe)
    directions, direction_streaks = _directional_streak(frame, streak)
    out = frame.with_columns(
        pl.Series("_cadence_streak", streak, dtype=pl.Int64),
        pl.Series("candle_direction", directions, dtype=pl.Int64),
        pl.Series("directional_streak", direction_streaks, dtype=pl.Int64),
    )

    n1 = _bars(timeframe, 1)
    n2 = _bars(timeframe, 2)
    n4 = _bars(timeframe, 4)
    n8 = _bars(timeframe, 8)
    n24 = _bars(timeframe, 24)
    valid = pl.col("_cadence_streak") > 0
    close = pl.col("mid_close")
    high = pl.col("mid_high")
    low = pl.col("mid_low")
    open_ = pl.col("mid_open")
    pip = pl.col("pip_size")

    return_1bar_raw = close / close.shift(1) - 1.0
    log_return_raw = (close / close.shift(1)).log()
    range_raw = (high - low) / pip
    true_range_raw = pl.max_horizontal(
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs(),
    ) / pip
    sma2_raw = close.rolling_mean(window_size=n2)
    sma8_raw = close.rolling_mean(window_size=n8)
    roc4_raw = close / close.shift(n4) - 1.0
    roc8_raw = close / close.shift(n8) - 1.0
    body_raw = (close - open_).abs() / pip
    upper_raw = (high - pl.max_horizontal(open_, close)) / pip
    lower_raw = (pl.min_horizontal(open_, close) - low) / pip
    candle_range = high - low

    out = out.with_columns(
        pl.when(pl.col("_cadence_streak") >= 2).then(return_1bar_raw).otherwise(None).alias("return_1bar"),
        pl.when(pl.col("_cadence_streak") >= n1 + 1).then(close / close.shift(n1) - 1.0).otherwise(None).alias("return_1h"),
        pl.when(pl.col("_cadence_streak") >= n24 + 1).then(close / close.shift(n24) - 1.0).otherwise(None).alias("return_24h"),
        pl.when(pl.col("_cadence_streak") >= 2).then(log_return_raw).otherwise(None).alias("log_return_1bar"),
        pl.when(valid).then(range_raw).otherwise(None).alias("range_pips"),
        pl.when(pl.col("_cadence_streak") >= 2).then(true_range_raw).otherwise(None).alias("true_range_pips"),
        pl.when(valid).then(body_raw).otherwise(None).alias("body_pips"),
        pl.when(valid).then(upper_raw).otherwise(None).alias("upper_wick_pips"),
        pl.when(valid).then(lower_raw).otherwise(None).alias("lower_wick_pips"),
        pl.when(valid & (candle_range > 0)).then((close - open_).abs() / candle_range).otherwise(None).alias("body_to_range"),
        pl.when(valid & (candle_range > 0)).then((close - low) / candle_range).otherwise(None).alias("close_location"),
        pl.when((pl.col("_cadence_streak") >= n2)).then((close - sma2_raw) / pip).otherwise(None).alias("sma_distance_2h_pips"),
        pl.when((pl.col("_cadence_streak") >= n8)).then((close - sma8_raw) / pip).otherwise(None).alias("sma_distance_8h_pips"),
        pl.when((pl.col("_cadence_streak") >= n2 + 1)).then((sma2_raw - sma2_raw.shift(1)) / pip).otherwise(None).alias("sma_slope_2h_pips"),
        pl.when((pl.col("_cadence_streak") >= n8 + 1)).then((sma8_raw - sma8_raw.shift(1)) / pip).otherwise(None).alias("sma_slope_8h_pips"),
        pl.when(pl.col("_cadence_streak") >= n4 + 1).then(roc4_raw).otherwise(None).alias("roc_4h"),
        pl.when(pl.col("_cadence_streak") >= n8 + 1).then(roc8_raw).otherwise(None).alias("roc_8h"),
        pl.when(pl.col("_cadence_streak") >= (2 * n4) + 1).then(roc4_raw - roc4_raw.shift(n4)).otherwise(None).alias("momentum_accel_4h"),
    )

    # Rolling calculations use row-count windows only after the exact-cadence
    # streak has proved those rows represent the complete requested duration.
    log_sq = (pl.col("log_return_1bar") ** 2)
    prior_range = pl.col("range_pips").shift(1)
    prior_high = high.shift(1)
    prior_low = low.shift(1)
    prior_median = prior_range.rolling_median(window_size=n8)
    prior_high_max = prior_high.rolling_max(window_size=n8)
    prior_low_min = prior_low.rolling_min(window_size=n8)
    out = out.with_columns(
        pl.when(pl.col("_cadence_streak") >= n1 + 1)
        .then(log_sq.rolling_sum(window_size=n1).sqrt())
        .otherwise(None)
        .alias("realized_vol_1h"),
        pl.when(pl.col("_cadence_streak") >= n8 + 1)
        .then(log_sq.rolling_sum(window_size=n8).sqrt())
        .otherwise(None)
        .alias("realized_vol_8h"),
        pl.when(pl.col("_cadence_streak") >= n24 + 1)
        .then(log_sq.rolling_sum(window_size=n24).sqrt())
        .otherwise(None)
        .alias("realized_vol_24h"),
        pl.when((pl.col("_cadence_streak") >= n8 + 1) & (prior_median > 0))
        .then(pl.col("range_pips") / prior_median)
        .otherwise(None)
        .alias("range_vs_prior_median_8h"),
        pl.when(pl.col("_cadence_streak") >= n8 + 1)
        .then((close > prior_high_max).cast(pl.Int64))
        .otherwise(None)
        .alias("breakout_above_prior_8h"),
        pl.when(pl.col("_cadence_streak") >= n8 + 1)
        .then((close < prior_low_min).cast(pl.Int64))
        .otherwise(None)
        .alias("breakout_below_prior_8h"),
    )
    return out.drop("_cadence_streak")
