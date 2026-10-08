from __future__ import annotations

"""DEC-620: offline *claimed* lock continuity coverage; never authenticated authority."""

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2023_disarmed_tag_amendment_preview import _source
from .annual_pattern_catalogue_2023_tag_ref_guard_rehearsal import (
    ANNUAL_WORKFLOW_BLOB,
    ANNUAL_WORKFLOW_PATH,
    REQUIRED_JOBS,
    _is_candidate_tag,
    _is_sha,
    verify_original_workflow_order,
)

DECISION = "DEC-620"
VERSION = "fmp-phase8a-2023-lock-witness-continuity-coverage-v1"
INTERVALS = (
    "reviewed_sha_check_to_dispatch_submission",
    "dispatch_submission_to_server_ref_resolution",
    "server_ref_resolution_to_run_record",
    "run_record_to_post_dispatch_audit",
)
REQUIRED_CLAIMS = (
    "lock_effective",
    "ref_updates_blocked",
    "ref_deletion_blocked",
    "ref_recreation_blocked",
    "all_bypass_paths_blocked",
    "all_inherited_rules_visible",
)
RUN = 385
ATTEMPT = 1
PREDECESSOR_RUN_ID = 37663157285

# Each interval is a *claim* supplied by an untrusted JSON file, not a live API
# event or effective administrator setting. Even complete claimed coverage is
# insufficient evidence of actual continuous exclusive-lock enforcement.
WITNESS_KEYS = frozenset(("schema", "ref", "reviewed_commit_sha", "intervals"))
INTERVAL_KEYS = frozenset(("interval", "resolved_ref_sha", *REQUIRED_CLAIMS))
LOCKED_FALSE = (
    "witness_authenticated",
    "server_transaction_continuity_proven",
    "effective_no_bypass_rules_verified",
    "exclusive_main_lock_proven",
    "immutable_tag_lock_proven",
    "live_run385_state_verified",
    "reviewed_workflow_runtime_amendment_approved",
    "workflow_amendment_installed_by_this_report",
    "tag_created_by_this_report",
    "branch_or_ruleset_mutated_by_this_report",
    "workflow_dispatch_authorized_by_this_report",
    "run385_execution_authorized_by_this_report",
    "dispatch_action_executed",
    "historical_artifact_read_executed",
    "rerun_authorized",
    "retry_authorized",
    "replacement_run_authorized",
    "run386_or_later_authorized",
    "later_year_research_authorized",
    "cross_year_comparison_authorized",
    "strategy_synthesis_authorized",
    "promotion_authorized",
    "phase8b_authorized",
    "broker_mutation_authorized",
    "demo_order_authorized",
    "live_order_authorized",
    "real_money_authorized",
    "trading_authorized",
)


