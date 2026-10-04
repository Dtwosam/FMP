from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping


ANNUAL_CATALOGUE_2016_POST_INSTALL_RUNTIME_REPAIR_DECISION = "DEC-531"
ANNUAL_CATALOGUE_2016_POST_INSTALL_RUNTIME_REPAIR_VERSION = (
    "fmp-annual-catalogue-2016-post-install-runtime-repair-v1"
)

ACTIVE_GATE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2016_runtime_authorization.py"
)
EXPECTED_ACTIVE_GATE_BLOB_SHA = "5b034fba697c3de0c0f8b6140d6f84771f1ae54b"
RUNTIME_PATH = "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
EXPECTED_RUNTIME_BLOB_SHA = "b564f5a26fdef146fc6080962e7c4762b0b5949a"
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA = "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"

INSTALL_COMMIT_SHA = "525386dd68955e9f02909f9692987968ab15e516"
FAILED_INSTALLER_RUN_ID = 37205170186
FAILED_INSTALLER_HEAD_SHA = "481e3127415e0b676c590a6edf7e30c0bc10760f"
FAILED_INSTALLER_RUN_NUMBER = 2
FAILED_INSTALLER_RUN_ATTEMPT = 1
FAILED_ORCHESTRATOR_RUN_ID = 37205093376
SOURCE_PLAN_RUN_ID = 37205141103


def _git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload
    ).hexdigest()


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _validate_commit(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"DEC-531 {field} must be a 40-character commit")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"DEC-531 {field} must be hexadecimal") from exc
    return value.lower()


def validate_2016_post_install_runtime_repair_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "active_gate_blob_sha": (
            root / ACTIVE_GATE_PATH,
            EXPECTED_ACTIVE_GATE_BLOB_SHA,
        ),
        "runtime_blob_sha": (
            root / RUNTIME_PATH,
            EXPECTED_RUNTIME_BLOB_SHA,
        ),
        "active_workflow_blob_sha": (
            root / ACTIVE_WORKFLOW_PATH,
            EXPECTED_ACTIVE_WORKFLOW_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-531 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-531 {field} mismatch")
        actual[field] = sha
    return actual


def build_2016_post_install_runtime_repair(
    *,
    repository_root: Path,
    installer_run: Mapping[str, object],
    installer_jobs: Mapping[str, object],
    repair_head_sha: str,
) -> dict[str, object]:
    source = validate_2016_post_install_runtime_repair_sources(
        repository_root=Path(repository_root)
    )
    repair_head_sha = _validate_commit(
        repair_head_sha,
        field="repair_head_sha",
    )

    exact_run = {
        "id": FAILED_INSTALLER_RUN_ID,
        "name": "phase8a-annual-catalogue-2016-runtime-install-executor",
        "path": (
            ".github/workflows/"
            "phase8a-annual-catalogue-2016-runtime-install-executor.yml"
        ),
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": FAILED_INSTALLER_HEAD_SHA,
        "run_number": FAILED_INSTALLER_RUN_NUMBER,
        "run_attempt": FAILED_INSTALLER_RUN_ATTEMPT,
        "status": "completed",
        "conclusion": "failure",
    }
    for field, expected in exact_run.items():
        if installer_run.get(field) != expected:
            raise ValueError(f"DEC-531 installer run {field} mismatch")

    jobs = installer_jobs.get("jobs")
    if not isinstance(jobs, list):
        raise ValueError("DEC-531 installer jobs payload malformed")
    install_jobs = [
        row
        for row in jobs
        if isinstance(row, Mapping)
        and row.get("name") == "install-runtime-authorization"
    ]
    if len(install_jobs) != 1:
        raise ValueError("DEC-531 install job inventory mismatch")
    job = install_jobs[0]
    if job.get("status") != "completed" or job.get("conclusion") != "failure":
        raise ValueError("DEC-531 install job must be completed failure")
    steps = job.get("steps")
    if not isinstance(steps, list):
        raise ValueError("DEC-531 installer steps payload malformed")
    by_name = {
        row.get("name"): row
        for row in steps
        if isinstance(row, Mapping) and isinstance(row.get("name"), str)
    }
    for name in (
        "Apply exact two-file runtime authorization install",
        "Commit exact DEC-518 install",
        "Push only the exact install commit to main",
    ):
        step = by_name.get(name)
        if not isinstance(step, Mapping) or step.get("conclusion") != "success":
            raise ValueError(f"DEC-531 required successful installer step: {name}")
    receipt_step = by_name.get("Build concrete DEC-508 install receipt")
    if (
        not isinstance(receipt_step, Mapping)
        or receipt_step.get("conclusion") != "failure"
    ):
        raise ValueError("DEC-531 DEC-508 receipt failure provenance mismatch")

    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2016_POST_INSTALL_RUNTIME_REPAIR_DECISION,
        "version": ANNUAL_CATALOGUE_2016_POST_INSTALL_RUNTIME_REPAIR_VERSION,
        **source,
        "stage": (
            "ANNUAL_CATALOGUE_2016_POST_INSTALL_RUNTIME_IMPORT_CYCLE_"
            "REPAIRED_DISPATCH_LOCKED"
        ),
        "repository_full_name": "Dtwosam/FMP",
        "install_commit_sha": INSTALL_COMMIT_SHA,
        "repair_head_sha": repair_head_sha,
        "failed_installer_run_id": FAILED_INSTALLER_RUN_ID,
        "failed_installer_run_number": FAILED_INSTALLER_RUN_NUMBER,
        "failed_installer_run_attempt": FAILED_INSTALLER_RUN_ATTEMPT,
        "failed_installer_head_sha": FAILED_INSTALLER_HEAD_SHA,
        "failed_orchestrator_run_id": FAILED_ORCHESTRATOR_RUN_ID,
        "source_plan_run_id": SOURCE_PLAN_RUN_ID,
        "install_mutation_committed": True,
        "install_mutation_pushed": True,
        "install_receipt_failed_after_push": True,
        "runtime_import_cycle_repaired": True,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "annual_workflow_dispatch_authorized": False,
        "run_378_authorized": False,
        "run_379_or_later_authorized": False,
        "next_segment_execution_authorized": False,
        "strategy_v1_synthesis_authorized": False,
        "promotion_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "next_gate": (
            "EXACT_POST_INSTALL_DEC508_RECONSTRUCTION_AND_RUN378_"
            "DISPATCH_RECOVERY"
        ),
    }
    value["repair_fingerprint_sha256"] = _sha256(value)
    validate_2016_post_install_runtime_repair(value)
    return value


