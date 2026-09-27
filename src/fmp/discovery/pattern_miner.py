from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Mapping, Sequence

from .pattern_protocol import (
    CONFIRMATION_MIN_SUPPORT,
    CONFIRMATION_WINDOW,
    CONTINUOUS_FEATURES,
    DIRECTIONS,
    DISCOVERY_RANK_FIELDS,
    DISCOVERY_SLIPPAGE_PIPS,
    DISCOVERY_WINDOW,
    HORIZONS_MINUTES,
    MAX_ADMISSIBLE_PATTERNS_PER_CELL_HORIZON,
    MAX_DISCOVERY_SHORTLIST_PER_CELL_HORIZON,
    MAX_FROZEN_PER_CELL_HORIZON,
    MIN_DISCOVERY_AGGREGATE_MEAN_NET_PIPS,
    MIN_DISCOVERY_TOTAL_SUPPORT,
    MIN_DISCOVERY_YEAR_SUPPORT,
    NEAR_DUPLICATE_JACCARD,
    QUANTILE_STATES,
    SESSION_DIMENSION,
    SESSION_STATES,
    STRESS_SLIPPAGE_PIPS,
    SYMBOLS,
    TIMEFRAMES,
    VALIDATION_MIN_POSITIVE_YEARS,
    VALIDATION_MIN_TOTAL_SUPPORT,
    VALIDATION_MIN_YEAR_SUPPORT,
    VALIDATION_WINDOW,
    empirical_tertile_cutpoints,
    pattern_fingerprint,
    quantile_state,
    session_state,
)


EXP061_MINER_CORE_DECISION = "DEC-271"
EXP061_MINER_CORE_VERSION = "fmp-exp061-in-memory-pattern-miner-v1"

HISTORICAL_SOURCE_ACCESS_AUTHORIZED = False
HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False

_SESSION_FLAG_COLUMNS = (
    "is_london_new_york_overlap",
    "is_london_session",
    "is_new_york_session",
    "is_asia_session",
)


