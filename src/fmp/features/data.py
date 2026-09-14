from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable, Mapping

import polars as pl

from .contracts import (
    PROCESSED_SCHEMA_VERSION,
    validate_source_range,
    validate_symbol,
    validate_timeframe,
)

_REQUIRED_COLUMNS = (
    "timestamp_utc",
    "symbol",
    "bid_open",
    "bid_high",
    "bid_low",
    "bid_close",
    "ask_open",
    "ask_high",
    "ask_low",
    "ask_close",
    "source_minutes",
    "expected_open_minutes",
    "is_complete",
    "timeframe",
    "schema_version",
)


@dataclass(frozen=True, slots=True)
class LoadedFeatureSource:
    frame: pl.DataFrame
    processed_manifest_sha256: str
    opened_months: tuple[str, ...]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _month_bounds(month_key: str) -> tuple[date, date]:
    try:
        year_text, month_text = month_key.split("-", 1)
        year = int(year_text)
        month = int(month_text)
        start = date(year, month, 1)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid processed artifact month key: {month_key!r}") from exc
    if month == 12:
        return start, date(year + 1, 1, 1)
    return start, date(year, month + 1, 1)


def _load_manifest(path: Path) -> tuple[Mapping[str, object], str]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read processed manifest: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError("processed manifest root must be an object")
    return value, _sha256_bytes(raw)


def _select_artifacts(
    *,
    dataset_root: Path,
    artifacts: Mapping[str, object],
    timeframe: str,
    start: date,
    end_exclusive: date,
) -> list[tuple[str, Path, Mapping[str, object]]]:
    prefix = f"{timeframe}:"
    root_resolved = dataset_root.resolve()
    selected: list[tuple[str, Path, Mapping[str, object]]] = []
    for key, raw_record in artifacts.items():
        if not key.startswith(prefix):
            continue
        month_key = key[len(prefix) :]
        month_start, month_end = _month_bounds(month_key)
        if month_end <= start or month_start >= end_exclusive:
            continue
        # The request range was validated before manifest I/O. This second guard
        # protects against a malformed/mislabeled manifest selecting a locked month.
        if month_start >= date(2024, 1, 1):
            raise ValueError("Phase 5 final-test lock: refusing to open a 2024+ processed partition")
        if not isinstance(raw_record, Mapping):
            raise ValueError(f"processed artifact record must be an object: {key}")
        raw_path = raw_record.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise ValueError(f"processed artifact path is missing: {key}")
        candidate = (dataset_root / raw_path).resolve()
        try:
            candidate.relative_to(root_resolved)
        except ValueError as exc:
            raise ValueError(f"processed artifact path escapes dataset root: {key}") from exc
        selected.append((month_key, candidate, raw_record))
    selected.sort(key=lambda item: item[0])
    if not selected:
        raise ValueError(f"processed manifest has no {timeframe} artifacts overlapping requested range")
    return selected


def load_feature_source(
    *,
    dataset_root: Path,
    manifest_path: Path,
    symbol: str,
    timeframe: str,
    start: date,
    end_exclusive: date,
    parquet_reader: Callable[[Path], pl.DataFrame] = pl.read_parquet,
) -> LoadedFeatureSource:
    # Order is intentional: all user-controlled scope is rejected before the
    # manifest or any Parquet source can be opened.
    validate_symbol(symbol)
    validate_timeframe(timeframe)
    validate_source_range(start, end_exclusive)

    root = Path(dataset_root)
    manifest, manifest_sha = _load_manifest(Path(manifest_path))
    if manifest.get("schema_version") != PROCESSED_SCHEMA_VERSION:
        raise ValueError("processed manifest schema identity does not match Phase 2")
    if manifest.get("symbol") != symbol:
        raise ValueError("processed manifest symbol does not match requested symbol")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ValueError("processed manifest artifacts must be an object")

    selected = _select_artifacts(
        dataset_root=root,
        artifacts=artifacts,
        timeframe=timeframe,
        start=start,
        end_exclusive=end_exclusive,
    )

    # Validate every selected path/identity before the first Parquet open. This
    # makes the reader fail closed rather than partially consuming a bad set.
    for month_key, path, record in selected:
        if not path.is_file():
            raise ValueError(f"processed artifact file is missing: {timeframe}:{month_key}")
        size = record.get("size_bytes")
        if isinstance(size, int) and not isinstance(size, bool) and path.stat().st_size != size:
            raise ValueError(f"processed artifact size mismatch: {timeframe}:{month_key}")
        expected_sha = record.get("sha256")
        if isinstance(expected_sha, str) and expected_sha and _sha256_file(path) != expected_sha:
            raise ValueError(f"processed artifact checksum mismatch: {timeframe}:{month_key}")

    frames = [parquet_reader(path) for _, path, _ in selected]
    frame = pl.concat(frames, how="vertical") if len(frames) > 1 else frames[0]
    missing = [name for name in _REQUIRED_COLUMNS if name not in frame.columns]
    if missing:
        raise ValueError(f"processed feature source is missing required columns: {missing}")
    if set(frame["symbol"].to_list()) != {symbol}:
        raise ValueError("processed feature source contains a different symbol")
    if set(frame["timeframe"].to_list()) != {timeframe}:
        raise ValueError("processed feature source contains a different timeframe")
    if set(frame["schema_version"].to_list()) != {"fmp-derived-bars-v1"}:
        raise ValueError("processed feature source derived-bar schema mismatch")

    start_utc = datetime(start.year, start.month, start.day, tzinfo=timezone.utc)
    end_utc = datetime(end_exclusive.year, end_exclusive.month, end_exclusive.day, tzinfo=timezone.utc)
    scoped = frame.filter(
        (pl.col("timestamp_utc") >= start_utc)
        & (pl.col("timestamp_utc") < end_utc)
        & (pl.col("symbol") == symbol)
    ).sort("timestamp_utc")
    if scoped.is_empty():
        raise ValueError("requested Phase 5 feature source range contains no rows")
    if scoped.select(pl.col("timestamp_utc").is_duplicated().any()).item():
        raise ValueError("duplicate processed feature source timestamp")
    timestamps = scoped["timestamp_utc"].to_list()
    if timestamps != sorted(timestamps):
        raise ValueError("processed feature source timestamps are not monotonic")
    return LoadedFeatureSource(
        frame=scoped,
        processed_manifest_sha256=manifest_sha,
        opened_months=tuple(month for month, _, _ in selected),
    )
