"""Direct market-learning research primitives for Phase 8A."""

from .contracts import (
    EVIDENCE_LABEL,
    EXPERIMENT_ID,
    HORIZONS_MINUTES,
    MARKET_FEATURE_SET_VERSION,
    PROTOCOL_VERSION,
    SLIPPAGE_PIPS,
    MarketObservation,
    MarketOutcomeLabel,
    MarketOutcomeResult,
)
from .labels import label_market_outcome, label_market_outcomes

__all__ = [
    "EVIDENCE_LABEL",
    "EXPERIMENT_ID",
    "HORIZONS_MINUTES",
    "MARKET_FEATURE_SET_VERSION",
    "PROTOCOL_VERSION",
    "SLIPPAGE_PIPS",
    "MarketObservation",
    "MarketOutcomeLabel",
    "MarketOutcomeResult",
    "label_market_outcome",
    "label_market_outcomes",
]
