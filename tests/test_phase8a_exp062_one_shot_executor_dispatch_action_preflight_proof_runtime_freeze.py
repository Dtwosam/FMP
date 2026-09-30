from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_one_shot_executor_dispatch_action_preflight_proof_runtime_freeze import (
    DEC433_REVIEWER_BLOB_SHA,
    DEC434_FREEZE_BUILDER_BLOB_SHA,
    DEC434_FREEZE_FINGERPRINT_SHA256,
    ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_CANONICAL_SHA256,
    ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_ARTIFACT_DIGEST,
    ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_ARTIFACT_ID,
    ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256,
    ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_HEAD_SHA,
    ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_JOB_ID,
    ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_RUN_ID,
    ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_RAW_SHA256,
    freeze_one_shot_executor_dispatch_action_preflight_proof_runtime_evidence,
    validate_one_shot_executor_dispatch_action_preflight_proof_runtime_freeze_sources,
)


def _preflight() -> dict[str, object]:
    return {
        "active_executor_workflow_blob_sha": "51ce87584369be957482460d81649adb1cb9f05d",
        "active_executor_workflow_path": ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml",
        "active_executor_workflow_present": True,
        "authorization_decision": "DEC-430",
        "authorization_version": "fmp-exp062-active-one-shot-historical-executor-dispatch-authorization-v1",
        "broker_mutation_authorized": False,
        "candidate_compilation_authorized": False,
        "dec430_dispatch_authorization_blob_sha": "87aada4c5224c633e8eb419f971c8f7f0699b18f",
        "decision": "DEC-431",
        "demo_order_authorized": False,
        "discovery_result_authorized": True,
        "executor_workflow_run_count": 0,
        "expected_executor_run_attempt": 1,
        "expected_executor_run_number": 1,
        "expected_head_sha": ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_HEAD_SHA,
        "expected_target_run_attempt": 1,
        "expected_target_run_number": 2,
        "explicit_one_shot_executor_dispatch_authorized": True,
        "historical_discovery_execution_authorized": True,
        "historical_execute_mode_available": False,
        "historical_executor_available": True,
        "historical_executor_workflow_installed": True,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_dispatch_authorized": True,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "live_order_authorized": False,
        "next_gate": "REPOSITORY_HOSTED_READ_ONLY_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_PROOF",
        "phase8b_authorized": False,
        "planned_executor_dispatch_command": "gh workflow run phase8a-exp062-one-shot-historical-executor.yml --ref main",
        "promotion_authorized": False,
        "real_money_authorized": False,
        "replacement_run_authorized": False,
        "rerun_authorized": False,
        "reserved_robustness_access_authorized": False,
        "retry_authorized": False,
        "stage": "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_AUTHORIZED_SLOT_AVAILABLE",
        "trading_authorized": False,
        "version": "fmp-exp062-active-one-shot-historical-executor-dispatch-action-preflight-v1",
    }


def _bytes() -> bytes:
    return (
        json.dumps(_preflight(), sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def _run() -> dict[str, object]:
    return {
        "id": ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_RUN_ID,
        "name": "phase8a-exp062-one-shot-executor-dispatch-action-preflight-proof",
        "path": ".github/workflows/phase8a-exp062-one-shot-executor-dispatch-action-preflight-proof.yml",
        "event": "push",
        "head_branch": "main",
        "head_sha": ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_HEAD_SHA,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    return {
        "jobs": [{
            "id": ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_JOB_ID,
            "name": "read-only-one-shot-executor-dispatch-action-preflight",
            "status": "completed",
            "conclusion": "success",
        }]
    }


def _artifacts() -> dict[str, object]:
    return {
        "artifacts": [{
            "id": ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_ARTIFACT_ID,
            "name": (
                "exp062-dec432-one-shot-executor-dispatch-action-preflight-"
                + ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_HEAD_SHA
            ),
            "digest": ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_ARTIFACT_DIGEST,
            "expired": False,
        }]
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-435 runtime binding requires the installed executor workflow",
)
class Exp062OneShotExecutorDispatchActionPreflightProofRuntimeFreezeTests(
    unittest.TestCase
):
    def test_source_bindings_pin_dec433_dec434(self) -> None:
        source = validate_one_shot_executor_dispatch_action_preflight_proof_runtime_freeze_sources(
            repository_root=Path("."),
        )
        self.assertEqual(source["dec433_reviewer"], DEC433_REVIEWER_BLOB_SHA)
        self.assertEqual(
            source["dec434_freeze_builder"],
            DEC434_FREEZE_BUILDER_BLOB_SHA,
        )

    def test_fixture_matches_downloaded_artifact_hashes(self) -> None:
        raw = _bytes()
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_RAW_SHA256,
        )
        value = json.loads(raw)
        canonical = (
            json.dumps(
                value,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_CANONICAL_SHA256,
        )

    def test_real_evidence_binds_authorized_unstarted_executor(self) -> None:
        value = freeze_one_shot_executor_dispatch_action_preflight_proof_runtime_evidence(
            repository_root=Path("."),
            run=_run(),
            jobs_payload=_jobs(),
            artifacts_payload=_artifacts(),
            preflight_bytes=_bytes(),
            artifact_zip_sha256=(
                ONE_SHOT_DISPATCH_ACTION_PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256
            ),
        )
        self.assertEqual(value["decision"], "DEC-435")
        self.assertEqual(
            value["one_shot_dispatch_action_preflight_proof_run_id"],
            36695220474,
        )
        self.assertEqual(
            value["dec434_freeze_fingerprint_sha256"],
            DEC434_FREEZE_FINGERPRINT_SHA256,
        )
        self.assertTrue(value["explicit_one_shot_executor_dispatch_authorized"])
        self.assertTrue(value["historical_result_dispatch_authorized"])
        self.assertTrue(value["historical_executor_workflow_installed"])
        self.assertTrue(value["historical_executor_available"])
        self.assertEqual(value["executor_workflow_run_count"], 0)
        self.assertEqual(value["historical_result_attempt_count"], 0)
        self.assertFalse(value["historical_execute_mode_available"])
        self.assertFalse(value["rerun_authorized"])
        self.assertFalse(value["trading_authorized"])
        self.assertEqual(
            value["next_gate"],
            "SUBMIT_AUTHORIZED_ONE_SHOT_EXECUTOR_RUN_1_ATTEMPT_1",
        )

    def test_zip_hash_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "artifact ZIP SHA-256 mismatch"):
            freeze_one_shot_executor_dispatch_action_preflight_proof_runtime_evidence(
                repository_root=Path("."),
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                preflight_bytes=_bytes(),
                artifact_zip_sha256="0" * 64,
            )


if __name__ == "__main__":
    unittest.main()
