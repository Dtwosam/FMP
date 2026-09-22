from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Mapping, Protocol

from .bridge import (
    Phase8BBridgeHeartbeatRecord,
    Phase8BBridgeProtocolError,
    Phase8BBridgeRecord,
    Phase8BBridgeSessionValidator,
    Phase8BBridgeStartRecord,
    Phase8BBridgeTickRecord,
    Phase8BQuote,
    parse_phase8b_bridge_line,
)
from .campaign_start import (
    READER_START_SEMANTICS,
    validate_phase8b_campaign_start_authorization,
)
from .registration import validate_phase8b_registration


PHASE8B_CAPTURE_PREFLIGHT_PROTOCOL = "fmp-phase8b-capture-preflight-v1"
PHASE8B_CAPTURE_PREFLIGHT_ARTIFACT_PROTOCOL = (
    "fmp-phase8b-capture-preflight-artifacts-v1"
)
PHASE8B_CAPTURE_EXPERIMENT_ID = "EXP-20260922-020"
PHASE8B_CAPTURE_FOUNDATION_READY = "PHASE8B_CAPTURE_FOUNDATION_READY"
CAPTURE_RECORD_PROTOCOL = "fmp-phase8b-capture-record-v1"

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
_CROSS_BOUND_FIELDS = (
    "registration_fingerprint",
    "registration_code_commit",
    "champion_set_id",
    "champion_set_fingerprint",
    "strategy_count",
    "strategy_fingerprints",
    "strategies",
    "required_symbols",
    "required_timeframes",
    "provider",
    "transport",
    "connector_protocol",
    "bridge_file_by_symbol",
    "account_fingerprint",
    "server",
    "bridge_session_id_by_symbol",
    "liveness",
    "slippage_scenarios",
)


class Phase8BRecordTail(Protocol):
    start_record: Phase8BBridgeStartRecord

    def read_available(self) -> tuple[Phase8BBridgeRecord, ...]: ...


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


def _utc_string(value: datetime, *, field: str) -> str:
    _validate_utc(value, field=field)
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


def _validate_exact_upstream(
    *,
    registration: Mapping[str, object],
    registration_sha256: str,
    authorization: Mapping[str, object],
    authorization_sha256: str,
) -> tuple[str, str]:
    validate_phase8b_registration(registration)
    validate_phase8b_campaign_start_authorization(authorization)
    registration_sha = _validate_sha256(
        registration_sha256,
        field="Phase 8B capture registration digest",
    )
    authorization_sha = _validate_sha256(
        authorization_sha256,
        field="Phase 8B capture start-authorization digest",
    )
    if authorization.get("registration_sha256") != registration_sha:
        raise ValueError("Phase 8B capture registration digest mismatch")
    for field in _CROSS_BOUND_FIELDS:
        if authorization.get(field) != registration.get(field):
            raise ValueError(
                f"Phase 8B capture upstream {field} mismatch"
            )
    return registration_sha, authorization_sha


def _validate_bridge_tails(
    *,
    authorization: Mapping[str, object],
    bridge_tails: Mapping[str, Phase8BRecordTail],
) -> dict[str, str]:
    raw_symbols = authorization.get("required_symbols")
    if not isinstance(raw_symbols, list) or not raw_symbols:
        raise ValueError("Phase 8B capture required symbols are malformed")
    symbols = tuple(str(item) for item in raw_symbols)
    if set(bridge_tails) != set(symbols):
        raise ValueError("Phase 8B capture bridge coverage mismatch")

    expected_sessions = authorization.get("bridge_session_id_by_symbol")
    if not isinstance(expected_sessions, Mapping):
        raise ValueError("Phase 8B capture bridge sessions are malformed")

    sessions: dict[str, str] = {}
    for symbol in symbols:
        start = getattr(bridge_tails[symbol], "start_record", None)
        if not isinstance(start, Phase8BBridgeStartRecord):
            raise ValueError(f"Phase 8B {symbol} capture requires BRIDGE_START")
        if start.symbol != symbol:
            raise ValueError(f"Phase 8B {symbol} current bridge symbol mismatch")
        if start.protocol != authorization.get("connector_protocol"):
            raise ValueError(f"Phase 8B {symbol} current bridge protocol mismatch")
        if start.bridge_session_id != expected_sessions.get(symbol):
            raise ValueError(f"Phase 8B {symbol} current bridge session mismatch")
        if start.account_fingerprint != authorization.get("account_fingerprint"):
            raise ValueError(f"Phase 8B {symbol} current bridge account mismatch")
        if start.server != authorization.get("server"):
            raise ValueError(f"Phase 8B {symbol} current bridge server mismatch")
        if start.account_mode != "DEMO":
            raise ValueError(f"Phase 8B {symbol} current bridge is not DEMO")
        sessions[symbol] = start.bridge_session_id

    if len(set(sessions.values())) != len(sessions):
        raise ValueError("Phase 8B current bridge sessions collide")
    return sessions


