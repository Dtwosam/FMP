from __future__ import annotations

"""DEC-622: inert exact runtime ref/SHA binding test contract, never installed."""

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2023_disarmed_tag_amendment_preview import _source
from .annual_pattern_catalogue_2023_tag_ref_guard_rehearsal import (
    ANNUAL_WORKFLOW_BLOB,
    ANNUAL_WORKFLOW_PATH,
    REQUIRED_JOBS,
    _git_blob,
    _is_candidate_tag,
    _is_sha,
    verify_original_workflow_order,
)

DECISION = "DEC-622"
VERSION = "fmp-2023-run385-inert-tag-runtime-ref-sha-binding-contract-v1"
RUNTIME_PATH = "src/fmp/discovery/annual_pattern_catalogue_2023_runtime_authorization.py"
RUNTIME_GIT_BLOB = "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191"
REPOSITORY = "Dtwosam/FMP"
WORKFLOW_NAME = "phase8a-annual-pattern-catalogue"
SEGMENT = "2023"
RUN_NUMBER = 385
ATTEMPT = 1
PREDECESSOR_RUN_ID = 37663157285
# Deliberately fabricated values: neither a tag nor an approved Git commit.
FIXTURE_TAG = "refs/tags/fmp/phase8a/2023/run385/dec622-unapproved-fixture"
FIXTURE_SHA = "a" * 40
WRONG_SHA = "b" * 40

FIELDS = frozenset((
    "github_event_name", "github_ref", "github_ref_type", "github_sha",
    "github_repository", "github_workflow", "github_workflow_ref",
    "annual_segment_label", "github_run_number", "github_run_attempt",
    "previous_annual_freeze_run_id",
))
DENIED = (
    "installed_runtime_ref_sha_binding",
    "installed_workflow_tag_ref_binding",
    "authoritative_immutable_tag_proven",
    "no_bypass_administrator_lock_proven",
    "live_github_context_authenticated",
    "reviewed_commit_approved",
    "tag_created_or_modified",
    "branch_protection_modified",
    "rulesets_modified",
    "annual_workflow_dispatch_authorized",
    "annual_run385_action_authorized",
    "annual_run385_live_state_verified",
    "annual_dispatch_executed",
    "retry_authorized",
    "rerun_authorized",
    "replacement_run_authorized",
    "run386_or_later_authorized",
    "future_year_research_authorized",
    "cross_year_research_authorized",
    "strategy_synthesis_authorized",
    "promotion_authorized",
    "phase8b_authorized",
    "protected_history_access_authorized_by_report",
    "broker_mutation_authorized",
    "demo_order_authorized",
    "live_order_authorized",
    "real_money_authorized",
    "trading_authorized",
)


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _fixture_context() -> dict[str, object]:
    return {
        "github_event_name": "workflow_dispatch",
        "github_ref": FIXTURE_TAG,
        "github_ref_type": "tag",
        "github_sha": FIXTURE_SHA,
        "github_repository": REPOSITORY,
        "github_workflow": WORKFLOW_NAME,
        "github_workflow_ref": f"{REPOSITORY}/{ANNUAL_WORKFLOW_PATH}@{FIXTURE_TAG}",
        "annual_segment_label": SEGMENT,
        "github_run_number": RUN_NUMBER,
        "github_run_attempt": ATTEMPT,
        "previous_annual_freeze_run_id": PREDECESSOR_RUN_ID,
    }


