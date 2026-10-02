from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from statistics import median
from typing import Mapping, Sequence

from .annual_pattern_catalogue_method import collection_segments
from .annual_pattern_catalogue_protocol import (
    ANNUAL_CATALOGUE_PROTOCOL_DECISION,
    ANNUAL_CATALOGUE_PROTOCOL_VERSION,
    DIMENSION_STATES,
    MIN_ANNUAL_EVALUABLE_SUPPORT,
    MIN_PRIOR_CALIBRATION_ROWS,
    PATTERN_CONDITION_COUNT,
    PatternDefinition,
    TRANSITION_LAGS_MINUTES,
    annual_record_identity,
    canonical_pattern_fingerprint,
    enumerate_pattern_definitions,
    protocol_fingerprint,
)
from .pattern_miner import FeatureObservation, OutcomeObservation
from .pattern_protocol import (
    CONTINUOUS_FEATURES,
    DIRECTIONS,
    HORIZONS_MINUTES,
    SESSION_DIMENSION,
    SYMBOLS,
    TIMEFRAMES,
    quantile_state,
    session_state,
)


ANNUAL_CATALOGUE_MINER_DECISION = "DEC-471"
ANNUAL_CATALOGUE_MINER_VERSION = "fmp-annual-pattern-catalogue-miner-v1"
SOURCE_PROTOCOL_DECISION = "DEC-470"
SOURCE_PROTOCOL_MERGE_SHA = "e5b20a2d8b45e5eda54673060060fbb9f480f545"
SOURCE_PROTOCOL_BLOB_SHA = "5ddd987cc480e6e31c0cd45328eba16cf690dee9"

HISTORICAL_ARTIFACT_READ_AUTHORIZED = False
HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED = False
HISTORICAL_RESULT_PRODUCTION_AUTHORIZED = False
CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED = False
STRATEGY_V1_SYNTHESIS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


class _TreapNode:
    __slots__ = ("key", "priority", "count", "size", "left", "right")

    def __init__(self, key: float) -> None:
        self.key = key
        self.priority = int.from_bytes(
            hashlib.sha256(key.hex().encode("ascii")).digest()[:8],
            "big",
        )
        self.count = 1
        self.size = 1
        self.left: _TreapNode | None = None
        self.right: _TreapNode | None = None


def _node_size(node: _TreapNode | None) -> int:
    return 0 if node is None else node.size


def _refresh(node: _TreapNode) -> _TreapNode:
    node.size = node.count + _node_size(node.left) + _node_size(node.right)
    return node


def _rotate_right(root: _TreapNode) -> _TreapNode:
    pivot = root.left
    if pivot is None:
        return root
    root.left = pivot.right
    pivot.right = root
    _refresh(root)
    return _refresh(pivot)


def _rotate_left(root: _TreapNode) -> _TreapNode:
    pivot = root.right
    if pivot is None:
        return root
    root.right = pivot.left
    pivot.left = root
    _refresh(root)
    return _refresh(pivot)


def _insert(root: _TreapNode | None, key: float) -> _TreapNode:
    if root is None:
        return _TreapNode(key)
    if key == root.key:
        root.count += 1
        return _refresh(root)
    if key < root.key:
        root.left = _insert(root.left, key)
        if root.left.priority < root.priority:
            root = _rotate_right(root)
    else:
        root.right = _insert(root.right, key)
        if root.right.priority < root.priority:
            root = _rotate_left(root)
    return _refresh(root)


def _kth(root: _TreapNode | None, index: int) -> float:
    if root is None or index < 0 or index >= _node_size(root):
        raise IndexError("DEC-471 order-statistic index out of range")
    left_size = _node_size(root.left)
    if index < left_size:
        return _kth(root.left, index)
    if index < left_size + root.count:
        return root.key
    return _kth(root.right, index - left_size - root.count)


def _treap_cutpoints(root: _TreapNode | None) -> tuple[float, float] | None:
    n = _node_size(root)
    if n < MIN_PRIOR_CALIBRATION_ROWS:
        return None
    lower = _kth(root, math.floor((n - 1) / 3))
    upper = _kth(root, math.floor((2 * (n - 1)) / 3))
    if not lower < upper:
        return None
    return lower, upper


