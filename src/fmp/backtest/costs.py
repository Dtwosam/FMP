from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, Protocol

from fmp.contracts import Direction, OrderSide

PIP_SIZES: dict[str, float] = {
    "EURUSD": 0.0001,
    "GBPUSD": 0.0001,
    "USDJPY": 0.01,
}


def pip_size(symbol: str) -> float:
    try:
        return PIP_SIZES[symbol]
    except KeyError as exc:
        raise ValueError(f"unsupported symbol: {symbol!r}") from exc


def apply_adverse_slippage(
    price: float,
    *,
    side: OrderSide,
    pips: float,
    symbol: str,
) -> float:
    if not math.isfinite(price) or price <= 0:
        raise ValueError("price must be finite and positive")
    if not math.isfinite(pips) or pips < 0:
        raise ValueError("slippage pips must be finite and non-negative")
    delta = pips * pip_size(symbol)
    out = price + delta if side is OrderSide.BUY else price - delta
    if not math.isfinite(out) or out <= 0:
        raise ValueError("slipped price must be finite and positive")
    return out


class CommissionModel(Protocol):
    def cost_usd(self, *, units: int) -> float: ...

    def to_config(self) -> Mapping[str, object]: ...


class FinancingModel(Protocol):
    def cost_usd(
        self,
        *,
        symbol: str,
        direction: Direction,
        units: int,
        entry_timestamp_utc: datetime,
        exit_timestamp_utc: datetime,
    ) -> float: ...

    def to_config(self) -> Mapping[str, object]: ...


@dataclass(frozen=True, slots=True)
class ZeroCommission:
    def cost_usd(self, *, units: int) -> float:
        return 0.0

    def to_config(self) -> Mapping[str, object]:
        return {"model": "zero_commission"}


@dataclass(frozen=True, slots=True)
class FixedCommissionPerMillion:
    usd_per_million_per_side: float

    def __post_init__(self) -> None:
        value = self.usd_per_million_per_side
        if not math.isfinite(value) or value < 0:
            raise ValueError("commission rate must be finite and non-negative")

    def cost_usd(self, *, units: int) -> float:
        return abs(units) / 1_000_000 * self.usd_per_million_per_side

    def to_config(self) -> Mapping[str, object]:
        return {
            "model": "fixed_per_million_per_side",
            "usd_per_million_per_side": self.usd_per_million_per_side,
        }


@dataclass(frozen=True, slots=True)
class ZeroFinancing:
    def cost_usd(
        self,
        *,
        symbol: str,
        direction: Direction,
        units: int,
        entry_timestamp_utc: datetime,
        exit_timestamp_utc: datetime,
    ) -> float:
        return 0.0

    def to_config(self) -> Mapping[str, object]:
        return {"model": "zero_financing"}
