from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2023_dispatch_authorization import (
    validate_2023_dispatch_authorization,
)
from .annual_pattern_catalogue_2023_dispatch_preflight import (
    _validate_annual_inventory,
)

DECISION = "DEC-610"
VERSION = "fmp-annual-catalogue-2023-dispatch-action-preflight-v1"

DEC609_RUN_ID = 37770601661
DEC609_HEAD_SHA = "7d40ccaf79270162dd96a8a1e7024dd94c3a72b7"
DEC609_ARTIFACT_ID = 11547430955
DEC609_ARTIFACT_DIGEST = "sha256:8e33ab04cf87e0f2fe6b6b05fec53531dd0c9ff33fcc16abde920667ad154132"
DEC609_FINGERPRINT = "af91a248811f0cf291aea1fd94f4fff72eddd7e016b8d2fce2afc543bccb88fe"
DEC609_CANONICAL_SHA256 = "044f7ec28570660fa04fb886e6ab194c4a986427b8df86754241b44e6efbf3ad"

ANNUAL_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
PINNED_SOURCES = {
    "authorization_source_blob_sha": (
        "src/fmp/discovery/annual_pattern_catalogue_2023_dispatch_authorization.py",
        "b7f55dd68d5054c472b4e070521c411c02a4da3c",
    ),
    "dispatch_preflight_source_blob_sha": (
        "src/fmp/discovery/annual_pattern_catalogue_2023_dispatch_preflight.py",
        "fb4f8fa390e94a75a8d52c99cbc041e9bf1e8164",
    ),
    "active_workflow_blob_sha": (
        ANNUAL_WORKFLOW_PATH,
        "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
    ),
    "installed_gate_blob_sha": (
        "src/fmp/discovery/annual_pattern_catalogue_2023_runtime_authorization.py",
        "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
    ),
    "installed_runtime_blob_sha": (
        "src/fmp/discovery/annual_pattern_catalogue_runtime.py",
        "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3",
    ),
}

EXPECTED_RUN_NUMBER = 385
EXPECTED_RUN_ATTEMPT = 1
PREVIOUS_RUN_ID = 37663157285
TRUE_SOURCE_FIELDS = (
    "source_only_authorization",
    "runtime_authorization_installed",
    "runtime_gate_active",
    "authorization_contract_validated",
    "annual_workflow_dispatch_authorized",
    "historical_artifact_read_authorized",
    "historical_catalogue_execution_authorized",
    "historical_result_production_authorized",
    "source_authorization_protected_history_access_authorized",
    "protected_history_access_authorized",
    "protected_catalogue_segment",
    "protocol_full_collection_catalogue_use_authorized",
    "protocol_2023_2026_catalogue_use_authorized",
)
FALSE_AUTHORITY_FIELDS = (
    "dispatch_command_present",
    "dispatch_action_executed",
    "rerun_authorized",
    "retry_authorized",
    "replacement_run_authorized",
    "run_386_or_later_authorized",
    "next_segment_execution_authorized",
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
)


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(data)}\0".encode("ascii") + data
    ).hexdigest()


def _require_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-610 {field} must be a 40-character commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-610 {field} must be hexadecimal") from exc
    if value.lower() != value:
        raise ValueError(f"DEC-610 {field} must be lowercase")
    return value


def validate_2023_dispatch_action_preflight_sources(
    *, repository_root: Path
) -> dict[str, str]:
    root = Path(repository_root)
    actual = {}
    for field, (path, expected) in PINNED_SOURCES.items():
        candidate = root / path
        if not candidate.is_file():
            raise ValueError(f"DEC-610 missing source: {path}")
        digest = _git_blob_sha(candidate)
        if digest != expected:
            raise ValueError(f"DEC-610 {field} mismatch")
        actual[field] = digest
    return actual


