from __future__ import annotations

import hashlib
import json
import math
import os
import re
from collections import defaultdict
from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Mapping, Sequence

from fmp.backtest.costs import ZeroCommission, ZeroFinancing
from fmp.backtest.execution import (
    close_time_exit,
    entry_reference_price,
    evaluate_exit,
    fill_entry,
)
from fmp.contracts import (
    Decision,
    Direction,
    EquityCheckpoint,
    OrderIntent,
    Position,
    QuoteBar,
    RejectionCode,
    ScheduledExit,
    TradeRecord,
)
from fmp.phase8b.bridge import (
    Phase8BBridgeHeartbeatRecord,
    Phase8BBridgeTickRecord,
    Phase8BQuote,
    parse_phase8b_bridge_line,
)
from fmp.phase8b.capture import (
    validate_phase8b_capture_preflight,
    validate_phase8b_capture_record_envelope,
)
from fmp.portfolio.contracts import (
    ChampionSet,
    PHASE8A_EXPERIMENT_ID,
    PortfolioCandidate,
    StrategyVersion,
)
from fmp.portfolio.research_runner import (
    REQUESTED_RISK_FRACTION,
    generate_strategy_candidates,
)
from fmp.portfolio.router import (
    route_shadow_candidates,
    summarize_candidate_exposure,
)
from fmp.reporting.backtest import compute_backtest_metrics
from fmp.research.adapter import candidate_to_decision
from fmp.risk import (
    RiskConfig,
    RiskState,
    assess_decision,
    pnl_usd,
    record_realized_pnl,
    release_risk,
    reserve_risk,
)
from fmp.shadow.contracts import ShadowOutcome
from fmp.strategies.contracts import SignalCandidate


PHASE8B_RUNTIME_EXPERIMENT_ID = "EXP-20260922-021"
PHASE8B_SEGMENT_PROTOCOL = "fmp-phase8b-segment-v1"
PHASE8B_REPLAY_PROTOCOL = "fmp-phase8b-replay-v1"
PHASE8B_SEGMENT_ARTIFACT_PROTOCOL = "fmp-phase8b-segment-artifacts-v1"
PHASE8B_RUNTIME_REPLAY_KERNEL_READY = "PHASE8B_RUNTIME_REPLAY_KERNEL_READY"

STARTING_EQUITY_USD = 100_000.0
SLIPPAGE_SCENARIOS = (0.2, 0.5, 1.0)
QUOTE_DEADLINE_SECONDS = 5.0
LIVENESS_TIMEOUT_SECONDS = 15.0

_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_TIMEFRAME_MINUTES = {"1m": 1, "5m": 5, "15m": 15, "1h": 60}
UTC = timezone.utc


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _COMMIT_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase 40-character commit SHA")
    return value


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase SHA-256")
    return value


