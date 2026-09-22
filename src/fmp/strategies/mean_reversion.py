from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
import math
from typing import Sequence
from zoneinfo import ZoneInfo

from fmp.contracts import Direction, QuoteBar
from fmp.strategies.contracts import SignalCandidate


LONDON = ZoneInfo("Europe/London")
_TIMEFRAME_MINUTES = {"5m": 5, "15m": 15, "1h": 60}
_PHASE4_LOOKBACK_HOURS = frozenset({4, 8, 16})
_PHASE4_THRESHOLDS = frozenset({1.5, 2.0})
_EXP015_LOOKBACK_HOURS = frozenset({2, 6, 12, 24})
_EXP015_THRESHOLDS = frozenset({1.25, 1.75, 2.25, 2.5})


@dataclass(frozen=True, slots=True)
class MeanReversionConfig:
    lookback_hours: int
    threshold_sigma: float
    timeframe: str
    parameter_region: str = "phase4"

    def __post_init__(self) -> None:
        if self.parameter_region == "phase4":
            lookbacks = _PHASE4_LOOKBACK_HOURS
            thresholds = _PHASE4_THRESHOLDS
        elif self.parameter_region == "exp015":
            lookbacks = _EXP015_LOOKBACK_HOURS
            thresholds = _EXP015_THRESHOLDS
        else:
            raise ValueError("unsupported mean-reversion parameter_region")
        if self.lookback_hours not in lookbacks:
            raise ValueError("lookback_hours is outside the selected parameter region")
        if self.threshold_sigma not in thresholds:
            raise ValueError("threshold_sigma is outside the selected parameter region")
        if self.timeframe not in _TIMEFRAME_MINUTES:
            raise ValueError("timeframe must be one of 5m, 15m, or 1h")


def duration_to_bars(
    timeframe: str,
    hours: int,
    *,
    parameter_region: str = "phase4",
) -> int:
    try:
        width_minutes = _TIMEFRAME_MINUTES[timeframe]
    except KeyError as exc:
        raise ValueError("timeframe must be one of 5m, 15m, or 1h") from exc
    if parameter_region == "phase4":
        allowed = _PHASE4_LOOKBACK_HOURS
    elif parameter_region == "exp015":
        allowed = _EXP015_LOOKBACK_HOURS
    else:
        raise ValueError("unsupported mean-reversion parameter_region")
    if hours not in allowed:
        raise ValueError("hours is outside the selected parameter region")
    duration_minutes = hours * 60
    if duration_minutes % width_minutes:
        raise ValueError("duration must be exactly divisible by timeframe width")
    return duration_minutes // width_minutes


def _midpoint_close(bar: QuoteBar) -> float:
    return (bar.bid_close + bar.ask_close) / 2.0


def rolling_reference(
    bars: Sequence[QuoteBar],
    *,
    observation_index: int,
    lookback_count: int,
    width: timedelta,
) -> tuple[float, float] | None:
    if lookback_count <= 0:
        raise ValueError("lookback_count must be positive")
    if width <= timedelta(0):
        raise ValueError("width must be positive")
    if observation_index < 0 or observation_index >= len(bars):
        return None

    start = observation_index - lookback_count
    if start < 0:
        return None
    required = bars[start : observation_index + 1]
    if len(required) != lookback_count + 1:
        return None
    if any(
        current.timestamp_utc - previous.timestamp_utc != width
        for previous, current in zip(required, required[1:])
    ):
        return None

    values = tuple(_midpoint_close(bar) for bar in required[:-1])
    if len(values) != lookback_count or any(not math.isfinite(value) for value in values):
        return None

    mean = sum(values) / lookback_count
    variance = sum((value - mean) ** 2 for value in values) / lookback_count
    if not math.isfinite(mean) or not math.isfinite(variance) or variance <= 0.0:
        return None
    std = math.sqrt(variance)
    if not math.isfinite(std) or std <= 0.0:
        return None
    return mean, std


def z_score_against_reference(value: float, mean: float, std: float) -> float:
    if not all(math.isfinite(item) for item in (value, mean, std)) or std <= 0.0:
        raise ValueError("value and mean must be finite and std must be positive and finite")
    return (value - mean) / std


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
    config: MeanReversionConfig,
    suffix: str,
) -> str:
    threshold = str(config.threshold_sigma).replace(".", "p")
    return (
        f"MR-{symbol}-{session_date:%Y%m%d}-{config.timeframe}-"
        f"L{config.lookback_hours}-Z{threshold}-{suffix}"
    )


def _no_trade(
    *,
    symbol: str,
    session_date: date,
    config: MeanReversionConfig,
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


def generate_mean_reversion_candidates(
    bars: Sequence[QuoteBar],
    *,
    config: MeanReversionConfig,
) -> tuple[SignalCandidate, ...]:
    if not bars:
        return ()

    ordered = tuple(sorted(bars, key=lambda item: (item.timestamp_utc, item.symbol)))
    symbols = {bar.symbol for bar in ordered}
    if len(symbols) != 1:
        raise ValueError("mean reversion requires bars for exactly one symbol")
    symbol = next(iter(symbols))
    identities = [(bar.timestamp_utc, bar.symbol) for bar in ordered]
    if len(set(identities)) != len(identities):
        raise ValueError("duplicate quote-bar identity in mean-reversion input")

    width_minutes = _TIMEFRAME_MINUTES[config.timeframe]
    width = timedelta(minutes=width_minutes)
    lookback_count = duration_to_bars(
        config.timeframe,
        config.lookback_hours,
        parameter_region=config.parameter_region,
    )
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
            "lookback_hours": config.lookback_hours,
            "threshold_sigma": config.threshold_sigma,
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
            if index is None or index <= 0:
                continue

            current_reference = rolling_reference(
                ordered,
                observation_index=index,
                lookback_count=lookback_count,
                width=width,
            )
            previous_reference = rolling_reference(
                ordered,
                observation_index=index - 1,
                lookback_count=lookback_count,
                width=width,
            )
            if current_reference is None or previous_reference is None:
                continue

            current_mean, current_std = current_reference
            previous_mean, previous_std = previous_reference
            current_close = _midpoint_close(ordered[index])
            previous_close = _midpoint_close(ordered[index - 1])
            current_z = z_score_against_reference(current_close, current_mean, current_std)
            previous_z = z_score_against_reference(previous_close, previous_mean, previous_std)
            threshold = config.threshold_sigma

            long_signal = previous_z > -threshold and current_z <= -threshold
            short_signal = previous_z < threshold and current_z >= threshold
            if not long_signal and not short_signal:
                continue

            direction = Direction.LONG if long_signal else Direction.SHORT
            stop = (
                current_close - current_std
                if direction is Direction.LONG
                else current_close + current_std
            )
            target = current_mean
            valid_geometry = (
                stop < current_close < target
                if direction is Direction.LONG
                else target < current_close < stop
            )
            metadata = {
                **base_metadata,
                "previous_z": previous_z,
                "current_z": current_z,
                "reference_mean": current_mean,
                "reference_std": current_std,
                "signal_mid_close": current_close,
            }
            if not valid_geometry:
                out.append(
                    _no_trade(
                        symbol=symbol,
                        session_date=session_date,
                        config=config,
                        observation_timestamp=label,
                        reason_code="INVALID_GEOMETRY",
                        metadata=metadata,
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
                    reason_code=f"REVERSION_{direction.value}",
                    metadata=metadata,
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
                    reason_code="NO_EXCURSION",
                    metadata=base_metadata,
                )
            )

    return tuple(out)
