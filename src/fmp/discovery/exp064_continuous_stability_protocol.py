from __future__ import annotations

import bisect
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Sequence

from .exp064_research_direction import SUCCESSOR_EXPERIMENT_ID
from .pattern_protocol import (
    CONTINUOUS_FEATURES,
    DIRECTIONS,
    HORIZONS_MINUTES,
    SYMBOLS,
    TIMEFRAMES,
)


EXP064_CONTINUOUS_STABILITY_PROTOCOL_DECISION = "DEC-452"
EXP064_CONTINUOUS_STABILITY_PROTOCOL_VERSION = (
    "fmp-exp064-continuous-stability-protocol-v1"
)

DEC451_MERGE_SHA = "e55df61f766ae49c72f04ac6259928252ae113dc"
DEC451_DIRECTION_BLOB_SHA = "6a7de1e93515fd3771e3763641ee6a07e425ee8a"

EVIDENCE_LABEL = "RETROSPECTIVE_ALREADY_SEEN"
OUTPUT_KIND = "RETROSPECTIVE_CONTINUOUS_STABILITY_HYPOTHESIS_NOT_VALIDATED"

DESIGN_YEARS = tuple(range(2015, 2023))
DESIGN_START = "2015-01-01"
DESIGN_END_EXCLUSIVE = "2023-01-01"
RESERVED_ROBUSTNESS_START = "2023-01-01"
RESERVED_ROBUSTNESS_END_EXCLUSIVE = "2026-08-21"

RANK_METHOD = "full_design_empirical_midrank_cdf"
RANK_CALIBRATION_START = DESIGN_START
RANK_CALIBRATION_END_EXCLUSIVE = DESIGN_END_EXCLUSIVE
MIN_RANK_CALIBRATION_ROWS = 600
MIN_RANK_CALIBRATION_DISTINCT_VALUES = 20

POLARITIES = ("INCREASING", "DECREASING")
LOWER_TAIL_MAX_PERCENTILE = 0.25
UPPER_TAIL_MIN_PERCENTILE = 0.75
MAX_FEATURES_PER_HYPOTHESIS = 1
INTERACTIONS_AUTHORIZED = False

DESIGN_SLIPPAGE_PIPS = 0.5
STRESS_SLIPPAGE_PIPS = 1.0

MIN_TOTAL_SELECTED_TAIL_SUPPORT = 600
MIN_YEAR_SELECTED_TAIL_SUPPORT = 75
MIN_POSITIVE_SLOPE_YEARS = 6
MIN_POSITIVE_TAIL_MEAN_YEARS = 6
MIN_EQUAL_YEAR_SIGNED_RANK_SLOPE_0P5 = 0.25
MIN_EQUAL_YEAR_SELECTED_TAIL_MEAN_0P5 = 0.25
REQUIRE_LOWER_HALF_SIGNED_RANK_SLOPE_POSITIVE = True
REQUIRE_LOWER_HALF_SELECTED_TAIL_MEAN_POSITIVE = True
REQUIRE_EACH_TWO_YEAR_BLOCK_SIGNED_RANK_SLOPE_POSITIVE = True
REQUIRE_EACH_TWO_YEAR_BLOCK_SELECTED_TAIL_MEAN_POSITIVE = True
REQUIRE_EQUAL_YEAR_SELECTED_TAIL_STRESS_MEAN_POSITIVE = True

TWO_YEAR_BLOCKS = (
    ("2015_2016", (2015, 2016)),
    ("2017_2018", (2017, 2018)),
    ("2019_2020", (2019, 2020)),
    ("2021_2022", (2021, 2022)),
)
LOWER_HALF_YEAR_COUNT = 4

NEAR_DUPLICATE_JACCARD = 0.95
MAX_SHORTLIST_PER_CELL_HORIZON = 5
MAX_FROZEN_PER_CELL_HORIZON = 2

HYPOTHESES_PER_CELL_HORIZON = (
    len(CONTINUOUS_FEATURES) * len(DIRECTIONS) * len(POLARITIES)
)
CELL_COUNT = len(SYMBOLS) * len(TIMEFRAMES) * len(HORIZONS_MINUTES)
MAX_DIRECTIONAL_HYPOTHESES_TOTAL = HYPOTHESES_PER_CELL_HORIZON * CELL_COUNT
MAX_SHORTLIST_GLOBAL = MAX_SHORTLIST_PER_CELL_HORIZON * CELL_COUNT
MAX_FROZEN_GLOBAL = MAX_FROZEN_PER_CELL_HORIZON * CELL_COUNT

