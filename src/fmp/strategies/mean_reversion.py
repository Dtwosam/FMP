from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import math
from typing import Sequence

from fmp.contracts import QuoteBar


_TIMEFRAME_MINUTES = {"5m": 5, "15m": 15, "1h": 60}
_ALLOWED_LOOKBACK_HOURS = frozenset({4, 8, 16})
_ALLOWED_THRESHOLDS = frozenset({1.5, 2.0})


@dataclass(frozen=True, slots=True)
class MeanReversionConfig:
    lookback_hours: int
    threshold_sigma: float
    timeframe: str

    def __post_init__(self) -> None:
        if self.lookback_hours not in _ALLOWED_LOOKBACK_HOURS:
            raise ValueError("lookback_hours must be one of 4, 8, or 16")
        if self.threshold_sigma not in _ALLOWED_THRESHOLDS:
            raise ValueError("threshold_sigma must be one of 1.5 or 2.0")
        if self.timeframe not in _TIMEFRAME_MINUTES:
            raise ValueError("timeframe must be one of 5m, 15m, or 1h")


def duration_to_bars(timeframe: str, hours: int) -> int:
    try:
        width_minutes = _TIMEFRAME_MINUTES[timeframe]
    except KeyError as exc:
        raise ValueError("timeframe must be one of 5m, 15m, or 1h") from exc
    if hours not in _ALLOWED_LOOKBACK_HOURS:
        raise ValueError("hours must be one of 4, 8, or 16")
    duration_minutes = hours * 60
    if duration_minutes % width_minutes:
        raise ValueError("duration must be exactly divisible by timeframe width")
    return duration_minutes // width_minutes


def _midpoint_close(bar: QuoteBar) -> float:
    return (bar.bid_close + bar.ask_close) / 2.0


def rolling_reference(
    bars: Sequence[QuoteBar],
    *,
    observation_index: int,
    lookback_count: int,
    width: timedelta,
) -> tuple[float, float] | None:
    if lookback_count <= 0:
        raise ValueError("lookback_count must be positive")
    if width <= timedelta(0):
        raise ValueError("width must be positive")
    if observation_index < 0 or observation_index >= len(bars):
        return None

    start = observation_index - lookback_count
    if start < 0:
        return None
    required = bars[start : observation_index + 1]
    if len(required) != lookback_count + 1:
        return None
    if any(
        current.timestamp_utc - previous.timestamp_utc != width
        for previous, current in zip(required, required[1:])
    ):
        return None

    values = tuple(_midpoint_close(bar) for bar in required[:-1])
    if len(values) != lookback_count or any(not math.isfinite(value) for value in values):
        return None

    mean = sum(values) / lookback_count
    variance = sum((value - mean) ** 2 for value in values) / lookback_count
    if not math.isfinite(mean) or not math.isfinite(variance) or variance <= 0.0:
        return None
    std = math.sqrt(variance)
    if not math.isfinite(std) or std <= 0.0:
        return None
    return mean, std


def z_score_against_reference(value: float, mean: float, std: float) -> float:
    if not all(math.isfinite(item) for item in (value, mean, std)) or std <= 0.0:
        raise ValueError("value and mean must be finite and std must be positive and finite")
    return (value - mean) / std
