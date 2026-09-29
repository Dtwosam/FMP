from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_active_one_shot_executor_workflow_install_decision_preflight_proof_freeze import (
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_DECISION_PREFLIGHT_PROOF_FREEZE_DECISION,
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_DECISION_PREFLIGHT_PROOF_FREEZE_VERSION,
    freeze_reviewed_active_one_shot_historical_executor_workflow_install_decision_preflight_proof,
)
from .exp062_historical_active_one_shot_executor_workflow_install_decision_preflight_proof_review import (
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_DECISION_PREFLIGHT_PROOF_REVIEW_DECISION,
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_DECISION_PREFLIGHT_PROOF_REVIEW_VERSION,
    review_active_one_shot_historical_executor_workflow_install_decision_preflight_proof,
)
from .exp062_historical_terminal_review_contract import (
    EXP062_HISTORICAL_TERMINAL_REVIEW_DECISION,
    EXP062_HISTORICAL_TERMINAL_REVIEW_VERSION,
)


EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_DECISION_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION = (
    "DEC-383"
)
EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_DECISION_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION = (
    "fmp-exp062-active-one-shot-historical-executor-workflow-install-decision-preflight-proof-runtime-freeze-v1"
)

ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_HEAD_SHA = (
    "fa96bc731ed8d21cec883451f7ec5e984b74df40"
)
ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_RUN_ID = 36553935570
ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_JOB_ID = 109358450875
ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_ARTIFACT_ID = 11025737149
ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_ARTIFACT_NAME = (
    "exp062-dec380-active-one-shot-historical-executor-workflow-"
    "install-decision-preflight-"
    "fa96bc731ed8d21cec883451f7ec5e984b74df40"
)
ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_ARTIFACT_DIGEST = (
    "sha256:f863ea57b45e2c0e12892732747094f8f4f63793cf212be018d7d6cbade6555b"
)
ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256 = (
    "f863ea57b45e2c0e12892732747094f8f4f63793cf212be018d7d6cbade6555b"
)
ACTIVE_INSTALL_DECISION_PREFLIGHT_RAW_SHA256 = (
    "05bb0e78cd14d22ba84a2bd46bc2fde894e088ad4e96fdd463a040ea91718ed0"
)
ACTIVE_INSTALL_DECISION_PREFLIGHT_CANONICAL_SHA256 = (
    "27e6ef7221062844b1f4b12f6fae55c9de2d933c4f606411cd676e982201487f"
)

DEC381_REVIEWER_BLOB_SHA = "2358d8fe3a54d9dbe86a51d3f97275b6557c0865"
DEC382_FREEZE_BUILDER_BLOB_SHA = "4a5691e0467b0ad1a272beb2333e4a987fa0806d"
DEC334_TERMINAL_REVIEW_BLOB_SHA = "fda2a45f74b101303467cf7b8527bec1bfc5e168"
DEC382_FREEZE_FINGERPRINT_SHA256 = (
    "be15d3ffe0a66befeec91694e5c412e0d7678818835774361258edf06b06b6f8"
)

DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA = (
    "51ce87584369be957482460d81649adb1cb9f05d"
)
EXPECTED_EXECUTOR_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
)

_REVIEW_SOURCE_BLOBS = {
    "dec380_workflow": "45129f3ef81348a344e2e88108ebae7b6506b10f",
    "dec379_preflight": "87e86b9c424e72ca67d39c230c038704523d3adc",
    "dec379_preflight_cli": "6aee1bc7f230567d403eeb1d3f8fea9751c9a20d",
    "dec378_install_decision_contract": (
        "4bdaa6f48b2a0d8ea467c7cbd1869358749660e5"
    ),
    "dormant_executor_workflow_template": (
        DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA
    ),
    "active_discovery_workflow": (
        "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
    ),
}

_FALSE_AUTHORITY_FIELDS = (
    "historical_executor_workflow_install_authorized",
    "historical_executor_workflow_installed",
    "historical_executor_available",
    "historical_result_dispatch_authorized",
    "historical_execute_mode_available",
    "rerun_authorized",
    "retry_authorized",
    "replacement_run_authorized",
    "reserved_robustness_access_authorized",
    "candidate_compilation_authorized",
    "promotion_authorized",
    "phase8b_authorized",
    "demo_order_authorized",
    "broker_mutation_authorized",
    "live_order_authorized",
    "real_money_authorized",
    "trading_authorized",
)


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


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must contain 64 hex characters")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _require_exact(
    value: Mapping[str, object],
    expected: Mapping[str, object],
    *,
    prefix: str,
) -> None:
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"{prefix} {field} mismatch")


