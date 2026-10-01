from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Sequence

from .exp064_continuous_stability_protocol import (
    centered_rank,
    empirical_midrank_percentile,
    rank_calibration_values,
)
from .pattern_protocol import CONTINUOUS_FEATURES, HORIZONS_MINUTES, SYMBOLS, TIMEFRAMES


EXP065_PAIRWISE_INTERACTION_PROTOCOL_DECISION = "DEC-460"
EXP065_PAIRWISE_INTERACTION_PROTOCOL_VERSION = (
    "fmp-exp065-pairwise-interaction-protocol-v1"
)

DEC459_MERGE_SHA = "c0d8ba052cc0cd662149aa787722874c7207ce4a"
DEC459_DIRECTION_BLOB_SHA = "7d9350f714bfec7cc39ebf76b2e6e313261e9a68"
DEC452_PROTOCOL_BLOB_SHA = "c108ea047c7bfb3e588bfbac33993180066c28ad"

EXPERIMENT_ID = "EXP-20261001-065"
SOURCE_EXPERIMENT_ID = "EXP-20261001-064"

DESIGN_YEARS = tuple(range(2015, 2023))
DESIGN_START = "2015-01-01"
DESIGN_END_EXCLUSIVE = "2023-01-01"
RESERVED_ROBUSTNESS_START = "2023-01-01"
RESERVED_ROBUSTNESS_END = "2026-08-20"

RANK_METHOD = "full_design_empirical_midrank_cdf"
INTERACTION_RAW_METHOD = "two_x_centered_rank_product"
INTERACTION_RANK_METHOD = "full_design_pairwise_interaction_empirical_midrank_cdf"
MAIN_EFFECT_CONTROL_METHOD = "annual_ols_with_constituent_centered_ranks"
INTERACTION_ESTIMATOR = (
    "annual_partial_ols_coefficient_on_centered_interaction_rank"
)
MAIN_EFFECT_RESIDUAL_METHOD = (
    "annual_main_effect_only_ols_residual_from_constituent_centered_ranks"
)

MIN_RANK_CALIBRATION_ROWS = 600
MIN_RANK_CALIBRATION_DISTINCT_VALUES = 20
MIN_INTERACTION_CALIBRATION_ROWS = 600
MIN_INTERACTION_CALIBRATION_DISTINCT_VALUES = 20
OLS_SINGULAR_TOLERANCE = 1e-12

DIRECTIONS = ("LONG", "SHORT")
POLARITIES = ("INCREASING", "DECREASING")
LOWER_TAIL_MAX_PERCENTILE = 0.25
UPPER_TAIL_MIN_PERCENTILE = 0.75

FEATURES_PER_HYPOTHESIS = 2
THREE_PLUS_FEATURE_INTERACTIONS_AUTHORIZED = False
PAIR_COUNT = len(CONTINUOUS_FEATURES) * (len(CONTINUOUS_FEATURES) - 1) // 2
HYPOTHESES_PER_CELL_HORIZON = PAIR_COUNT * len(DIRECTIONS) * len(POLARITIES)
CELL_COUNT = len(SYMBOLS) * len(TIMEFRAMES) * len(HORIZONS_MINUTES)
MAX_DIRECTIONAL_HYPOTHESES_TOTAL = HYPOTHESES_PER_CELL_HORIZON * CELL_COUNT

DESIGN_SLIPPAGE_PIPS = 0.5
STRESS_SLIPPAGE_PIPS = 1.0

MIN_TOTAL_SELECTED_TAIL_SUPPORT = 600
MIN_YEAR_SELECTED_TAIL_SUPPORT = 75
MIN_POSITIVE_PARTIAL_SLOPE_YEARS = 6
MIN_POSITIVE_RAW_TAIL_MEAN_YEARS = 6
MIN_POSITIVE_INCREMENTAL_TAIL_MEAN_YEARS = 6
MIN_EQUAL_YEAR_SIGNED_PARTIAL_SLOPE_0P5 = 0.25
MIN_EQUAL_YEAR_RAW_TAIL_MEAN_0P5 = 0.25
REQUIRE_EQUAL_YEAR_INCREMENTAL_TAIL_MEAN_POSITIVE = True
REQUIRE_LOWER_HALF_PARTIAL_SLOPE_POSITIVE = True
REQUIRE_LOWER_HALF_RAW_TAIL_MEAN_POSITIVE = True
REQUIRE_LOWER_HALF_INCREMENTAL_TAIL_MEAN_POSITIVE = True
REQUIRE_EACH_TWO_YEAR_BLOCK_PARTIAL_SLOPE_POSITIVE = True
REQUIRE_EACH_TWO_YEAR_BLOCK_RAW_TAIL_MEAN_POSITIVE = True
REQUIRE_EACH_TWO_YEAR_BLOCK_INCREMENTAL_TAIL_MEAN_POSITIVE = True
REQUIRE_EQUAL_YEAR_RAW_TAIL_STRESS_MEAN_POSITIVE = True

