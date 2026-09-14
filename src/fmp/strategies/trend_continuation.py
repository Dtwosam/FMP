from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Sequence

from fmp.contracts import Direction, QuoteBar


_TIMEFRAME_MINUTES = {"5m": 5, "15m": 15, "1h": 60}
_TREND_WINDOWS = {"A": (2, 8), "B": (4, 16), "C": (8, 32)}
_ALLOWED_TARGET_R = frozenset({1.0, 1.5})


@dataclass(frozen=True, slots=True)
class TrendContinuationConfig:
    trend_window_id: str
    target_r_multiple: float
    timeframe: str

    def __post_init__(self) -> None:
        if self.trend_window_id not in _TREND_WINDOWS:
            raise ValueError("trend_window_id must be one of A, B, or C")
        if self.target_r_multiple not in _ALLOWED_TARGET_R:
            raise ValueError("target_r_multiple must be one of 1.0 or 1.5")
        if self.timeframe not in _TIMEFRAME_MINUTES:
            raise ValueError("timeframe must be one of 5m, 15m, or 1h")


def duration_to_bars(timeframe: str, hours: int) -> int:
    try:
        width_minutes = _TIMEFRAME_MINUTES[timeframe]
    except KeyError as exc:
        raise ValueError("timeframe must be one of 5m, 15m, or 1h") from exc
    if not isinstance(hours, int) or isinstance(hours, bool) or hours <= 0:
        raise ValueError("hours must be a positive integer")
    duration_minutes = hours * 60
    if duration_minutes % width_minutes:
        raise ValueError("duration must be exactly divisible by timeframe width")
    return duration_minutes // width_minutes


def _midpoint_close(bar: QuoteBar) -> float:
    return (bar.bid_close + bar.ask_close) / 2.0


def _trend_context(
    bars: Sequence[QuoteBar],
    *,
    end_index: int,
    fast_count: int,
    slow_count: int,
    width: timedelta,
) -> Direction | None:
    if fast_count <= 0 or slow_count <= 0 or fast_count > slow_count:
        raise ValueError("SMA counts must be positive with fast_count <= slow_count")
    if width <= timedelta(0):
        raise ValueError("width must be positive")
    if end_index < 0 or end_index >= len(bars):
        return None

    first_required = end_index - slow_count
    if first_required < 0:
        return None
    required = bars[first_required : end_index + 1]
    if len(required) != slow_count + 1:
        return None
    if any(
        current.timestamp_utc - previous.timestamp_utc != width
        for previous, current in zip(required, required[1:])
    ):
        return None

    current_fast = bars[end_index - fast_count + 1 : end_index + 1]
    current_slow = bars[end_index - slow_count + 1 : end_index + 1]
    previous_slow = bars[end_index - slow_count : end_index]

    fast_sma = sum(_midpoint_close(bar) for bar in current_fast) / fast_count
    slow_sma = sum(_midpoint_close(bar) for bar in current_slow) / slow_count
    previous_slow_sma = sum(_midpoint_close(bar) for bar in previous_slow) / slow_count

    if fast_sma > slow_sma and slow_sma > previous_slow_sma:
        return Direction.LONG
    if fast_sma < slow_sma and slow_sma < previous_slow_sma:
        return Direction.SHORT
    return None
