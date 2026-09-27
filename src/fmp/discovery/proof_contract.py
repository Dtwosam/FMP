from __future__ import annotations

import hashlib
import json
from typing import Mapping

from .run_contract import (
    AGGREGATE_JOB_NAME,
    EXP061_RUN_CONTRACT_VERSION,
    PREFLIGHT_JOB_NAME,
    WORKFLOW_BRANCH,
    WORKFLOW_EVENT,
    WORKFLOW_NAME,
    WORKFLOW_PATH,
    WORKFLOW_RUN_ATTEMPT,
    expected_job_names,
    expected_preflight_artifact_name,
)
from .workflow_source import (
    EXP061_DORMANT_WORKFLOW_SOURCE_DECISION,
    EXP061_DORMANT_WORKFLOW_SOURCE_VERSION,
    workflow_source_payload,
)


EXP061_GATE_PROOF_CONTRACT_DECISION = "DEC-277"
EXP061_GATE_PROOF_CONTRACT_VERSION = "fmp-exp061-gate-proof-contract-v1"

PROOF_DISPATCH_AUTHORIZED = False
HISTORICAL_RESULT_DISPATCH_AUTHORIZED = False
HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED = False
DISCOVERY_RESULT_AUTHORIZED = False
RERUN_AUTHORIZED = False
RETRY_AUTHORIZED = False
REPLACEMENT_RUN_AUTHORIZED = False
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


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value


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