TWO_YEAR_BLOCKS = (
    ("2015-2016", (2015, 2016)),
    ("2017-2018", (2017, 2018)),
    ("2019-2020", (2019, 2020)),
    ("2021-2022", (2021, 2022)),
)

MAX_SHORTLIST_PER_CELL_HORIZON = 3
MAX_FROZEN_PER_CELL_HORIZON = 1
MAX_SHORTLIST_GLOBAL = MAX_SHORTLIST_PER_CELL_HORIZON * CELL_COUNT
MAX_FROZEN_GLOBAL = MAX_FROZEN_PER_CELL_HORIZON * CELL_COUNT
NEAR_DUPLICATE_JACCARD = 0.95

RANK_FIELDS = (
    "lower_half_incremental_tail_mean_net_pips_0p5_desc",
    "minimum_two_year_block_incremental_tail_mean_net_pips_0p5_desc",
    "lower_half_raw_tail_mean_net_pips_0p5_desc",
    "minimum_two_year_block_raw_tail_mean_net_pips_0p5_desc",
    "lower_half_signed_partial_slope_net_pips_0p5_desc",
    "minimum_two_year_block_signed_partial_slope_net_pips_0p5_desc",
    "positive_incremental_tail_mean_year_count_desc",
    "positive_raw_tail_mean_year_count_desc",
    "positive_partial_slope_year_count_desc",
    "equal_year_raw_tail_mean_net_pips_1p0_desc",
    "total_selected_tail_support_desc",
    "feature_a_asc",
    "feature_b_asc",
    "direction_asc",
    "polarity_asc",
)

OUTPUT_KIND = "RETROSPECTIVE_PAIRWISE_INTERACTION_HYPOTHESIS_NOT_VALIDATED"

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


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def feature_pairs() -> tuple[tuple[str, str], ...]:
    features = tuple(CONTINUOUS_FEATURES)
    return tuple(
        (features[left], features[right])
        for left in range(len(features))
        for right in range(left + 1, len(features))
    )


def canonical_feature_pair(
    feature_a: str,
    feature_b: str,
) -> tuple[str, str]:
    if feature_a == feature_b:
        raise ValueError("DEC-460 pair requires two distinct features")
    pairs = feature_pairs()
    direct = (feature_a, feature_b)
    reverse = (feature_b, feature_a)
    if direct in pairs:
        return direct
    if reverse in pairs:
        return reverse
    raise ValueError("DEC-460 unsupported feature pair")


def pairwise_interaction_raw(
    feature_a_percentile: float | int,
    feature_b_percentile: float | int,
) -> float:
    return 2.0 * centered_rank(feature_a_percentile) * centered_rank(
        feature_b_percentile
    )


def interaction_calibration_values(
    feature_a_percentiles: Sequence[float | int],
    feature_b_percentiles: Sequence[float | int],
) -> tuple[float, ...]:
    if len(feature_a_percentiles) != len(feature_b_percentiles):
        raise ValueError("DEC-460 pair calibration length mismatch")
    raw = [
        pairwise_interaction_raw(left, right)
        for left, right in zip(feature_a_percentiles, feature_b_percentiles)
    ]
    finite = rank_calibration_values(raw)
    if finite is None:
        raise ValueError(
            "DEC-460 interaction calibration does not satisfy frozen "
            "row/distinct requirements"
        )
    if len(finite) < MIN_INTERACTION_CALIBRATION_ROWS:
        raise ValueError("DEC-460 interaction calibration row count below protocol")
    if len(set(finite)) < MIN_INTERACTION_CALIBRATION_DISTINCT_VALUES:
        raise ValueError(
            "DEC-460 interaction calibration distinct count below protocol"
        )
    return finite