RANK_FIELDS = (
    "lower_half_selected_tail_mean_net_pips_0p5_desc",
    "minimum_two_year_block_selected_tail_mean_net_pips_0p5_desc",
    "lower_half_signed_rank_slope_net_pips_0p5_desc",
    "minimum_two_year_block_signed_rank_slope_net_pips_0p5_desc",
    "positive_tail_mean_year_count_desc",
    "positive_slope_year_count_desc",
    "equal_year_selected_tail_mean_net_pips_1p0_desc",
    "total_selected_tail_support_desc",
    "feature_name_asc",
    "direction_asc",
    "polarity_asc",
    "fingerprint_asc",
)

SOURCE_ACCESS_AUTHORIZED = False
HISTORICAL_EXECUTION_AUTHORIZED = False
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
class AnnualContinuousEffectStat:
    year: int
    evaluable_support: int
    selected_tail_support: int
    signed_rank_slope_net_pips_0p5: float
    selected_tail_mean_net_pips_0p5: float
    selected_tail_mean_net_pips_1p0: float

    def __post_init__(self) -> None:
        if self.year not in DESIGN_YEARS:
            raise ValueError("DEC-452 annual stat year outside 2015-2022")
        if (
            not isinstance(self.evaluable_support, int)
            or isinstance(self.evaluable_support, bool)
            or self.evaluable_support < 2
        ):
            raise ValueError("DEC-452 evaluable support must be an integer >= 2")
        if (
            not isinstance(self.selected_tail_support, int)
            or isinstance(self.selected_tail_support, bool)
            or self.selected_tail_support < 1
        ):
            raise ValueError(
                "DEC-452 selected-tail support must be a positive integer"
            )
        if self.selected_tail_support > self.evaluable_support:
            raise ValueError(
                "DEC-452 selected-tail support exceeds evaluable support"
            )
        for field, value in (
            (
                "signed_rank_slope_net_pips_0p5",
                self.signed_rank_slope_net_pips_0p5,
            ),
            (
                "selected_tail_mean_net_pips_0p5",
                self.selected_tail_mean_net_pips_0p5,
            ),
            (
                "selected_tail_mean_net_pips_1p0",
                self.selected_tail_mean_net_pips_1p0,
            ),
        ):
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not math.isfinite(float(value))
            ):
                raise ValueError(f"DEC-452 {field} must be finite")


def rank_calibration_values(
    values: Sequence[float | int | None],
) -> tuple[float, ...] | None:
    finite = tuple(
        sorted(
            float(value)
            for value in values
            if isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(float(value))
        )
    )
    if len(finite) < MIN_RANK_CALIBRATION_ROWS:
        return None
    if len(set(finite)) < MIN_RANK_CALIBRATION_DISTINCT_VALUES:
        return None
    return finite


def empirical_midrank_percentile(
    calibration: Sequence[float],
    value: float | int | None,
) -> float | None:
    if (
        not calibration
        or not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(float(value))
    ):
        return None
    numeric = float(value)
    left = bisect.bisect_left(calibration, numeric)
    right = bisect.bisect_right(calibration, numeric)
    return (left + right) / (2.0 * len(calibration))


def centered_rank(percentile: float | int) -> float:
    if (
        not isinstance(percentile, (int, float))
        or isinstance(percentile, bool)
        or not math.isfinite(float(percentile))
    ):
        raise ValueError("DEC-452 percentile must be finite")
    value = float(percentile)
    if value < 0.0 or value > 1.0:
        raise ValueError("DEC-452 percentile must be in [0,1]")
    return value - 0.5


def polarity_sign(polarity: str) -> int:
    if polarity == "INCREASING":
        return 1
    if polarity == "DECREASING":
        return -1
    raise ValueError("DEC-452 unsupported polarity")


def selected_tail_accepts(*, percentile: float, polarity: str) -> bool:
    sign = polarity_sign(polarity)
    if sign > 0:
        return percentile >= UPPER_TAIL_MIN_PERCENTILE
    return percentile <= LOWER_TAIL_MAX_PERCENTILE


