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

from fmp.contracts import SUPPORTED_SYMBOLS
from fmp.research.data import ELIGIBLE_TIMEFRAMES

from .challenger_round1 import (
    EXP013_STAGE_A_CELL_PROTOCOL,
    EXP013_STAGE_A_GATE_PROTOCOL,
    evaluate_exp013_stage_a_cell_pair,
)
from .challengers import EXP013_ID
from .research_data import PHASE8A_RETROSPECTIVE_LABEL


EXP013_STAGE_A_CELL_EVIDENCE_PROTOCOL = "fmp-phase8a-exp013-stage-a-cell-evidence-v1"
EXP013_STAGE_A_AUTHORIZATION_PROTOCOL = "fmp-phase8a-exp013-stage-a-authorization-v1"
EXP013_STAGE_A_ARTIFACT_PROTOCOL = "fmp-phase8a-exp013-stage-a-artifacts-v1"

_EXPECTED_CELLS = frozenset(
    (symbol, timeframe)
    for symbol in ("EURUSD", "GBPUSD", "USDJPY")
    for timeframe in ("5m", "15m", "1h")
)


def _cell_identity(value: Mapping[str, object]) -> tuple[str, str, str, str]:
    if value.get("protocol") != EXP013_STAGE_A_CELL_PROTOCOL:
        raise ValueError("EXP-013 Stage A cell protocol mismatch")
    if value.get("experiment_id") != EXP013_ID:
        raise ValueError("EXP-013 Stage A experiment identity mismatch")
    if value.get("evidence_label") != PHASE8A_RETROSPECTIVE_LABEL:
        raise ValueError("EXP-013 Stage A cell must be retrospective")
    if value.get("untouched_oos") is not False:
        raise ValueError("EXP-013 Stage A cell cannot be untouched OOS")
    if value.get("promotion_authorized") is not False:
        raise ValueError("EXP-013 Stage A cell cannot authorize promotion")

    symbol = value.get("symbol")
    timeframe = value.get("timeframe")
    commit = value.get("runner_code_commit")
    manifest_sha = value.get("processed_manifest_sha256")
    if not isinstance(symbol, str) or symbol not in SUPPORTED_SYMBOLS:
        raise ValueError("invalid EXP-013 Stage A symbol")
    if not isinstance(timeframe, str) or timeframe not in ELIGIBLE_TIMEFRAMES:
        raise ValueError("invalid EXP-013 Stage A timeframe")
    if not isinstance(commit, str) or len(commit) != 40:
        raise ValueError("invalid EXP-013 Stage A runner commit")
    if not isinstance(manifest_sha, str) or len(manifest_sha) != 64:
        raise ValueError("invalid EXP-013 processed manifest digest")
    return symbol, timeframe, commit, manifest_sha


def _strategy_fingerprints(value: Mapping[str, object]) -> tuple[str, ...]:
    rows = value.get("rows")
    if not isinstance(rows, list):
        raise ValueError("EXP-013 Stage A rows must be a list")
    fingerprints = {
        row.get("strategy_fingerprint")
        for row in rows
        if isinstance(row, Mapping)
    }
    if None in fingerprints or len(fingerprints) != 4:
        raise ValueError("EXP-013 Stage A cell must contain exactly four strategy identities")
    if value.get("strategy_identity_count") != 4:
        raise ValueError("EXP-013 Stage A strategy_identity_count mismatch")
    if value.get("scenario_run_count") != 12 or len(rows) != 12:
        raise ValueError("EXP-013 Stage A cell must contain exactly 12 scenario rows")
    return tuple(sorted(str(item) for item in fingerprints))


