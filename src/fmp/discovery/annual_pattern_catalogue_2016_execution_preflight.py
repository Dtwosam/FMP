from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2015_runtime_evidence_binding import (
    validate_2015_runtime_evidence_binding,
)
from .annual_pattern_catalogue_runtime import (
    HISTORICAL_ARTIFACT_READ_AUTHORIZED as RUNTIME_ARTIFACT_READ_AUTHORIZED,
    HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED as RUNTIME_EXECUTION_AUTHORIZED,
    HISTORICAL_RESULT_PRODUCTION_AUTHORIZED as RUNTIME_RESULT_AUTHORIZED,
)
from .annual_pattern_catalogue_workflow_source import (
    prior_segment_label,
    validate_annual_segment_label,
)


ANNUAL_CATALOGUE_2016_EXECUTION_PREFLIGHT_DECISION = "DEC-503"
ANNUAL_CATALOGUE_2016_EXECUTION_PREFLIGHT_VERSION = (
    "fmp-annual-catalogue-2016-execution-preflight-v1"
)

RUNTIME_BINDING_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2015_runtime_evidence_binding.py"
)
EXPECTED_RUNTIME_BINDING_SOURCE_BLOB_SHA = (
    "400e9715a6e3b2dab413ce2ecff0fbce8c46f6b0"
)
RUNTIME_SOURCE_PATH = "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
EXPECTED_RUNTIME_SOURCE_BLOB_SHA = (
    "f1fa50e7c862354931d919fe7da241de863f6834"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)

FAILED_FIRST_RUN_ID = 37126711695
FAILED_FIRST_RUN_HEAD_SHA = "fd85a886d07234ad584dcca08692b37e6af54b2e"
FAILED_RUN376_ID = 37191637168
FAILED_RUN376_HEAD_SHA = "4c14fa7db6eb812b89ecb79201f7e298fa9c04f3"

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


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return value