def _canonical(value: object) -> bytes:
    return (json.dumps(value, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _reject_duplicate_json_object_keys(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    # json.loads otherwise discards the earlier claim, including an explicit
    # adverse bypass or ref-lock field overwritten by a later duplicate.
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("DEC-620 duplicate JSON object key: " + key)
        result[key] = value
    return result


def parse_untrusted_witness_json(source: str) -> dict[str, object]:
    value = json.loads(source, object_pairs_hook=_reject_duplicate_json_object_keys)
    claims, _ = _validate_witness(value)
    return claims


def _validate_witness(witness: object) -> tuple[dict[str, object], str]:
    if not isinstance(witness, dict) or set(witness) != WITNESS_KEYS:
        raise ValueError("DEC-620 witness has invalid top-level fields")
    if witness.get("schema") != VERSION:
        raise ValueError("DEC-620 witness schema mismatch")
    ref = witness.get("ref")
    if not isinstance(ref, str) or (ref != "refs/heads/main" and not _is_candidate_tag(ref)):
        raise ValueError("DEC-620 ref must be exact main or an allowed hypothetical 2023 tag")
    sha = witness.get("reviewed_commit_sha")
    if not _is_sha(sha):
        raise ValueError("DEC-620 reviewed commit must be lowercase 40-hex")
    windows = witness.get("intervals")
    if not isinstance(windows, list):
        raise ValueError("DEC-620 intervals must be a list")
    seen = set()
    for item in windows:
        if not isinstance(item, dict) or set(item) != INTERVAL_KEYS:
            raise ValueError("DEC-620 interval has invalid fields")
        label = item.get("interval")
        if not isinstance(label, str) or label not in INTERVALS or label in seen:
            raise ValueError("DEC-620 invalid or duplicate interval label")
        seen.add(label)
        if not _is_sha(item.get("resolved_ref_sha")):
            raise ValueError("DEC-620 interval ref SHA malformed")
        for key in REQUIRED_CLAIMS:
            if type(item[key]) is not bool:
                raise ValueError("DEC-620 interval claim must be a strict boolean: " + key)
    return witness, "main" if ref == "refs/heads/main" else "tag"


def _report(*, repository_root: Path, witness: object) -> dict[str, object]:
    claims, ref_kind = _validate_witness(witness)
    workflow = _source(Path(repository_root))
    if verify_original_workflow_order(workflow) != list(REQUIRED_JOBS):
        raise ValueError("DEC-620 original workflow guards drift")
    window_map = {item["interval"]: item for item in claims["intervals"]}
    gaps: list[str] = []
    reviewed_sha = claims["reviewed_commit_sha"]
    for label in INTERVALS:
        row = window_map.get(label)
        if row is None:
            gaps.append(label + ":missing")
            continue
        if row["resolved_ref_sha"] != reviewed_sha:
            gaps.append(label + ":sha_drift")
        for key in REQUIRED_CLAIMS:
            if not row[key]:
                gaps.append(label + ":" + key)
    complete_claim = len(gaps) == 0
    return {
        "decision": DECISION,
        "version": VERSION,
        "stage": "UNAUTHENTICATED_OFFLINE_REF_LOCK_INTERVAL_CLAIMS_ONLY",
        "repository": "Dtwosam/FMP",
        "active_workflow_path": ANNUAL_WORKFLOW_PATH,
        "active_workflow_git_blob": ANNUAL_WORKFLOW_BLOB,
        "expected_run_number": RUN,
        "expected_run_attempt": ATTEMPT,
        "predecessor_2022_freeze_run_id": PREDECESSOR_RUN_ID,
        "ref_kind": ref_kind,
        "reviewed_commit_sha": reviewed_sha,
        "hypothetical_ref": claims["ref"],
        "active_workflow_ref_compatible": ref_kind == "main",
        "required_interval_labels": list(INTERVALS),
        "untrusted_witness": claims,
        "untrusted_witness_sha256": _digest(claims),
        "missing_or_adverse_interval_claims": gaps,
        "all_required_intervals_claimed_positive": complete_claim,
        "positive_claim_is_not_independent_proof": True,
        "time_slice_snapshots_cannot_prove_continuous_enforcement": True,
        "admin_api_authentication_and_effective_rules_still_required": True,
        "dispatch_blocked": True,
        "no_network_or_github_api_used": True,
        "source_only_analysis": True,
        **{name: False for name in LOCKED_FALSE},
        "next_gate": "INDEPENDENT_REAL_ADMIN_NO_BYPASS_CONTINUOUS_LOCK_WITNESS_AND_ACTION_APPROVAL",
    }


def build_2023_run385_lock_witness_coverage(
    *, repository_root: Path, witness: object,
) -> dict[str, object]:
    report = _report(repository_root=Path(repository_root), witness=witness)
    report["report_sha256"] = _digest(report)
    validate_2023_run385_lock_witness_coverage(report)
    return report


def validate_2023_run385_lock_witness_coverage(value: Mapping[str, object]) -> None:
    if not isinstance(value, Mapping):
        raise ValueError("DEC-620 report must be a JSON object")
    without_fingerprint = dict(value)
    fingerprint = without_fingerprint.pop("report_sha256", None)
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise ValueError("DEC-620 fingerprint invalid")
    if _digest(without_fingerprint) != fingerprint:
        raise ValueError("DEC-620 fingerprint mismatch")
    # Unlike an unkeyed checksum, this source-bound exact payload comparison
    # cannot be bypassed by merely recomputing the JSON fingerprint.
    expected = _report(
        repository_root=Path(__file__).resolve().parents[3],
        witness=without_fingerprint.get("untrusted_witness"),
    )
    # Python's ordinary dict equality equates False to 0 and True to 1.
    # Canonical JSON preserves those types and detects retyped permission
    # fields even when the adversary recomputes the report SHA-256.
    if _canonical(without_fingerprint) != _canonical(expected):
        raise ValueError("DEC-620 source-bound report payload mismatch")
