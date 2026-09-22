from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Mapping, Sequence

from fmp.phase9.acceptance import (
    MAX_MEDIAN_ADVERSE_SLIPPAGE_PIPS,
    MAX_P95_ADVERSE_SLIPPAGE_PIPS,
    MIN_COMPLETED_TRADES,
    MIN_DEMO_SESSION_DATES,
    MIN_ELAPSED_WEEKS,
    MIN_REPRESENTED_FAMILIES,
    MIN_REPRESENTED_PAIRS,
    PHASE9_DEMO_ACCEPTANCE_DECISION,
)
from fmp.phase9.execution_gate import DEMO_EXECUTION_SOURCE_ARMED
from fmp.phase9.permit import validate_phase9_demo_execution_permit


PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_DECISION = "DEC-067"
PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_EXPERIMENT_ID = "EXP-20260922-038"
PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_PROTOCOL = (
    "fmp-phase9-first-demo-authorization-packet-v1"
)
PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_ARTIFACT_PROTOCOL = (
    "fmp-phase9-first-demo-authorization-packet-artifacts-v1"
)
PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_READY = (
    "PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_READY"
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


def _positive_number(value: object, *, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be numeric")
    result = float(value)
    if result <= 0:
        raise ValueError(f"{field} must be positive")
    return result


def _strategy_summary(
    design: Mapping[str, object],
    *,
    strategy_fingerprint: str,
) -> dict[str, object]:
    strategies = design.get("strategies")
    if not isinstance(strategies, list):
        raise ValueError("Phase 9 design strategy rows are malformed")
    matches = [
        row
        for row in strategies
        if isinstance(row, Mapping)
        and row.get("fingerprint") == strategy_fingerprint
    ]
    if len(matches) != 1:
        raise ValueError("Phase 9 authorization packet strategy mismatch")
    row = matches[0]
    family = _text(
        row.get("family"),
        field="Phase 9 authorization packet strategy family",
    )
    timeframe = _text(
        row.get("timeframe"),
        field="Phase 9 authorization packet strategy timeframe",
    )
    symbol = _text(
        row.get("symbol"),
        field="Phase 9 authorization packet strategy symbol",
    )
    return {
        "strategy_fingerprint": strategy_fingerprint,
        "strategy_family": family,
        "strategy_timeframe": timeframe,
        "strategy_symbol": symbol,
    }


def _acceptance_obligations() -> dict[str, object]:
    return {
        "decision": PHASE9_DEMO_ACCEPTANCE_DECISION,
        "min_completed_trades": MIN_COMPLETED_TRADES,
        "min_elapsed_weeks": MIN_ELAPSED_WEEKS,
        "min_demo_session_dates": MIN_DEMO_SESSION_DATES,
        "min_represented_strategy_families": MIN_REPRESENTED_FAMILIES,
        "min_represented_pairs": MIN_REPRESENTED_PAIRS,
        "max_median_adverse_entry_slippage_pips": (
            MAX_MEDIAN_ADVERSE_SLIPPAGE_PIPS
        ),
        "max_p95_adverse_entry_slippage_pips": (
            MAX_P95_ADVERSE_SLIPPAGE_PIPS
        ),
    }


def _review_payload(
    *,
    design: Mapping[str, object],
    request: Mapping[str, object],
    execution_arm: Mapping[str, object],
    launch_preflight: Mapping[str, object],
    execution_permit: Mapping[str, object],
) -> dict[str, object]:
    execution = design.get("execution_path")
    if not isinstance(execution, Mapping):
        raise ValueError("Phase 9 execution path is malformed")
    strategy_fingerprint = _sha256(
        request.get("strategy_fingerprint"),
        field="Phase 9 authorization packet strategy fingerprint",
    )
    strategy = _strategy_summary(
        design,
        strategy_fingerprint=strategy_fingerprint,
    )
    order_check_request = launch_preflight.get("order_check_request")
    if not isinstance(order_check_request, Mapping):
        raise ValueError("Phase 9 authorization packet order-check request malformed")
    mt5_request = order_check_request.get("mt5_request")
    if not isinstance(mt5_request, Mapping):
        raise ValueError("Phase 9 authorization packet checked MT5 request malformed")

    checked_price = _positive_number(
        mt5_request.get("price"),
        field="Phase 9 authorization packet checked price",
    )
    volume_lots = _positive_number(
        mt5_request.get("volume"),
        field="Phase 9 authorization packet volume",
    )
    if execution_permit.get("checked_mt5_request_sha256") != _digest(
        dict(mt5_request)
    ):
        raise ValueError("Phase 9 authorization packet checked request mismatch")
    expected_type = (
        "ORDER_TYPE_BUY"
        if request.get("direction") == "LONG"
        else "ORDER_TYPE_SELL"
    )
    if request.get("direction") not in {"LONG", "SHORT"}:
        raise ValueError("Phase 9 authorization packet direction is invalid")
    if mt5_request.get("type") != expected_type:
        raise ValueError("Phase 9 authorization packet MT5 side mismatch")
    if mt5_request.get("comment") != request.get("client_order_id"):
        raise ValueError("Phase 9 authorization packet client comment mismatch")
    if mt5_request.get("symbol") != request.get("broker_symbol"):
        raise ValueError("Phase 9 authorization packet broker symbol mismatch")
    if mt5_request.get("sl") != request.get("stop_price"):
        raise ValueError("Phase 9 authorization packet protective stop mismatch")
    if mt5_request.get("tp") != request.get("target_price"):
        raise ValueError("Phase 9 authorization packet target mismatch")

    return {
        "account_mode": "DEMO",
        "account_fingerprint": execution["account_fingerprint"],
        "server": execution["server"],
        "provider": execution["provider"],
        "demo_design_fingerprint": design["demo_design_fingerprint"],
        "champion_set_fingerprint": design["champion_set_fingerprint"],
        **strategy,
        "request_fingerprint": request["request_fingerprint"],
        "execution_permit_fingerprint": execution_permit[
            "execution_permit_fingerprint"
        ],
        "client_order_id": request["client_order_id"],
        "decision_id": request["decision_id"],
        "symbol": request["symbol"],
        "broker_symbol": request["broker_symbol"],
        "direction": request["direction"],
        "units": request["units"],
        "volume_lots": volume_lots,
        "reserved_risk_usd": request["reserved_risk_usd"],
        "reference_entry_price": request["reference_entry_price"],
        "checked_mt5_price": checked_price,
        "protective_stop_price": request["stop_price"],
        "target_price": request["target_price"],
        "fill_mode": mt5_request.get("type_filling"),
        "time_in_force": mt5_request.get("type_time"),
        "decision_timestamp_utc": request["decision_timestamp_utc"],
        "earliest_executable_timestamp_utc": request[
            "earliest_executable_timestamp_utc"
        ],
        "launch_preflight_time_utc": launch_preflight[
            "launch_preflight_time_utc"
        ],
        "not_before_utc": execution_arm["not_before_utc"],
        "expires_at_utc": execution_arm["expires_at_utc"],
        "session_operator_reference": execution_arm[
            "operator_approval_reference"
        ],
        "checked_mt5_request_sha256": execution_permit[
            "checked_mt5_request_sha256"
        ],
        "demo_acceptance_obligations": _acceptance_obligations(),
    }


def build_phase9_first_demo_authorization_packet(
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
    code_commit: str,
) -> dict[str, object]:
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
    if DEMO_EXECUTION_SOURCE_ARMED is not False:
        raise ValueError(
            "DEC-067 packet construction requires demo execution source unarmed"
        )
    if execution_permit.get("demo_execution_permit_artifact_ready") is not True:
        raise ValueError("Phase 9 execution permit is not ready")
    if execution_permit.get("send_attempt_count") != 0:
        raise ValueError("Phase 9 execution permit is already spent")
    if execution_permit.get("practice_only") is not True:
        raise ValueError("Phase 9 authorization packet requires practice-only permit")
    if execution_permit.get("max_new_orders") != 1:
        raise ValueError("Phase 9 authorization packet requires one-order permit")

    commit = _commit(
        code_commit,
        field="Phase 9 authorization packet builder code commit",
    )
    review = _review_payload(
        design=design,
        request=request,
        execution_arm=execution_arm,
        launch_preflight=launch_preflight,
        execution_permit=execution_permit,
    )
    challenge = _digest(
        {
            "protocol": PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_PROTOCOL,
            "decision": PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_DECISION,
            "review": review,
        }
    )
    payload = {
        "protocol": PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_PROTOCOL,
        "experiment_id": PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_EXPERIMENT_ID,
        "decision": PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_DECISION,
        "outcome": PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_READY,
        "authorization_packet_builder_code_commit": commit,
        "review": review,
        "authorization_challenge_fingerprint": challenge,
        "first_demo_authorization_packet_ready": True,
        "explicit_execution_approval_recorded": False,
        "demo_execution_source_armed": False,
        "demo_execution_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
        "phase11_authorized": False,
    }
    result = payload | {
        "authorization_packet_fingerprint": _digest(payload)
    }
    validate_phase9_first_demo_authorization_packet(
        result,
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


def validate_phase9_first_demo_authorization_packet(
    value: Mapping[str, object],
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
) -> None:
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
    if DEMO_EXECUTION_SOURCE_ARMED is not False:
        raise ValueError(
            "DEC-067 packet validation requires demo execution source unarmed"
        )
    if value.get("protocol") != PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_PROTOCOL:
        raise ValueError("Phase 9 authorization packet protocol mismatch")
    if value.get("experiment_id") != PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_EXPERIMENT_ID:
        raise ValueError("Phase 9 authorization packet experiment mismatch")
    if value.get("decision") != PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_DECISION:
        raise ValueError("Phase 9 authorization packet decision mismatch")
    if value.get("outcome") != PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_READY:
        raise ValueError("Phase 9 authorization packet outcome mismatch")
    _commit(
        value.get("authorization_packet_builder_code_commit"),
        field="Phase 9 authorization packet builder code commit",
    )

    expected_review = _review_payload(
        design=design,
        request=request,
        execution_arm=execution_arm,
        launch_preflight=launch_preflight,
        execution_permit=execution_permit,
    )
    if value.get("review") != expected_review:
        raise ValueError("Phase 9 authorization packet review mismatch")
    expected_challenge = _digest(
        {
            "protocol": PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_PROTOCOL,
            "decision": PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_DECISION,
            "review": expected_review,
        }
    )
    if value.get("authorization_challenge_fingerprint") != expected_challenge:
        raise ValueError("Phase 9 authorization challenge mismatch")
    _sha256(
        value.get("authorization_challenge_fingerprint"),
        field="Phase 9 authorization challenge fingerprint",
    )
    _sha256(
        value.get("authorization_packet_fingerprint"),
        field="Phase 9 authorization packet fingerprint",
    )
    if value.get("first_demo_authorization_packet_ready") is not True:
        raise ValueError("Phase 9 first-demo authorization packet is not ready")

    for field in (
        "explicit_execution_approval_recorded",
        "demo_execution_source_armed",
        "demo_execution_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "phase10_authorized",
        "phase11_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(
                f"Phase 9 authorization packet requires {field}=false"
            )

    fingerprint = value["authorization_packet_fingerprint"]
    payload = dict(value)
    payload.pop("authorization_packet_fingerprint", None)
    if fingerprint != _digest(payload):
        raise ValueError("Phase 9 authorization packet fingerprint mismatch")


def write_phase9_first_demo_authorization_packet(
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
    execution_permit: Mapping[str, object],
    journal_rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    validate_phase9_first_demo_authorization_packet(
        value,
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
    packet_path = root / "first-demo-authorization-packet.json"
    manifest_path = root / "manifest.json"
    if packet_path.exists() or manifest_path.exists():
        raise FileExistsError(
            "Phase 9 first-demo authorization packet already exists"
        )
    root.mkdir(parents=True, exist_ok=True)
    payload = _stable_json_bytes(dict(value))
    _atomic_write(packet_path, payload)
    manifest = {
        "protocol": PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_ARTIFACT_PROTOCOL,
        "experiment_id": PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_EXPERIMENT_ID,
        "decision": PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_DECISION,
        "outcome": PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_READY,
        "authorization_challenge_fingerprint": value[
            "authorization_challenge_fingerprint"
        ],
        "authorization_packet_fingerprint": value[
            "authorization_packet_fingerprint"
        ],
        "explicit_execution_approval_recorded": False,
        "demo_execution_source_armed": False,
        "demo_execution_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "phase10_authorized": False,
        "phase11_authorized": False,
        "artifacts": [
            {
                "path": packet_path.name,
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        ],
    }
    _atomic_write(manifest_path, _stable_json_bytes(manifest))
    return manifest


__all__ = [
    "PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_ARTIFACT_PROTOCOL",
    "PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_DECISION",
    "PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_EXPERIMENT_ID",
    "PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_PROTOCOL",
    "PHASE9_FIRST_DEMO_AUTHORIZATION_PACKET_READY",
    "build_phase9_first_demo_authorization_packet",
    "validate_phase9_first_demo_authorization_packet",
    "write_phase9_first_demo_authorization_packet",
]