def _validate_utc(value: datetime, *, field: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{field} must use UTC")


def _finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


@dataclass(frozen=True, slots=True)
class FeatureObservation:
    observation_id: str
    symbol: str
    timeframe: str
    available_at_utc: datetime
    values: Mapping[str, object]

    def __post_init__(self) -> None:
        if not self.observation_id.strip():
            raise ValueError("feature observation id must be non-empty")
        if self.symbol not in SYMBOLS:
            raise ValueError("unsupported EXP-061 feature symbol")
        if self.timeframe not in TIMEFRAMES:
            raise ValueError("unsupported EXP-061 feature timeframe")
        _validate_utc(self.available_at_utc, field="available_at_utc")

        copied = dict(self.values)
        missing = set(CONTINUOUS_FEATURES).difference(copied)
        missing.update(set(_SESSION_FLAG_COLUMNS).difference(copied))
        if missing:
            raise ValueError(
                f"EXP-061 feature observation missing required values: {sorted(missing)!r}"
            )
        for name in CONTINUOUS_FEATURES:
            value = copied[name]
            if value is not None and not _finite_number(value):
                raise ValueError(f"EXP-061 continuous feature {name} must be finite or null")
        for name in _SESSION_FLAG_COLUMNS:
            if not isinstance(copied[name], bool):
                raise ValueError(f"EXP-061 session flag {name} must be boolean")
        object.__setattr__(self, "values", MappingProxyType(copied))


@dataclass(frozen=True, slots=True)
class OutcomeObservation:
    observation_id: str
    symbol: str
    timeframe: str
    available_at_utc: datetime
    horizon_minutes: int
    long_net_pips_0p5: float
    short_net_pips_0p5: float
    long_net_pips_1p0: float
    short_net_pips_1p0: float

    def __post_init__(self) -> None:
        if not self.observation_id.strip():
            raise ValueError("outcome observation id must be non-empty")
        if self.symbol not in SYMBOLS:
            raise ValueError("unsupported EXP-061 outcome symbol")
        if self.timeframe not in TIMEFRAMES:
            raise ValueError("unsupported EXP-061 outcome timeframe")
        if self.horizon_minutes not in HORIZONS_MINUTES:
            raise ValueError("unsupported EXP-061 outcome horizon")
        _validate_utc(self.available_at_utc, field="available_at_utc")
        for name in (
            "long_net_pips_0p5",
            "short_net_pips_0p5",
            "long_net_pips_1p0",
            "short_net_pips_1p0",
        ):
            if not _finite_number(getattr(self, name)):
                raise ValueError(f"{name} must be finite")


@dataclass(frozen=True, slots=True)
class StateModel:
    symbol: str
    timeframe: str
    cutpoints: tuple[tuple[str, float, float], ...]

    @property
    def active_continuous_features(self) -> tuple[str, ...]:
        return tuple(name for name, _, _ in self.cutpoints)


@dataclass(frozen=True, slots=True)
class PatternStatistics:
    total_support: int
    year_support: tuple[tuple[int, int], ...]
    aggregate_mean_net_pips_0p5: float
    year_mean_net_pips_0p5: tuple[tuple[int, float], ...]
    aggregate_mean_net_pips_1p0: float


@dataclass(frozen=True, slots=True)
class PatternHypothesis:
    symbol: str
    timeframe: str
    horizon_minutes: int
    direction: str
    predicates: tuple[tuple[str, str], ...]
    fingerprint: str
    discovery_statistics: PatternStatistics

    @property
    def depth(self) -> int:
        return len(self.predicates)


@dataclass(frozen=True, slots=True)
class DiscoveryReport:
    symbol: str
    timeframe: str
    horizon_minutes: int
    active_continuous_features: tuple[str, ...]
    enumerated_pattern_count: int
    directional_hypothesis_count: int
    qualifying_directional_hypothesis_count: int
    deduplicated_directional_hypothesis_count: int
    shortlist: tuple[PatternHypothesis, ...]


@dataclass(frozen=True, slots=True)
class ConfirmationEvaluation:
    hypothesis: PatternHypothesis
    support: int
    mean_net_pips_0p5: float | None
    passed: bool


@dataclass(frozen=True, slots=True)
class FrozenPatternHypothesis:
    hypothesis: PatternHypothesis
    confirmation_support: int
    confirmation_mean_net_pips_0p5: float


@dataclass(frozen=True, slots=True)
class ConfirmationReport:
    evaluations: tuple[ConfirmationEvaluation, ...]
    frozen: tuple[FrozenPatternHypothesis, ...]


@dataclass(frozen=True, slots=True)
class ValidationEvaluation:
    frozen: FrozenPatternHypothesis
    total_support: int
    year_support: tuple[tuple[int, int], ...]
    aggregate_mean_net_pips_0p5: float | None
    year_mean_net_pips_0p5: tuple[tuple[int, float | None], ...]
    positive_year_count: int
    passed: bool


@dataclass(frozen=True, slots=True)
class ValidationReport:
    evaluations: tuple[ValidationEvaluation, ...]
    validated: tuple[FrozenPatternHypothesis, ...]


@dataclass(frozen=True, slots=True)
class InMemoryDiscoveryResult:
    state_model: StateModel
    discovery: DiscoveryReport
    confirmation: ConfirmationReport
    validation: ValidationReport


def _window_contains(window: object, value: datetime) -> bool:
    start = datetime.combine(window.start, datetime.min.time(), tzinfo=timezone.utc)
    end = datetime.combine(window.end_exclusive, datetime.min.time(), tzinfo=timezone.utc)
    return start <= value < end


def _scoped_features(
    observations: Sequence[FeatureObservation],
    *,
    symbol: str,
    timeframe: str,
    window: object,
) -> tuple[FeatureObservation, ...]:
    scoped = tuple(
        row
        for row in observations
        if row.symbol == symbol
        and row.timeframe == timeframe
        and _window_contains(window, row.available_at_utc)
    )
    ids = [row.observation_id for row in scoped]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate EXP-061 feature observation identity")
    return tuple(sorted(scoped, key=lambda row: (row.available_at_utc, row.observation_id)))


def _scoped_outcomes(
    outcomes: Sequence[OutcomeObservation],
    *,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
    window: object,
) -> tuple[OutcomeObservation, ...]:
    scoped = tuple(
        row
        for row in outcomes
        if row.symbol == symbol
        and row.timeframe == timeframe
        and row.horizon_minutes == horizon_minutes
        and _window_contains(window, row.available_at_utc)
    )
    ids = [row.observation_id for row in scoped]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate EXP-061 outcome observation identity")
    return tuple(sorted(scoped, key=lambda row: (row.available_at_utc, row.observation_id)))


def calibrate_state_model(
    observations: Sequence[FeatureObservation],
    *,
    symbol: str,
    timeframe: str,
) -> StateModel:
    if symbol not in SYMBOLS or timeframe not in TIMEFRAMES:
        raise ValueError("unsupported EXP-061 state-model cell")
    discovery = _scoped_features(
        observations,
        symbol=symbol,
        timeframe=timeframe,
        window=DISCOVERY_WINDOW,
    )
    if not discovery:
        raise ValueError("EXP-061 state calibration has no discovery observations")

    cutpoints: list[tuple[str, float, float]] = []
    for name in CONTINUOUS_FEATURES:
        cuts = empirical_tertile_cutpoints([row.values[name] for row in discovery])
        if cuts is not None:
            cutpoints.append((name, cuts[0], cuts[1]))
    return StateModel(
        symbol=symbol,
        timeframe=timeframe,
        cutpoints=tuple(cutpoints),
    )


def _cutpoint_map(model: StateModel) -> dict[str, tuple[float, float]]:
    return {name: (lower, upper) for name, lower, upper in model.cutpoints}


def encode_state(
    observation: FeatureObservation,
    model: StateModel,
) -> tuple[tuple[str, str], ...]:
    if observation.symbol != model.symbol or observation.timeframe != model.timeframe:
        raise ValueError("EXP-061 state model and feature observation cell mismatch")
    cuts = _cutpoint_map(model)
    states: list[tuple[str, str]] = []
    for name in CONTINUOUS_FEATURES:
        if name not in cuts:
            continue
        state = quantile_state(observation.values[name], cuts[name])
        if state is not None:
            states.append((name, state))
    states.append((SESSION_DIMENSION, session_state(observation.values)))
    return tuple(states)


def enumerate_patterns(
    model: StateModel,
) -> tuple[tuple[tuple[str, str], ...], ...]:
    dimensions: list[tuple[str, tuple[str, ...]]] = [
        (name, QUANTILE_STATES)
        for name in model.active_continuous_features
    ]
    dimensions.append((SESSION_DIMENSION, SESSION_STATES))

    patterns: list[tuple[tuple[str, str], ...]] = []
    for name, states in dimensions:
        for state in states:
            patterns.append(((name, state),))

    for left_index, (left_name, left_states) in enumerate(dimensions):
        for right_name, right_states in dimensions[left_index + 1 :]:
            for left_state in left_states:
                for right_state in right_states:
                    patterns.append(
                        (
                            (left_name, left_state),
                            (right_name, right_state),
                        )
                    )

    if len(patterns) > MAX_ADMISSIBLE_PATTERNS_PER_CELL_HORIZON:
        raise ValueError("EXP-061 pattern enumeration exceeded frozen search bound")
    return tuple(patterns)


def _state_lookup(
    observations: Sequence[FeatureObservation],
    model: StateModel,
) -> dict[str, frozenset[tuple[str, str]]]:
    return {
        row.observation_id: frozenset(encode_state(row, model))
        for row in observations
    }


def _outcome_lookup(
    features: Sequence[FeatureObservation],
    outcomes: Sequence[OutcomeObservation],
) -> tuple[dict[str, FeatureObservation], dict[str, OutcomeObservation]]:
    feature_by_id = {row.observation_id: row for row in features}
    outcome_by_id = {row.observation_id: row for row in outcomes}
    for observation_id, outcome in outcome_by_id.items():
        feature = feature_by_id.get(observation_id)
        if feature is None:
            raise ValueError("EXP-061 outcome has no matching feature observation")
        if (
            feature.symbol != outcome.symbol
            or feature.timeframe != outcome.timeframe
            or feature.available_at_utc != outcome.available_at_utc
        ):
            raise ValueError("EXP-061 feature/outcome identity mismatch")
    return feature_by_id, outcome_by_id


def _direction_values(
    outcome: OutcomeObservation,
    direction: str,
) -> tuple[float, float]:
    if direction == "LONG":
        return outcome.long_net_pips_0p5, outcome.long_net_pips_1p0
    if direction == "SHORT":
        return outcome.short_net_pips_0p5, outcome.short_net_pips_1p0
    raise ValueError("unsupported EXP-061 direction")


def _mean(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("cannot average empty EXP-061 outcome sequence")
    return math.fsum(values) / len(values)


def _statistics(
    *,
    matched_ids: Sequence[str],
    feature_by_id: Mapping[str, FeatureObservation],
    outcome_by_id: Mapping[str, OutcomeObservation],
    direction: str,
    years: Sequence[int],
) -> PatternStatistics:
    half_values: list[float] = []
    stress_values: list[float] = []
    support_by_year = {year: 0 for year in years}
    half_by_year: dict[int, list[float]] = {year: [] for year in years}

    for observation_id in matched_ids:
        outcome = outcome_by_id[observation_id]
        feature = feature_by_id[observation_id]
        half, stress = _direction_values(outcome, direction)
        half_values.append(half)
        stress_values.append(stress)
        year = feature.available_at_utc.year
        if year in support_by_year:
            support_by_year[year] += 1
            half_by_year[year].append(half)

    return PatternStatistics(
        total_support=len(matched_ids),
        year_support=tuple((year, support_by_year[year]) for year in years),
        aggregate_mean_net_pips_0p5=_mean(half_values),
        year_mean_net_pips_0p5=tuple(
            (year, _mean(half_by_year[year]))
            for year in years
        ),
        aggregate_mean_net_pips_1p0=_mean(stress_values),
    )


def _passes_discovery_gate(stats: PatternStatistics) -> bool:
    if stats.total_support < MIN_DISCOVERY_TOTAL_SUPPORT:
        return False
    if any(count < MIN_DISCOVERY_YEAR_SUPPORT for _, count in stats.year_support):
        return False
    if stats.aggregate_mean_net_pips_0p5 < MIN_DISCOVERY_AGGREGATE_MEAN_NET_PIPS:
        return False
    if any(mean <= 0.0 for _, mean in stats.year_mean_net_pips_0p5):
        return False
    if stats.aggregate_mean_net_pips_1p0 <= 0.0:
        return False
    return True


def _rank_key(candidate: PatternHypothesis) -> tuple[object, ...]:
    year_means = [value for _, value in candidate.discovery_statistics.year_mean_net_pips_0p5]
    return (
        -min(year_means),
        -candidate.discovery_statistics.aggregate_mean_net_pips_0p5,
        -candidate.discovery_statistics.aggregate_mean_net_pips_1p0,
        -candidate.discovery_statistics.total_support,
        candidate.depth,
        candidate.fingerprint,
    )


def _jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def mine_discovery_shortlist(
    observations: Sequence[FeatureObservation],
    outcomes: Sequence[OutcomeObservation],
    *,
    model: StateModel,
    horizon_minutes: int,
) -> DiscoveryReport:
    if horizon_minutes not in HORIZONS_MINUTES:
        raise ValueError("unsupported EXP-061 mining horizon")
    features = _scoped_features(
        observations,
        symbol=model.symbol,
        timeframe=model.timeframe,
        window=DISCOVERY_WINDOW,
    )
    scoped_outcomes = _scoped_outcomes(
        outcomes,
        symbol=model.symbol,
        timeframe=model.timeframe,
        horizon_minutes=horizon_minutes,
        window=DISCOVERY_WINDOW,
    )
    feature_by_id, outcome_by_id = _outcome_lookup(features, scoped_outcomes)
    states = _state_lookup(features, model)
    evaluable_ids = frozenset(outcome_by_id)
    patterns = enumerate_patterns(model)

    candidates: list[PatternHypothesis] = []
    events_by_fingerprint: dict[str, frozenset[str]] = {}
    for predicates in patterns:
        required = frozenset(predicates)
        event_ids = frozenset(
            observation_id
            for observation_id, row_states in states.items()
            if observation_id in evaluable_ids and required.issubset(row_states)
        )
        if len(event_ids) < MIN_DISCOVERY_TOTAL_SUPPORT:
            continue
        discovery_year_counts = {2015: 0, 2016: 0, 2017: 0}
        for observation_id in event_ids:
            year = feature_by_id[observation_id].available_at_utc.year
            if year in discovery_year_counts:
                discovery_year_counts[year] += 1
        if any(
            discovery_year_counts[year] < MIN_DISCOVERY_YEAR_SUPPORT
            for year in (2015, 2016, 2017)
        ):
            continue
        ordered_ids = tuple(sorted(event_ids))
        for direction in DIRECTIONS:
            stats = _statistics(
                matched_ids=ordered_ids,
                feature_by_id=feature_by_id,
                outcome_by_id=outcome_by_id,
                direction=direction,
                years=(2015, 2016, 2017),
            )
            if not _passes_discovery_gate(stats):
                continue
            fingerprint = pattern_fingerprint(
                symbol=model.symbol,
                timeframe=model.timeframe,
                horizon_minutes=horizon_minutes,
                direction=direction,
                predicates=predicates,
            )
            candidate = PatternHypothesis(
                symbol=model.symbol,
                timeframe=model.timeframe,
                horizon_minutes=horizon_minutes,
                direction=direction,
                predicates=tuple(predicates),
                fingerprint=fingerprint,
                discovery_statistics=stats,
            )
            candidates.append(candidate)
            events_by_fingerprint[fingerprint] = event_ids

    ranked = sorted(candidates, key=_rank_key)
    deduplicated: list[PatternHypothesis] = []
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

    shortlist = tuple(deduplicated[:MAX_DISCOVERY_SHORTLIST_PER_CELL_HORIZON])
    return DiscoveryReport(
        symbol=model.symbol,
        timeframe=model.timeframe,
        horizon_minutes=horizon_minutes,
        active_continuous_features=model.active_continuous_features,
        enumerated_pattern_count=len(patterns),
        directional_hypothesis_count=len(patterns) * len(DIRECTIONS),
        qualifying_directional_hypothesis_count=len(candidates),
        deduplicated_directional_hypothesis_count=len(deduplicated),
        shortlist=shortlist,
    )


def _matches(
    observation: FeatureObservation,
    *,
    model: StateModel,
    predicates: Sequence[tuple[str, str]],
) -> bool:
    return frozenset(predicates).issubset(frozenset(encode_state(observation, model)))


def confirm_shortlist(
    observations: Sequence[FeatureObservation],
    outcomes: Sequence[OutcomeObservation],
    *,
    model: StateModel,
    discovery: DiscoveryReport,
) -> ConfirmationReport:
    if (
        discovery.symbol != model.symbol
        or discovery.timeframe != model.timeframe
        or discovery.horizon_minutes not in HORIZONS_MINUTES
    ):
        raise ValueError("EXP-061 discovery report/state model mismatch")

    features = _scoped_features(
        observations,
        symbol=model.symbol,
        timeframe=model.timeframe,
        window=CONFIRMATION_WINDOW,
    )
    scoped_outcomes = _scoped_outcomes(
        outcomes,
        symbol=model.symbol,
        timeframe=model.timeframe,
        horizon_minutes=discovery.horizon_minutes,
        window=CONFIRMATION_WINDOW,
    )
    feature_by_id, outcome_by_id = _outcome_lookup(features, scoped_outcomes)

    evaluations: list[ConfirmationEvaluation] = []
    frozen: list[FrozenPatternHypothesis] = []
    for hypothesis in discovery.shortlist:
        if (
            hypothesis.symbol != model.symbol
            or hypothesis.timeframe != model.timeframe
            or hypothesis.horizon_minutes != discovery.horizon_minutes
        ):
            raise ValueError("EXP-061 confirmation hypothesis cell mismatch")
        matched = tuple(
            observation_id
            for observation_id, feature in feature_by_id.items()
            if observation_id in outcome_by_id
            and _matches(feature, model=model, predicates=hypothesis.predicates)
        )
        values = [
            _direction_values(outcome_by_id[observation_id], hypothesis.direction)[0]
            for observation_id in matched
        ]
        mean_value = _mean(values) if values else None
        passed = (
            len(matched) >= CONFIRMATION_MIN_SUPPORT
            and mean_value is not None
            and mean_value > 0.0
        )
        evaluation = ConfirmationEvaluation(
            hypothesis=hypothesis,
            support=len(matched),
            mean_net_pips_0p5=mean_value,
            passed=passed,
        )
        evaluations.append(evaluation)
        if passed and len(frozen) < MAX_FROZEN_PER_CELL_HORIZON:
            frozen.append(
                FrozenPatternHypothesis(
                    hypothesis=hypothesis,
                    confirmation_support=len(matched),
                    confirmation_mean_net_pips_0p5=float(mean_value),
                )
            )

    return ConfirmationReport(
        evaluations=tuple(evaluations),
        frozen=tuple(frozen),
    )


def validate_frozen_patterns(
    observations: Sequence[FeatureObservation],
    outcomes: Sequence[OutcomeObservation],
    *,
    model: StateModel,
    horizon_minutes: int,
    frozen: Sequence[FrozenPatternHypothesis],
) -> ValidationReport:
    if horizon_minutes not in HORIZONS_MINUTES:
        raise ValueError("unsupported EXP-061 validation horizon")
    features = _scoped_features(
        observations,
        symbol=model.symbol,
        timeframe=model.timeframe,
        window=VALIDATION_WINDOW,
    )
    scoped_outcomes = _scoped_outcomes(
        outcomes,
        symbol=model.symbol,
        timeframe=model.timeframe,
        horizon_minutes=horizon_minutes,
        window=VALIDATION_WINDOW,
    )
    feature_by_id, outcome_by_id = _outcome_lookup(features, scoped_outcomes)
    years = (2019, 2020, 2021, 2022)

    evaluations: list[ValidationEvaluation] = []
    validated: list[FrozenPatternHypothesis] = []
    for frozen_pattern in frozen:
        hypothesis = frozen_pattern.hypothesis
        if (
            hypothesis.symbol != model.symbol
            or hypothesis.timeframe != model.timeframe
            or hypothesis.horizon_minutes != horizon_minutes
        ):
            raise ValueError("EXP-061 validation hypothesis cell mismatch")
        matched = tuple(
            observation_id
            for observation_id, feature in feature_by_id.items()
            if observation_id in outcome_by_id
            and _matches(feature, model=model, predicates=hypothesis.predicates)
        )
        values = [
            _direction_values(outcome_by_id[observation_id], hypothesis.direction)[0]
            for observation_id in matched
        ]
        aggregate_mean = _mean(values) if values else None
        support_by_year = {year: 0 for year in years}
        values_by_year: dict[int, list[float]] = {year: [] for year in years}
        for observation_id in matched:
            year = feature_by_id[observation_id].available_at_utc.year
            if year in support_by_year:
                support_by_year[year] += 1
                values_by_year[year].append(
                    _direction_values(
                        outcome_by_id[observation_id],
                        hypothesis.direction,
                    )[0]
                )

        year_support = tuple((year, support_by_year[year]) for year in years)
        year_means = tuple(
            (
                year,
                _mean(values_by_year[year]) if values_by_year[year] else None,
            )
            for year in years
        )
        positive_year_count = sum(
            mean is not None and mean > 0.0
            for _, mean in year_means
        )
        passed = (
            len(matched) >= VALIDATION_MIN_TOTAL_SUPPORT
            and all(count >= VALIDATION_MIN_YEAR_SUPPORT for _, count in year_support)
            and aggregate_mean is not None
            and aggregate_mean > 0.0
            and positive_year_count >= VALIDATION_MIN_POSITIVE_YEARS
        )
        evaluation = ValidationEvaluation(
            frozen=frozen_pattern,
            total_support=len(matched),
            year_support=year_support,
            aggregate_mean_net_pips_0p5=aggregate_mean,
            year_mean_net_pips_0p5=year_means,
            positive_year_count=positive_year_count,
            passed=passed,
        )
        evaluations.append(evaluation)
        if passed:
            validated.append(frozen_pattern)

    return ValidationReport(
        evaluations=tuple(evaluations),
        validated=tuple(validated),
    )


def run_in_memory_discovery(
    observations: Sequence[FeatureObservation],
    outcomes: Sequence[OutcomeObservation],
    *,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
) -> InMemoryDiscoveryResult:
    model = calibrate_state_model(
        observations,
        symbol=symbol,
        timeframe=timeframe,
    )
    discovery = mine_discovery_shortlist(
        observations,
        outcomes,
        model=model,
        horizon_minutes=horizon_minutes,
    )
    confirmation = confirm_shortlist(
        observations,
        outcomes,
        model=model,
        discovery=discovery,
    )
    validation = validate_frozen_patterns(
        observations,
        outcomes,
        model=model,
        horizon_minutes=horizon_minutes,
        frozen=confirmation.frozen,
    )
    return InMemoryDiscoveryResult(
        state_model=model,
        discovery=discovery,
        confirmation=confirmation,
        validation=validation,
    )


__all__ = [
    "BROKER_MUTATION_AUTHORIZED",
    "CANDIDATE_COMPILATION_AUTHORIZED",
    "ConfirmationEvaluation",
    "ConfirmationReport",
    "DEMO_ORDER_AUTHORIZED",
    "DiscoveryReport",
    "EXP061_MINER_CORE_DECISION",
    "EXP061_MINER_CORE_VERSION",
    "FeatureObservation",
    "FrozenPatternHypothesis",
    "HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED",
    "HISTORICAL_SOURCE_ACCESS_AUTHORIZED",
    "InMemoryDiscoveryResult",
    "LIVE_ORDER_AUTHORIZED",
    "OutcomeObservation",
    "PHASE8B_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "PatternHypothesis",
    "PatternStatistics",
    "REAL_MONEY_AUTHORIZED",
    "RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED",
    "StateModel",
    "TRADING_AUTHORIZED",
    "ValidationEvaluation",
    "ValidationReport",
    "calibrate_state_model",
    "confirm_shortlist",
    "encode_state",
    "enumerate_patterns",
    "mine_discovery_shortlist",
    "run_in_memory_discovery",
    "validate_frozen_patterns",
]
