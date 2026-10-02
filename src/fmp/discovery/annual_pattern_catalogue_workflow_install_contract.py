from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_workflow_source import (
    CLI_PATH,
    DORMANT_WORKFLOW_TEMPLATE_PATH,
    RESERVED_ACTIVE_WORKFLOW_PATH,
    validate_dormant_source_files,
)


ANNUAL_CATALOGUE_WORKFLOW_INSTALL_CONTRACT_DECISION = "DEC-479"
ANNUAL_CATALOGUE_WORKFLOW_INSTALL_CONTRACT_VERSION = (
    "fmp-annual-pattern-catalogue-workflow-install-contract-v1"
)
SOURCE_WORKFLOW_DECISION = "DEC-478"
SOURCE_WORKFLOW_HEAD_SHA = "aaf4ea66b2b5b908228102dfa387aae7d03ea4d9"

EXPECTED_WORKFLOW_SOURCE_BLOB_SHA = "154e4122b808aeee809361ac8faf6d4df1eeec74"
EXPECTED_CLI_BLOB_SHA = "ec5ea311b6c46d71cbdac9bf2bfb76d66fcce0f3"
EXPECTED_TEMPLATE_BLOB_SHA = "31633e87b79551f5b7dfa6b0deb76a82eb070129"
WORKFLOW_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_workflow_source.py"
)

REPOSITORY_MUTATION_AUTHORIZED = False
WORKFLOW_TEMPLATE_INSTALL_AUTHORIZED = False
WORKFLOW_INSTALLED = False
WORKFLOW_DISPATCH_AUTHORIZED = False
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


