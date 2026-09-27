from __future__ import annotations

import hashlib
import json
from typing import Mapping

from .proof_contract import (
    EXP061_GATE_PROOF_CONTRACT_DECISION,
    EXP061_GATE_PROOF_CONTRACT_VERSION,
)
from .run_contract import (
    AGGREGATE_JOB_NAME,
    PREFLIGHT_JOB_NAME,
    WORKFLOW_BRANCH,
    WORKFLOW_EVENT,
    WORKFLOW_NAME,
    WORKFLOW_PATH,
    WORKFLOW_RUN_ATTEMPT,
    expected_preflight_artifact_name,
)
from .workflow_source import (
    EXP061_DORMANT_WORKFLOW_SOURCE_DECISION,
    EXP061_DORMANT_WORKFLOW_SOURCE_VERSION,
    FEATURE_EVIDENCE_ARTIFACT,
    FEATURE_RUN,
    OUTCOME_EVIDENCE_ARTIFACT,
    OUTCOME_RUN,
    workflow_source_payload,
)


EXP061_REVIEWED_GATE_PROOF_DECISION = "DEC-280"
EXP061_REVIEWED_GATE_PROOF_VERSION = "fmp-exp061-reviewed-gate-proof-v1"

DEC279_MERGED_COMMIT = "041b7b2f5aac8821156fab346df8ab30f4be2a7b"
DEC279_EXECUTOR_RUN_ID = 36319870713
DEC279_EXECUTOR_WORKFLOW_NAME = "phase8a-exp061-proof-one-shot-execute"
DEC279_EXECUTOR_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp061-proof-one-shot-execute.yml"
)
DEC279_EXECUTOR_ARTIFACT_ID = 10931792980
DEC279_EXECUTOR_ARTIFACT_NAME = (
    "exp061-dec279-proof-dispatch-evidence-"
    "041b7b2f5aac8821156fab346df8ab30f4be2a7b"
)
DEC279_EXECUTOR_ARTIFACT_DIGEST = (
    "sha256:a7a0ea04de1b5f67a7eaa64419b6be15ddddee049a0fc53021920eb2308f540f"
)

EXP061_GATE_PROOF_RUN_ID = 36319888985
EXP061_GATE_PROOF_HEAD_SHA = DEC279_MERGED_COMMIT
EXP061_GATE_PROOF_PREFLIGHT_JOB_ID = 108621570094
EXP061_GATE_PROOF_SKIPPED_MATRIX_JOB_ID = 108621636801
EXP061_GATE_PROOF_AGGREGATE_JOB_ID = 108621637326
EXP061_GATE_PROOF_SKIPPED_MATRIX_JOB_NAME = (
    "exp061-cell-${{ matrix.dataset.symbol }}-"
    "${{ matrix.dataset.timeframe }}-"
    "${{ matrix.dataset.horizon }}m"
)
EXP061_GATE_PROOF_PREFLIGHT_ARTIFACT_ID = 10932485842
EXP061_GATE_PROOF_PREFLIGHT_ARTIFACT_DIGEST = (
    "sha256:0dfbf4c76874bb2b056a835ff0d7fdf2199ddda279e40a60924128a7ff29573d"
)

PROOF_RERUN_AUTHORIZED = False
PROOF_RETRY_AUTHORIZED = False
PROOF_REPLACEMENT_AUTHORIZED = False
HISTORICAL_RESULT_DISPATCH_AUTHORIZED = False
HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED = False
DISCOVERY_RESULT_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


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


