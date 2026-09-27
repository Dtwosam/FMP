from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence

import polars as pl

from fmp.data.phase2.artifacts import sha256_file
from fmp.features.schema import FEATURE_COLUMNS
from fmp.market_learning.contracts import (
    EVIDENCE_LABEL as MARKET_EVIDENCE_LABEL,
    EXPERIMENT_ID as MARKET_LEARNING_EXPERIMENT_ID,
    MARKET_FEATURE_SET_VERSION,
)
from fmp.market_learning.evidence import load_feature_evidence_index
from fmp.market_learning.outcome_evidence import load_outcome_evidence_index
from fmp.market_learning.outcomes import MARKET_OUTCOME_SET_VERSION, OUTCOME_COLUMNS

from .market_learning_adapter import (
    EXP061_INPUT_END_EXCLUSIVE_UTC,
    EXP061_INPUT_START_UTC,
)
from .pattern_protocol import CONTINUOUS_FEATURES, HORIZONS_MINUTES, SYMBOLS, TIMEFRAMES


EXP061_RANGE_LIMITED_LOADER_DECISION = "DEC-273"
EXP061_SELECTED_MONTH_COUNT = 96
EXP061_SELECTED_MONTHS = tuple(
    f"{year:04d}-{month:02d}"
    for year in range(2015, 2023)
    for month in range(1, 13)
)

HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED = False
DISCOVERY_RESULT_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False

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
class VerifiedExp061CellFrames:
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


def _load_json(path: Path, *, label: str) -> tuple[Mapping[str, object], str]:
    try:
        raw = Path(path).read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {label}: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} root must be an object")
    return value, hashlib.sha256(raw).hexdigest()


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value


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
        raise ValueError("unsupported EXP-061 loader symbol")
    if timeframe not in TIMEFRAMES:
        raise ValueError("unsupported EXP-061 loader timeframe")


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


def _expected_paths(
    *,
    prefix: str,
) -> tuple[str, ...]:
    return tuple(
        f"{prefix}{month[:4]}/{month[5:]}.parquet"
        for month in EXP061_SELECTED_MONTHS
    )


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


def _load_feature_selected(
    *,
    root: Path,
    artifacts: Mapping[str, Mapping[str, object]],
    symbol: str,
    timeframe: str,
) -> tuple[pl.DataFrame, tuple[str, ...]]:
    prefix = (
        f"data/features/{MARKET_FEATURE_SET_VERSION}/"
        f"{symbol}/{timeframe}/"
    )
    selected = _expected_paths(prefix=prefix)
    if len(selected) != EXP061_SELECTED_MONTH_COUNT:
        raise ValueError("EXP-061 feature selected-month count drift")
    frames: list[pl.DataFrame] = []
    for relative in selected:
        raw = artifacts.get(relative)
        if raw is None:
            raise ValueError(f"EXP-061 feature selected artifact missing from manifest: {relative}")
        path = _verify_selected_artifact(
            root=root,
            relative=relative,
            raw=raw,
            expected_schema=FEATURE_COLUMNS,
            label="EXP-061 feature",
        )
        frame = (
            pl.scan_parquet(path)
            .filter(
                (pl.col("available_at_utc") >= pl.lit(EXP061_INPUT_START_UTC))
                & (pl.col("available_at_utc") < pl.lit(EXP061_INPUT_END_EXCLUSIVE_UTC))
            )
            .select(list(_FEATURE_READ_COLUMNS))
            .collect()
        )
        frames.append(frame)

    combined = pl.concat(frames, how="vertical").sort(
        ["symbol", "timeframe", "bar_start_utc"]
    )
    if combined.is_empty():
        raise ValueError("EXP-061 selected feature range is empty")
    if set(combined["symbol"].to_list()) != {symbol}:
        raise ValueError("EXP-061 selected feature symbol mismatch")
    if set(combined["timeframe"].to_list()) != {timeframe}:
        raise ValueError("EXP-061 selected feature timeframe mismatch")
    if combined.filter(
        (pl.col("available_at_utc") < pl.lit(EXP061_INPUT_START_UTC))
        | (pl.col("available_at_utc") >= pl.lit(EXP061_INPUT_END_EXCLUSIVE_UTC))
    ).height:
        raise ValueError("EXP-061 selected feature frame escaped frozen range")
    return combined, selected


