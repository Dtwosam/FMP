from __future__ import annotations

import json
import os
import tempfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

import polars as pl

from fmp.data.types import RawChunkKey

from .artifacts import (
    ArtifactDigest,
    build_processed_manifest,
    sha256_file,
    write_parquet_partition,
    write_processed_manifest,
)
from .bi5 import decode_bi5_day
from .normalize import normalize_decoded_sides
from .quality import analyze_quality
from .raw_reader import LocalRawChunkReader
from .resample import resample_canonical
from .schema import CANONICAL_SCHEMA_VERSION


def _iter_days(start: date, end_exclusive: date) -> Iterable[date]:
    if end_exclusive <= start:
        raise ValueError("end must be after start")
    current = start
    while current < end_exclusive:
        yield current
        current += timedelta(days=1)


def _normalize_day(reader: LocalRawChunkReader, pair: str, day: date) -> pl.DataFrame | None:
    decoded: dict[str, pl.DataFrame | None] = {}
    for side in ("BID", "ASK"):
        key = RawChunkKey(pair, side, day)  # type: ignore[arg-type]
        body = reader.read(key)
        decoded[side] = None if body is None else decode_bi5_day(key, body)
    if decoded["BID"] is None and decoded["ASK"] is None:
        return None
    return normalize_decoded_sides(decoded["BID"], decoded["ASK"])


def _normalize_range(root: Path, pair: str, start: date, end_exclusive: date) -> pl.DataFrame:
    reader = LocalRawChunkReader(root)
    frames = [
        frame
        for day in _iter_days(start, end_exclusive)
        if (frame := _normalize_day(reader, pair, day)) is not None
    ]
    if not frames:
        raise ValueError("selected Phase 2 range contains no canonical rows")
    return pl.concat(frames, how="vertical").sort(["symbol", "timestamp_utc"])


def _json_ready(value: object) -> object:
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() != timedelta(0):
            raise ValueError("Phase 2 JSON timestamps must use UTC")
        return value.isoformat().replace("+00:00", "Z")
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def _write_json(path: Path, payload: object) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{destination.name}.part-", dir=destination.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(_json_ready(payload), handle, sort_keys=True, indent=2, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, destination)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


def _digest_record(digest: ArtifactDigest, root: Path) -> dict[str, object]:
    path = Path(digest.path)
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError:
        relative = path.as_posix()
    return {
        "path": relative,
        "sha256": digest.sha256,
        "size_bytes": digest.size_bytes,
        "row_count": digest.row_count,
    }


def _json_digest_record(path: Path, root: Path, row_count: int | None = None) -> dict[str, object]:
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError:
        relative = path.as_posix()
    return {
        "path": relative,
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "row_count": row_count,
    }


def _write_monthly_partitions(
    frame: pl.DataFrame,
    *,
    root: Path,
    symbol: str,
    timeframe: str,
) -> dict[str, dict[str, object]]:
    months = sorted(
        {
            (timestamp.year, timestamp.month)
            for timestamp in frame["timestamp_utc"].to_list()
            if isinstance(timestamp, datetime)
        }
    )
    artifacts: dict[str, dict[str, object]] = {}
    for year, month in months:
        partition = frame.filter(
            (pl.col("timestamp_utc").dt.year() == year)
            & (pl.col("timestamp_utc").dt.month() == month)
        )
        path = (
            root
            / "processed"
            / CANONICAL_SCHEMA_VERSION
            / timeframe
            / symbol
            / f"{year:04d}"
            / f"{month:02d}.parquet"
        )
        digest = write_parquet_partition(partition, path)
        artifacts[f"{timeframe}:{year:04d}-{month:02d}"] = _digest_record(digest, root)
    return artifacts


