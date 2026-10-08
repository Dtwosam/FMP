from __future__ import annotations

"""DEC-624: inert job-admission / preinstall / pre-evidence source topology model."""

import hashlib
import json
import re
from pathlib import Path
from typing import Mapping

from .annual_pattern_catalogue_2023_preaccess_identity_gate_topology_audit import (
    FIRST_EVIDENCE_STEP,
    INSTALL,
    _extract_job_step_names,
)
from .annual_pattern_catalogue_2023_tag_ref_guard_rehearsal import (
    ANNUAL_WORKFLOW_BLOB,
    ANNUAL_WORKFLOW_PATH,
    REQUIRED_JOBS,
    _git_blob,
    verify_original_workflow_order,
)

DECISION = "DEC-624"
VERSION = "fmp-run385-inert-three-layer-job-admission-preinstall-preaccess-model-v1"
CHECKOUT = "Checkout"
EXISTING_MAIN_ONLY = "Require exact merged main manual dispatch"
SETUP = "Set up Python"
# Artificial labels in in-memory arrays only; never inserted in GitHub Actions YAML.
EARLY_GATE = "SYNTHETIC only: exact ref and reviewed SHA check before runtime installation"
RUNTIME_GATE = "SYNTHETIC only: post-install exact workflow ref/SHA gate before evidence access"
DENIED = (
    "workflow_job_admission_gate_installed",
    "preinstall_ref_sha_gate_installed",
    "runtime_ref_sha_gate_installed",
    "installed_workflow_tag_compatible",
    "approved_commit_proven",
    "tag_created_or_mutated",
    "immutable_tag_proven",
    "admin_no_bypass_lock_proven",
    "github_context_authenticated_by_model",
    "workflow_amendment_authorized",
    "runtime_amendment_authorized",
    "annual_dispatch_authorized",
    "annual_run385_action_authorized",
    "annual_run385_live_inventory_authenticated",
    "annual_dispatch_executed",
    "retry_authorized",
    "rerun_authorized",
    "replacement_authorized",
    "future_year_authorized",
    "historical_artifact_access_authorized_by_model",
    "broker_mutation_authorized",
    "demo_order_authorized",
    "live_order_authorized",
    "trading_authorized",
)


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _index_once(steps: object, name: str) -> int:
    if type(steps) is not list or not all(type(item) is str for item in steps):
        raise ValueError("DEC-624 step-name list invalid")
    if steps.count(name) != 1:
        raise ValueError("DEC-624 missing/duplicate step: " + name)
    return steps.index(name)


def synthetic_three_layer_placement_matches(
    steps: object, job_admission_before_checkout: object
) -> bool:
    """An in-memory ordering predicate: a match cannot grant execution permission."""
    if not isinstance(steps, Mapping) or not isinstance(job_admission_before_checkout, Mapping):
        return False
    if set(steps) != set(REQUIRED_JOBS) or set(job_admission_before_checkout) != set(REQUIRED_JOBS):
        return False
    try:
        for job in REQUIRED_JOBS:
            if job_admission_before_checkout[job] is not True:
                return False
            s = steps[job]
            checkout = _index_once(s, CHECKOUT)
            existing = _index_once(s, EXISTING_MAIN_ONLY)
            early = _index_once(s, EARLY_GATE)
            setup = _index_once(s, SETUP)
            install = _index_once(s, INSTALL)
            runtime = _index_once(s, RUNTIME_GATE)
            first_evidence = _index_once(s, FIRST_EVIDENCE_STEP[job])
            if not (checkout < existing < early < setup < install < runtime < first_evidence):
                return False
    except (TypeError, ValueError, KeyError):
        return False
    return True


def _current_source(root: Path) -> dict[str, list[str]]:
    source_bytes = (root / ANNUAL_WORKFLOW_PATH).read_bytes()
    if _git_blob(source_bytes) != ANNUAL_WORKFLOW_BLOB:
        raise ValueError("DEC-624 installed workflow Git blob drift")
    workflow = source_bytes.decode("utf-8")
    if verify_original_workflow_order(workflow) != list(REQUIRED_JOBS):
        raise ValueError("DEC-624 current job main-ref guard topology drift")
    steps = _extract_job_step_names(workflow)
    for job in REQUIRED_JOBS:
        names = steps[job]
        if not (
            _index_once(names, CHECKOUT)
            < _index_once(names, EXISTING_MAIN_ONLY)
            < _index_once(names, SETUP)
            < _index_once(names, INSTALL)
            < _index_once(names, FIRST_EVIDENCE_STEP[job])
        ):
            raise ValueError("DEC-624 current preinstall ordering changed")
    return steps


def _candidate(current: Mapping[str, list[str]]) -> tuple[dict[str, list[str]], dict[str, bool]]:
    candidate = {}
    for job in REQUIRED_JOBS:
        names = list(current[job])
        names.insert(_index_once(names, EXISTING_MAIN_ONLY) + 1, EARLY_GATE)
        names.insert(_index_once(names, INSTALL) + 1, RUNTIME_GATE)
        candidate[job] = names
    # A fabricated marker for a proposed job-level condition, not a live YAML if.
    admission = {job: True for job in REQUIRED_JOBS}
    if not synthetic_three_layer_placement_matches(candidate, admission):
        raise ValueError("DEC-624 constructed synthetic gate order failed")
    return candidate, admission


