from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Mapping, Sequence

from fmp.phase9.arming import validate_phase9_demo_execution_arm
from fmp.phase9.design import validate_phase9_demo_design
from fmp.phase9.execution_gate import DEMO_EXECUTION_SOURCE_ARMED
from fmp.phase9.protocol import validate_phase9_demo_order_request
from fmp.phase9.session import (
    phase9_demo_session_attempt_count,
    validate_phase9_demo_session_arm,
    validate_phase9_demo_session_journal,
    validate_phase9_demo_session_ready,
)


PHASE9_DEMO_RUNTIME_AUTHORITY_DECISION = "DEC-062"
PHASE9_DEMO_RUNTIME_AUTHORITY_EXPERIMENT_ID = "EXP-20260922-033"
PHASE9_DEMO_RUNTIME_AUTHORITY_PROTOCOL = (
    "fmp-phase9-demo-runtime-authority-v1"
)
PHASE9_DEMO_RUNTIME_AUTHORITY_ARTIFACT_PROTOCOL = (
    "fmp-phase9-demo-runtime-authority-artifacts-v1"
)
PHASE9_DEMO_RUNTIME_AUTHORITY_READY = (
    "PHASE9_DEMO_RUNTIME_AUTHORITY_READY"
)

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


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


def _stable_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def _sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase SHA-256")
    return value


def _commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _COMMIT_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase 40-character commit SHA")
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


def _validate_upstream(
    *,
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
    execution_arm: Mapping[str, object],
) -> None:
    validate_phase9_demo_design(design)
    validate_phase9_demo_order_request(request, design=design)
    validate_phase9_demo_session_arm(
        session_arm,
        design=design,
        request=request,
    )
    validate_phase9_demo_session_ready(session_ready)
    validate_phase9_demo_execution_arm(
        execution_arm,
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
    )

    if DEMO_EXECUTION_SOURCE_ARMED is not False:
        raise ValueError(
            "DEC-062 runtime authority requires demo execution source unarmed"
        )

    identities = {
        "demo_design_fingerprint": design["demo_design_fingerprint"],
        "request_fingerprint": request["request_fingerprint"],
        "client_order_id": request["client_order_id"],
        "session_arm_fingerprint": session_arm["session_arm_fingerprint"],
        "session_ready_fingerprint": session_ready[
            "session_ready_fingerprint"
        ],
    }
    for field, expected in identities.items():
        if execution_arm.get(field) != expected:
            raise ValueError(
                f"Phase 9 execution arm {field} does not match runtime inputs"
            )

    if execution_arm.get("practice_only") is not True:
        raise ValueError("Phase 9 runtime authority requires practice-only arm")
    if execution_arm.get("max_new_orders") != 1:
        raise ValueError("Phase 9 runtime authority requires one-order arm")
    if session_ready.get("daily_halt_active") is not False:
        raise ValueError("Phase 9 runtime authority requires daily halt inactive")
    if session_ready.get("new_order_attempt_count") != 0:
        raise ValueError("Phase 9 runtime authority session is already spent")
    if session_ready.get("max_new_orders") != 1:
        raise ValueError("Phase 9 runtime authority requires one-order readiness")


def _validate_journal_binding(
    *,
    rows: Sequence[Mapping[str, object]],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
) -> tuple[int, str | None]:
    validate_phase9_demo_session_journal(rows)
    attempts = phase9_demo_session_attempt_count(rows)
    if attempts != 0:
        raise ValueError(
            "Phase 9 runtime authority requires zero prior SEND_ATTEMPTED events"
        )
    if not rows:
        return 0, None

    first = rows[0]
    identities = {
        "session_arm_fingerprint": session_arm["session_arm_fingerprint"],
        "request_fingerprint": request["request_fingerprint"],
        "client_order_id": request["client_order_id"],
    }
    for field, expected in identities.items():
        if first.get(field) != expected:
            raise ValueError(
                f"Phase 9 runtime journal {field} does not match arm inputs"
            )
    tip = _sha256(
        rows[-1].get("event_fingerprint"),
        field="Phase 9 runtime journal tip fingerprint",
    )
    return len(rows), tip


