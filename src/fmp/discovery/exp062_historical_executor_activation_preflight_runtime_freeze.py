from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_historical_executor_activation_preflight_freeze import (
    EXP062_REVIEWED_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_FREEZE_DECISION,
    EXP062_REVIEWED_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_FREEZE_VERSION,
    freeze_reviewed_historical_executor_activation_preflight,
)
from .exp062_historical_executor_activation_preflight_review import (
    EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_REVIEW_DECISION,
    EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_REVIEW_VERSION,
    review_historical_executor_activation_preflight_proof,
)
from .exp062_historical_terminal_review_contract import (
    EXP062_HISTORICAL_TERMINAL_REVIEW_DECISION,
    EXP062_HISTORICAL_TERMINAL_REVIEW_VERSION,
)


EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_RUNTIME_FREEZE_DECISION = "DEC-336"
EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_RUNTIME_FREEZE_VERSION = (
    "fmp-exp062-historical-executor-activation-preflight-runtime-freeze-v1"
)

ACTIVATION_PREFLIGHT_PROOF_HEAD_SHA = (
    "12d11320ae302902df0a0deb7343408922deee83"
)
ACTIVATION_PREFLIGHT_PROOF_RUN_ID = 36431469794
ACTIVATION_PREFLIGHT_PROOF_JOB_ID = 108958446980
ACTIVATION_PREFLIGHT_PROOF_ARTIFACT_ID = 10973597441
ACTIVATION_PREFLIGHT_PROOF_ARTIFACT_NAME = (
    "exp062-dec332-historical-executor-activation-preflight-"
    "12d11320ae302902df0a0deb7343408922deee83"
)
ACTIVATION_PREFLIGHT_PROOF_ARTIFACT_DIGEST = (
    "sha256:ee6e7ac2e8c18e1f8d276bba14ca942e20615143316ac185f4b814333804c2d5"
)
ACTIVATION_PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256 = (
    "ee6e7ac2e8c18e1f8d276bba14ca942e20615143316ac185f4b814333804c2d5"
)
ACTIVATION_PREFLIGHT_RAW_SHA256 = (
    "775010a0c3d4afe11191adb53d8ad54e7cf0d5de85b1a0b5adcb28c470e9a4a5"
)
ACTIVATION_PREFLIGHT_CANONICAL_SHA256 = (
    "98b9180ae3b438b3c372ba34cbab9473d7f38ba5c1eb1add2dee988df4e09ad8"
)

DEC333_REVIEWER_BLOB_SHA = "c540fb14c7048de2e6f368b0c96b51715c83e9a5"
DEC334_TERMINAL_REVIEW_BLOB_SHA = (
    "fda2a45f74b101303467cf7b8527bec1bfc5e168"
)
DEC335_FREEZE_BUILDER_BLOB_SHA = (
    "9cb660f06fc9da8a8d4927d8ff953413a6df13fe"
)
DEC335_FREEZE_FINGERPRINT_SHA256 = (
    "567320a598f245a8e7521281ddde3a1acaa0e3f294aebe12554688d2258f020b"
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


def validate_historical_executor_activation_preflight_runtime_freeze_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dec333_reviewer": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_executor_activation_preflight_review.py",
            DEC333_REVIEWER_BLOB_SHA,
        ),
        "dec334_terminal_review_contract": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_terminal_review_contract.py",
            DEC334_TERMINAL_REVIEW_BLOB_SHA,
        ),
        "dec335_freeze_builder": (
            root
            / "src/fmp/discovery/"
            "exp062_historical_executor_activation_preflight_freeze.py",
            DEC335_FREEZE_BUILDER_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"missing DEC-336 source dependency: {path}")
        actual_sha = _git_blob_sha(path)
        if actual_sha != expected_sha:
            raise ValueError(
                f"DEC-336 {label} Git blob mismatch: "
                f"{actual_sha} != {expected_sha}"
            )
        actual[label] = actual_sha
    return actual


