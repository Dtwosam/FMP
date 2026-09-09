from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .types import RawChunkKey

_PLAN_VERSION = 1
_FROZEN_START_DATE = date(2015, 1, 1)
_FROZEN_END_DATE_EXCLUSIVE = date(2026, 8, 21)
_REQUIRED_ROOT_FIELDS = {
    "plan_version",
    "frozen_start_date",
    "frozen_end_date_exclusive",
    "audited_at_utc",
    "present_manifests_at_audit",
    "missing_manifests_at_audit",
    "chunks",
}
_FROZEN_MANIFEST_TARGET = 25_500
_REQUIRED_CHUNK_FIELDS = {"pair", "side", "date_utc"}
_DEFAULT_MAX_PLAN_AGE = timedelta(hours=2)


def _load_validated_exact_gap_plan(path: Path) -> tuple[list[RawChunkKey], datetime]:
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

    audited_at_utc = payload.get("audited_at_utc")
    if not isinstance(audited_at_utc, str):
        raise ValueError("exact-gap plan audited_at_utc must be a string")
    try:
        audited_at = datetime.fromisoformat(audited_at_utc.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("exact-gap plan audited_at_utc must be ISO-8601") from exc
    if audited_at.tzinfo is None or audited_at.utcoffset() is None:
        raise ValueError("exact-gap plan audited_at_utc must be timezone-aware")
    if audited_at.utcoffset() != timedelta(0):
        raise ValueError("exact-gap plan audited_at_utc must use UTC")
    audited_at = audited_at.astimezone(timezone.utc)

    present = payload.get("present_manifests_at_audit")
    missing = payload.get("missing_manifests_at_audit")
    if (
        not isinstance(present, int)
        or isinstance(present, bool)
        or not isinstance(missing, int)
        or isinstance(missing, bool)
        or present < 0
        or missing < 0
    ):
        raise ValueError("exact-gap audit manifest counts must be non-negative integers")
    if present + missing != _FROZEN_MANIFEST_TARGET:
        raise ValueError("exact-gap audit manifest counts must reconcile to frozen 25,500 target")

    chunks = payload.get("chunks")
    if not isinstance(chunks, list) or not chunks:
        raise ValueError("exact-gap plan must contain a non-empty chunks list")
    if missing != len(chunks):
        raise ValueError("exact-gap missing manifest count must equal chunk count")

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

    return keys, audited_at


def load_exact_gap_plan(path: Path) -> list[RawChunkKey]:
    """Load and strictly validate an exact Phase 1 repair plan.

    This validates structural identity and the frozen-snapshot accounting
    contract. Operational freshness is a separate pre-source gate.
    """
    keys, _ = _load_validated_exact_gap_plan(path)
    return keys


def ensure_exact_gap_plan_fresh(
    path: Path,
    *,
    now_utc: datetime | None = None,
    max_age: timedelta = _DEFAULT_MAX_PLAN_AGE,
) -> list[RawChunkKey]:
    """Validate an exact-gap plan and reject stale/future cloud audits.

    Returns the validated explicit keys so callers can use the same parsed plan
    after the freshness gate. The default two-hour limit allows normal GitHub
    queue latency while preventing old sparse snapshots from driving new source
    requests.
    """
    if max_age <= timedelta(0):
        raise ValueError("exact-gap max plan age must be positive")

    now = now_utc or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("exact-gap freshness clock must be timezone-aware")
    now = now.astimezone(timezone.utc)

    keys, audited_at = _load_validated_exact_gap_plan(path)
    age = now - audited_at
    if age < timedelta(0):
        raise ValueError("exact-gap plan audit timestamp is in the future")
    if age > max_age:
        raise ValueError(
            f"exact-gap plan is stale: age {age} exceeds maximum {max_age}"
        )
    return keys
