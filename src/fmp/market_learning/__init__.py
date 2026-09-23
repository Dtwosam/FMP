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
from .evidence import load_feature_evidence_index
from .features import (
    LoadedMarketFeatureSource,
    build_market_feature_frame,
    load_market_feature_source,
    run_market_feature_generation,
    validate_market_feature_range,
    write_market_feature_artifacts,
)
from .labels import label_market_outcome, label_market_outcomes
from .materialize import (
    LoadedFeatureCell,
    load_verified_feature_cell,
    load_verified_minute_quotes,
    materialize_market_outcome_cell,
    run_market_outcome_materialization,
)
from .outcome_evidence import (
    compile_outcome_evidence,
    load_outcome_evidence_index,
    write_outcome_evidence,
)
from .readiness import (
    READINESS_VERSION,
    build_training_readiness,
    compile_training_readiness,
    write_training_readiness,
)
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
    "LoadedFeatureCell",
    "LoadedMarketFeatureSource",
    "MarketObservation",
    "MarketOutcomeLabel",
    "MarketOutcomeResult",
    "MarketOutcomeGridBuild",
    "MARKET_OUTCOME_SET_VERSION",
    "OUTCOME_COLUMNS",
    "READINESS_VERSION",
    "build_market_feature_frame",
    "build_market_outcome_grid",
    "build_training_readiness",
    "compile_outcome_evidence",
    "compile_training_readiness",
    "label_market_outcome",
    "load_feature_evidence_index",
    "load_market_feature_source",
    "load_outcome_evidence_index",
    "load_verified_feature_cell",
    "load_verified_minute_quotes",
    "materialize_market_outcome_cell",
    "run_market_feature_generation",
    "run_market_outcome_materialization",
    "validate_market_feature_range",
    "write_market_feature_artifacts",
    "write_market_outcome_artifacts",
    "write_outcome_evidence",
    "write_training_readiness",
    "label_market_outcomes",
]
