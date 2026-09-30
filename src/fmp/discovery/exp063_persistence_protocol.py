from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
import hashlib
import json
import math
from typing import Mapping, Sequence

from . import pattern_protocol as _base
from .exp063_research_direction import (
    POST_EXP062_RESEARCH_DIRECTION_DECISION,
    POST_EXP062_RESEARCH_DIRECTION_VERSION,
    SUCCESSOR_EXPERIMENT_ID,
)


EXP063_PERSISTENCE_PROTOCOL_DECISION = "DEC-444"
EXP063_PERSISTENCE_PROTOCOL_VERSION = (
    "fmp-exp063-persistence-first-pattern-protocol-v1"
)
EVIDENCE_LABEL = "RETROSPECTIVE_ALREADY_SEEN"

DEC443_MERGE_SHA = "2ff960cf51d614c8c446d5f7f4c85569312bfec8"
DEC443_DIRECTION_BLOB_SHA = "e32fe0da11e01e463a8c5110201b0b1ed223f85e"
BASE_PATTERN_PROTOCOL_BLOB_SHA = "63b3f0121d6a50eb9e8e62ab666d70eb91791621"

SYMBOLS = _base.SYMBOLS
TIMEFRAMES = _base.TIMEFRAMES
HORIZONS_MINUTES = _base.HORIZONS_MINUTES
CONTINUOUS_FEATURES = _base.CONTINUOUS_FEATURES
QUANTILE_STATES = _base.QUANTILE_STATES
SESSION_DIMENSION = _base.SESSION_DIMENSION
SESSION_STATES = _base.SESSION_STATES
DIRECTIONS = _base.DIRECTIONS
MAX_PATTERN_DEPTH = _base.MAX_PATTERN_DEPTH
MIN_QUANTILE_CALIBRATION_ROWS = _base.MIN_QUANTILE_CALIBRATION_ROWS
NEAR_DUPLICATE_JACCARD = _base.NEAR_DUPLICATE_JACCARD

MAX_ATOMIC_STATES = _base.MAX_ATOMIC_STATES
MAX_ADMISSIBLE_PATTERNS_PER_CELL_HORIZON = (
    _base.MAX_ADMISSIBLE_PATTERNS_PER_CELL_HORIZON
)
MAX_DIRECTIONAL_HYPOTHESES_PER_CELL_HORIZON = (
    _base.MAX_DIRECTIONAL_HYPOTHESES_PER_CELL_HORIZON
)
MAX_DIRECTIONAL_HYPOTHESES_TOTAL = _base.MAX_DIRECTIONAL_HYPOTHESES_TOTAL

CALIBRATION_WINDOW = _base.ResearchWindow(
    name="state_calibration",
    start=date(2015, 1, 1),
    end_exclusive=date(2018, 1, 1),
    role="fixed_empirical_tertile_calibration_only",
)

DESIGN_YEARS = tuple(range(2015, 2023))
DESIGN_YEAR_WINDOWS = tuple(
    _base.ResearchWindow(
        name=f"design_{year}",
        start=date(year, 1, 1),
        end_exclusive=date(year + 1, 1, 1),
        role="already_seen_annual_persistence_design_evidence",
    )
    for year in DESIGN_YEARS
)
PERSISTENCE_BLOCKS = (
    (2015, 2016),
    (2017, 2018),
    (2019, 2020),
    (2021, 2022),
)
RESERVED_ROBUSTNESS_WINDOW = _base.ResearchWindow(
    name="reserved_robustness",
    start=date(2023, 1, 1),
    end_exclusive=date(2026, 8, 21),
    role="closed_to_exp063_until_later_explicit_decision",
)

DESIGN_SLIPPAGE_PIPS = 0.5
STRESS_SLIPPAGE_PIPS = 1.0
MIN_TOTAL_SUPPORT = 600
MIN_YEAR_SUPPORT = 75
MIN_AGGREGATE_MEAN_NET_PIPS_0P5 = 0.25
MIN_POSITIVE_YEARS = 6
LOWER_HALF_YEAR_COUNT = 4
REQUIRE_POSITIVE_LOWER_HALF_MEAN = True
REQUIRE_POSITIVE_EACH_TWO_YEAR_BLOCK_MEAN = True
REQUIRE_POSITIVE_AGGREGATE_STRESS_MEAN = True