@dataclass(frozen=True, slots=True)
class EncodedAnnualObservation:
    observation_id: str
    available_at_utc: datetime
    states: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class AnnualPatternStatistics:
    support: int
    evaluable: bool
    mean_net_pips_0p5: float | None
    median_net_pips_0p5: float | None
    win_rate_0p5: float | None
    mean_net_pips_1p0: float | None
    median_net_pips_1p0: float | None

    def __post_init__(self) -> None:
        if self.support < 0:
            raise ValueError("DEC-471 annual support cannot be negative")
        if self.evaluable != (self.support >= MIN_ANNUAL_EVALUABLE_SUPPORT):
            raise ValueError("DEC-471 annual evaluable label drift")
        values = (
            self.mean_net_pips_0p5,
            self.median_net_pips_0p5,
            self.win_rate_0p5,
            self.mean_net_pips_1p0,
            self.median_net_pips_1p0,
        )
        if self.support == 0:
            if any(value is not None for value in values):
                raise ValueError("DEC-471 zero-support statistics must be null")
        else:
            if any(value is None for value in values):
                raise ValueError("DEC-471 supported statistics cannot be null")
            assert self.win_rate_0p5 is not None
            if not 0.0 <= self.win_rate_0p5 <= 1.0:
                raise ValueError("DEC-471 annual win rate drift")


@dataclass(frozen=True, slots=True)
class AnnualPatternRecord:
    annual_record_id: str
    canonical_pattern_fingerprint: str
    annual_segment_label: str
    symbol: str
    timeframe: str
    horizon_minutes: int
    direction: str
    family: str
    dimensions: tuple[str, ...]
    states: tuple[str, ...]
    lag_minutes: int | None
    event_fingerprint: str
    statistics: AnnualPatternStatistics


@dataclass(frozen=True, slots=True)
class AnnualCatalogueCellResult:
    annual_segment_label: str
    symbol: str
    timeframe: str
    horizon_minutes: int
    protocol_fingerprint: str
    feature_observation_count: int
    outcome_observation_count: int
    records: tuple[AnnualPatternRecord, ...]

    def __post_init__(self) -> None:
        expected = PATTERN_CONDITION_COUNT * len(DIRECTIONS)
        if len(self.records) != expected:
            raise ValueError("DEC-471 annual catalogue record-count drift")
        record_ids = [row.annual_record_id for row in self.records]
        if len(record_ids) != len(set(record_ids)):
            raise ValueError("DEC-471 duplicate annual record identity")
        canonical = [row.canonical_pattern_fingerprint for row in self.records]
        if len(canonical) != len(set(canonical)):
            raise ValueError(
                "DEC-471 duplicate canonical directional pattern identity"
            )


def _segment_bounds(label: str) -> tuple[datetime, datetime]:
    matches = [segment for segment in collection_segments() if segment.label == label]
    if len(matches) != 1:
        raise ValueError("DEC-471 annual segment label drift")
    segment = matches[0]
    start = datetime(
        segment.start.year,
        segment.start.month,
        segment.start.day,
        tzinfo=timezone.utc,
    )
    end_date = segment.end_inclusive + timedelta(days=1)
    end = datetime(
        end_date.year,
        end_date.month,
        end_date.day,
        tzinfo=timezone.utc,
    )
    return start, end


def _scope_features(
    observations: Sequence[FeatureObservation],
    *,
    symbol: str,
    timeframe: str,
    annual_segment_label: str,
) -> tuple[FeatureObservation, ...]:
    if symbol not in SYMBOLS or timeframe not in TIMEFRAMES:
        raise ValueError("DEC-471 unsupported feature cell")
    start, end = _segment_bounds(annual_segment_label)
    scoped = tuple(
        row
        for row in observations
        if row.symbol == symbol
        and row.timeframe == timeframe
        and start <= row.available_at_utc < end
    )
    ids = [row.observation_id for row in scoped]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate DEC-471 feature observation identity")
    timestamps = [row.available_at_utc for row in scoped]
    if len(timestamps) != len(set(timestamps)):
        raise ValueError("duplicate DEC-471 feature timestamp")
    return tuple(
        sorted(scoped, key=lambda row: (row.available_at_utc, row.observation_id))
    )


