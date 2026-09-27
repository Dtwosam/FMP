from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Mapping

import polars as pl

from fmp.market_learning.contracts import (
    EVIDENCE_LABEL as MARKET_EVIDENCE_LABEL,
    MARKET_FEATURE_SET_VERSION,
)
from fmp.market_learning.outcomes import MARKET_OUTCOME_SET_VERSION

from .pattern_miner import (
    BROKER_MUTATION_AUTHORIZED,
    CANDIDATE_COMPILATION_AUTHORIZED,
    DEMO_ORDER_AUTHORIZED,
    HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED,
    HISTORICAL_SOURCE_ACCESS_AUTHORIZED,
    LIVE_ORDER_AUTHORIZED,
    PHASE8B_AUTHORIZED,
    PROMOTION_AUTHORIZED,
    REAL_MONEY_AUTHORIZED,
    RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED,
    TRADING_AUTHORIZED,
    ConfirmationReport,
    DiscoveryReport,
    FeatureObservation,
    InMemoryDiscoveryResult,
    OutcomeObservation,
    PatternHypothesis,
    PatternStatistics,
    ValidationReport,
)
from .pattern_protocol import (
    CONFIRMATION_MIN_SUPPORT,
    CONTINUOUS_FEATURES,
    DIRECTIONS,
    EXPERIMENT_ID,
    HORIZONS_MINUTES,
    MAX_ADMISSIBLE_PATTERNS_PER_CELL_HORIZON,
    MAX_DISCOVERY_SHORTLIST_PER_CELL_HORIZON,
    MAX_FROZEN_PER_CELL_HORIZON,
    MIN_DISCOVERY_AGGREGATE_MEAN_NET_PIPS,
    MIN_DISCOVERY_TOTAL_SUPPORT,
    MIN_DISCOVERY_YEAR_SUPPORT,
    SYMBOLS,
    TIMEFRAMES,
    VALIDATION_MIN_POSITIVE_YEARS,
    VALIDATION_MIN_TOTAL_SUPPORT,
    VALIDATION_MIN_YEAR_SUPPORT,
    pattern_fingerprint,
    protocol_fingerprint,
)


EXP061_ADAPTER_EVIDENCE_DECISION = "DEC-272"
EXP061_CELL_EVIDENCE_VERSION = 1
EXP061_CELL_EVIDENCE_PROTOCOL = "fmp-exp061-cell-evidence-v1"

EXP061_INPUT_START_UTC = datetime(2015, 1, 1, tzinfo=timezone.utc)
EXP061_INPUT_END_EXCLUSIVE_UTC = datetime(2023, 1, 1, tzinfo=timezone.utc)

_SESSION_FLAG_COLUMNS = (
    "is_london_new_york_overlap",
    "is_london_session",
    "is_new_york_session",
    "is_asia_session",
)

_FEATURE_IDENTITY_COLUMNS = (
    "symbol",
    "timeframe",
    "bar_start_utc",
    "available_at_utc",
    "feature_set_version",
    "processed_manifest_sha256",
)

_OUTCOME_REQUIRED_COLUMNS = (
    *_FEATURE_IDENTITY_COLUMNS,
    "exit_timestamp_utc",
    "horizon_minutes",
    "long_net_pips_0p5",
    "short_net_pips_0p5",
    "long_net_pips_1p0",
    "short_net_pips_1p0",
    "outcome_set_version",
    "evidence_label",
)


@dataclass(frozen=True, slots=True)
class AdaptedCellInputs:
    symbol: str
    timeframe: str
    processed_manifest_sha256: str
    feature_observations: tuple[FeatureObservation, ...]
    outcome_observations: tuple[OutcomeObservation, ...]


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


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value


