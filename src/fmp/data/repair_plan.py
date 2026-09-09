from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .types import RawChunkKey

_PLAN_VERSION = 1
_FROZEN_START_DATE = date(2015, 1, 1)
_FROZEN_END_DATE_EXCLUSIVE = date(2026, 8, 21)
_REQUIRED_ROOT_FIELDS = {"plan_version", "frozen_start_date", "frozen_end_date_exclusive", "chunks"}
_REQUIRED_CHUNK_FIELDS = {"pair", "side", "date_utc"}


def load_exact_gap_plan(path: Path) -> list[RawChunkKey]:
    """Load and strictly validate an exact Phase 1 repair plan.

    The plan is intentionally explicit: every entry identifies exactly one
    pair/date/side chunk. This prevents sparse cleanup from silently expanding
    back into month- or range-level acquisition.
    """
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid exact-gap plan: {path}") from exc

    if not isinstance(payload, dict):
        raise ValueError("exact-gap plan root must be a JSON object")
    if set(payload) != _REQUIRED_ROOT_FIELDS:
        raise ValueError(
            f"exact-gap plan root must contain exactly {sorted(_REQUIRED_ROOT_FIELDS)}"
        )
    if payload.get("plan_version") != _PLAN_VERSION:
        raise ValueError(f"exact-gap plan_version must be {_PLAN_VERSION}")
    if payload.get("frozen_start_date") != _FROZEN_START_DATE.isoformat():
        raise ValueError("exact-gap plan frozen_start_date does not match Phase 1 snapshot")
    if payload.get("frozen_end_date_exclusive") != _FROZEN_END_DATE_EXCLUSIVE.isoformat():
        raise ValueError("exact-gap plan frozen_end_date_exclusive does not match Phase 1 snapshot")

    chunks = payload.get("chunks")
    if not isinstance(chunks, list) or not chunks:
        raise ValueError("exact-gap plan must contain a non-empty chunks list")

    keys: list[RawChunkKey] = []
    seen: set[RawChunkKey] = set()
    for index, chunk in enumerate(chunks):
        if not isinstance(chunk, dict):
            raise ValueError(f"exact-gap chunk {index} must be a JSON object")
        if set(chunk) != _REQUIRED_CHUNK_FIELDS:
            raise ValueError(
                f"exact-gap chunk {index} must contain exactly "
                f"{sorted(_REQUIRED_CHUNK_FIELDS)}"
            )

        pair = chunk["pair"]
        side = chunk["side"]
        date_utc = chunk["date_utc"]
        if not all(isinstance(value, str) for value in (pair, side, date_utc)):
            raise ValueError(f"exact-gap chunk {index} fields must be strings")
        try:
            day = date.fromisoformat(date_utc)
        except ValueError as exc:
            raise ValueError(f"exact-gap chunk {index} date_utc must be YYYY-MM-DD") from exc

        if not (_FROZEN_START_DATE <= day < _FROZEN_END_DATE_EXCLUSIVE):
            raise ValueError(
                f"exact-gap chunk {index} is outside the frozen Phase 1 snapshot: {date_utc}"
            )
        try:
            key = RawChunkKey(pair, side, day)  # type: ignore[arg-type]
        except ValueError as exc:
            raise ValueError(f"invalid exact-gap chunk {index}: {exc}") from exc
        if key in seen:
            raise ValueError(
                f"duplicate exact-gap chunk: {key.pair}/{key.day.isoformat()}/{key.side}"
            )
        seen.add(key)
        keys.append(key)

    canonical = sorted(keys, key=lambda item: (item.day, item.pair, item.side))
    if keys != canonical:
        raise ValueError("exact-gap chunks must be in canonical date/pair/side order")

    return keys
