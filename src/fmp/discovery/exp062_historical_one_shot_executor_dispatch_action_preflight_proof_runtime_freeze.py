from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_one_shot_executor_dispatch_action_preflight_proof_freeze import (
    freeze_reviewed_one_shot_executor_dispatch_action_preflight_proof,
)
from .exp062_historical_one_shot_executor_dispatch_action_preflight_proof_review import (
    review_one_shot_executor_dispatch_action_preflight_proof,
)


EXP062_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION = (
    "DEC-435"
)
EXP062_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION = (
    "fmp-exp062-one-shot-executor-dispatch-action-preflight-proof-runtime-freeze-v1"
)

ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_HEAD_SHA = (
    "7b4f9fe713e546efdb445a8f4e9982e1b8f219aa"
)
ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_RUN_ID = 36695220474
ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_JOB_ID = 109821445046
ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_ARTIFACT_ID = 11087821283
ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_ARTIFACT_DIGEST = (
    "sha256:16984f3cac059bb725c29953466131ffb710bbfc621ec8f35428bf2036e8cd63"
)
ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256 = (
    "16984f3cac059bb725c29953466131ffb710bbfc621ec8f35428bf2036e8cd63"
)
ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_RAW_SHA256 = (
    "fd512c6dc5c03248e0cd75b328ed32a81dc76564b94ab85436d6f5d8764746d9"
)
ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_CANONICAL_SHA256 = (
    "33daef766b6a2e91b20adef386d2fc44f3b2aff03eeb3a08792f1e49da2d667d"
)
DEC434_FREEZE_FINGERPRINT_SHA256 = (
    "9a59f7329cb5abe0786511b91d7b6d8e33d4df8f027271a7387830f8fbf11c8a"
)
DEC433_REVIEWER_BLOB_SHA = "2a1664277696d687dd6861bd22ad43ac85e4e34e"
DEC434_FREEZE_BUILDER_BLOB_SHA = "7a0e45d21560029782d7985b679770eb9489a526"


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


def validate_one_shot_executor_dispatch_action_preflight_proof_runtime_freeze_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dec433_reviewer": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_one_shot_executor_dispatch_action_preflight_proof_review.py",
            DEC433_REVIEWER_BLOB_SHA,
        ),
        "dec434_freeze_builder": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_one_shot_executor_dispatch_action_preflight_proof_freeze.py",
            DEC434_FREEZE_BUILDER_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-435 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-435 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha
    return actual


