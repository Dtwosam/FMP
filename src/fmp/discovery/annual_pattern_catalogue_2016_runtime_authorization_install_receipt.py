from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping, Sequence

from .annual_pattern_catalogue_2016_runtime_authorization_install_action import (
    ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_ACTION_DECISION,
    ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_ACTION_VERSION,
    validate_2016_runtime_authorization_install_action,
)
from .annual_pattern_catalogue_2016_runtime_authorization_plan import (
    EXPECTED_DORMANT_2016_GATE_TEMPLATE_BLOB_SHA,
    EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA,
    TARGET_2016_GATE_SOURCE_PATH,
    TARGET_RUNTIME_SOURCE_PATH,
)


ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_DECISION = "DEC-508"
ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_VERSION = (
    "fmp-annual-catalogue-2016-runtime-authorization-install-receipt-v1"
)

INSTALL_ACTION_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_2016_runtime_authorization_install_action.py"
)
EXPECTED_INSTALL_ACTION_SOURCE_BLOB_SHA = (
    "6046f07bb39518cfcce3ef11ebcb266ad8d8cab5"
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


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_hex(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"DEC-508 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-508 {field} must be hexadecimal") from exc
    return value.lower()


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"DEC-508 {field} must be a positive integer")
    return value


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-508 {field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-508 {field} must be hexadecimal") from exc
    return value.lower()


def validate_2016_runtime_authorization_install_receipt_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    path = root / INSTALL_ACTION_SOURCE_PATH
    if not path.is_file():
        raise ValueError(f"DEC-508 source file missing: {path}")
    sha = _git_blob_sha(path)
    if sha != EXPECTED_INSTALL_ACTION_SOURCE_BLOB_SHA:
        raise ValueError("DEC-508 install action source blob mismatch")

    if ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_ACTION_DECISION != "DEC-507":
        raise ValueError("DEC-508 install action decision drift")
    if (
        ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_ACTION_VERSION
        != "fmp-annual-catalogue-2016-runtime-authorization-install-action-v1"
    ):
        raise ValueError("DEC-508 install action version drift")

    return {"install_action_source_blob_sha": sha}


def review_2016_runtime_authorization_install(
    install_action: Mapping[str, object],
    *,
    repository_root: Path,
    install_commit_sha: str,
    changed_files: Sequence[str],
    installed_gate_blob_sha: str,
    installed_runtime_blob_sha: str,
) -> dict[str, object]:
    source = validate_2016_runtime_authorization_install_receipt_sources(
        repository_root=Path(repository_root),
    )
    validate_2016_runtime_authorization_install_action(install_action)

    install_commit_sha = _validate_commit(
        install_commit_sha,
        field="install_commit_sha",
    )
    expected_files = [
        TARGET_2016_GATE_SOURCE_PATH,
        TARGET_RUNTIME_SOURCE_PATH,
    ]
    if list(changed_files) != expected_files:
        raise ValueError("DEC-508 installed changed-file inventory mismatch")
    if installed_gate_blob_sha != EXPECTED_DORMANT_2016_GATE_TEMPLATE_BLOB_SHA:
        raise ValueError("DEC-508 installed 2016 gate blob mismatch")
    if installed_runtime_blob_sha != EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA:
        raise ValueError("DEC-508 installed runtime blob mismatch")

    action_fingerprint = _sha256_hex(
        install_action.get("install_action_fingerprint_sha256"),
        field="install action fingerprint",
    )

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_DECISION,
        "version": ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_VERSION,
        **source,
        "source_action_decision": "DEC-507",
        "source_action_fingerprint_sha256": action_fingerprint,
        "stage": "ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALLED_DISPATCH_LOCKED",
        "repository_full_name": "Dtwosam/FMP",
        "install_commit_sha": install_commit_sha,
        "annual_segment_label": "2016",
        "expected_run_number": 377,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": _positive_int(
            install_action.get("previous_annual_freeze_run_id"),
            field="previous annual freeze run id",
        ),
        "changed_file_count": 2,
        "changed_files": expected_files,
        "installed_gate_source_path": TARGET_2016_GATE_SOURCE_PATH,
        "installed_gate_source_blob_sha": installed_gate_blob_sha,
        "installed_runtime_source_path": TARGET_RUNTIME_SOURCE_PATH,
        "installed_runtime_source_blob_sha": installed_runtime_blob_sha,
        "install_action_consumed": True,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "annual_workflow_dispatch_authorized": (
            ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED
        ),
        "historical_artifact_read_authorized": (
            HISTORICAL_ARTIFACT_READ_AUTHORIZED
        ),
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
        "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2016_DISPATCH_PREFLIGHT",
    }
    value["receipt_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    validate_2016_runtime_authorization_install_receipt(value)
    return value


def validate_2016_runtime_authorization_install_receipt(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _sha256_hex(
        value.get("receipt_fingerprint_sha256"),
        field="receipt fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("receipt_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-508 receipt fingerprint mismatch")

    if value.get("decision") != "DEC-508":
        raise ValueError("DEC-508 decision mismatch")
    if value.get("source_action_decision") != "DEC-507":
        raise ValueError("DEC-508 source action mismatch")
    if value.get("install_action_source_blob_sha") != EXPECTED_INSTALL_ACTION_SOURCE_BLOB_SHA:
        raise ValueError("DEC-508 install action source blob mismatch")
    _sha256_hex(
        value.get("source_action_fingerprint_sha256"),
        field="source action fingerprint",
    )
    if value.get("annual_segment_label") != "2016":
        raise ValueError("DEC-508 annual segment mismatch")
    if value.get("expected_run_number") != 377:
        raise ValueError("DEC-508 expected run number mismatch")
    if value.get("expected_run_attempt") != 1:
        raise ValueError("DEC-508 expected run attempt mismatch")
    _positive_int(
        value.get("previous_annual_freeze_run_id"),
        field="previous annual freeze run id",
    )
    _validate_commit(value.get("install_commit_sha"), field="install_commit_sha")
    if value.get("repository_full_name") != "Dtwosam/FMP":
        raise ValueError("DEC-508 repository mismatch")
    if value.get("stage") != "ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALLED_DISPATCH_LOCKED":
        raise ValueError("DEC-508 stage mismatch")

    if value.get("changed_file_count") != 2:
        raise ValueError("DEC-508 changed file count mismatch")
    if value.get("installed_gate_source_path") != TARGET_2016_GATE_SOURCE_PATH:
        raise ValueError("DEC-508 installed gate path mismatch")
    if value.get("installed_runtime_source_path") != TARGET_RUNTIME_SOURCE_PATH:
        raise ValueError("DEC-508 installed runtime path mismatch")
    if value.get("changed_files") != [
        TARGET_2016_GATE_SOURCE_PATH,
        TARGET_RUNTIME_SOURCE_PATH,
    ]:
        raise ValueError("DEC-508 changed files mismatch")
    if (
        value.get("installed_gate_source_blob_sha")
        != EXPECTED_DORMANT_2016_GATE_TEMPLATE_BLOB_SHA
    ):
        raise ValueError("DEC-508 installed gate blob mismatch")
    if (
        value.get("installed_runtime_source_blob_sha")
        != EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA
    ):
        raise ValueError("DEC-508 installed runtime blob mismatch")

    if value.get("install_action_consumed") is not True:
        raise ValueError("DEC-508 install action must be consumed")
    if value.get("runtime_authorization_installed") is not True:
        raise ValueError("DEC-508 runtime authorization must be installed")
    if value.get("runtime_gate_active") is not True:
        raise ValueError("DEC-508 runtime gate must be active")

    for field in (
        "annual_workflow_dispatch_authorized",
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
    ):
        if value.get(field) is not False:
            raise ValueError(f"DEC-508 {field} must remain false")

    if (
        value.get("next_gate")
        != "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2016_DISPATCH_PREFLIGHT"
    ):
        raise ValueError("DEC-508 next gate mismatch")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_DECISION",
    "ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_VERSION",
    "review_2016_runtime_authorization_install",
    "validate_2016_runtime_authorization_install_receipt",
    "validate_2016_runtime_authorization_install_receipt_sources",
]
