from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta
from typing import Mapping, Protocol, Sequence

from fmp.phase9.execution_gate import DEMO_EXECUTION_SOURCE_ARMED
from fmp.phase9.mt5_mutation import (
    build_phase9_mt5_send_result,
    validate_phase9_mt5_send_result,
)
from fmp.phase9.permit import validate_phase9_demo_execution_permit
from fmp.phase9.protocol import (
    DemoExecutionLockedError,
    build_phase9_demo_reconciliation,
    validate_phase9_demo_reconciliation,
)
from fmp.phase9.session import (
    Phase9DemoSessionJournal,
    build_phase9_send_attempt_payload,
    phase9_demo_session_attempt_count,
    validate_phase9_demo_session_journal,
)


PHASE9_DEMO_ONE_SHOT_RUNNER_DECISION = "DEC-065"
PHASE9_DEMO_ONE_SHOT_RUNNER_EXPERIMENT_ID = "EXP-20260922-036"
PHASE9_DEMO_ONE_SHOT_RUN_PROTOCOL = "fmp-phase9-demo-one-shot-run-v1"

PHASE9_DEMO_ONE_SHOT_COMPLETED = "PHASE9_DEMO_ONE_SHOT_COMPLETED"
PHASE9_DEMO_ONE_SHOT_NOT_COMPLETED = "PHASE9_DEMO_ONE_SHOT_NOT_COMPLETED"
PHASE9_DEMO_ONE_SHOT_AMBIGUOUS = "PHASE9_DEMO_ONE_SHOT_AMBIGUOUS"

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class Phase9DemoOneShotBackend(Protocol):
    def order_send(
        self,
        mt5_request: Mapping[str, object],
    ) -> Mapping[str, object]: ...

    def broker_orders(self) -> Sequence[Mapping[str, object]]: ...

    def broker_positions(self) -> Sequence[Mapping[str, object]]: ...


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase SHA-256")
    return value


def _utc(value: object, *, field: str) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() != timedelta(0)
    ):
        raise ValueError(f"{field} must use UTC")
    return value


