from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2018_run380_evidence_review import (
    ANNUAL_CATALOGUE_2018_RUN380_EVIDENCE_REVIEW_DECISION,
    ANNUAL_CATALOGUE_2018_RUN380_EVIDENCE_REVIEW_VERSION,
    validate_2018_run380_evidence_review,
)


ANNUAL_CATALOGUE_2019_EXECUTION_PREFLIGHT_DECISION = "DEC-556"
ANNUAL_CATALOGUE_2019_EXECUTION_PREFLIGHT_VERSION = (
    "fmp-annual-catalogue-2019-execution-preflight-v1"
)

RUNTIME_BINDING_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_2018_run380_evidence_review.py"
)
EXPECTED_RUNTIME_BINDING_SOURCE_BLOB_SHA = (
    "c44123cb04a8f476cf3efdb635bd1efb1d072df1"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)

FAILED_FIRST_RUN_ID = 37126711695
FAILED_FIRST_RUN_HEAD_SHA = "fd85a886d07234ad584dcca08692b37e6af54b2e"
FAILED_RUN376_ID = 37191637168
FAILED_RUN376_HEAD_SHA = "4c14fa7db6eb812b89ecb79201f7e298fa9c04f3"
SUCCESSFUL_2015_RUN_NUMBER = 377
SUCCESSFUL_2015_RUN_ID = 37198002653
SUCCESSFUL_2015_RUN_HEAD_SHA = "a89db974be9a94481e7ed0990476bc661012f1e4"
SUCCESSFUL_2016_RUN_NUMBER = 378
SUCCESSFUL_2016_RUN_ID = 37206992367
SUCCESSFUL_2016_RUN_HEAD_SHA = "2524fde355349581c9440a172d0384c3cbce31ed"
SUCCESSFUL_2017_RUN_NUMBER = 379
SUCCESSFUL_2017_RUN_ID = 37227536041
SUCCESSFUL_2017_RUN_HEAD_SHA = "7b4c1ef8573e280c067443b72f1534d9091d5b7f"
SUCCESSFUL_2018_RUN_NUMBER = 380
SUCCESSFUL_2018_RUN_ID = 37237817538
SUCCESSFUL_2018_RUN_HEAD_SHA = "30971a996f514670a6f836d8e45cf80137197a4f"

SOURCE_RUNTIME_BINDING_RECOVERY_WORKFLOW_RUN_ID = 37240186365
SOURCE_RUNTIME_BINDING_RECOVERY_HEAD_SHA = (
    "b0de575d0ba564de523ba8e23ed05f052ae756a3"
)
SOURCE_RUNTIME_BINDING_ARTIFACT_ID = 11317140969
SOURCE_RUNTIME_BINDING_ARTIFACT_DIGEST = (
    "sha256:2d158ae5dc2040570c1738c6700b96d34d05820abe3cd71f91b3389c469094b5"
)
EXPECTED_RUNTIME_BINDING_FINGERPRINT_SHA256 = (
    "09950f6bfb577c4abe17a2466e466a08585fbcd05359ad5fa6c4bad16cce5fda"
)
EXPECTED_FREEZE_EVIDENCE_FINGERPRINT_SHA256 = (
    "355a1e5ca9282300a7a38e24dd3009ebe8470d1f029e62c38860bf710ac80559"
)
EXPECTED_2019_RUN_NUMBER = 381
EXPECTED_2019_RUN_ATTEMPT = 1

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
        raise ValueError(f"DEC-556 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-556 {field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-556 {field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-556 {field} must be hexadecimal") from exc
    return value.lower()


def _positive_int(value: object, *, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"DEC-556 {field} must be a positive integer")
    return value


