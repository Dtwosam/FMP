from __future__ import annotations

from typing import Mapping

from .exp062_adapter_probe import EXPECTED_CELLS


EXP062_ADAPTER_PROOF_REVIEW_DECISION = "DEC-295"
EXP062_ADAPTER_PROOF_REVIEW_VERSION = (
    "fmp-exp062-adapter-proof-review-contract-v1"
)

WORKFLOW_NAME = "phase8a-exp062-adapter-proof"
WORKFLOW_PATH = ".github/workflows/phase8a-exp062-adapter-proof.yml"

HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED = False
DISCOVERY_RESULT_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def expected_job_names() -> tuple[str, ...]:
    cells = tuple(
        f"exp062-adapter-probe-{symbol}-{timeframe}"
        for symbol, timeframe in EXPECTED_CELLS
    )
    return (*cells, "exp062-adapter-probe-aggregate")


def expected_artifact_names(*, head_sha: str) -> tuple[str, ...]:
    head_sha = _validate_commit(head_sha, field="head_sha")
    cells = tuple(
        f"exp062-dec294-adapter-probe-{symbol}-{timeframe}-{head_sha}"
        for symbol, timeframe in EXPECTED_CELLS
    )
    return (*cells, f"exp062-dec294-adapter-proof-{head_sha}")


def classify_exp062_adapter_proof_terminal(
    *,
    run: Mapping[str, object],
    jobs_payload: Mapping[str, object],
    artifacts_payload: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    expected_run = {
        "name": WORKFLOW_NAME,
        "path": WORKFLOW_PATH,
        "event": "push",
        "head_branch": "main",
        "head_sha": expected_head_sha,
        "run_attempt": 1,
        "status": "completed",
    }
    for field, expected in expected_run.items():
        if run.get(field) != expected:
            raise ValueError(f"DEC-295 proof run {field} mismatch")
    run_id = run.get("id")
    if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
        raise ValueError("DEC-295 proof run id is invalid")
    conclusion = run.get("conclusion")
    if not isinstance(conclusion, str) or not conclusion:
        raise ValueError("DEC-295 proof run conclusion is invalid")

    raw_jobs = jobs_payload.get("jobs")
    if not isinstance(raw_jobs, list):
        raise ValueError("DEC-295 jobs payload must contain jobs")
    jobs: list[Mapping[str, object]] = []
    job_names: list[str] = []
    for raw in raw_jobs:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-295 job row is malformed")
        name = raw.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError("DEC-295 job name is malformed")
        if raw.get("status") != "completed":
            raise ValueError("DEC-295 terminal proof has non-terminal job")
        job_conclusion = raw.get("conclusion")
        if not isinstance(job_conclusion, str) or not job_conclusion:
            raise ValueError("DEC-295 job conclusion is invalid")
        jobs.append(raw)
        job_names.append(name)
    if len(job_names) != len(set(job_names)):
        raise ValueError("DEC-295 duplicate job names")

    expected_jobs = set(expected_job_names())
    unexpected_jobs = set(job_names) - expected_jobs
    if unexpected_jobs:
        raise ValueError(
            f"DEC-295 unexpected jobs: {sorted(unexpected_jobs)!r}"
        )

    raw_artifacts = artifacts_payload.get("artifacts")
    if not isinstance(raw_artifacts, list):
        raise ValueError("DEC-295 artifacts payload must contain artifacts")
    expected_artifacts = set(
        expected_artifact_names(head_sha=expected_head_sha)
    )
    artifact_names: list[str] = []
    for raw in raw_artifacts:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-295 artifact row is malformed")
        artifact_id = raw.get("id")
        if (
            not isinstance(artifact_id, int)
            or isinstance(artifact_id, bool)
            or artifact_id <= 0
        ):
            raise ValueError("DEC-295 artifact id is invalid")
        name = raw.get("name")
        if not isinstance(name, str) or name not in expected_artifacts:
            raise ValueError("DEC-295 artifact name is unexpected")
        if raw.get("expired") is not False:
            raise ValueError("DEC-295 review requires non-expired artifacts")
        artifact_names.append(name)
    if len(artifact_names) != len(set(artifact_names)):
        raise ValueError("DEC-295 duplicate artifact names")

    success = conclusion == "success"
    if success:
        if set(job_names) != expected_jobs or len(job_names) != 10:
            raise ValueError(
                "DEC-295 successful proof requires exact ten-job inventory"
            )
        if any(job.get("conclusion") != "success" for job in jobs):
            raise ValueError(
                "DEC-295 successful proof requires every job to succeed"
            )
        if (
            set(artifact_names) != expected_artifacts
            or len(artifact_names) != 10
        ):
            raise ValueError(
                "DEC-295 successful proof requires exact ten-artifact inventory"
            )
        stage = "EXP062_ADAPTER_PROOF_SUCCESS_COMPLETE_REVIEW_REQUIRED"
    else:
        stage = "EXP062_ADAPTER_PROOF_NON_SUCCESS_REVIEW_REQUIRED"

    return {
        "decision": EXP062_ADAPTER_PROOF_REVIEW_DECISION,
        "version": EXP062_ADAPTER_PROOF_REVIEW_VERSION,
        "stage": stage,
        "proof_run_id": run_id,
        "proof_run_head_sha": expected_head_sha,
        "proof_run_conclusion": conclusion,
        "proof_run_attempt": 1,
        "proof_success_complete": success,
        "materialized_job_count": len(jobs),
        "artifact_count": len(artifact_names),
        "expected_success_job_count": 10,
        "expected_success_artifact_count": 10,
        "aggregate_content_review_required": success,
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
    }


__all__ = [
    "EXP062_ADAPTER_PROOF_REVIEW_DECISION",
    "EXP062_ADAPTER_PROOF_REVIEW_VERSION",
    "classify_exp062_adapter_proof_terminal",
    "expected_artifact_names",
    "expected_job_names",
]
