from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Mapping, Protocol, Sequence

from fmp.phase9.arming import validate_phase9_demo_execution_arm
from fmp.phase9.design import validate_phase9_demo_design
from fmp.phase9.execution_gate import DEMO_EXECUTION_SOURCE_ARMED
from fmp.phase9.mt5_preflight import (
    build_phase9_mt5_order_check,
    build_phase9_mt5_order_check_request,
    validate_phase9_mt5_order_check,
    validate_phase9_mt5_order_check_request,
)
from fmp.phase9.protocol import (
    build_phase9_demo_reconciliation,
    validate_phase9_demo_order_request,
    validate_phase9_demo_reconciliation,
)
from fmp.phase9.runtime_authority import (
    validate_phase9_demo_runtime_authority,
)
from fmp.phase9.session import (
    phase9_demo_session_attempt_count,
    validate_phase9_demo_session_arm,
    validate_phase9_demo_session_journal,
    validate_phase9_demo_session_ready,
)


PHASE9_DEMO_LAUNCH_PREFLIGHT_DECISION = "DEC-063"
PHASE9_DEMO_LAUNCH_PREFLIGHT_EXPERIMENT_ID = "EXP-20260922-034"
PHASE9_DEMO_LAUNCH_PREFLIGHT_PROTOCOL = (
    "fmp-phase9-demo-launch-preflight-v1"
)
PHASE9_DEMO_LAUNCH_PREFLIGHT_ARTIFACT_PROTOCOL = (
    "fmp-phase9-demo-launch-preflight-artifacts-v1"
)
PHASE9_DEMO_LAUNCH_PREFLIGHT_READY = (
    "PHASE9_DEMO_LAUNCH_PREFLIGHT_READY"
)

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


