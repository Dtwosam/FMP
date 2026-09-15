from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Mapping

import polars as pl

from fmp.contracts import QuoteBar
from fmp.data.phase2.schema import CANONICAL_SCHEMA_VERSION

from .contracts import (
    FROZEN_CANDIDATES,
    MAX_WARMUP_DAYS,
    USDJPY_PROCESSED_MANIFEST_SHA256,
    FrozenPhase7Candidate,
    Phase7Window,
    allowed_phase7_window,
)


_PROMOTION_START = date(2024, 1, 1)
_PROMOTION_END_EXCLUSIVE = date(2026, 8, 21)
_EXPECTED_WARMUP_DAYS = 7
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
class LoadedPhase7Bars:
    bars: tuple[QuoteBar, ...]
    scored_bars: tuple[QuoteBar, ...]
    eligible_scored_dates: tuple[date, ...]
    opened_partition_keys: tuple[str, ...]
    warmup_range: tuple[datetime, datetime]


def _resolve_contract_before_io(
    *, candidate_id: str, window_name: str
) -> tuple[FrozenPhase7Candidate, Phase7Window, datetime, datetime, datetime]:
    try:
        candidate = FROZEN_CANDIDATES[candidate_id]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"unsupported frozen Phase 7 candidate: {candidate_id!r}") from exc

    window = allowed_phase7_window(window_name)
    if MAX_WARMUP_DAYS != _EXPECTED_WARMUP_DAYS:
        raise ValueError("Phase 7 warm-up contract must remain exactly seven calendar days")
    if window.start < _PROMOTION_START or window.end_exclusive > _PROMOTION_END_EXCLUSIVE:
        raise ValueError("Phase 7 window endpoint violates the frozen promotion range")
    if candidate.symbol != "USDJPY" or candidate.timeframe not in {"15m", "1h"}:
        raise ValueError("Phase 7 candidate contract does not match the frozen USDJPY surface")

    scored_start = datetime(
        window.start.year, window.start.month, window.start.day, tzinfo=timezone.utc
    )
    scored_end = datetime(
        window.end_exclusive.year,
        window.end_exclusive.month,
        window.end_exclusive.day,
        tzinfo=timezone.utc,
    )
    warmup_start = scored_start - timedelta(days=MAX_WARMUP_DAYS)
    return candidate, window, warmup_start, scored_start, scored_end


