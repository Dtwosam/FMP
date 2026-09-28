from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_one_shot_executor_workflow_install_preflight_proof_freeze import (
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_FREEZE_DECISION,
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_FREEZE_VERSION,
    freeze_reviewed_one_shot_historical_executor_workflow_install_preflight_proof,
)
from .exp062_historical_one_shot_executor_workflow_install_preflight_proof_review import (
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_REVIEW_DECISION,
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_REVIEW_VERSION,
    review_one_shot_historical_executor_workflow_install_preflight_proof,
)
from .exp062_historical_terminal_review_contract import (
    EXP062_HISTORICAL_TERMINAL_REVIEW_DECISION,
    EXP062_HISTORICAL_TERMINAL_REVIEW_VERSION,
)


EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION = (
    "DEC-353"
)
EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION = (
    "fmp-exp062-one-shot-historical-executor-workflow-install-preflight-proof-runtime-freeze-v1"
)

WORKFLOW_INSTALL_PREFLIGHT_PROOF_HEAD_SHA = (
    "bef60cd8656f0db48293570c13f91e2e09fe5be8"
)
WORKFLOW_INSTALL_PREFLIGHT_PROOF_RUN_ID = 36461898040
WORKFLOW_INSTALL_PREFLIGHT_PROOF_JOB_ID = 109062250103
WORKFLOW_INSTALL_PREFLIGHT_PROOF_ARTIFACT_ID = 10987972547
WORKFLOW_INSTALL_PREFLIGHT_PROOF_ARTIFACT_NAME = (
    "exp062-dec350-one-shot-historical-executor-workflow-install-preflight-"
    "bef60cd8656f0db48293570c13f91e2e09fe5be8"
)
WORKFLOW_INSTALL_PREFLIGHT_PROOF_ARTIFACT_DIGEST = (
    "sha256:60a723a55502ee9b8145258c5482ce71b82b2331c572378536b14d78f6ef2f91"
)
WORKFLOW_INSTALL_PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256 = (
    "60a723a55502ee9b8145258c5482ce71b82b2331c572378536b14d78f6ef2f91"
)
WORKFLOW_INSTALL_PREFLIGHT_RAW_SHA256 = (
    "ee754581b87576c3c23228a2371b88b3b8a38fdcd9c20ebd2c222c18f7c65e0d"
)
WORKFLOW_INSTALL_PREFLIGHT_CANONICAL_SHA256 = (
    "5c1893ea24a627ea421f05564d6d0cc490215201c01162fbe0b6ab519a323c8b"
)

DEC351_REVIEWER_BLOB_SHA = "704877e4a0440744c29dd4338173fb8818f6c0d6"
DEC352_FREEZE_BUILDER_BLOB_SHA = "60256d2fa9201f666dd8e330c98b3d080ffe6b43"
DEC334_TERMINAL_REVIEW_BLOB_SHA = "fda2a45f74b101303467cf7b8527bec1bfc5e168"
DEC352_FREEZE_FINGERPRINT_SHA256 = (
    "75fad6795f4046d83f5ae29f08475c969e29d3fe3af0e3448dde46292a959f4a"
)

EXPECTED_EXECUTOR_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
)

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


