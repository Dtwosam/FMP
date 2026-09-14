from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from types import MappingProxyType
from typing import Mapping
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fmp.contracts import Direction, SUPPORTED_SYMBOLS


ELIGIBLE_SIGNAL_TIMEFRAMES = frozenset({"5m", "15m", "1h"})


def _require_utc(value: datetime, *, field: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must use UTC")


def _freeze_mapping(value: Mapping[str, object]) -> Mapping[str, object]:
    return MappingProxyType(dict(value))


def _jsonable(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, datetime):
        _require_utc(value, field="serialized datetime")
        return value.isoformat().replace("+00:00", "Z")
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("strategy serialization cannot contain non-finite floats")
        return value
    raise TypeError(f"unsupported strategy serialization type: {type(value).__name__}")


def _stable_json_bytes(value: Mapping[str, object]) -> bytes:
    return json.dumps(
        _jsonable(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


@dataclass(frozen=True, slots=True)
class StrategyConfig:
    family_id: str
    strategy_version: str
    timeframe: str
    parameters: Mapping[str, object]
    timezone_name: str

    def __post_init__(self) -> None:
        for field in ("family_id", "strategy_version", "timezone_name"):
            if not getattr(self, field).strip():
                raise ValueError(f"{field} must be non-empty")
        if self.timeframe not in ELIGIBLE_SIGNAL_TIMEFRAMES:
            raise ValueError(f"unsupported strategy timeframe: {self.timeframe!r}")
        try:
            ZoneInfo(self.timezone_name)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"unknown strategy timezone: {self.timezone_name!r}") from exc
        object.__setattr__(self, "parameters", _freeze_mapping(self.parameters))

    def stable_json_bytes(self) -> bytes:
        return _stable_json_bytes(
            {
                "family_id": self.family_id,
                "strategy_version": self.strategy_version,
                "timeframe": self.timeframe,
                "parameters": self.parameters,
                "timezone_name": self.timezone_name,
            }
        )


@dataclass(frozen=True, slots=True)
class SignalCandidate:
    candidate_id: str
    symbol: str
    observation_bar_timestamp_utc: datetime
    signal_known_timestamp_utc: datetime
    direction: Direction
    stop_price: float | None
    target_price: float | None
    latest_exit_timestamp_utc: datetime | None
    reason_code: str
    metadata: Mapping[str, object]

    def __post_init__(self) -> None:
        if not self.candidate_id.strip():
            raise ValueError("candidate_id must be non-empty")
        if self.symbol not in SUPPORTED_SYMBOLS:
            raise ValueError(f"unsupported symbol: {self.symbol!r}")
        if not self.reason_code.strip():
            raise ValueError("reason_code must be non-empty")
        _require_utc(self.observation_bar_timestamp_utc, field="observation_bar_timestamp_utc")
        _require_utc(self.signal_known_timestamp_utc, field="signal_known_timestamp_utc")
        if self.signal_known_timestamp_utc <= self.observation_bar_timestamp_utc:
            raise ValueError("signal known timestamp must be after observation bar timestamp")

        if self.latest_exit_timestamp_utc is not None:
            _require_utc(self.latest_exit_timestamp_utc, field="latest_exit_timestamp_utc")
            if self.latest_exit_timestamp_utc <= self.signal_known_timestamp_utc:
                raise ValueError("latest exit timestamp must be after signal known timestamp")

        if self.direction is Direction.NO_TRADE:
            if self.stop_price is not None or self.target_price is not None:
                raise ValueError("NO_TRADE candidate cannot define stop or target")
            if self.latest_exit_timestamp_utc is not None:
                raise ValueError("NO_TRADE candidate cannot define a latest exit")
        elif self.direction in {Direction.LONG, Direction.SHORT}:
            if self.stop_price is None or not math.isfinite(self.stop_price) or self.stop_price <= 0:
                raise ValueError("directional candidate requires a finite positive stop price")
            if self.target_price is not None and (
                not math.isfinite(self.target_price) or self.target_price <= 0
            ):
                raise ValueError("target price must be finite and positive")
        else:
            raise ValueError("unsupported candidate direction")

        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    def stable_json_bytes(self) -> bytes:
        return _stable_json_bytes(
            {
                "candidate_id": self.candidate_id,
                "symbol": self.symbol,
                "observation_bar_timestamp_utc": self.observation_bar_timestamp_utc,
                "signal_known_timestamp_utc": self.signal_known_timestamp_utc,
                "direction": self.direction,
                "stop_price": self.stop_price,
                "target_price": self.target_price,
                "latest_exit_timestamp_utc": self.latest_exit_timestamp_utc,
                "reason_code": self.reason_code,
                "metadata": self.metadata,
            }
        )