def _sha256_hex(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hexadecimal") from exc
    return value.lower()


def validate_2016_execution_preflight_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "runtime_binding_source_blob_sha": (
            root / RUNTIME_BINDING_SOURCE_PATH,
            EXPECTED_RUNTIME_BINDING_SOURCE_BLOB_SHA,
        ),
        "runtime_source_blob_sha": (
            root / RUNTIME_SOURCE_PATH,
            EXPECTED_RUNTIME_SOURCE_BLOB_SHA,
        ),
        "active_workflow_blob_sha": (
            root / ACTIVE_WORKFLOW_PATH,
            EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-503 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-503 {field} mismatch")
        actual[field] = sha

    if RUNTIME_ARTIFACT_READ_AUTHORIZED is not False:
        raise ValueError("DEC-503 requires default historical reads locked")
    if RUNTIME_EXECUTION_AUTHORIZED is not False:
        raise ValueError("DEC-503 requires default historical execution locked")
    if RUNTIME_RESULT_AUTHORIZED is not False:
        raise ValueError("DEC-503 requires default result production locked")

    return actual


def _validate_run_inventory(
    value: Mapping[str, object],
    *,
    binding: Mapping[str, object],
) -> dict[str, object]:
    runs = value.get("workflow_runs")
    if not isinstance(runs, list) or len(runs) != 3:
        raise ValueError(
            "DEC-503 requires exactly three prior annual-catalogue workflow runs"
        )

    by_number: dict[int, Mapping[str, object]] = {}
    for raw in runs:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-503 workflow run row malformed")
        number = raw.get("run_number")
        if not isinstance(number, int) or isinstance(number, bool):
            raise ValueError("DEC-503 workflow run number malformed")
        if number in by_number:
            raise ValueError("DEC-503 duplicate workflow run number")
        by_number[number] = raw

    if set(by_number) != {1, 376, 377}:
        raise ValueError("DEC-503 workflow run number inventory mismatch")

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
            raise ValueError(f"DEC-503 failed first run {field} mismatch")

    failed_376 = by_number[376]
    failed_376_exact = {
        "id": FAILED_RUN376_ID,
        "run_number": 376,
        "run_attempt": 1,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": FAILED_RUN376_HEAD_SHA,
        "status": "completed",
        "conclusion": "failure",
    }
    for field, expected in failed_376_exact.items():
        if failed_376.get(field) != expected:
            raise ValueError(f"DEC-503 failed run376 {field} mismatch")

    successful = by_number[377]
    successful_exact = {
        "id": binding.get("run_id"),
        "run_number": 377,
        "run_attempt": 1,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": binding.get("run_head_sha"),
        "status": "completed",
        "conclusion": "success",
    }
    for field, expected in successful_exact.items():
        if successful.get(field) != expected:
            raise ValueError(f"DEC-503 successful 2015 run {field} mismatch")

    return {
        "annual_workflow_run_count": 3,
        "failed_first_run_id": FAILED_FIRST_RUN_ID,
        "failed_run376_id": FAILED_RUN376_ID,
        "successful_2015_run_id": _positive_int(
            binding.get("run_id"),
            field="successful 2015 run id",
        ),
        "successful_2015_run_number": 377,
        "successful_2015_run_attempt": 1,
        "successful_2015_run_head_sha": _validate_commit(
            binding.get("run_head_sha"),
            field="successful 2015 run head",
        ),
    }


def build_2016_execution_preflight(
    *,
    repository_root: Path,
    runtime_binding: Mapping[str, object],
    main_branch: Mapping[str, object],
    annual_workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2016_execution_preflight_sources(
        repository_root=Path(repository_root),
    )
    validate_2015_runtime_evidence_binding(runtime_binding)

    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-503 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-503 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-503 main head mismatch")

    current_segment = validate_annual_segment_label("2016")
    predecessor = prior_segment_label(current_segment)
    if predecessor != "2015":
        raise ValueError("DEC-503 predecessor invariant drift")

    inventory = _validate_run_inventory(
        annual_workflow_runs,
        binding=runtime_binding,
    )

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2016_EXECUTION_PREFLIGHT_DECISION,
        "version": ANNUAL_CATALOGUE_2016_EXECUTION_PREFLIGHT_VERSION,
        **source,
        **inventory,
        "stage": (
            "ANNUAL_CATALOGUE_2016_EXECUTION_PREFLIGHT_"
            "PREDECESSOR_BOUND_AUTHORIZATION_LOCKED"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": expected_head_sha,
        "annual_segment_label": current_segment,
        "prior_segment_required": True,
        "prior_segment_label": predecessor,
        "previous_annual_freeze_run_id": _positive_int(
            runtime_binding.get("run_id"),
            field="previous annual freeze run id",
        ),
        "previous_runtime_binding_fingerprint": _sha256_hex(
            runtime_binding.get("binding_fingerprint_sha256"),
            field="previous runtime binding fingerprint",
        ),
        "previous_runtime_freeze_fingerprint": _sha256_hex(
            runtime_binding.get("runtime_freeze_fingerprint_sha256"),
            field="previous runtime freeze fingerprint",
        ),
        "previous_annual_freeze_evidence_fingerprint": _sha256_hex(
            runtime_binding.get("freeze_evidence_fingerprint"),
            field="previous annual freeze evidence fingerprint",
        ),
        "expected_next_run_number": 378,
        "expected_next_run_attempt": 1,
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
        "next_segment_execution_authorized": (
            NEXT_SEGMENT_EXECUTION_AUTHORIZED
        ),
        "cross_year_result_production_authorized": (
            CROSS_YEAR_RESULT_PRODUCTION_AUTHORIZED
        ),
        "strategy_v1_synthesis_authorized": (
            STRATEGY_V1_SYNTHESIS_AUTHORIZED
        ),
        "promotion_authorized": PROMOTION_AUTHORIZED,
        "phase8b_authorized": PHASE8B_AUTHORIZED,
        "demo_order_authorized": DEMO_ORDER_AUTHORIZED,
        "broker_mutation_authorized": BROKER_MUTATION_AUTHORIZED,
        "live_order_authorized": LIVE_ORDER_AUTHORIZED,
        "real_money_authorized": REAL_MONEY_AUTHORIZED,
        "trading_authorized": TRADING_AUTHORIZED,
        "preflight_read_only": True,
        "next_gate": (
            "ANNUAL_PATTERN_CATALOGUE_2016_EXECUTION_AUTHORIZATION_BEFORE_RUN"
        ),
    }
    validate_2016_execution_preflight(value)
    return value


def validate_2016_execution_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    if value.get("decision") != "DEC-503":
        raise ValueError("DEC-503 decision mismatch")
    if value.get("annual_segment_label") != "2016":
        raise ValueError("DEC-503 annual segment mismatch")
    if value.get("prior_segment_required") is not True:
        raise ValueError("DEC-503 predecessor must be required")
    if value.get("prior_segment_label") != "2015":
        raise ValueError("DEC-503 predecessor label mismatch")
    if value.get("annual_workflow_run_count") != 3:
        raise ValueError("DEC-503 workflow run count mismatch")
    if value.get("expected_next_run_number") != 378:
        raise ValueError("DEC-503 next run number mismatch")
    if value.get("expected_next_run_attempt") != 1:
        raise ValueError("DEC-503 next run attempt mismatch")
    _positive_int(
        value.get("previous_annual_freeze_run_id"),
        field="previous annual freeze run id",
    )
    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    for field in (
        "previous_runtime_binding_fingerprint",
        "previous_runtime_freeze_fingerprint",
        "previous_annual_freeze_evidence_fingerprint",
    ):
        _sha256_hex(value.get(field), field=field)

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
            raise ValueError(f"DEC-503 {field} must remain false")

    if value.get("preflight_read_only") is not True:
        raise ValueError("DEC-503 preflight must remain read-only")
    if (
        value.get("next_gate")
        != "ANNUAL_PATTERN_CATALOGUE_2016_EXECUTION_AUTHORIZATION_BEFORE_RUN"
    ):
        raise ValueError("DEC-503 next gate mismatch")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2016_EXECUTION_PREFLIGHT_DECISION",
    "ANNUAL_CATALOGUE_2016_EXECUTION_PREFLIGHT_VERSION",
    "build_2016_execution_preflight",
    "validate_2016_execution_preflight",
    "validate_2016_execution_preflight_sources",
]
