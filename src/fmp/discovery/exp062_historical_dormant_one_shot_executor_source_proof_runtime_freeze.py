from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_dormant_one_shot_executor_source_proof_freeze import (
    EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_DECISION,
    EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_VERSION,
    freeze_reviewed_dormant_one_shot_historical_executor_source_proof,
)
from .exp062_historical_dormant_one_shot_executor_source_proof_review import (
    EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_DECISION,
    EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_VERSION,
    review_dormant_one_shot_historical_executor_source_proof,
)
from .exp062_historical_terminal_review_contract import (
    EXP062_HISTORICAL_TERMINAL_REVIEW_DECISION,
    EXP062_HISTORICAL_TERMINAL_REVIEW_VERSION,
)


EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_RUNTIME_FREEZE_DECISION = (
    "DEC-359"
)
EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_RUNTIME_FREEZE_VERSION = (
    "fmp-exp062-dormant-one-shot-historical-executor-source-proof-runtime-freeze-v1"
)

DORMANT_SOURCE_PROOF_HEAD_SHA = "67337de4b21efab0cbafb3c9237397f0a98d524e"
DORMANT_SOURCE_PROOF_RUN_ID = 36473192632
DORMANT_SOURCE_PROOF_JOB_ID = 109100293950
DORMANT_SOURCE_PROOF_ARTIFACT_ID = 10991479562
DORMANT_SOURCE_PROOF_ARTIFACT_NAME = (
    "exp062-dec356-dormant-one-shot-historical-executor-source-"
    "67337de4b21efab0cbafb3c9237397f0a98d524e"
)
DORMANT_SOURCE_PROOF_ARTIFACT_DIGEST = (
    "sha256:092e1daebf889560d27ebe57242772c3806322627dab03e64a2ff400d9b4b1d1"
)
DORMANT_SOURCE_PROOF_ARTIFACT_ZIP_SHA256 = (
    "092e1daebf889560d27ebe57242772c3806322627dab03e64a2ff400d9b4b1d1"
)
DORMANT_SOURCE_RAW_SHA256 = (
    "1dfae5078e400fc2dbf0b10ef6d4297dc4d3c0660386ebb8c46b63c6dbe69060"
)
DORMANT_SOURCE_CANONICAL_SHA256 = (
    "4d6cf8999ecb5346a10ecb31cdc1b669736d4d466e6b31c503b3fbf1a5e633a7"
)

DEC357_REVIEWER_BLOB_SHA = "4c921577253fe7dcb74451299aecec4ad27fd522"
DEC358_FREEZE_BUILDER_BLOB_SHA = "878fa9e9be9d93c3ebd4c214a192cfb8ecdcc368"
DEC334_TERMINAL_REVIEW_BLOB_SHA = "fda2a45f74b101303467cf7b8527bec1bfc5e168"
DEC358_FREEZE_FINGERPRINT_SHA256 = (
    "8ba4411b8c7468a1f0eecc0352490e00577452ce96a81710fca6457e779e9897"
)