def validate_one_shot_historical_executor_workflow_install_preflight_proof_runtime_freeze_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dec351_reviewer": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_one_shot_executor_workflow_install_preflight_proof_review.py",
            DEC351_REVIEWER_BLOB_SHA,
        ),
        "dec352_freeze_builder": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_one_shot_executor_workflow_install_preflight_proof_freeze.py",
            DEC352_FREEZE_BUILDER_BLOB_SHA,
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
            raise ValueError(f"missing DEC-353 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-353 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha
    return actual


def _validate_reviewed_result(value: Mapping[str, object]) -> None:
    _require_exact(
        value,
        {
            "decision": (
                EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_REVIEW_DECISION
            ),
            "version": (
                EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_REVIEW_VERSION
            ),
            "stage": (
                "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_"
                "PROOF_REVIEWED_SOURCE_ABSENT_SLOT_AVAILABLE"
            ),
            "proof_run_id": WORKFLOW_INSTALL_PREFLIGHT_PROOF_RUN_ID,
            "proof_head_sha": WORKFLOW_INSTALL_PREFLIGHT_PROOF_HEAD_SHA,
            "proof_run_number": 1,
            "proof_run_attempt": 1,
            "proof_run_conclusion": "success",
            "proof_job_id": WORKFLOW_INSTALL_PREFLIGHT_PROOF_JOB_ID,
            "proof_artifact_id": WORKFLOW_INSTALL_PREFLIGHT_PROOF_ARTIFACT_ID,
            "proof_artifact_name": WORKFLOW_INSTALL_PREFLIGHT_PROOF_ARTIFACT_NAME,
            "proof_artifact_digest": WORKFLOW_INSTALL_PREFLIGHT_PROOF_ARTIFACT_DIGEST,
            "preflight_raw_sha256": WORKFLOW_INSTALL_PREFLIGHT_RAW_SHA256,
            "preflight_canonical_sha256": (
                WORKFLOW_INSTALL_PREFLIGHT_CANONICAL_SHA256
            ),
            "workflow_install_preflight_decision": "DEC-349",
            "workflow_install_preflight_version": (
                "fmp-exp062-one-shot-historical-executor-workflow-install-preflight-v1"
            ),
            "install_contract_decision": "DEC-348",
            "install_contract_version": (
                "fmp-exp062-one-shot-historical-executor-workflow-install-contract-v1"
            ),
            "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
            "executor_workflow_path_exists": False,
            "workflow_install_slot_verified_available": True,
            "historical_gate_proof_run_id": 36358289723,
            "historical_result_attempt_count": 0,
            "historical_result_slot_consumed": False,
            "historical_result_slot_verified_available": True,
            "expected_target_run_number": 2,
            "expected_target_run_attempt": 1,
            "one_shot_historical_executor_workflow_install_source_authorized": True,
            "historical_executor_workflow_install_authorized": False,
            "historical_executor_workflow_installed": False,
            "historical_executor_available": False,
            "historical_result_dispatch_authorized": False,
            "historical_execute_mode_available": False,
            "historical_discovery_execution_authorized": True,
            "discovery_result_authorized": True,
            "next_gate": (
                "IMMUTABLE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "PREFLIGHT_PROOF_FREEZE_BEFORE_WORKFLOW_INSTALL"
            ),
        },
        prefix="DEC-353 reviewed result",
    )
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-353 reviewed result {field} must remain false"
            )


