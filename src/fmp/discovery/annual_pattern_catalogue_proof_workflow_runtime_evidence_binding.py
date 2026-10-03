from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .annual_pattern_catalogue_proof_workflow_run_freeze import (
    ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_FREEZE_DECISION,
    ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_FREEZE_VERSION,
)


ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUNTIME_EVIDENCE_BINDING_DECISION = "DEC-490"
ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUNTIME_EVIDENCE_BINDING_VERSION = (
    "fmp-annual-catalogue-proof-workflow-runtime-evidence-binding-v1"
)

SOURCE_FREEZE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_proof_workflow_run_freeze.py"
)
SOURCE_REVIEW_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_proof_workflow_run_review.py"
)
SOURCE_PROOF_CONTRACT_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_workflow_install_preflight_proof.py"
)
ACTIVE_PROOF_WORKFLOW_PATH = (
    ".github/workflows/phase8a-annual-catalogue-workflow-install-preflight-proof.yml"
)

EXPECTED_SOURCE_FREEZE_BLOB_SHA = "f323deaca43fe50b21150d4dda79081227adb072"
EXPECTED_SOURCE_REVIEW_BLOB_SHA = "ec92323d910785d342028c5896528fa1dcf1cc96"
EXPECTED_SOURCE_PROOF_CONTRACT_BLOB_SHA = (
    "fb9ea8d4a17734ee91225d48012a0a5b0088d415"
)
EXPECTED_ACTIVE_PROOF_WORKFLOW_BLOB_SHA = (
    "0d6c93e2af04501f9ac2589fd24d6672b2b41910"
)

MAIN_HEAD_SHA = "6ee059cb451e7c6d2235b7744542dc194acc014e"
PROOF_RUN_ID = 37120635769
PROOF_JOB_ID = 111195887975
ARTIFACT_ID = 11273008137
ARTIFACT_NAME = (
    "phase8a-annual-catalogue-workflow-install-preflight-" + MAIN_HEAD_SHA
)
ARTIFACT_SIZE_IN_BYTES = 1370
ARTIFACT_DIGEST = (
    "sha256:3b242f14e89950eb828c614bf1b021dd51d9fc43b9045c2efccc6a1f7bcd8e32"
)
ARTIFACT_ZIP_SHA256 = (
    "3b242f14e89950eb828c614bf1b021dd51d9fc43b9045c2efccc6a1f7bcd8e32"
)
PREFLIGHT_RAW_SHA256 = (
    "70f6aaaca16fbb5de9e481e135cd8ec85d6dc7c6df524fcf328e23fd0d8de3d3"
)
PREFLIGHT_CANONICAL_SHA256 = (
    "f151fcbd487b40be35b54356f7b3002ba416812ec4ece2ea4bd7868cf5c0a163"
)
PREFLIGHT_FINGERPRINT = (
    "1313137f738a485586301dde66ceed0f6686cb97287ddbb850ffc6c6467b7c7f"
)
INSTALL_ACTION_FINGERPRINT = (
    "2a972b04b824cfcd701bb337204770e45c0ed2ad5ab8a85ffdff333eba924fbd"
)
REPOSITORY_HOSTED_PROOF_FINGERPRINT = (
    "4ad886232c6af5566c8ac5581c153274b8328c7cd41d508ba93dcf343fdf8578"
)
RUNTIME_FREEZE_FINGERPRINT_SHA256 = (
    "99397d1593f724bcc6024c5d0a2f4abf2b230273bf7ffb0edcc0b88562cd58fb"
)
EXPECTED_BINDING_FINGERPRINT_SHA256 = (
    "e45d7f3d88ea93e989da32d6f98c22837dfbe5937e7c1fa37260aadd88b256e3"
)