def build_exp013_stage_a_cell_evidence(
    *,
    development: Mapping[str, object],
    validation: Mapping[str, object],
    gate: Mapping[str, object],
) -> dict[str, object]:
    dev_symbol, dev_timeframe, dev_commit, dev_manifest = _cell_identity(development)
    val_symbol, val_timeframe, val_commit, val_manifest = _cell_identity(validation)
    if development.get("split_name") != "development":
        raise ValueError("EXP-013 development evidence split mismatch")
    if validation.get("split_name") != "validation":
        raise ValueError("EXP-013 validation evidence split mismatch")
    if (dev_symbol, dev_timeframe, dev_commit, dev_manifest) != (
        val_symbol,
        val_timeframe,
        val_commit,
        val_manifest,
    ):
        raise ValueError("EXP-013 Stage A development/validation identity mismatch")

    dev_fingerprints = _strategy_fingerprints(development)
    val_fingerprints = _strategy_fingerprints(validation)
    if dev_fingerprints != val_fingerprints:
        raise ValueError("EXP-013 Stage A split strategy identities differ")

    computed_gate = evaluate_exp013_stage_a_cell_pair(
        development=development,
        validation=validation,
    )
    if dict(gate) != computed_gate:
        raise ValueError("EXP-013 supplied Stage A gate does not match deterministic recomputation")
    if gate.get("protocol") != EXP013_STAGE_A_GATE_PROTOCOL:
        raise ValueError("EXP-013 Stage A gate protocol mismatch")

    raw_survivors = gate.get("survivor_fingerprints")
    if not isinstance(raw_survivors, list):
        raise ValueError("EXP-013 Stage A survivor list missing")
    survivors = tuple(sorted(str(item) for item in raw_survivors))
    if len(set(survivors)) != len(survivors):
        raise ValueError("duplicate EXP-013 Stage A survivor identity")
    if not set(survivors).issubset(set(dev_fingerprints)):
        raise ValueError("EXP-013 Stage A gate survivor is outside exact cell")

    return {
        "protocol": EXP013_STAGE_A_CELL_EVIDENCE_PROTOCOL,
        "experiment_id": EXP013_ID,
        "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "symbol": dev_symbol,
        "timeframe": dev_timeframe,
        "runner_code_commit": dev_commit,
        "processed_manifest_sha256": dev_manifest,
        "strategy_identity_count": 4,
        "strategy_fingerprints": list(dev_fingerprints),
        "survivor_fingerprints": list(survivors),
        "survivor_count": len(survivors),
        "development": dict(development),
        "validation": dict(validation),
        "gate": dict(gate),
    }


def _validate_cell_evidence(value: Mapping[str, object]) -> tuple[str, str, str, str, tuple[str, ...], tuple[str, ...]]:
    if value.get("protocol") != EXP013_STAGE_A_CELL_EVIDENCE_PROTOCOL:
        raise ValueError("EXP-013 Stage A cell-evidence protocol mismatch")
    if value.get("experiment_id") != EXP013_ID:
        raise ValueError("EXP-013 Stage A cell-evidence experiment mismatch")
    if value.get("evidence_label") != PHASE8A_RETROSPECTIVE_LABEL:
        raise ValueError("EXP-013 Stage A cell-evidence must be retrospective")
    if value.get("untouched_oos") is not False:
        raise ValueError("EXP-013 Stage A cell-evidence cannot be untouched OOS")
    if value.get("promotion_authorized") is not False:
        raise ValueError("EXP-013 Stage A cell-evidence cannot authorize promotion")

    symbol = value.get("symbol")
    timeframe = value.get("timeframe")
    commit = value.get("runner_code_commit")
    manifest = value.get("processed_manifest_sha256")
    if (symbol, timeframe) not in _EXPECTED_CELLS:
        raise ValueError("invalid EXP-013 Stage A cell key")
    if not isinstance(commit, str) or len(commit) != 40:
        raise ValueError("invalid EXP-013 Stage A cell runner commit")
    if not isinstance(manifest, str) or len(manifest) != 64:
        raise ValueError("invalid EXP-013 Stage A cell manifest digest")

    raw_fingerprints = value.get("strategy_fingerprints")
    raw_survivors = value.get("survivor_fingerprints")
    if not isinstance(raw_fingerprints, list) or len(raw_fingerprints) != 4:
        raise ValueError("EXP-013 Stage A cell must bind four strategy fingerprints")
    if not isinstance(raw_survivors, list):
        raise ValueError("EXP-013 Stage A cell survivor list missing")
    fingerprints = tuple(sorted(str(item) for item in raw_fingerprints))
    survivors = tuple(sorted(str(item) for item in raw_survivors))
    if len(set(fingerprints)) != 4:
        raise ValueError("duplicate EXP-013 Stage A strategy fingerprint")
    if len(set(survivors)) != len(survivors):
        raise ValueError("duplicate EXP-013 Stage A survivor fingerprint")
    if not set(survivors).issubset(set(fingerprints)):
        raise ValueError("EXP-013 Stage A survivor is outside bound cell")
    if value.get("strategy_identity_count") != 4:
        raise ValueError("EXP-013 Stage A cell strategy count mismatch")
    if value.get("survivor_count") != len(survivors):
        raise ValueError("EXP-013 Stage A cell survivor count mismatch")

    return str(symbol), str(timeframe), commit, manifest, fingerprints, survivors


