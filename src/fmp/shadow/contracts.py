from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from fmp.contracts import Decision, Direction, ScheduledExit


PHASE8_EXPERIMENT_ID = "EXP-20260917-010"
PHASE7_CHECKPOINT_TAG = "fmp-v1-phase7-walk-forward"
PHASE7_CHECKPOINT_SHA = "b6fb0176555b071fef6d1070edf3407b03cd60c9"

MT5_BRIDGE_PROTOCOL = "fmp-mt5-demo-file-bridge-v1"
MT5_PROVIDER = "FP_MARKETS_MT5_DEMO"
MT5_TRANSPORT = "MT5_FILE_COMMON_JSONL"
MT5_BRIDGE_FILE = "FMP/phase8-usdjpy-feed.jsonl"
MT5_ALLOWED_SERVERS = ("FPMarketsSC-Demo", "FPMarketsSC-Demo2")

# Retained temporarily for the legacy OANDA implementation while the amended
# MT5 bridge is introduced task-by-task. Active OANDA runtime surfaces are
# retired later in the implementation plan rather than during this identity-only
# contract change.
PRACTICE_STREAM_HOST = "stream-fxpractice.oanda.com"
PRACTICE_STREAM_PATH_TEMPLATE = "/v3/accounts/{account_id}/pricing/stream"
PROVIDER_INSTRUMENT = "USD_JPY"
FMP_SYMBOL = "USDJPY"

STRATEGY_FAMILY = "session_breakout"
TIMEFRAME = "15m"
BREAKOUT_BUFFER_PIPS = 5
TARGET_RANGE_MULTIPLE = 1.5

SLIPPAGE_SCENARIOS = (0.2, 0.5, 1.0)
STARTING_EQUITY_USD = 100_000.0
# Bridge silence at this threshold is a continuity failure. During live shadow
# capture, market no-tick gaps at the same threshold are diagnostic only unless
# they compromise required bar context or an open simulated trade path.
LIVENESS_TIMEOUT_SECONDS = 15.0
QUOTE_DEADLINE_SECONDS = 5.0


def _validate_utc(value: datetime, *, field: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError(f"{field} must be a datetime")
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must use UTC")


def _validate_price(value: float, *, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field} must be numeric")
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{field} must be a finite positive price")


def _validate_monotonic_ns(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("receive_monotonic_ns must be an integer")
    if value < 0:
        raise ValueError("receive_monotonic_ns must be non-negative")


@dataclass(frozen=True, slots=True)
class NormalizedQuote:
    source_time_utc: datetime
    received_at_utc: datetime
    receive_monotonic_ns: int
    symbol: str
    bid: float
    ask: float
    tradeable: bool

    def __post_init__(self) -> None:
        _validate_utc(self.source_time_utc, field="source_time_utc")
        _validate_utc(self.received_at_utc, field="received_at_utc")
        _validate_monotonic_ns(self.receive_monotonic_ns)
        if self.symbol != FMP_SYMBOL:
            raise ValueError(f"Phase 8 supports only {FMP_SYMBOL}")
        _validate_price(self.bid, field="bid")
        _validate_price(self.ask, field="ask")
        if self.bid > self.ask:
            raise ValueError("bid must not exceed ask")
        if type(self.tradeable) is not bool:
            raise TypeError("tradeable must be bool")


@dataclass(frozen=True, slots=True)
class HeartbeatEvent:
    source_time_utc: datetime
    received_at_utc: datetime
    receive_monotonic_ns: int

    def __post_init__(self) -> None:
        _validate_utc(self.source_time_utc, field="source_time_utc")
        _validate_utc(self.received_at_utc, field="received_at_utc")
        _validate_monotonic_ns(self.receive_monotonic_ns)


@dataclass(frozen=True, slots=True)
class ShadowIntent:
    decision: Decision
    scheduled_exit: ScheduledExit
    units: int
    reserved_risk_usd: float
    slippage_pips: float

    def __post_init__(self) -> None:
        if not isinstance(self.decision, Decision):
            raise TypeError("decision must be a Decision")
        if not isinstance(self.scheduled_exit, ScheduledExit):
            raise TypeError("scheduled_exit must be a ScheduledExit")
        if self.decision.direction is Direction.NO_TRADE:
            raise ValueError("ShadowIntent requires a directional decision")
        if self.decision.symbol != FMP_SYMBOL or self.scheduled_exit.symbol != FMP_SYMBOL:
            raise ValueError(f"Phase 8 shadow intents support only {FMP_SYMBOL}")
        if self.scheduled_exit.decision_id != self.decision.decision_id:
            raise ValueError("scheduled exit must match decision_id")
        if isinstance(self.units, bool) or not isinstance(self.units, int):
            raise TypeError("units must be an integer")
        if self.units <= 0:
            raise ValueError("units must be positive")
        if isinstance(self.reserved_risk_usd, bool) or not isinstance(
            self.reserved_risk_usd, (int, float)
        ):
            raise TypeError("reserved_risk_usd must be numeric")
        if not math.isfinite(self.reserved_risk_usd) or self.reserved_risk_usd <= 0:
            raise ValueError("reserved_risk_usd must be finite and positive")
        if self.slippage_pips not in SLIPPAGE_SCENARIOS:
            raise ValueError("slippage_pips must be one of the frozen Phase 8 scenarios")


class ShadowOutcome(str, Enum):
    COMPLETED = "COMPLETED"
    OUTCOME_UNKNOWN_AFTER_GAP = "OUTCOME_UNKNOWN_AFTER_GAP"
    ENTRY_DEADLINE_MISSED = "ENTRY_DEADLINE_MISSED"
    EXIT_DEADLINE_MISSED = "EXIT_DEADLINE_MISSED"


__all__ = [
    "BREAKOUT_BUFFER_PIPS",
    "FMP_SYMBOL",
    "HeartbeatEvent",
    "LIVENESS_TIMEOUT_SECONDS",
    "MT5_ALLOWED_SERVERS",
    "MT5_BRIDGE_FILE",
    "MT5_BRIDGE_PROTOCOL",
    "MT5_PROVIDER",
    "MT5_TRANSPORT",
    "NormalizedQuote",
    "PHASE7_CHECKPOINT_SHA",
    "PHASE7_CHECKPOINT_TAG",
    "PHASE8_EXPERIMENT_ID",
    "PRACTICE_STREAM_HOST",
    "PRACTICE_STREAM_PATH_TEMPLATE",
    "PROVIDER_INSTRUMENT",
    "QUOTE_DEADLINE_SECONDS",
    "SLIPPAGE_SCENARIOS",
    "STARTING_EQUITY_USD",
    "STRATEGY_FAMILY",
    "ShadowIntent",
    "ShadowOutcome",
    "TARGET_RANGE_MULTIPLE",
    "TIMEFRAME",
]
