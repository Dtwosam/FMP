from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

_ACTIVE_STATUSES = {"requested", "queued", "waiting", "pending", "in_progress"}
_KNOWN_STATUSES = _ACTIVE_STATUSES | {"completed"}


def _utc_timestamp(value: object, *, field: str, run_id: int) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"GitHub acquisition workflow run {run_id} has invalid {field}")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(
            f"GitHub acquisition workflow run {run_id} has invalid {field}"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError(
            f"GitHub acquisition workflow run {run_id} {field} must use UTC"
        )
    return parsed


def _is_no_source_push(run: dict[str, object]) -> bool:
    head_commit = run.get("head_commit")
    message = head_commit.get("message") if isinstance(head_commit, dict) else None
    return (
        run.get("event") == "push"
        and isinstance(message, str)
        and "[phase1-no-source]" in message
    )


def select_acquisition_baseline(workflow_runs: object) -> dict[str, Any]:
    """Select the newest completed source-capable Phase 1 acquisition run.

    Push-triggered [phase1-no-source] runs are ignored because their acquisition
    jobs are suppressed. Manual workflow_dispatch runs remain source-capable
    regardless of the underlying head-commit message.
    """

    if not isinstance(workflow_runs, list):
        raise ValueError("GitHub acquisition workflow runs must be a list")

    candidates: list[tuple[datetime, int, str]] = []
    ignored_no_source = 0

    for index, run in enumerate(workflow_runs):
        if not isinstance(run, dict):
            raise ValueError(f"GitHub acquisition workflow run {index} must be an object")

        run_id = run.get("id")
        if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
            raise ValueError(f"GitHub acquisition workflow run {index} has invalid id")

        if _is_no_source_push(run):
            ignored_no_source += 1
            continue

        status = run.get("status")
        if not isinstance(status, str) or status not in _KNOWN_STATUSES:
            raise ValueError(
                f"GitHub acquisition workflow run {run_id} has invalid status"
            )
        updated_at = _utc_timestamp(
            run.get("updated_at"), field="updated_at", run_id=run_id
        )
        candidates.append((updated_at, run_id, status))

    active_run_ids = sorted(
        run_id
        for _, run_id, status in candidates
        if status in _ACTIVE_STATUSES
    )
    if active_run_ids:
        raise ValueError(
            "Phase 1 acquisition is still active; final cloud audit requires "
            f"a stable cloud snapshot (runs {active_run_ids})"
        )

    if not candidates:
        raise ValueError(
            "Phase 1 final audit requires a completed source-capable acquisition baseline run"
        )

    latest_updated_at, latest_run_id, latest_status = max(
        candidates, key=lambda item: (item[0], item[1])
    )
    if latest_status != "completed":
        raise ValueError(
            "Phase 1 final audit requires the latest source-capable acquisition "
            "baseline run to be completed"
        )

    return {
        "latest_run_id": latest_run_id,
        "baseline_completed_at_utc": latest_updated_at.isoformat().replace(
            "+00:00", "Z"
        ),
        "source_capable_runs_checked": len(candidates),
        "no_source_runs_ignored": ignored_no_source,
    }
