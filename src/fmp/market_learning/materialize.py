from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Mapping

import polars as pl

from fmp.data.phase2.artifacts import sha256_file
from fmp.data.phase2.schema import CANONICAL_SCHEMA_VERSION
from fmp.features.schema import FEATURE_COLUMNS

from .contracts import (
    EVIDENCE_LABEL,
    EXPERIMENT_ID,
    MARKET_FEATURE_SET_VERSION,
    MARKET_HISTORY_END_EXCLUSIVE,
    MARKET_HISTORY_START,
)
from .evidence import load_feature_evidence_index
from .outcomes import build_market_outcome_grid, write_market_outcome_artifacts


@dataclass(frozen=True, slots=True)
class LoadedFeatureCell:
    frame: pl.DataFrame
    manifest: Mapping[str, object]
    manifest_sha256: str


def _canonical_json_sha256(path: Path) -> tuple[Mapping[str, object], str]:
    try:
        raw = Path(path).read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON artifact: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON artifact root must be an object: {path}")
    return value, hashlib.sha256(raw).hexdigest()


def _validate_safe_path(root: Path, relative: str, *, field: str) -> Path:
    base = root.resolve()
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise ValueError(f"{field} escapes its artifact root") from exc
    return candidate


def _evidence_cell(
    evidence: Mapping[str, object],
    *,
    symbol: str,
    timeframe: str,
) -> Mapping[str, object]:
    cells = evidence.get("cells")
    if not isinstance(cells, list):
        raise ValueError("feature evidence cells must be a list")
    matches = [
        cell
        for cell in cells
        if isinstance(cell, Mapping)
        and cell.get("symbol") == symbol
        and cell.get("timeframe") == timeframe
    ]
    if len(matches) != 1:
        raise ValueError("feature evidence must contain exactly one requested cell")
    return matches[0]


def load_verified_feature_cell(
    *,
    feature_root: Path,
    feature_evidence: Mapping[str, object],
    symbol: str,
    timeframe: str,
) -> LoadedFeatureCell:
    root = Path(feature_root)
    manifest_path = root / "manifest.json"
    manifest, manifest_sha = _canonical_json_sha256(manifest_path)
    evidence_cell = _evidence_cell(
        feature_evidence,
        symbol=symbol,
        timeframe=timeframe,
    )
    if evidence_cell.get("manifest_sha256") != manifest_sha:
        raise ValueError("feature cell manifest does not match aggregate evidence")
    if manifest.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("feature cell experiment identity mismatch")
    if manifest.get("feature_set_version") != MARKET_FEATURE_SET_VERSION:
        raise ValueError("feature cell feature-set identity mismatch")
    if manifest.get("evidence_label") != EVIDENCE_LABEL:
        raise ValueError("feature cell evidence label mismatch")
    if manifest.get("untouched_oos") is not False:
        raise ValueError("feature cell cannot claim untouched OOS")
    if manifest.get("model_training_authorized") is not False:
        raise ValueError("feature cell cannot authorize model fitting")
    if manifest.get("promotion_authorized") is not False:
        raise ValueError("feature cell cannot authorize promotion")
    if manifest.get("symbol") != symbol or manifest.get("timeframe") != timeframe:
        raise ValueError("feature cell symbol/timeframe identity mismatch")
    if manifest.get("code_commit") != feature_evidence.get("code_commit"):
        raise ValueError("feature cell code commit does not match aggregate evidence")
    if (
        manifest.get("processed_manifest_sha256")
        != evidence_cell.get("processed_manifest_sha256")
    ):
        raise ValueError("feature cell Phase 2 identity does not match aggregate evidence")

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("feature cell artifacts must be a non-empty list")

    frames: list[pl.DataFrame] = []
    total_rows = 0
    paths: list[str] = []
    for raw in artifacts:
        if not isinstance(raw, Mapping):
            raise ValueError("feature cell artifact row must be an object")
        relative = raw.get("path")
        expected_sha = raw.get("sha256")
        expected_size = raw.get("size_bytes")
        expected_rows = raw.get("row_count")
        if not isinstance(relative, str) or not relative.strip():
            raise ValueError("feature cell artifact path is invalid")
        path = _validate_safe_path(root, relative, field="feature cell artifact path")
        if not path.is_file():
            raise ValueError(f"feature cell artifact is missing: {relative}")
        if (
            not isinstance(expected_size, int)
            or isinstance(expected_size, bool)
            or path.stat().st_size != expected_size
        ):
            raise ValueError(f"feature cell artifact size mismatch: {relative}")
        if not isinstance(expected_sha, str) or sha256_file(path) != expected_sha:
            raise ValueError(f"feature cell artifact checksum mismatch: {relative}")
        frame = pl.read_parquet(path)
        if tuple(frame.columns) != FEATURE_COLUMNS:
            raise ValueError(f"feature cell schema mismatch: {relative}")
        if (
            not isinstance(expected_rows, int)
            or isinstance(expected_rows, bool)
            or frame.height != expected_rows
        ):
            raise ValueError(f"feature cell row-count mismatch: {relative}")
        frames.append(frame)
        total_rows += frame.height
        paths.append(relative)

    if paths != sorted(paths) or len(paths) != len(set(paths)):
        raise ValueError("feature cell artifact paths must be sorted and unique")
    if manifest.get("row_count") != total_rows:
        raise ValueError("feature cell artifact rows do not sum to manifest row count")

    frame = pl.concat(frames, how="vertical").sort(
        ["symbol", "timeframe", "bar_start_utc"]
    )
    return LoadedFeatureCell(
        frame=frame,
        manifest=manifest,
        manifest_sha256=manifest_sha,
    )


