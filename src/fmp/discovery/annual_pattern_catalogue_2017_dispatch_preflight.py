from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2017_runtime_authorization_install_receipt import (
    ANNUAL_CATALOGUE_2017_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_DECISION,
    ANNUAL_CATALOGUE_2017_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_VERSION,
    validate_2017_runtime_authorization_install_receipt,
)


ANNUAL_CATALOGUE_2017_DISPATCH_PREFLIGHT_DECISION = "DEC-540"
ANNUAL_CATALOGUE_2017_DISPATCH_PREFLIGHT_VERSION = (
    "fmp-annual-catalogue-2017-dispatch-preflight-v1"
)

INSTALL_RECEIPT_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_2017_runtime_authorization_install_receipt.py"
)
EXPECTED_INSTALL_RECEIPT_SOURCE_BLOB_SHA = (
    "c3662046efc7daf2c00637066aa78c885b85fa8e"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)
INSTALLED_GATE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2017_runtime_authorization.py"
)
EXPECTED_INSTALLED_GATE_BLOB_SHA = (
    "c1853eeec55ee98b3155a6054f07cf360793ba9b"
)
INSTALLED_RUNTIME_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
)
EXPECTED_INSTALLED_RUNTIME_BLOB_SHA = (
    "e9cbc76dc9e6866e80088d223498fbcc3b870fd1"
)

SOURCE_INSTALLER_WORKFLOW_RUN_ID = 37219929487
SOURCE_INSTALLER_WORKFLOW_HEAD_SHA = "9c3e2e6042b5a00109ee1f07ad6fd24c9ac33308"
SOURCE_INSTALL_ARTIFACT_ID = 11309927463
SOURCE_INSTALL_ARTIFACT_DIGEST = (
    "sha256:6672b0642a763424541d971d84b273f8c2fde5089fcd736e6152fe8dc9a7e32e"
)
SOURCE_INSTALL_COMMIT_SHA = "dcdf7210b0039077efa3a23c65c2ed8fa41e2427"

EXPECTED_RUN_NUMBER = 379
EXPECTED_RUN_ATTEMPT = 1
EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID = 37206992367

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
        raise ValueError(f"DEC-540 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-540 {field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-540 {field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-540 {field} must be hexadecimal") from exc
    return value.lower()