class Phase9DemoLaunchPreflightBackend(Protocol):
    def account_snapshot(self) -> Mapping[str, object]: ...

    def symbol_snapshot(self, symbol: str) -> Mapping[str, object]: ...

    def tick_snapshot(self, symbol: str) -> Mapping[str, object]: ...

    def order_check(
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


def _validate_authority_prefix(
    *,
    runtime_authority: Mapping[str, object],
    journal_rows: Sequence[Mapping[str, object]],
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
    execution_arm: Mapping[str, object],
) -> tuple[tuple[Mapping[str, object], ...], str | None]:
    raw_count = runtime_authority.get("journal_event_count")
    if (
        isinstance(raw_count, bool)
        or not isinstance(raw_count, int)
        or raw_count < 0
    ):
        raise ValueError("Phase 9 runtime-authority journal count is invalid")
    if raw_count > len(journal_rows):
        raise ValueError("Phase 9 current journal is shorter than authority prefix")

    authority_rows = tuple(journal_rows[:raw_count])
    validate_phase9_demo_runtime_authority(
        runtime_authority,
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
        journal_rows=authority_rows,
    )
    validate_phase9_demo_session_journal(journal_rows)

    if raw_count == 0:
        if runtime_authority.get("journal_tip_fingerprint") is not None:
            raise ValueError("Phase 9 zero-row authority journal tip must be null")
    else:
        prefix_tip = _sha256(
            authority_rows[-1].get("event_fingerprint"),
            field="Phase 9 authority journal-prefix tip",
        )
        if runtime_authority.get("journal_tip_fingerprint") != prefix_tip:
            raise ValueError("Phase 9 authority journal prefix changed")

    if phase9_demo_session_attempt_count(journal_rows) != 0:
        raise ValueError(
            "Phase 9 launch preflight requires zero SEND_ATTEMPTED events"
        )

    if not journal_rows:
        return authority_rows, None

    first = journal_rows[0]
    identities = {
        "session_arm_fingerprint": session_arm["session_arm_fingerprint"],
        "request_fingerprint": request["request_fingerprint"],
        "client_order_id": request["client_order_id"],
    }
    for field, expected in identities.items():
        if first.get(field) != expected:
            raise ValueError(
                f"Phase 9 launch journal {field} does not match authority"
            )
    current_tip = _sha256(
        journal_rows[-1].get("event_fingerprint"),
        field="Phase 9 current journal tip",
    )
    return authority_rows, current_tip


def run_phase9_demo_launch_preflight(
    *,
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
    execution_arm: Mapping[str, object],
    runtime_authority: Mapping[str, object],
    journal_rows: Sequence[Mapping[str, object]],
    backend: Phase9DemoLaunchPreflightBackend,
    now_utc: datetime,
    daily_halt_active: bool,
    code_commit: str,
) -> dict[str, object]:
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
            "DEC-063 launch preflight requires demo execution source unarmed"
        )
    if not isinstance(daily_halt_active, bool):
        raise ValueError("Phase 9 launch daily-halt state must be boolean")
    if daily_halt_active:
        raise ValueError("Phase 9 launch daily halt is active")

    now = _utc(now_utc, field="Phase 9 launch-preflight time")
    start = _parse_utc(
        execution_arm["not_before_utc"],
        field="Phase 9 launch arm not-before",
    )
    end = _parse_utc(
        execution_arm["expires_at_utc"],
        field="Phase 9 launch arm expiry",
    )
    authority_time = _parse_utc(
        runtime_authority.get("runtime_validation_time_utc"),
        field="Phase 9 runtime-authority validation time",
    )
    if now < start or now > end:
        raise ValueError("Phase 9 launch-preflight time is outside arm window")
    if now < authority_time:
        raise ValueError(
            "Phase 9 launch-preflight time precedes runtime authority"
        )

    _authority_rows, current_tip = _validate_authority_prefix(
        runtime_authority=runtime_authority,
        journal_rows=journal_rows,
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
    )

    commit = _commit(
        code_commit,
        field="Phase 9 launch-preflight code commit",
    )
    symbol = str(request["broker_symbol"])

    account_snapshot = dict(backend.account_snapshot())
    symbol_snapshot = dict(backend.symbol_snapshot(symbol))
    tick_snapshot = dict(backend.tick_snapshot(symbol))
    check_request = build_phase9_mt5_order_check_request(
        design=design,
        request=request,
        account_snapshot=account_snapshot,
        symbol_snapshot=symbol_snapshot,
        tick_snapshot=tick_snapshot,
    )
    validate_phase9_mt5_order_check_request(check_request)

    raw_check = dict(backend.order_check(check_request["mt5_request"]))
    check = build_phase9_mt5_order_check(
        order_check_request=check_request,
        raw_result=raw_check,
    )
    validate_phase9_mt5_order_check(check)
    if check.get("check_passed") is not True:
        raise ValueError(
            f"MT5 order_check failed with retcode {check.get('retcode')}"
        )

    broker_orders = [dict(row) for row in backend.broker_orders()]
    broker_positions = [dict(row) for row in backend.broker_positions()]
    reconciliation = build_phase9_demo_reconciliation(
        design=design,
        local_requests=[request],
        broker_orders=broker_orders,
        broker_positions=broker_positions,
    )
    validate_phase9_demo_reconciliation(reconciliation)
    if reconciliation.get("healthy") is not True:
        raise ValueError("Phase 9 launch reconciliation is unhealthy")

    payload = {
        "protocol": PHASE9_DEMO_LAUNCH_PREFLIGHT_PROTOCOL,
        "experiment_id": PHASE9_DEMO_LAUNCH_PREFLIGHT_EXPERIMENT_ID,
        "decision": PHASE9_DEMO_LAUNCH_PREFLIGHT_DECISION,
        "outcome": PHASE9_DEMO_LAUNCH_PREFLIGHT_READY,
        "launch_preflight_code_commit": commit,
        "launch_preflight_time_utc": _utc_string(now),
        "runtime_authority_fingerprint": runtime_authority[
            "runtime_authority_fingerprint"
        ],
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
        "journal_event_count": len(journal_rows),
        "journal_tip_fingerprint": current_tip,
        "send_attempt_count": 0,
        "daily_halt_active": False,
        "account": check_request["account"],
        "symbol_snapshot": check_request["symbol_snapshot"],
        "tick_snapshot": check_request["tick_snapshot"],
        "order_check_request": check_request,
        "order_check": check,
        "reconciliation": reconciliation,
        "broker_order_count": len(broker_orders),
        "broker_position_count": len(broker_positions),
        "broker_reads_performed": True,
        "order_check_performed": True,
        "order_send_attempted": False,
        "demo_launch_preflight_ready": True,
        "demo_execution_source_armed": False,
        "demo_execution_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
    }
    result = payload | {
        "launch_preflight_fingerprint": _digest(payload)
    }
    validate_phase9_demo_launch_preflight(
        result,
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
        runtime_authority=runtime_authority,
        journal_rows=journal_rows,
    )
    return result


