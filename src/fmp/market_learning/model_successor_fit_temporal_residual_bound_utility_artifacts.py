from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Mapping

from .model_protocol import MODEL_CELLS
from .model_successor_fit_temporal_residual_bound_utility_protocol import (
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_PROTOCOL_VERSION,
    FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL,
    fit_temporal_residual_bound_utility_protocol_fingerprint,
)
from .model_successor_fit_temporal_residual_bound_utility_training import (
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_DECISION,
    FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_VERSION,
    validate_fit_temporal_residual_bound_utility_training_sources,
)
from .model_successor_regime_utility_artifacts import _canonical_json, _git_blob_sha
from .model_successor_temporal_jackknife_utility_protocol import (
    FINANCIAL_TARGET_COLUMNS,
    FIT_JACKKNIFE_VIEWS,
)
from .model_successor_fit_temporal_support_utility_protocol import (
    FIT_TEMPORAL_SUPPORT_WINDOWS,
)

FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION = (
    "fmp-exp054-fit-temporal-residual-bound-utility-artifact-contract-v2"
)
FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION = "DEC-188"
FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_RESULT_EVIDENCE_VERSION = 1

DEC187_MERGED_COMMIT = "1c56ec7241d5795791ac83f1b58ac875b74e9645"
DEC188_TRAINING_CORE_BLOB_SHA = "4f3f189c104d41352433397421f021896c03a5e9"

AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED = False
FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_FIT_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
SHADOW_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _sha256(value: str | bytes) -> str:
    payload = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(payload).hexdigest()


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a sha256 hex digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be a sha256 hex digest") from exc
    return value


def _finite(value: object, *, field: str) -> float:
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(float(value))
    ):
        raise ValueError(f"{field} must be finite")
    return float(value)


