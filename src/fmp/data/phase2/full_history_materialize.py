from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import polars as pl

from .artifacts import build_processed_manifest, sha256_file, write_parquet_partition, write_processed_manifest
from .full_history import RecordingCompleteRawChunkReader, _atomic_json, _iter_month_ranges, _validate_workers, validate_full_history_ledger
from .normalize import normalize_day
from .quality import analyze_quality
from .resample import resample_canonical
from .schema import CANONICAL_SCHEMA_VERSION


def _json_ready(value: object) -> object:
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() != timedelta(0):
            raise ValueError("full-history JSON timestamps must use UTC")
        return value.isoformat().replace("+00:00", "Z")
    if isinstance(value, dict):
        return {str(k): _json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(v) for v in value]
    return value


def _ref(path: Path, root: Path, row_count: int | None = None) -> dict[str, object]:
    return {
        "path": path.relative_to(root).as_posix(),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "row_count": row_count,
    }


def _partition_path(root: Path, pair: str, timeframe: str, month_start: date) -> Path:
    return root / "processed" / CANONICAL_SCHEMA_VERSION / timeframe / pair / f"{month_start.year:04d}" / f"{month_start.month:02d}.parquet"


def _quality_summary(report: dict[str, object]) -> dict[str, object]:
    keys = (
        "row_count", "missing_bid_rows", "missing_ask_rows", "required_null_count",
        "duplicate_count", "missing_open_market_minutes", "max_suspicious_gap_minutes",
        "finding_counts", "spread_summary", "midpoint_return_summary",
    )
    return {key: _json_ready(report.get(key)) for key in keys}


def materialize_pair(
    reader: object,
    output_root: Path,
    pair: str,
    *,
    start: date,
    end_exclusive: date,
    code_commit: str | None,
    workers: int,
) -> dict[str, object]:
    workers = _validate_workers(workers)
    if end_exclusive <= start:
        raise ValueError("full-history materialization end must be after start")
    root = Path(output_root)
    recording = RecordingCompleteRawChunkReader(reader)  # type: ignore[arg-type]
    artifacts: dict[str, dict[str, object]] = {}
    row_counts = {"1m": 0, "5m": 0, "15m": 0, "1h": 0}
    one_minute_paths: list[Path] = []
    month_count = 0

    for month_start, month_end in _iter_month_ranges(start, end_exclusive):
        days: list[date] = []
        day = month_start
        while day < month_end:
            days.append(day)
            day += timedelta(days=1)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            frames = list(executor.map(lambda d: normalize_day(recording, pair, d), days))
        nonempty = [frame for frame in frames if not frame.is_empty()]
        if not nonempty:
            raise ValueError(f"full-history month produced no canonical rows: {pair} {month_start:%Y-%m}")
        canonical = pl.concat(nonempty, how="vertical").sort(["symbol", "timestamp_utc"])
        month_key = f"{month_start.year:04d}-{month_start.month:02d}"
        for timeframe in ("1m", "5m", "15m", "1h"):
            frame = canonical if timeframe == "1m" else resample_canonical(canonical, timeframe)  # type: ignore[arg-type]
            path = _partition_path(root, pair, timeframe, month_start)
            digest = write_parquet_partition(frame, path)
            artifacts[f"{timeframe}:{month_key}"] = {
                "path": path.relative_to(root).as_posix(),
                "sha256": digest.sha256,
                "size_bytes": digest.size_bytes,
                "row_count": digest.row_count,
            }
            row_counts[timeframe] += digest.row_count
            if timeframe == "1m":
                one_minute_paths.append(path)
        month_count += 1

    canonical_full = pl.scan_parquet([path.as_posix() for path in one_minute_paths]).sort(["symbol", "timestamp_utc"]).collect()
    quality = analyze_quality(canonical_full)
    quality_path = root / "processed" / CANONICAL_SCHEMA_VERSION / "quality" / f"{pair}.json"
    _atomic_json(quality_path, _json_ready(quality))
    artifacts["quality"] = _ref(quality_path, root, canonical_full.height)

    validate_full_history_ledger(recording.records, pair, start, end_exclusive)
    ledger_path = root / "raw-ledger.json"
    recording.write_ledger(ledger_path)
    ledger_ref = _ref(ledger_path, root, len(recording.records))

    actual_start = quality.get("actual_start_utc")
    actual_end = quality.get("actual_end_utc")
    if not isinstance(actual_start, datetime) or not isinstance(actual_end, datetime):
        raise ValueError("full-history processed manifest requires non-empty UTC range")
    manifest = build_processed_manifest(
        symbol=pair, actual_start_utc=actual_start, actual_end_utc=actual_end,
        artifacts=artifacts, row_counts=row_counts, quality_summary=_quality_summary(quality),
        generated_at_utc=datetime.now(timezone.utc), code_commit=code_commit,
    )
    manifest_path = root / "manifests" / "processed" / CANONICAL_SCHEMA_VERSION / f"{pair}.json"
    write_processed_manifest(manifest_path, manifest)
    manifest_ref = _ref(manifest_path, root)

    side_counts = Counter(str(item["side"]) for item in recording.records)
    summary: dict[str, object] = {
        "protocol": "fmp-phase2-full-history-v1", "pair": pair,
        "requested_start_utc": start.isoformat(),
        "requested_end_inclusive_utc": (end_exclusive - timedelta(days=1)).isoformat(),
        "month_count": month_count, "raw_read_count": len(recording.records),
        "raw_read_counts": dict(sorted(side_counts.items())), "row_counts": row_counts,
        "quality_finding_counts": quality.get("finding_counts", {}),
        "raw_ledger": ledger_ref, "quality": artifacts["quality"],
        "processed_manifest": manifest_ref, "code_commit": code_commit,
    }
    _atomic_json(root / "summary.json", summary)
    return summary
