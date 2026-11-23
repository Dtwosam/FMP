"""N1-v0 News-Shock USD Continuation.

Isolated signal authorized by DEC-637. It emits the existing Decision and
ScheduledExit values. It does not change execution, risk, or position
contracts, and it does not read market history.

Direction and the original stop use the 08:29 close and the completed
08:30–08:34 bars only. Prices at 08:35 or later can change a fill, a size,
or a risk rejection. They cannot change this signal.

The governing method remains DEC-469 / DEC-268 annual catalogue discovery.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from typing import Mapping, Sequence
from zoneinfo import ZoneInfo

from fmp.backtest.costs import FixedCommissionPerMillion
from fmp.contracts import Decision, Direction, QuoteBar, ScheduledExit
from fmp.research.retail_costs import IC_MT4_RAW_COMMISSION, STANDARD_LOT_UNITS

RULE_ID = "N1-v0"
RULE_NAME = "News-Shock USD Continuation"
REQUESTED_RISK_FRACTION = 0.0025
TRADED_SYMBOL = "EURUSD"
DIRECTION_SYMBOLS = ("EURUSD", "GBPUSD", "USDJPY")
OBSERVATION_MINUTES = (30, 31, 32, 33, 34)
REFERENCE_MINUTE = 29
NEW_YORK = ZoneInfo("America/New_York")

REASON_RELEASE_NOT_PUBLISHED = "RELEASE_NOT_PUBLISHED"
REASON_RELEASE_TIME_MISMATCH = "RELEASE_TIME_MISMATCH"
REASON_UNSUPPORTED_RELEASE = "UNSUPPORTED_RELEASE"
REASON_MISSING_QUOTE = "MISSING_QUOTE"
REASON_DISAGREEMENT = "DISAGREEMENT"
REASON_MULTIPLE_RELEASES = "MULTIPLE_RELEASES"
REASON_USD_STRENGTH = "USD_STRENGTH"
REASON_USD_WEAKNESS = "USD_WEAKNESS"

HYPOTHETICAL_COST_LABEL = (
    "hypothetical: bid/ask spread inside the caller-supplied quotes, plus the "
    "published IC Markets Raw Spread MetaTrader commission of 3.50 USD per "
    "standard lot per side accessed 2026-11-17. Not a verified Dukascopy fill "
    "and not verified broker execution. The spread is not charged again."
)
SEPARATE_SLIPPAGE_STRESS = "separate_run_single_adverse_slippage"


class ReleaseKind(str, Enum):
    CPI = "BLS_CPI"
    EMPLOYMENT_SITUATION = "BLS_EMPLOYMENT_SITUATION"


class ReleaseStatus(str, Enum):
    PUBLISHED = "PUBLISHED"
    NOT_PUBLISHED = "NOT_PUBLISHED"
    DELAYED = "DELAYED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True, slots=True)
class N1Release:
    release_id: str
    kind: str
    status: str
    new_york_date: date
    actual_release_utc: datetime | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.release_id, str) or not self.release_id.strip():
            raise ValueError("release_id must be non-empty")
        if isinstance(self.new_york_date, datetime) or not isinstance(self.new_york_date, date):
            raise TypeError("new_york_date must be a date")
        kind = self.kind.value if isinstance(self.kind, ReleaseKind) else self.kind
        status = self.status.value if isinstance(self.status, ReleaseStatus) else self.status
        if not isinstance(kind, str) or not kind.strip():
            raise ValueError("release kind must be a non-empty string")
        if not isinstance(status, str) or not status.strip():
            raise ValueError("release status must be a non-empty string")
        if self.actual_release_utc is not None:
            _require_utc(self.actual_release_utc, field="actual_release_utc")
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "status", status)


@dataclass(frozen=True, slots=True)
class N1Signal:
    """One event record. NO TRADE keeps the decision and omits the exit."""

    decision: Decision
    scheduled_exit: ScheduledExit | None
    reason_code: str
    release_utc: datetime
    bars_used_through_utc: datetime

    def __post_init__(self) -> None:
        if self.decision.direction is Direction.NO_TRADE:
            if self.scheduled_exit is not None:
                raise ValueError("NO TRADE has no scheduled exit")
            return
        if self.scheduled_exit is None:
            raise ValueError("a directional N1 signal requires a scheduled exit")
        if self.scheduled_exit.decision_id != self.decision.decision_id:
            raise ValueError("scheduled exit decision_id must match the decision")
        if self.decision.target_price is not None:
            raise ValueError("N1-v0 has no target")
        if self.decision.requested_risk_fraction != REQUESTED_RISK_FRACTION:
            raise ValueError("N1-v0 risk fraction is fixed")


def new_york_clock_utc(day: date, hour: int, minute: int) -> datetime:
    """Convert a New York clock time to UTC.

    The civil time must exist once. 08:30 and 09:30 do. A spring-forward gap
    does not round-trip to the same clock time and is rejected.
    """

    if isinstance(day, datetime) or not isinstance(day, date):
        raise TypeError("day must be a date")
    if isinstance(hour, bool) or isinstance(minute, bool):
        raise TypeError("hour and minute must be integers")
    if not isinstance(hour, int) or not isinstance(minute, int):
        raise TypeError("hour and minute must be integers")
    local = datetime(day.year, day.month, day.day, hour, minute, tzinfo=NEW_YORK)
    utc = local.astimezone(timezone.utc)
    if utc.utcoffset() != timedelta(0):
        raise ValueError("New York clock did not convert to UTC")
    restored = utc.astimezone(NEW_YORK)
    if (
        restored.year,
        restored.month,
        restored.day,
        restored.hour,
        restored.minute,
        restored.second,
    ) != (day.year, day.month, day.day, hour, minute, 0):
        raise ValueError("New York clock does not exist or is ambiguous")
    return utc


def hypothetical_published_commission_model() -> FixedCommissionPerMillion:
    """Published per-side commission, labeled hypothetical.

    3.50 USD per 100,000 units is 35 USD per million units per side. The
    quote spread stays in the bid/ask. This does not add a second spread,
    and it is not a live fill.
    """

    per_side = IC_MT4_RAW_COMMISSION.usd_per_standard_lot_per_side
    if per_side is None:
        raise ValueError("published commission figure is missing")
    per_million = per_side * (1_000_000 / STANDARD_LOT_UNITS)
    return FixedCommissionPerMillion(per_million)


def n1_run_decision_config() -> dict[str, str]:
    return {
        "rule_id": RULE_ID,
        "rule_name": RULE_NAME,
        "cost_package": "hypothetical_quote_spread_plus_published_commission",
        "cost_package_label": HYPOTHETICAL_COST_LABEL,
        "slippage": "one_adverse_pips_value_per_run",
        "evidence_class": "synthetic_engineering_check",
    }


def evaluate_n1_v0(release: N1Release, bars: Sequence[QuoteBar]) -> N1Signal:
    return evaluate_n1_v0_releases((release,), bars)[0]


def evaluate_n1_v0_releases(
    releases: Sequence[N1Release],
    bars: Sequence[QuoteBar],
) -> tuple[N1Signal, ...]:
    """Evaluate one or more releases. Same-day duplicates do not pyramid."""

    batch = tuple(releases)
    for release in batch:
        if not isinstance(release, N1Release):
            raise TypeError("releases must be N1Release values")
    release_ids = [release.release_id for release in batch]
    if len(set(release_ids)) != len(release_ids):
        raise ValueError("duplicate release_id")
    indexed = _index_bars(bars)
    counts = Counter(release.new_york_date for release in batch)
    signals = []
    for release in batch:
        if counts[release.new_york_date] > 1:
            signals.append(
                _no_trade(
                    release,
                    REASON_MULTIPLE_RELEASES,
                    "more than one release is registered on this New York date",
                )
            )
            continue
        signals.append(_evaluate_one(release, indexed))
    return tuple(signals)


def _evaluate_one(
    release: N1Release,
    bars: Mapping[tuple[datetime, str], QuoteBar],
) -> N1Signal:
    kind = _known_kind(release.kind)
    status = _known_status(release.status)
    if kind is None or status is None:
        return _no_trade(
            release,
            REASON_UNSUPPORTED_RELEASE,
            "release is not a BLS CPI or Employment Situation publication",
        )
    if status is not ReleaseStatus.PUBLISHED:
        return _no_trade(
            release,
            REASON_RELEASE_NOT_PUBLISHED,
            f"release status {status.value} is not an 08:30 publication",
        )
    release_utc = new_york_clock_utc(release.new_york_date, 8, 30)
    if release.actual_release_utc != release_utc:
        return _no_trade(
            release,
            REASON_RELEASE_TIME_MISMATCH,
            "publication timestamp is not 08:30 America/New_York",
        )

    needed = _required_bars(release.new_york_date)
    missing = [(timestamp, symbol) for timestamp, symbol in needed if (timestamp, symbol) not in bars]
    if missing:
        timestamp, symbol = missing[0]
        local = timestamp.astimezone(NEW_YORK)
        return _no_trade(
            release,
            REASON_MISSING_QUOTE,
            (
                f"missing {symbol} bar labelled "
                f"{local.hour:02d}:{local.minute:02d} America/New_York"
            ),
        )

    eur_change = _mid_change(bars, release.new_york_date, "EURUSD")
    gbp_change = _mid_change(bars, release.new_york_date, "GBPUSD")
    jpy_change = _mid_change(bars, release.new_york_date, "USDJPY")
    strength = eur_change < 0 and gbp_change < 0 and jpy_change > 0
    weakness = eur_change > 0 and gbp_change > 0 and jpy_change < 0
    if strength:
        direction = Direction.SHORT
        reason = REASON_USD_STRENGTH
        text = "EURUSD down, GBPUSD down, USDJPY up: short EURUSD"
        stop = max(
            bars[(_minute(release.new_york_date, 8, minute), "EURUSD")].ask_high
            for minute in OBSERVATION_MINUTES
        )
    elif weakness:
        direction = Direction.LONG
        reason = REASON_USD_WEAKNESS
        text = "EURUSD up, GBPUSD up, USDJPY down: long EURUSD"
        stop = min(
            bars[(_minute(release.new_york_date, 8, minute), "EURUSD")].bid_low
            for minute in OBSERVATION_MINUTES
        )
    else:
        return _no_trade(
            release,
            REASON_DISAGREEMENT,
            "the three USD signs are mixed or flat",
        )

    decision_utc = new_york_clock_utc(release.new_york_date, 8, 35)
    entry_utc = new_york_clock_utc(release.new_york_date, 8, 36)
    exit_utc = new_york_clock_utc(release.new_york_date, 9, 30)
    decision = Decision(
        decision_id=_decision_id(release),
        symbol=TRADED_SYMBOL,
        decision_timestamp_utc=decision_utc,
        direction=direction,
        earliest_executable_timestamp_utc=entry_utc,
        requested_risk_fraction=REQUESTED_RISK_FRACTION,
        stop_price=stop,
        target_price=None,
        reason_code=reason,
        reason_text=text,
    )
    scheduled_exit = ScheduledExit(
        decision_id=decision.decision_id,
        symbol=TRADED_SYMBOL,
        timestamp_utc=exit_utc,
    )
    return N1Signal(
        decision=decision,
        scheduled_exit=scheduled_exit,
        reason_code=reason,
        release_utc=release_utc,
        bars_used_through_utc=decision_utc,
    )


def _no_trade(release: N1Release, reason: str, text: str) -> N1Signal:
    decision_utc = new_york_clock_utc(release.new_york_date, 8, 35)
    release_utc = new_york_clock_utc(release.new_york_date, 8, 30)
    decision = Decision(
        decision_id=_decision_id(release),
        symbol=TRADED_SYMBOL,
        decision_timestamp_utc=decision_utc,
        direction=Direction.NO_TRADE,
        earliest_executable_timestamp_utc=None,
        requested_risk_fraction=None,
        stop_price=None,
        target_price=None,
        reason_code=reason,
        reason_text=text,
    )
    return N1Signal(
        decision=decision,
        scheduled_exit=None,
        reason_code=reason,
        release_utc=release_utc,
        bars_used_through_utc=decision_utc,
    )


def _decision_id(release: N1Release) -> str:
    return f"n1-v0|{release.kind}|{release.new_york_date.isoformat()}|{release.release_id}"


def _known_kind(value: str) -> ReleaseKind | None:
    try:
        return ReleaseKind(value)
    except ValueError:
        return None


def _known_status(value: str) -> ReleaseStatus | None:
    try:
        return ReleaseStatus(value)
    except ValueError:
        return None


def _minute(day: date, hour: int, minute: int) -> datetime:
    return new_york_clock_utc(day, hour, minute)


def _required_bars(day: date) -> tuple[tuple[datetime, str], ...]:
    minutes = (REFERENCE_MINUTE, *OBSERVATION_MINUTES)
    return tuple(
        (_minute(day, 8, minute), symbol)
        for symbol in DIRECTION_SYMBOLS
        for minute in minutes
    )


def _mid_change(
    bars: Mapping[tuple[datetime, str], QuoteBar],
    day: date,
    symbol: str,
) -> float:
    start = bars[(_minute(day, 8, REFERENCE_MINUTE), symbol)]
    end = bars[(_minute(day, 8, OBSERVATION_MINUTES[-1]), symbol)]
    return _mid_close(end) - _mid_close(start)


def _mid_close(bar: QuoteBar) -> float:
    return (bar.bid_close + bar.ask_close) / 2.0


def _index_bars(
    bars: Sequence[QuoteBar],
) -> dict[tuple[datetime, str], QuoteBar]:
    indexed: dict[tuple[datetime, str], QuoteBar] = {}
    for bar in bars:
        if not isinstance(bar, QuoteBar):
            raise TypeError("bars must be QuoteBar values")
        key = (bar.timestamp_utc, bar.symbol)
        if key in indexed:
            raise ValueError("duplicate quote-bar identity")
        indexed[key] = bar
    return indexed


def _require_utc(value: datetime, *, field: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must use UTC")
