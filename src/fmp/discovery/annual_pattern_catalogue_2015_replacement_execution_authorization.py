from __future__ import annotations

import hashlib
from pathlib import Path


ANNUAL_CATALOGUE_2015_REPLACEMENT_EXECUTION_AUTHORIZATION_DECISION = "DEC-498"
ANNUAL_CATALOGUE_2015_REPLACEMENT_EXECUTION_AUTHORIZATION_VERSION = (
    "fmp-annual-catalogue-2015-replacement-execution-authorization-v1"
)

REPLACEMENT_PREFLIGHT_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2015_replacement_dispatch_preflight.py"
)
EXPECTED_REPLACEMENT_PREFLIGHT_SOURCE_BLOB_SHA = (
    "e7a231e3bfb9093b9d1b289fb33b022c69571580"
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

AUTHORIZED_ANNUAL_SEGMENT_LABEL = "2015"
EXPECTED_REPLACEMENT_RUN_NUMBER = 376
EXPECTED_REPLACEMENT_RUN_ATTEMPT = 1
FAILED_FIRST_RUN_ID = 37126711695

REPLACEMENT_RUN_AUTHORIZED = True
HISTORICAL_ARTIFACT_READ_AUTHORIZED_FOR_REPLACEMENT = True
HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED_FOR_REPLACEMENT = True
HISTORICAL_RESULT_PRODUCTION_AUTHORIZED_FOR_REPLACEMENT = True

RERUN_FAILED_RUN_AUTHORIZED = False
RETRY_FAILED_RUN_AUTHORIZED = False
THIRD_OR_LATER_RUN_AUTHORIZED = False
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


def _validate_commit(value: object, *, field: str = "code_commit") -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return value


def validate_2015_replacement_execution_authorization_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "replacement_preflight_source_blob_sha": (
            root / REPLACEMENT_PREFLIGHT_SOURCE_PATH,
            EXPECTED_REPLACEMENT_PREFLIGHT_SOURCE_BLOB_SHA,
        ),
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
            raise ValueError(f"DEC-498 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-498 {field} mismatch")
        actual[field] = sha
    return actual


def require_2015_replacement_execution_authorized(
    *,
    annual_segment_label: str,
    code_commit: str,
    run_number: int,
    run_attempt: int,
) -> None:
    _validate_commit(code_commit)
    if annual_segment_label != AUTHORIZED_ANNUAL_SEGMENT_LABEL:
        raise PermissionError(
            "DEC-498 authorizes replacement execution only for annual segment 2015"
        )
    if (
        _positive_int(run_number, field="run_number")
        != EXPECTED_REPLACEMENT_RUN_NUMBER
    ):
        raise PermissionError(
            "DEC-498 authorizes only replacement workflow run number 376"
        )
    if (
        _positive_int(run_attempt, field="run_attempt")
        != EXPECTED_REPLACEMENT_RUN_ATTEMPT
    ):
        raise PermissionError(
            "DEC-498 authorizes only replacement workflow run attempt 1"
        )
    if not REPLACEMENT_RUN_AUTHORIZED:
        raise PermissionError("DEC-498 replacement run remains locked")
    if not HISTORICAL_ARTIFACT_READ_AUTHORIZED_FOR_REPLACEMENT:
        raise PermissionError("DEC-498 historical artifact reads remain locked")
    if not HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED_FOR_REPLACEMENT:
        raise PermissionError("DEC-498 replacement catalogue execution remains locked")
    if not HISTORICAL_RESULT_PRODUCTION_AUTHORIZED_FOR_REPLACEMENT:
        raise PermissionError("DEC-498 replacement result production remains locked")


def build_2015_replacement_execution_authorization(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_2015_replacement_execution_authorization_sources(
        repository_root=Path(repository_root),
    )
    return {
        "decision": ANNUAL_CATALOGUE_2015_REPLACEMENT_EXECUTION_AUTHORIZATION_DECISION,
        "version": ANNUAL_CATALOGUE_2015_REPLACEMENT_EXECUTION_AUTHORIZATION_VERSION,
        **source,
        "stage": "ANNUAL_CATALOGUE_2015_REPLACEMENT_RUN_AUTHORIZED_NOT_STARTED",
        "authorization_basis": "standing_operator_autonomous_build_authorization",
        "authorization_scope": "2015_replacement_run_376_attempt_1_only",
        "failed_first_run_id": FAILED_FIRST_RUN_ID,
        "annual_segment_label": AUTHORIZED_ANNUAL_SEGMENT_LABEL,
        "expected_run_number": EXPECTED_REPLACEMENT_RUN_NUMBER,
        "expected_run_attempt": EXPECTED_REPLACEMENT_RUN_ATTEMPT,
        "previous_annual_freeze_run_id": None,
        "replacement_run_authorized": REPLACEMENT_RUN_AUTHORIZED,
        "historical_artifact_read_authorized": (
            HISTORICAL_ARTIFACT_READ_AUTHORIZED_FOR_REPLACEMENT
        ),
        "historical_catalogue_execution_authorized": (
            HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED_FOR_REPLACEMENT
        ),
        "historical_result_production_authorized": (
            HISTORICAL_RESULT_PRODUCTION_AUTHORIZED_FOR_REPLACEMENT
        ),
        "rerun_failed_run_authorized": RERUN_FAILED_RUN_AUTHORIZED,
        "retry_failed_run_authorized": RETRY_FAILED_RUN_AUTHORIZED,
        "third_or_later_run_authorized": THIRD_OR_LATER_RUN_AUTHORIZED,
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
            "EXACT_2015_REPLACEMENT_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_"
            "DISPATCH_ON_CURRENT_MAIN"
        ),
    }


__all__ = [
    "ANNUAL_CATALOGUE_2015_REPLACEMENT_EXECUTION_AUTHORIZATION_DECISION",
    "ANNUAL_CATALOGUE_2015_REPLACEMENT_EXECUTION_AUTHORIZATION_VERSION",
    "AUTHORIZED_ANNUAL_SEGMENT_LABEL",
    "EXPECTED_REPLACEMENT_RUN_ATTEMPT",
    "EXPECTED_REPLACEMENT_RUN_NUMBER",
    "REPLACEMENT_RUN_AUTHORIZED",
    "build_2015_replacement_execution_authorization",
    "require_2015_replacement_execution_authorized",
    "validate_2015_replacement_execution_authorization_sources",
]