def _validate_dec352_freeze(value: Mapping[str, object]) -> None:
    _require_exact(
        value,
        {
            "decision": (
                EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_FREEZE_DECISION
            ),
            "version": (
                EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_FREEZE_VERSION
            ),
            "stage": (
                "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_"
                "PROOF_REVIEWED_AND_FROZEN"
            ),
            "proof_run_id": WORKFLOW_INSTALL_PREFLIGHT_PROOF_RUN_ID,
            "proof_head_sha": WORKFLOW_INSTALL_PREFLIGHT_PROOF_HEAD_SHA,
            "proof_run_number": 1,
            "proof_run_attempt": 1,
            "proof_run_conclusion": "success",
            "proof_job_id": WORKFLOW_INSTALL_PREFLIGHT_PROOF_JOB_ID,
            "proof_artifact_id": WORKFLOW_INSTALL_PREFLIGHT_PROOF_ARTIFACT_ID,
            "proof_artifact_name": WORKFLOW_INSTALL_PREFLIGHT_PROOF_ARTIFACT_NAME,
            "proof_artifact_digest": WORKFLOW_INSTALL_PREFLIGHT_PROOF_ARTIFACT_DIGEST,
            "preflight_raw_sha256": WORKFLOW_INSTALL_PREFLIGHT_RAW_SHA256,
            "preflight_canonical_sha256": (
                WORKFLOW_INSTALL_PREFLIGHT_CANONICAL_SHA256
            ),
            "workflow_install_preflight_decision": "DEC-349",
            "workflow_install_preflight_version": (
                "fmp-exp062-one-shot-historical-executor-workflow-install-preflight-v1"
            ),
            "install_contract_decision": "DEC-348",
            "install_contract_version": (
                "fmp-exp062-one-shot-historical-executor-workflow-install-contract-v1"
            ),
            "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
            "executor_workflow_path_exists": False,
            "workflow_install_slot_verified_available": True,
            "historical_result_attempt_count": 0,
            "historical_result_slot_consumed": False,
            "historical_result_slot_verified_available": True,
            "expected_target_run_number": 2,
            "expected_target_run_attempt": 1,
            "one_shot_historical_executor_workflow_install_source_authorized": True,
            "historical_executor_workflow_install_authorized": False,
            "historical_executor_workflow_installed": False,
            "historical_executor_available": False,
            "historical_result_dispatch_authorized": False,
            "historical_execute_mode_available": False,
            "historical_discovery_execution_authorized": True,
            "discovery_result_authorized": True,
            "freeze_fingerprint_sha256": DEC352_FREEZE_FINGERPRINT_SHA256,
            "next_gate": (
                "CONCRETE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "PREFLIGHT_PROOF_RUNTIME_EVIDENCE_BINDING_BEFORE_WORKFLOW_INSTALL"
            ),
        },
        prefix="DEC-353 DEC-352 freeze",
    )
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-353 DEC-352 freeze {field} must remain false"
            )

    unsigned = dict(value)
    fingerprint = unsigned.pop("freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC352_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC352_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-353 DEC-352 freeze fingerprint mismatch")


