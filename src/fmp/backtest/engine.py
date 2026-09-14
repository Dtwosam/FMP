from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Mapping, Sequence

from fmp.backtest import BACKTEST_ENGINE_VERSION
from fmp.backtest.costs import CommissionModel, FinancingModel
from fmp.backtest.execution import (
    ExitFill,
    close_end_of_data,
    entry_reference_price,
    evaluate_exit,
    fill_entry,
)
from fmp.contracts import (
    BacktestRun,
    Decision,
    Direction,
    EquityCheckpoint,
    OrderIntent,
    Position,
    QuoteBar,
    RejectionCode,
    RejectionRecord,
    TradeRecord,
    validate_decisions,
    validate_quote_bars,
)
from fmp.reporting.backtest import compute_backtest_metrics
from fmp.risk import (
    RiskConfig,
    RiskState,
    assess_decision,
    pnl_usd,
    record_realized_pnl,
    release_risk,
    reserve_risk,
    roll_utc_day,
)


def _require_utc(value: datetime, *, field: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must use UTC")


@dataclass(frozen=True, slots=True)
class BacktestConfig:
    starting_equity_usd: float
    slippage_pips: float
    risk_config: RiskConfig
    commission_model: CommissionModel
    financing_model: FinancingModel
    processed_data_manifest_id: str
    schema_version: str
    timeframe: str
    requested_start_utc: datetime
    requested_end_utc: datetime
    code_commit: str
    decision_config: Mapping[str, object]

    def __post_init__(self) -> None:
        if not math.isfinite(self.starting_equity_usd) or self.starting_equity_usd <= 0:
            raise ValueError("starting equity must be finite and positive")
        if not math.isfinite(self.slippage_pips) or self.slippage_pips < 0:
            raise ValueError("slippage pips must be finite and non-negative")
        _require_utc(self.requested_start_utc, field="requested_start_utc")
        _require_utc(self.requested_end_utc, field="requested_end_utc")
        if self.requested_end_utc < self.requested_start_utc:
            raise ValueError("requested end must not precede requested start")
        for field, value in (
            ("processed_data_manifest_id", self.processed_data_manifest_id),
            ("schema_version", self.schema_version),
            ("timeframe", self.timeframe),
            ("code_commit", self.code_commit),
        ):
            if not value.strip():
                raise ValueError(f"{field} must be non-empty")


def _rejection(
    decision: Decision,
    *,
    evaluated_timestamp_utc: datetime,
    code: RejectionCode,
    explanation: str,
) -> RejectionRecord:
    return RejectionRecord(
        decision_id=decision.decision_id,
        symbol=decision.symbol,
        decision_timestamp_utc=decision.decision_timestamp_utc,
        evaluated_timestamp_utc=evaluated_timestamp_utc,
        code=code,
        explanation=explanation,
    )


def _run_identity(config: BacktestConfig) -> dict[str, object]:
    return {
        "backtest_engine_version": BACKTEST_ENGINE_VERSION,
        "code_commit": config.code_commit,
        "processed_data_manifest_id": config.processed_data_manifest_id,
        "schema_version": config.schema_version,
        "timeframe": config.timeframe,
        "requested_start_utc": config.requested_start_utc,
        "requested_end_utc": config.requested_end_utc,
        "starting_equity_usd": config.starting_equity_usd,
        "slippage_pips": config.slippage_pips,
        "risk_config": config.risk_config.to_config(),
        "commission_model": dict(config.commission_model.to_config()),
        "financing_model": dict(config.financing_model.to_config()),
        "decision_config": dict(config.decision_config),
    }


def run_backtest(
    *,
    bars: Sequence[QuoteBar],
    decisions: Sequence[Decision],
    config: BacktestConfig,
) -> BacktestRun:
    validate_quote_bars(bars)
    validate_decisions(decisions)
    if not bars:
        raise ValueError("backtest requires at least one quote bar")

    bars_by_timestamp: dict[datetime, dict[str, QuoteBar]] = defaultdict(dict)
    bars_by_symbol: dict[str, list[QuoteBar]] = defaultdict(list)
    for bar in bars:
        bars_by_timestamp[bar.timestamp_utc][bar.symbol] = bar
        bars_by_symbol[bar.symbol].append(bar)

    last_timestamp_by_symbol = {
        symbol: symbol_bars[-1].timestamp_utc
        for symbol, symbol_bars in bars_by_symbol.items()
    }

    scheduled: dict[datetime, list[Decision]] = defaultdict(list)
    rejections: list[RejectionRecord] = []
    for decision in decisions:
        if decision.direction is Direction.NO_TRADE:
            explanation = decision.reason_text or decision.reason_code or "NO_TRADE"
            rejections.append(
                _rejection(
                    decision,
                    evaluated_timestamp_utc=decision.decision_timestamp_utc,
                    code=RejectionCode.NO_TRADE,
                    explanation=explanation,
                )
            )
            continue

        next_bar = next(
            (
                bar
                for bar in bars_by_symbol.get(decision.symbol, ())
                if bar.timestamp_utc > decision.decision_timestamp_utc
            ),
            None,
        )
        declared = decision.earliest_executable_timestamp_utc
        if next_bar is None or declared != next_bar.timestamp_utc:
            evaluated = (
                next_bar.timestamp_utc
                if next_bar is not None
                else decision.decision_timestamp_utc
            )
            rejections.append(
                _rejection(
                    decision,
                    evaluated_timestamp_utc=evaluated,
                    code=RejectionCode.TIMING_CONTRACT,
                    explanation=(
                        "earliest executable timestamp must equal the first supplied "
                        "bar for the symbol strictly after the decision timestamp"
                    ),
                )
            )
            continue
        scheduled[next_bar.timestamp_utc].append(decision)

    for bucket in scheduled.values():
        bucket.sort(key=lambda item: item.decision_id)

    state = RiskState(starting_equity_usd=config.starting_equity_usd)
    equity_checkpoints: list[EquityCheckpoint] = [
        EquityCheckpoint(
            timestamp_utc=bars[0].timestamp_utc,
            realized_risk_equity_usd=config.starting_equity_usd,
        )
    ]
    open_positions: dict[str, Position] = {}
    trades: list[TradeRecord] = []

    def finalize_position(position: Position, exit_fill: ExitFill) -> None:
        risk_equity_before = state.risk_equity_usd
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

        release_risk(state, position_id=position.position_id)
        record_realized_pnl(
            state,
            timestamp_utc=exit_fill.timestamp_utc,
            pnl_usd=net_pnl,
            config=config.risk_config,
        )
        risk_equity_after = state.risk_equity_usd

        trades.append(
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
        equity_checkpoints.append(
            EquityCheckpoint(
                timestamp_utc=exit_fill.timestamp_utc,
                realized_risk_equity_usd=risk_equity_after,
            )
        )
        open_positions.pop(position.position_id, None)

    for timestamp in sorted(bars_by_timestamp):
        roll_utc_day(state, timestamp_utc=timestamp)
        timestamp_bars = bars_by_timestamp[timestamp]

        # Existing positions exit before any new entries at the same timestamp.
        for position_id in sorted(tuple(open_positions)):
            position = open_positions.get(position_id)
            if position is None:
                continue
            bar = timestamp_bars.get(position.symbol)
            if bar is None:
                continue
            exit_fill = evaluate_exit(
                position,
                bar,
                slippage_pips=config.slippage_pips,
                commission_model=config.commission_model,
                financing_model=config.financing_model,
            )
            if exit_fill is not None:
                finalize_position(position, exit_fill)

        # Decisions are globally ordered by stable decision_id across symbols.
        for decision in scheduled.get(timestamp, ()):
            bar = timestamp_bars.get(decision.symbol)
            if bar is None:
                rejections.append(
                    _rejection(
                        decision,
                        evaluated_timestamp_utc=timestamp,
                        code=RejectionCode.INVALID_QUOTE,
                        explanation="no executable quote bar exists for decision symbol",
                    )
                )
                continue

            reference_entry = entry_reference_price(bar, decision.direction)
            assessment = assess_decision(
                decision=decision,
                reference_entry_price=reference_entry,
                timestamp_utc=timestamp,
                config=config.risk_config,
                state=state,
            )
            if not assessment.approved:
                assert assessment.rejection_code is not None
                rejections.append(
                    _rejection(
                        decision,
                        evaluated_timestamp_utc=timestamp,
                        code=assessment.rejection_code,
                        explanation=assessment.explanation,
                    )
                )
                continue

            assert decision.stop_price is not None
            assert decision.earliest_executable_timestamp_utc is not None
            intent = OrderIntent(
                decision_id=decision.decision_id,
                symbol=decision.symbol,
                direction=decision.direction,
                units=assessment.approved_units,
                reserved_risk_usd=assessment.approved_risk_usd,
                stop_price=decision.stop_price,
                target_price=decision.target_price,
                decision_timestamp_utc=decision.decision_timestamp_utc,
                earliest_executable_timestamp_utc=(
                    decision.earliest_executable_timestamp_utc
                ),
            )
            position = fill_entry(
                intent,
                bar,
                slippage_pips=config.slippage_pips,
                commission_model=config.commission_model,
            )
            reserve_risk(
                state,
                position_id=position.position_id,
                amount_usd=position.reserved_risk_usd,
            )
            open_positions[position.position_id] = position

            # Entry occurs at the open. The same bar's later high/low may close it.
            exit_fill = evaluate_exit(
                position,
                bar,
                slippage_pips=config.slippage_pips,
                commission_model=config.commission_model,
                financing_model=config.financing_model,
            )
            if exit_fill is not None:
                finalize_position(position, exit_fill)

        # Close positions on each symbol's own final supplied bar. Doing this here
        # preserves chronological daily-risk accounting even if symbols end at
        # different timestamps.
        for position_id in sorted(tuple(open_positions)):
            position = open_positions.get(position_id)
            if position is None:
                continue
            bar = timestamp_bars.get(position.symbol)
            if bar is None:
                continue
            if timestamp != last_timestamp_by_symbol[position.symbol]:
                continue
            finalize_position(
                position,
                close_end_of_data(
                    position,
                    bar,
                    slippage_pips=config.slippage_pips,
                    commission_model=config.commission_model,
                    financing_model=config.financing_model,
                ),
            )

    trades.sort(key=lambda item: (item.exit_timestamp_utc, item.trade_id))
    rejections.sort(key=lambda item: (item.evaluated_timestamp_utc, item.decision_id))
    metrics = compute_backtest_metrics(
        starting_equity_usd=config.starting_equity_usd,
        trades=trades,
        equity_checkpoints=equity_checkpoints,
    )
    return BacktestRun(
        run_identity=_run_identity(config),
        trades=tuple(trades),
        rejections=tuple(rejections),
        equity_checkpoints=tuple(equity_checkpoints),
        metrics=metrics,
    )
