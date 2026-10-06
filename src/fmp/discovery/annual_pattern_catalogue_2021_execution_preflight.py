from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2020_run382_recovery_evidence_review import (
    ANNUAL_CATALOGUE_2020_RUN382_RECOVERY_EVIDENCE_REVIEW_DECISION,
    ANNUAL_CATALOGUE_2020_RUN382_RECOVERY_EVIDENCE_REVIEW_VERSION,
    validate_2020_run382_recovery_evidence,
)


ANNUAL_CATALOGUE_2021_EXECUTION_PREFLIGHT_DECISION = "DEC-580"
ANNUAL_CATALOGUE_2021_EXECUTION_PREFLIGHT_VERSION = (
    "fmp-annual-catalogue-2021-execution-preflight-v1"
)

RUNTIME_BINDING_SOURCE_PATH = (
    "src/fmp/discovery/"
    "annual_pattern_catalogue_2020_run382_recovery_evidence_review.py"
)
EXPECTED_RUNTIME_BINDING_SOURCE_BLOB_SHA = (
    "7c721121197b83e687fd2c76773773f8ab4c07ae"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)

SOURCE_RUNTIME_BINDING_RECOVERY_WORKFLOW_RUN_ID = 37447286936
SOURCE_RUNTIME_BINDING_RECOVERY_HEAD_SHA = (
    "2fdbcb85f4509ca5e4342cc06a284e1bcd109cc4"
)
SOURCE_RUNTIME_BINDING_ARTIFACT_ID = 11404455773
SOURCE_RUNTIME_BINDING_ARTIFACT_DIGEST = (
    "sha256:bfd0286ed48e1ee8690921275ec34485025d95f92579519d8e68398867d45d5c"
)
EXPECTED_RUNTIME_BINDING_FINGERPRINT_SHA256 = (
    "ebde4b5ee78421cc2afb4c12c4ff2603b6d01f1990fbfe683aed11d00653a76c"
)
EXPECTED_FREEZE_EVIDENCE_FINGERPRINT_SHA256 = (
    "53cd4475b2e9f70252bc4962666ce421daf7795d3e78defbb38ec948448e1c3c"
)

FAILED_FIRST_RUN_ID = 37126711695
FAILED_FIRST_RUN_HEAD_SHA = "fd85a886d07234ad584dcca08692b37e6af54b2e"
FAILED_RUN376_ID = 37191637168
FAILED_RUN376_HEAD_SHA = "4c14fa7db6eb812b89ecb79201f7e298fa9c04f3"

SUCCESSFUL_RUNS = {
    377: (37198002653, "a89db974be9a94481e7ed0990476bc661012f1e4"),
    378: (37206992367, "2524fde355349581c9440a172d0384c3cbce31ed"),
    379: (37227536041, "7b4c1ef8573e280c067443b72f1534d9091d5b7f"),
    380: (37237817538, "30971a996f514670a6f836d8e45cf80137197a4f"),
    381: (37310525635, "8bcee3a7a834743f08bd9ad73109bfc09609a2fe"),
    382: (37443770076, "681e81e021d4970a67b18370142d55b17ec68864"),
}
SUCCESSFUL_2020_RUN_ID = 37443770076
SUCCESSFUL_2020_RUN_HEAD_SHA = "681e81e021d4970a67b18370142d55b17ec68864"

EXPECTED_2021_RUN_NUMBER = 383
EXPECTED_2021_RUN_ATTEMPT = 1

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
        raise ValueError(f"DEC-580 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-580 {field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-580 {field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-580 {field} must be hexadecimal") from exc
    return value.lower()


