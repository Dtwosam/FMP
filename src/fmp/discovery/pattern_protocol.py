from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from datetime import date
from typing import Mapping, Sequence

from fmp.features.schema import FEATURE_VALUE_COLUMNS


EXPERIMENT_ID = "EXP-20260927-061"
PATTERN_DISCOVERY_DECISION = "DEC-270"
PROTOCOL_VERSION = "fmp-discovery-first-pattern-protocol-v1"
EVIDENCE_LABEL = "RETROSPECTIVE_ALREADY_SEEN"

SYMBOLS = ("EURUSD", "GBPUSD", "USDJPY")
TIMEFRAMES = ("5m", "15m", "1h")
HORIZONS_MINUTES = (60, 240)

DISCOVERY_SLIPPAGE_PIPS = 0.5
STRESS_SLIPPAGE_PIPS = 1.0

CONTINUOUS_FEATURES = (
    "return_1h",
    "return_24h",
    "realized_vol_1h",
    "realized_vol_8h",
    "realized_vol_24h",
    "range_vs_prior_median_8h",
    "sma_distance_2h_pips",
    "sma_distance_8h_pips",
    "sma_slope_2h_pips",
    "sma_slope_8h_pips",
    "roc_4h",
    "roc_8h",
    "momentum_accel_4h",
    "body_to_range",
    "close_location",
    "prev_fx_day_high_dist_pips",
    "prev_fx_day_low_dist_pips",
    "prev_asia_high_dist_pips",
    "prev_asia_low_dist_pips",
    "spread_percentile_prior_24h",
)
QUANTILE_STATES = ("LOW", "MID", "HIGH")
SESSION_STATES = (
    "LONDON_NEW_YORK_OVERLAP",
    "LONDON",
    "NEW_YORK",
    "ASIA",
    "OFF_SESSION",
)
DIRECTIONS = ("LONG", "SHORT")

MAX_PATTERN_DEPTH = 2
MIN_QUANTILE_CALIBRATION_ROWS = 300
MIN_DISCOVERY_TOTAL_SUPPORT = 300
MIN_DISCOVERY_YEAR_SUPPORT = 75
MIN_DISCOVERY_AGGREGATE_MEAN_NET_PIPS = 0.25
REQUIRE_DISCOVERY_STRESS_MEAN_POSITIVE = True
CONFIRMATION_MIN_SUPPORT = 75
VALIDATION_MIN_TOTAL_SUPPORT = 200
VALIDATION_MIN_YEAR_SUPPORT = 40
VALIDATION_MIN_POSITIVE_YEARS = 3
NEAR_DUPLICATE_JACCARD = 0.90
MAX_FROZEN_PER_CELL_HORIZON = 3

SOURCE_ACCESS_AUTHORIZED = False
DISCOVERY_EXECUTION_AUTHORIZED = False
DISCOVERY_RESULT_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


@dataclass(frozen=True, slots=True)
class ResearchWindow:
    name: str
    start: date
    end_exclusive: date
    role: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("research window name must be non-empty")
        if self.start >= self.end_exclusive:
            raise ValueError("research window must be non-empty")
        if not self.role.strip():
            raise ValueError("research window role must be non-empty")


DISCOVERY_WINDOW = ResearchWindow(
    name="discovery",
    start=date(2015, 1, 1),
    end_exclusive=date(2018, 1, 1),
    role="pattern_search_and_cutpoint_calibration",
)
CONFIRMATION_WINDOW = ResearchWindow(
    name="confirmation",
    start=date(2018, 1, 1),
    end_exclusive=date(2019, 1, 1),
    role="frozen_pattern_confirmation_only",
)
VALIDATION_WINDOW = ResearchWindow(
    name="validation",
    start=date(2019, 1, 1),
    end_exclusive=date(2023, 1, 1),
    role="frozen_pattern_chronological_validation_only",
)
RESERVED_ROBUSTNESS_WINDOW = ResearchWindow(
    name="reserved_robustness",
    start=date(2023, 1, 1),
    end_exclusive=date(2026, 8, 21),
    role="closed_to_exp061_reserved_for_later_compiled_strategy_testing",
)
PROTOCOL_WINDOWS = (
    DISCOVERY_WINDOW,
    CONFIRMATION_WINDOW,
    VALIDATION_WINDOW,
    RESERVED_ROBUSTNESS_WINDOW,
)