def synthetic_runtime_tag_identity_matches(context: object) -> bool:
    """Pure predicate. A true return is NOT execution authorization or proof."""
    if not isinstance(context, dict) or set(context) != FIELDS:
        return False
    return bool(
        _is_candidate_tag(context["github_ref"])
        and type(context["github_ref"]) is str
        and context["github_ref"] == FIXTURE_TAG
        and context["github_ref_type"] == "tag"
        and type(context["github_ref_type"]) is str
        and _is_sha(context["github_sha"])
        and context["github_sha"] == FIXTURE_SHA
        and context["github_event_name"] == "workflow_dispatch"
        and type(context["github_event_name"]) is str
        and context["github_repository"] == REPOSITORY
        and type(context["github_repository"]) is str
        and context["github_workflow"] == WORKFLOW_NAME
        and type(context["github_workflow"]) is str
        and context["github_workflow_ref"] == (
            f"{REPOSITORY}/{ANNUAL_WORKFLOW_PATH}@{FIXTURE_TAG}"
        )
        and type(context["github_workflow_ref"]) is str
        and context["annual_segment_label"] == SEGMENT
        and type(context["annual_segment_label"]) is str
        and type(context["github_run_number"]) is int
        and context["github_run_number"] == RUN_NUMBER
        and type(context["github_run_attempt"]) is int
        and context["github_run_attempt"] == ATTEMPT
        and type(context["previous_annual_freeze_run_id"]) is int
        and context["previous_annual_freeze_run_id"] == PREDECESSOR_RUN_ID
    )


def _scenarios() -> tuple[tuple[str, str, object], ...]:
    return (
        ("event_push", "github_event_name", "push"),
        ("main_ref", "github_ref", "refs/heads/main"),
        ("other_tag", "github_ref", FIXTURE_TAG + "-moved"),
        ("branch_ref_type", "github_ref_type", "branch"),
        ("wrong_sha", "github_sha", WRONG_SHA),
        ("upper_sha", "github_sha", FIXTURE_SHA.upper()),
        ("wrong_repo", "github_repository", "other/FMP"),
        ("wrong_workflow_name", "github_workflow", "other-workflow"),
        ("wrong_workflow_ref_path", "github_workflow_ref",
         f"{REPOSITORY}/.github/workflows/other.yml@{FIXTURE_TAG}"),
        ("wrong_workflow_ref_tag", "github_workflow_ref",
         f"{REPOSITORY}/{ANNUAL_WORKFLOW_PATH}@{FIXTURE_TAG}-other"),
        ("wrong_year", "annual_segment_label", "2024"),
        ("wrong_run", "github_run_number", 386),
        ("bool_run", "github_run_number", True),
        ("wrong_attempt", "github_run_attempt", 2),
        ("bool_attempt", "github_run_attempt", True),
        ("wrong_predecessor", "previous_annual_freeze_run_id", 5),
        ("bool_predecessor", "previous_annual_freeze_run_id", True),
        ("wrong_event_type", "github_event_name", 1),
        ("wrong_sha_type", "github_sha", 123),
    )


def _source_contract(repository_root: Path) -> dict[str, object]:
    original = _source(repository_root)
    if verify_original_workflow_order(original) != list(REQUIRED_JOBS):
        raise ValueError("DEC-622 original main/event/ref guard order drift")
    runtime_bytes = (repository_root / RUNTIME_PATH).read_bytes()
    if _git_blob(runtime_bytes) != RUNTIME_GIT_BLOB:
        raise ValueError("DEC-622 installed 2023 runtime authorization source drift")
    runtime = runtime_bytes.decode("utf-8")
    if "def require_2023_execution_authorized(" not in runtime:
        raise ValueError("DEC-622 missing current 2023 authorization entry point")
    if "    _validate_commit(code_commit)" not in runtime:
        raise ValueError("DEC-622 source assumptions about commit syntax check drift")
    if "github_ref:" in runtime or "github_workflow_ref:" in runtime:
        raise ValueError("DEC-622 active runtime ref/SHA binding unexpectedly changed")
    return {
        "source_annual_workflow_path": ANNUAL_WORKFLOW_PATH,
        "source_annual_workflow_git_blob": ANNUAL_WORKFLOW_BLOB,
        "source_runtime_path": RUNTIME_PATH,
        "source_runtime_git_blob": RUNTIME_GIT_BLOB,
        "original_annual_jobs": list(REQUIRED_JOBS),
        "active_main_only_guard_detected": True,
        "active_runtime_only_checks_commit_syntax_not_exact_tag_binding": True,
    }