def _scope_outcomes(
    outcomes: Sequence[OutcomeObservation],
    *,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
    annual_segment_label: str,
) -> tuple[OutcomeObservation, ...]:
    if symbol not in SYMBOLS or timeframe not in TIMEFRAMES:
        raise ValueError("DEC-471 unsupported outcome cell")
    if horizon_minutes not in HORIZONS_MINUTES:
        raise ValueError("DEC-471 unsupported outcome horizon")
    start, end = _segment_bounds(annual_segment_label)
    scoped = tuple(
        row
        for row in outcomes
        if row.symbol == symbol
        and row.timeframe == timeframe
        and row.horizon_minutes == horizon_minutes
        and start <= row.available_at_utc < end
        and row.exit_timestamp_utc < end
    )
    ids = [row.observation_id for row in scoped]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate DEC-471 outcome observation identity")
    return tuple(
        sorted(scoped, key=lambda row: (row.available_at_utc, row.observation_id))
    )


def encode_annual_states(
    observations: Sequence[FeatureObservation],
    *,
    symbol: str,
    timeframe: str,
    annual_segment_label: str,
) -> tuple[EncodedAnnualObservation, ...]:
    scoped = _scope_features(
        observations,
        symbol=symbol,
        timeframe=timeframe,
        annual_segment_label=annual_segment_label,
    )
    roots: dict[str, _TreapNode | None] = {
        name: None for name in CONTINUOUS_FEATURES
    }
    encoded: list[EncodedAnnualObservation] = []
    for row in scoped:
        states: list[tuple[str, str]] = []
        for name in CONTINUOUS_FEATURES:
            value = row.values[name]
            cuts = _treap_cutpoints(roots[name])
            if cuts is not None and _finite_number(value):
                state = quantile_state(value, cuts)
                if state is not None:
                    states.append((name, state))
            if _finite_number(value):
                roots[name] = _insert(roots[name], float(value))
        states.append((SESSION_DIMENSION, session_state(row.values)))
        encoded.append(
            EncodedAnnualObservation(
                observation_id=row.observation_id,
                available_at_utc=row.available_at_utc,
                states=tuple(states),
            )
        )
    return tuple(encoded)


def _bind_outcomes(
    features: Sequence[FeatureObservation],
    outcomes: Sequence[OutcomeObservation],
) -> dict[str, OutcomeObservation]:
    feature_by_id = {row.observation_id: row for row in features}
    outcome_by_id = {row.observation_id: row for row in outcomes}
    for observation_id, outcome in outcome_by_id.items():
        feature = feature_by_id.get(observation_id)
        if feature is None:
            raise ValueError("DEC-471 outcome has no matching feature observation")
        if (
            feature.symbol != outcome.symbol
            or feature.timeframe != outcome.timeframe
            or feature.available_at_utc != outcome.available_at_utc
        ):
            raise ValueError("DEC-471 feature/outcome identity mismatch")
    return outcome_by_id


def _build_event_indexes(
    encoded: Sequence[EncodedAnnualObservation],
    outcome_by_id: Mapping[str, OutcomeObservation],
) -> tuple[
    dict[tuple[str, str], frozenset[str]],
    dict[tuple[str, str, str, int], frozenset[str]],
]:
    atomic_mut: dict[tuple[str, str], set[str]] = {
        (dimension, state): set()
        for dimension, states in DIMENSION_STATES.items()
        for state in states
    }
    transition_mut: dict[tuple[str, str, str, int], set[str]] = {
        (dimension, prior_state, current_state, lag): set()
        for dimension, states in DIMENSION_STATES.items()
        for prior_state in states
        for current_state in states
        for lag in TRANSITION_LAGS_MINUTES
    }

    by_timestamp = {row.available_at_utc: row for row in encoded}
    for row in encoded:
        if row.observation_id not in outcome_by_id:
            continue
        current = dict(row.states)
        for dimension, state in row.states:
            atomic_mut[(dimension, state)].add(row.observation_id)
        for lag in TRANSITION_LAGS_MINUTES:
            prior = by_timestamp.get(
                row.available_at_utc - timedelta(minutes=lag)
            )
            if prior is None:
                continue
            prior_states = dict(prior.states)
            for dimension, current_state in current.items():
                prior_state = prior_states.get(dimension)
                if prior_state is None:
                    continue
                transition_mut[
                    (dimension, prior_state, current_state, lag)
                ].add(row.observation_id)

    atomic = {key: frozenset(value) for key, value in atomic_mut.items()}
    transitions = {
        key: frozenset(value) for key, value in transition_mut.items()
    }
    return atomic, transitions