DISCOVERY_CELLS = tuple(
    (symbol, timeframe, horizon)
    for symbol in SYMBOLS
    for timeframe in TIMEFRAMES
    for horizon in HORIZONS_MINUTES
)


def empirical_tertile_cutpoints(
    values: Sequence[float | int | None],
) -> tuple[float, float] | None:
    finite = sorted(
        float(value)
        for value in values
        if isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )
    if len(finite) < MIN_QUANTILE_CALIBRATION_ROWS:
        return None
    n = len(finite)
    lower_index = math.floor((n - 1) / 3)
    upper_index = math.floor((2 * (n - 1)) / 3)
    lower = finite[lower_index]
    upper = finite[upper_index]
    if not lower < upper:
        return None
    return lower, upper


def quantile_state(
    value: float | int | None,
    cutpoints: tuple[float, float] | None,
) -> str | None:
    if (
        cutpoints is None
        or not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(float(value))
    ):
        return None
    lower, upper = cutpoints
    numeric = float(value)
    if numeric <= lower:
        return "LOW"
    if numeric <= upper:
        return "MID"
    return "HIGH"


def session_state(row: Mapping[str, object]) -> str:
    names = (
        "is_london_new_york_overlap",
        "is_london_session",
        "is_new_york_session",
        "is_asia_session",
    )
    for name in names:
        value = row.get(name)
        if not isinstance(value, bool):
            raise ValueError(f"{name} must be boolean for discovery session state")

    if row["is_london_new_york_overlap"]:
        return "LONDON_NEW_YORK_OVERLAP"
    if row["is_london_session"]:
        return "LONDON"
    if row["is_new_york_session"]:
        return "NEW_YORK"
    if row["is_asia_session"]:
        return "ASIA"
    return "OFF_SESSION"


def atomic_state_count() -> int:
    return len(CONTINUOUS_FEATURES) * len(QUANTILE_STATES) + len(SESSION_STATES)


