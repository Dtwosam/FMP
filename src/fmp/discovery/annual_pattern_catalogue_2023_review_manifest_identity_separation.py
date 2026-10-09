from __future__ import annotations

"""DEC-625: offline separation of fixed *review fixture* and observed runner context.

The positive comparison is synthetic only. This module never grants execution.
"""

import hashlib
import json
import re
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2023_runtime_tag_sha_binding_preview import (
    ANNUAL_WORKFLOW_BLOB,
    ANNUAL_WORKFLOW_PATH,
    ATTEMPT,
    FIXTURE_SHA,
    FIXTURE_TAG,
    PREDECESSOR_RUN_ID,
    REPOSITORY,
    RUNTIME_GIT_BLOB,
    RUNTIME_PATH,
    RUN_NUMBER,
    SEGMENT,
    WORKFLOW_NAME,
)
from .annual_pattern_catalogue_2023_tag_ref_guard_rehearsal import (
    _git_blob,
    _is_candidate_tag,
    _is_sha,
    verify_original_workflow_order,
    REQUIRED_JOBS,
)
from .annual_pattern_catalogue_2023_three_layer_admission_model import _current_source

DECISION = "DEC-625"
VERSION = "fmp-run385-inert-independently-reviewed-identity-source-separation-v1"
FIXTURE_PROVENANCE = "IN_MEMORY_UNAPPROVED_REVIEW_FIXTURE_NOT_AN_AUTHORITY"
MANIFEST_KEYS = frozenset((
    "provenance", "review_ticket", "repository", "reviewed_tag_ref",
    "reviewed_code_sha", "reviewed_workflow_sha", "workflow_name",
    "workflow_path", "workflow_blob", "runtime_path", "runtime_blob",
    "annual_segment", "run_number", "run_attempt", "predecessor_run_id",
))
OBSERVED_KEYS = frozenset((
    "github_event_name", "github_ref", "github_ref_type", "github_sha",
    "github_workflow_sha", "github_repository", "github_workflow",
    "github_workflow_ref", "annual_segment_label", "github_run_number",
    "github_run_attempt", "previous_annual_freeze_run_id",
))
DENIED = (
    "review_manifest_independently_authenticated",
    "reviewed_commit_approved",
    "observed_context_authenticated",
    "admin_ruleset_witness_authenticated",
    "continuous_admin_no_bypass_enforcement_proven",
    "immutable_tag_proven",
    "tag_exists_verified",
    "tag_created_or_mutated",
    "installed_job_level_admission",
    "installed_preinstall_ref_sha_check",
    "installed_runtime_ref_sha_check",
    "annual_workflow_tag_compatible",
    "live_2023_runtime_bound_to_reviewed_sha",
    "workflow_amendment_authorized",
    "runtime_amendment_authorized",
    "annual_dispatch_authorized",
    "run385_action_authorized",
    "run385_live_inventory_authenticated",
    "dispatch_performed",
    "retry_authorized",
    "rerun_authorized",
    "replacement_authorized",
    "future_year_authorized",
    "historical_artifact_read_authorized",
    "cross_year_synthesis_authorized",
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


def _fixture_manifest() -> dict[str, object]:
    # Deliberately synthetic. A GitHub environment variable is NOT an approval.
    return {
        "provenance": FIXTURE_PROVENANCE,
        "review_ticket": "DEC-625-FIXTURE-DO-NOT-DISPATCH",
        "repository": REPOSITORY,
        "reviewed_tag_ref": FIXTURE_TAG,
        "reviewed_code_sha": FIXTURE_SHA,
        "reviewed_workflow_sha": FIXTURE_SHA,
        "workflow_name": WORKFLOW_NAME,
        "workflow_path": ANNUAL_WORKFLOW_PATH,
        "workflow_blob": ANNUAL_WORKFLOW_BLOB,
        "runtime_path": RUNTIME_PATH,
        "runtime_blob": RUNTIME_GIT_BLOB,
        "annual_segment": SEGMENT,
        "run_number": RUN_NUMBER,
        "run_attempt": ATTEMPT,
        "predecessor_run_id": PREDECESSOR_RUN_ID,
    }


def _fixture_observation() -> dict[str, object]:
    return {
        "github_event_name": "workflow_dispatch",
        "github_ref": FIXTURE_TAG,
        "github_ref_type": "tag",
        "github_sha": FIXTURE_SHA,
        "github_workflow_sha": FIXTURE_SHA,
        "github_repository": REPOSITORY,
        "github_workflow": WORKFLOW_NAME,
        "github_workflow_ref": f"{REPOSITORY}/{ANNUAL_WORKFLOW_PATH}@{FIXTURE_TAG}",
        "annual_segment_label": SEGMENT,
        "github_run_number": RUN_NUMBER,
        "github_run_attempt": ATTEMPT,
        "previous_annual_freeze_run_id": PREDECESSOR_RUN_ID,
    }


def synthetic_separate_reviewed_and_observed_match(
    reviewed_manifest: object, observed_context: object
) -> bool:
    """Pure exact-match predicate. True is NOT proof of review or dispatch authority."""
    if type(reviewed_manifest) is not dict or type(observed_context) is not dict:
        return False
    if set(reviewed_manifest) != MANIFEST_KEYS or set(observed_context) != OBSERVED_KEYS:
        return False
    # Pin to the *compiled* fixed fixture. Never derive approved expected values
    # from github.ref, github.sha, github.workflow_ref, or caller-supplied marker.
    fixed = _fixture_manifest()
    if any(
        type(reviewed_manifest[key]) is not type(value)
        or reviewed_manifest[key] != value
        for key, value in fixed.items()
    ):
        return False
    if not _is_candidate_tag(reviewed_manifest["reviewed_tag_ref"]):
        return False
    if not _is_sha(reviewed_manifest["reviewed_code_sha"]):
        return False
    if not _is_sha(reviewed_manifest["reviewed_workflow_sha"]):
        return False
    required_observation = _fixture_observation()
    return all(
        type(observed_context[key]) is type(value)
        and observed_context[key] == value
        for key, value in required_observation.items()
    )


def _source_pins(root: Path) -> dict[str, object]:
    _current_source(root)  # Pins the current workflow and three job step topology.
    workflow_bytes = (root / ANNUAL_WORKFLOW_PATH).read_bytes()
    runtime_bytes = (root / RUNTIME_PATH).read_bytes()
    if _git_blob(workflow_bytes) != ANNUAL_WORKFLOW_BLOB:
        raise ValueError("DEC-625 annual workflow Git blob drift")
    if _git_blob(runtime_bytes) != RUNTIME_GIT_BLOB:
        raise ValueError("DEC-625 2023 runtime Git blob drift")
    if verify_original_workflow_order(workflow_bytes.decode("utf-8")) != list(REQUIRED_JOBS):
        raise ValueError("DEC-625 installed workflow guard/order drift")
    runtime = runtime_bytes.decode("utf-8")
    if "def require_2023_execution_authorized(" not in runtime:
        raise ValueError("DEC-625 2023 authorization entrypoint drift")
    if "    _validate_commit(code_commit)" not in runtime:
        raise ValueError("DEC-625 original format-only SHA validation drift")
    if "github_ref:" in runtime or "github_workflow_ref:" in runtime:
        raise ValueError("DEC-625 installed runtime binding source changed")
    return {
        "source_workflow_path": ANNUAL_WORKFLOW_PATH,
        "source_workflow_blob": ANNUAL_WORKFLOW_BLOB,
        "source_runtime_path": RUNTIME_PATH,
        "source_runtime_blob": RUNTIME_GIT_BLOB,
        "source_three_jobs": list(REQUIRED_JOBS),
    }


def _negative_matrix() -> list[dict[str, object]]:
    matrix: list[dict[str, object]] = []
    variants = (
        ("missing_manifest", "manifest", "remove", "reviewed_tag_ref", None),
        ("manifest_extra_field", "manifest", "add", "approved", True),
        ("manifest_untrusted_provenance", "manifest", "set", "provenance", "GITHUB_SHA"),
        ("manifest_provenance_bool", "manifest", "set", "provenance", True),
        ("manifest_sha_forged", "manifest", "set", "reviewed_code_sha", "b" * 40),
        ("manifest_workflow_sha_forged", "manifest", "set", "reviewed_workflow_sha", "b" * 40),
        ("manifest_run_bool", "manifest", "set", "run_number", True),
        ("manifest_attempt_replay", "manifest", "set", "run_attempt", 2),
        ("observation_missing", "context", "remove", "github_sha", None),
        ("observation_extra_authority", "context", "add", "trading_authorized", True),
        ("observation_push", "context", "set", "github_event_name", "push"),
        ("observation_other_tag", "context", "set", "github_ref", FIXTURE_TAG + "-move"),
        ("observation_branch_type", "context", "set", "github_ref_type", "branch"),
        ("observation_sha_changed", "context", "set", "github_sha", "b" * 40),
        ("observation_workflow_sha_changed", "context", "set", "github_workflow_sha", "b" * 40),
        ("observation_wrong_workflow_ref", "context", "set", "github_workflow_ref",
         f"{REPOSITORY}/.github/workflows/other.yml@{FIXTURE_TAG}"),
        ("observation_other_repo", "context", "set", "github_repository", "other/FMP"),
        ("observation_other_year", "context", "set", "annual_segment_label", "2024"),
        ("observation_other_run", "context", "set", "github_run_number", 386),
        ("observation_run_bool", "context", "set", "github_run_number", True),
        ("observation_attempt_2", "context", "set", "github_run_attempt", 2),
        ("observation_predecessor_wrong", "context", "set", "previous_annual_freeze_run_id", 1),
        ("observation_predecessor_bool", "context", "set", "previous_annual_freeze_run_id", True),
    )
    for label, side, op, key, value in variants:
        m, o = _fixture_manifest(), _fixture_observation()
        target = m if side == "manifest" else o
        if op == "remove":
            del target[key]
        else:
            target[key] = value
        matrix.append({
            "case": label,
            "synthetic_match": synthetic_separate_reviewed_and_observed_match(m, o),
        })
    # An attacker cannot make a new reviewed code identity merely by changing
    # both fields to match: its independent fixed source differs.
    m, o = _fixture_manifest(), _fixture_observation()
    m["reviewed_code_sha"] = "b" * 40
    m["reviewed_workflow_sha"] = "b" * 40
    o["github_sha"] = "b" * 40
    o["github_workflow_sha"] = "b" * 40
    matrix.append({
        "case": "self_attested_sha_rebound_on_both_sides",
        "synthetic_match": synthetic_separate_reviewed_and_observed_match(m, o),
    })
    m, o = _fixture_manifest(), _fixture_observation()
    m["reviewed_tag_ref"] = FIXTURE_TAG + "-replacement"
    o["github_ref"] = m["reviewed_tag_ref"]
    o["github_workflow_ref"] = f"{REPOSITORY}/{ANNUAL_WORKFLOW_PATH}@{m['reviewed_tag_ref']}"
    matrix.append({
        "case": "self_attested_tag_rebound_on_both_sides",
        "synthetic_match": synthetic_separate_reviewed_and_observed_match(m, o),
    })
    if len(matrix) != 25 or any(item["synthetic_match"] for item in matrix):
        raise ValueError("DEC-625 synthetic adversarial provenance matrix incomplete")
    return matrix


def _payload(root: Path) -> dict[str, object]:
    source = _source_pins(root)
    manifest = _fixture_manifest()
    observed = _fixture_observation()
    if not synthetic_separate_reviewed_and_observed_match(manifest, observed):
        raise ValueError("DEC-625 fixed positive synthetic comparison failed")
    failures = _negative_matrix()
    return {
        "decision": DECISION,
        "version": VERSION,
        "stage": "INERT_REVIEW_MANIFEST_VS_RUNNER_CONTEXT_BOUNDARY_UNINSTALLED",
        "repository": REPOSITORY,
        **source,
        "synthetic_unapproved_manifest_sha256": _digest(manifest),
        "synthetic_observation_sha256": _digest(observed),
        "synthetic_exact_match_only_not_execution_authority": True,
        "synthetic_cases_rejected": len(failures),
        "negative_cases": failures,
        "expected_values_must_not_be_derived_from_untrusted_github_context": True,
        "reviewed_identity_must_have_separately_authenticated_origin": True,
        "github_workflow_sha_must_match_separately_reviewed_definition_commit": True,
        "current_annual_workflow_main_only_not_tag_compatible": True,
        "current_2023_runtime_checks_sha_format_not_independent_identity": True,
        "independent_authenticated_continuous_admin_no_bypass_witness_missing": True,
        "requires_separately_approved_executable_three_job_amendment": True,
        "requires_distinct_one_shot_run385_decision": True,
        "no_external_io_or_api_calls": True,
        "no_active_source_mutation": True,
        "read_only": True,
        "dispatch_blocked": True,
        **{name: False for name in DENIED},
        "expected_annual_run": RUN_NUMBER,
        "expected_annual_attempt": ATTEMPT,
        "expected_predecessor_run_id": PREDECESSOR_RUN_ID,
        "next_gate": "INDEPENDENTLY_AUTHENTICATED_APPROVAL_AND_ADMIN_WITNESS_BEFORE_INSTALLED_GUARDS",
    }


def build_review_manifest_identity_separation(*, repository_root: Path) -> dict[str, object]:
    report = _payload(Path(repository_root))
    report["report_sha256"] = _digest(report)
    validate_review_manifest_identity_separation(report)
    return report


def validate_review_manifest_identity_separation(report: Mapping[str, object]) -> None:
    if not isinstance(report, Mapping):
        raise ValueError("DEC-625 report must be a mapping")
    unsigned = dict(report)
    fingerprint = unsigned.pop("report_sha256", None)
    if not isinstance(fingerprint, str) or re.fullmatch(r"[a-f0-9]{64}", fingerprint) is None:
        raise ValueError("DEC-625 invalid report fingerprint")
    if _digest(unsigned) != fingerprint:
        raise ValueError("DEC-625 report fingerprint mismatch")
    if _canonical(unsigned) != _canonical(_payload(Path(__file__).resolve().parents[3])):
        raise ValueError("DEC-625 forged or source-drifted canonical payload")
