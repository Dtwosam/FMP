from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2022_run384_evidence_review import (
    validate_2022_run384_evidence_review,
)
from .annual_pattern_catalogue_method import (
    ANNUAL_PATTERN_CATALOGUE_METHOD_DECISION,
    CURRENTLY_OPEN_CATALOGUE_YEARS,
    PROTECTED_CATALOGUE_YEARS,
    PROTECTED_2023_2026_ACCESS_AUTHORIZED,
    collection_segments,
)
from .annual_pattern_catalogue_protocol import (
    ANNUAL_CATALOGUE_PROTOCOL_DECISION,
    FORMER_EXP061_RESERVED_2023_2026_CATALOGUE_USE_AUTHORIZED,
    FORMER_EXP061_RESERVED_2023_2026_REMAINS_UNTOUCHED_OOS_FOR_STRATEGY_V1,
    FULL_COLLECTION_CATALOGUE_USE_AUTHORIZED,
    validate_protocol,
)


ANNUAL_CATALOGUE_2023_EXECUTION_PREFLIGHT_DECISION = "DEC-602"
ANNUAL_CATALOGUE_2023_EXECUTION_PREFLIGHT_VERSION = (
    "fmp-annual-catalogue-2023-execution-preflight-v1"
)

RUNTIME_BINDING_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2022_run384_evidence_review.py"
)
EXPECTED_RUNTIME_BINDING_SOURCE_BLOB_SHA = (
    "7048781474ce74b8bbed0fd380f8edf4ec51491d"
)
METHOD_SOURCE_PATH = "src/fmp/discovery/annual_pattern_catalogue_method.py"
EXPECTED_METHOD_SOURCE_BLOB_SHA = "d7486296c2e953d6b4e7602c753c5529ccf5eef2"
PROTOCOL_SOURCE_PATH = "src/fmp/discovery/annual_pattern_catalogue_protocol.py"
EXPECTED_PROTOCOL_SOURCE_BLOB_SHA = "5ddd987cc480e6e31c0cd45328eba16cf690dee9"
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = (
    "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
)

SOURCE_RUNTIME_BINDING_WORKFLOW_RUN_ID = 37670106681
SOURCE_RUNTIME_BINDING_WORKFLOW_HEAD_SHA = (
    "a08512973deb127f16e199c6ecd2876e0fc8d8e0"
)
SOURCE_RUNTIME_BINDING_ARTIFACT_ID = 11504596272
SOURCE_RUNTIME_BINDING_ARTIFACT_DIGEST = (
    "sha256:45e4436ce5536c7df7ed8a3af99d9dc911025ec441a554de627d4adf8de1f755"
)
EXPECTED_RUNTIME_BINDING_CANONICAL_SHA256 = (
    "7e36345fc0ca8592e5f5ede41b9afcfdc9becff72d2415b7e6741ed2352923ac"
)
EXPECTED_RUNTIME_BINDING_FINGERPRINT_SHA256 = (
    "926832634d5836b158d780e21886692e762709104a6d0048c54a75c77ad2f352"
)

FAILED_RUNS = {
    1: (37126711695, "fd85a886d07234ad584dcca08692b37e6af54b2e"),
    376: (37191637168, "4c14fa7db6eb812b89ecb79201f7e298fa9c04f3"),
}
SUCCESSFUL_RUNS = {
    377: (37198002653, "a89db974be9a94481e7ed0990476bc661012f1e4"),
    378: (37206992367, "2524fde355349581c9440a172d0384c3cbce31ed"),
    379: (37227536041, "7b4c1ef8573e280c067443b72f1534d9091d5b7f"),
    380: (37237817538, "30971a996f514670a6f836d8e45cf80137197a4f"),
    381: (37310525635, "8bcee3a7a834743f08bd9ad73109bfc09609a2fe"),
    382: (37443770076, "681e81e021d4970a67b18370142d55b17ec68864"),
    383: (37531960014, "a1e194907c273a2fcdddfb4c24d64a96cfd8d263"),
    384: (37663157285, "dd79687adc4ec179c56f91939cb600e6746fab5d"),
}

EXPECTED_2023_RUN_NUMBER = 385
EXPECTED_2023_RUN_ATTEMPT = 1
EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID = 37663157285

