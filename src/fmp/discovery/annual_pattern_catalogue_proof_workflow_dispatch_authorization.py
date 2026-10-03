from __future__ import annotations

import hashlib
from pathlib import Path

from .annual_pattern_catalogue_proof_workflow_dispatch_preflight import (
    ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_PREFLIGHT_DECISION,
    ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_PREFLIGHT_VERSION,
    EXPECTED_ACTIVE_PROOF_WORKFLOW_BLOB_SHA,
)
from .annual_pattern_catalogue_workflow_install_preflight_proof_workflow_source import (
    RESERVED_PROOF_WORKFLOW_PATH,
)


ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_AUTHORIZATION_DECISION = "DEC-487"
ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_AUTHORIZATION_VERSION = (
    "fmp-annual-catalogue-proof-workflow-dispatch-authorization-v1"
)
DISPATCH_PREFLIGHT_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_proof_workflow_dispatch_preflight.py"
)
EXPECTED_DISPATCH_PREFLIGHT_BLOB_SHA = (
    "9f5d4b2abbfdb02280b0011a5d61e189be1d6fed"
)

EXPLICIT_PROOF_WORKFLOW_DISPATCH_AUTHORIZED = True
EXPECTED_PROOF_WORKFLOW_RUN_NUMBER = 1
EXPECTED_PROOF_WORKFLOW_RUN_ATTEMPT = 1

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


def _git_blob_sha(path: Path) -> str:
    payload = Path(path).read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def validate_proof_workflow_dispatch_authorization_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    preflight_path = root / DISPATCH_PREFLIGHT_SOURCE_PATH
    active_path = root / RESERVED_PROOF_WORKFLOW_PATH

    if not preflight_path.is_file():
        raise ValueError("DEC-487 DEC-486 dispatch preflight source missing")
    preflight_blob = _git_blob_sha(preflight_path)
    if preflight_blob != EXPECTED_DISPATCH_PREFLIGHT_BLOB_SHA:
        raise ValueError("DEC-487 DEC-486 dispatch preflight blob mismatch")

    if not active_path.is_file():
        raise ValueError("DEC-487 requires installed proof workflow")
    active_blob = _git_blob_sha(active_path)
    if active_blob != EXPECTED_ACTIVE_PROOF_WORKFLOW_BLOB_SHA:
        raise ValueError("DEC-487 active proof workflow blob mismatch")

    text = active_path.read_text(encoding="utf-8")
    if "  workflow_dispatch:" not in text:
        raise ValueError("DEC-487 proof workflow must remain manual-dispatch only")
    if "  push:" in text or "  pull_request:" in text:
        raise ValueError("DEC-487 proof workflow gained automatic trigger")
    if "  actions: write" in text or "gh workflow run " in text:
        raise ValueError("DEC-487 proof workflow gained nested dispatch authority")

    return {
        "dispatch_preflight_blob_sha": preflight_blob,
        "active_proof_workflow_blob_sha": active_blob,
    }


def build_proof_workflow_dispatch_authorization(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_proof_workflow_dispatch_authorization_sources(
        repository_root=Path(repository_root),
    )
    return {
        "decision": ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_AUTHORIZATION_DECISION,
        "version": ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_AUTHORIZATION_VERSION,
        "stage": (
            "ANNUAL_CATALOGUE_PROOF_WORKFLOW_"
            "FIRST_DISPATCH_AUTHORIZED_RUN_NOT_STARTED"
        ),
        "authorization_basis": "explicit_operator_authorization",
        "authorization_scope": "single_first_proof_workflow_run_only",
        "source_dispatch_preflight_decision": (
            ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_PREFLIGHT_DECISION
        ),
        "source_dispatch_preflight_version": (
            ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_PREFLIGHT_VERSION
        ),
        **source,
        "active_proof_workflow_path": RESERVED_PROOF_WORKFLOW_PATH,
        "proof_workflow_installed": True,
        "proof_workflow_available": True,
        "proof_workflow_run_count_before_authorized_action": 0,
        "expected_proof_workflow_run_number": EXPECTED_PROOF_WORKFLOW_RUN_NUMBER,
        "expected_proof_workflow_run_attempt": EXPECTED_PROOF_WORKFLOW_RUN_ATTEMPT,
        "explicit_proof_workflow_dispatch_authorized": (
            EXPLICIT_PROOF_WORKFLOW_DISPATCH_AUTHORIZED
        ),
        "proof_workflow_dispatch_authorized": True,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "repository_mutation_authorized": REPOSITORY_MUTATION_AUTHORIZED,
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
            "EXACT_FIRST_ANNUAL_PATTERN_CATALOGUE_PROOF_WORKFLOW_"
            "DISPATCH_ON_CURRENT_MAIN"
        ),
    }


__all__ = [
    "ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_AUTHORIZATION_DECISION",
    "ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_AUTHORIZATION_VERSION",
    "EXPECTED_DISPATCH_PREFLIGHT_BLOB_SHA",
    "EXPECTED_PROOF_WORKFLOW_RUN_ATTEMPT",
    "EXPECTED_PROOF_WORKFLOW_RUN_NUMBER",
    "EXPLICIT_PROOF_WORKFLOW_DISPATCH_AUTHORIZED",
    "build_proof_workflow_dispatch_authorization",
    "validate_proof_workflow_dispatch_authorization_sources",
]
