from __future__ import annotations

from dataclasses import dataclass

from fmp.backtest.costs import (
    CommissionModel,
    FinancingModel,
    apply_adverse_slippage,
)
from fmp.contracts import (
    Direction,
    ExitReason,
    OrderIntent,
    OrderSide,
    Position,
    QuoteBar,
)


@dataclass(frozen=True, slots=True)
class ExitFill:
    timestamp_utc: object
    reference_price: float
    execution_price: float
    reason: ExitReason
    intrabar_ambiguous: bool
    exit_commission_usd: float
    financing_cost_usd: float


def _entry_side(direction: Direction) -> OrderSide:
    if direction is Direction.LONG:
        return OrderSide.BUY
    if direction is Direction.SHORT:
        return OrderSide.SELL
    raise ValueError("entry direction must be LONG or SHORT")


def _exit_side(direction: Direction) -> OrderSide:
    if direction is Direction.LONG:
        return OrderSide.SELL
    if direction is Direction.SHORT:
        return OrderSide.BUY
    raise ValueError("exit direction must be LONG or SHORT")


def entry_reference_price(bar: QuoteBar, direction: Direction) -> float:
    if direction is Direction.LONG:
        return bar.ask_open
    if direction is Direction.SHORT:
        return bar.bid_open
    raise ValueError("entry direction must be LONG or SHORT")


def fill_entry(
    intent: OrderIntent,
    bar: QuoteBar,
    *,
    slippage_pips: float,
    commission_model: CommissionModel,
) -> Position:
    if intent.symbol != bar.symbol:
        raise ValueError("order intent symbol does not match quote bar")
    if intent.earliest_executable_timestamp_utc != bar.timestamp_utc:
        raise ValueError("entry bar timestamp does not match earliest executable timestamp")
    reference = entry_reference_price(bar, intent.direction)
    execution = apply_adverse_slippage(
        reference,
        side=_entry_side(intent.direction),
        pips=slippage_pips,
        symbol=intent.symbol,
    )
    return Position(
        position_id=intent.decision_id,
        decision_id=intent.decision_id,
        symbol=intent.symbol,
        direction=intent.direction,
        units=intent.units,
        entry_timestamp_utc=bar.timestamp_utc,
        entry_reference_price=reference,
        entry_price=execution,
        entry_commission_usd=commission_model.cost_usd(units=intent.units),
        stop_price=intent.stop_price,
        target_price=intent.target_price,
        reserved_risk_usd=intent.reserved_risk_usd,
    )


def _make_exit_fill(
    position: Position,
    bar: QuoteBar,
    *,
    reference_price: float,
    reason: ExitReason,
    intrabar_ambiguous: bool,
    slippage_pips: float,
    commission_model: CommissionModel,
    financing_model: FinancingModel,
) -> ExitFill:
    execution = apply_adverse_slippage(
        reference_price,
        side=_exit_side(position.direction),
        pips=slippage_pips,
        symbol=position.symbol,
    )
    return ExitFill(
        timestamp_utc=bar.timestamp_utc,
        reference_price=reference_price,
        execution_price=execution,
        reason=reason,
        intrabar_ambiguous=intrabar_ambiguous,
        exit_commission_usd=commission_model.cost_usd(units=position.units),
        financing_cost_usd=financing_model.cost_usd(
            symbol=position.symbol,
            direction=position.direction,
            units=position.units,
            entry_timestamp_utc=position.entry_timestamp_utc,
            exit_timestamp_utc=bar.timestamp_utc,
        ),
    )


def evaluate_exit(
    position: Position,
    bar: QuoteBar,
    *,
    slippage_pips: float,
    commission_model: CommissionModel,
    financing_model: FinancingModel,
) -> ExitFill | None:
    if position.symbol != bar.symbol:
        raise ValueError("position symbol does not match quote bar")
    if bar.timestamp_utc < position.entry_timestamp_utc:
        raise ValueError("exit bar cannot precede position entry")

    if position.direction is Direction.LONG:
        executable_open = bar.bid_open
        executable_high = bar.bid_high
        executable_low = bar.bid_low
        stop_gap = executable_open <= position.stop_price
        stop_hit = executable_low <= position.stop_price
        target_hit = (
            position.target_price is not None
            and executable_high >= position.target_price
        )
    elif position.direction is Direction.SHORT:
        executable_open = bar.ask_open
        executable_high = bar.ask_high
        executable_low = bar.ask_low
        stop_gap = executable_open >= position.stop_price
        stop_hit = executable_high >= position.stop_price
        target_hit = (
            position.target_price is not None
            and executable_low <= position.target_price
        )
    else:
        raise ValueError("position direction must be LONG or SHORT")

    if stop_gap:
        return _make_exit_fill(
            position,
            bar,
            reference_price=executable_open,
            reason=ExitReason.STOP,
            intrabar_ambiguous=False,
            slippage_pips=slippage_pips,
            commission_model=commission_model,
            financing_model=financing_model,
        )

    if stop_hit and target_hit:
        return _make_exit_fill(
            position,
            bar,
            reference_price=position.stop_price,
            reason=ExitReason.STOP,
            intrabar_ambiguous=True,
            slippage_pips=slippage_pips,
            commission_model=commission_model,
            financing_model=financing_model,
        )

    if stop_hit:
        return _make_exit_fill(
            position,
            bar,
            reference_price=position.stop_price,
            reason=ExitReason.STOP,
            intrabar_ambiguous=False,
            slippage_pips=slippage_pips,
            commission_model=commission_model,
            financing_model=financing_model,
        )

    if target_hit:
        assert position.target_price is not None
        return _make_exit_fill(
            position,
            bar,
            reference_price=position.target_price,
            reason=ExitReason.TARGET,
            intrabar_ambiguous=False,
            slippage_pips=slippage_pips,
            commission_model=commission_model,
            financing_model=financing_model,
        )

    return None


def close_end_of_data(
    position: Position,
    bar: QuoteBar,
    *,
    slippage_pips: float,
    commission_model: CommissionModel,
    financing_model: FinancingModel,
) -> ExitFill:
    if position.symbol != bar.symbol:
        raise ValueError("position symbol does not match quote bar")
    reference = (
        bar.bid_close if position.direction is Direction.LONG else bar.ask_close
    )
    return _make_exit_fill(
        position,
        bar,
        reference_price=reference,
        reason=ExitReason.END_OF_DATA,
        intrabar_ambiguous=False,
        slippage_pips=slippage_pips,
        commission_model=commission_model,
        financing_model=financing_model,
    )
