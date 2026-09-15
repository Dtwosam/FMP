from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

import polars as pl

from fmp.features.schema import FEATURE_COLUMNS, FEATURE_VALUE_COLUMNS
from fmp.models.contracts import (
    FEATURE_SET_VERSION,
    USDJPY_PROCESSED_MANIFEST_SHA256,
)


PHASE5_IMPLEMENTATION_SHA = "74dce1b945ad31a05416a4fc9e63443a884cb90c"


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode("utf-8")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _schema_sha256(frame: pl.DataFrame) -> str:
    return hashlib.sha256(
        _canonical_json([(name, str(dtype)) for name, dtype in frame.schema.items()])
    ).hexdigest()


def _feature_value(name: str, *, ordinal: int, offset: float) -> object:
    if name in {
        "breakout_above_prior_8h",
        "breakout_below_prior_8h",
        "is_asia_session",
        "is_london_session",
        "is_new_york_session",
        "is_london_new_york_overlap",
    }:
        return bool((ordinal + len(name)) % 2)
    if name == "candle_direction":
        return 1 if ordinal % 2 == 0 else -1
    if name == "directional_streak":
        return ordinal + 1
    if name == "hour_utc":
        return ordinal % 24
    if name == "minute_utc":
        return (ordinal * 15) % 60
    if name == "day_of_week_utc":
        return ordinal % 7
    return float(ordinal + 1) + offset


def feature_row(
    timestamp: datetime,
    *,
    timeframe: str = "15m",
    ordinal: int = 0,
    value_offset: float = 0.0,
    available_at_utc: datetime | None = None,
) -> dict[str, object]:
    if timestamp.tzinfo is None or timestamp.utcoffset() != timedelta(0):
        raise ValueError("fixture timestamp must use UTC")
    width = timedelta(minutes={"15m": 15, "1h": 60}[timeframe])
    row: dict[str, object] = {
        "symbol": "USDJPY",
        "timeframe": timeframe,
        "bar_start_utc": timestamp,
        "bar_end_utc": timestamp + width,
        "available_at_utc": available_at_utc or timestamp + width,
        "feature_set_version": FEATURE_SET_VERSION,
        "processed_manifest_sha256": USDJPY_PROCESSED_MANIFEST_SHA256,
    }
    for name in FEATURE_VALUE_COLUMNS:
        row[name] = _feature_value(name, ordinal=ordinal, offset=value_offset)
    return row


def feature_frame(
    timestamps: Iterable[datetime],
    *,
    timeframe: str = "15m",
    value_offset: float = 0.0,
) -> pl.DataFrame:
    rows = [
        feature_row(ts, timeframe=timeframe, ordinal=index, value_offset=value_offset)
        for index, ts in enumerate(timestamps)
    ]
    return pl.DataFrame(rows).select(list(FEATURE_COLUMNS))


def write_feature_fixture(
    root: Path,
    *,
    timeframe: str = "15m",
    timestamps: tuple[datetime, ...] | None = None,
    frame: pl.DataFrame | None = None,
) -> tuple[Path, pl.DataFrame]:
    if frame is None:
        if timestamps is None:
            timestamps = (
                datetime(2018, 1, 2, 10, 0, tzinfo=timezone.utc),
                datetime(2018, 1, 2, 10, 15, tzinfo=timezone.utc),
            )
        frame = feature_frame(timestamps, timeframe=timeframe)
    if frame.is_empty():
        raise ValueError("fixture frame must be non-empty")

    artifact_rows: list[dict[str, object]] = []
    months = (
        frame.select(
            pl.col("bar_start_utc").dt.year().alias("year"),
            pl.col("bar_start_utc").dt.month().alias("month"),
        )
        .unique(maintain_order=True)
        .rows()
    )
    for year, month in months:
        monthly = frame.filter(
            (pl.col("bar_start_utc").dt.year() == year)
            & (pl.col("bar_start_utc").dt.month() == month)
        )
        relative = (
            Path("data")
            / "features"
            / FEATURE_SET_VERSION
            / "USDJPY"
            / timeframe
            / f"{year:04d}"
            / f"{month:02d}.parquet"
        )
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        monthly.write_parquet(path, compression="zstd", compression_level=3, statistics=True)
        artifact_rows.append(
            {
                "path": relative.as_posix(),
                "sha256": _sha256_file(path),
                "size_bytes": path.stat().st_size,
                "row_count": monthly.height,
            }
        )

    manifest = {
        "manifest_version": 1,
        "feature_set_version": FEATURE_SET_VERSION,
        "code_commit": PHASE5_IMPLEMENTATION_SHA,
        "processed_manifest_sha256": USDJPY_PROCESSED_MANIFEST_SHA256,
        "symbol": "USDJPY",
        "timeframe": timeframe,
        "generation_parameters": {
            "requested_start": "2015-01-01",
            "requested_end_exclusive": "2024-01-01",
        },
        "opened_source_months": [f"{year:04d}-{month:02d}" for year, month in months],
        "output_start_utc": frame["bar_start_utc"][0].astimezone(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        ),
        "output_end_utc": frame["bar_end_utc"][-1].astimezone(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        ),
        "row_count": frame.height,
        "unique_key_count": frame.select(
            pl.struct(["symbol", "timeframe", "bar_start_utc"]).n_unique()
        ).item(),
        "feature_columns": list(FEATURE_VALUE_COLUMNS),
        "schema_columns": list(FEATURE_COLUMNS),
        "schema_sha256": _schema_sha256(frame),
        "null_counts": {
            name: int(frame.select(pl.col(name).null_count()).item())
            for name in FEATURE_VALUE_COLUMNS
        },
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
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return manifest_path, frame


def mutate_manifest(manifest_path: Path, **updates: object) -> None:
    value = json.loads(manifest_path.read_text(encoding="utf-8"))
    value.update(updates)
    manifest_path.write_text(
        json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
