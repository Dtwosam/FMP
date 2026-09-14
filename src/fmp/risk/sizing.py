from __future__ import annotations

import math
from decimal import Decimal, ROUND_FLOOR

from fmp.contracts import Direction, SUPPORTED_SYMBOLS


def _positive_decimal(value: float, *, field: str) -> Decimal:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{field} must be finite and positive")
    return Decimal(str(value))


def _loss_usd_per_unit_decimal(
    symbol: str,
    entry_price: float,
    stop_price: float,
) -> Decimal:
    if symbol not in SUPPORTED_SYMBOLS:
        raise ValueError(f"unsupported symbol: {symbol!r}")
    entry = _positive_decimal(entry_price, field="entry price")
    stop = _positive_decimal(stop_price, field="stop price")
    distance = abs(entry - stop)
    if distance == 0:
        raise ValueError("stop distance must be positive")
    if symbol in {"EURUSD", "GBPUSD"}:
        return distance
    return distance / stop


def loss_usd_per_unit(symbol: str, entry_price: float, stop_price: float) -> float:
    return float(_loss_usd_per_unit_decimal(symbol, entry_price, stop_price))


def size_units(
    *,
    symbol: str,
    entry_price: float,
    stop_price: float,
    allowed_risk_usd: float,
) -> int:
    allowed = _positive_decimal(allowed_risk_usd, field="allowed risk")
    loss = _loss_usd_per_unit_decimal(symbol, entry_price, stop_price)
    units = int((allowed / loss).to_integral_value(rounding=ROUND_FLOOR))
    if units <= 0:
        raise ValueError("position size must be positive")
    return units


def pnl_usd(
    *,
    symbol: str,
    direction: Direction,
    units: int,
    entry_price: float,
    exit_price: float,
) -> float:
    if symbol not in SUPPORTED_SYMBOLS:
        raise ValueError(f"unsupported symbol: {symbol!r}")
    if direction not in {Direction.LONG, Direction.SHORT}:
        raise ValueError("PnL direction must be LONG or SHORT")
    if not isinstance(units, int) or isinstance(units, bool) or units <= 0:
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
        return float(quote_pnl)
    return float(quote_pnl / exit_)
