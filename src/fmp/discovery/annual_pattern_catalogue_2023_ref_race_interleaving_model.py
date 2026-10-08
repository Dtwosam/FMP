from __future__ import annotations

"""DEC-619: inert, exhaustive ordering model of the 2023 ref dispatch race.

Only local deterministic schedule evaluation. No GH API, dispatch or ref mutation.
"""

import hashlib
from itertools import permutations
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2023_disarmed_tag_amendment_preview import _source
from .annual_pattern_catalogue_2023_tag_ref_guard_rehearsal import (
    ANNUAL_WORKFLOW_BLOB,
    ANNUAL_WORKFLOW_PATH,
    REQUIRED_JOBS,
    verify_original_workflow_order,
)

DECISION = "DEC-619"
VERSION = "fmp-phase8a-2023-run385-ref-race-interleaving-model-v1"
REVIEWED_SHA = "a" * 40  # synthetic identifier, not a real approved commit
UNREVIEWED_SHA = "b" * 40  # synthetic identifier, not an actual pushed commit
EXPECTED_RUN_NUMBER = 385
EXPECTED_RUN_ATTEMPT = 1
PREDECESSOR_RUN_ID = 37663157285

CHECK = "client_verify_reviewed_sha"
MUTATE = "independent_actor_mutates_ref"
RESOLVE = "github_server_resolves_ref"
POST = "client_checks_run_head_sha"
REQUIRED_EVENTS = (CHECK, MUTATE, RESOLVE, POST)

PROFILES = (
    ("unprotected_main", "refs/heads/main", True, False, True),
    ("main_exclusive_lock_assumed", "refs/heads/main", False, False, False),
    ("mutable_tag", "refs/tags/fmp/phase8a/2023/run385/example", True, False, True),
    ("tag_ruleset_with_bypass_assumed", "refs/tags/fmp/phase8a/2023/run385/example", True, False, True),
    ("tag_delete_recreate_allowed", "refs/tags/fmp/phase8a/2023/run385/example", True, False, True),
    ("tag_no_bypass_lock_assumed", "refs/tags/fmp/phase8a/2023/run385/example", False, False, False),
)