def build_phase8b_capture_preflight(
    *,
    registration: Mapping[str, object],
    registration_sha256: str,
    authorization: Mapping[str, object],
    authorization_sha256: str,
    bridge_tails: Mapping[str, Phase8BRecordTail],
    code_commit: str,
    prepared_at_utc: datetime,
) -> dict[str, object]:
    registration_sha, authorization_sha = _validate_exact_upstream(
        registration=registration,
        registration_sha256=registration_sha256,
        authorization=authorization,
        authorization_sha256=authorization_sha256,
    )
    capture_commit = _validate_commit(
        code_commit,
        field="Phase 8B capture-foundation code commit",
    )
    _validate_utc(prepared_at_utc, field="Phase 8B capture preflight timestamp")
    campaign_start = _parse_utc_string(
        authorization.get("campaign_start_utc"),
        field="Phase 8B campaign start timestamp",
    )
    if prepared_at_utc < campaign_start:
        raise ValueError("Phase 8B capture preflight precedes campaign start")
    sessions = _validate_bridge_tails(
        authorization=authorization,
        bridge_tails=bridge_tails,
    )

    payload = {
        "protocol": PHASE8B_CAPTURE_PREFLIGHT_PROTOCOL,
        "experiment_id": PHASE8B_CAPTURE_EXPERIMENT_ID,
        "outcome": PHASE8B_CAPTURE_FOUNDATION_READY,
        "registration_sha256": registration_sha,
        "registration_fingerprint": registration["registration_fingerprint"],
        "start_authorization_sha256": authorization_sha,
        "start_authorization_fingerprint": authorization[
            "start_authorization_fingerprint"
        ],
        "capture_foundation_code_commit": capture_commit,
        "prepared_at_utc": _utc_string(
            prepared_at_utc,
            field="Phase 8B capture preflight timestamp",
        ),
        "campaign_start_utc": authorization["campaign_start_utc"],
        "first_london_date": authorization["first_london_date"],
        "reader_start_semantics": READER_START_SEMANTICS,
        "champion_set_id": authorization["champion_set_id"],
        "champion_set_fingerprint": authorization[
            "champion_set_fingerprint"
        ],
        "strategy_count": authorization["strategy_count"],
        "strategy_fingerprints": list(
            authorization["strategy_fingerprints"]
        ),
        "strategies": list(authorization["strategies"]),
        "required_symbols": list(authorization["required_symbols"]),
        "required_timeframes": list(
            authorization["required_timeframes"]
        ),
        "provider": authorization["provider"],
        "transport": authorization["transport"],
        "connector_protocol": authorization["connector_protocol"],
        "bridge_file_by_symbol": dict(
            authorization["bridge_file_by_symbol"]
        ),
        "account_fingerprint": authorization["account_fingerprint"],
        "server": authorization["server"],
        "bridge_session_id_by_symbol": sessions,
        "liveness": dict(authorization["liveness"]),
        "slippage_scenarios": list(
            authorization["slippage_scenarios"]
        ),
        "capture_runtime_ready": True,
        "live_shadow_segment_started": False,
        "acceptance_authorized": False,
        "promotion_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_authorized": False,
    }
    return payload | {
        "capture_preflight_fingerprint": _canonical_digest(payload)
    }