def validate_2017_dispatch_preflight_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "install_receipt_source_blob_sha": (
            root / INSTALL_RECEIPT_SOURCE_PATH,
            EXPECTED_INSTALL_RECEIPT_SOURCE_BLOB_SHA,
        ),
        "active_workflow_blob_sha": (
            root / ACTIVE_WORKFLOW_PATH,
            EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        ),
        "installed_gate_blob_sha": (
            root / INSTALLED_GATE_PATH,
            EXPECTED_INSTALLED_GATE_BLOB_SHA,
        ),
        "installed_runtime_blob_sha": (
            root / INSTALLED_RUNTIME_PATH,
            EXPECTED_INSTALLED_RUNTIME_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-540 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-540 {field} mismatch")
        actual[field] = sha

    if (
        ANNUAL_CATALOGUE_2017_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_DECISION
        != "DEC-539"
    ):
        raise ValueError("DEC-540 install receipt decision drift")
    if (
        ANNUAL_CATALOGUE_2017_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_VERSION
        != "fmp-annual-catalogue-2017-runtime-authorization-install-receipt-v1"
    ):
        raise ValueError("DEC-540 install receipt version drift")
    return actual


def _validate_annual_inventory(
    payload: Mapping[str, object],
) -> dict[str, object]:
    rows = payload.get("workflow_runs")
    if not isinstance(rows, list):
        raise ValueError("DEC-540 annual workflow_runs must be a list")
    if len(rows) != 4:
        raise ValueError("DEC-540 requires exactly four prior annual workflow runs")
    by_number: dict[int, Mapping[str, object]] = {}
    for raw in rows:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-540 annual run row malformed")
        number = raw.get("run_number")
        if not isinstance(number, int) or isinstance(number, bool):
            raise ValueError("DEC-540 annual run number malformed")
        if number in by_number:
            raise ValueError("DEC-540 duplicate annual run number")
        by_number[number] = raw
    if set(by_number) != {1, 376, 377, 378}:
        raise ValueError("DEC-540 annual run inventory mismatch")

    exact = {
        1: (
            37126711695,
            "fd85a886d07234ad584dcca08692b37e6af54b2e",
            "failure",
        ),
        376: (
            37191637168,
            "4c14fa7db6eb812b89ecb79201f7e298fa9c04f3",
            "failure",
        ),
        377: (
            37198002653,
            "a89db974be9a94481e7ed0990476bc661012f1e4",
            "success",
        ),
        378: (
            37206992367,
            "2524fde355349581c9440a172d0384c3cbce31ed",
            "success",
        ),
    }
    for number, (run_id, head_sha, conclusion) in exact.items():
        row = by_number[number]
        required = {
            "id": run_id,
            "name": "phase8a-annual-pattern-catalogue",
            "path": ACTIVE_WORKFLOW_PATH,
            "run_number": number,
            "run_attempt": 1,
            "event": "workflow_dispatch",
            "head_branch": "main",
            "head_sha": head_sha,
            "status": "completed",
            "conclusion": conclusion,
        }
        for field, expected in required.items():
            if row.get(field) != expected:
                raise ValueError(f"DEC-540 annual run {number} {field} mismatch")
    return {
        "annual_workflow_run_count": 4,
        "failed_run_1_id": 37126711695,
        "failed_run_376_id": 37191637168,
        "successful_2015_run_id": 37198002653,
        "successful_2016_run_id": 37206992367,
    }


def build_2017_dispatch_preflight(
    install_receipt: Mapping[str, object],
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    annual_workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2017_dispatch_preflight_sources(
        repository_root=Path(repository_root),
    )
    validate_2017_runtime_authorization_install_receipt(install_receipt)

    if install_receipt.get("install_commit_sha") != SOURCE_INSTALL_COMMIT_SHA:
        raise ValueError("DEC-540 source install commit mismatch")
    if install_receipt.get("expected_run_number") != EXPECTED_RUN_NUMBER:
        raise ValueError("DEC-540 source receipt run number mismatch")
    if install_receipt.get("expected_run_attempt") != EXPECTED_RUN_ATTEMPT:
        raise ValueError("DEC-540 source receipt run attempt mismatch")
    if (
        install_receipt.get("previous_annual_freeze_run_id")
        != EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID
    ):
        raise ValueError("DEC-540 source receipt predecessor mismatch")
    if install_receipt.get("runtime_authorization_installed") is not True:
        raise ValueError("DEC-540 runtime authorization is not installed")
    if install_receipt.get("runtime_gate_active") is not True:
        raise ValueError("DEC-540 runtime gate is not active")
    if install_receipt.get("annual_workflow_dispatch_authorized") is not False:
        raise ValueError("DEC-540 source receipt dispatch authority drift")

    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-540 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-540 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-540 current main head mismatch")

    inventory = _validate_annual_inventory(annual_workflow_runs)
    receipt_fingerprint = _sha256_hex(
        install_receipt.get("install_receipt_fingerprint_sha256"),
        field="install receipt fingerprint",
    )

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2017_DISPATCH_PREFLIGHT_DECISION,
        "version": ANNUAL_CATALOGUE_2017_DISPATCH_PREFLIGHT_VERSION,
        **source,
        **inventory,
        "source_install_receipt_decision": "DEC-539",
        "source_installer_workflow_run_id": SOURCE_INSTALLER_WORKFLOW_RUN_ID,
        "source_installer_workflow_head_sha": SOURCE_INSTALLER_WORKFLOW_HEAD_SHA,
        "source_install_artifact_id": SOURCE_INSTALL_ARTIFACT_ID,
        "source_install_artifact_digest": SOURCE_INSTALL_ARTIFACT_DIGEST,
        "source_install_commit_sha": SOURCE_INSTALL_COMMIT_SHA,
        "source_install_receipt_fingerprint_sha256": receipt_fingerprint,
        "stage": "ANNUAL_CATALOGUE_2017_DISPATCH_PREFLIGHT_READY",
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": expected_head_sha,
        "annual_segment_label": "2017",
        "previous_annual_freeze_run_id": EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID,
        "expected_run_number": EXPECTED_RUN_NUMBER,
        "expected_run_attempt": EXPECTED_RUN_ATTEMPT,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "dispatch_command_present": False,
        "preflight_read_only": True,
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
        "next_gate": "ANNUAL_PATTERN_CATALOGUE_2017_DISPATCH_AUTHORIZATION_BEFORE_RUN",
    }
    value["preflight_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    validate_2017_dispatch_preflight(value)
    return value


def validate_2017_dispatch_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _sha256_hex(
        value.get("preflight_fingerprint_sha256"),
        field="preflight fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("preflight_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-540 preflight fingerprint mismatch")

    exact = {
        "decision": "DEC-540",
        "version": "fmp-annual-catalogue-2017-dispatch-preflight-v1",
        "install_receipt_source_blob_sha": EXPECTED_INSTALL_RECEIPT_SOURCE_BLOB_SHA,
        "active_workflow_blob_sha": EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        "installed_gate_blob_sha": EXPECTED_INSTALLED_GATE_BLOB_SHA,
        "installed_runtime_blob_sha": EXPECTED_INSTALLED_RUNTIME_BLOB_SHA,
        "source_install_receipt_decision": "DEC-539",
        "source_installer_workflow_run_id": SOURCE_INSTALLER_WORKFLOW_RUN_ID,
        "source_installer_workflow_head_sha": SOURCE_INSTALLER_WORKFLOW_HEAD_SHA,
        "source_install_artifact_id": SOURCE_INSTALL_ARTIFACT_ID,
        "source_install_artifact_digest": SOURCE_INSTALL_ARTIFACT_DIGEST,
        "source_install_commit_sha": SOURCE_INSTALL_COMMIT_SHA,
        "stage": "ANNUAL_CATALOGUE_2017_DISPATCH_PREFLIGHT_READY",
        "repository_full_name": "Dtwosam/FMP",
        "annual_segment_label": "2017",
        "previous_annual_freeze_run_id": 37206992367,
        "expected_run_number": 379,
        "expected_run_attempt": 1,
        "annual_workflow_run_count": 4,
        "successful_2016_run_id": 37206992367,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "dispatch_command_present": False,
        "preflight_read_only": True,
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
        "next_gate": "ANNUAL_PATTERN_CATALOGUE_2017_DISPATCH_AUTHORIZATION_BEFORE_RUN",
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-540 {field} mismatch")
    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    _sha256_hex(
        value.get("source_install_receipt_fingerprint_sha256"),
        field="source install receipt fingerprint",
    )
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2017_DISPATCH_PREFLIGHT_DECISION",
    "ANNUAL_CATALOGUE_2017_DISPATCH_PREFLIGHT_VERSION",
    "build_2017_dispatch_preflight",
    "validate_2017_dispatch_preflight",
    "validate_2017_dispatch_preflight_sources",
]
