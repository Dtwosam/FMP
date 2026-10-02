from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Mapping, Sequence

import polars as pl

from fmp.data.phase2.artifacts import sha256_file
from fmp.features.schema import FEATURE_COLUMNS
from fmp.market_learning.contracts import (
    EVIDENCE_LABEL as MARKET_EVIDENCE_LABEL,
    EXPERIMENT_ID as MARKET_LEARNING_EXPERIMENT_ID,
    MARKET_FEATURE_SET_VERSION,
    MARKET_HISTORY_END_EXCLUSIVE,
    MARKET_HISTORY_START,
)
from fmp.market_learning.evidence import load_feature_evidence_index
from fmp.market_learning.outcome_evidence import load_outcome_evidence_index
from fmp.market_learning.outcomes import MARKET_OUTCOME_SET_VERSION, OUTCOME_COLUMNS

from .annual_pattern_catalogue_method import (
    COLLECTION_END_INCLUSIVE,
    COLLECTION_START,
    collection_segments,
)
from .pattern_protocol import CONTINUOUS_FEATURES, HORIZONS_MINUTES, SYMBOLS, TIMEFRAMES


ANNUAL_CATALOGUE_FULL_HISTORY_LOADER_DECISION = "DEC-473"
ANNUAL_CATALOGUE_FULL_HISTORY_LOADER_VERSION = (
    "fmp-annual-pattern-catalogue-full-history-loader-v1"
)
SOURCE_EVIDENCE_DECISION = "DEC-472"
SOURCE_EVIDENCE_MERGE_SHA = "310d31183802a2c29aad3f20ad6a6aa4990d579d"

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
NEW_DATA_ACQUISITION_AUTHORIZED = False
NEW_FEATURE_MATERIALIZATION_AUTHORIZED = False
NEW_OUTCOME_MATERIALIZATION_AUTHORIZED = False

_FEATURE_READ_COLUMNS = (
    "symbol",
    "timeframe",
    "bar_start_utc",
    "available_at_utc",
    *CONTINUOUS_FEATURES,
    "is_london_new_york_overlap",
    "is_london_session",
    "is_new_york_session",
    "is_asia_session",
    "feature_set_version",
    "processed_manifest_sha256",
)

_OUTCOME_READ_COLUMNS = (
    "symbol",
    "timeframe",
    "bar_start_utc",
    "available_at_utc",
    "exit_timestamp_utc",
    "horizon_minutes",
    "long_net_pips_0p5",
    "short_net_pips_0p5",
    "long_net_pips_1p0",
    "short_net_pips_1p0",
    "feature_set_version",
    "outcome_set_version",
    "evidence_label",
    "processed_manifest_sha256",
)


@dataclass(frozen=True, slots=True)
class VerifiedAnnualCatalogueSegmentFrames:
    annual_segment_label: str
    symbol: str
    timeframe: str
    feature_frame: pl.DataFrame
    outcome_frame: pl.DataFrame
    processed_manifest_sha256: str
    feature_manifest_sha256: str
    outcome_manifest_sha256: str
    feature_evidence_fingerprint: str
    outcome_evidence_fingerprint: str
    selected_feature_artifacts: tuple[str, ...]
    selected_outcome_artifacts: tuple[str, ...]


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value


def _month_keys(start: date, end_inclusive: date) -> tuple[str, ...]:
    if start > end_inclusive:
        raise ValueError("DEC-473 month range must be non-empty")
    year = start.year
    month = start.month
    out: list[str] = []
    while (year, month) <= (end_inclusive.year, end_inclusive.month):
        out.append(f"{year:04d}-{month:02d}")
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
    return tuple(out)


FULL_HISTORY_SELECTED_MONTHS = _month_keys(COLLECTION_START, COLLECTION_END_INCLUSIVE)
FULL_HISTORY_SELECTED_MONTH_COUNT = len(FULL_HISTORY_SELECTED_MONTHS)


