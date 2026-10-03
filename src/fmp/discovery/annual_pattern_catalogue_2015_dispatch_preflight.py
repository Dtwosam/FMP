from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2015_execution_authorization import (
    ANNUAL_CATALOGUE_2015_EXECUTION_AUTHORIZATION_DECISION,
    ANNUAL_CATALOGUE_2015_EXECUTION_AUTHORIZATION_VERSION,
    ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED,
    AUTHORIZED_ANNUAL_SEGMENT_LABEL,
    EXPECTED_ANNUAL_WORKFLOW_RUN_ATTEMPT,
    EXPECTED_ANNUAL_WORKFLOW_RUN_NUMBER,
    HISTORICAL_ARTIFACT_READ_AUTHORIZED_FOR_2015,
    HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED_FOR_2015,
    HISTORICAL_RESULT_PRODUCTION_AUTHORIZED_FOR_2015,
)
from .annual_pattern_catalogue_workflow_source import (
    RESERVED_ACTIVE_WORKFLOW_PATH,
)


ANNUAL_CATALOGUE_2015_DISPATCH_PREFLIGHT_DECISION = "DEC-494"
ANNUAL_CATALOGUE_2015_DISPATCH_PREFLIGHT_VERSION = (
    "fmp-annual-catalogue-2015-dispatch-preflight-v1"
)

AUTHORIZATION_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_2015_execution_authorization.py"
)
EXPECTED_AUTHORIZATION_SOURCE_BLOB_SHA = (
    "b5f394f7921d78f73636e28892575cbf4b64a95c"
)
RUNTIME_SOURCE_PATH = "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
EXPECTED_RUNTIME_SOURCE_BLOB_SHA = "4f23996b90b4253af06774d0330003179264c8ee"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "31633e87b79551f5b7dfa6b0deb76a82eb070129"
)


def _git_blob_sha(path: Path) -> str:
    payload = Path(path).read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def validate_2015_dispatch_preflight_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "authorization_source_blob_sha": (
            root / AUTHORIZATION_SOURCE_PATH,
            EXPECTED_AUTHORIZATION_SOURCE_BLOB_SHA,
        ),
        "runtime_source_blob_sha": (
            root / RUNTIME_SOURCE_PATH,
            EXPECTED_RUNTIME_SOURCE_BLOB_SHA,
        ),
        "active_workflow_blob_sha": (
            root / RESERVED_ACTIVE_WORKFLOW_PATH,
            EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-494 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-494 {field} mismatch")
        actual[field] = sha

    if ANNUAL_CATALOGUE_2015_EXECUTION_AUTHORIZATION_DECISION != "DEC-493":
        raise ValueError("DEC-494 authorization decision drift")
    if (
        ANNUAL_CATALOGUE_2015_EXECUTION_AUTHORIZATION_VERSION
        != "fmp-annual-catalogue-2015-execution-authorization-v1"
    ):
        raise ValueError("DEC-494 authorization version drift")
    if not ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED:
        raise ValueError("DEC-494 requires authorized first 2015 dispatch")
    if not HISTORICAL_ARTIFACT_READ_AUTHORIZED_FOR_2015:
        raise ValueError("DEC-494 requires authorized 2015 historical reads")
    if not HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED_FOR_2015:
        raise ValueError("DEC-494 requires authorized 2015 execution")
    if not HISTORICAL_RESULT_PRODUCTION_AUTHORIZED_FOR_2015:
        raise ValueError("DEC-494 requires authorized 2015 result production")

    return actual


def build_2015_dispatch_preflight(
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    annual_workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2015_dispatch_preflight_sources(
        repository_root=Path(repository_root),
    )
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-494 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-494 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-494 main head mismatch")

    runs = annual_workflow_runs.get("workflow_runs")
    if not isinstance(runs, list):
        raise ValueError("DEC-494 annual workflow_runs must be a list")
    if runs:
        raise ValueError(
            "DEC-494 requires zero annual-catalogue workflow runs before "
            "the authorized first 2015 dispatch"
        )

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2015_DISPATCH_PREFLIGHT_DECISION,
        "version": ANNUAL_CATALOGUE_2015_DISPATCH_PREFLIGHT_VERSION,
        **source,
        "source_authorization_decision": (
            ANNUAL_CATALOGUE_2015_EXECUTION_AUTHORIZATION_DECISION
        ),
        "source_authorization_version": (
            ANNUAL_CATALOGUE_2015_EXECUTION_AUTHORIZATION_VERSION
        ),
        "stage": "ANNUAL_CATALOGUE_2015_FIRST_DISPATCH_READY",
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": expected_head_sha,
        "active_workflow_path": RESERVED_ACTIVE_WORKFLOW_PATH,
        "annual_segment_label": AUTHORIZED_ANNUAL_SEGMENT_LABEL,
        "previous_annual_freeze_run_id": "",
        "annual_workflow_run_count": 0,
        "expected_run_number": EXPECTED_ANNUAL_WORKFLOW_RUN_NUMBER,
        "expected_run_attempt": EXPECTED_ANNUAL_WORKFLOW_RUN_ATTEMPT,
        "annual_workflow_dispatch_authorized": True,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
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
            "EXACT_FIRST_2015_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_"
            "DISPATCH_ON_CURRENT_MAIN"
        ),
    }
    validate_2015_dispatch_preflight(value)
    return value


def validate_2015_dispatch_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    exact = {
        "decision": ANNUAL_CATALOGUE_2015_DISPATCH_PREFLIGHT_DECISION,
        "version": ANNUAL_CATALOGUE_2015_DISPATCH_PREFLIGHT_VERSION,
        "authorization_source_blob_sha": EXPECTED_AUTHORIZATION_SOURCE_BLOB_SHA,
        "runtime_source_blob_sha": EXPECTED_RUNTIME_SOURCE_BLOB_SHA,
        "active_workflow_blob_sha": EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        "source_authorization_decision": "DEC-493",
        "source_authorization_version": (
            "fmp-annual-catalogue-2015-execution-authorization-v1"
        ),
        "stage": "ANNUAL_CATALOGUE_2015_FIRST_DISPATCH_READY",
        "repository_full_name": "Dtwosam/FMP",
        "active_workflow_path": RESERVED_ACTIVE_WORKFLOW_PATH,
        "annual_segment_label": "2015",
        "previous_annual_freeze_run_id": "",
        "annual_workflow_run_count": 0,
        "expected_run_number": 1,
        "expected_run_attempt": 1,
        "annual_workflow_dispatch_authorized": True,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
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
            "EXACT_FIRST_2015_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_"
            "DISPATCH_ON_CURRENT_MAIN"
        ),
    }
    expected_keys = set(exact) | {"expected_head_sha"}
    if set(value) != expected_keys:
        raise ValueError("DEC-494 dispatch preflight key set mismatch")
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-494 {field} mismatch")
    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2015_DISPATCH_PREFLIGHT_DECISION",
    "ANNUAL_CATALOGUE_2015_DISPATCH_PREFLIGHT_VERSION",
    "EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA",
    "EXPECTED_AUTHORIZATION_SOURCE_BLOB_SHA",
    "EXPECTED_RUNTIME_SOURCE_BLOB_SHA",
    "build_2015_dispatch_preflight",
    "validate_2015_dispatch_preflight",
    "validate_2015_dispatch_preflight_sources",
]