def _git_blob_sha(path: Path) -> str:
    payload = Path(path).read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def validate_runtime_evidence_binding_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "source_freeze_blob_sha": (
            root / SOURCE_FREEZE_PATH,
            EXPECTED_SOURCE_FREEZE_BLOB_SHA,
        ),
        "source_review_blob_sha": (
            root / SOURCE_REVIEW_PATH,
            EXPECTED_SOURCE_REVIEW_BLOB_SHA,
        ),
        "source_proof_contract_blob_sha": (
            root / SOURCE_PROOF_CONTRACT_PATH,
            EXPECTED_SOURCE_PROOF_CONTRACT_BLOB_SHA,
        ),
        "active_proof_workflow_blob_sha": (
            root / ACTIVE_PROOF_WORKFLOW_PATH,
            EXPECTED_ACTIVE_PROOF_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-490 source file missing: {path}")
        value = _git_blob_sha(path)
        if value != expected_sha:
            raise ValueError(f"DEC-490 {field} mismatch")
        actual[field] = value
    return actual


def build_runtime_evidence_binding(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_runtime_evidence_binding_sources(
        repository_root=Path(repository_root),
    )
    if ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_FREEZE_DECISION != "DEC-489":
        raise ValueError("DEC-490 source freeze decision drift")
    if (
        ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUN_FREEZE_VERSION
        != "fmp-annual-catalogue-proof-workflow-run-freeze-v1"
    ):
        raise ValueError("DEC-490 source freeze version drift")

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUNTIME_EVIDENCE_BINDING_DECISION,
        "version": ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUNTIME_EVIDENCE_BINDING_VERSION,
        "stage": (
            "ANNUAL_CATALOGUE_PROOF_WORKFLOW_"
            "FIRST_RUN_CONCRETE_RUNTIME_EVIDENCE_BOUND"
        ),
        "source_freeze_decision": "DEC-489",
        "source_freeze_version": (
            "fmp-annual-catalogue-proof-workflow-run-freeze-v1"
        ),
        **source,
        "repository_full_name": "Dtwosam/FMP",
        "main_head_sha": MAIN_HEAD_SHA,
        "proof_run_id": PROOF_RUN_ID,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_event": "workflow_dispatch",
        "proof_run_head_branch": "main",
        "proof_run_head_sha": MAIN_HEAD_SHA,
        "proof_run_status": "completed",
        "proof_run_conclusion": "success",
        "proof_job_id": PROOF_JOB_ID,
        "proof_job_name": "annual-catalogue-install-preflight-proof",
        "proof_job_status": "completed",
        "proof_job_conclusion": "success",
        "artifact_id": ARTIFACT_ID,
        "artifact_name": ARTIFACT_NAME,
        "artifact_size_in_bytes": ARTIFACT_SIZE_IN_BYTES,
        "artifact_expired": False,
        "artifact_digest": ARTIFACT_DIGEST,
        "artifact_zip_sha256": ARTIFACT_ZIP_SHA256,
        "preflight_raw_sha256": PREFLIGHT_RAW_SHA256,
        "preflight_canonical_sha256": PREFLIGHT_CANONICAL_SHA256,
        "preflight_fingerprint": PREFLIGHT_FINGERPRINT,
        "install_action_fingerprint": INSTALL_ACTION_FINGERPRINT,
        "repository_hosted_proof_fingerprint": (
            REPOSITORY_HOSTED_PROOF_FINGERPRINT
        ),
        "runtime_freeze_fingerprint_sha256": (
            RUNTIME_FREEZE_FINGERPRINT_SHA256
        ),
        "proof_workflow_dispatch_authorization_consumed": True,
        "runtime_review_validated": True,
        "runtime_evidence_frozen": True,
        "runtime_evidence_bound": True,
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
            "EXPLICIT_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_"
            "INSTALL_AUTHORIZATION_BEFORE_MUTATION"
        ),
    }
    value["binding_fingerprint_sha256"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    validate_runtime_evidence_binding(value)
    return value


def validate_runtime_evidence_binding(
    value: dict[str, object],
) -> dict[str, object]:
    fingerprint = value.get("binding_fingerprint_sha256")
    if fingerprint != EXPECTED_BINDING_FINGERPRINT_SHA256:
        raise ValueError("DEC-490 binding fingerprint mismatch")

    unsigned = dict(value)
    unsigned.pop("binding_fingerprint_sha256", None)
    if hashlib.sha256(_canonical_json(unsigned)).hexdigest() != fingerprint:
        raise ValueError("DEC-490 binding fingerprint is not canonical")

    exact = build_runtime_evidence_binding.__annotations__
    del exact
    for field in (
        "repository_mutation_authorized",
        "proof_workflow_dispatch_authorized",
        "annual_workflow_install_authorized",
        "annual_workflow_installed",
        "annual_workflow_dispatch_authorized",
        "historical_artifact_read_authorized",
        "historical_catalogue_execution_authorized",
        "historical_result_production_authorized",
        "next_segment_execution_authorized",
        "cross_year_result_production_authorized",
        "strategy_v1_synthesis_authorized",
        "promotion_authorized",
        "phase8b_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "trading_authorized",
    ):
        if value.get(field) is not False:
            raise ValueError(f"DEC-490 {field} must remain false")
    if value.get("proof_workflow_dispatch_authorization_consumed") is not True:
        raise ValueError("DEC-490 proof dispatch authorization must be consumed")
    if value.get("runtime_review_validated") is not True:
        raise ValueError("DEC-490 runtime review must be validated")
    if value.get("runtime_evidence_frozen") is not True:
        raise ValueError("DEC-490 runtime evidence must be frozen")
    if value.get("runtime_evidence_bound") is not True:
        raise ValueError("DEC-490 runtime evidence must be bound")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUNTIME_EVIDENCE_BINDING_DECISION",
    "ANNUAL_CATALOGUE_PROOF_WORKFLOW_RUNTIME_EVIDENCE_BINDING_VERSION",
    "EXPECTED_BINDING_FINGERPRINT_SHA256",
    "build_runtime_evidence_binding",
    "validate_runtime_evidence_binding",
    "validate_runtime_evidence_binding_sources",
]
