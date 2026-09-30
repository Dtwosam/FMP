from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_active_one_shot_executor_dispatch_preflight_proof_freeze import (
    freeze_reviewed_active_one_shot_historical_executor_dispatch_preflight_proof,
)
from .exp062_historical_active_one_shot_executor_dispatch_preflight_proof_review import (
    review_active_one_shot_historical_executor_dispatch_preflight_proof,
)


EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION = (
    "DEC-429"
)
EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION = (
    "fmp-exp062-active-one-shot-historical-executor-dispatch-preflight-proof-runtime-freeze-v1"
)

ACTIVE_DISPATCH_PREFLIGHT_PROOF_HEAD_SHA = (
    "f2b2a5629013749b74306201aac29d14b7124cd3"
)
ACTIVE_DISPATCH_PREFLIGHT_PROOF_RUN_ID = 36688457000
ACTIVE_DISPATCH_PREFLIGHT_PROOF_JOB_ID = 109799712311
ACTIVE_DISPATCH_PREFLIGHT_PROOF_ARTIFACT_ID = 11085100742
ACTIVE_DISPATCH_PREFLIGHT_PROOF_ARTIFACT_DIGEST = (
    "sha256:a335347c3e428f8eff653bfe4a8e022b0ed939c188634a5236f2354edaff9ac9"
)
ACTIVE_DISPATCH_PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256 = (
    "a335347c3e428f8eff653bfe4a8e022b0ed939c188634a5236f2354edaff9ac9"
)
ACTIVE_DISPATCH_PREFLIGHT_RAW_SHA256 = (
    "017f45bcec6633006b3d78c76f09890da0417fbd79f904743de659e614d73974"
)
ACTIVE_DISPATCH_PREFLIGHT_CANONICAL_SHA256 = (
    "26958a21f832609d2dfc57347f6637c35aaa2923c36ec14a40f9573e6a77cb02"
)
DEC428_FREEZE_FINGERPRINT_SHA256 = (
    "4a9a7b3e931fd12585638430afbc38f823b5016ecc11f9f4fe7dd3533aa82454"
)

_EXPECTED_SOURCE_BLOBS = {
    "dec427_reviewer": "0796656210dffc0dce3e82b3b3b85265061e526b",
    "dec428_freeze_builder": "ae724b8e798a7be03240883e1f6b10abea9df012",
}


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


def _sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character SHA-256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def validate_active_one_shot_historical_executor_dispatch_preflight_proof_runtime_freeze_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    paths = {
        "dec427_reviewer": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_active_one_shot_executor_dispatch_preflight_proof_review.py"
        ),
        "dec428_freeze_builder": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_active_one_shot_executor_dispatch_preflight_proof_freeze.py"
        ),
    }
    actual: dict[str, str] = {}
    for label, path in paths.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-429 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != _EXPECTED_SOURCE_BLOBS[label]:
            raise ValueError(f"DEC-429 {label} Git blob mismatch")
        actual[label] = actual_sha
    return actual


