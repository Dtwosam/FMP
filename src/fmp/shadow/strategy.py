from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from fmp.contracts import Decision, QuoteBar, ScheduledExit
from fmp.research.adapter import candidate_to_decision
from fmp.strategies.contracts import SignalCandidate
from fmp.strategies.session_breakout import (
    SessionBreakoutConfig,
    generate_session_breakout_candidates,
)

from .contracts import FMP_SYMBOL


FROZEN_SESSION_BREAKOUT_CONFIG = SessionBreakoutConfig(
    buffer_pips=5,
    target_range_multiple=1.5,
    timeframe="15m",
)
REQUESTED_RISK_FRACTION = 0.0025


@dataclass(frozen=True, slots=True)
class ShadowStrategyDecision:
    candidate: SignalCandidate
    decision: Decision
    scheduled_exit: ScheduledExit | None


def generate_shadow_strategy_decisions(
    bars: Sequence[QuoteBar],
) -> tuple[ShadowStrategyDecision, ...]:
    if not bars:
        return ()
    if any(bar.symbol != FMP_SYMBOL for bar in bars):
        raise ValueError(f"Phase 8 strategy supports only {FMP_SYMBOL}")

    candidates = generate_session_breakout_candidates(
        bars,
        config=FROZEN_SESSION_BREAKOUT_CONFIG,
        require_scheduled_exit_bar=False,
    )
    out: list[ShadowStrategyDecision] = []
    for candidate in candidates:
        decision, scheduled_exit = candidate_to_decision(
            candidate,
            next_bar_timestamp_utc=candidate.signal_known_timestamp_utc,
            requested_risk_fraction=REQUESTED_RISK_FRACTION,
        )
        out.append(
            ShadowStrategyDecision(
                candidate=candidate,
                decision=decision,
                scheduled_exit=scheduled_exit,
            )
        )
    return tuple(out)


__all__ = [
    "FROZEN_SESSION_BREAKOUT_CONFIG",
    "REQUESTED_RISK_FRACTION",
    "ShadowStrategyDecision",
    "generate_shadow_strategy_decisions",
]