def _events_for_pattern(
    pattern: PatternDefinition,
    *,
    atomic: Mapping[tuple[str, str], frozenset[str]],
    transitions: Mapping[tuple[str, str, str, int], frozenset[str]],
) -> frozenset[str]:
    if pattern.family == "SNAPSHOT_SINGLE":
        return atomic[(pattern.dimensions[0], pattern.states[0])]
    if pattern.family == "SNAPSHOT_PAIR":
        left = atomic[(pattern.dimensions[0], pattern.states[0])]
        right = atomic[(pattern.dimensions[1], pattern.states[1])]
        return left & right
    if pattern.family == "SAME_DIMENSION_TRANSITION":
        if pattern.lag_minutes is None:
            raise ValueError("DEC-471 transition is missing lag")
        return transitions[
            (
                pattern.dimensions[0],
                pattern.states[0],
                pattern.states[1],
                pattern.lag_minutes,
            )
        ]
    raise ValueError("DEC-471 unsupported pattern family")


def _event_fingerprint(event_ids: frozenset[str]) -> str:
    encoded = "\n".join(sorted(event_ids)).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _direction_values(
    outcome: OutcomeObservation,
    direction: str,
) -> tuple[float, float]:
    if direction == "LONG":
        return outcome.long_net_pips_0p5, outcome.long_net_pips_1p0
    if direction == "SHORT":
        return outcome.short_net_pips_0p5, outcome.short_net_pips_1p0
    raise ValueError("DEC-471 unsupported direction")


def _statistics(
    event_ids: frozenset[str],
    outcome_by_id: Mapping[str, OutcomeObservation],
    *,
    direction: str,
) -> AnnualPatternStatistics:
    if not event_ids:
        return AnnualPatternStatistics(
            support=0,
            evaluable=False,
            mean_net_pips_0p5=None,
            median_net_pips_0p5=None,
            win_rate_0p5=None,
            mean_net_pips_1p0=None,
            median_net_pips_1p0=None,
        )
    base: list[float] = []
    stress: list[float] = []
    for observation_id in sorted(event_ids):
        half, one = _direction_values(
            outcome_by_id[observation_id],
            direction,
        )
        base.append(float(half))
        stress.append(float(one))
    support = len(base)
    return AnnualPatternStatistics(
        support=support,
        evaluable=support >= MIN_ANNUAL_EVALUABLE_SUPPORT,
        mean_net_pips_0p5=math.fsum(base) / support,
        median_net_pips_0p5=float(median(base)),
        win_rate_0p5=sum(value > 0.0 for value in base) / support,
        mean_net_pips_1p0=math.fsum(stress) / support,
        median_net_pips_1p0=float(median(stress)),
    )