def _validate_sha256_digest(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        raise ValueError(f"{field} must use sha256:<hex>")
    raw = value.removeprefix("sha256:")
    if len(raw) != 64:
        raise ValueError(f"{field} must contain 64 hex characters")
    try:
        int(raw, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value


def _require_exact(
    value: Mapping[str, object],
    expected: Mapping[str, object],
    *,
    prefix: str,
) -> None:
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(f"{prefix} {field} mismatch")


def _validate_executor(
    *,
    executor_run: Mapping[str, object],
    executor_artifacts_payload: Mapping[str, object],
    executor_evidence: Mapping[str, object],
) -> None:
    _require_exact(
        executor_run,
        {
            "id": DEC279_EXECUTOR_RUN_ID,
            "name": DEC279_EXECUTOR_WORKFLOW_NAME,
            "path": DEC279_EXECUTOR_WORKFLOW_PATH,
            "event": "push",
            "head_branch": WORKFLOW_BRANCH,
            "head_sha": DEC279_MERGED_COMMIT,
            "run_attempt": 1,
            "status": "completed",
            "conclusion": "success",
        },
        prefix="DEC-279 executor run",
    )

    artifacts = executor_artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 1:
        raise ValueError("DEC-279 executor requires exactly one dispatch-evidence artifact")
    artifact = artifacts[0]
    if not isinstance(artifact, Mapping):
        raise ValueError("DEC-279 executor artifact row is malformed")
    _require_exact(
        artifact,
        {
            "id": DEC279_EXECUTOR_ARTIFACT_ID,
            "name": DEC279_EXECUTOR_ARTIFACT_NAME,
            "digest": DEC279_EXECUTOR_ARTIFACT_DIGEST,
            "expired": False,
        },
        prefix="DEC-279 executor artifact",
    )
    _validate_sha256_digest(
        artifact.get("digest"),
        field="DEC-279 executor artifact digest",
    )

    _require_exact(
        executor_evidence,
        {
            "decision": "DEC-278",
            "executor_decision": "DEC-279",
            "executor_version": "fmp-exp061-proof-one-shot-executor-v1",
            "expected_head_sha": DEC279_MERGED_COMMIT,
            "executor_head_sha": DEC279_MERGED_COMMIT,
            "fresh_plan_rechecked_twice": True,
            "matching_manual_main_run_count": 0,
            "planned_dispatch_command": (
                "gh workflow run phase8a-exp061-discovery.yml --ref main"
            ),
            "dispatch_command": (
                "gh workflow run phase8a-exp061-discovery.yml --ref main"
            ),
            "proof_contract_version": EXP061_GATE_PROOF_CONTRACT_VERSION,
            "proof_dispatch_authorized": False,
            "proof_dispatch_authorized_by_dec279": True,
            "proof_dispatch_submitted": True,
            "proof_execute_mode_available": False,
            "historical_result_claimed": False,
            "historical_result_dispatch_authorized": False,
            "historical_result_slot_consumed": False,
            "historical_discovery_execution_authorized": False,
            "discovery_result_authorized": False,
            "rerun_authorized": False,
            "retry_authorized": False,
            "replacement_run_authorized": False,
            "reserved_robustness_access_authorized": False,
            "candidate_compilation_authorized": False,
            "phase8b_authorized": False,
            "demo_order_authorized": False,
            "broker_mutation_authorized": False,
            "live_order_authorized": False,
            "real_money_authorized": False,
            "trading_authorized": False,
        },
        prefix="DEC-279 executor evidence",
    )


def _validate_proof_run(run: Mapping[str, object]) -> None:
    _require_exact(
        run,
        {
            "id": EXP061_GATE_PROOF_RUN_ID,
            "name": WORKFLOW_NAME,
            "path": WORKFLOW_PATH,
            "event": WORKFLOW_EVENT,
            "head_branch": WORKFLOW_BRANCH,
            "head_sha": EXP061_GATE_PROOF_HEAD_SHA,
            "run_attempt": WORKFLOW_RUN_ATTEMPT,
            "status": "completed",
            "conclusion": "failure",
        },
        prefix="EXP-061 gate proof run",
    )


def _validate_jobs(jobs_payload: Mapping[str, object]) -> None:
    jobs = jobs_payload.get("jobs")
    if not isinstance(jobs, list) or len(jobs) != 3:
        raise ValueError("DEC-280 requires the exact three materialized proof jobs")

    expected = {
        EXP061_GATE_PROOF_PREFLIGHT_JOB_ID: (
            PREFLIGHT_JOB_NAME,
            "failure",
        ),
        EXP061_GATE_PROOF_SKIPPED_MATRIX_JOB_ID: (
            EXP061_GATE_PROOF_SKIPPED_MATRIX_JOB_NAME,
            "skipped",
        ),
        EXP061_GATE_PROOF_AGGREGATE_JOB_ID: (
            AGGREGATE_JOB_NAME,
            "skipped",
        ),
    }
    seen: set[int] = set()
    for row in jobs:
        if not isinstance(row, Mapping):
            raise ValueError("DEC-280 proof job row is malformed")
        job_id = row.get("id")
        if (
            not isinstance(job_id, int)
            or isinstance(job_id, bool)
            or job_id not in expected
            or job_id in seen
        ):
            raise ValueError("DEC-280 proof job id mismatch")
        seen.add(job_id)
        name, conclusion = expected[job_id]
        _require_exact(
            row,
            {
                "name": name,
                "status": "completed",
                "conclusion": conclusion,
            },
            prefix=f"DEC-280 proof job {job_id}",
        )
    if seen != set(expected):
        raise ValueError("DEC-280 proof job coverage mismatch")


def _validate_proof_artifact(artifacts_payload: Mapping[str, object]) -> None:
    artifacts = artifacts_payload.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 1:
        raise ValueError("DEC-280 requires exactly one proof preflight artifact")
    artifact = artifacts[0]
    if not isinstance(artifact, Mapping):
        raise ValueError("DEC-280 proof artifact row is malformed")
    _require_exact(
        artifact,
        {
            "id": EXP061_GATE_PROOF_PREFLIGHT_ARTIFACT_ID,
            "name": expected_preflight_artifact_name(
                code_commit=EXP061_GATE_PROOF_HEAD_SHA
            ),
            "digest": EXP061_GATE_PROOF_PREFLIGHT_ARTIFACT_DIGEST,
            "expired": False,
        },
        prefix="DEC-280 proof artifact",
    )
    _validate_sha256_digest(
        artifact.get("digest"),
        field="DEC-280 proof artifact digest",
    )


def _validate_preflight(value: Mapping[str, object]) -> None:
    _require_exact(
        value,
        {
            "decision": EXP061_DORMANT_WORKFLOW_SOURCE_DECISION,
            "source_version": EXP061_DORMANT_WORKFLOW_SOURCE_VERSION,
            "feature_run_id": FEATURE_RUN["id"],
            "feature_head_sha": FEATURE_RUN["head_sha"],
            "outcome_run_id": OUTCOME_RUN["id"],
            "outcome_head_sha": OUTCOME_RUN["head_sha"],
            "feature_evidence_artifact_id": FEATURE_EVIDENCE_ARTIFACT["id"],
            "outcome_evidence_artifact_id": OUTCOME_EVIDENCE_ARTIFACT["id"],
            "verified_pair_timeframe_source_count": 9,
            "source_ready": True,
            "code_commit": EXP061_GATE_PROOF_HEAD_SHA,
            "workflow_source": workflow_source_payload(
                code_commit=EXP061_GATE_PROOF_HEAD_SHA
            ),
            "historical_discovery_execution_authorized": False,
            "discovery_result_authorized": False,
            "reserved_robustness_access_authorized": False,
            "candidate_compilation_authorized": False,
            "promotion_authorized": False,
            "phase8b_authorized": False,
            "demo_order_authorized": False,
            "broker_mutation_authorized": False,
            "live_order_authorized": False,
            "real_money_authorized": False,
            "trading_authorized": False,
        },
        prefix="DEC-280 preflight evidence",
    )

    fingerprint = value.get("source_fingerprint")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise ValueError("DEC-280 preflight source fingerprint is malformed")
    try:
        int(fingerprint, 16)
    except ValueError as exc:
        raise ValueError("DEC-280 preflight source fingerprint is not hexadecimal") from exc

    unsigned = dict(value)
    unsigned.pop("source_fingerprint", None)
    unsigned.pop("code_commit", None)
    unsigned.pop("workflow_source", None)
    if hashlib.sha256(_canonical_json(unsigned)).hexdigest() != fingerprint:
        raise ValueError("DEC-280 preflight source fingerprint mismatch")


def freeze_reviewed_gate_proof(
    *,
    executor_run: Mapping[str, object],
    executor_artifacts_payload: Mapping[str, object],
    executor_evidence: Mapping[str, object],
    proof_run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    proof_artifacts_payload: Mapping[str, object],
    preflight_evidence: Mapping[str, object],
) -> dict[str, object]:
    _validate_executor(
        executor_run=executor_run,
        executor_artifacts_payload=executor_artifacts_payload,
        executor_evidence=executor_evidence,
    )
    _validate_proof_run(proof_run)
    _validate_jobs(jobs_payload)
    _validate_proof_artifact(proof_artifacts_payload)
    _validate_preflight(preflight_evidence)

    return {
        "decision": EXP061_REVIEWED_GATE_PROOF_DECISION,
        "version": EXP061_REVIEWED_GATE_PROOF_VERSION,
        "proof_contract_decision": EXP061_GATE_PROOF_CONTRACT_DECISION,
        "proof_contract_version": EXP061_GATE_PROOF_CONTRACT_VERSION,
        "stage": "EXP061_GATE_PROOF_REVIEWED_FAIL_CLOSED_AND_FROZEN",
        "proof_outcome": "EXPECTED_FAIL_CLOSED_EXECUTION_GATE",
        "executor_run_id": DEC279_EXECUTOR_RUN_ID,
        "executor_head_sha": DEC279_MERGED_COMMIT,
        "proof_run_id": EXP061_GATE_PROOF_RUN_ID,
        "proof_head_sha": EXP061_GATE_PROOF_HEAD_SHA,
        "proof_run_attempt": WORKFLOW_RUN_ATTEMPT,
        "proof_run_conclusion": "failure",
        "preflight_job_id": EXP061_GATE_PROOF_PREFLIGHT_JOB_ID,
        "skipped_matrix_placeholder_job_id": (
            EXP061_GATE_PROOF_SKIPPED_MATRIX_JOB_ID
        ),
        "aggregate_job_id": EXP061_GATE_PROOF_AGGREGATE_JOB_ID,
        "preflight_artifact_id": EXP061_GATE_PROOF_PREFLIGHT_ARTIFACT_ID,
        "preflight_artifact_digest": (
            EXP061_GATE_PROOF_PREFLIGHT_ARTIFACT_DIGEST
        ),
        "github_skipped_matrix_api_shape": "UNEXPANDED_MATRIX_JOB_TEMPLATE",
        "dec277_exact_downstream_job_name_compatible": False,
        "fail_closed_semantics_verified": True,
        "historical_result_slot_consumed": False,
        "historical_discovery_execution_occurred": False,
        "cell_result_artifact_count": 0,
        "aggregate_result_artifact_count": 0,
        "proof_rerun_authorized": PROOF_RERUN_AUTHORIZED,
        "proof_retry_authorized": PROOF_RETRY_AUTHORIZED,
        "proof_replacement_authorized": PROOF_REPLACEMENT_AUTHORIZED,
        "historical_result_dispatch_authorized": (
            HISTORICAL_RESULT_DISPATCH_AUTHORIZED
        ),
        "historical_discovery_execution_authorized": (
            HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED
        ),
        "discovery_result_authorized": DISCOVERY_RESULT_AUTHORIZED,
        "reserved_robustness_access_authorized": (
            RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED
        ),
        "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
    }


__all__ = [
    "DEC279_EXECUTOR_ARTIFACT_DIGEST",
    "DEC279_EXECUTOR_ARTIFACT_ID",
    "DEC279_EXECUTOR_RUN_ID",
    "EXP061_GATE_PROOF_HEAD_SHA",
    "EXP061_GATE_PROOF_PREFLIGHT_ARTIFACT_DIGEST",
    "EXP061_GATE_PROOF_PREFLIGHT_ARTIFACT_ID",
    "EXP061_GATE_PROOF_RUN_ID",
    "EXP061_REVIEWED_GATE_PROOF_DECISION",
    "EXP061_REVIEWED_GATE_PROOF_VERSION",
    "freeze_reviewed_gate_proof",
]
