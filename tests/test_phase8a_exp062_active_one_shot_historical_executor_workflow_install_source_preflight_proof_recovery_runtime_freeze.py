from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_install_source_preflight_proof_recovery_runtime_freeze import (
    DEC409_FREEZE_FINGERPRINT_SHA256,
    FAILED_DEC404_PROOF_HEAD_SHA,
    FAILED_DEC404_PROOF_JOB_ID,
    FAILED_DEC404_PROOF_RUN_ID,
    RECOVERY_PREFLIGHT_CANONICAL_SHA256,
    RECOVERY_PREFLIGHT_RAW_SHA256,
    RECOVERY_PROOF_ARTIFACT_DIGEST,
    RECOVERY_PROOF_ARTIFACT_ID,
    RECOVERY_PROOF_HEAD_SHA,
    RECOVERY_PROOF_JOB_ID,
    RECOVERY_PROOF_RUN_ID,
    freeze_active_one_shot_historical_executor_workflow_install_source_preflight_recovery_proof_runtime_evidence,
    validate_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery_runtime_freeze_sources,
)


_PREFLIGHT_JSON = r"""{
  "active_one_shot_historical_executor_workflow_install_activation_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_authorization_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_decision_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_execution_authorization_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_execution_contract_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_source_authorized": true,
  "broker_mutation_authorized": false,
  "candidate_compilation_authorized": false,
  "dec402_install_source_contract": "a09eca21a8b5e7b88182040ada5d9298eb922282",
  "decision": "DEC-403",
  "demo_order_authorized": false,
  "discovery_result_authorized": true,
  "dormant_executor_workflow_template": "51ce87584369be957482460d81649adb1cb9f05d",
  "dormant_executor_workflow_template_blob_sha": "51ce87584369be957482460d81649adb1cb9f05d",
  "dormant_executor_workflow_template_path": "docs/superpowers/templates/phase8a-exp062-one-shot-historical-executor.yml.disabled",
  "dormant_executor_workflow_template_present": true,
  "executor_workflow_path_exists": false,
  "expected_executor_workflow_path": ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml",
  "expected_head_sha": "3ea7d3f7bfe8f1dfb3bbac612f74255da4fee432",
  "expected_target_run_attempt": 1,
  "expected_target_run_number": 2,
  "historical_discovery_execution_authorized": true,
  "historical_execute_mode_available": false,
  "historical_executor_available": false,
  "historical_executor_workflow_install_authorized": false,
  "historical_executor_workflow_installed": false,
  "historical_result_attempt_count": 0,
  "historical_result_dispatch_authorized": false,
  "historical_result_run_conclusion": null,
  "historical_result_run_id": null,
  "historical_result_run_status": null,
  "historical_result_slot_consumed": false,
  "historical_result_slot_verified_available": true,
  "install_source_contract_decision": "DEC-402",
  "install_source_contract_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-source-contract-v1",
  "live_order_authorized": false,
  "next_gate": "REPOSITORY_HOSTED_READ_ONLY_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF",
  "phase8b_authorized": false,
  "promotion_authorized": false,
  "proof_run_count": 1,
  "proof_run_id": 36358289723,
  "real_money_authorized": false,
  "replacement_run_authorized": false,
  "rerun_authorized": false,
  "reserved_robustness_access_authorized": false,
  "retry_authorized": false,
  "stage": "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_ACTIVE_WORKFLOW_ABSENT_SLOT_AVAILABLE",
  "trading_authorized": false,
  "version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-source-preflight-v1"
}"""


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _preflight() -> dict[str, object]:
    value = json.loads(_PREFLIGHT_JSON)
    assert isinstance(value, dict)
    return value


def _preflight_bytes(value: dict[str, object] | None = None) -> bytes:
    payload = _preflight() if value is None else value
    return (
        json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def _run() -> dict[str, object]:
    return {
        "id": RECOVERY_PROOF_RUN_ID,
        "name": (
            "phase8a-exp062-active-one-shot-historical-executor-"
            "workflow-install-source-preflight-proof"
        ),
        "path": (
            ".github/workflows/"
            "phase8a-exp062-active-one-shot-historical-executor-"
            "workflow-install-source-preflight-proof.yml"
        ),
        "event": "push",
        "head_branch": "main",
        "head_sha": RECOVERY_PROOF_HEAD_SHA,
        "run_number": 2,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": RECOVERY_PROOF_JOB_ID,
                "name": (
                    "read-only-active-one-shot-historical-executor-"
                    "workflow-install-source-preflight"
                ),
                "status": "completed",
                "conclusion": "success",
            }
        ]
    }