def freeze_active_one_shot_historical_executor_dispatch_preflight_proof_runtime_evidence(
    *,
    repository_root: Path,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    preflight_bytes: bytes,
    artifact_zip_sha256: str,
) -> dict[str, object]:
    source_blobs = (
        validate_active_one_shot_historical_executor_dispatch_preflight_proof_runtime_freeze_sources(
            repository_root=repository_root,
        )
    )

    reviewed = review_active_one_shot_historical_executor_dispatch_preflight_proof(
        run=run,
        jobs_payload=jobs_payload,
        artifacts_payload=artifacts_payload,
        preflight_bytes=preflight_bytes,
        expected_head_sha=ACTIVE_DISPATCH_PREFLIGHT_PROOF_HEAD_SHA,
        repository_root=repository_root,
    )
    frozen_review = (
        freeze_reviewed_active_one_shot_historical_executor_dispatch_preflight_proof(
            reviewed,
            expected_head_sha=ACTIVE_DISPATCH_PREFLIGHT_PROOF_HEAD_SHA,
        )
    )

    exact = {
        "proof_run_id": ACTIVE_DISPATCH_PREFLIGHT_PROOF_RUN_ID,
        "proof_job_id": ACTIVE_DISPATCH_PREFLIGHT_PROOF_JOB_ID,
        "proof_artifact_id": ACTIVE_DISPATCH_PREFLIGHT_PROOF_ARTIFACT_ID,
        "proof_artifact_digest": ACTIVE_DISPATCH_PREFLIGHT_PROOF_ARTIFACT_DIGEST,
        "preflight_raw_sha256": ACTIVE_DISPATCH_PREFLIGHT_RAW_SHA256,
        "preflight_canonical_sha256": ACTIVE_DISPATCH_PREFLIGHT_CANONICAL_SHA256,
    }
    for field, expected in exact.items():
        if reviewed.get(field) != expected:
            raise ValueError(f"DEC-429 reviewed evidence {field} mismatch")

    artifact_zip_sha256 = _sha256(
        artifact_zip_sha256,
        field="DEC-429 artifact ZIP SHA-256",
    )
    if artifact_zip_sha256 != ACTIVE_DISPATCH_PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256:
        raise ValueError("DEC-429 artifact ZIP SHA-256 mismatch")

    if frozen_review.get("freeze_fingerprint_sha256") != (
        DEC428_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-429 DEC-428 freeze fingerprint mismatch")

    frozen: dict[str, object] = {
        "decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION
        ),
        "version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "DISPATCH_PREFLIGHT_PROOF_RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "active_dispatch_preflight_proof_head_sha": (
            ACTIVE_DISPATCH_PREFLIGHT_PROOF_HEAD_SHA
        ),
        "active_dispatch_preflight_proof_run_id": (
            ACTIVE_DISPATCH_PREFLIGHT_PROOF_RUN_ID
        ),
        "active_dispatch_preflight_proof_run_number": 1,
        "active_dispatch_preflight_proof_run_attempt": 1,
        "active_dispatch_preflight_proof_run_conclusion": "success",
        "active_dispatch_preflight_proof_job_id": (
            ACTIVE_DISPATCH_PREFLIGHT_PROOF_JOB_ID
        ),
        "active_dispatch_preflight_proof_artifact_id": (
            ACTIVE_DISPATCH_PREFLIGHT_PROOF_ARTIFACT_ID
        ),
        "active_dispatch_preflight_proof_artifact_name": reviewed[
            "proof_artifact_name"
        ],
        "active_dispatch_preflight_proof_artifact_digest": (
            ACTIVE_DISPATCH_PREFLIGHT_PROOF_ARTIFACT_DIGEST
        ),
        "active_dispatch_preflight_proof_artifact_zip_sha256": (
            ACTIVE_DISPATCH_PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256
        ),
        "active_dispatch_preflight_raw_sha256": (
            ACTIVE_DISPATCH_PREFLIGHT_RAW_SHA256
        ),
        "active_dispatch_preflight_canonical_sha256": (
            ACTIVE_DISPATCH_PREFLIGHT_CANONICAL_SHA256
        ),
        "dec427_review_decision": reviewed["decision"],
        "dec427_review_version": reviewed["version"],
        "dec428_freeze_decision": frozen_review["decision"],
        "dec428_freeze_version": frozen_review["version"],
        "dec428_freeze_fingerprint_sha256": (
            DEC428_FREEZE_FINGERPRINT_SHA256
        ),
        "dec427_reviewer_blob_sha": source_blobs["dec427_reviewer"],
        "dec428_freeze_builder_blob_sha": source_blobs[
            "dec428_freeze_builder"
        ],
        "review_source_blobs": reviewed["review_source_blobs"],
        "active_executor_workflow_blob_sha": reviewed[
            "active_executor_workflow_blob_sha"
        ],
        "active_executor_workflow_path": reviewed[
            "active_executor_workflow_path"
        ],
        "active_executor_workflow_present": True,
        "historical_executor_workflow_install_authorized": True,
        "historical_executor_workflow_installed": True,
        "historical_executor_available": True,
        "executor_workflow_run_count": 0,
        "historical_gate_proof_run_id": reviewed[
            "historical_gate_proof_run_id"
        ],
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
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
            "EXPLICIT_ONE_SHOT_EXECUTOR_DISPATCH_AUTHORIZATION_BEFORE_RUN"
        ),
    }
    frozen["runtime_freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "ACTIVE_DISPATCH_PREFLIGHT_CANONICAL_SHA256",
    "ACTIVE_DISPATCH_PREFLIGHT_PROOF_ARTIFACT_DIGEST",
    "ACTIVE_DISPATCH_PREFLIGHT_PROOF_ARTIFACT_ID",
    "ACTIVE_DISPATCH_PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256",
    "ACTIVE_DISPATCH_PREFLIGHT_PROOF_HEAD_SHA",
    "ACTIVE_DISPATCH_PREFLIGHT_PROOF_JOB_ID",
    "ACTIVE_DISPATCH_PREFLIGHT_PROOF_RUN_ID",
    "ACTIVE_DISPATCH_PREFLIGHT_RAW_SHA256",
    "DEC428_FREEZE_FINGERPRINT_SHA256",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION",
    "freeze_active_one_shot_historical_executor_dispatch_preflight_proof_runtime_evidence",
    "validate_active_one_shot_historical_executor_dispatch_preflight_proof_runtime_freeze_sources",
]
