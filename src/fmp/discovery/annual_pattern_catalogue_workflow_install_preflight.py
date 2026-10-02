from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_workflow_install_contract import (
    ANNUAL_CATALOGUE_WORKFLOW_INSTALL_CONTRACT_DECISION,
    ANNUAL_CATALOGUE_WORKFLOW_INSTALL_CONTRACT_VERSION,
    EXPECTED_TEMPLATE_BLOB_SHA,
    REPOSITORY_MUTATION_AUTHORIZED,
    SOURCE_WORKFLOW_DECISION,
    SOURCE_WORKFLOW_HEAD_SHA,
    install_action_payload,
    validate_install_action_payload,
    validate_install_sources,
)
from .annual_pattern_catalogue_workflow_source import (
    DORMANT_WORKFLOW_TEMPLATE_PATH,
    RESERVED_ACTIVE_WORKFLOW_PATH,
)


ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_DECISION = "DEC-480"
ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_VERSION = (
    "fmp-annual-pattern-catalogue-workflow-install-preflight-v1"
)
SOURCE_INSTALL_CONTRACT_DECISION = (
    ANNUAL_CATALOGUE_WORKFLOW_INSTALL_CONTRACT_DECISION
)
SOURCE_INSTALL_CONTRACT_HEAD_SHA = "95750234d3bce325563f15c605c2312756562ee6"
EXPECTED_INSTALL_CONTRACT_BLOB_SHA = (
    "f9ac5dc517ec3efbb50057ade66c5b5aab2f52b3"
)

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


def validate_preflight_sources(*, repository_root: Path) -> dict[str, object]:
    root = Path(repository_root)
    install_contract = (
        root
        / "src/fmp/discovery/"
        "annual_pattern_catalogue_workflow_install_contract.py"
    )
    if not install_contract.is_file():
        raise ValueError("DEC-480 install contract source is missing")
    actual_contract_blob = _git_blob_sha(install_contract)
    if actual_contract_blob != EXPECTED_INSTALL_CONTRACT_BLOB_SHA:
        raise ValueError(
            "DEC-480 install contract Git blob mismatch: "
            f"{actual_contract_blob} != {EXPECTED_INSTALL_CONTRACT_BLOB_SHA}"
        )

    install_sources = validate_install_sources(repository_root=root)
    return {
        "install_contract_blob_sha": actual_contract_blob,
        "install_sources": install_sources,
    }


def build_workflow_install_preflight(
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    root = Path(repository_root)
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-480 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-480 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-480 main head mismatch")

    sources = validate_preflight_sources(repository_root=root)
    if (root / RESERVED_ACTIVE_WORKFLOW_PATH).exists():
        raise ValueError("DEC-480 requires active workflow path to remain absent")
    if REPOSITORY_MUTATION_AUTHORIZED is not False:
        raise ValueError("DEC-480 repository mutation authority drift")

    install_action = install_action_payload(repository_root=root)
    action_fingerprint = _sha256_bytes(_canonical_json(install_action))

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_DECISION,
        "version": ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_VERSION,
        "source_install_contract_decision": SOURCE_INSTALL_CONTRACT_DECISION,
        "source_install_contract_version": (
            ANNUAL_CATALOGUE_WORKFLOW_INSTALL_CONTRACT_VERSION
        ),
        "source_install_contract_head_sha": SOURCE_INSTALL_CONTRACT_HEAD_SHA,
        "source_workflow_decision": SOURCE_WORKFLOW_DECISION,
        "source_workflow_head_sha": SOURCE_WORKFLOW_HEAD_SHA,
        "expected_head_sha": expected_head_sha,
        "install_contract_blob_sha": sources["install_contract_blob_sha"],
        "install_sources": sources["install_sources"],
        "dormant_workflow_template_path": DORMANT_WORKFLOW_TEMPLATE_PATH,
        "dormant_workflow_template_blob_sha": EXPECTED_TEMPLATE_BLOB_SHA,
        "reserved_active_workflow_path": RESERVED_ACTIVE_WORKFLOW_PATH,
        "active_workflow_present": False,
        "install_action": install_action,
        "install_action_fingerprint": action_fingerprint,
        "preflight_read_only": True,
        "repository_mutation_authorized": False,
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
        "next_gate": (
            "REPOSITORY_HOSTED_READ_ONLY_ANNUAL_PATTERN_CATALOGUE_"
            "WORKFLOW_INSTALL_PREFLIGHT_PROOF"
        ),
    }
    value["preflight_fingerprint"] = _sha256_bytes(_canonical_json(value))
    validate_workflow_install_preflight(value)
    return value


def validate_workflow_install_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = value.get("preflight_fingerprint")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise ValueError("DEC-480 preflight fingerprint malformed")
    unsigned = dict(value)
    unsigned.pop("preflight_fingerprint", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-480 preflight fingerprint mismatch")

    exact = {
        "decision": ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_DECISION,
        "version": ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_VERSION,
        "source_install_contract_decision": SOURCE_INSTALL_CONTRACT_DECISION,
        "source_install_contract_version": (
            ANNUAL_CATALOGUE_WORKFLOW_INSTALL_CONTRACT_VERSION
        ),
        "source_install_contract_head_sha": SOURCE_INSTALL_CONTRACT_HEAD_SHA,
        "source_workflow_decision": SOURCE_WORKFLOW_DECISION,
        "source_workflow_head_sha": SOURCE_WORKFLOW_HEAD_SHA,
        "install_contract_blob_sha": EXPECTED_INSTALL_CONTRACT_BLOB_SHA,
        "dormant_workflow_template_path": DORMANT_WORKFLOW_TEMPLATE_PATH,
        "dormant_workflow_template_blob_sha": EXPECTED_TEMPLATE_BLOB_SHA,
        "reserved_active_workflow_path": RESERVED_ACTIVE_WORKFLOW_PATH,
        "active_workflow_present": False,
        "preflight_read_only": True,
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
        "next_gate": (
            "REPOSITORY_HOSTED_READ_ONLY_ANNUAL_PATTERN_CATALOGUE_"
            "WORKFLOW_INSTALL_PREFLIGHT_PROOF"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-480 {field} mismatch")
    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")

    action = value.get("install_action")
    if not isinstance(action, Mapping):
        raise ValueError("DEC-480 install action malformed")
    validate_install_action_payload(action)
    if action.get("repository_mutation_authorized") is not False:
        raise ValueError("DEC-480 install action mutation authority drift")
    action_fingerprint = value.get("install_action_fingerprint")
    if action_fingerprint != _sha256_bytes(_canonical_json(action)):
        raise ValueError("DEC-480 install action fingerprint mismatch")

    install_sources = value.get("install_sources")
    if not isinstance(install_sources, Mapping):
        raise ValueError("DEC-480 install sources payload malformed")
    source_validation = action.get("source_validation")
    if not isinstance(source_validation, Mapping):
        raise ValueError("DEC-480 install action source validation malformed")
    if dict(install_sources) != dict(source_validation):
        raise ValueError("DEC-480 install sources payload mismatch")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_DECISION",
    "ANNUAL_CATALOGUE_WORKFLOW_INSTALL_PREFLIGHT_VERSION",
    "EXPECTED_INSTALL_CONTRACT_BLOB_SHA",
    "SOURCE_INSTALL_CONTRACT_DECISION",
    "SOURCE_INSTALL_CONTRACT_HEAD_SHA",
    "build_workflow_install_preflight",
    "validate_preflight_sources",
    "validate_workflow_install_preflight",
]