ANNUAL_WORKFLOW_DISPATCH_AUTHORIZED = False
HISTORICAL_ARTIFACT_READ_AUTHORIZED = False
HISTORICAL_CATALOGUE_EXECUTION_AUTHORIZED = False
HISTORICAL_RESULT_PRODUCTION_AUTHORIZED = False
RERUN_AUTHORIZED = False
RETRY_AUTHORIZED = False
REPLACEMENT_RUN_AUTHORIZED = False
RUN_386_OR_LATER_AUTHORIZED = False
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
        raise ValueError(f"DEC-602 {field} must be a SHA-256 hex string")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-602 {field} must be hexadecimal") from exc
    return value.lower()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-602 {field} must be a 40-character Git commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-602 {field} must be hexadecimal") from exc
    return value.lower()


def validate_2023_execution_preflight_sources(
    *, repository_root: Path
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "runtime_binding_source_blob_sha": (
            root / RUNTIME_BINDING_SOURCE_PATH,
            EXPECTED_RUNTIME_BINDING_SOURCE_BLOB_SHA,
        ),
        "method_source_blob_sha": (
            root / METHOD_SOURCE_PATH,
            EXPECTED_METHOD_SOURCE_BLOB_SHA,
        ),
        "protocol_source_blob_sha": (
            root / PROTOCOL_SOURCE_PATH,
            EXPECTED_PROTOCOL_SOURCE_BLOB_SHA,
        ),
        "active_workflow_blob_sha": (
            root / ACTIVE_WORKFLOW_PATH,
            EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-602 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-602 {field} mismatch")
        actual[field] = sha

    if ANNUAL_PATTERN_CATALOGUE_METHOD_DECISION != "DEC-469":
        raise ValueError("DEC-602 governing method decision drift")
    labels = tuple(segment.label for segment in collection_segments())
    expected_labels = tuple(str(year) for year in range(2015, 2026)) + (
        "2026_YTD_TO_2026_08_20",
    )
    if labels != expected_labels:
        raise ValueError("DEC-602 annual collection segment inventory drift")
    if labels[labels.index("2022") + 1] != "2023":
        raise ValueError("DEC-602 2023 is not the successor to 2022")
    if 2023 in CURRENTLY_OPEN_CATALOGUE_YEARS:
        raise ValueError("DEC-602 2023 must remain outside the legacy open-year set")
    if 2023 not in PROTECTED_CATALOGUE_YEARS:
        raise ValueError("DEC-602 2023 protected-year inventory drift")
    if PROTECTED_2023_2026_ACCESS_AUTHORIZED:
        raise ValueError("DEC-602 DEC-469 protected-history gate drift")
    validate_protocol()
    if ANNUAL_CATALOGUE_PROTOCOL_DECISION != "DEC-470":
        raise ValueError("DEC-602 governing protocol decision drift")
    if not FULL_COLLECTION_CATALOGUE_USE_AUTHORIZED:
        raise ValueError("DEC-602 full-collection catalogue use is not authorized")
    if not FORMER_EXP061_RESERVED_2023_2026_CATALOGUE_USE_AUTHORIZED:
        raise ValueError("DEC-602 2023-2026 catalogue research use is not authorized")
    if FORMER_EXP061_RESERVED_2023_2026_REMAINS_UNTOUCHED_OOS_FOR_STRATEGY_V1:
        raise ValueError("DEC-602 protected-history untouched-OOS claim drift")
    return actual


def _validate_run_inventory(value: Mapping[str, object]) -> dict[str, object]:
    runs = value.get("workflow_runs")
    if not isinstance(runs, list) or len(runs) != 10:
        raise ValueError("DEC-602 requires exactly ten annual workflow dispatch runs")

    by_number: dict[int, Mapping[str, object]] = {}
    for raw in runs:
        if not isinstance(raw, Mapping):
            raise ValueError("DEC-602 workflow run row malformed")
        number = raw.get("run_number")
        if not isinstance(number, int) or isinstance(number, bool):
            raise ValueError("DEC-602 workflow run number malformed")
        if number in by_number:
            raise ValueError("DEC-602 duplicate workflow run number")
        by_number[number] = raw

    expected_numbers = {1, 376, 377, 378, 379, 380, 381, 382, 383, 384}
    if set(by_number) != expected_numbers:
        raise ValueError("DEC-602 workflow run inventory mismatch")

    for number, (run_id, head_sha) in FAILED_RUNS.items():
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
                raise ValueError(f"DEC-602 annual run {number} {field} mismatch")

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
                raise ValueError(f"DEC-602 annual run {number} {field} mismatch")

    return {
        "annual_workflow_run_count": 10,
        "successful_2021_run_id": SUCCESSFUL_RUNS[383][0],
        "successful_2021_run_number": 383,
        "successful_2022_run_id": SUCCESSFUL_RUNS[384][0],
        "successful_2022_run_number": 384,
        "successful_2022_run_attempt": 1,
        "successful_2022_run_head_sha": SUCCESSFUL_RUNS[384][1],
    }


def build_2023_execution_preflight(
    *,
    repository_root: Path,
    runtime_binding: Mapping[str, object],
    main_branch: Mapping[str, object],
    annual_workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    source = validate_2023_execution_preflight_sources(
        repository_root=Path(repository_root),
    )
    validate_2022_run384_evidence_review(runtime_binding)

    if runtime_binding.get("run_id") != EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID:
        raise ValueError("DEC-602 source binding run id mismatch")
    if runtime_binding.get("annual_segment_label") != "2022":
        raise ValueError("DEC-602 source binding segment mismatch")
    if runtime_binding.get("runtime_evidence_bound") is not True:
        raise ValueError("DEC-602 source binding evidence is not bound")
    if runtime_binding.get("binding_fingerprint_sha256") != (
        EXPECTED_RUNTIME_BINDING_FINGERPRINT_SHA256
    ):
        raise ValueError("DEC-602 source binding fingerprint mismatch")
    if _sha256_bytes(_canonical_json(dict(runtime_binding))) != (
        EXPECTED_RUNTIME_BINDING_CANONICAL_SHA256
    ):
        raise ValueError("DEC-602 source binding canonical SHA-256 mismatch")
    if runtime_binding.get("final_required_annual_segment_bound") is not True:
        raise ValueError("DEC-602 inherited terminal claim missing")
    if runtime_binding.get("next_gate") != (
        "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_CROSS_YEAR_COMPARISON_PREFLIGHT"
    ):
        raise ValueError("DEC-602 inherited successor claim mismatch")
    for field in (
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
        if runtime_binding.get(field) is not False:
            raise ValueError(f"DEC-602 source binding {field} drift")

    expected_head_sha = _validate_commit(
        expected_head_sha,
        field="expected_head_sha",
    )
    if main_branch.get("name") != "main":
        raise ValueError("DEC-602 requires main branch metadata")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping) or commit.get("sha") != expected_head_sha:
        raise ValueError("DEC-602 main head mismatch")

    inventory = _validate_run_inventory(annual_workflow_runs)

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2023_EXECUTION_PREFLIGHT_DECISION,
        "version": ANNUAL_CATALOGUE_2023_EXECUTION_PREFLIGHT_VERSION,
        **source,
        **inventory,
        "source_runtime_binding_decision": "DEC-601",
        "source_runtime_binding_workflow_run_id": (
            SOURCE_RUNTIME_BINDING_WORKFLOW_RUN_ID
        ),
        "source_runtime_binding_workflow_head_sha": (
            SOURCE_RUNTIME_BINDING_WORKFLOW_HEAD_SHA
        ),
        "source_runtime_binding_artifact_id": SOURCE_RUNTIME_BINDING_ARTIFACT_ID,
        "source_runtime_binding_artifact_digest": (
            SOURCE_RUNTIME_BINDING_ARTIFACT_DIGEST
        ),
        "source_runtime_binding_canonical_sha256": (
            EXPECTED_RUNTIME_BINDING_CANONICAL_SHA256
        ),
        "source_runtime_binding_fingerprint_sha256": (
            EXPECTED_RUNTIME_BINDING_FINGERPRINT_SHA256
        ),
        "source_final_required_annual_segment_bound_claim": True,
        "source_next_gate_claim": (
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_CROSS_YEAR_COMPARISON_PREFLIGHT"
        ),
        "source_terminal_successor_claim_superseded_by_dec469_dec470": True,
        "governing_method_decision": "DEC-469",
        "governing_protocol_decision": "DEC-470",
        "collection_segment_count": 12,
        "protected_catalogue_segment": True,
        "protocol_full_collection_catalogue_use_authorized": True,
        "protocol_2023_2026_catalogue_use_authorized": True,
        "protocol_2023_2026_remains_untouched_oos_for_strategy_v1": False,
        "collection_terminal_segment_label": "2026_YTD_TO_2026_08_20",
        "stage": (
            "ANNUAL_CATALOGUE_2023_EXECUTION_PREFLIGHT_"
            "PREDECESSOR_BOUND_AUTHORIZATION_LOCKED"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": expected_head_sha,
        "annual_segment_label": "2023",
        "prior_segment_required": True,
        "prior_segment_label": "2022",
        "previous_annual_freeze_run_id": EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID,
        "expected_next_run_number": EXPECTED_2023_RUN_NUMBER,
        "expected_next_run_attempt": EXPECTED_2023_RUN_ATTEMPT,
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
        "run_386_or_later_authorized": RUN_386_OR_LATER_AUTHORIZED,
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
        "preflight_read_only": True,
        "next_gate": (
            "ANNUAL_PATTERN_CATALOGUE_2023_EXECUTION_AUTHORIZATION_BEFORE_RUN"
        ),
    }
    value["preflight_fingerprint_sha256"] = _sha256_bytes(_canonical_json(value))
    validate_2023_execution_preflight(value)
    return value


def validate_2023_execution_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = _sha256_hex(
        value.get("preflight_fingerprint_sha256"),
        field="preflight fingerprint",
    )
    unsigned = dict(value)
    unsigned.pop("preflight_fingerprint_sha256", None)
    if _sha256_bytes(_canonical_json(unsigned)) != fingerprint:
        raise ValueError("DEC-602 preflight fingerprint mismatch")

    exact = {
        "decision": "DEC-602",
        "version": "fmp-annual-catalogue-2023-execution-preflight-v1",
        "source_runtime_binding_decision": "DEC-601",
        "source_runtime_binding_workflow_run_id": SOURCE_RUNTIME_BINDING_WORKFLOW_RUN_ID,
        "source_runtime_binding_workflow_head_sha": SOURCE_RUNTIME_BINDING_WORKFLOW_HEAD_SHA,
        "source_runtime_binding_artifact_id": SOURCE_RUNTIME_BINDING_ARTIFACT_ID,
        "source_runtime_binding_artifact_digest": SOURCE_RUNTIME_BINDING_ARTIFACT_DIGEST,
        "source_runtime_binding_canonical_sha256": EXPECTED_RUNTIME_BINDING_CANONICAL_SHA256,
        "source_runtime_binding_fingerprint_sha256": EXPECTED_RUNTIME_BINDING_FINGERPRINT_SHA256,
        "source_final_required_annual_segment_bound_claim": True,
        "source_next_gate_claim": (
            "READ_ONLY_ANNUAL_PATTERN_CATALOGUE_CROSS_YEAR_COMPARISON_PREFLIGHT"
        ),
        "source_terminal_successor_claim_superseded_by_dec469_dec470": True,
        "governing_method_decision": "DEC-469",
        "governing_protocol_decision": "DEC-470",
        "collection_segment_count": 12,
        "protected_catalogue_segment": True,
        "protocol_full_collection_catalogue_use_authorized": True,
        "protocol_2023_2026_catalogue_use_authorized": True,
        "protocol_2023_2026_remains_untouched_oos_for_strategy_v1": False,
        "collection_terminal_segment_label": "2026_YTD_TO_2026_08_20",
        "repository_full_name": "Dtwosam/FMP",
        "annual_segment_label": "2023",
        "prior_segment_required": True,
        "prior_segment_label": "2022",
        "annual_workflow_run_count": 10,
        "successful_2022_run_id": EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID,
        "successful_2022_run_number": 384,
        "successful_2022_run_attempt": 1,
        "previous_annual_freeze_run_id": EXPECTED_PREVIOUS_ANNUAL_FREEZE_RUN_ID,
        "expected_next_run_number": 385,
        "expected_next_run_attempt": 1,
        "annual_workflow_dispatch_authorized": False,
        "historical_artifact_read_authorized": False,
        "historical_catalogue_execution_authorized": False,
        "historical_result_production_authorized": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "run_386_or_later_authorized": False,
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
        "preflight_read_only": True,
        "next_gate": "ANNUAL_PATTERN_CATALOGUE_2023_EXECUTION_AUTHORIZATION_BEFORE_RUN",
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-602 {field} mismatch")
    _validate_commit(value.get("expected_head_sha"), field="expected_head_sha")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2023_EXECUTION_PREFLIGHT_DECISION",
    "ANNUAL_CATALOGUE_2023_EXECUTION_PREFLIGHT_VERSION",
    "EXPECTED_2023_RUN_ATTEMPT",
    "EXPECTED_2023_RUN_NUMBER",
    "build_2023_execution_preflight",
    "validate_2023_execution_preflight",
    "validate_2023_execution_preflight_sources",
]
