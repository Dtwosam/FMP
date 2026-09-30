from __future__ import annotations

import hashlib
import json
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_dispatch_preflight_proof_freeze import (
    freeze_reviewed_active_one_shot_historical_executor_dispatch_preflight_proof,
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
        "decision": "DEC-427",
        "version": "fmp-exp062-active-one-shot-historical-executor-dispatch-preflight-proof-review-v1",
        "stage": "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_REVIEWED_RUNTIME_LOCKED",
        "proof_workflow_name": "phase8a-exp062-active-one-shot-historical-executor-dispatch-preflight-proof",
        "proof_workflow_path": ".github/workflows/phase8a-exp062-active-one-shot-historical-executor-dispatch-preflight-proof.yml",
        "proof_run_id": 1,
        "proof_head_sha": HEAD,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "proof_job_id": 2,
        "proof_artifact_id": 3,
        "proof_artifact_name": "exp062-dec426-active-one-shot-historical-executor-dispatch-preflight-" + HEAD,
        "proof_artifact_digest": "sha256:" + "1" * 64,
        "preflight_raw_sha256": "2" * 64,
        "preflight_canonical_sha256": "3" * 64,
        "dispatch_preflight_decision": "DEC-425",
        "dispatch_preflight_version": "fmp-exp062-active-one-shot-historical-executor-dispatch-preflight-v1",
        "install_receipt_decision": "DEC-424",
        "install_receipt_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-receipt-v1",
        "dec424_install_receipt_blob_sha": "27e714620018413a09ceaf287fb7943bf884ee49",
        "active_executor_workflow_blob_sha": "51ce87584369be957482460d81649adb1cb9f05d",
        "active_executor_workflow_path": ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml",
        "active_executor_workflow_present": True,
        "historical_executor_workflow_install_authorized": True,
        "historical_executor_workflow_installed": True,
        "historical_executor_available": True,
        "executor_workflow_run_count": 0,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
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
        "review_source_blobs": {
            "dec426_workflow": "0bb9cd78639ebad68eb7db0fb9d083ce86b75319",
            "dec425_preflight": "1978f71bb11097613d3820127f7a04ce2bf81adb",
            "dec425_preflight_cli": "ef0f6df22d9208b6de8037585d706a1bb1e9eda4",
            "dec424_install_receipt": "27e714620018413a09ceaf287fb7943bf884ee49",
            "active_executor_workflow": "51ce87584369be957482460d81649adb1cb9f05d",
            "active_discovery_workflow": "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50",
        },
        "next_gate": "IMMUTABLE_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_DISPATCH_PREFLIGHT_PROOF_FREEZE_BEFORE_AUTHORIZATION",
    }


class Exp062ActiveOneShotHistoricalExecutorDispatchPreflightProofFreezeTests(
    unittest.TestCase
):
    def test_freeze_is_deterministic_and_preserves_installed_state(self) -> None:
        first = freeze_reviewed_active_one_shot_historical_executor_dispatch_preflight_proof(
            _reviewed(),
            expected_head_sha=HEAD,
        )
        second = freeze_reviewed_active_one_shot_historical_executor_dispatch_preflight_proof(
            _reviewed(),
            expected_head_sha=HEAD,
        )
        self.assertEqual(first, second)
        self.assertEqual(first["decision"], "DEC-428")
        self.assertEqual(first["source_review_decision"], "DEC-427")
        self.assertTrue(first["historical_executor_workflow_installed"])
        self.assertTrue(first["historical_executor_available"])
        self.assertEqual(first["executor_workflow_run_count"], 0)
        self.assertFalse(first["historical_result_dispatch_authorized"])
        self.assertFalse(first["historical_execute_mode_available"])
        self.assertFalse(first["trading_authorized"])
        unsigned = dict(first)
        fingerprint = unsigned.pop("freeze_fingerprint_sha256")
        self.assertEqual(
            fingerprint,
            hashlib.sha256(_canonical_json(unsigned)).hexdigest(),
        )

    def test_dispatch_authority_escalation_is_rejected(self) -> None:
        value = _reviewed()
        value["historical_result_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_dispatch_authorized",
        ):
            freeze_reviewed_active_one_shot_historical_executor_dispatch_preflight_proof(
                value,
                expected_head_sha=HEAD,
            )

    def test_source_map_drift_is_rejected(self) -> None:
        value = _reviewed()
        value["review_source_blobs"] = dict(value["review_source_blobs"])
        value["review_source_blobs"]["dec426_workflow"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "review_source_blobs mismatch"):
            freeze_reviewed_active_one_shot_historical_executor_dispatch_preflight_proof(
                value,
                expected_head_sha=HEAD,
            )

    def test_head_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "proof_head_sha mismatch"):
            freeze_reviewed_active_one_shot_historical_executor_dispatch_preflight_proof(
                _reviewed(),
                expected_head_sha="b" * 40,
            )


if __name__ == "__main__":
    unittest.main()
