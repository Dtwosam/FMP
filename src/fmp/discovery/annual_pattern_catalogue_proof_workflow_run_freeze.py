from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_proof_workflow_run_review import (
    ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_REVIEW_DECISION,
    ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_REVIEW_VERSION,
    validate_proof_workflow_run_review,
)


ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_FREEZE_DECISION = "DEC-489"
ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_FREEZE_VERSION = (
    "fmp-annual-catalogue-proof-workflow-run-freeze-v1"
)

RUN_REVIEW_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_proof_workflow_run_review.py"
)
EXPECTED_RUN_REVIEW_BLOB_SHA = "ec92323d910785d342028c5896528fa1dcf1cc96"

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


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return value


def _sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-character SHA-256")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def validate_proof_workflow_run_freeze_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    path = Path(repository_root) / RUN_REVIEW_SOURCE_PATH
    if not path.is_file():
        raise ValueError("DEC-489 DEC-488 run-review source missing")
    actual = _git_blob_sha(path)
    if actual != EXPECTED_RUN_REVIEW_BLOB_SHA:
        raise ValueError("DEC-489 DEC-488 run-review blob mismatch")
    return {"run_review_blob_sha": actual}


def freeze_reviewed_proof_workflow_run(
    reviewed_result: Mapping[str, object],
    *,
    repository_root: Path,
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_proof_workflow_run_freeze_sources(
        repository_root=Path(repository_root),
    )
    validate_proof_workflow_run_review(reviewed_result)
    expected_head_sha = _commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if reviewed_result.get("main_head_sha") != expected_head_sha:
        raise ValueError("DEC-489 reviewed main head mismatch")

    frozen: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_FREEZE_DECISION,
        "version": ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_FREEZE_VERSION,
        "stage": (
            "ANNUAL_CATALOGUE_PROOF_WORKFLOW_"
            "FIRST_RUN_REVIEWED_AND_DETERMINISTICALLY_FROZEN"
        ),
        "source_review_decision": ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_REVIEW_DECISION,
        "source_review_version": ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_REVIEW_VERSION,
        **source,
        "main_head_sha": expected_head_sha,
        "proof_run_id": reviewed_result["proof_run_id"],
        "proof_run_number": reviewed_result["proof_run_number"],
        "proof_run_attempt": reviewed_result["proof_run_attempt"],
        "proof_run_conclusion": reviewed_result["proof_run_conclusion"],
        "proof_job_id": reviewed_result["proof_job_id"],
        "proof_job_name": reviewed_result["proof_job_name"],
        "proof_job_conclusion": reviewed_result["proof_job_conclusion"],
        "artifact_id": reviewed_result["artifact_id"],
        "artifact_name": reviewed_result["artifact_name"],
        "preflight_raw_sha256": reviewed_result["preflight_raw_sha256"],
        "preflight_canonical_sha256": reviewed_result[
            "preflight_canonical_sha256"
        ],
        "repository_hosted_proof_fingerprint": reviewed_result[
            "repository_hosted_proof_fingerprint"
        ],
        "preflight_fingerprint": reviewed_result["preflight_fingerprint"],
        "install_action_fingerprint": reviewed_result[
            "install_action_fingerprint"
        ],
        "proof_workflow_dispatch_authorization_consumed": True,
        "runtime_review_validated": True,
        "runtime_evidence_frozen": True,
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
            "RUNTIME_EVIDENCE_BINDING"
        ),
    }
    frozen["freeze_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(frozen)
    ).hexdigest()
    validate_proof_workflow_run_freeze(frozen)
    return frozen


def validate_proof_workflow_run_freeze(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = value.get("freeze_fingerprint_sha256")
    _sha256(fingerprint, field="freeze_fingerprint_sha256")
    unsigned = dict(value)
    unsigned.pop("freeze_fingerprint_sha256", None)
    if hashlib.sha256(_canonical_json(unsigned)).hexdigest() != fingerprint:
        raise ValueError("DEC-489 freeze fingerprint mismatch")

    exact = {
        "decision": ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_FREEZE_DECISION,
        "version": ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_FREEZE_VERSION,
        "stage": (
            "ANNUAL_CATALOGUE_PROOF_WORKFLOW_"
            "FIRST_RUN_REVIEWED_AND_DETERMINISTICALLY_FROZEN"
        ),
        "source_review_decision": ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_REVIEW_DECISION,
        "source_review_version": ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_REVIEW_VERSION,
        "run_review_blob_sha": EXPECTED_RUN_REVIEW_BLOB_SHA,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "proof_job_name": "annual-catalogue-install-preflight-proof",
        "proof_job_conclusion": "success",
        "proof_workflow_dispatch_authorization_consumed": True,
        "runtime_review_validated": True,
        "runtime_evidence_frozen": True,
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
            "RUNTIME_EVIDENCE_BINDING"
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
        "repository_hosted_proof_fingerprint",
        "preflight_fingerprint",
        "install_action_fingerprint",
        "freeze_fingerprint_sha256",
    }
    if set(value) != expected_keys:
        raise ValueError("DEC-489 freeze key set mismatch")
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-489 {field} mismatch")

    head = _commit(value.get("main_head_sha"), field="main_head_sha")
    _positive_int(value.get("proof_run_id"), field="proof_run_id")
    _positive_int(value.get("proof_job_id"), field="proof_job_id")
    _positive_int(value.get("artifact_id"), field="artifact_id")
    if value.get("artifact_name") != (
        "phase8a-annual-catalogue-workflow-install-preflight-" + head
    ):
        raise ValueError("DEC-489 artifact name/main mismatch")
    for field in (
        "preflight_raw_sha256",
        "preflight_canonical_sha256",
        "repository_hosted_proof_fingerprint",
        "preflight_fingerprint",
        "install_action_fingerprint",
    ):
        _sha256(value.get(field), field=field)
    return value


__all__ = [
    "ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_FREEZE_DECISION",
    "ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_FREEZE_VERSION",
    "EXPECTED_RUN_REVIEW_BLOB_SHA",
    "freeze_reviewed_proof_workflow_run",
    "validate_proof_workflow_run_freeze",
    "validate_proof_workflow_run_freeze_sources",
]
