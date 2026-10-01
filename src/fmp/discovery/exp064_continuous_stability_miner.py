from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Mapping, Sequence

from .exp064_continuous_stability_protocol import (
    CONTINUOUS_FEATURES,
    DESIGN_YEARS,
    DIRECTIONS,
    HORIZONS_MINUTES,
    HYPOTHESES_PER_CELL_HORIZON,
    MAX_FROZEN_PER_CELL_HORIZON,
    MAX_SHORTLIST_PER_CELL_HORIZON,
    NEAR_DUPLICATE_JACCARD,
    OUTPUT_KIND,
    POLARITIES,
    RANK_FIELDS,
    SYMBOLS,
    TIMEFRAMES,
    AnnualContinuousEffectStat,
    continuous_stability_gate_passes,
    continuous_stability_metrics,
    effect_hypothesis_fingerprint,
    empirical_midrank_percentile,
    rank_calibration_values,
    selected_tail_accepts,
    signed_rank_slope,
)
from .pattern_miner import FeatureObservation, OutcomeObservation


EXP064_CONTINUOUS_STABILITY_MINER_DECISION = "DEC-453"
EXP064_CONTINUOUS_STABILITY_MINER_VERSION = (
    "fmp-exp064-continuous-stability-miner-core-v1"
)

DEC452_MERGE_SHA = "b44af18b7cc5f3fa67d2f938529151f74d9deceb"
DEC452_PROTOCOL_BLOB_SHA = "c108ea047c7bfb3e588bfbac33993180066c28ad"
BASE_OBSERVATION_MODEL_BLOB_SHA = (
    "495a67699eb5014e52129f0238a2737049fe38e6"
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
class FeatureRankCalibration:
    feature_name: str
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if self.feature_name not in CONTINUOUS_FEATURES:
            raise ValueError("DEC-453 unsupported calibration feature")
        if not self.values:
            raise ValueError("DEC-453 rank calibration cannot be empty")
        if tuple(sorted(self.values)) != self.values:
            raise ValueError("DEC-453 rank calibration must be sorted")
        if any(not math.isfinite(value) for value in self.values):
            raise ValueError("DEC-453 rank calibration must be finite")


@dataclass(frozen=True, slots=True)
class ContinuousStabilityHypothesis:
    symbol: str
    timeframe: str
    horizon_minutes: int
    feature_name: str
    direction: str
    polarity: str
    fingerprint: str
    annual_stats: tuple[AnnualContinuousEffectStat, ...]
    total_selected_tail_support: int
    minimum_year_selected_tail_support: int
    positive_slope_year_count: int
    positive_tail_mean_year_count: int
    equal_year_signed_rank_slope_net_pips_0p5: float
    lower_half_annual_signed_rank_slope_net_pips_0p5: float
    equal_year_selected_tail_mean_net_pips_0p5: float
    equal_year_selected_tail_mean_net_pips_1p0: float
    lower_half_annual_selected_tail_mean_net_pips_0p5: float
    two_year_block_signed_rank_slope_net_pips_0p5: tuple[
        tuple[str, float], ...
    ]
    minimum_two_year_block_signed_rank_slope_net_pips_0p5: float
    two_year_block_selected_tail_mean_net_pips_0p5: tuple[
        tuple[str, float], ...
    ]
    minimum_two_year_block_selected_tail_mean_net_pips_0p5: float


@dataclass(frozen=True, slots=True)
class ContinuousStabilityMiningReport:
    symbol: str
    timeframe: str
    horizon_minutes: int
    active_continuous_features: tuple[str, ...]
    hypothesis_count: int
    evaluable_hypothesis_count: int
    qualifying_hypothesis_count: int
    deduplicated_hypothesis_count: int
    shortlist: tuple[ContinuousStabilityHypothesis, ...]
    frozen: tuple[ContinuousStabilityHypothesis, ...]
    output_kind: str = OUTPUT_KIND


@dataclass(frozen=True, slots=True)
class InMemoryContinuousStabilityResult:
    calibrations: tuple[FeatureRankCalibration, ...]
    report: ContinuousStabilityMiningReport


def _validate_utc(value: datetime, *, field: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must use UTC")


def _design_features(
    observations: Sequence[FeatureObservation],
    *,
    symbol: str,
    timeframe: str,
) -> tuple[FeatureObservation, ...]:
    if symbol not in SYMBOLS or timeframe not in TIMEFRAMES:
        raise ValueError("unsupported DEC-453 EXP-064 feature cell")
    start = datetime(2015, 1, 1, tzinfo=timezone.utc)
    end = datetime(2023, 1, 1, tzinfo=timezone.utc)
    rows = tuple(
        row
        for row in observations
        if row.symbol == symbol
        and row.timeframe == timeframe
        and start <= row.available_at_utc < end
    )
    ids = [row.observation_id for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate DEC-453 feature observation identity")
    return tuple(
        sorted(rows, key=lambda row: (row.available_at_utc, row.observation_id))
    )


def _design_outcomes(
    outcomes: Sequence[OutcomeObservation],
    *,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
) -> tuple[OutcomeObservation, ...]:
    if horizon_minutes not in HORIZONS_MINUTES:
        raise ValueError("unsupported DEC-453 EXP-064 horizon")
    rows: list[OutcomeObservation] = []
    for year in DESIGN_YEARS:
        start = datetime(year, 1, 1, tzinfo=timezone.utc)
        end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        rows.extend(
            row
            for row in outcomes
            if row.symbol == symbol
            and row.timeframe == timeframe
            and row.horizon_minutes == horizon_minutes
            and start <= row.available_at_utc < end
            and row.exit_timestamp_utc < end
        )
    ids = [row.observation_id for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate DEC-453 outcome observation identity")
    return tuple(
        sorted(rows, key=lambda row: (row.available_at_utc, row.observation_id))
    )


def _bind_rows(
    features: Sequence[FeatureObservation],
    outcomes: Sequence[OutcomeObservation],
) -> tuple[
    dict[str, FeatureObservation],
    dict[str, OutcomeObservation],
]:
    feature_by_id = {row.observation_id: row for row in features}
    outcome_by_id = {row.observation_id: row for row in outcomes}
    for observation_id, outcome in outcome_by_id.items():
        feature = feature_by_id.get(observation_id)
        if feature is None:
            raise ValueError(
                "DEC-453 outcome has no matching feature observation"
            )
        if (
            feature.symbol != outcome.symbol
            or feature.timeframe != outcome.timeframe
            or feature.available_at_utc != outcome.available_at_utc
        ):
            raise ValueError("DEC-453 feature/outcome identity mismatch")
    return feature_by_id, outcome_by_id


def _direction_values(
    outcome: OutcomeObservation,
    direction: str,
) -> tuple[float, float]:
    if direction == "LONG":
        return outcome.long_net_pips_0p5, outcome.long_net_pips_1p0
    if direction == "SHORT":
        return outcome.short_net_pips_0p5, outcome.short_net_pips_1p0
    raise ValueError("unsupported DEC-453 market direction")


def _calibrations(
    features: Sequence[FeatureObservation],
) -> tuple[FeatureRankCalibration, ...]:
    result: list[FeatureRankCalibration] = []
    for feature_name in CONTINUOUS_FEATURES:
        values = rank_calibration_values(
            [row.values[feature_name] for row in features]
        )
        if values is None:
            continue
        result.append(
            FeatureRankCalibration(
                feature_name=feature_name,
                values=values,
            )
        )
    return tuple(result)


def _annual_stats(
    *,
    feature_name: str,
    calibration: Sequence[float],
    direction: str,
    polarity: str,
    feature_by_id: Mapping[str, FeatureObservation],
    outcome_by_id: Mapping[str, OutcomeObservation],
) -> tuple[AnnualContinuousEffectStat, ...] | None:
    annual: list[AnnualContinuousEffectStat] = []
    for year in DESIGN_YEARS:
        percentiles: list[float] = []
        half_values: list[float] = []
        tail_half: list[float] = []
        tail_stress: list[float] = []

        for observation_id, outcome in outcome_by_id.items():
            feature = feature_by_id[observation_id]
            if feature.available_at_utc.year != year:
                continue
            percentile = empirical_midrank_percentile(
                calibration,
                feature.values[feature_name],
            )
            if percentile is None:
                continue
            half, stress = _direction_values(outcome, direction)
            percentiles.append(percentile)
            half_values.append(half)
            if selected_tail_accepts(
                percentile=percentile,
                polarity=polarity,
            ):
                tail_half.append(half)
                tail_stress.append(stress)

        if len(percentiles) < 2 or not tail_half:
            return None
        try:
            slope = signed_rank_slope(
                percentiles,
                half_values,
                polarity=polarity,
            )
        except ValueError:
            return None
        annual.append(
            AnnualContinuousEffectStat(
                year=year,
                evaluable_support=len(percentiles),
                selected_tail_support=len(tail_half),
                signed_rank_slope_net_pips_0p5=slope,
                selected_tail_mean_net_pips_0p5=(
                    math.fsum(tail_half) / len(tail_half)
                ),
                selected_tail_mean_net_pips_1p0=(
                    math.fsum(tail_stress) / len(tail_stress)
                ),
            )
        )
    return tuple(annual)


def _candidate(
    *,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
    feature_name: str,
    direction: str,
    polarity: str,
    annual_stats: tuple[AnnualContinuousEffectStat, ...],
) -> ContinuousStabilityHypothesis:
    metrics = continuous_stability_metrics(annual_stats)
    slope_blocks = metrics[
        "two_year_block_signed_rank_slope_net_pips_0p5"
    ]
    tail_blocks = metrics[
        "two_year_block_selected_tail_mean_net_pips_0p5"
    ]
    if not isinstance(slope_blocks, dict) or not isinstance(tail_blocks, dict):
        raise ValueError("DEC-453 two-year-block metric contract drift")

    return ContinuousStabilityHypothesis(
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon_minutes,
        feature_name=feature_name,
        direction=direction,
        polarity=polarity,
        fingerprint=effect_hypothesis_fingerprint(
            symbol=symbol,
            timeframe=timeframe,
            horizon_minutes=horizon_minutes,
            feature_name=feature_name,
            direction=direction,
            polarity=polarity,
        ),
        annual_stats=annual_stats,
        total_selected_tail_support=int(
            metrics["total_selected_tail_support"]
        ),
        minimum_year_selected_tail_support=int(
            metrics["minimum_year_selected_tail_support"]
        ),
        positive_slope_year_count=int(
            metrics["positive_slope_year_count"]
        ),
        positive_tail_mean_year_count=int(
            metrics["positive_tail_mean_year_count"]
        ),
        equal_year_signed_rank_slope_net_pips_0p5=float(
            metrics["equal_year_signed_rank_slope_net_pips_0p5"]
        ),
        lower_half_annual_signed_rank_slope_net_pips_0p5=float(
            metrics[
                "lower_half_annual_signed_rank_slope_net_pips_0p5"
            ]
        ),
        equal_year_selected_tail_mean_net_pips_0p5=float(
            metrics["equal_year_selected_tail_mean_net_pips_0p5"]
        ),
        equal_year_selected_tail_mean_net_pips_1p0=float(
            metrics["equal_year_selected_tail_mean_net_pips_1p0"]
        ),
        lower_half_annual_selected_tail_mean_net_pips_0p5=float(
            metrics[
                "lower_half_annual_selected_tail_mean_net_pips_0p5"
            ]
        ),
        two_year_block_signed_rank_slope_net_pips_0p5=tuple(
            (name, float(value)) for name, value in slope_blocks.items()
        ),
        minimum_two_year_block_signed_rank_slope_net_pips_0p5=float(
            metrics[
                "minimum_two_year_block_signed_rank_slope_net_pips_0p5"
            ]
        ),
        two_year_block_selected_tail_mean_net_pips_0p5=tuple(
            (name, float(value)) for name, value in tail_blocks.items()
        ),
        minimum_two_year_block_selected_tail_mean_net_pips_0p5=float(
            metrics[
                "minimum_two_year_block_selected_tail_mean_net_pips_0p5"
            ]
        ),
    )


def _rank_key(
    candidate: ContinuousStabilityHypothesis,
) -> tuple[object, ...]:
    return (
        -candidate.lower_half_annual_selected_tail_mean_net_pips_0p5,
        -candidate.minimum_two_year_block_selected_tail_mean_net_pips_0p5,
        -candidate.lower_half_annual_signed_rank_slope_net_pips_0p5,
        -candidate.minimum_two_year_block_signed_rank_slope_net_pips_0p5,
        -candidate.positive_tail_mean_year_count,
        -candidate.positive_slope_year_count,
        -candidate.equal_year_selected_tail_mean_net_pips_1p0,
        -candidate.total_selected_tail_support,
        candidate.feature_name,
        candidate.direction,
        candidate.polarity,
        candidate.fingerprint,
    )


def _jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def mine_continuous_stability_shortlist(
    observations: Sequence[FeatureObservation],
    outcomes: Sequence[OutcomeObservation],
    *,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
) -> InMemoryContinuousStabilityResult:
    features = _design_features(
        observations,
        symbol=symbol,
        timeframe=timeframe,
    )
    scoped_outcomes = _design_outcomes(
        outcomes,
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon_minutes,
    )
    feature_by_id, outcome_by_id = _bind_rows(features, scoped_outcomes)
    calibrations = _calibrations(features)
    calibration_by_feature = {
        item.feature_name: item.values for item in calibrations
    }

    candidates: list[ContinuousStabilityHypothesis] = []
    events_by_fingerprint: dict[str, frozenset[str]] = {}
    evaluable_count = 0

    for feature_name in CONTINUOUS_FEATURES:
        calibration = calibration_by_feature.get(feature_name)
        for direction in DIRECTIONS:
            for polarity in POLARITIES:
                if calibration is None:
                    continue
                annual_stats = _annual_stats(
                    feature_name=feature_name,
                    calibration=calibration,
                    direction=direction,
                    polarity=polarity,
                    feature_by_id=feature_by_id,
                    outcome_by_id=outcome_by_id,
                )
                if annual_stats is None:
                    continue
                evaluable_count += 1
                if not continuous_stability_gate_passes(annual_stats):
                    continue
                candidate = _candidate(
                    symbol=symbol,
                    timeframe=timeframe,
                    horizon_minutes=horizon_minutes,
                    feature_name=feature_name,
                    direction=direction,
                    polarity=polarity,
                    annual_stats=annual_stats,
                )
                selected = frozenset(
                    observation_id
                    for observation_id, outcome in outcome_by_id.items()
                    if (
                        (percentile := empirical_midrank_percentile(
                            calibration,
                            feature_by_id[observation_id].values[feature_name],
                        ))
                        is not None
                        and selected_tail_accepts(
                            percentile=percentile,
                            polarity=polarity,
                        )
                    )
                )
                candidates.append(candidate)
                events_by_fingerprint[candidate.fingerprint] = selected

    ranked = sorted(candidates, key=_rank_key)
    deduplicated: list[ContinuousStabilityHypothesis] = []
    accepted_events: list[tuple[str, frozenset[str]]] = []
    for candidate in ranked:
        candidate_events = events_by_fingerprint[candidate.fingerprint]
        duplicate = False
        for direction, prior_events in accepted_events:
            if direction != candidate.direction:
                continue
            if _jaccard(candidate_events, prior_events) >= NEAR_DUPLICATE_JACCARD:
                duplicate = True
                break
        if duplicate:
            continue
        deduplicated.append(candidate)
        accepted_events.append((candidate.direction, candidate_events))

    shortlist = tuple(deduplicated[:MAX_SHORTLIST_PER_CELL_HORIZON])
    frozen = tuple(shortlist[:MAX_FROZEN_PER_CELL_HORIZON])
    report = ContinuousStabilityMiningReport(
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon_minutes,
        active_continuous_features=tuple(
            item.feature_name for item in calibrations
        ),
        hypothesis_count=HYPOTHESES_PER_CELL_HORIZON,
        evaluable_hypothesis_count=evaluable_count,
        qualifying_hypothesis_count=len(candidates),
        deduplicated_hypothesis_count=len(deduplicated),
        shortlist=shortlist,
        frozen=frozen,
    )
    return InMemoryContinuousStabilityResult(
        calibrations=calibrations,
        report=report,
    )


def run_in_memory_continuous_stability_miner(
    observations: Sequence[FeatureObservation],
    outcomes: Sequence[OutcomeObservation],
    *,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
) -> InMemoryContinuousStabilityResult:
    for row in observations:
        _validate_utc(row.available_at_utc, field="feature available_at_utc")
    for row in outcomes:
        _validate_utc(row.available_at_utc, field="outcome available_at_utc")
        _validate_utc(
            row.exit_timestamp_utc,
            field="outcome exit_timestamp_utc",
        )
    return mine_continuous_stability_shortlist(
        observations,
        outcomes,
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon_minutes,
    )


if RANK_FIELDS != (
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
):
    raise ValueError("DEC-453 ranking fields drifted from DEC-452")


__all__ = [
    "BROKER_MUTATION_AUTHORIZED",
    "CANDIDATE_COMPILATION_AUTHORIZED",
    "ContinuousStabilityHypothesis",
    "ContinuousStabilityMiningReport",
    "DEMO_ORDER_AUTHORIZED",
    "EXP064_CONTINUOUS_STABILITY_MINER_DECISION",
    "EXP064_CONTINUOUS_STABILITY_MINER_VERSION",
    "FeatureRankCalibration",
    "HISTORICAL_EXECUTION_AUTHORIZED",
    "HISTORICAL_RESULT_AUTHORIZED",
    "InMemoryContinuousStabilityResult",
    "LIVE_ORDER_AUTHORIZED",
    "PHASE8B_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED",
    "SOURCE_ACCESS_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "mine_continuous_stability_shortlist",
    "run_in_memory_continuous_stability_miner",
]