def interaction_percentile(
    raw_interaction: float | int,
    calibration_values: Sequence[float | int],
) -> float:
    percentile = empirical_midrank_percentile(
        calibration_values,
        raw_interaction,
    )
    if percentile is None:
        raise ValueError("DEC-460 interaction percentile input is not evaluable")
    return percentile


def selected_tail_accepts(
    *,
    interaction_percentile_value: float | int,
    polarity: str,
) -> bool:
    value = float(interaction_percentile_value)
    if not math.isfinite(value) or value < 0.0 or value > 1.0:
        raise ValueError("DEC-460 interaction percentile must be finite in [0,1]")
    if polarity == "INCREASING":
        return value >= UPPER_TAIL_MIN_PERCENTILE
    if polarity == "DECREASING":
        return value <= LOWER_TAIL_MAX_PERCENTILE
    raise ValueError("DEC-460 unsupported polarity")


def _validate_equal_lengths(*values: Sequence[float | int]) -> int:
    sizes = {len(item) for item in values}
    if len(sizes) != 1:
        raise ValueError("DEC-460 regression length mismatch")
    size = sizes.pop()
    if size < 4:
        raise ValueError("DEC-460 regression requires at least four rows")
    return size


def _finite_vector(values: Sequence[float | int], *, field: str) -> list[float]:
    out = [float(value) for value in values]
    if not all(math.isfinite(value) for value in out):
        raise ValueError(f"DEC-460 {field} must be finite")
    return out


def _solve_ols(
    columns: Sequence[Sequence[float | int]],
    outcomes: Sequence[float | int],
) -> tuple[float, ...]:
    if not columns:
        raise ValueError("DEC-460 OLS requires predictors")
    size = _validate_equal_lengths(*columns, outcomes)
    xs = [
        _finite_vector(column, field=f"OLS column {index}")
        for index, column in enumerate(columns)
    ]
    ys = _finite_vector(outcomes, field="OLS outcomes")
    width = len(xs)

    normal = [
        [
            math.fsum(xs[left][row] * xs[right][row] for row in range(size))
            for right in range(width)
        ]
        for left in range(width)
    ]
    target = [
        math.fsum(xs[column][row] * ys[row] for row in range(size))
        for column in range(width)
    ]
    matrix = [normal[row] + [target[row]] for row in range(width)]

    for pivot_col in range(width):
        pivot_row = max(
            range(pivot_col, width),
            key=lambda row: abs(matrix[row][pivot_col]),
        )
        pivot = matrix[pivot_row][pivot_col]
        if abs(pivot) <= OLS_SINGULAR_TOLERANCE:
            raise ValueError("DEC-460 OLS design is singular")
        if pivot_row != pivot_col:
            matrix[pivot_col], matrix[pivot_row] = (
                matrix[pivot_row],
                matrix[pivot_col],
            )

        pivot = matrix[pivot_col][pivot_col]
        matrix[pivot_col] = [value / pivot for value in matrix[pivot_col]]
        for row in range(width):
            if row == pivot_col:
                continue
            factor = matrix[row][pivot_col]
            if factor == 0.0:
                continue
            matrix[row] = [
                current - factor * reference
                for current, reference in zip(matrix[row], matrix[pivot_col])
            ]

    return tuple(matrix[row][-1] for row in range(width))


def partial_interaction_slope(
    feature_a_percentiles: Sequence[float | int],
    feature_b_percentiles: Sequence[float | int],
    interaction_percentiles: Sequence[float | int],
    outcomes: Sequence[float | int],
) -> float:
    size = _validate_equal_lengths(
        feature_a_percentiles,
        feature_b_percentiles,
        interaction_percentiles,
        outcomes,
    )
    ones = [1.0] * size
    feature_a = [centered_rank(value) for value in feature_a_percentiles]
    feature_b = [centered_rank(value) for value in feature_b_percentiles]
    interaction = [centered_rank(value) for value in interaction_percentiles]
    beta = _solve_ols((ones, feature_a, feature_b, interaction), outcomes)
    return beta[3]