def proof_contract_payload(*, expected_head_sha: str) -> dict[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    expected_jobs = expected_job_names()
    return {
        "decision": EXP061_GATE_PROOF_CONTRACT_DECISION,
        "contract_version": EXP061_GATE_PROOF_CONTRACT_VERSION,
        "run_contract_version": EXP061_RUN_CONTRACT_VERSION,
        "expected_head_sha": expected_head_sha,
        "workflow": {
            "name": WORKFLOW_NAME,
            "path": WORKFLOW_PATH,
            "event": WORKFLOW_EVENT,
            "branch": WORKFLOW_BRANCH,
            "run_attempt": WORKFLOW_RUN_ATTEMPT,
        },
        "expected_terminal_run_conclusion": "failure",
        "expected_preflight_job": {
            "name": PREFLIGHT_JOB_NAME,
            "conclusion": "failure",
        },
        "allowed_downstream_job_names": list(expected_jobs[1:]),
        "required_downstream_conclusion_if_materialized": "skipped",
        "expected_artifacts": [
            expected_preflight_artifact_name(code_commit=expected_head_sha)
        ],
        "forbidden_artifact_prefixes": [
            "phase8a-exp061-cell-",
            "phase8a-exp061-aggregate-",
        ],
        "historical_result_slot_consumed": False,
        "authorizations": {
            "proof_dispatch_authorized": PROOF_DISPATCH_AUTHORIZED,
            "historical_result_dispatch_authorized": (
                HISTORICAL_RESULT_DISPATCH_AUTHORIZED
            ),
            "historical_discovery_execution_authorized": (
                HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED
            ),
            "discovery_result_authorized": DISCOVERY_RESULT_AUTHORIZED,
            "rerun_authorized": RERUN_AUTHORIZED,
            "retry_authorized": RETRY_AUTHORIZED,
            "replacement_run_authorized": REPLACEMENT_RUN_AUTHORIZED,
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
        },
    }


def _validate_run(
    run: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> None:
    exact = {
        "name": WORKFLOW_NAME,
        "path": WORKFLOW_PATH,
        "event": WORKFLOW_EVENT,
        "head_branch": WORKFLOW_BRANCH,
        "head_sha": expected_head_sha,
        "run_attempt": WORKFLOW_RUN_ATTEMPT,
        "status": "completed",
        "conclusion": "failure",
    }
    for field, expected in exact.items():
        if run.get(field) != expected:
            raise ValueError(f"EXP-061 gate proof run {field} mismatch")
    run_id = run.get("id")
    if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
        raise ValueError("EXP-061 gate proof run id is invalid")


def _validate_jobs(jobs_payload: Mapping[str, object]) -> dict[str, object]:
    raw = jobs_payload.get("jobs")
    if not isinstance(raw, list) or not raw:
        raise ValueError("EXP-061 gate proof requires terminal job evidence")
    expected = set(expected_job_names())
    seen: set[str] = set()
    preflight_count = 0
    materialized_downstream: list[str] = []
    for item in raw:
        if not isinstance(item, Mapping):
            raise ValueError("EXP-061 gate proof job row is malformed")
        name = item.get("name")
        if not isinstance(name, str) or name not in expected:
            raise ValueError(f"unexpected EXP-061 gate proof job: {name!r}")
        if name in seen:
            raise ValueError(f"duplicate EXP-061 gate proof job: {name}")
        seen.add(name)
        if item.get("status") != "completed":
            raise ValueError("EXP-061 gate proof requires terminal materialized jobs")
        if name == PREFLIGHT_JOB_NAME:
            preflight_count += 1
            if item.get("conclusion") != "failure":
                raise ValueError("EXP-061 gate proof preflight must fail closed")
        else:
            materialized_downstream.append(name)
            if item.get("conclusion") != "skipped":
                raise ValueError(
                    "EXP-061 gate proof downstream jobs must be skipped"
                )

    if preflight_count != 1:
        raise ValueError("EXP-061 gate proof requires exactly one preflight job")
    return {
        "materialized_job_count": len(raw),
        "materialized_downstream_job_count": len(materialized_downstream),
        "materialized_downstream_job_names": sorted(materialized_downstream),
    }


def _validate_artifacts(
    artifacts_payload: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> Mapping[str, object]:
    raw = artifacts_payload.get("artifacts")
    if not isinstance(raw, list):
        raise ValueError("EXP-061 gate proof artifact payload is malformed")
    expected_name = expected_preflight_artifact_name(
        code_commit=expected_head_sha
    )
    if len(raw) != 1:
        raise ValueError(
            "EXP-061 gate proof requires exactly one preflight artifact"
        )
    item = raw[0]
    if not isinstance(item, Mapping):
        raise ValueError("EXP-061 gate proof artifact row is malformed")
    if item.get("name") != expected_name:
        raise ValueError("EXP-061 gate proof artifact name mismatch")
    if item.get("expired") is not False:
        raise ValueError("EXP-061 gate proof preflight artifact must be non-expired")
    _validate_sha256_digest(
        item.get("digest"),
        field="EXP-061 gate proof preflight artifact digest",
    )
    artifact_id = item.get("id")
    if not isinstance(artifact_id, int) or isinstance(artifact_id, bool) or artifact_id <= 0:
        raise ValueError("EXP-061 gate proof artifact id is invalid")
    return item


def _validate_preflight(
    value: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> None:
    if value.get("decision") != EXP061_DORMANT_WORKFLOW_SOURCE_DECISION:
        raise ValueError("EXP-061 gate proof preflight decision mismatch")
    if value.get("source_version") != EXP061_DORMANT_WORKFLOW_SOURCE_VERSION:
        raise ValueError("EXP-061 gate proof preflight source version mismatch")
    if value.get("source_ready") is not True:
        raise ValueError("EXP-061 gate proof source preflight must be ready")
    if value.get("code_commit") != expected_head_sha:
        raise ValueError("EXP-061 gate proof preflight code commit mismatch")

    expected_workflow_source = workflow_source_payload(
        code_commit=expected_head_sha
    )
    if value.get("workflow_source") != expected_workflow_source:
        raise ValueError("EXP-061 gate proof workflow-source payload mismatch")

    unsigned = dict(value)
    unsigned.pop("source_fingerprint", None)
    unsigned.pop("code_commit", None)
    unsigned.pop("workflow_source", None)
    fingerprint = value.get("source_fingerprint")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise ValueError("EXP-061 gate proof source fingerprint is malformed")
    if _sha256(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("EXP-061 gate proof source fingerprint mismatch")

    if value.get("verified_pair_timeframe_source_count") != 9:
        raise ValueError("EXP-061 gate proof source-count mismatch")
    for field in (
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
    ):
        if value.get(field) is not False:
            raise ValueError(
                f"EXP-061 gate proof preflight {field} must remain false"
            )


def validate_gate_proof_terminal(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    preflight_evidence: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    _validate_run(run, expected_head_sha=expected_head_sha)
    job_report = _validate_jobs(jobs_payload)
    artifact = _validate_artifacts(
        artifacts_payload,
        expected_head_sha=expected_head_sha,
    )
    _validate_preflight(
        preflight_evidence,
        expected_head_sha=expected_head_sha,
    )

    return {
        "decision": EXP061_GATE_PROOF_CONTRACT_DECISION,
        "contract_version": EXP061_GATE_PROOF_CONTRACT_VERSION,
        "stage": "EXP061_GATE_PROOF_REVIEWED_FAIL_CLOSED",
        "proof_run_id": run["id"],
        "proof_head_sha": expected_head_sha,
        "proof_run_attempt": WORKFLOW_RUN_ATTEMPT,
        "proof_run_conclusion": "failure",
        "preflight_artifact_id": artifact["id"],
        "preflight_artifact_digest": artifact["digest"],
        **job_report,
        "historical_result_slot_consumed": False,
        "historical_discovery_execution_occurred": False,
        "cell_result_artifact_count": 0,
        "aggregate_result_artifact_count": 0,
        "proof_dispatch_authorized": PROOF_DISPATCH_AUTHORIZED,
        "historical_result_dispatch_authorized": (
            HISTORICAL_RESULT_DISPATCH_AUTHORIZED
        ),
        "historical_discovery_execution_authorized": (
            HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED
        ),
        "discovery_result_authorized": DISCOVERY_RESULT_AUTHORIZED,
        "rerun_authorized": RERUN_AUTHORIZED,
        "retry_authorized": RETRY_AUTHORIZED,
        "replacement_run_authorized": REPLACEMENT_RUN_AUTHORIZED,
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
    "EXP061_GATE_PROOF_CONTRACT_DECISION",
    "EXP061_GATE_PROOF_CONTRACT_VERSION",
    "HISTORICAL_RESULT_DISPATCH_AUTHORIZED",
    "PROOF_DISPATCH_AUTHORIZED",
    "proof_contract_payload",
    "validate_gate_proof_terminal",
]
