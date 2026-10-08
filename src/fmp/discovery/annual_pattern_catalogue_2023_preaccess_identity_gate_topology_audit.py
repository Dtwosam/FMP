from __future__ import annotations

"""DEC-623: inert three-job pre-access tag/SHA identity gate placement audit."""

import hashlib
import json
import re
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2023_tag_ref_guard_rehearsal import (
    ANNUAL_WORKFLOW_BLOB,
    ANNUAL_WORKFLOW_PATH,
    REQUIRED_JOBS,
    _git_blob,
    verify_original_workflow_order,
)

DECISION = "DEC-623"
VERSION = "fmp-2023-run385-preaccess-identity-gate-topology-audit-v1"
# Only a label in fabricated step-name lists, never a workflow command.
SYNTHETIC_GATE = "DEC-623 SYNTHETIC tag-ref workflow-ref and SHA identity gate — NOT INSTALLED"
INSTALL = "Install pinned annual catalogue runtime"
CURRENT_AUTH = {
    "annual_preflight": "Require separately authorized annual catalogue execution",
    "annual_cell": "Recheck separately authorized annual catalogue execution",
    "annual_freeze": "Recheck separately authorized annual catalogue execution",
}
FIRST_EVIDENCE_STEP = {
    "annual_preflight": "Fetch exact accepted EXP-044 source snapshots",
    "annual_cell": "Download exact accepted EXP-044 feature/outcome/evidence artifacts",
    "annual_freeze": "Download all 18 annual catalogue cell products",
}
FOLLOWUP_EVIDENCE_STEP = {
    "annual_preflight": "Fetch exact prior annual freeze evidence",
}
DENIED = (
    "identity_gate_installed",
    "workflow_tag_ref_binding_installed",
    "runtime_tag_sha_binding_installed",
    "current_preflight_execution_auth_precedes_source_metadata_request",
    "immutable_tag_authenticated",
    "administrator_no_bypass_enforcement_authenticated",
    "tag_created_or_modified",
    "annual_dispatch_authorized",
    "annual_run385_action_authorized",
    "annual_dispatch_executed",
    "retry_authorized",
    "rerun_authorized",
    "replacement_run_authorized",
    "protected_history_read_authorized_by_audit",
    "trading_authorized",
    "broker_mutation_authorized",
    "live_order_authorized",
    "real_money_authorized",
)


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _extract_job_step_names(source: str) -> dict[str, list[str]]:
    if not isinstance(source, str):
        raise ValueError("DEC-623 workflow must be text")
    jobs: dict[str, list[str]] = {}
    in_jobs = False
    job: str | None = None
    for line in source.splitlines():
        if line == "jobs:":
            if in_jobs:
                raise ValueError("DEC-623 duplicate jobs section")
            in_jobs = True
            continue
        if in_jobs and line and not line.startswith(" "):
            in_jobs = False
            job = None
        if not in_jobs:
            continue
        found = re.fullmatch(r"  ([a-z][a-z0-9_-]*):", line)
        if found is not None:
            job = found.group(1)
            if job in jobs:
                raise ValueError("DEC-623 duplicate workflow job")
            jobs[job] = []
            continue
        if job is not None:
            step = re.fullmatch(r"      - name: (.+)", line)
            if step is not None:
                jobs[job].append(step.group(1))
    if set(jobs) != set(REQUIRED_JOBS):
        raise ValueError("DEC-623 exact three-job inventory drift")
    for job, names in jobs.items():
        if not names or len(names) != len(set(names)):
            raise ValueError(f"DEC-623 empty or duplicate step names in {job}")
    return jobs


def _require_once(names: list[str], name: str) -> int:
    if type(names) is not list or not all(type(x) is str for x in names):
        raise ValueError("DEC-623 step names must be a string list")
    if names.count(name) != 1:
        raise ValueError("DEC-623 missing or duplicated step: " + name)
    return names.index(name)


def assess_current_order(steps: Mapping[str, list[str]]) -> dict[str, bool]:
    if set(steps) != set(REQUIRED_JOBS):
        raise ValueError("DEC-623 current job inventory drift")
    result = {}
    for job in REQUIRED_JOBS:
        names = steps[job]
        install = _require_once(names, INSTALL)
        auth = _require_once(names, CURRENT_AUTH[job])
        evidence = _require_once(names, FIRST_EVIDENCE_STEP[job])
        if not install < auth:
            raise ValueError("DEC-623 existing runtime install order drift")
        if job in FOLLOWUP_EVIDENCE_STEP:
            if not evidence < _require_once(names, FOLLOWUP_EVIDENCE_STEP[job]):
                raise ValueError("DEC-623 historical evidence step order drift")
        result[job] = auth < evidence
    # This is the *observed source topology*, not evidence of live execution.
    if result != {"annual_preflight": False, "annual_cell": True, "annual_freeze": True}:
        raise ValueError("DEC-623 observed pre-access authorization ordering changed")
    return result


