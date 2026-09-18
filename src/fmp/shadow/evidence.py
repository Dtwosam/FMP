from __future__ import annotations

import hashlib
import json
import math
import os
import re
from dataclasses import fields, is_dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Mapping

from fmp.risk import RiskConfig

from .contracts import (
    FMP_SYMBOL,
    MT5_ALLOWED_SERVERS,
    MT5_BRIDGE_FILE,
    MT5_BRIDGE_PROTOCOL,
    MT5_PROVIDER,
    MT5_TRANSPORT,
    SLIPPAGE_SCENARIOS,
)


EVIDENCE_PROTOCOL = "fmp-phase8-shadow-evidence-v2"
CONNECTOR_PROTOCOL = MT5_BRIDGE_PROTOCOL
PHASE7_CHECKPOINT_TAG = "fmp-v1-phase7-walk-forward"
PHASE7_CHECKPOINT_SHA = "b6fb0176555b071fef6d1070edf3407b03cd60c9"
PHASE7_EXPERIMENT = "EXP-20260915-008"
PHASE7_OUTCOME = "PASS / PROMOTE"
_STREAM_FILES = (
    "raw.jsonl",
    "normalized.jsonl",
    "bars.jsonl",
    "decisions.jsonl",
    "scenarios.jsonl",
    "operational.jsonl",
)
_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_SENSITIVE_KEY = re.compile(
    r"(?:authorization|token|secret|password|cookie|account_?id|accountid|request_?headers?|headers?)",
    re.IGNORECASE,
)
_BEARER = re.compile(r"(?i)(?:authorization\s*:\s*)?bearer\s+[^\s;,]+")
_ACCOUNT = re.compile(r"\b\d{3}-\d{3}-\d+(?:-\d+)+\b")


