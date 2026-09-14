from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import polars as pl

from .contracts import timeframe_delta

_ASIA = ZoneInfo("Asia/Tokyo")
_LONDON = ZoneInfo("Europe/London")
_NEW_YORK = ZoneInfo("America/New_York")


@dataclass(frozen=True, slots=True)
class _Reference:
    available_at_utc: datetime
    high: float
    low: float
    close: float


def _finite(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _local_boundary(day: date, hour: int, zone: ZoneInfo) -> datetime:
    return datetime.combine(day, time(hour=hour), tzinfo=zone).astimezone(timezone.utc)


def _complete_reference(
    indices: list[int],
    *,
    timestamps: list[datetime],
    ends: list[datetime],
    complete: list[bool],
    highs: list[float],
    lows: list[float],
    closes: list[float],
    expected_start: datetime,
    expected_end: datetime,
    delta: timedelta,
) -> _Reference | None:
    expected_count_float = (expected_end - expected_start).total_seconds() / delta.total_seconds()
    expected_count = int(expected_count_float)
    if expected_count <= 0 or expected_count_float != expected_count or len(indices) != expected_count:
        return None
    ordered = sorted(indices, key=lambda i: timestamps[i])
    for offset, i in enumerate(ordered):
        if timestamps[i] != expected_start + delta * offset or ends[i] != timestamps[i] + delta:
            return None
        if not complete[i] or not all(_finite(v) for v in (highs[i], lows[i], closes[i])):
            return None
    if ends[ordered[-1]] != expected_end:
        return None
    return _Reference(
        available_at_utc=expected_end,
        high=max(float(highs[i]) for i in ordered),
        low=min(float(lows[i]) for i in ordered),
        close=float(closes[ordered[-1]]),
    )


def _session_references(
    frame: pl.DataFrame,
    *,
    zone: ZoneInfo,
    open_hour: int,
    close_hour: int,
) -> list[_Reference]:
    starts = frame["bar_start_utc"].to_list()
    ends = frame["bar_end_utc"].to_list()
    complete = frame["is_complete"].to_list()
    highs = frame["mid_high"].to_list()
    lows = frame["mid_low"].to_list()
    closes = frame["mid_close"].to_list()
    delta = timeframe_delta(str(frame["timeframe"][0]))
    groups: dict[date, list[int]] = {}
    for i, (start_utc, end_utc) in enumerate(zip(starts, ends)):
        start = start_utc.astimezone(zone)
        end = end_utc.astimezone(zone)
        start_min = start.hour * 60 + start.minute
        end_min = end.hour * 60 + end.minute
        if (
            start.date() == end.date()
            and start_min >= open_hour * 60
            and end_min <= close_hour * 60
            and start_min < close_hour * 60
            and end_min > open_hour * 60
        ):
            groups.setdefault(start.date(), []).append(i)
    refs: list[_Reference] = []
    for day, indices in groups.items():
        ref = _complete_reference(
            indices,
            timestamps=starts,
            ends=ends,
            complete=complete,
            highs=highs,
            lows=lows,
            closes=closes,
            expected_start=_local_boundary(day, open_hour, zone),
            expected_end=_local_boundary(day, close_hour, zone),
            delta=delta,
        )
        if ref is not None:
            refs.append(ref)
    refs.sort(key=lambda ref: ref.available_at_utc)
    return refs


def _fx_day_references(frame: pl.DataFrame) -> list[_Reference]:
    starts = frame["bar_start_utc"].to_list()
    ends = frame["bar_end_utc"].to_list()
    complete = frame["is_complete"].to_list()
    highs = frame["mid_high"].to_list()
    lows = frame["mid_low"].to_list()
    closes = frame["mid_close"].to_list()
    delta = timeframe_delta(str(frame["timeframe"][0]))
    groups: dict[date, list[int]] = {}
    for i, start_utc in enumerate(starts):
        local = start_utc.astimezone(_NEW_YORK)
        day = local.date() if (local.hour, local.minute) >= (17, 0) else local.date() - timedelta(days=1)
        groups.setdefault(day, []).append(i)
    refs: list[_Reference] = []
    for day, indices in groups.items():
        expected_start = _local_boundary(day, 17, _NEW_YORK)
        expected_end = _local_boundary(day + timedelta(days=1), 17, _NEW_YORK)
        ref = _complete_reference(
            indices,
            timestamps=starts,
            ends=ends,
            complete=complete,
            highs=highs,
            lows=lows,
            closes=closes,
            expected_start=expected_start,
            expected_end=expected_end,
            delta=delta,
        )
        if ref is not None:
            refs.append(ref)
    refs.sort(key=lambda ref: ref.available_at_utc)
    return refs


def _distances(
    frame: pl.DataFrame,
    refs: list[_Reference],
    *,
    include_close: bool,
) -> tuple[list[float | None], list[float | None], list[float | None] | None]:
    available = frame["available_at_utc"].to_list()
    current_complete = frame["is_complete"].to_list()
    closes = frame["mid_close"].to_list()
    pips = frame["pip_size"].to_list()
    highs_out: list[float | None] = []
    lows_out: list[float | None] = []
    closes_out: list[float | None] | None = [] if include_close else None
    pointer = 0
    latest: _Reference | None = None
    for i, when in enumerate(available):
        while pointer < len(refs) and refs[pointer].available_at_utc <= when:
            latest = refs[pointer]
            pointer += 1
        valid_current = bool(current_complete[i]) and _finite(closes[i]) and _finite(pips[i])
        if latest is None or not valid_current:
            highs_out.append(None)
            lows_out.append(None)
            if closes_out is not None:
                closes_out.append(None)
            continue
        current = float(closes[i])
        pip = float(pips[i])
        highs_out.append((current - latest.high) / pip)
        lows_out.append((current - latest.low) / pip)
        if closes_out is not None:
            closes_out.append((current - latest.close) / pip)
    return highs_out, lows_out, closes_out


def add_location_features(frame: pl.DataFrame) -> pl.DataFrame:
    if frame.is_empty():
        return frame
    fx = _fx_day_references(frame)
    asia = _session_references(frame, zone=_ASIA, open_hour=9, close_hour=17)
    london = _session_references(frame, zone=_LONDON, open_hour=8, close_hour=16)
    fx_high, fx_low, fx_close = _distances(frame, fx, include_close=True)
    asia_high, asia_low, _ = _distances(frame, asia, include_close=False)
    london_high, london_low, _ = _distances(frame, london, include_close=False)
    assert fx_close is not None
    return frame.with_columns(
        pl.Series("prev_fx_day_high_dist_pips", fx_high, dtype=pl.Float64),
        pl.Series("prev_fx_day_low_dist_pips", fx_low, dtype=pl.Float64),
        pl.Series("prev_fx_day_close_dist_pips", fx_close, dtype=pl.Float64),
        pl.Series("prev_asia_high_dist_pips", asia_high, dtype=pl.Float64),
        pl.Series("prev_asia_low_dist_pips", asia_low, dtype=pl.Float64),
        pl.Series("prev_london_high_dist_pips", london_high, dtype=pl.Float64),
        pl.Series("prev_london_low_dist_pips", london_low, dtype=pl.Float64),
    )