def build_phase9_demo_runtime_authority(
    *,
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
    execution_arm: Mapping[str, object],
    journal_rows: Sequence[Mapping[str, object]],
    now_utc: datetime,
    daily_halt_active: bool,
    code_commit: str,
) -> dict[str, object]:
    _validate_upstream(
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
    )
    if not isinstance(daily_halt_active, bool):
        raise ValueError("Phase 9 runtime daily-halt state must be boolean")
    if daily_halt_active:
        raise ValueError("Phase 9 runtime daily halt is active")

    now = _utc(now_utc, field="Phase 9 runtime validation time")
    start = _parse_utc(
        execution_arm["not_before_utc"],
        field="Phase 9 runtime arm not-before",
    )
    end = _parse_utc(
        execution_arm["expires_at_utc"],
        field="Phase 9 runtime arm expiry",
    )
    readiness = _parse_utc(
        session_ready["readiness_time_utc"],
        field="Phase 9 session readiness time",
    )
    if now < start or now > end:
        raise ValueError("Phase 9 runtime validation time is outside arm window")
    if now < readiness:
        raise ValueError(
            "Phase 9 runtime validation time precedes session readiness"
        )

    event_count, journal_tip = _validate_journal_binding(
        rows=journal_rows,
        request=request,
        session_arm=session_arm,
    )
    commit = _commit(
        code_commit,
        field="Phase 9 runtime-authority code commit",
    )
    execution = design.get("execution_path")
    if not isinstance(execution, Mapping):
        raise ValueError("Phase 9 execution path is malformed")

    payload = {
        "protocol": PHASE9_DEMO_RUNTIME_AUTHORITY_PROTOCOL,
        "experiment_id": PHASE9_DEMO_RUNTIME_AUTHORITY_EXPERIMENT_ID,
        "decision": PHASE9_DEMO_RUNTIME_AUTHORITY_DECISION,
        "outcome": PHASE9_DEMO_RUNTIME_AUTHORITY_READY,
        "runtime_authority_code_commit": commit,
        "runtime_validation_time_utc": _utc_string(now),
        "demo_design_fingerprint": design["demo_design_fingerprint"],
        "request_fingerprint": request["request_fingerprint"],
        "client_order_id": request["client_order_id"],
        "session_arm_fingerprint": session_arm["session_arm_fingerprint"],
        "session_ready_fingerprint": session_ready[
            "session_ready_fingerprint"
        ],
        "execution_arm_fingerprint": execution_arm[
            "execution_arm_fingerprint"
        ],
        "champion_set_fingerprint": design["champion_set_fingerprint"],
        "strategy_fingerprint": request["strategy_fingerprint"],
        "symbol": request["symbol"],
        "account_fingerprint": execution["account_fingerprint"],
        "server": execution["server"],
        "not_before_utc": execution_arm["not_before_utc"],
        "expires_at_utc": execution_arm["expires_at_utc"],
        "operator_approval_reference": execution_arm[
            "operator_approval_reference"
        ],
        "practice_only": True,
        "max_new_orders": 1,
        "journal_event_count": event_count,
        "journal_tip_fingerprint": journal_tip,
        "send_attempt_count": 0,
        "daily_halt_active": False,
        "demo_runtime_arm_authority_ready": True,
        "demo_execution_source_armed": False,
        "demo_execution_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
    }
    result = payload | {
        "runtime_authority_fingerprint": _digest(payload)
    }
    validate_phase9_demo_runtime_authority(
        result,
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
        journal_rows=journal_rows,
    )
    return result