def _parse_utc(value: object, *, field: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{field} must be an ISO-8601 UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO-8601 UTC timestamp") from exc
    return _utc(parsed, field=field)


def _journal_snapshot(
    journal: Phase9DemoSessionJournal,
) -> tuple[dict[str, object], ...]:
    rows = tuple(dict(row) for row in journal.rows)
    validate_phase9_demo_session_journal(rows)
    return rows


def _validate_runner_inputs(
    *,
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
    execution_arm: Mapping[str, object],
    runtime_authority: Mapping[str, object],
    launch_preflight: Mapping[str, object],
    execution_permit: Mapping[str, object],
    journal_rows: Sequence[Mapping[str, object]],
    now_utc: datetime,
    daily_halt_active: bool,
) -> Mapping[str, object]:
    validate_phase9_demo_execution_permit(
        execution_permit,
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
        runtime_authority=runtime_authority,
        launch_preflight=launch_preflight,
        journal_rows=journal_rows,
    )
    now = _utc(now_utc, field="Phase 9 one-shot runner time")
    if not isinstance(daily_halt_active, bool):
        raise ValueError("Phase 9 one-shot daily-halt state must be boolean")
    if daily_halt_active:
        raise ValueError("Phase 9 one-shot daily halt is active")

    start = _parse_utc(
        execution_permit.get("not_before_utc"),
        field="Phase 9 one-shot permit not-before",
    )
    end = _parse_utc(
        execution_permit.get("expires_at_utc"),
        field="Phase 9 one-shot permit expiry",
    )
    launch_time = _parse_utc(
        execution_permit.get("launch_preflight_time_utc"),
        field="Phase 9 one-shot launch-preflight time",
    )
    if now < start or now > end:
        raise ValueError("Phase 9 one-shot runner time is outside arm window")
    if now < launch_time:
        raise ValueError(
            "Phase 9 one-shot runner time precedes launch preflight"
        )
    if execution_permit.get("practice_only") is not True:
        raise ValueError("Phase 9 one-shot permit must be practice-only")
    if execution_permit.get("max_new_orders") != 1:
        raise ValueError("Phase 9 one-shot permit must allow exactly one order")
    if execution_permit.get("send_attempt_count") != 0:
        raise ValueError("Phase 9 one-shot permit is already spent")
    if execution_permit.get("daily_halt_active") is not False:
        raise ValueError("Phase 9 one-shot permit daily halt is active")

    validate_phase9_demo_session_journal(journal_rows)
    if phase9_demo_session_attempt_count(journal_rows) != 0:
        raise ValueError(
            "Phase 9 one-shot runner requires zero prior SEND_ATTEMPTED events"
        )
    if execution_permit.get("journal_event_count") != len(journal_rows):
        raise ValueError("Phase 9 one-shot journal count changed after permit")
    expected_tip = (
        None
        if not journal_rows
        else _sha256(
            journal_rows[-1].get("event_fingerprint"),
            field="Phase 9 one-shot journal tip",
        )
    )
    if execution_permit.get("journal_tip_fingerprint") != expected_tip:
        raise ValueError("Phase 9 one-shot journal tip changed after permit")

    order_check_request = launch_preflight.get("order_check_request")
    if not isinstance(order_check_request, Mapping):
        raise ValueError("Phase 9 one-shot checked request is malformed")
    checked_mt5_request = order_check_request.get("mt5_request")
    if not isinstance(checked_mt5_request, Mapping):
        raise ValueError("Phase 9 one-shot MT5 request is malformed")
    if execution_permit.get("checked_mt5_request_sha256") != _digest(
        dict(checked_mt5_request)
    ):
        raise ValueError("Phase 9 one-shot checked MT5 request changed")
    if execution_permit.get("order_check_request_fingerprint") != (
        order_check_request.get("order_check_request_fingerprint")
    ):
        raise ValueError("Phase 9 one-shot order-check request changed")
    order_check = launch_preflight.get("order_check")
    if not isinstance(order_check, Mapping):
        raise ValueError("Phase 9 one-shot order-check evidence is malformed")
    if execution_permit.get("order_check_fingerprint") != order_check.get(
        "order_check_fingerprint"
    ):
        raise ValueError("Phase 9 one-shot order-check evidence changed")
    if order_check.get("check_passed") is not True:
        raise ValueError("Phase 9 one-shot order-check is not passed")

    return checked_mt5_request


def _append_reconciliation(
    *,
    journal: Phase9DemoSessionJournal,
    event_time_utc: datetime,
    reconciliation: Mapping[str, object] | None,
    error: BaseException | None,
) -> dict[str, object]:
    healthy = (
        reconciliation is not None
        and reconciliation.get("healthy") is True
        and error is None
    )
    payload: dict[str, object] = {
        "healthy": healthy,
        "reconciliation_fingerprint": (
            None
            if reconciliation is None
            else reconciliation.get("reconciliation_fingerprint")
        ),
    }
    if error is not None:
        payload["error_type"] = type(error).__name__
        payload["error_message"] = str(error)
    return journal.append(
        event_time_utc=event_time_utc,
        event_type=(
            "POST_SEND_RECONCILIATION_OK"
            if healthy
            else "POST_SEND_RECONCILIATION_FAILED"
        ),
        payload=payload,
    )


def _reconcile_after_send(
    *,
    design: Mapping[str, object],
    request: Mapping[str, object],
    backend: Phase9DemoOneShotBackend,
) -> tuple[dict[str, object] | None, BaseException | None]:
    try:
        broker_orders = [dict(row) for row in backend.broker_orders()]
        broker_positions = [dict(row) for row in backend.broker_positions()]
        reconciliation = build_phase9_demo_reconciliation(
            design=design,
            local_requests=[request],
            broker_orders=broker_orders,
            broker_positions=broker_positions,
        )
        validate_phase9_demo_reconciliation(reconciliation)
        return reconciliation, None
    except BaseException as exc:
        return None, exc


def _build_run_result(
    *,
    outcome: str,
    execution_permit: Mapping[str, object],
    request: Mapping[str, object],
    checked_mt5_request: Mapping[str, object],
    send_attempt_event: Mapping[str, object],
    send_result: Mapping[str, object] | None,
    reconciliation: Mapping[str, object] | None,
    journal: Phase9DemoSessionJournal,
) -> dict[str, object]:
    rows = _journal_snapshot(journal)
    if phase9_demo_session_attempt_count(rows) != 1:
        raise ValueError("Phase 9 one-shot runner must spend exactly one attempt")
    payload = {
        "protocol": PHASE9_DEMO_ONE_SHOT_RUN_PROTOCOL,
        "experiment_id": PHASE9_DEMO_ONE_SHOT_RUNNER_EXPERIMENT_ID,
        "decision": PHASE9_DEMO_ONE_SHOT_RUNNER_DECISION,
        "outcome": outcome,
        "execution_permit_fingerprint": execution_permit[
            "execution_permit_fingerprint"
        ],
        "request_fingerprint": request["request_fingerprint"],
        "client_order_id": request["client_order_id"],
        "checked_mt5_request_sha256": _digest(dict(checked_mt5_request)),
        "send_attempt_event_fingerprint": send_attempt_event[
            "event_fingerprint"
        ],
        "send_result_fingerprint": (
            None
            if send_result is None
            else send_result["send_result_fingerprint"]
        ),
        "reconciliation_fingerprint": (
            None
            if reconciliation is None
            else reconciliation["reconciliation_fingerprint"]
        ),
        "journal_event_count": len(rows),
        "journal_tip_fingerprint": rows[-1]["event_fingerprint"],
        "send_attempt_count": 1,
        "arm_spent": True,
        "demo_one_shot_runner_source_ready": True,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
    }
    result = payload | {"one_shot_run_fingerprint": _digest(payload)}
    validate_phase9_demo_one_shot_run(result)
    return result


def validate_phase9_demo_one_shot_run(
    value: Mapping[str, object],
) -> None:
    if value.get("protocol") != PHASE9_DEMO_ONE_SHOT_RUN_PROTOCOL:
        raise ValueError("Phase 9 one-shot run protocol mismatch")
    if value.get("experiment_id") != PHASE9_DEMO_ONE_SHOT_RUNNER_EXPERIMENT_ID:
        raise ValueError("Phase 9 one-shot run experiment mismatch")
    if value.get("decision") != PHASE9_DEMO_ONE_SHOT_RUNNER_DECISION:
        raise ValueError("Phase 9 one-shot run decision mismatch")
    if value.get("outcome") not in {
        PHASE9_DEMO_ONE_SHOT_COMPLETED,
        PHASE9_DEMO_ONE_SHOT_NOT_COMPLETED,
        PHASE9_DEMO_ONE_SHOT_AMBIGUOUS,
    }:
        raise ValueError("Phase 9 one-shot run outcome is invalid")
    for field in (
        "execution_permit_fingerprint",
        "request_fingerprint",
        "checked_mt5_request_sha256",
        "send_attempt_event_fingerprint",
        "one_shot_run_fingerprint",
    ):
        _sha256(value.get(field), field=f"Phase 9 one-shot run {field}")
    for field in ("send_result_fingerprint", "reconciliation_fingerprint"):
        raw = value.get(field)
        if raw is not None:
            _sha256(raw, field=f"Phase 9 one-shot run {field}")
    if value.get("send_attempt_count") != 1:
        raise ValueError("Phase 9 one-shot run requires exactly one attempt")
    if value.get("arm_spent") is not True:
        raise ValueError("Phase 9 one-shot run must spend the arm")
    if value.get("demo_one_shot_runner_source_ready") is not True:
        raise ValueError("Phase 9 one-shot runner source is not ready")
    for field in (
        "live_order_authorized",
        "real_money_authorized",
        "phase10_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(f"Phase 9 one-shot run requires {field}=false")
    fingerprint = value["one_shot_run_fingerprint"]
    payload = dict(value)
    payload.pop("one_shot_run_fingerprint", None)
    if fingerprint != _digest(payload):
        raise ValueError("Phase 9 one-shot run fingerprint mismatch")


def run_phase9_demo_one_shot(
    *,
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
    execution_arm: Mapping[str, object],
    runtime_authority: Mapping[str, object],
    launch_preflight: Mapping[str, object],
    execution_permit: Mapping[str, object],
    journal: Phase9DemoSessionJournal,
    backend: Phase9DemoOneShotBackend,
    now_utc: datetime,
    daily_halt_active: bool,
) -> dict[str, object]:
    journal_rows = _journal_snapshot(journal)
    checked_mt5_request = _validate_runner_inputs(
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
        runtime_authority=runtime_authority,
        launch_preflight=launch_preflight,
        execution_permit=execution_permit,
        journal_rows=journal_rows,
        now_utc=now_utc,
        daily_halt_active=daily_halt_active,
    )
    if DEMO_EXECUTION_SOURCE_ARMED is not True:
        raise DemoExecutionLockedError(
            "DEC-065 keeps demo execution source unarmed"
        )

    attempt_payload = build_phase9_send_attempt_payload(
        order_check_request_fingerprint=str(
            execution_permit["order_check_request_fingerprint"]
        ),
        order_check_fingerprint=str(
            execution_permit["order_check_fingerprint"]
        ),
        checked_mt5_request=checked_mt5_request,
    )
    attempt_payload["execution_permit_fingerprint"] = _sha256(
        execution_permit.get("execution_permit_fingerprint"),
        field="Phase 9 execution-permit fingerprint",
    )
    send_attempt = journal.append(
        event_time_utc=now_utc,
        event_type="SEND_ATTEMPTED",
        payload=attempt_payload,
    )

    send_result: dict[str, object] | None = None
    send_error: BaseException | None = None
    try:
        raw_result = dict(backend.order_send(dict(checked_mt5_request)))
        expected_volume = checked_mt5_request.get("volume")
        if isinstance(expected_volume, bool) or not isinstance(
            expected_volume, (int, float)
        ):
            raise ValueError("Phase 9 checked MT5 volume is malformed")
        send_result = build_phase9_mt5_send_result(
            request_fingerprint=str(request["request_fingerprint"]),
            order_check_request_fingerprint=str(
                execution_permit["order_check_request_fingerprint"]
            ),
            order_check_fingerprint=str(
                execution_permit["order_check_fingerprint"]
            ),
            expected_volume_lots=float(expected_volume),
            raw_result=raw_result,
        )
        validate_phase9_mt5_send_result(send_result)
        journal.append(
            event_time_utc=now_utc,
            event_type="SEND_RESULT",
            payload=dict(send_result),
        )
    except BaseException as exc:
        send_error = exc
        journal.append(
            event_time_utc=now_utc,
            event_type="SESSION_HALTED",
            payload={
                "reason": "ORDER_SEND_AMBIGUOUS",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "retry_authorized": False,
            },
        )

    reconciliation, reconciliation_error = _reconcile_after_send(
        design=design,
        request=request,
        backend=backend,
    )
    _append_reconciliation(
        journal=journal,
        event_time_utc=now_utc,
        reconciliation=reconciliation,
        error=reconciliation_error,
    )

    if send_error is not None:
        outcome = PHASE9_DEMO_ONE_SHOT_AMBIGUOUS
    elif reconciliation_error is not None:
        outcome = PHASE9_DEMO_ONE_SHOT_AMBIGUOUS
    elif reconciliation is None or reconciliation.get("healthy") is not True:
        outcome = PHASE9_DEMO_ONE_SHOT_AMBIGUOUS
    elif send_result is not None and send_result.get("completed") is True:
        outcome = PHASE9_DEMO_ONE_SHOT_COMPLETED
    else:
        outcome = PHASE9_DEMO_ONE_SHOT_NOT_COMPLETED

    return _build_run_result(
        outcome=outcome,
        execution_permit=execution_permit,
        request=request,
        checked_mt5_request=checked_mt5_request,
        send_attempt_event=send_attempt,
        send_result=send_result,
        reconciliation=reconciliation,
        journal=journal,
    )


__all__ = [
    "PHASE9_DEMO_ONE_SHOT_AMBIGUOUS",
    "PHASE9_DEMO_ONE_SHOT_COMPLETED",
    "PHASE9_DEMO_ONE_SHOT_NOT_COMPLETED",
    "PHASE9_DEMO_ONE_SHOT_RUNNER_DECISION",
    "PHASE9_DEMO_ONE_SHOT_RUNNER_EXPERIMENT_ID",
    "PHASE9_DEMO_ONE_SHOT_RUN_PROTOCOL",
    "Phase9DemoOneShotBackend",
    "run_phase9_demo_one_shot",
    "validate_phase9_demo_one_shot_run",
]
