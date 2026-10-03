from __future__ import annotations

import hashlib
from pathlib import Path

from .annual_pattern_catalogue_workflow_install_preflight_proof_workflow_source import (
    DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH,
    EXPECTED_DORMANT_PROOF_WORKFLOW_TEMPLATE_BLOB_SHA,
    RESERVED_PROOF_WORKFLOW_PATH,
    validate_dormant_proof_workflow_template,
)


ANNUAL_CATALOGUE_PROOF_WORKFLOW_INSTALL_RECEIPT_DECISION = "DEC-485"
ANNUAL_CATALOGUE_PROOF_WORKFLOW_INSTALL_RECEIPT_VERSION = (
    "fmp-annual-catalogue-proof-workflow-install-receipt-v1"
)
AUTHORIZATION_PREFLIGHT_DECISION = "DEC-484"
AUTHORIZATION_PREFLIGHT_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_workflow_install_preflight_proof_workflow_install_preflight.py"
)
EXPECTED_AUTHORIZATION_PREFLIGHT_SOURCE_BLOB_SHA = (
    "ab434212007f3777fa4436a51268438ea44be6dd"
)
EXPECTED_PROOF_WORKFLOW_BLOB_SHA = (
    EXPECTED_DORMANT_PROOF_WORKFLOW_TEMPLATE_BLOB_SHA
)

PROOF_WORKFLOW_INSTALL_AUTHORIZED = True
PROOF_WORKFLOW_INSTALL_AUTHORIZATION_CONSUMED = True
PROOF_WORKFLOW_INSTALLED = True
PROOF_WORKFLOW_AVAILABLE = True
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


def validate_proof_workflow_install_receipt_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    preflight_path = root / AUTHORIZATION_PREFLIGHT_SOURCE_PATH
    dormant_path = root / DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH
    active_path = root / RESERVED_PROOF_WORKFLOW_PATH

    if not preflight_path.is_file():
        raise ValueError("DEC-485 DEC-484 authorization preflight source missing")
    preflight_blob = _git_blob_sha(preflight_path)
    if preflight_blob != EXPECTED_AUTHORIZATION_PREFLIGHT_SOURCE_BLOB_SHA:
        raise ValueError("DEC-485 DEC-484 authorization preflight blob mismatch")

    if not dormant_path.is_file():
        raise ValueError("DEC-485 dormant proof workflow template missing")
    dormant_blob = _git_blob_sha(dormant_path)
    if dormant_blob != EXPECTED_PROOF_WORKFLOW_BLOB_SHA:
        raise ValueError("DEC-485 dormant proof workflow template blob mismatch")

    if not active_path.is_file():
        raise ValueError("DEC-485 active proof workflow is not installed")
    active_blob = _git_blob_sha(active_path)
    if active_blob != EXPECTED_PROOF_WORKFLOW_BLOB_SHA:
        raise ValueError("DEC-485 active proof workflow blob mismatch")
    if active_path.read_bytes() != dormant_path.read_bytes():
        raise ValueError("DEC-485 active proof workflow differs from dormant template")

    text = active_path.read_text(encoding="utf-8")
    validate_dormant_proof_workflow_template(text)
    if "  workflow_dispatch:" not in text:
        raise ValueError("DEC-485 proof workflow must remain manual-dispatch only")
    if "  push:" in text or "  pull_request:" in text:
        raise ValueError("DEC-485 proof workflow gained an automatic trigger")
    if "  contents: read" not in text or "  actions: read" not in text:
        raise ValueError("DEC-485 proof workflow read permissions drift")
    if "  actions: write" in text or "gh workflow run " in text:
        raise ValueError("DEC-485 proof workflow gained dispatch authority")

    return {
        "authorization_preflight_source": preflight_blob,
        "dormant_proof_workflow_template": dormant_blob,
        "active_proof_workflow": active_blob,
    }


def build_proof_workflow_install_receipt(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source_blobs = validate_proof_workflow_install_receipt_sources(
        repository_root=repository_root,
    )
    return {
        "decision": ANNUAL_CATALOGUE_PROOF_WORKFLOW_INSTALL_RECEIPT_DECISION,
        "version": ANNUAL_CATALOGUE_PROOF_WORKFLOW_INSTALL_RECEIPT_VERSION,
        "stage": (
            "ANNUAL_CATALOGUE_PREFLIGHT_PROOF_WORKFLOW_"
            "INSTALLED_DISPATCH_LOCKED"
        ),
        **source_blobs,
        "authorization_preflight_decision": AUTHORIZATION_PREFLIGHT_DECISION,
        "authorization_basis": "explicit_operator_authorization",
        "authorization_scope": "single_exact_file_creation_consumed",
        "proof_workflow_path": RESERVED_PROOF_WORKFLOW_PATH,
        "proof_workflow_blob_sha": EXPECTED_PROOF_WORKFLOW_BLOB_SHA,
        "dormant_proof_workflow_template_path": (
            DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH
        ),
        "dormant_proof_workflow_template_blob_sha": (
            EXPECTED_PROOF_WORKFLOW_BLOB_SHA
        ),
        "workflow_trigger_mode": "workflow_dispatch_only",
        "workflow_permissions": {
            "contents": "read",
            "actions": "read",
        },
        "proof_workflow_install_authorized": PROOF_WORKFLOW_INSTALL_AUTHORIZED,
        "proof_workflow_install_authorization_consumed": (
            PROOF_WORKFLOW_INSTALL_AUTHORIZATION_CONSUMED
        ),
        "proof_workflow_installed": PROOF_WORKFLOW_INSTALLED,
        "proof_workflow_available": PROOF_WORKFLOW_AVAILABLE,
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
            "EXPLICIT_ANNUAL_PATTERN_CATALOGUE_PROOF_WORKFLOW_"
            "DISPATCH_AUTHORIZATION_BEFORE_RUN"
        ),
    }


__all__ = [
    "ANNUAL_CATALOGUE_PROOF_WORKFLOW_INSTALL_RECEIPT_DECISION",
    "ANNUAL_CATALOGUE_PROOF_WORKFLOW_INSTALL_RECEIPT_VERSION",
    "AUTHORIZATION_PREFLIGHT_DECISION",
    "EXPECTED_AUTHORIZATION_PREFLIGHT_SOURCE_BLOB_SHA",
    "EXPECTED_PROOF_WORKFLOW_BLOB_SHA",
    "PROOF_WORKFLOW_AVAILABLE",
    "PROOF_WORKFLOW_DISPATCH_AUTHORIZED",
    "PROOF_WORKFLOW_INSTALLED",
    "build_proof_workflow_install_receipt",
    "validate_proof_workflow_install_receipt_sources",
]
