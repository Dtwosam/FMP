from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_artifact_upload_repair import (
    ANNUAL_CATALOGUE_ARTIFACT_UPLOAD_REPAIR_DECISION,
    ANNUAL_CATALOGUE_ARTIFACT_UPLOAD_REPAIR_VERSION,
)


ANNUAL_CATALOGUE_2015_REPLACEMENT_DISPATCH_PREFLIGHT_DECISION = "DEC-497"
ANNUAL_CATALOGUE_2015_REPLACEMENT_DISPATCH_PREFLIGHT_VERSION = (
    "fmp-annual-catalogue-2015-replacement-dispatch-preflight-v1"
)

FAILURE_RECEIPT_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2015_run1_failure_receipt.py"
)
EXPECTED_FAILURE_RECEIPT_SOURCE_BLOB_SHA = (
    "1ae96e83dc5d895dce1c5f981f1c785401de22f5"
)
UPLOAD_REPAIR_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_artifact_upload_repair.py"
)
EXPECTED_UPLOAD_REPAIR_SOURCE_BLOB_SHA = (
    "adfa75b352a561667b8c23efbcfb07af804d1131"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_REPAIRED_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)

FAILED_RUN_ID = 37126711695
FAILED_RUN_NUMBER = 1
FAILED_RUN_ATTEMPT = 1
FAILED_RUN_HEAD_SHA = "fd85a886d07234ad584dcca08692b37e6af54b2e"

REPLACEMENT_RUN_AUTHORIZED = False
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


def validate_2015_replacement_dispatch_preflight_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "failure_receipt_source_blob_sha": (
            root / FAILURE_RECEIPT_SOURCE_PATH,
            EXPECTED_FAILURE_RECEIPT_SOURCE_BLOB_SHA,
        ),
        "upload_repair_source_blob_sha": (
            root / UPLOAD_REPAIR_SOURCE_PATH,
            EXPECTED_UPLOAD_REPAIR_SOURCE_BLOB_SHA,
        ),
        "active_workflow_blob_sha": (
            root / ACTIVE_WORKFLOW_PATH,
            EXPECTED_REPAIRED_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-497 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-497 {field} mismatch")
        actual[field] = sha

    if ANNUAL_CATALOGUE_ARTIFACT_UPLOAD_REPAIR_DECISION != "DEC-496":
        raise ValueError("DEC-497 upload repair decision drift")
    if (
        ANNUAL_CATALOGUE_ARTIFACT_UPLOAD_REPAIR_VERSION
        != "fmp-annual-catalogue-artifact-upload-repair-v1"
    ):
        raise ValueError("DEC-497 upload repair version drift")

    return actual


def _validate_failed_run_inventory(
    value: Mapping[str, object],
) -> dict[str, object]:
    runs = value.get("workflow_runs")
    if not isinstance(runs, list):
        raise ValueError("DEC-497 annual workflow_runs must be a list")
    if len(runs) != 1:
        raise ValueError(
            "DEC-497 requires exactly one prior annual-catalogue workflow run"
        )
    row = runs[0]
    if not isinstance(row, Mapping):
        raise ValueError("DEC-497 failed run row is malformed")

    exact = {
        "id": FAILED_RUN_ID,
        "run_number": FAILED_RUN_NUMBER,
        "run_attempt": FAILED_RUN_ATTEMPT,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": FAILED_RUN_HEAD_SHA,
        "status": "completed",
        "conclusion": "failure",
    }
    for field, expected in exact.items():
        if row.get(field) != expected:
            raise ValueError(f"DEC-497 prior failed run {field} mismatch")

    return {
        "prior_run_count": 1,
        "failed_run_id": FAILED_RUN_ID,
        "failed_run_number": FAILED_RUN_NUMBER,
        "failed_run_attempt": FAILED_RUN_ATTEMPT,
        "failed_run_head_sha": FAILED_RUN_HEAD_SHA,
        "failed_run_conclusion": "failure",
    }


def build_2015_replacement_dispatch_preflight(
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    annual_workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2015_replacement_dispatch_preflight_sources(
        repository_root=Path(repository_root),
    )
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-497 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-497 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-497 main head mismatch")

    inventory = _validate_failed_run_inventory(annual_workflow_runs)

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2015_REPLACEMENT_DISPATCH_PREFLIGHT_DECISION,
        "version": ANNUAL_CATALOGUE_2015_REPLACEMENT_DISPATCH_PREFLIGHT_VERSION,
        **source,
        **inventory,
        "stage": "ANNUAL_CATALOGUE_2015_REPLACEMENT_PREFLIGHT_AUTHORIZATION_LOCKED",
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": expected_head_sha,
        "annual_segment_label": "2015",
        "previous_annual_freeze_run_id": "",
        "active_workflow_path": ACTIVE_WORKFLOW_PATH,
        "expected_replacement_run_number": 2,
        "expected_replacement_run_attempt": 1,
        "replacement_run_authorized": REPLACEMENT_RUN_AUTHORIZED,
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
        "dispatch_command_present": False,
        "preflight_read_only": True,
        "next_gate": (
            "EXPLICIT_ANNUAL_PATTERN_CATALOGUE_2015_REPLACEMENT_RUN_"
            "AUTHORIZATION_BEFORE_DISPATCH"
        ),
    }
    validate_2015_replacement_dispatch_preflight(value)
    return value


def validate_2015_replacement_dispatch_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    if value.get("decision") != "DEC-497":
        raise ValueError("DEC-497 decision mismatch")
    if value.get("prior_run_count") != 1:
        raise ValueError("DEC-497 prior run count mismatch")
    if value.get("failed_run_id") != FAILED_RUN_ID:
        raise ValueError("DEC-497 failed run id mismatch")
    if value.get("expected_replacement_run_number") != 376:
        raise ValueError("DEC-497 replacement run number mismatch")
    if value.get("expected_replacement_run_attempt") != 1:
        raise ValueError("DEC-497 replacement run attempt mismatch")
    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    for field in (
        "replacement_run_authorized",
        "historical_artifact_read_authorized",
        "historical_catalogue_execution_authorized",
        "historical_result_production_authorized",
        "next_segment_execution_authorized",
        "cross_year_result_production_authorized",
        "strategy_v1_synthesis_authorized",
        "promotion_authorized",
        "phase8b_authorized",
        "demo_order_authorized",
        "broker_mutation_authorized",
        "live_order_authorized",
        "real_money_authorized",
        "trading_authorized",
        "dispatch_command_present",
    ):
        if value.get(field) is not False:
            raise ValueError(f"DEC-497 {field} must remain false")
    if value.get("preflight_read_only") is not True:
        raise ValueError("DEC-497 preflight must remain read-only")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2015_REPLACEMENT_DISPATCH_PREFLIGHT_DECISION",
    "ANNUAL_CATALOGUE_2015_REPLACEMENT_DISPATCH_PREFLIGHT_VERSION",
    "build_2015_replacement_dispatch_preflight",
    "validate_2015_replacement_dispatch_preflight",
    "validate_2015_replacement_dispatch_preflight_sources",
]
