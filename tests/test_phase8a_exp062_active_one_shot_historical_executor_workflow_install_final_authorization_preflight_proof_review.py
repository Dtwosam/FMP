from __future__ import annotations

import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_install_final_authorization_preflight_proof_review import (
    review_active_one_shot_historical_executor_workflow_install_final_authorization_preflight_proof,
    validate_active_one_shot_historical_executor_workflow_install_final_authorization_preflight_proof_review_sources,
)


HEAD = "a" * 40


def _preflight() -> dict[str, object]:
    return {
        "decision": "DEC-412",
        "version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-final-authorization-preflight-v1",
        "final_authorization_contract_decision": "DEC-411",
        "final_authorization_contract_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-final-authorization-contract-v1",
        "dec411_final_authorization_contract_blob_sha": "30493981eb2e5663e1fe620026c2c0af0cc03dd9",
        "dormant_executor_workflow_template_path": "docs/superpowers/templates/phase8a-exp062-one-shot-historical-executor.yml.disabled",
        "dormant_executor_workflow_template_blob_sha": "51ce87584369be957482460d81649adb1cb9f05d",
        "dormant_executor_workflow_template_present": True,
        "expected_head_sha": HEAD,
        "stage": "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_SOURCE_READY_ACTIVE_WORKFLOW_ABSENT_SLOT_AVAILABLE",
        "expected_executor_workflow_path": ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml",
        "executor_workflow_path_exists": False,
        "final_authorization_slot_verified_available": True,
        "proof_run_id": 36358289723,
        "proof_run_count": 1,
        "historical_result_attempt_count": 0,
        "historical_result_run_id": None,
        "historical_result_run_status": None,
        "historical_result_run_conclusion": None,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "active_one_shot_historical_executor_workflow_install_authorization_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_decision_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_execution_authorization_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_execution_contract_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_activation_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_source_authorized": True,
        "active_one_shot_historical_executor_workflow_install_final_authorization_contract_source_authorized": True,
        "historical_executor_workflow_install_authorized": False,
        "historical_executor_workflow_installed": False,
        "historical_executor_available": False,
        "historical_result_dispatch_authorized": False,
        "historical_execute_mode_available": False,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "next_gate": "REPOSITORY_HOSTED_READ_ONLY_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF",
    }


def _bytes(value: dict[str, object] | None = None) -> bytes:
    payload = _preflight() if value is None else value
    return (
        json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def _run() -> dict[str, object]:
    return {
        "id": 1,
        "name": "phase8a-exp062-active-one-shot-historical-executor-workflow-install-final-authorization-preflight-proof",
        "path": ".github/workflows/phase8a-exp062-active-one-shot-historical-executor-workflow-install-final-authorization-preflight-proof.yml",
        "event": "push",
        "head_branch": "main",
        "head_sha": HEAD,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    return {
        "jobs": [{
            "id": 2,
            "name": "read-only-active-one-shot-historical-executor-workflow-install-final-authorization-preflight",
            "status": "completed",
            "conclusion": "success",
        }]
    }


def _artifacts() -> dict[str, object]:
    return {
        "artifacts": [{
            "id": 3,
            "name": "exp062-dec413-active-one-shot-historical-executor-workflow-install-final-authorization-preflight-" + HEAD,
            "digest": "sha256:" + "1" * 64,
            "expired": False,
        }]
    }


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallFinalAuthorizationPreflightProofReviewTests(
    unittest.TestCase
):
    def test_source_bindings_pin_dec413_dec412_dec411(self) -> None:
        report = validate_active_one_shot_historical_executor_workflow_install_final_authorization_preflight_proof_review_sources(
            repository_root=Path("."),
        )
        self.assertEqual(report["dec413_workflow"], "dace2b0752937b2d15349f5564b88ed9aea82bf1")
        self.assertEqual(report["dec412_preflight"], "89c6a606703ce72916451e0168e1b58bb765baaa")
        self.assertEqual(report["dec411_final_authorization_contract"], "30493981eb2e5663e1fe620026c2c0af0cc03dd9")

    def test_valid_proof_reviews_and_preserves_locks(self) -> None:
        reviewed = review_active_one_shot_historical_executor_workflow_install_final_authorization_preflight_proof(
            run=_run(),
            jobs_payload=_jobs(),
            artifacts_payload=_artifacts(),
            preflight_bytes=_bytes(),
            expected_head_sha=HEAD,
            repository_root=Path("."),
        )
        self.assertEqual(reviewed["decision"], "DEC-414")
        self.assertEqual(reviewed["proof_run_number"], 1)
        self.assertEqual(reviewed["final_authorization_preflight_decision"], "DEC-412")
        self.assertFalse(reviewed["executor_workflow_path_exists"])
        for field in (
            "active_one_shot_historical_executor_workflow_install_authorization_source_authorized",
            "active_one_shot_historical_executor_workflow_install_decision_source_authorized",
            "active_one_shot_historical_executor_workflow_install_execution_authorization_source_authorized",
            "active_one_shot_historical_executor_workflow_install_execution_contract_source_authorized",
            "active_one_shot_historical_executor_workflow_install_activation_source_authorized",
            "active_one_shot_historical_executor_workflow_install_source_authorized",
            "active_one_shot_historical_executor_workflow_install_final_authorization_contract_source_authorized",
        ):
            self.assertTrue(reviewed[field], field)
        self.assertFalse(reviewed["historical_executor_workflow_install_authorized"])
        self.assertFalse(reviewed["historical_result_dispatch_authorized"])
        self.assertFalse(reviewed["trading_authorized"])

    def test_wrong_run_number_is_rejected(self) -> None:
        run = _run()
        run["run_number"] = 2
        with self.assertRaisesRegex(ValueError, "run run_number mismatch"):
            review_active_one_shot_historical_executor_workflow_install_final_authorization_preflight_proof(
                run=run,
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                preflight_bytes=_bytes(),
                expected_head_sha=HEAD,
                repository_root=Path("."),
            )

    def test_expired_artifact_is_rejected(self) -> None:
        artifacts = _artifacts()
        artifacts["artifacts"][0]["expired"] = True
        with self.assertRaisesRegex(ValueError, "must be non-expired"):
            review_active_one_shot_historical_executor_workflow_install_final_authorization_preflight_proof(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=artifacts,
                preflight_bytes=_bytes(),
                expected_head_sha=HEAD,
                repository_root=Path("."),
            )

    def test_authority_escalation_is_rejected(self) -> None:
        value = _preflight()
        value["historical_executor_workflow_install_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_workflow_install_authorized",
        ):
            review_active_one_shot_historical_executor_workflow_install_final_authorization_preflight_proof(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                preflight_bytes=_bytes(value),
                expected_head_sha=HEAD,
                repository_root=Path("."),
            )


if __name__ == "__main__":
    unittest.main()