def _segment(label: str):
    matches = [segment for segment in collection_segments() if segment.label == label]
    if len(matches) != 1:
        raise ValueError("DEC-473 annual segment label drift")
    return matches[0]


def _segment_bounds(label: str) -> tuple[datetime, datetime]:
    segment = _segment(label)
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


def _segment_months(label: str) -> tuple[str, ...]:
    segment = _segment(label)
    return _month_keys(segment.start, segment.end_inclusive)


def _expected_paths(*, prefix: str, months: Sequence[str]) -> tuple[str, ...]:
    return tuple(
        f"{prefix}{month[:4]}/{month[5:]}.parquet"
        for month in months
    )


def _load_json(path: Path, *, label: str) -> tuple[Mapping[str, object], str]:
    try:
        raw = Path(path).read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {label}: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} root must be an object")
    return value, hashlib.sha256(raw).hexdigest()


def _validate_evidence_mapping(
    evidence: Mapping[str, object],
    *,
    label: str,
    complete_field: str,
) -> str:
    fingerprint = _validate_sha256(
        evidence.get("evidence_fingerprint"),
        field=f"{label} evidence fingerprint",
    )
    unsigned = dict(evidence)
    unsigned.pop("evidence_fingerprint", None)
    if hashlib.sha256(_canonical_json(unsigned)).hexdigest() != fingerprint:
        raise ValueError(f"{label} evidence fingerprint mismatch")
    if evidence.get("experiment_id") != MARKET_LEARNING_EXPERIMENT_ID:
        raise ValueError(f"{label} evidence experiment identity mismatch")
    if evidence.get("feature_set_version") != MARKET_FEATURE_SET_VERSION:
        raise ValueError(f"{label} evidence feature-set identity mismatch")
    if evidence.get("evidence_label") != MARKET_EVIDENCE_LABEL:
        raise ValueError(f"{label} evidence label mismatch")
    if evidence.get(complete_field) is not True:
        raise ValueError(f"{label} evidence is incomplete")
    for field in (
        "model_fit_authorized",
        "shadow_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
    ):
        if evidence.get(field) is not False:
            raise ValueError(f"{label} evidence {field} must remain false")
    return fingerprint


def _validate_cell(symbol: str, timeframe: str) -> None:
    if symbol not in SYMBOLS:
        raise ValueError("unsupported DEC-473 loader symbol")
    if timeframe not in TIMEFRAMES:
        raise ValueError("unsupported DEC-473 loader timeframe")


def _evidence_cell(
    evidence: Mapping[str, object],
    *,
    symbol: str,
    timeframe: str,
    label: str,
) -> Mapping[str, object]:
    cells = evidence.get("cells")
    if not isinstance(cells, list):
        raise ValueError(f"{label} cells must be a list")
    matches = [
        cell
        for cell in cells
        if isinstance(cell, Mapping)
        and cell.get("symbol") == symbol
        and cell.get("timeframe") == timeframe
    ]
    if len(matches) != 1:
        raise ValueError(f"{label} must contain exactly one requested cell")
    return matches[0]


def _safe_path(root: Path, relative: str, *, field: str) -> Path:
    base = Path(root).resolve()
    candidate = (base / relative).resolve()
    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise ValueError(f"{field} escapes artifact root") from exc
    return candidate


def _artifact_map(
    manifest: Mapping[str, object],
    *,
    expected_prefix: str,
    label: str,
) -> dict[str, Mapping[str, object]]:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError(f"{label} artifacts must be non-empty")
    out: dict[str, Mapping[str, object]] = {}
    for raw in artifacts:
        if not isinstance(raw, Mapping):
            raise ValueError(f"{label} artifact row must be an object")
        relative = raw.get("path")
        if (
            not isinstance(relative, str)
            or not relative.startswith(expected_prefix)
            or not relative.endswith(".parquet")
        ):
            raise ValueError(f"{label} artifact path identity mismatch")
        if relative in out:
            raise ValueError(f"{label} artifact path is duplicated")
        _validate_sha256(raw.get("sha256"), field=f"{label} artifact sha256")
        size = raw.get("size_bytes")
        rows = raw.get("row_count")
        if (
            not isinstance(size, int)
            or isinstance(size, bool)
            or size <= 0
            or not isinstance(rows, int)
            or isinstance(rows, bool)
            or rows <= 0
        ):
            raise ValueError(f"{label} artifact size/row count is invalid")
        out[relative] = raw
    return out


