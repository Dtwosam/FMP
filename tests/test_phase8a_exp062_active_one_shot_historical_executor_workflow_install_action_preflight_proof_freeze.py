from __future__ import annotations

import hashlib
import json
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_install_action_preflight_proof_freeze import (
    freeze_reviewed_active_one_shot_historical_executor_workflow_install_action_preflight_proof,
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
        "decision": "DEC-420",
        "version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-action-preflight-proof-review-v1",
        "stage": "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_ACTION_PREFLIGHT_PROOF_REVIEWED_ACTIVE_WORKFLOW_ABSENT",
        "proof_workflow_name": "phase8a-exp062-active-one-shot-historical-executor-workflow-install-action-preflight-proof",
        "proof_workflow_path": ".github/workflows/phase8a-exp062-active-one-shot-historical-executor-workflow-install-action-preflight-proof.yml",
        "proof_run_id": 1,
        "proof_head_sha": HEAD,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "proof_job_id": 2,
        "proof_artifact_id": 3,
        "proof_artifact_name": "exp062-dec419-active-one-shot-historical-executor-workflow-install-action-preflight-" + HEAD,
        "proof_artifact_digest": "sha256:" + "1" * 64,
        "preflight_raw_sha256": "2" * 64,
        "preflight_canonical_sha256": "3" * 64,
        "action_preflight_decision": "DEC-418",
        "final_authorization_preflight_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-action-preflight-v1",
        "install_action_contract_decision": "DEC-417",
        "final_authorization_contract_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-action-contract-v1",
        "dormant_executor_workflow_template_blob_sha": "51ce87584369be957482460d81649adb1cb9f05d",
        "expected_executor_workflow_path": ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml",
        "executor_workflow_path_exists": False,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
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
        "active_one_shot_historical_executor_workflow_install_action_contract_source_authorized": True,
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
        "review_source_blobs": {
            "dec419_workflow": "6d22ffb3d93e7860033887987aff56f8870741c2",
            "dec418_preflight": "2d499f52b423bce5771c932e75a8196e0428304d",
            "dec418_preflight_cli": "9bd7815b58b9f057cf560f2c1d8874ee46bbd44a",
            "dec417_install_action_contract": "7d65e3b4359726d6cd920f31ceab84fdba88e922",
            "dormant_executor_workflow_template": "51ce87584369be957482460d81649adb1cb9f05d",
            "active_discovery_workflow": "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50",
        },
        "next_gate": "IMMUTABLE_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_ACTION_PREFLIGHT_PROOF_FREEZE_BEFORE_INSTALL",
    }


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallActionPreflightProofFreezeTests(
    unittest.TestCase
):
    def test_freeze_is_deterministic_and_preserves_locks(self) -> None:
        first = freeze_reviewed_active_one_shot_historical_executor_workflow_install_action_preflight_proof(
            _reviewed(),
            expected_head_sha=HEAD,
        )
        second = freeze_reviewed_active_one_shot_historical_executor_workflow_install_action_preflight_proof(
            _reviewed(),
            expected_head_sha=HEAD,
        )
        self.assertEqual(first, second)
        self.assertEqual(first["decision"], "DEC-421")
        self.assertEqual(first["source_review_decision"], "DEC-420")
        self.assertEqual(first["proof_run_number"], 1)
        self.assertFalse(first["historical_executor_workflow_install_authorized"])
        self.assertFalse(first["historical_result_dispatch_authorized"])
        self.assertFalse(first["trading_authorized"])
        self.assertEqual(
            first["next_gate"],
            (
                "CONCRETE_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "FINAL_AUTHORIZATION_PREFLIGHT_PROOF_RUNTIME_EVIDENCE_BINDING_BEFORE_INSTALL"
            ),
        )
        unsigned = dict(first)
        fingerprint = unsigned.pop("freeze_fingerprint_sha256")
        self.assertEqual(
            fingerprint,
            hashlib.sha256(_canonical_json(unsigned)).hexdigest(),
        )

    def test_authority_escalation_is_rejected(self) -> None:
        value = _reviewed()
        value["historical_executor_workflow_install_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_workflow_install_authorized",
        ):
            freeze_reviewed_active_one_shot_historical_executor_workflow_install_action_preflight_proof(
                value,
                expected_head_sha=HEAD,
            )

    def test_source_map_drift_is_rejected(self) -> None:
        value = _reviewed()
        value["review_source_blobs"] = dict(value["review_source_blobs"])
        value["review_source_blobs"]["dec419_workflow"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "review_source_blobs mismatch"):
            freeze_reviewed_active_one_shot_historical_executor_workflow_install_action_preflight_proof(
                value,
                expected_head_sha=HEAD,
            )

    def test_head_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "proof_head_sha mismatch"):
            freeze_reviewed_active_one_shot_historical_executor_workflow_install_action_preflight_proof(
                _reviewed(),
                expected_head_sha="b" * 40,
            )


if __name__ == "__main__":
    unittest.main()
