from __future__ import annotations

"""DEC-617 inert rehearsal of tag-ref guard predicates; no live execution path."""

import hashlib
import json
import re
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2023_tag_ruleset_static_review import (
    EXPECTED_TAG_NAMESPACE,
)

DECISION = "DEC-617"
VERSION = "fmp-2023-run385-tag-ref-guard-rehearsal-v1"
ANNUAL_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
ANNUAL_WORKFLOW_BLOB = "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
PREDECESSOR_RUN_ID = 37663157285
EXPECTED_RUN_NUMBER = 385
EXPECTED_ATTEMPT = 1
REQUIRED_JOBS = ("annual_preflight", "annual_cell", "annual_freeze")
MAIN_REF_GUARD = 'test "$GITHUB_REF" = "refs/heads/main"'
EVENT_GUARD = 'test "$GITHUB_EVENT_NAME" = "workflow_dispatch"'
LOCKED_FALSE = (
    "active_workflow_tag_compatible",
    "candidate_guard_installed",
    "workflow_amendment_authorized",
    "runtime_amendment_authorized",
    "immutable_tag_proven",
    "tag_creation_authorized",
    "annual_workflow_dispatch_authorized",
    "dispatch_action_executed",
    "rerun_authorized",
    "retry_authorized",
    "replacement_run_authorized",
    "run_386_or_later_authorized",
    "later_year_execution_authorized",
    "cross_year_research_authorized",
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
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _git_blob(value: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(value)).encode("ascii") + b"\0" + value).hexdigest()


def _is_sha(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) is not None


def _is_candidate_tag(ref: object) -> bool:
    if not isinstance(ref, str) or not ref.startswith(EXPECTED_TAG_NAMESPACE):
        return False
    suffix = ref[len(EXPECTED_TAG_NAMESPACE):]
    return (
        len(suffix) > 0
        and len(suffix) <= 80
        and re.fullmatch(r"[a-z0-9][a-z0-9._-]*", suffix) is not None
        and ".." not in suffix
        and not suffix.endswith((".", ".lock"))
    )


def verify_original_workflow_order(workflow: str) -> list[str]:
    """Fail closed unless original guards still precede install/auth/data work."""
    if not isinstance(workflow, str) or workflow.count(MAIN_REF_GUARD) != 3:
        raise ValueError("DEC-617 original main ref guard inventory changed")
    if workflow.count(EVENT_GUARD) != 3:
        raise ValueError("DEC-617 original dispatch event guard inventory changed")
    if "  workflow_dispatch:" not in workflow:
        raise ValueError("DEC-617 manual trigger missing")
    blocks: dict[str, list[str]] = {}
    in_jobs = False
    current: str | None = None
    for line in workflow.splitlines():
        if line == "jobs:":
            in_jobs = True
            current = None
            continue
        if in_jobs and line and not line.startswith(" "):
            in_jobs = False
            current = None
        if not in_jobs:
            continue
        match = re.fullmatch(r"  ([a-z][a-z0-9_-]*):", line)
        if match:
            current = match.group(1)
            if current in blocks:
                raise ValueError("DEC-617 duplicate job")
            blocks[current] = []
        elif current is not None:
            blocks[current].append(line)

    if set(blocks) != set(REQUIRED_JOBS):
        raise ValueError("DEC-617 job inventory changed")

    for job in REQUIRED_JOBS:
        text = "\n".join(blocks[job])
        if text.count(MAIN_REF_GUARD) != 1 or text.count(EVENT_GUARD) != 1:
            raise ValueError(f"DEC-617 {job} event/ref guard changed")
        pos_ref = text.index(MAIN_REF_GUARD)
        pos_event = text.index(EVENT_GUARD)
        pos_install = text.find("- name: Install pinned annual catalogue runtime")
        pos_exec = text.find("--code-commit \"$GITHUB_SHA\"")
        if not (0 <= pos_event < pos_ref < pos_install < pos_exec):
            raise ValueError(f"DEC-617 {job} ref guard ordering changed")
        if job == "annual_preflight":
            pos_fetch = text.find("- name: Fetch exact accepted EXP-044 source snapshots")
            if not pos_exec or not (pos_ref < pos_fetch):
                raise ValueError("DEC-617 preflight ref guard must precede source fetch")
        elif job == "annual_cell":
            pos_fetch = text.find("- name: Download exact accepted EXP-044 feature/outcome/evidence artifacts")
            if not (pos_ref < pos_fetch):
                raise ValueError("DEC-617 cells ref guard must precede historical downloads")
        else:
            pos_fetch = text.find("- name: Download all 18 annual catalogue cell products")
            if not (pos_ref < pos_fetch):
                raise ValueError("DEC-617 freeze ref guard must precede cell downloads")
    return list(REQUIRED_JOBS)