def _verify_selected_artifact(
    *,
    root: Path,
    relative: str,
    raw: Mapping[str, object],
    expected_schema: Sequence[str],
    label: str,
) -> Path:
    path = _safe_path(root, relative, field=f"{label} artifact path")
    if not path.is_file():
        raise ValueError(f"{label} selected artifact is missing: {relative}")
    if path.stat().st_size != raw.get("size_bytes"):
        raise ValueError(f"{label} selected artifact size mismatch: {relative}")
    if sha256_file(path) != raw.get("sha256"):
        raise ValueError(f"{label} selected artifact checksum mismatch: {relative}")
    schema = pl.read_parquet_schema(path)
    if tuple(schema.keys()) != tuple(expected_schema):
        raise ValueError(f"{label} selected artifact schema mismatch: {relative}")
    row_count = (
        pl.scan_parquet(path)
        .select(pl.len().alias("row_count"))
        .collect()
        .item()
    )
    if row_count != raw.get("row_count"):
        raise ValueError(f"{label} selected artifact row-count mismatch: {relative}")
    return path


def _load_feature_segment(
    *,
    root: Path,
    artifacts: Mapping[str, Mapping[str, object]],
    symbol: str,
    timeframe: str,
    annual_segment_label: str,
) -> tuple[pl.DataFrame, tuple[str, ...]]:
    start, end = _segment_bounds(annual_segment_label)
    prefix = (
        f"data/features/{MARKET_FEATURE_SET_VERSION}/"
        f"{symbol}/{timeframe}/"
    )
    selected = _expected_paths(
        prefix=prefix,
        months=_segment_months(annual_segment_label),
    )
    frames: list[pl.DataFrame] = []
    for relative in selected:
        raw = artifacts.get(relative)
        if raw is None:
            raise ValueError(
                f"DEC-473 feature selected artifact missing from manifest: {relative}"
            )
        path = _verify_selected_artifact(
            root=root,
            relative=relative,
            raw=raw,
            expected_schema=FEATURE_COLUMNS,
            label="DEC-473 feature",
        )
        frame = (
            pl.scan_parquet(path)
            .filter(
                (pl.col("available_at_utc") >= pl.lit(start))
                & (pl.col("available_at_utc") < pl.lit(end))
            )
            .select(list(_FEATURE_READ_COLUMNS))
            .collect()
        )
        if not frame.is_empty():
            frames.append(frame)
    if not frames:
        raise ValueError("DEC-473 selected feature segment is empty")
    combined = pl.concat(frames, how="vertical").sort(
        ["symbol", "timeframe", "bar_start_utc"]
    )
    if set(combined["symbol"].to_list()) != {symbol}:
        raise ValueError("DEC-473 selected feature symbol mismatch")
    if set(combined["timeframe"].to_list()) != {timeframe}:
        raise ValueError("DEC-473 selected feature timeframe mismatch")
    if combined.filter(
        (pl.col("available_at_utc") < pl.lit(start))
        | (pl.col("available_at_utc") >= pl.lit(end))
    ).height:
        raise ValueError("DEC-473 selected feature frame escaped annual segment")
    return combined, selected