def maximum_admissible_pattern_count() -> int:
    group_sizes = [len(QUANTILE_STATES)] * len(CONTINUOUS_FEATURES)
    group_sizes.append(len(SESSION_STATES))
    total = sum(group_sizes)
    singles = total
    all_pairs = total * (total - 1) // 2
    same_dimension_pairs = sum(size * (size - 1) // 2 for size in group_sizes)
    return singles + all_pairs - same_dimension_pairs


MAX_ATOMIC_STATES = atomic_state_count()
MAX_ADMISSIBLE_PATTERNS_PER_CELL_HORIZON = maximum_admissible_pattern_count()
MAX_DIRECTIONAL_HYPOTHESES_PER_CELL_HORIZON = (
    MAX_ADMISSIBLE_PATTERNS_PER_CELL_HORIZON * len(DIRECTIONS)
)
MAX_DIRECTIONAL_HYPOTHESES_TOTAL = (
    MAX_DIRECTIONAL_HYPOTHESES_PER_CELL_HORIZON * len(DISCOVERY_CELLS)
)
MAX_FROZEN_PATTERN_HYPOTHESES = (
    MAX_FROZEN_PER_CELL_HORIZON * len(DISCOVERY_CELLS)
)


def pattern_fingerprint(
    *,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
    direction: str,
    predicates: Sequence[tuple[str, str]],
) -> str:
    if symbol not in SYMBOLS:
        raise ValueError("unsupported discovery symbol")
    if timeframe not in TIMEFRAMES:
        raise ValueError("unsupported discovery timeframe")
    if horizon_minutes not in HORIZONS_MINUTES:
        raise ValueError("unsupported discovery horizon")
    if direction not in DIRECTIONS:
        raise ValueError("unsupported discovery direction")
    normalized = tuple(sorted((str(name), str(state)) for name, state in predicates))
    if not normalized or len(normalized) > MAX_PATTERN_DEPTH:
        raise ValueError("pattern predicate depth is outside the frozen protocol")
    if len({name for name, _ in normalized}) != len(normalized):
        raise ValueError("pattern cannot contain two states from the same dimension")
    payload = {
        "experiment_id": EXPERIMENT_ID,
        "protocol_version": PROTOCOL_VERSION,
        "symbol": symbol,
        "timeframe": timeframe,
        "horizon_minutes": horizon_minutes,
        "direction": direction,
        "predicates": normalized,
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _window_payload(window: ResearchWindow) -> dict[str, str]:
    raw = asdict(window)
    return {
        "name": str(raw["name"]),
        "start": window.start.isoformat(),
        "end_exclusive": window.end_exclusive.isoformat(),
        "role": str(raw["role"]),
    }


def protocol_payload() -> dict[str, object]:
    return {
        "experiment_id": EXPERIMENT_ID,
        "decision": PATTERN_DISCOVERY_DECISION,
        "protocol_version": PROTOCOL_VERSION,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "symbols": list(SYMBOLS),
        "timeframes": list(TIMEFRAMES),
        "horizons_minutes": list(HORIZONS_MINUTES),
        "cells": [
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "horizon_minutes": horizon,
            }
            for symbol, timeframe, horizon in DISCOVERY_CELLS
        ],
        "windows": [_window_payload(window) for window in PROTOCOL_WINDOWS],
        "market_state": {
            "continuous_features": list(CONTINUOUS_FEATURES),
            "continuous_state_method": "discovery_window_empirical_tertiles",
            "quantile_states": list(QUANTILE_STATES),
            "quantile_index_formula": "floor(p*(n-1)); p in {1/3,2/3}",
            "minimum_quantile_calibration_rows": MIN_QUANTILE_CALIBRATION_ROWS,
            "tied_cutpoint_policy": "skip_dimension_for_that_symbol_timeframe",
            "session_states": list(SESSION_STATES),
            "session_precedence": [
                "LONDON_NEW_YORK_OVERLAP",
                "LONDON",
                "NEW_YORK",
                "ASIA",
                "OFF_SESSION",
            ],
        },
        "search": {
            "max_pattern_depth": MAX_PATTERN_DEPTH,
            "directions": list(DIRECTIONS),
            "max_atomic_states": MAX_ATOMIC_STATES,
            "max_admissible_patterns_per_cell_horizon": (
                MAX_ADMISSIBLE_PATTERNS_PER_CELL_HORIZON
            ),
            "max_directional_hypotheses_per_cell_horizon": (
                MAX_DIRECTIONAL_HYPOTHESES_PER_CELL_HORIZON
            ),
            "max_directional_hypotheses_total": (
                MAX_DIRECTIONAL_HYPOTHESES_TOTAL
            ),
            "search_volume_must_be_recorded": True,
            "no_result_driven_feature_addition": True,
            "no_third_predicate_without_new_experiment": True,
        },
        "discovery_gate": {
            "slippage_pips": DISCOVERY_SLIPPAGE_PIPS,
            "stress_slippage_pips": STRESS_SLIPPAGE_PIPS,
            "minimum_total_support": MIN_DISCOVERY_TOTAL_SUPPORT,
            "minimum_support_each_discovery_year": MIN_DISCOVERY_YEAR_SUPPORT,
            "minimum_aggregate_mean_net_pips": (
                MIN_DISCOVERY_AGGREGATE_MEAN_NET_PIPS
            ),
            "require_positive_mean_each_discovery_year": True,
            "require_positive_aggregate_mean_at_stress_slippage": (
                REQUIRE_DISCOVERY_STRESS_MEAN_POSITIVE
            ),
        },
        "deduplication": {
            "same_cell_horizon_direction_only": True,
            "discovery_event_jaccard_threshold": NEAR_DUPLICATE_JACCARD,
            "keep_higher_frozen_rank": True,
        },
        "confirmation_gate": {
            "minimum_support": CONFIRMATION_MIN_SUPPORT,
            "require_positive_mean_net_pips_at_0p5": True,
            "may_redefine_pattern": False,
        },
        "validation_gate": {
            "minimum_total_support": VALIDATION_MIN_TOTAL_SUPPORT,
            "minimum_support_each_year": VALIDATION_MIN_YEAR_SUPPORT,
            "minimum_positive_years": VALIDATION_MIN_POSITIVE_YEARS,
            "year_count": 4,
            "require_positive_aggregate_mean_net_pips_at_0p5": True,
            "may_redefine_pattern": False,
        },
        "freeze": {
            "maximum_per_cell_horizon": MAX_FROZEN_PER_CELL_HORIZON,
            "maximum_global": MAX_FROZEN_PATTERN_HYPOTHESES,
            "output_kind": "PATTERN_HYPOTHESIS_NOT_EXECUTABLE_STRATEGY",
            "entry_stop_target_compilation_deferred": True,
            "reserved_2023_2026_window_remains_closed": True,
        },
        "authorizations": {
            "source_access_authorized": SOURCE_ACCESS_AUTHORIZED,
            "discovery_execution_authorized": DISCOVERY_EXECUTION_AUTHORIZED,
            "discovery_result_authorized": DISCOVERY_RESULT_AUTHORIZED,
            "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
            "reserved_robustness_access_authorized": (
                RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED
            ),
            "promotion_authorized": PROMOTION_AUTHORIZED,
            "phase8b_authorized": PHASE8B_AUTHORIZED,
            "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
            "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
            "live_order_authorized": LIVE_ORDER_AUTHORIZED,
            "real_money_authorized": REAL_MONEY_AUTHORIZED,
            "trading_authorized": TRADING_AUTHORIZED,
        },
    }


def protocol_fingerprint() -> str:
    encoded = (
        json.dumps(
            protocol_payload(),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_protocol() -> None:
    if len(CONTINUOUS_FEATURES) != 20:
        raise ValueError("DEC-270 requires exactly 20 continuous discovery dimensions")
    if len(set(CONTINUOUS_FEATURES)) != len(CONTINUOUS_FEATURES):
        raise ValueError("DEC-270 continuous feature inventory contains duplicates")
    missing = set(CONTINUOUS_FEATURES).difference(FEATURE_VALUE_COLUMNS)
    if missing:
        raise ValueError(f"DEC-270 discovery feature is not leakage-safe Phase 5 data: {sorted(missing)!r}")
    if len(DISCOVERY_CELLS) != 18:
        raise ValueError("DEC-270 requires exactly 18 symbol/timeframe/horizon cells")
    if MAX_ATOMIC_STATES != 65:
        raise ValueError("DEC-270 atomic state count drift")
    if MAX_ADMISSIBLE_PATTERNS_PER_CELL_HORIZON != 2075:
        raise ValueError("DEC-270 admissible pattern count drift")
    if MAX_DIRECTIONAL_HYPOTHESES_TOTAL != 74700:
        raise ValueError("DEC-270 directional search-volume bound drift")
    if MAX_FROZEN_PATTERN_HYPOTHESES != 54:
        raise ValueError("DEC-270 frozen pattern cap drift")
    for left, right in zip(PROTOCOL_WINDOWS, PROTOCOL_WINDOWS[1:]):
        if left.end_exclusive != right.start:
            raise ValueError("DEC-270 chronology windows must be contiguous")
    if RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED:
        raise ValueError("DEC-270 reserved robustness window must remain closed")


validate_protocol()


__all__ = [
    "CANDIDATE_COMPILATION_AUTHORIZED",
    "CONFIRMATION_MIN_SUPPORT",
    "CONFIRMATION_WINDOW",
    "CONTINUOUS_FEATURES",
    "DIRECTIONS",
    "DISCOVERY_CELLS",
    "DISCOVERY_EXECUTION_AUTHORIZED",
    "DISCOVERY_RESULT_AUTHORIZED",
    "DISCOVERY_SLIPPAGE_PIPS",
    "DISCOVERY_WINDOW",
    "EVIDENCE_LABEL",
    "EXPERIMENT_ID",
    "HORIZONS_MINUTES",
    "LIVE_ORDER_AUTHORIZED",
    "MAX_ADMISSIBLE_PATTERNS_PER_CELL_HORIZON",
    "MAX_ATOMIC_STATES",
    "MAX_DIRECTIONAL_HYPOTHESES_PER_CELL_HORIZON",
    "MAX_DIRECTIONAL_HYPOTHESES_TOTAL",
    "MAX_FROZEN_PATTERN_HYPOTHESES",
    "MAX_FROZEN_PER_CELL_HORIZON",
    "MAX_PATTERN_DEPTH",
    "NEAR_DUPLICATE_JACCARD",
    "PATTERN_DISCOVERY_DECISION",
    "PHASE8B_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "PROTOCOL_VERSION",
    "PROTOCOL_WINDOWS",
    "QUANTILE_STATES",
    "REAL_MONEY_AUTHORIZED",
    "RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED",
    "RESERVED_ROBUSTNESS_WINDOW",
    "SESSION_STATES",
    "SOURCE_ACCESS_AUTHORIZED",
    "STRESS_SLIPPAGE_PIPS",
    "SYMBOLS",
    "TIMEFRAMES",
    "TRADING_AUTHORIZED",
    "VALIDATION_WINDOW",
    "atomic_state_count",
    "empirical_tertile_cutpoints",
    "maximum_admissible_pattern_count",
    "pattern_fingerprint",
    "protocol_fingerprint",
    "protocol_payload",
    "quantile_state",
    "session_state",
    "validate_protocol",
]
