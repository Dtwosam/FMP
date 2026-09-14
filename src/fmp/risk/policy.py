from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from fmp.contracts import Decision, Direction, RejectionCode, RiskAssessment
from fmp.risk.sizing import size_units


def _require_utc(value: datetime, *, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field_name} must use UTC")


@dataclass(frozen=True, slots=True)
class RiskConfig:
    default_risk_fraction: float = 0.0025
    max_risk_fraction: float = 0.005
    max_simultaneous_risk_fraction: float = 0.01
    daily_loss_halt_fraction: float = 0.015

    def __post_init__(self) -> None:
        values = {
            "default_risk_fraction": self.default_risk_fraction,
            "max_risk_fraction": self.max_risk_fraction,
            "max_simultaneous_risk_fraction": self.max_simultaneous_risk_fraction,
            "daily_loss_halt_fraction": self.daily_loss_halt_fraction,
        }
        for name, value in values.items():
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if self.default_risk_fraction > self.max_risk_fraction:
            raise ValueError("default risk fraction must not exceed maximum risk fraction")
        if self.max_risk_fraction > self.max_simultaneous_risk_fraction:
            raise ValueError("maximum per-trade risk must not exceed simultaneous risk limit")

    def to_config(self) -> dict[str, float]:
        return {
            "default_risk_fraction": self.default_risk_fraction,
            "max_risk_fraction": self.max_risk_fraction,
            "max_simultaneous_risk_fraction": self.max_simultaneous_risk_fraction,
            "daily_loss_halt_fraction": self.daily_loss_halt_fraction,
        }


@dataclass(slots=True)
class RiskState:
    starting_equity_usd: float
    risk_equity_usd: float = field(init=False)
    current_utc_date: date | None = None
    day_start_equity_usd: float = 0.0
    day_realized_pnl_usd: float = 0.0
    daily_halt_active: bool = False
    halt_timestamp_utc: datetime | None = None
    reservations_usd: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not math.isfinite(self.starting_equity_usd) or self.starting_equity_usd <= 0:
            raise ValueError("starting equity must be finite and positive")
        self.risk_equity_usd = self.starting_equity_usd

    @property
    def total_reserved_risk_usd(self) -> float:
        return sum(self.reservations_usd.values())


def roll_utc_day(state: RiskState, *, timestamp_utc: datetime) -> None:
    _require_utc(timestamp_utc, field_name="timestamp_utc")
    target_date = timestamp_utc.date()
    if state.current_utc_date == target_date:
        return
    state.current_utc_date = target_date
    state.day_start_equity_usd = state.risk_equity_usd
    state.day_realized_pnl_usd = 0.0
    state.daily_halt_active = False
    state.halt_timestamp_utc = None


def reserve_risk(state: RiskState, *, position_id: str, amount_usd: float) -> None:
    if not position_id:
        raise ValueError("position_id must be non-empty")
    if position_id in state.reservations_usd:
        raise ValueError(f"risk already reserved for position {position_id!r}")
    if not math.isfinite(amount_usd) or amount_usd <= 0:
        raise ValueError("reserved risk amount must be finite and positive")
    state.reservations_usd[position_id] = amount_usd


def release_risk(state: RiskState, *, position_id: str) -> float:
    try:
        return state.reservations_usd.pop(position_id)
    except KeyError as exc:
        raise ValueError(f"no reserved risk for position {position_id!r}") from exc


def record_realized_pnl(
    state: RiskState,
    *,
    timestamp_utc: datetime,
    pnl_usd: float,
    config: RiskConfig,
) -> None:
    _require_utc(timestamp_utc, field_name="timestamp_utc")
    if not math.isfinite(pnl_usd):
        raise ValueError("realized PnL must be finite")
    roll_utc_day(state, timestamp_utc=timestamp_utc)
    state.risk_equity_usd += pnl_usd
    state.day_realized_pnl_usd += pnl_usd
    threshold = -config.daily_loss_halt_fraction * state.day_start_equity_usd
    if not state.daily_halt_active and state.day_realized_pnl_usd <= threshold:
        state.daily_halt_active = True
        state.halt_timestamp_utc = timestamp_utc


def _rejected(code: RejectionCode, explanation: str) -> RiskAssessment:
    return RiskAssessment(
        approved=False,
        approved_risk_usd=0.0,
        approved_units=0,
        rejection_code=code,
        explanation=explanation,
    )


def _valid_geometry(decision: Decision, reference_entry_price: float) -> bool:
    if decision.stop_price is None:
        return False
    if decision.direction is Direction.LONG:
        if decision.stop_price >= reference_entry_price:
            return False
        if decision.target_price is not None and decision.target_price <= reference_entry_price:
            return False
        return True
    if decision.direction is Direction.SHORT:
        if decision.stop_price <= reference_entry_price:
            return False
        if decision.target_price is not None and decision.target_price >= reference_entry_price:
            return False
        return True
    return False


def assess_decision(
    *,
    decision: Decision,
    reference_entry_price: float,
    timestamp_utc: datetime,
    config: RiskConfig,
    state: RiskState,
) -> RiskAssessment:
    _require_utc(timestamp_utc, field_name="timestamp_utc")
    roll_utc_day(state, timestamp_utc=timestamp_utc)

    if state.daily_halt_active:
        return _rejected(RejectionCode.DAILY_HALT, "daily realized-loss halt is active")

    if decision.direction not in {Direction.LONG, Direction.SHORT}:
        return _rejected(RejectionCode.INVALID_STOP_TARGET, "directional risk assessment requires LONG or SHORT")

    if not math.isfinite(reference_entry_price) or reference_entry_price <= 0:
        return _rejected(RejectionCode.INVALID_SIZE, "reference entry price is invalid")

    if not _valid_geometry(decision, reference_entry_price):
        return _rejected(RejectionCode.INVALID_STOP_TARGET, "stop/target geometry is invalid for direction")

    fraction = (
        config.default_risk_fraction
        if decision.requested_risk_fraction is None
        else decision.requested_risk_fraction
    )
    if fraction > config.max_risk_fraction:
        return _rejected(RejectionCode.PER_TRADE_RISK, "requested per-trade risk exceeds hard maximum")

    allowed_risk_usd = state.risk_equity_usd * fraction
    simultaneous_limit_usd = state.risk_equity_usd * config.max_simultaneous_risk_fraction
    if state.total_reserved_risk_usd + allowed_risk_usd > simultaneous_limit_usd + 1e-12:
        return _rejected(RejectionCode.SIMULTANEOUS_RISK, "simultaneous reserved risk limit would be exceeded")

    try:
        units = size_units(
            symbol=decision.symbol,
            entry_price=reference_entry_price,
            stop_price=decision.stop_price,
            allowed_risk_usd=allowed_risk_usd,
        )
    except ValueError as exc:
        return _rejected(RejectionCode.INVALID_SIZE, str(exc))

    return RiskAssessment(
        approved=True,
        approved_risk_usd=allowed_risk_usd,
        approved_units=units,
        rejection_code=None,
        explanation="approved",
    )
