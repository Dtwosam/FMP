from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .evidence import load_feature_evidence_index
from .outcome_evidence import load_outcome_evidence_index
from .readiness import build_training_readiness, load_training_readiness


STATUS_VERSION = "fmp-exp044-execution-status-v1"
FEATURE_WORKFLOW_NAME = "phase8a-exp044-market-features"
FEATURE_WORKFLOW_PATH = ".github/workflows/phase8a-exp044-market-features.yml"
OUTCOME_WORKFLOW_NAME = "phase8a-exp044-market-outcomes"
OUTCOME_WORKFLOW_PATH = ".github/workflows/phase8a-exp044-market-outcomes.yml"


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value


def validate_workflow_run(
    value: Mapping[str, object],
    *,
    expected_name: str,
    expected_path: str,
) -> Mapping[str, object]:
    if value.get("name") != expected_name:
        raise ValueError("workflow-run name mismatch")
    if value.get("path") != expected_path:
        raise ValueError("workflow-run path mismatch")
    if value.get("event") != "workflow_dispatch":
        raise ValueError("EXP-044 workflow run must use workflow_dispatch")
    if value.get("head_branch") != "main":
        raise ValueError("EXP-044 workflow run must originate from main")
    run_id = value.get("id")
    if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
        raise ValueError("workflow-run id must be a positive integer")
    _validate_commit(value.get("head_sha"), field="workflow-run head_sha")
    status = value.get("status")
    conclusion = value.get("conclusion")
    if not isinstance(status, str) or not status:
        raise ValueError("workflow-run status is invalid")
    if conclusion is not None and not isinstance(conclusion, str):
        raise ValueError("workflow-run conclusion is invalid")
    return value


def load_workflow_run(
    path: Path,
    *,
    expected_name: str,
    expected_path: str,
) -> Mapping[str, object]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read GitHub workflow-run metadata: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError("GitHub workflow-run metadata root must be an object")
    return validate_workflow_run(
        value,
        expected_name=expected_name,
        expected_path=expected_path,
    )


def _base_status(
    *,
    stage: str,
    next_action: str,
    feature_run: Mapping[str, object] | None,
    outcome_run: Mapping[str, object] | None,
    feature_evidence_verified: bool,
    outcome_evidence_verified: bool,
    readiness_verified: bool,
) -> dict[str, object]:
    status: dict[str, object] = {
        "status_version": STATUS_VERSION,
        "experiment_id": "EXP-20260923-044",
        "stage": stage,
        "next_action": next_action,
        "feature_run_id": feature_run.get("id") if feature_run is not None else None,
        "feature_run_head_sha": (
            feature_run.get("head_sha") if feature_run is not None else None
        ),
        "outcome_run_id": outcome_run.get("id") if outcome_run is not None else None,
        "outcome_run_head_sha": (
            outcome_run.get("head_sha") if outcome_run is not None else None
        ),
        "feature_evidence_verified": feature_evidence_verified,
        "outcome_evidence_verified": outcome_evidence_verified,
        "readiness_verified": readiness_verified,
        "data_preparation_complete": readiness_verified,
        "model_protocol_source_open_authorized": readiness_verified,
        "model_protocol_result_authorized": False,
        "model_fit_authorized": False,
        "promotion_authorized": False,
        "shadow_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
    }
    status["status_fingerprint"] = _sha256(_canonical_json(status))
    return status


