from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_active_one_shot_executor_workflow_install_source_preflight_proof_recovery_freeze import (
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_RECOVERY_FREEZE_DECISION,
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_RECOVERY_FREEZE_VERSION,
    freeze_reviewed_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery,
)
from .exp062_historical_active_one_shot_executor_workflow_install_source_preflight_proof_recovery_review import (
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_RECOVERY_REVIEW_DECISION,
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_RECOVERY_REVIEW_VERSION,
    review_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery,
)
from .exp062_historical_terminal_review_contract import (
    EXP062_HISTORICAL_TERMINAL_REVIEW_DECISION,
    EXP062_HISTORICAL_TERMINAL_REVIEW_VERSION,
)


EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_RECOVERY_RUNTIME_FREEZE_DECISION = (
    "DEC-410"
)
EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_RECOVERY_RUNTIME_FREEZE_VERSION = (
    "fmp-exp062-active-one-shot-historical-executor-workflow-install-source-preflight-proof-recovery-runtime-freeze-v1"
)

FAILED_DEC404_PROOF_RUN_ID = 36613664506
FAILED_DEC404_PROOF_HEAD_SHA = "0db04ae49b3533778b08afa31e9ef9a26576b80c"
FAILED_DEC404_PROOF_JOB_ID = 109561121322

RECOVERY_PROOF_HEAD_SHA = "3ea7d3f7bfe8f1dfb3bbac612f74255da4fee432"
RECOVERY_PROOF_RUN_ID = 36616131587
RECOVERY_PROOF_JOB_ID = 109569478100
RECOVERY_PROOF_ARTIFACT_ID = 11054938805
RECOVERY_PROOF_ARTIFACT_NAME = (
    "exp062-dec407-active-one-shot-historical-executor-workflow-"
    "install-source-preflight-recovery-"
    "3ea7d3f7bfe8f1dfb3bbac612f74255da4fee432"
)
RECOVERY_PROOF_ARTIFACT_DIGEST = (
    "sha256:e71ad4c19602bec2c3fa71ad6f76e41eadea53edd5ef310ea2110d251002da25"
)
RECOVERY_PROOF_ARTIFACT_ZIP_SHA256 = (
    "e71ad4c19602bec2c3fa71ad6f76e41eadea53edd5ef310ea2110d251002da25"
)
RECOVERY_PREFLIGHT_RAW_SHA256 = (
    "aea9a6f510ee7f5147adb7aea4cba2e9662093dfc2a8465adc9b7aec61556639"
)
RECOVERY_PREFLIGHT_CANONICAL_SHA256 = (
    "4f96d9df7e7e4fba224a376b500539e4581bc34d852178f00796ee7be66f6c6b"
)

DEC408_REVIEWER_BLOB_SHA = "b7c28510824b234337318042d8bc8714b7a1c230"
DEC409_FREEZE_BUILDER_BLOB_SHA = "18fdeb4700cb9233c66ed09dab81b8b61ce4272c"
DEC334_TERMINAL_REVIEW_BLOB_SHA = "fda2a45f74b101303467cf7b8527bec1bfc5e168"
DEC409_FREEZE_FINGERPRINT_SHA256 = (
    "c0c04735c57638fde0a57122c240ea6c9aacd86fc7e43cdc532aaf8ba54cd9d3"
)

DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA = (
    "51ce87584369be957482460d81649adb1cb9f05d"
)
EXPECTED_EXECUTOR_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
)