def validate_phase8b_capture_preflight(
    preflight: Mapping[str, object],
) -> None:
    if preflight.get("protocol") != PHASE8B_CAPTURE_PREFLIGHT_PROTOCOL:
        raise ValueError("Phase 8B capture-preflight protocol mismatch")
    if preflight.get("experiment_id") != PHASE8B_CAPTURE_EXPERIMENT_ID:
        raise ValueError("Phase 8B capture-preflight experiment mismatch")
    if preflight.get("outcome") != PHASE8B_CAPTURE_FOUNDATION_READY:
        raise ValueError("Phase 8B capture-preflight outcome mismatch")

    fingerprint = _validate_sha256(
        preflight.get("capture_preflight_fingerprint"),
        field="Phase 8B capture-preflight fingerprint",
    )
    payload = dict(preflight)
    payload.pop("capture_preflight_fingerprint", None)
    if fingerprint != _canonical_digest(payload):
        raise ValueError("Phase 8B capture-preflight fingerprint mismatch")

    for field in (
        "registration_sha256",
        "registration_fingerprint",
        "start_authorization_sha256",
        "start_authorization_fingerprint",
        "champion_set_fingerprint",
        "account_fingerprint",
    ):
        _validate_sha256(
            preflight.get(field),
            field=f"Phase 8B capture-preflight {field}",
        )
    _validate_commit(
        preflight.get("capture_foundation_code_commit"),
        field="Phase 8B capture-foundation code commit",
    )

    prepared = _parse_utc_string(
        preflight.get("prepared_at_utc"),
        field="Phase 8B capture preflight timestamp",
    )
    campaign_start = _parse_utc_string(
        preflight.get("campaign_start_utc"),
        field="Phase 8B campaign start timestamp",
    )
    if prepared < campaign_start:
        raise ValueError("Phase 8B capture preflight precedes campaign start")
    if preflight.get("reader_start_semantics") != READER_START_SEMANTICS:
        raise ValueError("Phase 8B capture reader semantics drift")

    symbols = preflight.get("required_symbols")
    sessions = preflight.get("bridge_session_id_by_symbol")
    bridge_files = preflight.get("bridge_file_by_symbol")
    if not isinstance(symbols, list) or not symbols:
        raise ValueError("Phase 8B capture-preflight symbols are malformed")
    if not isinstance(sessions, Mapping) or set(sessions) != set(symbols):
        raise ValueError("Phase 8B capture-preflight session coverage mismatch")
    if not isinstance(bridge_files, Mapping) or set(bridge_files) != set(symbols):
        raise ValueError("Phase 8B capture-preflight bridge-file coverage mismatch")
    for symbol in symbols:
        _validate_sha256(
            sessions[symbol],
            field=f"Phase 8B {symbol} capture-preflight bridge session",
        )
    if len(set(sessions.values())) != len(sessions):
        raise ValueError("Phase 8B capture-preflight bridge sessions collide")

    fingerprints = preflight.get("strategy_fingerprints")
    strategies = preflight.get("strategies")
    if (
        not isinstance(fingerprints, list)
        or not fingerprints
        or len(set(fingerprints)) != len(fingerprints)
    ):
        raise ValueError(
            "Phase 8B capture-preflight strategy fingerprints are malformed"
        )
    if preflight.get("strategy_count") != len(fingerprints):
        raise ValueError("Phase 8B capture-preflight strategy count mismatch")
    if not isinstance(strategies, list) or len(strategies) != len(fingerprints):
        raise ValueError("Phase 8B capture-preflight strategies are malformed")
    if [
        row.get("fingerprint")
        for row in strategies
        if isinstance(row, Mapping)
    ] != fingerprints:
        raise ValueError("Phase 8B capture-preflight strategy identity mismatch")

    if preflight.get("capture_runtime_ready") is not True:
        raise ValueError("Phase 8B capture runtime is not ready")
    for field in (
        "live_shadow_segment_started",
        "acceptance_authorized",
        "promotion_authorized",
        "demo_order_authorized",
        "live_order_authorized",
        "broker_mutation_authorized",
        "real_money_authorized",
        "phase9_authorized",
    ):
        if preflight.get(field) is not False:
            raise ValueError(f"Phase 8B capture-preflight requires {field}=false")


