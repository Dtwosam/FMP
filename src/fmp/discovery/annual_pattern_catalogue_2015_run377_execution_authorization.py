from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2015_run376_failure_receipt import (
    validate_2015_run376_failure_receipt,
)


ANNUAL_CATALOGUE_2015_RUN377_EXECUTION_AUTHORIZATION_DECISION = "DEC-527"
ANNUAL_CATALOGUE_2015_RUN377_EXECUTION_AUTHORIZATION_VERSION = (
    "fmp-annual-catalogue-2015-run377-execution-authorization-v1"
)

RUN376_FAILURE_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2015_run376_failure_receipt.py"
)
EXPECTED_RUN376_FAILURE_SOURCE_BLOB_SHA = (
    "b57b055129f57be1e3164c3b24a53bf5a0277a57"
)
CORRECTED_INSTALL_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_workflow_corrected_install_receipt.py"
)
EXPECTED_CORRECTED_INSTALL_SOURCE_BLOB_SHA = (
    "9c8237350484e3153f938a4df86d7f1c9955582e"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)

AUTHORIZED_ANNUAL_SEGMENT_LABEL = "2015"
EXPECTED_RUN_NUMBER = 377
EXPECTED_RUN_ATTEMPT = 1

HISTORICAL_ARTIFACT_READ_AUTHORIZED = True
HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED = True
HISTORICAL_RESULT_PRODUCTION_AUTHORIZED = True

RERUN_RUN376_AUTHORIZED = False
RETRY_RUN376_AUTHORIZED = False
RUN378_OR_LATER_AUTHORIZED = False
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
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def validate_2015_run377_execution_authorization_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "run376_failure_source_blob_sha": (
            root / RUN376_FAILURE_SOURCE_PATH,
            EXPECTED_RUN376_FAILURE_SOURCE_BLOB_SHA,
        ),
        "corrected_install_source_blob_sha": (
            root / CORRECTED_INSTALL_SOURCE_PATH,
            EXPECTED_CORRECTED_INSTALL_SOURCE_BLOB_SHA,
        ),
        "active_workflow_blob_sha": (
            root / ACTIVE_WORKFLOW_PATH,
            EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-527 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-527 {field} mismatch")
        actual[field] = sha
    return actual


def require_2015_run377_execution_authorized(
    *,
    annual_segment_label: str,
    code_commit: str,
    run_number: int,
    run_attempt: int,
) -> None:
    validate_2015_run377_execution_authorization_sources(
        repository_root=Path(".")
    )
    if annual_segment_label != AUTHORIZED_ANNUAL_SEGMENT_LABEL:
        raise PermissionError("DEC-527 authorizes only annual segment 2015")
    if not isinstance(code_commit, str) or len(code_commit) != 40:
        raise PermissionError("DEC-527 code commit is malformed")
    try:
        int(code_commit, 16)
    except ValueError as exc:
        raise PermissionError("DEC-527 code commit is malformed") from exc
    if run_number != EXPECTED_RUN_NUMBER:
        raise PermissionError("DEC-527 authorizes only workflow run 377")
    if run_attempt != EXPECTED_RUN_ATTEMPT:
        raise PermissionError("DEC-527 authorizes only workflow run attempt 1")
    if not HISTORICAL_ARTIFACT_READ_AUTHORIZED:
        raise PermissionError("DEC-527 historical reads remain locked")
    if not HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED:
        raise PermissionError("DEC-527 catalogue execution remains locked")
    if not HISTORICAL_RESULT_PRODUCTION_AUTHORIZED:
        raise PermissionError("DEC-527 result production remains locked")


def build_2015_run377_execution_authorization(
    *,
    repository_root: Path,
    run376_failure_receipt: Mapping[str, object],
) -> dict[str, object]:
    source = validate_2015_run377_execution_authorization_sources(
        repository_root=repository_root
    )
    validate_2015_run376_failure_receipt(run376_failure_receipt)
    if run376_failure_receipt.get("run_id") != 37191637168:
        raise ValueError("DEC-527 run376 failure receipt id mismatch")
    if run376_failure_receipt.get("run_number") != 376:
        raise ValueError("DEC-527 run376 failure receipt number mismatch")
    if run376_failure_receipt.get("run_attempt") != 1:
        raise ValueError("DEC-527 run376 failure receipt attempt mismatch")
    if run376_failure_receipt.get("run_conclusion") != "failure":
        raise ValueError("DEC-527 run376 failure receipt conclusion mismatch")
    return {
        "decision": ANNUAL_CATALOGUE_2015_RUN377_EXECUTION_AUTHORIZATION_DECISION,
        "version": ANNUAL_CATALOGUE_2015_RUN377_EXECUTION_AUTHORIZATION_VERSION,
        **source,
        "stage": "ANNUAL_CATALOGUE_2015_RUN377_AUTHORIZED_NOT_STARTED",
        "authorization_basis": "concrete_failed_run376_preflight_receipt",
        "source_failure_decision": "DEC-526",
        "source_failure_receipt_fingerprint_sha256": (
            run376_failure_receipt["receipt_fingerprint_sha256"]
        ),
        "failed_run_id": run376_failure_receipt["run_id"],
        "failed_run_number": run376_failure_receipt["run_number"],
        "failed_run_attempt": run376_failure_receipt["run_attempt"],
        "annual_segment_label": "2015",
        "expected_run_number": 377,
        "expected_run_attempt": 1,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "rerun_run376_authorized": False,
        "retry_run376_authorized": False,
        "run_378_or_later_authorized": False,
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
        "next_gate": "EXACT_2015_ANNUAL_PATTERN_CATALOGUE_RUN377_DISPATCH",
    }


__all__ = [
    "ANNUAL_CATALOGUE_2015_RUN377_EXECUTION_AUTHORIZATION_DECISION",
    "ANNUAL_CATALOGUE_2015_RUN377_EXECUTION_AUTHORIZATION_VERSION",
    "EXPECTED_RUN_ATTEMPT",
    "EXPECTED_RUN_NUMBER",
    "build_2015_run377_execution_authorization",
    "require_2015_run377_execution_authorized",
    "validate_2015_run377_execution_authorization_sources",
]