def validate_active_one_shot_historical_executor_workflow_install_decision_preflight_proof_runtime_freeze_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dec381_reviewer": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_active_one_shot_executor_workflow_install_decision_preflight_proof_review.py",
            DEC381_REVIEWER_BLOB_SHA,
        ),
        "dec382_freeze_builder": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_active_one_shot_executor_workflow_install_decision_preflight_proof_freeze.py",
            DEC382_FREEZE_BUILDER_BLOB_SHA,
        ),
        "dec334_terminal_review_contract": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_terminal_review_contract.py",
            DEC334_TERMINAL_REVIEW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-383 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-383 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha
    return actual


def _validate_reviewed_result(value: Mapping[str, object]) -> None:
    _require_exact(
        value,
        {
            "decision": (
                EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_DECISION_PREFLIGHT_PROOF_REVIEW_DECISION
            ),
            "version": (
                EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_DECISION_PREFLIGHT_PROOF_REVIEW_VERSION
            ),
            "stage": (
                "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "DECISION_PREFLIGHT_PROOF_REVIEWED_ACTIVE_WORKFLOW_ABSENT"
            ),
            "proof_run_id": ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_RUN_ID,
            "proof_head_sha": ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_HEAD_SHA,
            "proof_run_number": 1,
            "proof_run_attempt": 1,
            "proof_run_conclusion": "success",
            "proof_job_id": ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_JOB_ID,
            "proof_artifact_id": ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_ARTIFACT_ID,
            "proof_artifact_name": ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_ARTIFACT_NAME,
            "proof_artifact_digest": ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_ARTIFACT_DIGEST,
            "preflight_raw_sha256": ACTIVE_INSTALL_DECISION_PREFLIGHT_RAW_SHA256,
            "preflight_canonical_sha256": (
                ACTIVE_INSTALL_DECISION_PREFLIGHT_CANONICAL_SHA256
            ),
            "install_decision_preflight_decision": "DEC-379",
            "install_decision_preflight_version": (
                "fmp-exp062-active-one-shot-historical-executor-workflow-install-decision-preflight-v1"
            ),
            "install_decision_contract_decision": "DEC-378",
            "install_decision_contract_version": (
                "fmp-exp062-active-one-shot-historical-executor-workflow-install-decision-contract-v1"
            ),
            "dormant_executor_workflow_template_blob_sha": (
                DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA
            ),
            "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
            "executor_workflow_path_exists": False,
            "historical_gate_proof_run_id": 36358289723,
            "historical_result_attempt_count": 0,
            "historical_result_slot_consumed": False,
            "historical_result_slot_verified_available": True,
            "expected_target_run_number": 2,
            "expected_target_run_attempt": 1,
            "active_one_shot_historical_executor_workflow_install_authorization_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_decision_source_authorized": True,
            "historical_executor_workflow_install_authorized": False,
            "historical_executor_workflow_installed": False,
            "historical_executor_available": False,
            "historical_result_dispatch_authorized": False,
            "historical_execute_mode_available": False,
            "historical_discovery_execution_authorized": True,
            "discovery_result_authorized": True,
            "review_source_blobs": _REVIEW_SOURCE_BLOBS,
            "next_gate": (
                "IMMUTABLE_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "DECISION_PREFLIGHT_PROOF_FREEZE_BEFORE_INSTALL"
            ),
        },
        prefix="DEC-383 reviewed result",
    )
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-383 reviewed result {field} must remain false"
            )


