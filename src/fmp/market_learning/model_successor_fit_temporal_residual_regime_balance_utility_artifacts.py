from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Mapping

from .model_protocol import MODEL_CELLS
from .model_successor_density_protocol import CANDIDATE_BUDGET_ANCHORS
from .model_successor_fit_temporal_feature_support_utility_protocol import (
    FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL,
)
from .model_successor_fit_temporal_residual_bound_utility_artifacts import (
    validate_fit_temporal_residual_references,
)
from .model_successor_fit_temporal_residual_breadth_utility_protocol import (
    FIT_TEMPORAL_RESIDUAL_BREADTH_BOUND_COUNT_PER_ROW,
)
from .model_successor_fit_temporal_residual_lower_tail_utility_protocol import (
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_BOUND_COUNT_PER_ROW,
    FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_COUNT,
)
from .model_successor_fit_temporal_residual_regime_floor_utility_protocol import (
    FIT_TEMPORAL_RESIDUAL_REGIME_COUNT,
    FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_BOUND_COUNT_PER_ROW,
    FIT_TEMPORAL_RESIDUAL_WINDOWS_PER_REGIME,
)
from .model_successor_fit_temporal_residual_regime_balance_utility_protocol import (
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_PENALTY_MULTIPLIER,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_REGIME_COUNT,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_SOURCE_BOUND_COUNT_PER_ROW,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_EXPERIMENT_ID,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_PROTOCOL_DECISION,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_PROTOCOL_VERSION,
    fit_temporal_residual_regime_balance_utility_protocol_fingerprint,
)
from .model_successor_fit_temporal_residual_regime_balance_utility_training import (
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_TRAINING_CORE_DECISION,
    FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_TRAINING_CORE_VERSION,
    validate_fit_temporal_residual_regime_balance_utility_training_sources,
)
from .model_successor_fit_temporal_support_utility_protocol import (
    FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL,
)
from .model_successor_regime_utility_artifacts import (
    _canonical_json,
    _git_blob_sha,
)
from .model_successor_temporal_jackknife_utility_protocol import (
    TOTAL_REGRESSORS_PER_CELL,
)


FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION = (
    "fmp-exp059-fit-temporal-residual-regime-balance-utility-artifact-contract-v1"
)
FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION = (
    "DEC-244"
)
FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_RESULT_EVIDENCE_VERSION = 1

DEC243_MERGED_COMMIT = "9f427f06f315288bd9b132de19901beb5a5ddfc8"
DEC243_TRAINING_CORE_BLOB_SHA = (
    "4f99c1d0cb18551b67cc89357ad4a3940c190cd2"
)
PREDECESSOR_ARTIFACT_CONTRACT_BLOB_SHA = (
    "5a34f354b68e14bb7116c79f15f9cfebe149a811"
)

AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED = False
FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_FIT_AUTHORIZED = False
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
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _finite(value: object, *, field: str) -> float:
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(float(value))
    ):
        raise ValueError(f"{field} must be finite")
    return float(value)


def validate_fit_temporal_residual_regime_balance_utility_artifact_contract_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "dec243_training_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_regime_balance_utility_training.py",
            DEC243_TRAINING_CORE_BLOB_SHA,
        ),
        "predecessor_artifact_contract": (
            root
            / "src/fmp/market_learning/"
            "model_successor_fit_temporal_residual_regime_floor_utility_artifacts.py",
            PREDECESSOR_ARTIFACT_CONTRACT_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing EXP-059 artifact dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-059 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    training = (
        validate_fit_temporal_residual_regime_balance_utility_training_sources(
            repository_root=root,
        )
    )
    if training[
        "fit_temporal_residual_regime_balance_utility_training_core_decision"
    ] != FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_TRAINING_CORE_DECISION:
        raise ValueError("EXP-059 training-core decision drift")

    fingerprint = fit_temporal_residual_regime_balance_utility_protocol_fingerprint()
    if len(fingerprint) != 64:
        raise ValueError("EXP-059 protocol fingerprint invalid")

    return {
        "artifact_contract_version": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION
        ),
        "artifact_contract_decision": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION
        ),
        "dec243_merged_commit": DEC243_MERGED_COMMIT,
        "dec243_training_core_blob_sha": actual["dec243_training_core"],
        "predecessor_artifact_contract_blob_sha": actual[
            "predecessor_artifact_contract"
        ],
        "protocol_fingerprint": fingerprint,
        "authoritative_result_execution_authorized": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }


