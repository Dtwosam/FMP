from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_executor_preflight_freeze import (
    EXP062_REVIEWED_HISTORICAL_EXECUTOR_PREFLIGHT_FREEZE_DECISION,
    EXP062_REVIEWED_HISTORICAL_EXECUTOR_PREFLIGHT_FREEZE_VERSION,
    freeze_reviewed_historical_executor_preflight,
)
from .exp062_historical_executor_preflight_review import (
    EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_REVIEW_DECISION,
    EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_REVIEW_VERSION,
    review_historical_executor_preflight_proof,
)


EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_RUNTIME_FREEZE_DECISION = "DEC-329"
EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_RUNTIME_FREEZE_VERSION = (
    "fmp-exp062-historical-executor-preflight-runtime-freeze-v1"
)

PREFLIGHT_PROOF_HEAD_SHA = "a811aacaae82e15b18267b6e4ba659054abb0341"
PREFLIGHT_PROOF_RUN_ID = 36422936991
PREFLIGHT_PROOF_JOB_ID = 108929843306
PREFLIGHT_PROOF_ARTIFACT_ID = 10970303347
PREFLIGHT_PROOF_ARTIFACT_NAME = (
    "exp062-dec326-historical-executor-preflight-"
    "a811aacaae82e15b18267b6e4ba659054abb0341"
)
PREFLIGHT_PROOF_ARTIFACT_DIGEST = (
    "sha256:fe116a7fff7ffdec27e787d3cd7981ac67772276efb12a5b434b04ee3855c74c"
)
PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256 = (
    "fe116a7fff7ffdec27e787d3cd7981ac67772276efb12a5b434b04ee3855c74c"
)
PREFLIGHT_RAW_SHA256 = (
    "5dfa7800a8dcbe4537910690a0ba70b3c93467c685d7c5c99898d0b6d111f9d8"
)
PREFLIGHT_CANONICAL_SHA256 = (
    "9970dcbf44241a3b9ffc6aab01d8a3bab6749813f88d0771dee101ea640aec3d"
)

DEC327_REVIEWER_BLOB_SHA = "da3febc87e69a81f88088c0b34ba0650956d1873"
DEC328_FREEZE_BUILDER_BLOB_SHA = (
    "ce37dd70c167182441b503c38b1197223917ff72"
)
DEC328_FREEZE_FINGERPRINT_SHA256 = (
    "2e295d03066fcfa4dcea300c3f263bcf6a67cb96d6b356410821af493b2d5675"
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


def validate_historical_executor_preflight_runtime_freeze_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dec327_reviewer": (
            root
            / "src/fmp/discovery/exp062_historical_executor_preflight_review.py",
            DEC327_REVIEWER_BLOB_SHA,
        ),
        "dec328_freeze_builder": (
            root
            / "src/fmp/discovery/exp062_historical_executor_preflight_freeze.py",
            DEC328_FREEZE_BUILDER_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-329 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-329 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha
    return actual


def _validate_reviewed_result(value: Mapping[str, object]) -> None:
    _require_exact(
        value,
        {
            "decision": EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_REVIEW_DECISION,
            "version": EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_REVIEW_VERSION,
            "stage": (
                "EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_PROOF_REVIEWED_SLOT_AVAILABLE"
            ),
            "proof_run_id": PREFLIGHT_PROOF_RUN_ID,
            "proof_head_sha": PREFLIGHT_PROOF_HEAD_SHA,
            "proof_run_number": 1,
            "proof_run_attempt": 1,
            "proof_run_conclusion": "success",
            "proof_job_id": PREFLIGHT_PROOF_JOB_ID,
            "proof_artifact_id": PREFLIGHT_PROOF_ARTIFACT_ID,
            "proof_artifact_name": PREFLIGHT_PROOF_ARTIFACT_NAME,
            "proof_artifact_digest": PREFLIGHT_PROOF_ARTIFACT_DIGEST,
            "preflight_raw_sha256": PREFLIGHT_RAW_SHA256,
            "preflight_canonical_sha256": PREFLIGHT_CANONICAL_SHA256,
            "preflight_decision": "DEC-325",
            "preflight_version": (
                "fmp-exp062-historical-executor-preflight-v1"
            ),
            "historical_gate_proof_run_id": 36358289723,
            "historical_result_attempt_count": 0,
            "historical_result_slot_consumed": False,
            "historical_result_slot_verified_available": True,
            "expected_target_run_number": 2,
            "expected_target_run_attempt": 1,
            "one_shot_executor_source_authorized": True,
            "historical_executor_available": False,
            "historical_result_dispatch_authorized": False,
            "historical_execute_mode_available": False,
            "historical_discovery_execution_authorized": True,
            "discovery_result_authorized": True,
            "next_gate": (
                "IMMUTABLE_HISTORICAL_EXECUTOR_PREFLIGHT_PROOF_FREEZE_BEFORE_EXECUTOR"
            ),
        },
        prefix="DEC-329 reviewed result",
    )
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-329 reviewed result {field} must remain false"
            )


