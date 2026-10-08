from __future__ import annotations

"""DEC-626: uninstalled exact GitHub Actions job-level if expression rehearsal.

This module renders a literal expression into a JSON report only. It cannot
install or execute GitHub Actions, authorize a tag, or dispatch research.
"""

from pathlib import Path
from typing import Mapping
import re

from .annual_pattern_catalogue_2023_review_manifest_identity_separation import (
    _canonical,
    _digest,
    _fixture_manifest,
    _source_pins,
)
from .annual_pattern_catalogue_2023_tag_ref_guard_rehearsal import REQUIRED_JOBS

DECISION = "DEC-626"
VERSION = "fmp-run385-uninstalled-job-level-precheckout-github-if-preview-v1"
PLACEMENT = "jobs.<annual_job>.if-before-any-steps-SYNTHETIC-ONLY"
DENIED = (
    "candidate_job_if_installed",
    "tag_ref_immutable_proven",
    "admin_no_bypass_lock_proven",
    "independently_authenticated_review_manifest_proven",
    "workflow_ref_sha_live_binding_installed",
    "runtime_2023_ref_sha_binding_installed",
    "actual_job_evaluation_proven",
    "job_if_prevents_workflow_definition_loading_proven",
    "repository_rule_changes_authorized",
    "tag_creation_authorized",
    "annual_run385_action_authorized",
    "annual_dispatch_authorized",
    "annual_dispatch_executed",
    "historical_artifact_read_authorized",
    "retry_authorized",
    "replacement_authorized",
    "future_year_research_authorized",
    "broker_mutation_authorized",
    "demo_order_authorized",
    "live_order_authorized",
    "real_money_authorized",
    "trading_authorized",
)


def _approved_strings_from_fixed_unapproved_fixture() -> tuple[str, ...]:
    # The static fixture is NOT really approved. This function's name
    # emphasizes its *would-be* role in a separately approved design.
    m = _fixture_manifest()
    for key in ("repository", "reviewed_tag_ref", "reviewed_code_sha", "reviewed_workflow_sha",
                "workflow_name", "workflow_path", "annual_segment"):
        value = m[key]
        if type(value) is not str or not re.fullmatch(r"[a-zA-Z0-9._/-]+", value):
            raise ValueError("DEC-626 unsafe literal for candidate job if: " + key)
    if any(type(m[key]) is not int for key in ("run_number", "run_attempt", "predecessor_run_id")):
        raise ValueError("DEC-626 expected numeric fixture values changed")
    return (
        m["repository"], m["reviewed_tag_ref"], m["reviewed_code_sha"],
        m["reviewed_workflow_sha"], m["workflow_name"], m["workflow_path"],
        m["annual_segment"], str(m["run_number"]), str(m["run_attempt"]),
        str(m["predecessor_run_id"]),
    )


def _candidate_expression() -> str:
    (repo, tag, sha, workflow_sha, workflow_name, workflow_path,
     segment, run_number, attempt, predecessor) = _approved_strings_from_fixed_unapproved_fixture()
    terms = (
        "github.event_name == 'workflow_dispatch'",
        f"github.repository == '{repo}'",
        "github.ref_type == 'tag'",
        f"github.ref == '{tag}'",
        f"github.sha == '{sha}'",
        f"github.workflow_sha == '{workflow_sha}'",
        f"github.workflow == '{workflow_name}'",
        f"github.workflow_ref == '{repo}/{workflow_path}@{tag}'",
        f"inputs.annual_segment_label == '{segment}'",
        f"inputs.previous_annual_freeze_run_id == '{predecessor}'",
        f"github.run_number == {run_number}",
        f"github.run_attempt == {attempt}",
    )
    # Only source code renders this expression. No untrusted f-string
    # interpolation, YAML write, GitHub variable or API action occurs.
    return "$" + "{{ " + " && ".join(terms) + " }}"


def _candidate_jobs() -> dict[str, dict[str, str]]:
    return {
        job: {"placement": PLACEMENT, "expression": _candidate_expression()}
        for job in REQUIRED_JOBS
    }


def synthetic_precheckout_job_if_preview_matches(candidate: object) -> bool:
    """Exact string equality, NOT a GitHub Actions parser or auth verdict."""
    if type(candidate) is not dict or set(candidate) != set(REQUIRED_JOBS):
        return False
    reference = _candidate_jobs()
    return all(
        type(candidate[job]) is dict
        and set(candidate[job]) == {"placement", "expression"}
        and all(
            type(candidate[job][key]) is str
            and candidate[job][key] == reference[job][key]
            for key in ("placement", "expression")
        )
        for job in REQUIRED_JOBS
    )


