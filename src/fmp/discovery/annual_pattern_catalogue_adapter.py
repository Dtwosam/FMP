from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Mapping

import polars as pl

from fmp.features.contracts import timeframe_delta
from fmp.market_learning.contracts import (
    EVIDENCE_LABEL as MARKET_EVIDENCE_LABEL,
    MARKET_FEATURE_SET_VERSION,
)
from fmp.market_learning.outcomes import MARKET_OUTCOME_SET_VERSION

from .annual_pattern_catalogue_loader import VerifiedAnnualCatalogueSegmentFrames
from .annual_pattern_catalogue_method import collection_segments
from .pattern_miner import FeatureObservation, OutcomeObservation
from .pattern_protocol import CONTINUOUS_FEATURES, HORIZONS_MINUTES, SYMBOLS, TIMEFRAMES


ANNUAL_CATALOGUE_SEGMENT_ADAPTER_DECISION = "DEC-474"
ANNUAL_CATALOGUE_SEGMENT_ADAPTER_VERSION = (
    "fmp-annual-pattern-catalogue-segment-adapter-v1"
)
SOURCE_LOADER_DECISION = "DEC-473"
SOURCE_LOADER_HEAD_SHA = "9ee09b48db7890e8f652d23d2a6e7fcfc9af1369"

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
class AdaptedAnnualCatalogueSegmentInputs:
    annual_segment_label: str
    symbol: str
    timeframe: str
    processed_manifest_sha256: str
    feature_manifest_sha256: str
    outcome_manifest_sha256: str
    feature_evidence_fingerprint: str
    outcome_evidence_fingerprint: str
    selected_feature_artifacts: tuple[str, ...]
    selected_outcome_artifacts: tuple[str, ...]
    feature_observations: tuple[FeatureObservation, ...]
    outcome_observations: tuple[OutcomeObservation, ...]


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
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


def _require_utc(value: object, *, field: str) -> datetime:
    if not isinstance(value, datetime):
        raise ValueError(f"{field} must be a datetime")
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field} must use UTC")
    return value


def _segment_bounds(label: str) -> tuple[datetime, datetime]:
    matches = [segment for segment in collection_segments() if segment.label == label]
    if len(matches) != 1:
        raise ValueError("DEC-474 annual segment label drift")
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


def _normalize_continuous_feature_value(value: object) -> object:
    if value is None:
        return None
    if (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and not math.isfinite(float(value))
    ):
        return None
    return value


def _finite_float(value: object, *, field: str) -> float:
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(float(value))
    ):
        raise ValueError(f"{field} must be finite")
    return float(value)


def _require_columns(
    frame: pl.DataFrame,
    required: tuple[str, ...],
    *,
    label: str,
) -> None:
    missing = [name for name in required if name not in frame.columns]
    if missing:
        raise ValueError(f"{label} missing required columns: {missing}")


def _validate_bundle(bundle: VerifiedAnnualCatalogueSegmentFrames) -> None:
    if bundle.symbol not in SYMBOLS:
        raise ValueError("DEC-474 unsupported bundle symbol")
    if bundle.timeframe not in TIMEFRAMES:
        raise ValueError("DEC-474 unsupported bundle timeframe")
    _segment_bounds(bundle.annual_segment_label)
    for field, value in (
        ("processed_manifest_sha256", bundle.processed_manifest_sha256),
        ("feature_manifest_sha256", bundle.feature_manifest_sha256),
        ("outcome_manifest_sha256", bundle.outcome_manifest_sha256),
        ("feature_evidence_fingerprint", bundle.feature_evidence_fingerprint),
        ("outcome_evidence_fingerprint", bundle.outcome_evidence_fingerprint),
    ):
        _validate_sha256(value, field=f"DEC-474 bundle {field}")
    if not bundle.selected_feature_artifacts:
        raise ValueError("DEC-474 selected feature artifacts cannot be empty")
    if not bundle.selected_outcome_artifacts:
        raise ValueError("DEC-474 selected outcome artifacts cannot be empty")