def _validate_dec382_freeze(value: Mapping[str, object]) -> None:
    _require_exact(
        value,
        {
            "decision": (
                EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_DECISION_PREFLIGHT_PROOF_FREEZE_DECISION
            ),
            "version": (
                EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_DECISION_PREFLIGHT_PROOF_FREEZE_VERSION
            ),
            "stage": (
                "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "DECISION_PREFLIGHT_PROOF_REVIEWED_AND_FROZEN"
            ),
            "proof_run_id": ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_RUN_ID,
            "proof_head_sha": ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_HEAD_SHA,
            "proof_run_number": 1,
            "proof_run_attempt": 1,
            "proof_run_conclusion": "success",
            "proof_job_id": ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_JOB_ID,
            "proof_artifact_id": ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_ARTIFACT_ID,
            "proof_artifact_name": ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_ARTIFACT_NAME,
            "proof_artifact_digest": ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_ARTIFACT_DIGEST,
            "preflight_raw_sha256": ACTIVE_INSTALL_DECISION_PREFLIGHT_RAW_SHA256,
            "preflight_canonical_sha256": (
                ACTIVE_INSTALL_DECISION_PREFLIGHT_CANONICAL_SHA256
            ),
            "review_source_blobs": _REVIEW_SOURCE_BLOBS,
            "install_decision_preflight_decision": "DEC-379",
            "install_decision_preflight_version": (
                "fmp-exp062-active-one-shot-historical-executor-workflow-install-decision-preflight-v1"
            ),
            "install_decision_contract_decision": "DEC-378",
            "install_decision_contract_version": (
                "fmp-exp062-active-one-shot-historical-executor-workflow-install-decision-contract-v1"
            ),
            "dormant_executor_workflow_template_blob_sha": (
                DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA
            ),
            "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
            "executor_workflow_path_exists": False,
            "historical_result_attempt_count": 0,
            "historical_result_slot_consumed": False,
            "historical_result_slot_verified_available": True,
            "expected_target_run_number": 2,
            "expected_target_run_attempt": 1,
            "active_one_shot_historical_executor_workflow_install_authorization_source_authorized": True,
            "active_one_shot_historical_executor_workflow_install_decision_source_authorized": True,
            "historical_executor_workflow_install_authorized": False,
            "historical_executor_workflow_installed": False,
            "historical_executor_available": False,
            "historical_result_dispatch_authorized": False,
            "historical_execute_mode_available": False,
            "historical_discovery_execution_authorized": True,
            "discovery_result_authorized": True,
            "freeze_fingerprint_sha256": DEC382_FREEZE_FINGERPRINT_SHA256,
            "next_gate": (
                "CONCRETE_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "DECISION_PREFLIGHT_PROOF_RUNTIME_EVIDENCE_BINDING_BEFORE_INSTALL"
            ),
        },
        prefix="DEC-383 DEC-382 freeze",
    )
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-383 DEC-382 freeze {field} must remain false"
            )

    unsigned = dict(value)
    fingerprint = unsigned.pop("freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC382_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC382_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-383 DEC-382 freeze fingerprint mismatch")


