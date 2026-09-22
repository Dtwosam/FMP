from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Mapping, Sequence

from fmp.phase9.execution_gate import DEMO_EXECUTION_SOURCE_ARMED
from fmp.phase9.launch_preflight import (
    validate_phase9_demo_launch_preflight,
)


PHASE9_DEMO_EXECUTION_PERMIT_DECISION = "DEC-064"
PHASE9_DEMO_EXECUTION_PERMIT_EXPERIMENT_ID = "EXP-20260922-035"
PHASE9_DEMO_EXECUTION_PERMIT_PROTOCOL = (
    "fmp-phase9-demo-execution-permit-v1"
)
PHASE9_DEMO_EXECUTION_PERMIT_ARTIFACT_PROTOCOL = (
    "fmp-phase9-demo-execution-permit-artifacts-v1"
)
PHASE9_DEMO_EXECUTION_PERMIT_CONTRACT_READY = (
    "PHASE9_DEMO_EXECUTION_PERMIT_CONTRACT_READY"
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


def _validate_launch(
    *,
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
    execution_arm: Mapping[str, object],
    runtime_authority: Mapping[str, object],
    launch_preflight: Mapping[str, object],
    journal_rows: Sequence[Mapping[str, object]],
) -> None:
    validate_phase9_demo_launch_preflight(
        launch_preflight,
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
        runtime_authority=runtime_authority,
        journal_rows=journal_rows,
    )

    if DEMO_EXECUTION_SOURCE_ARMED is not False:
        raise ValueError(
            "DEC-064 permit construction requires demo execution source unarmed"
        )

    if launch_preflight.get("demo_launch_preflight_ready") is not True:
        raise ValueError("Phase 9 launch preflight is not ready")
    if launch_preflight.get("order_check_performed") is not True:
        raise ValueError("Phase 9 launch preflight lacks order_check")
    if launch_preflight.get("order_send_attempted") is not False:
        raise ValueError("Phase 9 launch preflight already attempted order_send")
    if launch_preflight.get("send_attempt_count") != 0:
        raise ValueError("Phase 9 launch preflight arm is already spent")
    if launch_preflight.get("daily_halt_active") is not False:
        raise ValueError("Phase 9 launch preflight daily halt is active")

    order_check = launch_preflight.get("order_check")
    reconciliation = launch_preflight.get("reconciliation")
    if not isinstance(order_check, Mapping):
        raise ValueError("Phase 9 launch order-check evidence is malformed")
    if not isinstance(reconciliation, Mapping):
        raise ValueError("Phase 9 launch reconciliation evidence is malformed")
    if order_check.get("check_passed") is not True:
        raise ValueError("Phase 9 launch order-check did not pass")
    if reconciliation.get("healthy") is not True:
        raise ValueError("Phase 9 launch reconciliation is unhealthy")


def build_phase9_demo_execution_permit(
    *,
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
    execution_arm: Mapping[str, object],
    runtime_authority: Mapping[str, object],
    launch_preflight: Mapping[str, object],
    journal_rows: Sequence[Mapping[str, object]],
    code_commit: str,
) -> dict[str, object]:
    _validate_launch(
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
        runtime_authority=runtime_authority,
        launch_preflight=launch_preflight,
        journal_rows=journal_rows,
    )
    commit = _commit(
        code_commit,
        field="Phase 9 execution-permit builder code commit",
    )

    execution = design.get("execution_path")
    if not isinstance(execution, Mapping):
        raise ValueError("Phase 9 execution path is malformed")
    order_check_request = launch_preflight.get("order_check_request")
    order_check = launch_preflight.get("order_check")
    reconciliation = launch_preflight.get("reconciliation")
    if not isinstance(order_check_request, Mapping):
        raise ValueError("Phase 9 launch order-check request is malformed")
    if not isinstance(order_check, Mapping):
        raise ValueError("Phase 9 launch order-check evidence is malformed")
    if not isinstance(reconciliation, Mapping):
        raise ValueError("Phase 9 launch reconciliation is malformed")
    checked_mt5_request = order_check_request.get("mt5_request")
    if not isinstance(checked_mt5_request, Mapping):
        raise ValueError("Phase 9 checked MT5 request is malformed")

    payload = {
        "protocol": PHASE9_DEMO_EXECUTION_PERMIT_PROTOCOL,
        "experiment_id": PHASE9_DEMO_EXECUTION_PERMIT_EXPERIMENT_ID,
        "decision": PHASE9_DEMO_EXECUTION_PERMIT_DECISION,
        "outcome": PHASE9_DEMO_EXECUTION_PERMIT_CONTRACT_READY,
        "execution_permit_builder_code_commit": commit,
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
        "runtime_authority_fingerprint": runtime_authority[
            "runtime_authority_fingerprint"
        ],
        "launch_preflight_fingerprint": launch_preflight[
            "launch_preflight_fingerprint"
        ],
        "champion_set_fingerprint": design["champion_set_fingerprint"],
        "strategy_fingerprint": request["strategy_fingerprint"],
        "symbol": request["symbol"],
        "account_fingerprint": execution["account_fingerprint"],
        "server": execution["server"],
        "practice_only": True,
        "max_new_orders": 1,
        "not_before_utc": execution_arm["not_before_utc"],
        "expires_at_utc": execution_arm["expires_at_utc"],
        "operator_approval_reference": execution_arm[
            "operator_approval_reference"
        ],
        "launch_preflight_time_utc": launch_preflight[
            "launch_preflight_time_utc"
        ],
        "order_check_request_fingerprint": order_check_request[
            "order_check_request_fingerprint"
        ],
        "order_check_fingerprint": order_check[
            "order_check_fingerprint"
        ],
        "reconciliation_fingerprint": reconciliation[
            "reconciliation_fingerprint"
        ],
        "checked_mt5_request_sha256": _digest(dict(checked_mt5_request)),
        "journal_event_count": launch_preflight["journal_event_count"],
        "journal_tip_fingerprint": launch_preflight[
            "journal_tip_fingerprint"
        ],
        "send_attempt_count": 0,
        "daily_halt_active": False,
        "demo_execution_permit_artifact_ready": True,
        "demo_execution_source_armed": False,
        "demo_execution_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
    }
    result = payload | {
        "execution_permit_fingerprint": _digest(payload)
    }
    validate_phase9_demo_execution_permit(
        result,
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
        runtime_authority=runtime_authority,
        launch_preflight=launch_preflight,
        journal_rows=journal_rows,
    )
    return result


def validate_phase9_demo_execution_permit(
    value: Mapping[str, object],
    *,
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
    execution_arm: Mapping[str, object],
    runtime_authority: Mapping[str, object],
    launch_preflight: Mapping[str, object],
    journal_rows: Sequence[Mapping[str, object]],
) -> None:
    _validate_launch(
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
        runtime_authority=runtime_authority,
        launch_preflight=launch_preflight,
        journal_rows=journal_rows,
    )
    if value.get("protocol") != PHASE9_DEMO_EXECUTION_PERMIT_PROTOCOL:
        raise ValueError("Phase 9 execution-permit protocol mismatch")
    if value.get("experiment_id") != PHASE9_DEMO_EXECUTION_PERMIT_EXPERIMENT_ID:
        raise ValueError("Phase 9 execution-permit experiment mismatch")
    if value.get("decision") != PHASE9_DEMO_EXECUTION_PERMIT_DECISION:
        raise ValueError("Phase 9 execution-permit decision mismatch")
    if value.get("outcome") != PHASE9_DEMO_EXECUTION_PERMIT_CONTRACT_READY:
        raise ValueError("Phase 9 execution-permit outcome mismatch")

    _commit(
        value.get("execution_permit_builder_code_commit"),
        field="Phase 9 execution-permit builder code commit",
    )
    execution = design.get("execution_path")
    assert isinstance(execution, Mapping)
    order_check_request = launch_preflight["order_check_request"]
    order_check = launch_preflight["order_check"]
    reconciliation = launch_preflight["reconciliation"]
    assert isinstance(order_check_request, Mapping)
    assert isinstance(order_check, Mapping)
    assert isinstance(reconciliation, Mapping)
    checked_mt5_request = order_check_request.get("mt5_request")
    assert isinstance(checked_mt5_request, Mapping)

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
        "runtime_authority_fingerprint": runtime_authority[
            "runtime_authority_fingerprint"
        ],
        "launch_preflight_fingerprint": launch_preflight[
            "launch_preflight_fingerprint"
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
        "launch_preflight_time_utc": launch_preflight[
            "launch_preflight_time_utc"
        ],
        "order_check_request_fingerprint": order_check_request[
            "order_check_request_fingerprint"
        ],
        "order_check_fingerprint": order_check[
            "order_check_fingerprint"
        ],
        "reconciliation_fingerprint": reconciliation[
            "reconciliation_fingerprint"
        ],
        "checked_mt5_request_sha256": _digest(dict(checked_mt5_request)),
        "journal_event_count": launch_preflight["journal_event_count"],
        "journal_tip_fingerprint": launch_preflight[
            "journal_tip_fingerprint"
        ],
    }
    for field, expected in identities.items():
        if value.get(field) != expected:
            raise ValueError(f"Phase 9 execution-permit {field} mismatch")

    for field in (
        "demo_design_fingerprint",
        "request_fingerprint",
        "session_arm_fingerprint",
        "session_ready_fingerprint",
        "execution_arm_fingerprint",
        "runtime_authority_fingerprint",
        "launch_preflight_fingerprint",
        "champion_set_fingerprint",
        "strategy_fingerprint",
        "account_fingerprint",
        "order_check_request_fingerprint",
        "order_check_fingerprint",
        "reconciliation_fingerprint",
        "checked_mt5_request_sha256",
        "execution_permit_fingerprint",
    ):
        _sha256(value.get(field), field=f"Phase 9 execution-permit {field}")

    _text(value.get("client_order_id"), field="Phase 9 client-order ID")
    _text(value.get("symbol"), field="Phase 9 symbol")
    _text(value.get("server"), field="Phase 9 server")
    _text(
        value.get("operator_approval_reference"),
        field="Phase 9 operator approval reference",
    )

    if value.get("practice_only") is not True:
        raise ValueError("Phase 9 execution permit must be practice-only")
    if value.get("max_new_orders") != 1:
        raise ValueError("Phase 9 execution permit permits exactly one order")
    if value.get("send_attempt_count") != 0:
        raise ValueError("Phase 9 execution permit requires zero attempts")
    if value.get("daily_halt_active") is not False:
        raise ValueError("Phase 9 execution permit requires daily halt inactive")
    if value.get("demo_execution_permit_artifact_ready") is not True:
        raise ValueError("Phase 9 execution-permit artifact is not ready")

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
                f"Phase 9 execution permit requires {field}=false"
            )

    fingerprint = value["execution_permit_fingerprint"]
    payload = dict(value)
    payload.pop("execution_permit_fingerprint", None)
    if fingerprint != _digest(payload):
        raise ValueError("Phase 9 execution-permit fingerprint mismatch")


