from __future__ import annotations

import hashlib
import json
import math
import os
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Mapping, Protocol, Sequence

from .bridge import (
    Phase8BBridgeProtocolError,
    Phase8BBridgeRecord,
    Phase8BBridgeStartRecord,
)
from .capture import (
    Phase8BCaptureFeedEnvelope,
    validate_phase8b_capture_preflight,
)
from .runtime import (
    compile_phase8b_segment,
    replay_phase8b_segment,
    write_phase8b_segment_artifacts,
)


PHASE8B_PROSPECTIVE_EXPERIMENT_ID = "EXP-20260922-023"
PHASE8B_PROSPECTIVE_SEGMENT_PROTOCOL = "fmp-phase8b-prospective-segment-v1"
PHASE8B_PROSPECTIVE_SEGMENT_ARTIFACT_PROTOCOL = (
    "fmp-phase8b-prospective-segment-artifacts-v1"
)
PHASE8B_PROSPECTIVE_SEGMENT_CLOSED = "PHASE8B_PROSPECTIVE_SEGMENT_CLOSED"

MIN_SEGMENT_DURATION_SECONDS = 1
MAX_SEGMENT_DURATION_SECONDS = 86_400
CAPTURE_POLL_INTERVAL_SECONDS = 0.10

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
UTC = timezone.utc


class Phase8BRecordTail(Protocol):
    start_record: Phase8BBridgeStartRecord

    def read_available(self) -> tuple[Phase8BBridgeRecord, ...]: ...


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _COMMIT_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase 40-character commit SHA")
    return value


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{field} must be a lowercase SHA-256")
    return value


def _require_utc(value: datetime, *, field: str) -> None:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() != timedelta(0)
    ):
        raise ValueError(f"{field} must use UTC")


def _utc_string(value: datetime, *, field: str) -> str:
    _require_utc(value, field=field)
    return value.isoformat().replace("+00:00", "Z")


