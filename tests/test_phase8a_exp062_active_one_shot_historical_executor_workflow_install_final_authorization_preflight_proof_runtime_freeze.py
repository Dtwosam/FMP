from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_install_final_authorization_preflight_proof_runtime_freeze import (
    ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_CANONICAL_SHA256,
    ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_ARTIFACT_DIGEST,
    ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_ARTIFACT_ID,
    ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_HEAD_SHA,
    ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_JOB_ID,
    ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_RUN_ID,
    ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_RAW_SHA256,
    DEC415_FREEZE_FINGERPRINT_SHA256,
    freeze_active_one_shot_historical_executor_workflow_install_final_authorization_preflight_proof_runtime_evidence,
    validate_active_one_shot_historical_executor_workflow_install_final_authorization_preflight_proof_runtime_freeze_sources,
)


_PREFLIGHT_JSON = r"""{
  "active_one_shot_historical_executor_workflow_install_authorization_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_decision_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_execution_authorization_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_execution_contract_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_activation_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_final_authorization_contract_source_authorized": true,
  "broker_mutation_authorized": false,
  "candidate_compilation_authorized": false,
  "dec411_final_authorization_contract_blob_sha": "30493981eb2e5663e1fe620026c2c0af0cc03dd9",
  "decision": "DEC-412",
  "demo_order_authorized": false,
  "discovery_result_authorized": true,
  "dormant_executor_workflow_template_blob_sha": "51ce87584369be957482460d81649adb1cb9f05d",
  "dormant_executor_workflow_template_path": "docs/superpowers/templates/phase8a-exp062-one-shot-historical-executor.yml.disabled",
  "dormant_executor_workflow_template_present": true,
  "executor_workflow_path_exists": false,
  "expected_executor_workflow_path": ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml",
  "expected_head_sha": "8c7598348ade4ed8ea23458eef958add378c3e6d",
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
  "final_authorization_contract_decision": "DEC-411",
  "final_authorization_contract_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-final-authorization-contract-v1",
  "final_authorization_slot_verified_available": true,
  "live_order_authorized": false,
  "next_gate": "REPOSITORY_HOSTED_READ_ONLY_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF",
  "phase8b_authorized": false,
  "promotion_authorized": false,
  "proof_run_count": 1,
  "proof_run_id": 36358289723,
  "real_money_authorized": false,
  "replacement_run_authorized": false,
  "rerun_authorized": false,
  "reserved_robustness_access_authorized": false,
  "retry_authorized": false,
  "stage": "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_SOURCE_READY_ACTIVE_WORKFLOW_ABSENT_SLOT_AVAILABLE",
  "trading_authorized": false,
  "version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-final-authorization-preflight-v1"
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
        "id": ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_RUN_ID,
        "name": (
            "phase8a-exp062-active-one-shot-historical-executor-"
            "workflow-install-final-authorization-preflight-proof"
        ),
        "path": (
            ".github/workflows/"
            "phase8a-exp062-active-one-shot-historical-executor-"
            "workflow-install-final-authorization-preflight-proof.yml"
        ),
        "event": "push",
        "head_branch": "main",
        "head_sha": ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_HEAD_SHA,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_JOB_ID,
                "name": (
                    "read-only-active-one-shot-historical-executor-"
                    "workflow-install-final-authorization-preflight"
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
                "id": ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_ARTIFACT_ID,
                "name": (
                    "exp062-dec413-active-one-shot-historical-executor-workflow-"
                    "install-final-authorization-preflight-"
                    + ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_HEAD_SHA
                ),
                "digest": ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_ARTIFACT_DIGEST,
                "expired": False,
            }
        ]
    }


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallFinalAuthorizationPreflightProofRuntimeFreezeTests(
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
        return freeze_active_one_shot_historical_executor_workflow_install_final_authorization_preflight_proof_runtime_evidence(
            repository_root=Path("."),
            proof_run=_run() if run is None else run,
            proof_jobs_payload=_jobs() if jobs is None else jobs,
            proof_artifacts_payload=_artifacts() if artifacts is None else artifacts,
            preflight_bytes=_preflight_bytes() if preflight_bytes is None else preflight_bytes,
            artifact_zip_sha256=(
                ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_ARTIFACT_DIGEST.removeprefix(
                    "sha256:"
                )
                if artifact_zip_sha256 is None
                else artifact_zip_sha256
            ),
        )

    def test_source_bindings_pin_dec414_dec415_and_terminal_contract(self) -> None:
        report = (
            validate_active_one_shot_historical_executor_workflow_install_final_authorization_preflight_proof_runtime_freeze_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            report["dec414_reviewer"],
            "331ebd4e6871bbf3dc81df3c76b40b5831048736",
        )
        self.assertEqual(
            report["dec415_freeze_builder"],
            "1c5e61ae1602e249c3888e8fa58532cb81fef1aa",
        )
        self.assertEqual(
            report["dec334_terminal_review_contract"],
            "fda2a45f74b101303467cf7b8527bec1bfc5e168",
        )

    def test_exact_real_evidence_freezes_deterministically(self) -> None:
        first = self._freeze()
        second = self._freeze()
        self.assertEqual(first, second)
        self.assertEqual(first["decision"], "DEC-416")
        self.assertEqual(
            first["active_install_final_authorization_preflight_proof_run_id"],
            ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_RUN_ID,
        )
        self.assertEqual(
            first["active_install_final_authorization_preflight_proof_job_id"],
            ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_JOB_ID,
        )
        self.assertEqual(
            first["active_install_final_authorization_preflight_proof_artifact_id"],
            ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_ARTIFACT_ID,
        )
        self.assertEqual(
            first["dec415_freeze_fingerprint_sha256"],
            DEC415_FREEZE_FINGERPRINT_SHA256,
        )
        self.assertEqual(first["dec334_terminal_review_decision"], "DEC-334")
        for field in (
            "active_one_shot_historical_executor_workflow_install_authorization_source_authorized",
            "active_one_shot_historical_executor_workflow_install_decision_source_authorized",
            "active_one_shot_historical_executor_workflow_install_execution_authorization_source_authorized",
            "active_one_shot_historical_executor_workflow_install_execution_contract_source_authorized",
            "active_one_shot_historical_executor_workflow_install_activation_source_authorized",
            "active_one_shot_historical_executor_workflow_install_source_authorized",
            "active_one_shot_historical_executor_workflow_install_final_authorization_contract_source_authorized",
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
            "SOURCE_ONLY_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_ACTION_CONTRACT_BEFORE_INSTALL",
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
            ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_RAW_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_CANONICAL_SHA256,
        )

    def test_wrong_run_id_is_rejected(self) -> None:
        run = _run()
        run["id"] = ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_RUN_ID + 1
        with self.assertRaisesRegex(ValueError, "reviewed result proof_run_id mismatch"):
            self._freeze(run=run)

    def test_wrong_job_id_is_rejected(self) -> None:
        jobs = _jobs()
        jobs["jobs"][0]["id"] = ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_JOB_ID + 1
        with self.assertRaisesRegex(ValueError, "reviewed result proof_job_id mismatch"):
            self._freeze(jobs=jobs)

    def test_wrong_artifact_id_is_rejected(self) -> None:
        artifacts = _artifacts()
        artifacts["artifacts"][0]["id"] = (
            ACTIVE_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_ARTIFACT_ID + 1
        )
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result proof_artifact_id mismatch",
        ):
            self._freeze(artifacts=artifacts)

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