EXPECTED_EXECUTOR_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
)
DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA = (
    "51ce87584369be957482460d81649adb1cb9f05d"
)
_REVIEW_SOURCE_BLOBS = {
    "dec356_workflow": "0522e443eda017759c78ccbc718f453cdb0bf8f9",
    "dec355_source": "003e44126d9d6a807efd51b5a589128f6d4b5aac",
    "dec354_installation_source_contract": (
        "e4fc6a7d1faaca50bc6936597f0e8b66fe096985"
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
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


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


def validate_dormant_one_shot_historical_executor_source_proof_runtime_freeze_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dec357_reviewer": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_dormant_one_shot_executor_source_proof_review.py",
            DEC357_REVIEWER_BLOB_SHA,
        ),
        "dec358_freeze_builder": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_dormant_one_shot_executor_source_proof_freeze.py",
            DEC358_FREEZE_BUILDER_BLOB_SHA,
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
            raise ValueError(f"missing DEC-359 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-359 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha
    return actual


def _validate_reviewed_result(value: Mapping[str, object]) -> None:
    _require_exact(
        value,
        {
            "decision": (
                EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_DECISION
            ),
            "version": (
                EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_VERSION
            ),
            "stage": (
                "EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
                "REVIEWED_ACTIVE_WORKFLOW_UNINSTALLED"
            ),
            "proof_run_id": DORMANT_SOURCE_PROOF_RUN_ID,
            "proof_head_sha": DORMANT_SOURCE_PROOF_HEAD_SHA,
            "proof_run_number": 1,
            "proof_run_attempt": 1,
            "proof_run_conclusion": "success",
            "proof_job_id": DORMANT_SOURCE_PROOF_JOB_ID,
            "proof_artifact_id": DORMANT_SOURCE_PROOF_ARTIFACT_ID,
            "proof_artifact_name": DORMANT_SOURCE_PROOF_ARTIFACT_NAME,
            "proof_artifact_digest": DORMANT_SOURCE_PROOF_ARTIFACT_DIGEST,
            "source_raw_sha256": DORMANT_SOURCE_RAW_SHA256,
            "source_canonical_sha256": DORMANT_SOURCE_CANONICAL_SHA256,
            "dormant_source_decision": "DEC-355",
            "dormant_source_version": (
                "fmp-exp062-one-shot-historical-executor-dormant-workflow-source-v1"
            ),
            "dormant_executor_workflow_template_blob_sha": (
                DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA
            ),
            "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
            "dormant_executor_workflow_template_present": True,
            "dormant_template_dispatch_capable_if_installed": True,
            "dormant_template_actions_write_required_if_installed": True,
            "historical_gate_proof_run_id": 36358289723,
            "historical_result_attempt_count": 0,
            "historical_result_slot_consumed": False,
            "historical_result_slot_verified_available": True,
            "expected_target_run_number": 2,
            "expected_target_run_attempt": 1,
            "historical_executor_workflow_install_authorized": False,
            "historical_executor_workflow_installed": False,
            "historical_executor_available": False,
            "historical_result_dispatch_authorized": False,
            "historical_execute_mode_available": False,
            "historical_discovery_execution_authorized": True,
            "discovery_result_authorized": True,
            "review_source_blobs": _REVIEW_SOURCE_BLOBS,
            "next_gate": (
                "IMMUTABLE_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_"
                "SOURCE_PROOF_FREEZE_BEFORE_INSTALL"
            ),
        },
        prefix="DEC-359 reviewed result",
    )
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-359 reviewed result {field} must remain false"
            )


def _validate_dec358_freeze(value: Mapping[str, object]) -> None:
    _require_exact(
        value,
        {
            "decision": (
                EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_DECISION
            ),
            "version": (
                EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_VERSION
            ),
            "stage": (
                "EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
                "REVIEWED_AND_FROZEN"
            ),
            "proof_run_id": DORMANT_SOURCE_PROOF_RUN_ID,
            "proof_head_sha": DORMANT_SOURCE_PROOF_HEAD_SHA,
            "proof_run_number": 1,
            "proof_run_attempt": 1,
            "proof_run_conclusion": "success",
            "proof_job_id": DORMANT_SOURCE_PROOF_JOB_ID,
            "proof_artifact_id": DORMANT_SOURCE_PROOF_ARTIFACT_ID,
            "proof_artifact_name": DORMANT_SOURCE_PROOF_ARTIFACT_NAME,
            "proof_artifact_digest": DORMANT_SOURCE_PROOF_ARTIFACT_DIGEST,
            "source_raw_sha256": DORMANT_SOURCE_RAW_SHA256,
            "source_canonical_sha256": DORMANT_SOURCE_CANONICAL_SHA256,
            "review_source_blobs": _REVIEW_SOURCE_BLOBS,
            "dormant_source_decision": "DEC-355",
            "dormant_source_version": (
                "fmp-exp062-one-shot-historical-executor-dormant-workflow-source-v1"
            ),
            "dormant_executor_workflow_template_blob_sha": (
                DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA
            ),
            "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
            "dormant_executor_workflow_template_present": True,
            "dormant_template_dispatch_capable_if_installed": True,
            "dormant_template_actions_write_required_if_installed": True,
            "historical_gate_proof_run_id": 36358289723,
            "historical_result_attempt_count": 0,
            "historical_result_slot_consumed": False,
            "historical_result_slot_verified_available": True,
            "expected_target_run_number": 2,
            "expected_target_run_attempt": 1,
            "historical_executor_workflow_install_authorized": False,
            "historical_executor_workflow_installed": False,
            "historical_executor_available": False,
            "historical_result_dispatch_authorized": False,
            "historical_execute_mode_available": False,
            "historical_discovery_execution_authorized": True,
            "discovery_result_authorized": True,
            "freeze_fingerprint_sha256": DEC358_FREEZE_FINGERPRINT_SHA256,
            "next_gate": (
                "CONCRETE_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
                "RUNTIME_EVIDENCE_BINDING_BEFORE_INSTALL"
            ),
        },
        prefix="DEC-359 DEC-358 freeze",
    )
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-359 DEC-358 freeze {field} must remain false"
            )

    unsigned = dict(value)
    fingerprint = unsigned.pop("freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC358_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC358_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-359 DEC-358 freeze fingerprint mismatch")