def _parse_utc(value: object, *, field: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{field} must be an ISO-8601 UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO-8601 UTC timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must use UTC")
    return parsed


def _utc_string(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError("timestamp must use UTC")
    return value.isoformat().replace("+00:00", "Z")


def _jsonable(value: object) -> object:
    if is_dataclass(value) and not isinstance(value, type):
        return {
            item.name: _jsonable(getattr(value, item.name))
            for item in fields(value)
        }
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return _utc_string(value)
    if isinstance(value, Mapping):
        return {
            str(key): _jsonable(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float cannot be serialized")
        return value
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise TypeError(f"unsupported serialization type: {type(value).__name__}")


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        _jsonable(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _canonical_digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _stable_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            _jsonable(value),
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def _bridge_record_from_envelope(
    envelope: Mapping[str, object],
):
    raw = envelope.get("bridge_record")
    if not isinstance(raw, Mapping):
        raise ValueError("Phase 8B capture-record bridge payload is malformed")
    return parse_phase8b_bridge_line(
        (
            json.dumps(
                dict(raw),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
    )


def _tick_to_quote(
    record: Phase8BBridgeTickRecord,
    envelope: Mapping[str, object],
) -> Phase8BQuote:
    received = _parse_utc(
        envelope.get("received_at_utc"),
        field="Phase 8B capture receive timestamp",
    )
    monotonic = envelope.get("receive_monotonic_ns")
    if isinstance(monotonic, bool) or not isinstance(monotonic, int) or monotonic < 0:
        raise ValueError("Phase 8B capture monotonic receive time is invalid")
    seconds, milliseconds = divmod(record.source_time_msc, 1000)
    source = datetime.fromtimestamp(seconds, tz=UTC).replace(
        microsecond=milliseconds * 1000
    )
    return Phase8BQuote(
        source_time_utc=source,
        received_at_utc=received,
        receive_monotonic_ns=monotonic,
        symbol=record.symbol,
        bid=record.bid,
        ask=record.ask,
        tradeable=True,
    )


def _strategy_from_row(row: Mapping[str, object]) -> StrategyVersion:
    identity_raw = row.get("identity_json")
    if not isinstance(identity_raw, str):
        raise ValueError("Phase 8B strategy identity_json is missing")
    try:
        identity = json.loads(identity_raw)
    except json.JSONDecodeError as exc:
        raise ValueError("Phase 8B strategy identity_json is invalid") from exc
    if not isinstance(identity, dict):
        raise ValueError("Phase 8B strategy identity_json must be an object")
    parameters = identity.get("parameters")
    if not isinstance(parameters, dict):
        raise ValueError("Phase 8B strategy parameters are malformed")
    strategy = StrategyVersion.create(
        family=str(identity.get("family")),
        version=str(identity.get("version")),
        symbol=str(identity.get("symbol")),
        timeframe=str(identity.get("timeframe")),
        parameters=parameters,
        signal_contract_version=str(identity.get("signal_contract_version")),
        code_commit=str(identity.get("code_commit")),
    )
    expected = row.get("fingerprint")
    if strategy.fingerprint != expected:
        raise ValueError("Phase 8B strategy fingerprint does not match identity_json")
    for field in ("family", "symbol", "timeframe", "code_commit"):
        if row.get(field) != getattr(strategy, field):
            raise ValueError(f"Phase 8B strategy {field} row mismatch")
    if row.get("parameters_json") != strategy.parameters_json:
        raise ValueError("Phase 8B strategy parameters_json row mismatch")
    return strategy


def reconstruct_phase8b_champion_set(
    preflight: Mapping[str, object],
) -> ChampionSet:
    validate_phase8b_capture_preflight(preflight)
    raw = preflight.get("strategies")
    if not isinstance(raw, list) or not raw:
        raise ValueError("Phase 8B capture preflight strategies are malformed")
    strategies = tuple(
        sorted(
            (
                _strategy_from_row(row)
                for row in raw
                if isinstance(row, Mapping)
            ),
            key=lambda item: item.fingerprint,
        )
    )
    if len(strategies) != len(raw):
        raise ValueError("Phase 8B capture preflight strategy row is malformed")
    champion = ChampionSet(
        champion_set_id=str(preflight.get("champion_set_id")),
        experiment_id=PHASE8A_EXPERIMENT_ID,
        strategies=strategies,
    )
    if champion.fingerprint != preflight.get("champion_set_fingerprint"):
        raise ValueError("Phase 8B champion-set fingerprint mismatch")
    if [item.fingerprint for item in strategies] != preflight.get(
        "strategy_fingerprints"
    ):
        raise ValueError("Phase 8B champion-set strategy ordering mismatch")
    return champion


@dataclass(frozen=True, slots=True)
class _MarketGap:
    symbol: str
    start_utc: datetime
    end_utc: datetime
    detected_at_utc: datetime
    receive_gap_seconds: float


@dataclass(frozen=True, slots=True)
class _BridgeGap:
    symbol: str
    previous_received_at_utc: datetime
    received_at_utc: datetime
    receive_gap_seconds: float


@dataclass(slots=True)
class _MinuteAccumulator:
    symbol: str
    timestamp_utc: datetime
    bid_open: float
    bid_high: float
    bid_low: float
    bid_close: float
    ask_open: float
    ask_high: float
    ask_low: float
    ask_close: float

    @classmethod
    def create(cls, quote: Phase8BQuote, label: datetime) -> "_MinuteAccumulator":
        return cls(
            symbol=quote.symbol,
            timestamp_utc=label,
            bid_open=quote.bid,
            bid_high=quote.bid,
            bid_low=quote.bid,
            bid_close=quote.bid,
            ask_open=quote.ask,
            ask_high=quote.ask,
            ask_low=quote.ask,
            ask_close=quote.ask,
        )

    def update(self, quote: Phase8BQuote) -> None:
        self.bid_high = max(self.bid_high, quote.bid)
        self.bid_low = min(self.bid_low, quote.bid)
        self.bid_close = quote.bid
        self.ask_high = max(self.ask_high, quote.ask)
        self.ask_low = min(self.ask_low, quote.ask)
        self.ask_close = quote.ask

    def to_bar(self) -> QuoteBar:
        return QuoteBar(
            timestamp_utc=self.timestamp_utc,
            symbol=self.symbol,
            bid_open=self.bid_open,
            bid_high=self.bid_high,
            bid_low=self.bid_low,
            bid_close=self.bid_close,
            ask_open=self.ask_open,
            ask_high=self.ask_high,
            ask_low=self.ask_low,
            ask_close=self.ask_close,
        )


def _minute_floor(value: datetime) -> datetime:
    return value.replace(second=0, microsecond=0)


def _first_full_minute(prepared_at: datetime) -> datetime:
    floor = _minute_floor(prepared_at)
    return floor if prepared_at == floor else floor + timedelta(minutes=1)


def _intersects(
    left_start: datetime,
    left_end: datetime,
    right_start: datetime,
    right_end: datetime,
) -> bool:
    return left_start < right_end and right_start < left_end


def _derive_minute_bars(
    *,
    symbol: str,
    quotes: Sequence[Phase8BQuote],
    prepared_at: datetime,
    market_gaps: Sequence[_MarketGap],
) -> tuple[QuoteBar, ...]:
    if not quotes:
        return ()
    first_allowed = _first_full_minute(prepared_at)
    latest_source = max(item.source_time_utc for item in quotes)
    accumulators: dict[datetime, _MinuteAccumulator] = {}
    for quote in quotes:
        label = _minute_floor(quote.source_time_utc)
        if label < first_allowed:
            continue
        current = accumulators.get(label)
        if current is None:
            accumulators[label] = _MinuteAccumulator.create(quote, label)
        else:
            current.update(quote)

    result: list[QuoteBar] = []
    for label in sorted(accumulators):
        end = label + timedelta(minutes=1)
        if end > latest_source:
            continue
        if any(
            gap.symbol == symbol
            and _intersects(label, end, gap.start_utc, gap.end_utc)
            for gap in market_gaps
        ):
            continue
        result.append(accumulators[label].to_bar())
    return tuple(result)


def _timeframe_label(value: datetime, minutes: int) -> datetime:
    if minutes == 60:
        return value.replace(minute=0, second=0, microsecond=0)
    return value.replace(
        minute=(value.minute // minutes) * minutes,
        second=0,
        microsecond=0,
    )


def _aggregate_bar_group(
    bars: Sequence[QuoteBar],
    *,
    label: datetime,
    symbol: str,
) -> QuoteBar:
    return QuoteBar(
        timestamp_utc=label,
        symbol=symbol,
        bid_open=bars[0].bid_open,
        bid_high=max(item.bid_high for item in bars),
        bid_low=min(item.bid_low for item in bars),
        bid_close=bars[-1].bid_close,
        ask_open=bars[0].ask_open,
        ask_high=max(item.ask_high for item in bars),
        ask_low=min(item.ask_low for item in bars),
        ask_close=bars[-1].ask_close,
    )


def _aggregate_minutes(
    minute_bars: Sequence[QuoteBar],
    *,
    timeframe: str,
) -> tuple[QuoteBar, ...]:
    minutes = _TIMEFRAME_MINUTES[timeframe]
    if minutes == 1:
        return tuple(minute_bars)
    by_label = {item.timestamp_utc: item for item in minute_bars}
    labels = sorted({_timeframe_label(item.timestamp_utc, minutes) for item in minute_bars})
    result: list[QuoteBar] = []
    for label in labels:
        expected = [label + timedelta(minutes=index) for index in range(minutes)]
        if not all(timestamp in by_label for timestamp in expected):
            continue
        group = [by_label[timestamp] for timestamp in expected]
        result.append(
            _aggregate_bar_group(
                group,
                label=label,
                symbol=group[0].symbol,
            )
        )
    return tuple(result)


def _bar_record(bar: QuoteBar) -> dict[str, object]:
    return {
        "timestamp_utc": _utc_string(bar.timestamp_utc),
        "symbol": bar.symbol,
        "bid_open": bar.bid_open,
        "bid_high": bar.bid_high,
        "bid_low": bar.bid_low,
        "bid_close": bar.bid_close,
        "ask_open": bar.ask_open,
        "ask_high": bar.ask_high,
        "ask_low": bar.ask_low,
        "ask_close": bar.ask_close,
    }


def _bound_candidate(
    strategy: StrategyVersion,
    candidate: SignalCandidate,
) -> SignalCandidate:
    if candidate.symbol != strategy.symbol:
        raise ValueError("Phase 8B generated candidate symbol mismatch")
    metadata = dict(candidate.metadata)
    metadata.update(
        {
            "original_candidate_id": candidate.candidate_id,
            "strategy_fingerprint": strategy.fingerprint,
            "strategy_family": strategy.family,
            "strategy_version": strategy.version,
            "strategy_timeframe": strategy.timeframe,
        }
    )
    return SignalCandidate(
        candidate_id=f"{strategy.fingerprint[:16]}::{candidate.candidate_id}",
        symbol=candidate.symbol,
        observation_bar_timestamp_utc=candidate.observation_bar_timestamp_utc,
        signal_known_timestamp_utc=candidate.signal_known_timestamp_utc,
        direction=candidate.direction,
        stop_price=candidate.stop_price,
        target_price=candidate.target_price,
        latest_exit_timestamp_utc=candidate.latest_exit_timestamp_utc,
        reason_code=candidate.reason_code,
        metadata=metadata,
    )


def _candidate_record(candidate: SignalCandidate) -> dict[str, object]:
    return {
        "candidate_id": candidate.candidate_id,
        "symbol": candidate.symbol,
        "observation_bar_timestamp_utc": _utc_string(
            candidate.observation_bar_timestamp_utc
        ),
        "signal_known_timestamp_utc": _utc_string(
            candidate.signal_known_timestamp_utc
        ),
        "direction": candidate.direction.value,
        "stop_price": candidate.stop_price,
        "target_price": candidate.target_price,
        "latest_exit_timestamp_utc": (
            None
            if candidate.latest_exit_timestamp_utc is None
            else _utc_string(candidate.latest_exit_timestamp_utc)
        ),
        "reason_code": candidate.reason_code,
        "metadata": dict(candidate.metadata),
    }


def _route_exposure_rows(
    accepted: Sequence[PortfolioCandidate],
) -> list[dict[str, object]]:
    grouped: dict[datetime, list[PortfolioCandidate]] = defaultdict(list)
    for candidate in accepted:
        grouped[candidate.observed_at_utc].append(candidate)
    rows: list[dict[str, object]] = []
    for timestamp in sorted(grouped):
        candidates = tuple(
            sorted(
                grouped[timestamp],
                key=lambda item: (
                    item.symbol,
                    item.strategy_fingerprint,
                    item.candidate_id,
                ),
            )
        )
        exposure = summarize_candidate_exposure(candidates)
        rows.append(
            {
                "signal_known_timestamp_utc": _utc_string(timestamp),
                "candidate_count": len(candidates),
                "candidate_ids": [item.candidate_id for item in candidates],
                "total_requested_risk_fraction": exposure.total_requested_risk_fraction,
                "usd_long_requested_risk_fraction": exposure.usd_long_requested_risk_fraction,
                "usd_short_requested_risk_fraction": exposure.usd_short_requested_risk_fraction,
                "gross_usd_directional_risk_fraction": (
                    exposure.gross_usd_directional_risk_fraction
                ),
                "net_usd_directional_risk_fraction": (
                    exposure.net_usd_directional_risk_fraction
                ),
            }
        )
    return rows


@dataclass(frozen=True, slots=True)
class _PendingDecision:
    decision: Decision
    scheduled_exit: ScheduledExit


@dataclass(frozen=True, slots=True)
class _OpenPosition:
    position: Position
    scheduled_exit: ScheduledExit


@dataclass(slots=True)
class _ScenarioState:
    slippage_pips: float
    risk_config: RiskConfig
    risk_state: RiskState
    pending_decisions: dict[str, _PendingDecision]
    open_positions: dict[str, _OpenPosition]
    completed_trades: list[TradeRecord]
    outcomes: dict[str, ShadowOutcome]
    rejections: dict[str, RejectionCode]


def _point_bar(quote: Phase8BQuote) -> QuoteBar:
    return QuoteBar(
        timestamp_utc=quote.source_time_utc,
        symbol=quote.symbol,
        bid_open=quote.bid,
        bid_high=quote.bid,
        bid_low=quote.bid,
        bid_close=quote.bid,
        ask_open=quote.ask,
        ask_high=quote.ask,
        ask_low=quote.ask,
        ask_close=quote.ask,
    )


class PortfolioShadowSimulator:
    def __init__(self) -> None:
        self.states: dict[float, _ScenarioState] = {
            slippage: _ScenarioState(
                slippage_pips=slippage,
                risk_config=RiskConfig(),
                risk_state=RiskState(starting_equity_usd=STARTING_EQUITY_USD),
                pending_decisions={},
                open_positions={},
                completed_trades=[],
                outcomes={},
                rejections={},
            )
            for slippage in SLIPPAGE_SCENARIOS
        }

    def register_decision(
        self,
        decision: Decision,
        scheduled_exit: ScheduledExit,
    ) -> None:
        if decision.direction not in {Direction.LONG, Direction.SHORT}:
            raise ValueError("Phase 8B shadow simulation requires directional decision")
        if scheduled_exit.decision_id != decision.decision_id:
            raise ValueError("Phase 8B scheduled exit identity mismatch")
        if scheduled_exit.symbol != decision.symbol:
            raise ValueError("Phase 8B scheduled exit symbol mismatch")
        earliest = decision.earliest_executable_timestamp_utc
        if earliest is None:
            raise ValueError("Phase 8B directional decision has no execution time")
        if scheduled_exit.timestamp_utc <= earliest:
            raise ValueError("Phase 8B scheduled exit must follow entry time")
        pending = _PendingDecision(decision=decision, scheduled_exit=scheduled_exit)
        for state in self.states.values():
            if any(
                decision.decision_id in collection
                for collection in (
                    state.pending_decisions,
                    state.open_positions,
                    state.outcomes,
                    state.rejections,
                )
            ):
                raise ValueError("duplicate Phase 8B shadow decision_id")
            state.pending_decisions[decision.decision_id] = pending

    def on_time_advance(self, now_utc: datetime) -> None:
        for state in self.states.values():
            for decision_id in sorted(tuple(state.pending_decisions)):
                pending = state.pending_decisions[decision_id]
                earliest = pending.decision.earliest_executable_timestamp_utc
                assert earliest is not None
                if now_utc > earliest + timedelta(seconds=QUOTE_DEADLINE_SECONDS):
                    state.pending_decisions.pop(decision_id, None)
                    state.outcomes[decision_id] = ShadowOutcome.ENTRY_DEADLINE_MISSED
            for decision_id in sorted(tuple(state.open_positions)):
                opened = state.open_positions.get(decision_id)
                if opened is None:
                    continue
                deadline = opened.scheduled_exit.timestamp_utc + timedelta(
                    seconds=QUOTE_DEADLINE_SECONDS
                )
                if now_utc > deadline:
                    self._invalidate(
                        state,
                        decision_id=decision_id,
                        outcome=ShadowOutcome.EXIT_DEADLINE_MISSED,
                    )

    def on_quote(self, quote: Phase8BQuote) -> None:
        self.on_time_advance(quote.source_time_utc)
        bar = _point_bar(quote)
        for state in self.states.values():
            for decision_id in sorted(tuple(state.open_positions)):
                opened = state.open_positions.get(decision_id)
                if opened is None or opened.position.symbol != quote.symbol:
                    continue
                position = opened.position
                if quote.source_time_utc < position.entry_timestamp_utc:
                    continue
                flat = opened.scheduled_exit.timestamp_utc
                if quote.source_time_utc >= flat:
                    if quote.source_time_utc <= flat + timedelta(
                        seconds=QUOTE_DEADLINE_SECONDS
                    ):
                        self._finalize(
                            state,
                            opened,
                            close_time_exit(
                                position,
                                bar,
                                slippage_pips=state.slippage_pips,
                                commission_model=ZeroCommission(),
                                financing_model=ZeroFinancing(),
                            ),
                        )
                    continue
                exit_fill = evaluate_exit(
                    position,
                    bar,
                    slippage_pips=state.slippage_pips,
                    commission_model=ZeroCommission(),
                    financing_model=ZeroFinancing(),
                )
                if exit_fill is not None:
                    self._finalize(state, opened, exit_fill)

        for state in self.states.values():
            for decision_id in sorted(tuple(state.pending_decisions)):
                pending = state.pending_decisions.get(decision_id)
                if pending is None or pending.decision.symbol != quote.symbol:
                    continue
                decision = pending.decision
                earliest = decision.earliest_executable_timestamp_utc
                assert earliest is not None
                if quote.source_time_utc < earliest:
                    continue
                if quote.source_time_utc > earliest + timedelta(
                    seconds=QUOTE_DEADLINE_SECONDS
                ):
                    continue
                assessment = assess_decision(
                    decision=decision,
                    reference_entry_price=entry_reference_price(
                        bar,
                        decision.direction,
                    ),
                    timestamp_utc=quote.source_time_utc,
                    config=state.risk_config,
                    state=state.risk_state,
                )
                state.pending_decisions.pop(decision_id, None)
                if not assessment.approved:
                    assert assessment.rejection_code is not None
                    state.rejections[decision_id] = assessment.rejection_code
                    continue
                assert decision.stop_price is not None
                intent = OrderIntent(
                    decision_id=decision.decision_id,
                    symbol=decision.symbol,
                    direction=decision.direction,
                    units=assessment.approved_units,
                    reserved_risk_usd=assessment.approved_risk_usd,
                    stop_price=decision.stop_price,
                    target_price=decision.target_price,
                    decision_timestamp_utc=decision.decision_timestamp_utc,
                    earliest_executable_timestamp_utc=quote.source_time_utc,
                )
                position = fill_entry(
                    intent,
                    bar,
                    slippage_pips=state.slippage_pips,
                    commission_model=ZeroCommission(),
                )
                reserve_risk(
                    state.risk_state,
                    position_id=position.position_id,
                    amount_usd=position.reserved_risk_usd,
                )
                state.open_positions[decision_id] = _OpenPosition(
                    position=position,
                    scheduled_exit=pending.scheduled_exit,
                )

    def mark_stale_gap(
        self,
        symbol: str,
        start_utc: datetime,
        end_utc: datetime,
    ) -> None:
        if end_utc < start_utc:
            raise ValueError("Phase 8B stale interval end precedes start")
        for state in self.states.values():
            for decision_id in sorted(tuple(state.open_positions)):
                opened = state.open_positions[decision_id]
                if opened.position.symbol != symbol:
                    continue
                if end_utc < opened.position.entry_timestamp_utc:
                    continue
                self._invalidate(
                    state,
                    decision_id=decision_id,
                    outcome=ShadowOutcome.OUTCOME_UNKNOWN_AFTER_GAP,
                )

    @staticmethod
    def _invalidate(
        state: _ScenarioState,
        *,
        decision_id: str,
        outcome: ShadowOutcome,
    ) -> None:
        opened = state.open_positions.pop(decision_id, None)
        if opened is None:
            return
        release_risk(
            state.risk_state,
            position_id=opened.position.position_id,
        )
        state.outcomes[decision_id] = outcome

    @staticmethod
    def _finalize(
        state: _ScenarioState,
        opened: _OpenPosition,
        exit_fill,
    ) -> None:
        position = opened.position
        before = state.risk_state.risk_equity_usd
        gross = pnl_usd(
            symbol=position.symbol,
            direction=position.direction,
            units=position.units,
            entry_price=position.entry_reference_price,
            exit_price=exit_fill.reference_price,
        )
        slipped = pnl_usd(
            symbol=position.symbol,
            direction=position.direction,
            units=position.units,
            entry_price=position.entry_price,
            exit_price=exit_fill.execution_price,
        )
        slippage_cost = max(0.0, gross - slipped)
        commission_cost = position.entry_commission_usd + exit_fill.exit_commission_usd
        financing_cost = exit_fill.financing_cost_usd
        net = gross - slippage_cost - commission_cost - financing_cost
        release_risk(
            state.risk_state,
            position_id=position.position_id,
        )
        record_realized_pnl(
            state.risk_state,
            timestamp_utc=exit_fill.timestamp_utc,
            pnl_usd=net,
            config=state.risk_config,
        )
        after = state.risk_state.risk_equity_usd
        state.completed_trades.append(
            TradeRecord(
                trade_id=position.position_id,
                decision_id=position.decision_id,
                symbol=position.symbol,
                direction=position.direction,
                units=position.units,
                entry_timestamp_utc=position.entry_timestamp_utc,
                exit_timestamp_utc=exit_fill.timestamp_utc,
                entry_reference_price=position.entry_reference_price,
                exit_reference_price=exit_fill.reference_price,
                entry_price=position.entry_price,
                exit_price=exit_fill.execution_price,
                stop_price=position.stop_price,
                target_price=position.target_price,
                exit_reason=exit_fill.reason,
                intrabar_ambiguous=exit_fill.intrabar_ambiguous,
                gross_pnl_usd=gross,
                slippage_cost_usd=slippage_cost,
                commission_cost_usd=commission_cost,
                financing_cost_usd=financing_cost,
                net_pnl_usd=net,
                risk_equity_before_usd=before,
                risk_equity_after_usd=after,
            )
        )
        state.open_positions.pop(position.decision_id, None)
        state.outcomes[position.decision_id] = ShadowOutcome.COMPLETED


def _scenario_record(state: _ScenarioState) -> dict[str, object]:
    ordered_trades = tuple(
        sorted(
            state.completed_trades,
            key=lambda item: (item.exit_timestamp_utc, item.trade_id),
        )
    )
    checkpoints = tuple(
        EquityCheckpoint(
            timestamp_utc=item.exit_timestamp_utc,
            realized_risk_equity_usd=item.risk_equity_after_usd,
        )
        for item in ordered_trades
    )
    metrics = compute_backtest_metrics(
        starting_equity_usd=STARTING_EQUITY_USD,
        trades=ordered_trades,
        equity_checkpoints=checkpoints,
    )
    return {
        "slippage_pips": state.slippage_pips,
        "risk_config": state.risk_config.to_config(),
        "completed_trades": [_jsonable(item) for item in ordered_trades],
        "risk_rejections": {
            key: value.value for key, value in sorted(state.rejections.items())
        },
        "outcomes": {
            key: value.value for key, value in sorted(state.outcomes.items())
        },
        "open_decision_ids": sorted(state.open_positions),
        "pending_decision_ids": sorted(state.pending_decisions),
        "metrics": metrics,
    }


def _capture_digest(fingerprints: Sequence[str]) -> str:
    digest = hashlib.sha256()
    for fingerprint in fingerprints:
        encoded = fingerprint.encode("ascii")
        digest.update(len(encoded).to_bytes(8, byteorder="big", signed=False))
        digest.update(encoded)
    return digest.hexdigest()


def _ordered_capture(
    *,
    preflight: Mapping[str, object],
    capture_records: Sequence[Mapping[str, object]],
) -> tuple[
    list[dict[str, object]],
    list[Phase8BQuote],
    list[_MarketGap],
    list[_BridgeGap],
]:
    materialized: list[dict[str, object]] = []
    quotes: list[Phase8BQuote] = []
    market_gaps: list[_MarketGap] = []
    bridge_gaps: list[_BridgeGap] = []
    last_monotonic: int | None = None
    last_bridge_by_symbol: dict[str, tuple[int, datetime]] = {}
    last_tick_by_symbol: dict[str, tuple[int, datetime]] = {}
    last_source_msc_by_symbol: dict[str, int] = {}

    for raw in capture_records:
        if not isinstance(raw, Mapping):
            raise TypeError("Phase 8B capture records must be objects")
        envelope = dict(raw)
        validate_phase8b_capture_record_envelope(
            envelope,
            preflight=preflight,
        )
        monotonic = envelope.get("receive_monotonic_ns")
        assert isinstance(monotonic, int) and not isinstance(monotonic, bool)
        if last_monotonic is not None and monotonic < last_monotonic:
            raise ValueError("Phase 8B capture monotonic receive order regressed")
        last_monotonic = monotonic
        received = _parse_utc(
            envelope.get("received_at_utc"),
            field="Phase 8B capture receive timestamp",
        )
        record = _bridge_record_from_envelope(envelope)
        symbol = record.symbol

        prior_bridge = last_bridge_by_symbol.get(symbol)
        if prior_bridge is not None:
            prior_ns, prior_received = prior_bridge
            gap_seconds = (monotonic - prior_ns) / 1_000_000_000
            if gap_seconds > LIVENESS_TIMEOUT_SECONDS:
                bridge_gaps.append(
                    _BridgeGap(
                        symbol=symbol,
                        previous_received_at_utc=prior_received,
                        received_at_utc=received,
                        receive_gap_seconds=gap_seconds,
                    )
                )
        last_bridge_by_symbol[symbol] = (monotonic, received)

        if isinstance(record, Phase8BBridgeTickRecord):
            prior_source = last_source_msc_by_symbol.get(symbol)
            if prior_source is not None and record.source_time_msc <= prior_source:
                raise ValueError("Phase 8B capture tick source time did not advance")
            last_source_msc_by_symbol[symbol] = record.source_time_msc
            quote = _tick_to_quote(record, envelope)
            prior_tick = last_tick_by_symbol.get(symbol)
            if prior_tick is not None:
                prior_ns, prior_source_time = prior_tick
                market_gap_seconds = (monotonic - prior_ns) / 1_000_000_000
                if market_gap_seconds > LIVENESS_TIMEOUT_SECONDS:
                    market_gaps.append(
                        _MarketGap(
                            symbol=symbol,
                            start_utc=prior_source_time,
                            end_utc=quote.source_time_utc,
                            detected_at_utc=quote.source_time_utc,
                            receive_gap_seconds=market_gap_seconds,
                        )
                    )
            last_tick_by_symbol[symbol] = (
                monotonic,
                quote.source_time_utc,
            )
            quotes.append(quote)
        elif not isinstance(record, Phase8BBridgeHeartbeatRecord):
            raise ValueError("Phase 8B runtime received unsupported bridge record")
        materialized.append(envelope)

    return materialized, quotes, market_gaps, bridge_gaps


def _candidate_and_routing(
    *,
    champion: ChampionSet,
    bars: Mapping[str, Mapping[str, tuple[QuoteBar, ...]]],
) -> tuple[
    list[SignalCandidate],
    tuple[PortfolioCandidate, ...],
    object,
]:
    bound: list[SignalCandidate] = []
    for strategy in champion.strategies:
        source = bars.get(strategy.symbol, {}).get(strategy.timeframe, ())
        generated = generate_strategy_candidates(strategy, source)
        for candidate in generated:
            if not isinstance(candidate, SignalCandidate):
                raise TypeError("Phase 8B strategy generator returned invalid candidate")
            bound.append(_bound_candidate(strategy, candidate))
    bound.sort(
        key=lambda item: (
            item.signal_known_timestamp_utc,
            item.symbol,
            item.candidate_id,
        )
    )
    ids = [item.candidate_id for item in bound]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate Phase 8B bound candidate identity")
    directional = tuple(
        PortfolioCandidate(
            candidate_id=item.candidate_id,
            strategy_fingerprint=str(item.metadata["strategy_fingerprint"]),
            symbol=item.symbol,
            direction=item.direction,
            observed_at_utc=item.signal_known_timestamp_utc,
            requested_risk_fraction=REQUESTED_RISK_FRACTION,
            applicability_passed=True,
        )
        for item in bound
        if item.direction in {Direction.LONG, Direction.SHORT}
    )
    route = route_shadow_candidates(champion, directional)
    return bound, directional, route


def _run_simulation(
    *,
    accepted_ids: set[str],
    candidates: Sequence[SignalCandidate],
    quotes: Sequence[Phase8BQuote],
    market_gaps: Sequence[_MarketGap],
) -> PortfolioShadowSimulator:
    simulator = PortfolioShadowSimulator()
    decision_events: dict[datetime, list[tuple[Decision, ScheduledExit]]] = defaultdict(list)
    for candidate in candidates:
        if candidate.candidate_id not in accepted_ids:
            continue
        decision, scheduled = candidate_to_decision(
            candidate,
            next_bar_timestamp_utc=candidate.signal_known_timestamp_utc,
            requested_risk_fraction=REQUESTED_RISK_FRACTION,
        )
        if decision.direction is Direction.NO_TRADE:
            continue
        if scheduled is None:
            raise ValueError("Phase 8B directional candidate has no scheduled exit")
        decision_events[candidate.signal_known_timestamp_utc].append(
            (decision, scheduled)
        )

    quote_events: dict[datetime, list[Phase8BQuote]] = defaultdict(list)
    for quote in quotes:
        quote_events[quote.source_time_utc].append(quote)
    gap_events: dict[datetime, list[_MarketGap]] = defaultdict(list)
    for gap in market_gaps:
        gap_events[gap.detected_at_utc].append(gap)

    timestamps = sorted(set(decision_events) | set(quote_events) | set(gap_events))
    for timestamp in timestamps:
        for decision, scheduled in sorted(
            decision_events.get(timestamp, ()),
            key=lambda item: item[0].decision_id,
        ):
            simulator.register_decision(decision, scheduled)
        for gap in sorted(
            gap_events.get(timestamp, ()),
            key=lambda item: (item.symbol, item.start_utc, item.end_utc),
        ):
            simulator.on_time_advance(timestamp)
            simulator.mark_stale_gap(
                gap.symbol,
                gap.start_utc,
                gap.end_utc,
            )
        for quote in sorted(
            quote_events.get(timestamp, ()),
            key=lambda item: item.symbol,
        ):
            simulator.on_quote(quote)
    return simulator


def compile_phase8b_segment(
    *,
    preflight: Mapping[str, object],
    capture_records: Sequence[Mapping[str, object]],
    code_commit: str,
) -> dict[str, object]:
    validate_phase8b_capture_preflight(preflight)
    commit = _validate_commit(
        code_commit,
        field="Phase 8B runtime code commit",
    )
    champion = reconstruct_phase8b_champion_set(preflight)
    materialized, quotes, market_gaps, bridge_gaps = _ordered_capture(
        preflight=preflight,
        capture_records=capture_records,
    )
    prepared_at = _parse_utc(
        preflight.get("prepared_at_utc"),
        field="Phase 8B capture preflight timestamp",
    )
    required_symbols = tuple(str(item) for item in preflight["required_symbols"])
    required_timeframes = tuple(
        str(item) for item in preflight["required_timeframes"]
    )

    bars: dict[str, dict[str, tuple[QuoteBar, ...]]] = {}
    quotes_by_symbol: dict[str, list[Phase8BQuote]] = defaultdict(list)
    for quote in quotes:
        quotes_by_symbol[quote.symbol].append(quote)
    for symbol in required_symbols:
        symbol_quotes = tuple(
            sorted(
                quotes_by_symbol.get(symbol, ()),
                key=lambda item: item.source_time_utc,
            )
        )
        minute = _derive_minute_bars(
            symbol=symbol,
            quotes=symbol_quotes,
            prepared_at=prepared_at,
            market_gaps=market_gaps,
        )
        bars[symbol] = {"1m": minute}
        for timeframe in required_timeframes:
            bars[symbol][timeframe] = _aggregate_minutes(
                minute,
                timeframe=timeframe,
            )

    candidates, _directional, route = _candidate_and_routing(
        champion=champion,
        bars=bars,
    )
    accepted_ids = {item.candidate_id for item in route.accepted}
    simulator = _run_simulation(
        accepted_ids=accepted_ids,
        candidates=candidates,
        quotes=quotes,
        market_gaps=market_gaps,
    )

    fingerprints = [
        _validate_sha256(
            row.get("record_fingerprint"),
            field="Phase 8B capture-record fingerprint",
        )
        for row in materialized
    ]
    operational_events = [
        {
            "event": "BRIDGE_LIVENESS_GAP",
            "symbol": item.symbol,
            "previous_received_at_utc": _utc_string(
                item.previous_received_at_utc
            ),
            "received_at_utc": _utc_string(item.received_at_utc),
            "receive_gap_seconds": item.receive_gap_seconds,
        }
        for item in bridge_gaps
    ] + [
        {
            "event": "MARKET_LIVENESS_GAP",
            "symbol": item.symbol,
            "start_utc": _utc_string(item.start_utc),
            "end_utc": _utc_string(item.end_utc),
            "receive_gap_seconds": item.receive_gap_seconds,
        }
        for item in market_gaps
    ]
    operational_events.sort(
        key=lambda item: (
            str(item["event"]),
            str(item["symbol"]),
            str(item.get("start_utc", item.get("previous_received_at_utc", ""))),
        )
    )

    payload = {
        "protocol": PHASE8B_SEGMENT_PROTOCOL,
        "experiment_id": PHASE8B_RUNTIME_EXPERIMENT_ID,
        "outcome": PHASE8B_RUNTIME_REPLAY_KERNEL_READY,
        "capture_preflight_fingerprint": preflight[
            "capture_preflight_fingerprint"
        ],
        "segment_code_commit": commit,
        "champion_set_id": preflight["champion_set_id"],
        "champion_set_fingerprint": preflight[
            "champion_set_fingerprint"
        ],
        "strategy_fingerprints": list(preflight["strategy_fingerprints"]),
        "required_symbols": list(required_symbols),
        "required_timeframes": list(required_timeframes),
        "reader_start_semantics": preflight["reader_start_semantics"],
        "capture_record_count": len(materialized),
        "capture_record_fingerprints": fingerprints,
        "capture_records_sha256": _capture_digest(fingerprints),
        "quote_count": len(quotes),
        "bars": {
            symbol: {
                timeframe: [_bar_record(item) for item in bars[symbol][timeframe]]
                for timeframe in ("1m", "5m", "15m", "1h")
                if timeframe == "1m" or timeframe in required_timeframes
            }
            for symbol in required_symbols
        },
        "generated_candidates": [_candidate_record(item) for item in candidates],
        "routing": {
            "accepted_candidate_ids": [
                item.candidate_id for item in route.accepted
            ],
            "rejected": [
                {
                    "candidate_id": item.candidate_id,
                    "code": item.code.value,
                    "explanation": item.explanation,
                }
                for item in route.rejected
            ],
            "exposure_by_signal_time": _route_exposure_rows(route.accepted),
        },
        "scenarios": {
            str(slippage): _scenario_record(simulator.states[slippage])
            for slippage in SLIPPAGE_SCENARIOS
        },
        "operational_events": operational_events,
        "live_shadow_segment_started": False,
        "acceptance_authorized": False,
        "promotion_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_authorized": False,
    }
    return payload | {"segment_fingerprint": _canonical_digest(payload)}


def validate_phase8b_segment(segment: Mapping[str, object]) -> None:
    if segment.get("protocol") != PHASE8B_SEGMENT_PROTOCOL:
        raise ValueError("Phase 8B segment protocol mismatch")
    if segment.get("experiment_id") != PHASE8B_RUNTIME_EXPERIMENT_ID:
        raise ValueError("Phase 8B segment experiment mismatch")
    if segment.get("outcome") != PHASE8B_RUNTIME_REPLAY_KERNEL_READY:
        raise ValueError("Phase 8B segment outcome mismatch")
    _validate_commit(
        segment.get("segment_code_commit"),
        field="Phase 8B segment code commit",
    )
    for field in (
        "capture_preflight_fingerprint",
        "champion_set_fingerprint",
        "capture_records_sha256",
        "segment_fingerprint",
    ):
        _validate_sha256(
            segment.get(field),
            field=f"Phase 8B segment {field}",
        )
    fingerprint = segment["segment_fingerprint"]
    payload = dict(segment)
    payload.pop("segment_fingerprint", None)
    if fingerprint != _canonical_digest(payload):
        raise ValueError("Phase 8B segment fingerprint mismatch")
    fingerprints = segment.get("capture_record_fingerprints")
    if not isinstance(fingerprints, list):
        raise ValueError("Phase 8B segment capture fingerprint list is malformed")
    if segment.get("capture_record_count") != len(fingerprints):
        raise ValueError("Phase 8B segment capture record count mismatch")
    if _capture_digest([str(item) for item in fingerprints]) != segment.get(
        "capture_records_sha256"
    ):
        raise ValueError("Phase 8B segment capture digest mismatch")
    for field in (
        "live_shadow_segment_started",
        "acceptance_authorized",
        "promotion_authorized",
        "demo_order_authorized",
        "live_order_authorized",
        "broker_mutation_authorized",
        "real_money_authorized",
        "phase9_authorized",
    ):
        if segment.get(field) is not False:
            raise ValueError(f"Phase 8B segment requires {field}=false")


def replay_phase8b_segment(
    *,
    expected_segment: Mapping[str, object],
    preflight: Mapping[str, object],
    capture_records: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    validate_phase8b_segment(expected_segment)
    if expected_segment.get("capture_preflight_fingerprint") != preflight.get(
        "capture_preflight_fingerprint"
    ):
        raise ValueError("Phase 8B replay preflight mismatch")
    replayed = compile_phase8b_segment(
        preflight=preflight,
        capture_records=capture_records,
        code_commit=str(expected_segment["segment_code_commit"]),
    )
    expected_bytes = _canonical_bytes(expected_segment)
    replay_bytes = _canonical_bytes(replayed)
    result = {
        "protocol": PHASE8B_REPLAY_PROTOCOL,
        "experiment_id": PHASE8B_RUNTIME_EXPERIMENT_ID,
        "capture_preflight_fingerprint": preflight[
            "capture_preflight_fingerprint"
        ],
        "expected_segment_fingerprint": expected_segment[
            "segment_fingerprint"
        ],
        "replay_segment_fingerprint": replayed["segment_fingerprint"],
        "expected_segment_sha256": hashlib.sha256(expected_bytes).hexdigest(),
        "replay_segment_sha256": hashlib.sha256(replay_bytes).hexdigest(),
        "match": expected_bytes == replay_bytes,
        "acceptance_authorized": False,
        "promotion_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_authorized": False,
    }
    return result


def write_phase8b_segment_artifacts(
    *,
    segment: Mapping[str, object],
    replay: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    validate_phase8b_segment(segment)
    if replay.get("protocol") != PHASE8B_REPLAY_PROTOCOL:
        raise ValueError("Phase 8B replay protocol mismatch")
    root = Path(out_dir)
    segment_path = root / "segment.json"
    replay_path = root / "replay.json"
    manifest_path = root / "manifest.json"
    if segment_path.exists() or replay_path.exists() or manifest_path.exists():
        raise FileExistsError("Phase 8B segment artifacts already exist")
    root.mkdir(parents=True, exist_ok=True)
    segment_bytes = _stable_json_bytes(segment)
    replay_bytes = _stable_json_bytes(replay)
    _atomic_write(segment_path, segment_bytes)
    _atomic_write(replay_path, replay_bytes)
    manifest = {
        "protocol": PHASE8B_SEGMENT_ARTIFACT_PROTOCOL,
        "experiment_id": PHASE8B_RUNTIME_EXPERIMENT_ID,
        "replay_match": replay.get("match") is True,
        "acceptance_authorized": False,
        "promotion_authorized": False,
        "artifacts": [
            {
                "path": segment_path.name,
                "size_bytes": len(segment_bytes),
                "sha256": hashlib.sha256(segment_bytes).hexdigest(),
            },
            {
                "path": replay_path.name,
                "size_bytes": len(replay_bytes),
                "sha256": hashlib.sha256(replay_bytes).hexdigest(),
            },
        ],
    }
    _atomic_write(manifest_path, _stable_json_bytes(manifest))
    return manifest


__all__ = [
    "LIVENESS_TIMEOUT_SECONDS",
    "PHASE8B_REPLAY_PROTOCOL",
    "PHASE8B_RUNTIME_EXPERIMENT_ID",
    "PHASE8B_RUNTIME_REPLAY_KERNEL_READY",
    "PHASE8B_SEGMENT_ARTIFACT_PROTOCOL",
    "PHASE8B_SEGMENT_PROTOCOL",
    "PortfolioShadowSimulator",
    "compile_phase8b_segment",
    "reconstruct_phase8b_champion_set",
    "replay_phase8b_segment",
    "validate_phase8b_segment",
    "write_phase8b_segment_artifacts",
]
