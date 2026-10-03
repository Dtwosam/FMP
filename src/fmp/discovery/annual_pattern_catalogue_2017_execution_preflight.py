from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2016_run377_evidence_review import (
    ANNUAL_CATALOGUE_2016_RUN377_EVIDENCE_REVIEW_DECISION,
    ANNUAL_CATALOGUE_2016_RUN377_EVIDENCE_REVIEW_VERSION,
    validate_2016_run377_evidence_review,
)


ANNUAL_CATALOGUE_2017_EXECUTION_PREFLIGHT_DECISION = "DEC-523"
ANNUAL_CATALOGUE_2017_EXECUTION_PREFLIGHT_VERSION = (
    "fmp-annual-catalogue-2017-execution-preflight-v1"
)

RUNTIME_BINDING_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_2016_run377_evidence_review.py"
)
EXPECTED_RUNTIME_BINDING_SOURCE_BLOB_SHA = (
    "b186c8049b045761ccd0f693feaf7637a4807e53"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)

FAILED_FIRST_RUN_ID = 37126711695
FAILED_FIRST_RUN_HEAD_SHA = "fd85a886d07234ad584dcca08692b37e6af54b2e"
SUCCESSFUL_2015_RUN_NUMBER = 376
SUCCESSFUL_2016_RUN_NUMBER = 377
EXPECTED_2017_RUN_NUMBER = 378
EXPECTED_2017_RUN_ATTEMPT = 1

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
        raise ValueError(f"DEC-523 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-523 {field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-523 {field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-523 {field} must be hexadecimal") from exc
    return value.lower()


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"DEC-523 {field} must be a positive integer")
    return value


def validate_2017_execution_preflight_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
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
            raise ValueError(f"DEC-523 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-523 {field} mismatch")
        actual[field] = sha

    if ANNUAL_CATALOGUE_2016_RUN377_EVIDENCE_REVIEW_DECISION != "DEC-522":
        raise ValueError("DEC-523 runtime binding decision drift")
    if (
        ANNUAL_CATALOGUE_2016_RUN377_EVIDENCE_REVIEW_VERSION
        != "fmp-annual-catalogue-2016-run377-evidence-review-v1"
    ):
        raise ValueError("DEC-523 runtime binding version drift")
    return actual


def _validate_run_inventory(
    value: Mapping[str, object],
    *,
    runtime_binding: Mapping[str, object],
) -> dict[str, object]:
    runs = value.get("workflow_runs")
    if not isinstance(runs, list) or len(runs) != 3:
        raise ValueError(
            "DEC-523 requires exactly three annual workflow dispatch runs"
        )

    by_number: dict[int, Mapping[str, object]] = {}
    for raw in runs:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-523 workflow run row malformed")
        number = raw.get("run_number")
        if not isinstance(number, int) or isinstance(number, bool):
            raise ValueError("DEC-523 workflow run number malformed")
        if number in by_number:
            raise ValueError("DEC-523 duplicate workflow run number")
        by_number[number] = raw

    expected_numbers = {
        1,
        SUCCESSFUL_2015_RUN_NUMBER,
        SUCCESSFUL_2016_RUN_NUMBER,
    }
    if set(by_number) != expected_numbers:
        raise ValueError("DEC-523 workflow run inventory mismatch")

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
            raise ValueError(f"DEC-523 failed first run {field} mismatch")

    previous_2015_run_id = _positive_int(
        runtime_binding.get("previous_annual_freeze_run_id"),
        field="2015 predecessor run id",
    )
    run376 = by_number[SUCCESSFUL_2015_RUN_NUMBER]
    run376_exact = {
        "id": previous_2015_run_id,
        "run_number": SUCCESSFUL_2015_RUN_NUMBER,
        "run_attempt": 1,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "status": "completed",
        "conclusion": "success",
    }
    for field, expected in run376_exact.items():
        if run376.get(field) != expected:
            raise ValueError(f"DEC-523 successful 2015 run {field} mismatch")
    run376_head_sha = _validate_commit(
        run376.get("head_sha"),
        field="successful 2015 run head",
    )

    run377 = by_number[SUCCESSFUL_2016_RUN_NUMBER]
    run377_exact = {
        "id": runtime_binding.get("run_id"),
        "run_number": SUCCESSFUL_2016_RUN_NUMBER,
        "run_attempt": 1,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": runtime_binding.get("run_head_sha"),
        "status": "completed",
        "conclusion": "success",
    }
    for field, expected in run377_exact.items():
        if run377.get(field) != expected:
            raise ValueError(f"DEC-523 successful 2016 run {field} mismatch")

    return {
        "annual_workflow_run_count": 3,
        "failed_first_run_id": FAILED_FIRST_RUN_ID,
        "successful_2015_run_id": previous_2015_run_id,
        "successful_2015_run_number": SUCCESSFUL_2015_RUN_NUMBER,
        "successful_2015_run_attempt": 1,
        "successful_2015_run_head_sha": run376_head_sha,
        "successful_2016_run_id": _positive_int(
            runtime_binding.get("run_id"),
            field="successful 2016 run id",
        ),
        "successful_2016_run_number": SUCCESSFUL_2016_RUN_NUMBER,
        "successful_2016_run_attempt": 1,
        "successful_2016_run_head_sha": _validate_commit(
            runtime_binding.get("run_head_sha"),
            field="successful 2016 run head",
        ),
    }