def synthetic_candidate_guard_matches(
    *,
    expected_tag_ref: object,
    reviewed_commit_sha: object,
    event_name: object,
    github_ref: object,
    github_sha: object,
    annual_segment_label: object,
    run_number: object,
    run_attempt: object,
    previous_annual_freeze_run_id: object,
) -> bool:
    """Predicate rehearsal only, not a runtime auth helper or dispatch decision."""
    return bool(
        _is_candidate_tag(expected_tag_ref)
        and _is_sha(reviewed_commit_sha)
        and event_name == "workflow_dispatch"
        and type(github_ref) is str
        and github_ref == expected_tag_ref
        and type(github_sha) is str
        and github_sha == reviewed_commit_sha
        and annual_segment_label == "2023"
        and type(run_number) is int
        and run_number == EXPECTED_RUN_NUMBER
        and type(run_attempt) is int
        and run_attempt == EXPECTED_ATTEMPT
        and type(previous_annual_freeze_run_id) is int
        and previous_annual_freeze_run_id == PREDECESSOR_RUN_ID
    )


def build_2023_tag_ref_guard_rehearsal(
    *,
    repository_root: Path,
    candidate_tag_ref: str,
    reviewed_commit_sha: str,
) -> dict[str, object]:
    # A caller-supplied ref/SHA pair is hypothetical. Neither is approved.
    if not _is_candidate_tag(candidate_tag_ref):
        raise ValueError("DEC-617 invalid proposed exact tag ref")
    if not _is_sha(reviewed_commit_sha):
        raise ValueError("DEC-617 invalid proposed reviewed SHA")
    workflow_bytes = (Path(repository_root) / ANNUAL_WORKFLOW_PATH).read_bytes()
    if _git_blob(workflow_bytes) != ANNUAL_WORKFLOW_BLOB:
        raise ValueError("DEC-617 active annual workflow drift")
    jobs = verify_original_workflow_order(workflow_bytes.decode("utf-8"))
    synthetic_match = synthetic_candidate_guard_matches(
        expected_tag_ref=candidate_tag_ref,
        reviewed_commit_sha=reviewed_commit_sha,
        event_name="workflow_dispatch",
        github_ref=candidate_tag_ref,
        github_sha=reviewed_commit_sha,
        annual_segment_label="2023",
        run_number=EXPECTED_RUN_NUMBER,
        run_attempt=EXPECTED_ATTEMPT,
        previous_annual_freeze_run_id=PREDECESSOR_RUN_ID,
    )
    if not synthetic_match:
        raise ValueError("DEC-617 synthetic discriminator unavailable")
    report: dict[str, object] = {
        "decision": DECISION,
        "version": VERSION,
        "stage": "INERT_TAG_REF_GUARD_REHEARSAL_ONLY",
        "repository_full_name": "Dtwosam/FMP",
        "active_workflow_path": ANNUAL_WORKFLOW_PATH,
        "active_workflow_git_blob": ANNUAL_WORKFLOW_BLOB,
        "reviewed_job_order": jobs,
        "hypothetical_tag_ref": candidate_tag_ref,
        "hypothetical_reviewed_commit_sha": reviewed_commit_sha,
        "expected_run_number": EXPECTED_RUN_NUMBER,
        "expected_run_attempt": EXPECTED_ATTEMPT,
        "expected_predecessor_run_id": PREDECESSOR_RUN_ID,
        "synthetic_matching_tuple_accepted_by_rehearsal": True,
        "synthetic_predicate_does_not_authenticate_tag_rulesets": True,
        "synthetic_predicate_does_not_prove_ref_immutability": True,
        "runtime_code_sha_binding_amendment_required": True,
        "job_guard_source_amendment_required": True,
        "tag_ruleset_admin_witness_required": True,
        "separate_one_shot_decision_required": True,
        "no_active_sources_mutated": True,
        "dispatch_blocked": True,
        "read_only": True,
        **{name: False for name in LOCKED_FALSE},
        "next_gate": "SEPARATE_WORKFLOW_RUNTIME_AMENDMENT_AND_ADMIN_TAG_LOCK_REVIEW",
    }
    report["rehearsal_fingerprint_sha256"] = _digest(report)
    validate_2023_tag_ref_guard_rehearsal(report)
    return report


