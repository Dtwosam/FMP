from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from fmp.contracts import QuoteBar

from .contracts import FMP_SYMBOL, NormalizedQuote


_ONE_MINUTE = timedelta(minutes=1)
_FIFTEEN_MINUTES = timedelta(minutes=15)


def _require_utc(value: datetime, *, field: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError(f"{field} must be a datetime")
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must use UTC")


def _minute_label(value: datetime) -> datetime:
    return value.replace(second=0, microsecond=0)


def _fifteen_minute_label(value: datetime) -> datetime:
    return value.replace(minute=(value.minute // 15) * 15, second=0, microsecond=0)


def _intersects(
    left_start: datetime,
    left_end: datetime,
    right_start: datetime,
    right_end: datetime,
) -> bool:
    return left_start < right_end and right_start < left_end


@dataclass(slots=True)
class _MinuteAccumulator:
    timestamp_utc: datetime
    bid_open: float
    bid_high: float
    bid_low: float
    bid_close: float
    ask_open: float
    ask_high: float
    ask_low: float
    ask_close: float

    @classmethod
    def from_quote(cls, quote: NormalizedQuote) -> "_MinuteAccumulator":
        label = _minute_label(quote.source_time_utc)
        return cls(
            timestamp_utc=label,
            bid_open=quote.bid,
            bid_high=quote.bid,
            bid_low=quote.bid,
            bid_close=quote.bid,
            ask_open=quote.ask,
            ask_high=quote.ask,
            ask_low=quote.ask,
            ask_close=quote.ask,
        )

    def update(self, quote: NormalizedQuote) -> None:
        self.bid_high = max(self.bid_high, quote.bid)
        self.bid_low = min(self.bid_low, quote.bid)
        self.bid_close = quote.bid
        self.ask_high = max(self.ask_high, quote.ask)
        self.ask_low = min(self.ask_low, quote.ask)
        self.ask_close = quote.ask

    def to_bar(self) -> QuoteBar:
        return QuoteBar(
            timestamp_utc=self.timestamp_utc,
            symbol=FMP_SYMBOL,
            bid_open=self.bid_open,
            bid_high=self.bid_high,
            bid_low=self.bid_low,
            bid_close=self.bid_close,
            ask_open=self.ask_open,
            ask_high=self.ask_high,
            ask_low=self.ask_low,
            ask_close=self.ask_close,
        )


class LiveBarBuilder:
    __slots__ = (
        "_current_minute",
        "_minute_bars",
        "_completed_minutes",
        "_stale_intervals",
        "_last_time",
        "_closed_fifteen",
    )

    def __init__(self) -> None:
        self._current_minute: _MinuteAccumulator | None = None
        self._minute_bars: dict[datetime, QuoteBar] = {}
        self._completed_minutes: list[QuoteBar] = []
        self._stale_intervals: list[tuple[datetime, datetime]] = []
        self._last_time: datetime | None = None
        self._closed_fifteen: set[datetime] = set()

    def on_quote(self, quote: NormalizedQuote) -> tuple[QuoteBar, ...]:
        if not isinstance(quote, NormalizedQuote):
            raise TypeError("quote must be a NormalizedQuote")

        completed = self._advance(quote.source_time_utc)
        if not quote.tradeable:
            return completed

        label = _minute_label(quote.source_time_utc)
        if self._current_minute is None:
            self._current_minute = _MinuteAccumulator.from_quote(quote)
        elif self._current_minute.timestamp_utc == label:
            self._current_minute.update(quote)
        else:
            raise RuntimeError("minute state did not advance before quote accumulation")
        return completed

    def on_time_advance(self, timestamp_utc: datetime) -> tuple[QuoteBar, ...]:
        return self._advance(timestamp_utc)

    def drain_completed_minute_bars(self) -> tuple[QuoteBar, ...]:
        completed = tuple(self._completed_minutes)
        self._completed_minutes.clear()
        return completed

    def mark_stale_interval(self, start_utc: datetime, end_utc: datetime) -> None:
        _require_utc(start_utc, field="start_utc")
        _require_utc(end_utc, field="end_utc")
        if end_utc <= start_utc:
            raise ValueError("stale interval end must be after start")

        for fifteen_start in self._closed_fifteen:
            fifteen_end = fifteen_start + _FIFTEEN_MINUTES
            if _intersects(start_utc, end_utc, fifteen_start, fifteen_end):
                if all(
                    fifteen_start + index * _ONE_MINUTE in self._minute_bars
                    for index in range(15)
                ):
                    raise ValueError("stale interval cannot invalidate an emitted 15m bar")

        self._stale_intervals.append((start_utc, end_utc))
        stale_minutes = [
            label
            for label in self._minute_bars
            if self._minute_is_stale(label)
        ]
        for label in stale_minutes:
            del self._minute_bars[label]
        self._completed_minutes = [
            item
            for item in self._completed_minutes
            if not self._minute_is_stale(item.timestamp_utc)
        ]

    def _advance(self, timestamp_utc: datetime) -> tuple[QuoteBar, ...]:
        _require_utc(timestamp_utc, field="timestamp_utc")
        if self._last_time is not None and timestamp_utc < self._last_time:
            raise ValueError("live bar time regressed")
        self._last_time = timestamp_utc

        current = self._current_minute
        if current is not None and current.timestamp_utc + _ONE_MINUTE <= timestamp_utc:
            self._finalize_current_minute()

        return self._complete_fifteen_minute_bars(timestamp_utc)

    def _finalize_current_minute(self) -> None:
        current = self._current_minute
        if current is None:
            return
        label = current.timestamp_utc
        if not self._minute_is_stale(label):
            completed = current.to_bar()
            self._minute_bars[label] = completed
            self._completed_minutes.append(completed)
        self._current_minute = None

    def _minute_is_stale(self, label: datetime) -> bool:
        end = label + _ONE_MINUTE
        return any(
            _intersects(label, end, stale_start, stale_end)
            for stale_start, stale_end in self._stale_intervals
        )

    def _complete_fifteen_minute_bars(
        self,
        timestamp_utc: datetime,
    ) -> tuple[QuoteBar, ...]:
        candidates = sorted(
            {
                _fifteen_minute_label(label)
                for label in self._minute_bars
                if _fifteen_minute_label(label) + _FIFTEEN_MINUTES <= timestamp_utc
            }
        )
        completed: list[QuoteBar] = []
        for start in candidates:
            if start in self._closed_fifteen:
                continue
            self._closed_fifteen.add(start)
            minute_bars = [
                self._minute_bars.get(start + index * _ONE_MINUTE)
                for index in range(15)
            ]
            if any(bar is None for bar in minute_bars):
                continue
            bars = [bar for bar in minute_bars if bar is not None]
            completed.append(
                QuoteBar(
                    timestamp_utc=start,
                    symbol=FMP_SYMBOL,
                    bid_open=bars[0].bid_open,
                    bid_high=max(bar.bid_high for bar in bars),
                    bid_low=min(bar.bid_low for bar in bars),
                    bid_close=bars[-1].bid_close,
                    ask_open=bars[0].ask_open,
                    ask_high=max(bar.ask_high for bar in bars),
                    ask_low=min(bar.ask_low for bar in bars),
                    ask_close=bars[-1].ask_close,
                )
            )
        return tuple(completed)


__all__ = ["LiveBarBuilder"]
