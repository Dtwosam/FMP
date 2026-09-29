from __future__ import annotations

import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_install_source_preflight_proof_review import (
    review_active_one_shot_historical_executor_workflow_install_source_preflight_proof,
    validate_active_one_shot_historical_executor_workflow_install_source_preflight_proof_review_sources,
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
            "736d77cf08169d5d111a411d1a2d9ae6a5e4cbf5"
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
            "SOURCE_PREFLIGHT_SOURCE_READY_ACTIVE_WORKFLOW_ABSENT_"
            "SLOT_AVAILABLE"
        ),
        "expected_executor_workflow_path": (
            ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
        ),
        "executor_workflow_path_exists": False,
        "install_source_slot_verified_available": True,
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


def _preflight_bytes(value: dict[str, object] | None = None) -> bytes:
    payload = _preflight() if value is None else value
    return (
        json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def _run() -> dict[str, object]:
    return {
        "id": 40000000001,
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
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": 50000000001,
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
                "id": 60000000001,
                "name": (
                    "exp062-dec404-active-one-shot-historical-executor-workflow-"
                    "install-source-preflight-" + HEAD
                ),
                "digest": "sha256:" + ("1" * 64),
                "expired": False,
            }
        ]
    }


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallAuthorizationPreflightProofReviewTests(
    unittest.TestCase
):
    def _review(
        self,
        *,
        run: dict[str, object] | None = None,
        jobs: dict[str, object] | None = None,
        artifacts: dict[str, object] | None = None,
        preflight_bytes: bytes | None = None,
    ) -> dict[str, object]:
        return review_active_one_shot_historical_executor_workflow_install_source_preflight_proof(
            run=_run() if run is None else run,
            jobs_payload=_jobs() if jobs is None else jobs,
            artifacts_payload=_artifacts() if artifacts is None else artifacts,
            preflight_bytes=(
                _preflight_bytes()
                if preflight_bytes is None
                else preflight_bytes
            ),
            expected_head_sha=HEAD,
            repository_root=Path("."),
        )

    def test_source_bindings_are_exact(self) -> None:
        report = (
            validate_active_one_shot_historical_executor_workflow_install_source_preflight_proof_review_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            report["dec404_workflow"],
            "1d08f85ac11402ce373b1f17a0867606fa6b86cf",
        )
        self.assertEqual(
            report["dec403_preflight"],
            "c3081cbe6b62738638321124463e4ac70dab0a5d",
        )
        self.assertEqual(
            report["dec402_install_source_contract"],
            "736d77cf08169d5d111a411d1a2d9ae6a5e4cbf5",
        )

    def test_valid_review_keeps_install_and_runtime_locked(self) -> None:
        first = self._review()
        second = self._review()
        self.assertEqual(first, second)
        self.assertEqual(first["decision"], "DEC-405")
        self.assertFalse(first["executor_workflow_path_exists"])
        self.assertTrue(first["install_source_slot_verified_available"])
        self.assertEqual(first["historical_result_attempt_count"], 0)
        self.assertFalse(first["historical_result_slot_consumed"])
        self.assertTrue(first["historical_result_slot_verified_available"])
        self.assertFalse(
            first["historical_executor_workflow_install_authorized"]
        )
        self.assertFalse(first["historical_executor_workflow_installed"])
        self.assertFalse(first["historical_executor_available"])
        self.assertFalse(first["historical_result_dispatch_authorized"])
        self.assertFalse(first["historical_execute_mode_available"])

    def test_wrong_run_head_is_rejected(self) -> None:
        run = _run()
        run["head_sha"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "run head_sha mismatch"):
            self._review(run=run)

    def test_expired_artifact_is_rejected(self) -> None:
        artifacts = _artifacts()
        artifacts["artifacts"][0]["expired"] = True
        with self.assertRaisesRegex(ValueError, "must be non-expired"):
            self._review(artifacts=artifacts)

    def test_install_authority_escalation_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["historical_executor_workflow_install_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_workflow_install_authorized",
        ):
            self._review(preflight_bytes=_preflight_bytes(preflight))

    def test_consumed_slot_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["historical_result_attempt_count"] = 1
        preflight["historical_result_slot_consumed"] = True
        preflight["historical_result_run_id"] = 40000000000
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_attempt_count mismatch",
        ):
            self._review(preflight_bytes=_preflight_bytes(preflight))

    def test_invalid_json_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            self._review(preflight_bytes=b"{not-json")


if __name__ == "__main__":
    unittest.main()