MAX_PERSISTENCE_SHORTLIST_PER_CELL_HORIZON = 10
MAX_FROZEN_PER_CELL_HORIZON = 3
MAX_PERSISTENCE_SHORTLIST_GLOBAL = (
    MAX_PERSISTENCE_SHORTLIST_PER_CELL_HORIZON
    * len(SYMBOLS)
    * len(TIMEFRAMES)
    * len(HORIZONS_MINUTES)
)
MAX_FROZEN_PATTERN_HYPOTHESES = (
    MAX_FROZEN_PER_CELL_HORIZON
    * len(SYMBOLS)
    * len(TIMEFRAMES)
    * len(HORIZONS_MINUTES)
)

PERSISTENCE_RANK_FIELDS = (
    "lower_half_annual_mean_net_pips_0p5_desc",
    "minimum_two_year_block_mean_net_pips_0p5_desc",
    "positive_year_count_desc",
    "worst_annual_mean_net_pips_0p5_desc",
    "aggregate_mean_net_pips_0p5_desc",
    "aggregate_mean_net_pips_1p0_desc",
    "total_support_desc",
    "pattern_depth_asc",
    "pattern_fingerprint_asc",
)

SOURCE_ACCESS_AUTHORIZED = False
EXECUTION_AUTHORIZED = False
HISTORICAL_RESULT_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


@dataclass(frozen=True, slots=True)
class AnnualPersistenceStat:
    year: int
    support: int
    total_net_pips_0p5: float
    total_net_pips_1p0: float

    def __post_init__(self) -> None:
        if self.year not in DESIGN_YEARS:
            raise ValueError("annual persistence year is outside 2015-2022")
        if isinstance(self.support, bool) or self.support < 0:
            raise ValueError("annual persistence support must be non-negative")
        for field in ("total_net_pips_0p5", "total_net_pips_1p0"):
            value = float(getattr(self, field))
            if not math.isfinite(value):
                raise ValueError(f"{field} must be finite")

    @property
    def mean_net_pips_0p5(self) -> float:
        if self.support <= 0:
            return float("-inf")
        return self.total_net_pips_0p5 / self.support

    @property
    def mean_net_pips_1p0(self) -> float:
        if self.support <= 0:
            return float("-inf")
        return self.total_net_pips_1p0 / self.support


def _ordered_annual_stats(
    stats: Sequence[AnnualPersistenceStat],
) -> tuple[AnnualPersistenceStat, ...]:
    ordered = tuple(sorted(stats, key=lambda item: item.year))
    if tuple(item.year for item in ordered) != DESIGN_YEARS:
        raise ValueError("DEC-444 requires exactly one annual stat for 2015-2022")
    return ordered


def persistence_metrics(
    stats: Sequence[AnnualPersistenceStat],
) -> dict[str, object]:
    ordered = _ordered_annual_stats(stats)
    total_support = sum(item.support for item in ordered)
    if total_support <= 0:
        raise ValueError("DEC-444 total support must be positive")

    annual_means_0p5 = tuple(item.mean_net_pips_0p5 for item in ordered)
    if any(not math.isfinite(value) for value in annual_means_0p5):
        raise ValueError("DEC-444 annual mean requires positive support every year")

    aggregate_mean_0p5 = (
        sum(item.total_net_pips_0p5 for item in ordered) / total_support
    )
    aggregate_mean_1p0 = (
        sum(item.total_net_pips_1p0 for item in ordered) / total_support
    )
    weakest = sorted(annual_means_0p5)[:LOWER_HALF_YEAR_COUNT]
    lower_half_mean = sum(weakest) / LOWER_HALF_YEAR_COUNT

    block_means: dict[str, float] = {}
    for first, second in PERSISTENCE_BLOCKS:
        left = annual_means_0p5[DESIGN_YEARS.index(first)]
        right = annual_means_0p5[DESIGN_YEARS.index(second)]
        block_means[f"{first}_{second}"] = (left + right) / 2.0

    return {
        "total_support": total_support,
        "minimum_year_support": min(item.support for item in ordered),
        "aggregate_mean_net_pips_0p5": aggregate_mean_0p5,
        "aggregate_mean_net_pips_1p0": aggregate_mean_1p0,
        "positive_year_count": sum(value > 0 for value in annual_means_0p5),
        "worst_annual_mean_net_pips_0p5": min(annual_means_0p5),
        "lower_half_annual_mean_net_pips_0p5": lower_half_mean,
        "two_year_block_mean_net_pips_0p5": block_means,
        "minimum_two_year_block_mean_net_pips_0p5": min(block_means.values()),
    }