def _validate_dec328_freeze(value: Mapping[str, object]) -> None:
    _require_exact(
        value,
        {
            "decision": (
                EXP062_REVIEWED_HISTORICAL_EXECUTOR_PREFLIGHT_FREEZE_DECISION
            ),
            "version": (
                EXP062_REVIEWED_HISTORICAL_EXECUTOR_PREFLIGHT_FREEZE_VERSION
            ),
            "stage": (
                "EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_REVIEWED_AND_FROZEN"
            ),
            "proof_run_id": PREFLIGHT_PROOF_RUN_ID,
            "proof_head_sha": PREFLIGHT_PROOF_HEAD_SHA,
            "proof_run_number": 1,
            "proof_run_attempt": 1,
            "proof_run_conclusion": "success",
            "proof_job_id": PREFLIGHT_PROOF_JOB_ID,
            "proof_artifact_id": PREFLIGHT_PROOF_ARTIFACT_ID,
            "proof_artifact_name": PREFLIGHT_PROOF_ARTIFACT_NAME,
            "proof_artifact_digest": PREFLIGHT_PROOF_ARTIFACT_DIGEST,
            "preflight_raw_sha256": PREFLIGHT_RAW_SHA256,
            "preflight_canonical_sha256": PREFLIGHT_CANONICAL_SHA256,
            "historical_result_attempt_count": 0,
            "historical_result_slot_consumed": False,
            "historical_result_slot_verified_available": True,
            "expected_target_run_number": 2,
            "expected_target_run_attempt": 1,
            "planned_dispatch_command_frozen": (
                "gh workflow run phase8a-exp062-discovery.yml --ref main"
            ),
            "one_shot_executor_source_authorized": True,
            "historical_executor_available": False,
            "historical_result_dispatch_authorized": False,
            "historical_execute_mode_available": False,
            "historical_discovery_execution_authorized": True,
            "discovery_result_authorized": True,
            "freeze_fingerprint_sha256": (
                DEC328_FREEZE_FINGERPRINT_SHA256
            ),
            "next_gate": (
                "CONCRETE_EXECUTOR_PREFLIGHT_RUNTIME_EVIDENCE_BINDING_BEFORE_EXECUTOR"
            ),
        },
        prefix="DEC-329 DEC-328 freeze",
    )
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-329 DEC-328 freeze {field} must remain false"
            )

    unsigned = dict(value)
    fingerprint = unsigned.pop("freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC328_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC328_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-329 DEC-328 freeze fingerprint mismatch")


