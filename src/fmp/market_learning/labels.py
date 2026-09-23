from __future__ import annotations

from datetime import datetime, timedelta
from typing import Mapping, Sequence

from fmp.backtest.costs import apply_adverse_slippage, pip_size
from fmp.contracts import Direction, OrderSide, QuoteBar

from .contracts import (
    HORIZONS_MINUTES,
    SLIPPAGE_PIPS,
    MarketObservation,
    MarketOutcomeLabel,
    MarketOutcomeResult,
)


def _bar_map(
    bars: Sequence[QuoteBar],
    *,
    symbol: str,
) -> Mapping[datetime, QuoteBar]:
    selected = [bar for bar in bars if bar.symbol == symbol]
    timestamps = [bar.timestamp_utc for bar in selected]
    if len(set(timestamps)) != len(timestamps):
        raise ValueError("duplicate quote-bar identity in market-learning label input")
    if timestamps != sorted(timestamps):
        raise ValueError(
            "market-learning label bars must be sorted by timestamp_utc"
        )
    return {bar.timestamp_utc: bar for bar in selected}


def _unavailable(
    observation: MarketObservation,
    *,
    horizon_minutes: int,
    slippage_pips: float,
    reason_code: str,
) -> MarketOutcomeResult:
    return MarketOutcomeResult(
        observation_fingerprint=observation.fingerprint,
        horizon_minutes=horizon_minutes,
        slippage_pips=slippage_pips,
        reason_code=reason_code,
        label=None,
    )


def _label_from_map(
    observation: MarketObservation,
    by_timestamp: Mapping[datetime, QuoteBar],
    *,
    horizon_minutes: int,
    slippage_pips: float,
) -> MarketOutcomeResult:
    if horizon_minutes not in HORIZONS_MINUTES:
        raise ValueError("unsupported market-learning horizon")
    if slippage_pips not in SLIPPAGE_PIPS:
        raise ValueError("unsupported market-learning slippage")

    entry_timestamp = observation.available_at_utc
    exit_timestamp = entry_timestamp + timedelta(minutes=horizon_minutes)
    entry_bar = by_timestamp.get(entry_timestamp)
    if entry_bar is None:
        return _unavailable(
            observation,
            horizon_minutes=horizon_minutes,
            slippage_pips=slippage_pips,
            reason_code="MISSING_ENTRY_BAR",
        )
    exit_bar = by_timestamp.get(exit_timestamp)
    if exit_bar is None:
        return _unavailable(
            observation,
            horizon_minutes=horizon_minutes,
            slippage_pips=slippage_pips,
            reason_code="MISSING_EXACT_HORIZON_BAR",
        )

    pip = pip_size(observation.symbol)
    entry_mid = (entry_bar.bid_open + entry_bar.ask_open) / 2.0
    exit_mid = (exit_bar.bid_open + exit_bar.ask_open) / 2.0
    future_mid_move_pips = (exit_mid - entry_mid) / pip

    long_entry = apply_adverse_slippage(
        entry_bar.ask_open,
        side=OrderSide.BUY,
        pips=slippage_pips,
        symbol=observation.symbol,
    )
    long_exit = apply_adverse_slippage(
        exit_bar.bid_open,
        side=OrderSide.SELL,
        pips=slippage_pips,
        symbol=observation.symbol,
    )
    long_net_pips = (long_exit - long_entry) / pip

    short_entry = apply_adverse_slippage(
        entry_bar.bid_open,
        side=OrderSide.SELL,
        pips=slippage_pips,
        symbol=observation.symbol,
    )
    short_exit = apply_adverse_slippage(
        exit_bar.ask_open,
        side=OrderSide.BUY,
        pips=slippage_pips,
        symbol=observation.symbol,
    )
    short_net_pips = (short_entry - short_exit) / pip

    if long_net_pips > 0.0 and long_net_pips > short_net_pips:
        best_direction = Direction.LONG
    elif short_net_pips > 0.0 and short_net_pips > long_net_pips:
        best_direction = Direction.SHORT
    else:
        best_direction = Direction.NO_TRADE

    label = MarketOutcomeLabel(
        observation_fingerprint=observation.fingerprint,
        symbol=observation.symbol,
        timeframe=observation.timeframe,
        available_at_utc=observation.available_at_utc,
        horizon_minutes=horizon_minutes,
        slippage_pips=slippage_pips,
        entry_timestamp_utc=entry_timestamp,
        exit_timestamp_utc=exit_timestamp,
        future_mid_move_pips=future_mid_move_pips,
        long_net_pips=long_net_pips,
        short_net_pips=short_net_pips,
        best_direction=best_direction,
    )
    return MarketOutcomeResult(
        observation_fingerprint=observation.fingerprint,
        horizon_minutes=horizon_minutes,
        slippage_pips=slippage_pips,
        reason_code="LABELED",
        label=label,
    )


def label_market_outcome(
    observation: MarketObservation,
    bars: Sequence[QuoteBar],
    *,
    horizon_minutes: int,
    slippage_pips: float,
) -> MarketOutcomeResult:
    return _label_from_map(
        observation,
        _bar_map(bars, symbol=observation.symbol),
        horizon_minutes=horizon_minutes,
        slippage_pips=slippage_pips,
    )


def label_market_outcomes(
    observations: Sequence[MarketObservation],
    bars: Sequence[QuoteBar],
) -> tuple[MarketOutcomeResult, ...]:
    fingerprints = [observation.fingerprint for observation in observations]
    if len(set(fingerprints)) != len(fingerprints):
        raise ValueError("duplicate market-learning observation identity")

    maps = {
        symbol: _bar_map(bars, symbol=symbol)
        for symbol in sorted({observation.symbol for observation in observations})
    }
    results: list[MarketOutcomeResult] = []
    for observation in sorted(observations, key=lambda item: item.fingerprint):
        by_timestamp = maps[observation.symbol]
        for horizon_minutes in HORIZONS_MINUTES:
            for slippage_pips in SLIPPAGE_PIPS:
                results.append(
                    _label_from_map(
                        observation,
                        by_timestamp,
                        horizon_minutes=horizon_minutes,
                        slippage_pips=slippage_pips,
                    )
                )
    return tuple(results)


__all__ = ["label_market_outcome", "label_market_outcomes"]
