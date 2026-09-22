from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Mapping

from .design import (
    MT5_ALLOWED_SERVERS,
    MT5_BRIDGE_PROTOCOL,
    MT5_PROVIDER,
    MT5_TRANSPORT,
    PHASE8B_DESIGN_PROTOCOL,
    validate_phase8b_design,
)
from .qualification import (
    PHASE8B_QUALIFICATION_PROTOCOL,
    Phase8BQualificationOutcome,
)


PHASE8B_REGISTRATION_PROTOCOL = "fmp-phase8b-campaign-registration-v1"
PHASE8B_REGISTRATION_ARTIFACT_PROTOCOL = (
    "fmp-phase8b-campaign-registration-artifacts-v1"
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase SHA-256")
    return value


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _COMMIT_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase 40-character commit SHA")
    return value


def _validate_utc(value: datetime) -> None:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() != timedelta(0)
    ):
        raise ValueError("registration timestamp must use UTC")


def _canonical_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


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


def _validate_qualification(
    *,
    design: Mapping[str, object],
    design_sha256: str,
    qualification: Mapping[str, object],
) -> tuple[str, str, dict[str, str]]:
    if qualification.get("protocol") != PHASE8B_QUALIFICATION_PROTOCOL:
        raise ValueError("Phase 8B qualification protocol mismatch")
    if qualification.get("experiment_id") != "EXP-20260922-018":
        raise ValueError("Phase 8B qualification experiment mismatch")
    if qualification.get("design_sha256") != design_sha256:
        raise ValueError("Phase 8B qualification/design digest mismatch")
    if qualification.get("design_fingerprint") != design.get(
        "design_fingerprint"
    ):
        raise ValueError("Phase 8B qualification design fingerprint mismatch")
    if qualification.get("provider") != MT5_PROVIDER:
        raise ValueError("Phase 8B qualification provider mismatch")
    if qualification.get("transport") != MT5_TRANSPORT:
        raise ValueError("Phase 8B qualification transport mismatch")
    if qualification.get("connector_protocol") != MT5_BRIDGE_PROTOCOL:
        raise ValueError("Phase 8B qualification bridge protocol mismatch")
    if qualification.get("allowed_servers") != list(MT5_ALLOWED_SERVERS):
        raise ValueError("Phase 8B qualification allowed-server mismatch")
    if qualification.get("required_symbols") != design.get("required_symbols"):
        raise ValueError("Phase 8B qualification symbol coverage mismatch")
    if qualification.get("bridge_file_by_symbol") != design.get(
        "connector",
        {},
    ).get("bridge_file_by_symbol"):
        raise ValueError("Phase 8B qualification bridge-file mapping mismatch")
    if qualification.get("outcome") != Phase8BQualificationOutcome.QUALIFIED.value:
        raise ValueError("Phase 8B registration requires qualified connector")
    if qualification.get("campaign_registration_authorized") is not True:
        raise ValueError("Phase 8B registration is not authorized by qualification")
    for field in (
        "campaign_start_authorized",
        "promotion_authorized",
        "demo_order_authorized",
        "live_order_authorized",
        "broker_mutation_authorized",
        "real_money_authorized",
        "phase9_authorized",
    ):
        if qualification.get(field) is not False:
            raise ValueError(
                f"Phase 8B qualification requires {field}=false"
            )

    account = _validate_sha256(
        qualification.get("common_account_fingerprint"),
        field="Phase 8B common account fingerprint",
    )
    server = qualification.get("common_server")
    if not isinstance(server, str) or server not in MT5_ALLOWED_SERVERS:
        raise ValueError("Phase 8B common server is invalid")

    raw_per_symbol = qualification.get("per_symbol")
    if not isinstance(raw_per_symbol, Mapping):
        raise ValueError("Phase 8B qualification per_symbol is malformed")
    required_symbols = tuple(str(item) for item in design["required_symbols"])
    if set(raw_per_symbol) != set(required_symbols):
        raise ValueError("Phase 8B qualification per-symbol coverage mismatch")

    sessions: dict[str, str] = {}
    for symbol in required_symbols:
        row = raw_per_symbol[symbol]
        if not isinstance(row, Mapping):
            raise ValueError("Phase 8B qualification symbol row is malformed")
        if row.get("symbol") != symbol or row.get("outcome") != "PASS":
            raise ValueError("Phase 8B qualification symbol did not PASS")
        if row.get("account_fingerprint") != account:
            raise ValueError("Phase 8B qualification account identity mismatch")
        if row.get("server") != server:
            raise ValueError("Phase 8B qualification server identity mismatch")
        session = _validate_sha256(
            row.get("bridge_session_id"),
            field=f"Phase 8B {symbol} bridge session",
        )
        sessions[symbol] = session
    if len(set(sessions.values())) != len(sessions):
        raise ValueError("Phase 8B bridge session IDs must be distinct")
    return account, server, sessions