def _validate_common_frame_identity(
    frame: pl.DataFrame,
    *,
    bundle: VerifiedAnnualCatalogueSegmentFrames,
    label: str,
) -> None:
    if frame.is_empty():
        raise ValueError(f"{label} must not be empty")
    if set(frame["symbol"].to_list()) != {bundle.symbol}:
        raise ValueError(f"{label} symbol identity mismatch")
    if set(frame["timeframe"].to_list()) != {bundle.timeframe}:
        raise ValueError(f"{label} timeframe identity mismatch")
    if set(frame["feature_set_version"].to_list()) != {MARKET_FEATURE_SET_VERSION}:
        raise ValueError(f"{label} feature-set identity mismatch")
    processed = set(frame["processed_manifest_sha256"].to_list())
    if processed != {bundle.processed_manifest_sha256}:
        raise ValueError(f"{label} processed-manifest identity mismatch")


def _adapt_feature_frame(
    bundle: VerifiedAnnualCatalogueSegmentFrames,
) -> tuple[FeatureObservation, ...]:
    frame = bundle.feature_frame
    required = (
        *_FEATURE_IDENTITY_COLUMNS,
        *CONTINUOUS_FEATURES,
        *_SESSION_FLAG_COLUMNS,
    )
    _require_columns(frame, required, label="DEC-474 feature frame")
    _validate_common_frame_identity(frame, bundle=bundle, label="DEC-474 feature frame")
    start, end = _segment_bounds(bundle.annual_segment_label)

    unique = frame.select(
        pl.struct(["symbol", "timeframe", "bar_start_utc"]).n_unique()
    ).item()
    if unique != frame.height:
        raise ValueError("duplicate DEC-474 feature-frame identity")

    observations: list[FeatureObservation] = []
    seen: set[str] = set()
    for row in frame.sort(["bar_start_utc"]).iter_rows(named=True):
        bar_start = _require_utc(row["bar_start_utc"], field="bar_start_utc")
        available = _require_utc(row["available_at_utc"], field="available_at_utc")
        if available != bar_start + timeframe_delta(bundle.timeframe):
            raise ValueError("DEC-474 feature availability identity mismatch")
        if not (start <= available < end):
            raise ValueError("DEC-474 feature row escaped annual segment")

        observation_id = _observation_id(row)
        if observation_id in seen:
            raise ValueError("duplicate DEC-474 adapted feature observation id")
        seen.add(observation_id)

        values = {
            name: _normalize_continuous_feature_value(row[name])
            for name in CONTINUOUS_FEATURES
        }
        values.update({name: row[name] for name in _SESSION_FLAG_COLUMNS})
        observations.append(
            FeatureObservation(
                observation_id=observation_id,
                symbol=bundle.symbol,
                timeframe=bundle.timeframe,
                available_at_utc=available,
                values=values,
            )
        )
    return tuple(observations)


def _adapt_outcome_frame(
    bundle: VerifiedAnnualCatalogueSegmentFrames,
) -> tuple[OutcomeObservation, ...]:
    frame = bundle.outcome_frame
    _require_columns(frame, _OUTCOME_REQUIRED_COLUMNS, label="DEC-474 outcome frame")
    _validate_common_frame_identity(frame, bundle=bundle, label="DEC-474 outcome frame")
    if set(frame["outcome_set_version"].to_list()) != {MARKET_OUTCOME_SET_VERSION}:
        raise ValueError("DEC-474 outcome-set identity mismatch")
    if set(frame["evidence_label"].to_list()) != {MARKET_EVIDENCE_LABEL}:
        raise ValueError("DEC-474 outcome evidence label mismatch")
    start, end = _segment_bounds(bundle.annual_segment_label)

    unique = frame.select(
        pl.struct(
            ["symbol", "timeframe", "bar_start_utc", "horizon_minutes"]
        ).n_unique()
    ).item()
    if unique != frame.height:
        raise ValueError("duplicate DEC-474 outcome-frame identity")

    observations: list[OutcomeObservation] = []
    seen: set[tuple[str, int]] = set()
    for row in frame.sort(["bar_start_utc", "horizon_minutes"]).iter_rows(named=True):
        bar_start = _require_utc(row["bar_start_utc"], field="bar_start_utc")
        available = _require_utc(row["available_at_utc"], field="available_at_utc")
        exit_timestamp = _require_utc(
            row["exit_timestamp_utc"],
            field="exit_timestamp_utc",
        )
        if available != bar_start + timeframe_delta(bundle.timeframe):
            raise ValueError("DEC-474 outcome availability identity mismatch")
        if not (start <= available < end):
            raise ValueError("DEC-474 outcome row escaped annual segment")
        if exit_timestamp >= end:
            raise ValueError("DEC-474 outcome exit crossed annual segment boundary")

        horizon = row["horizon_minutes"]
        if (
            not isinstance(horizon, int)
            or isinstance(horizon, bool)
            or horizon not in HORIZONS_MINUTES
        ):
            raise ValueError("DEC-474 outcome frame contains unsupported horizon")

        observation_id = _observation_id(row)
        identity = (observation_id, horizon)
        if identity in seen:
            raise ValueError("duplicate DEC-474 adapted outcome observation id")
        seen.add(identity)

        observations.append(
            OutcomeObservation(
                observation_id=observation_id,
                symbol=bundle.symbol,
                timeframe=bundle.timeframe,
                available_at_utc=available,
                exit_timestamp_utc=exit_timestamp,
                horizon_minutes=horizon,
                long_net_pips_0p5=_finite_float(
                    row["long_net_pips_0p5"],
                    field="long_net_pips_0p5",
                ),
                short_net_pips_0p5=_finite_float(
                    row["short_net_pips_0p5"],
                    field="short_net_pips_0p5",
                ),
                long_net_pips_1p0=_finite_float(
                    row["long_net_pips_1p0"],
                    field="long_net_pips_1p0",
                ),
                short_net_pips_1p0=_finite_float(
                    row["short_net_pips_1p0"],
                    field="short_net_pips_1p0",
                ),
            )
        )
    return tuple(observations)


