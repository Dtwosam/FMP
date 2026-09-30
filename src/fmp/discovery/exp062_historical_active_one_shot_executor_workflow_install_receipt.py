from __future__ import annotations

import hashlib
from pathlib import Path

from .exp062_historical_active_one_shot_executor_workflow_install_mutation_authorization import (
    EXPLICIT_REPOSITORY_MUTATION_AUTHORIZED,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED,
)


EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_RECEIPT_DECISION = (
    "DEC-424"
)
EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_RECEIPT_VERSION = (
    "fmp-exp062-active-one-shot-historical-executor-workflow-install-receipt-v1"
)

DEC423_MUTATION_AUTHORIZATION_BLOB_SHA = (
    "df6a80d1f6ee6315f3e3095433ed6704666ccd33"
)
DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH = (
    "docs/superpowers/templates/"
    "phase8a-exp062-one-shot-historical-executor.yml.disabled"
)
ACTIVE_EXECUTOR_WORKFLOW_PATH = (
    ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
)
EXECUTOR_WORKFLOW_BLOB_SHA = "51ce87584369be957482460d81649adb1cb9f05d"

HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED = True
HISTORICAL_EXECUTOR_AVAILABLE = True
HISTORICAL_RESULT_DISPATCH_AUTHORIZED = False
HISTORICAL_EXECUTE_MODE_AVAILABLE = False
RERUN_AUTHORIZED = False
RETRY_AUTHORIZED = False
REPLACEMENT_RUN_AUTHORIZED = False
RESERVED_ROBUSTNESS_ACCESS_AUTHORIZED = False
CANDIDATE_COMPILATION_AUTHORIZED = False
PROMOTION_AUTHORIZED = False
PHASE8B_AUTHORIZED = False
DEMO_ORDER_AUTHORIZED = False
BROKER_MUTATION_AUTHORIZED = False
LIVE_ORDER_AUTHORIZED = False
REAL_MONEY_AUTHORIZED = False
TRADING_AUTHORIZED = False


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def validate_active_one_shot_historical_executor_workflow_install_receipt_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    authorization_path = (
        root
        / "src/fmp/discovery/"
        "exp062_historical_active_one_shot_executor_workflow_install_mutation_authorization.py"
    )
    dormant_path = root / DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH
    active_path = root / ACTIVE_EXECUTOR_WORKFLOW_PATH

    if not authorization_path.is_file():
        raise ValueError(f"missing DEC-424 authorization source: {authorization_path}")
    authorization_sha = _git_blob_sha(authorization_path)
    if authorization_sha != DEC423_MUTATION_AUTHORIZATION_BLOB_SHA:
        raise ValueError("DEC-424 DEC-423 mutation-authorization Git blob mismatch")

    if not dormant_path.is_file():
        raise ValueError("DEC-424 dormant executor template missing")
    dormant_sha = _git_blob_sha(dormant_path)
    if dormant_sha != EXECUTOR_WORKFLOW_BLOB_SHA:
        raise ValueError("DEC-424 dormant executor template Git blob mismatch")

    if not active_path.is_file():
        raise ValueError("DEC-424 active executor workflow is not installed")
    active_sha = _git_blob_sha(active_path)
    if active_sha != EXECUTOR_WORKFLOW_BLOB_SHA:
        raise ValueError("DEC-424 active executor workflow Git blob mismatch")
    if active_path.read_bytes() != dormant_path.read_bytes():
        raise ValueError("DEC-424 active workflow differs from dormant template")

    return {
        "dec423_mutation_authorization": authorization_sha,
        "dormant_executor_workflow_template": dormant_sha,
        "active_executor_workflow": active_sha,
    }


def build_active_one_shot_historical_executor_workflow_install_receipt(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source_blobs = (
        validate_active_one_shot_historical_executor_workflow_install_receipt_sources(
            repository_root=repository_root,
        )
    )

    if EXPLICIT_REPOSITORY_MUTATION_AUTHORIZED is not True:
        raise ValueError("DEC-424 requires explicit repository mutation authorization")
    if HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED is not True:
        raise ValueError("DEC-424 requires workflow-install authorization")

    return {
        "decision": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_RECEIPT_DECISION
        ),
        "version": (
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_RECEIPT_VERSION
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "ACTIVE_WORKFLOW_INSTALLED_DISPATCH_LOCKED"
        ),
        **source_blobs,
        "authorization_decision": "DEC-423",
        "authorization_basis": "explicit_operator_authorization",
        "explicit_repository_mutation_authorized": True,
        "active_executor_workflow_path": ACTIVE_EXECUTOR_WORKFLOW_PATH,
        "active_executor_workflow_blob_sha": EXECUTOR_WORKFLOW_BLOB_SHA,
        "dormant_executor_workflow_template_path": (
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH
        ),
        "dormant_executor_workflow_template_blob_sha": (
            EXECUTOR_WORKFLOW_BLOB_SHA
        ),
        "workflow_trigger_mode": "workflow_dispatch_only",
        "historical_executor_workflow_install_authorized": True,
        "historical_executor_workflow_installed": True,
        "historical_executor_available": True,
        "historical_result_dispatch_authorized": False,
        "historical_execute_mode_available": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "next_gate": "EXPLICIT_ONE_SHOT_EXECUTOR_DISPATCH_AUTHORIZATION_BEFORE_RUN",
    }


__all__ = [
    "ACTIVE_EXECUTOR_WORKFLOW_PATH",
    "DEC423_MUTATION_AUTHORIZATION_BLOB_SHA",
    "EXECUTOR_WORKFLOW_BLOB_SHA",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_RECEIPT_DECISION",
    "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_RECEIPT_VERSION",
    "HISTORICAL_EXECUTOR_AVAILABLE",
    "HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED",
    "HISTORICAL_EXECUTE_MODE_AVAILABLE",
    "HISTORICAL_RESULT_DISPATCH_AUTHORIZED",
    "build_active_one_shot_historical_executor_workflow_install_receipt",
    "validate_active_one_shot_historical_executor_workflow_install_receipt_sources",
]
