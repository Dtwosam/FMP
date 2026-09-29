from __future__ import annotations

import hashlib
import json
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_install_source_preflight_proof_freeze import (
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_FREEZE_DECISION,
    freeze_reviewed_active_one_shot_historical_executor_workflow_install_source_preflight_proof,
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
        "decision": "DEC-405",
        "version": (
            "fmp-exp062-active-one-shot-historical-executor-workflow-install-"
            "source-preflight-proof-review-v1"
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "SOURCE_PREFLIGHT_PROOF_REVIEWED_ACTIVE_WORKFLOW_ABSENT"
        ),
        "proof_workflow_name": (
            "phase8a-exp062-active-one-shot-historical-executor-"
            "workflow-install-source-preflight-proof"
        ),
        "proof_workflow_path": (
            ".github/workflows/"
            "phase8a-exp062-active-one-shot-historical-executor-"
            "workflow-install-source-preflight-proof.yml"
        ),
        "proof_run_id": 40000000001,
        "proof_head_sha": HEAD,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "proof_job_id": 50000000001,
        "proof_artifact_id": 60000000001,
        "proof_artifact_name": (
            "exp062-dec404-active-one-shot-historical-executor-workflow-"
            "install-source-preflight-" + HEAD
        ),
        "proof_artifact_digest": "sha256:" + ("1" * 64),
        "preflight_raw_sha256": "2" * 64,
        "preflight_canonical_sha256": "3" * 64,
        "install_source_preflight_decision": "DEC-403",
        "install_source_preflight_version": (
            "fmp-exp062-active-one-shot-historical-executor-workflow-install-"
            "source-preflight-v1"
        ),
        "install_source_contract_decision": "DEC-402",
        "install_source_contract_version": (
            "fmp-exp062-active-one-shot-historical-executor-workflow-install-"
            "source-contract-v1"
        ),
        "dormant_executor_workflow_template_blob_sha": (
            "51ce87584369be957482460d81649adb1cb9f05d"
        ),
        "expected_executor_workflow_path": (
            ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
        ),
        "executor_workflow_path_exists": False,
        "install_activation_slot_verified_available": True,
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
            "dec404_workflow": (
                "819725442ea3b559c8b852e60b2e1929990afa47"
            ),
            "dec403_preflight": (
                "cb8ca1ca5b65e9703844d3df9b0a622e2e3ed1bc"
            ),
            "dec403_preflight_cli": (
                "1c9615b7ee55ff1387cd95464abf2202f8dd9d3f"
            ),
            "dec402_install_source_contract": (
                "a09eca21a8b5e7b88182040ada5d9298eb922282"
            ),
            "dormant_executor_workflow_template": (
                "51ce87584369be957482460d81649adb1cb9f05d"
            ),
            "active_discovery_workflow": (
                "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
            ),
        },
        "next_gate": (
            "IMMUTABLE_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "SOURCE_PREFLIGHT_PROOF_FREEZE_BEFORE_INSTALL"
        ),
    }


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallSourcePreflightProofFreezeTests(
    unittest.TestCase
):
    def test_reviewed_proof_freezes_deterministically(self) -> None:
        first = (
            freeze_reviewed_active_one_shot_historical_executor_workflow_install_source_preflight_proof(
                _reviewed(),
                expected_head_sha=HEAD,
            )
        )
        second = (
            freeze_reviewed_active_one_shot_historical_executor_workflow_install_source_preflight_proof(
                _reviewed(),
                expected_head_sha=HEAD,
            )
        )
        self.assertEqual(first, second)
        self.assertEqual(
            first["decision"],
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_FREEZE_DECISION,
        )
        self.assertEqual(
            first["stage"],
            (
                "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "SOURCE_PREFLIGHT_PROOF_REVIEWED_AND_FROZEN"
            ),
        )
        self.assertFalse(first["executor_workflow_path_exists"])
        self.assertFalse(
            first["historical_executor_workflow_install_authorized"]
        )
        self.assertFalse(first["historical_executor_workflow_installed"])
        self.assertFalse(first["historical_executor_available"])
        self.assertFalse(first["historical_result_dispatch_authorized"])
        self.assertFalse(first["historical_execute_mode_available"])
        self.assertTrue(
            first[
                "active_one_shot_historical_executor_workflow_"
                "install_activation_source_authorized"
            ]
        )

        unsigned = dict(first)
        fingerprint = unsigned.pop("freeze_fingerprint_sha256")
        self.assertEqual(
            fingerprint,
            hashlib.sha256(_canonical_json(unsigned)).hexdigest(),
        )

    def test_head_drift_is_rejected(self) -> None:
        reviewed = _reviewed()
        reviewed["proof_head_sha"] = "b" * 40
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result proof_head_sha mismatch",
        ):
            freeze_reviewed_active_one_shot_historical_executor_workflow_install_source_preflight_proof(
                reviewed,
                expected_head_sha=HEAD,
            )

    def test_install_authority_escalation_is_rejected(self) -> None:
        reviewed = _reviewed()
        reviewed["historical_executor_workflow_install_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_workflow_install_authorized",
        ):
            freeze_reviewed_active_one_shot_historical_executor_workflow_install_source_preflight_proof(
                reviewed,
                expected_head_sha=HEAD,
            )

    def test_installed_state_escalation_is_rejected(self) -> None:
        reviewed = _reviewed()
        reviewed["historical_executor_workflow_installed"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_workflow_installed",
        ):
            freeze_reviewed_active_one_shot_historical_executor_workflow_install_source_preflight_proof(
                reviewed,
                expected_head_sha=HEAD,
            )

    def test_invalid_runtime_identity_is_rejected(self) -> None:
        reviewed = _reviewed()
        reviewed["proof_job_id"] = 0
        with self.assertRaisesRegex(
            ValueError,
            "proof_job_id must be a positive integer",
        ):
            freeze_reviewed_active_one_shot_historical_executor_workflow_install_source_preflight_proof(
                reviewed,
                expected_head_sha=HEAD,
            )

    def test_source_blob_drift_is_rejected(self) -> None:
        reviewed = _reviewed()
        blobs = reviewed["review_source_blobs"]
        assert isinstance(blobs, dict)
        blobs["dec403_preflight"] = "f" * 40
        with self.assertRaisesRegex(
            ValueError,
            "review_source_blobs mismatch",
        ):
            freeze_reviewed_active_one_shot_historical_executor_workflow_install_source_preflight_proof(
                reviewed,
                expected_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