def freeze_historical_executor_preflight_runtime_evidence(
    *,
    repository_root: Path,
    proof_run: Mapping[str, object],
    proof_jobs_payload: Mapping[str, object],
    proof_artifacts_payload: Mapping[str, object],
    preflight_bytes: bytes,
    artifact_zip_sha256: str,
) -> dict[str, object]:
    source_blobs = (
        validate_historical_executor_preflight_runtime_freeze_sources(
            repository_root=repository_root,
        )
    )

    reviewed = review_historical_executor_preflight_proof(
        run=proof_run,
        jobs_payload=proof_jobs_payload,
        artifacts_payload=proof_artifacts_payload,
        preflight_bytes=preflight_bytes,
        expected_head_sha=PREFLIGHT_PROOF_HEAD_SHA,
        repository_root=repository_root,
    )
    _validate_reviewed_result(reviewed)

    frozen_review = freeze_reviewed_historical_executor_preflight(
        reviewed,
        expected_head_sha=PREFLIGHT_PROOF_HEAD_SHA,
    )
    _validate_dec328_freeze(frozen_review)

    artifact_zip_sha256 = _validate_sha256(
        artifact_zip_sha256,
        field="DEC-329 artifact ZIP sha256",
    )
    if artifact_zip_sha256 != PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256:
        raise ValueError("DEC-329 artifact ZIP sha256 mismatch")
    if artifact_zip_sha256 != PREFLIGHT_PROOF_ARTIFACT_DIGEST.removeprefix(
        "sha256:"
    ):
        raise ValueError(
            "DEC-329 artifact ZIP hash does not match GitHub digest"
        )

    frozen: dict[str, object] = {
        "decision": EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_RUNTIME_FREEZE_DECISION,
        "version": EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_RUNTIME_FREEZE_VERSION,
        "stage": (
            "EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "preflight_proof_head_sha": PREFLIGHT_PROOF_HEAD_SHA,
        "preflight_proof_run_id": PREFLIGHT_PROOF_RUN_ID,
        "preflight_proof_run_number": 1,
        "preflight_proof_run_attempt": 1,
        "preflight_proof_run_conclusion": "success",
        "preflight_proof_job_id": PREFLIGHT_PROOF_JOB_ID,
        "preflight_proof_artifact_id": PREFLIGHT_PROOF_ARTIFACT_ID,
        "preflight_proof_artifact_name": PREFLIGHT_PROOF_ARTIFACT_NAME,
        "preflight_proof_artifact_digest": PREFLIGHT_PROOF_ARTIFACT_DIGEST,
        "preflight_proof_artifact_zip_sha256": (
            PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256
        ),
        "preflight_raw_sha256": PREFLIGHT_RAW_SHA256,
        "preflight_canonical_sha256": PREFLIGHT_CANONICAL_SHA256,
        "dec327_review_decision": reviewed["decision"],
        "dec327_review_version": reviewed["version"],
        "dec328_freeze_decision": frozen_review["decision"],
        "dec328_freeze_version": frozen_review["version"],
        "dec328_freeze_fingerprint_sha256": (
            DEC328_FREEZE_FINGERPRINT_SHA256
        ),
        "dec327_reviewer_blob_sha": source_blobs["dec327_reviewer"],
        "dec328_freeze_builder_blob_sha": source_blobs[
            "dec328_freeze_builder"
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
        "one_shot_executor_source_authorized": True,
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
            "SOURCE_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_ACTIVATION_CONTRACT"
        ),
    }
    frozen["runtime_freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "DEC328_FREEZE_FINGERPRINT_SHA256",
    "EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_RUNTIME_FREEZE_DECISION",
    "EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_RUNTIME_FREEZE_VERSION",
    "PREFLIGHT_CANONICAL_SHA256",
    "PREFLIGHT_PROOF_ARTIFACT_DIGEST",
    "PREFLIGHT_PROOF_ARTIFACT_ID",
    "PREFLIGHT_PROOF_HEAD_SHA",
    "PREFLIGHT_PROOF_JOB_ID",
    "PREFLIGHT_PROOF_RUN_ID",
    "PREFLIGHT_RAW_SHA256",
    "freeze_historical_executor_preflight_runtime_evidence",
    "validate_historical_executor_preflight_runtime_freeze_sources",
]
