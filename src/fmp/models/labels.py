from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Sequence

from fmp.backtest.costs import ZeroCommission, ZeroFinancing
from fmp.backtest.execution import entry_reference_price, evaluate_exit
from fmp.contracts import Direction, ExitReason, Position, QuoteBar
from fmp.strategies.contracts import SignalCandidate


_FINAL_TEST_START_UTC = datetime(2024, 1, 1, tzinfo=timezone.utc)
_ZERO_COMMISSION = ZeroCommission()
_ZERO_FINANCING = ZeroFinancing()


@dataclass(frozen=True, slots=True)
class LabelResult:
    candidate_id: str
    label: int | None
    reason_code: str
    resolved_timestamp_utc: datetime | None


def _unlabeled(candidate: SignalCandidate, reason_code: str) -> LabelResult:
    return LabelResult(
        candidate_id=candidate.candidate_id,
        label=None,
        reason_code=reason_code,
        resolved_timestamp_utc=None,
    )


def _validate_final_test_lock(candidate: SignalCandidate) -> None:
    if candidate.signal_known_timestamp_utc >= _FINAL_TEST_START_UTC:
        raise ValueError("Phase 6 final-test lock: labeling may not require 2024 data")
    if (
        candidate.latest_exit_timestamp_utc is not None
        and candidate.latest_exit_timestamp_utc >= _FINAL_TEST_START_UTC
    ):
        raise ValueError("Phase 6 final-test lock: labeling may not require 2024 data")


def _valid_geometry(candidate: SignalCandidate, entry_reference: float) -> bool:
    stop = candidate.stop_price
    target = candidate.target_price
    if stop is None or target is None:
        return False
    if candidate.direction is Direction.LONG:
        return stop < entry_reference < target
    if candidate.direction is Direction.SHORT:
        return target < entry_reference < stop
    return False


def _bar_map(bars: Sequence[QuoteBar], *, symbol: str) -> dict[datetime, QuoteBar]:
    selected = [bar for bar in bars if bar.symbol == symbol]
    keys = [bar.timestamp_utc for bar in selected]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate quote-bar identity in Phase 6 label input")
    if keys != sorted(keys):
        raise ValueError("Phase 6 label bars must be sorted by timestamp_utc")
    return {bar.timestamp_utc: bar for bar in selected}


def label_candidate(
    candidate: SignalCandidate,
    bars: Sequence[QuoteBar],
) -> LabelResult:
    _validate_final_test_lock(candidate)

    if candidate.direction is Direction.NO_TRADE:
        return _unlabeled(candidate, "NO_TRADE")
    if candidate.direction not in {Direction.LONG, Direction.SHORT}:
        return _unlabeled(candidate, "UNSUPPORTED_DIRECTION")

    width = candidate.signal_known_timestamp_utc - candidate.observation_bar_timestamp_utc
    if width.total_seconds() <= 0:
        return _unlabeled(candidate, "INVALID_SIGNAL_CADENCE")

    latest_exit = candidate.latest_exit_timestamp_utc
    if latest_exit is None:
        return _unlabeled(candidate, "MISSING_SCHEDULED_EXIT")
    if latest_exit <= candidate.signal_known_timestamp_utc:
        return _unlabeled(candidate, "INVALID_SCHEDULED_EXIT")

    by_timestamp = _bar_map(bars, symbol=candidate.symbol)
    entry_bar = by_timestamp.get(candidate.signal_known_timestamp_utc)
    if entry_bar is None:
        return _unlabeled(candidate, "MISSING_ENTRY_BAR")

    entry_reference = entry_reference_price(entry_bar, candidate.direction)
    if not _valid_geometry(candidate, entry_reference):
        return _unlabeled(candidate, "INVALID_EXECUTABLE_GEOMETRY")

    assert candidate.stop_price is not None
    position = Position(
        position_id=candidate.candidate_id,
        decision_id=candidate.candidate_id,
        symbol=candidate.symbol,
        direction=candidate.direction,
        units=1,
        entry_timestamp_utc=entry_bar.timestamp_utc,
        entry_reference_price=entry_reference,
        entry_price=entry_reference,
        entry_commission_usd=0.0,
        stop_price=candidate.stop_price,
        target_price=candidate.target_price,
        reserved_risk_usd=1.0,
    )

    timestamp = candidate.signal_known_timestamp_utc
    while timestamp <= latest_exit:
        bar = by_timestamp.get(timestamp)
        if bar is None:
            if timestamp == latest_exit:
                return _unlabeled(candidate, "MISSING_SCHEDULED_EXIT")
            if timestamp == candidate.signal_known_timestamp_utc:
                return _unlabeled(candidate, "MISSING_ENTRY_BAR")
            return _unlabeled(candidate, "MISSING_EXECUTABLE_PATH")

        if timestamp == latest_exit:
            return LabelResult(
                candidate_id=candidate.candidate_id,
                label=0,
                reason_code="TIME_EXIT",
                resolved_timestamp_utc=timestamp,
            )

        exit_fill = evaluate_exit(
            position,
            bar,
            slippage_pips=0.0,
            commission_model=_ZERO_COMMISSION,
            financing_model=_ZERO_FINANCING,
        )
        if exit_fill is not None:
            if exit_fill.reason is ExitReason.TARGET:
                return LabelResult(
                    candidate_id=candidate.candidate_id,
                    label=1,
                    reason_code="TARGET_BEFORE_STOP",
                    resolved_timestamp_utc=timestamp,
                )
            if exit_fill.reason is ExitReason.STOP:
                return LabelResult(
                    candidate_id=candidate.candidate_id,
                    label=0,
                    reason_code=(
                        "STOP_FIRST_AMBIGUOUS"
                        if exit_fill.intrabar_ambiguous
                        else "STOP_BEFORE_TARGET"
                    ),
                    resolved_timestamp_utc=timestamp,
                )
            raise ValueError("unexpected Phase 3 exit reason during Phase 6 labeling")

        timestamp += width

    return _unlabeled(candidate, "UNRESOLVED_LABEL")


def label_candidates(
    candidates: Sequence[SignalCandidate],
    bars: Sequence[QuoteBar],
) -> tuple[LabelResult, ...]:
    ids = [candidate.candidate_id for candidate in candidates]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate candidate_id in Phase 6 label batch")
    return tuple(
        label_candidate(candidate, bars)
        for candidate in sorted(candidates, key=lambda item: item.candidate_id)
    )
