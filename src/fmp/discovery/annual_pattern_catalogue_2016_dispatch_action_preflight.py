from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2016_dispatch_authorization import (
    ANNUAL_CATALOGUE_2016_DISPATCH_AUTHORIZATION_DECISION,
    ANNUAL_CATALOGUE_2016_DISPATCH_AUTHORIZATION_VERSION,
    validate_2016_dispatch_authorization,
)


ANNUAL_CATALOGUE_2016_DISPATCH_ACTION_PREFLIGHT_DECISION = "DEC-511"
ANNUAL_CATALOGUE_2016_DISPATCH_ACTION_PREFLIGHT_VERSION = (
    "fmp-annual-catalogue-2016-dispatch-action-preflight-v1"
)

AUTHORIZATION_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2016_dispatch_authorization.py"
)
EXPECTED_AUTHORIZATION_SOURCE_BLOB_SHA = (
    "ffedb7b0f14f375e6b732678d95a2a48d21eb002"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)

FAILED_FIRST_RUN_ID = 37126711695
FAILED_FIRST_RUN_HEAD_SHA = "fd85a886d07234ad584dcca08692b37e6af54b2e"


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
        raise ValueError(f"DEC-511 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-511 {field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-511 {field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-511 {field} must be hexadecimal") from exc
    return value.lower()


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"DEC-511 {field} must be a positive integer")
    return value


