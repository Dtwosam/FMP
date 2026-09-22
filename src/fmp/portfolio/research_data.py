from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable, Mapping

import polars as pl

from fmp.contracts import QuoteBar, SUPPORTED_SYMBOLS
from fmp.data.phase2.schema import CANONICAL_SCHEMA_VERSION
from fmp.research.data import ELIGIBLE_TIMEFRAMES

PHASE8A_DATA_TIMEFRAMES = frozenset(set(ELIGIBLE_TIMEFRAMES) | {"1m"})

PHASE8A_RETROSPECTIVE_START = date(2015, 1, 1)
PHASE8A_RETROSPECTIVE_END_EXCLUSIVE = date(2026, 8, 21)
PHASE8A_RETROSPECTIVE_LABEL = "RETROSPECTIVE_ALREADY_SEEN"

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
class RetrospectiveRange:
    start: date
    end_exclusive: date
    evidence_label: str = PHASE8A_RETROSPECTIVE_LABEL

    def __post_init__(self) -> None:
        if self.start < PHASE8A_RETROSPECTIVE_START:
            raise ValueError("range starts before the accepted Phase 8A snapshot")
        if self.end_exclusive > PHASE8A_RETROSPECTIVE_END_EXCLUSIVE:
            raise ValueError("range ends after the accepted Phase 8A snapshot")
        if self.end_exclusive <= self.start:
            raise ValueError("retrospective range end must be after start")
        if self.evidence_label != PHASE8A_RETROSPECTIVE_LABEL:
            raise ValueError("Phase 8A retrospective evidence label is immutable")


@dataclass(frozen=True, slots=True)
class LoadedRetrospectiveBars:
    bars: tuple[QuoteBar, ...]
    excluded_incomplete_count: int
    eligible_utc_dates: tuple[date, ...]
    evidence_label: str
    start: date
    end_exclusive: date
    processed_manifest_sha256: str
    opened_artifact_months: tuple[str, ...]


def _validated_range(value: RetrospectiveRange) -> tuple[date, date]:
    if not isinstance(value, RetrospectiveRange):
        raise ValueError("research_range must be a valid accepted Phase 8A snapshot range")
    try:
        start = value.start
        end_exclusive = value.end_exclusive
        label = value.evidence_label
    except AttributeError as exc:
        raise ValueError("research_range must be a valid accepted Phase 8A snapshot range") from exc
    if (
        not isinstance(start, date)
        or not isinstance(end_exclusive, date)
        or start < PHASE8A_RETROSPECTIVE_START
        or end_exclusive > PHASE8A_RETROSPECTIVE_END_EXCLUSIVE
        or end_exclusive <= start
        or label != PHASE8A_RETROSPECTIVE_LABEL
    ):
        raise ValueError("research_range falls outside the accepted Phase 8A snapshot")
    return start, end_exclusive


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
    except OSError as exc:
        raise ValueError(f"cannot read processed manifest: {path}") from exc
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"cannot read processed manifest: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError("processed manifest root must be an object")
    return value, hashlib.sha256(raw).hexdigest()


def _artifact_paths(
    *,
    root: Path,
    artifacts: Mapping[str, object],
    timeframe: str,
    start: date,
    end_exclusive: date,
) -> tuple[tuple[str, Path], ...]:
    prefix = f"{timeframe}:"
    selected: list[tuple[str, Path]] = []
    root_resolved = root.resolve()

    for key, raw_record in artifacts.items():
        if not key.startswith(prefix):
            continue
        month_key = key[len(prefix) :]
        month_start, month_end = _month_bounds(month_key)
        if month_end <= start or month_start >= end_exclusive:
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
            f"processed manifest has no {timeframe} artifacts overlapping "
            f"{start.isoformat()}..{end_exclusive.isoformat()}"
        )
    return tuple(selected)


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


def load_phase8a_retrospective_bars(
    *,
    dataset_root: Path,
    manifest_path: Path,
    symbol: str,
    timeframe: str,
    research_range: RetrospectiveRange,
    parquet_reader: Callable[[Path], pl.DataFrame] = pl.read_parquet,
) -> LoadedRetrospectiveBars:
    """Load accepted Phase 2 bars for explicitly retrospective Phase 8A research.

    This is intentionally separate from the Phase 4/5/6 loaders. It permits
    already-inspected 2024-2026 history only under an immutable retrospective
    evidence label and only inside the accepted Phase 2 snapshot.
    """

    start, end_exclusive = _validated_range(research_range)
    if symbol not in SUPPORTED_SYMBOLS:
        raise ValueError(f"unsupported Phase 8A symbol: {symbol!r}")
    if timeframe not in PHASE8A_DATA_TIMEFRAMES:
        raise ValueError(f"unsupported Phase 8A data timeframe: {timeframe!r}")

    manifest, manifest_sha256 = _load_manifest(Path(manifest_path))
    if manifest.get("schema_version") != CANONICAL_SCHEMA_VERSION:
        raise ValueError("processed manifest schema identity does not match Phase 2")
    if manifest.get("symbol") != symbol:
        raise ValueError("processed manifest symbol does not match requested symbol")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ValueError("processed manifest artifacts must be an object")

    selected = _artifact_paths(
        root=Path(dataset_root),
        artifacts=artifacts,
        timeframe=timeframe,
        start=start,
        end_exclusive=end_exclusive,
    )
    frames = [parquet_reader(path) for _, path in selected]
    frame = pl.concat(frames, how="vertical") if len(frames) > 1 else frames[0]

    missing = [column for column in _REQUIRED_QUOTE_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"processed research data is missing required columns: {missing}")

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
    )

    identity_count = scoped.select(pl.struct(["symbol", "timestamp_utc"]).n_unique()).item()
    if identity_count != scoped.height:
        raise ValueError("duplicate processed retrospective bar identity")

    incomplete_count = scoped.filter(~pl.col("is_complete")).height
    complete = scoped.filter(pl.col("is_complete")).sort(["timestamp_utc", "symbol"])
    rows = complete.select(list(_REQUIRED_QUOTE_COLUMNS)).to_dicts()
    bars = tuple(_to_quote_bar(row) for row in rows)
    keys = [(bar.timestamp_utc, bar.symbol) for bar in bars]
    if keys != sorted(keys):
        raise ValueError("processed retrospective bars are not monotonic after loading")

    return LoadedRetrospectiveBars(
        bars=bars,
        excluded_incomplete_count=incomplete_count,
        eligible_utc_dates=tuple(sorted({bar.timestamp_utc.date() for bar in bars})),
        evidence_label=PHASE8A_RETROSPECTIVE_LABEL,
        start=start,
        end_exclusive=end_exclusive,
        processed_manifest_sha256=manifest_sha256,
        opened_artifact_months=tuple(month for month, _ in selected),
    )
