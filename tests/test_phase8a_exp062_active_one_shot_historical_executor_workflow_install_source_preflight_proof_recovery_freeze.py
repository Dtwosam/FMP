from __future__ import annotations

import hashlib
import json
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_install_source_preflight_proof_recovery_freeze import (
    EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_RECOVERY_FREEZE_DECISION,
    freeze_reviewed_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery,
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
        "decision": "DEC-408",
        "version": (
            "fmp-exp062-active-one-shot-historical-executor-workflow-install-"
            "source-preflight-proof-recovery-review-v1"
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "SOURCE_PREFLIGHT_RECOVERY_PROOF_REVIEWED_ACTIVE_WORKFLOW_ABSENT"
        ),
        "proof_recovery_decision": "DEC-407",
        "failed_proof_run_id": 36613664506,
        "failed_proof_head_sha": (
            "0db04ae49b3533778b08afa31e9ef9a26576b80c"
        ),
        "failed_proof_job_id": 109561121322,
        "failed_proof_run_number": 1,
        "failed_proof_run_attempt": 1,
        "failed_proof_run_conclusion": "failure",
        "proof_workflow_name": (
            "phase8a-exp062-active-one-shot-historical-executor-"
            "workflow-install-source-preflight-proof"
        ),
        "proof_workflow_path": (
            ".github/workflows/"
            "phase8a-exp062-active-one-shot-historical-executor-"
            "workflow-install-source-preflight-proof.yml"
        ),
        "proof_run_id": 40000000002,
        "proof_head_sha": HEAD,
        "proof_run_number": 2,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "proof_job_id": 50000000002,
        "proof_artifact_id": 60000000002,
        "proof_artifact_name": (
            "exp062-dec407-active-one-shot-historical-executor-workflow-"
            "install-source-preflight-recovery-" + HEAD
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
            "dec407_recovery_workflow": (
                "2adfc7bd1ccacd158a78532d31ff38f4f175229f"
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
            "SOURCE_PREFLIGHT_RECOVERY_PROOF_FREEZE_BEFORE_INSTALL"
        ),
    }


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallSourcePreflightProofRecoveryFreezeTests(
    unittest.TestCase
):
    def test_reviewed_recovery_freezes_deterministically(self) -> None:
        first = (
            freeze_reviewed_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery(
                _reviewed(),
                expected_head_sha=HEAD,
            )
        )
        second = (
            freeze_reviewed_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery(
                _reviewed(),
                expected_head_sha=HEAD,
            )
        )
        self.assertEqual(first, second)
        self.assertEqual(
            first["decision"],
            EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_RECOVERY_FREEZE_DECISION,
        )
        self.assertEqual(first["proof_run_number"], 2)
        self.assertEqual(first["failed_proof_run_number"], 1)
        self.assertEqual(first["failed_proof_run_conclusion"], "failure")
        self.assertFalse(first["executor_workflow_path_exists"])
        self.assertFalse(first["historical_executor_workflow_install_authorized"])
        self.assertFalse(first["historical_result_dispatch_authorized"])
        self.assertFalse(first["trading_authorized"])

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
            freeze_reviewed_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery(
                reviewed,
                expected_head_sha=HEAD,
            )

    def test_run_one_cannot_be_frozen_as_recovery(self) -> None:
        reviewed = _reviewed()
        reviewed["proof_run_number"] = 1
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result proof_run_number mismatch",
        ):
            freeze_reviewed_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery(
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
            freeze_reviewed_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery(
                reviewed,
                expected_head_sha=HEAD,
            )

    def test_source_blob_drift_is_rejected(self) -> None:
        reviewed = _reviewed()
        blobs = reviewed["review_source_blobs"]
        assert isinstance(blobs, dict)
        blobs["dec407_recovery_workflow"] = "f" * 40
        with self.assertRaisesRegex(
            ValueError,
            "review_source_blobs mismatch",
        ):
            freeze_reviewed_active_one_shot_historical_executor_workflow_install_source_preflight_proof_recovery(
                reviewed,
                expected_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
