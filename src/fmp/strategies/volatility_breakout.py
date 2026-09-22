from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
import math
from statistics import median
from typing import Sequence
from zoneinfo import ZoneInfo

from fmp.contracts import Direction, QuoteBar
from fmp.strategies.contracts import SignalCandidate


LONDON = ZoneInfo("Europe/London")
_TIMEFRAME_MINUTES = {"5m": 5, "15m": 15, "1h": 60}
_PHASE4_MULTIPLIERS = frozenset({1.0, 1.5, 2.0})
_EXP015_MULTIPLIERS = frozenset({0.75, 1.25, 1.75, 2.25, 2.5})
_REFERENCE_HOURS = 8


@dataclass(frozen=True, slots=True)
class VolatilityBreakoutConfig:
    range_multiplier: float
    timeframe: str
    parameter_region: str = "phase4"

    def __post_init__(self) -> None:
        if self.parameter_region == "phase4":
            allowed = _PHASE4_MULTIPLIERS
        elif self.parameter_region == "exp015":
            allowed = _EXP015_MULTIPLIERS
        else:
            raise ValueError("unsupported volatility-breakout parameter_region")
        if self.range_multiplier not in allowed:
            raise ValueError("range_multiplier is outside the selected parameter region")
        if self.timeframe not in _TIMEFRAME_MINUTES:
            raise ValueError("timeframe must be one of 5m, 15m, or 1h")


@dataclass(frozen=True, slots=True)
class _Midpoint:
    high: float
    low: float
    close: float


@dataclass(frozen=True, slots=True)
class _Reference:
    high: float
    low: float
    median_range: float
    start_utc: datetime
    end_utc: datetime


def _midpoint(bar: QuoteBar) -> _Midpoint:
    return _Midpoint(
        high=(bar.bid_high + bar.ask_high) / 2.0,
        low=(bar.bid_low + bar.ask_low) / 2.0,
        close=(bar.bid_close + bar.ask_close) / 2.0,
    )


def _valid_midpoint(value: _Midpoint) -> bool:
    return (
        math.isfinite(value.high)
        and math.isfinite(value.low)
        and math.isfinite(value.close)
        and value.high >= value.low
    )


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


def _eligible_signal_labels(
    session_date: date,
    *,
    width: timedelta,
) -> tuple[datetime, ...]:
    return _labels(
        _london_label(session_date, 8),
        _london_label(session_date, 14),
        width=width,
        include_end=True,
    )


def _required_session_labels(
    session_date: date,
    *,
    width: timedelta,
) -> tuple[datetime, ...]:
    return _labels(
        _london_label(session_date, 0),
        _london_label(session_date, 16),
        width=width,
        include_end=True,
    )


def _session_dates(bars: Sequence[QuoteBar]) -> tuple[date, ...]:
    dates: set[date] = set()
    for bar in bars:
        local = bar.timestamp_utc.astimezone(LONDON)
        clock = local.timetz().replace(tzinfo=None)
        if time(8, 0) <= clock <= time(16, 0):
            dates.add(local.date())
    return tuple(sorted(dates))


def _multiplier_token(value: float) -> str:
    return f"{value:.1f}".replace(".", "p")


def _candidate_id(
    *,
    symbol: str,
    session_date: date,
    config: VolatilityBreakoutConfig,
    suffix: str,
) -> str:
    return (
        f"VB-{symbol}-{session_date:%Y%m%d}-{config.timeframe}-"
        f"M{_multiplier_token(config.range_multiplier)}-{suffix}"
    )


def _base_metadata(
    *,
    session_date: date,
    config: VolatilityBreakoutConfig,
) -> dict[str, object]:
    return {
        "session_date": session_date.isoformat(),
        "signal_timezone": "Europe/London",
        "timeframe": config.timeframe,
        "range_multiplier": config.range_multiplier,
        "reference_hours": _REFERENCE_HOURS,
    }


