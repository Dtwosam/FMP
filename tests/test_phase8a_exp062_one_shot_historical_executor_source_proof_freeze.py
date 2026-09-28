from __future__ import annotations

import hashlib
import json
import unittest

from fmp.discovery.exp062_historical_one_shot_executor_source_proof_freeze import (
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_DECISION,
    freeze_reviewed_one_shot_historical_executor_source_proof,
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
        "decision": "DEC-339",
        "version": (
            "fmp-exp062-one-shot-historical-executor-source-proof-review-v1"
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
            "REVIEWED_SLOT_AVAILABLE"
        ),
        "proof_workflow_name": (
            "phase8a-exp062-one-shot-historical-executor-source-proof"
        ),
        "proof_workflow_path": (
            ".github/workflows/"
            "phase8a-exp062-one-shot-historical-executor-source-proof.yml"
        ),
        "proof_run_id": 40000000001,
        "proof_head_sha": HEAD,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "proof_job_id": 50000000001,
        "proof_artifact_id": 60000000001,
        "proof_artifact_name": (
            "exp062-dec338-one-shot-historical-executor-source-" + HEAD
        ),
        "proof_artifact_digest": "sha256:" + ("1" * 64),
        "contract_raw_sha256": "2" * 64,
        "contract_canonical_sha256": "3" * 64,
        "source_contract_decision": "DEC-337",
        "source_contract_version": (
            "fmp-exp062-one-shot-historical-executor-source-v1"
        ),
        "runtime_freeze_decision": "DEC-336",
        "runtime_freeze_fingerprint_sha256": (
            "147ab77116979afa8d0d07c3c748fb80e02865a382317824320f6af534bfc374"
        ),
        "terminal_review_decision": "DEC-334",
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "one_shot_historical_executor_source_authorized": True,
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
            "dec338_workflow": (
                "3104d6521e1c11f0c8be92eab0eef21c5e9eb80c"
            ),
            "dec337_source": (
                "26ee48241550d6e52501fc901ab88aaa3f42e755"
            ),
            "dec336_runtime_freeze": (
                "9673e115eeb373c4881d36a8b5d91a2801cd8ad1"
            ),
            "dec334_terminal_review": (
                "fda2a45f74b101303467cf7b8527bec1bfc5e168"
            ),
            "active_discovery_workflow": (
                "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
            ),
        },
        "next_gate": (
            "IMMUTABLE_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
            "FREEZE_BEFORE_EXECUTOR_WORKFLOW"
        ),
    }


class Exp062OneShotHistoricalExecutorSourceProofFreezeTests(
    unittest.TestCase
):
    def test_reviewed_source_proof_freezes_deterministically(self) -> None:
        first = freeze_reviewed_one_shot_historical_executor_source_proof(
            _reviewed(),
            expected_head_sha=HEAD,
        )
        second = freeze_reviewed_one_shot_historical_executor_source_proof(
            _reviewed(),
            expected_head_sha=HEAD,
        )
        self.assertEqual(first, second)
        self.assertEqual(
            first["decision"],
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_FREEZE_DECISION,
        )
        self.assertEqual(
            first["stage"],
            (
                "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
                "REVIEWED_AND_FROZEN"
            ),
        )
        self.assertTrue(first["historical_result_slot_verified_available"])
        self.assertFalse(first["historical_result_slot_consumed"])
        self.assertEqual(first["expected_target_run_number"], 2)
        self.assertEqual(first["expected_target_run_attempt"], 1)
        self.assertTrue(
            first["one_shot_historical_executor_source_authorized"]
        )
        self.assertFalse(first["historical_executor_available"])
        self.assertFalse(first["historical_result_dispatch_authorized"])
        self.assertFalse(first["historical_execute_mode_available"])
        self.assertFalse(first["demo_order_authorized"])
        self.assertFalse(first["live_order_authorized"])
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
            freeze_reviewed_one_shot_historical_executor_source_proof(
                reviewed,
                expected_head_sha=HEAD,
            )

    def test_executor_authority_escalation_is_rejected(self) -> None:
        reviewed = _reviewed()
        reviewed["historical_executor_available"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_available",
        ):
            freeze_reviewed_one_shot_historical_executor_source_proof(
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
            freeze_reviewed_one_shot_historical_executor_source_proof(
                reviewed,
                expected_head_sha=HEAD,
            )

    def test_malformed_artifact_digest_is_rejected(self) -> None:
        reviewed = _reviewed()
        reviewed["proof_artifact_digest"] = "sha256:not-a-digest"
        with self.assertRaisesRegex(
            ValueError,
            "proof_artifact_digest",
        ):
            freeze_reviewed_one_shot_historical_executor_source_proof(
                reviewed,
                expected_head_sha=HEAD,
            )

    def test_source_blob_drift_is_rejected(self) -> None:
        reviewed = _reviewed()
        blobs = reviewed["review_source_blobs"]
        assert isinstance(blobs, dict)
        blobs["dec337_source"] = "f" * 40
        with self.assertRaisesRegex(
            ValueError,
            "review_source_blobs mismatch",
        ):
            freeze_reviewed_one_shot_historical_executor_source_proof(
                reviewed,
                expected_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
