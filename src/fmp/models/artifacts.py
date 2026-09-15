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
from .data import MODEL_INPUT_COLUMNS
from .estimators import EXPERIMENT_SEED


PHASE6_ARTIFACT_PROTOCOL = "fmp-phase6-ml-filter-artifacts-v1"
EVIDENCE_CONTRACT_VERSION = 1
_ALLOWED_STRATEGIES = frozenset(FROZEN_STRATEGIES)
_ALLOWED_MODELS = frozenset(family.value for family in ModelFamily)
_DATE_2024_PLUS = re.compile(r"(?<!\d)(20(?:2[4-9]|[3-9]\d))-\d{2}-\d{2}(?!\d)")
_PATH_2024_PLUS = re.compile(r"(?:^|[/\\])(20(?:2[4-9]|[3-9]\d))(?:[/\\]|$)")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_REQUIRED_DATASET_FIELDS = frozenset(
    {
        "split",
        "candidate_row_count",
        "candidate_digest",
        "labeled_row_count",
        "labeled_digest",
        "unlabelable_counts_by_reason",
        "feature_row_count",
        "joined_row_count",
        "joined_digest",
        "input_columns",
        "label_prevalence",
        "feature_availability_range",
        "label_resolution_range",
        "feature_manifest_sha256",
        "processed_manifest_sha256",
        "phase5_checkpoint_sha",
        "phase5_code_commit",
        "opened_feature_artifacts",
        "opened_coverage_pre_2024",
    }
)
_REQUIRED_TRANSFORM_FIELDS = frozenset(
    {
        "row_count",
        "column_count",
        "input_columns",
        "null_counts_before",
        "null_counts_after",
        "matrix_digest",
    }
)


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
        if field.endswith(".end_exclusive") and value == FINAL_START.isoformat():
            return
        lowered = value.strip().lower()
        if lowered in {"final", "final-test", "final_test", "final test"}:
            raise ValueError(f"Phase 6 final-test lock: {field} names the final split")
        if _DATE_2024_PLUS.search(value) or _PATH_2024_PLUS.search(value):
            raise ValueError(f"Phase 6 final-test lock: {field} reaches 2024 or later")


def _require_mapping(value: object, field: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"Phase 6 evidence {field} must be a mapping")
    return value


def _require_keys(value: Mapping[str, object], required: frozenset[str], field: str) -> None:
    missing = sorted(required - set(value))
    if missing:
        raise ValueError(f"Phase 6 evidence {field} is missing required fields: {missing}")


def _validate_digest(value: object, field: str) -> None:
    if not isinstance(value, str) or _HEX64.fullmatch(value) is None:
        raise ValueError(f"Phase 6 evidence {field} must be a lowercase SHA-256 digest")


def _validate_count(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"Phase 6 evidence {field} must be a non-negative integer")
    return value


def _validate_range(value: object, field: str) -> None:
    if value is None:
        return
    mapping = _require_mapping(value, field)
    if set(mapping) != {"min", "max"}:
        raise ValueError(f"Phase 6 evidence {field} must contain exact min/max bounds")


