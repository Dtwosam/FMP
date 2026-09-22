from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Sequence
from zoneinfo import ZoneInfo

from fmp.backtest.costs import pip_size
from fmp.contracts import Direction, QuoteBar
from fmp.strategies.contracts import SignalCandidate


LONDON = ZoneInfo("Europe/London")
_TIMEFRAME_MINUTES = {"5m": 5, "15m": 15, "1h": 60}
_ALLOWED_BUFFERS = frozenset({0, 1, 2, 3, 4, 5, 6, 8})
_ALLOWED_TARGET_MULTIPLES = frozenset({0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0})


@dataclass(frozen=True, slots=True)
class SessionBreakoutConfig:
    buffer_pips: int
    target_range_multiple: float
    timeframe: str

    def __post_init__(self) -> None:
        if self.buffer_pips not in _ALLOWED_BUFFERS:
            raise ValueError("buffer_pips is outside the approved strategy grids")
        if self.target_range_multiple not in _ALLOWED_TARGET_MULTIPLES:
            raise ValueError("target_range_multiple is outside the approved strategy grids")
        if self.timeframe not in _TIMEFRAME_MINUTES:
            raise ValueError("timeframe must be one of 5m, 15m, or 1h")


@dataclass(frozen=True, slots=True)
class _Midpoint:
    high: float
    low: float
    close: float


def _midpoint(bar: QuoteBar) -> _Midpoint:
    return _Midpoint(
        high=(bar.bid_high + bar.ask_high) / 2.0,
        low=(bar.bid_low + bar.ask_low) / 2.0,
        close=(bar.bid_close + bar.ask_close) / 2.0,
    )


def _local_label(session_date: date, hour: int, minute: int = 0) -> datetime:
    local = datetime.combine(session_date, time(hour, minute), tzinfo=LONDON)
    return local.astimezone(timezone.utc)


def _window_labels(
    session_date: date,
    *,
    start_hour: int,
    end_hour: int,
    width_minutes: int,
) -> tuple[datetime, ...]:
    start = datetime.combine(session_date, time(start_hour, 0), tzinfo=LONDON)
    end = datetime.combine(session_date, time(end_hour, 0), tzinfo=LONDON)
    labels: list[datetime] = []
    current = start
    while current < end:
        labels.append(current.astimezone(timezone.utc))
        current += timedelta(minutes=width_minutes)
    return tuple(labels)


def _candidate_id(
    *,
    symbol: str,
    session_date: date,
    timeframe: str,
    buffer_pips: int,
    target_range_multiple: float,
    suffix: str,
) -> str:
    multiple = str(target_range_multiple).replace(".", "p")
    return (
        f"SB-{symbol}-{session_date:%Y%m%d}-{timeframe}-"
        f"B{buffer_pips}-R{multiple}-{suffix}"
    )


def _no_trade(
    *,
    symbol: str,
    session_date: date,
    config: SessionBreakoutConfig,
    observation_timestamp: datetime,
    reason_code: str,
    metadata: dict[str, object],
) -> SignalCandidate:
    width = timedelta(minutes=_TIMEFRAME_MINUTES[config.timeframe])
    return SignalCandidate(
        candidate_id=_candidate_id(
            symbol=symbol,
            session_date=session_date,
            timeframe=config.timeframe,
            buffer_pips=config.buffer_pips,
            target_range_multiple=config.target_range_multiple,
            suffix=reason_code,
        ),
        symbol=symbol,
        observation_bar_timestamp_utc=observation_timestamp,
        signal_known_timestamp_utc=observation_timestamp + width,
        direction=Direction.NO_TRADE,
        stop_price=None,
        target_price=None,
        latest_exit_timestamp_utc=None,
        reason_code=reason_code,
        metadata=metadata,
    )


def _session_dates(bars: Sequence[QuoteBar]) -> tuple[date, ...]:
    # Only dates with at least one supplied bar in the research session span are
    # candidates. This avoids fabricating weekend sessions from a Sunday-evening
    # reopen bar that occurs after the mandatory flat time.
    dates: set[date] = set()
    for bar in bars:
        local = bar.timestamp_utc.astimezone(LONDON)
        if time(0, 0) <= local.timetz().replace(tzinfo=None) <= time(16, 0):
            dates.add(local.date())
    return tuple(sorted(dates))


