from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping, Sequence

from .contracts import EVIDENCE_LABEL
from .model_artifacts import (
    AUTHORITATIVE_FEATURE_ARTIFACTS,
    AUTHORITATIVE_FEATURE_EVIDENCE_ARTIFACT_ID,
    AUTHORITATIVE_FEATURE_EVIDENCE_FINGERPRINT,
    AUTHORITATIVE_FEATURE_RUN_ID,
    AUTHORITATIVE_OUTCOME_ARTIFACTS,
    AUTHORITATIVE_OUTCOME_EVIDENCE_ARTIFACT_ID,
    AUTHORITATIVE_OUTCOME_EVIDENCE_FINGERPRINT,
    AUTHORITATIVE_OUTCOME_RUN_ID,
    AUTHORITATIVE_READINESS_ARTIFACT_ID,
    AUTHORITATIVE_READINESS_FINGERPRINT,
    VerifiedCellArtifacts,
    load_authoritative_cell_artifacts,
    validate_authoritative_readiness,
)
from .model_protocol import (
    CONFIDENCE_THRESHOLDS,
    MODEL_CELLS,
    MODEL_FAMILIES,
)
from .model_run_failure_review import (
    MODEL_RUN_FAILURE_REVIEW_DECISION,
    REVIEWED_FAILED_MODEL_HEAD_SHA,
    REVIEWED_FAILED_MODEL_RUN_ID,
)
from .model_successor_protocol import (
    BASE_PROTOCOL_FINGERPRINT,
    PREDECESSOR_FAILED_MODEL_HEAD_SHA,
    PREDECESSOR_FAILED_MODEL_RUN_ID,
    PREDECESSOR_FAILURE_REVIEW_DECISION,
    PRIOR_RESULT_INFORMED,
    SUCCESSOR_EXPERIMENT_ID,
    SUCCESSOR_PROTOCOL_DECISION,
    SUCCESSOR_PROTOCOL_VERSION,
    UNTOUCHED_OOS,
    successor_protocol_fingerprint,
)
from .model_successor_training import (
    BASE_TRAINING_CORE_BLOB_SHA,
    SUCCESSOR_TRAINING_CORE_DECISION,
    SUCCESSOR_TRAINING_CORE_VERSION,
    run_successor_model_cell_core,
)


SUCCESSOR_MODEL_ARTIFACT_RUNNER_VERSION = (
    "fmp-exp045-model-artifact-runner-v1"
)
SUCCESSOR_MODEL_ARTIFACT_RUNNER_DECISION = "DEC-097"

SUCCESSOR_PROTOCOL_COMMIT = (
    "f9c8a069076e1612c5d140dc85dffb83e100da6b"
)
SUCCESSOR_TRAINING_CORE_COMMIT = (
    "f30a233bdc8229b9141ce3aa7c8e1b57a598c437"
)

LEGACY_DATA_LOADER_BLOB_SHA = (
    "27c0848d16722a22b4762f5842396c2aebc92bec"
)
FAILURE_REVIEW_BLOB_SHA = (
    "2260ad4ad08a7e9874bd28030be977a3e71436f9"
)
SUCCESSOR_PROTOCOL_BLOB_SHA = (
    "44129fc5337fb55b9c7d81f5ba0561ea788bd264"
)
SUCCESSOR_TRAINING_CORE_BLOB_SHA = (
    "3f0bc1bfa9640d08175e72cdf131bb97c94d562c"
)

AUTHORITATIVE_SUCCESSOR_MODEL_RESULT_EXECUTION_AUTHORIZED = False
SUCCESSOR_MODEL_FIT_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
SHADOW_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False

