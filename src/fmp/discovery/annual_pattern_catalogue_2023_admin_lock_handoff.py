from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2023_dispatch_preflight import _validate_annual_inventory
from .annual_pattern_catalogue_2023_main_lock_readiness import (
    validate_2023_main_lock_readiness,
)

DECISION = "DEC-613"
VERSION = "fmp-annual-catalogue-2023-admin-lock-handoff-v1"
DEC612_HEAD = "895b9ad311bd5159b2591dcfc8da714191574d00"
DEC612_RUN_ID = 37791444781
DEC612_ARTIFACT_ID = 11555414803
DEC612_ZIP_SHA256 = "48b4512002af76c4fe88a256cff8ddc558d185d18411f2f9d8fd9b32fba80bf3"
DEC612_CANONICAL_SHA256 = "cc89cf90e820341a48d41cdd5518105dd99f3c867c9ec43b8c7d989a2535d0c5"
DEC612_FINGERPRINT = "d9555c20a7d7a5a2d4bc79f9dd621e7a6d73e1ac9340cfec81348dc4e5f6a787"
DEC612_SOURCE = "src/fmp/discovery/annual_pattern_catalogue_2023_main_lock_readiness.py"
DEC612_SOURCE_BLOB_SHA = "e4c76ef4993f03d51200139dee708250cf40e80f"

REQUIRED_HUMAN_PROOFS = (
    "independent_read_access_to_effective_main_protection_and_inherited_rulesets",
    "explicit_admin_approval_and_proven_no_bypass_or_concurrent_main_updates",
    "lock_applied_after_any_dispatch_controller_source_is_merged",
    "lock_remains_enforced_across_entire_server_side_dispatch_request",
    "current_main_matches_independently_reviewed_dispatch_source_commit",
    "source_runtime_and_dec609_dec610_dec611_dec612_evidence_reauthenticated",
    "exact_ten_run_history_and_unconsumed_run_385_verified",
    "separate_run385_action_decision_reviewed_before_single_submission",
    "failure_is_non_retryable_and_run_result_is_not_claimed_by_submission",
    "subsequent_2023_freeze_and_cell_results_reviewed_before_unlock",
)

FORBIDDEN = (
    "main_exclusive_lock_proven", "dispatch_atomic_to_vetted_sha",
    "annual_workflow_dispatch_authorized", "dispatch_action_executed",
    "protected_history_access_authorized", "rerun_authorized", "retry_authorized",
    "replacement_run_authorized", "run_386_or_later_authorized",
    "next_segment_execution_authorized", "cross_year_comparison_authorized",
    "cross_year_result_production_authorized", "strategy_v1_synthesis_authorized",
    "promotion_authorized", "phase8b_authorized", "demo_order_authorized",
    "broker_mutation_authorized", "live_order_authorized",
    "real_money_authorized", "trading_authorized",
)


