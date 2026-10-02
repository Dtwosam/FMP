from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_workflow_install_preflight import (
    ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_DECISION,
    ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_VERSION,
    validate_workflow_install_preflight,
)


ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_PROOF_DECISION = "DEC-481"
ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_PROOF_VERSION = (
    "fmp-annual-pattern-catalogue-workflow-install-preflight-proof-v1"
)
SOURCE_PREFLIGHT_DECISION = ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_DECISION
SOURCE_PREFLIGHT_HEAD_SHA = "3b9d3230a0ad5fc0a58803ef555c4694963a309d"
EXPECTED_PREFLIGHT_SOURCE_BLOB_SHA = "654a51a7bd647afe4664d9ecab81926044c2b824"
PREFLIGHT_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_workflow_install_preflight.py"
)

PROOF_WORKFLOW_NAME = (
    "phase8a-annual-catalogue-workflow-install-preflight-proof"
)
PROOF_WORKFLOW_PATH = (
    ".github/workflows/"
    "phase8a-annual-catalogue-workflow-install-preflight-proof.yml"
)

REPOSITORY_MUTATION_AUTHORIZED = False
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


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _git_blob_sha(path: Path) -> str:
    payload = Path(path).read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _validate_positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return value


def validate_proof_sources(*, repository_root: Path) -> dict[str, str]:
    path = Path(repository_root) / PREFLIGHT_SOURCE_PATH
    if not path.is_file():
        raise ValueError("DEC-481 preflight source is missing")
    actual = _git_blob_sha(path)
    if actual != EXPECTED_PREFLIGHT_SOURCE_BLOB_SHA:
        raise ValueError(
            "DEC-481 preflight source Git blob mismatch: "
            f"{actual} != {EXPECTED_PREFLIGHT_SOURCE_BLOB_SHA}"
        )
    return {"preflight_source_blob_sha": actual}


def compile_repository_hosted_preflight_proof(
    *,
    repository_root: Path,
    preflight: Mapping[str, object],
    main_branch: Mapping[str, object],
    proof_run: Mapping[str, object],
    expected_proof_run_id: int,
) -> dict[str, object]:
    validate_proof_sources(repository_root=Path(repository_root))
    validate_workflow_install_preflight(preflight)

    if main_branch.get("name") != "main":
        raise ValueError("DEC-481 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-481 main commit is malformed")
    main_head = _validate_commit(commit.get("sha"), field="main_head_sha")
    preflight_head = _validate_commit(
        preflight.get("expected_head_sha"),
        field="preflight expected_head_sha",
    )
    if main_head != preflight_head:
        raise ValueError("DEC-481 preflight/main head mismatch")

    expected_proof_run_id = _validate_positive_int(
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
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }
    for field, expected in exact_run.items():
        if proof_run.get(field) != expected:
            raise ValueError(f"DEC-481 proof run {field} mismatch")

    preflight_fingerprint = preflight.get("preflight_fingerprint")
    if not isinstance(preflight_fingerprint, str) or len(preflight_fingerprint) != 64:
        raise ValueError("DEC-481 preflight fingerprint malformed")
    install_action_fingerprint = preflight.get("install_action_fingerprint")
    if (
        not isinstance(install_action_fingerprint, str)
        or len(install_action_fingerprint) != 64
    ):
        raise ValueError("DEC-481 install-action fingerprint malformed")

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_PROOF_DECISION,
        "version": ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_PROOF_VERSION,
        "source_preflight_decision": SOURCE_PREFLIGHT_DECISION,
        "source_preflight_version": ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_VERSION,
        "source_preflight_head_sha": SOURCE_PREFLIGHT_HEAD_SHA,
        "preflight_source_blob_sha": EXPECTED_PREFLIGHT_SOURCE_BLOB_SHA,
        "repository_full_name": "Dtwosam/FMP",
        "main_head_sha": main_head,
        "proof_run_id": expected_proof_run_id,
        "proof_workflow_name": PROOF_WORKFLOW_NAME,
        "proof_workflow_path": PROOF_WORKFLOW_PATH,
        "proof_run_event": "workflow_dispatch",
        "proof_run_head_branch": "main",
        "proof_run_head_sha": main_head,
        "proof_run_attempt": 1,
        "proof_run_status": "completed",
        "proof_run_conclusion": "success",
        "preflight_fingerprint": preflight_fingerprint,
        "install_action_fingerprint": install_action_fingerprint,
        "repository_hosted_read_only_proof": True,
        "preflight_validated": True,
        "repository_mutation_authorized": REPOSITORY_MUTATION_AUTHORIZED,
        "annual_workflow_install_authorized": ANNUAL_WORKFLOW_INSTALL_AUTHORIZED,
        "annual_workflow_installed": ANNUAL_WORKFLOW_INSTALLED,
        "annual_workflow_dispatch_authorized": ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED,
        "historical_artifact_read_authorized": HISTORICAL_ARTIFACT_READ_AUTHORIZED,
        "historical_catalogue_execution_authorized": HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED,
        "historical_result_production_authorized": HISTORICAL_RESULT_PRODUCTION_AUTHORIZED,
        "next_segment_execution_authorized": NEXT_SEGMENT_EXECUTION_AUTHORIZED,
        "cross_year_result_production_authorized": CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED,
        "strategy_v1_synthesis_authorized": STRATEGY_V1_SYNTHESIS_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
        "next_gate": (
            "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_"
            "WORKFLOW_INSTALL_PREFLIGHT_PROOF_WORKFLOW_SOURCE"
        ),
    }
    value["proof_fingerprint"] = _sha256_bytes(_canonical_json(value))
    validate_repository_hosted_preflight_proof(value)
    return value


