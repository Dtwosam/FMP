from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping, Sequence

from .annual_pattern_catalogue_2020_runtime_authorization_install_action import (
    ANNUAL_CATALOGUE_2020_RUNTIME_AUTHORIZATION_INSTALL_ACTION_DECISION,
    ANNUAL_CATALOGUE_2020_RUNTIME_AUTHORIZATION_INSTALL_ACTION_VERSION,
    validate_2020_runtime_authorization_install_action,
)
from .annual_pattern_catalogue_2020_runtime_authorization_plan import (
    EXPECTED_DORMANT_2020_GATE_TEMPLATE_BLOB_SHA,
    EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA,
    TARGET_2020_GATE_SOURCE_PATH,
    TARGET_RUNTIME_SOURCE_PATH,
)


ANNUAL_CATALOGUE_2020_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_DECISION = "DEC-572"
ANNUAL_CATALOGUE_2020_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_VERSION = (
    "fmp-annual-catalogue-2020-runtime-authorization-install-receipt-v1"
)

INSTALL_ACTION_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_2020_runtime_authorization_install_action.py"
)
EXPECTED_INSTALL_ACTION_SOURCE_BLOB_SHA = (
    "98043c92240d00a343087e4d5fcef56575ba319e"
)

SOURCE_ACTION_WORKFLOW_RUN_ID = 37327905209
SOURCE_ACTION_WORKFLOW_HEAD_SHA = "4ed1da1cdc5a8df1272fb1f06a803a57a8043427"
SOURCE_ACTION_ARTIFACT_ID = 11352259131
SOURCE_ACTION_ARTIFACT_DIGEST = (
    "sha256:082c09ed64042f2c63252676be1d63aab6553c3cd92e3995256498ac4744b423"
)
SOURCE_ACTION_FINGERPRINT_SHA256 = (
    "0d617a5261a25d1fbdcc661fcc9518be63081ca442fb2ac068a2206f875e6939"
)

EXPECTED_RUN_NUMBER = 382
EXPECTED_RUN_ATTEMPT = 1
EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID = 37310525635

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
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_hex(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"DEC-572 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-572 {field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-572 {field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-572 {field} must be hexadecimal") from exc
    return value.lower()


def validate_2020_runtime_authorization_install_receipt_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    source_path = root / INSTALL_ACTION_SOURCE_PATH
    if not source_path.is_file():
        raise ValueError(f"DEC-572 source file missing: {source_path}")
    sha = _git_blob_sha(source_path)
    if sha != EXPECTED_INSTALL_ACTION_SOURCE_BLOB_SHA:
        raise ValueError("DEC-572 install action source blob mismatch")
    if ANNUAL_CATALOGUE_2020_RUNTIME_AUTHORIZATION_INSTALL_ACTION_DECISION != "DEC-571":
        raise ValueError("DEC-572 install action decision drift")
    if (
        ANNUAL_CATALOGUE_2020_RUNTIME_AUTHORIZATION_INSTALL_ACTION_VERSION
        != "fmp-annual-catalogue-2020-runtime-authorization-install-action-v1"
    ):
        raise ValueError("DEC-572 install action version drift")
    return {"install_action_source_blob_sha": sha}