def freeze_dormant_one_shot_historical_executor_source_proof_runtime_evidence(
    *,
    repository_root: Path,
    proof_run: Mapping[str, object],
    proof_jobs_payload: Mapping[str, object],
    proof_artifacts_payload: Mapping[str, object],
    source_bytes: bytes,
    artifact_zip_sha256: str,
) -> dict[str, object]:
    source_blobs = (
        validate_dormant_one_shot_historical_executor_source_proof_runtime_freeze_sources(
            repository_root=repository_root,
        )
    )

    reviewed = review_dormant_one_shot_historical_executor_source_proof(
        run=proof_run,
        jobs_payload=proof_jobs_payload,
        artifacts_payload=proof_artifacts_payload,
        source_bytes=source_bytes,
        expected_head_sha=DORMANT_SOURCE_PROOF_HEAD_SHA,
        repository_root=repository_root,
    )
    _validate_reviewed_result(reviewed)

    frozen_review = freeze_reviewed_dormant_one_shot_historical_executor_source_proof(
        reviewed,
        expected_head_sha=DORMANT_SOURCE_PROOF_HEAD_SHA,
    )
    _validate_dec358_freeze(frozen_review)

    artifact_zip_sha256 = _validate_sha256(
        artifact_zip_sha256,
        field="DEC-359 artifact ZIP sha256",
    )
    if artifact_zip_sha256 != DORMANT_SOURCE_PROOF_ARTIFACT_ZIP_SHA256:
        raise ValueError("DEC-359 artifact ZIP sha256 mismatch")
    if artifact_zip_sha256 != (
        DORMANT_SOURCE_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:")
    ):
        raise ValueError(
            "DEC-359 artifact ZIP hash does not match GitHub digest"
        )

    frozen: dict[str, object] = {
        "decision": (
            EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_RUNTIME_FREEZE_DECISION
        ),
        "version": (
            EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_RUNTIME_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
            "RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "dormant_source_proof_head_sha": DORMANT_SOURCE_PROOF_HEAD_SHA,
        "dormant_source_proof_run_id": DORMANT_SOURCE_PROOF_RUN_ID,
        "dormant_source_proof_run_number": 1,
        "dormant_source_proof_run_attempt": 1,
        "dormant_source_proof_run_conclusion": "success",
        "dormant_source_proof_job_id": DORMANT_SOURCE_PROOF_JOB_ID,
        "dormant_source_proof_artifact_id": DORMANT_SOURCE_PROOF_ARTIFACT_ID,
        "dormant_source_proof_artifact_name": DORMANT_SOURCE_PROOF_ARTIFACT_NAME,
        "dormant_source_proof_artifact_digest": (
            DORMANT_SOURCE_PROOF_ARTIFACT_DIGEST
        ),
        "dormant_source_proof_artifact_zip_sha256": (
            DORMANT_SOURCE_PROOF_ARTIFACT_ZIP_SHA256
        ),
        "dormant_source_raw_sha256": DORMANT_SOURCE_RAW_SHA256,
        "dormant_source_canonical_sha256": DORMANT_SOURCE_CANONICAL_SHA256,
        "dec357_review_decision": reviewed["decision"],
        "dec357_review_version": reviewed["version"],
        "dec358_freeze_decision": frozen_review["decision"],
        "dec358_freeze_version": frozen_review["version"],
        "dec358_freeze_fingerprint_sha256": DEC358_FREEZE_FINGERPRINT_SHA256,
        "dec334_terminal_review_decision": (
            EXP062_HISTORICAL_TERMINAL_REVIEW_DECISION
        ),
        "dec334_terminal_review_version": (
            EXP062_HISTORICAL_TERMINAL_REVIEW_VERSION
        ),
        "dec357_reviewer_blob_sha": source_blobs["dec357_reviewer"],
        "dec358_freeze_builder_blob_sha": source_blobs[
            "dec358_freeze_builder"
        ],
        "dec334_terminal_review_contract_blob_sha": source_blobs[
            "dec334_terminal_review_contract"
        ],
        "review_source_blobs": _REVIEW_SOURCE_BLOBS,
        "dormant_executor_workflow_template_blob_sha": (
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA
        ),
        "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
        "dormant_executor_workflow_template_present": True,
        "dormant_template_dispatch_capable_if_installed": True,
        "dormant_template_actions_write_required_if_installed": True,
        "historical_gate_proof_run_id": reviewed[
            "historical_gate_proof_run_id"
        ],
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
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
            "WORKFLOW_INSTALL_CONTRACT"
        ),
    }
    frozen["runtime_freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "DEC358_FREEZE_FINGERPRINT_SHA256",
    "DORMANT_SOURCE_CANONICAL_SHA256",
    "DORMANT_SOURCE_PROOF_ARTIFACT_DIGEST",
    "DORMANT_SOURCE_PROOF_ARTIFACT_ID",
    "DORMANT_SOURCE_PROOF_HEAD_SHA",
    "DORMANT_SOURCE_PROOF_JOB_ID",
    "DORMANT_SOURCE_PROOF_RUN_ID",
    "DORMANT_SOURCE_RAW_SHA256",
    "EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_RUNTIME_FREEZE_DECISION",
    "EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_RUNTIME_FREEZE_VERSION",
    "freeze_dormant_one_shot_historical_executor_source_proof_runtime_evidence",
    "validate_dormant_one_shot_historical_executor_source_proof_runtime_freeze_sources",
]