def build_execution_status(
    *,
    feature_run: Mapping[str, object] | None = None,
    feature_evidence: Mapping[str, object] | None = None,
    outcome_run: Mapping[str, object] | None = None,
    outcome_evidence: Mapping[str, object] | None = None,
    readiness: Mapping[str, object] | None = None,
) -> dict[str, object]:
    if feature_run is not None:
        validate_workflow_run(
            feature_run,
            expected_name=FEATURE_WORKFLOW_NAME,
            expected_path=FEATURE_WORKFLOW_PATH,
        )
    if outcome_run is not None:
        validate_workflow_run(
            outcome_run,
            expected_name=OUTCOME_WORKFLOW_NAME,
            expected_path=OUTCOME_WORKFLOW_PATH,
        )

    if feature_run is None:
        if any(
            item is not None
            for item in (feature_evidence, outcome_run, outcome_evidence, readiness)
        ):
            raise ValueError("downstream EXP-044 evidence cannot exist without feature run")
        return _base_status(
            stage="FEATURE_DISPATCH_REQUIRED",
            next_action="Dispatch phase8a-exp044-market-features from merged main.",
            feature_run=None,
            outcome_run=None,
            feature_evidence_verified=False,
            outcome_evidence_verified=False,
            readiness_verified=False,
        )

    feature_complete = (
        feature_run.get("status") == "completed"
        and feature_run.get("conclusion") == "success"
    )
    if not feature_complete:
        if any(
            item is not None
            for item in (feature_evidence, outcome_run, outcome_evidence, readiness)
        ):
            raise ValueError("downstream EXP-044 evidence cannot precede feature success")
        return _base_status(
            stage="FEATURE_RUN_NOT_SUCCESSFUL",
            next_action="Resolve the feature workflow run before using any downstream evidence.",
            feature_run=feature_run,
            outcome_run=None,
            feature_evidence_verified=False,
            outcome_evidence_verified=False,
            readiness_verified=False,
        )

    if feature_evidence is None:
        if any(item is not None for item in (outcome_run, outcome_evidence, readiness)):
            raise ValueError("downstream EXP-044 evidence cannot precede feature evidence")
        return _base_status(
            stage="FEATURE_EVIDENCE_REQUIRED",
            next_action="Preserve and validate the aggregate feature-evidence artifact.",
            feature_run=feature_run,
            outcome_run=None,
            feature_evidence_verified=False,
            outcome_evidence_verified=False,
            readiness_verified=False,
        )

    if feature_evidence.get("code_commit") != feature_run.get("head_sha"):
        raise ValueError("feature evidence code commit does not match feature workflow run")

    if outcome_run is None:
        if any(item is not None for item in (outcome_evidence, readiness)):
            raise ValueError("outcome evidence cannot exist without outcome workflow run")
        return _base_status(
            stage="OUTCOME_DISPATCH_REQUIRED",
            next_action=(
                "Dispatch phase8a-exp044-market-outcomes from merged main using "
                f"feature_run_id={feature_run['id']}."
            ),
            feature_run=feature_run,
            outcome_run=None,
            feature_evidence_verified=True,
            outcome_evidence_verified=False,
            readiness_verified=False,
        )

    outcome_complete = (
        outcome_run.get("status") == "completed"
        and outcome_run.get("conclusion") == "success"
    )
    if not outcome_complete:
        if any(item is not None for item in (outcome_evidence, readiness)):
            raise ValueError("readiness evidence cannot precede outcome workflow success")
        return _base_status(
            stage="OUTCOME_RUN_NOT_SUCCESSFUL",
            next_action="Resolve the outcome workflow run before using readiness evidence.",
            feature_run=feature_run,
            outcome_run=outcome_run,
            feature_evidence_verified=True,
            outcome_evidence_verified=False,
            readiness_verified=False,
        )

    if outcome_evidence is None:
        if readiness is not None:
            raise ValueError("readiness cannot exist without aggregate outcome evidence")
        return _base_status(
            stage="OUTCOME_EVIDENCE_REQUIRED",
            next_action="Preserve and validate the aggregate outcome-evidence artifact.",
            feature_run=feature_run,
            outcome_run=outcome_run,
            feature_evidence_verified=True,
            outcome_evidence_verified=False,
            readiness_verified=False,
        )

    if outcome_evidence.get("code_commit") != outcome_run.get("head_sha"):
        raise ValueError("outcome evidence code commit does not match outcome workflow run")
    if (
        outcome_evidence.get("feature_evidence_fingerprint")
        != feature_evidence.get("evidence_fingerprint")
    ):
        raise ValueError("outcome evidence does not bind the supplied feature evidence")

    if readiness is None:
        return _base_status(
            stage="READINESS_REQUIRED",
            next_action="Preserve and validate the DEC-074 training-readiness artifact.",
            feature_run=feature_run,
            outcome_run=outcome_run,
            feature_evidence_verified=True,
            outcome_evidence_verified=True,
            readiness_verified=False,
        )

    rebuilt_readiness = build_training_readiness(
        feature_evidence=feature_evidence,
        outcome_evidence=outcome_evidence,
    )
    if dict(readiness) != rebuilt_readiness:
        raise ValueError("readiness does not exactly match the supplied evidence chain")

    if (
        readiness.get("feature_evidence_fingerprint")
        != feature_evidence.get("evidence_fingerprint")
    ):
        raise ValueError("readiness does not bind the supplied feature evidence")
    if (
        readiness.get("outcome_evidence_fingerprint")
        != outcome_evidence.get("evidence_fingerprint")
    ):
        raise ValueError("readiness does not bind the supplied outcome evidence")
    if readiness.get("feature_code_commit") != feature_run.get("head_sha"):
        raise ValueError("readiness feature commit does not match feature run")
    if readiness.get("outcome_code_commit") != outcome_run.get("head_sha"):
        raise ValueError("readiness outcome commit does not match outcome run")

    return _base_status(
        stage="MODEL_PROTOCOL_SOURCE_OPEN",
        next_action=(
            "Draft and freeze a separate predeclared model-training protocol. "
            "Do not fit a model yet."
        ),
        feature_run=feature_run,
        outcome_run=outcome_run,
        feature_evidence_verified=True,
        outcome_evidence_verified=True,
        readiness_verified=True,
    )


def compile_execution_status(
    *,
    feature_run_path: Path | None = None,
    feature_evidence_path: Path | None = None,
    outcome_run_path: Path | None = None,
    outcome_evidence_path: Path | None = None,
    readiness_path: Path | None = None,
) -> dict[str, object]:
    feature_run = (
        load_workflow_run(
            feature_run_path,
            expected_name=FEATURE_WORKFLOW_NAME,
            expected_path=FEATURE_WORKFLOW_PATH,
        )
        if feature_run_path is not None
        else None
    )
    feature_evidence = (
        load_feature_evidence_index(feature_evidence_path)
        if feature_evidence_path is not None
        else None
    )
    outcome_run = (
        load_workflow_run(
            outcome_run_path,
            expected_name=OUTCOME_WORKFLOW_NAME,
            expected_path=OUTCOME_WORKFLOW_PATH,
        )
        if outcome_run_path is not None
        else None
    )
    outcome_evidence = (
        load_outcome_evidence_index(outcome_evidence_path)
        if outcome_evidence_path is not None
        else None
    )
    readiness = (
        load_training_readiness(readiness_path)
        if readiness_path is not None
        else None
    )
    return build_execution_status(
        feature_run=feature_run,
        feature_evidence=feature_evidence,
        outcome_run=outcome_run,
        outcome_evidence=outcome_evidence,
        readiness=readiness,
    )


__all__ = [
    "FEATURE_WORKFLOW_NAME",
    "FEATURE_WORKFLOW_PATH",
    "OUTCOME_WORKFLOW_NAME",
    "OUTCOME_WORKFLOW_PATH",
    "STATUS_VERSION",
    "build_execution_status",
    "compile_execution_status",
    "load_workflow_run",
    "validate_workflow_run",
]
