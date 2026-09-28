from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_one_shot_executor_source_proof_freeze import (
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_DECISION,
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_VERSION,
    freeze_reviewed_one_shot_historical_executor_source_proof,
)
from .exp062_historical_one_shot_executor_source_proof_review import (
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_DECISION,
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_VERSION,
    review_one_shot_historical_executor_source_proof,
)
from .exp062_historical_terminal_review_contract import (
    EXP062_HISTORICAL_TERMINAL_REVIEW_DECISION,
    EXP062_HISTORICAL_TERMINAL_REVIEW_VERSION,
)


EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_RUNTIME_FREEZE_DECISION = "DEC-341"
EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_RUNTIME_FREEZE_VERSION = (
    "fmp-exp062-one-shot-historical-executor-source-proof-runtime-freeze-v1"
)

SOURCE_PROOF_HEAD_SHA = "e9dfbf034614b54598d31653da3868ed66aa90ba"
SOURCE_PROOF_RUN_ID = 36442399041
SOURCE_PROOF_JOB_ID = 108995955292
SOURCE_PROOF_ARTIFACT_ID = 10979242048
SOURCE_PROOF_ARTIFACT_NAME = (
    "exp062-dec338-one-shot-historical-executor-source-"
    "e9dfbf034614b54598d31653da3868ed66aa90ba"
)
SOURCE_PROOF_ARTIFACT_DIGEST = (
    "sha256:7dff775fc559cf9dbd754f45c24fbc814035b1602b59ca5eb9f82678af4e8b88"
)
SOURCE_PROOF_ARTIFACT_ZIP_SHA256 = (
    "7dff775fc559cf9dbd754f45c24fbc814035b1602b59ca5eb9f82678af4e8b88"
)
SOURCE_CONTRACT_RAW_SHA256 = (
    "484ad49fa3b3e925ae4a3576af840a8736c9b25ef439b619e8b60e8011f94d63"
)
SOURCE_CONTRACT_CANONICAL_SHA256 = (
    "cb650b81c2549bfb5bfa62f6609bec9b39e4ed118f3e54c302a48a3a27a11616"
)

DEC339_REVIEWER_BLOB_SHA = "673bfc55bffa908f793a9dbc36d7aed1f4a13784"
DEC340_FREEZE_BUILDER_BLOB_SHA = "804e9a57be2a114f8754334f89f9f5b883d1cee5"
DEC334_TERMINAL_REVIEW_BLOB_SHA = "fda2a45f74b101303467cf7b8527bec1bfc5e168"
DEC340_FREEZE_FINGERPRINT_SHA256 = (
    "e340394fb987c68d9203a57c9cd363f255729b3424a9600ec03533ff421960a8"
)

_FALSE_AUTHORITY_FIELDS = (
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


def validate_one_shot_historical_executor_source_proof_runtime_freeze_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dec339_reviewer": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_one_shot_executor_source_proof_review.py",
            DEC339_REVIEWER_BLOB_SHA,
        ),
        "dec340_freeze_builder": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_one_shot_executor_source_proof_freeze.py",
            DEC340_FREEZE_BUILDER_BLOB_SHA,
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
            raise ValueError(f"missing DEC-341 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-341 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha
    return actual


def _validate_reviewed_result(value: Mapping[str, object]) -> None:
    _require_exact(
        value,
        {
            "decision": (
                EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_DECISION
            ),
            "version": (
                EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_VERSION
            ),
            "stage": (
                "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
                "REVIEWED_SLOT_AVAILABLE"
            ),
            "proof_run_id": SOURCE_PROOF_RUN_ID,
            "proof_head_sha": SOURCE_PROOF_HEAD_SHA,
            "proof_run_number": 1,
            "proof_run_attempt": 1,
            "proof_run_conclusion": "success",
            "proof_job_id": SOURCE_PROOF_JOB_ID,
            "proof_artifact_id": SOURCE_PROOF_ARTIFACT_ID,
            "proof_artifact_name": SOURCE_PROOF_ARTIFACT_NAME,
            "proof_artifact_digest": SOURCE_PROOF_ARTIFACT_DIGEST,
            "contract_raw_sha256": SOURCE_CONTRACT_RAW_SHA256,
            "contract_canonical_sha256": SOURCE_CONTRACT_CANONICAL_SHA256,
            "source_contract_decision": "DEC-337",
            "source_contract_version": (
                "fmp-exp062-one-shot-historical-executor-source-v1"
            ),
            "runtime_freeze_decision": "DEC-336",
            "runtime_freeze_fingerprint_sha256": (
                "147ab77116979afa8d0d07c3c748fb80e02865a382317824320f6af534bfc374"
            ),
            "terminal_review_decision": "DEC-334",
            "historical_gate_proof_run_id": 36358289723,
            "historical_result_attempt_count": 0,
            "historical_result_slot_consumed": False,
            "historical_result_slot_verified_available": True,
            "expected_target_run_number": 2,
            "expected_target_run_attempt": 1,
            "one_shot_historical_executor_source_authorized": True,
            "historical_executor_available": False,
            "historical_result_dispatch_authorized": False,
            "historical_execute_mode_available": False,
            "historical_discovery_execution_authorized": True,
            "discovery_result_authorized": True,
            "next_gate": (
                "IMMUTABLE_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
                "FREEZE_BEFORE_EXECUTOR_WORKFLOW"
            ),
        },
        prefix="DEC-341 reviewed result",
    )
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-341 reviewed result {field} must remain false"
            )


