from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .annual_pattern_catalogue_2020_dispatch_action_preflight import (
    ANNUAL_CATALOGUE_2020_DISPATCH_ACTION_PREFLIGHT_DECISION,
    ANNUAL_CATALOGUE_2020_DISPATCH_ACTION_PREFLIGHT_VERSION,
)


ANNUAL_CATALOGUE_2020_RUN382_DISPATCH_RECOVERY_DECISION = "DEC-578"
ANNUAL_CATALOGUE_2020_RUN382_DISPATCH_RECOVERY_VERSION = (
    "fmp-annual-catalogue-2020-run382-dispatch-recovery-v1"
)

DEC575_SOURCE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2020_dispatch_action_preflight.py"
)
DEC575_SOURCE_BLOB_SHA = "26b2148f0d1f49eb8b817f2b2504a11dcb99199a"
ORIGINAL_DISPATCHER_WORKFLOW_PATH = (
    ".github/workflows/phase8a-annual-catalogue-2020-run382-dispatch.yml"
)
ORIGINAL_DISPATCHER_WORKFLOW_BLOB_SHA = (
    "8da7e442ee91e68dc0f4d22947d46c7709f10022"
)
ACTIVE_WORKFLOW_PATH = ".github/workflows/phase8a-annual-pattern-catalogue.yml"
ACTIVE_WORKFLOW_BLOB_SHA = "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1"
INSTALLED_GATE_PATH = (
    "src/fmp/discovery/annual_pattern_catalogue_2020_runtime_authorization.py"
)
INSTALLED_GATE_BLOB_SHA = "695a50b418da752e1bd37d6302f209033ab611f5"
INSTALLED_RUNTIME_PATH = "src/fmp/discovery/annual_pattern_catalogue_runtime.py"
INSTALLED_RUNTIME_BLOB_SHA = "4e124365430672fa63825b272001937c60151644"

SOURCE_PREFLIGHT_WORKFLOW_RUN_ID = 37388217346
SOURCE_PREFLIGHT_WORKFLOW_HEAD_SHA = (
    "557b68e3361acfb1cd4dfdaf70c7b9fe63f68412"
)
SOURCE_PREFLIGHT_ARTIFACT_ID = 11380193702
SOURCE_PREFLIGHT_ARTIFACT_DIGEST = (
    "sha256:b061e88aa70a9897ddb129477ba62925c6ddd738b1cd49270bf46a1d4f3f7343"
)
SOURCE_PREFLIGHT_FINGERPRINT_SHA256 = (
    "f0aad3d285539bbe2f0124db0a0869cc9a6813892c5be75252c46ade933a0a92"
)

FAILED_DISPATCHER_RUN_ID = 37390547252
FAILED_DISPATCHER_JOB_ID = 112034309419
FAILED_DISPATCHER_HEAD_SHA = "3baf4b86a53b4d53d2fc5788b9776006eeacfeee"
FAILED_DISPATCHER_RUN_NUMBER = 1
FAILED_DISPATCHER_RUN_ATTEMPT = 1
FAILED_DISPATCHER_CONCLUSION = "failure"
FAILED_DISPATCHER_STEP = "Fetch and verify exact DEC-575 final preflight"
FAILED_DISPATCH_STEP = "Dispatch exact 2020 annual run 382"

RECOVERY_WORKFLOW_PATH = (
    ".github/workflows/phase8a-annual-catalogue-2020-run382-dispatch-recovery.yml"
)
EXPECTED_RECOVERY_RUN_NUMBER = 1
EXPECTED_RECOVERY_RUN_ATTEMPT = 1
EXPECTED_TARGET_RUN_NUMBER = 382
EXPECTED_TARGET_RUN_ATTEMPT = 1
ANNUAL_SEGMENT_LABEL = "2020"
PREVIOUS_ANNUAL_FREEZE_RUN_ID = 37310525635


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


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def validate_2020_run382_dispatch_recovery_sources(
    *,
    repository_root: Path,
) -> dict[str, str]:
    root = Path(repository_root)
    expected = {
        "dec575_source_blob_sha": (
            root / DEC575_SOURCE_PATH,
            DEC575_SOURCE_BLOB_SHA,
        ),
        "original_dispatcher_workflow_blob_sha": (
            root / ORIGINAL_DISPATCHER_WORKFLOW_PATH,
            ORIGINAL_DISPATCHER_WORKFLOW_BLOB_SHA,
        ),
        "active_workflow_blob_sha": (
            root / ACTIVE_WORKFLOW_PATH,
            ACTIVE_WORKFLOW_BLOB_SHA,
        ),
        "installed_gate_blob_sha": (
            root / INSTALLED_GATE_PATH,
            INSTALLED_GATE_BLOB_SHA,
        ),
        "installed_runtime_blob_sha": (
            root / INSTALLED_RUNTIME_PATH,
            INSTALLED_RUNTIME_BLOB_SHA,
        ),
    }
    actual: dict[str, str] = {}
    for field, (path, expected_sha) in expected.items():
        if not path.is_file():
            raise ValueError(f"DEC-578 source file missing: {path}")
        sha = _git_blob_sha(path)
        if sha != expected_sha:
            raise ValueError(f"DEC-578 {field} mismatch")
        actual[field] = sha

    if ANNUAL_CATALOGUE_2020_DISPATCH_ACTION_PREFLIGHT_DECISION != "DEC-575":
        raise ValueError("DEC-578 predecessor decision drift")
    if (
        ANNUAL_CATALOGUE_2020_DISPATCH_ACTION_PREFLIGHT_VERSION
        != "fmp-annual-catalogue-2020-dispatch-action-preflight-v1"
    ):
        raise ValueError("DEC-578 predecessor version drift")
    return actual


