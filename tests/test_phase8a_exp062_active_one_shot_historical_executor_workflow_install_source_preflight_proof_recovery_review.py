from __future__ import annotations

import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_install_source_preflight_proof_recovery_review import (
    FAILED_DEC404_PROOF_HEAD_SHA,
    FAILED_DEC404_PROOF_JOB_ID,
    FAILED_DEC404_PROOF_RUN_ID,
    review_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery,
    validate_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery_review_sources,
)


HEAD = "a" * 40


def _preflight() -> dict[str, object]:
    return {
        "decision": "DEC-403",
        "version": (
            "fmp-exp062-active-one-shot-historical-executor-workflow-install-"
            "source-preflight-v1"
        ),
        "install_source_contract_decision": "DEC-402",
        "install_source_contract_version": (
            "fmp-exp062-active-one-shot-historical-executor-workflow-install-"
            "source-contract-v1"
        ),
        "dec402_install_source_contract": (
            "a09eca21a8b5e7b88182040ada5d9298eb922282"
        ),
        "dormant_executor_workflow_template_path": (
            "docs/superpowers/templates/"
            "phase8a-exp062-one-shot-historical-executor.yml.disabled"
        ),
        "dormant_executor_workflow_template_blob_sha": (
            "51ce87584369be957482460d81649adb1cb9f05d"
        ),
        "dormant_executor_workflow_template_present": True,
        "expected_head_sha": HEAD,
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "SOURCE_PREFLIGHT_ACTIVE_WORKFLOW_ABSENT_SLOT_AVAILABLE"
        ),
        "expected_executor_workflow_path": (
            ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
        ),
        "executor_workflow_path_exists": False,
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
        "next_gate": (
            "REPOSITORY_HOSTED_READ_ONLY_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF"
        ),
    }


def _raw() -> bytes:
    return (json.dumps(_preflight(), indent=2, sort_keys=True) + "\n").encode()


def _run() -> dict[str, object]:
    return {
        "id": 40000000002,
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
        "head_sha": HEAD,
        "run_number": 2,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": 50000000002,
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
                "id": 60000000002,
                "name": (
                    "exp062-dec407-active-one-shot-historical-executor-"
                    "workflow-install-source-preflight-recovery-" + HEAD
                ),
                "expired": False,
                "digest": "sha256:" + ("1" * 64),
            }
        ]
    }


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallSourcePreflightProofRecoveryReviewTests(
    unittest.TestCase
):
    def test_source_bindings_pin_recovery_workflow_and_dec403(self) -> None:
        source = (
            validate_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery_review_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            source["dec407_recovery_workflow"],
            "2adfc7bd1ccacd158a78532d31ff38f4f175229f",
        )
        self.assertEqual(
            source["dec403_preflight"],
            "cb8ca1ca5b65e9703844d3df9b0a622e2e3ed1bc",
        )

    def test_successful_run_two_is_reviewed_with_failed_run_provenance(self) -> None:
        result = (
            review_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                preflight_bytes=_raw(),
                expected_head_sha=HEAD,
                repository_root=Path("."),
            )
        )
        self.assertEqual(result["decision"], "DEC-408")
        self.assertEqual(result["proof_run_number"], 2)
        self.assertEqual(result["proof_run_attempt"], 1)
        self.assertEqual(result["failed_proof_run_id"], FAILED_DEC404_PROOF_RUN_ID)
        self.assertEqual(result["failed_proof_job_id"], FAILED_DEC404_PROOF_JOB_ID)
        self.assertEqual(
            result["failed_proof_head_sha"],
            FAILED_DEC404_PROOF_HEAD_SHA,
        )
        self.assertEqual(result["failed_proof_run_conclusion"], "failure")
        self.assertFalse(result["executor_workflow_path_exists"])
        self.assertFalse(result["historical_executor_workflow_install_authorized"])
        self.assertFalse(result["historical_result_dispatch_authorized"])
        self.assertFalse(result["historical_execute_mode_available"])
        self.assertFalse(result["trading_authorized"])

    def test_run_one_cannot_be_reclassified_as_recovery_success(self) -> None:
        run = _run()
        run["run_number"] = 1
        with self.assertRaisesRegex(ValueError, "run run_number mismatch"):
            review_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery(
                run=run,
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                preflight_bytes=_raw(),
                expected_head_sha=HEAD,
                repository_root=Path("."),
            )

    def test_bad_preflight_stage_is_rejected(self) -> None:
        value = _preflight()
        value["stage"] = "wrong"
        raw = (json.dumps(value, sort_keys=True) + "\n").encode()
        with self.assertRaisesRegex(ValueError, "preflight stage mismatch"):
            review_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                preflight_bytes=raw,
                expected_head_sha=HEAD,
                repository_root=Path("."),
            )

    def test_artifact_name_drift_is_rejected(self) -> None:
        artifacts = _artifacts()
        row = artifacts["artifacts"][0]
        assert isinstance(row, dict)
        row["name"] = "wrong"
        with self.assertRaisesRegex(ValueError, "artifact name mismatch"):
            review_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=artifacts,
                preflight_bytes=_raw(),
                expected_head_sha=HEAD,
                repository_root=Path("."),
            )


if __name__ == "__main__":
    unittest.main()
