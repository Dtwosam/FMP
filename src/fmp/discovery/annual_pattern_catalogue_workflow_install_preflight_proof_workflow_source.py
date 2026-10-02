from __future__ import annotations

import hashlib
from pathlib import Path

from .annual_pattern_catalogue_workflow_install_preflight_proof import (
    ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_PROOF_DECISION,
    PROOF_WORKFLOW_NAME,
    PROOF_WORKFLOW_PATH,
)


ANNUAL_CATALOGUE_PREFLIGHT_PROOF_WORKFLOW_SOURCE_DECISION = "DEC-482"
ANNUAL_CATALOGUE_PREFLIGHT_PROOF_WORKFLOW_SOURCE_VERSION = (
    "fmp-annual-catalogue-preflight-proof-workflow-source-v1"
)
SOURCE_PROOF_CONTRACT_DECISION = (
    ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_PROOF_DECISION
)
SOURCE_PROOF_CONTRACT_HEAD_SHA = "d14b7e0f1f549b8396d2855f80a2c020d9cc3fa4"

DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH = (
    "docs/superpowers/templates/"
    "phase8a-annual-pattern-catalogue-workflow-install-preflight-proof.yml.disabled"
)
RESERVED_PROOF_WORKFLOW_PATH = PROOF_WORKFLOW_PATH
PREFLIGHT_CLI_PATH = (
    "scripts/phase8a_annual_pattern_catalogue_workflow_install_preflight.py"
)

EXPECTED_PROOF_CONTRACT_BLOB_SHA = "fb9ea8d4a17734ee91225d48012a0a5b0088d415"
EXPECTED_PREFLIGHT_CLI_BLOB_SHA = "f7bb6cdc62511d3dcc907d856f55f06f6302e640"
EXPECTED_DORMANT_PROOF_WORKFLOW_TEMPLATE_BLOB_SHA = (
    "0d6c93e2af04501f9ac2589fd24d6672b2b41910"
)

PROOF_WORKFLOW_TEMPLATE_INSTALL_AUTHORIZED = False
PROOF_WORKFLOW_INSTALLED = False
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


def validate_proof_workflow_source_dependencies(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "proof_contract": (
            root
            / "src/fmp/discovery/"
            "annual_pattern_catalogue_workflow_install_preflight_proof.py",
            EXPECTED_PROOF_CONTRACT_BLOB_SHA,
        ),
        "preflight_cli": (
            root / PREFLIGHT_CLI_PATH,
            EXPECTED_PREFLIGHT_CLI_BLOB_SHA,
        ),
    }
    out: dict[str, str] = {}
    for label, (path, expected_blob) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-482 source dependency is missing: {path}")
        actual = _git_blob_sha(path)
        if actual != expected_blob:
            raise ValueError(
                f"DEC-482 {label} Git blob mismatch: "
                f"{actual} != {expected_blob}"
            )
        out[label] = actual
    return out


def validate_dormant_proof_workflow_template(text: str) -> None:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("DEC-482 dormant proof workflow template must be non-empty")

    required = (
        f"name: {PROOF_WORKFLOW_NAME}",
        "workflow_dispatch:",
        "permissions:",
        "contents: read",
        "actions: read",
        "test \"$GITHUB_EVENT_NAME\" = \"workflow_dispatch\"",
        "test \"$GITHUB_REF\" = \"refs/heads/main\"",
        "gh api \"repos/$GITHUB_REPOSITORY/branches/main\"",
        "phase8a_annual_pattern_catalogue_workflow_install_preflight.py plan",
        "--expected-head-sha \"$GITHUB_SHA\"",
        "preflight.json",
        "actions/upload-artifact@v6",
    )
    for needle in required:
        if needle not in text:
            raise ValueError(
                f"DEC-482 proof workflow template missing frozen source: {needle}"
            )

    forbidden = (
        "gh workflow run ",
        "phase8a_annual_pattern_catalogue.py cell",
        "phase8a_annual_pattern_catalogue.py freeze",
        "run_locked_annual_catalogue_cell",
        "repository_mutation_authorized: true",
    )
    for needle in forbidden:
        if needle in text:
            raise ValueError(
                f"DEC-482 proof workflow contains forbidden surface: {needle}"
            )