def _load_outcome_selected(
    *,
    root: Path,
    artifacts: Mapping[str, Mapping[str, object]],
    symbol: str,
    timeframe: str,
) -> tuple[pl.DataFrame, tuple[str, ...]]:
    prefix = (
        f"data/market-outcomes/{MARKET_OUTCOME_SET_VERSION}/"
        f"{symbol}/{timeframe}/"
    )
    selected = _expected_paths(prefix=prefix)
    if len(selected) != EXP061_SELECTED_MONTH_COUNT:
        raise ValueError("EXP-061 outcome selected-month count drift")
    frames: list[pl.DataFrame] = []
    for relative in selected:
        raw = artifacts.get(relative)
        if raw is None:
            raise ValueError(f"EXP-061 outcome selected artifact missing from manifest: {relative}")
        path = _verify_selected_artifact(
            root=root,
            relative=relative,
            raw=raw,
            expected_schema=OUTCOME_COLUMNS,
            label="EXP-061 outcome",
        )
        frame = (
            pl.scan_parquet(path)
            .filter(
                (pl.col("available_at_utc") >= pl.lit(EXP061_INPUT_START_UTC))
                & (pl.col("available_at_utc") < pl.lit(EXP061_INPUT_END_EXCLUSIVE_UTC))
                & (pl.col("exit_timestamp_utc") < pl.lit(EXP061_INPUT_END_EXCLUSIVE_UTC))
                & pl.col("horizon_minutes").is_in(list(HORIZONS_MINUTES))
            )
            .select(list(_OUTCOME_READ_COLUMNS))
            .collect()
        )
        frames.append(frame)

    combined = pl.concat(frames, how="vertical").sort(
        ["symbol", "timeframe", "bar_start_utc", "horizon_minutes"]
    )
    if combined.is_empty():
        raise ValueError("EXP-061 selected outcome range is empty")
    if set(combined["symbol"].to_list()) != {symbol}:
        raise ValueError("EXP-061 selected outcome symbol mismatch")
    if set(combined["timeframe"].to_list()) != {timeframe}:
        raise ValueError("EXP-061 selected outcome timeframe mismatch")
    if set(combined["horizon_minutes"].to_list()) != set(HORIZONS_MINUTES):
        raise ValueError("EXP-061 selected outcome horizons are incomplete")
    if combined.filter(
        (pl.col("available_at_utc") < pl.lit(EXP061_INPUT_START_UTC))
        | (pl.col("available_at_utc") >= pl.lit(EXP061_INPUT_END_EXCLUSIVE_UTC))
        | (pl.col("exit_timestamp_utc") >= pl.lit(EXP061_INPUT_END_EXCLUSIVE_UTC))
    ).height:
        raise ValueError("EXP-061 selected outcome frame escaped frozen range")
    return combined, selected


