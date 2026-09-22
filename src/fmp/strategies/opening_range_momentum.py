from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
import math
from typing import Sequence
from zoneinfo import ZoneInfo

from fmp.backtest.costs import pip_size
from fmp.contracts import Direction, QuoteBar
from fmp.strategies.contracts import SignalCandidate


LONDON = ZoneInfo("Europe/London")
_TIMEFRAME_MINUTES = {"5m": 5, "15m": 15, "1h": 60}
_ALLOWED_BODY_FRACTIONS = frozenset({0.50, 0.70})
_ALLOWED_TARGET_R = frozenset({1.0, 1.5})
BREAKOUT_BUFFER_PIPS = 2
STOP_DEPTH_REFERENCE_FRACTION = 0.25


@dataclass(frozen=True, slots=True)
class OpeningRangeMomentumConfig:
    body_fraction_threshold: float
    target_r_multiple: float
    timeframe: str

    def __post_init__(self) -> None:
        if self.body_fraction_threshold not in _ALLOWED_BODY_FRACTIONS:
            raise ValueError("body_fraction_threshold must be one of 0.50 or 0.70")
        if self.target_r_multiple not in _ALLOWED_TARGET_R:
            raise ValueError("target_r_multiple must be one of 1.0 or 1.5")
        if self.timeframe not in _TIMEFRAME_MINUTES:
            raise ValueError("timeframe must be one of 5m, 15m, or 1h")


@dataclass(frozen=True, slots=True)
class _Midpoint:
    open: float
    high: float
    low: float
    close: float


def _midpoint(bar: QuoteBar) -> _Midpoint:
    return _Midpoint(
        open=(bar.bid_open + bar.ask_open) / 2.0,
        high=(bar.bid_high + bar.ask_high) / 2.0,
        low=(bar.bid_low + bar.ask_low) / 2.0,
        close=(bar.bid_close + bar.ask_close) / 2.0,
    )


def _local_label(session_date: date, hour: int, minute: int = 0) -> datetime:
    return datetime.combine(
        session_date,
        time(hour, minute),
        tzinfo=LONDON,
    ).astimezone(timezone.utc)


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


def _session_dates(bars: Sequence[QuoteBar]) -> tuple[date, ...]:
    dates: set[date] = set()
    for item in bars:
        local = item.timestamp_utc.astimezone(LONDON)
        clock = local.timetz().replace(tzinfo=None)
        if time(6, 0) <= clock <= time(16, 0):
            dates.add(local.date())
    return tuple(sorted(dates))


def _token(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".").replace(".", "p")


def _candidate_id(
    *,
    symbol: str,
    session_date: date,
    config: OpeningRangeMomentumConfig,
    suffix: str,
) -> str:
    return (
        f"ORM-{symbol}-{session_date:%Y%m%d}-{config.timeframe}-"
        f"B{BREAKOUT_BUFFER_PIPS}-F{_token(config.body_fraction_threshold)}-"
        f"R{_token(config.target_r_multiple)}-{suffix}"
    )


def _base_metadata(
    *,
    session_date: date,
    config: OpeningRangeMomentumConfig,
    breakout_buffer_price: float,
) -> dict[str, object]:
    return {
        "session_date": session_date.isoformat(),
        "timezone": "Europe/London",
        "timeframe": config.timeframe,
        "reference_start_local": "06:00",
        "reference_end_local": "08:00",
        "signal_start_local": "08:00",
        "signal_end_local": "12:00",
        "flat_local": "16:00",
        "breakout_buffer_pips": BREAKOUT_BUFFER_PIPS,
        "breakout_buffer_price": breakout_buffer_price,
        "body_fraction_threshold": config.body_fraction_threshold,
        "target_r_multiple": config.target_r_multiple,
        "stop_depth_reference_fraction": STOP_DEPTH_REFERENCE_FRACTION,
    }