def validate_phase9_demo_runtime_authority(
    value: Mapping[str, object],
    *,
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
    execution_arm: Mapping[str, object],
    journal_rows: Sequence[Mapping[str, object]],
) -> None:
    _validate_upstream(
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
    )
    if value.get("protocol") != PHASE9_DEMO_RUNTIME_AUTHORITY_PROTOCOL:
        raise ValueError("Phase 9 runtime-authority protocol mismatch")
    if value.get("experiment_id") != PHASE9_DEMO_RUNTIME_AUTHORITY_EXPERIMENT_ID:
        raise ValueError("Phase 9 runtime-authority experiment mismatch")
    if value.get("decision") != PHASE9_DEMO_RUNTIME_AUTHORITY_DECISION:
        raise ValueError("Phase 9 runtime-authority decision mismatch")
    if value.get("outcome") != PHASE9_DEMO_RUNTIME_AUTHORITY_READY:
        raise ValueError("Phase 9 runtime-authority outcome mismatch")

    _commit(
        value.get("runtime_authority_code_commit"),
        field="Phase 9 runtime-authority code commit",
    )
    validation_time = _parse_utc(
        value.get("runtime_validation_time_utc"),
        field="Phase 9 runtime validation time",
    )
    start = _parse_utc(
        execution_arm["not_before_utc"],
        field="Phase 9 runtime arm not-before",
    )
    end = _parse_utc(
        execution_arm["expires_at_utc"],
        field="Phase 9 runtime arm expiry",
    )
    readiness = _parse_utc(
        session_ready["readiness_time_utc"],
        field="Phase 9 session readiness time",
    )
    if validation_time < start or validation_time > end:
        raise ValueError("Phase 9 runtime validation time is outside arm window")
    if validation_time < readiness:
        raise ValueError(
            "Phase 9 runtime validation time precedes session readiness"
        )

    execution = design.get("execution_path")
    assert isinstance(execution, Mapping)
    identities = {
        "demo_design_fingerprint": design["demo_design_fingerprint"],
        "request_fingerprint": request["request_fingerprint"],
        "client_order_id": request["client_order_id"],
        "session_arm_fingerprint": session_arm["session_arm_fingerprint"],
        "session_ready_fingerprint": session_ready[
            "session_ready_fingerprint"
        ],
        "execution_arm_fingerprint": execution_arm[
            "execution_arm_fingerprint"
        ],
        "champion_set_fingerprint": design["champion_set_fingerprint"],
        "strategy_fingerprint": request["strategy_fingerprint"],
        "symbol": request["symbol"],
        "account_fingerprint": execution["account_fingerprint"],
        "server": execution["server"],
        "not_before_utc": execution_arm["not_before_utc"],
        "expires_at_utc": execution_arm["expires_at_utc"],
        "operator_approval_reference": execution_arm[
            "operator_approval_reference"
        ],
    }
    for field, expected in identities.items():
        if value.get(field) != expected:
            raise ValueError(f"Phase 9 runtime-authority {field} mismatch")

    for field in (
        "demo_design_fingerprint",
        "request_fingerprint",
        "session_arm_fingerprint",
        "session_ready_fingerprint",
        "execution_arm_fingerprint",
        "champion_set_fingerprint",
        "strategy_fingerprint",
        "account_fingerprint",
        "runtime_authority_fingerprint",
    ):
        _sha256(value.get(field), field=f"Phase 9 runtime-authority {field}")

    _text(value.get("client_order_id"), field="Phase 9 client-order ID")
    _text(value.get("symbol"), field="Phase 9 symbol")
    _text(value.get("server"), field="Phase 9 server")
    _text(
        value.get("operator_approval_reference"),
        field="Phase 9 operator approval reference",
    )

    event_count, journal_tip = _validate_journal_binding(
        rows=journal_rows,
        request=request,
        session_arm=session_arm,
    )
    if value.get("journal_event_count") != event_count:
        raise ValueError("Phase 9 runtime-authority journal count mismatch")
    if value.get("journal_tip_fingerprint") != journal_tip:
        raise ValueError("Phase 9 runtime-authority journal tip mismatch")
    if value.get("send_attempt_count") != 0:
        raise ValueError("Phase 9 runtime-authority requires zero attempts")
    if value.get("daily_halt_active") is not False:
        raise ValueError("Phase 9 runtime-authority requires daily halt inactive")
    if value.get("practice_only") is not True:
        raise ValueError("Phase 9 runtime-authority must be practice-only")
    if value.get("max_new_orders") != 1:
        raise ValueError("Phase 9 runtime-authority permits exactly one order")
    if value.get("demo_runtime_arm_authority_ready") is not True:
        raise ValueError("Phase 9 runtime-arm authority is not ready")

    for field in (
        "demo_execution_source_armed",
        "demo_execution_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "phase10_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(
                f"Phase 9 runtime-authority requires {field}=false"
            )

    fingerprint = value["runtime_authority_fingerprint"]
    payload = dict(value)
    payload.pop("runtime_authority_fingerprint", None)
    if fingerprint != _digest(payload):
        raise ValueError("Phase 9 runtime-authority fingerprint mismatch")


def write_phase9_demo_runtime_authority(
    value: Mapping[str, object],
    *,
    out_dir: Path,
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
    execution_arm: Mapping[str, object],
    journal_rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    validate_phase9_demo_runtime_authority(
        value,
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
        journal_rows=journal_rows,
    )
    root = Path(out_dir)
    result_path = root / "runtime-authority.json"
    manifest_path = root / "manifest.json"
    if result_path.exists() or manifest_path.exists():
        raise FileExistsError(
            "Phase 9 runtime-authority artifacts already exist"
        )
    root.mkdir(parents=True, exist_ok=True)
    payload = _stable_json_bytes(dict(value))
    _atomic_write(result_path, payload)
    manifest = {
        "protocol": PHASE9_DEMO_RUNTIME_AUTHORITY_ARTIFACT_PROTOCOL,
        "experiment_id": PHASE9_DEMO_RUNTIME_AUTHORITY_EXPERIMENT_ID,
        "decision": PHASE9_DEMO_RUNTIME_AUTHORITY_DECISION,
        "outcome": PHASE9_DEMO_RUNTIME_AUTHORITY_READY,
        "runtime_authority_fingerprint": value[
            "runtime_authority_fingerprint"
        ],
        "demo_execution_source_armed": False,
        "demo_execution_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
        "artifacts": [
            {
                "path": result_path.name,
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        ],
    }
    _atomic_write(manifest_path, _stable_json_bytes(manifest))
    return manifest


__all__ = [
    "PHASE9_DEMO_RUNTIME_AUTHORITY_ARTIFACT_PROTOCOL",
    "PHASE9_DEMO_RUNTIME_AUTHORITY_DECISION",
    "PHASE9_DEMO_RUNTIME_AUTHORITY_EXPERIMENT_ID",
    "PHASE9_DEMO_RUNTIME_AUTHORITY_PROTOCOL",
    "PHASE9_DEMO_RUNTIME_AUTHORITY_READY",
    "build_phase9_demo_runtime_authority",
    "validate_phase9_demo_runtime_authority",
    "write_phase9_demo_runtime_authority",
]