def build_exp013_stage_a_authorization(
    cell_evidences: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    cells = tuple(cell_evidences)
    if len(cells) != 9:
        raise ValueError("EXP-013 Stage A authorization requires exactly nine cells")

    seen_cells: set[tuple[str, str]] = set()
    all_fingerprints: list[str] = []
    all_survivors: list[str] = []
    commit: str | None = None
    manifests_by_symbol: dict[str, str] = {}
    summaries: list[dict[str, object]] = []

    for value in cells:
        if not isinstance(value, Mapping):
            raise TypeError("EXP-013 Stage A cell evidence must be a mapping")
        symbol, timeframe, cell_commit, manifest, fingerprints, survivors = _validate_cell_evidence(value)
        cell_key = (symbol, timeframe)
        if cell_key in seen_cells:
            raise ValueError("duplicate EXP-013 Stage A cell evidence")
        seen_cells.add(cell_key)

        if commit is None:
            commit = cell_commit
        elif commit != cell_commit:
            raise ValueError("EXP-013 Stage A cells use different runner commits")

        prior_manifest = manifests_by_symbol.get(symbol)
        if prior_manifest is None:
            manifests_by_symbol[symbol] = manifest
        elif prior_manifest != manifest:
            raise ValueError("EXP-013 Stage A manifest identity differs across timeframes")

        all_fingerprints.extend(fingerprints)
        all_survivors.extend(survivors)
        summaries.append(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "strategy_fingerprints": list(fingerprints),
                "survivor_fingerprints": list(survivors),
                "survivor_count": len(survivors),
            }
        )

    if seen_cells != _EXPECTED_CELLS:
        raise ValueError("EXP-013 Stage A authorization is missing required cells")
    if len(all_fingerprints) != 36 or len(set(all_fingerprints)) != 36:
        raise ValueError("EXP-013 Stage A authorization must bind exactly 36 unique strategies")
    if len(set(all_survivors)) != len(all_survivors):
        raise ValueError("EXP-013 Stage A survivor identity appears in multiple cells")
    assert commit is not None

    survivor_fingerprints = tuple(sorted(all_survivors))
    summaries.sort(key=lambda item: (str(item["symbol"]), str(item["timeframe"])))
    return {
        "protocol": EXP013_STAGE_A_AUTHORIZATION_PROTOCOL,
        "experiment_id": EXP013_ID,
        "evidence_label": PHASE8A_RETROSPECTIVE_LABEL,
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "runner_code_commit": commit,
        "cell_count": 9,
        "strategy_identity_count": 36,
        "processed_manifest_sha256_by_symbol": dict(sorted(manifests_by_symbol.items())),
        "survivor_count": len(survivor_fingerprints),
        "survivor_fingerprints": list(survivor_fingerprints),
        "stage_b_source_open_authorized": bool(survivor_fingerprints),
        "cells": summaries,
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


def _write_artifact(
    value: Mapping[str, object],
    *,
    out_dir: Path,
    filename: str,
) -> dict[str, object]:
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    result_path = root / filename
    payload = _stable_json_bytes(value)
    _atomic_write(result_path, payload)
    manifest = {
        "protocol": EXP013_STAGE_A_ARTIFACT_PROTOCOL,
        "artifacts": [
            {
                "path": filename,
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        ],
    }
    _atomic_write(root / "manifest.json", _stable_json_bytes(manifest))
    return manifest


def write_exp013_stage_a_cell_evidence(
    value: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    _validate_cell_evidence(value)
    return _write_artifact(
        value,
        out_dir=out_dir,
        filename="cell-evidence.json",
    )


def write_exp013_stage_a_authorization(
    value: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    if value.get("protocol") != EXP013_STAGE_A_AUTHORIZATION_PROTOCOL:
        raise ValueError("EXP-013 Stage A authorization protocol mismatch")
    return _write_artifact(
        value,
        out_dir=out_dir,
        filename="stage-a-authorization.json",
    )