def validate_residual_regime_balance_cutoff(
    raw: Mapping[str, object],
) -> tuple[float, ...]:
    fields = (
        "selection_derived_residual_regime_balance_cutoff",
        "selection_derived_residual_regime_floor_cutoff",
        "selection_derived_residual_lower_tail_cutoff",
        "selection_derived_residual_breadth_cutoff",
        "selection_derived_residual_bound_cutoff",
        "selection_derived_feature_support_cutoff",
        "selection_derived_support_cutoff",
        "selection_derived_pooled_calibrated_cutoff",
        "selection_derived_raw_cutoff",
    )
    values = tuple(
        _finite(raw.get(field), field=field)
        for field in fields
    )
    if not 0.0 <= values[3] <= 1.0:
        raise ValueError("EXP-059 residual-breadth cutoff out of range")
    for value in values[5:8]:
        if not 0.0 <= value <= 1.0:
            raise ValueError(
                "EXP-059 support/calibration cutoff out of range"
            )
    if values[8] <= 0.0:
        raise ValueError("EXP-059 raw cutoff must be positive")
    return values


def _validate_cell_fingerprint(row: Mapping[str, object]) -> None:
    supplied = dict(row)
    fingerprint = supplied.pop("result_fingerprint", None)
    expected = _sha256(_canonical_json(supplied))
    if _validate_sha256(
        fingerprint,
        field="EXP-059 cell result fingerprint",
    ) != expected:
        raise ValueError("EXP-059 cell result fingerprint mismatch")


def _validate_fit_block(fit: Mapping[str, object]) -> dict[str, int]:
    exact = {
        "regressor_count": TOTAL_REGRESSORS_PER_CELL,
        "calibration_reference_count": TOTAL_REGRESSORS_PER_CELL,
        "fit_temporal_support_reference_count": (
            FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL
        ),
        "fit_temporal_feature_support_reference_count": (
            FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL
        ),
        "fit_temporal_residual_reference_count": 24,
        "fit_temporal_residual_breadth_bound_count_per_row": (
            FIT_TEMPORAL_RESIDUAL_BREADTH_BOUND_COUNT_PER_ROW
        ),
        "fit_temporal_residual_lower_tail_bound_count_per_row": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_BOUND_COUNT_PER_ROW
        ),
        "fit_temporal_residual_lower_tail_count": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_COUNT
        ),
        "fit_temporal_residual_regime_count": (
            FIT_TEMPORAL_RESIDUAL_REGIME_COUNT
        ),
        "fit_temporal_residual_windows_per_regime": (
            FIT_TEMPORAL_RESIDUAL_WINDOWS_PER_REGIME
        ),
        "fit_temporal_residual_regime_floor_bound_count_per_row": (
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_BOUND_COUNT_PER_ROW
        ),
        "fit_temporal_residual_regime_balance_regime_count": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_REGIME_COUNT
        ),
        "fit_temporal_residual_regime_balance_source_bound_count_per_row": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_SOURCE_BOUND_COUNT_PER_ROW
        ),
        "fit_temporal_residual_regime_balance_penalty_multiplier": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_PENALTY_MULTIPLIER
        ),
    }
    for field, expected in exact.items():
        if fit.get(field) != expected:
            raise ValueError(f"EXP-059 {field} mismatch")

    residual_count = validate_fit_temporal_residual_references(fit)
    if residual_count != 24:
        raise ValueError("EXP-059 residual reference count mismatch")

    return {
        "verified_regressor_count": TOTAL_REGRESSORS_PER_CELL,
        "verified_pooled_calibration_reference_count": (
            TOTAL_REGRESSORS_PER_CELL
        ),
        "verified_fit_temporal_support_reference_count": (
            FIT_TEMPORAL_SUPPORT_REFERENCE_COUNT_PER_CELL
        ),
        "verified_fit_temporal_feature_support_reference_count": (
            FIT_TEMPORAL_FEATURE_SUPPORT_REFERENCE_COUNT_PER_CELL
        ),
        "verified_fit_temporal_residual_reference_count": residual_count,
    }


