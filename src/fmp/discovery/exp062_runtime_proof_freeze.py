from __future__ import annotations

import hashlib
import json
from typing import Mapping

from .exp062_proof_result_freeze import (
    EXP062_REVIEWED_GATE_PROOF_FREEZE_DECISION,
    EXP062_REVIEWED_GATE_PROOF_FREEZE_VERSION,
)


EXP062_RUNTIME_GATE_PROOF_FREEZE_DECISION = "DEC-306"
EXP062_RUNTIME_GATE_PROOF_FREEZE_VERSION = (
    "fmp-exp062-runtime-gate-proof-freeze-v1"
)

PROOF_HEAD_SHA = "f2c55ac36a1a9ba7596ec0d4559c877a66cda0fb"

EXECUTOR_RUN_ID = 36358278933
EXECUTOR_WORKFLOW_NAME = "phase8a-exp062-proof-one-shot-execute"
EXECUTOR_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp062-proof-one-shot-execute.yml"
)
EXECUTOR_ARTIFACT_ID = 10944404609
EXECUTOR_ARTIFACT_NAME = (
    "exp062-dec303-proof-dispatch-evidence-"
    "f2c55ac36a1a9ba7596ec0d4559c877a66cda0fb"
)
EXECUTOR_ARTIFACT_DIGEST = (
    "sha256:f1baf1e77100cb314b1e573a404508d379a569ffadea2f702bfdaebfad2c3f64"
)

PROOF_RUN_ID = 36358289723
PROOF_WORKFLOW_NAME = "phase8a-exp062-discovery"
PROOF_WORKFLOW_PATH = ".github/workflows/phase8a-exp062-discovery.yml"
PROOF_PREFLIGHT_JOB_ID = 108730271344
PROOF_MATRIX_JOB_ID = 108730343578
PROOF_AGGREGATE_JOB_ID = 108730343797
PROOF_MATRIX_JOB_NAME = (
    "exp062-cell-${{ matrix.dataset.symbol }}-"
    "${{ matrix.dataset.timeframe }}-"
    "${{ matrix.dataset.horizon }}m"
)
PROOF_PREFLIGHT_ARTIFACT_ID = 10943489995
PROOF_PREFLIGHT_ARTIFACT_NAME = (
    "phase8a-exp062-preflight-"
    "f2c55ac36a1a9ba7596ec0d4559c877a66cda0fb"
)
PROOF_PREFLIGHT_ARTIFACT_DIGEST = (
    "sha256:0cc405cc6d8b5941f7051e7907e2a7040a21a05411b29774ebbcd3884da9193f"
)

DEC305_FREEZE_FINGERPRINT_SHA256 = (
    "fadd6e512b95179fa682d05c8550c914db81e559d9c0ad8da0bedb03bb43a096"
)

EXPECTED_EVIDENCE_HASHES = {
    "executor_raw_sha256": (
        "64e8bfca0f7b5ae8814ec58c1dd7725c6b161276ec28ceacfc0ad0bc7c9483a1"
    ),
    "executor_canonical_sha256": (
        "1f7a90442cdfd587b66cb209625fbb2a4261ec1296f228663ed7bb7118320507"
    ),
    "proof_run_raw_sha256": (
        "a8926d829bffb87f3efb88dd6b5a35aa2baa59af919476dab21d592a3baac703"
    ),
    "proof_run_canonical_sha256": (
        "0e1d8cf042fbeb2b50842ed22a96df6aa62ebec8eab7460c96dae4ee41d45fca"
    ),
    "proof_inventory_raw_sha256": (
        "0e7b74527b17db5b27ce38e3bc7d26d2ef12ac2e5171170dca92c1844f209524"
    ),
    "proof_inventory_canonical_sha256": (
        "cf67da5ce88e075aed7a22168e547ac788e11144946d5b8e7d7f2209f9558b51"
    ),
    "preflight_raw_sha256": (
        "c9554dead93a0c9657a6e9f1ad18b43520bcd8ea7f0466e9f5f9f7a0bc6a7b43"
    ),
    "preflight_canonical_sha256": (
        "7c2456ce11639a23715d5c07fd28976e54631056e30d01691ef8f7cd822e100b"
    ),
    "preflight_source_fingerprint": (
        "6110876b9d2f620c780ee8952115dc6841c9269d89c6ca45d8e0c6d59ba32b3d"
    ),
}