def validate_2016_post_install_runtime_repair(
    value: Mapping[str, object],
) -> Mapping[str, object]:
    fingerprint = value.get("repair_fingerprint_sha256")
    unsigned = dict(value)
    unsigned.pop("repair_fingerprint_sha256", None)
    if fingerprint != _sha256(unsigned):
        raise ValueError("DEC-531 repair fingerprint mismatch")
    exact = {
        "decision": "DEC-531",
        "install_commit_sha": INSTALL_COMMIT_SHA,
        "failed_installer_run_id": FAILED_INSTALLER_RUN_ID,
        "failed_installer_run_number": 2,
        "failed_installer_run_attempt": 1,
        "failed_installer_head_sha": FAILED_INSTALLER_HEAD_SHA,
        "failed_orchestrator_run_id": FAILED_ORCHESTRATOR_RUN_ID,
        "source_plan_run_id": SOURCE_PLAN_RUN_ID,
        "install_mutation_committed": True,
        "install_mutation_pushed": True,
        "install_receipt_failed_after_push": True,
        "runtime_import_cycle_repaired": True,
        "runtime_authorization_installed": True,
        "runtime_gate_active": True,
        "annual_workflow_dispatch_authorized": False,
        "run_378_authorized": False,
        "run_379_or_later_authorized": False,
        "next_segment_execution_authorized": False,
        "strategy_v1_synthesis_authorized": False,
        "promotion_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }
    for field, expected in exact.items():
        if value.get(field) != expected:
            raise ValueError(f"DEC-531 {field} mismatch")
    _validate_commit(value.get("repair_head_sha"), field="repair_head_sha")
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2016_POST_INSTALL_RUNTIME_REPAIR_DECISION",
    "ANNUAL_CATALOGUE_2016_POST_INSTALL_RUNTIME_REPAIR_VERSION",
    "FAILED_INSTALLER_RUN_ID",
    "INSTALL_COMMIT_SHA",
    "build_2016_post_install_runtime_repair",
    "validate_2016_post_install_runtime_repair",
    "validate_2016_post_install_runtime_repair_sources",
]