_REVIEW_SOURCE_BLOBS = {
    "dec407_recovery_workflow": "2adfc7bd1ccacd158a78532d31ff38f4f175229f",
    "dec403_preflight": "cb8ca1ca5b65e9703844d3df9b0a622e2e3ed1bc",
    "dec403_preflight_cli": "1c9615b7ee55ff1387cd95464abf2202f8dd9d3f",
    "dec402_install_source_contract": (
        "a09eca21a8b5e7b88182040ada5d9298eb922282"
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


def validate_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery_runtime_freeze_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dec408_reviewer": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_active_one_shot_executor_workflow_install_source_preflight_proof_recovery_review.py",
            DEC408_REVIEWER_BLOB_SHA,
        ),
        "dec409_freeze_builder": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_active_one_shot_executor_workflow_install_source_preflight_proof_recovery_freeze.py",
            DEC409_FREEZE_BUILDER_BLOB_SHA,
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
            raise ValueError(f"missing DEC-410 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-410 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha
    return actual


def _validate_reviewed_result(value: Mapping[str, object]) -> None:
    _require_exact(
        value,
        {
            "decision": (
                EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_RECOVERY_REVIEW_DECISION
            ),
            "version": (
                EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_RECOVERY_REVIEW_VERSION
            ),
            "stage": (
                "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "SOURCE_PREFLIGHT_RECOVERY_PROOF_REVIEWED_ACTIVE_WORKFLOW_ABSENT"
            ),
            "proof_recovery_decision": "DEC-407",
            "failed_proof_run_id": FAILED_DEC404_PROOF_RUN_ID,
            "failed_proof_head_sha": FAILED_DEC404_PROOF_HEAD_SHA,
            "failed_proof_job_id": FAILED_DEC404_PROOF_JOB_ID,
            "failed_proof_run_number": 1,
            "failed_proof_run_attempt": 1,
            "failed_proof_run_conclusion": "failure",
            "proof_run_id": RECOVERY_PROOF_RUN_ID,
            "proof_head_sha": RECOVERY_PROOF_HEAD_SHA,
            "proof_run_number": 2,
            "proof_run_attempt": 1,
            "proof_run_conclusion": "success",
            "proof_job_id": RECOVERY_PROOF_JOB_ID,
            "proof_artifact_id": RECOVERY_PROOF_ARTIFACT_ID,
            "proof_artifact_name": RECOVERY_PROOF_ARTIFACT_NAME,
            "proof_artifact_digest": RECOVERY_PROOF_ARTIFACT_DIGEST,
            "preflight_raw_sha256": RECOVERY_PREFLIGHT_RAW_SHA256,
            "preflight_canonical_sha256": RECOVERY_PREFLIGHT_CANONICAL_SHA256,
            "install_source_preflight_decision": "DEC-403",
            "install_source_preflight_version": (
                "fmp-exp062-active-one-shot-historical-executor-workflow-install-"
                "source-preflight-v1"
            ),
            "install_source_contract_decision": "DEC-402",
            "install_source_contract_version": (
                "fmp-exp062-active-one-shot-historical-executor-workflow-install-"
                "source-contract-v1"
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
            "active_one_shot_historical_executor_workflow_install_execution_authorization_source_authorized": True,
            "active_one_shot_historical_executor_workflow_install_execution_contract_source_authorized": True,
            "active_one_shot_historical_executor_workflow_install_activation_source_authorized": True,
            "active_one_shot_historical_executor_workflow_install_source_authorized": True,
            "historical_discovery_execution_authorized": True,
            "discovery_result_authorized": True,
            "review_source_blobs": _REVIEW_SOURCE_BLOBS,
            "next_gate": (
                "IMMUTABLE_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "SOURCE_PREFLIGHT_RECOVERY_PROOF_FREEZE_BEFORE_INSTALL"
            ),
        },
        prefix="DEC-410 reviewed result",
    )
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-410 reviewed result {field} must remain false"
            )


def _validate_dec409_freeze(value: Mapping[str, object]) -> None:
    _require_exact(
        value,
        {
            "decision": (
                EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_RECOVERY_FREEZE_DECISION
            ),
            "version": (
                EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_RECOVERY_FREEZE_VERSION
            ),
            "stage": (
                "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "SOURCE_PREFLIGHT_RECOVERY_PROOF_REVIEWED_AND_FROZEN"
            ),
            "source_review_decision": "DEC-408",
            "proof_recovery_decision": "DEC-407",
            "failed_proof_run_id": FAILED_DEC404_PROOF_RUN_ID,
            "failed_proof_head_sha": FAILED_DEC404_PROOF_HEAD_SHA,
            "failed_proof_job_id": FAILED_DEC404_PROOF_JOB_ID,
            "failed_proof_run_number": 1,
            "failed_proof_run_attempt": 1,
            "failed_proof_run_conclusion": "failure",
            "proof_run_id": RECOVERY_PROOF_RUN_ID,
            "proof_head_sha": RECOVERY_PROOF_HEAD_SHA,
            "proof_run_number": 2,
            "proof_run_attempt": 1,
            "proof_run_conclusion": "success",
            "proof_job_id": RECOVERY_PROOF_JOB_ID,
            "proof_artifact_id": RECOVERY_PROOF_ARTIFACT_ID,
            "proof_artifact_name": RECOVERY_PROOF_ARTIFACT_NAME,
            "proof_artifact_digest": RECOVERY_PROOF_ARTIFACT_DIGEST,
            "preflight_raw_sha256": RECOVERY_PREFLIGHT_RAW_SHA256,
            "preflight_canonical_sha256": RECOVERY_PREFLIGHT_CANONICAL_SHA256,
            "review_source_blobs": _REVIEW_SOURCE_BLOBS,
            "install_source_preflight_decision": "DEC-403",
            "install_source_preflight_version": (
                "fmp-exp062-active-one-shot-historical-executor-workflow-install-"
                "source-preflight-v1"
            ),
            "install_source_contract_decision": "DEC-402",
            "install_source_contract_version": (
                "fmp-exp062-active-one-shot-historical-executor-workflow-install-"
                "source-contract-v1"
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
            "active_one_shot_historical_executor_workflow_install_execution_authorization_source_authorized": True,
            "active_one_shot_historical_executor_workflow_install_execution_contract_source_authorized": True,
            "active_one_shot_historical_executor_workflow_install_activation_source_authorized": True,
            "active_one_shot_historical_executor_workflow_install_source_authorized": True,
            "historical_executor_workflow_install_authorized": False,
            "historical_executor_workflow_installed": False,
            "historical_executor_available": False,
            "historical_result_dispatch_authorized": False,
            "historical_execute_mode_available": False,
            "historical_discovery_execution_authorized": True,
            "discovery_result_authorized": True,
            "freeze_fingerprint_sha256": DEC409_FREEZE_FINGERPRINT_SHA256,
            "next_gate": (
                "CONCRETE_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "SOURCE_PREFLIGHT_RECOVERY_PROOF_RUNTIME_EVIDENCE_BINDING_BEFORE_INSTALL"
            ),
        },
        prefix="DEC-410 DEC-409 freeze",
    )
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-410 DEC-409 freeze {field} must remain false"
            )

    unsigned = dict(value)
    fingerprint = unsigned.pop("freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC409_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC409_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-410 DEC-409 freeze fingerprint mismatch")


def freeze_active_one_shot_historical_executor_workflow_install_source_preflight_recovery_proof_runtime_evidence(
    *,
    repository_root: Path,
    proof_run: Mapping[str, object],
    proof_jobs_payload: Mapping[str, object],
    proof_artifacts_payload: Mapping[str, object],
    preflight_bytes: bytes,
    artifact_zip_sha256: str,
) -> dict[str, object]:
    source_blobs = (
        validate_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery_runtime_freeze_sources(
            repository_root=repository_root,
        )
    )

    reviewed = review_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery(
        run=proof_run,
        jobs_payload=proof_jobs_payload,
        artifacts_payload=proof_artifacts_payload,
        preflight_bytes=preflight_bytes,
        expected_head_sha=RECOVERY_PROOF_HEAD_SHA,
        repository_root=repository_root,
    )
    _validate_reviewed_result(reviewed)

    frozen_review = (
        freeze_reviewed_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery(
            reviewed,
            expected_head_sha=RECOVERY_PROOF_HEAD_SHA,
        )
    )
    _validate_dec409_freeze(frozen_review)

    artifact_zip_sha256 = _validate_sha256(
        artifact_zip_sha256,
        field="DEC-410 artifact ZIP sha256",
    )
    if artifact_zip_sha256 != RECOVERY_PROOF_ARTIFACT_ZIP_SHA256:
        raise ValueError("DEC-410 artifact ZIP sha256 mismatch")
    if artifact_zip_sha256 != (
        RECOVERY_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:")
    ):
        raise ValueError(
            "DEC-410 artifact ZIP hash does not match GitHub digest"
        )

    frozen: dict[str, object] = {
        "decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_RECOVERY_RUNTIME_FREEZE_DECISION
        ),
        "version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_RECOVERY_RUNTIME_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "SOURCE_PREFLIGHT_RECOVERY_PROOF_RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "failed_proof_run_id": FAILED_DEC404_PROOF_RUN_ID,
        "failed_proof_head_sha": FAILED_DEC404_PROOF_HEAD_SHA,
        "failed_proof_job_id": FAILED_DEC404_PROOF_JOB_ID,
        "failed_proof_run_number": 1,
        "failed_proof_run_attempt": 1,
        "failed_proof_run_conclusion": "failure",
        "recovery_proof_head_sha": RECOVERY_PROOF_HEAD_SHA,
        "recovery_proof_run_id": RECOVERY_PROOF_RUN_ID,
        "recovery_proof_run_number": 2,
        "recovery_proof_run_attempt": 1,
        "recovery_proof_run_conclusion": "success",
        "recovery_proof_job_id": RECOVERY_PROOF_JOB_ID,
        "recovery_proof_artifact_id": RECOVERY_PROOF_ARTIFACT_ID,
        "recovery_proof_artifact_name": RECOVERY_PROOF_ARTIFACT_NAME,
        "recovery_proof_artifact_digest": RECOVERY_PROOF_ARTIFACT_DIGEST,
        "recovery_proof_artifact_zip_sha256": (
            RECOVERY_PROOF_ARTIFACT_ZIP_SHA256
        ),
        "recovery_preflight_raw_sha256": RECOVERY_PREFLIGHT_RAW_SHA256,
        "recovery_preflight_canonical_sha256": (
            RECOVERY_PREFLIGHT_CANONICAL_SHA256
        ),
        "dec408_review_decision": reviewed["decision"],
        "dec408_review_version": reviewed["version"],
        "dec409_freeze_decision": frozen_review["decision"],
        "dec409_freeze_version": frozen_review["version"],
        "dec409_freeze_fingerprint_sha256": (
            DEC409_FREEZE_FINGERPRINT_SHA256
        ),
        "dec334_terminal_review_decision": (
            EXP062_HISTORICAL_TERMINAL_REVIEW_DECISION
        ),
        "dec334_terminal_review_version": (
            EXP062_HISTORICAL_TERMINAL_REVIEW_VERSION
        ),
        "dec408_reviewer_blob_sha": source_blobs["dec408_reviewer"],
        "dec409_freeze_builder_blob_sha": source_blobs[
            "dec409_freeze_builder"
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
        "active_one_shot_historical_executor_workflow_install_execution_authorization_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_execution_contract_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_activation_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_source_authorized": True,
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
            "SOURCE_ONLY_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "FINAL_AUTHORIZATION_CONTRACT_BEFORE_INSTALL"
        ),
    }
    frozen["runtime_freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "DEC409_FREEZE_FINGERPRINT_SHA256",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_RECOVERY_RUNTIME_FREEZE_DECISION",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_RECOVERY_RUNTIME_FREEZE_VERSION",
    "FAILED_DEC404_PROOF_HEAD_SHA",
    "FAILED_DEC404_PROOF_JOB_ID",
    "FAILED_DEC404_PROOF_RUN_ID",
    "RECOVERY_PREFLIGHT_CANONICAL_SHA256",
    "RECOVERY_PREFLIGHT_RAW_SHA256",
    "RECOVERY_PROOF_ARTIFACT_DIGEST",
    "RECOVERY_PROOF_ARTIFACT_ID",
    "RECOVERY_PROOF_HEAD_SHA",
    "RECOVERY_PROOF_JOB_ID",
    "RECOVERY_PROOF_RUN_ID",
    "freeze_active_one_shot_historical_executor_workflow_install_source_preflight_recovery_proof_runtime_evidence",
    "validate_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery_runtime_freeze_sources",
]