def _adversarial_matrix(
    candidate: Mapping[str, list[str]], admission: Mapping[str, bool]
) -> list[dict[str, object]]:
    scenarios: list[dict[str, object]] = []
    for job in REQUIRED_JOBS:
        for mode in (
            "admission_missing",
            "admission_retyped_integer",
            "early_missing",
            "early_after_install",
            "runtime_missing",
            "runtime_after_evidence",
        ):
            steps = {name: list(names) for name, names in candidate.items()}
            flags = dict(admission)
            if mode == "admission_missing":
                del flags[job]
            elif mode == "admission_retyped_integer":
                flags[job] = 1
            elif mode == "early_missing":
                steps[job].remove(EARLY_GATE)
            elif mode == "early_after_install":
                steps[job].remove(EARLY_GATE)
                steps[job].insert(steps[job].index(INSTALL) + 1, EARLY_GATE)
            elif mode == "runtime_missing":
                steps[job].remove(RUNTIME_GATE)
            else:
                steps[job].remove(RUNTIME_GATE)
                steps[job].insert(steps[job].index(FIRST_EVIDENCE_STEP[job]) + 1, RUNTIME_GATE)
            scenarios.append({
                "job": job,
                "adverse_case": mode,
                "synthetic_three_layer_placement_matches": synthetic_three_layer_placement_matches(
                    steps, flags
                ),
            })
    if len(scenarios) != 18 or any(
        x["synthetic_three_layer_placement_matches"] for x in scenarios
    ):
        raise ValueError("DEC-624 missing an adverse fail-closed case")
    return scenarios


def _payload(root: Path) -> dict[str, object]:
    current = _current_source(root)
    candidate, admission = _candidate(current)
    scenarios = _adversarial_matrix(candidate, admission)
    return {
        "decision": DECISION,
        "version": VERSION,
        "stage": "INERT_THREE_LAYER_TAG_REF_SHA_ADMISSION_MODEL_UNINSTALLED",
        "repository_full_name": "Dtwosam/FMP",
        "source_annual_workflow_path": ANNUAL_WORKFLOW_PATH,
        "source_annual_workflow_git_blob": ANNUAL_WORKFLOW_BLOB,
        "reviewed_jobs": list(REQUIRED_JOBS),
        "current_checkout_runs_before_existing_main_only_guard": True,
        "current_existing_main_only_guard_precedes_runtime_install": True,
        "current_exact_tag_sha_preinstall_gate_missing": True,
        "synthetic_job_admission_gate_before_checkout_in_all_three_jobs": True,
        "synthetic_ref_sha_gate_before_setup_and_install_in_all_three_jobs": True,
        "synthetic_runtime_ref_sha_gate_before_evidence_in_all_three_jobs": True,
        "synthetic_positive_placement_only_not_authorization": synthetic_three_layer_placement_matches(
            candidate, admission
        ),
        "adverse_scenario_count": len(scenarios),
        "adverse_scenario_results": scenarios,
        "github_workflow_ref_and_sha_require_independently_reviewed_expected_values": True,
        "github_ref_protected_alone_cannot_prove_unbypassable_immutability": True,
        "independent_continuous_admin_proof_and_one_shot_action_required": True,
        "no_executable_yaml_generated": True,
        "no_workflow_runtime_or_tag_changed": True,
        "no_github_api_calls_or_historical_reads": True,
        "read_only": True,
        "dispatch_blocked": True,
        **{name: False for name in DENIED},
        "expected_segment": "2023",
        "expected_run": 385,
        "expected_attempt": 1,
        "expected_2022_predecessor_run_id": 37663157285,
        "next_gate": "SEPARATELY_REVIEWED_INSTALLED_REF_SHA_ADMISSION_AND_ADMIN_IMMUTABILITY_PROOF",
    }


def build_three_layer_admission_model(*, repository_root: Path) -> dict[str, object]:
    report = _payload(Path(repository_root))
    report["report_sha256"] = _digest(report)
    validate_three_layer_admission_model(report)
    return report


def validate_three_layer_admission_model(value: Mapping[str, object]) -> None:
    if not isinstance(value, Mapping):
        raise ValueError("DEC-624 report must be a mapping")
    unsigned = dict(value)
    fingerprint = unsigned.pop("report_sha256", None)
    if not isinstance(fingerprint, str) or re.fullmatch(r"[0-9a-f]{64}", fingerprint) is None:
        raise ValueError("DEC-624 malformed report fingerprint")
    if _digest(unsigned) != fingerprint:
        raise ValueError("DEC-624 report fingerprint mismatch")
    if _canonical(unsigned) != _canonical(_payload(Path(__file__).resolve().parents[3])):
        raise ValueError("DEC-624 source-pinned canonical report mismatch")
