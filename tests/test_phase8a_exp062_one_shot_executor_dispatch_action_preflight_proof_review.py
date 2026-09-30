from __future__ import annotations

import json
import os
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_one_shot_executor_dispatch_action_preflight_proof_review import (
    review_one_shot_executor_dispatch_action_preflight_proof,
    validate_one_shot_executor_dispatch_action_preflight_proof_review_sources,
)


HEAD = "a" * 40


def _preflight() -> dict[str, object]:
    return {
        "decision": "DEC-431",
        "version": "fmp-exp062-active-one-shot-historical-executor-dispatch-action-preflight-v1",
        "authorization_decision": "DEC-430",
        "authorization_version": "fmp-exp062-active-one-shot-historical-executor-dispatch-authorization-v1",
        "dec430_dispatch_authorization_blob_sha": "87aada4c5224c633e8eb419f971c8f7f0699b18f",
        "active_executor_workflow_blob_sha": "51ce87584369be957482460d81649adb1cb9f05d",
        "expected_head_sha": HEAD,
        "stage": "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_AUTHORIZED_SLOT_AVAILABLE",
        "active_executor_workflow_path": ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml",
        "active_executor_workflow_present": True,
        "executor_workflow_run_count": 0,
        "expected_executor_run_number": 1,
        "expected_executor_run_attempt": 1,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_executor_dispatch_command": "gh workflow run phase8a-exp062-one-shot-historical-executor.yml --ref main",
        "explicit_one_shot_executor_dispatch_authorized": True,
        "historical_executor_workflow_installed": True,
        "historical_executor_available": True,
        "historical_result_dispatch_authorized": True,
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
        "next_gate": "REPOSITORY_HOSTED_READ_ONLY_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_PROOF",
    }


def _bytes(value: dict[str, object] | None = None) -> bytes:
    payload = _preflight() if value is None else value
    return (
        json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def _run() -> dict[str, object]:
    return {
        "id": 1,
        "name": "phase8a-exp062-one-shot-executor-dispatch-action-preflight-proof",
        "path": ".github/workflows/phase8a-exp062-one-shot-executor-dispatch-action-preflight-proof.yml",
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
            "name": "read-only-one-shot-executor-dispatch-action-preflight",
            "status": "completed",
            "conclusion": "success",
        }]
    }


def _artifacts() -> dict[str, object]:
    return {
        "artifacts": [{
            "id": 3,
            "name": (
                "exp062-dec432-one-shot-executor-dispatch-action-preflight-"
                + HEAD
            ),
            "digest": "sha256:" + "1" * 64,
            "expired": False,
        }]
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-433 source review requires the installed executor workflow",
)
class Exp062OneShotExecutorDispatchActionPreflightProofReviewTests(
    unittest.TestCase
):
    def test_source_bindings_pin_dec432_431_430(self) -> None:
        source = validate_one_shot_executor_dispatch_action_preflight_proof_review_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["dec432_workflow"],
            "29dc3eb49c5c682cb74cd80ed104d3c584859314",
        )
        self.assertEqual(
            source["dec431_preflight"],
            "93ab88965e74df0b067ba09dbbb8d0622c53e578",
        )
        self.assertEqual(
            source["dec430_authorization"],
            "87aada4c5224c633e8eb419f971c8f7f0699b18f",
        )

    def test_valid_proof_reviews_authorized_unstarted_run(self) -> None:
        value = review_one_shot_executor_dispatch_action_preflight_proof(
            run=_run(),
            jobs_payload=_jobs(),
            artifacts_payload=_artifacts(),
            preflight_bytes=_bytes(),
            expected_head_sha=HEAD,
            repository_root=Path("."),
        )
        self.assertEqual(value["decision"], "DEC-433")
        self.assertTrue(value["explicit_one_shot_executor_dispatch_authorized"])
        self.assertTrue(value["historical_result_dispatch_authorized"])
        self.assertEqual(value["executor_workflow_run_count"], 0)
        self.assertEqual(value["historical_result_attempt_count"], 0)
        self.assertFalse(value["historical_execute_mode_available"])
        self.assertFalse(value["rerun_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_existing_run_count_is_rejected(self) -> None:
        value = _preflight()
        value["executor_workflow_run_count"] = 1
        with self.assertRaisesRegex(ValueError, "executor_workflow_run_count"):
            review_one_shot_executor_dispatch_action_preflight_proof(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                preflight_bytes=_bytes(value),
                expected_head_sha=HEAD,
                repository_root=Path("."),
            )

    def test_authorization_drift_is_rejected(self) -> None:
        value = _preflight()
        value["explicit_one_shot_executor_dispatch_authorized"] = False
        with self.assertRaisesRegex(
            ValueError,
            "explicit_one_shot_executor_dispatch_authorized",
        ):
            review_one_shot_executor_dispatch_action_preflight_proof(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                preflight_bytes=_bytes(value),
                expected_head_sha=HEAD,
                repository_root=Path("."),
            )

    def test_trading_escalation_is_rejected(self) -> None:
        value = _preflight()
        value["trading_authorized"] = True
        with self.assertRaisesRegex(ValueError, "trading_authorized"):
            review_one_shot_executor_dispatch_action_preflight_proof(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                preflight_bytes=_bytes(value),
                expected_head_sha=HEAD,
                repository_root=Path("."),
            )


if __name__ == "__main__":
    unittest.main()
