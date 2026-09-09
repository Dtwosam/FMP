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
    plan_version = payload.get("plan_version")
    if (
        not isinstance(plan_version, int)
        or isinstance(plan_version, bool)
        or plan_version != _PLAN_VERSION
    ):
        raise ValueError(f"exact-gap plan_version must be integer {_PLAN_VERSION}")
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


def ensure_no_intervening_acquisition_runs(
    path: Path,
    workflow_runs: object,
    *,
    current_run_id: int,
) -> dict[str, object]:
    """Reject an exact-gap plan if another source-capable acquisition changed after its audit."""

    if (
        not isinstance(current_run_id, int)
        or isinstance(current_run_id, bool)
        or current_run_id <= 0
    ):
        raise ValueError("current GitHub workflow run id must be a positive integer")
    if not isinstance(workflow_runs, list):
        raise ValueError("GitHub acquisition workflow runs must be a list")

    _, audited_at = _load_validated_exact_gap_plan(path)
    github_precision_boundary = audited_at.replace(microsecond=0)
    checked = 0
    ignored_no_source = 0
    latest_prior_run_id: int | None = None
    latest_prior_updated_at: datetime | None = None

    for index, run in enumerate(workflow_runs):
        if not isinstance(run, dict):
            raise ValueError(f"GitHub acquisition workflow run {index} must be an object")

        run_id = run.get("id")
        if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
            raise ValueError(f"GitHub acquisition workflow run {index} has invalid id")
        if run_id == current_run_id:
            continue

        head_commit = run.get("head_commit")
        message = head_commit.get("message") if isinstance(head_commit, dict) else None
        if (
            run.get("event") == "push"
            and isinstance(message, str)
            and "[phase1-no-source]" in message
        ):
            ignored_no_source += 1
            continue

        updated_at_raw = run.get("updated_at")
        if not isinstance(updated_at_raw, str):
            raise ValueError(
                f"GitHub acquisition workflow run {run_id} has invalid updated_at"
            )
        try:
            updated_at = datetime.fromisoformat(
                updated_at_raw.replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise ValueError(
                f"GitHub acquisition workflow run {run_id} has invalid updated_at"
            ) from exc
        if updated_at.tzinfo is None or updated_at.utcoffset() != timedelta(0):
            raise ValueError(
                f"GitHub acquisition workflow run {run_id} updated_at must use UTC"
            )
        updated_at = updated_at.astimezone(timezone.utc)

        checked += 1
        if latest_prior_updated_at is None or updated_at > latest_prior_updated_at:
            latest_prior_run_id = run_id
            latest_prior_updated_at = updated_at

        if updated_at >= github_precision_boundary:
            raise ValueError(
                "exact-gap plan invalidated by intervening acquisition workflow run "
                f"{run_id}: GitHub reports run updated at {updated_at.isoformat()}, "
                "which is at or after the audit's observable UTC-second boundary "
                f"{github_precision_boundary.isoformat()} "
                f"(audit {audited_at.isoformat()})"
            )

    return {
        "guard_version": 1,
        "current_run_id": current_run_id,
        "plan_audited_at_utc": audited_at.isoformat().replace("+00:00", "Z"),
        "source_capable_runs_checked": checked,
        "no_source_runs_ignored": ignored_no_source,
        "latest_prior_source_run_id": latest_prior_run_id,
        "latest_prior_source_run_updated_at_utc": (
            latest_prior_updated_at.isoformat().replace("+00:00", "Z")
            if latest_prior_updated_at is not None
            else None
        ),
        "ready": True,
    }


def ensure_no_source_capable_acquisition_updates_since(
    workflow_runs: object,
    *,
    guard_started_at_utc: datetime,
) -> dict[str, object]:
    """Reject final audit evidence if source-capable acquisition changed after guard start."""

    if not isinstance(workflow_runs, list):
        raise ValueError("GitHub acquisition workflow runs must be a list")
    if (
        guard_started_at_utc.tzinfo is None
        or guard_started_at_utc.utcoffset() is None
        or guard_started_at_utc.utcoffset() != timedelta(0)
    ):
        raise ValueError("final cloud audit guard start must use UTC")

    github_precision_boundary = guard_started_at_utc.astimezone(timezone.utc).replace(
        microsecond=0
    )
    checked = 0
    ignored_no_source = 0
    latest_checked_run_id: int | None = None
    latest_checked_updated_at: datetime | None = None

    for index, run in enumerate(workflow_runs):
        if not isinstance(run, dict):
            raise ValueError(f"GitHub acquisition workflow run {index} must be an object")

        run_id = run.get("id")
        if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
            raise ValueError(f"GitHub acquisition workflow run {index} has invalid id")

        head_commit = run.get("head_commit")
        message = head_commit.get("message") if isinstance(head_commit, dict) else None
        if (
            run.get("event") == "push"
            and isinstance(message, str)
            and "[phase1-no-source]" in message
        ):
            ignored_no_source += 1
            continue

        updated_at_raw = run.get("updated_at")
        if not isinstance(updated_at_raw, str):
            raise ValueError(
                f"GitHub acquisition workflow run {run_id} has invalid updated_at"
            )
        try:
            updated_at = datetime.fromisoformat(
                updated_at_raw.replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise ValueError(
                f"GitHub acquisition workflow run {run_id} has invalid updated_at"
            ) from exc
        if updated_at.tzinfo is None or updated_at.utcoffset() != timedelta(0):
            raise ValueError(
                f"GitHub acquisition workflow run {run_id} updated_at must use UTC"
            )
        updated_at = updated_at.astimezone(timezone.utc)

        checked += 1
        if latest_checked_updated_at is None or updated_at > latest_checked_updated_at:
            latest_checked_run_id = run_id
            latest_checked_updated_at = updated_at

        if updated_at >= github_precision_boundary:
            raise ValueError(
                "Phase 1 acquisition changed during final cloud audit: "
                f"source-capable workflow run {run_id} was updated at "
                f"{updated_at.isoformat()}, at or after the audit guard's observable "
                f"UTC-second boundary {github_precision_boundary.isoformat()}"
            )

    return {
        "guard_version": 1,
        "guard_started_at_utc": guard_started_at_utc.isoformat().replace("+00:00", "Z"),
        "github_precision_boundary_utc": github_precision_boundary.isoformat().replace(
            "+00:00", "Z"
        ),
        "source_capable_runs_checked": checked,
        "no_source_runs_ignored": ignored_no_source,
        "latest_checked_source_run_id": latest_checked_run_id,
        "latest_checked_source_run_updated_at_utc": (
            latest_checked_updated_at.isoformat().replace("+00:00", "Z")
            if latest_checked_updated_at is not None
            else None
        ),
        "ready": True,
    }


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