def _require_utc(value: datetime, *, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError(f"{field_name} must use UTC")


def _validate_code_commit(value: str, *, field_name: str = "code_commit") -> None:
    if not isinstance(value, str) or _HEX40.fullmatch(value) is None:
        raise ValueError(f"{field_name} must be a lowercase 40-character commit SHA")


def _validate_sha256(value: str, *, field_name: str) -> None:
    if not isinstance(value, str) or _HEX64.fullmatch(value) is None:
        raise ValueError(f"{field_name} must be a lowercase SHA-256")


def _validate_server(value: str) -> None:
    if not isinstance(value, str) or value not in MT5_ALLOWED_SERVERS:
        raise ValueError("server must be an approved FP Markets MT5 demo server")


def _redact_string(value: str) -> str:
    redacted = _BEARER.sub("[REDACTED]", value)
    return _ACCOUNT.sub("[REDACTED_ACCOUNT]", redacted)


def _sanitize(value: object) -> object:
    if isinstance(value, Mapping):
        clean: dict[str, object] = {}
        for key, item in value.items():
            key_text = str(key)
            clean[key_text] = "[REDACTED]" if _SENSITIVE_KEY.search(key_text) else _sanitize(item)
        return clean
    if isinstance(value, (tuple, list)):
        return [_sanitize(item) for item in value]
    if isinstance(value, str):
        return _redact_string(value)
    return value


def _jsonable(value: object) -> object:
    if is_dataclass(value) and not isinstance(value, type):
        return {item.name: _jsonable(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        _require_utc(value, field_name="evidence datetime")
        return value.isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Phase 8 evidence requires finite JSON numbers")
        return value
    if value is None or isinstance(value, (str, bool, int)):
        return value
    raise TypeError(f"unsupported Phase 8 evidence value: {type(value).__name__}")


def _stable_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            _jsonable(_sanitize(value)),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _build_manifest(
    root: Path,
    *,
    code_commit: str,
    bridge_source_commit: str,
    bridge_session_id: str,
    server: str,
    account_fingerprint_sha256: str,
    run_start_utc: datetime,
    run_end_utc: datetime,
    replay_result_digest: str,
) -> dict[str, object]:
    _validate_code_commit(code_commit)
    _validate_code_commit(bridge_source_commit, field_name="bridge_source_commit")
    _validate_sha256(bridge_session_id, field_name="bridge_session_id")
    _validate_server(server)
    _validate_sha256(account_fingerprint_sha256, field_name="account_fingerprint_sha256")
    _validate_sha256(replay_result_digest, field_name="replay_result_digest")
    _require_utc(run_start_utc, field_name="run_start_utc")
    _require_utc(run_end_utc, field_name="run_end_utc")
    if run_end_utc < run_start_utc:
        raise ValueError("run_end_utc cannot precede run_start_utc")
    missing = [name for name in _STREAM_FILES if not (root / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Phase 8 evidence stream missing: {missing[0]}")

    return {
        "protocol": EVIDENCE_PROTOCOL,
        "code_commit": code_commit,
        "phase7_checkpoint_tag": PHASE7_CHECKPOINT_TAG,
        "phase7_checkpoint_sha": PHASE7_CHECKPOINT_SHA,
        "phase7_experiment": PHASE7_EXPERIMENT,
        "phase7_outcome": PHASE7_OUTCOME,
        "strategy": {
            "id": "session_breakout",
            "symbol": "USDJPY",
            "timeframe": "15m",
            "buffer_pips": 5,
            "target_range_multiple": 1.5,
        },
        "connector_protocol": CONNECTOR_PROTOCOL,
        "provider": MT5_PROVIDER,
        "provider_instrument": FMP_SYMBOL,
        "transport": MT5_TRANSPORT,
        "bridge_file": MT5_BRIDGE_FILE,
        "allowed_servers": list(MT5_ALLOWED_SERVERS),
        "bridge_session_id": bridge_session_id,
        "server": server,
        "account_fingerprint_sha256": account_fingerprint_sha256,
        "bridge_source_commit": bridge_source_commit,
        "slippage_scenarios": list(SLIPPAGE_SCENARIOS),
        "risk_policy": RiskConfig().to_config(),
        "run_start_utc": run_start_utc,
        "run_end_utc": run_end_utc,
        "file_sha256": {name: _file_sha256(root / name) for name in _STREAM_FILES},
        "replay_result_digest": replay_result_digest,
    }


def finalize_existing_segment(
    root: Path,
    *,
    code_commit: str,
    bridge_source_commit: str,
    bridge_session_id: str,
    server: str,
    account_fingerprint_sha256: str,
    run_start_utc: datetime,
    run_end_utc: datetime,
    replay_result_digest: str,
) -> dict[str, object]:
    root = Path(root)
    manifest = _build_manifest(
        root,
        code_commit=code_commit,
        bridge_source_commit=bridge_source_commit,
        bridge_session_id=bridge_session_id,
        server=server,
        account_fingerprint_sha256=account_fingerprint_sha256,
        run_start_utc=run_start_utc,
        run_end_utc=run_end_utc,
        replay_result_digest=replay_result_digest,
    )
    manifest_path = root / "manifest.json"
    expected_bytes = _stable_json_bytes(manifest)
    if manifest_path.exists():
        if manifest_path.read_bytes() != expected_bytes:
            raise ValueError("existing Phase 8 manifest conflicts with replay-verified segment")
    else:
        _atomic_write(manifest_path, expected_bytes)
    return _jsonable(manifest)  # type: ignore[return-value]


class EvidenceWriter:
    def __init__(
        self,
        root: Path,
        *,
        code_commit: str,
        bridge_source_commit: str,
        bridge_session_id: str,
        server: str,
        account_fingerprint_sha256: str,
        run_start_utc: datetime,
    ) -> None:
        _validate_code_commit(code_commit)
        _validate_code_commit(bridge_source_commit, field_name="bridge_source_commit")
        _validate_sha256(bridge_session_id, field_name="bridge_session_id")
        _validate_server(server)
        _validate_sha256(account_fingerprint_sha256, field_name="account_fingerprint_sha256")
        _require_utc(run_start_utc, field_name="run_start_utc")

        self.root = Path(root)
        self.code_commit = code_commit
        self.bridge_source_commit = bridge_source_commit
        self.bridge_session_id = bridge_session_id
        self.server = server
        self.account_fingerprint_sha256 = account_fingerprint_sha256
        self.run_start_utc = run_start_utc
        self._sealed = False
        self.root.mkdir(parents=True, exist_ok=True)
        for name in (*_STREAM_FILES, "manifest.json"):
            if (self.root / name).exists():
                raise FileExistsError(f"Phase 8 evidence path already exists: {name}")
        for name in _STREAM_FILES:
            (self.root / name).touch(exist_ok=False)

    def _append(self, filename: str, record: object) -> None:
        if self._sealed:
            raise RuntimeError("Phase 8 evidence writer is finalized")
        if filename not in _STREAM_FILES:
            raise ValueError("unsupported Phase 8 evidence stream")
        with (self.root / filename).open("ab") as handle:
            handle.write(_stable_json_bytes(record))
            handle.flush()
            os.fsync(handle.fileno())

    def append_raw(
        self,
        provider_object: Mapping[str, object],
        *,
        received_at_utc: datetime,
        receive_monotonic_ns: int,
    ) -> None:
        _require_utc(received_at_utc, field_name="received_at_utc")
        if (
            isinstance(receive_monotonic_ns, bool)
            or not isinstance(receive_monotonic_ns, int)
            or receive_monotonic_ns < 0
        ):
            raise ValueError("receive_monotonic_ns must be a non-negative integer")
        if not isinstance(provider_object, Mapping):
            raise TypeError("provider_object must be a mapping")
        self._append(
            "raw.jsonl",
            {
                "provider_object": provider_object,
                "received_at_utc": received_at_utc,
                "receive_monotonic_ns": receive_monotonic_ns,
            },
        )

    def append_normalized(self, event: object) -> None:
        self._append("normalized.jsonl", event)

    def append_bar(self, timeframe: str, bar: object) -> None:
        if timeframe not in {"1m", "15m"}:
            raise ValueError("Phase 8 evidence supports only 1m or 15m bars")
        self._append("bars.jsonl", {"timeframe": timeframe, "bar": bar})

    def append_decision(self, record: Mapping[str, object]) -> None:
        self._append("decisions.jsonl", record)

    def append_scenario(self, record: Mapping[str, object]) -> None:
        self._append("scenarios.jsonl", record)

    def append_operational(self, record: Mapping[str, object]) -> None:
        self._append("operational.jsonl", record)

    def finalize(
        self,
        *,
        run_end_utc: datetime,
        replay_result_digest: str,
    ) -> dict[str, object]:
        if self._sealed:
            raise RuntimeError("Phase 8 evidence writer is finalized")
        manifest = _build_manifest(
            self.root,
            code_commit=self.code_commit,
            bridge_source_commit=self.bridge_source_commit,
            bridge_session_id=self.bridge_session_id,
            server=self.server,
            account_fingerprint_sha256=self.account_fingerprint_sha256,
            run_start_utc=self.run_start_utc,
            run_end_utc=run_end_utc,
            replay_result_digest=replay_result_digest,
        )
        _atomic_write(self.root / "manifest.json", _stable_json_bytes(manifest))
        self._sealed = True
        return _jsonable(manifest)  # type: ignore[return-value]


__all__ = [
    "CONNECTOR_PROTOCOL",
    "EVIDENCE_PROTOCOL",
    "EvidenceWriter",
    "PHASE7_CHECKPOINT_SHA",
    "PHASE7_CHECKPOINT_TAG",
    "PHASE7_EXPERIMENT",
    "PHASE7_OUTCOME",
    "finalize_existing_segment",
]