def build_2017_execution_preflight(
    *,
    repository_root: Path,
    runtime_binding: Mapping[str, object],
    main_branch: Mapping[str, object],
    annual_workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2017_execution_preflight_sources(
        repository_root=Path(repository_root),
    )
    validate_2016_run377_evidence_review(runtime_binding)

    if runtime_binding.get("annual_segment_label") != "2016":
        raise ValueError("DEC-523 runtime binding segment mismatch")
    if runtime_binding.get("run_number") != SUCCESSFUL_2016_RUN_NUMBER:
        raise ValueError("DEC-523 runtime binding run number mismatch")
    if runtime_binding.get("run_attempt") != 1:
        raise ValueError("DEC-523 runtime binding run attempt mismatch")
    if runtime_binding.get("run_conclusion") != "success":
        raise ValueError("DEC-523 runtime binding conclusion mismatch")
    if runtime_binding.get("runtime_evidence_bound") is not True:
        raise ValueError("DEC-523 runtime evidence is not bound")
    if runtime_binding.get("next_segment_execution_authorized") is not False:
        raise ValueError("DEC-523 source binding already authorizes next segment")
    if runtime_binding.get("trading_authorized") is not False:
        raise ValueError("DEC-523 source binding trading authority drift")

    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-523 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-523 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-523 main head mismatch")

    inventory = _validate_run_inventory(
        annual_workflow_runs,
        runtime_binding=runtime_binding,
    )

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2017_EXECUTION_PREFLIGHT_DECISION,
        "version": ANNUAL_CATALOGUE_2017_EXECUTION_PREFLIGHT_VERSION,
        **source,
        **inventory,
        "source_runtime_binding_decision": "DEC-522",
        "source_runtime_binding_version": (
            "fmp-annual-catalogue-2016-run377-evidence-review-v1"
        ),
        "source_runtime_binding_fingerprint_sha256": _sha256_hex(
            runtime_binding.get("binding_fingerprint_sha256"),
            field="runtime binding fingerprint",
        ),
        "stage": (
            "ANNUAL_CATALOGUE_2017_EXECUTION_PREFLIGHT_"
            "PREDECESSOR_BOUND_AUTHORIZATION_LOCKED"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": expected_head_sha,
        "annual_segment_label": "2017",
        "prior_segment_required": True,
        "prior_segment_label": "2016",
        "previous_annual_freeze_run_id": _positive_int(
            runtime_binding.get("run_id"),
            field="previous annual freeze run id",
        ),
        "previous_runtime_binding_fingerprint_sha256": _sha256_hex(
            runtime_binding.get("binding_fingerprint_sha256"),
            field="previous runtime binding fingerprint",
        ),
        "previous_annual_freeze_evidence_fingerprint_sha256": _sha256_hex(
            runtime_binding.get("freeze_evidence_fingerprint"),
            field="previous annual freeze evidence fingerprint",
        ),
        "expected_next_run_number": EXPECTED_2017_RUN_NUMBER,
        "expected_next_run_attempt": EXPECTED_2017_RUN_ATTEMPT,
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
        "preflight_read_only": True,
        "next_gate": (
            "ANNUAL_PATTERN_CATALOGUE_2017_EXECUTION_AUTHORIZATION_BEFORE_RUN"
        ),
    }
    value["preflight_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    validate_2017_execution_preflight(value)
    return value


def validate_2017_execution_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _sha256_hex(
        value.get("preflight_fingerprint_sha256"),
        field="preflight fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("preflight_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-523 preflight fingerprint mismatch")

    exact = {
        "decision": "DEC-523",
        "version": "fmp-annual-catalogue-2017-execution-preflight-v1",
        "runtime_binding_source_blob_sha": EXPECTED_RUNTIME_BINDING_SOURCE_BLOB_SHA,
        "active_workflow_blob_sha": EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        "source_runtime_binding_decision": "DEC-522",
        "source_runtime_binding_version": (
            "fmp-annual-catalogue-2016-run377-evidence-review-v1"
        ),
        "stage": (
            "ANNUAL_CATALOGUE_2017_EXECUTION_PREFLIGHT_"
            "PREDECESSOR_BOUND_AUTHORIZATION_LOCKED"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "annual_segment_label": "2017",
        "prior_segment_required": True,
        "prior_segment_label": "2016",
        "annual_workflow_run_count": 3,
        "failed_first_run_id": FAILED_FIRST_RUN_ID,
        "successful_2015_run_number": 376,
        "successful_2015_run_attempt": 1,
        "successful_2016_run_number": 377,
        "successful_2016_run_attempt": 1,
        "expected_next_run_number": 378,
        "expected_next_run_attempt": 1,
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
        "preflight_read_only": True,
        "next_gate": (
            "ANNUAL_PATTERN_CATALOGUE_2017_EXECUTION_AUTHORIZATION_BEFORE_RUN"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-523 {field} mismatch")

    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    for field in (
        "successful_2015_run_id",
        "successful_2016_run_id",
        "previous_annual_freeze_run_id",
    ):
        _positive_int(value.get(field), field=field)
    for field in (
        "successful_2015_run_head_sha",
        "successful_2016_run_head_sha",
    ):
        _validate_commit(value.get(field), field=field)
    for field in (
        "source_runtime_binding_fingerprint_sha256",
        "previous_runtime_binding_fingerprint_sha256",
        "previous_annual_freeze_evidence_fingerprint_sha256",
    ):
        _sha256_hex(value.get(field), field=field)
    if value.get("previous_annual_freeze_run_id") != value.get(
        "successful_2016_run_id"
    ):
        raise ValueError("DEC-523 predecessor run identity mismatch")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2017_EXECUTION_PREFLIGHT_DECISION",
    "ANNUAL_CATALOGUE_2017_EXECUTION_PREFLIGHT_VERSION",
    "build_2017_execution_preflight",
    "validate_2017_execution_preflight",
    "validate_2017_execution_preflight_sources",
]
