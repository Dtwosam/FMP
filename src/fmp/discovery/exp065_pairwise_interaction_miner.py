from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Mapping, Sequence

from .exp064_continuous_stability_protocol import (
    empirical_midrank_percentile,
    rank_calibration_values,
)
from .exp065_pairwise_interaction_protocol import (
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
    AnnualPairwiseInteractionStat,
    canonical_feature_pair,
    feature_pairs,
    interaction_calibration_values,
    interaction_percentile,
    main_effect_residuals,
    pair_hypothesis_fingerprint,
    pairwise_interaction_gate_passes,
    pairwise_interaction_metrics,
    pairwise_interaction_raw,
    partial_interaction_slope,
    selected_tail_accepts,
)
from .pattern_miner import FeatureObservation, OutcomeObservation
from .pattern_protocol import CONTINUOUS_FEATURES


EXP065_PAIRWISE_INTERACTION_MINER_DECISION = "DEC-462"
EXP065_PAIRWISE_INTERACTION_MINER_VERSION = (
    "fmp-exp065-pairwise-interaction-miner-core-v1"
)

DEC461_MERGE_SHA = "2a8127b505c9b0d9e1adb562bd18a5cafc171df6"
DEC461_PROTOCOL_BLOB_SHA = "b54267d790667659749a96123ad23a491ff50dfa"
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
            raise ValueError("DEC-462 unsupported feature calibration")
        if not self.values:
            raise ValueError("DEC-462 feature calibration cannot be empty")
        if tuple(sorted(self.values)) != self.values:
            raise ValueError("DEC-462 feature calibration must be sorted")
        if any(not math.isfinite(value) for value in self.values):
            raise ValueError("DEC-462 feature calibration must be finite")


@dataclass(frozen=True, slots=True)
class PairInteractionCalibration:
    feature_a: str
    feature_b: str
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        pair = canonical_feature_pair(self.feature_a, self.feature_b)
        if pair != (self.feature_a, self.feature_b):
            raise ValueError("DEC-462 pair calibration must use canonical order")
        if not self.values:
            raise ValueError("DEC-462 pair calibration cannot be empty")
        if tuple(sorted(self.values)) != self.values:
            raise ValueError("DEC-462 pair calibration must be sorted")
        if any(not math.isfinite(value) for value in self.values):
            raise ValueError("DEC-462 pair calibration must be finite")


@dataclass(frozen=True, slots=True)
class PairwiseInteractionHypothesis:
    symbol: str
    timeframe: str
    horizon_minutes: int
    feature_a: str
    feature_b: str
    direction: str
    polarity: str
    fingerprint: str
    annual_stats: tuple[AnnualPairwiseInteractionStat, ...]
    total_selected_tail_support: int
    minimum_year_selected_tail_support: int
    positive_partial_slope_year_count: int
    positive_raw_tail_mean_year_count: int
    positive_incremental_tail_mean_year_count: int
    equal_year_signed_partial_slope_net_pips_0p5: float
    equal_year_raw_tail_mean_net_pips_0p5: float
    equal_year_incremental_tail_mean_net_pips_0p5: float
    equal_year_raw_tail_mean_net_pips_1p0: float
    lower_half_signed_partial_slope_net_pips_0p5: float
    lower_half_raw_tail_mean_net_pips_0p5: float
    lower_half_incremental_tail_mean_net_pips_0p5: float
    two_year_block_signed_partial_slope_net_pips_0p5: tuple[
        tuple[str, float], ...
    ]
    minimum_two_year_block_signed_partial_slope_net_pips_0p5: float
    two_year_block_raw_tail_mean_net_pips_0p5: tuple[tuple[str, float], ...]
    minimum_two_year_block_raw_tail_mean_net_pips_0p5: float
    two_year_block_incremental_tail_mean_net_pips_0p5: tuple[
        tuple[str, float], ...
    ]
    minimum_two_year_block_incremental_tail_mean_net_pips_0p5: float


@dataclass(frozen=True, slots=True)
class PairwiseInteractionMiningReport:
    symbol: str
    timeframe: str
    horizon_minutes: int
    active_continuous_features: tuple[str, ...]
    active_feature_pairs: tuple[tuple[str, str], ...]
    hypothesis_count: int
    evaluable_hypothesis_count: int
    qualifying_hypothesis_count: int
    deduplicated_hypothesis_count: int
    shortlist: tuple[PairwiseInteractionHypothesis, ...]
    frozen: tuple[PairwiseInteractionHypothesis, ...]
    output_kind: str = OUTPUT_KIND