def build_2020_run382_dispatch_recovery_authorization(
    *,
    repository_root: Path,
) -> dict[str, object]:
    source = validate_2020_run382_dispatch_recovery_sources(
        repository_root=repository_root,
    )
    value: dict[str, object] = {
        "decision": ANNUAL_CATALOGUE_2020_RUN382_DISPATCH_RECOVERY_DECISION,
        "version": ANNUAL_CATALOGUE_2020_RUN382_DISPATCH_RECOVERY_VERSION,
        "stage": (
            "ANNUAL_CATALOGUE_2020_RUN382_DISPATCH_RECOVERY_AUTHORIZED_"
            "RUN_NOT_STARTED"
        ),
        **source,
        "authorization_basis": (
            "failed_dec576_before_dispatch_due_stale_expected_run_number_assertion"
        ),
        "source_preflight_decision": "DEC-575",
        "source_preflight_workflow_run_id": SOURCE_PREFLIGHT_WORKFLOW_RUN_ID,
        "source_preflight_workflow_head_sha": SOURCE_PREFLIGHT_WORKFLOW_HEAD_SHA,
        "source_preflight_artifact_id": SOURCE_PREFLIGHT_ARTIFACT_ID,
        "source_preflight_artifact_digest": SOURCE_PREFLIGHT_ARTIFACT_DIGEST,
        "source_preflight_fingerprint_sha256": (
            SOURCE_PREFLIGHT_FINGERPRINT_SHA256
        ),
        "failed_dispatcher_decision": "DEC-576",
        "failed_dispatcher_run_id": FAILED_DISPATCHER_RUN_ID,
        "failed_dispatcher_job_id": FAILED_DISPATCHER_JOB_ID,
        "failed_dispatcher_head_sha": FAILED_DISPATCHER_HEAD_SHA,
        "failed_dispatcher_run_number": FAILED_DISPATCHER_RUN_NUMBER,
        "failed_dispatcher_run_attempt": FAILED_DISPATCHER_RUN_ATTEMPT,
        "failed_dispatcher_conclusion": FAILED_DISPATCHER_CONCLUSION,
        "failed_dispatcher_step": FAILED_DISPATCHER_STEP,
        "failed_dispatch_step": FAILED_DISPATCH_STEP,
        "failed_dispatcher_dispatched_annual_run": False,
        "failed_dispatcher_receipt_uploaded": False,
        "annual_segment_label": ANNUAL_SEGMENT_LABEL,
        "previous_annual_freeze_run_id": PREVIOUS_ANNUAL_FREEZE_RUN_ID,
        "annual_run_382_attempt_count": 0,
        "annual_run_382_slot_consumed": False,
        "annual_run_382_slot_verified_available": True,
        "recovery_workflow_path": RECOVERY_WORKFLOW_PATH,
        "expected_recovery_run_number": EXPECTED_RECOVERY_RUN_NUMBER,
        "expected_recovery_run_attempt": EXPECTED_RECOVERY_RUN_ATTEMPT,
        "expected_target_run_number": EXPECTED_TARGET_RUN_NUMBER,
        "expected_target_run_attempt": EXPECTED_TARGET_RUN_ATTEMPT,
        "explicit_recovery_dispatch_authorized": True,
        "annual_workflow_dispatch_authorized": True,
        "historical_artifact_read_authorized": True,
        "historical_catalogue_execution_authorized": True,
        "historical_result_production_authorized": True,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "run_383_or_later_authorized": False,
        "next_segment_execution_authorized": False,
        "cross_year_result_production_authorized": False,
        "strategy_v1_synthesis_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "next_gate": (
            "EXACT_2020_ANNUAL_PATTERN_CATALOGUE_RECOVERY_DISPATCH_ON_CURRENT_MAIN"
        ),
    }
    value["authorization_fingerprint_sha256"] = _sha256_bytes(
        _canonical_json(value)
    )
    return value


__all__ = [
    "ANNUAL_CATALOGUE_2020_RUN382_DISPATCH_RECOVERY_DECISION",
    "ANNUAL_CATALOGUE_2020_RUN382_DISPATCH_RECOVERY_VERSION",
    "FAILED_DISPATCHER_HEAD_SHA",
    "FAILED_DISPATCHER_JOB_ID",
    "FAILED_DISPATCHER_RUN_ATTEMPT",
    "FAILED_DISPATCHER_RUN_ID",
    "FAILED_DISPATCHER_RUN_NUMBER",
    "EXPECTED_RECOVERY_RUN_ATTEMPT",
    "EXPECTED_RECOVERY_RUN_NUMBER",
    "EXPECTED_TARGET_RUN_ATTEMPT",
    "EXPECTED_TARGET_RUN_NUMBER",
    "build_2020_run382_dispatch_recovery_authorization",
    "validate_2020_run382_dispatch_recovery_sources",
]
