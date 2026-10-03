from __future__ import annotations

import hashlib
from pathlib import Path

from .annual_pattern_catalogue_2015_run1_failure_receipt import (
    ANNUAL_CATALOGUE_2015_RUN1_FAILURE_RECEIPT_DECISION,
    ANNUAL_CATALOGUE_2015_RUN1_FAILURE_RECEIPT_VERSION,
)


ANNUAL_CATALOGUE_ARTIFACT_UPLOAD_REPAIR_DECISION = "DEC-496"
ANNUAL_CATALOGUE_ARTIFACT_UPLOAD_REPAIR_VERSION = (
    "fmp-annual-catalogue-artifact-upload-repair-v1"
)

FAILURE_RECEIPT_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2015_run1_failure_receipt.py"
)
EXPECTED_FAILURE_RECEIPT_SOURCE_BLOB_SHA = (
    "1ae96e83dc5d895dce1c5f981f1c785401de22f5"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
PRE_REPAIR_WORKFLOW_SNAPSHOT_PATH = (
    "tests/fixtures/phase8a_annual_pattern_catalogue_workflow_dec493.yml.snapshot"
)
EXPECTED_PRE_REPAIR_WORKFLOW_BLOB_SHA = (
    "31633e87b79551f5b7dfa6b0deb76a82eb070129"
)
EXPECTED_REPAIRED_WORKFLOW_BLOB_SHA = (
    "f7e65ee95f472918e390bceedd7cf2f38bbf7e92"
)

REPLACEMENT_RUN_AUTHORIZED = False
RERUN_AUTHORIZED = False
RETRY_AUTHORIZED = False
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


def validate_artifact_upload_repair_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "failure_receipt_source_blob_sha": (
            root / FAILURE_RECEIPT_SOURCE_PATH,
            EXPECTED_FAILURE_RECEIPT_SOURCE_BLOB_SHA,
        ),
        "pre_repair_workflow_blob_sha": (
            root / PRE_REPAIR_WORKFLOW_SNAPSHOT_PATH,
            EXPECTED_PRE_REPAIR_WORKFLOW_BLOB_SHA,
        ),
        "repaired_workflow_blob_sha": (
            root / ACTIVE_WORKFLOW_PATH,
            EXPECTED_REPAIRED_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-496 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-496 {field} mismatch")
        actual[field] = sha

    if ANNUAL_CATALOGUE_2015_RUN1_FAILURE_RECEIPT_DECISION != "DEC-495":
        raise ValueError("DEC-496 failure receipt decision drift")
    if (
        ANNUAL_CATALOGUE_2015_RUN1_FAILURE_RECEIPT_VERSION
        != "fmp-annual-catalogue-2015-run1-failure-receipt-v1"
    ):
        raise ValueError("DEC-496 failure receipt version drift")

    text = (root / ACTIVE_WORKFLOW_PATH).read_text(encoding="utf-8")
    if text.count("uses: actions/upload-artifact@v6") != 3:
        raise ValueError("DEC-496 upload-artifact action count drift")
    if text.count("include-hidden-files: true") != 3:
        raise ValueError("DEC-496 hidden-file upload repair count drift")
    for path in (
        "path: .preflight",
        "path: .result",
        "path: .annual-freeze/annual-freeze.json",
    ):
        if path not in text:
            raise ValueError(f"DEC-496 expected hidden artifact path missing: {path}")

    before = (root / PRE_REPAIR_WORKFLOW_SNAPSHOT_PATH).read_text(
        encoding="utf-8"
    )
    if "include-hidden-files: true" in before:
        raise ValueError("DEC-496 pre-repair snapshot unexpectedly contains repair")

    return actual


def build_artifact_upload_repair_receipt(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_artifact_upload_repair_sources(
        repository_root=Path(repository_root),
    )
    return {
        "decision": ANNUAL_CATALOGUE_ARTIFACT_UPLOAD_REPAIR_DECISION,
        "version": ANNUAL_CATALOGUE_ARTIFACT_UPLOAD_REPAIR_VERSION,
        **source,
        "stage": "ANNUAL_CATALOGUE_HIDDEN_ARTIFACT_UPLOADS_REPAIRED",
        "failure_receipt_decision": "DEC-495",
        "failed_run_id": 37126711695,
        "failed_run_number": 1,
        "failed_run_attempt": 1,
        "failed_run_conclusion": "failure",
        "failed_run_cell_execution": False,
        "failed_run_result_production": False,
        "repair_scope": "upload_hidden_artifacts_only",
        "upload_action": "actions/upload-artifact@v6",
        "repaired_upload_count": 3,
        "include_hidden_files": True,
        "preflight_upload_repaired": True,
        "cell_product_upload_repaired": True,
        "annual_freeze_upload_repaired": True,
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
            "EXPLICIT_ANNUAL_PATTERN_CATALOGUE_2015_REPLACEMENT_RUN_"
            "AUTHORIZATION_BEFORE_DISPATCH"
        ),
    }


__all__ = [
    "ANNUAL_CATALOGUE_ARTIFACT_UPLOAD_REPAIR_DECISION",
    "ANNUAL_CATALOGUE_ARTIFACT_UPLOAD_REPAIR_VERSION",
    "EXPECTED_REPAIRED_WORKFLOW_BLOB_SHA",
    "build_artifact_upload_repair_receipt",
    "validate_artifact_upload_repair_sources",
]
