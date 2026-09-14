from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Mapping

import polars as pl

from fmp.contracts import QuoteBar
from fmp.data.phase2.schema import CANONICAL_SCHEMA_VERSION
from fmp.research.contracts import ResearchSplit, allowed_split


ELIGIBLE_TIMEFRAMES = frozenset({"5m", "15m", "1h"})
_REQUIRED_QUOTE_COLUMNS = (
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
    "is_complete",
)


@dataclass(frozen=True, slots=True)
class LoadedResearchBars:
    bars: tuple[QuoteBar, ...]
    excluded_incomplete_count: int
    eligible_utc_dates: tuple[date, ...]


def _month_bounds(month_key: str) -> tuple[date, date]:
    try:
        year_text, month_text = month_key.split("-", 1)
        year = int(year_text)
        month = int(month_text)
        start = date(year, month, 1)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid processed artifact month key: {month_key!r}") from exc
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    return start, end


def _artifact_paths(
    *,
    root: Path,
    artifacts: Mapping[str, object],
    timeframe: str,
    split: ResearchSplit,
) -> list[Path]:
    prefix = f"{timeframe}:"
    selected: list[tuple[str, Path]] = []
    root_resolved = root.resolve()
    for key, raw_record in artifacts.items():
        if not key.startswith(prefix):
            continue
        month_key = key[len(prefix) :]
        month_start, month_end = _month_bounds(month_key)
        if month_end <= split.start or month_start >= split.end_exclusive:
            continue
        if not isinstance(raw_record, Mapping):
            raise ValueError(f"processed artifact record must be an object: {key}")
        raw_path = raw_record.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise ValueError(f"processed artifact path is missing: {key}")
        candidate = (root / raw_path).resolve()
        try:
            candidate.relative_to(root_resolved)
        except ValueError as exc:
            raise ValueError(f"processed artifact path escapes dataset root: {key}") from exc
        if not candidate.is_file():
            raise ValueError(f"processed artifact file is missing: {key}")
        selected.append((month_key, candidate))
    selected.sort(key=lambda item: item[0])
    if not selected:
        raise ValueError(
            f"processed manifest has no {timeframe} artifacts overlapping {split.name}"
        )
    return [path for _, path in selected]


def _load_manifest(path: Path) -> Mapping[str, object]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read processed manifest: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError("processed manifest root must be an object")
    return value


def _to_quote_bar(row: Mapping[str, object]) -> QuoteBar:
    timestamp = row["timestamp_utc"]
    if not isinstance(timestamp, datetime):
        raise ValueError("processed timestamp_utc must be a datetime")
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    elif timestamp.utcoffset() != timezone.utc.utcoffset(timestamp):
        timestamp = timestamp.astimezone(timezone.utc)
    return QuoteBar(
        timestamp_utc=timestamp,
        symbol=str(row["symbol"]),
        bid_open=float(row["bid_open"]),
        bid_high=float(row["bid_high"]),
        bid_low=float(row["bid_low"]),
        bid_close=float(row["bid_close"]),
        ask_open=float(row["ask_open"]),
        ask_high=float(row["ask_high"]),
        ask_low=float(row["ask_low"]),
        ask_close=float(row["ask_close"]),
    )


def load_processed_bars(
    *,
    dataset_root: Path,
    manifest_path: Path,
    symbol: str,
    timeframe: str,
    split_name: str,
) -> LoadedResearchBars:
    if timeframe not in ELIGIBLE_TIMEFRAMES:
        raise ValueError(f"unsupported Phase 4 signal timeframe: {timeframe!r}")
    split = allowed_split(split_name)
    manifest = _load_manifest(Path(manifest_path))

    if manifest.get("schema_version") != CANONICAL_SCHEMA_VERSION:
        raise ValueError("processed manifest schema identity does not match Phase 2")
    if manifest.get("symbol") != symbol:
        raise ValueError("processed manifest symbol does not match requested symbol")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ValueError("processed manifest artifacts must be an object")

    paths = _artifact_paths(
        root=Path(dataset_root),
        artifacts=artifacts,
        timeframe=timeframe,
        split=split,
    )
    frames = [pl.read_parquet(path) for path in paths]
    frame = pl.concat(frames, how="vertical") if len(frames) > 1 else frames[0]
    missing = [column for column in _REQUIRED_QUOTE_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"processed research data is missing required columns: {missing}")

    start_utc = datetime(split.start.year, split.start.month, split.start.day, tzinfo=timezone.utc)
    end_utc = datetime(
        split.end_exclusive.year,
        split.end_exclusive.month,
        split.end_exclusive.day,
        tzinfo=timezone.utc,
    )
    scoped = frame.filter(
        (pl.col("timestamp_utc") >= start_utc)
        & (pl.col("timestamp_utc") < end_utc)
        & (pl.col("symbol") == symbol)
    )

    identity_count = scoped.select(pl.struct(["symbol", "timestamp_utc"]).n_unique()).item()
    if identity_count != scoped.height:
        raise ValueError("duplicate processed research bar identity")

    incomplete_count = scoped.filter(~pl.col("is_complete")).height
    complete = scoped.filter(pl.col("is_complete")).sort(["timestamp_utc", "symbol"])
    rows = complete.select(list(_REQUIRED_QUOTE_COLUMNS)).to_dicts()
    bars = tuple(_to_quote_bar(row) for row in rows)
    keys = [(bar.timestamp_utc, bar.symbol) for bar in bars]
    if keys != sorted(keys):
        raise ValueError("processed research bars are not monotonic after loading")

    eligible_dates = tuple(sorted({bar.timestamp_utc.date() for bar in bars}))
    return LoadedResearchBars(
        bars=bars,
        excluded_incomplete_count=incomplete_count,
        eligible_utc_dates=eligible_dates,
    )
