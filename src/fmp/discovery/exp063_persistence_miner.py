from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Mapping, Sequence

from .exp063_persistence_protocol import (
    DESIGN_YEARS,
    DESIGN_YEAR_WINDOWS,
    MAX_ADMISSIBLE_PATTERNS_PER_CELL_HORIZON,
    MAX_FROZEN_PER_CELL_HORIZON,
    MAX_PERSISTENCE_SHORTLIST_PER_CELL_HORIZON,
    NEAR_DUPLICATE_JACCARD,
    PERSISTENCE_RANK_FIELDS,
    AnnualPersistenceStat,
    pattern_fingerprint,
    persistence_gate_passes,
    persistence_metrics,
)
from .pattern_miner import (
    FeatureObservation,
    OutcomeObservation,
    StateModel,
    calibrate_state_model,
    encode_state,
    enumerate_patterns,
)
from .pattern_protocol import (
    DIRECTIONS,
    HORIZONS_MINUTES,
    SYMBOLS,
    TIMEFRAMES,
    window_accepts_outcome,
)


EXP063_PERSISTENCE_MINER_DECISION = "DEC-445"
EXP063_PERSISTENCE_MINER_VERSION = "fmp-exp063-persistence-miner-core-v1"

DEC444_MERGE_SHA = "86d16d06444e56a1c6615f18e2906e8ecdaadbdf"
DEC444_PROTOCOL_BLOB_SHA = "2c781dd2811b66d2d88f008007bf5c8bcf99f14f"
BASE_MINER_BLOB_SHA = "495a67699eb5014e52129f0238a2737049fe38e6"

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
class PersistencePatternHypothesis:
    symbol: str
    timeframe: str
    horizon_minutes: int
    direction: str
    predicates: tuple[tuple[str, str], ...]
    fingerprint: str
    annual_stats: tuple[AnnualPersistenceStat, ...]
    total_support: int
    minimum_year_support: int
    aggregate_mean_net_pips_0p5: float
    aggregate_mean_net_pips_1p0: float
    positive_year_count: int
    worst_annual_mean_net_pips_0p5: float
    lower_half_annual_mean_net_pips_0p5: float
    two_year_block_mean_net_pips_0p5: tuple[tuple[str, float], ...]
    minimum_two_year_block_mean_net_pips_0p5: float

    @property
    def depth(self) -> int:
        return len(self.predicates)


@dataclass(frozen=True, slots=True)
class PersistenceMiningReport:
    symbol: str
    timeframe: str
    horizon_minutes: int
    active_continuous_features: tuple[str, ...]
    enumerated_pattern_count: int
    directional_hypothesis_count: int
    qualifying_directional_hypothesis_count: int
    deduplicated_directional_hypothesis_count: int
    shortlist: tuple[PersistencePatternHypothesis, ...]
    frozen: tuple[PersistencePatternHypothesis, ...]
    output_kind: str = (
        "RETROSPECTIVE_PERSISTENCE_PATTERN_HYPOTHESIS_NOT_VALIDATED"
    )


@dataclass(frozen=True, slots=True)
class InMemoryPersistenceResult:
    state_model: StateModel
    report: PersistenceMiningReport