def _validate_dec340_freeze(value: Mapping[str, object]) -> None:
    _require_exact(
        value,
        {
            "decision": (
                EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_DECISION
            ),
            "version": (
                EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_VERSION
            ),
            "stage": (
                "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
                "REVIEWED_AND_FROZEN"
            ),
            "proof_run_id": SOURCE_PROOF_RUN_ID,
            "proof_head_sha": SOURCE_PROOF_HEAD_SHA,
            "proof_run_number": 1,
            "proof_run_attempt": 1,
            "proof_run_conclusion": "success",
            "proof_job_id": SOURCE_PROOF_JOB_ID,
            "proof_artifact_id": SOURCE_PROOF_ARTIFACT_ID,
            "proof_artifact_name": SOURCE_PROOF_ARTIFACT_NAME,
            "proof_artifact_digest": SOURCE_PROOF_ARTIFACT_DIGEST,
            "contract_raw_sha256": SOURCE_CONTRACT_RAW_SHA256,
            "contract_canonical_sha256": SOURCE_CONTRACT_CANONICAL_SHA256,
            "source_contract_decision": "DEC-337",
            "source_contract_version": (
                "fmp-exp062-one-shot-historical-executor-source-v1"
            ),
            "runtime_freeze_decision": "DEC-336",
            "runtime_freeze_fingerprint_sha256": (
                "147ab77116979afa8d0d07c3c748fb80e02865a382317824320f6af534bfc374"
            ),
            "terminal_review_decision": "DEC-334",
            "historical_result_attempt_count": 0,
            "historical_result_slot_consumed": False,
            "historical_result_slot_verified_available": True,
            "expected_target_run_number": 2,
            "expected_target_run_attempt": 1,
            "planned_dispatch_command_frozen": (
                "gh workflow run phase8a-exp062-discovery.yml --ref main"
            ),
            "one_shot_historical_executor_source_authorized": True,
            "historical_executor_available": False,
            "historical_result_dispatch_authorized": False,
            "historical_execute_mode_available": False,
            "historical_discovery_execution_authorized": True,
            "discovery_result_authorized": True,
            "freeze_fingerprint_sha256": DEC340_FREEZE_FINGERPRINT_SHA256,
            "next_gate": (
                "CONCRETE_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
                "RUNTIME_EVIDENCE_BINDING_BEFORE_EXECUTOR_WORKFLOW"
            ),
        },
        prefix="DEC-341 DEC-340 freeze",
    )
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-341 DEC-340 freeze {field} must remain false"
            )

    unsigned = dict(value)
    fingerprint = unsigned.pop("freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC340_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC340_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-341 DEC-340 freeze fingerprint mismatch")