def _load_outcome_segment(
    *,
    root: Path,
    artifacts: Mapping[str, Mapping[str, object]],
    symbol: str,
    timeframe: str,
    annual_segment_label: str,
) -> tuple[pl.DataFrame, tuple[str, ...]]:
    start, end = _segment_bounds(annual_segment_label)
    prefix = (
        f"data/market-outcomes/{MARKET_OUTCOME_SET_VERSION}/"
        f"{symbol}/{timeframe}/"
    )
    selected = _expected_paths(
        prefix=prefix,
        months=_segment_months(annual_segment_label),
    )
    frames: list[pl.DataFrame] = []
    for relative in selected:
        raw = artifacts.get(relative)
        if raw is None:
            raise ValueError(
                f"DEC-473 outcome selected artifact missing from manifest: {relative}"
            )
        path = _verify_selected_artifact(
            root=root,
            relative=relative,
            raw=raw,
            expected_schema=OUTCOME_COLUMNS,
            label="DEC-473 outcome",
        )
        frame = (
            pl.scan_parquet(path)
            .filter(
                (pl.col("available_at_utc") >= pl.lit(start))
                & (pl.col("available_at_utc") < pl.lit(end))
                & (pl.col("exit_timestamp_utc") < pl.lit(end))
                & pl.col("horizon_minutes").is_in(list(HORIZONS_MINUTES))
            )
            .select(list(_OUTCOME_READ_COLUMNS))
            .collect()
        )
        if not frame.is_empty():
            frames.append(frame)
    if not frames:
        raise ValueError("DEC-473 selected outcome segment is empty")
    combined = pl.concat(frames, how="vertical").sort(
        ["symbol", "timeframe", "bar_start_utc", "horizon_minutes"]
    )
    if set(combined["symbol"].to_list()) != {symbol}:
        raise ValueError("DEC-473 selected outcome symbol mismatch")
    if set(combined["timeframe"].to_list()) != {timeframe}:
        raise ValueError("DEC-473 selected outcome timeframe mismatch")
    if set(combined["horizon_minutes"].to_list()) != set(HORIZONS_MINUTES):
        raise ValueError("DEC-473 selected outcome horizons are incomplete")
    if combined.filter(
        (pl.col("available_at_utc") < pl.lit(start))
        | (pl.col("available_at_utc") >= pl.lit(end))
        | (pl.col("exit_timestamp_utc") >= pl.lit(end))
    ).height:
        raise ValueError("DEC-473 selected outcome frame escaped annual segment")
    return combined, selected