def validate_2019_execution_preflight_sources(
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
    for field, (source_path, expected_sha) in expected.items():
        if not source_path.is_file():
            raise ValueError(f"DEC-556 source file missing: {source_path}")
        sha = _git_blob_sha(source_path)
        if sha != expected_sha:
            raise ValueError(f"DEC-556 {field} mismatch")
        actual[field] = sha

    if ANNUAL_CATALOGUE_2018_RUN380_EVIDENCE_REVIEW_DECISION != "DEC-555":
        raise ValueError("DEC-556 runtime binding decision drift")
    if (
        ANNUAL_CATALOGUE_2018_RUN380_EVIDENCE_REVIEW_VERSION
        != "fmp-annual-catalogue-2018-run380-evidence-review-v1"
    ):
        raise ValueError("DEC-556 runtime binding version drift")
    return actual


def _validate_run_inventory(
    value: Mapping[str, object],
    *,
    runtime_binding: Mapping[str, object],
) -> dict[str, object]:
    runs = value.get("workflow_runs")
    if not isinstance(runs, list) or len(runs) != 6:
        raise ValueError(
            "DEC-556 requires exactly six annual workflow dispatch runs"
        )

    by_number: dict[int, Mapping[str, object]] = {}
    for raw in runs:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-556 workflow run row malformed")
        number = raw.get("run_number")
        if not isinstance(number, int) or isinstance(number, bool):
            raise ValueError("DEC-556 workflow run number malformed")
        if number in by_number:
            raise ValueError("DEC-556 duplicate workflow run number")
        by_number[number] = raw

    if set(by_number) != {1, 376, 377, 378, 379, 380}:
        raise ValueError("DEC-556 workflow run inventory mismatch")

    exact_rows = {
        1: {
            "id": FAILED_FIRST_RUN_ID,
            "run_number": 1,
            "run_attempt": 1,
            "event": "workflow_dispatch",
            "head_branch": "main",
            "head_sha": FAILED_FIRST_RUN_HEAD_SHA,
            "status": "completed",
            "conclusion": "failure",
        },
        376: {
            "id": FAILED_RUN376_ID,
            "run_number": 376,
            "run_attempt": 1,
            "event": "workflow_dispatch",
            "head_branch": "main",
            "head_sha": FAILED_RUN376_HEAD_SHA,
            "status": "completed",
            "conclusion": "failure",
        },
        377: {
            "id": SUCCESSFUL_2015_RUN_ID,
            "run_number": 377,
            "run_attempt": 1,
            "event": "workflow_dispatch",
            "head_branch": "main",
            "head_sha": SUCCESSFUL_2015_RUN_HEAD_SHA,
            "status": "completed",
            "conclusion": "success",
        },
        378: {
            "id": SUCCESSFUL_2016_RUN_ID,
            "run_number": 378,
            "run_attempt": 1,
            "event": "workflow_dispatch",
            "head_branch": "main",
            "head_sha": SUCCESSFUL_2016_RUN_HEAD_SHA,
            "status": "completed",
            "conclusion": "success",
        },
        379: {
            "id": SUCCESSFUL_2017_RUN_ID,
            "run_number": 379,
            "run_attempt": 1,
            "event": "workflow_dispatch",
            "head_branch": "main",
            "head_sha": SUCCESSFUL_2017_RUN_HEAD_SHA,
            "status": "completed",
            "conclusion": "success",
        },
        380: {
            "id": SUCCESSFUL_2018_RUN_ID,
            "run_number": 380,
            "run_attempt": 1,
            "event": "workflow_dispatch",
            "head_branch": "main",
            "head_sha": SUCCESSFUL_2018_RUN_HEAD_SHA,
            "status": "completed",
            "conclusion": "success",
        },
    }
    for number, expected in exact_rows.items():
        row = by_number[number]
        for field, expected_value in expected.items():
            if row.get(field) != expected_value:
                raise ValueError(
                    f"DEC-556 annual run {number} {field} mismatch"
                )

    if (
        runtime_binding.get("previous_annual_freeze_run_id")
        != SUCCESSFUL_2017_RUN_ID
    ):
        raise ValueError("DEC-556 2017 predecessor run id mismatch")
    if runtime_binding.get("run_id") != SUCCESSFUL_2018_RUN_ID:
        raise ValueError("DEC-556 2018 run id mismatch")
    if runtime_binding.get("run_head_sha") != SUCCESSFUL_2018_RUN_HEAD_SHA:
        raise ValueError("DEC-556 2018 run head mismatch")

    return {
        "annual_workflow_run_count": 6,
        "failed_first_run_id": FAILED_FIRST_RUN_ID,
        "failed_run376_id": FAILED_RUN376_ID,
        "successful_2015_run_id": SUCCESSFUL_2015_RUN_ID,
        "successful_2015_run_number": SUCCESSFUL_2015_RUN_NUMBER,
        "successful_2015_run_attempt": 1,
        "successful_2015_run_head_sha": SUCCESSFUL_2015_RUN_HEAD_SHA,
        "successful_2016_run_id": SUCCESSFUL_2016_RUN_ID,
        "successful_2016_run_number": SUCCESSFUL_2016_RUN_NUMBER,
        "successful_2016_run_attempt": 1,
        "successful_2016_run_head_sha": SUCCESSFUL_2016_RUN_HEAD_SHA,
        "successful_2017_run_id": SUCCESSFUL_2017_RUN_ID,
        "successful_2017_run_number": SUCCESSFUL_2017_RUN_NUMBER,
        "successful_2017_run_attempt": 1,
        "successful_2017_run_head_sha": SUCCESSFUL_2017_RUN_HEAD_SHA,
        "successful_2018_run_id": SUCCESSFUL_2018_RUN_ID,
        "successful_2018_run_number": SUCCESSFUL_2018_RUN_NUMBER,
        "successful_2018_run_attempt": 1,
        "successful_2018_run_head_sha": SUCCESSFUL_2018_RUN_HEAD_SHA,
    }


def build_2019_execution_preflight(
    *,
    repository_root: Path,
    runtime_binding: Mapping[str, object],
    main_branch: Mapping[str, object],
    annual_workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2019_execution_preflight_sources(
        repository_root=Path(repository_root),
    )
    validate_2018_run380_evidence_review(runtime_binding)

    if runtime_binding.get("annual_segment_label") != "2018":
        raise ValueError("DEC-556 runtime binding segment mismatch")
    if runtime_binding.get("run_number") != SUCCESSFUL_2018_RUN_NUMBER:
        raise ValueError("DEC-556 runtime binding run number mismatch")
    if runtime_binding.get("run_attempt") != 1:
        raise ValueError("DEC-556 runtime binding run attempt mismatch")
    if runtime_binding.get("run_conclusion") != "success":
        raise ValueError("DEC-556 runtime binding conclusion mismatch")
    if runtime_binding.get("runtime_evidence_bound") is not True:
        raise ValueError("DEC-556 runtime evidence is not bound")
    if (
        runtime_binding.get("binding_fingerprint_sha256")
        != EXPECTED_RUNTIME_BINDING_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-556 runtime binding fingerprint mismatch")
    if (
        runtime_binding.get("freeze_evidence_fingerprint")
        != EXPECTED_FREEZE_EVIDENCE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-556 freeze evidence fingerprint mismatch")
    if runtime_binding.get("next_segment_execution_authorized") is not False:
        raise ValueError("DEC-556 source binding already authorizes next segment")
    if runtime_binding.get("trading_authorized") is not False:
        raise ValueError("DEC-556 source binding trading authority drift")

    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-556 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-556 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-556 main head mismatch")

    inventory = _validate_run_inventory(
        annual_workflow_runs,
        runtime_binding=runtime_binding,
    )

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2019_EXECUTION_PREFLIGHT_DECISION,
        "version": ANNUAL_CATALOGUE_2019_EXECUTION_PREFLIGHT_VERSION,
        **source,
        **inventory,
        "source_runtime_binding_decision": "DEC-555",
        "source_runtime_binding_version": (
            "fmp-annual-catalogue-2018-run380-evidence-review-v1"
        ),
        "source_runtime_binding_recovery_workflow_run_id": (
            SOURCE_RUNTIME_BINDING_RECOVERY_WORKFLOW_RUN_ID
        ),
        "source_runtime_binding_recovery_head_sha": (
            SOURCE_RUNTIME_BINDING_RECOVERY_HEAD_SHA
        ),
        "source_runtime_binding_fingerprint_sha256": (
            EXPECTED_RUNTIME_BINDING_FINGERPRINT_SHA256
        ),
        "source_runtime_binding_artifact_id": SOURCE_RUNTIME_BINDING_ARTIFACT_ID,
        "source_runtime_binding_artifact_digest": (
            SOURCE_RUNTIME_BINDING_ARTIFACT_DIGEST
        ),
        "stage": (
            "ANNUAL_CATALOGUE_2019_EXECUTION_PREFLIGHT_"
            "PREDECESSOR_BOUND_AUTHORIZATION_LOCKED"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": expected_head_sha,
        "annual_segment_label": "2019",
        "prior_segment_required": True,
        "prior_segment_label": "2018",
        "previous_annual_freeze_run_id": SUCCESSFUL_2018_RUN_ID,
        "previous_runtime_binding_fingerprint_sha256": (
            EXPECTED_RUNTIME_BINDING_FINGERPRINT_SHA256
        ),
        "previous_annual_freeze_evidence_fingerprint_sha256": (
            EXPECTED_FREEZE_EVIDENCE_FINGERPRINT_SHA256
        ),
        "expected_next_run_number": EXPECTED_2019_RUN_NUMBER,
        "expected_next_run_attempt": EXPECTED_2019_RUN_ATTEMPT,
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
            "ANNUAL_PATTERN_CATALOGUE_2019_EXECUTION_AUTHORIZATION_BEFORE_RUN"
        ),
    }
    value["preflight_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    validate_2019_execution_preflight(value)
    return value


def validate_2019_execution_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _sha256_hex(
        value.get("preflight_fingerprint_sha256"),
        field="preflight fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("preflight_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-556 preflight fingerprint mismatch")

    exact = {
        "decision": "DEC-556",
        "version": "fmp-annual-catalogue-2019-execution-preflight-v1",
        "runtime_binding_source_blob_sha": EXPECTED_RUNTIME_BINDING_SOURCE_BLOB_SHA,
        "active_workflow_blob_sha": EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        "source_runtime_binding_decision": "DEC-555",
        "source_runtime_binding_version": (
            "fmp-annual-catalogue-2018-run380-evidence-review-v1"
        ),
        "source_runtime_binding_recovery_workflow_run_id": (
            SOURCE_RUNTIME_BINDING_RECOVERY_WORKFLOW_RUN_ID
        ),
        "source_runtime_binding_recovery_head_sha": (
            SOURCE_RUNTIME_BINDING_RECOVERY_HEAD_SHA
        ),
        "source_runtime_binding_fingerprint_sha256": (
            EXPECTED_RUNTIME_BINDING_FINGERPRINT_SHA256
        ),
        "source_runtime_binding_artifact_id": SOURCE_RUNTIME_BINDING_ARTIFACT_ID,
        "source_runtime_binding_artifact_digest": (
            SOURCE_RUNTIME_BINDING_ARTIFACT_DIGEST
        ),
        "stage": (
            "ANNUAL_CATALOGUE_2019_EXECUTION_PREFLIGHT_"
            "PREDECESSOR_BOUND_AUTHORIZATION_LOCKED"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "annual_segment_label": "2019",
        "prior_segment_required": True,
        "prior_segment_label": "2018",
        "annual_workflow_run_count": 6,
        "failed_first_run_id": FAILED_FIRST_RUN_ID,
        "failed_run376_id": FAILED_RUN376_ID,
        "successful_2015_run_number": 377,
        "successful_2015_run_attempt": 1,
        "successful_2016_run_number": 378,
        "successful_2016_run_attempt": 1,
        "successful_2017_run_number": 379,
        "successful_2017_run_attempt": 1,
        "successful_2018_run_number": 380,
        "successful_2018_run_attempt": 1,
        "previous_annual_freeze_run_id": SUCCESSFUL_2018_RUN_ID,
        "expected_next_run_number": 381,
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
            "ANNUAL_PATTERN_CATALOGUE_2019_EXECUTION_AUTHORIZATION_BEFORE_RUN"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-556 {field} mismatch")

    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    for field in (
        "successful_2015_run_id",
        "successful_2016_run_id",
        "successful_2017_run_id",
        "successful_2018_run_id",
        "previous_annual_freeze_run_id",
    ):
        _positive_int(value.get(field), field=field)
    for field in (
        "successful_2015_run_head_sha",
        "successful_2016_run_head_sha",
        "successful_2017_run_head_sha",
        "successful_2018_run_head_sha",
    ):
        _validate_commit(value.get(field), field=field)
    for field in (
        "source_runtime_binding_fingerprint_sha256",
        "previous_runtime_binding_fingerprint_sha256",
        "previous_annual_freeze_evidence_fingerprint_sha256",
    ):
        _sha256_hex(value.get(field), field=field)
    if value.get("previous_annual_freeze_run_id") != SUCCESSFUL_2018_RUN_ID:
        raise ValueError("DEC-556 predecessor run identity mismatch")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2019_EXECUTION_PREFLIGHT_DECISION",
    "ANNUAL_CATALOGUE_2019_EXECUTION_PREFLIGHT_VERSION",
    "EXPECTED_2019_RUN_ATTEMPT",
    "EXPECTED_2019_RUN_NUMBER",
    "build_2019_execution_preflight",
    "validate_2019_execution_preflight",
    "validate_2019_execution_preflight_sources",
]
