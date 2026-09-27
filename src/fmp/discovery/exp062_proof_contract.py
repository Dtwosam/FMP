from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .exp062_run_contract import (
    EXP062_RUN_CONTRACT_VERSION,
    PREFLIGHT_JOB_NAME,
    WORKFLOW_BRANCH,
    WORKFLOW_EVENT,
    WORKFLOW_NAME,
    WORKFLOW_PATH,
    WORKFLOW_RUN_ATTEMPT,
    expected_job_names,
    expected_preflight_artifact_name,
)
from .exp062_workflow_source import (
    EXP062_DORMANT_WORKFLOW_SOURCE_DECISION,
    EXP062_DORMANT_WORKFLOW_SOURCE_VERSION,
    validate_exp062_workflow_source_dependencies,
    workflow_source_payload,
)


EXP062_GATE_PROOF_CONTRACT_DECISION = "DEC-301"
EXP062_GATE_PROOF_CONTRACT_VERSION = "fmp-exp062-gate-proof-contract-v1"
EXPECTED_PROOF_RUN_NUMBER = 1

MATRIX_TEMPLATE_JOB_NAME = (
    "exp062-cell-${{ matrix.dataset.symbol }}-"
    "${{ matrix.dataset.timeframe }}-"
    "${{ matrix.dataset.horizon }}m"
)

PROOF_DISPATCH_AUTHORIZED = False
HISTORICAL_RESULT_DISPATCH_AUTHORIZED = False
HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED = False
DISCOVERY_RESULT_AUTHORIZED = False
RERUN_AUTHORIZED = False
RETRY_AUTHORIZED = False
REPLACEMENT_RUN_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
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
    return value.lower()


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
    return value.lower()


