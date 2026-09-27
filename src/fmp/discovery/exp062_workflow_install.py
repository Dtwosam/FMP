from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from .exp062_workflow_source import (
    DORMANT_WORKFLOW_TEMPLATE_PATH,
    HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED,
    RESERVED_ACTIVE_WORKFLOW_PATH,
    WORKFLOW_DISPATCH_AUTHORIZED,
    require_historical_execution_authorized,
    validate_dormant_workflow_template,
)


EXP062_LOCKED_WORKFLOW_INSTALL_DECISION = "DEC-300"
EXP062_LOCKED_WORKFLOW_INSTALL_VERSION = (
    "fmp-exp062-locked-workflow-install-v1"
)

EXPECTED_TEMPLATE_BLOB_SHA = "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = EXPECTED_TEMPLATE_BLOB_SHA

ACTIVE_WORKFLOW_INSTALLED = True
PROOF_DISPATCH_AUTHORIZED = False
HISTORICAL_RESULT_DISPATCH_AUTHORIZED = False
DISCOVERY_RESULT_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def git_blob_sha(text: str) -> str:
    raw = text.encode("utf-8")
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def validate_locked_workflow_installation(
    *,
    dormant_text: str,
    active_text: str,
) -> dict[str, object]:
    validate_dormant_workflow_template(dormant_text)
    validate_dormant_workflow_template(active_text)
    if active_text != dormant_text:
        raise ValueError(
            "DEC-300 active workflow differs from frozen dormant template"
        )

    dormant_blob = git_blob_sha(dormant_text)
    active_blob = git_blob_sha(active_text)
    if dormant_blob != EXPECTED_TEMPLATE_BLOB_SHA:
        raise ValueError("DEC-300 dormant workflow blob identity mismatch")
    if active_blob != EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA:
        raise ValueError("DEC-300 active workflow blob identity mismatch")

    return {
        "decision": EXP062_LOCKED_WORKFLOW_INSTALL_DECISION,
        "install_version": EXP062_LOCKED_WORKFLOW_INSTALL_VERSION,
        "dormant_template_path": DORMANT_WORKFLOW_TEMPLATE_PATH,
        "active_workflow_path": RESERVED_ACTIVE_WORKFLOW_PATH,
        "dormant_template_blob_sha": dormant_blob,
        "active_workflow_blob_sha": active_blob,
        "active_workflow_installed": ACTIVE_WORKFLOW_INSTALLED,
        "workflow_dispatch_authorized": WORKFLOW_DISPATCH_AUTHORIZED,
        "proof_dispatch_authorized": PROOF_DISPATCH_AUTHORIZED,
        "historical_result_dispatch_authorized": (
            HISTORICAL_RESULT_DISPATCH_AUTHORIZED
        ),
        "historical_discovery_execution_authorized": (
            HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED
        ),
        "discovery_result_authorized": DISCOVERY_RESULT_AUTHORIZED,
        "reserved_robustness_access_authorized": (
            RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED
        ),
        "candidate_compilation_authorized": CANDIDATE_COMPILATION_AUTHORIZED,
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
    }


def validate_installed_paths_from_repo(
    root: Path = Path("."),
) -> Mapping[str, object]:
    dormant = root / DORMANT_WORKFLOW_TEMPLATE_PATH
    active = root / RESERVED_ACTIVE_WORKFLOW_PATH
    if not dormant.is_file():
        raise ValueError("DEC-300 dormant workflow template is missing")
    if not active.is_file():
        raise ValueError("DEC-300 active workflow installation is missing")
    return validate_locked_workflow_installation(
        dormant_text=dormant.read_text(encoding="utf-8"),
        active_text=active.read_text(encoding="utf-8"),
    )


def require_proof_dispatch_authorized() -> None:
    if not PROOF_DISPATCH_AUTHORIZED:
        raise PermissionError("DEC-300 proof dispatch remains locked")


def require_historical_result_dispatch_authorized(
    *,
    code_commit: str,
) -> None:
    if not HISTORICAL_RESULT_DISPATCH_AUTHORIZED:
        raise PermissionError(
            "DEC-300 historical result dispatch remains locked"
        )
    require_historical_execution_authorized(code_commit=code_commit)


__all__ = [
    "ACTIVE_WORKFLOW_INSTALLED",
    "EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA",
    "EXPECTED_TEMPLATE_BLOB_SHA",
    "EXP062_LOCKED_WORKFLOW_INSTALL_DECISION",
    "EXP062_LOCKED_WORKFLOW_INSTALL_VERSION",
    "HISTORICAL_RESULT_DISPATCH_AUTHORIZED",
    "PROOF_DISPATCH_AUTHORIZED",
    "git_blob_sha",
    "require_historical_result_dispatch_authorized",
    "require_proof_dispatch_authorized",
    "validate_installed_paths_from_repo",
    "validate_locked_workflow_installation",
]
