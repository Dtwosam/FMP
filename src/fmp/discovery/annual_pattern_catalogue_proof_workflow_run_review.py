from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_proof_workflow_dispatch_authorization import (
    ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_AUTHORIZATION_DECISION,
    ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_AUTHORIZATION_VERSION,
)
from .annual_pattern_catalogue_workflow_install_preflight_proof import (
    PROOF_WORKFLOW_NAME,
    PROOF_WORKFLOW_PATH,
    compile_repository_hosted_preflight_proof,
    validate_repository_hosted_preflight_proof,
)


ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_REVIEW_DECISION = "DEC-488"
ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_REVIEW_VERSION = (
    "fmp-annual-catalogue-proof-workflow-run-review-v1"
)

DISPATCH_AUTHORIZATION_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_proof_workflow_dispatch_authorization.py"
)
EXPECTED_DISPATCH_AUTHORIZATION_BLOB_SHA = (
    "5efc30607cf30426f099fd8b69bd8d4b8a2a0c9d"
)
PROOF_CONTRACT_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_workflow_install_preflight_proof.py"
)
EXPECTED_PROOF_CONTRACT_BLOB_SHA = (
    "fb9ea8d4a17734ee91225d48012a0a5b0088d415"
)
EXPECTED_ACTIVE_PROOF_WORKFLOW_BLOB_SHA = (
    "0d6c93e2af04501f9ac2589fd24d6672b2b41910"
)
EXPECTED_PROOF_RUN_NUMBER = 1
EXPECTED_PROOF_RUN_ATTEMPT = 1
PROOF_JOB_NAME = "annual-catalogue-install-preflight-proof"

REPOSITORY_MUTATION_AUTHORIZED = False
PROOF_WORKFLOW_DISPATCH_AUTHORIZED = False
ANNUAL_WORKFLOW_INSTALL_AUTHORIZED = False
ANNUAL_WORKFLOW_INSTALLED = False
ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED = False
HISTORICAL_ARTIFACT_READ_AUTHORIZED = False
HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED = False
HISTORICAL_RESULT_PRODUCTION_AUTHORIZED = False
NEXT_SEGMENT_EXECUTION_AUTHORIZED = False
CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED = False
STRATEGY_V1_SYNTHESIS_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _git_blob_sha(path: Path) -> str:
    payload = Path(path).read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return value


def _commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def validate_proof_workflow_run_review_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dispatch_authorization": (
            root / DISPATCH_AUTHORIZATION_SOURCE_PATH,
            EXPECTED_DISPATCH_AUTHORIZATION_BLOB_SHA,
        ),
        "proof_contract": (
            root / PROOF_CONTRACT_SOURCE_PATH,
            EXPECTED_PROOF_CONTRACT_BLOB_SHA,
        ),
        "active_proof_workflow": (
            root / PROOF_WORKFLOW_PATH,
            EXPECTED_ACTIVE_PROOF_WORKFLOW_BLOB_SHA,
        ),
    }
    out: dict[str, str] = {}
    for label, (path, expected_blob) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-488 source file missing: {path}")
        actual = _git_blob_sha(path)
        if actual != expected_blob:
            raise ValueError(
                f"DEC-488 {label} Git blob mismatch: {actual} != {expected_blob}"
            )
        out[label] = actual
    return out