def _validate_reviewed_result(value: Mapping[str, object]) -> None:
    _require_exact(
        value,
        {
            "decision": (
                EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_REVIEW_DECISION
            ),
            "version": (
                EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_REVIEW_VERSION
            ),
            "stage": (
                "EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_PROOF_"
                "REVIEWED_SLOT_AVAILABLE"
            ),
            "proof_run_id": ACTIVATION_PREFLIGHT_PROOF_RUN_ID,
            "proof_head_sha": ACTIVATION_PREFLIGHT_PROOF_HEAD_SHA,
            "proof_run_number": 1,
            "proof_run_attempt": 1,
            "proof_run_conclusion": "success",
            "proof_job_id": ACTIVATION_PREFLIGHT_PROOF_JOB_ID,
            "proof_artifact_id": ACTIVATION_PREFLIGHT_PROOF_ARTIFACT_ID,
            "proof_artifact_name": ACTIVATION_PREFLIGHT_PROOF_ARTIFACT_NAME,
            "proof_artifact_digest": ACTIVATION_PREFLIGHT_PROOF_ARTIFACT_DIGEST,
            "preflight_raw_sha256": ACTIVATION_PREFLIGHT_RAW_SHA256,
            "preflight_canonical_sha256": ACTIVATION_PREFLIGHT_CANONICAL_SHA256,
            "preflight_decision": "DEC-331",
            "preflight_version": (
                "fmp-exp062-historical-executor-activation-preflight-v1"
            ),
            "historical_gate_proof_run_id": 36358289723,
            "historical_result_attempt_count": 0,
            "historical_result_slot_consumed": False,
            "historical_result_slot_verified_available": True,
            "expected_target_run_number": 2,
            "expected_target_run_attempt": 1,
            "one_shot_executor_activation_source_authorized": True,
            "historical_executor_available": False,
            "historical_result_dispatch_authorized": False,
            "historical_execute_mode_available": False,
            "historical_discovery_execution_authorized": True,
            "discovery_result_authorized": True,
            "next_gate": (
                "IMMUTABLE_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_"
                "PROOF_FREEZE_BEFORE_EXECUTOR"
            ),
        },
        prefix="DEC-336 reviewed result",
    )
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-336 reviewed result {field} must remain false"
            )


def _validate_dec335_freeze(value: Mapping[str, object]) -> None:
    _require_exact(
        value,
        {
            "decision": (
                EXP062_REVIEWED_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_FREEZE_DECISION
            ),
            "version": (
                EXP062_REVIEWED_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_FREEZE_VERSION
            ),
            "stage": (
                "EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_"
                "REVIEWED_AND_FROZEN"
            ),
            "proof_run_id": ACTIVATION_PREFLIGHT_PROOF_RUN_ID,
            "proof_head_sha": ACTIVATION_PREFLIGHT_PROOF_HEAD_SHA,
            "proof_run_number": 1,
            "proof_run_attempt": 1,
            "proof_run_conclusion": "success",
            "proof_job_id": ACTIVATION_PREFLIGHT_PROOF_JOB_ID,
            "proof_artifact_id": ACTIVATION_PREFLIGHT_PROOF_ARTIFACT_ID,
            "proof_artifact_name": ACTIVATION_PREFLIGHT_PROOF_ARTIFACT_NAME,
            "proof_artifact_digest": ACTIVATION_PREFLIGHT_PROOF_ARTIFACT_DIGEST,
            "preflight_raw_sha256": ACTIVATION_PREFLIGHT_RAW_SHA256,
            "preflight_canonical_sha256": ACTIVATION_PREFLIGHT_CANONICAL_SHA256,
            "historical_result_attempt_count": 0,
            "historical_result_slot_consumed": False,
            "historical_result_slot_verified_available": True,
            "expected_target_run_number": 2,
            "expected_target_run_attempt": 1,
            "planned_dispatch_command_frozen": (
                "gh workflow run phase8a-exp062-discovery.yml --ref main"
            ),
            "one_shot_executor_activation_source_authorized": True,
            "historical_executor_available": False,
            "historical_result_dispatch_authorized": False,
            "historical_execute_mode_available": False,
            "historical_discovery_execution_authorized": True,
            "discovery_result_authorized": True,
            "freeze_fingerprint_sha256": (
                DEC335_FREEZE_FINGERPRINT_SHA256
            ),
            "next_gate": (
                "CONCRETE_EXECUTOR_ACTIVATION_PREFLIGHT_RUNTIME_"
                "EVIDENCE_BINDING_BEFORE_EXECUTOR"
            ),
        },
        prefix="DEC-336 DEC-335 freeze",
    )
    for field in _FALSE_AUTHORITY_FIELDS:
        if value.get(field) is not False:
            raise ValueError(
                f"DEC-336 DEC-335 freeze {field} must remain false"
            )

    unsigned = dict(value)
    fingerprint = unsigned.pop("freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC335_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC335_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-336 DEC-335 freeze fingerprint mismatch")


