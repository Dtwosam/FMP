from __future__ import annotations

import math
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

from .contracts import FMP_SYMBOL, PROVIDER_INSTRUMENT, HeartbeatEvent, NormalizedQuote


class ProviderMessageError(ValueError):
    """Fail-closed error for malformed or integrity-invalid provider messages."""


def _provider_time(value: object) -> datetime:
    if not isinstance(value, str):
        raise ProviderMessageError("provider timestamp is invalid")
    if not (value.endswith("Z") or value.endswith("+00:00")):
        raise ProviderMessageError("provider timestamp must use UTC")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except ValueError:
        raise ProviderMessageError("provider timestamp is invalid") from None
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ProviderMessageError("provider timestamp must use UTC")
    return parsed.astimezone(timezone.utc)


def _best_price(value: object, *, side: str) -> float:
    if not isinstance(value, list) or not value:
        raise ProviderMessageError("provider price ladder is invalid")
    prices: list[float] = []
    for level in value:
        if not isinstance(level, Mapping) or "price" not in level:
            raise ProviderMessageError("provider price ladder is invalid")
        raw_price = level["price"]
        if isinstance(raw_price, bool) or not isinstance(raw_price, (str, int, float)):
            raise ProviderMessageError("provider price ladder is invalid")
        try:
            price = float(raw_price)
        except (TypeError, ValueError):
            raise ProviderMessageError("provider price ladder is invalid") from None
        if not math.isfinite(price) or price <= 0:
            raise ProviderMessageError("provider price ladder is invalid")
        prices.append(price)
    return max(prices) if side == "bid" else min(prices)


def normalize_provider_message(
    raw: Mapping[str, Any],
    *,
    received_at_utc: datetime,
    receive_monotonic_ns: int,
) -> NormalizedQuote | HeartbeatEvent:
    if not isinstance(raw, Mapping):
        raise ProviderMessageError("provider message must be an object")
    message_type = raw.get("type")
    if message_type not in ("PRICE", "HEARTBEAT"):
        raise ProviderMessageError("provider message type is invalid")

    source_time = _provider_time(raw.get("time"))
    if message_type == "HEARTBEAT":
        try:
            return HeartbeatEvent(
                source_time_utc=source_time,
                received_at_utc=received_at_utc,
                receive_monotonic_ns=receive_monotonic_ns,
            )
        except (TypeError, ValueError):
            raise ProviderMessageError("heartbeat receive metadata is invalid") from None

    if raw.get("instrument") != PROVIDER_INSTRUMENT:
        raise ProviderMessageError("provider instrument is invalid")
    tradeable = raw.get("tradeable")
    if type(tradeable) is not bool:
        raise ProviderMessageError("provider tradeable state is invalid")
    bid = _best_price(raw.get("bids"), side="bid")
    ask = _best_price(raw.get("asks"), side="ask")
    if bid > ask:
        raise ProviderMessageError("provider quote is crossed")

    try:
        return NormalizedQuote(
            source_time_utc=source_time,
            received_at_utc=received_at_utc,
            receive_monotonic_ns=receive_monotonic_ns,
            symbol=FMP_SYMBOL,
            bid=bid,
            ask=ask,
            tradeable=tradeable,
        )
    except (TypeError, ValueError):
        raise ProviderMessageError("provider quote metadata is invalid") from None


class StreamSegmentNormalizer:
    __slots__ = ("_last_source_time", "_price_fingerprint")

    def __init__(self) -> None:
        self._last_source_time: datetime | None = None
        self._price_fingerprint: tuple[object, ...] | None = None

    def accept(
        self,
        raw: Mapping[str, Any],
        *,
        received_at_utc: datetime,
        receive_monotonic_ns: int,
    ) -> NormalizedQuote | HeartbeatEvent | None:
        event = normalize_provider_message(
            raw,
            received_at_utc=received_at_utc,
            receive_monotonic_ns=receive_monotonic_ns,
        )
        source_time = event.source_time_utc

        if self._last_source_time is not None and source_time < self._last_source_time:
            raise ProviderMessageError("provider source time regressed")
        if self._last_source_time is None or source_time > self._last_source_time:
            self._last_source_time = source_time
            self._price_fingerprint = None

        if isinstance(event, NormalizedQuote):
            fingerprint = (
                event.source_time_utc,
                event.symbol,
                event.bid,
                event.ask,
                event.tradeable,
            )
            if self._price_fingerprint is None:
                self._price_fingerprint = fingerprint
            elif fingerprint == self._price_fingerprint:
                return None
            else:
                raise ProviderMessageError("conflicting duplicate provider price")
        return event


__all__ = [
    "ProviderMessageError",
    "StreamSegmentNormalizer",
    "normalize_provider_message",
]