def review_2020_runtime_authorization_install(
    install_action: Mapping[str, object],
    *,
    repository_root: Path,
    install_commit_sha: str,
    changed_files: Sequence[str],
    installed_gate_blob_sha: str,
    installed_runtime_blob_sha: str,
) -> dict[str, object]:
    source = validate_2020_runtime_authorization_install_receipt_sources(
        repository_root=Path(repository_root),
    )
    validate_2020_runtime_authorization_install_action(install_action)

    install_commit_sha = _validate_commit(
        install_commit_sha,
        field="install_commit_sha",
    )
    expected_files = [TARGET_2020_GATE_SOURCE_PATH, TARGET_RUNTIME_SOURCE_PATH]
    if list(changed_files) != expected_files:
        raise ValueError("DEC-572 installed changed-file inventory mismatch")
    if installed_gate_blob_sha != EXPECTED_DORMANT_2020_GATE_TEMPLATE_BLOB_SHA:
        raise ValueError("DEC-572 installed 2020 gate blob mismatch")
    if installed_runtime_blob_sha != EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA:
        raise ValueError("DEC-572 installed runtime blob mismatch")

    if install_action.get("expected_run_number") != EXPECTED_RUN_NUMBER:
        raise ValueError("DEC-572 action run number mismatch")
    if install_action.get("expected_run_attempt") != EXPECTED_RUN_ATTEMPT:
        raise ValueError("DEC-572 action run attempt mismatch")
    if (
        install_action.get("previous_annual_freeze_run_id")
        != EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID
    ):
        raise ValueError("DEC-572 action predecessor mismatch")

    action_fingerprint = _sha256_hex(
        install_action.get("install_action_fingerprint_sha256"),
        field="install action fingerprint",
    )
    if action_fingerprint != SOURCE_ACTION_FINGERPRINT_SHA256:
        raise ValueError("DEC-572 source action fingerprint mismatch")

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2020_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_DECISION,
        "version": ANNUAL_CATALOGUE_2020_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_VERSION,
        **source,
        "source_action_decision": "DEC-571",
        "source_action_workflow_run_id": SOURCE_ACTION_WORKFLOW_RUN_ID,
        "source_action_workflow_head_sha": SOURCE_ACTION_WORKFLOW_HEAD_SHA,
        "source_action_artifact_id": SOURCE_ACTION_ARTIFACT_ID,
        "source_action_artifact_digest": SOURCE_ACTION_ARTIFACT_DIGEST,
        "source_action_fingerprint_sha256": action_fingerprint,
        "stage": "ANNUAL_CATALOGUE_2020_RUNTIME_AUTHORIZATION_INSTALLED",
        "repository_full_name": "Dtwosam/FMP",
        "install_commit_sha": install_commit_sha,
        "annual_segment_label": "2020",
        "expected_run_number": EXPECTED_RUN_NUMBER,
        "expected_run_attempt": EXPECTED_RUN_ATTEMPT,
        "previous_annual_freeze_run_id": EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID,
        "changed_files": expected_files,
        "installed_gate_blob_sha": installed_gate_blob_sha,
        "installed_runtime_blob_sha": installed_runtime_blob_sha,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "install_action_consumed": True,
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
        "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2020_DISPATCH_PREFLIGHT",
    }
    value["install_receipt_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    validate_2020_runtime_authorization_install_receipt(value)
    return value


def validate_2020_runtime_authorization_install_receipt(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _sha256_hex(
        value.get("install_receipt_fingerprint_sha256"),
        field="install receipt fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("install_receipt_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-572 install receipt fingerprint mismatch")

    exact = {
        "decision": "DEC-572",
        "version": "fmp-annual-catalogue-2020-runtime-authorization-install-receipt-v1",
        "install_action_source_blob_sha": EXPECTED_INSTALL_ACTION_SOURCE_BLOB_SHA,
        "source_action_decision": "DEC-571",
        "source_action_workflow_run_id": SOURCE_ACTION_WORKFLOW_RUN_ID,
        "source_action_workflow_head_sha": SOURCE_ACTION_WORKFLOW_HEAD_SHA,
        "source_action_artifact_id": SOURCE_ACTION_ARTIFACT_ID,
        "source_action_artifact_digest": SOURCE_ACTION_ARTIFACT_DIGEST,
        "source_action_fingerprint_sha256": SOURCE_ACTION_FINGERPRINT_SHA256,
        "stage": "ANNUAL_CATALOGUE_2020_RUNTIME_AUTHORIZATION_INSTALLED",
        "repository_full_name": "Dtwosam/FMP",
        "annual_segment_label": "2020",
        "expected_run_number": 382,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": 37310525635,
        "changed_files": [TARGET_2020_GATE_SOURCE_PATH, TARGET_RUNTIME_SOURCE_PATH],
        "installed_gate_blob_sha": EXPECTED_DORMANT_2020_GATE_TEMPLATE_BLOB_SHA,
        "installed_runtime_blob_sha": EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "install_action_consumed": True,
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
        "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2020_DISPATCH_PREFLIGHT",
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-572 {field} mismatch")
    _validate_commit(value.get("install_commit_sha"), field="install_commit_sha")
    _sha256_hex(
        value.get("source_action_fingerprint_sha256"),
        field="source action fingerprint",
    )
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2020_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_DECISION",
    "ANNUAL_CATALOGUE_2020_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_VERSION",
    "review_2020_runtime_authorization_install",
    "validate_2020_runtime_authorization_install_receipt",
    "validate_2020_runtime_authorization_install_receipt_sources",
]
