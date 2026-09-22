from __future__ import annotations

import hashlib
import json
import math
import os
from dataclasses import fields, is_dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Mapping, Sequence

from .contracts import StrategyRecord
from .historical_inventory import build_phase4_baseline_inventory

JOINT_EVIDENCE_PROTOCOL = "fmp-phase8a-joint-evidence-v1"
JOINT_EVIDENCE_ARTIFACT_PROTOCOL = "fmp-phase8a-joint-evidence-artifacts-v1"


def resolve_historical_strategy_records(
    fingerprints: Sequence[str],
) -> tuple[StrategyRecord, ...]:
    requested = tuple(fingerprints)
    if not requested:
        raise ValueError("at least one strategy fingerprint is required")
    if len(set(requested)) != len(requested):
        raise ValueError("duplicate strategy fingerprint requested")

    inventory = {
        item.strategy.fingerprint: item
        for item in build_phase4_baseline_inventory()
    }
    unknown = sorted(set(requested) - set(inventory))
    if unknown:
        raise ValueError(f"unknown historical strategy fingerprints: {unknown}")

    return tuple(
        sorted(
            (inventory[fingerprint] for fingerprint in requested),
            key=lambda item: item.strategy.fingerprint,
        )
    )


def build_joint_evidence_envelope(
    *,
    joint_result: Mapping[str, object],
    strategy_records: Sequence[StrategyRecord],
) -> dict[str, object]:
    records = tuple(strategy_records)
    if not records:
        raise ValueError("joint evidence requires at least one strategy record")
    if any(not isinstance(item, StrategyRecord) for item in records):
        raise TypeError("strategy_records must contain StrategyRecord")

    if joint_result.get("protocol") != "fmp-phase8a-joint-portfolio-v1":
        raise ValueError("joint result protocol mismatch")
    if joint_result.get("promotion_authorized") is not False:
        raise ValueError("joint retrospective result cannot authorize promotion")
    if joint_result.get("evidence_label") != "RETROSPECTIVE_ALREADY_SEEN":
        raise ValueError("joint result must be explicitly retrospective")
    if joint_result.get("untouched_oos") is not False:
        raise ValueError("joint retrospective result cannot be untouched OOS")

    expected = tuple(sorted(item.strategy.fingerprint for item in records))
    raw_actual = joint_result.get("strategy_fingerprints")
    if not isinstance(raw_actual, (tuple, list)):
        raise ValueError("joint result strategy_fingerprints missing")
    actual = tuple(raw_actual)
    if tuple(sorted(actual)) != expected:
        raise ValueError("joint result strategy identity does not match evidence records")

    return {
        "protocol": JOINT_EVIDENCE_PROTOCOL,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "historical_strategy_status": [
            {
                "fingerprint": item.strategy.fingerprint,
                "family": item.strategy.family,
                "version": item.strategy.version,
                "symbol": item.strategy.symbol,
                "timeframe": item.strategy.timeframe,
                "parameters_json": item.strategy.parameters_json,
                "lifecycle": item.lifecycle.value,
                "evidence_id": item.evidence_id,
            }
            for item in sorted(records, key=lambda value: value.strategy.fingerprint)
        ],
        "joint_result": dict(joint_result),
    }


def _jsonable(value: object) -> object:
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _jsonable(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() != timedelta(0):
            raise ValueError("serialized datetime must use UTC")
        return value.isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("cannot serialize non-finite float")
        return value
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise TypeError(f"unsupported deterministic serialization type: {type(value).__name__}")


def _stable_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            _jsonable(value),
            sort_keys=True,
            indent=2,
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


def write_joint_evidence_artifacts(
    envelope: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    result_path = root / "joint-evidence.json"
    payload = _stable_json_bytes(envelope)
    _atomic_write(result_path, payload)

    manifest = {
        "protocol": JOINT_EVIDENCE_ARTIFACT_PROTOCOL,
        "artifacts": [
            {
                "path": result_path.name,
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        ],
    }
    _atomic_write(root / "manifest.json", _stable_json_bytes(manifest))
    return manifest