def _validate_selection_block(selection: Mapping[str, object]) -> None:
    diagnostics = selection.get(
        "fit_temporal_residual_regime_balance_utility_consensus"
    )
    if not isinstance(diagnostics, Mapping):
        raise ValueError("EXP-059 consensus diagnostics missing")
    if diagnostics.get(
        "fit_temporal_residual_breadth_bound_count_per_row"
    ) != FIT_TEMPORAL_RESIDUAL_BREADTH_BOUND_COUNT_PER_ROW:
        raise ValueError("EXP-059 breadth bound count mismatch")
    if diagnostics.get(
        "fit_temporal_residual_lower_tail_bound_count_per_row"
    ) != FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_BOUND_COUNT_PER_ROW:
        raise ValueError("EXP-059 lower-tail bound count mismatch")
    if diagnostics.get(
        "fit_temporal_residual_lower_tail_count"
    ) != FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_COUNT:
        raise ValueError("EXP-059 lower-tail count mismatch")
    if diagnostics.get(
        "fit_temporal_residual_regime_count"
    ) != FIT_TEMPORAL_RESIDUAL_REGIME_COUNT:
        raise ValueError("EXP-059 residual regime count mismatch")
    if diagnostics.get(
        "fit_temporal_residual_windows_per_regime"
    ) != FIT_TEMPORAL_RESIDUAL_WINDOWS_PER_REGIME:
        raise ValueError("EXP-059 residual windows-per-regime mismatch")
    if diagnostics.get(
        "fit_temporal_residual_regime_floor_bound_count_per_row"
    ) != FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_BOUND_COUNT_PER_ROW:
        raise ValueError("EXP-059 regime-floor bound count mismatch")
    if diagnostics.get(
        "fit_temporal_residual_regime_balance_regime_count"
    ) != FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_REGIME_COUNT:
        raise ValueError("EXP-059 regime-balance regime count mismatch")
    if diagnostics.get(
        "fit_temporal_residual_regime_balance_source_bound_count_per_row"
    ) != FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_SOURCE_BOUND_COUNT_PER_ROW:
        raise ValueError("EXP-059 regime-balance source-bound count mismatch")
    if diagnostics.get(
        "fit_temporal_residual_regime_balance_penalty_multiplier"
    ) != FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_PENALTY_MULTIPLIER:
        raise ValueError("EXP-059 regime-balance penalty multiplier mismatch")
    if diagnostics.get(
        "fit_temporal_residual_reference_count"
    ) != 24:
        raise ValueError("EXP-059 consensus residual reference count mismatch")

    for field in (
        "minimum_fit_temporal_residual_breadth",
        "maximum_fit_temporal_residual_breadth",
    ):
        value = diagnostics.get(field)
        if value is not None:
            numeric = _finite(value, field=field)
            if not 0.0 <= numeric <= 1.0:
                raise ValueError(
                    "EXP-059 consensus breadth diagnostic out of range"
                )

    for field in (
        "minimum_fit_temporal_residual_lower_tail_mean",
        "maximum_fit_temporal_residual_lower_tail_mean",
        "minimum_fit_temporal_residual_regime_floor_utility",
        "maximum_fit_temporal_residual_regime_floor_utility",
        "minimum_fit_temporal_residual_regime_balance_utility",
        "maximum_fit_temporal_residual_regime_balance_utility",
    ):
        value = diagnostics.get(field)
        if value is not None:
            _finite(value, field=field)

    _validate_sha256(
        selection.get(
            "fit_temporal_residual_regime_balance_utility_consensus_digest"
        ),
        field="EXP-059 consensus digest",
    )

    variants = selection.get("variants")
    if not isinstance(variants, list) or len(variants) != len(
        CANDIDATE_BUDGET_ANCHORS
    ):
        raise ValueError("EXP-059 selection variant inventory mismatch")
    if {
        row.get("candidate_budget_anchor")
        for row in variants
        if isinstance(row, Mapping)
    } != set(CANDIDATE_BUDGET_ANCHORS):
        raise ValueError("EXP-059 selection budget identity mismatch")

    cutoff_fields = (
        "selection_derived_residual_regime_balance_cutoff",
        "selection_derived_residual_regime_floor_cutoff",
        "selection_derived_residual_lower_tail_cutoff",
        "selection_derived_residual_breadth_cutoff",
        "selection_derived_residual_bound_cutoff",
        "selection_derived_feature_support_cutoff",
        "selection_derived_support_cutoff",
        "selection_derived_pooled_calibrated_cutoff",
        "selection_derived_raw_cutoff",
    )
    for row in variants:
        if not isinstance(row, Mapping):
            raise ValueError("EXP-059 selection variant malformed")
        status = row.get("status")
        evaluation = row.get("evaluation_status")
        if status == "BUDGET_UNAVAILABLE":
            if evaluation != "BUDGET_UNAVAILABLE":
                raise ValueError("EXP-059 unavailable variant status drift")
            if any(row.get(field) is not None for field in cutoff_fields):
                raise ValueError(
                    "EXP-059 unavailable variant exposes cutoff"
                )
            if row.get("selection_gate_passed") is not False:
                raise ValueError(
                    "EXP-059 unavailable variant cannot pass selection"
                )
            continue

        if status != "AVAILABLE" or evaluation != "EVALUATED":
            raise ValueError("EXP-059 evaluated variant status drift")
        validate_residual_regime_balance_cutoff(row)
        if not isinstance(row.get("scenarios"), Mapping):
            raise ValueError("EXP-059 evaluated variant scenarios missing")
        if not isinstance(row.get("temporal_stability"), Mapping):
            raise ValueError("EXP-059 temporal stability evidence missing")

    selected = selection.get("selected_variant")
    status = selection.get("status")
    if selected is None:
        if status != (
            "NO_FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_"
            "STABLE_MODEL_CHALLENGER"
        ):
            raise ValueError("EXP-059 no-selection status mismatch")
    else:
        if not isinstance(selected, Mapping):
            raise ValueError("EXP-059 selected variant malformed")
        if status != "SELECTED":
            raise ValueError("EXP-059 selected status mismatch")
        if selected.get("candidate_budget_anchor") not in (
            CANDIDATE_BUDGET_ANCHORS
        ):
            raise ValueError("EXP-059 selected budget mismatch")
        validate_residual_regime_balance_cutoff(selected)


