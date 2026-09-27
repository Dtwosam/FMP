from __future__ import annotations

import hashlib
import json
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
    CONTINUOUS_FEATURES,
    EXPERIMENT_ID,
    HORIZONS_MINUTES,
    SYMBOLS,
    TIMEFRAMES,
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
