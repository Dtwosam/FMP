from __future__ import annotations

import hashlib
import json
import math
import os
import re
from dataclasses import fields, is_dataclass
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Mapping, Sequence

from fmp.backtest.costs import ZeroCommission, ZeroFinancing
from fmp.data.phase2.schema import CANONICAL_SCHEMA_VERSION
from fmp.risk import RiskConfig

from .contracts import (
    EXPERIMENT_ID,
    FROZEN_CANDIDATES,
    PHASE6_CHECKPOINT_SHA,
    REQUESTED_RISK_FRACTION,
    SLIPPAGE_SCENARIOS,
    STARTING_EQUITY_USD,
    STAGE1_WINDOW,
    STAGE2_WINDOWS,
    USDJPY_PHASE2_ARTIFACT_ID,
    USDJPY_PHASE2_ZIP_SHA256,
    USDJPY_PROCESSED_MANIFEST_SHA256,
)
from .gates import GateResult, aggregate_windows, stage1_gate, stage2_gate


PHASE7_ARTIFACT_PROTOCOL = "fmp-phase7-walk-forward-artifacts-v1"
EVIDENCE_CONTRACT_VERSION = 1
PHASE6_CHECKPOINT_TAG = "fmp-v1-phase6-models"
STRATEGY_VERSION = 1
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _jsonable(value: object) -> object:
    if is_dataclass(value) and not isinstance(value, type):
        return {item.name: _jsonable(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() != timedelta(0):
            raise ValueError("Phase 7 evidence datetime must use UTC")
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
            raise ValueError("Phase 7 evidence requires finite JSON numbers")
        return value
    if value is None or isinstance(value, (str, bool, int)):
        return value
    raise TypeError(f"unsupported Phase 7 evidence value: {type(value).__name__}")


def _stable_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            _jsonable(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _atomic_write(path: Path, data: bytes) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, destination)


def _artifact_record(path: Path) -> dict[str, object]:
    data = Path(path).read_bytes()
    return {
        "path": Path(path).name,
        "sha256": hashlib.sha256(data).hexdigest(),
        "size_bytes": len(data),
    }


def _candidate_identity(candidate_id: str) -> dict[str, object]:
    try:
        candidate = FROZEN_CANDIDATES[candidate_id]
    except (KeyError, TypeError) as exc:
        raise ValueError(f"unsupported frozen Phase 7 candidate: {candidate_id!r}") from exc
    return {
        "candidate_id": candidate.candidate_id,
        "strategy_version": STRATEGY_VERSION,
        "symbol": candidate.symbol,
        "timeframe": candidate.timeframe,
        "parameters": dict(candidate.parameters),
    }


def _base_identity(candidate_id: str, code_commit: str) -> dict[str, object]:
    if not isinstance(code_commit, str) or not code_commit.strip():
        raise ValueError("Phase 7 evidence code_commit must be non-empty")
    return {
        "experiment_id": EXPERIMENT_ID,
        "evidence_contract_version": EVIDENCE_CONTRACT_VERSION,
        "code_commit": code_commit,
        "phase6_checkpoint_tag": PHASE6_CHECKPOINT_TAG,
        "phase6_checkpoint_sha": PHASE6_CHECKPOINT_SHA,
        "phase2_artifact_id": USDJPY_PHASE2_ARTIFACT_ID,
        "phase2_zip_sha256": USDJPY_PHASE2_ZIP_SHA256,
        "processed_manifest_sha256": USDJPY_PROCESSED_MANIFEST_SHA256,
        "canonical_schema_version": CANONICAL_SCHEMA_VERSION,
        "candidate": _candidate_identity(candidate_id),
        "starting_equity_usd": STARTING_EQUITY_USD,
        "requested_risk_fraction": REQUESTED_RISK_FRACTION,
        "risk_policy": dict(RiskConfig().to_config()),
        "slippage_scenarios": list(SLIPPAGE_SCENARIOS),
        "commission_model": dict(ZeroCommission().to_config()),
        "financing_model": dict(ZeroFinancing().to_config()),
    }


def _utc_range(start: datetime, end: datetime) -> dict[str, str]:
    if start.tzinfo is None or start.utcoffset() != timedelta(0):
        raise ValueError("Phase 7 evidence range start must use UTC")
    if end.tzinfo is None or end.utcoffset() != timedelta(0):
        raise ValueError("Phase 7 evidence range end must use UTC")
    if start >= end:
        raise ValueError("Phase 7 evidence range start must precede end")
    return {
        "start_utc": start.isoformat().replace("+00:00", "Z"),
        "end_exclusive_utc": end.isoformat().replace("+00:00", "Z"),
    }


def _date_window_range(window) -> dict[str, str]:
    start = datetime(window.start.year, window.start.month, window.start.day, tzinfo=timezone.utc)
    end = datetime(
        window.end_exclusive.year,
        window.end_exclusive.month,
        window.end_exclusive.day,
        tzinfo=timezone.utc,
    )
    return _utc_range(start, end)


def _result_row(value: object) -> dict[str, object]:
    required = (
        "candidate_id",
        "window_name",
        "slippage_pips",
        "candidate_count",
        "scored_candidate_count",
        "directional_candidate_count",
        "trade_count",
        "net_pnl_usd",
        "net_return",
        "expectancy_usd",
        "gross_profit_usd",
        "gross_loss_usd",
        "profit_factor",
        "max_drawdown_fraction",
        "warmup_range",
        "opened_partition_keys",
        "scored_start_utc",
        "scored_end_utc",
        "refit_status",
    )
    missing = [name for name in required if not hasattr(value, name)]
    if missing:
        raise ValueError(f"Phase 7 window evidence is missing fields: {missing}")
    warmup = getattr(value, "warmup_range")
    if not isinstance(warmup, (tuple, list)) or len(warmup) != 2:
        raise ValueError("Phase 7 warmup_range must contain exact start/end")
    opened = getattr(value, "opened_partition_keys")
    if not isinstance(opened, (tuple, list)) or not opened:
        raise ValueError("Phase 7 opened partition accounting must be non-empty")
    return {
        "candidate_id": getattr(value, "candidate_id"),
        "window_name": getattr(value, "window_name"),
        "slippage_pips": getattr(value, "slippage_pips"),
        "candidate_count": getattr(value, "candidate_count"),
        "scored_candidate_count": getattr(value, "scored_candidate_count"),
        "directional_candidate_count": getattr(value, "directional_candidate_count"),
        "trade_count": getattr(value, "trade_count"),
        "net_pnl_usd": getattr(value, "net_pnl_usd"),
        "net_return": getattr(value, "net_return"),
        "expectancy_usd": getattr(value, "expectancy_usd"),
        "gross_profit_usd": getattr(value, "gross_profit_usd"),
        "gross_loss_usd": getattr(value, "gross_loss_usd"),
        "profit_factor": getattr(value, "profit_factor"),
        "max_drawdown_fraction": getattr(value, "max_drawdown_fraction"),
        "warmup_range": _utc_range(warmup[0], warmup[1]),
        "opened_partition_keys": list(opened),
        "scored_range": _utc_range(
            getattr(value, "scored_start_utc"), getattr(value, "scored_end_utc")
        ),
        "refit_status": getattr(value, "refit_status"),
    }


def _gate_payload(gate: GateResult) -> dict[str, object]:
    return {"passed": gate.passed, "criteria": dict(gate.criteria)}


def _require_matching_gate(supplied: GateResult, expected: GateResult) -> None:
    if supplied.passed != expected.passed or dict(supplied.criteria) != dict(expected.criteria):
        raise ValueError("Phase 7 supplied gate does not match recomputed gate")


def _validate_stage1_rows(candidate_id: str, results_by_slippage: Mapping[float, object]) -> None:
    if set(results_by_slippage) != set(SLIPPAGE_SCENARIOS):
        raise ValueError("Phase 7 Stage 1 evidence requires exact slippage scenarios")
    for slippage in SLIPPAGE_SCENARIOS:
        row = results_by_slippage[slippage]
        if getattr(row, "candidate_id", None) != candidate_id:
            raise ValueError("Phase 7 Stage 1 candidate identity mismatch")
        if getattr(row, "window_name", None) != STAGE1_WINDOW.name:
            raise ValueError("Phase 7 Stage 1 window identity mismatch")
        if float(getattr(row, "slippage_pips", -1.0)) != slippage:
            raise ValueError("Phase 7 Stage 1 slippage identity mismatch")


def _validate_stage2_rows(candidate_id: str, results_by_slippage: Mapping[float, Sequence[object]]) -> None:
    if set(results_by_slippage) != set(SLIPPAGE_SCENARIOS):
        raise ValueError("Phase 7 Stage 2 evidence requires exact slippage scenarios")
    expected_names = tuple(window.name for window in STAGE2_WINDOWS)
    for slippage in SLIPPAGE_SCENARIOS:
        rows = tuple(results_by_slippage[slippage])
        if tuple(getattr(row, "window_name", None) for row in rows) != expected_names:
            raise ValueError("Phase 7 Stage 2 window identity/order mismatch")
        for row in rows:
            if getattr(row, "candidate_id", None) != candidate_id:
                raise ValueError("Phase 7 Stage 2 candidate identity mismatch")
            if float(getattr(row, "slippage_pips", -1.0)) != slippage:
                raise ValueError("Phase 7 Stage 2 slippage identity mismatch")


def _validate_stage1_identity(value: Mapping[str, object], candidate_id: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError("Phase 7 Stage 2 requires Stage 1 identity evidence")
    identity = dict(value)
    if identity.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("Phase 7 Stage 1 experiment identity mismatch")
    if identity.get("candidate_id") != candidate_id:
        raise ValueError("Phase 7 Stage 1 candidate identity mismatch")
    if identity.get("status") != "STAGE1_PASS":
        raise ValueError("Phase 7 Stage 2 requires STAGE1_PASS")
    code_commit = identity.get("code_commit")
    if not isinstance(code_commit, str) or not code_commit.strip():
        raise ValueError("Phase 7 Stage 1 code identity is missing")
    if identity.get("phase6_checkpoint_sha") != PHASE6_CHECKPOINT_SHA:
        raise ValueError("Phase 7 Stage 1 Phase 6 checkpoint identity mismatch")
    if identity.get("processed_manifest_sha256") != USDJPY_PROCESSED_MANIFEST_SHA256:
        raise ValueError("Phase 7 Stage 1 processed manifest identity mismatch")
    manifest_sha = identity.get("manifest_sha256")
    if not isinstance(manifest_sha, str) or _HEX64.fullmatch(manifest_sha) is None:
        raise ValueError("Phase 7 Stage 1 manifest identity must be a lowercase SHA-256")
    return identity


def write_stage1_evidence(
    *,
    out_dir: Path,
    candidate_id: str,
    code_commit: str,
    results_by_slippage: Mapping[float, object],
    gate: GateResult,
) -> dict[str, object]:
    _candidate_identity(candidate_id)
    _validate_stage1_rows(candidate_id, results_by_slippage)
    expected_gate = stage1_gate(results_by_slippage)
    _require_matching_gate(gate, expected_gate)

    base = _base_identity(candidate_id, code_commit)
    status = "STAGE1_PASS" if gate.passed else "STAGE1_REJECT"
    serialized_results = {
        f"{slippage:.1f}": _result_row(results_by_slippage[slippage])
        for slippage in SLIPPAGE_SCENARIOS
    }
    stage1_payload = {
        **base,
        "protocol": PHASE7_ARTIFACT_PROTOCOL,
        "stage": "stage1",
        "status": status,
        "scored_range": _date_window_range(STAGE1_WINDOW),
        "results_by_slippage": serialized_results,
        "gate": _gate_payload(gate),
    }
    result_payload = {
        **base,
        "protocol": PHASE7_ARTIFACT_PROTOCOL,
        "stage": "stage1",
        "status": status,
        "candidate_statuses": {candidate_id: "PASS" if gate.passed else "REJECT"},
        "stage2_authorized": gate.passed,
        "gate": _gate_payload(gate),
    }

    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    _atomic_write(root / "stage1.json", _stable_json_bytes(stage1_payload))
    _atomic_write(root / "result.json", _stable_json_bytes(result_payload))

    manifest = {
        **base,
        "protocol": PHASE7_ARTIFACT_PROTOCOL,
        "stage": "stage1",
        "status": status,
        "artifacts": [
            _artifact_record(root / name) for name in ("result.json", "stage1.json")
        ],
    }
    _atomic_write(root / "manifest.json", _stable_json_bytes(manifest))
    return manifest


def write_stage2_evidence(
    *,
    out_dir: Path,
    candidate_id: str,
    code_commit: str,
    results_by_slippage: Mapping[float, Sequence[object]],
    gate: GateResult,
    stage1_identity: Mapping[str, object],
) -> dict[str, object]:
    _candidate_identity(candidate_id)
    _validate_stage2_rows(candidate_id, results_by_slippage)
    verified_stage1 = _validate_stage1_identity(stage1_identity, candidate_id)
    expected_gate = stage2_gate(results_by_slippage)
    _require_matching_gate(gate, expected_gate)

    base = _base_identity(candidate_id, code_commit)
    status = "PHASE7_PROMOTE_TO_SHADOW_DESIGN" if gate.passed else "PHASE7_COMPLETE_REJECT"
    windows_by_slippage = {
        f"{slippage:.1f}": [_result_row(row) for row in results_by_slippage[slippage]]
        for slippage in SLIPPAGE_SCENARIOS
    }
    aggregate_by_slippage = {
        f"{slippage:.1f}": _jsonable(aggregate_windows(results_by_slippage[slippage]))
        for slippage in SLIPPAGE_SCENARIOS
    }
    windows_payload = {
        **base,
        "protocol": PHASE7_ARTIFACT_PROTOCOL,
        "stage": "stage2",
        "status": status,
        "stage1_identity": verified_stage1,
        "windows_by_slippage": windows_by_slippage,
        "aggregate_by_slippage": aggregate_by_slippage,
        "gate": _gate_payload(gate),
    }
    result_payload = {
        **base,
        "protocol": PHASE7_ARTIFACT_PROTOCOL,
        "stage": "stage2",
        "status": status,
        "candidate_statuses": {candidate_id: "PASS" if gate.passed else "REJECT"},
        "stage1_identity": verified_stage1,
        "gate": _gate_payload(gate),
    }

    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    _atomic_write(root / "windows.json", _stable_json_bytes(windows_payload))
    _atomic_write(root / "result.json", _stable_json_bytes(result_payload))

    manifest = {
        **base,
        "protocol": PHASE7_ARTIFACT_PROTOCOL,
        "stage": "stage2",
        "status": status,
        "stage1_identity": verified_stage1,
        "artifacts": [
            _artifact_record(root / name) for name in ("result.json", "windows.json")
        ],
    }
    _atomic_write(root / "manifest.json", _stable_json_bytes(manifest))
    return manifest
