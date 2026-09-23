from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from fmp.contracts import Direction, SUPPORTED_SYMBOLS
from fmp.features.contracts import SUPPORTED_TIMEFRAMES, timeframe_delta


EXPERIMENT_ID = "EXP-20260923-044"
PROTOCOL_VERSION = "fmp-market-learning-v1"
MARKET_FEATURE_SET_VERSION = "fmp-market-feature-v1"
BASE_FEATURE_DEFINITION_VERSION = "fmp-feature-v1"
MARKET_HISTORY_START = date(2015, 1, 1)
MARKET_HISTORY_END_EXCLUSIVE = date(2026, 8, 21)
EVIDENCE_LABEL = "RETROSPECTIVE_ALREADY_SEEN"
HORIZONS_MINUTES = (60, 240)
SLIPPAGE_PIPS = (0.2, 0.5, 1.0)


def _validate_utc(value: datetime, *, field: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must use UTC")


@dataclass(frozen=True, slots=True)
class MarketObservation:
    symbol: str
    timeframe: str
    bar_start_utc: datetime
    available_at_utc: datetime
    feature_set_version: str = MARKET_FEATURE_SET_VERSION

    def __post_init__(self) -> None:
        if self.symbol not in SUPPORTED_SYMBOLS:
            raise ValueError(f"unsupported market-learning symbol: {self.symbol!r}")
        if self.timeframe not in SUPPORTED_TIMEFRAMES:
            raise ValueError(f"unsupported market-learning timeframe: {self.timeframe!r}")
        _validate_utc(self.bar_start_utc, field="bar_start_utc")
        _validate_utc(self.available_at_utc, field="available_at_utc")
        if self.available_at_utc != self.bar_start_utc + timeframe_delta(self.timeframe):
            raise ValueError(
                "available_at_utc must equal bar_start_utc plus the exact timeframe"
            )
        if not self.feature_set_version.strip():
            raise ValueError("feature_set_version must be non-empty")

    @property
    def fingerprint(self) -> str:
        payload = {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "bar_start_utc": self.bar_start_utc.isoformat(),
            "available_at_utc": self.available_at_utc.isoformat(),
            "feature_set_version": self.feature_set_version,
        }
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class MarketOutcomeLabel:
    observation_fingerprint: str
    symbol: str
    timeframe: str
    available_at_utc: datetime
    horizon_minutes: int
    slippage_pips: float
    entry_timestamp_utc: datetime
    exit_timestamp_utc: datetime
    future_mid_move_pips: float
    long_net_pips: float
    short_net_pips: float
    best_direction: Direction
    evidence_label: str = EVIDENCE_LABEL

    def __post_init__(self) -> None:
        if not self.observation_fingerprint.strip():
            raise ValueError("observation_fingerprint must be non-empty")
        if self.symbol not in SUPPORTED_SYMBOLS:
            raise ValueError(f"unsupported market-learning symbol: {self.symbol!r}")
        if self.timeframe not in SUPPORTED_TIMEFRAMES:
            raise ValueError(f"unsupported market-learning timeframe: {self.timeframe!r}")
        _validate_utc(self.available_at_utc, field="available_at_utc")
        _validate_utc(self.entry_timestamp_utc, field="entry_timestamp_utc")
        _validate_utc(self.exit_timestamp_utc, field="exit_timestamp_utc")
        if self.horizon_minutes not in HORIZONS_MINUTES:
            raise ValueError("unsupported market-learning horizon")
        if self.slippage_pips not in SLIPPAGE_PIPS:
            raise ValueError("unsupported market-learning slippage")
        if self.entry_timestamp_utc != self.available_at_utc:
            raise ValueError("entry timestamp must equal observation availability")
        if self.exit_timestamp_utc != self.entry_timestamp_utc + timedelta(
            minutes=self.horizon_minutes
        ):
            raise ValueError("exit timestamp must equal the exact frozen horizon")
        for field, value in (
            ("future_mid_move_pips", self.future_mid_move_pips),
            ("long_net_pips", self.long_net_pips),
            ("short_net_pips", self.short_net_pips),
        ):
            if not math.isfinite(value):
                raise ValueError(f"{field} must be finite")
        if self.best_direction not in {
            Direction.LONG,
            Direction.SHORT,
            Direction.NO_TRADE,
        }:
            raise ValueError("unsupported best_direction")
        if self.evidence_label != EVIDENCE_LABEL:
            raise ValueError("market-learning historical evidence label mismatch")


@dataclass(frozen=True, slots=True)
class MarketOutcomeResult:
    observation_fingerprint: str
    horizon_minutes: int
    slippage_pips: float
    reason_code: str
    label: MarketOutcomeLabel | None

    def __post_init__(self) -> None:
        if not self.observation_fingerprint.strip():
            raise ValueError("observation_fingerprint must be non-empty")
        if self.horizon_minutes not in HORIZONS_MINUTES:
            raise ValueError("unsupported market-learning horizon")
        if self.slippage_pips not in SLIPPAGE_PIPS:
            raise ValueError("unsupported market-learning slippage")
        if not self.reason_code.strip():
            raise ValueError("reason_code must be non-empty")
        if (self.label is None) == (self.reason_code == "LABELED"):
            raise ValueError("LABELED reason and label presence must agree")


__all__ = [
    "BASE_FEATURE_DEFINITION_VERSION",
    "EVIDENCE_LABEL",
    "EXPERIMENT_ID",
    "HORIZONS_MINUTES",
    "MARKET_FEATURE_SET_VERSION",
    "MARKET_HISTORY_END_EXCLUSIVE",
    "MARKET_HISTORY_START",
    "PROTOCOL_VERSION",
    "SLIPPAGE_PIPS",
    "MarketObservation",
    "MarketOutcomeLabel",
    "MarketOutcomeResult",
]
