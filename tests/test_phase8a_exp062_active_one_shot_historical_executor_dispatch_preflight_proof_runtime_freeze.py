from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_dispatch_preflight_proof_runtime_freeze import (
    ACTIVE_DISPATCH_PREFLIGHT_CANONICAL_SHA256,
    ACTIVE_DISPATCH_PREFLIGHT_PROOF_ARTIFACT_DIGEST,
    ACTIVE_DISPATCH_PREFLIGHT_PROOF_ARTIFACT_ID,
    ACTIVE_DISPATCH_PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256,
    ACTIVE_DISPATCH_PREFLIGHT_PROOF_HEAD_SHA,
    ACTIVE_DISPATCH_PREFLIGHT_PROOF_JOB_ID,
    ACTIVE_DISPATCH_PREFLIGHT_PROOF_RUN_ID,
    ACTIVE_DISPATCH_PREFLIGHT_RAW_SHA256,
    DEC428_FREEZE_FINGERPRINT_SHA256,
    freeze_active_one_shot_historical_executor_dispatch_preflight_proof_runtime_evidence,
    validate_active_one_shot_historical_executor_dispatch_preflight_proof_runtime_freeze_sources,
)


def _preflight() -> dict[str, object]:
    return {
        "active_executor_workflow_blob_sha": "51ce87584369be957482460d81649adb1cb9f05d",
        "active_executor_workflow_path": ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml",
        "active_executor_workflow_present": True,
        "broker_mutation_authorized": False,
        "candidate_compilation_authorized": False,
        "dec424_install_receipt_blob_sha": "27e714620018413a09ceaf287fb7943bf884ee49",
        "decision": "DEC-425",
        "demo_order_authorized": False,
        "discovery_result_authorized": True,
        "executor_workflow_run_conclusion": None,
        "executor_workflow_run_count": 0,
        "executor_workflow_run_id": None,
        "executor_workflow_run_status": None,
        "expected_head_sha": ACTIVE_DISPATCH_PREFLIGHT_PROOF_HEAD_SHA,
        "expected_target_run_attempt": 1,
        "expected_target_run_number": 2,
        "historical_discovery_execution_authorized": True,
        "historical_execute_mode_available": False,
        "historical_executor_available": True,
        "historical_executor_workflow_install_authorized": True,
        "historical_executor_workflow_installed": True,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_dispatch_authorized": False,
        "historical_result_run_conclusion": None,
        "historical_result_run_id": None,
        "historical_result_run_status": None,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "install_receipt_decision": "DEC-424",
        "install_receipt_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-receipt-v1",
        "live_order_authorized": False,
        "next_gate": "EXPLICIT_ONE_SHOT_EXECUTOR_DISPATCH_AUTHORIZATION_BEFORE_RUN",
        "phase8b_authorized": False,
        "promotion_authorized": False,
        "real_money_authorized": False,
        "replacement_run_authorized": False,
        "rerun_authorized": False,
        "reserved_robustness_access_authorized": False,
        "retry_authorized": False,
        "stage": "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_INSTALLED_EXECUTOR_READY_RUNTIME_LOCKED",
        "trading_authorized": False,
        "version": "fmp-exp062-active-one-shot-historical-executor-dispatch-preflight-v1",
    }


def _bytes() -> bytes:
    return (
        json.dumps(_preflight(), sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def _run() -> dict[str, object]:
    return {
        "id": ACTIVE_DISPATCH_PREFLIGHT_PROOF_RUN_ID,
        "name": "phase8a-exp062-active-one-shot-historical-executor-dispatch-preflight-proof",
        "path": ".github/workflows/phase8a-exp062-active-one-shot-historical-executor-dispatch-preflight-proof.yml",
        "event": "push",
        "head_branch": "main",
        "head_sha": ACTIVE_DISPATCH_PREFLIGHT_PROOF_HEAD_SHA,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    return {
        "jobs": [{
            "id": ACTIVE_DISPATCH_PREFLIGHT_PROOF_JOB_ID,
            "name": "read-only-active-one-shot-historical-executor-dispatch-preflight",
            "status": "completed",
            "conclusion": "success",
        }]
    }


def _artifacts() -> dict[str, object]:
    return {
        "artifacts": [{
            "id": ACTIVE_DISPATCH_PREFLIGHT_PROOF_ARTIFACT_ID,
            "name": (
                "exp062-dec426-active-one-shot-historical-executor-"
                "dispatch-preflight-"
                + ACTIVE_DISPATCH_PREFLIGHT_PROOF_HEAD_SHA
            ),
            "digest": ACTIVE_DISPATCH_PREFLIGHT_PROOF_ARTIFACT_DIGEST,
            "expired": False,
        }]
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-429 runtime binding requires the installed executor workflow",
)
class Exp062ActiveOneShotHistoricalExecutorDispatchPreflightProofRuntimeFreezeTests(
    unittest.TestCase
):
    def test_source_bindings_pin_dec427_dec428(self) -> None:
        source = validate_active_one_shot_historical_executor_dispatch_preflight_proof_runtime_freeze_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["dec427_reviewer"],
            "0796656210dffc0dce3e82b3b3b85265061e526b",
        )
        self.assertEqual(
            source["dec428_freeze_builder"],
            "ae724b8e798a7be03240883e1f6b10abea9df012",
        )

    def test_fixture_matches_downloaded_artifact_hashes(self) -> None:
        raw = _bytes()
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            ACTIVE_DISPATCH_PREFLIGHT_RAW_SHA256,
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
            ACTIVE_DISPATCH_PREFLIGHT_CANONICAL_SHA256,
        )

    def test_real_evidence_binds_and_preserves_dispatch_lock(self) -> None:
        value = freeze_active_one_shot_historical_executor_dispatch_preflight_proof_runtime_evidence(
            repository_root=Path("."),
            run=_run(),
            jobs_payload=_jobs(),
            artifacts_payload=_artifacts(),
            preflight_bytes=_bytes(),
            artifact_zip_sha256=(
                ACTIVE_DISPATCH_PREFLIGHT_PROOF_ARTIFACT_ZIP_SHA256
            ),
        )
        self.assertEqual(value["decision"], "DEC-429")
        self.assertEqual(
            value["active_dispatch_preflight_proof_run_id"],
            36688457000,
        )
        self.assertEqual(
            value["dec428_freeze_fingerprint_sha256"],
            DEC428_FREEZE_FINGERPRINT_SHA256,
        )
        self.assertTrue(value["historical_executor_workflow_installed"])
        self.assertTrue(value["historical_executor_available"])
        self.assertEqual(value["executor_workflow_run_count"], 0)
        self.assertFalse(value["historical_result_dispatch_authorized"])
        self.assertFalse(value["historical_execute_mode_available"])
        self.assertFalse(value["trading_authorized"])
        self.assertEqual(
            value["next_gate"],
            "EXPLICIT_ONE_SHOT_EXECUTOR_DISPATCH_AUTHORIZATION_BEFORE_RUN",
        )

    def test_zip_hash_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "artifact ZIP SHA-256 mismatch"):
            freeze_active_one_shot_historical_executor_dispatch_preflight_proof_runtime_evidence(
                repository_root=Path("."),
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                preflight_bytes=_bytes(),
                artifact_zip_sha256="0" * 64,
            )


if __name__ == "__main__":
    unittest.main()