def _load_verified_manifest(path: Path) -> Mapping[str, object]:
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise ValueError(f"cannot read Phase 7 processed manifest: {path}") from exc
    actual_sha = hashlib.sha256(raw).hexdigest()
    if actual_sha != USDJPY_PROCESSED_MANIFEST_SHA256:
        raise ValueError(
            "processed manifest sha mismatch for frozen Phase 7 USDJPY source"
        )
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("Phase 7 processed manifest is not valid JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("Phase 7 processed manifest root must be an object")
    return value


def _next_month(value: date) -> date:
    if value.month == 12:
        return date(value.year + 1, 1, 1)
    return date(value.year, value.month + 1, 1)


def _required_partition_keys(
    *, timeframe: str, start: datetime, end_exclusive: datetime
) -> tuple[str, ...]:
    cursor = date(start.year, start.month, 1)
    end_date = end_exclusive.date()
    keys: list[str] = []
    while cursor < end_date:
        keys.append(f"{timeframe}:{cursor.year:04d}-{cursor.month:02d}")
        cursor = _next_month(cursor)
    return tuple(keys)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise ValueError(f"cannot read Phase 7 processed artifact: {path}") from exc
    return digest.hexdigest()


def _verify_selected_artifacts(
    *,
    root: Path,
    artifacts: Mapping[str, object],
    keys: tuple[str, ...],
) -> tuple[tuple[str, Path, int], ...]:
    root_resolved = root.resolve()
    verified: list[tuple[str, Path, int]] = []
    seen_paths: set[Path] = set()

    for key in keys:
        record = artifacts.get(key)
        if not isinstance(record, Mapping):
            raise ValueError(f"processed manifest is missing required Phase 7 partition: {key}")
        raw_path = record.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise ValueError(f"processed artifact path is missing: {key}")
        candidate = (root / raw_path).resolve()
        try:
            candidate.relative_to(root_resolved)
        except ValueError as exc:
            raise ValueError(f"processed artifact path escapes dataset root: {key}") from exc
        if candidate in seen_paths:
            raise ValueError("duplicate Phase 7 processed artifact path")
        seen_paths.add(candidate)
        if not candidate.is_file():
            raise ValueError(f"processed artifact file is missing: {key}")

        expected_size = record.get("size_bytes")
        if not isinstance(expected_size, int) or isinstance(expected_size, bool) or expected_size < 0:
            raise ValueError(f"processed artifact size metadata is invalid: {key}")
        if candidate.stat().st_size != expected_size:
            raise ValueError(f"processed artifact size mismatch: {key}")
        expected_sha = record.get("sha256")
        if not isinstance(expected_sha, str) or _sha256_file(candidate) != expected_sha:
            raise ValueError(f"processed artifact checksum/sha mismatch: {key}")
        expected_rows = record.get("row_count")
        if not isinstance(expected_rows, int) or isinstance(expected_rows, bool) or expected_rows < 0:
            raise ValueError(f"processed artifact row-count metadata is invalid: {key}")
        verified.append((key, candidate, expected_rows))

    return tuple(verified)


def _utc_timestamp(value: object) -> datetime:
    if not isinstance(value, datetime):
        raise ValueError("processed timestamp_utc must be a datetime")
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError("processed timestamp_utc must use UTC")
    return value.astimezone(timezone.utc)


def _validate_cadence(timestamp: datetime, timeframe: str) -> None:
    if timestamp.second != 0 or timestamp.microsecond != 0:
        raise ValueError("processed Phase 7 bar violates frozen timeframe cadence")
    if timeframe == "15m" and timestamp.minute % 15 != 0:
        raise ValueError("processed Phase 7 bar violates frozen timeframe cadence")
    if timeframe == "1h" and timestamp.minute != 0:
        raise ValueError("processed Phase 7 bar violates frozen timeframe cadence")


def _to_quote_bar(row: Mapping[str, object]) -> QuoteBar:
    return QuoteBar(
        timestamp_utc=_utc_timestamp(row["timestamp_utc"]),
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


def load_phase7_bars(
    *,
    dataset_root: Path,
    manifest_path: Path,
    candidate_id: str,
    window_name: str,
    parquet_reader: Callable[[Path], pl.DataFrame] = pl.read_parquet,
) -> LoadedPhase7Bars:
    """Load one exact promotion-only Phase 7 window plus bounded warm-up context.

    Candidate/window authorization and the frozen range checks run before manifest
    access. Manifest and artifact identities are then fully verified before any
    Parquet reader is invoked.
    """
    candidate, _, warmup_start, scored_start, scored_end = _resolve_contract_before_io(
        candidate_id=candidate_id,
        window_name=window_name,
    )

    manifest = _load_verified_manifest(Path(manifest_path))
    version = manifest.get("manifest_version")
    if version != 1 or isinstance(version, bool):
        raise ValueError("processed manifest version must be exact integer 1")
    if manifest.get("schema_version") != CANONICAL_SCHEMA_VERSION:
        raise ValueError("processed manifest schema identity does not match Phase 2")
    if manifest.get("symbol") != candidate.symbol:
        raise ValueError("processed manifest symbol does not match frozen Phase 7 candidate")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, Mapping):
        raise ValueError("processed manifest artifacts must be an object")

    required_keys = _required_partition_keys(
        timeframe=candidate.timeframe,
        start=warmup_start,
        end_exclusive=scored_end,
    )
    verified = _verify_selected_artifacts(
        root=Path(dataset_root), artifacts=artifacts, keys=required_keys
    )

    frames: list[pl.DataFrame] = []
    for key, path, expected_rows in verified:
        frame = parquet_reader(path)
        if not isinstance(frame, pl.DataFrame):
            raise ValueError(f"Parquet reader did not return a DataFrame: {key}")
        if frame.height != expected_rows:
            raise ValueError(f"processed artifact row-count mismatch: {key}")
        missing = [column for column in _REQUIRED_QUOTE_COLUMNS if column not in frame.columns]
        if missing:
            raise ValueError(f"processed Phase 7 data is missing required columns: {missing}")
        frames.append(frame.select(list(_REQUIRED_QUOTE_COLUMNS)))

    if not frames:
        raise ValueError("no Phase 7 processed partitions were selected")
    frame = pl.concat(frames, how="vertical") if len(frames) > 1 else frames[0]
    if frame.is_empty():
        raise ValueError("Phase 7 processed window is empty")
    if set(frame["symbol"].to_list()) != {candidate.symbol}:
        raise ValueError("processed Phase 7 bar symbol mismatch")

    identity_count = frame.select(pl.struct(["symbol", "timestamp_utc"]).n_unique()).item()
    if identity_count != frame.height:
        raise ValueError("duplicate Phase 7 processed bar identity")

    rows = frame.to_dicts()
    converted: list[QuoteBar] = []
    for row in rows:
        timestamp = _utc_timestamp(row["timestamp_utc"])
        _validate_cadence(timestamp, candidate.timeframe)
        is_complete = row["is_complete"]
        if not isinstance(is_complete, bool):
            raise ValueError("processed Phase 7 is_complete must be boolean")
        if not is_complete:
            continue
        if timestamp < warmup_start or timestamp >= scored_end:
            continue
        converted.append(_to_quote_bar(row))

    converted.sort(key=lambda bar: (bar.timestamp_utc, bar.symbol))
    bars = tuple(converted)
    if not bars:
        raise ValueError("Phase 7 processed window has no complete bars in approved range")
    scored_bars = tuple(bar for bar in bars if bar.timestamp_utc >= scored_start)
    eligible_scored_dates = tuple(
        sorted({bar.timestamp_utc.date() for bar in scored_bars})
    )
    return LoadedPhase7Bars(
        bars=bars,
        scored_bars=scored_bars,
        eligible_scored_dates=eligible_scored_dates,
        opened_partition_keys=required_keys,
        warmup_range=(warmup_start, scored_start),
    )