def validate_phase9_demo_launch_preflight(
    value: Mapping[str, object],
    *,
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
    execution_arm: Mapping[str, object],
    runtime_authority: Mapping[str, object],
    journal_rows: Sequence[Mapping[str, object]],
) -> None:
    if value.get("protocol") != PHASE9_DEMO_LAUNCH_PREFLIGHT_PROTOCOL:
        raise ValueError("Phase 9 launch-preflight protocol mismatch")
    if value.get("experiment_id") != PHASE9_DEMO_LAUNCH_PREFLIGHT_EXPERIMENT_ID:
        raise ValueError("Phase 9 launch-preflight experiment mismatch")
    if value.get("decision") != PHASE9_DEMO_LAUNCH_PREFLIGHT_DECISION:
        raise ValueError("Phase 9 launch-preflight decision mismatch")
    if value.get("outcome") != PHASE9_DEMO_LAUNCH_PREFLIGHT_READY:
        raise ValueError("Phase 9 launch-preflight outcome mismatch")

    _commit(
        value.get("launch_preflight_code_commit"),
        field="Phase 9 launch-preflight code commit",
    )
    launch_time = _parse_utc(
        value.get("launch_preflight_time_utc"),
        field="Phase 9 launch-preflight time",
    )
    authority_time = _parse_utc(
        runtime_authority.get("runtime_validation_time_utc"),
        field="Phase 9 runtime-authority validation time",
    )
    start = _parse_utc(
        execution_arm["not_before_utc"],
        field="Phase 9 launch arm not-before",
    )
    end = _parse_utc(
        execution_arm["expires_at_utc"],
        field="Phase 9 launch arm expiry",
    )
    if launch_time < start or launch_time > end:
        raise ValueError("Phase 9 launch-preflight time is outside arm window")
    if launch_time < authority_time:
        raise ValueError(
            "Phase 9 launch-preflight time precedes runtime authority"
        )

    _prefix, current_tip = _validate_authority_prefix(
        runtime_authority=runtime_authority,
        journal_rows=journal_rows,
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
    )

    identities = {
        "runtime_authority_fingerprint": runtime_authority[
            "runtime_authority_fingerprint"
        ],
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
    }
    for field, expected in identities.items():
        if value.get(field) != expected:
            raise ValueError(f"Phase 9 launch-preflight {field} mismatch")

    for field in (
        "runtime_authority_fingerprint",
        "demo_design_fingerprint",
        "request_fingerprint",
        "session_arm_fingerprint",
        "session_ready_fingerprint",
        "execution_arm_fingerprint",
        "launch_preflight_fingerprint",
    ):
        _sha256(value.get(field), field=f"Phase 9 launch-preflight {field}")

    if value.get("journal_event_count") != len(journal_rows):
        raise ValueError("Phase 9 launch-preflight journal count mismatch")
    if value.get("journal_tip_fingerprint") != current_tip:
        raise ValueError("Phase 9 launch-preflight journal tip mismatch")
    if value.get("send_attempt_count") != 0:
        raise ValueError("Phase 9 launch-preflight requires zero send attempts")
    if value.get("daily_halt_active") is not False:
        raise ValueError("Phase 9 launch-preflight requires daily halt inactive")

    check_request = value.get("order_check_request")
    check = value.get("order_check")
    reconciliation = value.get("reconciliation")
    if not isinstance(check_request, Mapping):
        raise ValueError("Phase 9 launch order-check request is malformed")
    if not isinstance(check, Mapping):
        raise ValueError("Phase 9 launch order-check evidence is malformed")
    if not isinstance(reconciliation, Mapping):
        raise ValueError("Phase 9 launch reconciliation is malformed")
    validate_phase9_mt5_order_check_request(check_request)
    validate_phase9_mt5_order_check(check)
    validate_phase9_demo_reconciliation(reconciliation)
    if check.get("order_check_request_fingerprint") != check_request.get(
        "order_check_request_fingerprint"
    ):
        raise ValueError("Phase 9 launch order-check identity mismatch")
    if check.get("check_passed") is not True:
        raise ValueError("Phase 9 launch order-check did not pass")
    if reconciliation.get("healthy") is not True:
        raise ValueError("Phase 9 launch reconciliation is unhealthy")

    if value.get("broker_reads_performed") is not True:
        raise ValueError("Phase 9 launch preflight requires broker reads")
    if value.get("order_check_performed") is not True:
        raise ValueError("Phase 9 launch preflight requires order_check")
    if value.get("order_send_attempted") is not False:
        raise ValueError("Phase 9 launch preflight forbids order_send")
    if value.get("demo_launch_preflight_ready") is not True:
        raise ValueError("Phase 9 demo launch preflight is not ready")

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
                f"Phase 9 launch-preflight requires {field}=false"
            )

    fingerprint = value["launch_preflight_fingerprint"]
    payload = dict(value)
    payload.pop("launch_preflight_fingerprint", None)
    if fingerprint != _digest(payload):
        raise ValueError("Phase 9 launch-preflight fingerprint mismatch")