def _no_trade(
    *,
    symbol: str,
    session_date: date,
    config: OpeningRangeMomentumConfig,
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


def generate_opening_range_momentum_candidates(
    bars: Sequence[QuoteBar],
    *,
    config: OpeningRangeMomentumConfig,
    require_scheduled_exit_bar: bool = True,
) -> tuple[SignalCandidate, ...]:
    if type(require_scheduled_exit_bar) is not bool:
        raise TypeError("require_scheduled_exit_bar must be bool")
    if not bars:
        return ()

    ordered = tuple(sorted(bars, key=lambda item: (item.timestamp_utc, item.symbol)))
    symbols = {item.symbol for item in ordered}
    if len(symbols) != 1:
        raise ValueError("opening-range momentum requires bars for exactly one symbol")
    symbol = next(iter(symbols))
    identities = [(item.timestamp_utc, item.symbol) for item in ordered]
    if len(set(identities)) != len(identities):
        raise ValueError("duplicate quote-bar identity in opening-range momentum input")

    by_timestamp = {item.timestamp_utc: item for item in ordered}
    width_minutes = _TIMEFRAME_MINUTES[config.timeframe]
    width = timedelta(minutes=width_minutes)
    breakout_buffer_price = BREAKOUT_BUFFER_PIPS * pip_size(symbol)
    out: list[SignalCandidate] = []

    for session_date in _session_dates(ordered):
        reference_labels = _window_labels(
            session_date,
            start_hour=6,
            end_hour=8,
            width_minutes=width_minutes,
        )
        signal_labels = _window_labels(
            session_date,
            start_hour=8,
            end_hour=12,
            width_minutes=width_minutes,
        )
        exit_timestamp = _local_label(session_date, 16)
        base = _base_metadata(
            session_date=session_date,
            config=config,
            breakout_buffer_price=breakout_buffer_price,
        )

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
                    reason_code="INCOMPLETE_SESSION",
                    metadata={**base, "missing_timestamp_utc": missing_reference},
                )
            )
            continue

        if require_scheduled_exit_bar and exit_timestamp not in by_timestamp:
            out.append(
                _no_trade(
                    symbol=symbol,
                    session_date=session_date,
                    config=config,
                    observation_timestamp=reference_labels[-1],
                    reason_code="INCOMPLETE_SESSION",
                    metadata={**base, "missing_timestamp_utc": exit_timestamp},
                )
            )
            continue

        reference = [_midpoint(by_timestamp[label]) for label in reference_labels]
        reference_high = max(item.high for item in reference)
        reference_low = min(item.low for item in reference)
        reference_width = reference_high - reference_low
        reference_metadata = {
            **base,
            "reference_high": reference_high,
            "reference_low": reference_low,
            "reference_width": reference_width,
        }

        if (
            not math.isfinite(reference_width)
            or reference_width <= 0.0
            or not math.isfinite(reference_high)
            or not math.isfinite(reference_low)
        ):
            out.append(
                _no_trade(
                    symbol=symbol,
                    session_date=session_date,
                    config=config,
                    observation_timestamp=reference_labels[-1],
                    reason_code="INVALID_REFERENCE_RANGE",
                    metadata=reference_metadata,
                )
            )
            continue

        emitted = False
        for label in signal_labels:
            source_bar = by_timestamp.get(label)
            if source_bar is None:
                out.append(
                    _no_trade(
                        symbol=symbol,
                        session_date=session_date,
                        config=config,
                        observation_timestamp=label,
                        reason_code="INCOMPLETE_SESSION",
                        metadata={**reference_metadata, "missing_timestamp_utc": label},
                    )
                )
                emitted = True
                break

            midpoint = _midpoint(source_bar)
            candle_range = midpoint.high - midpoint.low
            body = abs(midpoint.close - midpoint.open)
            body_fraction = (
                body / candle_range
                if math.isfinite(candle_range) and candle_range > 0.0
                else None
            )
            observation_metadata = {
                **reference_metadata,
                "signal_mid_open": midpoint.open,
                "signal_mid_high": midpoint.high,
                "signal_mid_low": midpoint.low,
                "signal_mid_close": midpoint.close,
                "candle_range": candle_range,
                "body": body,
                "body_fraction": body_fraction,
            }
            if body_fraction is None or not math.isfinite(body_fraction):
                continue

            long_qualifies = (
                midpoint.close > reference_high + breakout_buffer_price
                and midpoint.close > midpoint.open
                and body_fraction >= config.body_fraction_threshold
            )
            short_qualifies = (
                midpoint.close < reference_low - breakout_buffer_price
                and midpoint.close < midpoint.open
                and body_fraction >= config.body_fraction_threshold
            )
            if long_qualifies and short_qualifies:
                out.append(
                    _no_trade(
                        symbol=symbol,
                        session_date=session_date,
                        config=config,
                        observation_timestamp=label,
                        reason_code="INVALID_DIRECTIONAL_SIGNAL",
                        metadata=observation_metadata,
                    )
                )
                emitted = True
                break
            if not long_qualifies and not short_qualifies:
                continue

            direction = Direction.LONG if long_qualifies else Direction.SHORT
            if direction is Direction.LONG:
                stop = reference_high - STOP_DEPTH_REFERENCE_FRACTION * reference_width
                risk_reference = midpoint.close - stop
                target = midpoint.close + config.target_r_multiple * risk_reference
            else:
                stop = reference_low + STOP_DEPTH_REFERENCE_FRACTION * reference_width
                risk_reference = stop - midpoint.close
                target = midpoint.close - config.target_r_multiple * risk_reference

            if (
                not math.isfinite(stop)
                or stop <= 0.0
                or not math.isfinite(risk_reference)
                or risk_reference <= 0.0
                or not math.isfinite(target)
                or target <= 0.0
            ):
                out.append(
                    _no_trade(
                        symbol=symbol,
                        session_date=session_date,
                        config=config,
                        observation_timestamp=label,
                        reason_code="INVALID_GEOMETRY",
                        metadata={
                            **observation_metadata,
                            "stop_price": stop,
                            "risk_reference": risk_reference,
                            "target_price": target,
                        },
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
                    stop_price=stop,
                    target_price=target,
                    latest_exit_timestamp_utc=exit_timestamp,
                    reason_code=f"OPENING_RANGE_MOMENTUM_{direction.value}",
                    metadata={
                        **observation_metadata,
                        "stop_price": stop,
                        "risk_reference": risk_reference,
                        "target_price": target,
                    },
                )
            )
            emitted = True
            break

        if not emitted:
            final_label = signal_labels[-1]
            out.append(
                _no_trade(
                    symbol=symbol,
                    session_date=session_date,
                    config=config,
                    observation_timestamp=final_label,
                    reason_code="NO_QUALIFYING_MOMENTUM",
                    metadata=reference_metadata,
                )
            )

    return tuple(out)