def _validate_dataset_evidence(
    raw: object,
    *,
    expected_split: str,
) -> Mapping[str, object]:
    dataset = _require_mapping(raw, f"dataset.{expected_split}")
    _require_keys(dataset, _REQUIRED_DATASET_FIELDS, f"dataset.{expected_split}")
    split = _require_mapping(dataset["split"], f"dataset.{expected_split}.split")
    if split.get("name") != expected_split:
        raise ValueError(f"Phase 6 evidence dataset.{expected_split} split identity mismatch")

    candidate_count = _validate_count(
        dataset["candidate_row_count"], f"dataset.{expected_split}.candidate_row_count"
    )
    labeled_count = _validate_count(
        dataset["labeled_row_count"], f"dataset.{expected_split}.labeled_row_count"
    )
    _validate_count(dataset["feature_row_count"], f"dataset.{expected_split}.feature_row_count")
    joined_count = _validate_count(
        dataset["joined_row_count"], f"dataset.{expected_split}.joined_row_count"
    )
    if labeled_count > candidate_count or joined_count > candidate_count:
        raise ValueError(f"Phase 6 evidence dataset.{expected_split} row counts are inconsistent")

    for name in ("candidate_digest", "labeled_digest", "joined_digest"):
        _validate_digest(dataset[name], f"dataset.{expected_split}.{name}")
    if list(dataset["input_columns"]) != list(MODEL_INPUT_COLUMNS):
        raise ValueError(f"Phase 6 evidence dataset.{expected_split} input columns mismatch")

    reasons = _require_mapping(
        dataset["unlabelable_counts_by_reason"],
        f"dataset.{expected_split}.unlabelable_counts_by_reason",
    )
    unlabelable = sum(
        _validate_count(value, f"dataset.{expected_split}.unlabelable_counts_by_reason.{key}")
        for key, value in reasons.items()
    )
    if labeled_count + unlabelable != candidate_count:
        raise ValueError(f"Phase 6 evidence dataset.{expected_split} label accounting mismatch")

    prevalence = dataset["label_prevalence"]
    if labeled_count == 0:
        if prevalence is not None:
            raise ValueError(f"Phase 6 evidence dataset.{expected_split} prevalence must be null")
    elif isinstance(prevalence, bool) or not isinstance(prevalence, (int, float)) or not 0.0 <= float(prevalence) <= 1.0:
        raise ValueError(f"Phase 6 evidence dataset.{expected_split} prevalence is invalid")

    _validate_range(dataset["feature_availability_range"], f"dataset.{expected_split}.feature_availability_range")
    _validate_range(dataset["label_resolution_range"], f"dataset.{expected_split}.label_resolution_range")
    if dataset["processed_manifest_sha256"] != USDJPY_PROCESSED_MANIFEST_SHA256:
        raise ValueError(f"Phase 6 evidence dataset.{expected_split} processed identity mismatch")
    if dataset["phase5_checkpoint_sha"] != PHASE5_CHECKPOINT_SHA:
        raise ValueError(f"Phase 6 evidence dataset.{expected_split} checkpoint identity mismatch")
    if not isinstance(dataset["feature_manifest_sha256"], str) or not dataset["feature_manifest_sha256"]:
        raise ValueError(f"Phase 6 evidence dataset.{expected_split} feature manifest identity missing")
    if not isinstance(dataset["phase5_code_commit"], str) or not dataset["phase5_code_commit"]:
        raise ValueError(f"Phase 6 evidence dataset.{expected_split} Phase 5 code identity missing")
    opened = dataset["opened_feature_artifacts"]
    if not isinstance(opened, (tuple, list)):
        raise ValueError(f"Phase 6 evidence dataset.{expected_split} opened feature artifacts must be a list")
    if dataset["opened_coverage_pre_2024"] is not True:
        raise ValueError(f"Phase 6 evidence dataset.{expected_split} must prove pre-2024 coverage")
    return dataset


def _validate_transform(raw: object, *, field: str, expected_rows: int) -> None:
    transform = _require_mapping(raw, field)
    _require_keys(transform, _REQUIRED_TRANSFORM_FIELDS, field)
    if _validate_count(transform["row_count"], f"{field}.row_count") != expected_rows:
        raise ValueError(f"Phase 6 evidence {field} row count mismatch")
    if transform["column_count"] != len(MODEL_INPUT_COLUMNS):
        raise ValueError(f"Phase 6 evidence {field} column count mismatch")
    if list(transform["input_columns"]) != list(MODEL_INPUT_COLUMNS):
        raise ValueError(f"Phase 6 evidence {field} input columns mismatch")
    before = transform["null_counts_before"]
    after = transform["null_counts_after"]
    if not isinstance(before, (tuple, list)) or len(before) != len(MODEL_INPUT_COLUMNS):
        raise ValueError(f"Phase 6 evidence {field} pre-transform null counts mismatch")
    if not isinstance(after, (tuple, list)) or list(after) != [0] * len(MODEL_INPUT_COLUMNS):
        raise ValueError(f"Phase 6 evidence {field} post-transform null counts mismatch")
    _validate_digest(transform["matrix_digest"], f"{field}.matrix_digest")


def _validate_retention(raw: object, *, field: str, expected_candidates: int) -> None:
    retention = _require_mapping(raw, field)
    if set(retention) != {"candidate_count", "retained_count", "retained_rate"}:
        raise ValueError(f"Phase 6 evidence {field} retention fields mismatch")
    candidate_count = _validate_count(retention["candidate_count"], f"{field}.candidate_count")
    retained_count = _validate_count(retention["retained_count"], f"{field}.retained_count")
    if candidate_count != expected_candidates or retained_count > candidate_count:
        raise ValueError(f"Phase 6 evidence {field} retention counts mismatch")
    expected_rate = float(retained_count / candidate_count) if candidate_count else 0.0
    rate = retention["retained_rate"]
    if isinstance(rate, bool) or not isinstance(rate, (int, float)) or float(rate) != expected_rate:
        raise ValueError(f"Phase 6 evidence {field} retained rate mismatch")