def _payload(root: Path) -> dict[str, object]:
    source = _source_contract(root)
    base = _fixture_context()
    if not synthetic_runtime_tag_identity_matches(base):
        raise ValueError("DEC-622 intended positive fixture no longer matches")
    rows: list[dict[str, object]] = [
        {"scenario": "exact_synthetic_tuple", "synthetic_predicate_match": True},
    ]
    for name, key, value in _scenarios():
        changed = dict(base)
        changed[key] = value
        rows.append({
            "scenario": name,
            "synthetic_predicate_match": synthetic_runtime_tag_identity_matches(changed),
        })
    for name, key in (("missing_sha", "github_sha"), ("missing_workflow_ref", "github_workflow_ref")):
        changed = dict(base)
        del changed[key]
        rows.append({
            "scenario": name,
            "synthetic_predicate_match": synthetic_runtime_tag_identity_matches(changed),
        })
    changed = dict(base)
    changed["admin_authorized"] = True
    rows.append({
        "scenario": "unexpected_authority_field",
        "synthetic_predicate_match": synthetic_runtime_tag_identity_matches(changed),
    })
    if len(rows) != 23 or any(r["synthetic_predicate_match"] for r in rows[1:]):
        raise ValueError("DEC-622 negative synthetic scenario matrix drift")
    return {
        "decision": DECISION,
        "version": VERSION,
        "stage": "INERT_2023_TAG_RUNTIME_REF_SHA_BINDING_DESIGN_PREVIEW",
        "repository": REPOSITORY,
        **source,
        "fixture_tag_ref_not_approved": FIXTURE_TAG,
        "fixture_reviewed_sha_not_approved": FIXTURE_SHA,
        "expected_annual_segment": SEGMENT,
        "expected_run_number": RUN_NUMBER,
        "expected_run_attempt": ATTEMPT,
        "expected_previous_2022_freeze_run_id": PREDECESSOR_RUN_ID,
        "scenario_count": len(rows),
        "scenario_results": rows,
        "one_synthetic_fixture_matches": True,
        "every_adverse_synthetic_fixture_rejected": True,
        "synthetic_match_is_never_execution_authorization": True,
        "tag_workflow_amendment_and_runtime_amendment_both_required": True,
        "independent_admin_immutable_ref_witness_required": True,
        "separate_one_shot_run385_action_required": True,
        "no_network_or_live_github_event": True,
        "no_workflow_or_runtime_file_mutated": True,
        "no_real_dispatch_or_historical_read": True,
        "read_only": True,
        "dispatch_blocked": True,
        **{key: False for key in DENIED},
        "next_gate": "SEPARATELY_APPROVED_WORKFLOW_AND_RUNTIME_TAG_SHA_BINDING_WITH_REAL_ADMIN_PROOF",
    }


def build_2023_runtime_tag_sha_binding_preview(*, repository_root: Path) -> dict[str, object]:
    data = _payload(Path(repository_root))
    data["report_sha256"] = _digest(data)
    validate_2023_runtime_tag_sha_binding_preview(data)
    return data


def validate_2023_runtime_tag_sha_binding_preview(value: Mapping[str, object]) -> None:
    if not isinstance(value, Mapping):
        raise ValueError("DEC-622 report must be a mapping")
    unsigned = dict(value)
    fp = unsigned.pop("report_sha256", None)
    if not isinstance(fp, str) or len(fp) != 64:
        raise ValueError("DEC-622 report SHA missing or malformed")
    if _digest(unsigned) != fp:
        raise ValueError("DEC-622 report fingerprint mismatch")
    # A rehashed JSON file is NOT an authenticated source. Regenerate the
    # complete fixture matrix from pinned installed workflow and 2023 runtime,
    # then compare canonical JSON bytes to distinguish booleans from integers.
    expected = _payload(Path(__file__).resolve().parents[3])
    if _canonical(unsigned) != _canonical(expected):
        raise ValueError("DEC-622 source-bound exact report mismatch")