def build_2023_dispatch_action_preflight(
    authorization: Mapping[str, object],
    *,
    repository_root: Path,
    main_branch: Mapping[str, object],
    annual_workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    sources = validate_2023_dispatch_action_preflight_sources(
        repository_root=repository_root
    )
    validate_2023_dispatch_authorization(authorization)
    if authorization.get("authorization_head_sha") != DEC609_HEAD_SHA:
        raise ValueError("DEC-610 source authorization head mismatch")
    if authorization.get("authorization_fingerprint_sha256") != DEC609_FINGERPRINT:
        raise ValueError("DEC-610 source authorization fingerprint mismatch")
    if _sha256(dict(authorization)) != DEC609_CANONICAL_SHA256:
        raise ValueError("DEC-610 source authorization canonical SHA-256 mismatch")
    for field in TRUE_SOURCE_FIELDS:
        if authorization.get(field) is not True:
            raise ValueError(f"DEC-610 source {field} must be true")
    for field in FALSE_AUTHORITY_FIELDS:
        if authorization.get(field) is not False:
            raise ValueError(f"DEC-610 source {field} must remain false")
    for field, expected in {
        "decision": "DEC-609",
        "authorization_scope": "2023_run_385_attempt_1_only",
        "repository_full_name": "Dtwosam/FMP",
        "annual_segment_label": "2023",
        "prior_segment_label": "2022",
        "governing_method_decision": "DEC-469",
        "governing_protocol_decision": "DEC-470",
        "previous_annual_freeze_run_id": PREVIOUS_RUN_ID,
        "expected_run_number": EXPECTED_RUN_NUMBER,
        "expected_run_attempt": EXPECTED_RUN_ATTEMPT,
    }.items():
        if type(expected) is int and type(authorization.get(field)) is not int:
            raise ValueError(f"DEC-610 source {field} type mismatch")
        if authorization.get(field) != expected:
            raise ValueError(f"DEC-610 source {field} mismatch")

    head = _require_commit(expected_head_sha, field="expected_head_sha")
    if main_branch.get("name") != "main":
        raise ValueError("DEC-610 requires main branch")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping) or commit.get("sha") != head:
        raise ValueError("DEC-610 main head mismatch")

    inventory = _validate_annual_inventory(annual_workflow_runs)
    if inventory["successful_2022_run_id"] != PREVIOUS_RUN_ID:
        raise ValueError("DEC-610 predecessor inventory mismatch")
    value: dict[str, object] = {
        "decision": DECISION,
        "version": VERSION,
        **sources,
        **inventory,
        "stage": "ANNUAL_CATALOGUE_2023_DISPATCH_ACTION_PREFLIGHT_READY",
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": head,
        "active_workflow_path": ANNUAL_WORKFLOW_PATH,
        "source_authorization_decision": "DEC-609",
        "source_authorization_workflow_run_id": DEC609_RUN_ID,
        "source_authorization_workflow_head_sha": DEC609_HEAD_SHA,
        "source_authorization_artifact_id": DEC609_ARTIFACT_ID,
        "source_authorization_artifact_digest": DEC609_ARTIFACT_DIGEST,
        "source_authorization_fingerprint_sha256": DEC609_FINGERPRINT,
        "source_authorization_canonical_sha256": DEC609_CANONICAL_SHA256,
        "authorization_head_sha": DEC609_HEAD_SHA,
        "governing_method_decision": "DEC-469",
        "governing_protocol_decision": "DEC-470",
        "annual_segment_label": "2023",
        "prior_segment_label": "2022",
        "previous_annual_freeze_run_id": PREVIOUS_RUN_ID,
        "expected_run_number": EXPECTED_RUN_NUMBER,
        "expected_run_attempt": EXPECTED_RUN_ATTEMPT,
        "dispatch_ref": "main",
        "dispatch_input_annual_segment_label": "2023",
        "dispatch_input_previous_annual_freeze_run_id": str(PREVIOUS_RUN_ID),
        "dispatch_parameters_frozen": True,
        "source_authorization_protected_history_access_authorized": True,
        "protected_catalogue_segment": True,
        "protocol_full_collection_catalogue_use_authorized": True,
        "protocol_2023_2026_catalogue_use_authorized": True,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "annual_workflow_dispatch_authorized": True,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "dispatch_command_present": False,
        "dispatch_action_executed": False,
        "preflight_read_only": True,
        # Source authorization is protected, but this preflight never accesses
        # historical market data or executes the annual catalogue.
        "protected_history_access_authorized": False,
        **{field: False for field in FALSE_AUTHORITY_FIELDS},
        "next_gate": "EXACT_2023_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN",
    }
    value["preflight_fingerprint_sha256"] = _sha256(value)
    validate_2023_dispatch_action_preflight(value)
    return value


