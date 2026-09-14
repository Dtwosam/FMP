from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import polars as pl

from fmp.data.phase2.artifacts import sha256_file, write_parquet_partition

from .contracts import FEATURE_SET_VERSION, FINAL_SOURCE_END_EXCLUSIVE, validate_symbol, validate_timeframe
from .schema import FEATURE_COLUMNS, FEATURE_VALUE_COLUMNS


def _canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def _schema_sha256(frame: pl.DataFrame) -> str:
    schema = [(name, str(dtype)) for name, dtype in frame.schema.items()]
    return hashlib.sha256(_canonical_json(schema)).hexdigest()


def _iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return value.isoformat().replace("+00:00", "Z")


def _locked_boundary_utc() -> datetime:
    return datetime(
        FINAL_SOURCE_END_EXCLUSIVE.year,
        FINAL_SOURCE_END_EXCLUSIVE.month,
        FINAL_SOURCE_END_EXCLUSIVE.day,
        tzinfo=timezone.utc,
    )


def write_feature_artifacts(
    *,
    features: pl.DataFrame,
    output_root: Path,
    symbol: str,
    timeframe: str,
    processed_manifest_sha256: str,
    code_commit: str,
    opened_months: Iterable[str],
) -> dict[str, object]:
    validate_symbol(symbol)
    validate_timeframe(timeframe)
    if features.is_empty():
        raise ValueError("cannot write empty Phase 5 feature dataset")
    if tuple(features.columns) != FEATURE_COLUMNS:
        raise ValueError("Phase 5 feature frame does not match frozen schema")
    if set(features["symbol"].to_list()) != {symbol} or set(features["timeframe"].to_list()) != {timeframe}:
        raise ValueError("Phase 5 feature artifact identity mismatch")
    boundary = _locked_boundary_utc()
    if features.filter(pl.col("available_at_utc") >= boundary).height:
        raise ValueError("Phase 5 final-test lock: refusing feature output reaching 2024-01-01")
    months = tuple(opened_months)
    if any(month >= "2024-01" for month in months):
        raise ValueError("Phase 5 final-test lock: opened source months include 2024+")
    unique_count = features.select(
        pl.struct(["symbol", "timeframe", "bar_start_utc"]).n_unique()
    ).item()
    if unique_count != features.height:
        raise ValueError("duplicate Phase 5 feature output identity")

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
        relative = Path("data") / "features" / FEATURE_SET_VERSION / symbol / timeframe / f"{year:04d}" / f"{month:02d}.parquet"
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

    null_row = features.select([pl.col(name).null_count().alias(name) for name in FEATURE_VALUE_COLUMNS]).row(0, named=True)
    first_start = features["bar_start_utc"][0]
    last_end = features["bar_end_utc"][-1]
    manifest: dict[str, object] = {
        "manifest_version": 1,
        "feature_set_version": FEATURE_SET_VERSION,
        "code_commit": code_commit,
        "processed_manifest_sha256": processed_manifest_sha256,
        "symbol": symbol,
        "timeframe": timeframe,
        "opened_source_months": list(months),
        "output_start_utc": _iso(first_start),
        "output_end_utc": _iso(last_end),
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
        raise ValueError(f"conflicting existing Phase 5 manifest: {manifest_path}")
    manifest_path.write_text(payload, encoding="utf-8")
    return manifest
