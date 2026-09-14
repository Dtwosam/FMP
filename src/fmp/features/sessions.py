from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import polars as pl

_ASIA = ZoneInfo("Asia/Tokyo")
_LONDON = ZoneInfo("Europe/London")
_NEW_YORK = ZoneInfo("America/New_York")


def _minute_of_day(value: datetime) -> int:
    return value.hour * 60 + value.minute


def _session_membership(
    start_utc: datetime,
    end_utc: datetime,
    *,
    zone: ZoneInfo,
    open_minute: int,
    close_minute: int,
) -> tuple[bool, int | None]:
    start = start_utc.astimezone(zone)
    end = end_utc.astimezone(zone)
    start_minute = _minute_of_day(start)
    end_minute = _minute_of_day(end)
    inside = (
        start.date() == end.date()
        and start_minute >= open_minute
        and end_minute <= close_minute
        and start_minute < close_minute
        and end_minute > open_minute
    )
    return inside, (start_minute - open_minute if inside else None)


def add_session_features(frame: pl.DataFrame) -> pl.DataFrame:
    starts = frame["bar_start_utc"].to_list()
    ends = frame["bar_end_utc"].to_list()
    hour_utc: list[int] = []
    minute_utc: list[int] = []
    dow_utc: list[int] = []
    asia: list[bool] = []
    london: list[bool] = []
    new_york: list[bool] = []
    overlap: list[bool] = []
    asia_minutes: list[int | None] = []
    london_minutes: list[int | None] = []
    new_york_minutes: list[int | None] = []

    for start, end in zip(starts, ends):
        a, am = _session_membership(
            start, end, zone=_ASIA, open_minute=9 * 60, close_minute=17 * 60
        )
        l, lm = _session_membership(
            start, end, zone=_LONDON, open_minute=8 * 60, close_minute=16 * 60
        )
        n, nm = _session_membership(
            start, end, zone=_NEW_YORK, open_minute=8 * 60, close_minute=17 * 60
        )
        hour_utc.append(start.hour)
        minute_utc.append(start.minute)
        dow_utc.append(start.weekday())
        asia.append(a)
        london.append(l)
        new_york.append(n)
        overlap.append(l and n)
        asia_minutes.append(am)
        london_minutes.append(lm)
        new_york_minutes.append(nm)

    return frame.with_columns(
        pl.Series("hour_utc", hour_utc, dtype=pl.Int64),
        pl.Series("minute_utc", minute_utc, dtype=pl.Int64),
        pl.Series("day_of_week_utc", dow_utc, dtype=pl.Int64),
        pl.Series("is_asia_session", asia, dtype=pl.Boolean),
        pl.Series("is_london_session", london, dtype=pl.Boolean),
        pl.Series("is_new_york_session", new_york, dtype=pl.Boolean),
        pl.Series("is_london_new_york_overlap", overlap, dtype=pl.Boolean),
        pl.Series("minutes_since_asia_open", asia_minutes, dtype=pl.Int64),
        pl.Series("minutes_since_london_open", london_minutes, dtype=pl.Int64),
        pl.Series("minutes_since_new_york_open", new_york_minutes, dtype=pl.Int64),
    )