def write_phase9_demo_execution_permit(
    value: Mapping[str, object],
    *,
    out_dir: Path,
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
    execution_arm: Mapping[str, object],
    runtime_authority: Mapping[str, object],
    launch_preflight: Mapping[str, object],
    journal_rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    validate_phase9_demo_execution_permit(
        value,
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
        execution_arm=execution_arm,
        runtime_authority=runtime_authority,
        launch_preflight=launch_preflight,
        journal_rows=journal_rows,
    )
    root = Path(out_dir)
    result_path = root / "execution-permit.json"
    manifest_path = root / "manifest.json"
    if result_path.exists() or manifest_path.exists():
        raise FileExistsError(
            "Phase 9 execution-permit artifacts already exist"
        )
    root.mkdir(parents=True, exist_ok=True)
    payload = _stable_json_bytes(dict(value))
    _atomic_write(result_path, payload)
    manifest = {
        "protocol": PHASE9_DEMO_EXECUTION_PERMIT_ARTIFACT_PROTOCOL,
        "experiment_id": PHASE9_DEMO_EXECUTION_PERMIT_EXPERIMENT_ID,
        "decision": PHASE9_DEMO_EXECUTION_PERMIT_DECISION,
        "outcome": PHASE9_DEMO_EXECUTION_PERMIT_CONTRACT_READY,
        "execution_permit_fingerprint": value[
            "execution_permit_fingerprint"
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
    "PHASE9_DEMO_EXECUTION_PERMIT_ARTIFACT_PROTOCOL",
    "PHASE9_DEMO_EXECUTION_PERMIT_CONTRACT_READY",
    "PHASE9_DEMO_EXECUTION_PERMIT_DECISION",
    "PHASE9_DEMO_EXECUTION_PERMIT_EXPERIMENT_ID",
    "PHASE9_DEMO_EXECUTION_PERMIT_PROTOCOL",
    "build_phase9_demo_execution_permit",
    "validate_phase9_demo_execution_permit",
    "write_phase9_demo_execution_permit",
]