def persistence_gate_passes(
    stats: Sequence[AnnualPersistenceStat],
) -> bool:
    metrics = persistence_metrics(stats)
    return bool(
        metrics["total_support"] >= MIN_TOTAL_SUPPORT
        and metrics["minimum_year_support"] >= MIN_YEAR_SUPPORT
        and metrics["aggregate_mean_net_pips_0p5"]
        >= MIN_AGGREGATE_MEAN_NET_PIPS_0P5
        and metrics["aggregate_mean_net_pips_1p0"] > 0
        and metrics["positive_year_count"] >= MIN_POSITIVE_YEARS
        and metrics["lower_half_annual_mean_net_pips_0p5"] > 0
        and metrics["minimum_two_year_block_mean_net_pips_0p5"] > 0
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
        raise ValueError("unsupported EXP-063 symbol")
    if timeframe not in TIMEFRAMES:
        raise ValueError("unsupported EXP-063 timeframe")
    if horizon_minutes not in HORIZONS_MINUTES:
        raise ValueError("unsupported EXP-063 horizon")
    if direction not in DIRECTIONS:
        raise ValueError("unsupported EXP-063 direction")

    normalized = tuple(sorted((str(name), str(state)) for name, state in predicates))
    if not normalized or len(normalized) > MAX_PATTERN_DEPTH:
        raise ValueError("EXP-063 pattern depth is outside the frozen protocol")
    if len({name for name, _ in normalized}) != len(normalized):
        raise ValueError("EXP-063 pattern cannot repeat a dimension")

    for name, state in normalized:
        if name in CONTINUOUS_FEATURES:
            if state not in QUANTILE_STATES:
                raise ValueError("EXP-063 continuous dimension has invalid state")
        elif name == SESSION_DIMENSION:
            if state not in SESSION_STATES:
                raise ValueError("EXP-063 session dimension has invalid state")
        else:
            raise ValueError(f"unsupported EXP-063 pattern dimension: {name!r}")

    payload = {
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "protocol_version": EXP063_PERSISTENCE_PROTOCOL_VERSION,
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


def _window_payload(window: _base.ResearchWindow) -> dict[str, str]:
    raw = asdict(window)
    return {
        "name": str(raw["name"]),
        "start": window.start.isoformat(),
        "end_exclusive": window.end_exclusive.isoformat(),
        "role": str(raw["role"]),
    }


def protocol_payload() -> dict[str, object]:
    return {
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "decision": EXP063_PERSISTENCE_PROTOCOL_DECISION,
        "protocol_version": EXP063_PERSISTENCE_PROTOCOL_VERSION,
        "source_direction_decision": POST_EXP062_RESEARCH_DIRECTION_DECISION,
        "source_direction_version": POST_EXP062_RESEARCH_DIRECTION_VERSION,
        "dec443_merge_sha": DEC443_MERGE_SHA,
        "dec443_direction_blob_sha": DEC443_DIRECTION_BLOB_SHA,
        "base_pattern_protocol_blob_sha": BASE_PATTERN_PROTOCOL_BLOB_SHA,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "symbols": list(SYMBOLS),
        "timeframes": list(TIMEFRAMES),
        "horizons_minutes": list(HORIZONS_MINUTES),
        "calibration_window": _window_payload(CALIBRATION_WINDOW),
        "annual_design_windows": [
            _window_payload(window) for window in DESIGN_YEAR_WINDOWS
        ],
        "persistence_blocks": [list(block) for block in PERSISTENCE_BLOCKS],
        "reserved_robustness_window": _window_payload(
            RESERVED_ROBUSTNESS_WINDOW
        ),
        "chronology": {
            "2015_2022_label": "ALREADY_SEEN_DESIGN_EVIDENCE",
            "2019_2022_may_not_be_called_fresh_validation": True,
            "reserved_2023_2026_remains_closed": True,
            "outcomes_crossing_year_or_reserved_boundary_are_purged": True,
        },
        "market_state": {
            "continuous_features": list(CONTINUOUS_FEATURES),
            "continuous_state_method": (
                "fixed_2015_2017_empirical_tertiles_applied_through_2022"
            ),
            "quantile_states": list(QUANTILE_STATES),
            "minimum_quantile_calibration_rows": MIN_QUANTILE_CALIBRATION_ROWS,
            "tied_cutpoint_policy": "skip_dimension_for_that_symbol_timeframe",
            "session_states": list(SESSION_STATES),
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
            "no_new_feature_or_third_predicate": True,
        },
        "persistence_gate": {
            "design_slippage_pips": DESIGN_SLIPPAGE_PIPS,
            "stress_slippage_pips": STRESS_SLIPPAGE_PIPS,
            "minimum_total_support": MIN_TOTAL_SUPPORT,
            "minimum_support_each_year": MIN_YEAR_SUPPORT,
            "minimum_aggregate_mean_net_pips_0p5": (
                MIN_AGGREGATE_MEAN_NET_PIPS_0P5
            ),
            "minimum_positive_years": MIN_POSITIVE_YEARS,
            "year_count": len(DESIGN_YEARS),
            "lower_half_year_count": LOWER_HALF_YEAR_COUNT,
            "require_positive_lower_half_annual_mean": (
                REQUIRE_POSITIVE_LOWER_HALF_MEAN
            ),
            "require_positive_each_two_year_block_mean": (
                REQUIRE_POSITIVE_EACH_TWO_YEAR_BLOCK_MEAN
            ),
            "require_positive_aggregate_stress_mean": (
                REQUIRE_POSITIVE_AGGREGATE_STRESS_MEAN
            ),
            "annual_years_equal_status_in_persistence_metrics": True,
        },
        "ranking": {
            "fields": list(PERSISTENCE_RANK_FIELDS),
            "maximum_shortlist_per_cell_horizon": (
                MAX_PERSISTENCE_SHORTLIST_PER_CELL_HORIZON
            ),
            "maximum_shortlist_global": MAX_PERSISTENCE_SHORTLIST_GLOBAL,
        },
        "deduplication": {
            "same_cell_horizon_direction_only": True,
            "event_jaccard_threshold": NEAR_DUPLICATE_JACCARD,
            "keep_higher_frozen_rank": True,
        },
        "freeze": {
            "maximum_per_cell_horizon": MAX_FROZEN_PER_CELL_HORIZON,
            "maximum_global": MAX_FROZEN_PATTERN_HYPOTHESES,
            "output_kind": (
                "RETROSPECTIVE_PERSISTENCE_PATTERN_HYPOTHESIS_NOT_VALIDATED"
            ),
            "candidate_compilation_deferred": True,
            "reserved_2023_2026_window_remains_closed": True,
        },
        "authorizations": {
            "source_access_authorized": SOURCE_ACCESS_AUTHORIZED,
            "execution_authorized": EXECUTION_AUTHORIZED,
            "historical_result_authorized": HISTORICAL_RESULT_AUTHORIZED,
            "reserved_robustness_access_authorized": (
                RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED
            ),
            "candidate_compilation_authorized": (
                CANDIDATE_COMPILATION_AUTHORIZED
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
    if SUCCESSOR_EXPERIMENT_ID != "EXP-20260930-063":
        raise ValueError("DEC-444 successor experiment identity drift")
    if len(DESIGN_YEAR_WINDOWS) != 8:
        raise ValueError("DEC-444 requires eight annual design windows")
    if MAX_DIRECTIONAL_HYPOTHESES_TOTAL != 74700:
        raise ValueError("DEC-444 search-volume bound drift")
    if MAX_PERSISTENCE_SHORTLIST_GLOBAL != 180:
        raise ValueError("DEC-444 shortlist bound drift")
    if MAX_FROZEN_PATTERN_HYPOTHESES != 54:
        raise ValueError("DEC-444 frozen hypothesis bound drift")
    if MIN_YEAR_SUPPORT < _base.MIN_DISCOVERY_YEAR_SUPPORT:
        raise ValueError("DEC-444 may not loosen the prior discovery year support")
    if MIN_AGGREGATE_MEAN_NET_PIPS_0P5 < _base.MIN_DISCOVERY_AGGREGATE_MEAN_NET_PIPS:
        raise ValueError("DEC-444 may not loosen the prior discovery mean gate")
    if RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED:
        raise ValueError("DEC-444 reserved robustness window must remain closed")
    for value in protocol_payload()["authorizations"].values():
        if value is not False:
            raise ValueError("DEC-444 execution/trading authorization drift")


validate_protocol()


__all__ = [
    "AnnualPersistenceStat",
    "DESIGN_YEAR_WINDOWS",
    "EXP063_PERSISTENCE_PROTOCOL_DECISION",
    "EXP063_PERSISTENCE_PROTOCOL_VERSION",
    "MAX_DIRECTIONAL_HYPOTHESES_TOTAL",
    "MAX_FROZEN_PATTERN_HYPOTHESES",
    "MAX_PERSISTENCE_SHORTLIST_GLOBAL",
    "PERSISTENCE_BLOCKS",
    "PERSISTENCE_RANK_FIELDS",
    "RESERVED_ROBUSTNESS_WINDOW",
    "pattern_fingerprint",
    "persistence_gate_passes",
    "persistence_metrics",
    "protocol_fingerprint",
    "protocol_payload",
]
