from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_runtime import (
    HISTORICAL_ARTIFACT_READ_AUTHORIZED as RUNTIME_ARTIFACT_READ_AUTHORIZED,
    HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED as RUNTIME_EXECUTION_AUTHORIZED,
    HISTORICAL_RESULT_PRODUCTION_AUTHORIZED as RUNTIME_RESULT_AUTHORIZED,
)
from .annual_pattern_catalogue_workflow_install_receipt import (
    ANNUAL_WORKFLOW_AVAILABLE as RECEIPT_WORKFLOW_AVAILABLE,
    ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED as RECEIPT_DISPATCH_AUTHORIZED,
    ANNUAL_WORKFLOW_INSTALLED as RECEIPT_WORKFLOW_INSTALLED,
)
from .annual_pattern_catalogue_workflow_source import (
    RESERVED_ACTIVE_WORKFLOW_PATH,
    prior_segment_label,
    validate_annual_segment_label,
)


ANNUAL_CATALOGUE_2015_EXECUTION_PREFLIGHT_DECISION = "DEC-492"
ANNUAL_CATALOGUE_2015_EXECUTION_PREFLIGHT_VERSION = (
    "fmp-annual-catalogue-2015-execution-preflight-v1"
)

INSTALL_RECEIPT_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_workflow_install_receipt.py"
)
EXPECTED_INSTALL_RECEIPT_BLOB_SHA = "970ab466dfa5f87c6955ad65da4653a993e9d6fd"
RUNTIME_SOURCE_PATH = "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
EXPECTED_RUNTIME_SOURCE_BLOB_SHA = "0044c19575ec005a31ab98beefccfc57fe9e72da"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "31633e87b79551f5b7dfa6b0deb76a82eb070129"
)

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


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def validate_2015_execution_preflight_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    receipt_path = root / INSTALL_RECEIPT_SOURCE_PATH
    runtime_path = root / RUNTIME_SOURCE_PATH
    workflow_path = root / RESERVED_ACTIVE_WORKFLOW_PATH

    expected = {
        "install_receipt_blob_sha": (
            receipt_path,
            EXPECTED_INSTALL_RECEIPT_BLOB_SHA,
        ),
        "runtime_source_blob_sha": (
            runtime_path,
            EXPECTED_RUNTIME_SOURCE_BLOB_SHA,
        ),
        "active_workflow_blob_sha": (
            workflow_path,
            EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-492 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-492 {field} mismatch")
        actual[field] = sha

    if RECEIPT_WORKFLOW_INSTALLED is not True:
        raise ValueError("DEC-492 requires installed annual workflow")
    if RECEIPT_WORKFLOW_AVAILABLE is not True:
        raise ValueError("DEC-492 requires available annual workflow")
    if RECEIPT_DISPATCH_AUTHORIZED is not False:
        raise ValueError("DEC-492 requires annual workflow dispatch locked")
    if RUNTIME_ARTIFACT_READ_AUTHORIZED is not False:
        raise ValueError("DEC-492 requires historical artifact reads locked")
    if RUNTIME_EXECUTION_AUTHORIZED is not False:
        raise ValueError("DEC-492 requires historical execution locked")
    if RUNTIME_RESULT_AUTHORIZED is not False:
        raise ValueError("DEC-492 requires result production locked")

    return actual


def _validate_run_inventory(
    value: Mapping[str, object],
) -> dict[str, object]:
    runs = value.get("workflow_runs")
    if not isinstance(runs, list):
        raise ValueError("DEC-492 annual workflow_runs must be a list")
    if runs:
        raise ValueError(
            "DEC-492 requires zero annual-catalogue workflow runs before "
            "first 2015 execution authorization"
        )
    return {
        "annual_workflow_run_count": 0,
        "annual_workflow_run_id": None,
        "annual_workflow_run_number": None,
        "annual_workflow_run_attempt": None,
        "annual_workflow_run_status": None,
        "annual_workflow_run_conclusion": None,
    }


def build_2015_execution_preflight(
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    annual_workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2015_execution_preflight_sources(
        repository_root=Path(repository_root),
    )
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-492 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-492 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-492 main head mismatch")

    segment = validate_annual_segment_label("2015")
    if prior_segment_label(segment) is not None:
        raise ValueError("DEC-492 2015 predecessor invariant drift")

    inventory = _validate_run_inventory(annual_workflow_runs)

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2015_EXECUTION_PREFLIGHT_DECISION,
        "version": ANNUAL_CATALOGUE_2015_EXECUTION_PREFLIGHT_VERSION,
        **source,
        "expected_head_sha": expected_head_sha,
        "stage": (
            "ANNUAL_CATALOGUE_2015_EXECUTION_PREFLIGHT_"
            "INSTALLED_READY_AUTHORIZATION_LOCKED"
        ),
        "annual_segment_label": segment,
        "prior_segment_required": False,
        "prior_segment_label": None,
        "previous_annual_freeze_run_id": None,
        "active_workflow_path": RESERVED_ACTIVE_WORKFLOW_PATH,
        "annual_workflow_installed": True,
        "annual_workflow_available": True,
        **inventory,
        "expected_first_run_number": 1,
        "expected_first_run_attempt": 1,
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
            "EXPLICIT_ANNUAL_PATTERN_CATALOGUE_2015_EXECUTION_"
            "AUTHORIZATION_BEFORE_RUN"
        ),
    }
    validate_2015_execution_preflight(value)
    return value


def validate_2015_execution_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    exact = {
        "decision": ANNUAL_CATALOGUE_2015_EXECUTION_PREFLIGHT_DECISION,
        "version": ANNUAL_CATALOGUE_2015_EXECUTION_PREFLIGHT_VERSION,
        "install_receipt_blob_sha": EXPECTED_INSTALL_RECEIPT_BLOB_SHA,
        "runtime_source_blob_sha": EXPECTED_RUNTIME_SOURCE_BLOB_SHA,
        "active_workflow_blob_sha": EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        "stage": (
            "ANNUAL_CATALOGUE_2015_EXECUTION_PREFLIGHT_"
            "INSTALLED_READY_AUTHORIZATION_LOCKED"
        ),
        "annual_segment_label": "2015",
        "prior_segment_required": False,
        "prior_segment_label": None,
        "previous_annual_freeze_run_id": None,
        "active_workflow_path": RESERVED_ACTIVE_WORKFLOW_PATH,
        "annual_workflow_installed": True,
        "annual_workflow_available": True,
        "annual_workflow_run_count": 0,
        "annual_workflow_run_id": None,
        "annual_workflow_run_number": None,
        "annual_workflow_run_attempt": None,
        "annual_workflow_run_status": None,
        "annual_workflow_run_conclusion": None,
        "expected_first_run_number": 1,
        "expected_first_run_attempt": 1,
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
            "EXPLICIT_ANNUAL_PATTERN_CATALOGUE_2015_EXECUTION_"
            "AUTHORIZATION_BEFORE_RUN"
        ),
    }
    expected_keys = set(exact) | {"expected_head_sha"}
    if set(value) != expected_keys:
        raise ValueError("DEC-492 execution preflight key set mismatch")
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-492 {field} mismatch")
    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2015_EXECUTION_PREFLIGHT_DECISION",
    "ANNUAL_CATALOGUE_2015_EXECUTION_PREFLIGHT_VERSION",
    "EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA",
    "EXPECTED_INSTALL_RECEIPT_BLOB_SHA",
    "EXPECTED_RUNTIME_SOURCE_BLOB_SHA",
    "build_2015_execution_preflight",
    "validate_2015_execution_preflight",
    "validate_2015_execution_preflight_sources",
]
