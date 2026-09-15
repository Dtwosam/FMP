from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from fmp.backtest.costs import ZeroCommission, ZeroFinancing, apply_adverse_slippage
from fmp.backtest.execution import (
    close_time_exit,
    entry_reference_price,
    evaluate_exit,
    fill_entry,
)
from fmp.contracts import (
    Decision,
    Direction,
    ExitReason,
    OrderIntent,
    Position,
    QuoteBar,
    RejectionCode,
    ScheduledExit,
    TradeRecord,
)
from fmp.risk import (
    RiskConfig,
    RiskState,
    assess_decision,
    pnl_usd,
    record_realized_pnl,
    release_risk,
    reserve_risk,
)

from .contracts import (
    FMP_SYMBOL,
    NormalizedQuote,
    QUOTE_DEADLINE_SECONDS,
    SLIPPAGE_SCENARIOS,
    STARTING_EQUITY_USD,
    ShadowOutcome,
)


@dataclass(frozen=True, slots=True)
class PendingShadowDecision:
    decision: Decision
    scheduled_exit: ScheduledExit


@dataclass(frozen=True, slots=True)
class ShadowPosition:
    position: Position
    scheduled_exit: ScheduledExit
    slippage_pips: float


ShadowTrade = TradeRecord


@dataclass(slots=True)
class ScenarioState:
    slippage_pips: float
    risk_config: RiskConfig = field(default_factory=RiskConfig)
    risk_state: RiskState = field(
        default_factory=lambda: RiskState(starting_equity_usd=STARTING_EQUITY_USD)
    )
    commission_model: ZeroCommission = field(default_factory=ZeroCommission)
    financing_model: ZeroFinancing = field(default_factory=ZeroFinancing)
    pending_decisions: dict[str, PendingShadowDecision] = field(default_factory=dict)
    open_positions: dict[str, ShadowPosition] = field(default_factory=dict)
    completed_trades: list[ShadowTrade] = field(default_factory=list)
    outcomes: dict[str, ShadowOutcome] = field(default_factory=dict)
    rejections: dict[str, RejectionCode] = field(default_factory=dict)


def _require_utc(value: datetime, *, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field_name} must use UTC")


def _point_bar(quote: NormalizedQuote) -> QuoteBar:
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


def _deadline(start_utc: datetime) -> datetime:
    return start_utc + timedelta(seconds=QUOTE_DEADLINE_SECONDS)


