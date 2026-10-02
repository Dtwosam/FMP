from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_workflow_install_preflight_proof_workflow_source import (
    ANNUAL_CATALOGUE_PREFLIGHT_PROOF_WORKFLOW_SOURCE_DECISION,
    DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH,
    EXPECTED_DORMANT_PROOF_WORKFLOW_TEMPLATE_BLOB_SHA,
    EXPECTED_PREFLIGHT_CLI_BLOB_SHA,
    EXPECTED_PROOF_CONTRACT_BLOB_SHA,
    PREFLIGHT_CLI_PATH,
    RESERVED_PROOF_WORKFLOW_PATH,
    SOURCE_PROOF_CONTRACT_DECISION,
    SOURCE_PROOF_CONTRACT_HEAD_SHA,
    validate_dormant_proof_workflow_source,
)


ANNUAL_CATALOGUE_PREFLIGHT_PROOF_WORKFLOW_INSTALL_CONTRACT_DECISION = "DEC-483"
ANNUAL_CATALOGUE_PREFLIGHT_PROOF_WORKFLOW_INSTALL_CONTRACT_VERSION = (
    "fmp-annual-catalogue-preflight-proof-workflow-install-contract-v1"
)
SOURCE_PROOF_WORKFLOW_DECISION = (
    ANNUAL_CATALOGUE_PREFLIGHT_PROOF_WORKFLOW_SOURCE_DECISION
)
SOURCE_PROOF_WORKFLOW_HEAD_SHA = "532ab82a6c028c4f4cdf47d9515f18ef83457c45"

PROOF_WORKFLOW_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_workflow_install_preflight_proof_workflow_source.py"
)
PROOF_CONTRACT_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_workflow_install_preflight_proof.py"
)
EXPECTED_PROOF_WORKFLOW_SOURCE_BLOB_SHA = (
    "625c311a8f19633b3ee05459175d640d30762ecc"
)
EXPECTED_PROOF_WORKFLOW_TEMPLATE_BLOB_SHA = (
    EXPECTED_DORMANT_PROOF_WORKFLOW_TEMPLATE_BLOB_SHA
)

REPOSITORY_MUTATION_AUTHORIZED = False
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


def _expected_source_validation() -> dict[str, object]:
    return {
        "decision": SOURCE_PROOF_WORKFLOW_DECISION,
        "source_proof_contract_decision": SOURCE_PROOF_CONTRACT_DECISION,
        "source_proof_contract_head_sha": SOURCE_PROOF_CONTRACT_HEAD_SHA,
        "source_dependencies": {
            "proof_contract": EXPECTED_PROOF_CONTRACT_BLOB_SHA,
            "preflight_cli": EXPECTED_PREFLIGHT_CLI_BLOB_SHA,
        },
        "dormant_template_path": DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH,
        "dormant_template_blob_sha": EXPECTED_PROOF_WORKFLOW_TEMPLATE_BLOB_SHA,
        "reserved_proof_workflow_path": RESERVED_PROOF_WORKFLOW_PATH,
        "proof_workflow_present": False,
        "proof_workflow_template_install_authorized": False,
        "proof_workflow_installed": False,
        "proof_workflow_dispatch_authorized": False,
    }