def _negatives() -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for job in REQUIRED_JOBS:
        for attack in (
            "missing_job_gate",
            "moved_after_checkout",
            "self_attested_sha",
            "workflow_sha_omitted",
            "wrong_tag",
            "event_gate_weakened",
            "run_number_as_string",
            "extra_authority_field",
        ):
            candidate = _candidate_jobs()
            item = candidate[job]
            expr = item["expression"]
            if attack == "missing_job_gate":
                del candidate[job]
            elif attack == "moved_after_checkout":
                item["placement"] = "steps.after-checkout"
            elif attack == "self_attested_sha":
                item["expression"] = expr.replace(
                    "github.sha == '" + _fixture_manifest()["reviewed_code_sha"] + "'",
                    "github.sha == github.sha",
                )
            elif attack == "workflow_sha_omitted":
                item["expression"] = expr.replace(
                    " && github.workflow_sha == '" + _fixture_manifest()["reviewed_workflow_sha"] + "'",
                    "",
                )
            elif attack == "wrong_tag":
                item["expression"] = expr.replace(
                    "github.ref == '" + _fixture_manifest()["reviewed_tag_ref"] + "'",
                    "github.ref == 'refs/heads/main'",
                )
            elif attack == "event_gate_weakened":
                item["expression"] = expr.replace(
                    "github.event_name == 'workflow_dispatch'",
                    "github.event_name != 'push'",
                )
            elif attack == "run_number_as_string":
                item["expression"] = expr.replace(
                    "github.run_number == 385", "github.run_number == '385'"
                )
            else:
                item["can_trade"] = "true"
            results.append({
                "job": job,
                "attack": attack,
                "candidate_exact_match": synthetic_precheckout_job_if_preview_matches(candidate),
            })
    if len(results) != 24 or any(x["candidate_exact_match"] for x in results):
        raise ValueError("DEC-626 precheckout expression negative matrix invalid")
    return results


def _payload(root: Path) -> dict[str, object]:
    source = _source_pins(root)
    model = _candidate_jobs()
    if not synthetic_precheckout_job_if_preview_matches(model):
        raise ValueError("DEC-626 fixed in-memory job if cannot be reviewed")
    negatives = _negatives()
    return {
        "decision": DECISION,
        "version": VERSION,
        "stage": "INERT_PRECHECKOUT_JOB_IF_EXPRESSION_REVIEW_ONLY",
        "source": source,
        "jobs": model,
        "adversarial_case_count": len(negatives),
        "adversarial_cases": negatives,
        "job_if_conditions_would_apply_to_all_three_jobs_before_checkout": True,
        "context_literals_are_compiled_from_fixed_unapproved_fixture_not_live_environment": True,
        "github_context_versus_external_review_source_not_authenticated_here": True,
        "github_workflow_ref_and_workflow_sha_both_compared": True,
        "job_if_not_guaranteed_to_prevent_loading_workflow_definition": True,
        "synthetic_preview_never_installable_as_report": True,
        "requires_approved_external_manifest_and_admin_lock": True,
        "requires_install_review_and_runtime_rechecks": True,
        "requires_separate_one_shot_run385_decision": True,
        "offline_no_github_api_calls": True,
        "no_live_yaml_or_runtime_writes": True,
        "read_only": True,
        "dispatch_blocked": True,
        **{name: False for name in DENIED},
        "next_gate": "SEPARATELY_APPROVED_INSTALL_OF_REAL_PRECHECKOUT_PREINSTALL_PREACCESS_GUARDS",
    }


def build_precheckout_job_if_preview(*, repository_root: Path) -> dict[str, object]:
    report = _payload(Path(repository_root))
    report["report_sha256"] = _digest(report)
    validate_precheckout_job_if_preview(report)
    return report


def validate_precheckout_job_if_preview(report: Mapping[str, object]) -> None:
    if not isinstance(report, Mapping):
        raise ValueError("DEC-626 report not an object")
    unsigned = dict(report)
    digest = unsigned.pop("report_sha256", None)
    if type(digest) is not str or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise ValueError("DEC-626 fingerprint malformed")
    if _digest(unsigned) != digest:
        raise ValueError("DEC-626 report fingerprint mismatch")
    if _canonical(unsigned) != _canonical(_payload(Path(__file__).resolve().parents[3])):
        raise ValueError("DEC-626 report body does not match pinned source")
