from __future__ import annotations

import hashlib
import json
import unittest

from fmp.discovery.exp062_historical_one_shot_executor_workflow_install_preflight_proof_freeze import (
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_FREEZE_DECISION,
    freeze_reviewed_one_shot_historical_executor_workflow_install_preflight_proof,
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
        "decision": "DEC-351",
        "version": (
            "fmp-exp062-one-shot-historical-executor-workflow-install-"
            "preflight-proof-review-v1"
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_"
            "PROOF_REVIEWED_SOURCE_ABSENT_SLOT_AVAILABLE"
        ),
        "proof_workflow_name": (
            "phase8a-exp062-one-shot-historical-executor-"
            "workflow-install-preflight-proof"
        ),
        "proof_workflow_path": (
            ".github/workflows/"
            "phase8a-exp062-one-shot-historical-executor-"
            "workflow-install-preflight-proof.yml"
        ),
        "proof_run_id": 40000000001,
        "proof_head_sha": HEAD,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "proof_job_id": 50000000001,
        "proof_artifact_id": 60000000001,
        "proof_artifact_name": (
            "exp062-dec350-one-shot-historical-executor-"
            "workflow-install-preflight-" + HEAD
        ),
        "proof_artifact_digest": "sha256:" + ("1" * 64),
        "preflight_raw_sha256": "2" * 64,
        "preflight_canonical_sha256": "3" * 64,
        "workflow_install_preflight_decision": "DEC-349",
        "workflow_install_preflight_version": (
            "fmp-exp062-one-shot-historical-executor-workflow-install-preflight-v1"
        ),
        "install_contract_decision": "DEC-348",
        "install_contract_version": (
            "fmp-exp062-one-shot-historical-executor-workflow-install-contract-v1"
        ),
        "expected_executor_workflow_path": (
            ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
        ),
        "executor_workflow_path_exists": False,
        "workflow_install_slot_verified_available": True,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
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
        "review_source_blobs": {
            "dec350_workflow": (
                "e35c61e91475078f2c40d971c683b899e298c6c3"
            ),
            "dec349_preflight": (
                "e91b032a4e5e43e5fae5e4f6cc677501cabc8381"
            ),
            "dec349_preflight_cli": (
                "431cc88658dddfb29c698f026851e78d4574f8a2"
            ),
            "dec348_install_contract": (
                "111a56fdbb8844c119307465e7b7cf6a4d43d95a"
            ),
            "active_discovery_workflow": (
                "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
            ),
        },
        "next_gate": (
            "IMMUTABLE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "PREFLIGHT_PROOF_FREEZE_BEFORE_WORKFLOW_INSTALL"
        ),
    }


class Exp062OneShotHistoricalExecutorWorkflowInstallPreflightProofFreezeTests(
    unittest.TestCase
):
    def test_reviewed_install_preflight_proof_freezes_deterministically(
        self,
    ) -> None:
        first = (
            freeze_reviewed_one_shot_historical_executor_workflow_install_preflight_proof(
                _reviewed(),
                expected_head_sha=HEAD,
            )
        )
        second = (
            freeze_reviewed_one_shot_historical_executor_workflow_install_preflight_proof(
                _reviewed(),
                expected_head_sha=HEAD,
            )
        )
        self.assertEqual(first, second)
        self.assertEqual(
            first["decision"],
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_FREEZE_DECISION,
        )
        self.assertFalse(first["executor_workflow_path_exists"])
        self.assertTrue(first["workflow_install_slot_verified_available"])
        self.assertFalse(
            first["historical_executor_workflow_install_authorized"]
        )
        self.assertFalse(first["historical_executor_workflow_installed"])
        self.assertFalse(first["historical_executor_available"])
        self.assertFalse(first["historical_result_dispatch_authorized"])
        self.assertFalse(first["historical_execute_mode_available"])

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
            freeze_reviewed_one_shot_historical_executor_workflow_install_preflight_proof(
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
            freeze_reviewed_one_shot_historical_executor_workflow_install_preflight_proof(
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
            freeze_reviewed_one_shot_historical_executor_workflow_install_preflight_proof(
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
            freeze_reviewed_one_shot_historical_executor_workflow_install_preflight_proof(
                reviewed,
                expected_head_sha=HEAD,
            )

    def test_source_blob_drift_is_rejected(self) -> None:
        reviewed = _reviewed()
        blobs = reviewed["review_source_blobs"]
        assert isinstance(blobs, dict)
        blobs["dec349_preflight"] = "f" * 40
        with self.assertRaisesRegex(
            ValueError,
            "review_source_blobs mismatch",
        ):
            freeze_reviewed_one_shot_historical_executor_workflow_install_preflight_proof(
                reviewed,
                expected_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
