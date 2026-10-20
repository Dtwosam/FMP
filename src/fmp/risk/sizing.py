from __future__ import annotations

import math
from decimal import Decimal, ROUND_FLOOR

from fmp.contracts import Direction, SUPPORTED_SYMBOLS


def _positive_decimal(value: float, *, field: str) -> Decimal:
    if type(value) not in (int, float):
        raise ValueError(f"{field} must be finite numeric and positive")
    try:
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{field} must be finite and positive")
        return Decimal(str(value))
    except (TypeError, OverflowError) as exc:
        raise ValueError(f"{field} must be finite and positive") from exc


def _loss_usd_per_unit_decimal(
    symbol: str,
    entry_price: float,
    stop_price: float,
) -> Decimal:
    if type(symbol) is not str or symbol not in SUPPORTED_SYMBOLS:
        raise ValueError("unsupported symbol: expected exact supported FX pair")
    entry = _positive_decimal(entry_price, field="entry price")
    stop = _positive_decimal(stop_price, field="stop price")
    distance = abs(entry - stop)
    if distance == 0:
        raise ValueError("stop distance must be positive")
    if symbol in {"EURUSD", "GBPUSD"}:
        return distance
    return distance / stop


def _finite_risk_result(value: Decimal, *, field: str) -> float:
    try:
        result = float(value)
    except (ValueError, OverflowError) as exc:
        raise ValueError(f"{field} must remain finite") from exc
    if not math.isfinite(result):
        raise ValueError(f"{field} must remain finite")
    return result


def loss_usd_per_unit(symbol: str, entry_price: float, stop_price: float) -> float:
    return _finite_risk_result(
        _loss_usd_per_unit_decimal(symbol, entry_price, stop_price),
        field="loss per unit",
    )


def size_units(
    *,
    symbol: str,
    entry_price: float,
    stop_price: float,
    allowed_risk_usd: float,
) -> int:
    allowed = _positive_decimal(allowed_risk_usd, field="allowed risk")
    loss = _loss_usd_per_unit_decimal(symbol, entry_price, stop_price)
    try:
        units = int((allowed / loss).to_integral_value(rounding=ROUND_FLOOR))
    except (ArithmeticError, ValueError, OverflowError) as exc:
        raise ValueError("position size cannot be calculated safely") from exc
    if units <= 0:
        raise ValueError("position size must be positive")
    if units > (2 ** 63 - 1):
        raise ValueError("position size exceeds supported safety limit")
    return units


def pnl_usd(
    *,
    symbol: str,
    direction: Direction,
    units: int,
    entry_price: float,
    exit_price: float,
) -> float:
    if type(symbol) is not str or symbol not in SUPPORTED_SYMBOLS:
        raise ValueError("unsupported symbol: expected exact supported FX pair")
    if (
        type(direction) is not Direction
        or direction not in (Direction.LONG, Direction.SHORT)
    ):
        raise ValueError("PnL direction must be LONG or SHORT")
    if type(units) is not int or units <= 0:
        raise ValueError("units must be a positive integer")
    entry = _positive_decimal(entry_price, field="entry price")
    exit_ = _positive_decimal(exit_price, field="exit price")
    count = Decimal(units)
    quote_pnl = (
        (exit_ - entry) * count
        if direction is Direction.LONG
        else (entry - exit_) * count
    )
    if symbol in {"EURUSD", "GBPUSD"}:
        return _finite_risk_result(quote_pnl, field="trade PnL")
    return _finite_risk_result(quote_pnl / exit_, field="trade PnL")