def main_effect_residuals(
    feature_a_percentiles: Sequence[float | int],
    feature_b_percentiles: Sequence[float | int],
    outcomes: Sequence[float | int],
) -> tuple[float, ...]:
    size = _validate_equal_lengths(
        feature_a_percentiles,
        feature_b_percentiles,
        outcomes,
    )
    ones = [1.0] * size
    feature_a = [centered_rank(value) for value in feature_a_percentiles]
    feature_b = [centered_rank(value) for value in feature_b_percentiles]
    ys = _finite_vector(outcomes, field="main-effect outcomes")
    beta = _solve_ols((ones, feature_a, feature_b), ys)
    return tuple(
        ys[index]
        - (
            beta[0]
            + beta[1] * feature_a[index]
            + beta[2] * feature_b[index]
        )
        for index in range(size)
    )


def pair_hypothesis_fingerprint(
    *,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
    feature_a: str,
    feature_b: str,
    direction: str,
    polarity: str,
) -> str:
    if symbol not in SYMBOLS:
        raise ValueError("DEC-460 unsupported symbol")
    if timeframe not in TIMEFRAMES:
        raise ValueError("DEC-460 unsupported timeframe")
    if horizon_minutes not in HORIZONS_MINUTES:
        raise ValueError("DEC-460 unsupported horizon")
    pair = canonical_feature_pair(feature_a, feature_b)
    if direction not in DIRECTIONS:
        raise ValueError("DEC-460 unsupported direction")
    if polarity not in POLARITIES:
        raise ValueError("DEC-460 unsupported polarity")
    payload = {
        "experiment_id": EXPERIMENT_ID,
        "symbol": symbol,
        "timeframe": timeframe,
        "horizon_minutes": horizon_minutes,
        "feature_a": pair[0],
        "feature_b": pair[1],
        "direction": direction,
        "polarity": polarity,
    }
    return hashlib.sha256(_canonical_json(payload)).hexdigest()


@dataclass(frozen=True, slots=True)
class AnnualPairwiseInteractionStat:
    year: int
    evaluable_support: int
    selected_tail_support: int
    signed_partial_interaction_slope_net_pips_0p5: float
    selected_tail_mean_net_pips_0p5: float
    selected_tail_incremental_residual_mean_net_pips_0p5: float
    selected_tail_mean_net_pips_1p0: float

    def __post_init__(self) -> None:
        if self.year not in DESIGN_YEARS:
            raise ValueError("DEC-460 annual stat year outside design years")
        if (
            not isinstance(self.evaluable_support, int)
            or isinstance(self.evaluable_support, bool)
            or self.evaluable_support < 1
        ):
            raise ValueError("DEC-460 evaluable support must be positive")
        if (
            not isinstance(self.selected_tail_support, int)
            or isinstance(self.selected_tail_support, bool)
            or self.selected_tail_support < 1
        ):
            raise ValueError("DEC-460 selected-tail support must be positive")
        if self.selected_tail_support > self.evaluable_support:
            raise ValueError("DEC-460 selected-tail support exceeds evaluable support")
        for value in (
            self.signed_partial_interaction_slope_net_pips_0p5,
            self.selected_tail_mean_net_pips_0p5,
            self.selected_tail_incremental_residual_mean_net_pips_0p5,
            self.selected_tail_mean_net_pips_1p0,
        ):
            if not math.isfinite(float(value)):
                raise ValueError("DEC-460 annual metrics must be finite")


def _ordered_stats(
    annual_stats: Sequence[AnnualPairwiseInteractionStat],
) -> tuple[AnnualPairwiseInteractionStat, ...]:
    ordered = tuple(sorted(annual_stats, key=lambda item: item.year))
    if tuple(item.year for item in ordered) != DESIGN_YEARS:
        raise ValueError("DEC-460 annual stats must cover exactly 2015-2022")
    return ordered


