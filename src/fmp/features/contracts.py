from __future__ import annotations

from datetime import date, timedelta

FEATURE_SET_VERSION = "fmp-feature-v1"
PROCESSED_SCHEMA_VERSION = "fmp-canonical-1m-v1"
SOURCE_START_INCLUSIVE = date(2015, 1, 1)
FINAL_SOURCE_END_EXCLUSIVE = date(2024, 1, 1)
SUPPORTED_SYMBOLS = ("EURUSD", "GBPUSD", "USDJPY")
SUPPORTED_TIMEFRAMES = ("5m", "15m", "1h")
TIMEFRAME_MINUTES = {"5m": 5, "15m": 15, "1h": 60}
PIP_SIZES = {"EURUSD": 0.0001, "GBPUSD": 0.0001, "USDJPY": 0.01}


def validate_symbol(symbol: str) -> str:
    if symbol not in SUPPORTED_SYMBOLS:
        raise ValueError(f"unsupported Phase 5 symbol: {symbol}")
    return symbol


def validate_timeframe(timeframe: str) -> str:
    if timeframe not in SUPPORTED_TIMEFRAMES:
        raise ValueError(f"unsupported Phase 5 timeframe: {timeframe}")
    return timeframe


def timeframe_minutes(timeframe: str) -> int:
    validate_timeframe(timeframe)
    return TIMEFRAME_MINUTES[timeframe]


def timeframe_delta(timeframe: str) -> timedelta:
    return timedelta(minutes=timeframe_minutes(timeframe))


def pip_size(symbol: str) -> float:
    validate_symbol(symbol)
    return PIP_SIZES[symbol]


def validate_source_range(start: date, end_exclusive: date) -> None:
    if start >= end_exclusive:
        raise ValueError("Phase 5 source range must be non-empty")
    if start < SOURCE_START_INCLUSIVE:
        raise ValueError("Phase 5 source coverage may not start before 2015-01-01")
    if end_exclusive > FINAL_SOURCE_END_EXCLUSIVE:
        raise ValueError(
            "Phase 5 final-test lock: source coverage may not reach 2024-01-01 or later"
        )