def build_phase8b_registration(
    *,
    design: Mapping[str, object],
    design_sha256: str,
    qualification: Mapping[str, object],
    qualification_sha256: str,
    code_commit: str,
    registered_at_utc: datetime,
) -> dict[str, object]:
    validate_phase8b_design(design)
    design_sha = _validate_sha256(
        design_sha256,
        field="Phase 8B design artifact digest",
    )
    qualification_sha = _validate_sha256(
        qualification_sha256,
        field="Phase 8B qualification artifact digest",
    )
    commit = _validate_commit(
        code_commit,
        field="Phase 8B registration code commit",
    )
    _validate_utc(registered_at_utc)
    account, server, sessions = _validate_qualification(
        design=design,
        design_sha256=design_sha,
        qualification=qualification,
    )

    payload = {
        "protocol": PHASE8B_REGISTRATION_PROTOCOL,
        "experiment_id": "EXP-20260922-018",
        "design_sha256": design_sha,
        "qualification_sha256": qualification_sha,
        "design_fingerprint": design["design_fingerprint"],
        "qualification_code_commit": qualification[
            "qualification_code_commit"
        ],
        "registration_code_commit": commit,
        "registered_at_utc": registered_at_utc.isoformat().replace(
            "+00:00",
            "Z",
        ),
        "champion_set_id": design["champion_set_id"],
        "champion_set_fingerprint": design[
            "champion_set_fingerprint"
        ],
        "strategy_count": design["strategy_count"],
        "strategy_fingerprints": list(
            design["strategy_fingerprints"]
        ),
        "strategies": list(design["strategies"]),
        "required_symbols": list(design["required_symbols"]),
        "required_timeframes": list(design["required_timeframes"]),
        "provider": MT5_PROVIDER,
        "transport": MT5_TRANSPORT,
        "connector_protocol": MT5_BRIDGE_PROTOCOL,
        "bridge_file_by_symbol": dict(
            design["connector"]["bridge_file_by_symbol"]
        ),
        "allowed_servers": list(MT5_ALLOWED_SERVERS),
        "account_fingerprint": account,
        "server": server,
        "bridge_session_id_by_symbol": sessions,
        "liveness": dict(design["liveness"]),
        "slippage_scenarios": list(design["slippage_scenarios"]),
        "campaign_start_authorized": False,
        "promotion_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_authorized": False,
    }
    return payload | {
        "registration_fingerprint": _canonical_digest(payload)
    }