@dataclass(frozen=True, slots=True)
class InMemoryPairwiseInteractionResult:
    feature_calibrations: tuple[FeatureRankCalibration, ...]
    pair_calibrations: tuple[PairInteractionCalibration, ...]
    report: PairwiseInteractionMiningReport


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
        raise ValueError("unsupported DEC-462 EXP-065 feature cell")
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
        raise ValueError("duplicate DEC-462 feature observation identity")
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
        raise ValueError("unsupported DEC-462 EXP-065 horizon")
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
        raise ValueError("duplicate DEC-462 outcome observation identity")
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
            raise ValueError("DEC-462 outcome has no matching feature observation")
        if (
            feature.symbol != outcome.symbol
            or feature.timeframe != outcome.timeframe
            or feature.available_at_utc != outcome.available_at_utc
        ):
            raise ValueError("DEC-462 feature/outcome identity mismatch")
    return feature_by_id, outcome_by_id


def _direction_values(
    outcome: OutcomeObservation,
    direction: str,
) -> tuple[float, float]:
    if direction == "LONG":
        return outcome.long_net_pips_0p5, outcome.long_net_pips_1p0
    if direction == "SHORT":
        return outcome.short_net_pips_0p5, outcome.short_net_pips_1p0
    raise ValueError("unsupported DEC-462 market direction")


def _polarity_sign(polarity: str) -> int:
    if polarity == "INCREASING":
        return 1
    if polarity == "DECREASING":
        return -1
    raise ValueError("unsupported DEC-462 interaction polarity")


