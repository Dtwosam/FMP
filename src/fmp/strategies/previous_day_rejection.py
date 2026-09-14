from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Sequence
from zoneinfo import ZoneInfo

from fmp.backtest.costs import pip_size
from fmp.contracts import Direction, QuoteBar
from fmp.strategies.contracts import SignalCandidate


LONDON = ZoneInfo("Europe/London")
NEW_YORK = ZoneInfo("America/New_York")
_TIMEFRAME_MINUTES = {"5m": 5, "15m": 15, "1h": 60}
_ALLOWED_BUFFERS = frozenset({0, 2, 5})


@dataclass(frozen=True, slots=True)
class PreviousDayRejectionConfig:
    buffer_pips: int
    timeframe: str

    def __post_init__(self) -> None:
        if self.buffer_pips not in _ALLOWED_BUFFERS:
            raise ValueError("buffer_pips must be one of 0, 2, or 5")
        if self.timeframe not in _TIMEFRAME_MINUTES:
            raise ValueError("timeframe must be one of 5m, 15m, or 1h")


@dataclass(frozen=True, slots=True)
class _Midpoint:
    high: float
    low: float
    close: float


@dataclass(frozen=True, slots=True)
class _ReferenceLevels:
    high: float
    low: float
    midpoint: float
    start_utc: datetime
    end_utc: datetime
    end_date_new_york: date


def _midpoint(bar: QuoteBar) -> _Midpoint:
    return _Midpoint(
        high=(bar.bid_high + bar.ask_high) / 2.0,
        low=(bar.bid_low + bar.ask_low) / 2.0,
        close=(bar.bid_close + bar.ask_close) / 2.0,
    )


def _london_label(session_date: date, hour: int, minute: int = 0) -> datetime:
    return datetime.combine(session_date, time(hour, minute), tzinfo=LONDON).astimezone(
        timezone.utc
    )


def previous_completed_ny_session_bounds(london_date: date) -> tuple[datetime, datetime]:
    """Return the most recent completed Mon-Fri 17:00 New York FX session."""
    signal_start_utc = _london_label(london_date, 8)
    candidate_end_date = signal_start_utc.astimezone(NEW_YORK).date()

    while True:
        candidate_end = datetime.combine(
            candidate_end_date,
            time(17, 0),
            tzinfo=NEW_YORK,
        )
        if candidate_end_date.weekday() < 5 and candidate_end.astimezone(timezone.utc) < signal_start_utc:
            end_utc = candidate_end.astimezone(timezone.utc)
            start_local = datetime.combine(
                candidate_end_date - timedelta(days=1),
                time(17, 0),
                tzinfo=NEW_YORK,
            )
            return start_local.astimezone(timezone.utc), end_utc
        candidate_end_date -= timedelta(days=1)


def _labels(start_utc: datetime, end_utc: datetime, *, width: timedelta) -> tuple[datetime, ...]:
    labels: list[datetime] = []
    current = start_utc
    while current < end_utc:
        labels.append(current)
        current += width
    return tuple(labels)


def _eligible_signal_labels(
    london_date: date,
    *,
    width: timedelta,
) -> tuple[datetime, ...]:
    start = _london_label(london_date, 8)
    end = _london_label(london_date, 14)
    labels: list[datetime] = []
    current = start
    while current <= end:
        labels.append(current)
        current += width
    return tuple(labels)


def _required_signal_session_labels(
    london_date: date,
    *,
    width: timedelta,
) -> tuple[datetime, ...]:
    start = _london_label(london_date, 8) - width
    end = _london_label(london_date, 16)
    labels: list[datetime] = []
    current = start
    while current <= end:
        labels.append(current)
        current += width
    return tuple(labels)


def _session_dates(bars: Sequence[QuoteBar]) -> tuple[date, ...]:
    dates: set[date] = set()
    for bar in bars:
        local = bar.timestamp_utc.astimezone(LONDON)
        local_clock = local.timetz().replace(tzinfo=None)
        if time(8, 0) <= local_clock <= time(16, 0):
            dates.add(local.date())
    return tuple(sorted(dates))


def _candidate_id(
    *,
    symbol: str,
    session_date: date,
    config: PreviousDayRejectionConfig,
    suffix: str,
) -> str:
    return (
        f"PDR-{symbol}-{session_date:%Y%m%d}-{config.timeframe}-"
        f"B{config.buffer_pips}-{suffix}"
    )


def _base_metadata(
    *,
    session_date: date,
    config: PreviousDayRejectionConfig,
    reference_start: datetime,
    reference_end: datetime,
) -> dict[str, object]:
    return {
        "session_date": session_date.isoformat(),
        "signal_timezone": "Europe/London",
        "reference_timezone": "America/New_York",
        "timeframe": config.timeframe,
        "buffer_pips": config.buffer_pips,
        "reference_session_start_utc": reference_start,
        "reference_session_end_utc": reference_end,
        "reference_session_end_date_new_york": reference_end.astimezone(NEW_YORK).date().isoformat(),
    }


