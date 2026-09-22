from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Mapping, Sequence

from fmp.phase9.design import validate_phase9_demo_design
from fmp.phase9.mt5_mutation import (
    DEMO_EXECUTION_SOURCE_ARMED,
    GatedMT5DemoMutationAdapter,
)
from fmp.phase9.protocol import (
    build_phase9_demo_reconciliation,
    validate_phase9_demo_order_request,
    validate_phase9_demo_reconciliation,
)


PHASE9_DEMO_SESSION_DECISION = "DEC-059"
PHASE9_DEMO_SESSION_EXPERIMENT_ID = "EXP-20260922-030"
PHASE9_DEMO_SESSION_ARM_PROTOCOL = "fmp-phase9-demo-session-arm-v1"
PHASE9_DEMO_SESSION_READY_PROTOCOL = "fmp-phase9-demo-session-ready-v1"
PHASE9_DEMO_SESSION_JOURNAL_PROTOCOL = "fmp-phase9-demo-session-journal-v1"
PHASE9_DEMO_SESSION_CONTRACT_READY = "PHASE9_DEMO_SESSION_CONTRACT_READY"

SESSION_EVENT_TYPES = frozenset(
    {
        "SESSION_OPENED",
        "RECONCILIATION_OK",
        "RECONCILIATION_FAILED",
        "PREFLIGHT_OK",
        "PREFLIGHT_FAILED",
        "SEND_ATTEMPTED",
        "SEND_RESULT",
        "POST_SEND_RECONCILIATION_OK",
        "POST_SEND_RECONCILIATION_FAILED",
        "SESSION_HALTED",
        "SESSION_CLOSED",
    }
)

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