def load_verified_annual_catalogue_segment(
    *,
    feature_root: Path,
    outcome_root: Path,
    feature_evidence: Mapping[str, object],
    outcome_evidence: Mapping[str, object],
    symbol: str,
    timeframe: str,
    annual_segment_label: str,
) -> VerifiedAnnualCatalogueSegmentFrames:
    _validate_cell(symbol, timeframe)
    _segment(annual_segment_label)
    feature_cell = _evidence_cell(
        feature_evidence,
        symbol=symbol,
        timeframe=timeframe,
        label="EXP-044 feature evidence",
    )
    outcome_cell = _evidence_cell(
        outcome_evidence,
        symbol=symbol,
        timeframe=timeframe,
        label="EXP-044 outcome evidence",
    )
    feature_fingerprint = _validate_evidence_mapping(
        feature_evidence,
        label="EXP-044 feature",
        complete_field="feature_evidence_complete",
    )
    outcome_fingerprint = _validate_evidence_mapping(
        outcome_evidence,
        label="EXP-044 outcome",
        complete_field="outcome_evidence_complete",
    )
    if outcome_evidence.get("outcome_set_version") != MARKET_OUTCOME_SET_VERSION:
        raise ValueError("DEC-473 outcome evidence set identity mismatch")
    if outcome_evidence.get("feature_evidence_fingerprint") != feature_fingerprint:
        raise ValueError("DEC-473 outcome evidence is not bound to supplied feature evidence")

    feature_manifest, feature_manifest_sha = _load_json(
        Path(feature_root) / "manifest.json",
        label="EXP-044 feature manifest",
    )
    outcome_manifest, outcome_manifest_sha = _load_json(
        Path(outcome_root) / "manifest.json",
        label="EXP-044 outcome manifest",
    )
    if feature_manifest_sha != feature_cell.get("manifest_sha256"):
        raise ValueError("DEC-473 feature manifest does not match aggregate evidence")
    if outcome_manifest_sha != outcome_cell.get("manifest_sha256"):
        raise ValueError("DEC-473 outcome manifest does not match aggregate evidence")

    if (
        feature_manifest.get("symbol") != symbol
        or feature_manifest.get("timeframe") != timeframe
        or feature_manifest.get("feature_set_version") != MARKET_FEATURE_SET_VERSION
        or feature_manifest.get("evidence_label") != MARKET_EVIDENCE_LABEL
        or feature_manifest.get("model_training_authorized") is not False
        or feature_manifest.get("promotion_authorized") is not False
        or tuple(feature_manifest.get("schema_columns", ())) != FEATURE_COLUMNS
    ):
        raise ValueError("DEC-473 feature manifest cell identity mismatch")
    if (
        outcome_manifest.get("symbol") != symbol
        or outcome_manifest.get("timeframe") != timeframe
        or outcome_manifest.get("feature_set_version") != MARKET_FEATURE_SET_VERSION
        or outcome_manifest.get("outcome_set_version") != MARKET_OUTCOME_SET_VERSION
        or outcome_manifest.get("evidence_label") != MARKET_EVIDENCE_LABEL
        or outcome_manifest.get("model_fit_authorized") is not False
        or outcome_manifest.get("promotion_authorized") is not False
        or tuple(outcome_manifest.get("schema_columns", ())) != OUTCOME_COLUMNS
        or outcome_manifest.get("feature_evidence_fingerprint") != feature_fingerprint
    ):
        raise ValueError("DEC-473 outcome manifest cell identity mismatch")

    processed_sha = _validate_sha256(
        feature_manifest.get("processed_manifest_sha256"),
        field="feature processed_manifest_sha256",
    )
    if outcome_manifest.get("processed_manifest_sha256") != processed_sha:
        raise ValueError("DEC-473 feature/outcome manifest source identity mismatch")
    if feature_cell.get("processed_manifest_sha256") != processed_sha:
        raise ValueError("DEC-473 feature evidence source identity mismatch")
    if outcome_cell.get("processed_manifest_sha256") != processed_sha:
        raise ValueError("DEC-473 outcome evidence source identity mismatch")
    if outcome_manifest.get("feature_manifest_sha256") != feature_manifest_sha:
        raise ValueError("DEC-473 outcome manifest is not bound to feature manifest")

    feature_prefix = (
        f"data/features/{MARKET_FEATURE_SET_VERSION}/"
        f"{symbol}/{timeframe}/"
    )
    outcome_prefix = (
        f"data/market-outcomes/{MARKET_OUTCOME_SET_VERSION}/"
        f"{symbol}/{timeframe}/"
    )
    feature_artifacts = _artifact_map(
        feature_manifest,
        expected_prefix=feature_prefix,
        label="DEC-473 feature manifest",
    )
    outcome_artifacts = _artifact_map(
        outcome_manifest,
        expected_prefix=outcome_prefix,
        label="DEC-473 outcome manifest",
    )

    feature_frame, feature_selected = _load_feature_segment(
        root=Path(feature_root),
        artifacts=feature_artifacts,
        symbol=symbol,
        timeframe=timeframe,
        annual_segment_label=annual_segment_label,
    )
    outcome_frame, outcome_selected = _load_outcome_segment(
        root=Path(outcome_root),
        artifacts=outcome_artifacts,
        symbol=symbol,
        timeframe=timeframe,
        annual_segment_label=annual_segment_label,
    )

    return VerifiedAnnualCatalogueSegmentFrames(
        annual_segment_label=annual_segment_label,
        symbol=symbol,
        timeframe=timeframe,
        feature_frame=feature_frame,
        outcome_frame=outcome_frame,
        processed_manifest_sha256=processed_sha,
        feature_manifest_sha256=feature_manifest_sha,
        outcome_manifest_sha256=outcome_manifest_sha,
        feature_evidence_fingerprint=feature_fingerprint,
        outcome_evidence_fingerprint=outcome_fingerprint,
        selected_feature_artifacts=feature_selected,
        selected_outcome_artifacts=outcome_selected,
    )