def freeze_active_one_shot_historical_executor_workflow_install_decision_preflight_proof_runtime_evidence(
    *,
    repository_root: Path,
    proof_run: Mapping[str, object],
    proof_jobs_payload: Mapping[str, object],
    proof_artifacts_payload: Mapping[str, object],
    preflight_bytes: bytes,
    artifact_zip_sha256: str,
) -> dict[str, object]:
    source_blobs = (
        validate_active_one_shot_historical_executor_workflow_install_decision_preflight_proof_runtime_freeze_sources(
            repository_root=repository_root,
        )
    )

    reviewed = review_active_one_shot_historical_executor_workflow_install_decision_preflight_proof(
        run=proof_run,
        jobs_payload=proof_jobs_payload,
        artifacts_payload=proof_artifacts_payload,
        preflight_bytes=preflight_bytes,
        expected_head_sha=ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_HEAD_SHA,
        repository_root=repository_root,
    )
    _validate_reviewed_result(reviewed)

    frozen_review = (
        freeze_reviewed_active_one_shot_historical_executor_workflow_install_decision_preflight_proof(
            reviewed,
            expected_head_sha=ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_HEAD_SHA,
        )
    )
    _validate_dec382_freeze(frozen_review)

    artifact_zip_sha256 = _validate_sha256(
        artifact_zip_sha256,
        field="DEC-383 artifact ZIP sha256",
    )
    if artifact_zip_sha256 != ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256:
        raise ValueError("DEC-383 artifact ZIP sha256 mismatch")
    if artifact_zip_sha256 != (
        ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:")
    ):
        raise ValueError(
            "DEC-383 artifact ZIP hash does not match GitHub digest"
        )

    frozen: dict[str, object] = {
        "decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_DECISION_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION
        ),
        "version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_DECISION_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "DECISION_PREFLIGHT_PROOF_RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "active_install_decision_preflight_proof_head_sha": (
            ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_HEAD_SHA
        ),
        "active_install_decision_preflight_proof_run_id": (
            ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_RUN_ID
        ),
        "active_install_decision_preflight_proof_run_number": 1,
        "active_install_decision_preflight_proof_run_attempt": 1,
        "active_install_decision_preflight_proof_run_conclusion": "success",
        "active_install_decision_preflight_proof_job_id": (
            ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_JOB_ID
        ),
        "active_install_decision_preflight_proof_artifact_id": (
            ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_ARTIFACT_ID
        ),
        "active_install_decision_preflight_proof_artifact_name": (
            ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_ARTIFACT_NAME
        ),
        "active_install_decision_preflight_proof_artifact_digest": (
            ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_ARTIFACT_DIGEST
        ),
        "active_install_decision_preflight_proof_artifact_zip_sha256": (
            ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256
        ),
        "active_install_decision_preflight_raw_sha256": (
            ACTIVE_INSTALL_DECISION_PREFLIGHT_RAW_SHA256
        ),
        "active_install_decision_preflight_canonical_sha256": (
            ACTIVE_INSTALL_DECISION_PREFLIGHT_CANONICAL_SHA256
        ),
        "dec381_review_decision": reviewed["decision"],
        "dec381_review_version": reviewed["version"],
        "dec382_freeze_decision": frozen_review["decision"],
        "dec382_freeze_version": frozen_review["version"],
        "dec382_freeze_fingerprint_sha256": DEC382_FREEZE_FINGERPRINT_SHA256,
        "dec334_terminal_review_decision": (
            EXP062_HISTORICAL_TERMINAL_REVIEW_DECISION
        ),
        "dec334_terminal_review_version": (
            EXP062_HISTORICAL_TERMINAL_REVIEW_VERSION
        ),
        "dec381_reviewer_blob_sha": source_blobs["dec381_reviewer"],
        "dec382_freeze_builder_blob_sha": source_blobs[
            "dec382_freeze_builder"
        ],
        "dec334_terminal_review_contract_blob_sha": source_blobs[
            "dec334_terminal_review_contract"
        ],
        "review_source_blobs": _REVIEW_SOURCE_BLOBS,
        "dormant_executor_workflow_template_blob_sha": (
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA
        ),
        "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
        "executor_workflow_path_exists": False,
        "historical_gate_proof_run_id": reviewed[
            "historical_gate_proof_run_id"
        ],
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "active_one_shot_historical_executor_workflow_install_authorization_source_authorized": True,
            "active_one_shot_historical_executor_workflow_install_decision_source_authorized": True,
        "historical_executor_workflow_install_authorized": False,
        "historical_executor_workflow_installed": False,
        "historical_executor_available": False,
        "historical_result_dispatch_authorized": False,
        "historical_execute_mode_available": False,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "next_gate": (
            "SOURCE_ONLY_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_CONTRACT"
        ),
    }
    frozen["runtime_freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "ACTIVE_INSTALL_DECISION_PREFLIGHT_CANONICAL_SHA256",
    "ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_ARTIFACT_DIGEST",
    "ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_ARTIFACT_ID",
    "ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_HEAD_SHA",
    "ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_JOB_ID",
    "ACTIVE_INSTALL_DECISION_PREFLIGHT_PROOF_RUN_ID",
    "ACTIVE_INSTALL_DECISION_PREFLIGHT_RAW_SHA256",
    "DEC382_FREEZE_FINGERPRINT_SHA256",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_DECISION_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_DECISION_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION",
    "freeze_active_one_shot_historical_executor_workflow_install_decision_preflight_proof_runtime_evidence",
    "validate_active_one_shot_historical_executor_workflow_install_decision_preflight_proof_runtime_freeze_sources",
]