def synthetic_gate_precedes_evidence(steps: Mapping[str, list[str]]) -> bool:
    """Only checks fabricated step-name ordering, never authenticates a gate."""
    if not isinstance(steps, Mapping) or set(steps) != set(REQUIRED_JOBS):
        return False
    try:
        for job in REQUIRED_JOBS:
            names = steps[job]
            gate = _require_once(names, SYNTHETIC_GATE)
            install = _require_once(names, INSTALL)
            first = _require_once(names, FIRST_EVIDENCE_STEP[job])
            _require_once(names, CURRENT_AUTH[job])
            if not (install < gate < first):
                return False
            if job in FOLLOWUP_EVIDENCE_STEP and not (
                gate < _require_once(names, FOLLOWUP_EVIDENCE_STEP[job])
            ):
                return False
    except (ValueError, TypeError):
        return False
    return True


def _synthetic_steps(current: Mapping[str, list[str]]) -> dict[str, list[str]]:
    candidate = {}
    for job in REQUIRED_JOBS:
        names = list(current[job])
        names.insert(_require_once(names, INSTALL) + 1, SYNTHETIC_GATE)
        candidate[job] = names
    if not synthetic_gate_precedes_evidence(candidate):
        raise ValueError("DEC-623 synthetic early gate placement failed")
    return candidate


def _negative_matrix(candidate: Mapping[str, list[str]]) -> list[dict[str, object]]:
    rows = []
    for job in REQUIRED_JOBS:
        for mode in ("missing", "late", "duplicate"):
            changed = {name: list(steps) for name, steps in candidate.items()}
            changed[job].remove(SYNTHETIC_GATE)
            if mode == "late":
                idx = changed[job].index(FIRST_EVIDENCE_STEP[job])
                changed[job].insert(idx + 1, SYNTHETIC_GATE)
            elif mode == "duplicate":
                idx = changed[job].index(INSTALL)
                changed[job][idx + 1:idx + 1] = [SYNTHETIC_GATE, SYNTHETIC_GATE]
            accepted = synthetic_gate_precedes_evidence(changed)
            rows.append({"job": job, "mode": mode, "synthetic_topology_valid": accepted})
    if len(rows) != 9 or any(row["synthetic_topology_valid"] for row in rows):
        raise ValueError("DEC-623 adverse matrix must fail closed")
    return rows


def _payload(root: Path) -> dict[str, object]:
    source_bytes = (root / ANNUAL_WORKFLOW_PATH).read_bytes()
    if _git_blob(source_bytes) != ANNUAL_WORKFLOW_BLOB:
        raise ValueError("DEC-623 pinned installed annual workflow blob drift")
    source = source_bytes.decode("utf-8")
    if verify_original_workflow_order(source) != list(REQUIRED_JOBS):
        raise ValueError("DEC-623 existing workflow guard order drift")
    current = _extract_job_step_names(source)
    current_authorization_before_evidence = assess_current_order(current)
    candidate = _synthetic_steps(current)
    adverse = _negative_matrix(candidate)
    return {
        "decision": DECISION,
        "version": VERSION,
        "stage": "INERT_STEP_TOPOLOGY_AUDIT_NOT_INSTALLED",
        "repository": "Dtwosam/FMP",
        "annual_workflow_path": ANNUAL_WORKFLOW_PATH,
        "annual_workflow_git_blob": ANNUAL_WORKFLOW_BLOB,
        "reviewed_jobs": list(REQUIRED_JOBS),
        "current_execution_authorization_precedes_first_evidence_step_by_job": current_authorization_before_evidence,
        "preflight_accepted_source_metadata_api_step_before_existing_execution_authorization": True,
        "synthetic_gate_step_label_not_executable": SYNTHETIC_GATE,
        "synthetic_identity_gate_after_runtime_install_before_evidence_by_job": True,
        "synthetic_adverse_scenario_count": len(adverse),
        "synthetic_adverse_scenarios": adverse,
        "requires_real_exact_tag_sha_workflow_ref_runtime_gate_before_external_evidence_access": True,
        "requires_separate_live_three_job_workflow_runtime_amendment": True,
        "requires_independent_continuous_admin_tag_enforcement": True,
        "requires_distinct_one_shot_run385_approval": True,
        "expected_annual_segment": "2023",
        "expected_run_number": 385,
        "expected_attempt": 1,
        "expected_2022_predecessor": 37663157285,
        "no_installed_workflow_or_runtime_mutations": True,
        "offline_no_github_requests_or_historical_downloads": True,
        "read_only": True,
        "dispatch_blocked": True,
        **{key: False for key in DENIED},
        "next_gate": "EXTERNALLY_APPROVED_TAG_AND_WORKFLOW_RUNTIME_AMENDMENT_AND_ADMIN_WITNESS",
    }


def build_2023_preaccess_identity_topology_audit(*, repository_root: Path) -> dict[str, object]:
    report = _payload(Path(repository_root))
    report["report_sha256"] = _digest(report)
    validate_2023_preaccess_identity_topology_audit(report)
    return report


def validate_2023_preaccess_identity_topology_audit(report: Mapping[str, object]) -> None:
    if not isinstance(report, Mapping):
        raise ValueError("DEC-623 report must be a mapping")
    unsigned = dict(report)
    digest = unsigned.pop("report_sha256", None)
    if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise ValueError("DEC-623 fingerprint malformed")
    if _digest(unsigned) != digest:
        raise ValueError("DEC-623 fingerprint mismatch")
    expected = _payload(Path(__file__).resolve().parents[3])
    if _canonical(unsigned) != _canonical(expected):
        raise ValueError("DEC-623 source-bound exact report mismatch")