def _validate_strategy(selection: Mapping[str, object], strategy_id: str) -> None:
    strategy = FROZEN_STRATEGIES[strategy_id]
    supplied = _require_mapping(selection.get("strategy"), "selection.strategy")
    expected = {
        "family": strategy.family,
        "symbol": strategy.symbol,
        "timeframe": strategy.timeframe,
        "parameters": dict(strategy.parameters),
    }
    if _jsonable(supplied) != _jsonable(expected):
        raise ValueError("Phase 6 frozen strategy configuration evidence mismatch")


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
    if selection.get("evidence_contract_version") != EVIDENCE_CONTRACT_VERSION:
        raise ValueError("Phase 6 evidence contract version mismatch")
    if selection.get("strategy_id") != strategy_id:
        raise ValueError("Phase 6 selection strategy identity mismatch")
    _validate_strategy(selection, str(strategy_id))
    if selection.get("code_commit") != code_commit:
        raise ValueError("Phase 6 selection code commit mismatch")
    if selection.get("feature_set_version") != FEATURE_SET_VERSION:
        raise ValueError("Phase 6 feature identity mismatch")
    if selection.get("phase5_checkpoint_sha") != PHASE5_CHECKPOINT_SHA:
        raise ValueError("Phase 6 Phase 5 checkpoint identity mismatch")
    if selection.get("processed_manifest_sha256") != USDJPY_PROCESSED_MANIFEST_SHA256:
        raise ValueError("Phase 6 processed manifest identity mismatch")

    datasets = _require_mapping(selection.get("datasets"), "selection.datasets")
    if set(datasets) != {"fit", "selection"}:
        raise ValueError("Phase 6 selection datasets must contain exactly fit and selection")
    fit_dataset = _validate_dataset_evidence(datasets["fit"], expected_split="fit")
    selection_dataset = _validate_dataset_evidence(datasets["selection"], expected_split="selection")

    models = selection.get("models")
    if not isinstance(models, Mapping) or set(models) != _ALLOWED_MODELS:
        raise ValueError("Phase 6 model identity set must contain exactly the two approved models")
    for family_name, raw_model in models.items():
        model = _require_mapping(raw_model, f"selection.models.{family_name}")
        required_model = frozenset(
            {
                "preprocessing",
                "model_config",
                "random_seed",
                "fit_row_count",
                "fit_status",
                "transforms",
                "fit_score_digest",
                "selection_score_digest",
                "cutoffs",
                "fit_diagnostics",
                "selection_diagnostics",
            }
        )
        _require_keys(model, required_model, f"selection.models.{family_name}")
        if model["random_seed"] != EXPERIMENT_SEED:
            raise ValueError(f"Phase 6 model {family_name} random seed mismatch")
        fit_rows = _validate_count(model["fit_row_count"], f"selection.models.{family_name}.fit_row_count")
        if fit_rows != fit_dataset["labeled_row_count"]:
            raise ValueError(f"Phase 6 model {family_name} fit row count mismatch")
        status = _require_mapping(model["fit_status"], f"selection.models.{family_name}.fit_status")
        if status.get("status") != "FIT_OK" or status.get("fit_count") != 1 or status.get("refit_after_selection") is not False:
            raise ValueError(f"Phase 6 model {family_name} fit status mismatch")
        preprocessing = _require_mapping(model["preprocessing"], f"selection.models.{family_name}.preprocessing")
        if list(preprocessing.get("input_columns", ())) != list(MODEL_INPUT_COLUMNS):
            raise ValueError(f"Phase 6 model {family_name} preprocessing input columns mismatch")
        transforms = _require_mapping(model["transforms"], f"selection.models.{family_name}.transforms")
        if set(transforms) != {"fit", "selection"}:
            raise ValueError(f"Phase 6 model {family_name} transform evidence mismatch")
        _validate_transform(transforms["fit"], field=f"selection.models.{family_name}.transforms.fit", expected_rows=fit_rows)
        _validate_transform(
            transforms["selection"],
            field=f"selection.models.{family_name}.transforms.selection",
            expected_rows=int(selection_dataset["joined_row_count"]),
        )
        _validate_digest(model["fit_score_digest"], f"selection.models.{family_name}.fit_score_digest")
        _validate_digest(model["selection_score_digest"], f"selection.models.{family_name}.selection_score_digest")

    variants = selection.get("variants")
    if not isinstance(variants, (tuple, list)) or len(variants) != 6:
        raise ValueError("Phase 6 selection evidence must contain exactly six model-threshold variants")
    for index, raw_variant in enumerate(variants):
        variant = _require_mapping(raw_variant, f"selection.variants[{index}]")
        _validate_retention(
            variant.get("retention"),
            field=f"selection.variants[{index}].retention",
            expected_candidates=int(selection_dataset["joined_row_count"]),
        )

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
    if status == "NO_ML_CHALLENGER":
        if validation.get("validation_loaded") is not False:
            raise ValueError("Phase 6 no-challenger result must not load validation")
    else:
        if validation.get("validation_loaded") is not True:
            raise ValueError("Phase 6 selected challenger must load validation exactly once")
        model_family = validation.get("model_family")
        if model_family not in _ALLOWED_MODELS:
            raise ValueError(f"unapproved Phase 6 validation model identity: {model_family!r}")
        validation_dataset = _validate_dataset_evidence(validation.get("dataset"), expected_split="validation")
        _validate_transform(
            validation.get("transformation"),
            field="validation.transformation",
            expected_rows=int(validation_dataset["joined_row_count"]),
        )
        _validate_retention(
            validation.get("retention"),
            field="validation.retention",
            expected_candidates=int(validation_dataset["joined_row_count"]),
        )
        if validation.get("refit_count_after_selection") != 0:
            raise ValueError("Phase 6 validation evidence must prove zero refits after selection")

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