def load_verified_exp061_cell(
    *,
    feature_root: Path,
    outcome_root: Path,
    feature_evidence: Mapping[str, object],
    outcome_evidence: Mapping[str, object],
    symbol: str,
    timeframe: str,
) -> VerifiedExp061CellFrames:
    _validate_cell(symbol, timeframe)
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
        raise ValueError("EXP-061 outcome evidence set identity mismatch")
    if outcome_evidence.get("feature_evidence_fingerprint") != feature_fingerprint:
        raise ValueError("EXP-061 outcome evidence is not bound to supplied feature evidence")

    feature_manifest, feature_manifest_sha = _load_json(
        Path(feature_root) / "manifest.json",
        label="EXP-044 feature manifest",
    )
    outcome_manifest, outcome_manifest_sha = _load_json(
        Path(outcome_root) / "manifest.json",
        label="EXP-044 outcome manifest",
    )
    if feature_manifest_sha != feature_cell.get("manifest_sha256"):
        raise ValueError("EXP-061 feature manifest does not match aggregate evidence")
    if outcome_manifest_sha != outcome_cell.get("manifest_sha256"):
        raise ValueError("EXP-061 outcome manifest does not match aggregate evidence")

    if (
        feature_manifest.get("symbol") != symbol
        or feature_manifest.get("timeframe") != timeframe
        or feature_manifest.get("feature_set_version") != MARKET_FEATURE_SET_VERSION
        or feature_manifest.get("evidence_label") != MARKET_EVIDENCE_LABEL
        or feature_manifest.get("model_training_authorized") is not False
        or feature_manifest.get("promotion_authorized") is not False
        or tuple(feature_manifest.get("schema_columns", ())) != FEATURE_COLUMNS
    ):
        raise ValueError("EXP-061 feature manifest cell identity mismatch")
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
        raise ValueError("EXP-061 outcome manifest cell identity mismatch")

    processed_sha = _validate_sha256(
        feature_manifest.get("processed_manifest_sha256"),
        field="feature processed_manifest_sha256",
    )
    if outcome_manifest.get("processed_manifest_sha256") != processed_sha:
        raise ValueError("EXP-061 feature/outcome manifest source identity mismatch")
    if feature_cell.get("processed_manifest_sha256") != processed_sha:
        raise ValueError("EXP-061 feature evidence source identity mismatch")
    if outcome_cell.get("processed_manifest_sha256") != processed_sha:
        raise ValueError("EXP-061 outcome evidence source identity mismatch")
    if outcome_manifest.get("feature_manifest_sha256") != feature_manifest_sha:
        raise ValueError("EXP-061 outcome manifest is not bound to feature manifest")

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
        label="EXP-061 feature manifest",
    )
    outcome_artifacts = _artifact_map(
        outcome_manifest,
        expected_prefix=outcome_prefix,
        label="EXP-061 outcome manifest",
    )

    feature_frame, feature_selected = _load_feature_selected(
        root=Path(feature_root),
        artifacts=feature_artifacts,
        symbol=symbol,
        timeframe=timeframe,
    )
    outcome_frame, outcome_selected = _load_outcome_selected(
        root=Path(outcome_root),
        artifacts=outcome_artifacts,
        symbol=symbol,
        timeframe=timeframe,
    )

    return VerifiedExp061CellFrames(
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


def load_verified_exp061_cell_from_indexes(
    *,
    feature_root: Path,
    outcome_root: Path,
    feature_evidence_path: Path,
    outcome_evidence_path: Path,
    symbol: str,
    timeframe: str,
) -> VerifiedExp061CellFrames:
    feature_evidence = load_feature_evidence_index(Path(feature_evidence_path))
    outcome_evidence = load_outcome_evidence_index(Path(outcome_evidence_path))
    return load_verified_exp061_cell(
        feature_root=Path(feature_root),
        outcome_root=Path(outcome_root),
        feature_evidence=feature_evidence,
        outcome_evidence=outcome_evidence,
        symbol=symbol,
        timeframe=timeframe,
    )


def loader_contract_payload() -> dict[str, object]:
    return {
        "decision": EXP061_RANGE_LIMITED_LOADER_DECISION,
        "selected_months": list(EXP061_SELECTED_MONTHS),
        "selected_month_count": EXP061_SELECTED_MONTH_COUNT,
        "input_start_utc": EXP061_INPUT_START_UTC.isoformat(),
        "input_end_exclusive_utc": EXP061_INPUT_END_EXCLUSIVE_UTC.isoformat(),
        "reads_2023_or_later_partitions": False,
        "filters_targets_reaching_2023_before_adapter": True,
        "historical_discovery_execution_authorized": (
            HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED
        ),
        "discovery_result_authorized": DISCOVERY_RESULT_AUTHORIZED,
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


__all__ = [
    "BROKER_MUTATION_AUTHORIZED",
    "CANDIDATE_COMPILATION_AUTHORIZED",
    "DEMO_ORDER_AUTHORIZED",
    "DISCOVERY_RESULT_AUTHORIZED",
    "EXP061_RANGE_LIMITED_LOADER_DECISION",
    "EXP061_SELECTED_MONTH_COUNT",
    "EXP061_SELECTED_MONTHS",
    "HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED",
    "LIVE_ORDER_AUTHORIZED",
    "PHASE8B_AUTHORIZED",
    "PROMOTION_AUTHORIZED",
    "REAL_MONEY_AUTHORIZED",
    "RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED",
    "TRADING_AUTHORIZED",
    "VerifiedExp061CellFrames",
    "load_verified_exp061_cell",
    "load_verified_exp061_cell_from_indexes",
    "loader_contract_payload",
]
