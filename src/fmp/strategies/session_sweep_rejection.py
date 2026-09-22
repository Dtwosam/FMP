from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from math import isfinite
from typing import Sequence
from zoneinfo import ZoneInfo

from fmp.backtest.costs import pip_size
from fmp.contracts import Direction, QuoteBar
from fmp.strategies.contracts import SignalCandidate


LONDON = ZoneInfo("Europe/London")
_TIMEFRAME_MINUTES = {"5m": 5, "15m": 15, "1h": 60}
_ALLOWED_BUFFERS = frozenset({0, 1, 2, 3, 4, 5, 6, 8})


@dataclass(frozen=True, slots=True)
class SessionSweepRejectionConfig:
    buffer_pips: int
    timeframe: str

    def __post_init__(self) -> None:
        if self.buffer_pips not in _ALLOWED_BUFFERS:
            raise ValueError("buffer_pips is outside the approved strategy grids")
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


def _finite_midpoint(item: _Midpoint) -> bool:
    return isfinite(item.high) and isfinite(item.low) and isfinite(item.close)


def _london_label(session_date: date, hour: int, minute: int = 0) -> datetime:
    return datetime.combine(session_date, time(hour, minute), tzinfo=LONDON).astimezone(
        timezone.utc
    )


def _labels(
    start_utc: datetime,
    end_utc: datetime,
    *,
    width: timedelta,
    include_end: bool,
) -> tuple[datetime, ...]:
    labels: list[datetime] = []
    current = start_utc
    while current < end_utc or (include_end and current == end_utc):
        labels.append(current)
        current += width
    return tuple(labels)


def _reference_labels(session_date: date, *, width: timedelta) -> tuple[datetime, ...]:
    return _labels(
        _london_label(session_date, 0),
        _london_label(session_date, 8),
        width=width,
        include_end=False,
    )


def _eligible_signal_labels(session_date: date, *, width: timedelta) -> tuple[datetime, ...]:
    return _labels(
        _london_label(session_date, 8),
        _london_label(session_date, 14),
        width=width,
        include_end=True,
    )


def _required_signal_labels(session_date: date, *, width: timedelta) -> tuple[datetime, ...]:
    return _labels(
        _london_label(session_date, 8),
        _london_label(session_date, 16),
        width=width,
        include_end=True,
    )


def _session_dates(bars: Sequence[QuoteBar]) -> tuple[date, ...]:
    dates: set[date] = set()
    for bar in bars:
        local = bar.timestamp_utc.astimezone(LONDON)
        local_clock = local.timetz().replace(tzinfo=None)
        if time(0, 0) <= local_clock <= time(16, 0):
            dates.add(local.date())
    return tuple(sorted(dates))


def _candidate_id(
    *,
    symbol: str,
    session_date: date,
    config: SessionSweepRejectionConfig,
    suffix: str,
) -> str:
    return (
        f"SSR-{symbol}-{session_date:%Y%m%d}-{config.timeframe}-"
        f"B{config.buffer_pips}-{suffix}"
    )


def _base_metadata(
    *,
    session_date: date,
    config: SessionSweepRejectionConfig,
) -> dict[str, object]:
    return {
        "session_date": session_date.isoformat(),
        "timezone": "Europe/London",
        "timeframe": config.timeframe,
        "buffer_pips": config.buffer_pips,
        "reference_session_start_utc": _london_label(session_date, 0),
        "reference_session_end_utc": _london_label(session_date, 8),
    }


