from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2015_replacement_execution_authorization import (
    ANNUAL_CATALOGUE_2015_REPLACEMENT_EXECUTION_AUTHORIZATION_DECISION,
    ANNUAL_CATALOGUE_2015_REPLACEMENT_EXECUTION_AUTHORIZATION_VERSION,
    EXPECTED_REPLACEMENT_RUN_ATTEMPT,
    EXPECTED_REPLACEMENT_RUN_NUMBER,
    REPLACEMENT_RUN_AUTHORIZED,
    HISTORICAL_ARTIFACT_READ_AUTHORIZED_FOR_REPLACEMENT,
    HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED_FOR_REPLACEMENT,
    HISTORICAL_RESULT_PRODUCTION_AUTHORIZED_FOR_REPLACEMENT,
)


ANNUAL_CATALOGUE_2015_REPLACEMENT_DISPATCH_ACTION_PREFLIGHT_DECISION = "DEC-499"
ANNUAL_CATALOGUE_2015_REPLACEMENT_DISPATCH_ACTION_PREFLIGHT_VERSION = (
    "fmp-annual-catalogue-2015-replacement-dispatch-action-preflight-v1"
)

AUTHORIZATION_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_2015_replacement_execution_authorization.py"
)
EXPECTED_AUTHORIZATION_SOURCE_BLOB_SHA = (
    "c63fc9f72ad34fa6fd903f2dde8e85570521c9b9"
)
RUNTIME_SOURCE_PATH = "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
EXPECTED_RUNTIME_SOURCE_BLOB_SHA = (
    "ef50c43fe6fe9c0cba3d220adf7d4b4883f5312b"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_REPAIRED_WORKFLOW_BLOB_SHA = (
    "f7e65ee95f472918e390bceedd7cf2f38bbf7e92"
)

FAILED_FIRST_RUN_ID = 37126711695
FAILED_FIRST_RUN_NUMBER = 1
FAILED_FIRST_RUN_ATTEMPT = 1
FAILED_FIRST_RUN_HEAD_SHA = "fd85a886d07234ad584dcca08692b37e6af54b2e"


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


def validate_2015_replacement_dispatch_action_preflight_sources(
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
            root / ACTIVE_WORKFLOW_PATH,
            EXPECTED_REPAIRED_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-499 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-499 {field} mismatch")
        actual[field] = sha

    if (
        ANNUAL_CATALOGUE_2015_REPLACEMENT_EXECUTION_AUTHORIZATION_DECISION
        != "DEC-498"
    ):
        raise ValueError("DEC-499 replacement authorization decision drift")
    if (
        ANNUAL_CATALOGUE_2015_REPLACEMENT_EXECUTION_AUTHORIZATION_VERSION
        != "fmp-annual-catalogue-2015-replacement-execution-authorization-v1"
    ):
        raise ValueError("DEC-499 replacement authorization version drift")
    if REPLACEMENT_RUN_AUTHORIZED is not True:
        raise ValueError("DEC-499 replacement run authorization is not active")
    if HISTORICAL_ARTIFACT_READ_AUTHORIZED_FOR_REPLACEMENT is not True:
        raise ValueError("DEC-499 replacement historical reads are not active")
    if HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED_FOR_REPLACEMENT is not True:
        raise ValueError("DEC-499 replacement execution is not active")
    if HISTORICAL_RESULT_PRODUCTION_AUTHORIZED_FOR_REPLACEMENT is not True:
        raise ValueError("DEC-499 replacement result production is not active")

    return actual


def _validate_prior_run_inventory(
    value: Mapping[str, object],
) -> dict[str, object]:
    runs = value.get("workflow_runs")
    if not isinstance(runs, list):
        raise ValueError("DEC-499 annual workflow_runs must be a list")
    if len(runs) != 1:
        raise ValueError(
            "DEC-499 requires exactly one prior annual-catalogue workflow run"
        )
    row = runs[0]
    if not isinstance(row, Mapping):
        raise ValueError("DEC-499 prior run row is malformed")
    exact = {
        "id": FAILED_FIRST_RUN_ID,
        "run_number": FAILED_FIRST_RUN_NUMBER,
        "run_attempt": FAILED_FIRST_RUN_ATTEMPT,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": FAILED_FIRST_RUN_HEAD_SHA,
        "status": "completed",
        "conclusion": "failure",
    }
    for field, expected in exact.items():
        if row.get(field) != expected:
            raise ValueError(f"DEC-499 prior failed run {field} mismatch")
    return {
        "prior_run_count": 1,
        "failed_first_run_id": FAILED_FIRST_RUN_ID,
        "failed_first_run_number": FAILED_FIRST_RUN_NUMBER,
        "failed_first_run_attempt": FAILED_FIRST_RUN_ATTEMPT,
        "failed_first_run_head_sha": FAILED_FIRST_RUN_HEAD_SHA,
        "failed_first_run_conclusion": "failure",
    }


def build_2015_replacement_dispatch_action_preflight(
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    annual_workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2015_replacement_dispatch_action_preflight_sources(
        repository_root=Path(repository_root),
    )
    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-499 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-499 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-499 main head mismatch")

    inventory = _validate_prior_run_inventory(annual_workflow_runs)

    value: dict[str, object] = {
        "decision": (
            ANNUAL_CATALOGUE_2015_REPLACEMENT_DISPATCH_ACTION_PREFLIGHT_DECISION
        ),
        "version": (
            ANNUAL_CATALOGUE_2015_REPLACEMENT_DISPATCH_ACTION_PREFLIGHT_VERSION
        ),
        **source,
        **inventory,
        "source_authorization_decision": "DEC-498",
        "stage": "ANNUAL_CATALOGUE_2015_REPLACEMENT_DISPATCH_READY",
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": expected_head_sha,
        "active_workflow_path": ACTIVE_WORKFLOW_PATH,
        "annual_segment_label": "2015",
        "previous_annual_freeze_run_id": "",
        "expected_replacement_run_number": EXPECTED_REPLACEMENT_RUN_NUMBER,
        "expected_replacement_run_attempt": EXPECTED_REPLACEMENT_RUN_ATTEMPT,
        "replacement_run_authorized": True,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "rerun_failed_run_authorized": False,
        "retry_failed_run_authorized": False,
        "third_or_later_run_authorized": False,
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
            "EXACT_2015_REPLACEMENT_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_"
            "DISPATCH_ON_CURRENT_MAIN"
        ),
    }
    validate_2015_replacement_dispatch_action_preflight(value)
    return value


def validate_2015_replacement_dispatch_action_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    if value.get("decision") != "DEC-499":
        raise ValueError("DEC-499 decision mismatch")
    if value.get("prior_run_count") != 1:
        raise ValueError("DEC-499 prior run count mismatch")
    if value.get("failed_first_run_id") != FAILED_FIRST_RUN_ID:
        raise ValueError("DEC-499 failed first run id mismatch")
    if value.get("expected_replacement_run_number") != 2:
        raise ValueError("DEC-499 replacement run number mismatch")
    if value.get("expected_replacement_run_attempt") != 1:
        raise ValueError("DEC-499 replacement run attempt mismatch")
    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    for field in (
        "replacement_run_authorized",
        "historical_artifact_read_authorized",
        "historical_catalogue_execution_authorized",
        "historical_result_production_authorized",
    ):
        if value.get(field) is not True:
            raise ValueError(f"DEC-499 {field} must be true")
    for field in (
        "rerun_failed_run_authorized",
        "retry_failed_run_authorized",
        "third_or_later_run_authorized",
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
        "dispatch_command_present",
    ):
        if value.get(field) is not False:
            raise ValueError(f"DEC-499 {field} must remain false")
    if value.get("preflight_read_only") is not True:
        raise ValueError("DEC-499 preflight must remain read-only")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2015_REPLACEMENT_DISPATCH_ACTION_PREFLIGHT_DECISION",
    "ANNUAL_CATALOGUE_2015_REPLACEMENT_DISPATCH_ACTION_PREFLIGHT_VERSION",
    "build_2015_replacement_dispatch_action_preflight",
    "validate_2015_replacement_dispatch_action_preflight",
    "validate_2015_replacement_dispatch_action_preflight_sources",
]
