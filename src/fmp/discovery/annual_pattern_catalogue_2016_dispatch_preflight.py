from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2015_runtime_evidence_binding import (
    validate_2015_runtime_evidence_binding,
)
from .annual_pattern_catalogue_2016_runtime_authorization_install_receipt import (
    ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_DECISION,
    ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_VERSION,
    validate_2016_runtime_authorization_install_receipt,
)


ANNUAL_CATALOGUE_2016_DISPATCH_PREFLIGHT_DECISION = "DEC-509"
ANNUAL_CATALOGUE_2016_DISPATCH_PREFLIGHT_VERSION = (
    "fmp-annual-catalogue-2016-dispatch-preflight-v1"
)

INSTALL_RECEIPT_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_2016_runtime_authorization_install_receipt.py"
)
EXPECTED_INSTALL_RECEIPT_SOURCE_BLOB_SHA = (
    "7da956910e24e788a2f2a60834c04048a660bc75"
)
RUNTIME_BINDING_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2015_runtime_evidence_binding.py"
)
EXPECTED_RUNTIME_BINDING_SOURCE_BLOB_SHA = (
    "bbb3bba32c3677d3bd971a2744eb93498868433b"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)

FAILED_FIRST_RUN_ID = 37126711695
FAILED_FIRST_RUN_HEAD_SHA = "fd85a886d07234ad584dcca08692b37e6af54b2e"

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


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-509 {field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-509 {field} must be hexadecimal") from exc
    return value.lower()


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"DEC-509 {field} must be a positive integer")
    return value


def _sha256_hex(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"DEC-509 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-509 {field} must be hexadecimal") from exc
    return value.lower()


