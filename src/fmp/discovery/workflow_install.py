from __future__ import annotations

from pathlib import Path
from typing import Mapping

from .run_contract import expected_job_names
from .workflow_source import (
    DORMANT_WORKFLOW_TEMPLATE_PATH,
    HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED,
    RESERVED_ACTIVE_WORKFLOW_PATH,
    WORKFLOW_DISPATCH_AUTHORIZED,
    WORKFLOW_TEMPLATE_INSTALL_AUTHORIZED,
    validate_dormant_workflow_template,
)


EXP061_GUARDED_WORKFLOW_INSTALL_DECISION = "DEC-276"
EXP061_GUARDED_WORKFLOW_INSTALL_VERSION = "fmp-exp061-guarded-workflow-install-v1"

REVIEWED_WORKFLOW_BLOB_SHA = "ca7dfccc1a11aeb49a91e5fb1d84519f08623538"

ACTIVE_WORKFLOW_INSTALLED = True
ACTIVE_WORKFLOW_SOURCE_REVIEWED = True
ACTIVE_WORKFLOW_DISPATCH_AUTHORIZED = False
HISTORICAL_RESULT_RUN_AUTHORIZED = False
HISTORICAL_DISCOVERY_RESULT_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def validate_installed_workflow(
    *,
    dormant_text: str,
    active_text: str,
) -> None:
    validate_dormant_workflow_template(dormant_text)
    validate_dormant_workflow_template(active_text)
    if active_text != dormant_text:
        raise ValueError(
            "DEC-276 active EXP-061 workflow must equal reviewed dormant template"
        )
    if HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED:
        raise ValueError("DEC-276 historical execution gate must remain false")
    if WORKFLOW_DISPATCH_AUTHORIZED:
        raise ValueError("DEC-276 workflow dispatch authority must remain false")


def validate_installed_workflow_paths(
    *,
    repository_root: Path,
) -> None:
    root = Path(repository_root)
    dormant_path = root / DORMANT_WORKFLOW_TEMPLATE_PATH
    active_path = root / RESERVED_ACTIVE_WORKFLOW_PATH
    if not dormant_path.is_file():
        raise ValueError("DEC-276 reviewed dormant workflow template is missing")
    if not active_path.is_file():
        raise ValueError("DEC-276 active guarded workflow source is missing")
    validate_installed_workflow(
        dormant_text=dormant_path.read_text(encoding="utf-8"),
        active_text=active_path.read_text(encoding="utf-8"),
    )


def workflow_install_payload() -> dict[str, object]:
    return {
        "decision": EXP061_GUARDED_WORKFLOW_INSTALL_DECISION,
        "install_version": EXP061_GUARDED_WORKFLOW_INSTALL_VERSION,
        "reviewed_workflow_blob_sha": REVIEWED_WORKFLOW_BLOB_SHA,
        "dormant_template_path": DORMANT_WORKFLOW_TEMPLATE_PATH,
        "active_workflow_path": RESERVED_ACTIVE_WORKFLOW_PATH,
        "active_workflow_installed": ACTIVE_WORKFLOW_INSTALLED,
        "active_workflow_source_reviewed": ACTIVE_WORKFLOW_SOURCE_REVIEWED,
        "expected_job_names": list(expected_job_names()),
        "manual_dispatch_surface_present": True,
        "workflow_dispatch_authorized": ACTIVE_WORKFLOW_DISPATCH_AUTHORIZED,
        "historical_result_run_authorized": HISTORICAL_RESULT_RUN_AUTHORIZED,
        "historical_discovery_execution_authorized": (
            HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED
        ),
        "historical_discovery_result_authorized": (
            HISTORICAL_DISCOVERY_RESULT_AUTHORIZED
        ),
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


__all__ = [
    "ACTIVE_WORKFLOW_DISPATCH_AUTHORIZED",
    "ACTIVE_WORKFLOW_INSTALLED",
    "ACTIVE_WORKFLOW_SOURCE_REVIEWED",
    "EXP061_GUARDED_WORKFLOW_INSTALL_DECISION",
    "EXP061_GUARDED_WORKFLOW_INSTALL_VERSION",
    "HISTORICAL_RESULT_RUN_AUTHORIZED",
    "REVIEWED_WORKFLOW_BLOB_SHA",
    "validate_installed_workflow",
    "validate_installed_workflow_paths",
    "workflow_install_payload",
]