def _validate_cell(
    row: Mapping[str, object],
) -> dict[str, int]:
    if row.get("experiment_id") != (
        FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_EXPERIMENT_ID
    ):
        raise ValueError("EXP-059 cell experiment identity mismatch")
    if row.get("protocol_decision") != (
        FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_PROTOCOL_DECISION
    ):
        raise ValueError("EXP-059 cell protocol decision mismatch")
    if row.get("training_core_decision") != (
        FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_TRAINING_CORE_DECISION
    ):
        raise ValueError("EXP-059 cell training decision mismatch")
    if row.get("dec242_merged_commit") != (
        "a14afb226722d168c3d899d7079776388161a52d"
    ):
        raise ValueError("EXP-059 cell DEC-242 merge identity mismatch")
    if row.get("dec242_protocol_blob_sha") != (
        "cd4e790098a5c8d99ea2aa5264465b5d4b6b6acc"
    ):
        raise ValueError("EXP-059 cell regime-balance protocol blob mismatch")
    if row.get("predecessor_training_core_blob_sha") != (
        "77f2010574b3d8ecc958930d5bfadf7ddb4f2231"
    ):
        raise ValueError("EXP-059 cell predecessor training-core blob mismatch")

    cell = row.get("cell")
    fit = row.get("fit")
    selection = row.get("selection")
    validation = row.get("validation")
    holdout = row.get("retrospective_holdout")
    if (
        not isinstance(cell, Mapping)
        or not isinstance(fit, Mapping)
        or not isinstance(selection, Mapping)
        or not isinstance(validation, Mapping)
        or not isinstance(holdout, Mapping)
    ):
        raise ValueError("EXP-059 cell evidence malformed")

    counts = _validate_fit_block(fit)
    _validate_selection_block(selection)
    _validate_cell_fingerprint(row)

    if selection.get("selected_variant") is None:
        if validation.get("status") != "LOCKED_NO_SELECTION":
            raise ValueError("EXP-059 validation lock mismatch")
        if holdout.get("status") != "LOCKED_NO_SELECTION":
            raise ValueError("EXP-059 holdout lock mismatch")

    for field in (
        "model_fit_authorized",
        "promotion_authorized",
        "shadow_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "trading_authorized",
    ):
        if row.get(field) is not False:
            raise ValueError(f"EXP-059 cell {field} must remain false")

    return counts