def review_proof_workflow_run(
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    proof_run: Mapping[str, object],
    proof_job: Mapping[str, object],
    artifact: Mapping[str, object],
    preflight_bytes: bytes,
    expected_proof_run_id: int,
) -> dict[str, object]:
    sources = validate_proof_workflow_run_review_sources(
        repository_root=Path(repository_root),
    )
    if not isinstance(preflight_bytes, bytes) or not preflight_bytes:
        raise ValueError("DEC-488 preflight artifact bytes must be non-empty")
    try:
        preflight = json.loads(preflight_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("DEC-488 preflight artifact JSON is invalid") from exc
    if not isinstance(preflight, dict):
        raise ValueError("DEC-488 preflight artifact root must be an object")

    if main_branch.get("name") != "main":
        raise ValueError("DEC-488 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-488 main commit is malformed")
    main_head = _commit(commit.get("sha"), field="main_head_sha")

    expected_proof_run_id = _positive_int(
        expected_proof_run_id,
        field="expected_proof_run_id",
    )
    exact_run = {
        "id": expected_proof_run_id,
        "name": PROOF_WORKFLOW_NAME,
        "path": PROOF_WORKFLOW_PATH,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": main_head,
        "run_number": EXPECTED_PROOF_RUN_NUMBER,
        "run_attempt": EXPECTED_PROOF_RUN_ATTEMPT,
        "status": "completed",
        "conclusion": "success",
    }
    for field, expected in exact_run.items():
        if proof_run.get(field) != expected:
            raise ValueError(f"DEC-488 proof run {field} mismatch")

    proof_job_id = _positive_int(proof_job.get("id"), field="proof_job_id")
    exact_job = {
        "name": PROOF_JOB_NAME,
        "run_id": expected_proof_run_id,
        "status": "completed",
        "conclusion": "success",
    }
    for field, expected in exact_job.items():
        if proof_job.get(field) != expected:
            raise ValueError(f"DEC-488 proof job {field} mismatch")

    artifact_id = _positive_int(artifact.get("id"), field="artifact_id")
    expected_artifact_name = (
        "phase8a-annual-catalogue-workflow-install-preflight-" + main_head
    )
    if artifact.get("name") != expected_artifact_name:
        raise ValueError("DEC-488 proof artifact name mismatch")
    if artifact.get("expired") is not False:
        raise ValueError("DEC-488 proof artifact must be unexpired")

    repository_hosted_proof = compile_repository_hosted_preflight_proof(
        repository_root=Path(repository_root),
        preflight=preflight,
        main_branch=main_branch,
        proof_run=proof_run,
        expected_proof_run_id=expected_proof_run_id,
    )
    validate_repository_hosted_preflight_proof(repository_hosted_proof)

    raw_sha256 = _sha256_bytes(preflight_bytes)
    canonical_sha256 = _sha256_bytes(_canonical_json(preflight))
    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_REVIEW_DECISION,
        "version": ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_REVIEW_VERSION,
        "source_dispatch_authorization_decision": (
            ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_AUTHORIZATION_DECISION
        ),
        "source_dispatch_authorization_version": (
            ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_AUTHORIZATION_VERSION
        ),
        "dispatch_authorization_blob_sha": sources["dispatch_authorization"],
        "proof_contract_blob_sha": sources["proof_contract"],
        "active_proof_workflow_blob_sha": sources["active_proof_workflow"],
        "repository_full_name": "Dtwosam/FMP",
        "main_head_sha": main_head,
        "proof_run_id": expected_proof_run_id,
        "proof_run_number": EXPECTED_PROOF_RUN_NUMBER,
        "proof_run_attempt": EXPECTED_PROOF_RUN_ATTEMPT,
        "proof_run_status": "completed",
        "proof_run_conclusion": "success",
        "proof_job_id": proof_job_id,
        "proof_job_name": PROOF_JOB_NAME,
        "proof_job_status": "completed",
        "proof_job_conclusion": "success",
        "artifact_id": artifact_id,
        "artifact_name": expected_artifact_name,
        "artifact_expired": False,
        "preflight_raw_sha256": raw_sha256,
        "preflight_canonical_sha256": canonical_sha256,
        "repository_hosted_proof": repository_hosted_proof,
        "repository_hosted_proof_fingerprint": (
            repository_hosted_proof["proof_fingerprint"]
        ),
        "preflight_fingerprint": preflight["preflight_fingerprint"],
        "install_action_fingerprint": preflight["install_action_fingerprint"],
        "review_only": True,
        "proof_workflow_first_run_reviewed": True,
        "proof_workflow_dispatch_authorization_consumed": True,
        "repository_mutation_authorized": REPOSITORY_MUTATION_AUTHORIZED,
        "proof_workflow_dispatch_authorized": PROOF_WORKFLOW_DISPATCH_AUTHORIZED,
        "annual_workflow_install_authorized": ANNUAL_WORKFLOW_INSTALL_AUTHORIZED,
        "annual_workflow_installed": ANNUAL_WORKFLOW_INSTALLED,
        "annual_workflow_dispatch_authorized": ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED,
        "historical_artifact_read_authorized": HISTORICAL_ARTIFACT_READ_AUTHORIZED,
        "historical_catalogue_execution_authorized": (
            HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED
        ),
        "historical_result_production_authorized": (
            HISTORICAL_RESULT_PRODUCTION_AUTHORIZED
        ),
        "next_segment_execution_authorized": NEXT_SEGMENT_EXECUTION_AUTHORIZED,
        "cross_year_result_production_authorized": (
            CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED
        ),
        "strategy_v1_synthesis_authorized": STRATEGY_V1_SYNTHESIS_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
        "next_gate": (
            "CONCRETE_ANNUAL_PATTERN_CATALOGUE_PROOF_WORKFLOW_"
            "RUNTIME_EVIDENCE_FREEZE"
        ),
    }
    validate_proof_workflow_run_review(value)
    return value


