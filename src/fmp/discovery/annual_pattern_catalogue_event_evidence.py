"""Source-only event-level evidence for annual pattern catalogue observations.

Governing method: annual pattern catalogue discovery under DEC-469 / DEC-268.
Event-level evidence is a pattern-tool inside that method. It records
caller-supplied outcome events so a later milestone can study overlap,
episode structure, and uncertainty.

The tool does not mine catalogues, read market artifacts, open protected
years, score the DEC-470 gate, or estimate a p-value. Structural checks on
synthetic rows are not independent validation of frozen annual evidence.

Annual catalogue records store an event_fingerprint hash of a membership
set. That hash does not contain observation ids, timestamps, or per-event
nets. This module refuses to recover event ids from it.

The same observation id inside one annual segment, symbol, and timeframe
keeps one availability timestamp across horizons. The adapter hashes that
timestamp into the id and leaves the horizon out, and DEC-471 binds a
feature row to an outcome only when the timestamps match. A caller-supplied
id that uses two timestamps in that scope is rejected. The same id on
another symbol, timeframe, or segment stays unresolved.

Pattern membership is a caller assertion. Two current states of one
dimension, or two prior states of one dimension at one lag, are rejected.
Feature values are not read, and a structurally valid pattern is not
evidence that an observation satisfied it.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Mapping, Sequence

from .annual_pattern_catalogue_method import (
    GOVERNING_RESEARCH_METHOD,
    collection_segments,
)
from .annual_pattern_catalogue_protocol import (
    ANNUAL_CATALOGUE_PROTOCOL_DECISION,
    ANNUAL_CATALOGUE_PROTOCOL_VERSION,
    DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT,
    DISCOVERY_SLIPPAGE_PIPS,
    MAX_CROSS_YEAR_SHORTLIST_PER_CELL_FAMILY,
    MAX_SIGN_FLIPS,
    MIN_ANNUAL_EVALUABLE_SUPPORT,
    MIN_BASE_POSITIVE_FRACTION,
    MIN_CROSS_YEAR_EVALUABLE_SEGMENTS,
    MIN_MEDIAN_ANNUAL_MEAN_NET_PIPS_0P5,
    MIN_POOLED_MEAN_NET_PIPS_0P5,
    MIN_STRESS_POSITIVE_FRACTION,
    NEAR_DUPLICATE_JACCARD,
    PATTERN_CONDITION_COUNT,
    REQUIRE_POOLED_STRESS_MEAN_POSITIVE,
    STRESS_SLIPPAGE_PIPS,
    PatternDefinition,
    annual_record_identity,
    canonical_pattern_fingerprint,
    protocol_fingerprint,
)
from .pattern_miner import FeatureObservation, OutcomeObservation
from .pattern_protocol import DIRECTIONS, HORIZONS_MINUTES, SYMBOLS, TIMEFRAMES


EVENT_LEVEL_EVIDENCE_VERSION = 1
EVENT_LEVEL_EVIDENCE_PROTOCOL = "fmp-annual-pattern-catalogue-event-evidence-v1"
PATTERN_TOOL = "event-level-evidence-v1"
EVIDENCE_BASIS = "CALLER_SUPPLIED_SYNTHETIC_EVENTS_NOT_FROZEN_EVIDENCE"
IDENTITY_SCHEME = "observation-key-sha256-v1"
OUTCOME_WINDOW_CONVENTION = "half_open_[available_at_utc, exit_timestamp_utc)"
CORRELATED_NOISE_CALIBRATION_EXPERIMENT = "EXP-20261118-069"
CORRELATED_NOISE_CALIBRATION_SUMMARY = (
    "EXP-20261118-069 observed synthetic false passes of the frozen DEC-470 "
    "gate. Independent zero-gross noise of 8 pips passed 163, 147, and 143 "
    "hypotheses across seeds 20261118, 20261119, and 20261120. Correlated "
    "zero-gross noise of 8 pips passed 0, 0, and 4922. The 4922 count is "
    "seed 20261120. Those counts are a recorded constraint. They are not an "
    "acceptance threshold and they were not used to retune DEC-470."
)
HISTORICAL_EVENT_RECOVERY_DEPENDENCY = (
    "Frozen annual catalogues store event_fingerprint hashes, not observation "
    "ids, timestamps, or per-event nets. Authentic event-level evidence needs "
    "the original observation rows. Those rows are historical artifacts. This "
    "module does not open them and does not reconstruct ids from the hash."
)
MEMBERSHIP_VALIDATION_BOUNDARY = (
    "Caller-supplied pattern membership is an assertion. One observation id "
    "inside one annual segment, symbol, and timeframe cannot be assigned two "
    "current states of one dimension, or two prior states of one dimension at "
    "one lag. That check uses the asserted pattern definitions. Feature values "
    "are unread. DEC-471 calibration cutpoints are not built. A structurally "
    "valid PatternDefinition is not evidence that an observation satisfied "
    "the pattern."
)

HISTORICAL_ARTIFACT_READ_AUTHORIZED = False
HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED = False
HISTORICAL_RESULT_PRODUCTION_AUTHORIZED = False
CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED = False
STRATEGY_V1_SYNTHESIS_AUTHORIZED = False
STATISTICAL_PROMOTION_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False
WORKFLOW_ACTIVATION_AUTHORIZED = False
DEC629_ADOPTED = False
DEC630_ADOPTED = False
ANNUAL_RUN_385_CONSUMED = False

_MAX_OBSERVATION_ID_LENGTH = 200
_MAX_SOURCE_LABEL_LENGTH = 128
_AUTHORIZATION_FLAGS = (
    ("historical_artifact_read_authorized", HISTORICAL_ARTIFACT_READ_AUTHORIZED),
    ("historical_catalogue_execution_authorized", HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED),
    ("historical_result_production_authorized", HISTORICAL_RESULT_PRODUCTION_AUTHORIZED),
    ("cross_year_result_production_authorized", CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED),
    ("strategy_v1_synthesis_authorized", STRATEGY_V1_SYNTHESIS_AUTHORIZED),
    ("statistical_promotion_authorized", STATISTICAL_PROMOTION_AUTHORIZED),
    ("candidate_compilation_authorized", CANDIDATE_COMPILATION_AUTHORIZED),
    ("promotion_authorized", PROMOTION_AUTHORIZED),
    ("phase8b_authorized", PHASE8B_AUTHORIZED),
    ("demo_order_authorized", DEMO_ORDER_AUTHORIZED),
    ("broker_mutation_authorized", BROKER_MUTATION_AUTHORIZED),
    ("live_order_authorized", LIVE_ORDER_AUTHORIZED),
    ("real_money_authorized", REAL_MONEY_AUTHORIZED),
    ("trading_authorized", TRADING_AUTHORIZED),
    ("workflow_activation_authorized", WORKFLOW_ACTIVATION_AUTHORIZED),
    ("dec629_adopted", DEC629_ADOPTED),
    ("dec630_adopted", DEC630_ADOPTED),
    ("annual_run_385_consumed", ANNUAL_RUN_385_CONSUMED),
)


def _fail(code: str, detail: str) -> None:
    raise ValueError(f"{code}: {detail}")


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


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_json(value: object) -> str:
    return _sha256_bytes(_canonical_json(value))


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        _fail("EVENT_EVIDENCE_MALFORMED_PROVENANCE", f"{field} must be a 64-character sha256")
    try:
        int(value, 16)
    except ValueError:
        _fail("EVENT_EVIDENCE_MALFORMED_PROVENANCE", f"{field} must be hexadecimal")
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        _fail("EVENT_EVIDENCE_MALFORMED_PROVENANCE", f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError:
        _fail("EVENT_EVIDENCE_MALFORMED_PROVENANCE", f"{field} must be hexadecimal")
    return value.lower()


def _require_utc(value: datetime, *, field: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        _fail("EVENT_EVIDENCE_TIMESTAMP_NOT_UTC", f"{field} must use UTC")


def _finite_float(value: object, *, field: str) -> float:
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(float(value))
    ):
        _fail("EVENT_EVIDENCE_MALFORMED_OUTCOME", f"{field} must be finite")
    return float(value)


def _timestamp_text(value: datetime) -> str:
    _require_utc(value, field="timestamp")
    text = value.isoformat()
    if text.endswith("+00:00"):
        return text[:-6] + "Z"
    _fail("EVENT_EVIDENCE_TIMESTAMP_NOT_UTC", "timestamp must be UTC")
    return text


def _parse_timestamp(value: object, *, field: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        _fail("EVENT_EVIDENCE_TIMESTAMP_NOT_UTC", f"{field} must be a UTC timestamp ending in Z")
    parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    _require_utc(parsed, field=field)
    if _timestamp_text(parsed) != value:
        _fail("EVENT_EVIDENCE_TIMESTAMP_NOT_UTC", f"{field} is not canonical UTC")
    return parsed


def _segment_bounds(label: str) -> tuple[datetime, datetime]:
    matches = [segment for segment in collection_segments() if segment.label == label]
    if len(matches) != 1:
        _fail("EVENT_EVIDENCE_SEGMENT_BOUNDARY", f"unknown annual segment {label!r}")
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


def _segment_index(label: str) -> int:
    labels = [segment.label for segment in collection_segments()]
    return labels.index(label)


def _vocabulary_index(value: str, allowed: Sequence[str], *, field: str) -> int:
    try:
        return tuple(allowed).index(value)
    except ValueError:
        _fail("EVENT_EVIDENCE_MALFORMED_OBSERVATION", f"unsupported {field} {value!r}")
    raise AssertionError


def event_identity_for(
    *,
    observation_id: str,
    annual_segment_label: str,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
) -> str:
    """Stable identity of one physical outcome event.

    The identity is the hash of the caller-supplied observation key. It is
    not derived from an annual event_fingerprint.
    """

    payload = {
        "identity_scheme": IDENTITY_SCHEME,
        "observation_id": observation_id,
        "annual_segment_label": annual_segment_label,
        "symbol": symbol,
        "timeframe": timeframe,
        "horizon_minutes": horizon_minutes,
    }
    return _sha256_json(payload)


def recover_event_ids_from_event_fingerprint(event_fingerprint: object) -> tuple[str, ...]:
    """Refuse recovery from an annual event_fingerprint hash."""

    del event_fingerprint
    _fail(
        "EVENT_EVIDENCE_EVENT_FINGERPRINT_RECOVERY_REFUSED",
        "an annual event_fingerprint is a hash of a membership set and does "
        "not contain recoverable event ids",
    )
    return ()


def _pattern_key(pattern: PatternDefinition) -> tuple[object, ...]:
    return (pattern.family, pattern.dimensions, pattern.states, pattern.lag_minutes)


@dataclass(frozen=True, slots=True)
class EventEvidenceProvenance:
    source_label: str
    code_commit: str
    synthetic_manifest_sha256: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.source_label, str)
            or not self.source_label
            or self.source_label != self.source_label.strip()
            or len(self.source_label) > _MAX_SOURCE_LABEL_LENGTH
            or any(character in self.source_label for character in "\r\n")
        ):
            _fail(
                "EVENT_EVIDENCE_MALFORMED_PROVENANCE",
                "source_label must be a single non-empty line",
            )
        object_commit = _validate_commit(self.code_commit, field="code_commit")
        object_manifest = _validate_sha256(
            self.synthetic_manifest_sha256,
            field="synthetic_manifest_sha256",
        )
        object.__setattr__(self, "code_commit", object_commit)
        object.__setattr__(self, "synthetic_manifest_sha256", object_manifest)


@dataclass(frozen=True, slots=True)
class EventObservationSubmission:
    observation_id: str
    annual_segment_label: str
    symbol: str
    timeframe: str
    horizon_minutes: int
    available_at_utc: datetime
    exit_timestamp_utc: datetime
    direction: str
    net_pips_0p5: float
    net_pips_1p0: float
    memberships: tuple[PatternDefinition, ...]

    def __post_init__(self) -> None:
        if (
            not isinstance(self.observation_id, str)
            or not self.observation_id
            or self.observation_id != self.observation_id.strip()
            or len(self.observation_id) > _MAX_OBSERVATION_ID_LENGTH
            or any(character in self.observation_id for character in "\r\n")
        ):
            _fail(
                "EVENT_EVIDENCE_MALFORMED_OBSERVATION",
                "observation_id must be a single non-empty line",
            )
        if not isinstance(self.annual_segment_label, str):
            _fail("EVENT_EVIDENCE_SEGMENT_BOUNDARY", "annual segment label is missing")
        _vocabulary_index(self.symbol, SYMBOLS, field="symbol")
        _vocabulary_index(self.timeframe, TIMEFRAMES, field="timeframe")
        if self.horizon_minutes not in HORIZONS_MINUTES:
            _fail(
                "EVENT_EVIDENCE_MALFORMED_OBSERVATION",
                f"unsupported horizon {self.horizon_minutes!r}",
            )
        if self.direction not in DIRECTIONS:
            _fail(
                "EVENT_EVIDENCE_MALFORMED_OBSERVATION",
                f"unsupported direction {self.direction!r}",
            )
        if not isinstance(self.available_at_utc, datetime):
            _fail("EVENT_EVIDENCE_TIMESTAMP_NOT_UTC", "available_at_utc must be a datetime")
        if not isinstance(self.exit_timestamp_utc, datetime):
            _fail("EVENT_EVIDENCE_TIMESTAMP_NOT_UTC", "exit_timestamp_utc must be a datetime")
        _require_utc(self.available_at_utc, field="available_at_utc")
        _require_utc(self.exit_timestamp_utc, field="exit_timestamp_utc")
        expected_exit = self.available_at_utc + timedelta(minutes=int(self.horizon_minutes))
        if self.exit_timestamp_utc != expected_exit:
            _fail(
                "EVENT_EVIDENCE_WINDOW_BOUNDARY",
                "exit_timestamp_utc must equal available_at_utc plus the horizon",
            )
        start, end = _segment_bounds(self.annual_segment_label)
        if not start <= self.available_at_utc < end or not self.exit_timestamp_utc < end:
            _fail(
                "EVENT_EVIDENCE_SEGMENT_BOUNDARY",
                f"outcome window exits annual segment {self.annual_segment_label}",
            )
        base = _finite_float(self.net_pips_0p5, field="net_pips_0p5")
        stress = _finite_float(self.net_pips_1p0, field="net_pips_1p0")
        object.__setattr__(self, "net_pips_0p5", base)
        object.__setattr__(self, "net_pips_1p0", stress)
        if isinstance(self.memberships, (str, bytes)) or not isinstance(
            self.memberships, Sequence
        ):
            _fail("EVENT_EVIDENCE_INCOMPLETE_MEMBERSHIP", "memberships must be a sequence")
        if len(self.memberships) == 0:
            _fail(
                "EVENT_EVIDENCE_INCOMPLETE_MEMBERSHIP",
                "each measurement needs at least one pattern membership",
            )
        if len(self.memberships) > PATTERN_CONDITION_COUNT:
            _fail(
                "EVENT_EVIDENCE_INCOMPLETE_MEMBERSHIP",
                "membership count exceeds the frozen pattern-condition count",
            )
        seen: set[tuple[object, ...]] = set()
        copied: list[PatternDefinition] = []
        for pattern in self.memberships:
            if not isinstance(pattern, PatternDefinition):
                _fail(
                    "EVENT_EVIDENCE_INCOMPLETE_MEMBERSHIP",
                    "membership must be a DEC-470 pattern definition",
                )
            key = _pattern_key(pattern)
            if key in seen:
                _fail(
                    "EVENT_EVIDENCE_DUPLICATE_MEMBERSHIP",
                    "the same pattern is repeated on one measurement",
                )
            seen.add(key)
            copied.append(pattern)
        copied.sort(key=_pattern_key)
        object.__setattr__(self, "memberships", tuple(copied))

    @property
    def event_identity(self) -> str:
        return event_identity_for(
            observation_id=self.observation_id,
            annual_segment_label=self.annual_segment_label,
            symbol=self.symbol,
            timeframe=self.timeframe,
            horizon_minutes=self.horizon_minutes,
        )


def submission_from_outcome(
    outcome: OutcomeObservation,
    *,
    annual_segment_label: str,
    direction: str,
    memberships: Sequence[PatternDefinition],
    feature: FeatureObservation | None = None,
) -> EventObservationSubmission:
    """Build one directional submission from an existing outcome observation.

    A supplied feature row is an identity check. Its values are not read and
    do not prove the supplied pattern membership.
    """

    if not isinstance(outcome, OutcomeObservation):
        _fail(
            "EVENT_EVIDENCE_MALFORMED_OBSERVATION",
            "outcome must be an OutcomeObservation",
        )
    if feature is not None:
        if not isinstance(feature, FeatureObservation):
            _fail(
                "EVENT_EVIDENCE_MALFORMED_OBSERVATION",
                "feature must be a FeatureObservation",
            )
        if (
            feature.observation_id != outcome.observation_id
            or feature.symbol != outcome.symbol
            or feature.timeframe != outcome.timeframe
            or feature.available_at_utc != outcome.available_at_utc
        ):
            _fail(
                "EVENT_EVIDENCE_FEATURE_OUTCOME_MISMATCH",
                "feature and outcome observation identity differ",
            )
    if direction == "LONG":
        base = outcome.long_net_pips_0p5
        stress = outcome.long_net_pips_1p0
    elif direction == "SHORT":
        base = outcome.short_net_pips_0p5
        stress = outcome.short_net_pips_1p0
    else:
        _fail("EVENT_EVIDENCE_MALFORMED_OBSERVATION", f"unsupported direction {direction!r}")
        raise AssertionError
    return EventObservationSubmission(
        observation_id=outcome.observation_id,
        annual_segment_label=annual_segment_label,
        symbol=outcome.symbol,
        timeframe=outcome.timeframe,
        horizon_minutes=outcome.horizon_minutes,
        available_at_utc=outcome.available_at_utc,
        exit_timestamp_utc=outcome.exit_timestamp_utc,
        direction=direction,
        net_pips_0p5=base,
        net_pips_1p0=stress,
        memberships=tuple(memberships),
    )


@dataclass(frozen=True, slots=True)
class _Measurement:
    direction: str
    net_pips_0p5: float
    net_pips_1p0: float
    memberships: tuple[PatternDefinition, ...]


@dataclass(frozen=True, slots=True)
class _PhysicalEvent:
    event_identity: str
    observation_id: str
    annual_segment_label: str
    symbol: str
    timeframe: str
    horizon_minutes: int
    available_at_utc: datetime
    exit_timestamp_utc: datetime
    measurements: tuple[_Measurement, ...]

    def sort_key(self) -> tuple[object, ...]:
        return (
            _segment_index(self.annual_segment_label),
            _vocabulary_index(self.symbol, SYMBOLS, field="symbol"),
            _vocabulary_index(self.timeframe, TIMEFRAMES, field="timeframe"),
            self.horizon_minutes,
            self.available_at_utc,
            self.exit_timestamp_utc,
            self.event_identity,
        )


def _collect_events(
    submissions: Sequence[EventObservationSubmission],
) -> tuple[_PhysicalEvent, ...]:
    if isinstance(submissions, (str, bytes)) or not isinstance(submissions, Sequence):
        _fail("EVENT_EVIDENCE_MALFORMED_SUBMISSION", "submissions must be a sequence")
    if len(submissions) == 0:
        _fail("EVENT_EVIDENCE_INCOMPLETE", "at least one event measurement is required")
    grouped: dict[str, list[EventObservationSubmission]] = {}
    for submission in submissions:
        if not isinstance(submission, EventObservationSubmission):
            _fail(
                "EVENT_EVIDENCE_MALFORMED_SUBMISSION",
                "each submission must be an EventObservationSubmission",
            )
        grouped.setdefault(submission.event_identity, []).append(submission)

    events: list[_PhysicalEvent] = []
    for identity, rows in grouped.items():
        anchor = rows[0]
        for row in rows[1:]:
            if (
                row.available_at_utc != anchor.available_at_utc
                or row.exit_timestamp_utc != anchor.exit_timestamp_utc
                or row.observation_id != anchor.observation_id
            ):
                _fail(
                    "EVENT_EVIDENCE_CONTRADICTORY_TIMESTAMPS",
                    f"event {identity} has conflicting outcome windows",
                )
        by_direction: dict[str, EventObservationSubmission] = {}
        for row in rows:
            previous = by_direction.get(row.direction)
            if previous is None:
                by_direction[row.direction] = row
                continue
            if (
                previous.net_pips_0p5 != row.net_pips_0p5
                or previous.net_pips_1p0 != row.net_pips_1p0
            ):
                _fail(
                    "EVENT_EVIDENCE_CONTRADICTORY_OUTCOME",
                    f"event {identity} direction {row.direction} has conflicting nets",
                )
            if previous.memberships != row.memberships:
                _fail(
                    "EVENT_EVIDENCE_CONTRADICTORY_MEMBERSHIP",
                    f"event {identity} direction {row.direction} has conflicting memberships",
                )
            _fail(
                "EVENT_EVIDENCE_DUPLICATE_MEASUREMENT",
                f"event {identity} direction {row.direction} is repeated",
            )
        measurements = tuple(
            _Measurement(
                direction=direction,
                net_pips_0p5=by_direction[direction].net_pips_0p5,
                net_pips_1p0=by_direction[direction].net_pips_1p0,
                memberships=by_direction[direction].memberships,
            )
            for direction in DIRECTIONS
            if direction in by_direction
        )
        events.append(
            _PhysicalEvent(
                event_identity=identity,
                observation_id=anchor.observation_id,
                annual_segment_label=anchor.annual_segment_label,
                symbol=anchor.symbol,
                timeframe=anchor.timeframe,
                horizon_minutes=anchor.horizon_minutes,
                available_at_utc=anchor.available_at_utc,
                exit_timestamp_utc=anchor.exit_timestamp_utc,
                measurements=measurements,
            )
        )
    events.sort(key=lambda event: event.sort_key())
    _assert_observation_identity(events)
    return tuple(events)


def _assert_current_state(
    current: dict[str, str],
    *,
    dimension: str,
    state: str,
    observation_id: str,
) -> None:
    previous = current.get(dimension)
    if previous is not None and previous != state:
        _fail(
            "EVENT_EVIDENCE_CONTRADICTORY_STATE",
            f"observation {observation_id} dimension {dimension} is asserted as "
            f"{previous} and {state}",
        )
    current[dimension] = state


def _record_state_claim(
    pattern: PatternDefinition,
    *,
    observation_id: str,
    current: dict[str, str],
    transitions: dict[tuple[str, int], tuple[str, str]],
) -> None:
    if pattern.family == "SNAPSHOT_SINGLE":
        _assert_current_state(
            current,
            dimension=pattern.dimensions[0],
            state=pattern.states[0],
            observation_id=observation_id,
        )
        return
    if pattern.family == "SNAPSHOT_PAIR":
        _assert_current_state(
            current,
            dimension=pattern.dimensions[0],
            state=pattern.states[0],
            observation_id=observation_id,
        )
        _assert_current_state(
            current,
            dimension=pattern.dimensions[1],
            state=pattern.states[1],
            observation_id=observation_id,
        )
        return
    if pattern.family != "SAME_DIMENSION_TRANSITION" or pattern.lag_minutes is None:
        _fail("EVENT_EVIDENCE_INCOMPLETE_MEMBERSHIP", "unsupported pattern family")
    dimension = pattern.dimensions[0]
    prior, now = pattern.states
    _assert_current_state(
        current,
        dimension=dimension,
        state=now,
        observation_id=observation_id,
    )
    claim = (prior, now)
    key = (dimension, pattern.lag_minutes)
    previous = transitions.get(key)
    if previous is not None and previous != claim:
        _fail(
            "EVENT_EVIDENCE_CONTRADICTORY_STATE",
            f"observation {observation_id} dimension {dimension} lag "
            f"{pattern.lag_minutes} has conflicting transition states",
        )
    transitions[key] = claim


def _assert_observation_identity(events: Sequence[_PhysicalEvent]) -> None:
    """One observation key has one availability timestamp and one state claim.

    The key is observation id, annual segment, symbol, and timeframe. Horizons
    and directions share that timestamp and those state claims. This is the
    DEC-471 bind: a feature row and every outcome horizon of that id share
    available_at_utc. It does not prove the feature row produced the state.
    """

    grouped: dict[tuple[str, str, str, str], list[_PhysicalEvent]] = {}
    for event in events:
        key = (
            event.observation_id,
            event.annual_segment_label,
            event.symbol,
            event.timeframe,
        )
        grouped.setdefault(key, []).append(event)
    for (observation_id, segment, symbol, timeframe), rows in grouped.items():
        if len({row.available_at_utc for row in rows}) != 1:
            _fail(
                "EVENT_EVIDENCE_CONTRADICTORY_OBSERVATION_TIMESTAMP",
                f"observation {observation_id} in {segment} {symbol} {timeframe} "
                "must keep one availability timestamp across horizons",
            )
        current: dict[str, str] = {}
        transitions: dict[tuple[str, int], tuple[str, str]] = {}
        for event in rows:
            for measurement in event.measurements:
                for pattern in measurement.memberships:
                    _record_state_claim(
                        pattern,
                        observation_id=observation_id,
                        current=current,
                        transitions=transitions,
                    )


def _time_key(event: _PhysicalEvent) -> tuple[object, ...]:
    return (event.available_at_utc, event.exit_timestamp_utc, event.event_identity)


def _connected_groups(events: Sequence[_PhysicalEvent]) -> tuple[tuple[_PhysicalEvent, ...], ...]:
    """Connected components of half-open outcome windows.

    Sort by availability time. Horizon is not part of the sort, so a short
    window nested inside a longer window joins that component.
    """

    ordered = tuple(sorted(events, key=_time_key))
    groups: list[list[_PhysicalEvent]] = []
    current: list[_PhysicalEvent] = []
    current_end: datetime | None = None
    for event in ordered:
        if current_end is None or event.available_at_utc >= current_end:
            if current:
                groups.append(current)
            current = [event]
            current_end = event.exit_timestamp_utc
            continue
        current.append(event)
        if event.exit_timestamp_utc > current_end:
            current_end = event.exit_timestamp_utc
    if current:
        groups.append(current)
    return tuple(tuple(group) for group in groups)


class _EndRankTree:
    """Fenwick tree of end-time ranks.

    ``greater_than(rank)`` is the number of stored ends whose rank is strictly
    above ``rank``. Half-open overlap is that query: an end equal to the next
    start does not count. The tree stores frequencies, not event pairs.
    """

    def __init__(self, size: int) -> None:
        self._tree = [0] * (size + 1)

    def add(self, index: int, delta: int) -> None:
        cursor = index + 1
        while cursor < len(self._tree):
            self._tree[cursor] += delta
            cursor += cursor & -cursor

    def prefix(self, index: int) -> int:
        if index < 0:
            return 0
        cursor = index + 1
        total = 0
        while cursor > 0:
            total += self._tree[cursor]
            cursor -= cursor & -cursor
        return total

    def greater_than(self, index: int) -> int:
        return self.prefix(len(self._tree) - 2) - self.prefix(index)


def _overlapping_pair_count(events: Sequence[_PhysicalEvent]) -> int:
    """Count half-open overlaps in O(n log n) without storing pairs.

    Sort by availability, exit, and event identity. For each event, count
    earlier ends that are strictly after its start, then record its own end.
    Equal-length windows, nested windows, chains, and touching endpoints use
    the same count. A clique is quadratic in the count and linearithmic in
    the work.
    """

    ordered = tuple(sorted(events, key=_time_key))
    if len(ordered) < 2:
        return 0
    stamps = sorted(
        {event.available_at_utc for event in ordered}
        | {event.exit_timestamp_utc for event in ordered}
    )
    rank = {stamp: index for index, stamp in enumerate(stamps)}
    tree = _EndRankTree(len(stamps))
    pairs = 0
    for event in ordered:
        pairs += tree.greater_than(rank[event.available_at_utc])
        tree.add(rank[event.exit_timestamp_utc], 1)
    return pairs


def _episode_group_id(
    *,
    scope: str,
    member_event_identities: Sequence[str],
) -> str:
    return _sha256_json(
        {
            "scheme": "overlap-component-v1",
            "scope": scope,
            "member_event_identities": list(member_event_identities),
        }
    )


def _group_payload(
    group: Sequence[_PhysicalEvent],
    *,
    scope: str,
) -> dict[str, object]:
    members = [event.event_identity for event in group]
    horizons = sorted({event.horizon_minutes for event in group})
    return {
        "episode_group_id": _episode_group_id(
            scope=scope,
            member_event_identities=sorted(members),
        ),
        "member_event_identities": members,
        "member_count": len(members),
        "horizons_minutes": horizons,
        "window_start_utc": _timestamp_text(min(event.available_at_utc for event in group)),
        "window_end_utc": _timestamp_text(max(event.exit_timestamp_utc for event in group)),
        "overlaps_inside_group": len(group) > 1,
        "statistically_independent_of_other_groups": False,
    }


def _overlap_summary(
    events: Sequence[_PhysicalEvent],
    *,
    scope: str,
) -> dict[str, object]:
    groups = _connected_groups(events)
    payloads = [_group_payload(group, scope=scope) for group in groups]
    overlapping_events = sum(group["member_count"] for group in payloads if group["member_count"] != 1)
    return {
        "unique_observed_event_count": len(events),
        "overlapping_event_count": overlapping_events,
        "overlapping_pair_count": _overlapping_pair_count(events),
        "connected_episode_group_count": len(payloads),
        "candidate_effective_independent_sample_size": len(payloads),
        "candidate_effective_independent_sample_size_is_an_independent_trial_count": False,
        "episode_groups_are_statistically_independent": False,
        "episode_groups": payloads,
    }


def _event_payload(event: _PhysicalEvent) -> dict[str, object]:
    directions: list[dict[str, object]] = []
    for measurement in event.measurements:
        memberships: list[dict[str, object]] = []
        for pattern in measurement.memberships:
            fingerprint = canonical_pattern_fingerprint(
                pattern=pattern,
                symbol=event.symbol,
                timeframe=event.timeframe,
                horizon_minutes=event.horizon_minutes,
                direction=measurement.direction,
            )
            memberships.append(
                {
                    "canonical_pattern_fingerprint": fingerprint,
                    "family": pattern.family,
                    "dimensions": list(pattern.dimensions),
                    "states": list(pattern.states),
                    "lag_minutes": pattern.lag_minutes,
                }
            )
        memberships.sort(key=lambda item: str(item["canonical_pattern_fingerprint"]))
        directions.append(
            {
                "direction": measurement.direction,
                "net_pips_0p5": measurement.net_pips_0p5,
                "net_pips_1p0": measurement.net_pips_1p0,
                "memberships": memberships,
            }
        )
    return {
        "event_identity": event.event_identity,
        "identity_scheme": IDENTITY_SCHEME,
        "recovered_from_event_fingerprint": False,
        "observation_id": event.observation_id,
        "annual_segment_label": event.annual_segment_label,
        "symbol": event.symbol,
        "timeframe": event.timeframe,
        "horizon_minutes": event.horizon_minutes,
        "available_at_utc": _timestamp_text(event.available_at_utc),
        "exit_timestamp_utc": _timestamp_text(event.exit_timestamp_utc),
        "directional_outcomes": directions,
    }


def _pattern_rows(
    events: Sequence[_PhysicalEvent],
    component_by_event: Mapping[str, str],
) -> list[dict[str, object]]:
    buckets: dict[tuple[str, str], list[_PhysicalEvent]] = {}
    definitions: dict[
        tuple[str, str],
        tuple[_PhysicalEvent, _Measurement, PatternDefinition, str],
    ] = {}
    for event in events:
        for measurement in event.measurements:
            for pattern in measurement.memberships:
                fingerprint = canonical_pattern_fingerprint(
                    pattern=pattern,
                    symbol=event.symbol,
                    timeframe=event.timeframe,
                    horizon_minutes=event.horizon_minutes,
                    direction=measurement.direction,
                )
                bucket_key = (event.annual_segment_label, fingerprint)
                buckets.setdefault(bucket_key, []).append(event)
                definitions.setdefault(
                    bucket_key,
                    (event, measurement, pattern, fingerprint),
                )
    rows: list[dict[str, object]] = []
    for bucket_key, members in buckets.items():
        event, measurement, pattern, fingerprint = definitions[bucket_key]
        ordered_members = tuple(sorted(members, key=lambda item: item.sort_key()))
        direct = _connected_groups(ordered_members)
        episode_ids = sorted(
            {component_by_event[item.event_identity] for item in ordered_members}
        )
        direct_pairs = _overlapping_pair_count(ordered_members)
        direct_overlapping = sum(len(group) for group in direct if len(group) > 1)
        rows.append(
            {
                "annual_record_id": annual_record_identity(
                    canonical_pattern_fingerprint_value=fingerprint,
                    annual_segment_label=event.annual_segment_label,
                ),
                "canonical_pattern_fingerprint": fingerprint,
                "annual_segment_label": event.annual_segment_label,
                "symbol": event.symbol,
                "timeframe": event.timeframe,
                "horizon_minutes": event.horizon_minutes,
                "direction": measurement.direction,
                "family": pattern.family,
                "dimensions": list(pattern.dimensions),
                "states": list(pattern.states),
                "lag_minutes": pattern.lag_minutes,
                "member_event_identities": [
                    item.event_identity for item in ordered_members
                ],
                "raw_membership_support": len(ordered_members),
                "unique_event_count": len(ordered_members),
                "direct_overlapping_event_count": direct_overlapping,
                "direct_overlapping_pair_count": direct_pairs,
                "direct_overlap_component_count": len(direct),
                "episode_group_ids": episode_ids,
                "candidate_effective_independent_sample_size": len(episode_ids),
                "candidate_effective_independent_sample_size_is_an_independent_trial_count": False,
                "support_counts_overlapping_events_as_separate_observations": True,
                "support_is_an_independent_trial_count": False,
                "ignores_cross_horizon_dependence": True,
                "ignores_cross_symbol_dependence": True,
                "ignores_cross_timeframe_dependence": True,
            }
        )
    rows.sort(
        key=lambda row: (
            _segment_index(str(row["annual_segment_label"])),
            _vocabulary_index(str(row["symbol"]), SYMBOLS, field="symbol"),
            _vocabulary_index(str(row["timeframe"]), TIMEFRAMES, field="timeframe"),
            int(row["horizon_minutes"]),
            tuple(DIRECTIONS).index(str(row["direction"])),
            str(row["canonical_pattern_fingerprint"]),
        )
    )
    return rows


def _hypothesis_dependence(rows: Sequence[Mapping[str, object]]) -> dict[str, object]:
    event_to_fingerprints: dict[str, set[str]] = {}
    for row in rows:
        fingerprint = str(row["canonical_pattern_fingerprint"])
        members = row["member_event_identities"]
        if not isinstance(members, list):
            _fail("EVENT_EVIDENCE_INCOMPLETE", "pattern membership is malformed")
        for event_identity in members:
            event_to_fingerprints.setdefault(str(event_identity), set()).add(fingerprint)
    shared_events = 0
    max_share = 0
    sharing_patterns: set[str] = set()
    for fingerprints in event_to_fingerprints.values():
        max_share = max(max_share, len(fingerprints))
        if len(fingerprints) > 1:
            shared_events += 1
            sharing_patterns.update(fingerprints)
    return {
        "events_shared_by_multiple_hypotheses": shared_events,
        "max_hypotheses_sharing_one_event": max_share,
        "hypotheses_that_share_an_event": len(sharing_patterns),
        "independence_across_hypotheses_established": False,
        "near_duplicate_jaccard_threshold_applied": False,
        "near_duplicate_jaccard_threshold_recorded": NEAR_DUPLICATE_JACCARD,
        "patterns_dropped": 0,
        "reason": (
            "Hypotheses that share an event are dependent observations of the "
            "same outcome window. LONG and SHORT are separate hypotheses and "
            "share the physical window. The recorded Jaccard threshold is not "
            "applied, and no pattern is dropped."
        ),
    }


def _observation_id_reuse(events: Sequence[_PhysicalEvent]) -> dict[str, object]:
    grouped: dict[str, list[_PhysicalEvent]] = {}
    for event in events:
        grouped.setdefault(event.observation_id, []).append(event)
    expected: list[dict[str, object]] = []
    unresolved: list[dict[str, object]] = []
    for observation_id in sorted(grouped):
        rows = grouped[observation_id]
        if len(rows) == 1:
            continue
        scopes = {
            (
                row.annual_segment_label,
                row.symbol,
                row.timeframe,
            )
            for row in rows
        }
        identities = [row.event_identity for row in sorted(rows, key=lambda item: item.sort_key())]
        horizons = sorted({row.horizon_minutes for row in rows})
        if len(scopes) == 1:
            segment, symbol, timeframe = next(iter(scopes))
            available = {row.available_at_utc for row in rows}
            if len(available) != 1:
                _fail(
                    "EVENT_EVIDENCE_CONTRADICTORY_OBSERVATION_TIMESTAMP",
                    f"observation {observation_id} in {segment} {symbol} {timeframe} "
                    "must keep one availability timestamp across horizons",
                )
            expected.append(
                {
                    "observation_id": observation_id,
                    "annual_segment_label": segment,
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "available_at_utc": _timestamp_text(next(iter(available))),
                    "availability_timestamp_shared": True,
                    "horizons_minutes": horizons,
                    "event_identities": identities,
                    "merged_into_one_event": False,
                    "reason": (
                        "The same observation id on more than one horizon shares "
                        "one availability timestamp and remains two events. The "
                        "horizon changes the outcome window. The windows may "
                        "overlap."
                    ),
                }
            )
            continue
        unresolved.append(
            {
                "observation_id": observation_id,
                "event_identities": identities,
                "scopes": [
                    {
                        "annual_segment_label": row.annual_segment_label,
                        "symbol": row.symbol,
                        "timeframe": row.timeframe,
                        "horizon_minutes": row.horizon_minutes,
                    }
                    for row in sorted(rows, key=lambda item: item.sort_key())
                ],
                "merged": False,
                "independence_established": False,
                "reason": (
                    "The same observation id appears in more than one symbol, "
                    "timeframe, or annual segment. The events are not merged, "
                    "and independence is not established."
                ),
            }
        )
    return {
        "expected_multi_horizon": expected,
        "unresolved_reuse": unresolved,
    }


def _membership_validation() -> dict[str, object]:
    return {
        "caller_supplied_membership_is_feature_state_proof": False,
        "feature_values_consulted": False,
        "quantile_cutpoints_available": False,
        "mutually_exclusive_current_states_rejected": True,
        "boundary": MEMBERSHIP_VALIDATION_BOUNDARY,
    }


def _authorizations() -> dict[str, bool]:
    payload = {key: value for key, value in _AUTHORIZATION_FLAGS}
    if any(payload.values()):
        _fail("EVENT_EVIDENCE_AUTHORIZATION_DRIFT", "an authorization flag is open")
    return payload


def _recorded_thresholds() -> dict[str, object]:
    return {
        "minimum_annual_evaluable_support": MIN_ANNUAL_EVALUABLE_SUPPORT,
        "minimum_cross_year_evaluable_segments": MIN_CROSS_YEAR_EVALUABLE_SEGMENTS,
        "minimum_base_positive_fraction": MIN_BASE_POSITIVE_FRACTION,
        "minimum_stress_positive_fraction": MIN_STRESS_POSITIVE_FRACTION,
        "minimum_median_annual_mean_net_pips_0p5": MIN_MEDIAN_ANNUAL_MEAN_NET_PIPS_0P5,
        "minimum_pooled_mean_net_pips_0p5": MIN_POOLED_MEAN_NET_PIPS_0P5,
        "require_pooled_stress_mean_positive": REQUIRE_POOLED_STRESS_MEAN_POSITIVE,
        "maximum_sign_flips": MAX_SIGN_FLIPS,
        "near_duplicate_jaccard": NEAR_DUPLICATE_JACCARD,
        "maximum_shortlist_per_cell_family": MAX_CROSS_YEAR_SHORTLIST_PER_CELL_FAMILY,
        "base_slippage_pips": DISCOVERY_SLIPPAGE_PIPS,
        "stress_slippage_pips": STRESS_SLIPPAGE_PIPS,
        "applied_as_event_acceptance_gate": False,
        "retuned": False,
    }


def _statistical_limits() -> dict[str, object]:
    return {
        "descriptive_fields": [
            "raw_observation_support",
            "unique_observed_event_count",
            "overlapping_event_count",
            "overlapping_pair_count",
            "connected_episode_group_count",
            "candidate_effective_independent_sample_size",
            "directional net pips",
        ],
        "statistical_inference_performed": False,
        "p_values": "UNAVAILABLE_NOT_COMPUTED",
        "confidence_intervals": "UNAVAILABLE_NOT_COMPUTED",
        "standard_errors": "UNAVAILABLE_NOT_COMPUTED",
        "multiple_comparison_adjustment": "UNAVAILABLE_NOT_COMPUTED",
        "statistical_significance_claimed": False,
        "profitability_claimed": False,
        "annual_aggregate_counts_are_significance": False,
        "episode_groups_are_statistically_independent": False,
        "search_universe_directional_hypotheses_per_annual_segment": (
            DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT
        ),
        "subsequent_requirements": {
            "serial_dependence": (
                "A later uncertainty estimate has to model dependence beyond "
                "geometric overlap. Windows that only touch, and separate "
                "episode groups, can still be serially dependent. The component "
                "count is not a variance correction."
            ),
            "multiple_hypothesis_correction": (
                "A later correction has to cover the frozen 89460-hypothesis "
                "search universe in each annual segment and the dependence "
                "among hypotheses that share events. An uncorrected p-value is "
                "not evidence of profitability."
            ),
            "selection_bias_control": (
                "Thresholds, rankings, and shortlists chosen after seeing "
                "outcomes are outside this contract. The EXP-20261118-069 "
                "false-pass counts stay a constraint and are not a new "
                "acceptance rule."
            ),
            "effective_sample_size": (
                "Raw support and the candidate component count are descriptive. "
                "Neither is an independent-trial count until a dependence model "
                "is stated and tested."
            ),
        },
    }


def _cross_scope_dependence() -> dict[str, object]:
    return {
        "cross_symbol_dependence_measured": False,
        "cross_timeframe_dependence_measured": False,
        "cross_direction_independence_established": False,
        "clock_time_overlap_across_symbols_measured": False,
        "clock_time_overlap_across_timeframes_measured": False,
        "independence_established": False,
        "reason": (
            "Events on different symbols or timeframes can share clock time "
            "and economic shocks. This contract does not measure that "
            "dependence and does not treat those scopes as independent."
        ),
    }


def _build_body(
    events: Sequence[_PhysicalEvent],
    provenance: EventEvidenceProvenance,
) -> dict[str, object]:
    within_scopes: list[dict[str, object]] = []
    component_by_event: dict[str, str] = {}
    scope_groups: dict[tuple[str, str, str, int], list[_PhysicalEvent]] = {}
    horizon_groups: dict[tuple[str, str, str], list[_PhysicalEvent]] = {}
    for event in events:
        scope_groups.setdefault(
            (
                event.annual_segment_label,
                event.symbol,
                event.timeframe,
                event.horizon_minutes,
            ),
            [],
        ).append(event)
        horizon_groups.setdefault(
            (event.annual_segment_label, event.symbol, event.timeframe),
            [],
        ).append(event)

    scope_keys = sorted(
        scope_groups,
        key=lambda key: (
            _segment_index(key[0]),
            _vocabulary_index(key[1], SYMBOLS, field="symbol"),
            _vocabulary_index(key[2], TIMEFRAMES, field="timeframe"),
            key[3],
        ),
    )
    for segment, symbol, timeframe, horizon in scope_keys:
        scoped = scope_groups[(segment, symbol, timeframe, horizon)]
        scope_id = f"{segment}|{symbol}|{timeframe}|{horizon}"
        summary = _overlap_summary(scoped, scope=f"within:{scope_id}")
        raw_support = sum(len(event.measurements) for event in scoped)
        for group in summary["episode_groups"]:
            if not isinstance(group, Mapping):
                continue
            for identity in group["member_event_identities"]:
                component_by_event[str(identity)] = str(group["episode_group_id"])
        within_scopes.append(
            {
                "scope_id": scope_id,
                "annual_segment_label": segment,
                "symbol": symbol,
                "timeframe": timeframe,
                "horizon_minutes": horizon,
                "raw_observation_support": raw_support,
                **summary,
            }
        )

    cross_horizon: list[dict[str, object]] = []
    horizon_keys = sorted(
        horizon_groups,
        key=lambda key: (
            _segment_index(key[0]),
            _vocabulary_index(key[1], SYMBOLS, field="symbol"),
            _vocabulary_index(key[2], TIMEFRAMES, field="timeframe"),
        ),
    )
    within_candidate_by_stream: dict[tuple[str, str, str], int] = {}
    for scope in within_scopes:
        stream = (
            str(scope["annual_segment_label"]),
            str(scope["symbol"]),
            str(scope["timeframe"]),
        )
        within_candidate_by_stream[stream] = within_candidate_by_stream.get(stream, 0) + int(
            scope["candidate_effective_independent_sample_size"]
        )
    for segment, symbol, timeframe in horizon_keys:
        scoped = horizon_groups[(segment, symbol, timeframe)]
        scope_id = f"{segment}|{symbol}|{timeframe}|horizons"
        summary = _overlap_summary(scoped, scope=f"cross-horizon:{scope_id}")
        multi = 0
        for group in summary["episode_groups"]:
            if isinstance(group, Mapping) and len(group["horizons_minutes"]) > 1:
                multi += 1
        within_sum = within_candidate_by_stream[(segment, symbol, timeframe)]
        cross_horizon.append(
            {
                "scope_id": scope_id,
                "annual_segment_label": segment,
                "symbol": symbol,
                "timeframe": timeframe,
                "horizons_minutes": sorted({event.horizon_minutes for event in scoped}),
                "groups_containing_multiple_horizons": multi,
                "within_horizon_candidate_sum": within_sum,
                "within_horizon_candidate_sum_is_a_global_independent_sample_size": False,
                **summary,
            }
        )

    pattern_rows = _pattern_rows(events, component_by_event)
    raw_observation_support = sum(len(event.measurements) for event in events)
    candidate_sum = sum(
        int(scope["candidate_effective_independent_sample_size"]) for scope in within_scopes
    )
    return {
        "evidence_version": EVENT_LEVEL_EVIDENCE_VERSION,
        "evidence_protocol": EVENT_LEVEL_EVIDENCE_PROTOCOL,
        "governing_method": GOVERNING_RESEARCH_METHOD,
        "pattern_tool": PATTERN_TOOL,
        "evidence_basis": EVIDENCE_BASIS,
        "structural_validation_is_independent_frozen_evidence_validation": False,
        "recovered_event_ids_from_event_fingerprint": False,
        "annual_catalogue_schema_modified": False,
        "dec470_thresholds_modified": False,
        "protocol_decision": ANNUAL_CATALOGUE_PROTOCOL_DECISION,
        "protocol_version": ANNUAL_CATALOGUE_PROTOCOL_VERSION,
        "protocol_fingerprint": protocol_fingerprint(),
        "search_universe_directional_hypotheses_per_annual_segment": (
            DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT
        ),
        "correlated_noise_calibration": {
            "experiment_id": CORRELATED_NOISE_CALIBRATION_EXPERIMENT,
            "status": "RECORDED_CONSTRAINT_NOT_A_THRESHOLD",
            "used_to_retune_dec470": False,
            "summary": CORRELATED_NOISE_CALIBRATION_SUMMARY,
        },
        "dec470_thresholds_recorded_not_applied": _recorded_thresholds(),
        "provenance": {
            "source_label": provenance.source_label,
            "code_commit": provenance.code_commit,
            "synthetic_manifest_sha256": provenance.synthetic_manifest_sha256,
            "evidence_basis": EVIDENCE_BASIS,
            "historical_artifact_read": False,
            "caller_supplied_events": True,
        },
        "outcome_window": {
            "convention": OUTCOME_WINDOW_CONVENTION,
            "exit_equals_available_plus_horizon": True,
            "touching_endpoints_count_as_overlap": False,
            "segment_exit_must_be_strictly_inside": True,
            "basis": (
                "OutcomeObservation requires exit_timestamp_utc to equal "
                "available_at_utc plus the frozen horizon. Overlap uses that "
                "half-open window. A window that only touches the next start "
                "does not overlap it."
            ),
        },
        "historical_event_recovery": {
            "possible_from_event_fingerprint": False,
            "dependency": HISTORICAL_EVENT_RECOVERY_DEPENDENCY,
        },
        "events": [_event_payload(event) for event in events],
        "pattern_memberships": pattern_rows,
        "membership_validation": _membership_validation(),
        "overlap_scopes": within_scopes,
        "cross_horizon_scopes": cross_horizon,
        "hypothesis_dependence": _hypothesis_dependence(pattern_rows),
        "cross_scope_dependence": _cross_scope_dependence(),
        "observation_id_reuse": _observation_id_reuse(events),
        "counts": {
            "event_count": len(events),
            "raw_observation_support": raw_observation_support,
            "pattern_membership_count": sum(
                int(row["raw_membership_support"]) for row in pattern_rows
            ),
            "within_horizon_scope_count": len(within_scopes),
            "sum_of_within_horizon_candidate_sizes": candidate_sum,
            "sum_of_within_horizon_candidate_sizes_is_a_global_independent_sample_size": False,
        },
        "statistical_limits": _statistical_limits(),
        "authorizations": _authorizations(),
    }


def compile_event_evidence(
    submissions: Sequence[EventObservationSubmission],
    provenance: EventEvidenceProvenance,
) -> tuple[dict[str, object], bytes]:
    """Compile a canonical event-evidence document from synthetic submissions.

    The returned document is descriptive. Its candidate sample size is the
    count of overlap-connected episode groups. Those groups are not claimed
    to be statistically independent.
    """

    if not isinstance(provenance, EventEvidenceProvenance):
        _fail("EVENT_EVIDENCE_MALFORMED_PROVENANCE", "provenance type mismatch")
    events = _collect_events(submissions)
    body = _build_body(events, provenance)
    body["content_sha256"] = _sha256_json(
        {key: value for key, value in body.items() if key != "content_sha256"}
    )
    raw = _canonical_json(body)
    validate_event_evidence(raw)
    return body, raw


def _pattern_from_payload(raw: Mapping[str, object]) -> PatternDefinition:
    family = raw.get("family")
    dimensions = raw.get("dimensions")
    states = raw.get("states")
    lag = raw.get("lag_minutes")
    if not isinstance(family, str) or not isinstance(dimensions, list) or not isinstance(states, list):
        _fail("EVENT_EVIDENCE_INCOMPLETE_MEMBERSHIP", "stored pattern membership is malformed")
    if lag is not None and (not isinstance(lag, int) or isinstance(lag, bool)):
        _fail("EVENT_EVIDENCE_INCOMPLETE_MEMBERSHIP", "stored lag is malformed")
    try:
        return PatternDefinition(
            family=family,
            dimensions=tuple(str(item) for item in dimensions),
            states=tuple(str(item) for item in states),
            lag_minutes=None if lag is None else int(lag),
        )
    except ValueError:
        _fail("EVENT_EVIDENCE_INCOMPLETE_MEMBERSHIP", "stored pattern definition is not DEC-470")
    raise AssertionError


def _submissions_from_document(
    document: Mapping[str, object],
) -> tuple[list[EventObservationSubmission], EventEvidenceProvenance]:
    provenance_raw = document.get("provenance")
    if not isinstance(provenance_raw, Mapping):
        _fail("EVENT_EVIDENCE_MALFORMED_PROVENANCE", "provenance is missing")
    provenance = EventEvidenceProvenance(
        source_label=str(provenance_raw.get("source_label")),
        code_commit=str(provenance_raw.get("code_commit")),
        synthetic_manifest_sha256=str(provenance_raw.get("synthetic_manifest_sha256")),
    )
    events = document.get("events")
    if not isinstance(events, list) or len(events) == 0:
        _fail("EVENT_EVIDENCE_INCOMPLETE", "events are missing")
    submissions: list[EventObservationSubmission] = []
    for event in events:
        if not isinstance(event, Mapping):
            _fail("EVENT_EVIDENCE_INCOMPLETE", "event row is malformed")
        available = _parse_timestamp(event.get("available_at_utc"), field="available_at_utc")
        exit_at = _parse_timestamp(event.get("exit_timestamp_utc"), field="exit_timestamp_utc")
        outcomes = event.get("directional_outcomes")
        if not isinstance(outcomes, list) or len(outcomes) == 0:
            _fail("EVENT_EVIDENCE_INCOMPLETE", "directional outcomes are missing")
        horizon = event.get("horizon_minutes")
        if not isinstance(horizon, int) or isinstance(horizon, bool):
            _fail("EVENT_EVIDENCE_MALFORMED_OBSERVATION", "horizon is malformed")
        symbol = event.get("symbol")
        timeframe = event.get("timeframe")
        observation_id = event.get("observation_id")
        segment_label = event.get("annual_segment_label")
        if not isinstance(symbol, str) or not isinstance(timeframe, str):
            _fail("EVENT_EVIDENCE_MALFORMED_OBSERVATION", "symbol or timeframe is malformed")
        if not isinstance(observation_id, str) or not isinstance(segment_label, str):
            _fail("EVENT_EVIDENCE_MALFORMED_OBSERVATION", "observation identity is malformed")
        if event.get("identity_scheme") != IDENTITY_SCHEME:
            _fail(
                "EVENT_EVIDENCE_CONTRADICTORY_EVENT_IDENTITY",
                "event identity scheme does not match observation-key-sha256-v1",
            )
        if event.get("recovered_from_event_fingerprint") is not False:
            _fail(
                "EVENT_EVIDENCE_EVENT_FINGERPRINT_RECOVERY_REFUSED",
                "event identity was not recovered from an event fingerprint",
            )
        expected_identity = event_identity_for(
            observation_id=observation_id,
            annual_segment_label=segment_label,
            symbol=symbol,
            timeframe=timeframe,
            horizon_minutes=horizon,
        )
        if event.get("event_identity") != expected_identity:
            _fail(
                "EVENT_EVIDENCE_CONTRADICTORY_EVENT_IDENTITY",
                "stored event identity does not match the observation key",
            )
        for outcome in outcomes:
            if not isinstance(outcome, Mapping):
                _fail("EVENT_EVIDENCE_INCOMPLETE", "directional outcome is malformed")
            direction = outcome.get("direction")
            if not isinstance(direction, str):
                _fail("EVENT_EVIDENCE_MALFORMED_OBSERVATION", "direction is malformed")
            memberships_raw = outcome.get("memberships")
            if not isinstance(memberships_raw, list) or len(memberships_raw) == 0:
                _fail("EVENT_EVIDENCE_INCOMPLETE_MEMBERSHIP", "stored memberships are missing")
            patterns: list[PatternDefinition] = []
            for membership in memberships_raw:
                if not isinstance(membership, Mapping):
                    _fail("EVENT_EVIDENCE_INCOMPLETE_MEMBERSHIP", "stored membership is malformed")
                pattern = _pattern_from_payload(membership)
                try:
                    fingerprint = canonical_pattern_fingerprint(
                        pattern=pattern,
                        symbol=symbol,
                        timeframe=timeframe,
                        horizon_minutes=horizon,
                        direction=direction,
                    )
                except ValueError:
                    _fail(
                        "EVENT_EVIDENCE_FINGERPRINT_MISMATCH",
                        "stored pattern cannot be fingerprinted",
                    )
                if membership.get("canonical_pattern_fingerprint") != fingerprint:
                    _fail(
                        "EVENT_EVIDENCE_FINGERPRINT_MISMATCH",
                        "stored canonical pattern fingerprint does not match the pattern",
                    )
                patterns.append(pattern)
            submissions.append(
                EventObservationSubmission(
                    observation_id=observation_id,
                    annual_segment_label=segment_label,
                    symbol=symbol,
                    timeframe=timeframe,
                    horizon_minutes=horizon,
                    available_at_utc=available,
                    exit_timestamp_utc=exit_at,
                    direction=direction,
                    net_pips_0p5=_finite_float(
                        outcome.get("net_pips_0p5"),
                        field="net_pips_0p5",
                    ),
                    net_pips_1p0=_finite_float(
                        outcome.get("net_pips_1p0"),
                        field="net_pips_1p0",
                    ),
                    memberships=tuple(patterns),
                )
            )
    return submissions, provenance


def _reject_independence_claims(document: Mapping[str, object]) -> None:
    stats = document.get("statistical_limits")
    if not isinstance(stats, Mapping):
        _fail("EVENT_EVIDENCE_INCOMPLETE", "statistical limits are missing")
    if stats.get("statistical_inference_performed") is not False:
        _fail("EVENT_EVIDENCE_INDEPENDENCE_CLAIM", "statistical inference is not available")
    if stats.get("p_values") != "UNAVAILABLE_NOT_COMPUTED":
        _fail("EVENT_EVIDENCE_INDEPENDENCE_CLAIM", "p-values are not evidence in this contract")
    if stats.get("statistical_significance_claimed") is not False:
        _fail("EVENT_EVIDENCE_INDEPENDENCE_CLAIM", "statistical significance is not claimed")
    if stats.get("profitability_claimed") is not False:
        _fail("EVENT_EVIDENCE_INDEPENDENCE_CLAIM", "profitability is not claimed")
    if stats.get("episode_groups_are_statistically_independent") is not False:
        _fail(
            "EVENT_EVIDENCE_INDEPENDENCE_CLAIM",
            "episode groups are not statistically independent",
        )
    if stats.get("annual_aggregate_counts_are_significance") is not False:
        _fail(
            "EVENT_EVIDENCE_INDEPENDENCE_CLAIM",
            "annual aggregate counts are not significance",
        )
    hypothesis = document.get("hypothesis_dependence")
    if not isinstance(hypothesis, Mapping) or hypothesis.get(
        "independence_across_hypotheses_established"
    ) is not False:
        _fail(
            "EVENT_EVIDENCE_INDEPENDENCE_CLAIM",
            "hypotheses that share structure are not established as independent",
        )
    cross_scope = document.get("cross_scope_dependence")
    if not isinstance(cross_scope, Mapping) or cross_scope.get("independence_established") is not False:
        _fail(
            "EVENT_EVIDENCE_INDEPENDENCE_CLAIM",
            "cross-symbol and cross-timeframe independence is not established",
        )
    for key in ("overlap_scopes", "cross_horizon_scopes"):
        scopes = document.get(key)
        if not isinstance(scopes, list):
            _fail("EVENT_EVIDENCE_INCOMPLETE", f"{key} is missing")
        for scope in scopes:
            if not isinstance(scope, Mapping):
                _fail("EVENT_EVIDENCE_INCOMPLETE", f"{key} row is malformed")
            if scope.get(
                "candidate_effective_independent_sample_size_is_an_independent_trial_count"
            ) is not False:
                _fail(
                    "EVENT_EVIDENCE_INDEPENDENCE_CLAIM",
                    "candidate sample size is not an independent-trial count",
                )
            if scope.get("episode_groups_are_statistically_independent") is not False:
                _fail(
                    "EVENT_EVIDENCE_INDEPENDENCE_CLAIM",
                    "episode groups are not statistically independent",
                )
            groups = scope.get("episode_groups")
            if not isinstance(groups, list):
                _fail("EVENT_EVIDENCE_INCOMPLETE", "episode groups are missing")
            for group in groups:
                if not isinstance(group, Mapping) or group.get(
                    "statistically_independent_of_other_groups"
                ) is not False:
                    _fail(
                        "EVENT_EVIDENCE_INDEPENDENCE_CLAIM",
                        "an episode group is not statistically independent of other groups",
                    )


def _object_without_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    parsed: dict[str, object] = {}
    for key, value in pairs:
        if key in parsed:
            _fail(
                "EVENT_EVIDENCE_NONCANONICAL_JSON",
                f"duplicate JSON object key {key!r}",
            )
        parsed[key] = value
    return parsed


def _parse_json_object(text: str) -> dict[str, object]:
    try:
        parsed = json.loads(text, object_pairs_hook=_object_without_duplicate_keys)
    except json.JSONDecodeError:
        _fail("EVENT_EVIDENCE_INTEGRITY", "document is not JSON")
        raise AssertionError
    if not isinstance(parsed, dict):
        _fail("EVENT_EVIDENCE_INTEGRITY", "document must be a JSON object")
    return parsed


def _require_canonical_bytes(raw: bytes) -> dict[str, object]:
    """Accept serialized evidence only when the bytes are canonical JSON."""

    if raw.startswith(b"\xef\xbb\xbf"):
        _fail("EVENT_EVIDENCE_NONCANONICAL_JSON", "UTF-8 BOM is not canonical JSON")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        _fail(
            "EVENT_EVIDENCE_NONCANONICAL_JSON",
            "serialized evidence must be canonical UTF-8 JSON",
        )
        raise AssertionError
    parsed = _parse_json_object(text)
    try:
        canonical = _canonical_json(parsed)
    except (TypeError, ValueError):
        _fail(
            "EVENT_EVIDENCE_NONCANONICAL_JSON",
            "serialized evidence is not canonical JSON",
        )
        raise AssertionError
    if raw != canonical:
        _fail(
            "EVENT_EVIDENCE_NONCANONICAL_JSON",
            "serialized evidence must match canonical JSON bytes",
        )
    return parsed


def _reject_membership_proof_claim(document: Mapping[str, object]) -> None:
    block = document.get("membership_validation")
    if not isinstance(block, Mapping):
        _fail("EVENT_EVIDENCE_INCOMPLETE", "membership validation boundary is missing")
    if block.get("caller_supplied_membership_is_feature_state_proof") is not False:
        _fail(
            "EVENT_EVIDENCE_MEMBERSHIP_BOUNDARY",
            "pattern membership is not a feature-state proof",
        )
    if block.get("feature_values_consulted") is not False:
        _fail(
            "EVENT_EVIDENCE_MEMBERSHIP_BOUNDARY",
            "feature values are not consulted",
        )
    if block.get("quantile_cutpoints_available") is not False:
        _fail(
            "EVENT_EVIDENCE_MEMBERSHIP_BOUNDARY",
            "quantile cutpoints are not available",
        )
    if block.get("mutually_exclusive_current_states_rejected") is not True:
        _fail(
            "EVENT_EVIDENCE_MEMBERSHIP_BOUNDARY",
            "mutually exclusive current states must be rejected",
        )


def validate_event_evidence(
    document: Mapping[str, object] | bytes | str,
) -> dict[str, object]:
    """Recompute the canonical document and reject tampered or incomplete evidence.

    Bytes and text are serialized evidence. They must be canonical UTF-8 JSON:
    sorted keys, compact separators, a trailing newline, no byte-order mark,
    and no duplicate object keys. A mapping is an in-memory document and is
    checked by recomputation. A passing validation means the synthetic
    document is internally consistent. It does not validate authentic frozen
    annual evidence, and it does not prove that a feature row satisfied a
    pattern.
    """

    if isinstance(document, str):
        document = document.encode("utf-8")
    if isinstance(document, bytes):
        parsed = _require_canonical_bytes(document)
    elif isinstance(document, Mapping):
        parsed = dict(document)
    else:
        _fail("EVENT_EVIDENCE_INTEGRITY", "document must be a mapping or canonical bytes")
        raise AssertionError
    if not isinstance(parsed, dict):
        _fail("EVENT_EVIDENCE_INTEGRITY", "document must be a JSON object")
    digest = parsed.get("content_sha256")
    body = {key: value for key, value in parsed.items() if key != "content_sha256"}
    if digest != _sha256_json(body):
        _fail("EVENT_EVIDENCE_INTEGRITY", "content sha256 does not match the canonical body")
    if parsed.get("evidence_basis") != EVIDENCE_BASIS:
        _fail(
            "EVENT_EVIDENCE_INTEGRITY",
            "evidence basis must stay caller-supplied synthetic events",
        )
    if parsed.get("structural_validation_is_independent_frozen_evidence_validation") is not False:
        _fail(
            "EVENT_EVIDENCE_INTEGRITY",
            "structural validation is not independent validation of frozen evidence",
        )
    if parsed.get("recovered_event_ids_from_event_fingerprint") is not False:
        _fail(
            "EVENT_EVIDENCE_EVENT_FINGERPRINT_RECOVERY_REFUSED",
            "event ids were not recovered from an event fingerprint",
        )
    _reject_independence_claims(parsed)
    _reject_membership_proof_claim(parsed)
    submissions, provenance = _submissions_from_document(parsed)
    events = _collect_events(submissions)
    rebuilt = _build_body(events, provenance)
    if rebuilt != body:
        _fail(
            "EVENT_EVIDENCE_INTEGRITY",
            "document does not match the canonical compilation of its events",
        )
    parsed["content_sha256"] = digest
    return parsed


def event_level_evidence_contract() -> dict[str, object]:
    """Static contract. It contains no observations and no inference."""

    return {
        "evidence_version": EVENT_LEVEL_EVIDENCE_VERSION,
        "evidence_protocol": EVENT_LEVEL_EVIDENCE_PROTOCOL,
        "governing_method": GOVERNING_RESEARCH_METHOD,
        "pattern_tool": PATTERN_TOOL,
        "evidence_basis": EVIDENCE_BASIS,
        "protocol_decision": ANNUAL_CATALOGUE_PROTOCOL_DECISION,
        "protocol_fingerprint": protocol_fingerprint(),
        "search_universe_directional_hypotheses_per_annual_segment": (
            DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT
        ),
        "dec470_thresholds_modified": False,
        "dec470_thresholds_recorded_not_applied": _recorded_thresholds(),
        "correlated_noise_calibration": {
            "experiment_id": CORRELATED_NOISE_CALIBRATION_EXPERIMENT,
            "status": "RECORDED_CONSTRAINT_NOT_A_THRESHOLD",
            "used_to_retune_dec470": False,
            "summary": CORRELATED_NOISE_CALIBRATION_SUMMARY,
        },
        "historical_event_recovery": {
            "possible_from_event_fingerprint": False,
            "dependency": HISTORICAL_EVENT_RECOVERY_DEPENDENCY,
        },
        "membership_validation": _membership_validation(),
        "statistical_limits": _statistical_limits(),
        "authorizations": _authorizations(),
        "annual_catalogue_schema_modified": False,
    }


if DIRECTIONAL_HYPOTHESES_PER_ANNUAL_SEGMENT != 89460:
    raise ValueError("EVENT_EVIDENCE_SEARCH_UNIVERSE_DRIFT")
if MIN_ANNUAL_EVALUABLE_SUPPORT != 75:
    raise ValueError("EVENT_EVIDENCE_THRESHOLD_DRIFT")
if MIN_CROSS_YEAR_EVALUABLE_SEGMENTS != 9:
    raise ValueError("EVENT_EVIDENCE_THRESHOLD_DRIFT")
if MIN_BASE_POSITIVE_FRACTION != 0.80:
    raise ValueError("EVENT_EVIDENCE_THRESHOLD_DRIFT")
if MIN_STRESS_POSITIVE_FRACTION != 2.0 / 3.0:
    raise ValueError("EVENT_EVIDENCE_THRESHOLD_DRIFT")
if MIN_MEDIAN_ANNUAL_MEAN_NET_PIPS_0P5 != 0.10:
    raise ValueError("EVENT_EVIDENCE_THRESHOLD_DRIFT")
if MIN_POOLED_MEAN_NET_PIPS_0P5 != 0.25:
    raise ValueError("EVENT_EVIDENCE_THRESHOLD_DRIFT")
if REQUIRE_POOLED_STRESS_MEAN_POSITIVE is not True:
    raise ValueError("EVENT_EVIDENCE_THRESHOLD_DRIFT")
if MAX_SIGN_FLIPS != 3:
    raise ValueError("EVENT_EVIDENCE_THRESHOLD_DRIFT")
if NEAR_DUPLICATE_JACCARD != 0.90:
    raise ValueError("EVENT_EVIDENCE_THRESHOLD_DRIFT")
if GOVERNING_RESEARCH_METHOD != "DISCOVERY_FIRST_ANNUAL_PATTERN_CATALOGUE":
    raise ValueError("EVENT_EVIDENCE_METHOD_DRIFT")
if any(value for _key, value in _AUTHORIZATION_FLAGS):
    raise ValueError("EVENT_EVIDENCE_AUTHORIZATION_DRIFT")


__all__ = [
    "ANNUAL_RUN_385_CONSUMED",
    "CORRELATED_NOISE_CALIBRATION_EXPERIMENT",
    "DEC629_ADOPTED",
    "DEC630_ADOPTED",
    "EVENT_LEVEL_EVIDENCE_PROTOCOL",
    "EVENT_LEVEL_EVIDENCE_VERSION",
    "EVIDENCE_BASIS",
    "HISTORICAL_ARTIFACT_READ_AUTHORIZED",
    "HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED",
    "HISTORICAL_EVENT_RECOVERY_DEPENDENCY",
    "EventEvidenceProvenance",
    "EventObservationSubmission",
    "STATISTICAL_PROMOTION_AUTHORIZED",
    "STRATEGY_V1_SYNTHESIS_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "WORKFLOW_ACTIVATION_AUTHORIZED",
    "compile_event_evidence",
    "event_identity_for",
    "event_level_evidence_contract",
    "recover_event_ids_from_event_fingerprint",
    "submission_from_outcome",
    "validate_event_evidence",
]