def _validate_commit(value: str) -> str:
    if len(value) != 40:
        raise ValueError("code_commit must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError("code_commit must be hexadecimal") from exc
    return value


def _require_utc(value: object, *, field: str) -> datetime:
    if not isinstance(value, datetime):
        raise ValueError(f"{field} must be a datetime")
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must use UTC")
    return value


def _observation_id(row: Mapping[str, object]) -> str:
    bar_start = _require_utc(row.get("bar_start_utc"), field="bar_start_utc")
    available = _require_utc(row.get("available_at_utc"), field="available_at_utc")
    payload = {
        "symbol": row.get("symbol"),
        "timeframe": row.get("timeframe"),
        "bar_start_utc": bar_start.isoformat(),
        "available_at_utc": available.isoformat(),
        "feature_set_version": row.get("feature_set_version"),
        "processed_manifest_sha256": row.get("processed_manifest_sha256"),
    }
    return _sha256_bytes(_canonical_json(payload))


def _validate_cell_identity(symbol: str, timeframe: str) -> None:
    if symbol not in SYMBOLS:
        raise ValueError("unsupported EXP-061 adapter symbol")
    if timeframe not in TIMEFRAMES:
        raise ValueError("unsupported EXP-061 adapter timeframe")


def _require_columns(frame: pl.DataFrame, required: tuple[str, ...], *, label: str) -> None:
    missing = [name for name in required if name not in frame.columns]
    if missing:
        raise ValueError(f"{label} missing required columns: {missing}")


def _validate_common_frame_identity(
    frame: pl.DataFrame,
    *,
    symbol: str,
    timeframe: str,
    label: str,
) -> str:
    if frame.is_empty():
        raise ValueError(f"{label} must not be empty")
    if set(frame["symbol"].to_list()) != {symbol}:
        raise ValueError(f"{label} symbol identity mismatch")
    if set(frame["timeframe"].to_list()) != {timeframe}:
        raise ValueError(f"{label} timeframe identity mismatch")
    if set(frame["feature_set_version"].to_list()) != {MARKET_FEATURE_SET_VERSION}:
        raise ValueError(f"{label} feature-set identity mismatch")
    processed = set(frame["processed_manifest_sha256"].to_list())
    if len(processed) != 1:
        raise ValueError(f"{label} processed-manifest identity is not singular")
    processed_sha = _validate_sha256(
        next(iter(processed)),
        field=f"{label} processed_manifest_sha256",
    )
    return processed_sha


def adapt_feature_frame(
    frame: pl.DataFrame,
    *,
    symbol: str,
    timeframe: str,
) -> tuple[tuple[FeatureObservation, ...], str]:
    _validate_cell_identity(symbol, timeframe)
    required = (
        *_FEATURE_IDENTITY_COLUMNS,
        *CONTINUOUS_FEATURES,
        *_SESSION_FLAG_COLUMNS,
    )
    _require_columns(frame, required, label="EXP-061 feature frame")
    processed_sha = _validate_common_frame_identity(
        frame,
        symbol=symbol,
        timeframe=timeframe,
        label="EXP-061 feature frame",
    )

    unique = frame.select(
        pl.struct(["symbol", "timeframe", "bar_start_utc"]).n_unique()
    ).item()
    if unique != frame.height:
        raise ValueError("duplicate EXP-061 feature-frame identity")

    rows = frame.sort(["bar_start_utc"]).iter_rows(named=True)
    observations: list[FeatureObservation] = []
    seen: set[str] = set()
    for row in rows:
        available = _require_utc(row["available_at_utc"], field="available_at_utc")
        if not (EXP061_INPUT_START_UTC <= available < EXP061_INPUT_END_EXCLUSIVE_UTC):
            raise ValueError("EXP-061 feature adapter received row outside 2015-2022 input range")
        observation_id = _observation_id(row)
        if observation_id in seen:
            raise ValueError("duplicate EXP-061 adapted feature observation id")
        seen.add(observation_id)
        values = {
            name: row[name]
            for name in (*CONTINUOUS_FEATURES, *_SESSION_FLAG_COLUMNS)
        }
        observations.append(
            FeatureObservation(
                observation_id=observation_id,
                symbol=symbol,
                timeframe=timeframe,
                available_at_utc=available,
                values=values,
            )
        )
    return tuple(observations), processed_sha


def adapt_outcome_frame(
    frame: pl.DataFrame,
    *,
    symbol: str,
    timeframe: str,
    expected_processed_manifest_sha256: str,
) -> tuple[OutcomeObservation, ...]:
    _validate_cell_identity(symbol, timeframe)
    expected_processed_manifest_sha256 = _validate_sha256(
        expected_processed_manifest_sha256,
        field="expected_processed_manifest_sha256",
    )
    _require_columns(frame, _OUTCOME_REQUIRED_COLUMNS, label="EXP-061 outcome frame")
    processed_sha = _validate_common_frame_identity(
        frame,
        symbol=symbol,
        timeframe=timeframe,
        label="EXP-061 outcome frame",
    )
    if processed_sha != expected_processed_manifest_sha256:
        raise ValueError("EXP-061 feature/outcome processed-manifest identity mismatch")
    if set(frame["outcome_set_version"].to_list()) != {MARKET_OUTCOME_SET_VERSION}:
        raise ValueError("EXP-061 outcome-set identity mismatch")
    if set(frame["evidence_label"].to_list()) != {MARKET_EVIDENCE_LABEL}:
        raise ValueError("EXP-061 outcome evidence label mismatch")

    unique = frame.select(
        pl.struct(
            ["symbol", "timeframe", "bar_start_utc", "horizon_minutes"]
        ).n_unique()
    ).item()
    if unique != frame.height:
        raise ValueError("duplicate EXP-061 outcome-frame identity")

    observations: list[OutcomeObservation] = []
    seen: set[tuple[str, int]] = set()
    for row in frame.sort(["bar_start_utc", "horizon_minutes"]).iter_rows(named=True):
        available = _require_utc(row["available_at_utc"], field="available_at_utc")
        exit_timestamp = _require_utc(
            row["exit_timestamp_utc"],
            field="exit_timestamp_utc",
        )
        if not (EXP061_INPUT_START_UTC <= available < EXP061_INPUT_END_EXCLUSIVE_UTC):
            raise ValueError("EXP-061 outcome adapter received row outside 2015-2022 input range")
        if exit_timestamp >= EXP061_INPUT_END_EXCLUSIVE_UTC:
            raise ValueError(
                "EXP-061 outcome adapter refuses any target that reaches reserved 2023+ history"
            )
        horizon = row["horizon_minutes"]
        if not isinstance(horizon, int) or isinstance(horizon, bool) or horizon not in HORIZONS_MINUTES:
            raise ValueError("EXP-061 outcome frame contains unsupported horizon")
        observation_id = _observation_id(row)
        identity = (observation_id, horizon)
        if identity in seen:
            raise ValueError("duplicate EXP-061 adapted outcome observation id")
        seen.add(identity)
        observations.append(
            OutcomeObservation(
                observation_id=observation_id,
                symbol=symbol,
                timeframe=timeframe,
                available_at_utc=available,
                exit_timestamp_utc=exit_timestamp,
                horizon_minutes=horizon,
                long_net_pips_0p5=float(row["long_net_pips_0p5"]),
                short_net_pips_0p5=float(row["short_net_pips_0p5"]),
                long_net_pips_1p0=float(row["long_net_pips_1p0"]),
                short_net_pips_1p0=float(row["short_net_pips_1p0"]),
            )
        )
    return tuple(observations)


def adapt_market_learning_cell(
    *,
    feature_frame: pl.DataFrame,
    outcome_frame: pl.DataFrame,
    symbol: str,
    timeframe: str,
) -> AdaptedCellInputs:
    feature_observations, processed_sha = adapt_feature_frame(
        feature_frame,
        symbol=symbol,
        timeframe=timeframe,
    )
    outcome_observations = adapt_outcome_frame(
        outcome_frame,
        symbol=symbol,
        timeframe=timeframe,
        expected_processed_manifest_sha256=processed_sha,
    )
    feature_ids = {row.observation_id for row in feature_observations}
    missing = {
        row.observation_id
        for row in outcome_observations
        if row.observation_id not in feature_ids
    }
    if missing:
        raise ValueError("EXP-061 adapted outcome has no matching feature observation")
    return AdaptedCellInputs(
        symbol=symbol,
        timeframe=timeframe,
        processed_manifest_sha256=processed_sha,
        feature_observations=feature_observations,
        outcome_observations=outcome_observations,
    )


def _stats_payload(stats: PatternStatistics) -> dict[str, object]:
    return {
        "total_support": stats.total_support,
        "year_support": [[year, count] for year, count in stats.year_support],
        "aggregate_mean_net_pips_0p5": stats.aggregate_mean_net_pips_0p5,
        "year_mean_net_pips_0p5": [
            [year, mean] for year, mean in stats.year_mean_net_pips_0p5
        ],
        "aggregate_mean_net_pips_1p0": stats.aggregate_mean_net_pips_1p0,
    }


def _hypothesis_payload(value: PatternHypothesis) -> dict[str, object]:
    return {
        "symbol": value.symbol,
        "timeframe": value.timeframe,
        "horizon_minutes": value.horizon_minutes,
        "direction": value.direction,
        "predicates": [[name, state] for name, state in value.predicates],
        "fingerprint": value.fingerprint,
        "discovery_statistics": _stats_payload(value.discovery_statistics),
    }


def _discovery_payload(value: DiscoveryReport) -> dict[str, object]:
    return {
        "symbol": value.symbol,
        "timeframe": value.timeframe,
        "horizon_minutes": value.horizon_minutes,
        "active_continuous_features": list(value.active_continuous_features),
        "enumerated_pattern_count": value.enumerated_pattern_count,
        "directional_hypothesis_count": value.directional_hypothesis_count,
        "qualifying_directional_hypothesis_count": (
            value.qualifying_directional_hypothesis_count
        ),
        "deduplicated_directional_hypothesis_count": (
            value.deduplicated_directional_hypothesis_count
        ),
        "shortlist": [_hypothesis_payload(item) for item in value.shortlist],
    }


def _confirmation_payload(value: ConfirmationReport) -> dict[str, object]:
    return {
        "evaluations": [
            {
                "pattern_fingerprint": item.hypothesis.fingerprint,
                "support": item.support,
                "mean_net_pips_0p5": item.mean_net_pips_0p5,
                "passed": item.passed,
            }
            for item in value.evaluations
        ],
        "frozen_pattern_fingerprints": [
            item.hypothesis.fingerprint for item in value.frozen
        ],
    }


def _validation_payload(value: ValidationReport) -> dict[str, object]:
    return {
        "evaluations": [
            {
                "pattern_fingerprint": item.frozen.hypothesis.fingerprint,
                "total_support": item.total_support,
                "year_support": [[year, count] for year, count in item.year_support],
                "aggregate_mean_net_pips_0p5": item.aggregate_mean_net_pips_0p5,
                "year_mean_net_pips_0p5": [
                    [year, mean] for year, mean in item.year_mean_net_pips_0p5
                ],
                "positive_year_count": item.positive_year_count,
                "passed": item.passed,
            }
            for item in value.evaluations
        ],
        "validated_pattern_fingerprints": [
            item.hypothesis.fingerprint for item in value.validated
        ],
    }


def compile_cell_evidence(
    result: InMemoryDiscoveryResult,
    *,
    code_commit: str,
    processed_manifest_sha256: str,
    feature_manifest_sha256: str,
    outcome_manifest_sha256: str,
    feature_evidence_fingerprint: str,
    outcome_evidence_fingerprint: str,
) -> dict[str, object]:
    _validate_commit(code_commit)
    _validate_sha256(
        processed_manifest_sha256,
        field="processed_manifest_sha256",
    )
    _validate_sha256(
        feature_manifest_sha256,
        field="feature_manifest_sha256",
    )
    _validate_sha256(
        outcome_manifest_sha256,
        field="outcome_manifest_sha256",
    )
    _validate_sha256(
        feature_evidence_fingerprint,
        field="feature_evidence_fingerprint",
    )
    _validate_sha256(
        outcome_evidence_fingerprint,
        field="outcome_evidence_fingerprint",
    )
    if (
        result.discovery.symbol != result.state_model.symbol
        or result.discovery.timeframe != result.state_model.timeframe
    ):
        raise ValueError("EXP-061 evidence result/state-model identity mismatch")

    evidence: dict[str, object] = {
        "evidence_version": EXP061_CELL_EVIDENCE_VERSION,
        "evidence_protocol": EXP061_CELL_EVIDENCE_PROTOCOL,
        "experiment_id": EXPERIMENT_ID,
        "protocol_fingerprint": protocol_fingerprint(),
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "code_commit": code_commit,
        "processed_manifest_sha256": processed_manifest_sha256,
        "feature_manifest_sha256": feature_manifest_sha256,
        "outcome_manifest_sha256": outcome_manifest_sha256,
        "feature_evidence_fingerprint": feature_evidence_fingerprint,
        "outcome_evidence_fingerprint": outcome_evidence_fingerprint,
        "cell": {
            "symbol": result.discovery.symbol,
            "timeframe": result.discovery.timeframe,
            "horizon_minutes": result.discovery.horizon_minutes,
        },
        "state_model": {
            "cutpoints": [
                [name, lower, upper]
                for name, lower, upper in result.state_model.cutpoints
            ],
        },
        "discovery": _discovery_payload(result.discovery),
        "confirmation": _confirmation_payload(result.confirmation),
        "validation": _validation_payload(result.validation),
        "reserved_robustness_opened": False,
        "historical_source_access_authorized": HISTORICAL_SOURCE_ACCESS_AUTHORIZED,
        "historical_discovery_execution_authorized": (
            HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED
        ),
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
    }
    evidence["evidence_fingerprint"] = _sha256_bytes(_canonical_json(evidence))
    return evidence



def _finite_float(value: object, *, field: str) -> float:
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(float(value))
    ):
        raise ValueError(f"{field} must be finite")
    return float(value)