def validate_2016_dispatch_preflight_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "install_receipt_source_blob_sha": (
            root / INSTALL_RECEIPT_SOURCE_PATH,
            EXPECTED_INSTALL_RECEIPT_SOURCE_BLOB_SHA,
        ),
        "runtime_binding_source_blob_sha": (
            root / RUNTIME_BINDING_SOURCE_PATH,
            EXPECTED_RUNTIME_BINDING_SOURCE_BLOB_SHA,
        ),
        "active_workflow_blob_sha": (
            root / ACTIVE_WORKFLOW_PATH,
            EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-509 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-509 {field} mismatch")
        actual[field] = sha

    if (
        ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_DECISION
        != "DEC-508"
    ):
        raise ValueError("DEC-509 install receipt decision drift")
    if (
        ANNUAL_CATALOGUE_2016_RUNTIME_AUTHORIZATION_INSTALL_RECEIPT_VERSION
        != "fmp-annual-catalogue-2016-runtime-authorization-install-receipt-v1"
    ):
        raise ValueError("DEC-509 install receipt version drift")
    return actual


def _validate_run_inventory(
    value: Mapping[str, object],
    *,
    runtime_binding: Mapping[str, object],
) -> dict[str, object]:
    runs = value.get("workflow_runs")
    if not isinstance(runs, list) or len(runs) != 2:
        raise ValueError(
            "DEC-509 requires exactly two prior annual-catalogue workflow runs"
        )

    by_number: dict[int, Mapping[str, object]] = {}
    for raw in runs:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-509 workflow run row malformed")
        number = raw.get("run_number")
        if not isinstance(number, int) or isinstance(number, bool):
            raise ValueError("DEC-509 workflow run number malformed")
        if number in by_number:
            raise ValueError("DEC-509 duplicate workflow run number")
        by_number[number] = raw

    if set(by_number) != {1, 376}:
        raise ValueError("DEC-509 workflow run number inventory mismatch")

    first = by_number[1]
    first_exact = {
        "id": FAILED_FIRST_RUN_ID,
        "run_number": 1,
        "run_attempt": 1,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": FAILED_FIRST_RUN_HEAD_SHA,
        "status": "completed",
        "conclusion": "failure",
    }
    for field, expected in first_exact.items():
        if first.get(field) != expected:
            raise ValueError(f"DEC-509 failed first run {field} mismatch")

    second = by_number[376]
    second_exact = {
        "id": runtime_binding.get("run_id"),
        "run_number": 376,
        "run_attempt": 1,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": runtime_binding.get("run_head_sha"),
        "status": "completed",
        "conclusion": "success",
    }
    for field, expected in second_exact.items():
        if second.get(field) != expected:
            raise ValueError(f"DEC-509 successful 2015 run {field} mismatch")

    return {
        "annual_workflow_run_count": 2,
        "failed_first_run_id": FAILED_FIRST_RUN_ID,
        "successful_2015_run_id": _positive_int(
            runtime_binding.get("run_id"),
            field="successful 2015 run id",
        ),
        "successful_2015_run_number": 376,
        "successful_2015_run_attempt": 1,
        "successful_2015_run_head_sha": _validate_commit(
            runtime_binding.get("run_head_sha"),
            field="successful 2015 run head",
        ),
    }


def build_2016_dispatch_preflight(
    *,
    repository_root: Path,
    install_receipt: Mapping[str, object],
    runtime_binding: Mapping[str, object],
    main_branch: Mapping[str, object],
    annual_workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2016_dispatch_preflight_sources(
        repository_root=Path(repository_root),
    )
    validate_2016_runtime_authorization_install_receipt(install_receipt)
    validate_2015_runtime_evidence_binding(runtime_binding)

    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-509 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-509 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-509 main head mismatch")

    install_commit_sha = _validate_commit(
        install_receipt.get("install_commit_sha"),
        field="install commit",
    )
    if install_commit_sha != expected_head_sha:
        raise ValueError("DEC-509 install receipt/main head mismatch")

    if install_receipt.get("annual_segment_label") != "2016":
        raise ValueError("DEC-509 install receipt annual segment mismatch")
    if install_receipt.get("expected_run_number") != 377:
        raise ValueError("DEC-509 install receipt expected run number mismatch")
    if install_receipt.get("expected_run_attempt") != 1:
        raise ValueError("DEC-509 install receipt expected run attempt mismatch")
    if install_receipt.get("install_action_consumed") is not True:
        raise ValueError("DEC-509 install action is not consumed")
    if install_receipt.get("runtime_authorization_installed") is not True:
        raise ValueError("DEC-509 runtime authorization is not installed")
    if install_receipt.get("runtime_gate_active") is not True:
        raise ValueError("DEC-509 runtime gate is not active")
    if install_receipt.get("annual_workflow_dispatch_authorized") is not False:
        raise ValueError("DEC-509 source receipt dispatch authority drift")

    previous_run_id = _positive_int(
        runtime_binding.get("run_id"),
        field="previous annual freeze run id",
    )
    if install_receipt.get("previous_annual_freeze_run_id") != previous_run_id:
        raise ValueError("DEC-509 install receipt predecessor mismatch")

    inventory = _validate_run_inventory(
        annual_workflow_runs,
        runtime_binding=runtime_binding,
    )

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2016_DISPATCH_PREFLIGHT_DECISION,
        "version": ANNUAL_CATALOGUE_2016_DISPATCH_PREFLIGHT_VERSION,
        **source,
        **inventory,
        "source_install_receipt_decision": "DEC-508",
        "source_install_receipt_version": (
            "fmp-annual-catalogue-2016-runtime-authorization-install-receipt-v1"
        ),
        "source_install_receipt_fingerprint_sha256": _sha256_hex(
            install_receipt.get("receipt_fingerprint_sha256"),
            field="install receipt fingerprint",
        ),
        "previous_runtime_binding_fingerprint_sha256": _sha256_hex(
            runtime_binding.get("binding_fingerprint_sha256"),
            field="previous runtime binding fingerprint",
        ),
        "previous_runtime_freeze_fingerprint_sha256": _sha256_hex(
            runtime_binding.get("runtime_freeze_fingerprint_sha256"),
            field="previous runtime freeze fingerprint",
        ),
        "previous_annual_freeze_evidence_fingerprint_sha256": _sha256_hex(
            runtime_binding.get("freeze_evidence_fingerprint"),
            field="previous annual freeze evidence fingerprint",
        ),
        "stage": (
            "ANNUAL_CATALOGUE_2016_DISPATCH_PREFLIGHT_"
            "INSTALLED_RUNTIME_BOUND_AUTHORIZATION_LOCKED"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": expected_head_sha,
        "install_commit_sha": install_commit_sha,
        "annual_segment_label": "2016",
        "prior_segment_label": "2015",
        "previous_annual_freeze_run_id": previous_run_id,
        "expected_run_number": 377,
        "expected_run_attempt": 1,
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
        "dispatch_command_present": False,
        "preflight_read_only": True,
        "next_gate": (
            "ANNUAL_PATTERN_CATALOGUE_2016_DISPATCH_AUTHORIZATION_BEFORE_RUN"
        ),
    }
    value["preflight_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    validate_2016_dispatch_preflight(value)
    return value


def validate_2016_dispatch_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _sha256_hex(
        value.get("preflight_fingerprint_sha256"),
        field="preflight fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("preflight_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-509 preflight fingerprint mismatch")

    exact = {
        "decision": "DEC-509",
        "version": "fmp-annual-catalogue-2016-dispatch-preflight-v1",
        "install_receipt_source_blob_sha": EXPECTED_INSTALL_RECEIPT_SOURCE_BLOB_SHA,
        "runtime_binding_source_blob_sha": EXPECTED_RUNTIME_BINDING_SOURCE_BLOB_SHA,
        "active_workflow_blob_sha": EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        "source_install_receipt_decision": "DEC-508",
        "source_install_receipt_version": (
            "fmp-annual-catalogue-2016-runtime-authorization-install-receipt-v1"
        ),
        "stage": (
            "ANNUAL_CATALOGUE_2016_DISPATCH_PREFLIGHT_"
            "INSTALLED_RUNTIME_BOUND_AUTHORIZATION_LOCKED"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "annual_segment_label": "2016",
        "prior_segment_label": "2015",
        "annual_workflow_run_count": 2,
        "failed_first_run_id": FAILED_FIRST_RUN_ID,
        "successful_2015_run_number": 376,
        "successful_2015_run_attempt": 1,
        "expected_run_number": 377,
        "expected_run_attempt": 1,
        "install_action_consumed": True,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
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
        "dispatch_command_present": False,
        "preflight_read_only": True,
        "next_gate": (
            "ANNUAL_PATTERN_CATALOGUE_2016_DISPATCH_AUTHORIZATION_BEFORE_RUN"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-509 {field} mismatch")

    expected_head = _validate_commit(
        value.get("expected_head_sha"),
        field="expected_head_sha",
    )
    install_commit = _validate_commit(
        value.get("install_commit_sha"),
        field="install_commit_sha",
    )
    if install_commit != expected_head:
        raise ValueError("DEC-509 install/main commit mismatch")
    _positive_int(
        value.get("previous_annual_freeze_run_id"),
        field="previous annual freeze run id",
    )
    _positive_int(
        value.get("successful_2015_run_id"),
        field="successful 2015 run id",
    )
    _validate_commit(
        value.get("successful_2015_run_head_sha"),
        field="successful 2015 run head",
    )
    for field in (
        "source_install_receipt_fingerprint_sha256",
        "previous_runtime_binding_fingerprint_sha256",
        "previous_runtime_freeze_fingerprint_sha256",
        "previous_annual_freeze_evidence_fingerprint_sha256",
    ):
        _sha256_hex(value.get(field), field=field)

    return value


__all__ = [
    "ANNUAL_CATALOGUE_2016_DISPATCH_PREFLIGHT_DECISION",
    "ANNUAL_CATALOGUE_2016_DISPATCH_PREFLIGHT_VERSION",
    "build_2016_dispatch_preflight",
    "validate_2016_dispatch_preflight",
    "validate_2016_dispatch_preflight_sources",
]
