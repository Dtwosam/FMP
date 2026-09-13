from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

_NEW_YORK = ZoneInfo("America/New_York")
_UTC = ZoneInfo("UTC")


def is_market_open_minute(timestamp_utc: datetime) -> bool:
    if timestamp_utc.tzinfo is None or timestamp_utc.utcoffset() != timedelta(0):
        raise ValueError("timestamp must be timezone-aware UTC")
    local = timestamp_utc.astimezone(_NEW_YORK)
    weekday = local.weekday()
    if weekday == 5:
        return False
    if weekday == 6:
        return local.hour >= 17
    if weekday == 4:
        return local.hour < 17
    return True
