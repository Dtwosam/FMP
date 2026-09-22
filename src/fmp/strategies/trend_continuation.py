from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Sequence
from zoneinfo import ZoneInfo

from fmp.contracts import Direction, QuoteBar
from fmp.strategies.contracts import SignalCandidate


LONDON = ZoneInfo("Europe/London")
_TIMEFRAME_MINUTES = {"5m": 5, "15m": 15, "1h": 60}
_TREND_WINDOWS = {"A": (2, 8), "B": (4, 16), "C": (8, 32)}
_PHASE4_TARGET_R = frozenset({1.0, 1.5})
_EXP015_TARGET_R = frozenset({0.75, 1.25, 1.75, 2.0})


@dataclass(frozen=True, slots=True)
class TrendContinuationConfig:
    trend_window_id: str
    target_r_multiple: float
    timeframe: str
    parameter_region: str = "phase4"

    def __post_init__(self) -> None:
        if self.trend_window_id not in _TREND_WINDOWS:
            raise ValueError("trend_window_id must be one of A, B, or C")
        if self.parameter_region == "phase4":
            targets = _PHASE4_TARGET_R
        elif self.parameter_region == "exp015":
            targets = _EXP015_TARGET_R
        else:
            raise ValueError("unsupported trend-continuation parameter_region")
        if self.target_r_multiple not in targets:
            raise ValueError("target_r_multiple is outside the selected parameter region")
        if self.timeframe not in _TIMEFRAME_MINUTES:
            raise ValueError("timeframe must be one of 5m, 15m, or 1h")


def duration_to_bars(timeframe: str, hours: int) -> int:
    try:
        width_minutes = _TIMEFRAME_MINUTES[timeframe]
    except KeyError as exc:
        raise ValueError("timeframe must be one of 5m, 15m, or 1h") from exc
    if not isinstance(hours, int) or isinstance(hours, bool) or hours <= 0:
        raise ValueError("hours must be a positive integer")
    duration_minutes = hours * 60
    if duration_minutes % width_minutes:
        raise ValueError("duration must be exactly divisible by timeframe width")
    return duration_minutes // width_minutes


def _midpoint_close(bar: QuoteBar) -> float:
    return (bar.bid_close + bar.ask_close) / 2.0


def _midpoint_high(bar: QuoteBar) -> float:
    return (bar.bid_high + bar.ask_high) / 2.0


def _midpoint_low(bar: QuoteBar) -> float:
    return (bar.bid_low + bar.ask_low) / 2.0


def _trend_context(
    bars: Sequence[QuoteBar],
    *,
    end_index: int,
    fast_count: int,
    slow_count: int,
    width: timedelta,
) -> Direction | None:
    if fast_count <= 0 or slow_count <= 0 or fast_count > slow_count:
        raise ValueError("SMA counts must be positive with fast_count <= slow_count")
    if width <= timedelta(0):
        raise ValueError("width must be positive")
    if end_index < 0 or end_index >= len(bars):
        return None

    first_required = end_index - slow_count
    if first_required < 0:
        return None
    required = bars[first_required : end_index + 1]
    if len(required) != slow_count + 1:
        return None
    if any(
        current.timestamp_utc - previous.timestamp_utc != width
        for previous, current in zip(required, required[1:])
    ):
        return None

    current_fast = bars[end_index - fast_count + 1 : end_index + 1]
    current_slow = bars[end_index - slow_count + 1 : end_index + 1]
    previous_slow = bars[end_index - slow_count : end_index]

    fast_sma = sum(_midpoint_close(bar) for bar in current_fast) / fast_count
    slow_sma = sum(_midpoint_close(bar) for bar in current_slow) / slow_count
    previous_slow_sma = sum(_midpoint_close(bar) for bar in previous_slow) / slow_count

    if fast_sma > slow_sma and slow_sma > previous_slow_sma:
        return Direction.LONG
    if fast_sma < slow_sma and slow_sma < previous_slow_sma:
        return Direction.SHORT
    return None


def _fast_sma(bars: Sequence[QuoteBar], *, end_index: int, fast_count: int) -> float:
    window = bars[end_index - fast_count + 1 : end_index + 1]
    return sum(_midpoint_close(bar) for bar in window) / fast_count


def _local_label(session_date: date, hour: int) -> datetime:
    return datetime.combine(session_date, time(hour, 0), tzinfo=LONDON).astimezone(timezone.utc)


def _eligible_labels(session_date: date, *, width_minutes: int) -> tuple[datetime, ...]:
    start = datetime.combine(session_date, time(8, 0), tzinfo=LONDON)
    end = datetime.combine(session_date, time(14, 0), tzinfo=LONDON)
    labels: list[datetime] = []
    current = start
    while current <= end:
        labels.append(current.astimezone(timezone.utc))
        current += timedelta(minutes=width_minutes)
    return tuple(labels)


def _session_dates(bars: Sequence[QuoteBar]) -> tuple[date, ...]:
    dates: set[date] = set()
    for bar in bars:
        local = bar.timestamp_utc.astimezone(LONDON)
        local_time = local.timetz().replace(tzinfo=None)
        if time(8, 0) <= local_time <= time(16, 0):
            dates.add(local.date())
    return tuple(sorted(dates))