def load_verified_annual_catalogue_segment_from_indexes(
    *,
    feature_root: Path,
    outcome_root: Path,
    feature_evidence_path: Path,
    outcome_evidence_path: Path,
    symbol: str,
    timeframe: str,
    annual_segment_label: str,
) -> VerifiedAnnualCatalogueSegmentFrames:
    feature_evidence = load_feature_evidence_index(Path(feature_evidence_path))
    outcome_evidence = load_outcome_evidence_index(Path(outcome_evidence_path))
    return load_verified_annual_catalogue_segment(
        feature_root=Path(feature_root),
        outcome_root=Path(outcome_root),
        feature_evidence=feature_evidence,
        outcome_evidence=outcome_evidence,
        symbol=symbol,
        timeframe=timeframe,
        annual_segment_label=annual_segment_label,
    )


def loader_contract_payload() -> dict[str, object]:
    segments = collection_segments()
    return {
        "decision": ANNUAL_CATALOGUE_FULL_HISTORY_LOADER_DECISION,
        "version": ANNUAL_CATALOGUE_FULL_HISTORY_LOADER_VERSION,
        "source_evidence_decision": SOURCE_EVIDENCE_DECISION,
        "source_evidence_merge_sha": SOURCE_EVIDENCE_MERGE_SHA,
        "source_experiment_id": MARKET_LEARNING_EXPERIMENT_ID,
        "source_feature_set_version": MARKET_FEATURE_SET_VERSION,
        "source_outcome_set_version": MARKET_OUTCOME_SET_VERSION,
        "source_evidence_label": MARKET_EVIDENCE_LABEL,
        "collection_start": COLLECTION_START.isoformat(),
        "collection_end_inclusive": COLLECTION_END_INCLUSIVE.isoformat(),
        "selected_months": list(FULL_HISTORY_SELECTED_MONTHS),
        "selected_month_count": FULL_HISTORY_SELECTED_MONTH_COUNT,
        "annual_segments": [segment.label for segment in segments],
        "annual_segment_count": len(segments),
        "loads_one_annual_segment_at_a_time": True,
        "verifies_selected_artifact_sha_size_schema_and_rows": True,
        "filters_outcomes_crossing_annual_boundary": True,
        "reuses_exp044_materialized_features": True,
        "reuses_exp044_materialized_outcomes": True,
        "new_data_acquisition_authorized": NEW_DATA_ACQUISITION_AUTHORIZED,
        "new_feature_materialization_authorized": NEW_FEATURE_MATERIALIZATION_AUTHORIZED,
        "new_outcome_materialization_authorized": NEW_OUTCOME_MATERIALIZATION_AUTHORIZED,
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
        "next_gate": "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_SEGMENT_ADAPTER",
    }


if FULL_HISTORY_SELECTED_MONTH_COUNT != 140:
    raise ValueError("DEC-473 full-history month count drift")
if MARKET_HISTORY_START != COLLECTION_START:
    raise ValueError("DEC-473 EXP-044 collection start drift")
if MARKET_HISTORY_END_EXCLUSIVE != COLLECTION_END_INCLUSIVE + timedelta(days=1):
    raise ValueError("DEC-473 EXP-044 collection end drift")
if len(collection_segments()) != 12:
    raise ValueError("DEC-473 annual segment count drift")


__all__ = [
    "ANNUAL_CATALOGUE_FULL_HISTORY_LOADER_DECISION",
    "ANNUAL_CATALOGUE_FULL_HISTORY_LOADER_VERSION",
    "FULL_HISTORY_SELECTED_MONTH_COUNT",
    "FULL_HISTORY_SELECTED_MONTHS",
    "VerifiedAnnualCatalogueSegmentFrames",
    "load_verified_annual_catalogue_segment",
    "load_verified_annual_catalogue_segment_from_indexes",
    "loader_contract_payload",
]