def _no_trade(
    *,
    symbol: str,
    session_date: date,
    config: SessionSweepRejectionConfig,
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


def generate_session_sweep_rejection_candidates(
    bars: Sequence[QuoteBar],
    *,
    config: SessionSweepRejectionConfig,
) -> tuple[SignalCandidate, ...]:
    if not bars:
        return ()

    ordered = tuple(sorted(bars, key=lambda item: (item.timestamp_utc, item.symbol)))
    symbols = {bar.symbol for bar in ordered}
    if len(symbols) != 1:
        raise ValueError("session sweep rejection requires bars for exactly one symbol")
    symbol = next(iter(symbols))
    identities = [(bar.timestamp_utc, bar.symbol) for bar in ordered]
    if len(set(identities)) != len(identities):
        raise ValueError("duplicate quote-bar identity in session sweep rejection input")

    width = timedelta(minutes=_TIMEFRAME_MINUTES[config.timeframe])
    buffer = config.buffer_pips * pip_size(symbol)
    by_timestamp = {bar.timestamp_utc: bar for bar in ordered}
    out: list[SignalCandidate] = []

    for session_date in _session_dates(ordered):
        metadata = _base_metadata(session_date=session_date, config=config)
        reference_labels = _reference_labels(session_date, width=width)
        missing_reference = next(
            (label for label in reference_labels if label not in by_timestamp),
            None,
        )
        if missing_reference is not None:
            out.append(
                _no_trade(
                    symbol=symbol,
                    session_date=session_date,
                    config=config,
                    observation_timestamp=missing_reference,
                    reason_code="INCOMPLETE_REFERENCE_SESSION",
                    metadata={**metadata, "missing_timestamp_utc": missing_reference},
                )
            )
            continue

        reference_midpoints = tuple(_midpoint(by_timestamp[label]) for label in reference_labels)
        malformed_reference = next(
            (
                label
                for label, midpoint in zip(reference_labels, reference_midpoints, strict=True)
                if not _finite_midpoint(midpoint)
            ),
            None,
        )
        if malformed_reference is not None:
            out.append(
                _no_trade(
                    symbol=symbol,
                    session_date=session_date,
                    config=config,
                    observation_timestamp=malformed_reference,
                    reason_code="INVALID_REFERENCE_SESSION",
                    metadata={**metadata, "invalid_timestamp_utc": malformed_reference},
                )
            )
            continue

        reference_high = max(item.high for item in reference_midpoints)
        reference_low = min(item.low for item in reference_midpoints)
        reference_midpoint = (reference_high + reference_low) / 2.0
        level_metadata = {
            **metadata,
            "reference_high": reference_high,
            "reference_low": reference_low,
            "reference_midpoint": reference_midpoint,
        }
        if not (
            isfinite(reference_high)
            and isfinite(reference_low)
            and isfinite(reference_midpoint)
            and reference_high > reference_low
        ):
            out.append(
                _no_trade(
                    symbol=symbol,
                    session_date=session_date,
                    config=config,
                    observation_timestamp=_london_label(session_date, 8),
                    reason_code="INVALID_REFERENCE_SESSION",
                    metadata=level_metadata,
                )
            )
            continue

        required_signal = _required_signal_labels(session_date, width=width)
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
                    metadata={**level_metadata, "missing_timestamp_utc": missing_signal},
                )
            )
            continue

        invalid_signal = next(
            (
                label
                for label in required_signal
                if not _finite_midpoint(_midpoint(by_timestamp[label]))
            ),
            None,
        )
        if invalid_signal is not None:
            out.append(
                _no_trade(
                    symbol=symbol,
                    session_date=session_date,
                    config=config,
                    observation_timestamp=invalid_signal,
                    reason_code="INCOMPLETE_SIGNAL_SESSION",
                    metadata={**level_metadata, "invalid_timestamp_utc": invalid_signal},
                )
            )
            continue

        emitted = False
        for label in _eligible_signal_labels(session_date, width=width):
            previous_mid = _midpoint(by_timestamp[label - width])
            current_mid = _midpoint(by_timestamp[label])
            short_signal = (
                previous_mid.close <= reference_high
                and current_mid.high >= reference_high + buffer
                and current_mid.close < reference_high
            )
            long_signal = (
                previous_mid.close >= reference_low
                and current_mid.low <= reference_low - buffer
                and current_mid.close > reference_low
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
                        reason_code="AMBIGUOUS_DUAL_SESSION_SWEEP",
                        metadata=signal_metadata,
                    )
                )
                emitted = True
                break

            if not long_signal and not short_signal:
                continue

            direction = Direction.LONG if long_signal else Direction.SHORT
            stop_price = current_mid.low if direction is Direction.LONG else current_mid.high
            valid_geometry = (
                stop_price < current_mid.close < reference_midpoint
                if direction is Direction.LONG
                else reference_midpoint < current_mid.close < stop_price
            )
            if not valid_geometry:
                out.append(
                    _no_trade(
                        symbol=symbol,
                        session_date=session_date,
                        config=config,
                        observation_timestamp=label,
                        reason_code="INVALID_SESSION_SWEEP_GEOMETRY",
                        metadata=signal_metadata,
                    )
                )
                emitted = True
                break

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
                    target_price=reference_midpoint,
                    latest_exit_timestamp_utc=_london_label(session_date, 16),
                    reason_code=f"SESSION_SWEEP_REJECTION_{direction.value}",
                    metadata=signal_metadata,
                )
            )
            emitted = True
            break

        if not emitted:
            signal_labels = _eligible_signal_labels(session_date, width=width)
            out.append(
                _no_trade(
                    symbol=symbol,
                    session_date=session_date,
                    config=config,
                    observation_timestamp=signal_labels[-1],
                    reason_code="NO_SESSION_SWEEP_REJECTION",
                    metadata=level_metadata,
                )
            )

    return tuple(out)
