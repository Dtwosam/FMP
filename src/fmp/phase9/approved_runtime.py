from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta
from typing import Mapping

from fmp.phase9.approval import (
    validate_phase9_demo_gate_activation_contract,
)
from fmp.phase9.execution_gate import DEMO_EXECUTION_SOURCE_ARMED
from fmp.phase9.protocol import DemoExecutionLockedError
from fmp.phase9.runner import (
    Phase9DemoOneShotBackend,
    run_phase9_demo_one_shot,
    validate_phase9_demo_one_shot_run,
)
from fmp.phase9.session import (
    Phase9DemoSessionJournal,
    phase9_demo_session_attempt_count,
    validate_phase9_demo_session_journal,
)


PHASE9_APPROVED_DEMO_RUNTIME_DECISION = "DEC-069"
PHASE9_APPROVED_DEMO_RUNTIME_EXPERIMENT_ID = "EXP-20260922-040"
PHASE9_APPROVED_DEMO_RUNTIME_PROTOCOL = "fmp-phase9-approved-demo-runtime-v1"

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


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


def _utc_string(value: datetime) -> str:
    _utc(value, field="timestamp")
    return value.isoformat().replace("+00:00", "Z")


def _parse_utc(value: object, *, field: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{field} must be an ISO-8601 UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO-8601 UTC timestamp") from exc
    return _utc(parsed, field=field)


def _journal_rows(
    journal: Phase9DemoSessionJournal,
) -> tuple[dict[str, object], ...]:
    rows = tuple(dict(row) for row in journal.rows)
    validate_phase9_demo_session_journal(rows)
    return rows


def _validate_runtime_state(
    *,
    activation_contract: Mapping[str, object],
    approval: Mapping[str, object],
    packet: Mapping[str, object],
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
    execution_arm: Mapping[str, object],
    runtime_authority: Mapping[str, object],
    launch_preflight: Mapping[str, object],
    execution_permit: Mapping[str, object],
    journal_rows: tuple[dict[str, object], ...],
    now_utc: datetime,
    daily_halt_active: bool,
) -> datetime:
    validate_phase9_demo_gate_activation_contract(
        activation_contract,
        approval=approval,
        packet=packet,
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
        runtime_authority=runtime_authority,
        launch_preflight=launch_preflight,
        execution_permit=execution_permit,
        journal_rows=journal_rows,
    )

    if not isinstance(daily_halt_active, bool):
        raise ValueError("Phase 9 approved-runtime daily-halt state must be boolean")
    if daily_halt_active:
        raise ValueError("Phase 9 approved-runtime daily halt is active")
    if phase9_demo_session_attempt_count(journal_rows) != 0:
        raise ValueError(
            "Phase 9 approved runtime requires zero prior SEND_ATTEMPTED events"
        )

    now = _utc(now_utc, field="Phase 9 approved-runtime time")
    start = _parse_utc(
        activation_contract.get("not_before_utc"),
        field="Phase 9 approved-runtime not-before",
    )
    end = _parse_utc(
        activation_contract.get("expires_at_utc"),
        field="Phase 9 approved-runtime expiry",
    )
    activated = _parse_utc(
        activation_contract.get("activation_time_utc"),
        field="Phase 9 approved-runtime activation time",
    )
    if now < start or now > end:
        raise ValueError("Phase 9 approved-runtime time is outside arm window")
    if now < activated:
        raise ValueError("Phase 9 approved-runtime time precedes activation")

    if activation_contract.get("practice_only") is not True:
        raise ValueError("Phase 9 approved runtime must be practice-only")
    if activation_contract.get("max_new_orders") != 1:
        raise ValueError("Phase 9 approved runtime must be one-order-only")
    if activation_contract.get("explicit_execution_approval_recorded") is not True:
        raise ValueError("Phase 9 approved runtime lacks explicit approval")
    if activation_contract.get("operator_gate_activation_contract_ready") is not True:
        raise ValueError("Phase 9 approved runtime activation contract is not ready")

    identities = {
        "execution_permit_fingerprint": execution_permit[
            "execution_permit_fingerprint"
        ],
        "request_fingerprint": request["request_fingerprint"],
        "client_order_id": request["client_order_id"],
    }
    review = packet.get("review")
    if not isinstance(review, Mapping):
        raise ValueError("Phase 9 approved-runtime packet review is malformed")
    execution = design.get("execution_path")
    if not isinstance(execution, Mapping):
        raise ValueError("Phase 9 approved-runtime execution path is malformed")
    identities.update(
        {
            "authorization_packet_fingerprint": packet[
                "authorization_packet_fingerprint"
            ],
            "authorization_challenge_fingerprint": packet[
                "authorization_challenge_fingerprint"
            ],
            "explicit_approval_fingerprint": approval[
                "explicit_approval_fingerprint"
            ],
            "account_fingerprint": execution["account_fingerprint"],
            "server": execution["server"],
        }
    )
    for field, expected in identities.items():
        if activation_contract.get(field) != expected:
            raise ValueError(f"Phase 9 approved-runtime {field} mismatch")

    return now


def run_phase9_approved_demo_one_shot(
    *,
    activation_contract: Mapping[str, object],
    approval: Mapping[str, object],
    packet: Mapping[str, object],
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
    rows = _journal_rows(journal)
    now = _validate_runtime_state(
        activation_contract=activation_contract,
        approval=approval,
        packet=packet,
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
        runtime_authority=runtime_authority,
        launch_preflight=launch_preflight,
        execution_permit=execution_permit,
        journal_rows=rows,
        now_utc=now_utc,
        daily_halt_active=daily_halt_active,
    )

    if DEMO_EXECUTION_SOURCE_ARMED is not True:
        raise DemoExecutionLockedError(
            "DEC-069 keeps approved demo runtime source unarmed"
        )

    one_shot = run_phase9_demo_one_shot(
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
        runtime_authority=runtime_authority,
        launch_preflight=launch_preflight,
        execution_permit=execution_permit,
        journal=journal,
        backend=backend,
        now_utc=now,
        daily_halt_active=daily_halt_active,
    )
    validate_phase9_demo_one_shot_run(one_shot)

    payload = {
        "protocol": PHASE9_APPROVED_DEMO_RUNTIME_PROTOCOL,
        "experiment_id": PHASE9_APPROVED_DEMO_RUNTIME_EXPERIMENT_ID,
        "decision": PHASE9_APPROVED_DEMO_RUNTIME_DECISION,
        "gate_activation_contract_fingerprint": activation_contract[
            "gate_activation_contract_fingerprint"
        ],
        "explicit_approval_fingerprint": approval[
            "explicit_approval_fingerprint"
        ],
        "authorization_packet_fingerprint": packet[
            "authorization_packet_fingerprint"
        ],
        "authorization_challenge_fingerprint": packet[
            "authorization_challenge_fingerprint"
        ],
        "execution_permit_fingerprint": execution_permit[
            "execution_permit_fingerprint"
        ],
        "request_fingerprint": request["request_fingerprint"],
        "client_order_id": request["client_order_id"],
        "activation_time_utc": activation_contract["activation_time_utc"],
        "runtime_time_utc": _utc_string(now),
        "one_shot_run_fingerprint": one_shot["one_shot_run_fingerprint"],
        "one_shot_outcome": one_shot["outcome"],
        "arm_spent": one_shot["arm_spent"],
        "send_attempt_count": one_shot["send_attempt_count"],
        "approved_runner_wiring_used": True,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
        "phase11_authorized": False,
    }
    result = payload | {"approved_runtime_fingerprint": _digest(payload)}
    validate_phase9_approved_demo_runtime(result)
    return result


def validate_phase9_approved_demo_runtime(
    value: Mapping[str, object],
) -> None:
    if value.get("protocol") != PHASE9_APPROVED_DEMO_RUNTIME_PROTOCOL:
        raise ValueError("Phase 9 approved-runtime protocol mismatch")
    if value.get("experiment_id") != PHASE9_APPROVED_DEMO_RUNTIME_EXPERIMENT_ID:
        raise ValueError("Phase 9 approved-runtime experiment mismatch")
    if value.get("decision") != PHASE9_APPROVED_DEMO_RUNTIME_DECISION:
        raise ValueError("Phase 9 approved-runtime decision mismatch")
    for field in (
        "gate_activation_contract_fingerprint",
        "explicit_approval_fingerprint",
        "authorization_packet_fingerprint",
        "authorization_challenge_fingerprint",
        "execution_permit_fingerprint",
        "request_fingerprint",
        "one_shot_run_fingerprint",
        "approved_runtime_fingerprint",
    ):
        _sha256(value.get(field), field=f"Phase 9 approved-runtime {field}")
    client = value.get("client_order_id")
    if not isinstance(client, str) or not client.strip():
        raise ValueError("Phase 9 approved-runtime client-order ID is invalid")
    _parse_utc(
        value.get("activation_time_utc"),
        field="Phase 9 approved-runtime activation time",
    )
    _parse_utc(
        value.get("runtime_time_utc"),
        field="Phase 9 approved-runtime time",
    )
    if value.get("send_attempt_count") != 1:
        raise ValueError("Phase 9 approved runtime requires exactly one attempt")
    if value.get("arm_spent") is not True:
        raise ValueError("Phase 9 approved runtime must spend the arm")
    if value.get("approved_runner_wiring_used") is not True:
        raise ValueError("Phase 9 approved runtime wiring flag mismatch")
    for field in (
        "live_order_authorized",
        "real_money_authorized",
        "phase10_authorized",
        "phase11_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(f"Phase 9 approved runtime requires {field}=false")
    fingerprint = value["approved_runtime_fingerprint"]
    payload = dict(value)
    payload.pop("approved_runtime_fingerprint", None)
    if fingerprint != _digest(payload):
        raise ValueError("Phase 9 approved-runtime fingerprint mismatch")


__all__ = [
    "PHASE9_APPROVED_DEMO_RUNTIME_DECISION",
    "PHASE9_APPROVED_DEMO_RUNTIME_EXPERIMENT_ID",
    "PHASE9_APPROVED_DEMO_RUNTIME_PROTOCOL",
    "run_phase9_approved_demo_one_shot",
    "validate_phase9_approved_demo_runtime",
]