def compile_fit_temporal_residual_regime_balance_utility_model_result_evidence(
    cells: list[Mapping[str, object]],
    *,
    code_commit: str,
) -> dict[str, object]:
    commit = _validate_commit(
        code_commit,
        field="EXP-059 code commit",
    )
    expected = {
        (cell.symbol, cell.timeframe, cell.horizon_minutes)
        for cell in MODEL_CELLS
    }
    identities: list[tuple[object, object, object]] = []
    totals = {
        "verified_regressor_count": 0,
        "verified_pooled_calibration_reference_count": 0,
        "verified_fit_temporal_support_reference_count": 0,
        "verified_fit_temporal_feature_support_reference_count": 0,
        "verified_fit_temporal_residual_reference_count": 0,
    }

    for row in cells:
        counts = _validate_cell(row)
        identity = row["cell"]
        assert isinstance(identity, Mapping)
        identities.append(
            (
                identity.get("symbol"),
                identity.get("timeframe"),
                identity.get("horizon_minutes"),
            )
        )
        for field, count in counts.items():
            totals[field] += int(count)

    if (
        len(cells) != len(MODEL_CELLS)
        or set(identities) != expected
        or len(set(identities)) != len(identities)
    ):
        raise ValueError("EXP-059 model-result cell evidence incomplete")

    expected_totals = {
        "verified_regressor_count": 108,
        "verified_pooled_calibration_reference_count": 108,
        "verified_fit_temporal_support_reference_count": 432,
        "verified_fit_temporal_feature_support_reference_count": 216,
        "verified_fit_temporal_residual_reference_count": 432,
    }
    if totals != expected_totals:
        raise ValueError("EXP-059 aggregate evidence counts mismatch")

    payload = {
        "evidence_version": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_RESULT_EVIDENCE_VERSION
        ),
        "experiment_id": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_EXPERIMENT_ID
        ),
        "protocol_version": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_PROTOCOL_VERSION
        ),
        "protocol_decision": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_PROTOCOL_DECISION
        ),
        "training_core_version": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_TRAINING_CORE_DECISION
        ),
        "artifact_contract_decision": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION
        ),
        "code_commit": commit,
        "cell_count": len(cells),
        **totals,
        "verified_fit_temporal_residual_breadth_bound_count_per_row": (
            FIT_TEMPORAL_RESIDUAL_BREADTH_BOUND_COUNT_PER_ROW
        ),
        "verified_fit_temporal_residual_lower_tail_bound_count_per_row": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_BOUND_COUNT_PER_ROW
        ),
        "verified_fit_temporal_residual_lower_tail_count": (
            FIT_TEMPORAL_RESIDUAL_LOWER_TAIL_COUNT
        ),
        "verified_fit_temporal_residual_regime_count": (
            FIT_TEMPORAL_RESIDUAL_REGIME_COUNT
        ),
        "verified_fit_temporal_residual_windows_per_regime": (
            FIT_TEMPORAL_RESIDUAL_WINDOWS_PER_REGIME
        ),
        "verified_fit_temporal_residual_regime_floor_bound_count_per_row": (
            FIT_TEMPORAL_RESIDUAL_REGIME_FLOOR_BOUND_COUNT_PER_ROW
        ),
        "verified_fit_temporal_residual_regime_balance_regime_count": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_REGIME_COUNT
        ),
        "verified_fit_temporal_residual_regime_balance_source_bound_count_per_row": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_SOURCE_BOUND_COUNT_PER_ROW
        ),
        "verified_fit_temporal_residual_regime_balance_penalty_multiplier": (
            FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_PENALTY_MULTIPLIER
        ),
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
    payload["evidence_fingerprint"] = _sha256(
        _canonical_json(payload)
    )
    return payload


def write_fit_temporal_residual_regime_balance_utility_model_result_evidence(
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
            "conflicting existing EXP-059 model-result evidence"
        )
    destination.write_text(payload, encoding="utf-8")


def run_authoritative_fit_temporal_residual_regime_balance_utility_model_bundle(
    **_: object,
) -> dict[str, object]:
    if (
        AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "DEC-244 source is non-executable for authoritative "
            "EXP-059 model fitting"
        )
    raise PermissionError("EXP-059 authoritative runner is not armed")


__all__ = [
    "AUTHORITATIVE_FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "DEC243_MERGED_COMMIT",
    "DEC243_TRAINING_CORE_BLOB_SHA",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_ARTIFACT_RUNNER_DECISION",
    "FIT_TEMPORAL_RESIDUAL_REGIME_BALANCE_UTILITY_MODEL_ARTIFACT_RUNNER_VERSION",
    "compile_fit_temporal_residual_regime_balance_utility_model_result_evidence",
    "run_authoritative_fit_temporal_residual_regime_balance_utility_model_bundle",
    "validate_fit_temporal_residual_regime_balance_utility_artifact_contract_sources",
    "validate_residual_regime_balance_cutoff",
    "write_fit_temporal_residual_regime_balance_utility_model_result_evidence",
]