def _parse_utc(value: object, *, field: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{field} must be an ISO-8601 UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO-8601 UTC timestamp") from exc
    _require_utc(parsed, field=field)
    return parsed


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _canonical_digest(value: object) -> str:
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


def _compact_json_line(value: object) -> bytes:
    return _canonical_bytes(value) + b"\n"


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def _durable_append(handle, row: Mapping[str, object]) -> None:
    handle.write(_compact_json_line(dict(row)))
    handle.flush()
    os.fsync(handle.fileno())


def _file_record(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    return {
        "path": path.name,
        "size_bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def _duration_seconds(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("Phase 8B segment duration must be an integer")
    if not MIN_SEGMENT_DURATION_SECONDS <= value <= MAX_SEGMENT_DURATION_SECONDS:
        raise ValueError(
            "Phase 8B segment duration must be between 1 and 86400 seconds"
        )
    return value


def _validate_tail_identity(
    *,
    preflight: Mapping[str, object],
    symbol: str,
    tail: Phase8BRecordTail,
) -> None:
    start = getattr(tail, "start_record", None)
    if not isinstance(start, Phase8BBridgeStartRecord):
        raise ValueError(f"Phase 8B {symbol} prospective tail requires BRIDGE_START")
    sessions = preflight.get("bridge_session_id_by_symbol")
    if not isinstance(sessions, Mapping):
        raise ValueError("Phase 8B preflight bridge sessions are malformed")
    expected = {
        "symbol": symbol,
        "protocol": preflight.get("connector_protocol"),
        "bridge_session_id": sessions.get(symbol),
        "account_fingerprint": preflight.get("account_fingerprint"),
        "server": preflight.get("server"),
        "account_mode": "DEMO",
    }
    actual = {
        "symbol": start.symbol,
        "protocol": start.protocol,
        "bridge_session_id": start.bridge_session_id,
        "account_fingerprint": start.account_fingerprint,
        "server": start.server,
        "account_mode": start.account_mode,
    }
    if actual != expected:
        raise ValueError(f"Phase 8B {symbol} prospective bridge identity mismatch")


def _build_segment_id(
    *,
    preflight_fingerprint: str,
    started_at_utc: datetime,
    code_commit: str,
) -> str:
    return _canonical_digest(
        {
            "capture_preflight_fingerprint": preflight_fingerprint,
            "segment_started_at_utc": _utc_string(
                started_at_utc,
                field="Phase 8B prospective segment start",
            ),
            "segment_code_commit": code_commit,
        }
    )


def _write_operational_event(
    handle,
    *,
    event: str,
    timestamp_utc: datetime,
    details: Mapping[str, object] | None = None,
) -> None:
    row: dict[str, object] = {
        "event": event,
        "timestamp_utc": _utc_string(
            timestamp_utc,
            field="Phase 8B operational event timestamp",
        ),
    }
    if details:
        row["details"] = dict(details)
    _durable_append(handle, row)


def validate_phase8b_prospective_segment(
    segment: Mapping[str, object],
) -> None:
    if segment.get("protocol") != PHASE8B_PROSPECTIVE_SEGMENT_PROTOCOL:
        raise ValueError("Phase 8B prospective-segment protocol mismatch")
    if segment.get("experiment_id") != PHASE8B_PROSPECTIVE_EXPERIMENT_ID:
        raise ValueError("Phase 8B prospective-segment experiment mismatch")
    if segment.get("outcome") != PHASE8B_PROSPECTIVE_SEGMENT_CLOSED:
        raise ValueError("Phase 8B prospective-segment outcome mismatch")
    if segment.get("prospective_evidence") is not True:
        raise ValueError("Phase 8B prospective segment must be prospective")
    if segment.get("prospective_segment_closed") is not True:
        raise ValueError("Phase 8B prospective segment must be closed")
    if segment.get("replay_match") is not True:
        raise ValueError("Phase 8B prospective segment requires replay match")

    for field in (
        "segment_id",
        "capture_preflight_fingerprint",
        "capture_records_sha256",
        "audit_sha256",
        "operational_events_sha256",
        "runtime_segment_fingerprint",
        "replay_fingerprint",
        "prospective_segment_fingerprint",
    ):
        _validate_sha256(
            segment.get(field),
            field=f"Phase 8B prospective segment {field}",
        )
    _validate_commit(
        segment.get("segment_code_commit"),
        field="Phase 8B prospective segment code commit",
    )
    start = _parse_utc(
        segment.get("segment_started_at_utc"),
        field="Phase 8B prospective segment start",
    )
    end = _parse_utc(
        segment.get("segment_ended_at_utc"),
        field="Phase 8B prospective segment end",
    )
    if end < start:
        raise ValueError("Phase 8B prospective segment end precedes start")

    duration = segment.get("duration_seconds")
    _duration_seconds(duration)
    for field in ("capture_record_count", "audit_row_count"):
        value = segment.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"Phase 8B prospective segment {field} is invalid")
    if segment.get("capture_record_count") != segment.get("audit_row_count"):
        raise ValueError("Phase 8B prospective segment audit coverage mismatch")

    for field in (
        "acceptance_authorized",
        "promotion_authorized",
        "demo_order_authorized",
        "live_order_authorized",
        "broker_mutation_authorized",
        "real_money_authorized",
        "phase9_execution_authorized",
    ):
        if segment.get(field) is not False:
            raise ValueError(
                f"Phase 8B prospective segment requires {field}=false"
            )

    fingerprint = str(segment["prospective_segment_fingerprint"])
    payload = dict(segment)
    payload.pop("prospective_segment_fingerprint", None)
    if fingerprint != _canonical_digest(payload):
        raise ValueError("Phase 8B prospective segment fingerprint mismatch")


def capture_phase8b_prospective_segment(
    *,
    preflight: Mapping[str, object],
    bridge_tails: Mapping[str, Phase8BRecordTail],
    code_commit: str,
    duration_seconds: int,
    segments_root: Path,
    utc_now: Callable[[], datetime] = lambda: datetime.now(UTC),
    monotonic_ns: Callable[[], int] = time.monotonic_ns,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, object]:
    validate_phase8b_capture_preflight(preflight)
    commit = _validate_commit(
        code_commit,
        field="Phase 8B prospective capture code commit",
    )
    duration = _duration_seconds(duration_seconds)

    raw_symbols = preflight.get("required_symbols")
    if not isinstance(raw_symbols, list) or not raw_symbols:
        raise ValueError("Phase 8B prospective required symbols are malformed")
    symbols = tuple(str(item) for item in raw_symbols)
    if set(bridge_tails) != set(symbols):
        raise ValueError("Phase 8B prospective bridge coverage mismatch")
    for symbol in symbols:
        _validate_tail_identity(
            preflight=preflight,
            symbol=symbol,
            tail=bridge_tails[symbol],
        )

    started_at = utc_now()
    _require_utc(started_at, field="Phase 8B prospective segment start")
    preflight_fingerprint = _validate_sha256(
        preflight.get("capture_preflight_fingerprint"),
        field="Phase 8B capture-preflight fingerprint",
    )
    segment_id = _build_segment_id(
        preflight_fingerprint=preflight_fingerprint,
        started_at_utc=started_at,
        code_commit=commit,
    )
    root = Path(segments_root)
    segment_dir = root / segment_id
    segment_dir.mkdir(parents=True, exist_ok=False)

    start_payload = {
        "protocol": "fmp-phase8b-prospective-segment-start-v1",
        "experiment_id": PHASE8B_PROSPECTIVE_EXPERIMENT_ID,
        "segment_id": segment_id,
        "capture_preflight_fingerprint": preflight_fingerprint,
        "segment_code_commit": commit,
        "segment_started_at_utc": _utc_string(
            started_at,
            field="Phase 8B prospective segment start",
        ),
        "duration_seconds": duration,
        "required_symbols": list(symbols),
        "reader_start_semantics": preflight["reader_start_semantics"],
        "acceptance_authorized": False,
        "promotion_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_execution_authorized": False,
    }
    _atomic_write(segment_dir / "start.json", _stable_json_bytes(start_payload))

    capture_path = segment_dir / "capture-records.jsonl"
    audit_path = segment_dir / "audit.jsonl"
    events_path = segment_dir / "operational-events.jsonl"

    feeds = {
        symbol: Phase8BCaptureFeedEnvelope(
            preflight=preflight,
            start_record=bridge_tails[symbol].start_record,
        )
        for symbol in symbols
    }
    captured: list[dict[str, object]] = []
    audit_count = 0
    start_ns = monotonic_ns()

    with (
        capture_path.open("xb") as capture_handle,
        audit_path.open("xb") as audit_handle,
        events_path.open("xb") as events_handle,
    ):
        _write_operational_event(
            events_handle,
            event="SEGMENT_STARTED",
            timestamp_utc=started_at,
            details={"segment_id": segment_id},
        )
        try:
            while True:
                loop_ns = monotonic_ns()
                if loop_ns - start_ns >= duration * 1_000_000_000:
                    break
                for symbol in sorted(symbols):
                    records = bridge_tails[symbol].read_available()
                    for record in records:
                        received_at = utc_now()
                        _require_utc(
                            received_at,
                            field="Phase 8B prospective record receive timestamp",
                        )
                        received_ns = monotonic_ns()
                        accepted = feeds[symbol].accept(
                            record,
                            received_at_utc=received_at,
                            receive_monotonic_ns=received_ns,
                        )
                        if accepted is None:
                            continue
                        envelope, _quote = accepted
                        _durable_append(capture_handle, envelope)
                        completed_ns = monotonic_ns()
                        if completed_ns < received_ns:
                            raise ValueError(
                                "Phase 8B prospective monotonic clock regressed"
                            )
                        latency_ms = (completed_ns - received_ns) / 1_000_000
                        if not math.isfinite(latency_ms) or latency_ms < 0:
                            raise ValueError(
                                "Phase 8B prospective processing latency is invalid"
                            )
                        audit_row = {
                            "record_fingerprint": envelope["record_fingerprint"],
                            "received_at_utc": envelope["received_at_utc"],
                            "receive_monotonic_ns": received_ns,
                            "append_completed_monotonic_ns": completed_ns,
                            "processing_latency_ms": latency_ms,
                        }
                        _durable_append(audit_handle, audit_row)
                        captured.append(dict(envelope))
                        audit_count += 1
                sleep(CAPTURE_POLL_INTERVAL_SECONDS)
        except Exception as exc:
            event_time = utc_now()
            _require_utc(
                event_time,
                field="Phase 8B prospective protocol-failure timestamp",
            )
            try:
                _write_operational_event(
                    events_handle,
                    event="PROTOCOL_FAILURE",
                    timestamp_utc=event_time,
                    details={"error_type": type(exc).__name__},
                )
            finally:
                raise

        ended_at = utc_now()
        _require_utc(ended_at, field="Phase 8B prospective segment end")
        _write_operational_event(
            events_handle,
            event="SEGMENT_DURATION_REACHED",
            timestamp_utc=ended_at,
            details={"duration_seconds": duration},
        )

    runtime_dir = segment_dir / "runtime"
    runtime_segment = compile_phase8b_segment(
        preflight=preflight,
        capture_records=captured,
        code_commit=commit,
    )
    replay = replay_phase8b_segment(
        expected_segment=runtime_segment,
        preflight=preflight,
        capture_records=captured,
    )
    if replay.get("match") is not True:
        raise ValueError("Phase 8B prospective segment replay mismatch")
    write_phase8b_segment_artifacts(
        segment=runtime_segment,
        replay=replay,
        out_dir=runtime_dir,
    )

    capture_record = _file_record(capture_path)
    audit_record = _file_record(audit_path)
    events_record = _file_record(events_path)
    replay_fingerprint = _canonical_digest(replay)
    payload = {
        "protocol": PHASE8B_PROSPECTIVE_SEGMENT_PROTOCOL,
        "experiment_id": PHASE8B_PROSPECTIVE_EXPERIMENT_ID,
        "outcome": PHASE8B_PROSPECTIVE_SEGMENT_CLOSED,
        "segment_id": segment_id,
        "capture_preflight_fingerprint": preflight_fingerprint,
        "segment_code_commit": commit,
        "segment_started_at_utc": _utc_string(
            started_at,
            field="Phase 8B prospective segment start",
        ),
        "segment_ended_at_utc": _utc_string(
            ended_at,
            field="Phase 8B prospective segment end",
        ),
        "duration_seconds": duration,
        "required_symbols": list(symbols),
        "capture_record_count": len(captured),
        "capture_records_sha256": capture_record["sha256"],
        "audit_row_count": audit_count,
        "audit_sha256": audit_record["sha256"],
        "operational_events_sha256": events_record["sha256"],
        "runtime_segment_fingerprint": runtime_segment["segment_fingerprint"],
        "replay_fingerprint": replay_fingerprint,
        "replay_match": True,
        "prospective_evidence": True,
        "prospective_segment_closed": True,
        "acceptance_authorized": False,
        "promotion_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "broker_mutation_authorized": False,
        "real_money_authorized": False,
        "phase9_execution_authorized": False,
    }
    result = payload | {
        "prospective_segment_fingerprint": _canonical_digest(payload)
    }
    validate_phase8b_prospective_segment(result)
    result_path = segment_dir / "prospective-segment.json"
    _atomic_write(result_path, _stable_json_bytes(result))

    artifacts = [
        _file_record(segment_dir / "start.json"),
        capture_record,
        audit_record,
        events_record,
        _file_record(runtime_dir / "segment.json"),
        _file_record(runtime_dir / "replay.json"),
        _file_record(runtime_dir / "manifest.json"),
        _file_record(result_path),
    ]
    manifest = {
        "protocol": PHASE8B_PROSPECTIVE_SEGMENT_ARTIFACT_PROTOCOL,
        "experiment_id": PHASE8B_PROSPECTIVE_EXPERIMENT_ID,
        "segment_id": segment_id,
        "prospective_segment_closed": True,
        "replay_match": True,
        "acceptance_authorized": False,
        "promotion_authorized": False,
        "artifacts": artifacts,
    }
    _atomic_write(
        segment_dir / "manifest.json",
        _stable_json_bytes(manifest),
    )
    return result


__all__ = [
    "CAPTURE_POLL_INTERVAL_SECONDS",
    "MAX_SEGMENT_DURATION_SECONDS",
    "MIN_SEGMENT_DURATION_SECONDS",
    "PHASE8B_PROSPECTIVE_EXPERIMENT_ID",
    "PHASE8B_PROSPECTIVE_SEGMENT_ARTIFACT_PROTOCOL",
    "PHASE8B_PROSPECTIVE_SEGMENT_CLOSED",
    "PHASE8B_PROSPECTIVE_SEGMENT_PROTOCOL",
    "capture_phase8b_prospective_segment",
    "validate_phase8b_prospective_segment",
]
