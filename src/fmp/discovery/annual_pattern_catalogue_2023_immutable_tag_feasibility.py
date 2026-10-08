from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2023_admin_lock_handoff import (
    validate_2023_admin_lock_handoff,
)
from .annual_pattern_catalogue_2023_dispatch_preflight import _validate_annual_inventory

DECISION = "DEC-615"
VERSION = "fmp-2023-annual-workflow-immutable-tag-feasibility-v1"
ANNUAL_WORKFLOW = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
ANNUAL_WORKFLOW_BLOB = "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
INSTALLED_GATE = "src/fmp/discovery/annual_pattern_catalogue_2023_runtime_authorization.py"
INSTALLED_GATE_BLOB = "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191"
INSTALLED_RUNTIME = "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
INSTALLED_RUNTIME_BLOB = "0fb5cf4d5de1355ff8faffcff565cbbabaf1d7a3"
DEC613_SOURCE = "src/fmp/discovery/annual_pattern_catalogue_2023_admin_lock_handoff.py"
DEC613_SOURCE_BLOB = "6de695a5ea0c27f4fb16b5eae3289c0014155e3b"
DEC614_HEAD_SHA = "ab7c5b34889e666ce14b8a00d572bcd0a07fb2cf"
DEC614_RUN_ID = 37799674451
DEC614_ARTIFACT_ID = 11559788794
DEC614_ZIP_SHA256 = "52f2c02a3ac8002c2f8b7d043080bcf47292e36f9574e9d37bcce2fb93d4f11d"
DEC614_HANDOFF_CANONICAL_SHA256 = "7e470b83d4b9a04017955835ff412aa07a0a7dc91b2193b350354bbbf659a267"
DEC614_HANDOFF_FINGERPRINT = "6376c28695301ff68e44d2c353c47421c5f2a0b1574310ccf39e5508ae5ca3c0"
GITHUB_REF_DOC = "https://docs.github.com/en/actions/reference/workflows-and-actions/variables"
GITHUB_DISPATCH_DOC = "https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event"
MAIN_REF_GUARD = 'test "$GITHUB_REF" = "refs/heads/main"'
REQUIRED_JOBS = ("annual_preflight", "annual_cell", "annual_freeze")
LOCKED_FALSE = (
    "tag_path_compatible_with_current_workflow",
    "immutable_tag_proven",
    "tag_creation_or_movement_authorized",
    "main_exclusive_lock_proven",
    "alternate_ref_execution_authorized",
    "annual_workflow_dispatch_authorized",
    "protected_history_access_authorized",
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
    "broker_mutation_authorized",
    "demo_order_authorized",
    "live_order_authorized",
    "real_money_authorized",
    "trading_authorized",
)


