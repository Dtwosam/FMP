from __future__ import annotations

import hashlib
import json
import unittest

from fmp.discovery.exp062_historical_dormant_one_shot_executor_source_proof_freeze import (
    EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_DECISION,
    freeze_reviewed_dormant_one_shot_historical_executor_source_proof,
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
        "decision": "DEC-357",
        "version": (
            "fmp-exp062-dormant-one-shot-historical-executor-"
            "source-proof-review-v1"
        ),
        "stage": (
            "EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
            "REVIEWED_ACTIVE_WORKFLOW_UNINSTALLED"
        ),
        "proof_workflow_name": (
            "phase8a-exp062-dormant-one-shot-historical-executor-"
            "workflow-source-proof"
        ),
        "proof_workflow_path": (
            ".github/workflows/"
            "phase8a-exp062-dormant-one-shot-historical-executor-"
            "workflow-source-proof.yml"
        ),
        "proof_run_id": 40000000001,
        "proof_head_sha": HEAD,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "proof_job_id": 50000000001,
        "proof_artifact_id": 60000000001,
        "proof_artifact_name": (
            "exp062-dec356-dormant-one-shot-historical-executor-source-"
            + HEAD
        ),
        "proof_artifact_digest": "sha256:" + ("1" * 64),
        "source_raw_sha256": "2" * 64,
        "source_canonical_sha256": "3" * 64,
        "dormant_source_decision": "DEC-355",
        "dormant_source_version": (
            "fmp-exp062-one-shot-historical-executor-dormant-workflow-source-v1"
        ),
        "dormant_executor_workflow_template_blob_sha": (
            "51ce87584369be957482460d81649adb1cb9f05d"
        ),
        "expected_executor_workflow_path": (
            ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
        ),
        "dormant_executor_workflow_template_present": True,
        "dormant_template_dispatch_capable_if_installed": True,
        "dormant_template_actions_write_required_if_installed": True,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
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
            "dec356_workflow": (
                "1cf665417e32c6810bf8ff62e5bc4a3b7a1ac598"
            ),
            "dec355_source": (
                "0672310946ab6bb3b77d2de5c4ea5d68e41f810a"
            ),
            "dec354_installation_source_contract": (
                "e4fc6a7d1faaca50bc6936597f0e8b66fe096985"
            ),
            "dormant_executor_workflow_template": (
                "51ce87584369be957482460d81649adb1cb9f05d"
            ),
            "active_discovery_workflow": (
                "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
            ),
        },
        "next_gate": (
            "IMMUTABLE_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "SOURCE_PROOF_FREEZE_BEFORE_INSTALL"
        ),
    }


class Exp062DormantOneShotHistoricalExecutorSourceProofFreezeTests(
    unittest.TestCase
):
    def test_reviewed_source_proof_freezes_deterministically(self) -> None:
        first = freeze_reviewed_dormant_one_shot_historical_executor_source_proof(
            _reviewed(),
            expected_head_sha=HEAD,
        )
        second = freeze_reviewed_dormant_one_shot_historical_executor_source_proof(
            _reviewed(),
            expected_head_sha=HEAD,
        )
        self.assertEqual(first, second)
        self.assertEqual(
            first["decision"],
            EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_DECISION,
        )
        self.assertTrue(first["dormant_executor_workflow_template_present"])
        self.assertTrue(
            first["dormant_template_dispatch_capable_if_installed"]
        )
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
            freeze_reviewed_dormant_one_shot_historical_executor_source_proof(
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
            freeze_reviewed_dormant_one_shot_historical_executor_source_proof(
                reviewed,
                expected_head_sha=HEAD,
            )

    def test_dispatch_authority_escalation_is_rejected(self) -> None:
        reviewed = _reviewed()
        reviewed["historical_result_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_dispatch_authorized",
        ):
            freeze_reviewed_dormant_one_shot_historical_executor_source_proof(
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
            freeze_reviewed_dormant_one_shot_historical_executor_source_proof(
                reviewed,
                expected_head_sha=HEAD,
            )

    def test_source_blob_drift_is_rejected(self) -> None:
        reviewed = _reviewed()
        blobs = reviewed["review_source_blobs"]
        assert isinstance(blobs, dict)
        blobs["dec355_source"] = "f" * 40
        with self.assertRaisesRegex(
            ValueError,
            "review_source_blobs mismatch",
        ):
            freeze_reviewed_dormant_one_shot_historical_executor_source_proof(
                reviewed,
                expected_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
