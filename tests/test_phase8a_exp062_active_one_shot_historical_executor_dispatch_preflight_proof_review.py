from __future__ import annotations

import json
import os
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_dispatch_preflight_proof_review import (
    review_active_one_shot_historical_executor_dispatch_preflight_proof,
    validate_active_one_shot_historical_executor_dispatch_preflight_proof_review_sources,
)


HEAD = "a" * 40


def _preflight() -> dict[str, object]:
    return {
        "decision": "DEC-425",
        "version": "fmp-exp062-active-one-shot-historical-executor-dispatch-preflight-v1",
        "install_receipt_decision": "DEC-424",
        "install_receipt_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-receipt-v1",
        "dec424_install_receipt_blob_sha": "27e714620018413a09ceaf287fb7943bf884ee49",
        "active_executor_workflow_blob_sha": "51ce87584369be957482460d81649adb1cb9f05d",
        "expected_head_sha": HEAD,
        "stage": "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_INSTALLED_EXECUTOR_READY_RUNTIME_LOCKED",
        "active_executor_workflow_path": ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml",
        "active_executor_workflow_present": True,
        "historical_executor_workflow_install_authorized": True,
        "historical_executor_workflow_installed": True,
        "historical_executor_available": True,
        "executor_workflow_run_count": 0,
        "executor_workflow_run_id": None,
        "executor_workflow_run_status": None,
        "executor_workflow_run_conclusion": None,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_run_id": None,
        "historical_result_run_status": None,
        "historical_result_run_conclusion": None,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
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
        "next_gate": "EXPLICIT_ONE_SHOT_EXECUTOR_DISPATCH_AUTHORIZATION_BEFORE_RUN",
    }


def _bytes(value: dict[str, object] | None = None) -> bytes:
    payload = _preflight() if value is None else value
    return (
        json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def _run() -> dict[str, object]:
    return {
        "id": 1,
        "name": "phase8a-exp062-active-one-shot-historical-executor-dispatch-preflight-proof",
        "path": ".github/workflows/phase8a-exp062-active-one-shot-historical-executor-dispatch-preflight-proof.yml",
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
            "name": "read-only-active-one-shot-historical-executor-dispatch-preflight",
            "status": "completed",
            "conclusion": "success",
        }]
    }


def _artifacts() -> dict[str, object]:
    return {
        "artifacts": [{
            "id": 3,
            "name": (
                "exp062-dec426-active-one-shot-historical-executor-"
                "dispatch-preflight-" + HEAD
            ),
            "digest": "sha256:" + "1" * 64,
            "expired": False,
        }]
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-427 source review requires the installed executor workflow",
)
class Exp062ActiveOneShotHistoricalExecutorDispatchPreflightProofReviewTests(
    unittest.TestCase
):
    def test_source_bindings_pin_dec426_dec425_dec424(self) -> None:
        report = validate_active_one_shot_historical_executor_dispatch_preflight_proof_review_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            report["dec426_workflow"],
            "0bb9cd78639ebad68eb7db0fb9d083ce86b75319",
        )
        self.assertEqual(
            report["dec425_preflight"],
            "1978f71bb11097613d3820127f7a04ce2bf81adb",
        )
        self.assertEqual(
            report["dec424_install_receipt"],
            "27e714620018413a09ceaf287fb7943bf884ee49",
        )
        self.assertEqual(
            report["active_executor_workflow"],
            "51ce87584369be957482460d81649adb1cb9f05d",
        )

    def test_valid_proof_reviews_installed_state_and_preserves_locks(self) -> None:
        reviewed = review_active_one_shot_historical_executor_dispatch_preflight_proof(
            run=_run(),
            jobs_payload=_jobs(),
            artifacts_payload=_artifacts(),
            preflight_bytes=_bytes(),
            expected_head_sha=HEAD,
            repository_root=Path("."),
        )
        self.assertEqual(reviewed["decision"], "DEC-427")
        self.assertEqual(reviewed["proof_run_number"], 1)
        self.assertEqual(reviewed["dispatch_preflight_decision"], "DEC-425")
        self.assertTrue(reviewed["active_executor_workflow_present"])
        self.assertTrue(reviewed["historical_executor_workflow_installed"])
        self.assertTrue(reviewed["historical_executor_available"])
        self.assertEqual(reviewed["executor_workflow_run_count"], 0)
        self.assertFalse(reviewed["historical_result_dispatch_authorized"])
        self.assertFalse(reviewed["historical_execute_mode_available"])
        self.assertFalse(reviewed["trading_authorized"])

    def test_wrong_run_number_is_rejected(self) -> None:
        run = _run()
        run["run_number"] = 2
        with self.assertRaisesRegex(ValueError, "run run_number mismatch"):
            review_active_one_shot_historical_executor_dispatch_preflight_proof(
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
            review_active_one_shot_historical_executor_dispatch_preflight_proof(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=artifacts,
                preflight_bytes=_bytes(),
                expected_head_sha=HEAD,
                repository_root=Path("."),
            )

    def test_dispatch_authority_escalation_is_rejected(self) -> None:
        value = _preflight()
        value["historical_result_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_dispatch_authorized",
        ):
            review_active_one_shot_historical_executor_dispatch_preflight_proof(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                preflight_bytes=_bytes(value),
                expected_head_sha=HEAD,
                repository_root=Path("."),
            )

    def test_missing_installed_state_is_rejected(self) -> None:
        value = _preflight()
        value["historical_executor_workflow_installed"] = False
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_workflow_installed",
        ):
            review_active_one_shot_historical_executor_dispatch_preflight_proof(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                preflight_bytes=_bytes(value),
                expected_head_sha=HEAD,
                repository_root=Path("."),
            )


if __name__ == "__main__":
    unittest.main()
