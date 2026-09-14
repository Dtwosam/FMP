from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

import polars as pl

from .artifacts import write_feature_artifacts
from .contracts import validate_source_range, validate_symbol, validate_timeframe
from .data import load_feature_source
from .engine import build_feature_frame


def validate_generation_request(
    *, symbol: str, timeframe: str, start: date, end_exclusive: date
) -> None:
    validate_symbol(symbol)
    validate_timeframe(timeframe)
    validate_source_range(start, end_exclusive)


def run_feature_generation(
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
    # Must happen before manifest/data access.
    validate_generation_request(
        symbol=symbol, timeframe=timeframe, start=start, end_exclusive=end_exclusive
    )
    if not code_commit.strip():
        raise ValueError("code_commit must be non-empty")
    loaded = load_feature_source(
        dataset_root=Path(dataset_root),
        manifest_path=Path(manifest_path),
        symbol=symbol,
        timeframe=timeframe,
        start=start,
        end_exclusive=end_exclusive,
    )
    features = build_feature_frame(
        loaded.frame,
        symbol=symbol,
        timeframe=timeframe,
        processed_manifest_sha256=loaded.processed_manifest_sha256,
    )
    # Output coverage is availability-time bounded. The source reader is already
    # path-bounded; this also prevents a last pre-boundary bar from emitting a
    # row whose bar close lands on the next period boundary.
    start_utc = datetime(start.year, start.month, start.day, tzinfo=timezone.utc)
    end_utc = datetime(end_exclusive.year, end_exclusive.month, end_exclusive.day, tzinfo=timezone.utc)
    features = features.filter(
        (pl.col("available_at_utc") >= start_utc)
        & (pl.col("available_at_utc") < end_utc)
    )
    if features.is_empty():
        raise ValueError("Phase 5 generation produced no rows in requested availability range")
    return write_feature_artifacts(
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