def _validate_utc(value: datetime, *, field: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must use UTC")


def _design_feature_rows(
    observations: Sequence[FeatureObservation],
    *,
    symbol: str,
    timeframe: str,
) -> tuple[FeatureObservation, ...]:
    if symbol not in SYMBOLS or timeframe not in TIMEFRAMES:
        raise ValueError("unsupported EXP-063 persistence cell")

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
        raise ValueError("duplicate EXP-063 feature observation identity")
    return tuple(
        sorted(rows, key=lambda row: (row.available_at_utc, row.observation_id))
    )


def _design_outcome_rows(
    outcomes: Sequence[OutcomeObservation],
    *,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
) -> tuple[OutcomeObservation, ...]:
    if horizon_minutes not in HORIZONS_MINUTES:
        raise ValueError("unsupported EXP-063 persistence horizon")

    rows: list[OutcomeObservation] = []
    for window in DESIGN_YEAR_WINDOWS:
        rows.extend(
            row
            for row in outcomes
            if row.symbol == symbol
            and row.timeframe == timeframe
            and row.horizon_minutes == horizon_minutes
            and window_accepts_outcome(
                window,
                available_at_utc=row.available_at_utc,
                exit_timestamp_utc=row.exit_timestamp_utc,
            )
        )
    ids = [row.observation_id for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate EXP-063 outcome observation identity")
    return tuple(
        sorted(rows, key=lambda row: (row.available_at_utc, row.observation_id))
    )


def _bind_design_rows(
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
            raise ValueError("EXP-063 outcome has no matching feature observation")
        if (
            feature.symbol != outcome.symbol
            or feature.timeframe != outcome.timeframe
            or feature.available_at_utc != outcome.available_at_utc
        ):
            raise ValueError("EXP-063 feature/outcome identity mismatch")
    return feature_by_id, outcome_by_id


def _direction_values(
    outcome: OutcomeObservation,
    direction: str,
) -> tuple[float, float]:
    if direction == "LONG":
        return outcome.long_net_pips_0p5, outcome.long_net_pips_1p0
    if direction == "SHORT":
        return outcome.short_net_pips_0p5, outcome.short_net_pips_1p0
    raise ValueError("unsupported EXP-063 direction")


def _annual_stats(
    *,
    matched_ids: Sequence[str],
    feature_by_id: Mapping[str, FeatureObservation],
    outcome_by_id: Mapping[str, OutcomeObservation],
    direction: str,
) -> tuple[AnnualPersistenceStat, ...]:
    support = {year: 0 for year in DESIGN_YEARS}
    total_half = {year: 0.0 for year in DESIGN_YEARS}
    total_stress = {year: 0.0 for year in DESIGN_YEARS}

    for observation_id in matched_ids:
        feature = feature_by_id[observation_id]
        outcome = outcome_by_id[observation_id]
        year = feature.available_at_utc.year
        if year not in support:
            raise ValueError("EXP-063 design row escaped 2015-2022")
        half, stress = _direction_values(outcome, direction)
        support[year] += 1
        total_half[year] = math.fsum((total_half[year], half))
        total_stress[year] = math.fsum((total_stress[year], stress))

    return tuple(
        AnnualPersistenceStat(
            year=year,
            support=support[year],
            total_net_pips_0p5=total_half[year],
            total_net_pips_1p0=total_stress[year],
        )
        for year in DESIGN_YEARS
    )


def _candidate_from_stats(
    *,
    model: StateModel,
    horizon_minutes: int,
    direction: str,
    predicates: tuple[tuple[str, str], ...],
    annual_stats: tuple[AnnualPersistenceStat, ...],
) -> PersistencePatternHypothesis:
    metrics = persistence_metrics(annual_stats)
    block_means = metrics["two_year_block_mean_net_pips_0p5"]
    if not isinstance(block_means, dict):
        raise ValueError("DEC-445 block-mean metric contract drift")

    return PersistencePatternHypothesis(
        symbol=model.symbol,
        timeframe=model.timeframe,
        horizon_minutes=horizon_minutes,
        direction=direction,
        predicates=predicates,
        fingerprint=pattern_fingerprint(
            symbol=model.symbol,
            timeframe=model.timeframe,
            horizon_minutes=horizon_minutes,
            direction=direction,
            predicates=predicates,
        ),
        annual_stats=annual_stats,
        total_support=int(metrics["total_support"]),
        minimum_year_support=int(metrics["minimum_year_support"]),
        aggregate_mean_net_pips_0p5=float(
            metrics["aggregate_mean_net_pips_0p5"]
        ),
        aggregate_mean_net_pips_1p0=float(
            metrics["aggregate_mean_net_pips_1p0"]
        ),
        positive_year_count=int(metrics["positive_year_count"]),
        worst_annual_mean_net_pips_0p5=float(
            metrics["worst_annual_mean_net_pips_0p5"]
        ),
        lower_half_annual_mean_net_pips_0p5=float(
            metrics["lower_half_annual_mean_net_pips_0p5"]
        ),
        two_year_block_mean_net_pips_0p5=tuple(
            (name, float(value))
            for name, value in block_means.items()
        ),
        minimum_two_year_block_mean_net_pips_0p5=float(
            metrics["minimum_two_year_block_mean_net_pips_0p5"]
        ),
    )


def _rank_key(
    candidate: PersistencePatternHypothesis,
) -> tuple[object, ...]:
    return (
        -candidate.lower_half_annual_mean_net_pips_0p5,
        -candidate.minimum_two_year_block_mean_net_pips_0p5,
        -candidate.positive_year_count,
        -candidate.worst_annual_mean_net_pips_0p5,
        -candidate.aggregate_mean_net_pips_0p5,
        -candidate.aggregate_mean_net_pips_1p0,
        -candidate.total_support,
        candidate.depth,
        candidate.fingerprint,
    )


def _jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def mine_persistence_shortlist(
    observations: Sequence[FeatureObservation],
    outcomes: Sequence[OutcomeObservation],
    *,
    model: StateModel,
    horizon_minutes: int,
) -> PersistenceMiningReport:
    if model.symbol not in SYMBOLS or model.timeframe not in TIMEFRAMES:
        raise ValueError("unsupported EXP-063 state-model cell")
    if horizon_minutes not in HORIZONS_MINUTES:
        raise ValueError("unsupported EXP-063 persistence horizon")

    features = _design_feature_rows(
        observations,
        symbol=model.symbol,
        timeframe=model.timeframe,
    )
    scoped_outcomes = _design_outcome_rows(
        outcomes,
        symbol=model.symbol,
        timeframe=model.timeframe,
        horizon_minutes=horizon_minutes,
    )
    feature_by_id, outcome_by_id = _bind_design_rows(
        features,
        scoped_outcomes,
    )
    state_by_id = {
        row.observation_id: frozenset(encode_state(row, model))
        for row in features
    }
    evaluable_ids = frozenset(outcome_by_id)
    patterns = enumerate_patterns(model)
    if len(patterns) > MAX_ADMISSIBLE_PATTERNS_PER_CELL_HORIZON:
        raise ValueError("DEC-445 pattern enumeration exceeded frozen bound")

    candidates: list[PersistencePatternHypothesis] = []
    events_by_fingerprint: dict[str, frozenset[str]] = {}

    for predicates in patterns:
        required = frozenset(predicates)
        event_ids = frozenset(
            observation_id
            for observation_id, states in state_by_id.items()
            if observation_id in evaluable_ids and required.issubset(states)
        )

        if len(event_ids) < 600:
            continue

        support_by_year = {year: 0 for year in DESIGN_YEARS}
        for observation_id in event_ids:
            year = feature_by_id[observation_id].available_at_utc.year
            if year in support_by_year:
                support_by_year[year] += 1
        if any(support_by_year[year] < 75 for year in DESIGN_YEARS):
            continue

        ordered_ids = tuple(sorted(event_ids))
        for direction in DIRECTIONS:
            annual_stats = _annual_stats(
                matched_ids=ordered_ids,
                feature_by_id=feature_by_id,
                outcome_by_id=outcome_by_id,
                direction=direction,
            )
            if not persistence_gate_passes(annual_stats):
                continue
            candidate = _candidate_from_stats(
                model=model,
                horizon_minutes=horizon_minutes,
                direction=direction,
                predicates=tuple(predicates),
                annual_stats=annual_stats,
            )
            candidates.append(candidate)
            events_by_fingerprint[candidate.fingerprint] = event_ids

    ranked = sorted(candidates, key=_rank_key)
    deduplicated: list[PersistencePatternHypothesis] = []
    accepted_events: list[tuple[str, frozenset[str]]] = []

    for candidate in ranked:
        events = events_by_fingerprint[candidate.fingerprint]
        duplicate = False
        for direction, prior_events in accepted_events:
            if direction != candidate.direction:
                continue
            if _jaccard(events, prior_events) >= NEAR_DUPLICATE_JACCARD:
                duplicate = True
                break
        if duplicate:
            continue
        deduplicated.append(candidate)
        accepted_events.append((candidate.direction, events))

    shortlist = tuple(
        deduplicated[:MAX_PERSISTENCE_SHORTLIST_PER_CELL_HORIZON]
    )
    frozen = shortlist[:MAX_FROZEN_PER_CELL_HORIZON]
    return PersistenceMiningReport(
        symbol=model.symbol,
        timeframe=model.timeframe,
        horizon_minutes=horizon_minutes,
        active_continuous_features=model.active_continuous_features,
        enumerated_pattern_count=len(patterns),
        directional_hypothesis_count=len(patterns) * len(DIRECTIONS),
        qualifying_directional_hypothesis_count=len(candidates),
        deduplicated_directional_hypothesis_count=len(deduplicated),
        shortlist=shortlist,
        frozen=frozen,
    )


def run_in_memory_persistence_miner(
    observations: Sequence[FeatureObservation],
    outcomes: Sequence[OutcomeObservation],
    *,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
) -> InMemoryPersistenceResult:
    for row in observations:
        _validate_utc(row.available_at_utc, field="available_at_utc")
    for row in outcomes:
        _validate_utc(row.available_at_utc, field="available_at_utc")
        _validate_utc(row.exit_timestamp_utc, field="exit_timestamp_utc")

    model = calibrate_state_model(
        observations,
        symbol=symbol,
        timeframe=timeframe,
    )
    report = mine_persistence_shortlist(
        observations,
        outcomes,
        model=model,
        horizon_minutes=horizon_minutes,
    )
    return InMemoryPersistenceResult(
        state_model=model,
        report=report,
    )


if PERSISTENCE_RANK_FIELDS != (
    "lower_half_annual_mean_net_pips_0p5_desc",
    "minimum_two_year_block_mean_net_pips_0p5_desc",
    "positive_year_count_desc",
    "worst_annual_mean_net_pips_0p5_desc",
    "aggregate_mean_net_pips_0p5_desc",
    "aggregate_mean_net_pips_1p0_desc",
    "total_support_desc",
    "pattern_depth_asc",
    "pattern_fingerprint_asc",
):
    raise ValueError("DEC-445 persistence ranking contract drift")


__all__ = [
    "BASE_MINER_BLOB_SHA",
    "BROKER_MUTATION_AUTHORIZED",
    "CANDIDATE_COMPILATION_AUTHORIZED",
    "DEC444_MERGE_SHA",
    "DEC444_PROTOCOL_BLOB_SHA",
    "DEMO_ORDER_AUTHORIZED",
    "EXP063_PERSISTENCE_MINER_DECISION",
    "EXP063_PERSISTENCE_MINER_VERSION",
    "HISTORICAL_EXECUTION_AUTHORIZED",
    "HISTORICAL_RESULT_AUTHORIZED",
    "InMemoryPersistenceResult",
    "LIVE_ORDER_AUTHORIZED",
    "PHASE8B_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "PersistenceMiningReport",
    "PersistencePatternHypothesis",
    "REAL_MONEY_AUTHORIZED",
    "RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED",
    "SOURCE_ACCESS_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "mine_persistence_shortlist",
    "run_in_memory_persistence_miner",
]