def validate_dormant_proof_workflow_source(
    *,
    repository_root: Path,
) -> dict[str, object]:
    root = Path(repository_root)
    deps = validate_proof_workflow_source_dependencies(repository_root=root)
    template = root / DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH
    active = root / RESERVED_PROOF_WORKFLOW_PATH
    if not template.is_file():
        raise ValueError("DEC-482 dormant proof workflow template is missing")
    template_blob = _git_blob_sha(template)
    if template_blob != EXPECTED_DORMANT_PROOF_WORKFLOW_TEMPLATE_BLOB_SHA:
        raise ValueError(
            "DEC-482 dormant proof workflow template Git blob mismatch: "
            f"{template_blob} != "
            f"{EXPECTED_DORMANT_PROOF_WORKFLOW_TEMPLATE_BLOB_SHA}"
        )
    if active.exists():
        raise ValueError("DEC-482 proof workflow must not be installed")
    validate_dormant_proof_workflow_template(
        template.read_text(encoding="utf-8")
    )
    return {
        "decision": ANNUAL_CATALOGUE_PREFLIGHT_PROOF_WORKFLOW_SOURCE_DECISION,
        "source_proof_contract_decision": SOURCE_PROOF_CONTRACT_DECISION,
        "source_proof_contract_head_sha": SOURCE_PROOF_CONTRACT_HEAD_SHA,
        "source_dependencies": deps,
        "dormant_template_path": DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH,
        "dormant_template_blob_sha": template_blob,
        "reserved_proof_workflow_path": RESERVED_PROOF_WORKFLOW_PATH,
        "proof_workflow_present": False,
        "proof_workflow_template_install_authorized": False,
        "proof_workflow_installed": False,
        "proof_workflow_dispatch_authorized": False,
    }


def proof_workflow_source_payload(*, repository_root: Path) -> dict[str, object]:
    source = validate_dormant_proof_workflow_source(
        repository_root=Path(repository_root)
    )
    return {
        "decision": ANNUAL_CATALOGUE_PREFLIGHT_PROOF_WORKFLOW_SOURCE_DECISION,
        "version": ANNUAL_CATALOGUE_PREFLIGHT_PROOF_WORKFLOW_SOURCE_VERSION,
        "source_proof_contract_decision": SOURCE_PROOF_CONTRACT_DECISION,
        "source_proof_contract_head_sha": SOURCE_PROOF_CONTRACT_HEAD_SHA,
        "proof_workflow_name": PROOF_WORKFLOW_NAME,
        "proof_workflow_path": RESERVED_PROOF_WORKFLOW_PATH,
        "source_validation": source,
        "proof_workflow_template_install_authorized": (
            PROOF_WORKFLOW_TEMPLATE_INSTALL_AUTHORIZED
        ),
        "proof_workflow_installed": PROOF_WORKFLOW_INSTALLED,
        "proof_workflow_dispatch_authorized": PROOF_WORKFLOW_DISPATCH_AUTHORIZED,
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
            "WORKFLOW_INSTALL_PREFLIGHT_PROOF_WORKFLOW_INSTALL_CONTRACT"
        ),
    }


__all__ = [
    "ANNUAL_CATALOGUE_PREFLIGHT_PROOF_WORKFLOW_SOURCE_DECISION",
    "ANNUAL_CATALOGUE_PREFLIGHT_PROOF_WORKFLOW_SOURCE_VERSION",
    "DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH",
    "EXPECTED_DORMANT_PROOF_WORKFLOW_TEMPLATE_BLOB_SHA",
    "EXPECTED_PREFLIGHT_CLI_BLOB_SHA",
    "EXPECTED_PROOF_CONTRACT_BLOB_SHA",
    "PREFLIGHT_CLI_PATH",
    "RESERVED_PROOF_WORKFLOW_PATH",
    "SOURCE_PROOF_CONTRACT_DECISION",
    "SOURCE_PROOF_CONTRACT_HEAD_SHA",
    "proof_workflow_source_payload",
    "validate_dormant_proof_workflow_source",
    "validate_dormant_proof_workflow_template",
    "validate_proof_workflow_source_dependencies",
]