def validate_install_sources(*, repository_root: Path) -> dict[str, object]:
    root = Path(repository_root)
    source_validation = validate_dormant_proof_workflow_source(
        repository_root=root
    )
    if dict(source_validation) != _expected_source_validation():
        raise ValueError("DEC-483 DEC-482 source validation payload mismatch")

    expected = {
        "proof_workflow_source": (
            root / PROOF_WORKFLOW_SOURCE_PATH,
            EXPECTED_PROOF_WORKFLOW_SOURCE_BLOB_SHA,
        ),
        "dormant_template": (
            root / DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH,
            EXPECTED_PROOF_WORKFLOW_TEMPLATE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-483 source file is missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(
                f"DEC-483 {label} Git blob mismatch: {sha} != {expected_sha}"
            )
        actual[label] = sha

    active = root / RESERVED_PROOF_WORKFLOW_PATH
    if active.exists():
        raise ValueError(
            "DEC-483 reserved proof workflow path must still be absent"
        )

    return {
        "decision": (
            ANNUAL_CATALOGUE_PREFLIGHT_PROOF_WORKFLOW_INSTALL_CONTRACT_DECISION
        ),
        "source_proof_workflow_decision": SOURCE_PROOF_WORKFLOW_DECISION,
        "source_proof_workflow_head_sha": SOURCE_PROOF_WORKFLOW_HEAD_SHA,
        "source_validation": source_validation,
        "source_blobs": actual,
        "reserved_proof_workflow_path": RESERVED_PROOF_WORKFLOW_PATH,
        "proof_workflow_present": False,
        "repository_mutation_authorized": False,
        "proof_workflow_template_install_authorized": False,
        "proof_workflow_installed": False,
        "proof_workflow_dispatch_authorized": False,
    }


def install_action_payload(*, repository_root: Path) -> dict[str, object]:
    sources = validate_install_sources(repository_root=Path(repository_root))
    value: dict[str, object] = {
        "decision": (
            ANNUAL_CATALOGUE_PREFLIGHT_PROOF_WORKFLOW_INSTALL_CONTRACT_DECISION
        ),
        "version": (
            ANNUAL_CATALOGUE_PREFLIGHT_PROOF_WORKFLOW_INSTALL_CONTRACT_VERSION
        ),
        "source_proof_workflow_decision": SOURCE_PROOF_WORKFLOW_DECISION,
        "source_proof_workflow_head_sha": SOURCE_PROOF_WORKFLOW_HEAD_SHA,
        "source_validation": sources["source_validation"],
        "source_blobs": sources["source_blobs"],
        "mutation": {
            "kind": "create_file_from_exact_source_bytes",
            "source_path": DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH,
            "target_path": RESERVED_PROOF_WORKFLOW_PATH,
            "target_must_be_absent": True,
            "post_install_bytes_must_equal_source": True,
            "source_template_blob_sha": EXPECTED_PROOF_WORKFLOW_TEMPLATE_BLOB_SHA,
        },
        "files_allowed_to_change": [RESERVED_PROOF_WORKFLOW_PATH],
        "files_forbidden_to_change": [
            DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH,
            PROOF_WORKFLOW_SOURCE_PATH,
            PROOF_CONTRACT_SOURCE_PATH,
            PREFLIGHT_CLI_PATH,
        ],
        "repository_mutation_authorized": REPOSITORY_MUTATION_AUTHORIZED,
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
            "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_"
            "PROOF_WORKFLOW_INSTALL_PREFLIGHT"
        ),
    }
    validate_install_action_payload(value)
    return value


def validate_install_action_payload(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    exact = {
        "decision": (
            ANNUAL_CATALOGUE_PREFLIGHT_PROOF_WORKFLOW_INSTALL_CONTRACT_DECISION
        ),
        "version": (
            ANNUAL_CATALOGUE_PREFLIGHT_PROOF_WORKFLOW_INSTALL_CONTRACT_VERSION
        ),
        "source_proof_workflow_decision": SOURCE_PROOF_WORKFLOW_DECISION,
        "source_proof_workflow_head_sha": SOURCE_PROOF_WORKFLOW_HEAD_SHA,
        "files_allowed_to_change": [RESERVED_PROOF_WORKFLOW_PATH],
        "files_forbidden_to_change": [
            DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH,
            PROOF_WORKFLOW_SOURCE_PATH,
            PROOF_CONTRACT_SOURCE_PATH,
            PREFLIGHT_CLI_PATH,
        ],
        "repository_mutation_authorized": False,
        "proof_workflow_template_install_authorized": False,
        "proof_workflow_installed": False,
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
            "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_"
            "PROOF_WORKFLOW_INSTALL_PREFLIGHT"
        ),
    }
    expected_keys = set(exact) | {"source_validation", "source_blobs", "mutation"}
    if set(value) != expected_keys:
        raise ValueError("DEC-483 install action key set mismatch")
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-483 install action {field} mismatch")

    source_validation = value.get("source_validation")
    if not isinstance(source_validation, Mapping):
        raise ValueError("DEC-483 source validation payload malformed")
    if dict(source_validation) != _expected_source_validation():
        raise ValueError("DEC-483 source validation payload mismatch")

    source_blobs = value.get("source_blobs")
    expected_source_blobs = {
        "proof_workflow_source": EXPECTED_PROOF_WORKFLOW_SOURCE_BLOB_SHA,
        "dormant_template": EXPECTED_PROOF_WORKFLOW_TEMPLATE_BLOB_SHA,
    }
    if not isinstance(source_blobs, Mapping):
        raise ValueError("DEC-483 source blobs payload malformed")
    if dict(source_blobs) != expected_source_blobs:
        raise ValueError("DEC-483 source blobs payload mismatch")

    mutation = value.get("mutation")
    if not isinstance(mutation, Mapping):
        raise ValueError("DEC-483 mutation payload malformed")
    expected_mutation = {
        "kind": "create_file_from_exact_source_bytes",
        "source_path": DORMANT_PROOF_WORKFLOW_TEMPLATE_PATH,
        "target_path": RESERVED_PROOF_WORKFLOW_PATH,
        "target_must_be_absent": True,
        "post_install_bytes_must_equal_source": True,
        "source_template_blob_sha": EXPECTED_PROOF_WORKFLOW_TEMPLATE_BLOB_SHA,
    }
    if dict(mutation) != expected_mutation:
        raise ValueError("DEC-483 mutation payload mismatch")
    return value


def require_repository_mutation_authorized() -> None:
    if not REPOSITORY_MUTATION_AUTHORIZED:
        raise PermissionError(
            "DEC-483 proof workflow repository mutation remains locked"
        )


__all__ = [
    "ANNUAL_CATALOGUE_PREFLIGHT_PROOF_WORKFLOW_INSTALL_CONTRACT_DECISION",
    "ANNUAL_CATALOGUE_PREFLIGHT_PROOF_WORKFLOW_INSTALL_CONTRACT_VERSION",
    "EXPECTED_PROOF_WORKFLOW_SOURCE_BLOB_SHA",
    "EXPECTED_PROOF_WORKFLOW_TEMPLATE_BLOB_SHA",
    "PROOF_CONTRACT_SOURCE_PATH",
    "PROOF_WORKFLOW_SOURCE_PATH",
    "REPOSITORY_MUTATION_AUTHORIZED",
    "SOURCE_PROOF_WORKFLOW_DECISION",
    "SOURCE_PROOF_WORKFLOW_HEAD_SHA",
    "install_action_payload",
    "require_repository_mutation_authorized",
    "validate_install_action_payload",
    "validate_install_sources",
]
