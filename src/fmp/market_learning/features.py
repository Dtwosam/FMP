from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, Mapping

import polars as pl

from fmp.data.phase2.artifacts import sha256_file, write_parquet_partition
from fmp.features.contracts import (
    PROCESSED_SCHEMA_VERSION,
    validate_symbol,
    validate_timeframe,
)
from fmp.features.engine import build_feature_frame
from fmp.features.schema import FEATURE_COLUMNS, FEATURE_VALUE_COLUMNS

from .contracts import (
    BASE_FEATURE_DEFINITION_VERSION,
    EVIDENCE_LABEL,
    MARKET_FEATURE_SET_VERSION,
    MARKET_HISTORY_END_EXCLUSIVE,
    MARKET_HISTORY_START,
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
class LoadedMarketFeatureSource:
    frame: pl.DataFrame
    processed_manifest_sha256: str
    opened_months: tuple[str, ...]


def validate_market_feature_range(start: date, end_exclusive: date) -> None:
    if start >= end_exclusive:
        raise ValueError("market-learning source range must be non-empty")
    if start < MARKET_HISTORY_START:
        raise ValueError("market-learning source coverage may not start before 2015-01-01")
    if end_exclusive > MARKET_HISTORY_END_EXCLUSIVE:
        raise ValueError(
            "market-learning source coverage may not extend beyond accepted 2026-08-20 history"
        )


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
        raw = Path(path).read_bytes()
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
        month_key = key[len(prefix):]
        month_start, month_end = _month_bounds(month_key)
        if month_end <= start or month_start >= end_exclusive:
            continue
        if month_start >= MARKET_HISTORY_END_EXCLUSIVE:
            raise ValueError("processed manifest selects source beyond accepted history")
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
        raise ValueError(
            f"processed manifest has no {timeframe} artifacts overlapping requested range"
        )
    return selected


def load_market_feature_source(
    *,
    dataset_root: Path,
    manifest_path: Path,
    symbol: str,
    timeframe: str,
    start: date,
    end_exclusive: date,
    parquet_reader: Callable[[Path], pl.DataFrame] = pl.read_parquet,
) -> LoadedMarketFeatureSource:
    validate_symbol(symbol)
    validate_timeframe(timeframe)
    validate_market_feature_range(start, end_exclusive)

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

    frames: list[pl.DataFrame] = []
    for month_key, path, record in selected:
        if not path.is_file():
            raise ValueError(f"processed artifact file is missing: {timeframe}:{month_key}")
        size = record.get("size_bytes")
        if isinstance(size, int) and not isinstance(size, bool) and path.stat().st_size != size:
            raise ValueError(f"processed artifact size mismatch: {timeframe}:{month_key}")
        expected_sha = record.get("sha256")
        if isinstance(expected_sha, str) and expected_sha and sha256_file(path) != expected_sha:
            raise ValueError(f"processed artifact checksum mismatch: {timeframe}:{month_key}")
        frame = parquet_reader(path)
        expected_rows = record.get("row_count")
        if (
            isinstance(expected_rows, int)
            and not isinstance(expected_rows, bool)
            and frame.height != expected_rows
        ):
            raise ValueError(f"processed artifact row-count mismatch: {timeframe}:{month_key}")
        frames.append(frame)

    frame = pl.concat(frames, how="vertical") if len(frames) > 1 else frames[0]
    missing = [name for name in _REQUIRED_COLUMNS if name not in frame.columns]
    if missing:
        raise ValueError(f"processed market-learning source is missing columns: {missing}")
    if set(frame["symbol"].to_list()) != {symbol}:
        raise ValueError("processed market-learning source contains a different symbol")
    if set(frame["timeframe"].to_list()) != {timeframe}:
        raise ValueError("processed market-learning source contains a different timeframe")
    if set(frame["schema_version"].to_list()) != {"fmp-derived-bars-v1"}:
        raise ValueError("processed market-learning source derived-bar schema mismatch")

    start_utc = datetime(start.year, start.month, start.day, tzinfo=timezone.utc)
    end_utc = datetime(
        end_exclusive.year,
        end_exclusive.month,
        end_exclusive.day,
        tzinfo=timezone.utc,
    )
    scoped = frame.filter(
        (pl.col("timestamp_utc") >= start_utc)
        & (pl.col("timestamp_utc") < end_utc)
        & (pl.col("symbol") == symbol)
    ).sort("timestamp_utc")
    if scoped.is_empty():
        raise ValueError("requested market-learning source range contains no rows")
    if scoped.select(pl.col("timestamp_utc").is_duplicated().any()).item():
        raise ValueError("duplicate market-learning source timestamp")
    return LoadedMarketFeatureSource(
        frame=scoped,
        processed_manifest_sha256=manifest_sha,
        opened_months=tuple(month for month, _, _ in selected),
    )


def build_market_feature_frame(
    source: pl.DataFrame,
    *,
    symbol: str,
    timeframe: str,
    processed_manifest_sha256: str,
) -> pl.DataFrame:
    out = build_feature_frame(
        source,
        symbol=symbol,
        timeframe=timeframe,
        processed_manifest_sha256=processed_manifest_sha256,
    ).with_columns(
        pl.lit(MARKET_FEATURE_SET_VERSION).alias("feature_set_version")
    )
    if tuple(out.columns) != FEATURE_COLUMNS:
        raise ValueError("market-learning feature frame does not match frozen schema")
    if set(out["feature_set_version"].to_list()) != {MARKET_FEATURE_SET_VERSION}:
        raise ValueError("market-learning feature-set identity mismatch")
    return out


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode("utf-8")


def _schema_sha256(frame: pl.DataFrame) -> str:
    schema = [(name, str(dtype)) for name, dtype in frame.schema.items()]
    return hashlib.sha256(_canonical_json(schema)).hexdigest()


def _iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return value.isoformat().replace("+00:00", "Z")


def write_market_feature_artifacts(
    *,
    features: pl.DataFrame,
    output_root: Path,
    symbol: str,
    timeframe: str,
    processed_manifest_sha256: str,
    code_commit: str,
    opened_months: Iterable[str],
    requested_start: date,
    requested_end_exclusive: date,
) -> dict[str, object]:
    validate_symbol(symbol)
    validate_timeframe(timeframe)
    validate_market_feature_range(requested_start, requested_end_exclusive)
    if not code_commit.strip():
        raise ValueError("code_commit must be non-empty")
    if features.is_empty():
        raise ValueError("cannot write empty market-learning feature dataset")
    if tuple(features.columns) != FEATURE_COLUMNS:
        raise ValueError("market-learning feature frame does not match frozen schema")
    if set(features["symbol"].to_list()) != {symbol}:
        raise ValueError("market-learning feature symbol identity mismatch")
    if set(features["timeframe"].to_list()) != {timeframe}:
        raise ValueError("market-learning feature timeframe identity mismatch")
    if set(features["feature_set_version"].to_list()) != {MARKET_FEATURE_SET_VERSION}:
        raise ValueError("market-learning feature-set identity mismatch")
    if set(features["processed_manifest_sha256"].to_list()) != {
        processed_manifest_sha256
    }:
        raise ValueError("market-learning processed manifest identity mismatch")

    accepted_end = datetime(
        MARKET_HISTORY_END_EXCLUSIVE.year,
        MARKET_HISTORY_END_EXCLUSIVE.month,
        MARKET_HISTORY_END_EXCLUSIVE.day,
        tzinfo=timezone.utc,
    )
    if features.filter(pl.col("available_at_utc") >= accepted_end).height:
        raise ValueError("market-learning feature output extends beyond accepted history")

    months = tuple(opened_months)
    if tuple(sorted(months)) != months or len(set(months)) != len(months):
        raise ValueError("opened source months must be sorted and unique")
    if any(month > "2026-08" for month in months):
        raise ValueError("opened source months extend beyond accepted history")

    unique_count = features.select(
        pl.struct(["symbol", "timeframe", "bar_start_utc"]).n_unique()
    ).item()
    if unique_count != features.height:
        raise ValueError("duplicate market-learning feature output identity")

    root = Path(output_root)
    artifact_rows: list[dict[str, object]] = []
    month_pairs = (
        features.select(
            pl.col("bar_start_utc").dt.year().alias("year"),
            pl.col("bar_start_utc").dt.month().alias("month"),
        )
        .unique()
        .sort(["year", "month"])
        .rows()
    )
    for year, month in month_pairs:
        monthly = features.filter(
            (pl.col("bar_start_utc").dt.year() == year)
            & (pl.col("bar_start_utc").dt.month() == month)
        ).sort(["symbol", "timeframe", "bar_start_utc"])
        relative = (
            Path("data")
            / "features"
            / MARKET_FEATURE_SET_VERSION
            / symbol
            / timeframe
            / f"{year:04d}"
            / f"{month:02d}.parquet"
        )
        destination = root / relative
        digest = write_parquet_partition(monthly, destination)
        artifact_rows.append(
            {
                "path": relative.as_posix(),
                "sha256": digest.sha256,
                "size_bytes": digest.size_bytes,
                "row_count": digest.row_count,
            }
        )

    null_row = features.select(
        [pl.col(name).null_count().alias(name) for name in FEATURE_VALUE_COLUMNS]
    ).row(0, named=True)
    manifest: dict[str, object] = {
        "manifest_version": 1,
        "experiment_id": "EXP-20260923-044",
        "feature_set_version": MARKET_FEATURE_SET_VERSION,
        "base_feature_definition_version": BASE_FEATURE_DEFINITION_VERSION,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "model_training_authorized": False,
        "promotion_authorized": False,
        "code_commit": code_commit,
        "processed_manifest_sha256": processed_manifest_sha256,
        "symbol": symbol,
        "timeframe": timeframe,
        "generation_parameters": {
            "requested_start": requested_start.isoformat(),
            "requested_end_exclusive": requested_end_exclusive.isoformat(),
        },
        "opened_source_months": list(months),
        "output_start_utc": _iso(features["bar_start_utc"][0]),
        "output_end_utc": _iso(features["bar_end_utc"][-1]),
        "row_count": features.height,
        "unique_key_count": unique_count,
        "feature_columns": list(FEATURE_VALUE_COLUMNS),
        "schema_columns": list(FEATURE_COLUMNS),
        "schema_sha256": _schema_sha256(features),
        "null_counts": {name: int(null_row[name]) for name in FEATURE_VALUE_COLUMNS},
        "writer": {
            "format": "parquet",
            "compression": "zstd",
            "compression_level": 3,
            "statistics": True,
        },
        "artifacts": artifact_rows,
    }
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / "manifest.json"
    payload = json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if manifest_path.exists() and manifest_path.read_text(encoding="utf-8") != payload:
        raise ValueError(f"conflicting existing market-learning manifest: {manifest_path}")
    manifest_path.write_text(payload, encoding="utf-8")
    return manifest


def run_market_feature_generation(
    *,
    dataset_root: Path,
    manifest_path: Path,
    symbol: str,
    timeframe: str,
    start: date,
    end_exclusive: date,
    output_root: Path,
    code_commit: str,
) -> dict[str, object]:
    validate_symbol(symbol)
    validate_timeframe(timeframe)
    validate_market_feature_range(start, end_exclusive)
    if not code_commit.strip():
        raise ValueError("code_commit must be non-empty")

    loaded = load_market_feature_source(
        dataset_root=Path(dataset_root),
        manifest_path=Path(manifest_path),
        symbol=symbol,
        timeframe=timeframe,
        start=start,
        end_exclusive=end_exclusive,
    )
    features = build_market_feature_frame(
        loaded.frame,
        symbol=symbol,
        timeframe=timeframe,
        processed_manifest_sha256=loaded.processed_manifest_sha256,
    )

    start_utc = datetime(start.year, start.month, start.day, tzinfo=timezone.utc)
    end_utc = datetime(
        end_exclusive.year,
        end_exclusive.month,
        end_exclusive.day,
        tzinfo=timezone.utc,
    )
    features = features.filter(
        (pl.col("available_at_utc") >= start_utc)
        & (pl.col("available_at_utc") < end_utc)
    )
    if features.is_empty():
        raise ValueError(
            "market-learning feature generation produced no rows in requested range"
        )
    return write_market_feature_artifacts(
        features=features,
        output_root=Path(output_root),
        symbol=symbol,
        timeframe=timeframe,
        processed_manifest_sha256=loaded.processed_manifest_sha256,
        code_commit=code_commit,
        opened_months=loaded.opened_months,
        requested_start=start,
        requested_end_exclusive=end_exclusive,
    )


__all__ = [
    "LoadedMarketFeatureSource",
    "build_market_feature_frame",
    "load_market_feature_source",
    "run_market_feature_generation",
    "validate_market_feature_range",
    "write_market_feature_artifacts",
]