def _no_trade(
    *,
    symbol: str,
    session_date: date,
    config: PreviousDayRejectionConfig,
    observation_timestamp: datetime,
    reason_code: str,
    metadata: dict[str, object],
) -> SignalCandidate:
    width = timedelta(minutes=_TIMEFRAME_MINUTES[config.timeframe])
    return SignalCandidate(
        candidate_id=_candidate_id(
            symbol=symbol,
            session_date=session_date,
            config=config,
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


def _reference_levels(
    by_timestamp: dict[datetime, QuoteBar],
    *,
    london_date: date,
    width: timedelta,
) -> tuple[_ReferenceLevels | None, datetime | None]:
    start_utc, end_utc = previous_completed_ny_session_bounds(london_date)
    required = _labels(start_utc, end_utc, width=width)
    missing = next((label for label in required if label not in by_timestamp), None)
    if missing is not None:
        return None, missing

    mids = tuple(_midpoint(by_timestamp[label]) for label in required)
    high = max(item.high for item in mids)
    low = min(item.low for item in mids)
    return (
        _ReferenceLevels(
            high=high,
            low=low,
            midpoint=(high + low) / 2.0,
            start_utc=start_utc,
            end_utc=end_utc,
            end_date_new_york=end_utc.astimezone(NEW_YORK).date(),
        ),
        None,
    )


def generate_previous_day_rejection_candidates(
    bars: Sequence[QuoteBar],
    *,
    config: PreviousDayRejectionConfig,
) -> tuple[SignalCandidate, ...]:
    if not bars:
        return ()

    ordered = tuple(sorted(bars, key=lambda item: (item.timestamp_utc, item.symbol)))
    symbols = {bar.symbol for bar in ordered}
    if len(symbols) != 1:
        raise ValueError("previous-day rejection requires bars for exactly one symbol")
    symbol = next(iter(symbols))
    identities = [(bar.timestamp_utc, bar.symbol) for bar in ordered]
    if len(set(identities)) != len(identities):
        raise ValueError("duplicate quote-bar identity in previous-day rejection input")

    width = timedelta(minutes=_TIMEFRAME_MINUTES[config.timeframe])
    buffer = config.buffer_pips * pip_size(symbol)
    by_timestamp = {bar.timestamp_utc: bar for bar in ordered}
    out: list[SignalCandidate] = []

    for session_date in _session_dates(ordered):
        reference_start, reference_end = previous_completed_ny_session_bounds(session_date)
        metadata = _base_metadata(
            session_date=session_date,
            config=config,
            reference_start=reference_start,
            reference_end=reference_end,
        )

        required_signal = _required_signal_session_labels(session_date, width=width)
        missing_signal = next(
            (label for label in required_signal if label not in by_timestamp),
            None,
        )
        if missing_signal is not None:
            out.append(
                _no_trade(
                    symbol=symbol,
                    session_date=session_date,
                    config=config,
                    observation_timestamp=missing_signal,
                    reason_code="INCOMPLETE_SIGNAL_SESSION",
                    metadata={**metadata, "missing_timestamp_utc": missing_signal},
                )
            )
            continue

        levels, missing_reference = _reference_levels(
            by_timestamp,
            london_date=session_date,
            width=width,
        )
        if levels is None:
            out.append(
                _no_trade(
                    symbol=symbol,
                    session_date=session_date,
                    config=config,
                    observation_timestamp=_london_label(session_date, 8),
                    reason_code="INCOMPLETE_REFERENCE_SESSION",
                    metadata={**metadata, "missing_timestamp_utc": missing_reference},
                )
            )
            continue

        level_metadata = {
            **metadata,
            "previous_day_high": levels.high,
            "previous_day_low": levels.low,
            "previous_day_midpoint": levels.midpoint,
        }
        signal_labels = _eligible_signal_labels(session_date, width=width)
        emitted = False

        for label in signal_labels:
            previous_bar = by_timestamp[label - width]
            current_bar = by_timestamp[label]
            previous_mid = _midpoint(previous_bar)
            current_mid = _midpoint(current_bar)

            short_signal = (
                previous_mid.close <= levels.high
                and current_mid.high >= levels.high + buffer
                and current_mid.close < levels.high
            )
            long_signal = (
                previous_mid.close >= levels.low
                and current_mid.low <= levels.low - buffer
                and current_mid.close > levels.low
            )
            signal_metadata = {
                **level_metadata,
                "previous_mid_close": previous_mid.close,
                "signal_mid_high": current_mid.high,
                "signal_mid_low": current_mid.low,
                "signal_mid_close": current_mid.close,
            }

            if long_signal and short_signal:
                out.append(
                    _no_trade(
                        symbol=symbol,
                        session_date=session_date,
                        config=config,
                        observation_timestamp=label,
                        reason_code="AMBIGUOUS_DUAL_REJECTION",
                        metadata=signal_metadata,
                    )
                )
                emitted = True
                break

            if not long_signal and not short_signal:
                continue

            direction = Direction.LONG if long_signal else Direction.SHORT
            stop_price = current_mid.low if direction is Direction.LONG else current_mid.high
            out.append(
                SignalCandidate(
                    candidate_id=_candidate_id(
                        symbol=symbol,
                        session_date=session_date,
                        config=config,
                        suffix=direction.value,
                    ),
                    symbol=symbol,
                    observation_bar_timestamp_utc=label,
                    signal_known_timestamp_utc=label + width,
                    direction=direction,
                    stop_price=stop_price,
                    target_price=levels.midpoint,
                    latest_exit_timestamp_utc=_london_label(session_date, 16),
                    reason_code=f"PREVIOUS_DAY_REJECTION_{direction.value}",
                    metadata=signal_metadata,
                )
            )
            emitted = True
            break

        if not emitted:
            out.append(
                _no_trade(
                    symbol=symbol,
                    session_date=session_date,
                    config=config,
                    observation_timestamp=signal_labels[-1],
                    reason_code="NO_REJECTION",
                    metadata=level_metadata,
                )
            )

    return tuple(out)