def _canonical(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha_for_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _check_commit(value: object, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-613 {field} must be 40-character commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-613 {field} must be hex") from exc
    if value.lower() != value:
        raise ValueError(f"DEC-613 {field} must be lowercase")
    return value


def build_2023_admin_lock_handoff(
    *,
    readiness: Mapping[str, object],
    repository_root: Path,
    main_branch: Mapping[str, object],
    annual_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    validate_2023_main_lock_readiness(readiness)
    if readiness.get("expected_head_sha") != DEC612_HEAD:
        raise ValueError("DEC-613 DEC-612 head mismatch")
    if readiness.get("readiness_fingerprint_sha256") != DEC612_FINGERPRINT:
        raise ValueError("DEC-613 DEC-612 fingerprint mismatch")
    if _digest(dict(readiness)) != DEC612_CANONICAL_SHA256:
        raise ValueError("DEC-613 DEC-612 canonical SHA-256 mismatch")
    if readiness.get("dispatch_blocked") is not True or readiness.get(
        "dispatch_action_executed"
    ) is not False:
        raise ValueError("DEC-613 source has consumed dispatch authority")
    path = Path(repository_root) / DEC612_SOURCE
    if not path.is_file() or _sha_for_blob(path) != DEC612_SOURCE_BLOB_SHA:
        raise ValueError("DEC-613 DEC-612 source blob drift")

    head = _check_commit(expected_head_sha, "expected_head_sha")
    if main_branch.get("name") != "main":
        raise ValueError("DEC-613 branch must be main")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping) or commit.get("sha") != head:
        raise ValueError("DEC-613 main changed since checkout")
    if type(main_branch.get("protected")) is not bool:
        raise ValueError("DEC-613 missing current main protection flag")
    inventory = _validate_annual_inventory(annual_runs)
    if inventory.get("successful_2022_run_id") != 37663157285:
        raise ValueError("DEC-613 predecessor not frozen")

    result: dict[str, object] = {
        "decision": DECISION,
        "version": VERSION,
        "stage": "ANNUAL_CATALOGUE_2023_ADMIN_LOCK_HANDOFF_PREPARED",
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": head,
        "source_dec612_head_sha": DEC612_HEAD,
        "source_dec612_workflow_run_id": DEC612_RUN_ID,
        "source_dec612_artifact_id": DEC612_ARTIFACT_ID,
        "source_dec612_zip_sha256": DEC612_ZIP_SHA256,
        "source_dec612_canonical_sha256": DEC612_CANONICAL_SHA256,
        "source_dec612_fingerprint_sha256": DEC612_FINGERPRINT,
        "source_dec612_blob_sha": DEC612_SOURCE_BLOB_SHA,
        **inventory,
        "current_main_protected_reported": main_branch["protected"],
        "dec612_was_historical_read_only_snapshot": True,
        "admin_evidence_gathered_by_this_packet": False,
        "human_proof_required": True,
        "required_human_proofs": list(REQUIRED_HUMAN_PROOFS),
        "annual_segment_label": "2023",
        "expected_run_number": 385,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": 37663157285,
        "preflight_read_only": True,
        "dispatch_blocked": True,
        "dispatch_command_present": False,
        "dispatch_result_claimed": False,
        **{field: False for field in FORBIDDEN},
        "next_gate": "HUMAN_ADMIN_EXCLUSIVE_MAIN_LOCK_WITNESS_AND_SEPARATE_DISPATCH_DECISION",
    }
    result["handoff_fingerprint_sha256"] = _digest(result)
    validate_2023_admin_lock_handoff(result)
    return result


def validate_2023_admin_lock_handoff(value: Mapping[str, object]) -> Mapping[str, object]:
    fp = value.get("handoff_fingerprint_sha256")
    if not isinstance(fp, str) or len(fp) != 64:
        raise ValueError("DEC-613 missing fingerprint")
    unsigned = dict(value)
    unsigned.pop("handoff_fingerprint_sha256", None)
    if _digest(unsigned) != fp:
        raise ValueError("DEC-613 fingerprint mismatch")
    expected: dict[str, object] = {
        "decision": DECISION, "version": VERSION,
        "stage": "ANNUAL_CATALOGUE_2023_ADMIN_LOCK_HANDOFF_PREPARED",
        "repository_full_name": "Dtwosam/FMP",
        "source_dec612_head_sha": DEC612_HEAD,
        "source_dec612_workflow_run_id": DEC612_RUN_ID,
        "source_dec612_artifact_id": DEC612_ARTIFACT_ID,
        "source_dec612_zip_sha256": DEC612_ZIP_SHA256,
        "source_dec612_canonical_sha256": DEC612_CANONICAL_SHA256,
        "source_dec612_fingerprint_sha256": DEC612_FINGERPRINT,
        "source_dec612_blob_sha": DEC612_SOURCE_BLOB_SHA,
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
        "successful_2022_run_id": 37663157285,
        "dec612_was_historical_read_only_snapshot": True,
        "admin_evidence_gathered_by_this_packet": False,
        "human_proof_required": True,
        "required_human_proofs": list(REQUIRED_HUMAN_PROOFS),
        "annual_segment_label": "2023",
        "expected_run_number": 385,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": 37663157285,
        "preflight_read_only": True,
        "dispatch_blocked": True,
        "dispatch_command_present": False,
        "dispatch_result_claimed": False,
        **{field: False for field in FORBIDDEN},
        "next_gate": "HUMAN_ADMIN_EXCLUSIVE_MAIN_LOCK_WITNESS_AND_SEPARATE_DISPATCH_DECISION",
    }
    allowed=set(expected) | {
        "expected_head_sha", "current_main_protected_reported",
        "handoff_fingerprint_sha256",
    }
    if set(value) != allowed:
        raise ValueError("DEC-613 unauthorized handoff fields")
    _check_commit(value.get("expected_head_sha"), "expected_head_sha")
    if type(value.get("current_main_protected_reported")) is not bool:
        raise ValueError("DEC-613 missing exact protected bool")
    for field, wanted in expected.items():
        actual=value.get(field)
        if isinstance(wanted,bool):
            valid=actual is wanted
        elif type(wanted) is int:
            valid=type(actual) is int and actual==wanted
        else:
            valid=actual==wanted
        if not valid:
            raise ValueError(f"DEC-613 {field} mismatch")
    return value


__all__ = [
    "build_2023_admin_lock_handoff",
    "validate_2023_admin_lock_handoff",
    "REQUIRED_HUMAN_PROOFS",
]