def validate_proof_workflow_run_review(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    exact = {
        "decision": ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_REVIEW_DECISION,
        "version": ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_REVIEW_VERSION,
        "source_dispatch_authorization_decision": (
            ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_AUTHORIZATION_DECISION
        ),
        "source_dispatch_authorization_version": (
            ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_AUTHORIZATION_VERSION
        ),
        "dispatch_authorization_blob_sha": EXPECTED_DISPATCH_AUTHORIZATION_BLOB_SHA,
        "proof_contract_blob_sha": EXPECTED_PROOF_CONTRACT_BLOB_SHA,
        "active_proof_workflow_blob_sha": EXPECTED_ACTIVE_PROOF_WORKFLOW_BLOB_SHA,
        "repository_full_name": "Dtwosam/FMP",
        "proof_run_number": EXPECTED_PROOF_RUN_NUMBER,
        "proof_run_attempt": EXPECTED_PROOF_RUN_ATTEMPT,
        "proof_run_status": "completed",
        "proof_run_conclusion": "success",
        "proof_job_name": PROOF_JOB_NAME,
        "proof_job_status": "completed",
        "proof_job_conclusion": "success",
        "artifact_expired": False,
        "review_only": True,
        "proof_workflow_first_run_reviewed": True,
        "proof_workflow_dispatch_authorization_consumed": True,
        "repository_mutation_authorized": False,
        "proof_workflow_dispatch_authorized": False,
        "annual_workflow_install_authorized": False,
        "annual_workflow_installed": False,
        "annual_workflow_dispatch_authorized": False,
        "historical_artifact_read_authorized": False,
        "historical_catalogue_execution_authorized": False,
        "historical_result_production_authorized": False,
        "next_segment_execution_authorized": False,
        "cross_year_result_production_authorized": False,
        "strategy_v1_synthesis_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "next_gate": (
            "CONCRETE_ANNUAL_PATTERN_CATALOGUE_PROOF_WORKFLOW_"
            "RUNTIME_EVIDENCE_FREEZE"
        ),
    }
    expected_keys = set(exact) | {
        "main_head_sha",
        "proof_run_id",
        "proof_job_id",
        "artifact_id",
        "artifact_name",
        "preflight_raw_sha256",
        "preflight_canonical_sha256",
        "repository_hosted_proof",
        "repository_hosted_proof_fingerprint",
        "preflight_fingerprint",
        "install_action_fingerprint",
    }
    if set(value) != expected_keys:
        raise ValueError("DEC-488 run review key set mismatch")
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-488 {field} mismatch")

    main_head = _commit(value.get("main_head_sha"), field="main_head_sha")
    _positive_int(value.get("proof_run_id"), field="proof_run_id")
    _positive_int(value.get("proof_job_id"), field="proof_job_id")
    _positive_int(value.get("artifact_id"), field="artifact_id")
    if value.get("artifact_name") != (
        "phase8a-annual-catalogue-workflow-install-preflight-" + main_head
    ):
        raise ValueError("DEC-488 artifact name/main mismatch")

    for field in (
        "preflight_raw_sha256",
        "preflight_canonical_sha256",
        "repository_hosted_proof_fingerprint",
        "preflight_fingerprint",
        "install_action_fingerprint",
    ):
        raw = value.get(field)
        if not isinstance(raw, str) or len(raw) != 64:
            raise ValueError(f"DEC-488 {field} malformed")
        try:
            int(raw, 16)
        except ValueError as exc:
            raise ValueError(f"DEC-488 {field} must be hexadecimal") from exc

    proof = value.get("repository_hosted_proof")
    if not isinstance(proof, Mapping):
        raise ValueError("DEC-488 repository hosted proof malformed")
    validate_repository_hosted_preflight_proof(proof)
    if proof.get("main_head_sha") != main_head:
        raise ValueError("DEC-488 proof/main head mismatch")
    if proof.get("proof_run_id") != value.get("proof_run_id"):
        raise ValueError("DEC-488 proof run id mismatch")
    if proof.get("proof_fingerprint") != value.get(
        "repository_hosted_proof_fingerprint"
    ):
        raise ValueError("DEC-488 repository hosted proof fingerprint mismatch")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_REVIEW_DECISION",
    "ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_REVIEW_VERSION",
    "EXPECTED_ACTIVE_PROOF_WORKFLOW_BLOB_SHA",
    "EXPECTED_DISPATCH_AUTHORIZATION_BLOB_SHA",
    "EXPECTED_PROOF_CONTRACT_BLOB_SHA",
    "EXPECTED_PROOF_RUN_ATTEMPT",
    "EXPECTED_PROOF_RUN_NUMBER",
    "PROOF_JOB_NAME",
    "review_proof_workflow_run",
    "validate_proof_workflow_run_review",
    "validate_proof_workflow_run_review_sources",
]