def validate_2021_execution_preflight_sources(
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
            raise ValueError(f"DEC-580 source file missing: {source_path}")
        sha = _git_blob_sha(source_path)
        if sha != expected_sha:
            raise ValueError(f"DEC-580 {field} mismatch")
        actual[field] = sha

    if ANNUAL_CATALOGUE_2020_RUN382_RECOVERY_EVIDENCE_REVIEW_DECISION != "DEC-579":
        raise ValueError("DEC-580 runtime binding decision drift")
    if (
        ANNUAL_CATALOGUE_2020_RUN382_RECOVERY_EVIDENCE_REVIEW_VERSION
        != "fmp-annual-catalogue-2020-run382-recovery-evidence-review-v1"
    ):
        raise ValueError("DEC-580 runtime binding version drift")
    return actual


def _validate_run_inventory(
    value: Mapping[str, object],
    *,
    runtime_binding: Mapping[str, object],
) -> dict[str, object]:
    runs = value.get("workflow_runs")
    if not isinstance(runs, list) or len(runs) != 7:
        raise ValueError("DEC-580 requires exactly eight annual workflow dispatch runs")

    by_number: dict[int, Mapping[str, object]] = {}
    for raw in runs:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-580 workflow run row malformed")
        number = raw.get("run_number")
        if not isinstance(number, int) or isinstance(number, bool):
            raise ValueError("DEC-580 workflow run number malformed")
        if number in by_number:
            raise ValueError("DEC-580 duplicate workflow run number")
        by_number[number] = raw

    expected_numbers = {1, 376, 377, 378, 379, 380, 381, 382}
    if set(by_number) != expected_numbers:
        raise ValueError("DEC-580 workflow run inventory mismatch")

    failures = {
        1: (FAILED_FIRST_RUN_ID, FAILED_FIRST_RUN_HEAD_SHA),
        376: (FAILED_RUN376_ID, FAILED_RUN376_HEAD_SHA),
    }
    for number, (run_id, head_sha) in failures.items():
        row = by_number[number]
        exact = {
            "id": run_id,
            "run_number": number,
            "run_attempt": 1,
            "event": "workflow_dispatch",
            "head_branch": "main",
            "head_sha": head_sha,
            "status": "completed",
            "conclusion": "failure",
        }
        for field, expected in exact.items():
            if row.get(field) != expected:
                raise ValueError(
                    f"DEC-580 annual run {number} {field} mismatch"
                )

    for number, (run_id, head_sha) in SUCCESSFUL_RUNS.items():
        row = by_number[number]
        exact = {
            "id": run_id,
            "run_number": number,
            "run_attempt": 1,
            "event": "workflow_dispatch",
            "head_branch": "main",
            "head_sha": head_sha,
            "status": "completed",
            "conclusion": "success",
        }
        for field, expected in exact.items():
            if row.get(field) != expected:
                raise ValueError(
                    f"DEC-580 annual run {number} {field} mismatch"
                )

    if runtime_binding.get("run_id") != SUCCESSFUL_2020_RUN_ID:
        raise ValueError("DEC-580 2020 run id mismatch")
    if runtime_binding.get("run_head_sha") != SUCCESSFUL_2020_RUN_HEAD_SHA:
        raise ValueError("DEC-580 2020 run head mismatch")
    if runtime_binding.get("previous_annual_freeze_run_id") != 37310525635:
        raise ValueError("DEC-580 2019 predecessor run id mismatch")

    return {
        "annual_workflow_run_count": 8,
        "failed_first_run_id": FAILED_FIRST_RUN_ID,
        "failed_run376_id": FAILED_RUN376_ID,
        "successful_2015_run_id": SUCCESSFUL_RUNS[377][0],
        "successful_2015_run_number": 377,
        "successful_2016_run_id": SUCCESSFUL_RUNS[378][0],
        "successful_2016_run_number": 378,
        "successful_2017_run_id": SUCCESSFUL_RUNS[379][0],
        "successful_2017_run_number": 379,
        "successful_2018_run_id": SUCCESSFUL_RUNS[380][0],
        "successful_2018_run_number": 380,
        "successful_2019_run_id": SUCCESSFUL_RUNS[381][0],
        "successful_2019_run_number": 381,
        "successful_2019_run_attempt": 1,
        "successful_2019_run_head_sha": SUCCESSFUL_RUNS[381][1],
        "successful_2020_run_id": SUCCESSFUL_2020_RUN_ID,
        "successful_2020_run_number": 382,
        "successful_2020_run_attempt": 1,
        "successful_2020_run_head_sha": SUCCESSFUL_2020_RUN_HEAD_SHA,
    }


def build_2021_execution_preflight(
    *,
    repository_root: Path,
    runtime_binding: Mapping[str, object],
    main_branch: Mapping[str, object],
    annual_workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2021_execution_preflight_sources(
        repository_root=Path(repository_root),
    )
    validate_2020_run382_recovery_evidence(runtime_binding)

    if runtime_binding.get("annual_segment_label") != "2020":
        raise ValueError("DEC-580 runtime binding segment mismatch")
    if runtime_binding.get("run_number") != 382:
        raise ValueError("DEC-580 runtime binding run number mismatch")
    if runtime_binding.get("run_attempt") != 1:
        raise ValueError("DEC-580 runtime binding run attempt mismatch")
    if runtime_binding.get("run_conclusion") != "success":
        raise ValueError("DEC-580 runtime binding conclusion mismatch")
    if runtime_binding.get("runtime_evidence_bound") is not True:
        raise ValueError("DEC-580 runtime evidence is not bound")
    if runtime_binding.get("next_segment_execution_authorized") is not False:
        raise ValueError("DEC-580 source binding already authorizes next segment")
    if runtime_binding.get("trading_authorized") is not False:
        raise ValueError("DEC-580 source binding trading authority drift")

    binding_fingerprint = _sha256_hex(
        runtime_binding.get("binding_fingerprint_sha256"),
        field="runtime binding fingerprint",
    )
    if binding_fingerprint != EXPECTED_RUNTIME_BINDING_FINGERPRINT_SHA256:
        raise ValueError("DEC-580 runtime binding fingerprint mismatch")
    freeze_fingerprint = _sha256_hex(
        runtime_binding.get("freeze_evidence_fingerprint"),
        field="freeze evidence fingerprint",
    )
    if freeze_fingerprint != EXPECTED_FREEZE_EVIDENCE_FINGERPRINT_SHA256:
        raise ValueError("DEC-580 freeze evidence fingerprint mismatch")

    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-580 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping):
        raise ValueError("DEC-580 main commit is malformed")
    if commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-580 main head mismatch")

    inventory = _validate_run_inventory(
        annual_workflow_runs,
        runtime_binding=runtime_binding,
    )

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2021_EXECUTION_PREFLIGHT_DECISION,
        "version": ANNUAL_CATALOGUE_2021_EXECUTION_PREFLIGHT_VERSION,
        **source,
        **inventory,
        "source_runtime_binding_decision": "DEC-579",
        "source_runtime_binding_version": (
            "fmp-annual-catalogue-2020-run382-recovery-evidence-review-v1"
        ),
        "source_runtime_binding_recovery_workflow_run_id": (
            SOURCE_RUNTIME_BINDING_RECOVERY_WORKFLOW_RUN_ID
        ),
        "source_runtime_binding_recovery_head_sha": (
            SOURCE_RUNTIME_BINDING_RECOVERY_HEAD_SHA
        ),
        "source_runtime_binding_artifact_id": SOURCE_RUNTIME_BINDING_ARTIFACT_ID,
        "source_runtime_binding_artifact_digest": (
            SOURCE_RUNTIME_BINDING_ARTIFACT_DIGEST
        ),
        "source_runtime_binding_fingerprint_sha256": binding_fingerprint,
        "source_freeze_evidence_fingerprint_sha256": freeze_fingerprint,
        "stage": (
            "ANNUAL_CATALOGUE_2021_EXECUTION_PREFLIGHT_"
            "PREDECESSOR_BOUND_AUTHORIZATION_LOCKED"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": expected_head_sha,
        "annual_segment_label": "2021",
        "prior_segment_required": True,
        "prior_segment_label": "2020",
        "previous_annual_freeze_run_id": SUCCESSFUL_2020_RUN_ID,
        "expected_next_run_number": EXPECTED_2021_RUN_NUMBER,
        "expected_next_run_attempt": EXPECTED_2021_RUN_ATTEMPT,
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
            "ANNUAL_PATTERN_CATALOGUE_2021_EXECUTION_AUTHORIZATION_BEFORE_RUN"
        ),
    }
    value["preflight_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    validate_2021_execution_preflight(value)
    return value


def validate_2021_execution_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _sha256_hex(
        value.get("preflight_fingerprint_sha256"),
        field="preflight fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("preflight_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-580 preflight fingerprint mismatch")

    exact = {
        "decision": "DEC-580",
        "version": "fmp-annual-catalogue-2021-execution-preflight-v1",
        "runtime_binding_source_blob_sha": EXPECTED_RUNTIME_BINDING_SOURCE_BLOB_SHA,
        "active_workflow_blob_sha": EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        "source_runtime_binding_decision": "DEC-579",
        "source_runtime_binding_version": (
            "fmp-annual-catalogue-2020-run382-recovery-evidence-review-v1"
        ),
        "source_runtime_binding_recovery_workflow_run_id": (
            SOURCE_RUNTIME_BINDING_RECOVERY_WORKFLOW_RUN_ID
        ),
        "source_runtime_binding_recovery_head_sha": (
            SOURCE_RUNTIME_BINDING_RECOVERY_HEAD_SHA
        ),
        "source_runtime_binding_artifact_id": SOURCE_RUNTIME_BINDING_ARTIFACT_ID,
        "source_runtime_binding_artifact_digest": (
            SOURCE_RUNTIME_BINDING_ARTIFACT_DIGEST
        ),
        "source_runtime_binding_fingerprint_sha256": (
            EXPECTED_RUNTIME_BINDING_FINGERPRINT_SHA256
        ),
        "source_freeze_evidence_fingerprint_sha256": (
            EXPECTED_FREEZE_EVIDENCE_FINGERPRINT_SHA256
        ),
        "stage": (
            "ANNUAL_CATALOGUE_2021_EXECUTION_PREFLIGHT_"
            "PREDECESSOR_BOUND_AUTHORIZATION_LOCKED"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "annual_segment_label": "2021",
        "prior_segment_required": True,
        "prior_segment_label": "2020",
        "annual_workflow_run_count": 8,
        "failed_first_run_id": FAILED_FIRST_RUN_ID,
        "failed_run376_id": FAILED_RUN376_ID,
        "successful_2015_run_number": 377,
        "successful_2016_run_number": 378,
        "successful_2017_run_number": 379,
        "successful_2018_run_number": 380,
        "successful_2019_run_number": 381,
        "successful_2019_run_attempt": 1,
        "successful_2020_run_number": 382,
        "successful_2020_run_attempt": 1,
        "previous_annual_freeze_run_id": SUCCESSFUL_2020_RUN_ID,
        "expected_next_run_number": 383,
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
            "ANNUAL_PATTERN_CATALOGUE_2021_EXECUTION_AUTHORIZATION_BEFORE_RUN"
        ),
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-580 {field} mismatch")

    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    if (
        _sha256_hex(
            value.get("source_runtime_binding_fingerprint_sha256"),
            field="runtime binding fingerprint",
        )
        != EXPECTED_RUNTIME_BINDING_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-580 runtime binding fingerprint mismatch")
    if (
        _sha256_hex(
            value.get("source_freeze_evidence_fingerprint_sha256"),
            field="freeze evidence fingerprint",
        )
        != EXPECTED_FREEZE_EVIDENCE_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-580 freeze evidence fingerprint mismatch")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2021_EXECUTION_PREFLIGHT_DECISION",
    "ANNUAL_CATALOGUE_2021_EXECUTION_PREFLIGHT_VERSION",
    "EXPECTED_2021_RUN_ATTEMPT",
    "EXPECTED_2021_RUN_NUMBER",
    "build_2021_execution_preflight",
    "validate_2021_execution_preflight",
    "validate_2021_execution_preflight_sources",
]