_FALSE_FREEZE_FIELDS = (
    "historical_result_slot_consumed",
    "historical_result_slot_open_authorized",
    "historical_discovery_execution_occurred",
    "proof_rerun_authorized",
    "proof_retry_authorized",
    "proof_replacement_authorized",
    "historical_result_dispatch_authorized",
    "historical_discovery_execution_authorized",
    "discovery_result_authorized",
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


def _require_exact(
    value: Mapping[str, object],
    expected: Mapping[str, object],
    *,
    prefix: str,
) -> None:
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"{prefix} {field} mismatch")


def _validate_sha256_hex(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must contain 64 hex characters")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _validate_sha256_digest(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        raise ValueError(f"{field} must use sha256:<hex>")
    raw = value.removeprefix("sha256:")
    _validate_sha256_hex(raw, field=field)
    return value.lower()


def _validate_executor(
    *,
    run: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
) -> None:
    _require_exact(
        run,
        {
            "id": EXECUTOR_RUN_ID,
            "name": EXECUTOR_WORKFLOW_NAME,
            "path": EXECUTOR_WORKFLOW_PATH,
            "event": "push",
            "head_branch": "main",
            "head_sha": PROOF_HEAD_SHA,
            "run_number": 1,
            "run_attempt": 1,
            "status": "completed",
            "conclusion": "success",
        },
        prefix="DEC-306 executor run",
    )

    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 1:
        raise ValueError(
            "DEC-306 executor requires exactly one dispatch-evidence artifact"
        )
    artifact = artifacts[0]
    if not isinstance(artifact, Mapping):
        raise ValueError("DEC-306 executor artifact row is malformed")
    _require_exact(
        artifact,
        {
            "id": EXECUTOR_ARTIFACT_ID,
            "name": EXECUTOR_ARTIFACT_NAME,
            "digest": EXECUTOR_ARTIFACT_DIGEST,
            "expired": False,
        },
        prefix="DEC-306 executor artifact",
    )
    _validate_sha256_digest(
        artifact.get("digest"),
        field="DEC-306 executor artifact digest",
    )


def _validate_proof(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
) -> None:
    _require_exact(
        run,
        {
            "id": PROOF_RUN_ID,
            "name": PROOF_WORKFLOW_NAME,
            "path": PROOF_WORKFLOW_PATH,
            "event": "workflow_dispatch",
            "head_branch": "main",
            "head_sha": PROOF_HEAD_SHA,
            "run_number": 1,
            "run_attempt": 1,
            "status": "completed",
            "conclusion": "failure",
        },
        prefix="DEC-306 proof run",
    )

    jobs = jobs_payload.get("jobs")
    if not isinstance(jobs, list) or len(jobs) != 3:
        raise ValueError("DEC-306 proof requires exactly three materialized jobs")
    expected_jobs = {
        PROOF_PREFLIGHT_JOB_ID: ("exp062-preflight", "failure"),
        PROOF_MATRIX_JOB_ID: (PROOF_MATRIX_JOB_NAME, "skipped"),
        PROOF_AGGREGATE_JOB_ID: ("exp062-aggregate", "skipped"),
    }
    seen: set[int] = set()
    for row in jobs:
        if not isinstance(row, Mapping):
            raise ValueError("DEC-306 proof job row is malformed")
        job_id = row.get("id")
        if (
            isinstance(job_id, bool)
            or not isinstance(job_id, int)
            or job_id not in expected_jobs
            or job_id in seen
        ):
            raise ValueError("DEC-306 proof job id mismatch")
        seen.add(job_id)
        name, conclusion = expected_jobs[job_id]
        _require_exact(
            row,
            {
                "name": name,
                "status": "completed",
                "conclusion": conclusion,
            },
            prefix=f"DEC-306 proof job {job_id}",
        )
    if seen != set(expected_jobs):
        raise ValueError("DEC-306 proof job coverage mismatch")

    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 1:
        raise ValueError("DEC-306 proof requires exactly one preflight artifact")
    artifact = artifacts[0]
    if not isinstance(artifact, Mapping):
        raise ValueError("DEC-306 proof artifact row is malformed")
    _require_exact(
        artifact,
        {
            "id": PROOF_PREFLIGHT_ARTIFACT_ID,
            "name": PROOF_PREFLIGHT_ARTIFACT_NAME,
            "digest": PROOF_PREFLIGHT_ARTIFACT_DIGEST,
            "expired": False,
        },
        prefix="DEC-306 proof artifact",
    )
    _validate_sha256_digest(
        artifact.get("digest"),
        field="DEC-306 proof artifact digest",
    )


def _validate_evidence_hashes(value: Mapping[str, object]) -> None:
    for field, expected in EXPECTED_EVIDENCE_HASHES.items():
        actual = _validate_sha256_hex(
            value.get(field),
            field=f"DEC-306 evidence {field}",
        )
        if actual != expected:
            raise ValueError(f"DEC-306 evidence {field} mismatch")


def _validate_dec305_freeze(value: Mapping[str, object]) -> None:
    _require_exact(
        value,
        {
            "decision": EXP062_REVIEWED_GATE_PROOF_FREEZE_DECISION,
            "version": EXP062_REVIEWED_GATE_PROOF_FREEZE_VERSION,
            "stage": "EXP062_GATE_PROOF_REVIEWED_FAIL_CLOSED_AND_FROZEN",
            "source_review_decision": "DEC-304",
            "source_review_version": "fmp-exp062-proof-result-review-v1",
            "proof_contract_decision": "DEC-301",
            "proof_contract_version": "fmp-exp062-gate-proof-contract-v1",
            "proof_executor_decision": "DEC-303",
            "proof_executor_version": "fmp-exp062-proof-one-shot-executor-v1",
            "proof_outcome": "EXPECTED_FAIL_CLOSED_EXECUTION_GATE",
            "proof_run_id": PROOF_RUN_ID,
            "proof_head_sha": PROOF_HEAD_SHA,
            "proof_run_number": 1,
            "proof_run_attempt": 1,
            "proof_run_conclusion": "failure",
            "preflight_artifact_id": PROOF_PREFLIGHT_ARTIFACT_ID,
            "preflight_artifact_digest": PROOF_PREFLIGHT_ARTIFACT_DIGEST,
            "materialized_job_count": 3,
            "materialized_downstream_job_count": 2,
            "materialized_downstream_job_names": [
                "exp062-aggregate",
                PROOF_MATRIX_JOB_NAME,
            ],
            "github_unexpanded_matrix_placeholder_present": True,
            "fail_closed_semantics_verified": True,
            "cell_result_artifact_count": 0,
            "aggregate_result_artifact_count": 0,
            "freeze_fingerprint_sha256": DEC305_FREEZE_FINGERPRINT_SHA256,
            "next_gate": "SOURCE_ONLY_HISTORICAL_RUN_AUTHORIZATION_CONTRACT",
        },
        prefix="DEC-306 DEC-305 freeze",
    )
    for field in _FALSE_FREEZE_FIELDS:
        if value.get(field) is not False:
            raise ValueError(f"DEC-306 DEC-305 freeze {field} must remain false")

    unsigned = dict(value)
    fingerprint = unsigned.pop("freeze_fingerprint_sha256", None)
    if (
        hashlib.sha256(_canonical_json(unsigned)).hexdigest()
        != DEC305_FREEZE_FINGERPRINT_SHA256
        or fingerprint != DEC305_FREEZE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-306 DEC-305 freeze fingerprint content mismatch")


def freeze_runtime_gate_proof_evidence(
    *,
    executor_run: Mapping[str, object],
    executor_artifacts_payload: Mapping[str, object],
    proof_run: Mapping[str, object],
    proof_jobs_payload: Mapping[str, object],
    proof_artifacts_payload: Mapping[str, object],
    evidence_hashes: Mapping[str, object],
    reviewed_freeze: Mapping[str, object],
) -> dict[str, object]:
    _validate_executor(
        run=executor_run,
        artifacts_payload=executor_artifacts_payload,
    )
    _validate_proof(
        run=proof_run,
        jobs_payload=proof_jobs_payload,
        artifacts_payload=proof_artifacts_payload,
    )
    _validate_evidence_hashes(evidence_hashes)
    _validate_dec305_freeze(reviewed_freeze)

    frozen: dict[str, object] = {
        "decision": EXP062_RUNTIME_GATE_PROOF_FREEZE_DECISION,
        "version": EXP062_RUNTIME_GATE_PROOF_FREEZE_VERSION,
        "stage": "EXP062_GATE_PROOF_RUNTIME_EVIDENCE_BOUND_AND_FROZEN",
        "proof_outcome": "EXPECTED_FAIL_CLOSED_EXECUTION_GATE",
        "proof_head_sha": PROOF_HEAD_SHA,
        "executor_run_id": EXECUTOR_RUN_ID,
        "executor_run_number": 1,
        "executor_run_attempt": 1,
        "executor_run_conclusion": "success",
        "executor_artifact_id": EXECUTOR_ARTIFACT_ID,
        "executor_artifact_name": EXECUTOR_ARTIFACT_NAME,
        "executor_artifact_digest": EXECUTOR_ARTIFACT_DIGEST,
        "proof_run_id": PROOF_RUN_ID,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "failure",
        "preflight_job_id": PROOF_PREFLIGHT_JOB_ID,
        "skipped_matrix_placeholder_job_id": PROOF_MATRIX_JOB_ID,
        "aggregate_job_id": PROOF_AGGREGATE_JOB_ID,
        "preflight_artifact_id": PROOF_PREFLIGHT_ARTIFACT_ID,
        "preflight_artifact_name": PROOF_PREFLIGHT_ARTIFACT_NAME,
        "preflight_artifact_digest": PROOF_PREFLIGHT_ARTIFACT_DIGEST,
        **dict(EXPECTED_EVIDENCE_HASHES),
        "dec305_freeze_fingerprint_sha256": DEC305_FREEZE_FINGERPRINT_SHA256,
        "fail_closed_semantics_verified": True,
        "historical_result_slot_consumed": False,
        "historical_result_slot_open_authorized": False,
        "historical_result_dispatch_authorized": False,
        "historical_discovery_execution_authorized": False,
        "discovery_result_authorized": False,
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
        "next_gate": "SOURCE_ONLY_HISTORICAL_RUN_AUTHORIZATION_CONTRACT",
    }
    frozen["runtime_freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    return frozen


__all__ = [
    "DEC305_FREEZE_FINGERPRINT_SHA256",
    "EXECUTOR_ARTIFACT_DIGEST",
    "EXECUTOR_ARTIFACT_ID",
    "EXECUTOR_RUN_ID",
    "EXP062_RUNTIME_GATE_PROOF_FREEZE_DECISION",
    "EXP062_RUNTIME_GATE_PROOF_FREEZE_VERSION",
    "EXPECTED_EVIDENCE_HASHES",
    "PROOF_HEAD_SHA",
    "PROOF_PREFLIGHT_ARTIFACT_DIGEST",
    "PROOF_PREFLIGHT_ARTIFACT_ID",
    "PROOF_RUN_ID",
    "freeze_runtime_gate_proof_evidence",
]