def _no_trade(
    *,
    symbol: str,
    session_date: date,
    config: VolatilityBreakoutConfig,
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


def _reference_for_label(
    by_timestamp: dict[datetime, QuoteBar],
    *,
    label: datetime,
    width: timedelta,
) -> _Reference | None:
    start = label - timedelta(hours=_REFERENCE_HOURS)
    required = _labels(start, label, width=width, include_end=False)
    if any(item not in by_timestamp for item in required):
        return None

    mids = tuple(_midpoint(by_timestamp[item]) for item in required)
    if not mids or any(not _valid_midpoint(item) for item in mids):
        return None
    ranges = tuple(item.high - item.low for item in mids)
    reference_median_range = float(median(ranges))
    if not math.isfinite(reference_median_range) or reference_median_range <= 0:
        return None
    return _Reference(
        high=max(item.high for item in mids),
        low=min(item.low for item in mids),
        median_range=reference_median_range,
        start_utc=start,
        end_utc=label,
    )


def _at_least(value: float, threshold: float) -> bool:
    return value > threshold or math.isclose(
        value,
        threshold,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )


def generate_volatility_breakout_candidates(
    bars: Sequence[QuoteBar],
    *,
    config: VolatilityBreakoutConfig,
) -> tuple[SignalCandidate, ...]:
    if not bars:
        return ()

    ordered = tuple(sorted(bars, key=lambda item: (item.timestamp_utc, item.symbol)))
    symbols = {bar.symbol for bar in ordered}
    if len(symbols) != 1:
        raise ValueError("volatility breakout requires bars for exactly one symbol")
    symbol = next(iter(symbols))
    identities = [(bar.timestamp_utc, bar.symbol) for bar in ordered]
    if len(set(identities)) != len(identities):
        raise ValueError("duplicate quote-bar identity in volatility breakout input")

    width = timedelta(minutes=_TIMEFRAME_MINUTES[config.timeframe])
    by_timestamp = {bar.timestamp_utc: bar for bar in ordered}
    out: list[SignalCandidate] = []

    for session_date in _session_dates(ordered):
        metadata = _base_metadata(session_date=session_date, config=config)
        required = _required_session_labels(session_date, width=width)
        missing = next((label for label in required if label not in by_timestamp), None)
        if missing is not None:
            out.append(
                _no_trade(
                    symbol=symbol,
                    session_date=session_date,
                    config=config,
                    observation_timestamp=missing,
                    reason_code="INCOMPLETE_VOLATILITY_SESSION",
                    metadata={**metadata, "missing_timestamp_utc": missing},
                )
            )
            continue

        signal_labels = _eligible_signal_labels(session_date, width=width)
        emitted = False
        last_reference_metadata: dict[str, object] = dict(metadata)

        for label in signal_labels:
            reference = _reference_for_label(
                by_timestamp,
                label=label,
                width=width,
            )
            if reference is None:
                out.append(
                    _no_trade(
                        symbol=symbol,
                        session_date=session_date,
                        config=config,
                        observation_timestamp=label,
                        reason_code="INCOMPLETE_VOLATILITY_SESSION",
                        metadata={**metadata, "reference_end_utc": label},
                    )
                )
                emitted = True
                break

            current = _midpoint(by_timestamp[label])
            if not _valid_midpoint(current):
                out.append(
                    _no_trade(
                        symbol=symbol,
                        session_date=session_date,
                        config=config,
                        observation_timestamp=label,
                        reason_code="INVALID_VOLATILITY_BAR",
                        metadata=metadata,
                    )
                )
                emitted = True
                break

            current_range = current.high - current.low
            threshold = config.range_multiplier * reference.median_range
            range_ok = _at_least(current_range, threshold)
            long_signal = current.close > reference.high and range_ok
            short_signal = current.close < reference.low and range_ok
            signal_metadata = {
                **metadata,
                "reference_start_utc": reference.start_utc,
                "reference_end_utc": reference.end_utc,
                "reference_high": reference.high,
                "reference_low": reference.low,
                "reference_median_range": reference.median_range,
                "signal_mid_high": current.high,
                "signal_mid_low": current.low,
                "signal_mid_close": current.close,
                "signal_mid_range": current_range,
                "range_threshold": threshold,
                "range_expansion_ratio": current_range / reference.median_range,
            }
            last_reference_metadata = signal_metadata

            if long_signal and short_signal:
                out.append(
                    _no_trade(
                        symbol=symbol,
                        session_date=session_date,
                        config=config,
                        observation_timestamp=label,
                        reason_code="AMBIGUOUS_VOLATILITY_BREAKOUT",
                        metadata=signal_metadata,
                    )
                )
                emitted = True
                break
            if not long_signal and not short_signal:
                continue

            direction = Direction.LONG if long_signal else Direction.SHORT
            stop_price = current.low if direction is Direction.LONG else current.high
            risk = (
                current.close - stop_price
                if direction is Direction.LONG
                else stop_price - current.close
            )
            if not math.isfinite(risk) or risk <= 0:
                out.append(
                    _no_trade(
                        symbol=symbol,
                        session_date=session_date,
                        config=config,
                        observation_timestamp=label,
                        reason_code="INVALID_VOLATILITY_GEOMETRY",
                        metadata=signal_metadata,
                    )
                )
                emitted = True
                break

            target_price = (
                current.close + risk
                if direction is Direction.LONG
                else current.close - risk
            )
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
                    target_price=target_price,
                    latest_exit_timestamp_utc=_london_label(session_date, 16),
                    reason_code=f"VOLATILITY_BREAKOUT_{direction.value}",
                    metadata={**signal_metadata, "signal_r": risk},
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
                    reason_code="NO_VOLATILITY_BREAKOUT",
                    metadata=last_reference_metadata,
                )
            )

    return tuple(out)
