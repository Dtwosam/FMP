from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping, Sequence

from .annual_pattern_catalogue_2022_runtime_authorization_install_action import (
    ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_ACTION_DECISION,
    ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_ACTION_VERSION,
    validate_2022_runtime_authorization_install_action,
)
from .annual_pattern_catalogue_2022_runtime_authorization_plan import (
    EXPECTED_DORMANT_2022_GATE_TEMPLATE_BLOB_SHA,
    EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA,
    TARGET_2022_GATE_SOURCE_PATH,
    TARGET_RUNTIME_SOURCE_PATH,
)


ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_DECISION = "DEC-596"
ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_VERSION = (
    "fmp-annual-catalogue-2022-runtime-authorization-install-receipt-v1"
)

INSTALL_ACTION_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_2022_runtime_authorization_install_action.py"
)
EXPECTED_INSTALL_ACTION_SOURCE_BLOB_SHA = (
    "90fbc26b51d50d019e39c467d461bd7ba6b4f22b"
)

SOURCE_ACTION_WORKFLOW_RUN_ID = 37618517412
SOURCE_ACTION_WORKFLOW_HEAD_SHA = "1351125bb903f7d7b636d945c4446ad815a2efb1"
SOURCE_ACTION_ARTIFACT_ID = 11480463531
SOURCE_ACTION_ARTIFACT_DIGEST = (
    "sha256:6ff7996ac313a5437c0862cf58931a1246c5caf85251a6df4e0829602d9c07e8"
)
SOURCE_ACTION_FINGERPRINT_SHA256 = (
    "3352e4254ce62247d56c9fd16c9eb6972c3c7210dce7e08d6582f4c46c5e4a51"
)
SOURCE_ACTION_CANONICAL_SHA256 = (
    "2b99a8b914ee01d27902daa626d2ca01e31384e17de1b3a63b99fcbb1c90070c"
)


EXPECTED_RUN_NUMBER = 384
EXPECTED_RUN_ATTEMPT = 1
EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID = 37531960014

ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED = False
HISTORICAL_ARTIFACT_READ_AUTHORIZED = False
HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED = False
HISTORICAL_RESULT_PRODUCTION_AUTHORIZED = False
RERUN_AUTHORIZED = False
RETRY_AUTHORIZED = False
REPLACEMENT_RUN_AUTHORIZED = False
RUN_385_OR_LATER_AUTHORIZED = False
NEXT_SEGMENT_EXECUTION_AUTHORIZED = False
PROTECTED_HISTORY_ACCESS_AUTHORIZED = False
CROSS_YEAR_COMPARISON_AUTHORIZED = False
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
        raise ValueError(f"DEC-596 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-596 {field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-596 {field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-596 {field} must be hexadecimal") from exc
    return value.lower()


def validate_2022_runtime_authorization_install_receipt_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    source_path = root / INSTALL_ACTION_SOURCE_PATH
    if not source_path.is_file():
        raise ValueError(f"DEC-596 source file missing: {source_path}")
    sha = _git_blob_sha(source_path)
    if sha != EXPECTED_INSTALL_ACTION_SOURCE_BLOB_SHA:
        raise ValueError("DEC-596 install action source blob mismatch")
    if ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_ACTION_DECISION != "DEC-595":
        raise ValueError("DEC-596 install action decision drift")
    if (
        ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_ACTION_VERSION
        != "fmp-annual-catalogue-2022-runtime-authorization-install-action-v1"
    ):
        raise ValueError("DEC-596 install action version drift")
    return {"install_action_source_blob_sha": sha}