def load_verified_minute_quotes(
    *,
    dataset_root: Path,
    processed_manifest_path: Path,
    expected_processed_manifest_sha256: str,
    symbol: str,
    start_utc: datetime,
    end_exclusive_utc: datetime,
) -> pl.DataFrame:
    if start_utc.tzinfo is None or start_utc.utcoffset() != timedelta(0):
        raise ValueError("quote start_utc must use UTC")
    if end_exclusive_utc.tzinfo is None or end_exclusive_utc.utcoffset() != timedelta(0):
        raise ValueError("quote end_exclusive_utc must use UTC")
    if start_utc >= end_exclusive_utc:
        raise ValueError("quote source range must be non-empty")

    manifest_path = Path(processed_manifest_path)
    manifest, manifest_sha = _canonical_json_sha256(manifest_path)
    if manifest_sha != expected_processed_manifest_sha256:
        raise ValueError("Phase 2 processed manifest sha256 mismatch")
    if manifest.get("schema_version") != CANONICAL_SCHEMA_VERSION:
        raise ValueError("Phase 2 canonical schema identity mismatch")
    if manifest.get("symbol") != symbol:
        raise ValueError("Phase 2 processed manifest symbol mismatch")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ValueError("Phase 2 processed manifest artifacts must be an object")

    root = Path(dataset_root)
    selected: list[tuple[str, Path, Mapping[str, object]]] = []
    for key, raw in artifacts.items():
        if not key.startswith("1m:"):
            continue
        month = key[3:]
        if not isinstance(raw, Mapping):
            raise ValueError(f"Phase 2 artifact record must be an object: {key}")
        relative = raw.get("path")
        if not isinstance(relative, str) or not relative.strip():
            raise ValueError(f"Phase 2 artifact path is invalid: {key}")
        selected.append(
            (
                month,
                _validate_safe_path(root, relative, field="Phase 2 artifact path"),
                raw,
            )
        )
    selected.sort(key=lambda item: item[0])
    if not selected:
        raise ValueError("Phase 2 manifest contains no 1m artifacts")

    frames: list[pl.DataFrame] = []
    for month, path, raw in selected:
        if not path.is_file():
            raise ValueError(f"Phase 2 1m artifact is missing: {month}")
        expected_size = raw.get("size_bytes")
        expected_sha = raw.get("sha256")
        expected_rows = raw.get("row_count")
        if (
            not isinstance(expected_size, int)
            or isinstance(expected_size, bool)
            or path.stat().st_size != expected_size
        ):
            raise ValueError(f"Phase 2 1m artifact size mismatch: {month}")
        if not isinstance(expected_sha, str) or sha256_file(path) != expected_sha:
            raise ValueError(f"Phase 2 1m artifact checksum mismatch: {month}")
        frame = pl.read_parquet(path)
        required = {"timestamp_utc", "symbol", "bid_open", "ask_open", "schema_version"}
        if not required.issubset(frame.columns):
            raise ValueError(f"Phase 2 1m artifact schema is incomplete: {month}")
        if (
            not isinstance(expected_rows, int)
            or isinstance(expected_rows, bool)
            or frame.height != expected_rows
        ):
            raise ValueError(f"Phase 2 1m artifact row-count mismatch: {month}")
        if set(frame["schema_version"].to_list()) != {CANONICAL_SCHEMA_VERSION}:
            raise ValueError(f"Phase 2 1m artifact schema identity mismatch: {month}")
        frames.append(
            frame.select(["timestamp_utc", "symbol", "bid_open", "ask_open"])
        )

    quotes = pl.concat(frames, how="vertical").filter(
        (pl.col("timestamp_utc") >= start_utc)
        & (pl.col("timestamp_utc") < end_exclusive_utc)
        & (pl.col("symbol") == symbol)
    ).sort(["symbol", "timestamp_utc"])
    if quotes.is_empty():
        raise ValueError("Phase 2 1m quote window contains no rows")
    if quotes.select(
        pl.struct(["symbol", "timestamp_utc"]).n_unique()
    ).item() != quotes.height:
        raise ValueError("duplicate Phase 2 1m quote identity")
    return quotes



