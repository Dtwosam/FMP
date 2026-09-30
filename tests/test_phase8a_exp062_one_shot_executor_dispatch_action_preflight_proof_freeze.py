from __future__ import annotations

import hashlib
import json
import unittest

from fmp.discovery.exp062_historical_one_shot_executor_dispatch_action_preflight_proof_freeze import (
    freeze_reviewed_one_shot_executor_dispatch_action_preflight_proof,
)


HEAD = "a" * 40


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


def _reviewed() -> dict[str, object]:
    return {
        "decision": "DEC-433",
        "version": "fmp-exp062-one-shot-executor-dispatch-action-preflight-proof-review-v1",
        "stage": "EXP062_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_PROOF_REVIEWED_AUTHORIZED_RUN_NOT_STARTED",
        "proof_workflow_name": "phase8a-exp062-one-shot-executor-dispatch-action-preflight-proof",
        "proof_workflow_path": ".github/workflows/phase8a-exp062-one-shot-executor-dispatch-action-preflight-proof.yml",
        "proof_run_id": 1,
        "proof_head_sha": HEAD,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "proof_job_id": 2,
        "proof_artifact_id": 3,
        "proof_artifact_name": "exp062-dec432-one-shot-executor-dispatch-action-preflight-" + HEAD,
        "proof_artifact_digest": "sha256:" + "1" * 64,
        "preflight_raw_sha256": "2" * 64,
        "preflight_canonical_sha256": "3" * 64,
        "action_preflight_decision": "DEC-431",
        "action_preflight_version": "fmp-exp062-active-one-shot-historical-executor-dispatch-action-preflight-v1",
        "authorization_decision": "DEC-430",
        "authorization_version": "fmp-exp062-active-one-shot-historical-executor-dispatch-authorization-v1",
        "dec430_dispatch_authorization_blob_sha": "87aada4c5224c633e8eb419f971c8f7f0699b18f",
        "active_executor_workflow_blob_sha": "51ce87584369be957482460d81649adb1cb9f05d",
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
        "review_source_blobs": {
            "dec432_workflow": "29dc3eb49c5c682cb74cd80ed104d3c584859314",
            "dec431_preflight": "93ab88965e74df0b067ba09dbbb8d0622c53e578",
            "dec431_preflight_cli": "df486dd739952ab10b9ff31d6c35a01eab38618e",
            "dec430_authorization": "87aada4c5224c633e8eb419f971c8f7f0699b18f",
            "active_executor_workflow": "51ce87584369be957482460d81649adb1cb9f05d",
            "active_discovery_workflow": "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50",
        },
        "next_gate": "IMMUTABLE_ONE_SHOT_EXECUTOR_DISPATCH_ACTION_PREFLIGHT_PROOF_FREEZE_BEFORE_RUN",
    }


class Exp062OneShotExecutorDispatchActionPreflightProofFreezeTests(
    unittest.TestCase
):
    def test_freeze_is_deterministic_and_preserves_authorized_unstarted_state(self) -> None:
        first = freeze_reviewed_one_shot_executor_dispatch_action_preflight_proof(
            _reviewed(),
            expected_head_sha=HEAD,
        )
        second = freeze_reviewed_one_shot_executor_dispatch_action_preflight_proof(
            _reviewed(),
            expected_head_sha=HEAD,
        )
        self.assertEqual(first, second)
        self.assertEqual(first["decision"], "DEC-434")
        self.assertTrue(first["explicit_one_shot_executor_dispatch_authorized"])
        self.assertTrue(first["historical_result_dispatch_authorized"])
        self.assertEqual(first["executor_workflow_run_count"], 0)
        self.assertFalse(first["historical_execute_mode_available"])
        self.assertFalse(first["rerun_authorized"])
        self.assertFalse(first["trading_authorized"])
        unsigned = dict(first)
        fingerprint = unsigned.pop("freeze_fingerprint_sha256")
        self.assertEqual(
            fingerprint,
            hashlib.sha256(_canonical_json(unsigned)).hexdigest(),
        )

    def test_authorization_drift_is_rejected(self) -> None:
        value = _reviewed()
        value["explicit_one_shot_executor_dispatch_authorized"] = False
        with self.assertRaisesRegex(
            ValueError,
            "explicit_one_shot_executor_dispatch_authorized",
        ):
            freeze_reviewed_one_shot_executor_dispatch_action_preflight_proof(
                value,
                expected_head_sha=HEAD,
            )

    def test_run_count_drift_is_rejected(self) -> None:
        value = _reviewed()
        value["executor_workflow_run_count"] = 1
        with self.assertRaisesRegex(ValueError, "executor_workflow_run_count"):
            freeze_reviewed_one_shot_executor_dispatch_action_preflight_proof(
                value,
                expected_head_sha=HEAD,
            )

    def test_source_map_drift_is_rejected(self) -> None:
        value = _reviewed()
        value["review_source_blobs"] = dict(value["review_source_blobs"])
        value["review_source_blobs"]["dec432_workflow"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "review_source_blobs mismatch"):
            freeze_reviewed_one_shot_executor_dispatch_action_preflight_proof(
                value,
                expected_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