def run_decode_day(args: object) -> int:
    root = Path(getattr(args, "root"))
    pair = str(getattr(args, "pair"))
    side = str(getattr(args, "side"))
    day = getattr(args, "date")
    key = RawChunkKey(pair, side, day)  # type: ignore[arg-type]
    body = LocalRawChunkReader(root).read(key)
    if body is None:
        raise ValueError(f"cannot decode canonical not_found chunk: {pair} {side} {day}")
    frame = decode_bi5_day(key, body)
    digest = write_parquet_partition(frame, Path(getattr(args, "out")))
    print(json.dumps(digest.to_dict(), sort_keys=True))
    return 0


def run_normalize(args: object) -> int:
    frame = _normalize_range(
        Path(getattr(args, "root")),
        str(getattr(args, "pair")),
        getattr(args, "start"),
        getattr(args, "end"),
    )
    digest = write_parquet_partition(frame, Path(getattr(args, "out")))
    print(json.dumps(digest.to_dict(), sort_keys=True))
    return 0


def run_quality(args: object) -> int:
    frame = pl.read_parquet(Path(getattr(args, "input")))
    report = analyze_quality(frame)
    output = Path(getattr(args, "out"))
    _write_json(output, report)
    print(json.dumps(_json_ready({"path": output.as_posix(), "row_count": frame.height}), sort_keys=True))
    return 0


def run_resample(args: object) -> int:
    frame = pl.read_parquet(Path(getattr(args, "input")))
    derived = resample_canonical(frame, getattr(args, "timeframe"))
    digest = write_parquet_partition(derived, Path(getattr(args, "out")))
    print(json.dumps(digest.to_dict(), sort_keys=True))
    return 0


def _quality_summary(report: dict[str, object]) -> dict[str, object]:
    keys = (
        "row_count",
        "missing_bid_rows",
        "missing_ask_rows",
        "required_null_count",
        "duplicate_count",
        "finding_counts",
        "spread_summary",
        "midpoint_return_summary",
    )
    return {key: _json_ready(report.get(key)) for key in keys}


def run_process_phase2(args: object) -> int:
    root = Path(getattr(args, "root"))
    pair = str(getattr(args, "pair"))
    canonical = _normalize_range(root, pair, getattr(args, "start"), getattr(args, "end"))
    quality_report = analyze_quality(canonical)

    artifacts: dict[str, dict[str, object]] = {}
    artifacts.update(_write_monthly_partitions(canonical, root=root, symbol=pair, timeframe="1m"))

    row_counts: dict[str, int] = {"1m": canonical.height}
    for timeframe in ("5m", "15m", "1h"):
        derived = resample_canonical(canonical, timeframe)  # type: ignore[arg-type]
        row_counts[timeframe] = derived.height
        artifacts.update(
            _write_monthly_partitions(derived, root=root, symbol=pair, timeframe=timeframe)
        )

    quality_path = root / "processed" / CANONICAL_SCHEMA_VERSION / "quality" / f"{pair}.json"
    _write_json(quality_path, quality_report)
    artifacts["quality"] = _json_digest_record(quality_path, root, canonical.height)

    actual_start = quality_report.get("actual_start_utc")
    actual_end = quality_report.get("actual_end_utc")
    if not isinstance(actual_start, datetime) or not isinstance(actual_end, datetime):
        raise ValueError("processed manifest requires non-empty canonical UTC range")

    manifest = build_processed_manifest(
        symbol=pair,
        actual_start_utc=actual_start,
        actual_end_utc=actual_end,
        artifacts=artifacts,
        row_counts=row_counts,
        quality_summary=_quality_summary(quality_report),
        generated_at_utc=datetime.now(timezone.utc),
        code_commit=getattr(args, "code_commit", None),
    )
    manifest_path = (
        root
        / "manifests"
        / "processed"
        / CANONICAL_SCHEMA_VERSION
        / f"{pair}.json"
    )
    write_processed_manifest(manifest_path, manifest)
    print(
        json.dumps(
            {
                "symbol": pair,
                "row_counts": row_counts,
                "manifest": manifest_path.as_posix(),
            },
            sort_keys=True,
        )
    )
    return 0