def generate_session_breakout_candidates(
    bars: Sequence[QuoteBar],
    *,
    config: SessionBreakoutConfig,
    require_scheduled_exit_bar: bool = True,
) -> tuple[SignalCandidate, ...]:
    if type(require_scheduled_exit_bar) is not bool:
        raise TypeError("require_scheduled_exit_bar must be bool")
    if not bars:
        return ()

    ordered = tuple(sorted(bars, key=lambda item: (item.timestamp_utc, item.symbol)))
    symbols = {bar.symbol for bar in ordered}
    if len(symbols) != 1:
        raise ValueError("session breakout requires bars for exactly one symbol")
    symbol = next(iter(symbols))
    identities = [(bar.timestamp_utc, bar.symbol) for bar in ordered]
    if len(set(identities)) != len(identities):
        raise ValueError("duplicate quote-bar identity in session breakout input")

    by_timestamp = {bar.timestamp_utc: bar for bar in ordered}
    width_minutes = _TIMEFRAME_MINUTES[config.timeframe]
    width = timedelta(minutes=width_minutes)
    buffer = config.buffer_pips * pip_size(symbol)
    out: list[SignalCandidate] = []

    for session_date in _session_dates(ordered):
        range_labels = _window_labels(
            session_date,
            start_hour=0,
            end_hour=8,
            width_minutes=width_minutes,
        )
        breakout_labels = _window_labels(
            session_date,
            start_hour=8,
            end_hour=12,
            width_minutes=width_minutes,
        )
        exit_timestamp = _local_label(session_date, 16)
        base_metadata: dict[str, object] = {
            "session_date": session_date.isoformat(),
            "timezone": "Europe/London",
            "timeframe": config.timeframe,
            "buffer_pips": config.buffer_pips,
            "target_range_multiple": config.target_range_multiple,
        }

        missing_range = next((label for label in range_labels if label not in by_timestamp), None)
        if missing_range is not None:
            out.append(
                _no_trade(
                    symbol=symbol,
                    session_date=session_date,
                    config=config,
                    observation_timestamp=missing_range,
                    reason_code="INCOMPLETE_SESSION",
                    metadata={**base_metadata, "missing_timestamp_utc": missing_range},
                )
            )
            continue

        if require_scheduled_exit_bar and exit_timestamp not in by_timestamp:
            out.append(
                _no_trade(
                    symbol=symbol,
                    session_date=session_date,
                    config=config,
                    observation_timestamp=range_labels[-1],
                    reason_code="INCOMPLETE_SESSION",
                    metadata={**base_metadata, "missing_timestamp_utc": exit_timestamp},
                )
            )
            continue

        range_midpoints = [_midpoint(by_timestamp[label]) for label in range_labels]
        range_high = max(item.high for item in range_midpoints)
        range_low = min(item.low for item in range_midpoints)
        range_width = range_high - range_low
        range_metadata = {
            **base_metadata,
            "range_high": range_high,
            "range_low": range_low,
            "range_width": range_width,
        }
        if range_width <= 0:
            out.append(
                _no_trade(
                    symbol=symbol,
                    session_date=session_date,
                    config=config,
                    observation_timestamp=range_labels[-1],
                    reason_code="ZERO_RANGE",
                    metadata=range_metadata,
                )
            )
            continue

        emitted = False
        for label in breakout_labels:
            bar = by_timestamp.get(label)
            if bar is None:
                out.append(
                    _no_trade(
                        symbol=symbol,
                        session_date=session_date,
                        config=config,
                        observation_timestamp=label,
                        reason_code="INCOMPLETE_SESSION",
                        metadata={**range_metadata, "missing_timestamp_utc": label},
                    )
                )
                emitted = True
                break

            signal_mid_close = _midpoint(bar).close
            long_break = signal_mid_close > range_high + buffer
            short_break = signal_mid_close < range_low - buffer
            if long_break and short_break:
                out.append(
                    _no_trade(
                        symbol=symbol,
                        session_date=session_date,
                        config=config,
                        observation_timestamp=label,
                        reason_code="INVALID_BREAKOUT",
                        metadata={**range_metadata, "signal_mid_close": signal_mid_close},
                    )
                )
                emitted = True
                break
            if not long_break and not short_break:
                continue

            direction = Direction.LONG if long_break else Direction.SHORT
            stop = range_low if direction is Direction.LONG else range_high
            target = (
                signal_mid_close + config.target_range_multiple * range_width
                if direction is Direction.LONG
                else signal_mid_close - config.target_range_multiple * range_width
            )
            out.append(
                SignalCandidate(
                    candidate_id=_candidate_id(
                        symbol=symbol,
                        session_date=session_date,
                        timeframe=config.timeframe,
                        buffer_pips=config.buffer_pips,
                        target_range_multiple=config.target_range_multiple,
                        suffix=direction.value,
                    ),
                    symbol=symbol,
                    observation_bar_timestamp_utc=label,
                    signal_known_timestamp_utc=label + width,
                    direction=direction,
                    stop_price=stop,
                    target_price=target,
                    latest_exit_timestamp_utc=exit_timestamp,
                    reason_code=f"BREAKOUT_{direction.value}",
                    metadata={
                        **range_metadata,
                        "signal_mid_close": signal_mid_close,
                    },
                )
            )
            emitted = True
            break

        if not emitted:
            final_label = breakout_labels[-1]
            out.append(
                _no_trade(
                    symbol=symbol,
                    session_date=session_date,
                    config=config,
                    observation_timestamp=final_label,
                    reason_code="NO_BREAKOUT",
                    metadata=range_metadata,
                )
            )

    return tuple(out)