def _lower_half_mean(values: Sequence[float]) -> float:
    if len(values) != len(DESIGN_YEARS):
        raise ValueError("DEC-460 lower-half metric requires eight years")
    return math.fsum(sorted(values)[: len(values) // 2]) / (len(values) // 2)


def pairwise_interaction_metrics(
    annual_stats: Sequence[AnnualPairwiseInteractionStat],
) -> dict[str, object]:
    ordered = _ordered_stats(annual_stats)
    partial = [
        float(item.signed_partial_interaction_slope_net_pips_0p5)
        for item in ordered
    ]
    raw_tail = [float(item.selected_tail_mean_net_pips_0p5) for item in ordered]
    incremental = [
        float(item.selected_tail_incremental_residual_mean_net_pips_0p5)
        for item in ordered
    ]
    stress = [float(item.selected_tail_mean_net_pips_1p0) for item in ordered]

    partial_by_year = {item.year: partial[index] for index, item in enumerate(ordered)}
    raw_by_year = {item.year: raw_tail[index] for index, item in enumerate(ordered)}
    incremental_by_year = {
        item.year: incremental[index] for index, item in enumerate(ordered)
    }

    partial_blocks = {
        name: math.fsum(partial_by_year[year] for year in years) / len(years)
        for name, years in TWO_YEAR_BLOCKS
    }
    raw_blocks = {
        name: math.fsum(raw_by_year[year] for year in years) / len(years)
        for name, years in TWO_YEAR_BLOCKS
    }
    incremental_blocks = {
        name: math.fsum(incremental_by_year[year] for year in years) / len(years)
        for name, years in TWO_YEAR_BLOCKS
    }

    return {
        "total_selected_tail_support": sum(
            item.selected_tail_support for item in ordered
        ),
        "minimum_year_selected_tail_support": min(
            item.selected_tail_support for item in ordered
        ),
        "positive_partial_slope_year_count": sum(value > 0.0 for value in partial),
        "positive_raw_tail_mean_year_count": sum(
            value > 0.0 for value in raw_tail
        ),
        "positive_incremental_tail_mean_year_count": sum(
            value > 0.0 for value in incremental
        ),
        "equal_year_signed_partial_slope_net_pips_0p5": (
            math.fsum(partial) / len(partial)
        ),
        "equal_year_raw_tail_mean_net_pips_0p5": (
            math.fsum(raw_tail) / len(raw_tail)
        ),
        "equal_year_incremental_tail_mean_net_pips_0p5": (
            math.fsum(incremental) / len(incremental)
        ),
        "equal_year_raw_tail_mean_net_pips_1p0": (
            math.fsum(stress) / len(stress)
        ),
        "lower_half_signed_partial_slope_net_pips_0p5": _lower_half_mean(partial),
        "lower_half_raw_tail_mean_net_pips_0p5": _lower_half_mean(raw_tail),
        "lower_half_incremental_tail_mean_net_pips_0p5": (
            _lower_half_mean(incremental)
        ),
        "two_year_block_signed_partial_slope_net_pips_0p5": partial_blocks,
        "minimum_two_year_block_signed_partial_slope_net_pips_0p5": min(
            partial_blocks.values()
        ),
        "two_year_block_raw_tail_mean_net_pips_0p5": raw_blocks,
        "minimum_two_year_block_raw_tail_mean_net_pips_0p5": min(
            raw_blocks.values()
        ),
        "two_year_block_incremental_tail_mean_net_pips_0p5": incremental_blocks,
        "minimum_two_year_block_incremental_tail_mean_net_pips_0p5": min(
            incremental_blocks.values()
        ),
    }


def pairwise_interaction_gate_passes(
    annual_stats: Sequence[AnnualPairwiseInteractionStat],
) -> bool:
    metrics = pairwise_interaction_metrics(annual_stats)
    if int(metrics["total_selected_tail_support"]) < MIN_TOTAL_SELECTED_TAIL_SUPPORT:
        return False
    if (
        int(metrics["minimum_year_selected_tail_support"])
        < MIN_YEAR_SELECTED_TAIL_SUPPORT
    ):
        return False
    if (
        int(metrics["positive_partial_slope_year_count"])
        < MIN_POSITIVE_PARTIAL_SLOPE_YEARS
    ):
        return False
    if (
        int(metrics["positive_raw_tail_mean_year_count"])
        < MIN_POSITIVE_RAW_TAIL_MEAN_YEARS
    ):
        return False
    if (
        int(metrics["positive_incremental_tail_mean_year_count"])
        < MIN_POSITIVE_INCREMENTAL_TAIL_MEAN_YEARS
    ):
        return False
    if (
        float(metrics["equal_year_signed_partial_slope_net_pips_0p5"])
        < MIN_EQUAL_YEAR_SIGNED_PARTIAL_SLOPE_0P5
    ):
        return False
    if (
        float(metrics["equal_year_raw_tail_mean_net_pips_0p5"])
        < MIN_EQUAL_YEAR_RAW_TAIL_MEAN_0P5
    ):
        return False
    if (
        REQUIRE_EQUAL_YEAR_INCREMENTAL_TAIL_MEAN_POSITIVE
        and float(metrics["equal_year_incremental_tail_mean_net_pips_0p5"]) <= 0.0
    ):
        return False
    if (
        REQUIRE_LOWER_HALF_PARTIAL_SLOPE_POSITIVE
        and float(metrics["lower_half_signed_partial_slope_net_pips_0p5"]) <= 0.0
    ):
        return False
    if (
        REQUIRE_LOWER_HALF_RAW_TAIL_MEAN_POSITIVE
        and float(metrics["lower_half_raw_tail_mean_net_pips_0p5"]) <= 0.0
    ):
        return False
    if (
        REQUIRE_LOWER_HALF_INCREMENTAL_TAIL_MEAN_POSITIVE
        and float(metrics["lower_half_incremental_tail_mean_net_pips_0p5"]) <= 0.0
    ):
        return False
    if (
        REQUIRE_EACH_TWO_YEAR_BLOCK_PARTIAL_SLOPE_POSITIVE
        and float(
            metrics[
                "minimum_two_year_block_signed_partial_slope_net_pips_0p5"
            ]
        )
        <= 0.0
    ):
        return False
    if (
        REQUIRE_EACH_TWO_YEAR_BLOCK_RAW_TAIL_MEAN_POSITIVE
        and float(metrics["minimum_two_year_block_raw_tail_mean_net_pips_0p5"])
        <= 0.0
    ):
        return False
    if (
        REQUIRE_EACH_TWO_YEAR_BLOCK_INCREMENTAL_TAIL_MEAN_POSITIVE
        and float(
            metrics[
                "minimum_two_year_block_incremental_tail_mean_net_pips_0p5"
            ]
        )
        <= 0.0
    ):
        return False
    if (
        REQUIRE_EQUAL_YEAR_RAW_TAIL_STRESS_MEAN_POSITIVE
        and float(metrics["equal_year_raw_tail_mean_net_pips_1p0"]) <= 0.0
    ):
        return False
    return True


def protocol_payload() -> dict[str, object]:
    payload: dict[str, object] = {
        "decision": EXP065_PAIRWISE_INTERACTION_PROTOCOL_DECISION,
        "version": EXP065_PAIRWISE_INTERACTION_PROTOCOL_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "source_experiment_id": SOURCE_EXPERIMENT_ID,
        "dec459_merge_sha": DEC459_MERGE_SHA,
        "dec459_direction_blob_sha": DEC459_DIRECTION_BLOB_SHA,
        "dec452_rank_protocol_blob_sha": DEC452_PROTOCOL_BLOB_SHA,
        "chronology": {
            "design_start": DESIGN_START,
            "design_end_exclusive": DESIGN_END_EXCLUSIVE,
            "design_years": list(DESIGN_YEARS),
            "design_role": "ALREADY_SEEN_DESIGN_EVIDENCE",
            "reserved_robustness_start": RESERVED_ROBUSTNESS_START,
            "reserved_robustness_end": RESERVED_ROBUSTNESS_END,
            "reserved_robustness_opened": False,
        },
        "bounded_universe": {
            "symbols": list(SYMBOLS),
            "timeframes": list(TIMEFRAMES),
            "horizons_minutes": list(HORIZONS_MINUTES),
            "continuous_features": list(CONTINUOUS_FEATURES),
            "feature_pair_count": PAIR_COUNT,
            "features_per_hypothesis": FEATURES_PER_HYPOTHESIS,
            "three_plus_feature_interactions_authorized": False,
        },
        "rank_transform": {
            "feature_rank_method": RANK_METHOD,
            "interaction_raw_method": INTERACTION_RAW_METHOD,
            "interaction_rank_method": INTERACTION_RANK_METHOD,
            "minimum_feature_calibration_rows": MIN_RANK_CALIBRATION_ROWS,
            "minimum_feature_distinct_values": (
                MIN_RANK_CALIBRATION_DISTINCT_VALUES
            ),
            "minimum_interaction_calibration_rows": (
                MIN_INTERACTION_CALIBRATION_ROWS
            ),
            "minimum_interaction_distinct_values": (
                MIN_INTERACTION_CALIBRATION_DISTINCT_VALUES
            ),
            "interaction_raw_formula": (
                "2 * (feature_a_percentile - 0.5) * "
                "(feature_b_percentile - 0.5)"
            ),
            "interaction_percentile_calibration_scope": "full_2015_2022_design",
        },
        "hypothesis": {
            "unit": "unordered_feature_pair_direction_polarity",
            "directions": list(DIRECTIONS),
            "polarities": list(POLARITIES),
            "pair_order": "canonical_continuous_feature_list_index",
            "same_feature_pair_allowed": False,
            "hypotheses_per_cell_horizon": HYPOTHESES_PER_CELL_HORIZON,
            "maximum_directional_hypotheses_total": (
                MAX_DIRECTIONAL_HYPOTHESES_TOTAL
            ),
            "selected_tail": {
                "increasing_minimum_percentile": UPPER_TAIL_MIN_PERCENTILE,
                "decreasing_maximum_percentile": LOWER_TAIL_MAX_PERCENTILE,
            },
        },
        "incrementality": {
            "interaction_estimator": INTERACTION_ESTIMATOR,
            "main_effect_control_method": MAIN_EFFECT_CONTROL_METHOD,
            "main_effect_residual_method": MAIN_EFFECT_RESIDUAL_METHOD,
            "ols_singular_tolerance": OLS_SINGULAR_TOLERANCE,
            "constituent_main_effects_must_be_controlled": True,
            "selected_tail_incremental_residual_must_be_positive": True,
        },
        "costs": {
            "design_slippage_pips": DESIGN_SLIPPAGE_PIPS,
            "stress_slippage_pips": STRESS_SLIPPAGE_PIPS,
            "economic_tail_metric": "selected_tail_mean_net_pips",
        },
        "qualification": {
            "minimum_total_selected_tail_support": (
                MIN_TOTAL_SELECTED_TAIL_SUPPORT
            ),
            "minimum_selected_tail_support_each_year": (
                MIN_YEAR_SELECTED_TAIL_SUPPORT
            ),
            "minimum_positive_partial_slope_years": (
                MIN_POSITIVE_PARTIAL_SLOPE_YEARS
            ),
            "minimum_positive_raw_tail_mean_years": (
                MIN_POSITIVE_RAW_TAIL_MEAN_YEARS
            ),
            "minimum_positive_incremental_tail_mean_years": (
                MIN_POSITIVE_INCREMENTAL_TAIL_MEAN_YEARS
            ),
            "minimum_equal_year_signed_partial_slope_net_pips_0p5": (
                MIN_EQUAL_YEAR_SIGNED_PARTIAL_SLOPE_0P5
            ),
            "minimum_equal_year_raw_tail_mean_net_pips_0p5": (
                MIN_EQUAL_YEAR_RAW_TAIL_MEAN_0P5
            ),
            "require_positive_equal_year_incremental_tail_mean": True,
            "require_positive_lower_half_partial_slope": True,
            "require_positive_lower_half_raw_tail_mean": True,
            "require_positive_lower_half_incremental_tail_mean": True,
            "require_positive_each_two_year_block_partial_slope": True,
            "require_positive_each_two_year_block_raw_tail_mean": True,
            "require_positive_each_two_year_block_incremental_tail_mean": True,
            "require_positive_equal_year_raw_tail_mean_at_1p0": True,
            "two_year_blocks": [
                [name, list(years)] for name, years in TWO_YEAR_BLOCKS
            ],
        },
        "ranking": {
            "fields": list(RANK_FIELDS),
            "maximum_shortlist_per_cell_horizon": (
                MAX_SHORTLIST_PER_CELL_HORIZON
            ),
            "maximum_shortlist_global": MAX_SHORTLIST_GLOBAL,
            "selected_tail_event_jaccard_threshold": NEAR_DUPLICATE_JACCARD,
            "maximum_frozen_per_cell_horizon": MAX_FROZEN_PER_CELL_HORIZON,
            "maximum_frozen_global": MAX_FROZEN_GLOBAL,
        },
        "evidence_semantics": {
            "label": "RETROSPECTIVE_ALREADY_SEEN",
            "untouched_oos": False,
            "output_kind": OUTPUT_KIND,
        },
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
        "next_gate": "SOURCE_ONLY_EXP065_PAIRWISE_INTERACTION_MINER",
    }
    payload["protocol_fingerprint"] = hashlib.sha256(
        _canonical_json(payload)
    ).hexdigest()
    return payload


def protocol_fingerprint() -> str:
    return str(protocol_payload()["protocol_fingerprint"])


def validate_protocol() -> dict[str, object]:
    if DEC459_MERGE_SHA != "c0d8ba052cc0cd662149aa787722874c7207ce4a":
        raise ValueError("DEC-460 DEC-459 merge pin drift")
    if DEC459_DIRECTION_BLOB_SHA != "7d9350f714bfec7cc39ebf76b2e6e313261e9a68":
        raise ValueError("DEC-460 DEC-459 direction pin drift")
    if tuple(SYMBOLS) != ("EURUSD", "GBPUSD", "USDJPY"):
        raise ValueError("DEC-460 symbol universe drift")
    if tuple(TIMEFRAMES) != ("5m", "15m", "1h"):
        raise ValueError("DEC-460 timeframe universe drift")
    if tuple(HORIZONS_MINUTES) != (60, 240):
        raise ValueError("DEC-460 horizon universe drift")
    if len(CONTINUOUS_FEATURES) != 20:
        raise ValueError("DEC-460 requires exactly 20 continuous features")
    if len(feature_pairs()) != 190 or PAIR_COUNT != 190:
        raise ValueError("DEC-460 feature pair count drift")
    if FEATURES_PER_HYPOTHESIS != 2:
        raise ValueError("DEC-460 must remain exactly pairwise")
    if THREE_PLUS_FEATURE_INTERACTIONS_AUTHORIZED:
        raise ValueError("DEC-460 cannot authorize 3+ feature interactions")
    if HYPOTHESES_PER_CELL_HORIZON != 760:
        raise ValueError("DEC-460 per-cell hypothesis bound drift")
    if MAX_DIRECTIONAL_HYPOTHESES_TOTAL != 13680:
        raise ValueError("DEC-460 global hypothesis bound drift")
    if MAX_SHORTLIST_GLOBAL != 54:
        raise ValueError("DEC-460 global shortlist cap drift")
    if MAX_FROZEN_GLOBAL != 18:
        raise ValueError("DEC-460 global frozen cap drift")
    if LOWER_TAIL_MAX_PERCENTILE >= UPPER_TAIL_MIN_PERCENTILE:
        raise ValueError("DEC-460 tail definitions overlap")
    if tuple(year for _, years in TWO_YEAR_BLOCKS for year in years) != DESIGN_YEARS:
        raise ValueError("DEC-460 two-year block coverage drift")
    if DESIGN_END_EXCLUSIVE != RESERVED_ROBUSTNESS_START:
        raise ValueError("DEC-460 design/reserved boundary drift")

    payload = protocol_payload()
    for field in (
        "source_access_authorized",
        "historical_execution_authorized",
        "historical_result_authorized",
        "reserved_robustness_access_authorized",
        "candidate_compilation_authorized",
        "promotion_authorized",
        "phase8b_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "trading_authorized",
    ):
        if payload[field] is not False:
            raise ValueError(f"DEC-460 {field} must remain false")
    return payload


__all__ = [
    "AnnualPairwiseInteractionStat",
    "DEC459_DIRECTION_BLOB_SHA",
    "DEC459_MERGE_SHA",
    "EXP065_PAIRWISE_INTERACTION_PROTOCOL_DECISION",
    "HYPOTHESES_PER_CELL_HORIZON",
    "MAX_DIRECTIONAL_HYPOTHESES_TOTAL",
    "MAX_FROZEN_GLOBAL",
    "MAX_FROZEN_PER_CELL_HORIZON",
    "MAX_SHORTLIST_GLOBAL",
    "MAX_SHORTLIST_PER_CELL_HORIZON",
    "OUTPUT_KIND",
    "PAIR_COUNT",
    "RANK_FIELDS",
    "canonical_feature_pair",
    "feature_pairs",
    "interaction_calibration_values",
    "interaction_percentile",
    "main_effect_residuals",
    "pair_hypothesis_fingerprint",
    "pairwise_interaction_gate_passes",
    "pairwise_interaction_metrics",
    "pairwise_interaction_raw",
    "partial_interaction_slope",
    "protocol_fingerprint",
    "protocol_payload",
    "selected_tail_accepts",
    "validate_protocol",
]