def validate_install_sources(*, repository_root: Path) -> dict[str, object]:
    root = Path(repository_root)
    validate_dormant_source_files(repository_root=root)

    expected = {
        "workflow_source": (
            root / WORKFLOW_SOURCE_PATH,
            EXPECTED_WORKFLOW_SOURCE_BLOB_SHA,
        ),
        "cli": (
            root / CLI_PATH,
            EXPECTED_CLI_BLOB_SHA,
        ),
        "dormant_template": (
            root / DORMANT_WORKFLOW_TEMPLATE_PATH,
            EXPECTED_TEMPLATE_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for label, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-479 source file is missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(
                f"DEC-479 {label} Git blob mismatch: {sha} != {expected_sha}"
            )
        actual[label] = sha

    active = root / RESERVED_ACTIVE_WORKFLOW_PATH
    if active.exists():
        raise ValueError("DEC-479 reserved active workflow path must still be absent")

    return {
        "decision": ANNUAL_CATALOGUE_WORKFLOW_INSTALL_CONTRACT_DECISION,
        "source_workflow_decision": SOURCE_WORKFLOW_DECISION,
        "source_workflow_head_sha": SOURCE_WORKFLOW_HEAD_SHA,
        "source_blobs": actual,
        "reserved_active_workflow_path": RESERVED_ACTIVE_WORKFLOW_PATH,
        "active_workflow_present": False,
        "repository_mutation_authorized": False,
        "workflow_template_install_authorized": False,
        "workflow_installed": False,
        "workflow_dispatch_authorized": False,
    }


def install_action_payload(*, repository_root: Path) -> dict[str, object]:
    sources = validate_install_sources(repository_root=Path(repository_root))
    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_WORKFLOW_INSTALL_CONTRACT_DECISION,
        "version": ANNUAL_CATALOGUE_WORKFLOW_INSTALL_CONTRACT_VERSION,
        "source_workflow_decision": SOURCE_WORKFLOW_DECISION,
        "source_workflow_head_sha": SOURCE_WORKFLOW_HEAD_SHA,
        "source_validation": sources,
        "mutation": {
            "kind": "create_file_from_exact_source_bytes",
            "source_path": DORMANT_WORKFLOW_TEMPLATE_PATH,
            "target_path": RESERVED_ACTIVE_WORKFLOW_PATH,
            "target_must_be_absent": True,
            "post_install_bytes_must_equal_source": True,
            "source_template_blob_sha": EXPECTED_TEMPLATE_BLOB_SHA,
        },
        "files_allowed_to_change": [RESERVED_ACTIVE_WORKFLOW_PATH],
        "files_forbidden_to_change": [
            DORMANT_WORKFLOW_TEMPLATE_PATH,
            CLI_PATH,
            WORKFLOW_SOURCE_PATH,
        ],
        "repository_mutation_authorized": REPOSITORY_MUTATION_AUTHORIZED,
        "workflow_template_install_authorized": WORKFLOW_TEMPLATE_INSTALL_AUTHORIZED,
        "workflow_installed": WORKFLOW_INSTALLED,
        "workflow_dispatch_authorized": WORKFLOW_DISPATCH_AUTHORIZED,
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
        "next_gate": "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT",
    }
    validate_install_action_payload(value)
    return value


def validate_install_action_payload(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    exact = {
        "decision": ANNUAL_CATALOGUE_WORKFLOW_INSTALL_CONTRACT_DECISION,
        "version": ANNUAL_CATALOGUE_WORKFLOW_INSTALL_CONTRACT_VERSION,
        "source_workflow_decision": SOURCE_WORKFLOW_DECISION,
        "source_workflow_head_sha": SOURCE_WORKFLOW_HEAD_SHA,
        "files_allowed_to_change": [RESERVED_ACTIVE_WORKFLOW_PATH],
        "files_forbidden_to_change": [
            DORMANT_WORKFLOW_TEMPLATE_PATH,
            CLI_PATH,
            WORKFLOW_SOURCE_PATH,
        ],
        "repository_mutation_authorized": False,
        "workflow_template_install_authorized": False,
        "workflow_installed": False,
        "workflow_dispatch_authorized": False,
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
        "next_gate": "SOURCE_ONLY_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT",
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-479 install action {field} mismatch")

    source_validation = value.get("source_validation")
    if not isinstance(source_validation, Mapping):
        raise ValueError("DEC-479 source validation payload malformed")
    expected_source_validation = {
        "decision": ANNUAL_CATALOGUE_WORKFLOW_INSTALL_CONTRACT_DECISION,
        "source_workflow_decision": SOURCE_WORKFLOW_DECISION,
        "source_workflow_head_sha": SOURCE_WORKFLOW_HEAD_SHA,
        "source_blobs": {
            "workflow_source": EXPECTED_WORKFLOW_SOURCE_BLOB_SHA,
            "cli": EXPECTED_CLI_BLOB_SHA,
            "dormant_template": EXPECTED_TEMPLATE_BLOB_SHA,
        },
        "reserved_active_workflow_path": RESERVED_ACTIVE_WORKFLOW_PATH,
        "active_workflow_present": False,
        "repository_mutation_authorized": False,
        "workflow_template_install_authorized": False,
        "workflow_installed": False,
        "workflow_dispatch_authorized": False,
    }
    if dict(source_validation) != expected_source_validation:
        raise ValueError("DEC-479 source validation payload mismatch")

    mutation = value.get("mutation")
    if not isinstance(mutation, Mapping):
        raise ValueError("DEC-479 mutation payload malformed")
    expected_mutation = {
        "kind": "create_file_from_exact_source_bytes",
        "source_path": DORMANT_WORKFLOW_TEMPLATE_PATH,
        "target_path": RESERVED_ACTIVE_WORKFLOW_PATH,
        "target_must_be_absent": True,
        "post_install_bytes_must_equal_source": True,
        "source_template_blob_sha": EXPECTED_TEMPLATE_BLOB_SHA,
    }
    if dict(mutation) != expected_mutation:
        raise ValueError("DEC-479 mutation payload mismatch")
    return value


def require_repository_mutation_authorized() -> None:
    if not REPOSITORY_MUTATION_AUTHORIZED:
        raise PermissionError(
            "DEC-479 annual catalogue workflow repository mutation remains locked"
        )


__all__ = [
    "ANNUAL_CATALOGUE_WORKFLOW_INSTALL_CONTRACT_DECISION",
    "ANNUAL_CATALOGUE_WORKFLOW_INSTALL_CONTRACT_VERSION",
    "EXPECTED_CLI_BLOB_SHA",
    "EXPECTED_TEMPLATE_BLOB_SHA",
    "EXPECTED_WORKFLOW_SOURCE_BLOB_SHA",
    "REPOSITORY_MUTATION_AUTHORIZED",
    "SOURCE_WORKFLOW_DECISION",
    "SOURCE_WORKFLOW_HEAD_SHA",
    "WORKFLOW_SOURCE_PATH",
    "install_action_payload",
    "require_repository_mutation_authorized",
    "validate_install_action_payload",
    "validate_install_sources",
]