def _candidate_id(
    *,
    symbol: str,
    session_date: date,
    config: TrendContinuationConfig,
    suffix: str,
) -> str:
    multiple = str(config.target_r_multiple).replace(".", "p")
    return (
        f"TC-{symbol}-{session_date:%Y%m%d}-{config.timeframe}-"
        f"{config.trend_window_id}-R{multiple}-{suffix}"
    )


def _no_trade(
    *,
    symbol: str,
    session_date: date,
    config: TrendContinuationConfig,
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


def generate_trend_continuation_candidates(
    bars: Sequence[QuoteBar],
    *,
    config: TrendContinuationConfig,
) -> tuple[SignalCandidate, ...]:
    if not bars:
        return ()

    ordered = tuple(sorted(bars, key=lambda item: (item.timestamp_utc, item.symbol)))
    symbols = {bar.symbol for bar in ordered}
    if len(symbols) != 1:
        raise ValueError("trend continuation requires bars for exactly one symbol")
    symbol = next(iter(symbols))
    identities = [(bar.timestamp_utc, bar.symbol) for bar in ordered]
    if len(set(identities)) != len(identities):
        raise ValueError("duplicate quote-bar identity in trend continuation input")

    width_minutes = _TIMEFRAME_MINUTES[config.timeframe]
    width = timedelta(minutes=width_minutes)
    fast_hours, slow_hours = _TREND_WINDOWS[config.trend_window_id]
    fast_count = duration_to_bars(config.timeframe, fast_hours)
    slow_count = duration_to_bars(config.timeframe, slow_hours)
    by_timestamp = {bar.timestamp_utc: bar for bar in ordered}
    index_by_timestamp = {bar.timestamp_utc: index for index, bar in enumerate(ordered)}
    out: list[SignalCandidate] = []

    for session_date in _session_dates(ordered):
        exit_timestamp = _local_label(session_date, 16)
        labels = _eligible_labels(session_date, width_minutes=width_minutes)
        base_metadata: dict[str, object] = {
            "session_date": session_date.isoformat(),
            "timezone": "Europe/London",
            "timeframe": config.timeframe,
            "trend_window_id": config.trend_window_id,
            "fast_hours": fast_hours,
            "slow_hours": slow_hours,
            "target_r_multiple": config.target_r_multiple,
        }

        if exit_timestamp not in by_timestamp:
            out.append(
                _no_trade(
                    symbol=symbol,
                    session_date=session_date,
                    config=config,
                    observation_timestamp=labels[-1],
                    reason_code="INCOMPLETE_SESSION",
                    metadata={**base_metadata, "missing_timestamp_utc": exit_timestamp},
                )
            )
            continue

        emitted = False
        for label in labels:
            index = index_by_timestamp.get(label)
            if index is None:
                continue
            context = _trend_context(
                ordered,
                end_index=index,
                fast_count=fast_count,
                slow_count=slow_count,
                width=width,
            )
            if context is None or index < 2:
                continue

            current_fast_sma = _fast_sma(ordered, end_index=index, fast_count=fast_count)
            previous_fast_sma = _fast_sma(ordered, end_index=index - 1, fast_count=fast_count)
            previous_close = _midpoint_close(ordered[index - 1])
            signal_close = _midpoint_close(ordered[index])

            long_signal = (
                context is Direction.LONG
                and previous_close <= previous_fast_sma
                and signal_close > current_fast_sma
            )
            short_signal = (
                context is Direction.SHORT
                and previous_close >= previous_fast_sma
                and signal_close < current_fast_sma
            )
            if not long_signal and not short_signal:
                continue

            stop_bars = ordered[index - 2 : index + 1]
            if len(stop_bars) != 3 or any(
                current.timestamp_utc - previous.timestamp_utc != width
                for previous, current in zip(stop_bars, stop_bars[1:])
            ):
                continue

            direction = Direction.LONG if long_signal else Direction.SHORT
            stop = (
                min(_midpoint_low(bar) for bar in stop_bars)
                if direction is Direction.LONG
                else max(_midpoint_high(bar) for bar in stop_bars)
            )
            risk_distance = (
                signal_close - stop
                if direction is Direction.LONG
                else stop - signal_close
            )
            if risk_distance <= 0:
                out.append(
                    _no_trade(
                        symbol=symbol,
                        session_date=session_date,
                        config=config,
                        observation_timestamp=label,
                        reason_code="INVALID_GEOMETRY",
                        metadata={
                            **base_metadata,
                            "signal_mid_close": signal_close,
                            "stop_price": stop,
                        },
                    )
                )
                emitted = True
                break

            target = (
                signal_close + config.target_r_multiple * risk_distance
                if direction is Direction.LONG
                else signal_close - config.target_r_multiple * risk_distance
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
                    stop_price=stop,
                    target_price=target,
                    latest_exit_timestamp_utc=exit_timestamp,
                    reason_code=f"CONTINUATION_{direction.value}",
                    metadata={
                        **base_metadata,
                        "previous_fast_sma": previous_fast_sma,
                        "current_fast_sma": current_fast_sma,
                        "signal_mid_close": signal_close,
                        "risk_distance": risk_distance,
                    },
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
                    observation_timestamp=labels[-1],
                    reason_code="NO_CONTINUATION",
                    metadata=base_metadata,
                )
            )

    return tuple(out)