def signed_rank_slope(
    percentiles: Sequence[float],
    outcomes: Sequence[float],
    *,
    polarity: str,
) -> float:
    if len(percentiles) != len(outcomes) or len(percentiles) < 2:
        raise ValueError("DEC-452 slope inputs must have equal length >= 2")
    ranks = [centered_rank(value) for value in percentiles]
    ys: list[float] = []
    for value in outcomes:
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(float(value))
        ):
            raise ValueError("DEC-452 slope outcome must be finite")
        ys.append(float(value))
    mean_rank = math.fsum(ranks) / len(ranks)
    mean_y = math.fsum(ys) / len(ys)
    variance = math.fsum((value - mean_rank) ** 2 for value in ranks)
    if variance <= 0.0:
        raise ValueError("DEC-452 rank slope requires non-zero rank variance")
    covariance = math.fsum(
        (rank - mean_rank) * (value - mean_y)
        for rank, value in zip(ranks, ys)
    )
    return polarity_sign(polarity) * covariance / variance


def effect_hypothesis_fingerprint(
    *,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
    feature_name: str,
    direction: str,
    polarity: str,
) -> str:
    if symbol not in SYMBOLS:
        raise ValueError("DEC-452 unsupported symbol")
    if timeframe not in TIMEFRAMES:
        raise ValueError("DEC-452 unsupported timeframe")
    if horizon_minutes not in HORIZONS_MINUTES:
        raise ValueError("DEC-452 unsupported horizon")
    if feature_name not in CONTINUOUS_FEATURES:
        raise ValueError("DEC-452 unsupported feature")
    if direction not in DIRECTIONS:
        raise ValueError("DEC-452 unsupported market direction")
    if polarity not in POLARITIES:
        raise ValueError("DEC-452 unsupported effect polarity")
    payload = {
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "protocol_version": EXP064_CONTINUOUS_STABILITY_PROTOCOL_VERSION,
        "symbol": symbol,
        "timeframe": timeframe,
        "horizon_minutes": horizon_minutes,
        "feature_name": feature_name,
        "direction": direction,
        "polarity": polarity,
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _require_exact_annual_stats(
    annual_stats: Sequence[AnnualContinuousEffectStat],
) -> tuple[AnnualContinuousEffectStat, ...]:
    ordered = tuple(sorted(annual_stats, key=lambda item: item.year))
    if tuple(item.year for item in ordered) != DESIGN_YEARS:
        raise ValueError("DEC-452 annual stats must cover exactly 2015-2022")
    return ordered


def _lower_half_mean(values: Sequence[float]) -> float:
    if len(values) != len(DESIGN_YEARS):
        raise ValueError("DEC-452 lower-half metric requires eight annual values")
    weakest = sorted(float(value) for value in values)[:LOWER_HALF_YEAR_COUNT]
    return math.fsum(weakest) / LOWER_HALF_YEAR_COUNT


def continuous_stability_metrics(
    annual_stats: Sequence[AnnualContinuousEffectStat],
) -> dict[str, object]:
    ordered = _require_exact_annual_stats(annual_stats)
    slopes = [float(item.signed_rank_slope_net_pips_0p5) for item in ordered]
    tail_half = [
        float(item.selected_tail_mean_net_pips_0p5) for item in ordered
    ]
    tail_stress = [
        float(item.selected_tail_mean_net_pips_1p0) for item in ordered
    ]

    slope_by_year = {item.year: float(item.signed_rank_slope_net_pips_0p5) for item in ordered}
    tail_by_year = {item.year: float(item.selected_tail_mean_net_pips_0p5) for item in ordered}

    slope_blocks = {
        name: math.fsum(slope_by_year[year] for year in years) / len(years)
        for name, years in TWO_YEAR_BLOCKS
    }
    tail_blocks = {
        name: math.fsum(tail_by_year[year] for year in years) / len(years)
        for name, years in TWO_YEAR_BLOCKS
    }

    return {
        "total_selected_tail_support": sum(
            item.selected_tail_support for item in ordered
        ),
        "minimum_year_selected_tail_support": min(
            item.selected_tail_support for item in ordered
        ),
        "positive_slope_year_count": sum(value > 0.0 for value in slopes),
        "positive_tail_mean_year_count": sum(value > 0.0 for value in tail_half),
        "equal_year_signed_rank_slope_net_pips_0p5": (
            math.fsum(slopes) / len(slopes)
        ),
        "lower_half_annual_signed_rank_slope_net_pips_0p5": (
            _lower_half_mean(slopes)
        ),
        "equal_year_selected_tail_mean_net_pips_0p5": (
            math.fsum(tail_half) / len(tail_half)
        ),
        "equal_year_selected_tail_mean_net_pips_1p0": (
            math.fsum(tail_stress) / len(tail_stress)
        ),
        "lower_half_annual_selected_tail_mean_net_pips_0p5": (
            _lower_half_mean(tail_half)
        ),
        "two_year_block_signed_rank_slope_net_pips_0p5": slope_blocks,
        "minimum_two_year_block_signed_rank_slope_net_pips_0p5": min(
            slope_blocks.values()
        ),
        "two_year_block_selected_tail_mean_net_pips_0p5": tail_blocks,
        "minimum_two_year_block_selected_tail_mean_net_pips_0p5": min(
            tail_blocks.values()
        ),
    }


def continuous_stability_gate_passes(
    annual_stats: Sequence[AnnualContinuousEffectStat],
) -> bool:
    try:
        metrics = continuous_stability_metrics(annual_stats)
    except ValueError:
        return False

    if (
        int(metrics["total_selected_tail_support"])
        < MIN_TOTAL_SELECTED_TAIL_SUPPORT
    ):
        return False
    if (
        int(metrics["minimum_year_selected_tail_support"])
        < MIN_YEAR_SELECTED_TAIL_SUPPORT
    ):
        return False
    if int(metrics["positive_slope_year_count"]) < MIN_POSITIVE_SLOPE_YEARS:
        return False
    if (
        int(metrics["positive_tail_mean_year_count"])
        < MIN_POSITIVE_TAIL_MEAN_YEARS
    ):
        return False
    if (
        float(metrics["equal_year_signed_rank_slope_net_pips_0p5"])
        < MIN_EQUAL_YEAR_SIGNED_RANK_SLOPE_0P5
    ):
        return False
    if (
        float(metrics["equal_year_selected_tail_mean_net_pips_0p5"])
        < MIN_EQUAL_YEAR_SELECTED_TAIL_MEAN_0P5
    ):
        return False
    if (
        REQUIRE_LOWER_HALF_SIGNED_RANK_SLOPE_POSITIVE
        and float(
            metrics["lower_half_annual_signed_rank_slope_net_pips_0p5"]
        )
        <= 0.0
    ):
        return False
    if (
        REQUIRE_LOWER_HALF_SELECTED_TAIL_MEAN_POSITIVE
        and float(
            metrics["lower_half_annual_selected_tail_mean_net_pips_0p5"]
        )
        <= 0.0
    ):
        return False
    if (
        REQUIRE_EACH_TWO_YEAR_BLOCK_SIGNED_RANK_SLOPE_POSITIVE
        and float(
            metrics["minimum_two_year_block_signed_rank_slope_net_pips_0p5"]
        )
        <= 0.0
    ):
        return False
    if (
        REQUIRE_EACH_TWO_YEAR_BLOCK_SELECTED_TAIL_MEAN_POSITIVE
        and float(
            metrics["minimum_two_year_block_selected_tail_mean_net_pips_0p5"]
        )
        <= 0.0
    ):
        return False
    if (
        REQUIRE_EQUAL_YEAR_SELECTED_TAIL_STRESS_MEAN_POSITIVE
        and float(metrics["equal_year_selected_tail_mean_net_pips_1p0"]) <= 0.0
    ):
        return False
    return True


def protocol_payload() -> dict[str, object]:
    return {
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "decision": EXP064_CONTINUOUS_STABILITY_PROTOCOL_DECISION,
        "protocol_version": EXP064_CONTINUOUS_STABILITY_PROTOCOL_VERSION,
        "source_direction_decision": "DEC-451",
        "source_direction_merge_sha": DEC451_MERGE_SHA,
        "source_direction_blob_sha": DEC451_DIRECTION_BLOB_SHA,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "symbols": list(SYMBOLS),
        "timeframes": list(TIMEFRAMES),
        "horizons_minutes": list(HORIZONS_MINUTES),
        "continuous_features": list(CONTINUOUS_FEATURES),
        "chronology": {
            "design_start": DESIGN_START,
            "design_end_exclusive": DESIGN_END_EXCLUSIVE,
            "design_years": list(DESIGN_YEARS),
            "design_role": "ALREADY_SEEN_DESIGN_EVIDENCE",
            "reserved_robustness_start": RESERVED_ROBUSTNESS_START,
            "reserved_robustness_end_exclusive": RESERVED_ROBUSTNESS_END_EXCLUSIVE,
            "reserved_robustness_opened": False,
        },
        "rank_transform": {
            "method": RANK_METHOD,
            "calibration_start": RANK_CALIBRATION_START,
            "calibration_end_exclusive": RANK_CALIBRATION_END_EXCLUSIVE,
            "minimum_calibration_rows": MIN_RANK_CALIBRATION_ROWS,
            "minimum_distinct_values": MIN_RANK_CALIBRATION_DISTINCT_VALUES,
            "tie_policy": "empirical_midrank",
            "out_of_range_policy": "empirical_cdf_clips_naturally_to_0_or_1",
            "centered_rank": "percentile_minus_0p5",
            "reserve_rows_must_not_affect_calibration": True,
        },
        "hypothesis": {
            "unit": "single_feature_direction_polarity",
            "features_per_hypothesis": MAX_FEATURES_PER_HYPOTHESIS,
            "directions": list(DIRECTIONS),
            "polarities": list(POLARITIES),
            "interactions_authorized": INTERACTIONS_AUTHORIZED,
            "selected_tail": {
                "INCREASING": {
                    "minimum_percentile": UPPER_TAIL_MIN_PERCENTILE,
                },
                "DECREASING": {
                    "maximum_percentile": LOWER_TAIL_MAX_PERCENTILE,
                },
            },
            "hypotheses_per_cell_horizon": HYPOTHESES_PER_CELL_HORIZON,
            "maximum_directional_hypotheses_total": (
                MAX_DIRECTIONAL_HYPOTHESES_TOTAL
            ),
        },
        "effect_estimator": {
            "primary": "polarity_signed_ols_slope_of_0p5_net_pips_on_centered_rank",
            "economic_tail_metric": "selected_tail_mean_net_pips",
            "design_slippage_pips": DESIGN_SLIPPAGE_PIPS,
            "stress_slippage_pips": STRESS_SLIPPAGE_PIPS,
            "annual_effects_required": True,
            "equal_year_aggregation": True,
        },
        "gate": {
            "minimum_total_selected_tail_support": (
                MIN_TOTAL_SELECTED_TAIL_SUPPORT
            ),
            "minimum_selected_tail_support_each_year": (
                MIN_YEAR_SELECTED_TAIL_SUPPORT
            ),
            "minimum_positive_slope_years": MIN_POSITIVE_SLOPE_YEARS,
            "minimum_positive_tail_mean_years": (
                MIN_POSITIVE_TAIL_MEAN_YEARS
            ),
            "minimum_equal_year_signed_rank_slope_net_pips_0p5": (
                MIN_EQUAL_YEAR_SIGNED_RANK_SLOPE_0P5
            ),
            "minimum_equal_year_selected_tail_mean_net_pips_0p5": (
                MIN_EQUAL_YEAR_SELECTED_TAIL_MEAN_0P5
            ),
            "require_positive_lower_half_signed_rank_slope": (
                REQUIRE_LOWER_HALF_SIGNED_RANK_SLOPE_POSITIVE
            ),
            "require_positive_lower_half_selected_tail_mean": (
                REQUIRE_LOWER_HALF_SELECTED_TAIL_MEAN_POSITIVE
            ),
            "require_positive_each_two_year_block_signed_rank_slope": (
                REQUIRE_EACH_TWO_YEAR_BLOCK_SIGNED_RANK_SLOPE_POSITIVE
            ),
            "require_positive_each_two_year_block_selected_tail_mean": (
                REQUIRE_EACH_TWO_YEAR_BLOCK_SELECTED_TAIL_MEAN_POSITIVE
            ),
            "require_positive_equal_year_selected_tail_mean_at_1p0": (
                REQUIRE_EQUAL_YEAR_SELECTED_TAIL_STRESS_MEAN_POSITIVE
            ),
            "two_year_blocks": [
                {"name": name, "years": list(years)}
                for name, years in TWO_YEAR_BLOCKS
            ],
        },
        "ranking": {
            "fields": list(RANK_FIELDS),
            "maximum_shortlist_per_cell_horizon": (
                MAX_SHORTLIST_PER_CELL_HORIZON
            ),
            "maximum_shortlist_global": MAX_SHORTLIST_GLOBAL,
        },
        "deduplication": {
            "same_cell_horizon_direction_only": True,
            "selected_tail_event_jaccard_threshold": NEAR_DUPLICATE_JACCARD,
            "keep_higher_frozen_rank": True,
        },
        "freeze": {
            "maximum_per_cell_horizon": MAX_FROZEN_PER_CELL_HORIZON,
            "maximum_global": MAX_FROZEN_GLOBAL,
            "output_kind": OUTPUT_KIND,
            "candidate_compilation_deferred": True,
            "reserved_2023_2026_window_remains_closed": True,
        },
        "authorizations": {
            "source_access_authorized": SOURCE_ACCESS_AUTHORIZED,
            "historical_execution_authorized": HISTORICAL_EXECUTION_AUTHORIZED,
            "historical_result_authorized": HISTORICAL_RESULT_AUTHORIZED,
            "reserved_robustness_access_authorized": (
                RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED
            ),
            "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
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
    if SUCCESSOR_EXPERIMENT_ID != "EXP-20261001-064":
        raise ValueError("DEC-452 EXP-064 identity drift")
    if len(CONTINUOUS_FEATURES) != 20:
        raise ValueError("DEC-452 requires exactly 20 continuous features")
    if CELL_COUNT != 18:
        raise ValueError("DEC-452 requires exactly 18 cells")
    if HYPOTHESES_PER_CELL_HORIZON != 80:
        raise ValueError("DEC-452 requires exactly 80 hypotheses per cell")
    if MAX_DIRECTIONAL_HYPOTHESES_TOTAL != 1440:
        raise ValueError("DEC-452 global search bound drift")
    if MAX_SHORTLIST_GLOBAL != 90:
        raise ValueError("DEC-452 global shortlist cap drift")
    if MAX_FROZEN_GLOBAL != 36:
        raise ValueError("DEC-452 global frozen cap drift")
    if MAX_FEATURES_PER_HYPOTHESIS != 1 or INTERACTIONS_AUTHORIZED:
        raise ValueError("DEC-452 v1 must remain single-feature only")
    if LOWER_TAIL_MAX_PERCENTILE >= UPPER_TAIL_MIN_PERCENTILE:
        raise ValueError("DEC-452 tail definitions overlap")
    if tuple(year for _, years in TWO_YEAR_BLOCKS for year in years) != DESIGN_YEARS:
        raise ValueError("DEC-452 two-year block coverage drift")
    if RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED:
        raise ValueError("DEC-452 reserved robustness must remain closed")
    if HISTORICAL_EXECUTION_AUTHORIZED or HISTORICAL_RESULT_AUTHORIZED:
        raise ValueError("DEC-452 execution/result authority must remain false")


validate_protocol()


__all__ = [
    "AnnualContinuousEffectStat",
    "CONTINUOUS_FEATURES",
    "DESIGN_YEARS",
    "DIRECTIONS",
    "EXP064_CONTINUOUS_STABILITY_PROTOCOL_DECISION",
    "EXP064_CONTINUOUS_STABILITY_PROTOCOL_VERSION",
    "HORIZONS_MINUTES",
    "HYPOTHESES_PER_CELL_HORIZON",
    "MAX_DIRECTIONAL_HYPOTHESES_TOTAL",
    "MAX_FROZEN_GLOBAL",
    "MAX_FROZEN_PER_CELL_HORIZON",
    "MAX_SHORTLIST_GLOBAL",
    "MAX_SHORTLIST_PER_CELL_HORIZON",
    "POLARITIES",
    "RANK_FIELDS",
    "SYMBOLS",
    "TIMEFRAMES",
    "continuous_stability_gate_passes",
    "continuous_stability_metrics",
    "effect_hypothesis_fingerprint",
    "empirical_midrank_percentile",
    "polarity_sign",
    "protocol_fingerprint",
    "protocol_payload",
    "rank_calibration_values",
    "selected_tail_accepts",
    "signed_rank_slope",
    "validate_protocol",
]