def freeze_one_shot_historical_executor_workflow_install_preflight_proof_runtime_evidence(
    *,
    repository_root: Path,
    proof_run: Mapping[str, object],
    proof_jobs_payload: Mapping[str, object],
    proof_artifacts_payload: Mapping[str, object],
    preflight_bytes: bytes,
    artifact_zip_sha256: str,
) -> dict[str, object]:
    source_blobs = (
        validate_one_shot_historical_executor_workflow_install_preflight_proof_runtime_freeze_sources(
            repository_root=repository_root,
        )
    )

    reviewed = review_one_shot_historical_executor_workflow_install_preflight_proof(
        run=proof_run,
        jobs_payload=proof_jobs_payload,
        artifacts_payload=proof_artifacts_payload,
        preflight_bytes=preflight_bytes,
        expected_head_sha=WORKFLOW_INSTALL_PREFLIGHT_PROOF_HEAD_SHA,
        repository_root=repository_root,
    )
    _validate_reviewed_result(reviewed)

    frozen_review = (
        freeze_reviewed_one_shot_historical_executor_workflow_install_preflight_proof(
            reviewed,
            expected_head_sha=WORKFLOW_INSTALL_PREFLIGHT_PROOF_HEAD_SHA,
        )
    )
    _validate_dec352_freeze(frozen_review)

    artifact_zip_sha256 = _validate_sha256(
        artifact_zip_sha256,
        field="DEC-353 artifact ZIP sha256",
    )
    if artifact_zip_sha256 != WORKFLOW_INSTALL_PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256:
        raise ValueError("DEC-353 artifact ZIP sha256 mismatch")
    if artifact_zip_sha256 != (
        WORKFLOW_INSTALL_PREFLIGHT_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:")
    ):
        raise ValueError(
            "DEC-353 artifact ZIP hash does not match GitHub digest"
        )

    frozen: dict[str, object] = {
        "decision": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION
        ),
        "version": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_"
            "RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "workflow_install_preflight_proof_head_sha": (
            WORKFLOW_INSTALL_PREFLIGHT_PROOF_HEAD_SHA
        ),
        "workflow_install_preflight_proof_run_id": (
            WORKFLOW_INSTALL_PREFLIGHT_PROOF_RUN_ID
        ),
        "workflow_install_preflight_proof_run_number": 1,
        "workflow_install_preflight_proof_run_attempt": 1,
        "workflow_install_preflight_proof_run_conclusion": "success",
        "workflow_install_preflight_proof_job_id": (
            WORKFLOW_INSTALL_PREFLIGHT_PROOF_JOB_ID
        ),
        "workflow_install_preflight_proof_artifact_id": (
            WORKFLOW_INSTALL_PREFLIGHT_PROOF_ARTIFACT_ID
        ),
        "workflow_install_preflight_proof_artifact_name": (
            WORKFLOW_INSTALL_PREFLIGHT_PROOF_ARTIFACT_NAME
        ),
        "workflow_install_preflight_proof_artifact_digest": (
            WORKFLOW_INSTALL_PREFLIGHT_PROOF_ARTIFACT_DIGEST
        ),
        "workflow_install_preflight_proof_artifact_zip_sha256": (
            WORKFLOW_INSTALL_PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256
        ),
        "workflow_install_preflight_raw_sha256": (
            WORKFLOW_INSTALL_PREFLIGHT_RAW_SHA256
        ),
        "workflow_install_preflight_canonical_sha256": (
            WORKFLOW_INSTALL_PREFLIGHT_CANONICAL_SHA256
        ),
        "dec351_review_decision": reviewed["decision"],
        "dec351_review_version": reviewed["version"],
        "dec352_freeze_decision": frozen_review["decision"],
        "dec352_freeze_version": frozen_review["version"],
        "dec352_freeze_fingerprint_sha256": (
            DEC352_FREEZE_FINGERPRINT_SHA256
        ),
        "dec334_terminal_review_decision": (
            EXP062_HISTORICAL_TERMINAL_REVIEW_DECISION
        ),
        "dec334_terminal_review_version": (
            EXP062_HISTORICAL_TERMINAL_REVIEW_VERSION
        ),
        "dec351_reviewer_blob_sha": source_blobs["dec351_reviewer"],
        "dec352_freeze_builder_blob_sha": source_blobs[
            "dec352_freeze_builder"
        ],
        "dec334_terminal_review_contract_blob_sha": source_blobs[
            "dec334_terminal_review_contract"
        ],
        "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
        "executor_workflow_path_exists": False,
        "workflow_install_slot_verified_available": True,
        "historical_gate_proof_run_id": reviewed[
            "historical_gate_proof_run_id"
        ],
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "one_shot_historical_executor_workflow_install_source_authorized": True,
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
            "SOURCE_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_"
            "INSTALLATION_SOURCE_CONTRACT"
        ),
    }
    frozen["runtime_freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "DEC352_FREEZE_FINGERPRINT_SHA256",
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION",
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION",
    "WORKFLOW_INSTALL_PREFLIGHT_CANONICAL_SHA256",
    "WORKFLOW_INSTALL_PREFLIGHT_PROOF_ARTIFACT_DIGEST",
    "WORKFLOW_INSTALL_PREFLIGHT_PROOF_ARTIFACT_ID",
    "WORKFLOW_INSTALL_PREFLIGHT_PROOF_HEAD_SHA",
    "WORKFLOW_INSTALL_PREFLIGHT_PROOF_JOB_ID",
    "WORKFLOW_INSTALL_PREFLIGHT_PROOF_RUN_ID",
    "WORKFLOW_INSTALL_PREFLIGHT_RAW_SHA256",
    "freeze_one_shot_historical_executor_workflow_install_preflight_proof_runtime_evidence",
    "validate_one_shot_historical_executor_workflow_install_preflight_proof_runtime_freeze_sources",
]