def mine_annual_catalogue_cell(
    observations: Sequence[FeatureObservation],
    outcomes: Sequence[OutcomeObservation],
    *,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
    annual_segment_label: str,
) -> AnnualCatalogueCellResult:
    features = _scope_features(
        observations,
        symbol=symbol,
        timeframe=timeframe,
        annual_segment_label=annual_segment_label,
    )
    scoped_outcomes = _scope_outcomes(
        outcomes,
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon_minutes,
        annual_segment_label=annual_segment_label,
    )
    outcome_by_id = _bind_outcomes(features, scoped_outcomes)
    encoded = encode_annual_states(
        features,
        symbol=symbol,
        timeframe=timeframe,
        annual_segment_label=annual_segment_label,
    )
    atomic, transitions = _build_event_indexes(encoded, outcome_by_id)

    records: list[AnnualPatternRecord] = []
    for pattern in enumerate_pattern_definitions():
        event_ids = _events_for_pattern(
            pattern,
            atomic=atomic,
            transitions=transitions,
        )
        event_fp = _event_fingerprint(event_ids)
        for direction in DIRECTIONS:
            canonical = canonical_pattern_fingerprint(
                pattern=pattern,
                symbol=symbol,
                timeframe=timeframe,
                horizon_minutes=horizon_minutes,
                direction=direction,
            )
            records.append(
                AnnualPatternRecord(
                    annual_record_id=annual_record_identity(
                        canonical_pattern_fingerprint_value=canonical,
                        annual_segment_label=annual_segment_label,
                    ),
                    canonical_pattern_fingerprint=canonical,
                    annual_segment_label=annual_segment_label,
                    symbol=symbol,
                    timeframe=timeframe,
                    horizon_minutes=horizon_minutes,
                    direction=direction,
                    family=pattern.family,
                    dimensions=pattern.dimensions,
                    states=pattern.states,
                    lag_minutes=pattern.lag_minutes,
                    event_fingerprint=event_fp,
                    statistics=_statistics(
                        event_ids,
                        outcome_by_id,
                        direction=direction,
                    ),
                )
            )

    return AnnualCatalogueCellResult(
        annual_segment_label=annual_segment_label,
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon_minutes,
        protocol_fingerprint=protocol_fingerprint(),
        feature_observation_count=len(features),
        outcome_observation_count=len(scoped_outcomes),
        records=tuple(records),
    )


def miner_contract_payload() -> dict[str, object]:
    return {
        "decision": ANNUAL_CATALOGUE_MINER_DECISION,
        "version": ANNUAL_CATALOGUE_MINER_VERSION,
        "source_protocol_decision": SOURCE_PROTOCOL_DECISION,
        "source_protocol_version": ANNUAL_CATALOGUE_PROTOCOL_VERSION,
        "source_protocol_merge_sha": SOURCE_PROTOCOL_MERGE_SHA,
        "source_protocol_blob_sha": SOURCE_PROTOCOL_BLOB_SHA,
        "produces_every_nominal_record": True,
        "selects_winners": False,
        "reranks_patterns": False,
        "continuous_state_encoding": "strict_prior_only_expanding_tertiles",
        "transition_matching": "exact_timestamp_only",
        "annual_boundary_enforced": True,
        "authorizations": {
            "historical_artifact_read_authorized": (
                HISTORICAL_ARTIFACT_READ_AUTHORIZED
            ),
            "historical_catalogue_execution_authorized": (
                HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED
            ),
            "historical_result_production_authorized": (
                HISTORICAL_RESULT_PRODUCTION_AUTHORIZED
            ),
            "cross_year_result_production_authorized": (
                CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED
            ),
            "strategy_v1_synthesis_authorized": (
                STRATEGY_V1_SYNTHESIS_AUTHORIZED
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
        "next_gate": (
            "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_EVIDENCE_CONTRACT"
        ),
    }


if ANNUAL_CATALOGUE_PROTOCOL_DECISION != "DEC-470":
    raise ValueError("DEC-471 source protocol decision drift")
if SOURCE_PROTOCOL_DECISION != ANNUAL_CATALOGUE_PROTOCOL_DECISION:
    raise ValueError("DEC-471 protocol binding drift")
if PATTERN_CONDITION_COUNT != len(enumerate_pattern_definitions()):
    raise ValueError("DEC-471 pattern enumeration drift")
for _enabled in miner_contract_payload()["authorizations"].values():
    if _enabled:
        raise ValueError("DEC-471 source-only authority drift")


__all__ = [
    "ANNUAL_CATALOGUE_MINER_DECISION",
    "ANNUAL_CATALOGUE_MINER_VERSION",
    "AnnualCatalogueCellResult",
    "AnnualPatternRecord",
    "AnnualPatternStatistics",
    "EncodedAnnualObservation",
    "HISTORICAL_ARTIFACT_READ_AUTHORIZED",
    "HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED",
    "HISTORICAL_RESULT_PRODUCTION_AUTHORIZED",
    "STRATEGY_V1_SYNTHESIS_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "encode_annual_states",
    "mine_annual_catalogue_cell",
    "miner_contract_payload",
]