_PAIR_TIMEFRAMES = ("5m", "15m", "1h")


def materialize_market_outcome_pair(
    *,
    feature_roots: Mapping[str, Path],
    feature_evidence: Mapping[str, object],
    dataset_root: Path,
    processed_manifest_path: Path,
    symbol: str,
    output_root: Path,
    code_commit: str,
) -> dict[str, dict[str, object]]:
    if tuple(sorted(feature_roots)) != tuple(sorted(_PAIR_TIMEFRAMES)):
        raise ValueError("pair outcome materialization requires exact 5m/15m/1h feature roots")

    loaded_by_timeframe: dict[str, LoadedFeatureCell] = {}
    processed_by_timeframe: dict[str, str] = {}
    min_available_values: list[datetime] = []
    max_available_values: list[datetime] = []

    for timeframe in _PAIR_TIMEFRAMES:
        loaded = load_verified_feature_cell(
            feature_root=Path(feature_roots[timeframe]),
            feature_evidence=feature_evidence,
            symbol=symbol,
            timeframe=timeframe,
        )
        evidence_cell = _evidence_cell(
            feature_evidence,
            symbol=symbol,
            timeframe=timeframe,
        )
        processed_sha = str(evidence_cell["processed_manifest_sha256"])
        loaded_by_timeframe[timeframe] = loaded
        processed_by_timeframe[timeframe] = processed_sha

        min_available = loaded.frame["available_at_utc"].min()
        max_available = loaded.frame["available_at_utc"].max()
        if not isinstance(min_available, datetime) or not isinstance(max_available, datetime):
            raise ValueError("feature availability coverage is invalid")
        min_available_values.append(min_available)
        max_available_values.append(max_available)

    processed_shas = set(processed_by_timeframe.values())
    if len(processed_shas) != 1:
        raise ValueError("pair feature cells do not share one Phase 2 processed manifest")
    processed_sha = next(iter(processed_shas))

    accepted_end = datetime(
        MARKET_HISTORY_END_EXCLUSIVE.year,
        MARKET_HISTORY_END_EXCLUSIVE.month,
        MARKET_HISTORY_END_EXCLUSIVE.day,
        tzinfo=timezone.utc,
    )
    accepted_start = datetime(
        MARKET_HISTORY_START.year,
        MARKET_HISTORY_START.month,
        MARKET_HISTORY_START.day,
        tzinfo=timezone.utc,
    )
    quote_start = max(min(min_available_values), accepted_start)
    quote_end = min(max(max_available_values) + timedelta(minutes=241), accepted_end)

    quotes = load_verified_minute_quotes(
        dataset_root=Path(dataset_root),
        processed_manifest_path=Path(processed_manifest_path),
        expected_processed_manifest_sha256=processed_sha,
        symbol=symbol,
        start_utc=quote_start,
        end_exclusive_utc=quote_end,
    )

    fingerprint = feature_evidence.get("evidence_fingerprint")
    if not isinstance(fingerprint, str):
        raise ValueError("feature evidence fingerprint is missing")

    manifests: dict[str, dict[str, object]] = {}
    base = Path(output_root)
    for timeframe in _PAIR_TIMEFRAMES:
        loaded = loaded_by_timeframe[timeframe]
        build = build_market_outcome_grid(
            loaded.frame,
            quotes,
            symbol=symbol,
            timeframe=timeframe,
        )
        manifests[timeframe] = write_market_outcome_artifacts(
            build=build,
            output_root=base / f"{symbol}-{timeframe}",
            symbol=symbol,
            timeframe=timeframe,
            code_commit=code_commit,
            feature_manifest_sha256=loaded.manifest_sha256,
            feature_evidence_fingerprint=fingerprint,
            processed_manifest_sha256=processed_sha,
        )
    return manifests