def adapt_verified_annual_catalogue_segment(
    bundle: VerifiedAnnualCatalogueSegmentFrames,
) -> AdaptedAnnualCatalogueSegmentInputs:
    _validate_bundle(bundle)
    feature_observations = _adapt_feature_frame(bundle)
    outcome_observations = _adapt_outcome_frame(bundle)

    feature_ids = {row.observation_id for row in feature_observations}
    missing = {
        row.observation_id
        for row in outcome_observations
        if row.observation_id not in feature_ids
    }
    if missing:
        raise ValueError("DEC-474 adapted outcome has no matching feature observation")

    return AdaptedAnnualCatalogueSegmentInputs(
        annual_segment_label=bundle.annual_segment_label,
        symbol=bundle.symbol,
        timeframe=bundle.timeframe,
        processed_manifest_sha256=bundle.processed_manifest_sha256,
        feature_manifest_sha256=bundle.feature_manifest_sha256,
        outcome_manifest_sha256=bundle.outcome_manifest_sha256,
        feature_evidence_fingerprint=bundle.feature_evidence_fingerprint,
        outcome_evidence_fingerprint=bundle.outcome_evidence_fingerprint,
        selected_feature_artifacts=bundle.selected_feature_artifacts,
        selected_outcome_artifacts=bundle.selected_outcome_artifacts,
        feature_observations=feature_observations,
        outcome_observations=outcome_observations,
    )


def adapter_contract_payload() -> dict[str, object]:
    return {
        "decision": ANNUAL_CATALOGUE_SEGMENT_ADAPTER_DECISION,
        "version": ANNUAL_CATALOGUE_SEGMENT_ADAPTER_VERSION,
        "source_loader_decision": SOURCE_LOADER_DECISION,
        "source_loader_head_sha": SOURCE_LOADER_HEAD_SHA,
        "accepts_verified_loader_bundle_only": True,
        "preserves_manifest_and_evidence_identities": True,
        "preserves_processed_source_identity": True,
        "uses_exp044_observation_identity": True,
        "normalizes_nonfinite_continuous_features_to_null": True,
        "requires_exact_feature_availability_identity": True,
        "requires_exact_outcome_horizon_identity": True,
        "enforces_annual_segment_boundaries": True,
        "historical_artifact_read_authorized": HISTORICAL_ARTIFACT_READ_AUTHORIZED,
        "historical_catalogue_execution_authorized": HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED,
        "historical_result_production_authorized": HISTORICAL_RESULT_PRODUCTION_AUTHORIZED,
        "cross_year_result_production_authorized": CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED,
        "strategy_v1_synthesis_authorized": STRATEGY_V1_SYNTHESIS_AUTHORIZED,
        "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
        "next_gate": "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_RUNTIME_WIRING",
    }


__all__ = [
    "ANNUAL_CATALOGUE_SEGMENT_ADAPTER_DECISION",
    "ANNUAL_CATALOGUE_SEGMENT_ADAPTER_VERSION",
    "AdaptedAnnualCatalogueSegmentInputs",
    "adapt_verified_annual_catalogue_segment",
    "adapter_contract_payload",
]
