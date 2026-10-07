from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2022_runtime_authorization_install_receipt import (
    ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_DECISION,
    ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_VERSION,
    validate_2022_runtime_authorization_install_receipt,
)


ANNUAL_CATALOGUE_2022_DISPATCH_PREFLIGHT_DECISION = "DEC-597"
ANNUAL_CATALOGUE_2022_DISPATCH_PREFLIGHT_VERSION = (
    "fmp-annual-catalogue-2022-dispatch-preflight-v1"
)

INSTALL_RECEIPT_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_2022_runtime_authorization_install_receipt.py"
)
EXPECTED_INSTALL_RECEIPT_SOURCE_BLOB_SHA = (
    "8f7891820c91bcac1fec5627c7b93ee967ab3754"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)
INSTALLED_GATE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2022_runtime_authorization.py"
)
EXPECTED_INSTALLED_GATE_BLOB_SHA = (
    "ecb21dc7106e7bd43447f4135c3a696251a75e05"
)
INSTALLED_RUNTIME_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
)
EXPECTED_INSTALLED_RUNTIME_BLOB_SHA = (
    "f2734c7ea32355b1024d1097812578b23fc4409d"
)

SOURCE_INSTALLER_WORKFLOW_RUN_ID = 37635483891
SOURCE_INSTALLER_WORKFLOW_HEAD_SHA = "68bdb581a89247b0a2e5046fe9a30f086260e498"
SOURCE_INSTALL_ARTIFACT_ID = 11489650716
SOURCE_INSTALL_ARTIFACT_DIGEST = (
    "sha256:704fa463bbd6d23fea6a829be3db9d84b8789fb09df1dd924e526040e4d53112"
)
SOURCE_INSTALL_COMMIT_SHA = "df6da8cb52578c82e36c6206714a0452496614d9"
SOURCE_INSTALL_RECEIPT_FINGERPRINT_SHA256 = (
    "99e99b92f74776694bdfcaab2499587b36129f6c371ef87c1696e3ba4ad3ecfd"
)
SOURCE_INSTALL_RECEIPT_CANONICAL_SHA256 = (
    "79ebf56af148c5976734976e5332b3a16b314c8a42916223c771a3fd32b78de4"
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
        raise ValueError(f"DEC-597 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-597 {field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-597 {field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-597 {field} must be hexadecimal") from exc
    return value.lower()


def validate_2022_dispatch_preflight_sources(
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
    for field, (source_path, expected_sha) in expected.items():
        if not source_path.is_file():
            raise ValueError(f"DEC-597 source file missing: {source_path}")
        sha = _git_blob_sha(source_path)
        if sha != expected_sha:
            raise ValueError(f"DEC-597 {field} mismatch")
        actual[field] = sha

    if (
        ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_DECISION
        != "DEC-596"
    ):
        raise ValueError("DEC-597 install receipt decision drift")
    if (
        ANNUAL_CATALOGUE_2022_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_VERSION
        != "fmp-annual-catalogue-2022-runtime-authorization-install-receipt-v1"
    ):
        raise ValueError("DEC-597 install receipt version drift")
    return actual


def _validate_annual_inventory(
    payload: Mapping[str, object],
) -> dict[str, object]:
    rows = payload.get("workflow_runs")
    if not isinstance(rows, list):
        raise ValueError("DEC-597 annual workflow_runs must be a list")
    if len(rows) != 9:
        raise ValueError("DEC-597 requires exactly nine prior annual workflow runs")
    by_number: dict[int, Mapping[str, object]] = {}
    for raw in rows:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-597 annual run row malformed")
        number = raw.get("run_number")
        if not isinstance(number, int) or isinstance(number, bool):
            raise ValueError("DEC-597 annual run number malformed")
        if number in by_number:
            raise ValueError("DEC-597 duplicate annual run number")
        by_number[number] = raw
    if set(by_number) != {1, 376, 377, 378, 379, 380, 381, 382, 383}:
        raise ValueError("DEC-597 annual run inventory mismatch")

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
        379: (
            37227536041,
            "7b4c1ef8573e280c067443b72f1534d9091d5b7f",
            "success",
        ),
        380: (
            37237817538,
            "30971a996f514670a6f836d8e45cf80137197a4f",
            "success",
        ),
        381: (
            37310525635,
            "8bcee3a7a834743f08bd9ad73109bfc09609a2fe",
            "success",
        ),
        382: (
            37443770076,
            "681e81e021d4970a67b18370142d55b17ec68864",
            "success",
        ),
        383: (
            37531960014,
            "a1e194907c273a2fcdddfb4c24d64a96cfd8d263",
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
                raise ValueError(
                    f"DEC-597 annual run {number} {field} mismatch"
                )

    return {
        "annual_workflow_run_count": 9,
        "failed_run_1_id": 37126711695,
        "failed_run_376_id": 37191637168,
        "successful_2015_run_id": 37198002653,
        "successful_2016_run_id": 37206992367,
        "successful_2017_run_id": 37227536041,
        "successful_2018_run_id": 37237817538,
        "successful_2019_run_id": 37310525635,
        "successful_2020_run_id": 37443770076,
        "successful_2021_run_id": 37531960014,
    }


def build_2022_dispatch_preflight(
    install_receipt: Mapping[str, object],
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    annual_workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2022_dispatch_preflight_sources(
        repository_root=Path(repository_root),
    )
    validate_2022_runtime_authorization_install_receipt(install_receipt)

    if install_receipt.get("install_commit_sha") != SOURCE_INSTALL_COMMIT_SHA:
        raise ValueError("DEC-597 source install commit mismatch")
    if (
        install_receipt.get("install_receipt_fingerprint_sha256")
        != SOURCE_INSTALL_RECEIPT_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-597 source install receipt fingerprint mismatch")
    if install_receipt.get("expected_run_number") != EXPECTED_RUN_NUMBER:
        raise ValueError("DEC-597 source receipt run number mismatch")
    if install_receipt.get("expected_run_attempt") != EXPECTED_RUN_ATTEMPT:
        raise ValueError("DEC-597 source receipt run attempt mismatch")
    if (
        install_receipt.get("previous_annual_freeze_run_id")
        != EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID
    ):
        raise ValueError("DEC-597 source receipt predecessor mismatch")
    if install_receipt.get("runtime_authorization_installed") is not True:
        raise ValueError("DEC-597 runtime authorization is not installed")
    if install_receipt.get("runtime_gate_active") is not True:
        raise ValueError("DEC-597 runtime gate is not active")
    if install_receipt.get("annual_workflow_dispatch_authorized") is not False:
        raise ValueError("DEC-597 source receipt dispatch authority drift")
    for field in (
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
        if install_receipt.get(field) is not False:
            raise ValueError(f"DEC-597 source receipt {field} drift")

    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-597 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-597 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-597 current main head mismatch")

    inventory = _validate_annual_inventory(annual_workflow_runs)
    receipt_fingerprint = _sha256_hex(
        install_receipt.get("install_receipt_fingerprint_sha256"),
        field="install receipt fingerprint",
    )
    receipt_canonical_sha = _sha256_bytes(_canonical_json(dict(install_receipt)))
    if receipt_canonical_sha != SOURCE_INSTALL_RECEIPT_CANONICAL_SHA256:
        raise ValueError("DEC-597 source install receipt canonical SHA-256 mismatch")

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2022_DISPATCH_PREFLIGHT_DECISION,
        "version": ANNUAL_CATALOGUE_2022_DISPATCH_PREFLIGHT_VERSION,
        **source,
        **inventory,
        "source_install_receipt_decision": "DEC-596",
        "source_installer_workflow_run_id": SOURCE_INSTALLER_WORKFLOW_RUN_ID,
        "source_installer_workflow_head_sha": SOURCE_INSTALLER_WORKFLOW_HEAD_SHA,
        "source_install_artifact_id": SOURCE_INSTALL_ARTIFACT_ID,
        "source_install_artifact_digest": SOURCE_INSTALL_ARTIFACT_DIGEST,
        "source_install_commit_sha": SOURCE_INSTALL_COMMIT_SHA,
        "source_install_receipt_fingerprint_sha256": receipt_fingerprint,
        "source_install_receipt_canonical_sha256": receipt_canonical_sha,
        "stage": "ANNUAL_CATALOGUE_2022_DISPATCH_PREFLIGHT_READY",
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": expected_head_sha,
        "annual_segment_label": "2022",
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
        "next_gate": (
            "ANNUAL_PATTERN_CATALOGUE_2022_DISPATCH_AUTHORIZATION_BEFORE_RUN"
        ),
    }
    value["preflight_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    validate_2022_dispatch_preflight(value)
    return value


def validate_2022_dispatch_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _sha256_hex(
        value.get("preflight_fingerprint_sha256"),
        field="preflight fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("preflight_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-597 preflight fingerprint mismatch")

    exact = {
        "decision": "DEC-597",
        "version": "fmp-annual-catalogue-2022-dispatch-preflight-v1",
        "install_receipt_source_blob_sha": EXPECTED_INSTALL_RECEIPT_SOURCE_BLOB_SHA,
        "active_workflow_blob_sha": EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        "installed_gate_blob_sha": EXPECTED_INSTALLED_GATE_BLOB_SHA,
        "installed_runtime_blob_sha": EXPECTED_INSTALLED_RUNTIME_BLOB_SHA,
        "source_install_receipt_decision": "DEC-596",
        "source_installer_workflow_run_id": SOURCE_INSTALLER_WORKFLOW_RUN_ID,
        "source_installer_workflow_head_sha": SOURCE_INSTALLER_WORKFLOW_HEAD_SHA,
        "source_install_artifact_id": SOURCE_INSTALL_ARTIFACT_ID,
        "source_install_artifact_digest": SOURCE_INSTALL_ARTIFACT_DIGEST,
        "source_install_commit_sha": SOURCE_INSTALL_COMMIT_SHA,
        "source_install_receipt_fingerprint_sha256": (
            SOURCE_INSTALL_RECEIPT_FINGERPRINT_SHA256
        ),
        "source_install_receipt_canonical_sha256": SOURCE_INSTALL_RECEIPT_CANONICAL_SHA256,
        "stage": "ANNUAL_CATALOGUE_2022_DISPATCH_PREFLIGHT_READY",
        "repository_full_name": "Dtwosam/FMP",
        "annual_segment_label": "2022",
        "previous_annual_freeze_run_id": 37531960014,
        "expected_run_number": 384,
        "expected_run_attempt": 1,
        "annual_workflow_run_count": 9,
        "successful_2020_run_id": 37443770076,
        "successful_2021_run_id": 37531960014,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "dispatch_command_present": False,
        "preflight_read_only": True,
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
        "next_gate": (
            "ANNUAL_PATTERN_CATALOGUE_2022_DISPATCH_AUTHORIZATION_BEFORE_RUN"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-597 {field} mismatch")
    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2022_DISPATCH_PREFLIGHT_DECISION",
    "ANNUAL_CATALOGUE_2022_DISPATCH_PREFLIGHT_VERSION",
    "build_2022_dispatch_preflight",
    "validate_2022_dispatch_preflight",
    "validate_2022_dispatch_preflight_sources",
]