class ShadowSimulator:
    def __init__(self) -> None:
        self.states: dict[float, ScenarioState] = {
            slippage: ScenarioState(slippage_pips=slippage)
            for slippage in SLIPPAGE_SCENARIOS
        }

    def register_decision(
        self,
        decision: Decision,
        scheduled_exit: ScheduledExit,
    ) -> None:
        if decision.direction not in {Direction.LONG, Direction.SHORT}:
            raise ValueError("Phase 8 simulation requires a directional decision")
        if decision.symbol != FMP_SYMBOL or scheduled_exit.symbol != FMP_SYMBOL:
            raise ValueError(f"Phase 8 simulation supports only {FMP_SYMBOL}")
        if scheduled_exit.decision_id != decision.decision_id:
            raise ValueError("scheduled exit must match decision_id")
        earliest = decision.earliest_executable_timestamp_utc
        if earliest is None:
            raise ValueError("directional decision requires earliest executable timestamp")
        if scheduled_exit.timestamp_utc <= earliest:
            raise ValueError("scheduled exit must follow earliest executable timestamp")
        pending = PendingShadowDecision(decision=decision, scheduled_exit=scheduled_exit)
        for state in self.states.values():
            if (
                decision.decision_id in state.pending_decisions
                or decision.decision_id in state.open_positions
                or decision.decision_id in state.outcomes
                or decision.decision_id in state.rejections
            ):
                raise ValueError(f"duplicate shadow decision_id: {decision.decision_id!r}")
            state.pending_decisions[decision.decision_id] = pending

    def on_time_advance(self, now_utc: datetime) -> None:
        _require_utc(now_utc, field_name="now_utc")
        for state in self.states.values():
            for decision_id in sorted(tuple(state.pending_decisions)):
                pending = state.pending_decisions[decision_id]
                earliest = pending.decision.earliest_executable_timestamp_utc
                assert earliest is not None
                if now_utc > _deadline(earliest):
                    state.pending_decisions.pop(decision_id, None)
                    state.outcomes[decision_id] = ShadowOutcome.ENTRY_DEADLINE_MISSED

            for decision_id in sorted(tuple(state.open_positions)):
                shadow_position = state.open_positions.get(decision_id)
                if shadow_position is None:
                    continue
                if now_utc > _deadline(shadow_position.scheduled_exit.timestamp_utc):
                    self._invalidate_open_position(
                        state,
                        decision_id=decision_id,
                        outcome=ShadowOutcome.EXIT_DEADLINE_MISSED,
                    )

    def on_quote(self, quote: NormalizedQuote) -> None:
        self.on_time_advance(quote.source_time_utc)
        if not quote.tradeable:
            return
        bar = _point_bar(quote)

        # Existing hypothetical positions are evaluated before same-timestamp entries,
        # matching the Phase 3 accounting order. Scheduled flat takes precedence over
        # stop/target checks for the first eligible quote at or after the flat time.
        for state in self.states.values():
            for decision_id in sorted(tuple(state.open_positions)):
                shadow_position = state.open_positions.get(decision_id)
                if shadow_position is None:
                    continue
                position = shadow_position.position
                if quote.source_time_utc < position.entry_timestamp_utc:
                    continue
                flat = shadow_position.scheduled_exit.timestamp_utc
                if quote.source_time_utc >= flat:
                    if quote.source_time_utc <= _deadline(flat):
                        self._finalize_position(
                            state,
                            shadow_position,
                            close_time_exit(
                                position,
                                bar,
                                slippage_pips=state.slippage_pips,
                                commission_model=state.commission_model,
                                financing_model=state.financing_model,
                            ),
                        )
                    continue

                exit_fill = evaluate_exit(
                    position,
                    bar,
                    slippage_pips=state.slippage_pips,
                    commission_model=state.commission_model,
                    financing_model=state.financing_model,
                )
                if exit_fill is not None:
                    self._finalize_position(state, shadow_position, exit_fill)

        for state in self.states.values():
            for decision_id in sorted(tuple(state.pending_decisions)):
                pending = state.pending_decisions.get(decision_id)
                if pending is None:
                    continue
                decision = pending.decision
                earliest = decision.earliest_executable_timestamp_utc
                assert earliest is not None
                if quote.source_time_utc < earliest:
                    continue
                if quote.source_time_utc > _deadline(earliest):
                    continue

                reference_entry = entry_reference_price(bar, decision.direction)
                assessment = assess_decision(
                    decision=decision,
                    reference_entry_price=reference_entry,
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
                private_intent = OrderIntent(
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
                    private_intent,
                    bar,
                    slippage_pips=state.slippage_pips,
                    commission_model=state.commission_model,
                )
                reserve_risk(
                    state.risk_state,
                    position_id=position.position_id,
                    amount_usd=position.reserved_risk_usd,
                )
                state.open_positions[decision_id] = ShadowPosition(
                    position=position,
                    scheduled_exit=pending.scheduled_exit,
                    slippage_pips=state.slippage_pips,
                )

    def mark_stale_gap(self, start_utc: datetime, end_utc: datetime) -> None:
        _require_utc(start_utc, field_name="start_utc")
        _require_utc(end_utc, field_name="end_utc")
        if end_utc < start_utc:
            raise ValueError("stale interval end cannot precede start")
        for state in self.states.values():
            for decision_id in sorted(tuple(state.open_positions)):
                shadow_position = state.open_positions[decision_id]
                if end_utc < shadow_position.position.entry_timestamp_utc:
                    continue
                self._invalidate_open_position(
                    state,
                    decision_id=decision_id,
                    outcome=ShadowOutcome.OUTCOME_UNKNOWN_AFTER_GAP,
                )

    @staticmethod
    def _invalidate_open_position(
        state: ScenarioState,
        *,
        decision_id: str,
        outcome: ShadowOutcome,
    ) -> None:
        shadow_position = state.open_positions.pop(decision_id, None)
        if shadow_position is None:
            return
        release_risk(state.risk_state, position_id=shadow_position.position.position_id)
        state.outcomes[decision_id] = outcome

    @staticmethod
    def _finalize_position(state: ScenarioState, shadow_position: ShadowPosition, exit_fill) -> None:
        position = shadow_position.position
        risk_equity_before = state.risk_state.risk_equity_usd
        gross_pnl = pnl_usd(
            symbol=position.symbol,
            direction=position.direction,
            units=position.units,
            entry_price=position.entry_reference_price,
            exit_price=exit_fill.reference_price,
        )
        slipped_pnl = pnl_usd(
            symbol=position.symbol,
            direction=position.direction,
            units=position.units,
            entry_price=position.entry_price,
            exit_price=exit_fill.execution_price,
        )
        slippage_cost = max(0.0, gross_pnl - slipped_pnl)
        commission_cost = position.entry_commission_usd + exit_fill.exit_commission_usd
        financing_cost = exit_fill.financing_cost_usd
        net_pnl = gross_pnl - slippage_cost - commission_cost - financing_cost

        release_risk(state.risk_state, position_id=position.position_id)
        record_realized_pnl(
            state.risk_state,
            timestamp_utc=exit_fill.timestamp_utc,
            pnl_usd=net_pnl,
            config=state.risk_config,
        )
        risk_equity_after = state.risk_state.risk_equity_usd
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
                gross_pnl_usd=gross_pnl,
                slippage_cost_usd=slippage_cost,
                commission_cost_usd=commission_cost,
                financing_cost_usd=financing_cost,
                net_pnl_usd=net_pnl,
                risk_equity_before_usd=risk_equity_before,
                risk_equity_after_usd=risk_equity_after,
            )
        )
        state.open_positions.pop(position.position_id, None)
        state.outcomes[position.decision_id] = ShadowOutcome.COMPLETED


__all__ = [
    "PendingShadowDecision",
    "ScenarioState",
    "ShadowPosition",
    "ShadowSimulator",
    "ShadowTrade",
]
