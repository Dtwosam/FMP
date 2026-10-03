from __future__ import annotations

import hashlib
from pathlib import Path


ANNUAL_CATALOGUE_2015_EXECUTION_AUTHORIZATION_DECISION = "DEC-493"
ANNUAL_CATALOGUE_2015_EXECUTION_AUTHORIZATION_VERSION = (
    "fmp-annual-catalogue-2015-execution-authorization-v1"
)

EXECUTION_PREFLIGHT_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2015_execution_preflight.py"
)
EXPECTED_EXECUTION_PREFLIGHT_BLOB_SHA = (
    "d36343a6f2c69ccc2f942e537f5599cbc92b263b"
)
INSTALL_RECEIPT_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_workflow_install_receipt.py"
)
EXPECTED_INSTALL_RECEIPT_BLOB_SHA = "970ab466dfa5f87c6955ad65da4653a993e9d6fd"
ACTIVE_WORKFLOW_PATH = (
    ".github/workflows/phase8a-annual-pattern-catalogue.yml"
)
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "31633e87b79551f5b7dfa6b0deb76a82eb070129"
)

AUTHORIZED_ANNUAL_SEGMENT_LABEL = "2015"
EXPECTED_ANNUAL_WORKFLOW_RUN_NUMBER = 1
EXPECTED_ANNUAL_WORKFLOW_RUN_ATTEMPT = 1

ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED = True
HISTORICAL_ARTIFACT_READ_AUTHORIZED_FOR_2015 = True
HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED_FOR_2015 = True
HISTORICAL_RESULT_PRODUCTION_AUTHORIZED_FOR_2015 = True

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


def validate_2015_execution_authorization_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "execution_preflight_blob_sha": (
            root / EXECUTION_PREFLIGHT_SOURCE_PATH,
            EXPECTED_EXECUTION_PREFLIGHT_BLOB_SHA,
        ),
        "install_receipt_blob_sha": (
            root / INSTALL_RECEIPT_SOURCE_PATH,
            EXPECTED_INSTALL_RECEIPT_BLOB_SHA,
        ),
        "active_workflow_blob_sha": (
            root / ACTIVE_WORKFLOW_PATH,
            EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-493 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-493 {field} mismatch")
        actual[field] = sha
    return actual


def require_2015_execution_authorized(
    *,
    annual_segment_label: str,
    code_commit: str,
    run_number: int,
    run_attempt: int,
) -> None:
    _validate_commit(code_commit)
    if annual_segment_label != AUTHORIZED_ANNUAL_SEGMENT_LABEL:
        raise PermissionError(
            "DEC-493 authorizes annual catalogue execution only for 2015"
        )
    if _positive_int(run_number, field="run_number") != EXPECTED_ANNUAL_WORKFLOW_RUN_NUMBER:
        raise PermissionError(
            "DEC-493 authorizes only annual workflow run number 1"
        )
    if _positive_int(run_attempt, field="run_attempt") != EXPECTED_ANNUAL_WORKFLOW_RUN_ATTEMPT:
        raise PermissionError(
            "DEC-493 authorizes only annual workflow run attempt 1"
        )
    if not ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED:
        raise PermissionError("DEC-493 annual workflow dispatch remains locked")
    if not HISTORICAL_ARTIFACT_READ_AUTHORIZED_FOR_2015:
        raise PermissionError("DEC-493 2015 historical artifact reads remain locked")
    if not HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED_FOR_2015:
        raise PermissionError("DEC-493 2015 catalogue execution remains locked")
    if not HISTORICAL_RESULT_PRODUCTION_AUTHORIZED_FOR_2015:
        raise PermissionError("DEC-493 2015 result production remains locked")


def build_2015_execution_authorization(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_2015_execution_authorization_sources(
        repository_root=Path(repository_root),
    )
    return {
        "decision": ANNUAL_CATALOGUE_2015_EXECUTION_AUTHORIZATION_DECISION,
        "version": ANNUAL_CATALOGUE_2015_EXECUTION_AUTHORIZATION_VERSION,
        **source,
        "stage": "ANNUAL_CATALOGUE_2015_FIRST_RUN_AUTHORIZED_NOT_STARTED",
        "authorization_basis": "explicit_operator_authorization",
        "authorization_scope": "2015_run_1_attempt_1_only",
        "annual_segment_label": AUTHORIZED_ANNUAL_SEGMENT_LABEL,
        "expected_run_number": EXPECTED_ANNUAL_WORKFLOW_RUN_NUMBER,
        "expected_run_attempt": EXPECTED_ANNUAL_WORKFLOW_RUN_ATTEMPT,
        "previous_annual_freeze_run_id": None,
        "annual_workflow_dispatch_authorized": ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED,
        "historical_artifact_read_authorized": (
            HISTORICAL_ARTIFACT_READ_AUTHORIZED_FOR_2015
        ),
        "historical_catalogue_execution_authorized": (
            HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED_FOR_2015
        ),
        "historical_result_production_authorized": (
            HISTORICAL_RESULT_PRODUCTION_AUTHORIZED_FOR_2015
        ),
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
            "EXACT_FIRST_2015_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_"
            "DISPATCH_ON_CURRENT_MAIN"
        ),
    }


__all__ = [
    "ANNUAL_CATALOGUE_2015_EXECUTION_AUTHORIZATION_DECISION",
    "ANNUAL_CATALOGUE_2015_EXECUTION_AUTHORIZATION_VERSION",
    "ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED",
    "AUTHORIZED_ANNUAL_SEGMENT_LABEL",
    "EXPECTED_ANNUAL_WORKFLOW_RUN_ATTEMPT",
    "EXPECTED_ANNUAL_WORKFLOW_RUN_NUMBER",
    "build_2015_execution_authorization",
    "require_2015_execution_authorized",
    "validate_2015_execution_authorization_sources",
]