SUCCESSOR_MODEL_RESULT_EVIDENCE_VERSION = 1


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _git_blob_sha(path: Path) -> str:
    payload = Path(path).read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character sha256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def validate_successor_artifact_runner_sources(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    expected = {
        "legacy_data_loader": (
            root / "src/fmp/market_learning/model_artifacts.py",
            LEGACY_DATA_LOADER_BLOB_SHA,
        ),
        "failure_review": (
            root
            / "src/fmp/market_learning/"
            "model_run_failure_review.py",
            FAILURE_REVIEW_BLOB_SHA,
        ),
        "successor_protocol": (
            root
            / "src/fmp/market_learning/"
            "model_successor_protocol.py",
            SUCCESSOR_PROTOCOL_BLOB_SHA,
        ),
        "successor_training_core": (
            root
            / "src/fmp/market_learning/"
            "model_successor_training.py",
            SUCCESSOR_TRAINING_CORE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(
                f"missing EXP-045 artifact-runner dependency: {path}"
            )
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"EXP-045 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha

    if MODEL_RUN_FAILURE_REVIEW_DECISION != (
        PREDECESSOR_FAILURE_REVIEW_DECISION
    ):
        raise ValueError(
            "EXP-045 predecessor failure-review decision drift"
        )
    if REVIEWED_FAILED_MODEL_RUN_ID != (
        PREDECESSOR_FAILED_MODEL_RUN_ID
    ):
        raise ValueError(
            "EXP-045 predecessor failed-run id drift"
        )
    if REVIEWED_FAILED_MODEL_HEAD_SHA != (
        PREDECESSOR_FAILED_MODEL_HEAD_SHA
    ):
        raise ValueError(
            "EXP-045 predecessor failed-run head SHA drift"
        )

    protocol_fingerprint = successor_protocol_fingerprint()
    return {
        "successor_model_artifact_runner_version": (
            SUCCESSOR_MODEL_ARTIFACT_RUNNER_VERSION
        ),
        "successor_model_artifact_runner_decision": (
            SUCCESSOR_MODEL_ARTIFACT_RUNNER_DECISION
        ),
        "legacy_data_loader_blob_sha": actual[
            "legacy_data_loader"
        ],
        "failure_review_blob_sha": actual[
            "failure_review"
        ],
        "successor_protocol_blob_sha": actual[
            "successor_protocol"
        ],
        "successor_training_core_blob_sha": actual[
            "successor_training_core"
        ],
        "successor_protocol_fingerprint": (
            protocol_fingerprint
        ),
        "authoritative_successor_model_result_execution_authorized": False,
        "successor_model_fit_authorized": False,
        "promotion_authorized": False,
        "trading_authorized": False,
    }


def _validate_status_chain(
    *,
    selection: object,
    validation: object,
    holdout: object,
) -> None:
    if selection == "NO_MODEL_FAMILY_AVAILABLE":
        if validation != "LOCKED_NO_MODEL_FAMILY":
            raise ValueError(
                "EXP-045 no-family cell must keep validation locked"
            )
        if holdout != "LOCKED_NO_MODEL_FAMILY":
            raise ValueError(
                "EXP-045 no-family cell must keep holdout locked"
            )
        return

    if selection == "NO_MODEL_CHALLENGER":
        if validation != "LOCKED_NO_SELECTION":
            raise ValueError(
                "EXP-045 no-challenger cell must keep validation locked"
            )
        if holdout != "LOCKED_NO_SELECTION":
            raise ValueError(
                "EXP-045 no-challenger cell must keep holdout locked"
            )
        return

    if selection != "SELECTED":
        raise ValueError(
            f"unexpected EXP-045 selection status: {selection!r}"
        )

    if validation == "REJECT":
        if holdout != "LOCKED_VALIDATION_REJECT":
            raise ValueError(
                "EXP-045 rejected validation must keep holdout locked"
            )
        return

    if validation == "PASS":
        if holdout not in {"PASS", "REJECT"}:
            raise ValueError(
                "EXP-045 passed validation must produce a holdout result"
            )
        return

    raise ValueError(
        f"unexpected EXP-045 validation status: {validation!r}"
    )


def _validate_successor_cell_result(
    result: Mapping[str, object],
) -> dict[str, object]:
    cell = result.get("cell")
    if not isinstance(cell, Mapping):
        raise ValueError(
            "EXP-045 model result is missing cell identity"
        )
    horizon = cell.get("horizon_minutes")
    if (
        not isinstance(horizon, int)
        or isinstance(horizon, bool)
    ):
        raise ValueError(
            "EXP-045 model result horizon is malformed"
        )
    identity = (
        str(cell.get("symbol")),
        str(cell.get("timeframe")),
        horizon,
    )

    expected_cells = {
        (item.symbol, item.timeframe, item.horizon_minutes)
        for item in MODEL_CELLS
    }
    if identity not in expected_cells:
        raise ValueError(
            f"unexpected EXP-045 model result cell: {identity}"
        )

    exact = {
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "training_core_version": (
            SUCCESSOR_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            SUCCESSOR_TRAINING_CORE_DECISION
        ),
        "base_training_core_blob_sha": (
            BASE_TRAINING_CORE_BLOB_SHA
        ),
        "protocol_decision": SUCCESSOR_PROTOCOL_DECISION,
        "protocol_version": SUCCESSOR_PROTOCOL_VERSION,
        "protocol_fingerprint": (
            successor_protocol_fingerprint()
        ),
        "base_protocol_fingerprint": (
            BASE_PROTOCOL_FINGERPRINT
        ),
        "predecessor_failed_model_run_id": (
            PREDECESSOR_FAILED_MODEL_RUN_ID
        ),
        "prior_result_informed": True,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }
    for field, expected in exact.items():
        if result.get(field) != expected:
            raise ValueError(
                f"EXP-045 model result {field} mismatch"
            )

    fit = result.get("fit")
    if not isinstance(fit, Mapping):
        raise ValueError("EXP-045 model result fit block is malformed")
    families = fit.get("families")
    if not isinstance(families, Mapping):
        raise ValueError(
            "EXP-045 model result family-fit block is malformed"
        )
    if set(families) != {
        "logistic_regression",
        "hist_gradient_boosting",
    }:
        raise ValueError(
            "EXP-045 model result family set mismatch"
        )

    for family, raw in families.items():
        if not isinstance(raw, Mapping):
            raise ValueError(
                f"EXP-045 {family} fit record is malformed"
            )
        status = raw.get("status")
        if status == "FITTED":
            _validate_sha256(
                raw.get("preprocessor_fingerprint"),
                field=f"EXP-045 {family} preprocessor fingerprint",
            )
            _validate_sha256(
                raw.get("model_fingerprint"),
                field=f"EXP-045 {family} model fingerprint",
            )
            if raw.get("fit_attempt_count") != 1:
                raise ValueError(
                    f"EXP-045 {family} fit-attempt count mismatch"
                )
            continue

        if family == "logistic_regression" and status == "FAILED_NON_CONVERGENCE":
            if raw.get("failure_reason") != "LBFGS_MAX_ITER_REACHED":
                raise ValueError(
                    "EXP-045 logistic failure reason mismatch"
                )
            if raw.get("fit_attempt_count") != 1:
                raise ValueError(
                    "EXP-045 logistic fit-attempt count mismatch"
                )
            if raw.get("retry_authorized") is not False:
                raise ValueError(
                    "EXP-045 logistic retry must remain false"
                )
            continue

        raise ValueError(
            f"unexpected EXP-045 {family} fit status: {status!r}"
        )

    selection = result.get("selection")
    validation = result.get("validation")
    holdout = result.get("retrospective_holdout")
    if (
        not isinstance(selection, Mapping)
        or not isinstance(validation, Mapping)
        or not isinstance(holdout, Mapping)
    ):
        raise ValueError(
            "EXP-045 model result chronology blocks are malformed"
        )

    variants = selection.get("variants")
    if not isinstance(variants, list) or len(variants) != 6:
        raise ValueError(
            "EXP-045 model result must preserve six selection variants"
        )

    expected_slots = {
        (family, float(threshold))
        for family in MODEL_FAMILIES
        for threshold in CONFIDENCE_THRESHOLDS
    }
    indexed_variants: dict[
        tuple[str, float],
        Mapping[str, object],
    ] = {}
    for raw in variants:
        if not isinstance(raw, Mapping):
            raise ValueError(
                "EXP-045 model result variant is malformed"
            )
        family = raw.get("model_family")
        threshold = raw.get("confidence_threshold")
        if (
            not isinstance(family, str)
            or not isinstance(threshold, (int, float))
            or isinstance(threshold, bool)
        ):
            raise ValueError(
                "EXP-045 model result variant identity is malformed"
            )
        slot = (family, float(threshold))
        if slot not in expected_slots:
            raise ValueError(
                f"unexpected EXP-045 model variant slot: {slot}"
            )
        if slot in indexed_variants:
            raise ValueError(
                "duplicate EXP-045 model variant slot"
            )

        family_record = families[family]
        assert isinstance(family_record, Mapping)
        family_status = family_record.get("status")
        if raw.get("family_fit_status") != family_status:
            raise ValueError(
                "EXP-045 variant family-fit status mismatch"
            )

        if family_status == "FITTED":
            if raw.get("evaluation_status") != "EVALUATED":
                raise ValueError(
                    "EXP-045 fitted-family variant must be evaluated"
                )
            if not isinstance(
                raw.get("selection_gate_passed"),
                bool,
            ):
                raise ValueError(
                    "EXP-045 evaluated variant gate status is malformed"
                )
        else:
            if family != "logistic_regression":
                raise ValueError(
                    "EXP-045 unavailable family must be logistic regression"
                )
            if raw.get("evaluation_status") != "FAMILY_UNAVAILABLE":
                raise ValueError(
                    "EXP-045 unavailable logistic variant status mismatch"
                )
            if raw.get("failure_reason") != "LBFGS_MAX_ITER_REACHED":
                raise ValueError(
                    "EXP-045 unavailable logistic variant reason mismatch"
                )
            if raw.get("selection_gate_passed") is not False:
                raise ValueError(
                    "EXP-045 unavailable logistic variant cannot pass"
                )
        indexed_variants[slot] = raw

    if set(indexed_variants) != expected_slots:
        raise ValueError(
            "EXP-045 model result variant-slot inventory mismatch"
        )

    selection_status = selection.get("status")
    selected_variant = selection.get("selected_variant")
    if selection_status == "SELECTED":
        if not isinstance(selected_variant, Mapping):
            raise ValueError(
                "EXP-045 selected cell is missing selected variant"
            )
        selected_family = selected_variant.get("model_family")
        selected_threshold = selected_variant.get(
            "confidence_threshold"
        )
        if (
            not isinstance(selected_family, str)
            or not isinstance(
                selected_threshold,
                (int, float),
            )
            or isinstance(selected_threshold, bool)
        ):
            raise ValueError(
                "EXP-045 selected variant identity is malformed"
            )
        selected_slot = (
            selected_family,
            float(selected_threshold),
        )
        chosen = indexed_variants.get(selected_slot)
        if (
            chosen is None
            or chosen.get("selection_gate_passed") is not True
            or chosen.get("family_fit_status") != "FITTED"
        ):
            raise ValueError(
                "EXP-045 selected variant is not an eligible passing slot"
            )
    elif selected_variant is not None:
        raise ValueError(
            "EXP-045 unselected cell must not name a selected variant"
        )

    _validate_status_chain(
        selection=selection.get("status"),
        validation=validation.get("status"),
        holdout=holdout.get("status"),
    )

    result_fingerprint = _validate_sha256(
        result.get("result_fingerprint"),
        field="EXP-045 model cell result fingerprint",
    )
    unsigned = dict(result)
    unsigned.pop("result_fingerprint", None)
    if _sha256(_canonical_json(unsigned)) != result_fingerprint:
        raise ValueError(
            "EXP-045 model cell result fingerprint mismatch"
        )

    return {
        "symbol": identity[0],
        "timeframe": identity[1],
        "horizon_minutes": identity[2],
        "result_fingerprint": result_fingerprint,
        "selection_status": selection.get("status"),
        "validation_status": validation.get("status"),
        "retrospective_holdout_status": holdout.get("status"),
        "logistic_fit_status": families[
            "logistic_regression"
        ].get("status"),
        "hgb_fit_status": families[
            "hist_gradient_boosting"
        ].get("status"),
    }


def compile_successor_model_result_evidence(
    cell_results: Sequence[Mapping[str, object]],
    *,
    code_commit: str,
) -> dict[str, object]:
    commit = _validate_commit(
        code_commit,
        field="EXP-045 model-result code commit",
    )
    expected_cells = {
        (cell.symbol, cell.timeframe, cell.horizon_minutes)
        for cell in MODEL_CELLS
    }

    indexed: dict[
        tuple[str, str, int],
        dict[str, object],
    ] = {}
    for result in cell_results:
        if not isinstance(result, Mapping):
            raise ValueError(
                "EXP-045 model result row must be an object"
            )
        summary = _validate_successor_cell_result(result)
        identity = (
            str(summary["symbol"]),
            str(summary["timeframe"]),
            int(summary["horizon_minutes"]),
        )
        if identity in indexed:
            raise ValueError(
                "duplicate EXP-045 model result cell"
            )
        indexed[identity] = summary

    if set(indexed) != expected_cells:
        missing = sorted(expected_cells - set(indexed))
        raise ValueError(
            f"EXP-045 model result evidence is incomplete: {missing}"
        )

    cells = [indexed[key] for key in sorted(indexed)]
    evidence: dict[str, object] = {
        "evidence_version": (
            SUCCESSOR_MODEL_RESULT_EVIDENCE_VERSION
        ),
        "runner_version": (
            SUCCESSOR_MODEL_ARTIFACT_RUNNER_VERSION
        ),
        "runner_decision": (
            SUCCESSOR_MODEL_ARTIFACT_RUNNER_DECISION
        ),
        "experiment_id": SUCCESSOR_EXPERIMENT_ID,
        "training_core_version": (
            SUCCESSOR_TRAINING_CORE_VERSION
        ),
        "training_core_decision": (
            SUCCESSOR_TRAINING_CORE_DECISION
        ),
        "training_core_commit": (
            SUCCESSOR_TRAINING_CORE_COMMIT
        ),
        "training_core_blob_sha": (
            SUCCESSOR_TRAINING_CORE_BLOB_SHA
        ),
        "protocol_decision": SUCCESSOR_PROTOCOL_DECISION,
        "protocol_version": SUCCESSOR_PROTOCOL_VERSION,
        "protocol_commit": SUCCESSOR_PROTOCOL_COMMIT,
        "protocol_blob_sha": SUCCESSOR_PROTOCOL_BLOB_SHA,
        "protocol_fingerprint": (
            successor_protocol_fingerprint()
        ),
        "base_protocol_fingerprint": (
            BASE_PROTOCOL_FINGERPRINT
        ),
        "predecessor_failure_review_decision": (
            PREDECESSOR_FAILURE_REVIEW_DECISION
        ),
        "predecessor_failure_review_blob_sha": (
            FAILURE_REVIEW_BLOB_SHA
        ),
        "predecessor_failed_model_run_id": (
            PREDECESSOR_FAILED_MODEL_RUN_ID
        ),
        "predecessor_failed_model_head_sha": (
            PREDECESSOR_FAILED_MODEL_HEAD_SHA
        ),
        "prior_result_informed": PRIOR_RESULT_INFORMED,
        "evidence_label": EVIDENCE_LABEL,
        "untouched_oos": UNTOUCHED_OOS,
        "code_commit": commit,
        "source_data_experiment_id": "EXP-20260923-044",
        "feature_run_id": AUTHORITATIVE_FEATURE_RUN_ID,
        "feature_evidence_artifact_id": (
            AUTHORITATIVE_FEATURE_EVIDENCE_ARTIFACT_ID
        ),
        "feature_evidence_fingerprint": (
            AUTHORITATIVE_FEATURE_EVIDENCE_FINGERPRINT
        ),
        "outcome_run_id": AUTHORITATIVE_OUTCOME_RUN_ID,
        "outcome_evidence_artifact_id": (
            AUTHORITATIVE_OUTCOME_EVIDENCE_ARTIFACT_ID
        ),
        "outcome_evidence_fingerprint": (
            AUTHORITATIVE_OUTCOME_EVIDENCE_FINGERPRINT
        ),
        "readiness_artifact_id": (
            AUTHORITATIVE_READINESS_ARTIFACT_ID
        ),
        "readiness_fingerprint": (
            AUTHORITATIVE_READINESS_FINGERPRINT
        ),
        "verified_cell_count": len(cells),
        "cells": cells,
        "model_protocol_result_authorized": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }
    evidence["evidence_fingerprint"] = _sha256(
        _canonical_json(evidence)
    )
    return evidence


def run_authoritative_successor_model_bundle(
    *,
    repository_root: Path,
    readiness: Mapping[str, object],
    feature_roots: Mapping[tuple[str, str], Path],
    outcome_roots: Mapping[tuple[str, str], Path],
    code_commit: str,
) -> dict[str, object]:
    if (
        AUTHORITATIVE_SUCCESSOR_MODEL_RESULT_EXECUTION_AUTHORIZED
        is not True
    ):
        raise PermissionError(
            "DEC-097 source is non-executable for authoritative "
            "EXP-045 model fitting"
        )

    # Intentionally unreachable under DEC-097. A later separately
    # merged execution decision must open this gate.
    validate_successor_artifact_runner_sources(
        repository_root=repository_root,
    )
    indexed = validate_authoritative_readiness(readiness)
    cell_results: list[dict[str, object]] = []
    for cell in MODEL_CELLS:
        identity = (cell.symbol, cell.timeframe)
        if identity not in indexed:
            raise ValueError(
                f"missing authoritative EXP-045 source cell: {identity}"
            )
        if (
            identity not in feature_roots
            or identity not in outcome_roots
        ):
            raise ValueError(
                f"missing extracted artifact root for {identity}"
            )
        loaded: VerifiedCellArtifacts = (
            load_authoritative_cell_artifacts(
                readiness=readiness,
                feature_root=feature_roots[identity],
                outcome_root=outcome_roots[identity],
                symbol=cell.symbol,
                timeframe=cell.timeframe,
            )
        )
        cell_results.append(
            run_successor_model_cell_core(
                features=loaded.feature_frame,
                outcomes=loaded.outcome_frame,
                cell=cell,
            )
        )

    return compile_successor_model_result_evidence(
        cell_results,
        code_commit=code_commit,
    )


def write_successor_model_result_evidence(
    evidence: Mapping[str, object],
    *,
    path: Path,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    payload = json.dumps(
        dict(evidence),
        sort_keys=True,
        indent=2,
        allow_nan=False,
    ) + "\n"
    if (
        destination.exists()
        and destination.read_text(encoding="utf-8")
        != payload
    ):
        raise ValueError(
            "conflicting existing EXP-045 model-result evidence: "
            f"{destination}"
        )
    destination.write_text(
        payload,
        encoding="utf-8",
    )


__all__ = [
    "AUTHORITATIVE_FEATURE_ARTIFACTS",
    "AUTHORITATIVE_OUTCOME_ARTIFACTS",
    "AUTHORITATIVE_SUCCESSOR_MODEL_RESULT_EXECUTION_AUTHORIZED",
    "LEGACY_DATA_LOADER_BLOB_SHA",
    "SUCCESSOR_MODEL_ARTIFACT_RUNNER_DECISION",
    "SUCCESSOR_MODEL_ARTIFACT_RUNNER_VERSION",
    "SUCCESSOR_MODEL_FIT_AUTHORIZED",
    "SUCCESSOR_MODEL_RESULT_EVIDENCE_VERSION",
    "SUCCESSOR_PROTOCOL_BLOB_SHA",
    "SUCCESSOR_PROTOCOL_COMMIT",
    "SUCCESSOR_TRAINING_CORE_BLOB_SHA",
    "SUCCESSOR_TRAINING_CORE_COMMIT",
    "compile_successor_model_result_evidence",
    "run_authoritative_successor_model_bundle",
    "validate_successor_artifact_runner_sources",
    "write_successor_model_result_evidence",
]