def review_2022_runtime_authorization_install(
    install_action: Mapping[str, object],
    *,
    repository_root: Path,
    install_commit_sha: str,
    changed_files: Sequence[str],
    installed_gate_blob_sha: str,
    installed_runtime_blob_sha: str,
) -> dict[str, object]:
    source = validate_2022_runtime_authorization_install_receipt_sources(
        repository_root=Path(repository_root),
    )
    validate_2022_runtime_authorization_install_action(install_action)

    install_commit_sha = _validate_commit(
        install_commit_sha,
        field="install_commit_sha",
    )
    expected_files = [TARGET_2022_GATE_SOURCE_PATH, TARGET_RUNTIME_SOURCE_PATH]
    if list(changed_files) != expected_files:
        raise ValueError("DEC-596 installed changed-file inventory mismatch")
    if installed_gate_blob_sha != EXPECTED_DORMANT_2022_GATE_TEMPLATE_BLOB_SHA:
        raise ValueError("DEC-596 installed 2022 gate blob mismatch")
    if installed_runtime_blob_sha != EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA:
        raise ValueError("DEC-596 installed runtime blob mismatch")

    if install_action.get("expected_run_number") != EXPECTED_RUN_NUMBER:
        raise ValueError("DEC-596 action run number mismatch")
    if install_action.get("expected_run_attempt") != EXPECTED_RUN_ATTEMPT:
        raise ValueError("DEC-596 action run attempt mismatch")
    if (
        install_action.get("previous_annual_freeze_run_id")
        != EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID
    ):
        raise ValueError("DEC-596 action predecessor mismatch")

    action_fingerprint = _sha256_hex(
        install_action.get("install_action_fingerprint_sha256"),
        field="install action fingerprint",
    )
    if action_fingerprint != SOURCE_ACTION_FINGERPRINT_SHA256:
        raise ValueError("DEC-596 source action fingerprint mismatch")
    action_canonical_sha = _sha256_bytes(_canonical_json(dict(install_action)))
    if action_canonical_sha != SOURCE_ACTION_CANONICAL_SHA256:
        raise ValueError("DEC-596 source action canonical SHA-256 mismatch")
    if install_action.get("repository_mutation_authorized") is not True:
        raise ValueError("DEC-596 source action mutation authority missing")
    for field in (
        "runtime_authorization_installed",
        "runtime_gate_active",
        "annual_workflow_dispatch_authorized",
        "historical_artifact_read_authorized",
        "historical_catalogue_execution_authorized",
        "historical_result_production_authorized",
        "rerun_authorized",
        "retry_authorized",
        "replacement_run_authorized",
        "run_385_or_later_authorized",
        "next_segment_execution_authorized",
        "protected_history_access_authorized",
        "cross_year_comparison_authorized",
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
        if install_action.get(field) is not False:
            raise ValueError(f"DEC-596 source action {field} drift")

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_DECISION,
        "version": ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_VERSION,
        **source,
        "source_action_decision": "DEC-595",
        "source_action_workflow_run_id": SOURCE_ACTION_WORKFLOW_RUN_ID,
        "source_action_workflow_head_sha": SOURCE_ACTION_WORKFLOW_HEAD_SHA,
        "source_action_artifact_id": SOURCE_ACTION_ARTIFACT_ID,
        "source_action_artifact_digest": SOURCE_ACTION_ARTIFACT_DIGEST,
        "source_action_fingerprint_sha256": action_fingerprint,
        "source_action_canonical_sha256": action_canonical_sha,
        "stage": "ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALLED",
        "repository_full_name": "Dtwosam/FMP",
        "install_commit_sha": install_commit_sha,
        "annual_segment_label": "2022",
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
        "rerun_authorized": RERUN_AUTHORIZED,
        "retry_authorized": RETRY_AUTHORIZED,
        "replacement_run_authorized": REPLACEMENT_RUN_AUTHORIZED,
        "run_385_or_later_authorized": RUN_385_OR_LATER_AUTHORIZED,
        "next_segment_execution_authorized": NEXT_SEGMENT_EXECUTION_AUTHORIZED,
        "protected_history_access_authorized": PROTECTED_HISTORY_ACCESS_AUTHORIZED,
        "cross_year_comparison_authorized": CROSS_YEAR_COMPARISON_AUTHORIZED,
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
        "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2022_DISPATCH_PREFLIGHT",
    }
    value["install_receipt_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    validate_2022_runtime_authorization_install_receipt(value)
    return value


def validate_2022_runtime_authorization_install_receipt(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _sha256_hex(
        value.get("install_receipt_fingerprint_sha256"),
        field="install receipt fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("install_receipt_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-596 install receipt fingerprint mismatch")

    exact = {
        "decision": "DEC-596",
        "version": "fmp-annual-catalogue-2022-runtime-authorization-install-receipt-v1",
        "install_action_source_blob_sha": EXPECTED_INSTALL_ACTION_SOURCE_BLOB_SHA,
        "source_action_decision": "DEC-595",
        "source_action_workflow_run_id": SOURCE_ACTION_WORKFLOW_RUN_ID,
        "source_action_workflow_head_sha": SOURCE_ACTION_WORKFLOW_HEAD_SHA,
        "source_action_artifact_id": SOURCE_ACTION_ARTIFACT_ID,
        "source_action_artifact_digest": SOURCE_ACTION_ARTIFACT_DIGEST,
        "source_action_fingerprint_sha256": SOURCE_ACTION_FINGERPRINT_SHA256,
        "source_action_canonical_sha256": SOURCE_ACTION_CANONICAL_SHA256,
        "stage": "ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALLED",
        "repository_full_name": "Dtwosam/FMP",
        "annual_segment_label": "2022",
        "expected_run_number": 384,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": 37531960014,
        "changed_files": [TARGET_2022_GATE_SOURCE_PATH, TARGET_RUNTIME_SOURCE_PATH],
        "installed_gate_blob_sha": EXPECTED_DORMANT_2022_GATE_TEMPLATE_BLOB_SHA,
        "installed_runtime_blob_sha": EXPECTED_DORMANT_RUNTIME_TARGET_TEMPLATE_BLOB_SHA,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "install_action_consumed": True,
        "annual_workflow_dispatch_authorized": False,
        "historical_artifact_read_authorized": False,
        "historical_catalogue_execution_authorized": False,
        "historical_result_production_authorized": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "run_385_or_later_authorized": False,
        "next_segment_execution_authorized": False,
        "protected_history_access_authorized": False,
        "cross_year_comparison_authorized": False,
        "cross_year_result_production_authorized": False,
        "strategy_v1_synthesis_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "next_gate": "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_2022_DISPATCH_PREFLIGHT",
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-596 {field} mismatch")
    _validate_commit(value.get("install_commit_sha"), field="install_commit_sha")
    _sha256_hex(
        value.get("source_action_fingerprint_sha256"),
        field="source action fingerprint",
    )
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_DECISION",
    "ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_VERSION",
    "review_2022_runtime_authorization_install",
    "validate_2022_runtime_authorization_install_receipt",
    "validate_2022_runtime_authorization_install_receipt_sources",
]
