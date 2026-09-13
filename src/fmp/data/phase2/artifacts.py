from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Mapping

import polars as pl

from .schema import CANONICAL_SCHEMA_VERSION, INGESTION_VERSION

PHASE1_SOURCE_CHECKPOINT = "fmp-v1-phase1-source-of-truth"
PHASE1_FROZEN_PLAN_SHA256 = "2328a5417e04dcda862bd93066243ebf95d480443e8d098d08c9e0e1f78b3be6"
PARQUET_WRITER_CONFIG: dict[str, object] = {
    "compression": "zstd",
    "compression_level": 3,
    "statistics": True,
}


@dataclass(frozen=True, slots=True)
class ArtifactDigest:
    path: str
    sha256: str
    size_bytes: int
    row_count: int

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
            "row_count": self.row_count,
        }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stable_frame(frame: pl.DataFrame) -> pl.DataFrame:
    out = frame.select(frame.columns)
    sort_columns = [name for name in ("symbol", "timestamp_utc") if name in out.columns]
    if sort_columns:
        out = out.sort(sort_columns)
    return out


def write_parquet_partition(frame: pl.DataFrame, path: Path) -> ArtifactDigest:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    stable = _stable_frame(frame)

    fd, tmp_name = tempfile.mkstemp(prefix=f".{destination.name}.part-", dir=destination.parent)
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        stable.write_parquet(
            tmp_path,
            compression=str(PARQUET_WRITER_CONFIG["compression"]),
            compression_level=int(PARQUET_WRITER_CONFIG["compression_level"]),
            statistics=bool(PARQUET_WRITER_CONFIG["statistics"]),
        )
        candidate_sha256 = sha256_file(tmp_path)
        candidate_size = tmp_path.stat().st_size

        if destination.exists():
            existing_size = destination.stat().st_size
            existing_sha256 = sha256_file(destination)
            if existing_size != candidate_size or existing_sha256 != candidate_sha256:
                raise ValueError(f"conflicting existing Parquet partition: {destination}")
            tmp_path.unlink()
            return ArtifactDigest(
                path=destination.as_posix(),
                sha256=existing_sha256,
                size_bytes=existing_size,
                row_count=stable.height,
            )

        os.replace(tmp_path, destination)
        written_size = destination.stat().st_size
        written_sha256 = sha256_file(destination)
        if written_size != candidate_size or written_sha256 != candidate_sha256:
            raise ValueError(f"Parquet output checksum verification failed: {destination}")
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise

    return ArtifactDigest(
        path=destination.as_posix(),
        sha256=written_sha256,
        size_bytes=written_size,
        row_count=stable.height,
    )


def _utc_iso(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError("processed-manifest timestamps must use UTC")
    return value.isoformat().replace("+00:00", "Z")


def build_processed_manifest(
    *,
    symbol: str,
    actual_start_utc: datetime,
    actual_end_utc: datetime,
    artifacts: Mapping[str, object],
    row_counts: Mapping[str, int],
    quality_summary: Mapping[str, object],
    generated_at_utc: datetime,
    code_commit: str | None = None,
) -> dict[str, object]:
    manifest: dict[str, object] = {
        "manifest_version": 1,
        "symbol": symbol,
        "schema_version": CANONICAL_SCHEMA_VERSION,
        "ingestion_version": INGESTION_VERSION,
        "source_snapshot": {
            "checkpoint": PHASE1_SOURCE_CHECKPOINT,
            "frozen_plan_sha256": PHASE1_FROZEN_PLAN_SHA256,
        },
        "actual_start_utc": _utc_iso(actual_start_utc),
        "actual_end_utc": _utc_iso(actual_end_utc),
        "artifacts": dict(artifacts),
        "row_counts": dict(row_counts),
        "quality_summary": dict(quality_summary),
        "polars_version": pl.__version__,
        "parquet_writer": dict(PARQUET_WRITER_CONFIG),
        "generated_at_utc": _utc_iso(generated_at_utc),
        "code_commit": code_commit,
    }
    return manifest


def write_processed_manifest(path: Path, manifest: Mapping[str, object]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{destination.name}.part-", dir=destination.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(dict(manifest), handle, sort_keys=True, indent=2, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, destination)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise
