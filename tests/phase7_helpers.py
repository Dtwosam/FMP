from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence

import polars as pl

from fmp.data.phase2.schema import CANONICAL_SCHEMA_VERSION
from fmp.walkforward.contracts import FROZEN_CANDIDATES


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def quote_row(
    timestamp: datetime,
    *,
    symbol: str = "USDJPY",
    complete: bool = True,
) -> dict[str, object]:
    return {
        "timestamp_utc": timestamp,
        "symbol": symbol,
        "bid_open": 150.00,
        "bid_high": 150.10,
        "bid_low": 149.90,
        "bid_close": 150.04,
        "ask_open": 150.02,
        "ask_high": 150.12,
        "ask_low": 149.92,
        "ask_close": 150.06,
        "is_complete": complete,
    }


def month_timestamp(month_key: str, *, minute: int = 0) -> datetime:
    year_text, month_text = month_key.split("-", 1)
    return datetime(int(year_text), int(month_text), 28, 0, minute, tzinfo=timezone.utc)


def write_manifest(path: Path, manifest: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(dict(manifest), sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def manifest_sha256(path: Path) -> str:
    return sha256_file(path)


def write_phase7_fixture(
    root: Path,
    *,
    candidate_id: str,
    months: Sequence[str],
    rows_by_month: Mapping[str, Sequence[dict[str, object]]] | None = None,
    manifest_symbol: str = "USDJPY",
    schema_version: str = CANONICAL_SCHEMA_VERSION,
) -> Path:
    candidate = FROZEN_CANDIDATES[candidate_id]
    timeframe = candidate.timeframe
    rows_by_month = rows_by_month or {}
    artifacts: dict[str, dict[str, object]] = {}

    for month_key in months:
        year_text, month_text = month_key.split("-", 1)
        rows = list(rows_by_month.get(month_key, (quote_row(month_timestamp(month_key)),)))
        relative = (
            Path("processed")
            / CANONICAL_SCHEMA_VERSION
            / timeframe
            / "USDJPY"
            / year_text
            / f"{month_text}.parquet"
        )
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        pl.DataFrame(rows).write_parquet(path)
        artifacts[f"{timeframe}:{month_key}"] = {
            "path": relative.as_posix(),
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
            "row_count": len(rows),
        }

    manifest = {
        "manifest_version": 1,
        "symbol": manifest_symbol,
        "schema_version": schema_version,
        "artifacts": artifacts,
    }
    manifest_path = root / "manifests" / "processed" / CANONICAL_SCHEMA_VERSION / "USDJPY.json"
    write_manifest(manifest_path, manifest)
    return manifest_path


def refresh_artifact_record(root: Path, manifest: dict[str, object], key: str) -> None:
    artifacts = manifest["artifacts"]
    assert isinstance(artifacts, dict)
    record = artifacts[key]
    assert isinstance(record, dict)
    path = root / str(record["path"])
    frame = pl.read_parquet(path)
    record["sha256"] = sha256_file(path)
    record["size_bytes"] = path.stat().st_size
    record["row_count"] = frame.height
