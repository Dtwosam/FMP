from __future__ import annotations

"""DEC-632: offline workflow-definition SHA admission model, never a live gate.

The synthetic fixture is deliberately NOT an approved tag, commit, or
workflow. Even a matching tuple cannot authorize a dispatch or trading.
"""

import hashlib
import json
from typing import Mapping

DECISION = "DEC-632"
REPOSITORY = "Dtwosam/FMP"
WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
WORKFLOW_NAME = "phase8a-annual-pattern-catalogue"
FIXTURE_TAG = "refs/tags/fmp/phase8a/2023/run385/dec632-unapproved-fixture"
FIXTURE_COMMIT = "a" * 40
FIXTURE_WORKFLOW_SHA = "c" * 40
PREDECESSOR_RUN_ID = 37663157285
FIELDS = frozenset({
    "event_name", "repository", "ref", "ref_type", "sha", "workflow",
    "workflow_ref", "workflow_sha", "segment", "run_number", "run_attempt",
    "predecessor_2022_freeze_run_id",
})
EXPECTED = {
    "event_name": "workflow_dispatch",
    "repository": REPOSITORY,
    "ref": FIXTURE_TAG,
    "ref_type": "tag",
    "sha": FIXTURE_COMMIT,
    "workflow": WORKFLOW_NAME,
    "workflow_ref": f"{REPOSITORY}/{WORKFLOW_PATH}@{FIXTURE_TAG}",
    "workflow_sha": FIXTURE_WORKFLOW_SHA,
    "segment": "2023",
    "run_number": 385,
    "run_attempt": 1,
    "predecessor_2022_freeze_run_id": PREDECESSOR_RUN_ID,
}


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def synthetic_identity_matches(value: object) -> bool:
    """A match is only a model fixture, never authority to execute."""
    if not isinstance(value, Mapping) or set(value.keys()) != FIELDS:
        return False
    for key, expected in EXPECTED.items():
        actual = value[key]
        if type(actual) is not type(expected) or actual != expected:
            return False
    return True


def _adverse_cases() -> tuple[tuple[str, dict[str, object]], ...]:
    cases: list[tuple[str, dict[str, object]]] = []
    replacements: tuple[tuple[str, str, object], ...] = (
        ("wrong_event", "event_name", "push"),
        ("wrong_repository", "repository", "fork/FMP"),
        ("mutable_main_ref", "ref", "refs/heads/main"),
        ("different_tag_ref", "ref", FIXTURE_TAG + "-other"),
        ("branch_ref_type", "ref_type", "branch"),
        ("source_commit_drift", "sha", "b" * 40),
        ("malformed_source_commit", "sha", 123),
        ("workflow_name_drift", "workflow", "not-the-annual-workflow"),
        ("workflow_path_drift", "workflow_ref", f"{REPOSITORY}/.github/workflows/other.yml@{FIXTURE_TAG}"),
        ("workflow_ref_drift", "workflow_ref", f"{REPOSITORY}/{WORKFLOW_PATH}@refs/heads/main"),
        ("workflow_definition_sha_drift", "workflow_sha", "d" * 40),
        ("missing_workflow_sha_value", "workflow_sha", None),
        ("wrong_segment", "segment", "2024"),
        ("wrong_run", "run_number", 386),
        ("bool_run", "run_number", True),
        ("wrong_attempt", "run_attempt", 2),
        ("bool_attempt", "run_attempt", True),
        ("wrong_predecessor", "predecessor_2022_freeze_run_id", 123),
    )
    for name, key, replacement in replacements:
        data = dict(EXPECTED)
        data[key] = replacement
        cases.append((name, data))
    for key in ("workflow_sha", "sha", "workflow_ref"):
        data = dict(EXPECTED)
        data.pop(key)
        cases.append((f"absent_{key}", data))
    additional = dict(EXPECTED)
    additional["authorized"] = True
    cases.append(("injected_authority", additional))
    return tuple(cases)


def _report_payload() -> dict[str, object]:
    cases = [
        {"name": "synthetic_exact_tuple", "matches": synthetic_identity_matches(EXPECTED)}
    ]
    cases.extend({"name": name, "matches": synthetic_identity_matches(data)} for name, data in _adverse_cases())
    if cases[0]["matches"] is not True or any(case["matches"] for case in cases[1:]):
        raise ValueError("DEC-632 offline scenario invariant failed")
    return {
        "decision": DECISION,
        "stage": "OFFLINE_UNAPPROVED_WORKFLOW_SHA_IDENTITY_PREVIEW",
        "fixture_is_not_approved": True,
        "synthetic_exact_tuple_match": True,
        "workflow_sha_separately_bound": True,
        "adverse_scenario_count": len(cases) - 1,
        "scenarios": cases,
        "real_git_ref_immutability_verified": False,
        "independent_review_present": False,
        "workflow_amendment_installed": False,
        "annual_workflow_dispatch_authorized": False,
        "run385_execution_authorized": False,
        "rerun_authorized": False,
        "trading_authorized": False,
        "dispatch_blocked": True,
        "no_network_or_repo_mutation": True,
        "next_gate": "INDEPENDENT_REVIEW_AND_EXTERNALLY_PROVEN_REF_PLUS_WORKFLOW_SHA_BINDING",
    }


def build_offline_workflow_sha_identity_report() -> dict[str, object]:
    payload = _report_payload()
    return {**payload, "report_sha256": _digest(payload)}


def validate_offline_workflow_sha_identity_report(value: object) -> None:
    if not isinstance(value, Mapping):
        raise ValueError("DEC-632 report must be a mapping")
    actual = dict(value)
    fp = actual.pop("report_sha256", None)
    if not isinstance(fp, str) or len(fp) != 64 or _digest(actual) != fp:
        raise ValueError("DEC-632 report digest mismatch")
    if _canonical(actual) != _canonical(_report_payload()):
        raise ValueError("DEC-632 source-bound report mismatch")