def freeze_historical_executor_activation_preflight_runtime_evidence(
    *,
    repository_root: Path,
    proof_run: Mapping[str, object],
    proof_jobs_payload: Mapping[str, object],
    proof_artifacts_payload: Mapping[str, object],
    preflight_bytes: bytes,
    artifact_zip_sha256: str,
) -> dict[str, object]:
    source_blobs = (
        validate_historical_executor_activation_preflight_runtime_freeze_sources(
            repository_root=repository_root,
        )
    )

    reviewed = review_historical_executor_activation_preflight_proof(
        run=proof_run,
        jobs_payload=proof_jobs_payload,
        artifacts_payload=proof_artifacts_payload,
        preflight_bytes=preflight_bytes,
        expected_head_sha=ACTIVATION_PREFLIGHT_PROOF_HEAD_SHA,
        repository_root=repository_root,
    )
    _validate_reviewed_result(reviewed)

    frozen_review = freeze_reviewed_historical_executor_activation_preflight(
        reviewed,
        expected_head_sha=ACTIVATION_PREFLIGHT_PROOF_HEAD_SHA,
    )
    _validate_dec335_freeze(frozen_review)

    artifact_zip_sha256 = _validate_sha256(
        artifact_zip_sha256,
        field="DEC-336 artifact ZIP sha256",
    )
    if (
        artifact_zip_sha256
        != ACTIVATION_PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256
    ):
        raise ValueError("DEC-336 artifact ZIP sha256 mismatch")
    if artifact_zip_sha256 != (
        ACTIVATION_PREFLIGHT_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:")
    ):
        raise ValueError(
            "DEC-336 artifact ZIP hash does not match GitHub digest"
        )

    frozen: dict[str, object] = {
        "decision": (
            EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_RUNTIME_FREEZE_DECISION
        ),
        "version": (
            EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_RUNTIME_FREEZE_VERSION
        ),
        "stage": (
            "EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_"
            "RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "activation_preflight_proof_head_sha": (
            ACTIVATION_PREFLIGHT_PROOF_HEAD_SHA
        ),
        "activation_preflight_proof_run_id": (
            ACTIVATION_PREFLIGHT_PROOF_RUN_ID
        ),
        "activation_preflight_proof_run_number": 1,
        "activation_preflight_proof_run_attempt": 1,
        "activation_preflight_proof_run_conclusion": "success",
        "activation_preflight_proof_job_id": (
            ACTIVATION_PREFLIGHT_PROOF_JOB_ID
        ),
        "activation_preflight_proof_artifact_id": (
            ACTIVATION_PREFLIGHT_PROOF_ARTIFACT_ID
        ),
        "activation_preflight_proof_artifact_name": (
            ACTIVATION_PREFLIGHT_PROOF_ARTIFACT_NAME
        ),
        "activation_preflight_proof_artifact_digest": (
            ACTIVATION_PREFLIGHT_PROOF_ARTIFACT_DIGEST
        ),
        "activation_preflight_proof_artifact_zip_sha256": (
            ACTIVATION_PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256
        ),
        "activation_preflight_raw_sha256": ACTIVATION_PREFLIGHT_RAW_SHA256,
        "activation_preflight_canonical_sha256": (
            ACTIVATION_PREFLIGHT_CANONICAL_SHA256
        ),
        "dec333_review_decision": reviewed["decision"],
        "dec333_review_version": reviewed["version"],
        "dec334_terminal_review_decision": (
            EXP062_HISTORICAL_TERMINAL_REVIEW_DECISION
        ),
        "dec334_terminal_review_version": (
            EXP062_HISTORICAL_TERMINAL_REVIEW_VERSION
        ),
        "dec335_freeze_decision": frozen_review["decision"],
        "dec335_freeze_version": frozen_review["version"],
        "dec335_freeze_fingerprint_sha256": (
            DEC335_FREEZE_FINGERPRINT_SHA256
        ),
        "dec333_reviewer_blob_sha": source_blobs["dec333_reviewer"],
        "dec334_terminal_review_contract_blob_sha": source_blobs[
            "dec334_terminal_review_contract"
        ],
        "dec335_freeze_builder_blob_sha": source_blobs[
            "dec335_freeze_builder"
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
        "one_shot_executor_activation_source_authorized": True,
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
            "SOURCE_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_BEFORE_DISPATCH"
        ),
    }
    frozen["runtime_freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "ACTIVATION_PREFLIGHT_CANONICAL_SHA256",
    "ACTIVATION_PREFLIGHT_PROOF_ARTIFACT_DIGEST",
    "ACTIVATION_PREFLIGHT_PROOF_ARTIFACT_ID",
    "ACTIVATION_PREFLIGHT_PROOF_HEAD_SHA",
    "ACTIVATION_PREFLIGHT_PROOF_JOB_ID",
    "ACTIVATION_PREFLIGHT_PROOF_RUN_ID",
    "ACTIVATION_PREFLIGHT_RAW_SHA256",
    "DEC335_FREEZE_FINGERPRINT_SHA256",
    "EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_RUNTIME_FREEZE_DECISION",
    "EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_RUNTIME_FREEZE_VERSION",
    "freeze_historical_executor_activation_preflight_runtime_evidence",
    "validate_historical_executor_activation_preflight_runtime_freeze_sources",
]
