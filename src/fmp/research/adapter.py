from __future__ import annotations

import math
from datetime import datetime, timedelta

from fmp.contracts import Decision, Direction, ScheduledExit
from fmp.strategies.contracts import SignalCandidate


def _require_utc(value: datetime, *, field: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must use UTC")


def candidate_to_decision(
    candidate: SignalCandidate,
    *,
    next_bar_timestamp_utc: datetime,
    requested_risk_fraction: float = 0.0025,
) -> tuple[Decision, ScheduledExit | None]:
    _require_utc(next_bar_timestamp_utc, field="next_bar_timestamp_utc")
    if next_bar_timestamp_utc != candidate.signal_known_timestamp_utc:
        raise ValueError(
            "candidate true known timestamp must equal the immediately following supplied bar label"
        )
    if not math.isfinite(requested_risk_fraction) or requested_risk_fraction <= 0:
        raise ValueError("requested_risk_fraction must be finite and positive")

    if candidate.direction is Direction.NO_TRADE:
        decision = Decision(
            decision_id=candidate.candidate_id,
            symbol=candidate.symbol,
            decision_timestamp_utc=candidate.observation_bar_timestamp_utc,
            direction=Direction.NO_TRADE,
            earliest_executable_timestamp_utc=None,
            requested_risk_fraction=None,
            stop_price=None,
            target_price=None,
            reason_code=candidate.reason_code,
            reason_text=candidate.reason_code,
        )
        return decision, None

    decision = Decision(
        decision_id=candidate.candidate_id,
        symbol=candidate.symbol,
        decision_timestamp_utc=candidate.observation_bar_timestamp_utc,
        direction=candidate.direction,
        earliest_executable_timestamp_utc=next_bar_timestamp_utc,
        requested_risk_fraction=requested_risk_fraction,
        stop_price=candidate.stop_price,
        target_price=candidate.target_price,
        reason_code=candidate.reason_code,
        reason_text=None,
    )
    scheduled_exit = (
        ScheduledExit(
            decision_id=candidate.candidate_id,
            symbol=candidate.symbol,
            timestamp_utc=candidate.latest_exit_timestamp_utc,
        )
        if candidate.latest_exit_timestamp_utc is not None
        else None
    )
    return decision, scheduled_exit