def _text(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
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


def build_phase9_demo_session_arm(
    *,
    design: Mapping[str, object],
    request: Mapping[str, object],
    not_before_utc: datetime,
    expires_at_utc: datetime,
    operator_approval_reference: str,
) -> dict[str, object]:
    validate_phase9_demo_design(design)
    validate_phase9_demo_order_request(request, design=design)

    start = _utc(not_before_utc, field="Phase 9 session not-before")
    end = _utc(expires_at_utc, field="Phase 9 session expiry")
    if end <= start:
        raise ValueError("Phase 9 session expiry must be after not-before")
    if end.date() != start.date():
        raise ValueError("Phase 9 session arm must remain within one UTC date")

    approval = _text(
        operator_approval_reference,
        field="Phase 9 operator approval reference",
    )
    execution = design.get("execution_path")
    if not isinstance(execution, Mapping):
        raise ValueError("Phase 9 execution path is malformed")

    payload = {
        "protocol": PHASE9_DEMO_SESSION_ARM_PROTOCOL,
        "experiment_id": PHASE9_DEMO_SESSION_EXPERIMENT_ID,
        "decision": PHASE9_DEMO_SESSION_DECISION,
        "demo_design_fingerprint": design["demo_design_fingerprint"],
        "request_fingerprint": request["request_fingerprint"],
        "client_order_id": request["client_order_id"],
        "champion_set_fingerprint": design["champion_set_fingerprint"],
        "strategy_fingerprint": request["strategy_fingerprint"],
        "symbol": request["symbol"],
        "account_fingerprint": execution["account_fingerprint"],
        "server": execution["server"],
        "practice_only": True,
        "max_new_orders": 1,
        "not_before_utc": _utc_string(start),
        "expires_at_utc": _utc_string(end),
        "operator_approval_reference": approval,
        "demo_execution_source_armed": False,
        "demo_execution_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
    }
    result = payload | {"session_arm_fingerprint": _digest(payload)}
    validate_phase9_demo_session_arm(
        result,
        design=design,
        request=request,
    )
    return result


def validate_phase9_demo_session_arm(
    arm: Mapping[str, object],
    *,
    design: Mapping[str, object],
    request: Mapping[str, object],
) -> None:
    validate_phase9_demo_design(design)
    validate_phase9_demo_order_request(request, design=design)

    if arm.get("protocol") != PHASE9_DEMO_SESSION_ARM_PROTOCOL:
        raise ValueError("Phase 9 demo-session arm protocol mismatch")
    if arm.get("experiment_id") != PHASE9_DEMO_SESSION_EXPERIMENT_ID:
        raise ValueError("Phase 9 demo-session arm experiment mismatch")
    if arm.get("decision") != PHASE9_DEMO_SESSION_DECISION:
        raise ValueError("Phase 9 demo-session arm decision mismatch")

    identities = {
        "demo_design_fingerprint": design["demo_design_fingerprint"],
        "request_fingerprint": request["request_fingerprint"],
        "client_order_id": request["client_order_id"],
        "champion_set_fingerprint": design["champion_set_fingerprint"],
        "strategy_fingerprint": request["strategy_fingerprint"],
        "symbol": request["symbol"],
    }
    execution = design.get("execution_path")
    assert isinstance(execution, Mapping)
    identities["account_fingerprint"] = execution["account_fingerprint"]
    identities["server"] = execution["server"]
    for field, expected in identities.items():
        if arm.get(field) != expected:
            raise ValueError(f"Phase 9 demo-session arm {field} mismatch")

    for field in (
        "demo_design_fingerprint",
        "request_fingerprint",
        "champion_set_fingerprint",
        "strategy_fingerprint",
        "account_fingerprint",
        "session_arm_fingerprint",
    ):
        _sha256(arm.get(field), field=f"Phase 9 session arm {field}")

    if arm.get("practice_only") is not True:
        raise ValueError("Phase 9 session arm must be practice-only")
    if arm.get("max_new_orders") != 1:
        raise ValueError("Phase 9 first session arm permits exactly one order")
    _text(
        arm.get("operator_approval_reference"),
        field="Phase 9 operator approval reference",
    )
    start = _parse_utc(
        arm.get("not_before_utc"),
        field="Phase 9 session arm not-before",
    )
    end = _parse_utc(
        arm.get("expires_at_utc"),
        field="Phase 9 session arm expiry",
    )
    if end <= start or end.date() != start.date():
        raise ValueError("Phase 9 session arm UTC window is invalid")

    for field in (
        "demo_execution_source_armed",
        "demo_execution_authorized",
        "demo_order_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "phase10_authorized",
    ):
        if arm.get(field) is not False:
            raise ValueError(f"Phase 9 session arm requires {field}=false")

    fingerprint = arm["session_arm_fingerprint"]
    payload = dict(arm)
    payload.pop("session_arm_fingerprint", None)
    if fingerprint != _digest(payload):
        raise ValueError("Phase 9 demo-session arm fingerprint mismatch")


def build_phase9_demo_session_ready(
    *,
    design: Mapping[str, object],
    request: Mapping[str, object],
    arm: Mapping[str, object],
    local_requests: Sequence[Mapping[str, object]],
    broker_orders: Sequence[Mapping[str, object]],
    broker_positions: Sequence[Mapping[str, object]],
    now_utc: datetime,
    daily_halt_active: bool,
    new_order_attempt_count: int = 0,
) -> dict[str, object]:
    validate_phase9_demo_session_arm(
        arm,
        design=design,
        request=request,
    )
    now = _utc(now_utc, field="Phase 9 session readiness time")
    if not isinstance(daily_halt_active, bool):
        raise ValueError("Phase 9 daily halt state must be boolean")
    if daily_halt_active:
        raise ValueError("Phase 9 daily halt is active")
    if (
        isinstance(new_order_attempt_count, bool)
        or not isinstance(new_order_attempt_count, int)
        or new_order_attempt_count < 0
    ):
        raise ValueError("Phase 9 new-order attempt count is invalid")
    if new_order_attempt_count != 0:
        raise ValueError("Phase 9 one-order session arm is already spent")

    start = _parse_utc(
        arm["not_before_utc"],
        field="Phase 9 session arm not-before",
    )
    end = _parse_utc(
        arm["expires_at_utc"],
        field="Phase 9 session arm expiry",
    )
    if now < start or now > end:
        raise ValueError("Phase 9 session readiness time is outside arm window")

    reconciliation = build_phase9_demo_reconciliation(
        design=design,
        local_requests=local_requests,
        broker_orders=broker_orders,
        broker_positions=broker_positions,
    )
    validate_phase9_demo_reconciliation(reconciliation)
    if reconciliation["healthy"] is not True:
        raise ValueError("Phase 9 startup reconciliation is unhealthy")

    payload = {
        "protocol": PHASE9_DEMO_SESSION_READY_PROTOCOL,
        "experiment_id": PHASE9_DEMO_SESSION_EXPERIMENT_ID,
        "decision": PHASE9_DEMO_SESSION_DECISION,
        "outcome": PHASE9_DEMO_SESSION_CONTRACT_READY,
        "session_arm_fingerprint": arm["session_arm_fingerprint"],
        "demo_design_fingerprint": design["demo_design_fingerprint"],
        "request_fingerprint": request["request_fingerprint"],
        "client_order_id": request["client_order_id"],
        "reconciliation_fingerprint": reconciliation[
            "reconciliation_fingerprint"
        ],
        "readiness_time_utc": _utc_string(now),
        "daily_halt_active": False,
        "new_order_attempt_count": 0,
        "max_new_orders": 1,
        "demo_session_contract_ready": True,
        "demo_execution_source_armed": DEMO_EXECUTION_SOURCE_ARMED,
        "demo_execution_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
    }
    result = payload | {"session_ready_fingerprint": _digest(payload)}
    validate_phase9_demo_session_ready(result)
    return result


def validate_phase9_demo_session_ready(
    value: Mapping[str, object],
) -> None:
    if value.get("protocol") != PHASE9_DEMO_SESSION_READY_PROTOCOL:
        raise ValueError("Phase 9 session-ready protocol mismatch")
    if value.get("experiment_id") != PHASE9_DEMO_SESSION_EXPERIMENT_ID:
        raise ValueError("Phase 9 session-ready experiment mismatch")
    if value.get("decision") != PHASE9_DEMO_SESSION_DECISION:
        raise ValueError("Phase 9 session-ready decision mismatch")
    if value.get("outcome") != PHASE9_DEMO_SESSION_CONTRACT_READY:
        raise ValueError("Phase 9 session-ready outcome mismatch")

    for field in (
        "session_arm_fingerprint",
        "demo_design_fingerprint",
        "request_fingerprint",
        "reconciliation_fingerprint",
        "session_ready_fingerprint",
    ):
        _sha256(value.get(field), field=f"Phase 9 session-ready {field}")

    _parse_utc(
        value.get("readiness_time_utc"),
        field="Phase 9 session-ready timestamp",
    )
    if value.get("daily_halt_active") is not False:
        raise ValueError("Phase 9 session-ready requires daily halt inactive")
    if value.get("new_order_attempt_count") != 0:
        raise ValueError("Phase 9 session-ready requires zero attempts")
    if value.get("max_new_orders") != 1:
        raise ValueError("Phase 9 session-ready requires one-order cap")
    if value.get("demo_session_contract_ready") is not True:
        raise ValueError("Phase 9 demo-session contract is not ready")
    if value.get("demo_execution_source_armed") is not False:
        raise ValueError("Phase 9 demo execution source must remain unarmed")
    for field in (
        "demo_execution_authorized",
        "demo_order_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "phase10_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(f"Phase 9 session-ready requires {field}=false")

    fingerprint = value["session_ready_fingerprint"]
    payload = dict(value)
    payload.pop("session_ready_fingerprint", None)
    if fingerprint != _digest(payload):
        raise ValueError("Phase 9 session-ready fingerprint mismatch")


def build_phase9_demo_session_journal_event(
    *,
    arm: Mapping[str, object],
    request: Mapping[str, object],
    sequence: int,
    event_time_utc: datetime,
    event_type: str,
    payload: Mapping[str, object],
    prior_event_fingerprint: str | None,
) -> dict[str, object]:
    if (
        isinstance(sequence, bool)
        or not isinstance(sequence, int)
        or sequence <= 0
    ):
        raise ValueError("Phase 9 journal sequence must be positive")
    if event_type not in SESSION_EVENT_TYPES:
        raise ValueError("Phase 9 journal event type is invalid")
    when = _utc(event_time_utc, field="Phase 9 journal event time")
    if not isinstance(payload, Mapping):
        raise ValueError("Phase 9 journal event payload must be an object")
    if prior_event_fingerprint is not None:
        _sha256(
            prior_event_fingerprint,
            field="Phase 9 prior journal event fingerprint",
        )

    event_payload = {
        "protocol": PHASE9_DEMO_SESSION_JOURNAL_PROTOCOL,
        "experiment_id": PHASE9_DEMO_SESSION_EXPERIMENT_ID,
        "decision": PHASE9_DEMO_SESSION_DECISION,
        "session_arm_fingerprint": _sha256(
            arm.get("session_arm_fingerprint"),
            field="Phase 9 journal arm fingerprint",
        ),
        "request_fingerprint": _sha256(
            request.get("request_fingerprint"),
            field="Phase 9 journal request fingerprint",
        ),
        "client_order_id": _text(
            request.get("client_order_id"),
            field="Phase 9 journal client-order ID",
        ),
        "sequence": sequence,
        "event_time_utc": _utc_string(when),
        "event_type": event_type,
        "prior_event_fingerprint": prior_event_fingerprint,
        "payload": dict(payload),
    }
    return event_payload | {
        "event_fingerprint": _digest(event_payload)
    }


def validate_phase9_demo_session_journal(
    rows: Sequence[Mapping[str, object]],
) -> None:
    previous: str | None = None
    expected_sequence = 1
    common_arm: str | None = None
    common_request: str | None = None
    common_client: str | None = None

    for row in rows:
        if row.get("protocol") != PHASE9_DEMO_SESSION_JOURNAL_PROTOCOL:
            raise ValueError("Phase 9 journal protocol mismatch")
        if row.get("experiment_id") != PHASE9_DEMO_SESSION_EXPERIMENT_ID:
            raise ValueError("Phase 9 journal experiment mismatch")
        if row.get("decision") != PHASE9_DEMO_SESSION_DECISION:
            raise ValueError("Phase 9 journal decision mismatch")
        if row.get("sequence") != expected_sequence:
            raise ValueError("Phase 9 journal sequence is not contiguous")
        _parse_utc(
            row.get("event_time_utc"),
            field="Phase 9 journal event time",
        )
        if row.get("event_type") not in SESSION_EVENT_TYPES:
            raise ValueError("Phase 9 journal event type is invalid")
        if not isinstance(row.get("payload"), Mapping):
            raise ValueError("Phase 9 journal payload is malformed")

        arm_fp = _sha256(
            row.get("session_arm_fingerprint"),
            field="Phase 9 journal arm fingerprint",
        )
        request_fp = _sha256(
            row.get("request_fingerprint"),
            field="Phase 9 journal request fingerprint",
        )
        client = _text(
            row.get("client_order_id"),
            field="Phase 9 journal client-order ID",
        )
        if common_arm is None:
            common_arm = arm_fp
            common_request = request_fp
            common_client = client
        elif (
            arm_fp != common_arm
            or request_fp != common_request
            or client != common_client
        ):
            raise ValueError("Phase 9 journal identity changed")

        if row.get("prior_event_fingerprint") != previous:
            raise ValueError("Phase 9 journal hash chain is broken")
        fingerprint = _sha256(
            row.get("event_fingerprint"),
            field="Phase 9 journal event fingerprint",
        )
        event_payload = dict(row)
        event_payload.pop("event_fingerprint", None)
        if fingerprint != _digest(event_payload):
            raise ValueError("Phase 9 journal event fingerprint mismatch")
        previous = fingerprint
        expected_sequence += 1


def phase9_demo_session_attempt_count(
    rows: Sequence[Mapping[str, object]],
) -> int:
    validate_phase9_demo_session_journal(rows)
    return sum(1 for row in rows if row["event_type"] == "SEND_ATTEMPTED")


def build_phase9_send_attempt_payload(
    *,
    order_check_request_fingerprint: str,
    order_check_fingerprint: str,
    checked_mt5_request: Mapping[str, object],
) -> dict[str, object]:
    return {
        "order_check_request_fingerprint": _sha256(
            order_check_request_fingerprint,
            field="Phase 9 order-check request fingerprint",
        ),
        "order_check_fingerprint": _sha256(
            order_check_fingerprint,
            field="Phase 9 order-check fingerprint",
        ),
        "checked_mt5_request_sha256": _digest(dict(checked_mt5_request)),
    }


class Phase9DemoSessionJournal:
    __slots__ = (
        "path",
        "_handle",
        "_arm",
        "_request",
        "_sequence",
        "_previous",
        "_rows",
    )

    def __init__(
        self,
        *,
        path: Path,
        arm: Mapping[str, object],
        request: Mapping[str, object],
    ) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.path.open("xb")
        self._arm = arm
        self._request = request
        self._sequence = 0
        self._previous: str | None = None
        self._rows: list[dict[str, object]] = []

    @property
    def rows(self) -> tuple[dict[str, object], ...]:
        return tuple(dict(row) for row in self._rows)

    def append(
        self,
        *,
        event_time_utc: datetime,
        event_type: str,
        payload: Mapping[str, object],
    ) -> dict[str, object]:
        self._sequence += 1
        row = build_phase9_demo_session_journal_event(
            arm=self._arm,
            request=self._request,
            sequence=self._sequence,
            event_time_utc=event_time_utc,
            event_type=event_type,
            payload=payload,
            prior_event_fingerprint=self._previous,
        )
        encoded = _canonical_bytes(row) + b"\n"
        self._handle.write(encoded)
        self._handle.flush()
        os.fsync(self._handle.fileno())
        self._previous = str(row["event_fingerprint"])
        self._rows.append(row)
        return dict(row)

    def close(self) -> None:
        if not self._handle.closed:
            self._handle.close()

    def __enter__(self) -> "Phase9DemoSessionJournal":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


@dataclass(frozen=True, slots=True)
class BoundedDemoSessionController:
    design: Mapping[str, object]
    request: Mapping[str, object]
    arm: Mapping[str, object]
    adapter: GatedMT5DemoMutationAdapter

    def __post_init__(self) -> None:
        validate_phase9_demo_session_arm(
            self.arm,
            design=self.design,
            request=self.request,
        )

    def submit(self) -> dict[str, object]:
        return self.adapter.submit(self.request)


__all__ = [
    "BoundedDemoSessionController",
    "PHASE9_DEMO_SESSION_ARM_PROTOCOL",
    "PHASE9_DEMO_SESSION_CONTRACT_READY",
    "PHASE9_DEMO_SESSION_DECISION",
    "PHASE9_DEMO_SESSION_EXPERIMENT_ID",
    "PHASE9_DEMO_SESSION_JOURNAL_PROTOCOL",
    "PHASE9_DEMO_SESSION_READY_PROTOCOL",
    "Phase9DemoSessionJournal",
    "SESSION_EVENT_TYPES",
    "build_phase9_demo_session_arm",
    "build_phase9_demo_session_journal_event",
    "build_phase9_demo_session_ready",
    "build_phase9_send_attempt_payload",
    "phase9_demo_session_attempt_count",
    "validate_phase9_demo_session_arm",
    "validate_phase9_demo_session_journal",
    "validate_phase9_demo_session_ready",
]