def validate_repository_hosted_preflight_proof(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = value.get("proof_fingerprint")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise ValueError("DEC-481 proof fingerprint malformed")
    unsigned = dict(value)
    unsigned.pop("proof_fingerprint", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-481 proof fingerprint mismatch")

    exact = {
        "decision": ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_PROOF_DECISION,
        "version": ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_PROOF_VERSION,
        "source_preflight_decision": SOURCE_PREFLIGHT_DECISION,
        "source_preflight_version": ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_VERSION,
        "source_preflight_head_sha": SOURCE_PREFLIGHT_HEAD_SHA,
        "preflight_source_blob_sha": EXPECTED_PREFLIGHT_SOURCE_BLOB_SHA,
        "repository_full_name": "Dtwosam/FMP",
        "proof_workflow_name": PROOF_WORKFLOW_NAME,
        "proof_workflow_path": PROOF_WORKFLOW_PATH,
        "proof_run_event": "workflow_dispatch",
        "proof_run_head_branch": "main",
        "proof_run_attempt": 1,
        "proof_run_status": "completed",
        "proof_run_conclusion": "success",
        "repository_hosted_read_only_proof": True,
        "preflight_validated": True,
        "repository_mutation_authorized": False,
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
            "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_"
            "WORKFLOW_INSTALL_PREFLIGHT_PROOF_WORKFLOW_SOURCE"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-481 {field} mismatch")

    main_head = _validate_commit(value.get("main_head_sha"), field="main_head_sha")
    proof_run_head = _validate_commit(
        value.get("proof_run_head_sha"),
        field="proof_run_head_sha",
    )
    if proof_run_head != main_head:
        raise ValueError("DEC-481 proof run head/main mismatch")
    _validate_positive_int(value.get("proof_run_id"), field="proof_run_id")
    for field in ("preflight_fingerprint", "install_action_fingerprint"):
        raw = value.get(field)
        if not isinstance(raw, str) or len(raw) != 64:
            raise ValueError(f"DEC-481 {field} malformed")
        try:
            int(raw, 16)
        except ValueError as exc:
            raise ValueError(f"DEC-481 {field} must be hexadecimal") from exc
    return value


__all__ = [
    "ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_PROOF_DECISION",
    "ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_PROOF_VERSION",
    "EXPECTED_PREFLIGHT_SOURCE_BLOB_SHA",
    "PREFLIGHT_SOURCE_PATH",
    "PROOF_WORKFLOW_NAME",
    "PROOF_WORKFLOW_PATH",
    "SOURCE_PREFLIGHT_DECISION",
    "SOURCE_PREFLIGHT_HEAD_SHA",
    "compile_repository_hosted_preflight_proof",
    "validate_proof_sources",
    "validate_repository_hosted_preflight_proof",
]
