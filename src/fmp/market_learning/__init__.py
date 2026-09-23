"""Direct market-learning research primitives for Phase 8A."""

from .contracts import (
    BASE_FEATURE_DEFINITION_VERSION,
    EVIDENCE_LABEL,
    EXPERIMENT_ID,
    HORIZONS_MINUTES,
    MARKET_FEATURE_SET_VERSION,
    MARKET_HISTORY_END_EXCLUSIVE,
    MARKET_HISTORY_START,
    PROTOCOL_VERSION,
    SLIPPAGE_PIPS,
    MarketObservation,
    MarketOutcomeLabel,
    MarketOutcomeResult,
)
from .features import (
    LoadedMarketFeatureSource,
    build_market_feature_frame,
    load_market_feature_source,
    run_market_feature_generation,
    validate_market_feature_range,
    write_market_feature_artifacts,
)
from .labels import label_market_outcome, label_market_outcomes
from .outcomes import (
    MARKET_OUTCOME_SET_VERSION,
    OUTCOME_COLUMNS,
    MarketOutcomeGridBuild,
    build_market_outcome_grid,
    write_market_outcome_artifacts,
)

__all__ = [
    "BASE_FEATURE_DEFINITION_VERSION",
    "EVIDENCE_LABEL",
    "EXPERIMENT_ID",
    "HORIZONS_MINUTES",
    "MARKET_FEATURE_SET_VERSION",
    "MARKET_HISTORY_END_EXCLUSIVE",
    "MARKET_HISTORY_START",
    "PROTOCOL_VERSION",
    "SLIPPAGE_PIPS",
    "LoadedMarketFeatureSource",
    "MarketObservation",
    "MarketOutcomeLabel",
    "MarketOutcomeResult",
    "MarketOutcomeGridBuild",
    "MARKET_OUTCOME_SET_VERSION",
    "OUTCOME_COLUMNS",
    "build_market_feature_frame",
    "build_market_outcome_grid",
    "label_market_outcome",
    "load_market_feature_source",
    "run_market_feature_generation",
    "validate_market_feature_range",
    "write_market_feature_artifacts",
    "write_market_outcome_artifacts",
    "label_market_outcomes",
]
