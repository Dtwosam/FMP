from __future__ import annotations

import hashlib
from pathlib import Path


ANNUAL_CATALOGUE_2015_RUN1_FAILURE_RECEIPT_DECISION = "DEC-495"
ANNUAL_CATALOGUE_2015_RUN1_FAILURE_RECEIPT_VERSION = (
    "fmp-annual-catalogue-2015-run1-failure-receipt-v1"
)

DISPATCH_PREFLIGHT_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2015_dispatch_preflight.py"
)
EXPECTED_DISPATCH_PREFLIGHT_SOURCE_BLOB_SHA = (
    "ac78fb75c4743edaa6883203aac24b3ddb23eeeb"
)
PRE_REPAIR_WORKFLOW_SNAPSHOT_PATH = (
    "tests/fixtures/phase8a_annual_pattern_catalogue_workflow_dec493.yml.snapshot"
)
EXPECTED_PRE_REPAIR_WORKFLOW_BLOB_SHA = (
    "31633e87b79551f5b7dfa6b0deb76a82eb070129"
)

MAIN_HEAD_SHA = "fd85a886d07234ad584dcca08692b37e6af54b2e"
RUN_ID = 37126711695
RUN_NUMBER = 1
RUN_ATTEMPT = 1
PREFLIGHT_JOB_ID = 111213380390

RERUN_AUTHORIZED = False
RETRY_AUTHORIZED = False
REPLACEMENT_RUN_AUTHORIZED = False
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


def validate_2015_run1_failure_receipt_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dispatch_preflight_source_blob_sha": (
            root / DISPATCH_PREFLIGHT_SOURCE_PATH,
            EXPECTED_DISPATCH_PREFLIGHT_SOURCE_BLOB_SHA,
        ),
        "pre_repair_workflow_blob_sha": (
            root / PRE_REPAIR_WORKFLOW_SNAPSHOT_PATH,
            EXPECTED_PRE_REPAIR_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-495 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-495 {field} mismatch")
        actual[field] = sha
    return actual


def build_2015_run1_failure_receipt(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_2015_run1_failure_receipt_sources(
        repository_root=Path(repository_root),
    )
    return {
        "decision": ANNUAL_CATALOGUE_2015_RUN1_FAILURE_RECEIPT_DECISION,
        "version": ANNUAL_CATALOGUE_2015_RUN1_FAILURE_RECEIPT_VERSION,
        **source,
        "stage": "ANNUAL_CATALOGUE_2015_RUN1_FAILED_BEFORE_CELL_EXECUTION",
        "repository_full_name": "Dtwosam/FMP",
        "main_head_sha": MAIN_HEAD_SHA,
        "annual_segment_label": "2015",
        "run_id": RUN_ID,
        "run_number": RUN_NUMBER,
        "run_attempt": RUN_ATTEMPT,
        "run_event": "workflow_dispatch",
        "run_status": "completed",
        "run_conclusion": "failure",
        "preflight_job_id": PREFLIGHT_JOB_ID,
        "preflight_job_name": "annual-preflight-2015",
        "preflight_job_status": "completed",
        "preflight_job_conclusion": "failure",
        "failing_step": "Upload annual catalogue preflight evidence",
        "failure_class": "hidden_artifact_path_filtered_by_upload_action",
        "upload_action": "actions/upload-artifact@v6",
        "upload_include_hidden_files": False,
        "preflight_files_created_before_failure": True,
        "preflight_artifact_uploaded": False,
        "annual_cell_jobs_executed": False,
        "annual_freeze_job_executed": False,
        "catalogue_results_produced": False,
        "annual_freeze_produced": False,
        "first_run_authorization_consumed": True,
        "rerun_authorized": RERUN_AUTHORIZED,
        "retry_authorized": RETRY_AUTHORIZED,
        "replacement_run_authorized": REPLACEMENT_RUN_AUTHORIZED,
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
            "REPAIR_ANNUAL_CATALOGUE_HIDDEN_ARTIFACT_UPLOADS_THEN_"
            "EXPLICIT_2015_REPLACEMENT_RUN_AUTHORIZATION"
        ),
    }


__all__ = [
    "ANNUAL_CATALOGUE_2015_RUN1_FAILURE_RECEIPT_DECISION",
    "ANNUAL_CATALOGUE_2015_RUN1_FAILURE_RECEIPT_VERSION",
    "build_2015_run1_failure_receipt",
    "validate_2015_run1_failure_receipt_sources",
]