def run_market_outcome_pair_materialization(
    *,
    feature_roots: Mapping[str, Path],
    feature_evidence_path: Path,
    dataset_root: Path,
    processed_manifest_path: Path,
    symbol: str,
    output_root: Path,
    code_commit: str,
) -> dict[str, dict[str, object]]:
    evidence = load_feature_evidence_index(Path(feature_evidence_path))
    return materialize_market_outcome_pair(
        feature_roots=feature_roots,
        feature_evidence=evidence,
        dataset_root=Path(dataset_root),
        processed_manifest_path=Path(processed_manifest_path),
        symbol=symbol,
        output_root=Path(output_root),
        code_commit=code_commit,
    )


def materialize_market_outcome_cell(
    *,
    feature_root: Path,
    feature_evidence: Mapping[str, object],
    dataset_root: Path,
    processed_manifest_path: Path,
    symbol: str,
    timeframe: str,
    output_root: Path,
    code_commit: str,
) -> dict[str, object]:
    loaded = load_verified_feature_cell(
        feature_root=Path(feature_root),
        feature_evidence=feature_evidence,
        symbol=symbol,
        timeframe=timeframe,
    )
    evidence_cell = _evidence_cell(
        feature_evidence,
        symbol=symbol,
        timeframe=timeframe,
    )
    processed_sha = str(evidence_cell["processed_manifest_sha256"])
    accepted_end = datetime(
        MARKET_HISTORY_END_EXCLUSIVE.year,
        MARKET_HISTORY_END_EXCLUSIVE.month,
        MARKET_HISTORY_END_EXCLUSIVE.day,
        tzinfo=timezone.utc,
    )
    accepted_start = datetime(
        MARKET_HISTORY_START.year,
        MARKET_HISTORY_START.month,
        MARKET_HISTORY_START.day,
        tzinfo=timezone.utc,
    )
    min_available = loaded.frame["available_at_utc"].min()
    max_available = loaded.frame["available_at_utc"].max()
    if not isinstance(min_available, datetime) or not isinstance(max_available, datetime):
        raise ValueError("feature availability coverage is invalid")
    quote_start = max(min_available, accepted_start)
    quote_end = min(max_available + timedelta(minutes=241), accepted_end)

    quotes = load_verified_minute_quotes(
        dataset_root=Path(dataset_root),
        processed_manifest_path=Path(processed_manifest_path),
        expected_processed_manifest_sha256=processed_sha,
        symbol=symbol,
        start_utc=quote_start,
        end_exclusive_utc=quote_end,
    )
    build = build_market_outcome_grid(
        loaded.frame,
        quotes,
        symbol=symbol,
        timeframe=timeframe,
    )
    fingerprint = feature_evidence.get("evidence_fingerprint")
    if not isinstance(fingerprint, str):
        raise ValueError("feature evidence fingerprint is missing")
    return write_market_outcome_artifacts(
        build=build,
        output_root=Path(output_root),
        symbol=symbol,
        timeframe=timeframe,
        code_commit=code_commit,
        feature_manifest_sha256=loaded.manifest_sha256,
        feature_evidence_fingerprint=fingerprint,
        processed_manifest_sha256=processed_sha,
    )


def run_market_outcome_materialization(
    *,
    feature_root: Path,
    feature_evidence_path: Path,
    dataset_root: Path,
    processed_manifest_path: Path,
    symbol: str,
    timeframe: str,
    output_root: Path,
    code_commit: str,
) -> dict[str, object]:
    evidence = load_feature_evidence_index(Path(feature_evidence_path))
    return materialize_market_outcome_cell(
        feature_root=Path(feature_root),
        feature_evidence=evidence,
        dataset_root=Path(dataset_root),
        processed_manifest_path=Path(processed_manifest_path),
        symbol=symbol,
        timeframe=timeframe,
        output_root=Path(output_root),
        code_commit=code_commit,
    )


__all__ = [
    "LoadedFeatureCell",
    "load_verified_feature_cell",
    "load_verified_minute_quotes",
    "materialize_market_outcome_cell",
    "materialize_market_outcome_pair",
    "run_market_outcome_materialization",
    "run_market_outcome_pair_materialization",
]