def freeze_one_shot_historical_executor_source_proof_runtime_evidence(
    *,
    repository_root: Path,
    proof_run: Mapping[str, object],
    proof_jobs_payload: Mapping[str, object],
    proof_artifacts_payload: Mapping[str, object],
    contract_bytes: bytes,
    artifact_zip_sha256: str,
) -> dict[str, object]:
    source_blobs = (
        validate_one_shot_historical_executor_source_proof_runtime_freeze_sources(
            repository_root=repository_root,
        )
    )

    reviewed = review_one_shot_historical_executor_source_proof(
        run=proof_run,
        jobs_payload=proof_jobs_payload,
        artifacts_payload=proof_artifacts_payload,
        contract_bytes=contract_bytes,
        expected_head_sha=SOURCE_PROOF_HEAD_SHA,
        repository_root=repository_root,
    )
    _validate_reviewed_result(reviewed)

    frozen_review = freeze_reviewed_one_shot_historical_executor_source_proof(
        reviewed,
        expected_head_sha=SOURCE_PROOF_HEAD_SHA,
    )
    _validate_dec340_freeze(frozen_review)

    artifact_zip_sha256 = _validate_sha256(
        artifact_zip_sha256,
        field="DEC-341 artifact ZIP sha256",
    )
    if artifact_zip_sha256 != SOURCE_PROOF_ARTIFACT_ZIP_SHA256:
        raise ValueError("DEC-341 artifact ZIP sha256 mismatch")
    if artifact_zip_sha256 != SOURCE_PROOF_ARTIFACT_DIGEST.removeprefix(
        "sha256:"
    ):
        raise ValueError(
            "DEC-341 artifact ZIP hash does not match GitHub digest"
        )

    frozen: dict[str, object] = {
        "decision": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_RUNTIME_FREEZE_DECISION
        ),
        "version": (
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_RUNTIME_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
            "RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "source_proof_head_sha": SOURCE_PROOF_HEAD_SHA,
        "source_proof_run_id": SOURCE_PROOF_RUN_ID,
        "source_proof_run_number": 1,
        "source_proof_run_attempt": 1,
        "source_proof_run_conclusion": "success",
        "source_proof_job_id": SOURCE_PROOF_JOB_ID,
        "source_proof_artifact_id": SOURCE_PROOF_ARTIFACT_ID,
        "source_proof_artifact_name": SOURCE_PROOF_ARTIFACT_NAME,
        "source_proof_artifact_digest": SOURCE_PROOF_ARTIFACT_DIGEST,
        "source_proof_artifact_zip_sha256": (
            SOURCE_PROOF_ARTIFACT_ZIP_SHA256
        ),
        "source_contract_raw_sha256": SOURCE_CONTRACT_RAW_SHA256,
        "source_contract_canonical_sha256": (
            SOURCE_CONTRACT_CANONICAL_SHA256
        ),
        "dec339_review_decision": reviewed["decision"],
        "dec339_review_version": reviewed["version"],
        "dec340_freeze_decision": frozen_review["decision"],
        "dec340_freeze_version": frozen_review["version"],
        "dec340_freeze_fingerprint_sha256": (
            DEC340_FREEZE_FINGERPRINT_SHA256
        ),
        "dec334_terminal_review_decision": (
            EXP062_HISTORICAL_TERMINAL_REVIEW_DECISION
        ),
        "dec334_terminal_review_version": (
            EXP062_HISTORICAL_TERMINAL_REVIEW_VERSION
        ),
        "dec339_reviewer_blob_sha": source_blobs["dec339_reviewer"],
        "dec340_freeze_builder_blob_sha": source_blobs[
            "dec340_freeze_builder"
        ],
        "dec334_terminal_review_contract_blob_sha": source_blobs[
            "dec334_terminal_review_contract"
        ],
        "historical_gate_proof_run_id": reviewed[
            "historical_gate_proof_run_id"
        ],
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "one_shot_historical_executor_source_authorized": True,
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
            "SOURCE_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_CONTRACT"
        ),
    }
    frozen["runtime_freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "DEC340_FREEZE_FINGERPRINT_SHA256",
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_RUNTIME_FREEZE_DECISION",
    "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_RUNTIME_FREEZE_VERSION",
    "SOURCE_CONTRACT_CANONICAL_SHA256",
    "SOURCE_CONTRACT_RAW_SHA256",
    "SOURCE_PROOF_ARTIFACT_DIGEST",
    "SOURCE_PROOF_ARTIFACT_ID",
    "SOURCE_PROOF_HEAD_SHA",
    "SOURCE_PROOF_JOB_ID",
    "SOURCE_PROOF_RUN_ID",
    "freeze_one_shot_historical_executor_source_proof_runtime_evidence",
    "validate_one_shot_historical_executor_source_proof_runtime_freeze_sources",
]
