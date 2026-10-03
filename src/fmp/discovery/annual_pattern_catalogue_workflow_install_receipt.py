from __future__ import annotations

import hashlib
from pathlib import Path

from .annual_pattern_catalogue_workflow_source import (
    DORMANT_WORKFLOW_TEMPLATE_PATH,
    RESERVED_ACTIVE_WORKFLOW_PATH,
    validate_dormant_workflow_template,
)


ANNUAL_CATALOGUE_WORKFLOW_INSTALL_RECEIPT_DECISION = "DEC-491"
ANNUAL_CATALOGUE_WORKFLOW_INSTALL_RECEIPT_VERSION = (
    "fmp-annual-catalogue-workflow-install-receipt-v1"
)
RUNTIME_EVIDENCE_BINDING_DECISION = "DEC-490"
RUNTIME_EVIDENCE_BINDING_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_proof_workflow_runtime_evidence_binding.py"
)
EXPECTED_RUNTIME_EVIDENCE_BINDING_SOURCE_BLOB_SHA = (
    "ed6eccd796a6c35f9ed768a4bc1ce2d4ae78f830"
)
INSTALL_CONTRACT_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_workflow_install_contract.py"
)
EXPECTED_INSTALL_CONTRACT_SOURCE_BLOB_SHA = (
    "f9ac5dc517ec3efbb50057ade66c5b5aab2f52b3"
)
EXPECTED_ANNUAL_WORKFLOW_BLOB_SHA = (
    "31633e87b79551f5b7dfa6b0deb76a82eb070129"
)

ANNUAL_WORKFLOW_INSTALL_AUTHORIZED = True
ANNUAL_WORKFLOW_INSTALL_AUTHORIZATION_CONSUMED = True
ANNUAL_WORKFLOW_INSTALLED = True
ANNUAL_WORKFLOW_AVAILABLE = True

REPOSITORY_MUTATION_AUTHORIZED = False
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
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def validate_annual_workflow_install_receipt_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    binding_path = root / RUNTIME_EVIDENCE_BINDING_SOURCE_PATH
    contract_path = root / INSTALL_CONTRACT_SOURCE_PATH
    dormant_path = root / DORMANT_WORKFLOW_TEMPLATE_PATH
    active_path = root / RESERVED_ACTIVE_WORKFLOW_PATH

    expected = {
        "runtime_evidence_binding_source": (
            binding_path,
            EXPECTED_RUNTIME_EVIDENCE_BINDING_SOURCE_BLOB_SHA,
        ),
        "install_contract_source": (
            contract_path,
            EXPECTED_INSTALL_CONTRACT_SOURCE_BLOB_SHA,
        ),
        "dormant_annual_workflow_template": (
            dormant_path,
            EXPECTED_ANNUAL_WORKFLOW_BLOB_SHA,
        ),
        "active_annual_workflow": (
            active_path,
            EXPECTED_ANNUAL_WORKFLOW_BLOB_SHA,
        ),
    }

    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-491 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(
                f"DEC-491 {label} Git blob mismatch: {sha} != {expected_sha}"
            )
        actual[label] = sha

    if active_path.read_bytes() != dormant_path.read_bytes():
        raise ValueError("DEC-491 active annual workflow differs from dormant template")

    text = active_path.read_text(encoding="utf-8")
    validate_dormant_workflow_template(text)
    if "  workflow_dispatch:" not in text:
        raise ValueError("DEC-491 annual workflow must remain manual-dispatch only")
    if "  push:" in text or "  pull_request:" in text:
        raise ValueError("DEC-491 annual workflow gained an automatic trigger")
    if "  contents: read" not in text or "  actions: read" not in text:
        raise ValueError("DEC-491 annual workflow read permissions drift")
    if "  actions: write" in text or "gh workflow run " in text:
        raise ValueError("DEC-491 annual workflow gained nested dispatch authority")
    if text.count(
        "python scripts/phase8a_annual_pattern_catalogue.py require-execution"
    ) != 3:
        raise ValueError("DEC-491 annual workflow execution-gate count drift")

    return actual


def build_annual_workflow_install_receipt(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source_blobs = validate_annual_workflow_install_receipt_sources(
        repository_root=Path(repository_root),
    )
    return {
        "decision": ANNUAL_CATALOGUE_WORKFLOW_INSTALL_RECEIPT_DECISION,
        "version": ANNUAL_CATALOGUE_WORKFLOW_INSTALL_RECEIPT_VERSION,
        "stage": "ANNUAL_CATALOGUE_WORKFLOW_INSTALLED_EXECUTION_LOCKED",
        **source_blobs,
        "runtime_evidence_binding_decision": RUNTIME_EVIDENCE_BINDING_DECISION,
        "authorization_basis": "explicit_operator_authorization",
        "authorization_scope": "single_exact_annual_workflow_file_creation_consumed",
        "annual_workflow_path": RESERVED_ACTIVE_WORKFLOW_PATH,
        "annual_workflow_blob_sha": EXPECTED_ANNUAL_WORKFLOW_BLOB_SHA,
        "dormant_annual_workflow_template_path": DORMANT_WORKFLOW_TEMPLATE_PATH,
        "dormant_annual_workflow_template_blob_sha": (
            EXPECTED_ANNUAL_WORKFLOW_BLOB_SHA
        ),
        "workflow_trigger_mode": "workflow_dispatch_only",
        "workflow_permissions": {
            "contents": "read",
            "actions": "read",
        },
        "execution_gate_count": 3,
        "annual_workflow_install_authorized": ANNUAL_WORKFLOW_INSTALL_AUTHORIZED,
        "annual_workflow_install_authorization_consumed": (
            ANNUAL_WORKFLOW_INSTALL_AUTHORIZATION_CONSUMED
        ),
        "annual_workflow_installed": ANNUAL_WORKFLOW_INSTALLED,
        "annual_workflow_available": ANNUAL_WORKFLOW_AVAILABLE,
        "repository_mutation_authorized": REPOSITORY_MUTATION_AUTHORIZED,
        "annual_workflow_dispatch_authorized": (
            ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED
        ),
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
            "EXPLICIT_ANNUAL_PATTERN_CATALOGUE_2015_EXECUTION_"
            "AUTHORIZATION_BEFORE_RUN"
        ),
    }


__all__ = [
    "ANNUAL_CATALOGUE_WORKFLOW_INSTALL_RECEIPT_DECISION",
    "ANNUAL_CATALOGUE_WORKFLOW_INSTALL_RECEIPT_VERSION",
    "ANNUAL_WORKFLOW_AVAILABLE",
    "ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED",
    "ANNUAL_WORKFLOW_INSTALLED",
    "EXPECTED_ANNUAL_WORKFLOW_BLOB_SHA",
    "EXPECTED_INSTALL_CONTRACT_SOURCE_BLOB_SHA",
    "EXPECTED_RUNTIME_EVIDENCE_BINDING_SOURCE_BLOB_SHA",
    "build_annual_workflow_install_receipt",
    "validate_annual_workflow_install_receipt_sources",
]
