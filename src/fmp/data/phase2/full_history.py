from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import date, timedelta
from pathlib import Path
from threading import Lock
from typing import Protocol

from fmp.data.types import RawChunkKey

FULL_HISTORY_START = date(2015, 1, 1)
FULL_HISTORY_END_EXCLUSIVE = date(2026, 8, 21)
FULL_HISTORY_PAIRS = ("EURUSD", "GBPUSD", "USDJPY")
DEFAULT_WORKERS = 4
MAX_WORKERS = 8


class ReaderLike(Protocol):
    def read(self, key: RawChunkKey) -> bytes | None: ...


def _validate_workers(workers: int) -> int:
    if not isinstance(workers, int) or isinstance(workers, bool) or not 1 <= workers <= MAX_WORKERS:
        raise ValueError(f"full-history workers must be an integer in 1..{MAX_WORKERS}")
    return workers


def _next_month(value: date) -> date:
    if value.month == 12:
        return date(value.year + 1, 1, 1)
    return date(value.year, value.month + 1, 1)


def _iter_month_ranges(start: date, end_exclusive: date):
    if end_exclusive <= start:
        raise ValueError("full-history end must be after start")
    current = start
    while current < end_exclusive:
        boundary = _next_month(date(current.year, current.month, 1))
        right = min(boundary, end_exclusive)
        yield current, right
        current = right


def _atomic_json(path: Path, payload: object) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{destination.name}.part-", dir=destination.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, sort_keys=True, indent=2, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, destination)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise


class RecordingCompleteRawChunkReader:
    def __init__(self, inner: ReaderLike) -> None:
        self.inner = inner
        self.records: list[dict[str, object]] = []
        self._lock = Lock()

    def read(self, key: RawChunkKey) -> bytes:
        body = self.inner.read(key)
        if body is None:
            raise ValueError(
                f"full-history raw chunk unexpectedly not_found: {key.pair} {key.side} {key.day}"
            )
        record = {
            "pair": key.pair,
            "side": key.side,
            "date_utc": key.day.isoformat(),
            "sha256": hashlib.sha256(body).hexdigest(),
            "size_bytes": len(body),
            "status": "complete",
        }
        with self._lock:
            self.records.append(record)
        return body

    def write_ledger(self, path: Path) -> None:
        ordered = sorted(
            self.records,
            key=lambda item: (str(item["date_utc"]), str(item["side"]), str(item["pair"])),
        )
        _atomic_json(Path(path), ordered)


def _expected_identities(pair: str, start: date, end_exclusive: date) -> set[tuple[str, str, str]]:
    expected: set[tuple[str, str, str]] = set()
    day = start
    while day < end_exclusive:
        for side in ("BID", "ASK"):
            expected.add((pair, side, day.isoformat()))
        day += timedelta(days=1)
    return expected


def validate_full_history_ledger(
    records: list[dict[str, object]],
    pair: str,
    start: date,
    end_exclusive: date,
) -> None:
    if pair not in FULL_HISTORY_PAIRS:
        raise ValueError("full-history ledger pair is outside frozen V1 scope")
    if end_exclusive <= start:
        raise ValueError("full-history ledger range is invalid")

    observed: set[tuple[str, str, str]] = set()
    for record in records:
        record_pair = record.get("pair")
        side = record.get("side")
        date_utc = record.get("date_utc")
        status = record.get("status")
        digest = record.get("sha256")
        size = record.get("size_bytes")
        if record_pair != pair or side not in ("BID", "ASK") or not isinstance(date_utc, str):
            raise ValueError("full-history raw ledger identity mismatch")
        if status != "complete":
            raise ValueError("full-history raw ledger requires complete chunks")
        if not isinstance(digest, str) or len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ValueError("full-history raw ledger SHA-256 is invalid")
        if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
            raise ValueError("full-history raw ledger size is invalid")
        identity = (str(record_pair), str(side), date_utc)
        if identity in observed:
            raise ValueError("full-history raw ledger contains duplicate identity")
        observed.add(identity)

    expected = _expected_identities(pair, start, end_exclusive)
    if observed != expected or len(records) != len(expected):
        raise ValueError("full-history raw ledger does not match frozen pair/date/side plan")


def materialize_pair(
    reader: ReaderLike,
    output_root: Path,
    pair: str,
    *,
    start: date,
    end_exclusive: date,
    code_commit: str | None,
    workers: int,
) -> dict[str, object]:
    from .full_history_materialize import materialize_pair as _materialize_pair

    return _materialize_pair(
        reader,
        output_root,
        pair,
        start=start,
        end_exclusive=end_exclusive,
        code_commit=code_commit,
        workers=workers,
    )