def validate_phase8b_registration(
    registration: Mapping[str, object],
) -> None:
    if registration.get("protocol") != PHASE8B_REGISTRATION_PROTOCOL:
        raise ValueError("Phase 8B registration protocol mismatch")
    if registration.get("experiment_id") != "EXP-20260922-018":
        raise ValueError("Phase 8B registration experiment mismatch")
    for field in (
        "design_sha256",
        "qualification_sha256",
        "design_fingerprint",
        "champion_set_fingerprint",
        "account_fingerprint",
    ):
        _validate_sha256(
            registration.get(field),
            field=f"Phase 8B registration {field}",
        )
    _validate_commit(
        registration.get("qualification_code_commit"),
        field="Phase 8B qualification code commit",
    )
    _validate_commit(
        registration.get("registration_code_commit"),
        field="Phase 8B registration code commit",
    )
    raw_time = registration.get("registered_at_utc")
    if not isinstance(raw_time, str) or not raw_time.endswith("Z"):
        raise ValueError("Phase 8B registration timestamp is invalid")
    try:
        parsed = datetime.fromisoformat(
            raw_time.replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise ValueError("Phase 8B registration timestamp is invalid") from exc
    _validate_utc(parsed)

    required_symbols = registration.get("required_symbols")
    sessions = registration.get("bridge_session_id_by_symbol")
    if not isinstance(required_symbols, list) or not required_symbols:
        raise ValueError("Phase 8B registration required symbols are malformed")
    if not isinstance(sessions, Mapping) or set(sessions) != set(required_symbols):
        raise ValueError("Phase 8B registration session coverage mismatch")
    for symbol in required_symbols:
        _validate_sha256(
            sessions[symbol],
            field=f"Phase 8B {symbol} bridge session",
        )
    if len(set(sessions.values())) != len(sessions):
        raise ValueError("Phase 8B registration bridge sessions collide")

    server = registration.get("server")
    if not isinstance(server, str) or server not in MT5_ALLOWED_SERVERS:
        raise ValueError("Phase 8B registration server is invalid")
    if registration.get("provider") != MT5_PROVIDER:
        raise ValueError("Phase 8B registration provider mismatch")
    if registration.get("transport") != MT5_TRANSPORT:
        raise ValueError("Phase 8B registration transport mismatch")
    if registration.get("connector_protocol") != MT5_BRIDGE_PROTOCOL:
        raise ValueError("Phase 8B registration bridge protocol mismatch")

    for field in (
        "campaign_start_authorized",
        "promotion_authorized",
        "demo_order_authorized",
        "live_order_authorized",
        "broker_mutation_authorized",
        "real_money_authorized",
        "phase9_authorized",
    ):
        if registration.get(field) is not False:
            raise ValueError(f"Phase 8B registration requires {field}=false")

    fingerprint = _validate_sha256(
        registration.get("registration_fingerprint"),
        field="Phase 8B registration fingerprint",
    )
    payload = dict(registration)
    payload.pop("registration_fingerprint", None)
    if fingerprint != _canonical_digest(payload):
        raise ValueError("Phase 8B registration fingerprint mismatch")


def write_phase8b_registration(
    registration: Mapping[str, object],
    campaign_dir: Path,
) -> dict[str, object]:
    validate_phase8b_registration(registration)
    root = Path(campaign_dir)
    registration_path = root / "registration.json"
    manifest_path = root / "registration-manifest.json"
    if registration_path.exists() or manifest_path.exists():
        raise FileExistsError(
            "Phase 8B campaign registration already exists"
        )
    root.mkdir(parents=True, exist_ok=True)
    payload = _stable_json_bytes(dict(registration))
    _atomic_write(registration_path, payload)
    manifest = {
        "protocol": PHASE8B_REGISTRATION_ARTIFACT_PROTOCOL,
        "experiment_id": "EXP-20260922-018",
        "campaign_start_authorized": False,
        "promotion_authorized": False,
        "artifacts": [
            {
                "path": registration_path.name,
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        ],
    }
    _atomic_write(manifest_path, _stable_json_bytes(manifest))
    return manifest


__all__ = [
    "PHASE8B_REGISTRATION_PROTOCOL",
    "build_phase8b_registration",
    "validate_phase8b_registration",
    "write_phase8b_registration",
]