def _nonnegative_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _positive_int(value: object, *, field: str) -> int:
    out = _nonnegative_int(value, field=field)
    if out <= 0:
        raise ValueError(f"{field} must be positive")
    return out


def _expected_pattern_count(active_continuous_count: int) -> int:
    group_sizes = [3] * active_continuous_count + [5]
    total = sum(group_sizes)
    singles = total
    pairs = total * (total - 1) // 2
    same_dimension_pairs = sum(size * (size - 1) // 2 for size in group_sizes)
    return singles + pairs - same_dimension_pairs


def _validate_year_support(
    value: object,
    *,
    years: tuple[int, ...],
    field: str,
) -> tuple[tuple[int, int], ...]:
    if not isinstance(value, list) or len(value) != len(years):
        raise ValueError(f"{field} must contain exact years")
    out: list[tuple[int, int]] = []
    for raw, year in zip(value, years):
        if (
            not isinstance(raw, list)
            or len(raw) != 2
            or raw[0] != year
        ):
            raise ValueError(f"{field} year identity mismatch")
        out.append((year, _nonnegative_int(raw[1], field=f"{field} {year} support")))
    return tuple(out)


def _validate_year_means(
    value: object,
    *,
    years: tuple[int, ...],
    field: str,
    allow_none: bool,
) -> tuple[tuple[int, float | None], ...]:
    if not isinstance(value, list) or len(value) != len(years):
        raise ValueError(f"{field} must contain exact years")
    out: list[tuple[int, float | None]] = []
    for raw, year in zip(value, years):
        if (
            not isinstance(raw, list)
            or len(raw) != 2
            or raw[0] != year
        ):
            raise ValueError(f"{field} year identity mismatch")
        mean = raw[1]
        if mean is None and allow_none:
            out.append((year, None))
        else:
            out.append((year, _finite_float(mean, field=f"{field} {year} mean")))
    return tuple(out)


def _validate_discovery_hypothesis(
    raw: object,
    *,
    symbol: str,
    timeframe: str,
    horizon_minutes: int,
) -> tuple[str, tuple[object, ...]]:
    if not isinstance(raw, Mapping):
        raise ValueError("EXP-061 discovery shortlist row must be an object")
    if (
        raw.get("symbol") != symbol
        or raw.get("timeframe") != timeframe
        or raw.get("horizon_minutes") != horizon_minutes
    ):
        raise ValueError("EXP-061 discovery shortlist cell identity mismatch")
    direction = raw.get("direction")
    if direction not in DIRECTIONS:
        raise ValueError("EXP-061 discovery shortlist direction mismatch")
    predicates_raw = raw.get("predicates")
    if not isinstance(predicates_raw, list) or not 1 <= len(predicates_raw) <= 2:
        raise ValueError("EXP-061 discovery shortlist predicate depth mismatch")
    predicates: list[tuple[str, str]] = []
    for item in predicates_raw:
        if (
            not isinstance(item, list)
            or len(item) != 2
            or not isinstance(item[0], str)
            or not isinstance(item[1], str)
        ):
            raise ValueError("EXP-061 discovery shortlist predicate is malformed")
        predicates.append((item[0], item[1]))

    expected_fingerprint = pattern_fingerprint(
        symbol=symbol,
        timeframe=timeframe,
        horizon_minutes=horizon_minutes,
        direction=str(direction),
        predicates=tuple(predicates),
    )
    if raw.get("fingerprint") != expected_fingerprint:
        raise ValueError("EXP-061 discovery shortlist fingerprint mismatch")

    stats = raw.get("discovery_statistics")
    if not isinstance(stats, Mapping):
        raise ValueError("EXP-061 discovery statistics must be an object")
    total_support = _positive_int(
        stats.get("total_support"),
        field="EXP-061 discovery total support",
    )
    year_support = _validate_year_support(
        stats.get("year_support"),
        years=(2015, 2016, 2017),
        field="EXP-061 discovery year support",
    )
    if sum(count for _, count in year_support) != total_support:
        raise ValueError("EXP-061 discovery support does not reconcile")
    if total_support < MIN_DISCOVERY_TOTAL_SUPPORT:
        raise ValueError("EXP-061 discovery shortlist fails total-support gate")
    if any(count < MIN_DISCOVERY_YEAR_SUPPORT for _, count in year_support):
        raise ValueError("EXP-061 discovery shortlist fails yearly-support gate")

    aggregate_half = _finite_float(
        stats.get("aggregate_mean_net_pips_0p5"),
        field="EXP-061 discovery aggregate 0.5-pip mean",
    )
    if aggregate_half < MIN_DISCOVERY_AGGREGATE_MEAN_NET_PIPS:
        raise ValueError("EXP-061 discovery shortlist fails aggregate economic gate")
    year_means = _validate_year_means(
        stats.get("year_mean_net_pips_0p5"),
        years=(2015, 2016, 2017),
        field="EXP-061 discovery year means",
        allow_none=False,
    )
    if any(mean is None or mean <= 0.0 for _, mean in year_means):
        raise ValueError("EXP-061 discovery shortlist fails yearly economic gate")
    aggregate_stress = _finite_float(
        stats.get("aggregate_mean_net_pips_1p0"),
        field="EXP-061 discovery aggregate 1.0-pip mean",
    )
    if aggregate_stress <= 0.0:
        raise ValueError("EXP-061 discovery shortlist fails stress gate")

    rank_key: tuple[object, ...] = (
        -min(float(mean) for _, mean in year_means if mean is not None),
        -aggregate_half,
        -aggregate_stress,
        -total_support,
        len(predicates),
        expected_fingerprint,
    )
    return expected_fingerprint, rank_key


def _validate_nested_result_semantics(value: Mapping[str, object]) -> None:
    cell = value.get("cell")
    if not isinstance(cell, Mapping):
        raise ValueError("EXP-061 cell evidence cell must be an object")
    symbol = cell.get("symbol")
    timeframe = cell.get("timeframe")
    horizon = cell.get("horizon_minutes")
    if symbol not in SYMBOLS or timeframe not in TIMEFRAMES or horizon not in HORIZONS_MINUTES:
        raise ValueError("EXP-061 cell evidence cell identity mismatch")

    state_model = value.get("state_model")
    if not isinstance(state_model, Mapping):
        raise ValueError("EXP-061 state model evidence must be an object")
    cutpoints_raw = state_model.get("cutpoints")
    if not isinstance(cutpoints_raw, list):
        raise ValueError("EXP-061 state model cutpoints must be a list")
    cutpoint_names: list[str] = []
    for raw in cutpoints_raw:
        if (
            not isinstance(raw, list)
            or len(raw) != 3
            or raw[0] not in CONTINUOUS_FEATURES
        ):
            raise ValueError("EXP-061 state model cutpoint is malformed")
        name = str(raw[0])
        lower = _finite_float(raw[1], field=f"EXP-061 {name} lower cutpoint")
        upper = _finite_float(raw[2], field=f"EXP-061 {name} upper cutpoint")
        if not lower < upper:
            raise ValueError("EXP-061 state model cutpoints must be strictly ordered")
        cutpoint_names.append(name)
    if len(cutpoint_names) != len(set(cutpoint_names)):
        raise ValueError("EXP-061 state model has duplicate dimensions")

    discovery = value.get("discovery")
    if not isinstance(discovery, Mapping):
        raise ValueError("EXP-061 discovery evidence must be an object")
    if (
        discovery.get("symbol") != symbol
        or discovery.get("timeframe") != timeframe
        or discovery.get("horizon_minutes") != horizon
    ):
        raise ValueError("EXP-061 discovery evidence cell identity mismatch")
    active = discovery.get("active_continuous_features")
    if active != cutpoint_names:
        raise ValueError("EXP-061 discovery active-feature identity mismatch")

    expected_patterns = _expected_pattern_count(len(cutpoint_names))
    if expected_patterns > MAX_ADMISSIBLE_PATTERNS_PER_CELL_HORIZON:
        raise ValueError("EXP-061 discovery expected pattern count exceeds protocol")
    if discovery.get("enumerated_pattern_count") != expected_patterns:
        raise ValueError("EXP-061 discovery enumerated pattern count mismatch")
    if discovery.get("directional_hypothesis_count") != expected_patterns * len(DIRECTIONS):
        raise ValueError("EXP-061 discovery directional search count mismatch")

    qualifying = _nonnegative_int(
        discovery.get("qualifying_directional_hypothesis_count"),
        field="EXP-061 discovery qualifying count",
    )
    deduplicated = _nonnegative_int(
        discovery.get("deduplicated_directional_hypothesis_count"),
        field="EXP-061 discovery deduplicated count",
    )
    if deduplicated > qualifying:
        raise ValueError("EXP-061 discovery deduplicated count exceeds qualifying count")

    shortlist = discovery.get("shortlist")
    if not isinstance(shortlist, list):
        raise ValueError("EXP-061 discovery shortlist must be a list")
    if len(shortlist) > MAX_DISCOVERY_SHORTLIST_PER_CELL_HORIZON:
        raise ValueError("EXP-061 discovery shortlist exceeds frozen cap")
    if len(shortlist) > deduplicated:
        raise ValueError("EXP-061 discovery shortlist exceeds deduplicated count")

    fingerprints: list[str] = []
    rank_keys: list[tuple[object, ...]] = []
    for raw in shortlist:
        fingerprint, rank_key = _validate_discovery_hypothesis(
            raw,
            symbol=str(symbol),
            timeframe=str(timeframe),
            horizon_minutes=int(horizon),
        )
        fingerprints.append(fingerprint)
        rank_keys.append(rank_key)
    if len(fingerprints) != len(set(fingerprints)):
        raise ValueError("EXP-061 discovery shortlist fingerprints are duplicated")
    if rank_keys != sorted(rank_keys):
        raise ValueError("EXP-061 discovery shortlist rank order mismatch")

    confirmation = value.get("confirmation")
    if not isinstance(confirmation, Mapping):
        raise ValueError("EXP-061 confirmation evidence must be an object")
    evaluations = confirmation.get("evaluations")
    if not isinstance(evaluations, list) or len(evaluations) != len(fingerprints):
        raise ValueError("EXP-061 confirmation evaluation inventory mismatch")
    passed_fingerprints: list[str] = []
    for raw, expected_fingerprint in zip(evaluations, fingerprints):
        if not isinstance(raw, Mapping):
            raise ValueError("EXP-061 confirmation evaluation must be an object")
        if raw.get("pattern_fingerprint") != expected_fingerprint:
            raise ValueError("EXP-061 confirmation evaluation order mismatch")
        support = _nonnegative_int(
            raw.get("support"),
            field="EXP-061 confirmation support",
        )
        mean_raw = raw.get("mean_net_pips_0p5")
        mean = None if mean_raw is None else _finite_float(
            mean_raw,
            field="EXP-061 confirmation mean",
        )
        expected_pass = (
            support >= CONFIRMATION_MIN_SUPPORT
            and mean is not None
            and mean > 0.0
        )
        if raw.get("passed") is not expected_pass:
            raise ValueError("EXP-061 confirmation pass flag mismatch")
        if expected_pass:
            passed_fingerprints.append(expected_fingerprint)

    frozen = confirmation.get("frozen_pattern_fingerprints")
    expected_frozen = passed_fingerprints[:MAX_FROZEN_PER_CELL_HORIZON]
    if frozen != expected_frozen:
        raise ValueError("EXP-061 confirmation frozen inventory mismatch")

    validation = value.get("validation")
    if not isinstance(validation, Mapping):
        raise ValueError("EXP-061 validation evidence must be an object")
    validation_evaluations = validation.get("evaluations")
    if not isinstance(validation_evaluations, list) or len(validation_evaluations) != len(expected_frozen):
        raise ValueError("EXP-061 validation evaluation inventory mismatch")

    expected_validated: list[str] = []
    for raw, expected_fingerprint in zip(validation_evaluations, expected_frozen):
        if not isinstance(raw, Mapping):
            raise ValueError("EXP-061 validation evaluation must be an object")
        if raw.get("pattern_fingerprint") != expected_fingerprint:
            raise ValueError("EXP-061 validation evaluation order mismatch")
        total_support = _nonnegative_int(
            raw.get("total_support"),
            field="EXP-061 validation total support",
        )
        year_support = _validate_year_support(
            raw.get("year_support"),
            years=(2019, 2020, 2021, 2022),
            field="EXP-061 validation year support",
        )
        if sum(count for _, count in year_support) != total_support:
            raise ValueError("EXP-061 validation support does not reconcile")

        aggregate_raw = raw.get("aggregate_mean_net_pips_0p5")
        aggregate = None if aggregate_raw is None else _finite_float(
            aggregate_raw,
            field="EXP-061 validation aggregate mean",
        )
        year_means = _validate_year_means(
            raw.get("year_mean_net_pips_0p5"),
            years=(2019, 2020, 2021, 2022),
            field="EXP-061 validation year means",
            allow_none=True,
        )
        positive_year_count = sum(
            mean is not None and mean > 0.0 for _, mean in year_means
        )
        if raw.get("positive_year_count") != positive_year_count:
            raise ValueError("EXP-061 validation positive-year count mismatch")
        expected_pass = (
            total_support >= VALIDATION_MIN_TOTAL_SUPPORT
            and all(
                count >= VALIDATION_MIN_YEAR_SUPPORT
                for _, count in year_support
            )
            and aggregate is not None
            and aggregate > 0.0
            and positive_year_count >= VALIDATION_MIN_POSITIVE_YEARS
        )
        if raw.get("passed") is not expected_pass:
            raise ValueError("EXP-061 validation pass flag mismatch")
        if expected_pass:
            expected_validated.append(expected_fingerprint)

    if validation.get("validated_pattern_fingerprints") != expected_validated:
        raise ValueError("EXP-061 validation accepted inventory mismatch")


def validate_cell_evidence(value: Mapping[str, object]) -> Mapping[str, object]:
    fingerprint = _validate_sha256(
        value.get("evidence_fingerprint"),
        field="EXP-061 cell evidence fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("evidence_fingerprint", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("EXP-061 cell evidence fingerprint mismatch")
    if value.get("evidence_version") != EXP061_CELL_EVIDENCE_VERSION:
        raise ValueError("EXP-061 cell evidence version mismatch")
    if value.get("evidence_protocol") != EXP061_CELL_EVIDENCE_PROTOCOL:
        raise ValueError("EXP-061 cell evidence protocol mismatch")
    if value.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("EXP-061 cell evidence experiment mismatch")
    if value.get("protocol_fingerprint") != protocol_fingerprint():
        raise ValueError("EXP-061 cell evidence protocol fingerprint mismatch")
    if value.get("evidence_label") != "RETROSPECTIVE_ALREADY_SEEN":
        raise ValueError("EXP-061 cell evidence label mismatch")
    if value.get("untouched_oos") is not False:
        raise ValueError("EXP-061 cell evidence cannot claim untouched OOS")
    if value.get("reserved_robustness_opened") is not False:
        raise ValueError("EXP-061 cell evidence cannot open reserved robustness")
    for field in (
        "historical_source_access_authorized",
        "historical_discovery_execution_authorized",
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
        if value.get(field) is not False:
            raise ValueError(f"EXP-061 cell evidence {field} must remain false")
    _validate_commit(str(value.get("code_commit")))
    for field in (
        "processed_manifest_sha256",
        "feature_manifest_sha256",
        "outcome_manifest_sha256",
        "feature_evidence_fingerprint",
        "outcome_evidence_fingerprint",
    ):
        _validate_sha256(value.get(field), field=field)
    _validate_nested_result_semantics(value)
    return value


__all__ = [
    "AdaptedCellInputs",
    "EXP061_ADAPTER_EVIDENCE_DECISION",
    "EXP061_CELL_EVIDENCE_PROTOCOL",
    "EXP061_CELL_EVIDENCE_VERSION",
    "EXP061_INPUT_END_EXCLUSIVE_UTC",
    "EXP061_INPUT_START_UTC",
    "adapt_feature_frame",
    "adapt_market_learning_cell",
    "adapt_outcome_frame",
    "compile_cell_evidence",
    "validate_cell_evidence",
]
