from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Mapping

from fmp.phase9.design import validate_phase9_demo_design
from fmp.phase9.mt5_mutation import DEMO_EXECUTION_SOURCE_ARMED
from fmp.phase9.protocol import validate_phase9_demo_order_request
from fmp.phase9.session import (
    validate_phase9_demo_session_arm,
    validate_phase9_demo_session_ready,
)


PHASE9_DEMO_EXECUTION_ARM_DECISION = "DEC-060"
PHASE9_DEMO_EXECUTION_ARM_EXPERIMENT_ID = "EXP-20260922-031"
PHASE9_DEMO_EXECUTION_ARM_PROTOCOL = "fmp-phase9-demo-execution-arm-v1"
PHASE9_DEMO_EXECUTION_ARM_ARTIFACT_PROTOCOL = (
    "fmp-phase9-demo-execution-arm-artifacts-v1"
)
PHASE9_DEMO_EXECUTION_ARM_CONTRACT_READY = (
    "PHASE9_DEMO_EXECUTION_ARM_CONTRACT_READY"
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


def _validate_input_binding(
    *,
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
) -> None:
    validate_phase9_demo_design(design)
    validate_phase9_demo_order_request(request, design=design)
    validate_phase9_demo_session_arm(
        session_arm,
        design=design,
        request=request,
    )
    validate_phase9_demo_session_ready(session_ready)

    if DEMO_EXECUTION_SOURCE_ARMED is not False:
        raise ValueError(
            "DEC-060 source verification requires demo execution unarmed"
        )

    identities = {
        "session_arm_fingerprint": session_arm["session_arm_fingerprint"],
        "demo_design_fingerprint": design["demo_design_fingerprint"],
        "request_fingerprint": request["request_fingerprint"],
        "client_order_id": request["client_order_id"],
    }
    for field, expected in identities.items():
        if session_ready.get(field) != expected:
            raise ValueError(
                f"Phase 9 session-ready {field} does not match arm inputs"
            )

    if session_ready.get("daily_halt_active") is not False:
        raise ValueError("Phase 9 session-ready daily halt must be inactive")
    if session_ready.get("new_order_attempt_count") != 0:
        raise ValueError("Phase 9 session-ready arm is already spent")
    if session_ready.get("max_new_orders") != 1:
        raise ValueError("Phase 9 session-ready must permit exactly one order")
    if session_ready.get("demo_session_contract_ready") is not True:
        raise ValueError("Phase 9 demo-session contract is not ready")
    if session_ready.get("demo_execution_source_armed") is not False:
        raise ValueError("Phase 9 demo execution source is already armed")


def build_phase9_demo_execution_arm(
    *,
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
    code_commit: str,
) -> dict[str, object]:
    _validate_input_binding(
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
    )
    commit = _commit(
        code_commit,
        field="Phase 9 execution-arm builder code commit",
    )
    execution = design.get("execution_path")
    if not isinstance(execution, Mapping):
        raise ValueError("Phase 9 execution path is malformed")

    payload = {
        "protocol": PHASE9_DEMO_EXECUTION_ARM_PROTOCOL,
        "experiment_id": PHASE9_DEMO_EXECUTION_ARM_EXPERIMENT_ID,
        "decision": PHASE9_DEMO_EXECUTION_ARM_DECISION,
        "outcome": PHASE9_DEMO_EXECUTION_ARM_CONTRACT_READY,
        "execution_arm_builder_code_commit": commit,
        "demo_design_fingerprint": design["demo_design_fingerprint"],
        "request_fingerprint": request["request_fingerprint"],
        "client_order_id": request["client_order_id"],
        "session_arm_fingerprint": session_arm["session_arm_fingerprint"],
        "session_ready_fingerprint": session_ready[
            "session_ready_fingerprint"
        ],
        "champion_set_fingerprint": design["champion_set_fingerprint"],
        "strategy_fingerprint": request["strategy_fingerprint"],
        "symbol": request["symbol"],
        "account_fingerprint": execution["account_fingerprint"],
        "server": execution["server"],
        "practice_only": True,
        "max_new_orders": 1,
        "not_before_utc": session_arm["not_before_utc"],
        "expires_at_utc": session_arm["expires_at_utc"],
        "operator_approval_reference": session_arm[
            "operator_approval_reference"
        ],
        "demo_execution_arm_artifact_ready": True,
        "demo_execution_source_armed": False,
        "demo_execution_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
    }
    result = payload | {"execution_arm_fingerprint": _digest(payload)}
    validate_phase9_demo_execution_arm(
        result,
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
    )
    return result


def validate_phase9_demo_execution_arm(
    value: Mapping[str, object],
    *,
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
) -> None:
    _validate_input_binding(
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
    )
    if value.get("protocol") != PHASE9_DEMO_EXECUTION_ARM_PROTOCOL:
        raise ValueError("Phase 9 execution-arm protocol mismatch")
    if value.get("experiment_id") != PHASE9_DEMO_EXECUTION_ARM_EXPERIMENT_ID:
        raise ValueError("Phase 9 execution-arm experiment mismatch")
    if value.get("decision") != PHASE9_DEMO_EXECUTION_ARM_DECISION:
        raise ValueError("Phase 9 execution-arm decision mismatch")
    if value.get("outcome") != PHASE9_DEMO_EXECUTION_ARM_CONTRACT_READY:
        raise ValueError("Phase 9 execution-arm outcome mismatch")

    _commit(
        value.get("execution_arm_builder_code_commit"),
        field="Phase 9 execution-arm builder code commit",
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
        "champion_set_fingerprint": design["champion_set_fingerprint"],
        "strategy_fingerprint": request["strategy_fingerprint"],
        "symbol": request["symbol"],
        "account_fingerprint": execution["account_fingerprint"],
        "server": execution["server"],
        "not_before_utc": session_arm["not_before_utc"],
        "expires_at_utc": session_arm["expires_at_utc"],
        "operator_approval_reference": session_arm[
            "operator_approval_reference"
        ],
    }
    for field, expected in identities.items():
        if value.get(field) != expected:
            raise ValueError(f"Phase 9 execution-arm {field} mismatch")

    for field in (
        "demo_design_fingerprint",
        "request_fingerprint",
        "session_arm_fingerprint",
        "session_ready_fingerprint",
        "champion_set_fingerprint",
        "strategy_fingerprint",
        "account_fingerprint",
        "execution_arm_fingerprint",
    ):
        _sha256(value.get(field), field=f"Phase 9 execution-arm {field}")

    _text(value.get("client_order_id"), field="Phase 9 client-order ID")
    _text(value.get("symbol"), field="Phase 9 symbol")
    _text(value.get("server"), field="Phase 9 server")
    _text(
        value.get("operator_approval_reference"),
        field="Phase 9 operator approval reference",
    )

    if value.get("practice_only") is not True:
        raise ValueError("Phase 9 execution arm must be practice-only")
    if value.get("max_new_orders") != 1:
        raise ValueError("Phase 9 execution arm permits exactly one new order")
    if value.get("demo_execution_arm_artifact_ready") is not True:
        raise ValueError("Phase 9 execution-arm artifact is not ready")

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
            raise ValueError(f"Phase 9 execution arm requires {field}=false")

    fingerprint = value["execution_arm_fingerprint"]
    payload = dict(value)
    payload.pop("execution_arm_fingerprint", None)
    if fingerprint != _digest(payload):
        raise ValueError("Phase 9 execution-arm fingerprint mismatch")


def write_phase9_demo_execution_arm(
    value: Mapping[str, object],
    *,
    out_dir: Path,
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
) -> dict[str, object]:
    validate_phase9_demo_execution_arm(
        value,
        design=design,
        request=request,
        session_arm=session_arm,
        session_ready=session_ready,
    )
    root = Path(out_dir)
    result_path = root / "execution-arm.json"
    manifest_path = root / "manifest.json"
    if result_path.exists() or manifest_path.exists():
        raise FileExistsError("Phase 9 execution-arm artifacts already exist")
    root.mkdir(parents=True, exist_ok=True)

    payload = _stable_json_bytes(dict(value))
    _atomic_write(result_path, payload)
    manifest = {
        "protocol": PHASE9_DEMO_EXECUTION_ARM_ARTIFACT_PROTOCOL,
        "experiment_id": PHASE9_DEMO_EXECUTION_ARM_EXPERIMENT_ID,
        "decision": PHASE9_DEMO_EXECUTION_ARM_DECISION,
        "outcome": PHASE9_DEMO_EXECUTION_ARM_CONTRACT_READY,
        "execution_arm_fingerprint": value["execution_arm_fingerprint"],
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
    "PHASE9_DEMO_EXECUTION_ARM_ARTIFACT_PROTOCOL",
    "PHASE9_DEMO_EXECUTION_ARM_CONTRACT_READY",
    "PHASE9_DEMO_EXECUTION_ARM_DECISION",
    "PHASE9_DEMO_EXECUTION_ARM_EXPERIMENT_ID",
    "PHASE9_DEMO_EXECUTION_ARM_PROTOCOL",
    "build_phase9_demo_execution_arm",
    "validate_phase9_demo_execution_arm",
    "write_phase9_demo_execution_arm",
]