def _canonical(value: object) -> bytes:
    return (json.dumps(value, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _sha(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _schedules(*, mutation_allowed: bool) -> list[dict[str, object]]:
    """Enumerate all four legal orderings, including a post-resolution race."""
    if type(mutation_allowed) is not bool:
        raise TypeError("DEC-619 schedule mutation permission must be boolean")
    result: list[dict[str, object]] = []
    for sequence in permutations(REQUIRED_EVENTS):
        if not (sequence.index(CHECK) < sequence.index(RESOLVE) < sequence.index(POST)):
            continue
        index_mutate = sequence.index(MUTATE)
        index_check = sequence.index(CHECK)
        index_resolve = sequence.index(RESOLVE)
        ref_at_check = (
            UNREVIEWED_SHA if mutation_allowed and index_mutate < index_check
            else REVIEWED_SHA
        )
        check_passed = ref_at_check == REVIEWED_SHA
        ref_at_server = (
            UNREVIEWED_SHA if mutation_allowed and index_mutate < index_resolve
            else REVIEWED_SHA
        )
        dispatched_sha = ref_at_server if check_passed else None
        # A run-number slot is "consumed" only *hypothetically* in this model;
        # the synthetic model never submits a real workflow_dispatch request.
        consumed_hypothetically = check_passed
        wrong_code_consumed_hypothetically = bool(
            consumed_hypothetically and dispatched_sha != REVIEWED_SHA
        )
        postcheck_accepts_hypothetically = bool(
            check_passed and dispatched_sha == REVIEWED_SHA
        )
        result.append({
            "event_order": list(sequence),
            "client_sha_check_passed": check_passed,
            "server_dispatched_sha_hypothetical": dispatched_sha,
            "run385_consumed_hypothetically": consumed_hypothetically,
            "wrong_sha_consumed_hypothetically": wrong_code_consumed_hypothetically,
            "postcheck_accepts_hypothetically": postcheck_accepts_hypothetically,
            "late_postcheck_cannot_undo_consumption": wrong_code_consumed_hypothetically,
        })
    if len(result) != 4 or len({tuple(x["event_order"]) for x in result}) != 4:
        raise ValueError("DEC-619 exhaustive schedule count drift")
    return result


def _payload(*, repository_root: Path) -> dict[str, object]:
    original = _source(repository_root)
    if verify_original_workflow_order(original) != list(REQUIRED_JOBS):
        raise ValueError("DEC-619 active guard/source job drift")
    profiles: list[dict[str, object]] = []
    for name, ref, mutation_allowed, active_tag_compatible, may_have_counterexample in PROFILES:
        schedules = _schedules(mutation_allowed=mutation_allowed)
        count = sum(int(row["wrong_sha_consumed_hypothetically"]) for row in schedules)
        if (count > 0) is not may_have_counterexample:
            raise ValueError("DEC-619 race counterexample contract drift")
        profiles.append({
            "name": name,
            "ref": ref,
            "ref_mutation_possible_under_assumption": mutation_allowed,
            "active_annual_workflow_tag_compatible": active_tag_compatible,
            "assumption_authenticated_by_live_admin": False,
            "synthetic_counterexample_count": count,
            "schedules": schedules,
        })
    return {
        "decision": DECISION,
        "version": VERSION,
        "stage": "OFFLINE_REF_RACE_INTERLEAVING_MODEL_ONLY",
        "repository_full_name": "Dtwosam/FMP",
        "original_workflow_path": ANNUAL_WORKFLOW_PATH,
        "original_workflow_git_blob": ANNUAL_WORKFLOW_BLOB,
        "reviewed_sha_is_synthetic_fixture": REVIEWED_SHA,
        "unreviewed_sha_is_synthetic_fixture": UNREVIEWED_SHA,
        "event_count": len(REQUIRED_EVENTS),
        "valid_schedule_count_per_profile": 4,
        "expected_run_number": EXPECTED_RUN_NUMBER,
        "expected_run_attempt": EXPECTED_RUN_ATTEMPT,
        "expected_predecessor_run_id": PREDECESSOR_RUN_ID,
        "profiles": profiles,
        "client_check_not_atomic_with_github_server_resolution": True,
        "post_dispatch_check_cannot_unconsume_one_shot_number": True,
        "synthetic_lock_is_not_authenticated_admin_proof": True,
        "tag_path_still_incompatible_with_active_workflow": True,
        "no_network_requests_made": True,
        "no_repository_mutations_made": True,
        "no_real_dispatch_performed": True,
        "live_annual_run385_consumption_state_verified": False,
        "real_exclusive_main_lock_proven": False,
        "real_tag_immutability_proven": False,
        "workflow_runtime_amendment_approved": False,
        "annual_dispatch_authorized": False,
        "run385_execution_authorized_by_this_report": False,
        "rerun_authorized": False,
        "run386_or_later_authorized": False,
        "historical_execution_authorized_by_this_report": False,
        "broker_mutation_authorized": False,
        "demo_order_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "dispatch_blocked": True,
        "next_gate": "AUTHENTICATED_ADMIN_LOCK_AND_SEPARATELY_APPROVED_WORKFLOW_RUNTIME_ACTION",
    }


def build_2023_run385_ref_race_interleaving_report(*, repository_root: Path) -> dict[str, object]:
    value = _payload(repository_root=Path(repository_root))
    value["report_sha256"] = _sha(value)
    validate_2023_run385_ref_race_interleaving_report(value)
    return value


def validate_2023_run385_ref_race_interleaving_report(value: Mapping[str, object]) -> None:
    if not isinstance(value, Mapping):
        raise ValueError("DEC-619 report must be a JSON object")
    supplied = dict(value)
    fingerprint = supplied.pop("report_sha256", None)
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise ValueError("DEC-619 fingerprint invalid")
    if _sha(supplied) != fingerprint:
        raise ValueError("DEC-619 fingerprint mismatch")
    # A recomputed, unkeyed fingerprint is not authority. Independently
    # rebuild every model step from pinned active workflow and code constants.
    expected = _payload(repository_root=Path(__file__).resolve().parents[3])
    if supplied != expected:
        raise ValueError("DEC-619 source-bound report payload mismatch")