def proof_contract_payload(*, expected_head_sha: str) -> dict[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    jobs = expected_job_names()
    return {
        "decision": EXP062_GATE_PROOF_CONTRACT_DECISION,
        "contract_version": EXP062_GATE_PROOF_CONTRACT_VERSION,
        "run_contract_version": EXP062_RUN_CONTRACT_VERSION,
        "expected_head_sha": expected_head_sha,
        "expected_proof_run_number": EXPECTED_PROOF_RUN_NUMBER,
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
        "allowed_expanded_downstream_job_names": list(jobs[1:]),
        "allowed_matrix_template_job_name": MATRIX_TEMPLATE_JOB_NAME,
        "required_downstream_conclusion_if_materialized": "skipped",
        "expected_artifacts": [
            expected_preflight_artifact_name(
                code_commit=expected_head_sha
            )
        ],
        "forbidden_artifact_prefixes": [
            "phase8a-exp062-cell-",
            "phase8a-exp062-aggregate-",
        ],
        "historical_result_slot_consumed": False,
        "authorizations": {
            "proof_dispatch_authorized": False,
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
        },
    }


def _validate_run(
    run: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> int:
    exact = {
        "name": WORKFLOW_NAME,
        "path": WORKFLOW_PATH,
        "event": WORKFLOW_EVENT,
        "head_branch": WORKFLOW_BRANCH,
        "head_sha": expected_head_sha,
        "run_number": EXPECTED_PROOF_RUN_NUMBER,
        "run_attempt": WORKFLOW_RUN_ATTEMPT,
        "status": "completed",
        "conclusion": "failure",
    }
    for field, expected in exact.items():
        if run.get(field) != expected:
            raise ValueError(f"DEC-301 proof run {field} mismatch")
    run_id = run.get("id")
    if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
        raise ValueError("DEC-301 proof run id is invalid")
    return run_id


def _validate_jobs(
    jobs_payload: Mapping[str, object],
) -> dict[str, object]:
    raw = jobs_payload.get("jobs")
    if not isinstance(raw, list) or not raw:
        raise ValueError("DEC-301 requires terminal job evidence")

    expected = set(expected_job_names())
    allowed = expected | {MATRIX_TEMPLATE_JOB_NAME}
    seen: set[str] = set()
    preflight_count = 0
    downstream: list[str] = []

    for item in raw:
        if not isinstance(item, Mapping):
            raise ValueError("DEC-301 job row is malformed")
        name = item.get("name")
        if not isinstance(name, str) or name not in allowed:
            raise ValueError(f"DEC-301 unexpected proof job: {name!r}")
        if name in seen:
            raise ValueError(f"DEC-301 duplicate proof job: {name}")
        seen.add(name)
        if item.get("status") != "completed":
            raise ValueError("DEC-301 materialized jobs must be terminal")

        if name == PREFLIGHT_JOB_NAME:
            preflight_count += 1
            if item.get("conclusion") != "failure":
                raise ValueError("DEC-301 proof preflight must fail closed")
        else:
            downstream.append(name)
            if item.get("conclusion") != "skipped":
                raise ValueError(
                    "DEC-301 proof downstream jobs must be skipped"
                )

    if preflight_count != 1:
        raise ValueError("DEC-301 requires exactly one preflight job")

    if MATRIX_TEMPLATE_JOB_NAME in seen:
        expanded_cells = {
            name
            for name in seen
            if name.startswith("exp062-cell-")
            and name != MATRIX_TEMPLATE_JOB_NAME
        }
        if expanded_cells:
            raise ValueError(
                "DEC-301 cannot mix matrix placeholder with expanded cells"
            )

    return {
        "materialized_job_count": len(raw),
        "materialized_downstream_job_count": len(downstream),
        "materialized_downstream_job_names": sorted(downstream),
        "github_unexpanded_matrix_placeholder_present": (
            MATRIX_TEMPLATE_JOB_NAME in seen
        ),
    }


def _validate_artifacts(
    artifacts_payload: Mapping[str, object],
    *,
    expected_head_sha: str,
) -> Mapping[str, object]:
    raw = artifacts_payload.get("artifacts")
    if not isinstance(raw, list):
        raise ValueError("DEC-301 artifact payload is malformed")
    if len(raw) != 1:
        raise ValueError(
            "DEC-301 proof requires exactly one preflight artifact"
        )

    item = raw[0]
    if not isinstance(item, Mapping):
        raise ValueError("DEC-301 proof artifact row is malformed")
    expected_name = expected_preflight_artifact_name(
        code_commit=expected_head_sha
    )
    if item.get("name") != expected_name:
        raise ValueError("DEC-301 preflight artifact name mismatch")
    if item.get("expired") is not False:
        raise ValueError("DEC-301 preflight artifact must be non-expired")
    _validate_sha256_digest(
        item.get("digest"),
        field="DEC-301 preflight artifact digest",
    )
    artifact_id = item.get("id")
    if (
        not isinstance(artifact_id, int)
        or isinstance(artifact_id, bool)
        or artifact_id <= 0
    ):
        raise ValueError("DEC-301 preflight artifact id is invalid")
    return item


def _validate_preflight(
    value: Mapping[str, object],
    *,
    expected_head_sha: str,
    repository_root: Path,
) -> None:
    if value.get("decision") != EXP062_DORMANT_WORKFLOW_SOURCE_DECISION:
        raise ValueError("DEC-301 preflight decision mismatch")
    if value.get("source_version") != EXP062_DORMANT_WORKFLOW_SOURCE_VERSION:
        raise ValueError("DEC-301 preflight source version mismatch")
    if value.get("experiment_id") != "EXP-20260927-062":
        raise ValueError("DEC-301 preflight experiment identity mismatch")
    if value.get("source_ready") is not True:
        raise ValueError("DEC-301 source preflight must be ready")
    if value.get("code_commit") != expected_head_sha:
        raise ValueError("DEC-301 preflight code commit mismatch")

    expected_source = workflow_source_payload(
        code_commit=expected_head_sha
    )
    if value.get("workflow_source") != expected_source:
        raise ValueError("DEC-301 workflow-source payload mismatch")

    expected_dependencies = validate_exp062_workflow_source_dependencies(
        repository_root=repository_root,
    )
    if value.get("source_dependencies") != expected_dependencies:
        raise ValueError("DEC-301 source-dependency payload mismatch")

    unsigned = dict(value)
    unsigned.pop("source_fingerprint", None)
    unsigned.pop("code_commit", None)
    unsigned.pop("workflow_source", None)
    unsigned.pop("source_dependencies", None)
    fingerprint = value.get("source_fingerprint")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise ValueError("DEC-301 source fingerprint is malformed")
    if _sha256(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-301 source fingerprint mismatch")

    if value.get("verified_pair_timeframe_source_count") != 9:
        raise ValueError("DEC-301 source-count mismatch")

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
            raise ValueError(f"DEC-301 preflight {field} must remain false")


def validate_gate_proof_terminal(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    preflight_evidence: Mapping[str, object],
    expected_head_sha: str,
    repository_root: Path = Path("."),
) -> dict[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    run_id = _validate_run(
        run,
        expected_head_sha=expected_head_sha,
    )
    job_report = _validate_jobs(jobs_payload)
    artifact = _validate_artifacts(
        artifacts_payload,
        expected_head_sha=expected_head_sha,
    )
    _validate_preflight(
        preflight_evidence,
        expected_head_sha=expected_head_sha,
        repository_root=repository_root,
    )

    return {
        "decision": EXP062_GATE_PROOF_CONTRACT_DECISION,
        "contract_version": EXP062_GATE_PROOF_CONTRACT_VERSION,
        "stage": "EXP062_GATE_PROOF_REVIEWED_FAIL_CLOSED",
        "proof_run_id": run_id,
        "proof_head_sha": expected_head_sha,
        "proof_run_number": EXPECTED_PROOF_RUN_NUMBER,
        "proof_run_attempt": WORKFLOW_RUN_ATTEMPT,
        "proof_run_conclusion": "failure",
        "preflight_artifact_id": artifact["id"],
        "preflight_artifact_digest": artifact["digest"],
        **job_report,
        "historical_result_slot_consumed": False,
        "historical_discovery_execution_occurred": False,
        "cell_result_artifact_count": 0,
        "aggregate_result_artifact_count": 0,
        "proof_dispatch_authorized": False,
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
    }


__all__ = [
    "EXPECTED_PROOF_RUN_NUMBER",
    "EXP062_GATE_PROOF_CONTRACT_DECISION",
    "EXP062_GATE_PROOF_CONTRACT_VERSION",
    "HISTORICAL_RESULT_DISPATCH_AUTHORIZED",
    "MATRIX_TEMPLATE_JOB_NAME",
    "PROOF_DISPATCH_AUTHORIZED",
    "proof_contract_payload",
    "validate_gate_proof_terminal",
]