def validate_fit_temporal_residual_bound_utility_artifact_contract_sources(
    *, repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    path = root / "src/fmp/market_learning/model_successor_fit_temporal_residual_bound_utility_training.py"
    if not path.is_file():
        raise ValueError(f"missing EXP-054 training dependency: {path}")
    actual = _git_blob_sha(path)
    if actual != DEC188_TRAINING_CORE_BLOB_SHA:
        raise ValueError(
            f"EXP-054 training-core Git blob mismatch: {actual} != {DEC188_TRAINING_CORE_BLOB_SHA}"
        )
    training = validate_fit_temporal_residual_bound_utility_training_sources(
        repository_root=root
    )
    if training["fit_temporal_residual_bound_utility_training_core_decision"] != (
        FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_DECISION
    ):
        raise ValueError("EXP-054 training-core decision drift")
    fingerprint = fit_temporal_residual_bound_utility_protocol_fingerprint()
    if len(fingerprint) != 64:
        raise ValueError("EXP-054 protocol fingerprint invalid")
    return {
        "artifact_contract_version": FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION,
        "artifact_contract_decision": FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
        "dec187_merged_commit": DEC187_MERGED_COMMIT,
        "dec188_training_core_blob_sha": actual,
        "protocol_fingerprint": fingerprint,
        "authoritative_result_execution_authorized": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "trading_authorized": False,
    }


def _expected_views() -> dict[str, dict[str, object]]:
    return {
        str(raw["name"]): {
            "included_regimes": tuple(str(x) for x in raw["included_regimes"]),
            "excluded_regime": str(raw["excluded_regime"]),
        }
        for raw in FIT_JACKKNIFE_VIEWS
    }


def _expected_windows() -> dict[str, dict[str, dict[str, object]]]:
    out: dict[str, dict[str, dict[str, object]]] = {}
    for raw in FIT_TEMPORAL_SUPPORT_WINDOWS:
        parent = str(raw["parent_regime"])
        out.setdefault(parent, {})[str(raw["name"])] = dict(raw)
    return out


def validate_fit_temporal_residual_references(fit: Mapping[str, object]) -> int:
    refs = fit.get("fit_temporal_residual_references")
    views = _expected_views()
    windows = _expected_windows()
    if not isinstance(refs, Mapping) or set(refs) != set(views):
        raise ValueError("EXP-054 residual reference view inventory mismatch")
    verified = 0
    for view_name, expected in views.items():
        record = refs.get(view_name)
        if not isinstance(record, Mapping):
            raise ValueError("EXP-054 residual reference view malformed")
        if record.get("status") != "FROZEN":
            raise ValueError("EXP-054 residual reference status mismatch")
        if tuple(record.get("included_regimes", ())) != expected["included_regimes"]:
            raise ValueError("EXP-054 residual included-regime mismatch")
        excluded = str(expected["excluded_regime"])
        if record.get("excluded_regime") != excluded:
            raise ValueError("EXP-054 residual excluded-regime mismatch")
        targets = record.get("targets")
        if not isinstance(targets, Mapping) or set(targets) != set(FINANCIAL_TARGET_COLUMNS):
            raise ValueError("EXP-054 residual target inventory mismatch")
        for target in FINANCIAL_TARGET_COLUMNS:
            target_windows = targets.get(target)
            if not isinstance(target_windows, Mapping) or set(target_windows) != set(windows[excluded]):
                raise ValueError("EXP-054 residual window inventory mismatch")
            for name, supplied in target_windows.items():
                if not isinstance(supplied, Mapping):
                    raise ValueError("EXP-054 residual window malformed")
                expected_window = windows[excluded][name]
                if (
                    supplied.get("status") != "FROZEN"
                    or supplied.get("name") != name
                    or supplied.get("parent_regime") != excluded
                    or supplied.get("start") != expected_window["start"]
                    or supplied.get("end_exclusive") != expected_window["end_exclusive"]
                    or supplied.get("target_column") != target
                ):
                    raise ValueError("EXP-054 residual window identity mismatch")
                row_count = supplied.get("row_count")
                if not isinstance(row_count, int) or isinstance(row_count, bool) or row_count <= 0:
                    raise ValueError("EXP-054 residual row count invalid")
                _validate_sha256(supplied.get("prediction_digest"), field="prediction digest")
                _validate_sha256(supplied.get("sorted_residual_digest"), field="residual digest")
                _finite(supplied.get("downside_residual"), field="downside residual")
                verified += 1
    if (
        fit.get("fit_temporal_residual_reference_count")
        != FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL
        or verified != FIT_TEMPORAL_RESIDUAL_REFERENCE_COUNT_PER_CELL
    ):
        raise ValueError("EXP-054 residual reference count mismatch")
    return verified


def validate_residual_bound_cutoff(raw: Mapping[str, object]) -> tuple[float, ...]:
    fields = (
        "selection_derived_residual_bound_cutoff",
        "selection_derived_feature_support_cutoff",
        "selection_derived_support_cutoff",
        "selection_derived_pooled_calibrated_cutoff",
        "selection_derived_raw_cutoff",
    )
    values = tuple(_finite(raw.get(field), field=field) for field in fields)
    for value in values[1:4]:
        if not 0.0 <= value <= 1.0:
            raise ValueError("EXP-054 support/calibration cutoff out of range")
    if values[4] <= 0.0:
        raise ValueError("EXP-054 raw cutoff must be positive")
    return values


def compile_fit_temporal_residual_bound_utility_model_result_evidence(
    cells: list[Mapping[str, object]], *, code_commit: str
) -> dict[str, object]:
    if len(code_commit) != 40:
        raise ValueError("EXP-054 code commit must be full SHA")
    identities = []
    residual_count = 0
    for row in cells:
        cell = row.get("cell")
        fit = row.get("fit")
        if not isinstance(cell, Mapping) or not isinstance(fit, Mapping):
            raise ValueError("EXP-054 cell evidence malformed")
        identities.append((cell.get("symbol"), cell.get("timeframe"), cell.get("horizon_minutes")))
        residual_count += validate_fit_temporal_residual_references(fit)
    expected = {(c.symbol, c.timeframe, c.horizon_minutes) for c in MODEL_CELLS}
    if len(cells) != len(MODEL_CELLS) or set(identities) != expected or len(set(identities)) != len(identities):
        raise ValueError("EXP-054 model-result cell evidence incomplete")
    payload = {
        "evidence_version": FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_RESULT_EVIDENCE_VERSION,
        "experiment_id": FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_EXPERIMENT_ID,
        "protocol_version": FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_PROTOCOL_VERSION,
        "protocol_decision": FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_PROTOCOL_DECISION,
        "training_core_version": FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_VERSION,
        "training_core_decision": FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_TRAINING_CORE_DECISION,
        "artifact_contract_decision": FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION,
        "code_commit": code_commit,
        "cell_count": len(cells),
        "verified_fit_temporal_residual_reference_count": residual_count,
        "cells": [dict(row) for row in cells],
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }
    payload["evidence_fingerprint"] = _sha256(_canonical_json(payload))
    return payload


def write_fit_temporal_residual_bound_utility_model_result_evidence(
    evidence: Mapping[str, object],
    *,
    path: Path,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        dict(evidence),
        sort_keys=True,
        indent=2,
        allow_nan=False,
    ) + "\n"
    if (
        destination.exists()
        and destination.read_text(encoding="utf-8") != payload
    ):
        raise ValueError(
            "conflicting existing EXP-054 model-result evidence"
        )
    destination.write_text(payload, encoding="utf-8")


def run_authoritative_fit_temporal_residual_bound_utility_model_bundle(**_: object) -> dict[str, object]:
    if AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED is not True:
        raise PermissionError(
            "DEC-188 source is non-executable for authoritative EXP-054 model fitting"
        )
    raise PermissionError("EXP-054 authoritative runner is not armed")


__all__ = [
    "AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "DEC186_MERGED_COMMIT",
    "DEC188_TRAINING_CORE_BLOB_SHA",
    "FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION",
    "FIT_TEMPORAL_RESIDUAL_BOUND_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION",
    "compile_fit_temporal_residual_bound_utility_model_result_evidence",
    "run_authoritative_fit_temporal_residual_bound_utility_model_bundle",
    "validate_fit_temporal_residual_bound_utility_artifact_contract_sources",
    "validate_fit_temporal_residual_references",
    "validate_residual_bound_cutoff",
    "write_fit_temporal_residual_bound_utility_model_result_evidence",
]
