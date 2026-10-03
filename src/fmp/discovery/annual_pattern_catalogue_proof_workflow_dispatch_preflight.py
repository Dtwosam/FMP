from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_workflow_install_preflight_proof_workflow_install_receipt import (
    ANNUAL_CATALOGUE_PROOF_WORKFLOW_INSTALL_RECEIPT_DECISION,
    ANNUAL_CATALOGUE_PROOF_WORKFLOW_INSTALL_RECEIPT_VERSION,
    PROOF_WORKFLOW_AVAILABLE as RECEIPT_PROOF_WORKFLOW_AVAILABLE,
    PROOF_WORKFLOW_DISPATCH_AUTHORIZED as RECEIPT_DISPATCH_AUTHORIZED,
    PROOF_WORKFLOW_INSTALLED as RECEIPT_PROOF_WORKFLOW_INSTALLED,
)
from .annual_pattern_catalogue_workflow_install_preflight_proof_workflow_source import (
    RESERVED_PROOF_WORKFLOW_PATH,
)


ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_PREFLIGHT_DECISION = "DEC-486"
ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_PREFLIGHT_VERSION = (
    "fmp-annual-catalogue-proof-workflow-dispatch-preflight-v1"
)
INSTALL_RECEIPT_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_workflow_install_preflight_proof_workflow_install_receipt.py"
)
EXPECTED_INSTALL_RECEIPT_BLOB_SHA = "638c988524ccf8ada27067c2b0bdb3403823a6f5"
EXPECTED_ACTIVE_PROOF_WORKFLOW_BLOB_SHA = (
    "0d6c93e2af04501f9ac2589fd24d6672b2b41910"
)

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


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def validate_proof_workflow_dispatch_preflight_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    receipt_path = root / INSTALL_RECEIPT_SOURCE_PATH
    active_path = root / RESERVED_PROOF_WORKFLOW_PATH

    if not receipt_path.is_file():
        raise ValueError("DEC-486 DEC-485 install receipt source missing")
    receipt_blob = _git_blob_sha(receipt_path)
    if receipt_blob != EXPECTED_INSTALL_RECEIPT_BLOB_SHA:
        raise ValueError("DEC-486 DEC-485 install receipt blob mismatch")

    if not active_path.is_file():
        raise ValueError("DEC-486 requires installed proof workflow")
    active_blob = _git_blob_sha(active_path)
    if active_blob != EXPECTED_ACTIVE_PROOF_WORKFLOW_BLOB_SHA:
        raise ValueError("DEC-486 active proof workflow blob mismatch")

    if RECEIPT_PROOF_WORKFLOW_INSTALLED is not True:
        raise ValueError("DEC-486 requires installed proof workflow state")
    if RECEIPT_PROOF_WORKFLOW_AVAILABLE is not True:
        raise ValueError("DEC-486 requires proof workflow availability")
    if RECEIPT_DISPATCH_AUTHORIZED is not False:
        raise ValueError("DEC-486 requires proof dispatch authority false")

    return {
        "install_receipt_blob_sha": receipt_blob,
        "active_proof_workflow_blob_sha": active_blob,
    }


def _validate_proof_run_inventory(
    value: Mapping[str, object],
) -> dict[str, object]:
    runs = value.get("workflow_runs")
    if not isinstance(runs, list):
        raise ValueError("DEC-486 proof workflow_runs must be a list")
    if runs:
        raise ValueError(
            "DEC-486 requires zero proof-workflow runs before dispatch authorization"
        )
    return {
        "proof_workflow_run_count": 0,
        "proof_workflow_run_id": None,
        "proof_workflow_run_number": None,
        "proof_workflow_run_attempt": None,
        "proof_workflow_run_status": None,
        "proof_workflow_run_conclusion": None,
    }


def build_proof_workflow_dispatch_preflight(
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    proof_workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_proof_workflow_dispatch_preflight_sources(
        repository_root=Path(repository_root),
    )
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-486 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-486 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-486 main head mismatch")

    inventory = _validate_proof_run_inventory(proof_workflow_runs)

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_PREFLIGHT_DECISION,
        "version": ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_PREFLIGHT_VERSION,
        "install_receipt_decision": (
            ANNUAL_CATALOGUE_PROOF_WORKFLOW_INSTALL_RECEIPT_DECISION
        ),
        "install_receipt_version": (
            ANNUAL_CATALOGUE_PROOF_WORKFLOW_INSTALL_RECEIPT_VERSION
        ),
        **source,
        "expected_head_sha": expected_head_sha,
        "stage": (
            "ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_"
            "PREFLIGHT_INSTALLED_READY_AUTHORIZATION_LOCKED"
        ),
        "active_proof_workflow_path": RESERVED_PROOF_WORKFLOW_PATH,
        "active_proof_workflow_present": True,
        "proof_workflow_installed": True,
        "proof_workflow_available": True,
        **inventory,
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
    validate_proof_workflow_dispatch_preflight(value)
    return value


def validate_proof_workflow_dispatch_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    exact = {
        "decision": ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_PREFLIGHT_DECISION,
        "version": ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_PREFLIGHT_VERSION,
        "install_receipt_decision": (
            ANNUAL_CATALOGUE_PROOF_WORKFLOW_INSTALL_RECEIPT_DECISION
        ),
        "install_receipt_version": (
            ANNUAL_CATALOGUE_PROOF_WORKFLOW_INSTALL_RECEIPT_VERSION
        ),
        "install_receipt_blob_sha": EXPECTED_INSTALL_RECEIPT_BLOB_SHA,
        "active_proof_workflow_blob_sha": EXPECTED_ACTIVE_PROOF_WORKFLOW_BLOB_SHA,
        "stage": (
            "ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_"
            "PREFLIGHT_INSTALLED_READY_AUTHORIZATION_LOCKED"
        ),
        "active_proof_workflow_path": RESERVED_PROOF_WORKFLOW_PATH,
        "active_proof_workflow_present": True,
        "proof_workflow_installed": True,
        "proof_workflow_available": True,
        "proof_workflow_run_count": 0,
        "proof_workflow_run_id": None,
        "proof_workflow_run_number": None,
        "proof_workflow_run_attempt": None,
        "proof_workflow_run_status": None,
        "proof_workflow_run_conclusion": None,
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
            "EXPLICIT_ANNUAL_PATTERN_CATALOGUE_PROOF_WORKFLOW_"
            "DISPATCH_AUTHORIZATION_BEFORE_RUN"
        ),
    }
    expected_keys = set(exact) | {"expected_head_sha"}
    if set(value) != expected_keys:
        raise ValueError("DEC-486 dispatch preflight key set mismatch")
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-486 {field} mismatch")
    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_PREFLIGHT_DECISION",
    "ANNUAL_CATALOGUE_PROOF_WORKFLOW_DISPATCH_PREFLIGHT_VERSION",
    "EXPECTED_ACTIVE_PROOF_WORKFLOW_BLOB_SHA",
    "EXPECTED_INSTALL_RECEIPT_BLOB_SHA",
    "build_proof_workflow_dispatch_preflight",
    "validate_proof_workflow_dispatch_preflight",
    "validate_proof_workflow_dispatch_preflight_sources",
]