def validate_2023_dispatch_action_preflight(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fp = value.get("preflight_fingerprint_sha256")
    if not isinstance(fp, str) or len(fp) != 64:
        raise ValueError("DEC-610 missing SHA-256 fingerprint")
    unsigned = dict(value)
    unsigned.pop("preflight_fingerprint_sha256", None)
    if _sha256(unsigned) != fp:
        raise ValueError("DEC-610 preflight fingerprint mismatch")

    exact: dict[str, object] = {
        "decision": DECISION,
        "version": VERSION,
        **{field: digest for field, (_, digest) in PINNED_SOURCES.items()},
        "annual_workflow_run_count": 10,
        "failed_run_1_id": 37126711695,
        "failed_run_376_id": 37191637168,
        "successful_2015_run_id": 37198002653,
        "successful_2016_run_id": 37206992367,
        "successful_2017_run_id": 37227536041,
        "successful_2018_run_id": 37237817538,
        "successful_2019_run_id": 37310525635,
        "successful_2020_run_id": 37443770076,
        "successful_2021_run_id": 37531960014,
        "successful_2022_run_id": PREVIOUS_RUN_ID,
        "stage": "ANNUAL_CATALOGUE_2023_DISPATCH_ACTION_PREFLIGHT_READY",
        "repository_full_name": "Dtwosam/FMP",
        "active_workflow_path": ANNUAL_WORKFLOW_PATH,
        "source_authorization_decision": "DEC-609",
        "source_authorization_workflow_run_id": DEC609_RUN_ID,
        "source_authorization_workflow_head_sha": DEC609_HEAD_SHA,
        "source_authorization_artifact_id": DEC609_ARTIFACT_ID,
        "source_authorization_artifact_digest": DEC609_ARTIFACT_DIGEST,
        "source_authorization_fingerprint_sha256": DEC609_FINGERPRINT,
        "source_authorization_canonical_sha256": DEC609_CANONICAL_SHA256,
        "authorization_head_sha": DEC609_HEAD_SHA,
        "governing_method_decision": "DEC-469",
        "governing_protocol_decision": "DEC-470",
        "annual_segment_label": "2023",
        "prior_segment_label": "2022",
        "previous_annual_freeze_run_id": PREVIOUS_RUN_ID,
        "expected_run_number": EXPECTED_RUN_NUMBER,
        "expected_run_attempt": EXPECTED_RUN_ATTEMPT,
        "dispatch_ref": "main",
        "dispatch_input_annual_segment_label": "2023",
        "dispatch_input_previous_annual_freeze_run_id": str(PREVIOUS_RUN_ID),
        "dispatch_parameters_frozen": True,
        "source_authorization_protected_history_access_authorized": True,
        "protected_catalogue_segment": True,
        "protocol_full_collection_catalogue_use_authorized": True,
        "protocol_2023_2026_catalogue_use_authorized": True,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "annual_workflow_dispatch_authorized": True,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "dispatch_command_present": False,
        "dispatch_action_executed": False,
        "preflight_read_only": True,
        "protected_history_access_authorized": False,
        **{field: False for field in FALSE_AUTHORITY_FIELDS},
        "next_gate": "EXACT_2023_ANNUAL_PATTERN_CATALOGUE_WORKFLOW_DISPATCH_ON_CURRENT_MAIN",
    }
    allowed = set(exact) | {"expected_head_sha", "preflight_fingerprint_sha256"}
    if set(value) != allowed:
        raise ValueError("DEC-610 fields missing or unauthorized extra fields")
    for key, expected in exact.items():
        actual = value.get(key)
        if type(expected) is bool:
            valid = actual is expected
        elif type(expected) is int:
            valid = type(actual) is int and actual == expected
        else:
            valid = actual == expected
        if not valid:
            raise ValueError(f"DEC-610 {key} mismatch")
    _require_commit(value.get("expected_head_sha"), field="expected_head_sha")
    return value


__all__ = [
    "DECISION", "VERSION", "DEC609_RUN_ID", "DEC609_HEAD_SHA",
    "build_2023_dispatch_action_preflight",
    "validate_2023_dispatch_action_preflight",
    "validate_2023_dispatch_action_preflight_sources",
]