def validate_2016_dispatch_action_preflight_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "authorization_source_blob_sha": (
            root / AUTHORIZATION_SOURCE_PATH,
            EXPECTED_AUTHORIZATION_SOURCE_BLOB_SHA,
        ),
        "active_workflow_blob_sha": (
            root / ACTIVE_WORKFLOW_PATH,
            EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-511 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-511 {field} mismatch")
        actual[field] = sha

    if ANNUAL_CATALOGUE_2016_DISPATCH_AUTHORIZATION_DECISION != "DEC-510":
        raise ValueError("DEC-511 authorization decision drift")
    if (
        ANNUAL_CATALOGUE_2016_DISPATCH_AUTHORIZATION_VERSION
        != "fmp-annual-catalogue-2016-dispatch-authorization-v1"
    ):
        raise ValueError("DEC-511 authorization version drift")
    return actual


def _validate_run_inventory(
    value: Mapping[str, object],
    *,
    authorization: Mapping[str, object],
) -> dict[str, object]:
    runs = value.get("workflow_runs")
    if not isinstance(runs, list) or len(runs) != 2:
        raise ValueError(
            "DEC-511 requires exactly two prior annual-catalogue workflow runs"
        )

    by_number: dict[int, Mapping[str, object]] = {}
    for raw in runs:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-511 workflow run row malformed")
        number = raw.get("run_number")
        if not isinstance(number, int) or isinstance(number, bool):
            raise ValueError("DEC-511 workflow run number malformed")
        if number in by_number:
            raise ValueError("DEC-511 duplicate workflow run number")
        by_number[number] = raw

    if set(by_number) != {1, 376}:
        raise ValueError("DEC-511 workflow run number inventory mismatch")

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
            raise ValueError(f"DEC-511 failed first run {field} mismatch")

    second = by_number[376]
    second_exact = {
        "id": authorization.get("successful_2015_run_id"),
        "run_number": 376,
        "run_attempt": 1,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": authorization.get("successful_2015_run_head_sha"),
        "status": "completed",
        "conclusion": "success",
    }
    for field, expected in second_exact.items():
        if second.get(field) != expected:
            raise ValueError(f"DEC-511 successful 2015 run {field} mismatch")

    return {
        "annual_workflow_run_count": 2,
        "failed_first_run_id": FAILED_FIRST_RUN_ID,
        "successful_2015_run_id": _positive_int(
            authorization.get("successful_2015_run_id"),
            field="successful 2015 run id",
        ),
        "successful_2015_run_head_sha": _validate_commit(
            second.get("head_sha"),
            field="successful 2015 run head",
        ),
    }


def build_2016_dispatch_action_preflight(
    authorization: Mapping[str, object],
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    annual_workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2016_dispatch_action_preflight_sources(
        repository_root=Path(repository_root),
    )
    validate_2016_dispatch_authorization(authorization)

    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-511 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-511 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-511 main head mismatch")

    authorization_head = _validate_commit(
        authorization.get("expected_head_sha"),
        field="authorization expected head",
    )
    install_commit = _validate_commit(
        authorization.get("install_commit_sha"),
        field="install commit",
    )
    if authorization_head != expected_head_sha:
        raise ValueError("DEC-511 authorization/main head mismatch")
    if install_commit != expected_head_sha:
        raise ValueError("DEC-511 install/main head mismatch")

    if authorization.get("annual_segment_label") != "2016":
        raise ValueError("DEC-511 annual segment mismatch")
    if authorization.get("expected_run_number") != 377:
        raise ValueError("DEC-511 expected run number mismatch")
    if authorization.get("expected_run_attempt") != 1:
        raise ValueError("DEC-511 expected run attempt mismatch")
    for field in (
        "annual_workflow_dispatch_authorized",
        "historical_artifact_read_authorized",
        "historical_catalogue_execution_authorized",
        "historical_result_production_authorized",
        "authorization_contract_validated",
        "runtime_authorization_installed",
        "runtime_gate_active",
        "source_only_authorization",
    ):
        if authorization.get(field) is not True:
            raise ValueError(f"DEC-511 authorization {field} must be true")
    for field in (
        "dispatch_action_executed",
        "dispatch_command_present",
        "rerun_authorized",
        "retry_authorized",
        "fourth_or_later_run_authorized",
        "next_segment_execution_authorized",
        "trading_authorized",
    ):
        if authorization.get(field) is not False:
            raise ValueError(f"DEC-511 authorization {field} must remain false")

    inventory = _validate_run_inventory(
        annual_workflow_runs,
        authorization=authorization,
    )
    previous_run_id = _positive_int(
        authorization.get("previous_annual_freeze_run_id"),
        field="previous annual freeze run id",
    )
    if inventory["successful_2015_run_id"] != previous_run_id:
        raise ValueError("DEC-511 predecessor run identity mismatch")

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2016_DISPATCH_ACTION_PREFLIGHT_DECISION,
        "version": ANNUAL_CATALOGUE_2016_DISPATCH_ACTION_PREFLIGHT_VERSION,
        **source,
        **inventory,
        "source_authorization_decision": "DEC-510",
        "source_authorization_version": (
            "fmp-annual-catalogue-2016-dispatch-authorization-v1"
        ),
        "source_authorization_fingerprint_sha256": _sha256_hex(
            authorization.get("authorization_fingerprint_sha256"),
            field="source authorization fingerprint",
        ),
        "stage": "ANNUAL_CATALOGUE_2016_DISPATCH_ACTION_PREFLIGHT_READY",
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": expected_head_sha,
        "install_commit_sha": install_commit,
        "active_workflow_path": ACTIVE_WORKFLOW_PATH,
        "annual_segment_label": "2016",
        "previous_annual_freeze_run_id": previous_run_id,
        "expected_run_number": 377,
        "expected_run_attempt": 1,
        "dispatch_ref": "main",
        "dispatch_input_annual_segment_label": "2016",
        "dispatch_input_previous_annual_freeze_run_id": str(previous_run_id),
        "dispatch_parameters_frozen": True,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "annual_workflow_dispatch_authorized": True,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "dispatch_command_present": False,
        "dispatch_action_executed": False,
        "preflight_read_only": True,
        "rerun_authorized": False,
        "retry_authorized": False,
        "fourth_or_later_run_authorized": False,
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
        "next_gate": (
            "EXACT_2016_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN"
        ),
    }
    value["preflight_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    validate_2016_dispatch_action_preflight(value)
    return value


def validate_2016_dispatch_action_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _sha256_hex(
        value.get("preflight_fingerprint_sha256"),
        field="preflight fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("preflight_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-511 preflight fingerprint mismatch")

    exact = {
        "decision": "DEC-511",
        "version": "fmp-annual-catalogue-2016-dispatch-action-preflight-v1",
        "authorization_source_blob_sha": EXPECTED_AUTHORIZATION_SOURCE_BLOB_SHA,
        "active_workflow_blob_sha": EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        "source_authorization_decision": "DEC-510",
        "source_authorization_version": (
            "fmp-annual-catalogue-2016-dispatch-authorization-v1"
        ),
        "stage": "ANNUAL_CATALOGUE_2016_DISPATCH_ACTION_PREFLIGHT_READY",
        "repository_full_name": "Dtwosam/FMP",
        "active_workflow_path": ACTIVE_WORKFLOW_PATH,
        "annual_segment_label": "2016",
        "annual_workflow_run_count": 2,
        "failed_first_run_id": FAILED_FIRST_RUN_ID,
        "expected_run_number": 377,
        "expected_run_attempt": 1,
        "dispatch_ref": "main",
        "dispatch_input_annual_segment_label": "2016",
        "dispatch_parameters_frozen": True,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "annual_workflow_dispatch_authorized": True,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "dispatch_command_present": False,
        "dispatch_action_executed": False,
        "preflight_read_only": True,
        "rerun_authorized": False,
        "retry_authorized": False,
        "fourth_or_later_run_authorized": False,
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
        "next_gate": (
            "EXACT_2016_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-511 {field} mismatch")

    expected_head = _validate_commit(
        value.get("expected_head_sha"),
        field="expected_head_sha",
    )
    install_commit = _validate_commit(
        value.get("install_commit_sha"),
        field="install_commit_sha",
    )
    if install_commit != expected_head:
        raise ValueError("DEC-511 install/main commit mismatch")
    previous_run_id = _positive_int(
        value.get("previous_annual_freeze_run_id"),
        field="previous annual freeze run id",
    )
    if value.get("dispatch_input_previous_annual_freeze_run_id") != str(
        previous_run_id
    ):
        raise ValueError("DEC-511 dispatch predecessor input mismatch")
    successful_run_id = _positive_int(
        value.get("successful_2015_run_id"),
        field="successful 2015 run id",
    )
    if successful_run_id != previous_run_id:
        raise ValueError("DEC-511 successful/predecessor run mismatch")
    _validate_commit(
        value.get("successful_2015_run_head_sha"),
        field="successful 2015 run head",
    )
    _sha256_hex(
        value.get("source_authorization_fingerprint_sha256"),
        field="source authorization fingerprint",
    )
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2016_DISPATCH_ACTION_PREFLIGHT_DECISION",
    "ANNUAL_CATALOGUE_2016_DISPATCH_ACTION_PREFLIGHT_VERSION",
    "build_2016_dispatch_action_preflight",
    "validate_2016_dispatch_action_preflight",
    "validate_2016_dispatch_action_preflight_sources",
]
