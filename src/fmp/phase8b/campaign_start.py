from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Mapping
from zoneinfo import ZoneInfo

from .bridge import Phase8BBridgeFileTail
from .registration import validate_phase8b_registration


PHASE8B_CAMPAIGN_START_PROTOCOL = "fmp-phase8b-campaign-start-v1"
PHASE8B_CAMPAIGN_START_ARTIFACT_PROTOCOL = (
    "fmp-phase8b-campaign-start-artifacts-v1"
)
PHASE8B_CAMPAIGN_START_AUTHORIZED = "PHASE8B_CAMPAIGN_START_AUTHORIZED"
PHASE8B_CAMPAIGN_START_EXPERIMENT_ID = "EXP-20260922-019"
READER_START_SEMANTICS = "TAIL_AT_EOF_NO_BACKFILL"

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
_LONDON = ZoneInfo("Europe/London")


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase SHA-256")
    return value


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _COMMIT_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase 40-character commit SHA")
    return value


def _validate_utc(value: datetime, *, field: str) -> None:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() != timedelta(0)
    ):
        raise ValueError(f"{field} must use UTC")


def _utc_string(value: datetime) -> str:
    _validate_utc(value, field="campaign start timestamp")
    return value.isoformat().replace("+00:00", "Z")


def _parse_utc_string(value: object, *, field: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{field} must be an ISO-8601 UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO-8601 UTC timestamp") from exc
    _validate_utc(parsed, field=field)
    return parsed


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


def _validate_bridge_tails(
    *,
    registration: Mapping[str, object],
    bridge_tails: Mapping[str, Phase8BBridgeFileTail],
) -> dict[str, str]:
    raw_symbols = registration.get("required_symbols")
    if not isinstance(raw_symbols, list) or not raw_symbols:
        raise ValueError("Phase 8B registration required symbols are malformed")
    required_symbols = tuple(str(item) for item in raw_symbols)
    if set(bridge_tails) != set(required_symbols):
        raise ValueError(
            "Phase 8B campaign start bridge coverage does not match registration"
        )

    registered_sessions = registration.get("bridge_session_id_by_symbol")
    if not isinstance(registered_sessions, Mapping):
        raise ValueError("Phase 8B registered bridge sessions are malformed")

    sessions: dict[str, str] = {}
    for symbol in required_symbols:
        tail = bridge_tails[symbol]
        start = getattr(tail, "start_record", None)
        if start is None:
            raise ValueError(
                f"Phase 8B {symbol} bridge tail has no start record"
            )
        if start.symbol != symbol:
            raise ValueError(
                f"Phase 8B {symbol} current bridge symbol mismatch"
            )
        if start.protocol != registration.get("connector_protocol"):
            raise ValueError(
                f"Phase 8B {symbol} current bridge protocol mismatch"
            )
        expected_session = registered_sessions.get(symbol)
        if start.bridge_session_id != expected_session:
            raise ValueError(
                f"Phase 8B {symbol} current bridge session mismatch"
            )
        if start.account_fingerprint != registration.get(
            "account_fingerprint"
        ):
            raise ValueError(
                f"Phase 8B {symbol} current bridge account mismatch"
            )
        if start.server != registration.get("server"):
            raise ValueError(
                f"Phase 8B {symbol} current bridge server mismatch"
            )
        if start.account_mode != "DEMO":
            raise ValueError(
                f"Phase 8B {symbol} current bridge is not DEMO"
            )
        sessions[symbol] = start.bridge_session_id

    if len(set(sessions.values())) != len(sessions):
        raise ValueError("Phase 8B current bridge sessions collide")
    return sessions


def build_phase8b_campaign_start_authorization(
    *,
    registration: Mapping[str, object],
    registration_sha256: str,
    bridge_tails: Mapping[str, Phase8BBridgeFileTail],
    code_commit: str,
    started_at_utc: datetime,
) -> dict[str, object]:
    validate_phase8b_registration(registration)
    registration_sha = _validate_sha256(
        registration_sha256,
        field="Phase 8B registration artifact digest",
    )
    start_commit = _validate_commit(
        code_commit,
        field="Phase 8B campaign-start code commit",
    )
    _validate_utc(started_at_utc, field="campaign start timestamp")
    sessions = _validate_bridge_tails(
        registration=registration,
        bridge_tails=bridge_tails,
    )

    payload = {
        "protocol": PHASE8B_CAMPAIGN_START_PROTOCOL,
        "experiment_id": PHASE8B_CAMPAIGN_START_EXPERIMENT_ID,
        "outcome": PHASE8B_CAMPAIGN_START_AUTHORIZED,
        "registration_sha256": registration_sha,
        "registration_fingerprint": registration[
            "registration_fingerprint"
        ],
        "registration_code_commit": registration[
            "registration_code_commit"
        ],
        "start_authorization_code_commit": start_commit,
        "campaign_start_utc": _utc_string(started_at_utc),
        "first_london_date": started_at_utc.astimezone(
            _LONDON
        ).date().isoformat(),
        "reader_start_semantics": READER_START_SEMANTICS,
        "champion_set_id": registration["champion_set_id"],
        "champion_set_fingerprint": registration[
            "champion_set_fingerprint"
        ],
        "strategy_count": registration["strategy_count"],
        "strategy_fingerprints": list(
            registration["strategy_fingerprints"]
        ),
        "strategies": list(registration["strategies"]),
        "required_symbols": list(registration["required_symbols"]),
        "required_timeframes": list(
            registration["required_timeframes"]
        ),
        "provider": registration["provider"],
        "transport": registration["transport"],
        "connector_protocol": registration["connector_protocol"],
        "bridge_file_by_symbol": dict(
            registration["bridge_file_by_symbol"]
        ),
        "allowed_servers": list(registration["allowed_servers"]),
        "account_fingerprint": registration["account_fingerprint"],
        "server": registration["server"],
        "bridge_session_id_by_symbol": sessions,
        "liveness": dict(registration["liveness"]),
        "slippage_scenarios": list(
            registration["slippage_scenarios"]
        ),
        "campaign_start_authorized": True,
        "prospective_capture_authorized": True,
        "promotion_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_authorized": False,
    }
    return payload | {
        "start_authorization_fingerprint": _canonical_digest(payload)
    }


def validate_phase8b_campaign_start_authorization(
    authorization: Mapping[str, object],
) -> None:
    if authorization.get("protocol") != PHASE8B_CAMPAIGN_START_PROTOCOL:
        raise ValueError("Phase 8B campaign-start protocol mismatch")
    if authorization.get(
        "experiment_id"
    ) != PHASE8B_CAMPAIGN_START_EXPERIMENT_ID:
        raise ValueError("Phase 8B campaign-start experiment mismatch")
    if authorization.get(
        "outcome"
    ) != PHASE8B_CAMPAIGN_START_AUTHORIZED:
        raise ValueError("Phase 8B campaign-start outcome mismatch")

    for field in (
        "registration_sha256",
        "registration_fingerprint",
        "champion_set_fingerprint",
        "account_fingerprint",
    ):
        _validate_sha256(
            authorization.get(field),
            field=f"Phase 8B campaign-start {field}",
        )
    for field in (
        "registration_code_commit",
        "start_authorization_code_commit",
    ):
        _validate_commit(
            authorization.get(field),
            field=f"Phase 8B campaign-start {field}",
        )

    fingerprint = _validate_sha256(
        authorization.get("start_authorization_fingerprint"),
        field="Phase 8B start-authorization fingerprint",
    )
    payload = dict(authorization)
    payload.pop("start_authorization_fingerprint", None)
    if fingerprint != _canonical_digest(payload):
        raise ValueError(
            "Phase 8B start-authorization fingerprint mismatch"
        )

    started = _parse_utc_string(
        authorization.get("campaign_start_utc"),
        field="Phase 8B campaign start timestamp",
    )
    expected_london_date = started.astimezone(
        _LONDON
    ).date().isoformat()
    if authorization.get("first_london_date") != expected_london_date:
        raise ValueError("Phase 8B campaign-start London date mismatch")
    if authorization.get(
        "reader_start_semantics"
    ) != READER_START_SEMANTICS:
        raise ValueError("Phase 8B campaign-start reader semantics drift")

    required_symbols = authorization.get("required_symbols")
    sessions = authorization.get("bridge_session_id_by_symbol")
    bridge_files = authorization.get("bridge_file_by_symbol")
    if not isinstance(required_symbols, list) or not required_symbols:
        raise ValueError(
            "Phase 8B campaign-start required symbols are malformed"
        )
    if (
        not isinstance(sessions, Mapping)
        or set(sessions) != set(required_symbols)
    ):
        raise ValueError(
            "Phase 8B campaign-start session coverage mismatch"
        )
    if (
        not isinstance(bridge_files, Mapping)
        or set(bridge_files) != set(required_symbols)
    ):
        raise ValueError(
            "Phase 8B campaign-start bridge-file coverage mismatch"
        )
    for symbol in required_symbols:
        _validate_sha256(
            sessions[symbol],
            field=f"Phase 8B {symbol} campaign-start bridge session",
        )
    if len(set(sessions.values())) != len(sessions):
        raise ValueError("Phase 8B campaign-start bridge sessions collide")

    strategy_fingerprints = authorization.get(
        "strategy_fingerprints"
    )
    strategies = authorization.get("strategies")
    if (
        not isinstance(strategy_fingerprints, list)
        or not strategy_fingerprints
        or len(set(strategy_fingerprints))
        != len(strategy_fingerprints)
    ):
        raise ValueError(
            "Phase 8B campaign-start strategy fingerprints are malformed"
        )
    if authorization.get("strategy_count") != len(
        strategy_fingerprints
    ):
        raise ValueError("Phase 8B campaign-start strategy count mismatch")
    if (
        not isinstance(strategies, list)
        or len(strategies) != len(strategy_fingerprints)
    ):
        raise ValueError("Phase 8B campaign-start strategies are malformed")
    if [
        row.get("fingerprint")
        for row in strategies
        if isinstance(row, Mapping)
    ] != strategy_fingerprints:
        raise ValueError(
            "Phase 8B campaign-start strategy identity mismatch"
        )

    if authorization.get("campaign_start_authorized") is not True:
        raise ValueError("Phase 8B campaign start is not authorized")
    if authorization.get("prospective_capture_authorized") is not True:
        raise ValueError("Phase 8B prospective capture is not authorized")
    for field in (
        "promotion_authorized",
        "demo_order_authorized",
        "live_order_authorized",
        "broker_mutation_authorized",
        "real_money_authorized",
        "phase9_authorized",
    ):
        if authorization.get(field) is not False:
            raise ValueError(
                f"Phase 8B campaign-start requires {field}=false"
            )

def write_phase8b_campaign_start_authorization(
    authorization: Mapping[str, object],
    campaign_dir: Path,
) -> dict[str, object]:
    validate_phase8b_campaign_start_authorization(authorization)
    root = Path(campaign_dir)
    result_path = root / "start-authorization.json"
    manifest_path = root / "start-authorization-manifest.json"
    if result_path.exists() or manifest_path.exists():
        raise FileExistsError(
            "Phase 8B campaign start authorization already exists"
        )
    root.mkdir(parents=True, exist_ok=True)
    payload = _stable_json_bytes(dict(authorization))
    _atomic_write(result_path, payload)
    manifest = {
        "protocol": PHASE8B_CAMPAIGN_START_ARTIFACT_PROTOCOL,
        "experiment_id": PHASE8B_CAMPAIGN_START_EXPERIMENT_ID,
        "campaign_start_authorized": True,
        "prospective_capture_authorized": True,
        "promotion_authorized": False,
        "artifacts": [
            {
                "path": result_path.name,
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        ],
    }
    _atomic_write(
        manifest_path,
        _stable_json_bytes(manifest),
    )
    return manifest


__all__ = [
    "PHASE8B_CAMPAIGN_START_ARTIFACT_PROTOCOL",
    "PHASE8B_CAMPAIGN_START_AUTHORIZED",
    "PHASE8B_CAMPAIGN_START_EXPERIMENT_ID",
    "PHASE8B_CAMPAIGN_START_PROTOCOL",
    "READER_START_SEMANTICS",
    "build_phase8b_campaign_start_authorization",
    "validate_phase8b_campaign_start_authorization",
    "write_phase8b_campaign_start_authorization",
]
