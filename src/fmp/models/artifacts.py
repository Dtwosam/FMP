from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import re
from dataclasses import fields, is_dataclass
from datetime import date, datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Mapping

import numpy as np
import polars as pl
import scipy
import sklearn

from .contracts import (
    EXPERIMENT_ID,
    FEATURE_SET_VERSION,
    FINAL_START,
    FROZEN_STRATEGIES,
    PHASE5_CHECKPOINT_SHA,
    USDJPY_PROCESSED_MANIFEST_SHA256,
    ModelFamily,
)


PHASE6_ARTIFACT_PROTOCOL = "fmp-phase6-ml-filter-artifacts-v1"
_ALLOWED_STRATEGIES = frozenset(FROZEN_STRATEGIES)
_ALLOWED_MODELS = frozenset(family.value for family in ModelFamily)
_DATE_2024_PLUS = re.compile(r"(?<!\d)(20(?:2[4-9]|[3-9]\d))-\d{2}-\d{2}(?!\d)")
_PATH_2024_PLUS = re.compile(r"(?:^|[/\\])(20(?:2[4-9]|[3-9]\d))(?:[/\\]|$)")


def _jsonable(value: object) -> object:
    if is_dataclass(value) and not isinstance(value, type):
        return {item.name: _jsonable(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        if value.tzinfo is None:
            raise ValueError("Phase 6 evidence datetime must be timezone-aware")
        utc = value.astimezone(timezone.utc)
        return utc.isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (np.integer, np.floating, np.bool_)):
        return _jsonable(value.item())
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Phase 6 evidence requires finite JSON numbers")
        return value
    if value is None or isinstance(value, (str, bool, int)):
        return value
    raise TypeError(f"unsupported Phase 6 evidence value: {type(value).__name__}")


def _scan_final_test_lock(value: object, *, field: str = "root") -> None:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            raise ValueError(f"{field} evidence datetime must be timezone-aware")
        if value.astimezone(timezone.utc).date() >= FINAL_START:
            raise ValueError(f"Phase 6 final-test lock: {field} reaches 2024 or later")
        return
    if isinstance(value, date):
        if value >= FINAL_START:
            raise ValueError(f"Phase 6 final-test lock: {field} reaches 2024 or later")
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            if key_text.isdigit() and len(key_text) == 4 and int(key_text) >= FINAL_START.year:
                raise ValueError(f"Phase 6 final-test lock: {field}.{key_text} reaches 2024 or later")
            _scan_final_test_lock(item, field=f"{field}.{key_text}")
        return
    if isinstance(value, (tuple, list)):
        for index, item in enumerate(value):
            _scan_final_test_lock(item, field=f"{field}[{index}]")
        return
    if isinstance(value, Path):
        value = value.as_posix()
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"final", "final-test", "final_test", "final test"}:
            raise ValueError(f"Phase 6 final-test lock: {field} names the final split")
        if _DATE_2024_PLUS.search(value) or _PATH_2024_PLUS.search(value):
            raise ValueError(f"Phase 6 final-test lock: {field} reaches 2024 or later")


def _validate_result(result: Mapping[str, object]) -> dict[str, object]:
    if result.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("Phase 6 experiment identity mismatch")
    strategy_id = result.get("strategy_id")
    if strategy_id not in _ALLOWED_STRATEGIES:
        raise ValueError(f"unapproved Phase 6 strategy identity: {strategy_id!r}")
    code_commit = result.get("code_commit")
    if not isinstance(code_commit, str) or not code_commit.strip():
        raise ValueError("Phase 6 code_commit must be non-empty")

    selection_raw = result.get("selection")
    if not isinstance(selection_raw, Mapping):
        raise ValueError("Phase 6 result requires selection evidence")
    selection = dict(selection_raw)
    if selection.get("experiment_id") != EXPERIMENT_ID:
        raise ValueError("Phase 6 selection experiment identity mismatch")
    if selection.get("strategy_id") != strategy_id:
        raise ValueError("Phase 6 selection strategy identity mismatch")
    if selection.get("code_commit") != code_commit:
        raise ValueError("Phase 6 selection code commit mismatch")

    supplied_feature_version = selection.get("feature_set_version", FEATURE_SET_VERSION)
    if supplied_feature_version != FEATURE_SET_VERSION:
        raise ValueError("Phase 6 feature identity mismatch")
    selection["feature_set_version"] = FEATURE_SET_VERSION
    if selection.get("phase5_checkpoint_sha") != PHASE5_CHECKPOINT_SHA:
        raise ValueError("Phase 6 Phase 5 checkpoint identity mismatch")
    if selection.get("processed_manifest_sha256") != USDJPY_PROCESSED_MANIFEST_SHA256:
        raise ValueError("Phase 6 processed manifest identity mismatch")

    models = selection.get("models")
    if not isinstance(models, Mapping) or set(models) != _ALLOWED_MODELS:
        raise ValueError("Phase 6 model identity set must contain exactly the two approved models")
    selected = selection.get("selected_variant")
    if isinstance(selected, Mapping):
        selected_model = selected.get("model_family")
        if selected_model not in _ALLOWED_MODELS:
            raise ValueError(f"unapproved Phase 6 selected model identity: {selected_model!r}")
    elif selected != "NO_ML_CHALLENGER":
        raise ValueError("Phase 6 selected_variant must be approved or NO_ML_CHALLENGER")

    validation = result.get("validation")
    if not isinstance(validation, Mapping):
        raise ValueError("Phase 6 result requires validation evidence")
    status = validation.get("status")
    if status not in {"NO_ML_CHALLENGER", "PROMOTE_ML_FILTER", "REJECT_ML_FILTER"}:
        raise ValueError(f"unapproved Phase 6 validation status: {status!r}")
    if status != "NO_ML_CHALLENGER":
        model_family = validation.get("model_family")
        if model_family not in _ALLOWED_MODELS:
            raise ValueError(f"unapproved Phase 6 validation model identity: {model_family!r}")

    normalized = dict(result)
    normalized["selection"] = selection
    _scan_final_test_lock(normalized)
    return _jsonable(normalized)  # type: ignore[return-value]


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


def _artifact_record(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": path.name,
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def _runtime_versions() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "scikit_learn": sklearn.__version__,
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "polars": pl.__version__,
    }


def write_phase6_artifacts(
    result: Mapping[str, object],
    out_dir: Path,
) -> dict[str, object]:
    normalized = _validate_result(result)
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)

    selection = normalized["selection"]
    selection_path = root / "selection.json"
    result_path = root / "result.json"
    _atomic_write(selection_path, _stable_json_bytes(selection))
    _atomic_write(result_path, _stable_json_bytes(normalized))

    manifest: dict[str, object] = {
        "protocol": PHASE6_ARTIFACT_PROTOCOL,
        "experiment_id": EXPERIMENT_ID,
        "strategy_id": normalized["strategy_id"],
        "code_commit": normalized["code_commit"],
        "feature_set_version": FEATURE_SET_VERSION,
        "phase5_checkpoint_sha": PHASE5_CHECKPOINT_SHA,
        "processed_manifest_sha256": USDJPY_PROCESSED_MANIFEST_SHA256,
        "runtime_versions": _runtime_versions(),
        "artifacts": [
            _artifact_record(selection_path),
            _artifact_record(result_path),
        ],
    }
    _scan_final_test_lock(manifest)
    _atomic_write(root / "manifest.json", _stable_json_bytes(manifest))
    return manifest