def write_phase9_demo_launch_preflight(
    value: Mapping[str, object],
    *,
    out_dir: Path,
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
    execution_arm: Mapping[str, object],
    runtime_authority: Mapping[str, object],
    journal_rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    validate_phase9_demo_launch_preflight(
        value,
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
        runtime_authority=runtime_authority,
        journal_rows=journal_rows,
    )
    root = Path(out_dir)
    result_path = root / "launch-preflight.json"
    manifest_path = root / "manifest.json"
    if result_path.exists() or manifest_path.exists():
        raise FileExistsError(
            "Phase 9 launch-preflight artifacts already exist"
        )
    root.mkdir(parents=True, exist_ok=True)
    payload = _stable_json_bytes(dict(value))
    _atomic_write(result_path, payload)
    manifest = {
        "protocol": PHASE9_DEMO_LAUNCH_PREFLIGHT_ARTIFACT_PROTOCOL,
        "experiment_id": PHASE9_DEMO_LAUNCH_PREFLIGHT_EXPERIMENT_ID,
        "decision": PHASE9_DEMO_LAUNCH_PREFLIGHT_DECISION,
        "outcome": PHASE9_DEMO_LAUNCH_PREFLIGHT_READY,
        "launch_preflight_fingerprint": value[
            "launch_preflight_fingerprint"
        ],
        "broker_reads_performed": True,
        "order_check_performed": True,
        "order_send_attempted": False,
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
    "PHASE9_DEMO_LAUNCH_PREFLIGHT_ARTIFACT_PROTOCOL",
    "PHASE9_DEMO_LAUNCH_PREFLIGHT_DECISION",
    "PHASE9_DEMO_LAUNCH_PREFLIGHT_EXPERIMENT_ID",
    "PHASE9_DEMO_LAUNCH_PREFLIGHT_PROTOCOL",
    "PHASE9_DEMO_LAUNCH_PREFLIGHT_READY",
    "Phase9DemoLaunchPreflightBackend",
    "run_phase9_demo_launch_preflight",
    "validate_phase9_demo_launch_preflight",
    "write_phase9_demo_launch_preflight",
]
