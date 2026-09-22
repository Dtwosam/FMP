from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Mapping, Sequence

from fmp.phase9.authorization_packet import (
    validate_phase9_first_demo_authorization_packet,
)
from fmp.phase9.execution_gate import DEMO_EXECUTION_SOURCE_ARMED


PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_DECISION = "DEC-068"
PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_EXPERIMENT_ID = "EXP-20260922-039"
PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_PROTOCOL = (
    "fmp-phase9-first-demo-explicit-approval-v1"
)
PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_ARTIFACT_PROTOCOL = (
    "fmp-phase9-first-demo-explicit-approval-artifacts-v1"
)
PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_RECORDED = (
    "PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_RECORDED"
)
PHASE9_DEMO_GATE_ACTIVATION_CONTRACT_PROTOCOL = (
    "fmp-phase9-demo-gate-activation-contract-v1"
)
PHASE9_DEMO_GATE_ACTIVATION_ARTIFACT_PROTOCOL = (
    "fmp-phase9-demo-gate-activation-contract-artifacts-v1"
)
PHASE9_DEMO_GATE_ACTIVATION_CONTRACT_READY = (
    "PHASE9_DEMO_GATE_ACTIVATION_CONTRACT_READY"
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


def approval_statement_for_challenge(challenge_fingerprint: str) -> str:
    challenge = _sha256(
        challenge_fingerprint,
        field="Phase 9 authorization challenge fingerprint",
    )
    return f"APPROVE FIRST DEMO ORDER {challenge}"


def _validate_packet(
    *,
    packet: Mapping[str, object],
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
    execution_arm: Mapping[str, object],
    runtime_authority: Mapping[str, object],
    launch_preflight: Mapping[str, object],
    execution_permit: Mapping[str, object],
    journal_rows: Sequence[Mapping[str, object]],
) -> Mapping[str, object]:
    validate_phase9_first_demo_authorization_packet(
        packet,
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
    if DEMO_EXECUTION_SOURCE_ARMED is not False:
        raise ValueError(
            "DEC-068 source contract requires demo execution source unarmed"
        )
    review = packet.get("review")
    if not isinstance(review, Mapping):
        raise ValueError("Phase 9 authorization packet review is malformed")
    if review.get("account_mode") != "DEMO":
        raise ValueError("Phase 9 approval requires DEMO account")
    if packet.get("first_demo_authorization_packet_ready") is not True:
        raise ValueError("Phase 9 authorization packet is not ready")
    if packet.get("explicit_execution_approval_recorded") is not False:
        raise ValueError("Phase 9 authorization packet already records approval")
    return review


def _approval_window(
    review: Mapping[str, object],
) -> tuple[datetime, datetime, datetime]:
    start = _parse_utc(
        review.get("not_before_utc"),
        field="Phase 9 approval not-before",
    )
    launch = _parse_utc(
        review.get("launch_preflight_time_utc"),
        field="Phase 9 approval launch-preflight time",
    )
    expiry = _parse_utc(
        review.get("expires_at_utc"),
        field="Phase 9 approval expiry",
    )
    if expiry < start:
        raise ValueError("Phase 9 approval arm window is reversed")
    if launch < start or launch > expiry:
        raise ValueError("Phase 9 launch preflight is outside arm window")
    return start, launch, expiry


def build_phase9_first_demo_explicit_approval(
    *,
    packet: Mapping[str, object],
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
    execution_arm: Mapping[str, object],
    runtime_authority: Mapping[str, object],
    launch_preflight: Mapping[str, object],
    execution_permit: Mapping[str, object],
    journal_rows: Sequence[Mapping[str, object]],
    operator_identity_reference: str,
    operator_approval_reference: str,
    approval_statement: str,
    approval_time_utc: datetime,
    code_commit: str,
) -> dict[str, object]:
    review = _validate_packet(
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
    challenge = _sha256(
        packet.get("authorization_challenge_fingerprint"),
        field="Phase 9 authorization challenge fingerprint",
    )
    expected_statement = approval_statement_for_challenge(challenge)
    if approval_statement != expected_statement:
        raise ValueError("Phase 9 explicit approval statement mismatch")

    approval_time = _utc(
        approval_time_utc,
        field="Phase 9 explicit approval time",
    )
    start, launch, expiry = _approval_window(review)
    if approval_time < start or approval_time < launch or approval_time > expiry:
        raise ValueError("Phase 9 explicit approval time is outside approval window")

    commit = _commit(
        code_commit,
        field="Phase 9 explicit approval builder code commit",
    )
    operator_identity = _text(
        operator_identity_reference,
        field="Phase 9 operator identity reference",
    )
    operator_reference = _text(
        operator_approval_reference,
        field="Phase 9 operator approval reference",
    )
    payload = {
        "protocol": PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_PROTOCOL,
        "experiment_id": PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_EXPERIMENT_ID,
        "decision": PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_DECISION,
        "outcome": PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_RECORDED,
        "explicit_approval_builder_code_commit": commit,
        "authorization_packet_fingerprint": packet[
            "authorization_packet_fingerprint"
        ],
        "authorization_challenge_fingerprint": challenge,
        "execution_permit_fingerprint": review[
            "execution_permit_fingerprint"
        ],
        "request_fingerprint": review["request_fingerprint"],
        "client_order_id": review["client_order_id"],
        "account_fingerprint": review["account_fingerprint"],
        "server": review["server"],
        "not_before_utc": review["not_before_utc"],
        "launch_preflight_time_utc": review["launch_preflight_time_utc"],
        "expires_at_utc": review["expires_at_utc"],
        "operator_identity_reference": operator_identity,
        "operator_approval_reference": operator_reference,
        "approval_time_utc": _utc_string(approval_time),
        "approval_statement": expected_statement,
        "practice_only": True,
        "max_new_orders": 1,
        "explicit_execution_approval_recorded": True,
        "source_only_approval_record": True,
        "demo_execution_source_armed": False,
        "runner_activation_wired": False,
        "demo_execution_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
        "phase11_authorized": False,
    }
    result = payload | {"explicit_approval_fingerprint": _digest(payload)}
    validate_phase9_first_demo_explicit_approval(
        result,
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
    return result


def validate_phase9_first_demo_explicit_approval(
    value: Mapping[str, object],
    *,
    packet: Mapping[str, object],
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
    execution_arm: Mapping[str, object],
    runtime_authority: Mapping[str, object],
    launch_preflight: Mapping[str, object],
    execution_permit: Mapping[str, object],
    journal_rows: Sequence[Mapping[str, object]],
) -> None:
    review = _validate_packet(
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
    if value.get("protocol") != PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_PROTOCOL:
        raise ValueError("Phase 9 explicit approval protocol mismatch")
    if value.get("experiment_id") != PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_EXPERIMENT_ID:
        raise ValueError("Phase 9 explicit approval experiment mismatch")
    if value.get("decision") != PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_DECISION:
        raise ValueError("Phase 9 explicit approval decision mismatch")
    if value.get("outcome") != PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_RECORDED:
        raise ValueError("Phase 9 explicit approval outcome mismatch")
    _commit(
        value.get("explicit_approval_builder_code_commit"),
        field="Phase 9 explicit approval builder code commit",
    )

    challenge = _sha256(
        packet.get("authorization_challenge_fingerprint"),
        field="Phase 9 authorization challenge fingerprint",
    )
    identities = {
        "authorization_packet_fingerprint": packet[
            "authorization_packet_fingerprint"
        ],
        "authorization_challenge_fingerprint": challenge,
        "execution_permit_fingerprint": review[
            "execution_permit_fingerprint"
        ],
        "request_fingerprint": review["request_fingerprint"],
        "client_order_id": review["client_order_id"],
        "account_fingerprint": review["account_fingerprint"],
        "server": review["server"],
        "not_before_utc": review["not_before_utc"],
        "launch_preflight_time_utc": review["launch_preflight_time_utc"],
        "expires_at_utc": review["expires_at_utc"],
    }
    for field, expected in identities.items():
        if value.get(field) != expected:
            raise ValueError(f"Phase 9 explicit approval {field} mismatch")
    for field in (
        "authorization_packet_fingerprint",
        "authorization_challenge_fingerprint",
        "execution_permit_fingerprint",
        "request_fingerprint",
        "account_fingerprint",
        "explicit_approval_fingerprint",
    ):
        _sha256(value.get(field), field=f"Phase 9 explicit approval {field}")
    _text(value.get("client_order_id"), field="Phase 9 client-order ID")
    _text(value.get("server"), field="Phase 9 demo server")
    _text(
        value.get("operator_identity_reference"),
        field="Phase 9 operator identity reference",
    )
    _text(
        value.get("operator_approval_reference"),
        field="Phase 9 operator approval reference",
    )

    expected_statement = approval_statement_for_challenge(challenge)
    if value.get("approval_statement") != expected_statement:
        raise ValueError("Phase 9 explicit approval statement mismatch")
    approval_time = _parse_utc(
        value.get("approval_time_utc"),
        field="Phase 9 explicit approval time",
    )
    start, launch, expiry = _approval_window(review)
    if approval_time < start or approval_time < launch or approval_time > expiry:
        raise ValueError("Phase 9 explicit approval time is outside approval window")

    if value.get("practice_only") is not True:
        raise ValueError("Phase 9 explicit approval must be practice-only")
    if value.get("max_new_orders") != 1:
        raise ValueError("Phase 9 explicit approval must be one-order-only")
    if value.get("explicit_execution_approval_recorded") is not True:
        raise ValueError("Phase 9 explicit approval record flag mismatch")
    if value.get("source_only_approval_record") is not True:
        raise ValueError("Phase 9 approval record must remain source-only")

    for field in (
        "demo_execution_source_armed",
        "runner_activation_wired",
        "demo_execution_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "phase10_authorized",
        "phase11_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(f"Phase 9 explicit approval requires {field}=false")

    fingerprint = value["explicit_approval_fingerprint"]
    payload = dict(value)
    payload.pop("explicit_approval_fingerprint", None)
    if fingerprint != _digest(payload):
        raise ValueError("Phase 9 explicit approval fingerprint mismatch")


def build_phase9_demo_gate_activation_contract(
    *,
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
    journal_rows: Sequence[Mapping[str, object]],
    activation_time_utc: datetime,
    code_commit: str,
) -> dict[str, object]:
    validate_phase9_first_demo_explicit_approval(
        approval,
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
    if DEMO_EXECUTION_SOURCE_ARMED is not False:
        raise ValueError(
            "DEC-068 activation contract requires source gate unarmed"
        )
    review = packet["review"]
    assert isinstance(review, Mapping)
    activation_time = _utc(
        activation_time_utc,
        field="Phase 9 gate activation time",
    )
    approval_time = _parse_utc(
        approval.get("approval_time_utc"),
        field="Phase 9 explicit approval time",
    )
    start, _, expiry = _approval_window(review)
    if activation_time < approval_time:
        raise ValueError("Phase 9 activation time precedes approval")
    if activation_time < start or activation_time > expiry:
        raise ValueError("Phase 9 activation time is outside arm window")

    commit = _commit(
        code_commit,
        field="Phase 9 gate activation builder code commit",
    )
    payload = {
        "protocol": PHASE9_DEMO_GATE_ACTIVATION_CONTRACT_PROTOCOL,
        "experiment_id": PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_EXPERIMENT_ID,
        "decision": PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_DECISION,
        "outcome": PHASE9_DEMO_GATE_ACTIVATION_CONTRACT_READY,
        "gate_activation_builder_code_commit": commit,
        "authorization_packet_fingerprint": packet[
            "authorization_packet_fingerprint"
        ],
        "authorization_challenge_fingerprint": packet[
            "authorization_challenge_fingerprint"
        ],
        "explicit_approval_fingerprint": approval[
            "explicit_approval_fingerprint"
        ],
        "execution_permit_fingerprint": review[
            "execution_permit_fingerprint"
        ],
        "request_fingerprint": review["request_fingerprint"],
        "client_order_id": review["client_order_id"],
        "account_fingerprint": review["account_fingerprint"],
        "server": review["server"],
        "not_before_utc": review["not_before_utc"],
        "expires_at_utc": review["expires_at_utc"],
        "approval_time_utc": approval["approval_time_utc"],
        "activation_time_utc": _utc_string(activation_time),
        "practice_only": True,
        "max_new_orders": 1,
        "explicit_execution_approval_recorded": True,
        "operator_gate_activation_contract_ready": True,
        "demo_execution_source_armed": False,
        "runner_activation_wired": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
        "phase11_authorized": False,
    }
    result = payload | {"gate_activation_contract_fingerprint": _digest(payload)}
    validate_phase9_demo_gate_activation_contract(
        result,
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
    return result


def validate_phase9_demo_gate_activation_contract(
    value: Mapping[str, object],
    *,
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
    journal_rows: Sequence[Mapping[str, object]],
) -> None:
    validate_phase9_first_demo_explicit_approval(
        approval,
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
    if DEMO_EXECUTION_SOURCE_ARMED is not False:
        raise ValueError(
            "DEC-068 activation validation requires source gate unarmed"
        )
    if value.get("protocol") != PHASE9_DEMO_GATE_ACTIVATION_CONTRACT_PROTOCOL:
        raise ValueError("Phase 9 gate activation protocol mismatch")
    if value.get("experiment_id") != PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_EXPERIMENT_ID:
        raise ValueError("Phase 9 gate activation experiment mismatch")
    if value.get("decision") != PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_DECISION:
        raise ValueError("Phase 9 gate activation decision mismatch")
    if value.get("outcome") != PHASE9_DEMO_GATE_ACTIVATION_CONTRACT_READY:
        raise ValueError("Phase 9 gate activation outcome mismatch")
    _commit(
        value.get("gate_activation_builder_code_commit"),
        field="Phase 9 gate activation builder code commit",
    )

    review = packet.get("review")
    assert isinstance(review, Mapping)
    identities = {
        "authorization_packet_fingerprint": packet[
            "authorization_packet_fingerprint"
        ],
        "authorization_challenge_fingerprint": packet[
            "authorization_challenge_fingerprint"
        ],
        "explicit_approval_fingerprint": approval[
            "explicit_approval_fingerprint"
        ],
        "execution_permit_fingerprint": review[
            "execution_permit_fingerprint"
        ],
        "request_fingerprint": review["request_fingerprint"],
        "client_order_id": review["client_order_id"],
        "account_fingerprint": review["account_fingerprint"],
        "server": review["server"],
        "not_before_utc": review["not_before_utc"],
        "expires_at_utc": review["expires_at_utc"],
        "approval_time_utc": approval["approval_time_utc"],
    }
    for field, expected in identities.items():
        if value.get(field) != expected:
            raise ValueError(f"Phase 9 gate activation {field} mismatch")
    for field in (
        "authorization_packet_fingerprint",
        "authorization_challenge_fingerprint",
        "explicit_approval_fingerprint",
        "execution_permit_fingerprint",
        "request_fingerprint",
        "account_fingerprint",
        "gate_activation_contract_fingerprint",
    ):
        _sha256(value.get(field), field=f"Phase 9 gate activation {field}")
    _text(value.get("client_order_id"), field="Phase 9 client-order ID")
    _text(value.get("server"), field="Phase 9 demo server")

    activation_time = _parse_utc(
        value.get("activation_time_utc"),
        field="Phase 9 gate activation time",
    )
    approval_time = _parse_utc(
        value.get("approval_time_utc"),
        field="Phase 9 explicit approval time",
    )
    start, _, expiry = _approval_window(review)
    if activation_time < approval_time:
        raise ValueError("Phase 9 activation time precedes approval")
    if activation_time < start or activation_time > expiry:
        raise ValueError("Phase 9 activation time is outside arm window")

    if value.get("practice_only") is not True:
        raise ValueError("Phase 9 gate activation must be practice-only")
    if value.get("max_new_orders") != 1:
        raise ValueError("Phase 9 gate activation must be one-order-only")
    if value.get("explicit_execution_approval_recorded") is not True:
        raise ValueError("Phase 9 gate activation lacks explicit approval")
    if value.get("operator_gate_activation_contract_ready") is not True:
        raise ValueError("Phase 9 gate activation contract is not ready")

    for field in (
        "demo_execution_source_armed",
        "runner_activation_wired",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "phase10_authorized",
        "phase11_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(f"Phase 9 gate activation requires {field}=false")

    fingerprint = value["gate_activation_contract_fingerprint"]
    payload = dict(value)
    payload.pop("gate_activation_contract_fingerprint", None)
    if fingerprint != _digest(payload):
        raise ValueError("Phase 9 gate activation fingerprint mismatch")


def write_phase9_first_demo_explicit_approval(
    value: Mapping[str, object],
    *,
    out_dir: Path,
    packet: Mapping[str, object],
    design: Mapping[str, object],
    request: Mapping[str, object],
    session_arm: Mapping[str, object],
    session_ready: Mapping[str, object],
    execution_arm: Mapping[str, object],
    runtime_authority: Mapping[str, object],
    launch_preflight: Mapping[str, object],
    execution_permit: Mapping[str, object],
    journal_rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    validate_phase9_first_demo_explicit_approval(
        value,
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
    root = Path(out_dir)
    result_path = root / "explicit-approval.json"
    manifest_path = root / "manifest.json"
    if result_path.exists() or manifest_path.exists():
        raise FileExistsError("Phase 9 explicit approval artifacts already exist")
    root.mkdir(parents=True, exist_ok=True)
    payload = _stable_json_bytes(dict(value))
    _atomic_write(result_path, payload)
    manifest = {
        "protocol": PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_ARTIFACT_PROTOCOL,
        "experiment_id": PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_EXPERIMENT_ID,
        "decision": PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_DECISION,
        "outcome": PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_RECORDED,
        "explicit_approval_fingerprint": value[
            "explicit_approval_fingerprint"
        ],
        "demo_execution_source_armed": False,
        "runner_activation_wired": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
        "phase11_authorized": False,
        "artifacts": [{
            "path": result_path.name,
            "size_bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }],
    }
    _atomic_write(manifest_path, _stable_json_bytes(manifest))
    return manifest


def write_phase9_demo_gate_activation_contract(
    value: Mapping[str, object],
    *,
    out_dir: Path,
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
    journal_rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    validate_phase9_demo_gate_activation_contract(
        value,
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
    root = Path(out_dir)
    result_path = root / "gate-activation-contract.json"
    manifest_path = root / "manifest.json"
    if result_path.exists() or manifest_path.exists():
        raise FileExistsError(
            "Phase 9 gate-activation artifacts already exist"
        )
    root.mkdir(parents=True, exist_ok=True)
    payload = _stable_json_bytes(dict(value))
    _atomic_write(result_path, payload)
    manifest = {
        "protocol": PHASE9_DEMO_GATE_ACTIVATION_ARTIFACT_PROTOCOL,
        "experiment_id": PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_EXPERIMENT_ID,
        "decision": PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_DECISION,
        "outcome": PHASE9_DEMO_GATE_ACTIVATION_CONTRACT_READY,
        "gate_activation_contract_fingerprint": value[
            "gate_activation_contract_fingerprint"
        ],
        "demo_execution_source_armed": False,
        "runner_activation_wired": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
        "phase11_authorized": False,
        "artifacts": [{
            "path": result_path.name,
            "size_bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }],
    }
    _atomic_write(manifest_path, _stable_json_bytes(manifest))
    return manifest


__all__ = [
    "PHASE9_DEMO_GATE_ACTIVATION_ARTIFACT_PROTOCOL",
    "PHASE9_DEMO_GATE_ACTIVATION_CONTRACT_PROTOCOL",
    "PHASE9_DEMO_GATE_ACTIVATION_CONTRACT_READY",
    "PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_ARTIFACT_PROTOCOL",
    "PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_DECISION",
    "PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_EXPERIMENT_ID",
    "PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_PROTOCOL",
    "PHASE9_FIRST_DEMO_EXPLICIT_APPROVAL_RECORDED",
    "approval_statement_for_challenge",
    "build_phase9_demo_gate_activation_contract",
    "build_phase9_first_demo_explicit_approval",
    "validate_phase9_demo_gate_activation_contract",
    "validate_phase9_first_demo_explicit_approval",
    "write_phase9_demo_gate_activation_contract",
    "write_phase9_first_demo_explicit_approval",
]
