from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Mapping, Sequence

SUPPORTED_SYMBOLS = frozenset({"EURUSD", "GBPUSD", "USDJPY"})


class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    NO_TRADE = "NO_TRADE"


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class ExitReason(str, Enum):
    STOP = "STOP"
    TARGET = "TARGET"
    TIME_EXIT = "TIME_EXIT"
    END_OF_DATA = "END_OF_DATA"


class RejectionCode(str, Enum):
    NO_TRADE = "NO_TRADE"
    TIMING_CONTRACT = "TIMING_CONTRACT"
    INVALID_QUOTE = "INVALID_QUOTE"
    INVALID_STOP_TARGET = "INVALID_STOP_TARGET"
    PER_TRADE_RISK = "PER_TRADE_RISK"
    SIMULTANEOUS_RISK = "SIMULTANEOUS_RISK"
    DAILY_HALT = "DAILY_HALT"
    INVALID_SIZE = "INVALID_SIZE"


def _validate_utc(value: datetime, *, field: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must use UTC")


def _validate_symbol(symbol: str) -> None:
    if symbol not in SUPPORTED_SYMBOLS:
        raise ValueError(f"unsupported symbol: {symbol!r}")


def _validate_price(value: float, *, field: str) -> None:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{field} must be a finite positive price")


@dataclass(frozen=True, slots=True)
class QuoteBar:
    timestamp_utc: datetime
    symbol: str
    bid_open: float
    bid_high: float
    bid_low: float
    bid_close: float
    ask_open: float
    ask_high: float
    ask_low: float
    ask_close: float

    def __post_init__(self) -> None:
        _validate_utc(self.timestamp_utc, field="timestamp_utc")
        _validate_symbol(self.symbol)
        values = {
            "bid_open": self.bid_open,
            "bid_high": self.bid_high,
            "bid_low": self.bid_low,
            "bid_close": self.bid_close,
            "ask_open": self.ask_open,
            "ask_high": self.ask_high,
            "ask_low": self.ask_low,
            "ask_close": self.ask_close,
        }
        for field, value in values.items():
            _validate_price(value, field=field)

        for side in ("bid", "ask"):
            low = getattr(self, f"{side}_low")
            high = getattr(self, f"{side}_high")
            open_ = getattr(self, f"{side}_open")
            close = getattr(self, f"{side}_close")
            if low > high or not (low <= open_ <= high) or not (low <= close <= high):
                raise ValueError(f"{side.upper()} OHLC is internally inconsistent")

        for field in ("open", "high", "low", "close"):
            if getattr(self, f"ask_{field}") < getattr(self, f"bid_{field}"):
                raise ValueError(f"ask {field} must not be below bid {field}")


@dataclass(frozen=True, slots=True)
class Decision:
    decision_id: str
    symbol: str
    decision_timestamp_utc: datetime
    direction: Direction
    earliest_executable_timestamp_utc: datetime | None
    requested_risk_fraction: float | None
    stop_price: float | None
    target_price: float | None
    reason_code: str | None = None
    reason_text: str | None = None

    def __post_init__(self) -> None:
        if not self.decision_id.strip():
            raise ValueError("decision_id must be non-empty")
        _validate_symbol(self.symbol)
        _validate_utc(self.decision_timestamp_utc, field="decision_timestamp_utc")

        if self.requested_risk_fraction is not None:
            if not math.isfinite(self.requested_risk_fraction) or self.requested_risk_fraction <= 0:
                raise ValueError("requested_risk_fraction must be finite and positive")

        if self.direction is Direction.NO_TRADE:
            return

        if self.earliest_executable_timestamp_utc is None:
            raise ValueError("earliest executable timestamp is required for directional decisions")
        _validate_utc(
            self.earliest_executable_timestamp_utc,
            field="earliest_executable_timestamp_utc",
        )
        if self.earliest_executable_timestamp_utc <= self.decision_timestamp_utc:
            raise ValueError("earliest executable timestamp must be after decision timestamp")
        if self.stop_price is None:
            raise ValueError("stop price is required for directional decisions")
        _validate_price(self.stop_price, field="stop_price")
        if self.target_price is not None:
            _validate_price(self.target_price, field="target_price")


@dataclass(frozen=True, slots=True)
class ScheduledExit:
    decision_id: str
    symbol: str
    timestamp_utc: datetime

    def __post_init__(self) -> None:
        if not self.decision_id.strip():
            raise ValueError("scheduled-exit decision_id must be non-empty")
        _validate_symbol(self.symbol)
        _validate_utc(self.timestamp_utc, field="scheduled-exit timestamp_utc")


@dataclass(frozen=True, slots=True)
class RiskAssessment:
    approved: bool
    approved_risk_usd: float
    approved_units: int
    rejection_code: RejectionCode | None
    explanation: str


@dataclass(frozen=True, slots=True)
class OrderIntent:
    decision_id: str
    symbol: str
    direction: Direction
    units: int
    reserved_risk_usd: float
    stop_price: float
    target_price: float | None
    decision_timestamp_utc: datetime
    earliest_executable_timestamp_utc: datetime


@dataclass(frozen=True, slots=True)
class Position:
    position_id: str
    decision_id: str
    symbol: str
    direction: Direction
    units: int
    entry_timestamp_utc: datetime
    entry_reference_price: float
    entry_price: float
    entry_commission_usd: float
    stop_price: float
    target_price: float | None
    reserved_risk_usd: float


@dataclass(frozen=True, slots=True)
class TradeRecord:
    trade_id: str
    decision_id: str
    symbol: str
    direction: Direction
    units: int
    entry_timestamp_utc: datetime
    exit_timestamp_utc: datetime
    entry_reference_price: float
    exit_reference_price: float
    entry_price: float
    exit_price: float
    stop_price: float
    target_price: float | None
    exit_reason: ExitReason
    intrabar_ambiguous: bool
    gross_pnl_usd: float
    slippage_cost_usd: float
    commission_cost_usd: float
    financing_cost_usd: float
    net_pnl_usd: float
    risk_equity_before_usd: float
    risk_equity_after_usd: float


@dataclass(frozen=True, slots=True)
class RejectionRecord:
    decision_id: str
    symbol: str
    decision_timestamp_utc: datetime
    evaluated_timestamp_utc: datetime
    code: RejectionCode
    explanation: str


@dataclass(frozen=True, slots=True)
class EquityCheckpoint:
    timestamp_utc: datetime
    realized_risk_equity_usd: float


@dataclass(frozen=True, slots=True)
class BacktestRun:
    run_identity: Mapping[str, object]
    trades: tuple[TradeRecord, ...]
    rejections: tuple[RejectionRecord, ...]
    equity_checkpoints: tuple[EquityCheckpoint, ...]
    metrics: Mapping[str, object]


def validate_quote_bars(bars: Sequence[QuoteBar]) -> None:
    keys = [(bar.timestamp_utc, bar.symbol) for bar in bars]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate quote-bar identity")
    if keys != sorted(keys):
        raise ValueError("quote bars must be sorted by timestamp_utc then symbol")


def validate_decisions(decisions: Sequence[Decision]) -> None:
    ids = [decision.decision_id for decision in decisions]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate decision_id")