def _artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": RECOVERY_PROOF_ARTIFACT_ID,
                "name": (
                    "exp062-dec407-active-one-shot-historical-executor-workflow-"
                    "install-source-preflight-recovery-"
                    + RECOVERY_PROOF_HEAD_SHA
                ),
                "digest": RECOVERY_PROOF_ARTIFACT_DIGEST,
                "expired": False,
            }
        ]
    }


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallSourcePreflightProofRecoveryRuntimeFreezeTests(
    unittest.TestCase
):
    def _freeze(
        self,
        *,
        run: dict[str, object] | None = None,
        jobs: dict[str, object] | None = None,
        artifacts: dict[str, object] | None = None,
        preflight_bytes: bytes | None = None,
        artifact_zip_sha256: str | None = None,
    ) -> dict[str, object]:
        return freeze_active_one_shot_historical_executor_workflow_install_source_preflight_recovery_proof_runtime_evidence(
            repository_root=Path("."),
            proof_run=_run() if run is None else run,
            proof_jobs_payload=_jobs() if jobs is None else jobs,
            proof_artifacts_payload=_artifacts() if artifacts is None else artifacts,
            preflight_bytes=(
                _preflight_bytes()
                if preflight_bytes is None
                else preflight_bytes
            ),
            artifact_zip_sha256=(
                RECOVERY_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:")
                if artifact_zip_sha256 is None
                else artifact_zip_sha256
            ),
        )

    def test_source_bindings_pin_dec408_dec409_and_terminal_contract(self) -> None:
        report = (
            validate_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery_runtime_freeze_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            report["dec408_reviewer"],
            "b7c28510824b234337318042d8bc8714b7a1c230",
        )
        self.assertEqual(
            report["dec409_freeze_builder"],
            "18fdeb4700cb9233c66ed09dab81b8b61ce4272c",
        )
        self.assertEqual(
            report["dec334_terminal_review_contract"],
            "fda2a45f74b101303467cf7b8527bec1bfc5e168",
        )

    def test_exact_recovery_evidence_freezes_deterministically(self) -> None:
        first = self._freeze()
        second = self._freeze()
        self.assertEqual(first, second)
        self.assertEqual(first["decision"], "DEC-410")
        self.assertEqual(first["failed_proof_run_id"], FAILED_DEC404_PROOF_RUN_ID)
        self.assertEqual(first["failed_proof_head_sha"], FAILED_DEC404_PROOF_HEAD_SHA)
        self.assertEqual(first["failed_proof_job_id"], FAILED_DEC404_PROOF_JOB_ID)
        self.assertEqual(first["failed_proof_run_number"], 1)
        self.assertEqual(first["failed_proof_run_conclusion"], "failure")
        self.assertEqual(first["recovery_proof_run_id"], RECOVERY_PROOF_RUN_ID)
        self.assertEqual(first["recovery_proof_run_number"], 2)
        self.assertEqual(first["recovery_proof_run_conclusion"], "success")
        self.assertEqual(first["recovery_proof_job_id"], RECOVERY_PROOF_JOB_ID)
        self.assertEqual(
            first["recovery_proof_artifact_id"],
            RECOVERY_PROOF_ARTIFACT_ID,
        )
        self.assertEqual(
            first["dec409_freeze_fingerprint_sha256"],
            DEC409_FREEZE_FINGERPRINT_SHA256,
        )
        for field in (
            "active_one_shot_historical_executor_workflow_install_authorization_source_authorized",
            "active_one_shot_historical_executor_workflow_install_decision_source_authorized",
            "active_one_shot_historical_executor_workflow_install_execution_authorization_source_authorized",
            "active_one_shot_historical_executor_workflow_install_execution_contract_source_authorized",
            "active_one_shot_historical_executor_workflow_install_activation_source_authorized",
            "active_one_shot_historical_executor_workflow_install_source_authorized",
        ):
            self.assertTrue(first[field], field)
        self.assertFalse(first["executor_workflow_path_exists"])
        self.assertFalse(first["historical_executor_workflow_install_authorized"])
        self.assertFalse(first["historical_executor_workflow_installed"])
        self.assertFalse(first["historical_executor_available"])
        self.assertFalse(first["historical_result_dispatch_authorized"])
        self.assertFalse(first["historical_execute_mode_available"])
        self.assertFalse(first["trading_authorized"])
        self.assertEqual(
            first["next_gate"],
            (
                "SOURCE_ONLY_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "FINAL_AUTHORIZATION_CONTRACT_BEFORE_INSTALL"
            ),
        )

        unsigned = dict(first)
        fingerprint = unsigned.pop("runtime_freeze_fingerprint_sha256")
        self.assertEqual(
            fingerprint,
            hashlib.sha256(_canonical_json(unsigned)).hexdigest(),
        )

    def test_preflight_fixture_matches_real_hashes(self) -> None:
        raw = _preflight_bytes()
        canonical = _canonical_json(_preflight())
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            RECOVERY_PREFLIGHT_RAW_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            RECOVERY_PREFLIGHT_CANONICAL_SHA256,
        )

    def test_wrong_recovery_run_number_is_rejected(self) -> None:
        run = _run()
        run["run_number"] = 1
        with self.assertRaisesRegex(
            ValueError,
            "recovery proof run run_number mismatch",
        ):
            self._freeze(run=run)

    def test_wrong_recovery_run_id_is_rejected(self) -> None:
        run = _run()
        run["id"] = RECOVERY_PROOF_RUN_ID + 1
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result proof_run_id mismatch",
        ):
            self._freeze(run=run)

    def test_artifact_zip_hash_mismatch_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "artifact ZIP sha256 mismatch"):
            self._freeze(artifact_zip_sha256="0" * 64)

    def test_install_authority_escalation_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["historical_executor_workflow_install_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_workflow_install_authorized",
        ):
            self._freeze(preflight_bytes=_preflight_bytes(preflight))


if __name__ == "__main__":
    unittest.main()