def write_phase8b_capture_preflight(
    preflight: Mapping[str, object],
    campaign_dir: Path,
) -> dict[str, object]:
    validate_phase8b_capture_preflight(preflight)
    root = Path(campaign_dir)
    result_path = root / "capture-preflight.json"
    manifest_path = root / "capture-preflight-manifest.json"
    if result_path.exists() or manifest_path.exists():
        raise FileExistsError("Phase 8B capture preflight already exists")
    root.mkdir(parents=True, exist_ok=True)
    payload = _stable_json_bytes(dict(preflight))
    _atomic_write(result_path, payload)
    manifest = {
        "protocol": PHASE8B_CAPTURE_PREFLIGHT_ARTIFACT_PROTOCOL,
        "experiment_id": PHASE8B_CAPTURE_EXPERIMENT_ID,
        "capture_runtime_ready": True,
        "live_shadow_segment_started": False,
        "acceptance_authorized": False,
        "promotion_authorized": False,
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


def _bridge_record_dict(record: Phase8BBridgeRecord) -> dict[str, object]:
    common = {
        "record_type": record.record_type,
        "protocol": record.protocol,
        "bridge_session_id": record.bridge_session_id,
        "symbol": record.symbol,
        "server": record.server,
        "account_fingerprint": record.account_fingerprint,
    }
    if isinstance(record, Phase8BBridgeTickRecord):
        return common | {
            "source_time_msc": record.source_time_msc,
            "bid": record.bid,
            "ask": record.ask,
            "flags": record.flags,
        }
    if isinstance(record, Phase8BBridgeHeartbeatRecord):
        return common | {
            "bridge_emitted_time_msc": record.bridge_emitted_time_msc,
            "last_tick_time_msc": record.last_tick_time_msc,
        }
    if isinstance(record, Phase8BBridgeStartRecord):
        return common | {
            "account_mode": record.account_mode,
            "bridge_start_time_msc": record.bridge_start_time_msc,
        }
    raise TypeError("unsupported Phase 8B bridge record")


def _validate_start_identity(
    *,
    preflight: Mapping[str, object],
    start_record: Phase8BBridgeStartRecord,
) -> str:
    symbols = preflight.get("required_symbols")
    sessions = preflight.get("bridge_session_id_by_symbol")
    if not isinstance(symbols, list) or start_record.symbol not in symbols:
        raise ValueError("Phase 8B capture feed symbol is not authorized")
    if not isinstance(sessions, Mapping):
        raise ValueError("Phase 8B capture feed sessions are malformed")
    if start_record.protocol != preflight.get("connector_protocol"):
        raise ValueError("Phase 8B capture feed protocol mismatch")
    if start_record.bridge_session_id != sessions.get(start_record.symbol):
        raise ValueError("Phase 8B capture feed session mismatch")
    if start_record.account_fingerprint != preflight.get("account_fingerprint"):
        raise ValueError("Phase 8B capture feed account mismatch")
    if start_record.server != preflight.get("server"):
        raise ValueError("Phase 8B capture feed server mismatch")
    if start_record.account_mode != "DEMO":
        raise ValueError("Phase 8B capture feed must be DEMO")
    return start_record.symbol


class Phase8BCaptureFeedEnvelope:
    __slots__ = ("_preflight", "_symbol", "_validator")

    def __init__(
        self,
        *,
        preflight: Mapping[str, object],
        start_record: Phase8BBridgeStartRecord,
    ) -> None:
        validate_phase8b_capture_preflight(preflight)
        if not isinstance(start_record, Phase8BBridgeStartRecord):
            raise TypeError("Phase 8B capture feed requires BRIDGE_START")
        self._preflight = dict(preflight)
        self._symbol = _validate_start_identity(
            preflight=preflight,
            start_record=start_record,
        )
        self._validator = Phase8BBridgeSessionValidator(self._symbol)
        prepared = _parse_utc_string(
            preflight.get("prepared_at_utc"),
            field="Phase 8B capture preflight timestamp",
        )
        self._validator.accept(
            start_record,
            received_at_utc=prepared,
            receive_monotonic_ns=0,
        )

    def accept(
        self,
        record: Phase8BBridgeRecord,
        *,
        received_at_utc: datetime,
        receive_monotonic_ns: int,
    ) -> tuple[dict[str, object], Phase8BQuote | None] | None:
        quote = self._validator.accept(
            record,
            received_at_utc=received_at_utc,
            receive_monotonic_ns=receive_monotonic_ns,
        )
        if isinstance(record, Phase8BBridgeTickRecord) and quote is None:
            return None
        payload = {
            "protocol": CAPTURE_RECORD_PROTOCOL,
            "experiment_id": PHASE8B_CAPTURE_EXPERIMENT_ID,
            "capture_preflight_fingerprint": self._preflight[
                "capture_preflight_fingerprint"
            ],
            "symbol": self._symbol,
            "received_at_utc": _utc_string(
                received_at_utc,
                field="Phase 8B capture receive timestamp",
            ),
            "receive_monotonic_ns": receive_monotonic_ns,
            "bridge_record": _bridge_record_dict(record),
        }
        envelope = payload | {
            "record_fingerprint": _canonical_digest(payload)
        }
        validate_phase8b_capture_record_envelope(
            envelope,
            preflight=self._preflight,
        )
        return envelope, quote


def validate_phase8b_capture_record_envelope(
    envelope: Mapping[str, object],
    *,
    preflight: Mapping[str, object],
) -> None:
    validate_phase8b_capture_preflight(preflight)
    if envelope.get("protocol") != CAPTURE_RECORD_PROTOCOL:
        raise ValueError("Phase 8B capture-record protocol mismatch")
    if envelope.get("experiment_id") != PHASE8B_CAPTURE_EXPERIMENT_ID:
        raise ValueError("Phase 8B capture-record experiment mismatch")

    fingerprint = _validate_sha256(
        envelope.get("record_fingerprint"),
        field="Phase 8B capture-record fingerprint",
    )
    payload = dict(envelope)
    payload.pop("record_fingerprint", None)
    if fingerprint != _canonical_digest(payload):
        raise ValueError("Phase 8B capture-record fingerprint mismatch")

    if envelope.get("capture_preflight_fingerprint") != preflight.get(
        "capture_preflight_fingerprint"
    ):
        raise ValueError("Phase 8B capture-record preflight mismatch")
    symbol = envelope.get("symbol")
    symbols = preflight.get("required_symbols")
    if not isinstance(symbol, str) or not isinstance(symbols, list) or symbol not in symbols:
        raise ValueError("Phase 8B capture-record symbol mismatch")
    _parse_utc_string(
        envelope.get("received_at_utc"),
        field="Phase 8B capture-record receive timestamp",
    )
    monotonic = envelope.get("receive_monotonic_ns")
    if isinstance(monotonic, bool) or not isinstance(monotonic, int) or monotonic < 0:
        raise ValueError("Phase 8B capture-record monotonic time is invalid")

    raw = envelope.get("bridge_record")
    if not isinstance(raw, Mapping):
        raise ValueError("Phase 8B capture-record bridge payload is malformed")
    try:
        parsed = parse_phase8b_bridge_line(
            (
                json.dumps(
                    dict(raw),
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                    allow_nan=False,
                )
                + "\n"
            ).encode("utf-8")
        )
    except (Phase8BBridgeProtocolError, TypeError, ValueError) as exc:
        raise ValueError("Phase 8B capture-record bridge payload is invalid") from exc
    if isinstance(parsed, Phase8BBridgeStartRecord):
        raise ValueError("Phase 8B capture-record cannot contain BRIDGE_START")
    if parsed.symbol != symbol:
        raise ValueError("Phase 8B capture-record bridge symbol mismatch")
    sessions = preflight.get("bridge_session_id_by_symbol")
    if not isinstance(sessions, Mapping) or parsed.bridge_session_id != sessions.get(symbol):
        raise ValueError("Phase 8B capture-record bridge session mismatch")
    if parsed.protocol != preflight.get("connector_protocol"):
        raise ValueError("Phase 8B capture-record bridge protocol mismatch")
    if parsed.account_fingerprint != preflight.get("account_fingerprint"):
        raise ValueError("Phase 8B capture-record bridge account mismatch")
    if parsed.server != preflight.get("server"):
        raise ValueError("Phase 8B capture-record bridge server mismatch")


__all__ = [
    "CAPTURE_RECORD_PROTOCOL",
    "PHASE8B_CAPTURE_EXPERIMENT_ID",
    "PHASE8B_CAPTURE_FOUNDATION_READY",
    "PHASE8B_CAPTURE_PREFLIGHT_ARTIFACT_PROTOCOL",
    "PHASE8B_CAPTURE_PREFLIGHT_PROTOCOL",
    "Phase8BCaptureFeedEnvelope",
    "build_phase8b_capture_preflight",
    "validate_phase8b_capture_preflight",
    "validate_phase8b_capture_record_envelope",
    "write_phase8b_capture_preflight",
]