def _feature_calibrations(
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


def _pair_calibrations(
    features: Sequence[FeatureObservation],
    *,
    feature_calibration_by_name: Mapping[str, Sequence[float]],
) -> tuple[PairInteractionCalibration, ...]:
    result: list[PairInteractionCalibration] = []
    for feature_a, feature_b in feature_pairs():
        calibration_a = feature_calibration_by_name.get(feature_a)
        calibration_b = feature_calibration_by_name.get(feature_b)
        if calibration_a is None or calibration_b is None:
            continue

        percentiles_a: list[float] = []
        percentiles_b: list[float] = []
        for row in features:
            percentile_a = empirical_midrank_percentile(
                calibration_a,
                row.values[feature_a],
            )
            percentile_b = empirical_midrank_percentile(
                calibration_b,
                row.values[feature_b],
            )
            if percentile_a is None or percentile_b is None:
                continue
            percentiles_a.append(percentile_a)
            percentiles_b.append(percentile_b)

        try:
            values = interaction_calibration_values(
                percentiles_a,
                percentiles_b,
            )
        except ValueError:
            continue

        result.append(
            PairInteractionCalibration(
                feature_a=feature_a,
                feature_b=feature_b,
                values=values,
            )
        )
    return tuple(result)


def _annual_stats(
    *,
    feature_a: str,
    feature_b: str,
    feature_calibration_a: Sequence[float],
    feature_calibration_b: Sequence[float],
    interaction_calibration: Sequence[float],
    direction: str,
    polarity: str,
    feature_by_id: Mapping[str, FeatureObservation],
    outcome_by_id: Mapping[str, OutcomeObservation],
) -> tuple[AnnualPairwiseInteractionStat, ...] | None:
    annual: list[AnnualPairwiseInteractionStat] = []
    sign = _polarity_sign(polarity)

    for year in DESIGN_YEARS:
        percentiles_a: list[float] = []
        percentiles_b: list[float] = []
        interaction_percentiles: list[float] = []
        half_values: list[float] = []
        stress_values: list[float] = []

        for observation_id, outcome in outcome_by_id.items():
            feature = feature_by_id[observation_id]
            if feature.available_at_utc.year != year:
                continue

            percentile_a = empirical_midrank_percentile(
                feature_calibration_a,
                feature.values[feature_a],
            )
            percentile_b = empirical_midrank_percentile(
                feature_calibration_b,
                feature.values[feature_b],
            )
            if percentile_a is None or percentile_b is None:
                continue

            raw_interaction = pairwise_interaction_raw(
                percentile_a,
                percentile_b,
            )
            try:
                pair_percentile = interaction_percentile(
                    raw_interaction,
                    interaction_calibration,
                )
            except ValueError:
                continue

            half, stress = _direction_values(outcome, direction)
            percentiles_a.append(percentile_a)
            percentiles_b.append(percentile_b)
            interaction_percentiles.append(pair_percentile)
            half_values.append(half)
            stress_values.append(stress)

        if len(interaction_percentiles) < 4:
            return None

        try:
            signed_partial_slope = sign * partial_interaction_slope(
                percentiles_a,
                percentiles_b,
                interaction_percentiles,
                half_values,
            )
            residuals = main_effect_residuals(
                percentiles_a,
                percentiles_b,
                half_values,
            )
        except ValueError:
            return None

        selected_indices = [
            index
            for index, percentile in enumerate(interaction_percentiles)
            if selected_tail_accepts(
                interaction_percentile_value=percentile,
                polarity=polarity,
            )
        ]
        if not selected_indices:
            return None

        tail_half = [half_values[index] for index in selected_indices]
        tail_stress = [stress_values[index] for index in selected_indices]
        tail_incremental = [residuals[index] for index in selected_indices]

        annual.append(
            AnnualPairwiseInteractionStat(
                year=year,
                evaluable_support=len(interaction_percentiles),
                selected_tail_support=len(selected_indices),
                signed_partial_interaction_slope_net_pips_0p5=(
                    signed_partial_slope
                ),
                selected_tail_mean_net_pips_0p5=(
                    math.fsum(tail_half) / len(tail_half)
                ),
                selected_tail_incremental_residual_mean_net_pips_0p5=(
                    math.fsum(tail_incremental) / len(tail_incremental)
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
    feature_a: str,
    feature_b: str,
    direction: str,
    polarity: str,
    annual_stats: tuple[AnnualPairwiseInteractionStat, ...],
) -> PairwiseInteractionHypothesis:
    metrics = pairwise_interaction_metrics(annual_stats)
    partial_blocks = metrics[
        "two_year_block_signed_partial_slope_net_pips_0p5"
    ]
    raw_blocks = metrics["two_year_block_raw_tail_mean_net_pips_0p5"]
    incremental_blocks = metrics[
        "two_year_block_incremental_tail_mean_net_pips_0p5"
    ]
    if not all(
        isinstance(value, dict)
        for value in (partial_blocks, raw_blocks, incremental_blocks)
    ):
        raise ValueError("DEC-462 two-year-block metric contract drift")

    return PairwiseInteractionHypothesis(
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon_minutes,
        feature_a=feature_a,
        feature_b=feature_b,
        direction=direction,
        polarity=polarity,
        fingerprint=pair_hypothesis_fingerprint(
            symbol=symbol,
            timeframe=timeframe,
            horizon_minutes=horizon_minutes,
            feature_a=feature_a,
            feature_b=feature_b,
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
        positive_partial_slope_year_count=int(
            metrics["positive_partial_slope_year_count"]
        ),
        positive_raw_tail_mean_year_count=int(
            metrics["positive_raw_tail_mean_year_count"]
        ),
        positive_incremental_tail_mean_year_count=int(
            metrics["positive_incremental_tail_mean_year_count"]
        ),
        equal_year_signed_partial_slope_net_pips_0p5=float(
            metrics["equal_year_signed_partial_slope_net_pips_0p5"]
        ),
        equal_year_raw_tail_mean_net_pips_0p5=float(
            metrics["equal_year_raw_tail_mean_net_pips_0p5"]
        ),
        equal_year_incremental_tail_mean_net_pips_0p5=float(
            metrics["equal_year_incremental_tail_mean_net_pips_0p5"]
        ),
        equal_year_raw_tail_mean_net_pips_1p0=float(
            metrics["equal_year_raw_tail_mean_net_pips_1p0"]
        ),
        lower_half_signed_partial_slope_net_pips_0p5=float(
            metrics["lower_half_signed_partial_slope_net_pips_0p5"]
        ),
        lower_half_raw_tail_mean_net_pips_0p5=float(
            metrics["lower_half_raw_tail_mean_net_pips_0p5"]
        ),
        lower_half_incremental_tail_mean_net_pips_0p5=float(
            metrics["lower_half_incremental_tail_mean_net_pips_0p5"]
        ),
        two_year_block_signed_partial_slope_net_pips_0p5=tuple(
            (name, float(value)) for name, value in partial_blocks.items()
        ),
        minimum_two_year_block_signed_partial_slope_net_pips_0p5=float(
            metrics[
                "minimum_two_year_block_signed_partial_slope_net_pips_0p5"
            ]
        ),
        two_year_block_raw_tail_mean_net_pips_0p5=tuple(
            (name, float(value)) for name, value in raw_blocks.items()
        ),
        minimum_two_year_block_raw_tail_mean_net_pips_0p5=float(
            metrics["minimum_two_year_block_raw_tail_mean_net_pips_0p5"]
        ),
        two_year_block_incremental_tail_mean_net_pips_0p5=tuple(
            (name, float(value)) for name, value in incremental_blocks.items()
        ),
        minimum_two_year_block_incremental_tail_mean_net_pips_0p5=float(
            metrics[
                "minimum_two_year_block_incremental_tail_mean_net_pips_0p5"
            ]
        ),
    )


def _rank_key(
    candidate: PairwiseInteractionHypothesis,
) -> tuple[object, ...]:
    return (
        -candidate.lower_half_incremental_tail_mean_net_pips_0p5,
        -candidate.minimum_two_year_block_incremental_tail_mean_net_pips_0p5,
        -candidate.lower_half_raw_tail_mean_net_pips_0p5,
        -candidate.minimum_two_year_block_raw_tail_mean_net_pips_0p5,
        -candidate.lower_half_signed_partial_slope_net_pips_0p5,
        -candidate.minimum_two_year_block_signed_partial_slope_net_pips_0p5,
        -candidate.positive_incremental_tail_mean_year_count,
        -candidate.positive_raw_tail_mean_year_count,
        -candidate.positive_partial_slope_year_count,
        -candidate.equal_year_raw_tail_mean_net_pips_1p0,
        -candidate.total_selected_tail_support,
        candidate.feature_a,
        candidate.feature_b,
        candidate.direction,
        candidate.polarity,
    )


def _jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def _selected_event_ids(
    *,
    feature_a: str,
    feature_b: str,
    feature_calibration_a: Sequence[float],
    feature_calibration_b: Sequence[float],
    interaction_calibration: Sequence[float],
    polarity: str,
    feature_by_id: Mapping[str, FeatureObservation],
    outcome_by_id: Mapping[str, OutcomeObservation],
) -> frozenset[str]:
    selected: set[str] = set()
    for observation_id in outcome_by_id:
        feature = feature_by_id[observation_id]
        percentile_a = empirical_midrank_percentile(
            feature_calibration_a,
            feature.values[feature_a],
        )
        percentile_b = empirical_midrank_percentile(
            feature_calibration_b,
            feature.values[feature_b],
        )
        if percentile_a is None or percentile_b is None:
            continue
        raw_interaction = pairwise_interaction_raw(
            percentile_a,
            percentile_b,
        )
        try:
            pair_percentile = interaction_percentile(
                raw_interaction,
                interaction_calibration,
            )
        except ValueError:
            continue
        if selected_tail_accepts(
            interaction_percentile_value=pair_percentile,
            polarity=polarity,
        ):
            selected.add(observation_id)
    return frozenset(selected)


def mine_pairwise_interaction_shortlist(
    observations: Sequence[FeatureObservation],
    outcomes: Sequence[OutcomeObservation],
    *,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
) -> InMemoryPairwiseInteractionResult:
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

    feature_calibrations = _feature_calibrations(features)
    feature_calibration_by_name = {
        item.feature_name: item.values for item in feature_calibrations
    }
    pair_calibrations = _pair_calibrations(
        features,
        feature_calibration_by_name=feature_calibration_by_name,
    )
    pair_calibration_by_pair = {
        (item.feature_a, item.feature_b): item.values
        for item in pair_calibrations
    }

    candidates: list[PairwiseInteractionHypothesis] = []
    events_by_fingerprint: dict[str, frozenset[str]] = {}
    evaluable_count = 0

    for feature_a, feature_b in feature_pairs():
        interaction_calibration = pair_calibration_by_pair.get(
            (feature_a, feature_b)
        )
        feature_calibration_a = feature_calibration_by_name.get(feature_a)
        feature_calibration_b = feature_calibration_by_name.get(feature_b)
        if (
            interaction_calibration is None
            or feature_calibration_a is None
            or feature_calibration_b is None
        ):
            continue

        for direction in DIRECTIONS:
            for polarity in POLARITIES:
                annual_stats = _annual_stats(
                    feature_a=feature_a,
                    feature_b=feature_b,
                    feature_calibration_a=feature_calibration_a,
                    feature_calibration_b=feature_calibration_b,
                    interaction_calibration=interaction_calibration,
                    direction=direction,
                    polarity=polarity,
                    feature_by_id=feature_by_id,
                    outcome_by_id=outcome_by_id,
                )
                if annual_stats is None:
                    continue

                evaluable_count += 1
                if not pairwise_interaction_gate_passes(annual_stats):
                    continue

                candidate = _candidate(
                    symbol=symbol,
                    timeframe=timeframe,
                    horizon_minutes=horizon_minutes,
                    feature_a=feature_a,
                    feature_b=feature_b,
                    direction=direction,
                    polarity=polarity,
                    annual_stats=annual_stats,
                )
                candidates.append(candidate)
                events_by_fingerprint[candidate.fingerprint] = _selected_event_ids(
                    feature_a=feature_a,
                    feature_b=feature_b,
                    feature_calibration_a=feature_calibration_a,
                    feature_calibration_b=feature_calibration_b,
                    interaction_calibration=interaction_calibration,
                    polarity=polarity,
                    feature_by_id=feature_by_id,
                    outcome_by_id=outcome_by_id,
                )

    ranked = sorted(candidates, key=_rank_key)
    deduplicated: list[PairwiseInteractionHypothesis] = []
    accepted_events: list[frozenset[str]] = []
    for candidate in ranked:
        candidate_events = events_by_fingerprint[candidate.fingerprint]
        if any(
            _jaccard(candidate_events, prior_events) >= NEAR_DUPLICATE_JACCARD
            for prior_events in accepted_events
        ):
            continue
        deduplicated.append(candidate)
        accepted_events.append(candidate_events)

    shortlist = tuple(deduplicated[:MAX_SHORTLIST_PER_CELL_HORIZON])
    frozen = tuple(shortlist[:MAX_FROZEN_PER_CELL_HORIZON])
    report = PairwiseInteractionMiningReport(
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon_minutes,
        active_continuous_features=tuple(
            item.feature_name for item in feature_calibrations
        ),
        active_feature_pairs=tuple(
            (item.feature_a, item.feature_b) for item in pair_calibrations
        ),
        hypothesis_count=HYPOTHESES_PER_CELL_HORIZON,
        evaluable_hypothesis_count=evaluable_count,
        qualifying_hypothesis_count=len(candidates),
        deduplicated_hypothesis_count=len(deduplicated),
        shortlist=shortlist,
        frozen=frozen,
    )
    return InMemoryPairwiseInteractionResult(
        feature_calibrations=feature_calibrations,
        pair_calibrations=pair_calibrations,
        report=report,
    )


def run_in_memory_pairwise_interaction_miner(
    observations: Sequence[FeatureObservation],
    outcomes: Sequence[OutcomeObservation],
    *,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
) -> InMemoryPairwiseInteractionResult:
    for row in observations:
        _validate_utc(row.available_at_utc, field="feature available_at_utc")
    for row in outcomes:
        _validate_utc(row.available_at_utc, field="outcome available_at_utc")
        _validate_utc(
            row.exit_timestamp_utc,
            field="outcome exit_timestamp_utc",
        )
    return mine_pairwise_interaction_shortlist(
        observations,
        outcomes,
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon_minutes,
    )


if RANK_FIELDS != (
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
):
    raise ValueError("DEC-462 ranking fields drifted from repaired DEC-461 protocol")


__all__ = [
    "BASE_OBSERVATION_MODEL_BLOB_SHA",
    "BROKER_MUTATION_AUTHORIZED",
    "CANDIDATE_COMPILATION_AUTHORIZED",
    "DEC461_MERGE_SHA",
    "DEC461_PROTOCOL_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "EXP065_PAIRWISE_INTERACTION_MINER_DECISION",
    "EXP065_PAIRWISE_INTERACTION_MINER_VERSION",
    "FeatureRankCalibration",
    "HISTORICAL_EXECUTION_AUTHORIZED",
    "HISTORICAL_RESULT_AUTHORIZED",
    "InMemoryPairwiseInteractionResult",
    "LIVE_ORDER_AUTHORIZED",
    "PHASE8B_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "PairInteractionCalibration",
    "PairwiseInteractionHypothesis",
    "PairwiseInteractionMiningReport",
    "REAL_MONEY_AUTHORIZED",
    "RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED",
    "SOURCE_ACCESS_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "mine_pairwise_interaction_shortlist",
    "run_in_memory_pairwise_interaction_miner",
]