def validate_2023_tag_ref_guard_rehearsal(value: Mapping[str, object]) -> None:
    if not isinstance(value, Mapping):
        raise ValueError("DEC-617 report not a JSON object")
    unsigned = dict(value)
    fingerprint = unsigned.pop("rehearsal_fingerprint_sha256", None)
    if not isinstance(fingerprint, str) or not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
        raise ValueError("DEC-617 fingerprint malformed")
    if _digest(unsigned) != fingerprint:
        raise ValueError("DEC-617 fingerprint mismatch")
    required: dict[str, object] = {
        "decision": DECISION,
        "version": VERSION,
        "stage": "INERT_TAG_REF_GUARD_REHEARSAL_ONLY",
        "repository_full_name": "Dtwosam/FMP",
        "active_workflow_path": ANNUAL_WORKFLOW_PATH,
        "active_workflow_git_blob": ANNUAL_WORKFLOW_BLOB,
        "reviewed_job_order": list(REQUIRED_JOBS),
        "expected_run_number": EXPECTED_RUN_NUMBER,
        "expected_run_attempt": EXPECTED_ATTEMPT,
        "expected_predecessor_run_id": PREDECESSOR_RUN_ID,
        "synthetic_matching_tuple_accepted_by_rehearsal": True,
        "synthetic_predicate_does_not_authenticate_tag_rulesets": True,
        "synthetic_predicate_does_not_prove_ref_immutability": True,
        "runtime_code_sha_binding_amendment_required": True,
        "job_guard_source_amendment_required": True,
        "tag_ruleset_admin_witness_required": True,
        "separate_one_shot_decision_required": True,
        "no_active_sources_mutated": True,
        "dispatch_blocked": True,
        "read_only": True,
        **{key: False for key in LOCKED_FALSE},
        "next_gate": "SEPARATE_WORKFLOW_RUNTIME_AMENDMENT_AND_ADMIN_TAG_LOCK_REVIEW",
    }
    allowed = set(required) | {
        "hypothetical_tag_ref", "hypothetical_reviewed_commit_sha",
        "rehearsal_fingerprint_sha256",
    }
    if set(value) != allowed:
        raise ValueError("DEC-617 unauthorized report fields")
    if not _is_candidate_tag(value.get("hypothetical_tag_ref")) or not _is_sha(
        value.get("hypothetical_reviewed_commit_sha")
    ):
        raise ValueError("DEC-617 malformed hypothetical identity")
    for key, expected in required.items():
        actual = value.get(key)
        if type(expected) is bool:
            valid = actual is expected
        elif type(expected) is int:
            valid = type(actual) is int and actual == expected
        else:
            valid = actual == expected
        if not valid:
            raise ValueError("DEC-617 forbidden or changed field: " + key)
