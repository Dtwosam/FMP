from __future__ import annotations

import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_one_shot_executor_workflow_install_preflight_proof_review import (
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_REVIEW_DECISION,
    review_one_shot_historical_executor_workflow_install_preflight_proof,
    validate_one_shot_historical_executor_workflow_install_preflight_proof_review_sources,
)


HEAD = "a" * 40


def _preflight() -> dict[str, object]:
    return {
        "decision": "DEC-349",
        "version": (
            "fmp-exp062-one-shot-historical-executor-workflow-install-preflight-v1"
        ),
        "install_contract_decision": "DEC-348",
        "install_contract_version": (
            "fmp-exp062-one-shot-historical-executor-workflow-install-contract-v1"
        ),
        "dec348_install_contract_blob_sha": (
            "111a56fdbb8844c119307465e7b7cf6a4d43d95a"
        ),
        "expected_head_sha": HEAD,
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "PREFLIGHT_SOURCE_ABSENT_SLOT_AVAILABLE"
        ),
        "expected_executor_workflow_path": (
            ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
        ),
        "executor_workflow_path_exists": False,
        "workflow_install_slot_verified_available": True,
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
        "one_shot_historical_executor_source_authorized": True,
        "one_shot_historical_executor_workflow_source_authorized": True,
        "one_shot_historical_executor_workflow_install_source_authorized": True,
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
            "REPOSITORY_HOSTED_READ_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "WORKFLOW_INSTALL_PREFLIGHT_PROOF"
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
            "phase8a-exp062-one-shot-historical-executor-"
            "workflow-install-preflight-proof"
        ),
        "path": (
            ".github/workflows/"
            "phase8a-exp062-one-shot-historical-executor-"
            "workflow-install-preflight-proof.yml"
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
                    "read-only-one-shot-historical-executor-"
                    "workflow-install-preflight"
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
                    "exp062-dec350-one-shot-historical-executor-"
                    "workflow-install-preflight-" + HEAD
                ),
                "digest": "sha256:" + ("1" * 64),
                "expired": False,
            }
        ]
    }


class Exp062OneShotHistoricalExecutorWorkflowInstallPreflightProofReviewTests(
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
        return review_one_shot_historical_executor_workflow_install_preflight_proof(
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

    def test_source_bindings_pin_dec350_349_348(self) -> None:
        report = (
            validate_one_shot_historical_executor_workflow_install_preflight_proof_review_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            report["dec350_workflow"],
            "e35c61e91475078f2c40d971c683b899e298c6c3",
        )
        self.assertEqual(
            report["dec349_preflight"],
            "e91b032a4e5e43e5fae5e4f6cc677501cabc8381",
        )
        self.assertEqual(
            report["dec349_preflight_cli"],
            "431cc88658dddfb29c698f026851e78d4574f8a2",
        )
        self.assertEqual(
            report["dec348_install_contract"],
            "111a56fdbb8844c119307465e7b7cf6a4d43d95a",
        )

    def test_valid_proof_reviews_without_install_or_runtime_authority(self) -> None:
        first = self._review()
        second = self._review()
        self.assertEqual(first, second)
        self.assertEqual(
            first["decision"],
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_REVIEW_DECISION,
        )
        self.assertFalse(first["executor_workflow_path_exists"])
        self.assertTrue(first["workflow_install_slot_verified_available"])
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

    def test_installed_state_escalation_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["historical_executor_workflow_installed"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_workflow_installed",
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