def freeze_one_shot_executor_dispatch_action_preflight_proof_runtime_evidence(
    *,
    repository_root: Path,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    preflight_bytes: bytes,
    artifact_zip_sha256: str,
) -> dict[str, object]:
    source_blobs = (
        validate_one_shot_executor_dispatch_action_preflight_proof_runtime_freeze_sources(
            repository_root=repository_root,
        )
    )

    reviewed = review_one_shot_executor_dispatch_action_preflight_proof(
        run=run,
        jobs_payload=jobs_payload,
        artifacts_payload=artifacts_payload,
        preflight_bytes=preflight_bytes,
        expected_head_sha=ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_HEAD_SHA,
        repository_root=repository_root,
    )
    frozen_review = freeze_reviewed_one_shot_executor_dispatch_action_preflight_proof(
        reviewed,
        expected_head_sha=ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_HEAD_SHA,
    )

    exact = {
        "proof_run_id": ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_RUN_ID,
        "proof_job_id": ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_JOB_ID,
        "proof_artifact_id": ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_ARTIFACT_ID,
        "proof_artifact_digest": ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_ARTIFACT_DIGEST,
        "preflight_raw_sha256": ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_RAW_SHA256,
        "preflight_canonical_sha256": (
            ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_CANONICAL_SHA256
        ),
    }
    for field, expected in exact.items():
        if reviewed.get(field) != expected:
            raise ValueError(f"DEC-435 reviewed evidence {field} mismatch")

    artifact_zip_sha256 = _sha256(
        artifact_zip_sha256,
        field="DEC-435 artifact ZIP SHA-256",
    )
    if artifact_zip_sha256 != (
        ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256
    ):
        raise ValueError("DEC-435 artifact ZIP SHA-256 mismatch")
    if artifact_zip_sha256 != (
        ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_ARTIFACT_DIGEST.removeprefix(
            "sha256:"
        )
    ):
        raise ValueError("DEC-435 artifact ZIP hash does not match GitHub digest")

    if frozen_review.get("freeze_fingerprint_sha256") != (
        DEC434_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-435 DEC-434 freeze fingerprint mismatch")

    frozen: dict[str, object] = {
        "decision": (
            EXP062_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION
        ),
        "version": (
            EXP062_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_PROOF_"
            "RUNTIME_EVIDENCE_BOUND_AND_FROZEN_AUTHORIZED_RUN_NOT_STARTED"
        ),
        "one_shot_dispatch_action_preflight_proof_head_sha": (
            ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_HEAD_SHA
        ),
        "one_shot_dispatch_action_preflight_proof_run_id": (
            ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_RUN_ID
        ),
        "one_shot_dispatch_action_preflight_proof_run_number": 1,
        "one_shot_dispatch_action_preflight_proof_run_attempt": 1,
        "one_shot_dispatch_action_preflight_proof_run_conclusion": "success",
        "one_shot_dispatch_action_preflight_proof_job_id": (
            ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_JOB_ID
        ),
        "one_shot_dispatch_action_preflight_proof_artifact_id": (
            ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_ARTIFACT_ID
        ),
        "one_shot_dispatch_action_preflight_proof_artifact_name": reviewed[
            "proof_artifact_name"
        ],
        "one_shot_dispatch_action_preflight_proof_artifact_digest": (
            ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_ARTIFACT_DIGEST
        ),
        "one_shot_dispatch_action_preflight_proof_artifact_zip_sha256": (
            ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256
        ),
        "one_shot_dispatch_action_preflight_raw_sha256": (
            ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_RAW_SHA256
        ),
        "one_shot_dispatch_action_preflight_canonical_sha256": (
            ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_CANONICAL_SHA256
        ),
        "dec433_review_decision": reviewed["decision"],
        "dec433_review_version": reviewed["version"],
        "dec434_freeze_decision": frozen_review["decision"],
        "dec434_freeze_version": frozen_review["version"],
        "dec434_freeze_fingerprint_sha256": DEC434_FREEZE_FINGERPRINT_SHA256,
        "dec433_reviewer_blob_sha": source_blobs["dec433_reviewer"],
        "dec434_freeze_builder_blob_sha": source_blobs[
            "dec434_freeze_builder"
        ],
        "review_source_blobs": reviewed["review_source_blobs"],
        "action_preflight_decision": reviewed["action_preflight_decision"],
        "action_preflight_version": reviewed["action_preflight_version"],
        "authorization_decision": reviewed["authorization_decision"],
        "authorization_version": reviewed["authorization_version"],
        "dec430_dispatch_authorization_blob_sha": reviewed[
            "dec430_dispatch_authorization_blob_sha"
        ],
        "active_executor_workflow_blob_sha": reviewed[
            "active_executor_workflow_blob_sha"
        ],
        "active_executor_workflow_path": reviewed[
            "active_executor_workflow_path"
        ],
        "active_executor_workflow_present": True,
        "executor_workflow_run_count": 0,
        "expected_executor_run_number": 1,
        "expected_executor_run_attempt": 1,
        "historical_gate_proof_run_id": reviewed[
            "historical_gate_proof_run_id"
        ],
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_executor_dispatch_command": reviewed[
            "planned_executor_dispatch_command"
        ],
        "explicit_one_shot_executor_dispatch_authorized": True,
        "historical_executor_workflow_installed": True,
        "historical_executor_available": True,
        "historical_result_dispatch_authorized": True,
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
        "next_gate": "SUBMIT_AUTHORIZED_ONE_SHOT_EXECUTOR_RUN_1_ATTEMPT_1",
    }
    frozen["runtime_freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "DEC433_REVIEWER_BLOB_SHA",
    "DEC434_FREEZE_BUILDER_BLOB_SHA",
    "DEC434_FREEZE_FINGERPRINT_SHA256",
    "EXP062_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_PROOF_RUNTIME_FREEZE_DECISION",
    "EXP062_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_PROOF_RUNTIME_FREEZE_VERSION",
    "ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_CANONICAL_SHA256",
    "ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_ARTIFACT_DIGEST",
    "ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_ARTIFACT_ID",
    "ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256",
    "ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_HEAD_SHA",
    "ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_JOB_ID",
    "ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_RUN_ID",
    "ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_RAW_SHA256",
    "freeze_one_shot_executor_dispatch_action_preflight_proof_runtime_evidence",
    "validate_one_shot_executor_dispatch_action_preflight_proof_runtime_freeze_sources",
]