def _canonical(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _commit(value: object) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError("DEC-615 requires a 40-digit main SHA")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError("DEC-615 main SHA is not hexadecimal") from exc
    if value.lower() != value:
        raise ValueError("DEC-615 main SHA must be lowercase")
    return value


def _verify_source(root: Path) -> str:
    for relative, expected in (
        (ANNUAL_WORKFLOW, ANNUAL_WORKFLOW_BLOB),
        (INSTALLED_GATE, INSTALLED_GATE_BLOB),
        (INSTALLED_RUNTIME, INSTALLED_RUNTIME_BLOB),
        (DEC613_SOURCE, DEC613_SOURCE_BLOB),
    ):
        target = root / relative
        if not target.is_file() or _blob_sha(target) != expected:
            raise ValueError(f"DEC-615 source changed: {relative}")
    return (root / ANNUAL_WORKFLOW).read_text(encoding="utf-8")


def _main_guards(workflow: str) -> list[str]:
    found: list[str] = []
    current: str | None = None
    jobs: dict[str, list[str]] = {}
    for line in workflow.splitlines():
        if line.startswith("  ") and not line.startswith("   ") and line.rstrip().endswith(":"):
            job = line.strip()[:-1]
            if job in REQUIRED_JOBS:
                current = job
                jobs[current] = []
            else:
                current = None
        elif current is not None:
            jobs[current].append(line)
    if set(jobs) != set(REQUIRED_JOBS):
        raise ValueError("DEC-615 annual workflow job set changed")
    for job in REQUIRED_JOBS:
        matches = sum(MAIN_REF_GUARD in line for line in jobs[job])
        if matches != 1:
            raise ValueError(f"DEC-615 unexpected main-ref guard count: {job}")
        found.append(job)
    if workflow.count(MAIN_REF_GUARD) != 3:
        raise ValueError("DEC-615 unexpected total main-ref guard count")
    if "  workflow_dispatch:" not in workflow:
        raise ValueError("DEC-615 workflow dispatch trigger missing")
    return found


def build_2023_immutable_tag_feasibility(
    *,
    repository_root: Path,
    handoff: Mapping[str, object],
    main_branch: Mapping[str, object],
    annual_workflow_runs: Mapping[str, object],
    expected_head_sha: str,
) -> dict[str, object]:
    validate_2023_admin_lock_handoff(handoff)
    if handoff.get("expected_head_sha") != DEC614_HEAD_SHA:
        raise ValueError("DEC-615 DEC-614 handoff head mismatch")
    if handoff.get("handoff_fingerprint_sha256") != DEC614_HANDOFF_FINGERPRINT:
        raise ValueError("DEC-615 DEC-614 handoff fingerprint mismatch")
    if _digest(dict(handoff)) != DEC614_HANDOFF_CANONICAL_SHA256:
        raise ValueError("DEC-615 DEC-614 canonical SHA mismatch")
    if handoff.get("dispatch_blocked") is not True:
        raise ValueError("DEC-615 source dispatch block missing")
    if handoff.get("dispatch_action_executed") is not False:
        raise ValueError("DEC-615 source dispatch already executed")

    workflow = _verify_source(Path(repository_root))
    guarded_jobs = _main_guards(workflow)
    head = _commit(expected_head_sha)
    if main_branch.get("name") != "main":
        raise ValueError("DEC-615 requires main")
    commit = main_branch.get("commit")
    if not isinstance(commit, Mapping) or commit.get("sha") != head:
        raise ValueError("DEC-615 main SHA drift")
    if type(main_branch.get("protected")) is not bool:
        raise ValueError("DEC-615 main protection visibility missing")
    inventory = _validate_annual_inventory(annual_workflow_runs)
    if inventory.get("successful_2022_run_id") != 37663157285:
        raise ValueError("DEC-615 2022 predecessor mismatch")
    result: dict[str, object] = {
        "decision": DECISION,
        "version": VERSION,
        "stage": "ANNUAL_CATALOGUE_2023_IMMUTABLE_TAG_FEASIBILITY_BLOCKED",
        "repository_full_name": "Dtwosam/FMP",
        "expected_head_sha": head,
        "source_dec614_head_sha": DEC614_HEAD_SHA,
        "source_dec614_workflow_run_id": DEC614_RUN_ID,
        "source_dec614_artifact_id": DEC614_ARTIFACT_ID,
        "source_dec614_zip_sha256": DEC614_ZIP_SHA256,
        "source_dec614_handoff_canonical_sha256": DEC614_HANDOFF_CANONICAL_SHA256,
        "source_dec614_handoff_fingerprint_sha256": DEC614_HANDOFF_FINGERPRINT,
        "active_annual_workflow_blob_sha": ANNUAL_WORKFLOW_BLOB,
        "installed_gate_blob_sha": INSTALLED_GATE_BLOB,
        "installed_runtime_blob_sha": INSTALLED_RUNTIME_BLOB,
        "dec613_handoff_source_blob_sha": DEC613_SOURCE_BLOB,
        **inventory,
        "annual_segment_label": "2023",
        "expected_run_number": 385,
        "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": 37663157285,
        "main_protected_reported": main_branch["protected"],
        "github_workflow_dispatch_supports_branch_or_tag": True,
        "github_workflow_dispatch_ref_is_not_commit_sha": True,
        "github_ref_for_tag_differs_from_main": True,
        "required_main_ref_guard_jobs": guarded_jobs,
        "current_workflow_requires_main_ref": True,
        "current_main_mutability_blocker_unresolved": True,
        "requires_separate_tag_ruleset_and_no_bypass_review": True,
        "requires_separate_annual_workflow_runtime_amendment": True,
        "requires_separate_immutable_ref_execution_decision": True,
        "read_only": True,
        "dispatch_blocked": True,
        "dispatch_command_present": False,
        **{name: False for name in LOCKED_FALSE},
        "github_ref_documentation": GITHUB_REF_DOC,
        "github_dispatch_documentation": GITHUB_DISPATCH_DOC,
        "next_gate": "REVIEW_TAG_RULES_AND_ANNUAL_WORKFLOW_AMENDMENT_OR_ADMIN_LOCK",
    }
    result["feasibility_fingerprint_sha256"] = _digest(result)
    validate_2023_immutable_tag_feasibility(result)
    return result


def validate_2023_immutable_tag_feasibility(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fp = value.get("feasibility_fingerprint_sha256")
    if not isinstance(fp, str) or len(fp) != 64:
        raise ValueError("DEC-615 feasibility fingerprint missing")
    unsigned = dict(value)
    unsigned.pop("feasibility_fingerprint_sha256", None)
    if _digest(unsigned) != fp:
        raise ValueError("DEC-615 feasibility fingerprint mismatch")
    exact = {
        "decision": DECISION, "version": VERSION,
        "stage": "ANNUAL_CATALOGUE_2023_IMMUTABLE_TAG_FEASIBILITY_BLOCKED",
        "repository_full_name": "Dtwosam/FMP",
        "source_dec614_head_sha": DEC614_HEAD_SHA,
        "source_dec614_workflow_run_id": DEC614_RUN_ID,
        "source_dec614_artifact_id": DEC614_ARTIFACT_ID,
        "source_dec614_zip_sha256": DEC614_ZIP_SHA256,
        "source_dec614_handoff_canonical_sha256": DEC614_HANDOFF_CANONICAL_SHA256,
        "source_dec614_handoff_fingerprint_sha256": DEC614_HANDOFF_FINGERPRINT,
        "active_annual_workflow_blob_sha": ANNUAL_WORKFLOW_BLOB,
        "installed_gate_blob_sha": INSTALLED_GATE_BLOB,
        "installed_runtime_blob_sha": INSTALLED_RUNTIME_BLOB,
        "dec613_handoff_source_blob_sha": DEC613_SOURCE_BLOB,
        "annual_workflow_run_count": 10,
        "failed_run_1_id": 37126711695, "failed_run_376_id": 37191637168,
        "successful_2015_run_id": 37198002653,
        "successful_2016_run_id": 37206992367,
        "successful_2017_run_id": 37227536041,
        "successful_2018_run_id": 37237817538,
        "successful_2019_run_id": 37310525635,
        "successful_2020_run_id": 37443770076,
        "successful_2021_run_id": 37531960014,
        "successful_2022_run_id": 37663157285,
        "annual_segment_label": "2023",
        "expected_run_number": 385, "expected_run_attempt": 1,
        "previous_annual_freeze_run_id": 37663157285,
        "github_workflow_dispatch_supports_branch_or_tag": True,
        "github_workflow_dispatch_ref_is_not_commit_sha": True,
        "github_ref_for_tag_differs_from_main": True,
        "required_main_ref_guard_jobs": list(REQUIRED_JOBS),
        "current_workflow_requires_main_ref": True,
        "current_main_mutability_blocker_unresolved": True,
        "requires_separate_tag_ruleset_and_no_bypass_review": True,
        "requires_separate_annual_workflow_runtime_amendment": True,
        "requires_separate_immutable_ref_execution_decision": True,
        "read_only": True, "dispatch_blocked": True, "dispatch_command_present": False,
        **{name: False for name in LOCKED_FALSE},
        "github_ref_documentation": GITHUB_REF_DOC,
        "github_dispatch_documentation": GITHUB_DISPATCH_DOC,
        "next_gate": "REVIEW_TAG_RULES_AND_ANNUAL_WORKFLOW_AMENDMENT_OR_ADMIN_LOCK",
    }
    allowed = set(exact) | {
        "expected_head_sha", "main_protected_reported",
        "feasibility_fingerprint_sha256",
    }
    if set(value) != allowed:
        raise ValueError("DEC-615 unauthorized fields")
    _commit(value.get("expected_head_sha"))
    if type(value.get("main_protected_reported")) is not bool:
        raise ValueError("DEC-615 protected field type mismatch")
    for key, expected in exact.items():
        actual = value.get(key)
        valid = (actual is expected if type(expected) is bool
                 else (type(actual) is int and actual == expected)
                 if type(expected) is int else actual == expected)
        if not valid:
            raise ValueError(f"DEC-615 {key} mismatch")
    return value
