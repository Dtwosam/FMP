from __future__ import annotations

import hashlib
import json
import unittest

from fmp.discovery.exp062_historical_execution_plan_freeze import (
    EXP062_REVIEWED_HISTORICAL_EXECUTION_PLAN_FREEZE_DECISION,
    freeze_reviewed_historical_execution_plan,
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
        "decision": "DEC-315",
        "version": "fmp-exp062-historical-execution-plan-proof-review-v1",
        "stage": (
            "EXP062_HISTORICAL_EXECUTION_PLAN_PROOF_REVIEWED_SLOT_AVAILABLE"
        ),
        "proof_workflow_name": "phase8a-exp062-historical-execution-plan",
        "proof_workflow_path": (
            ".github/workflows/phase8a-exp062-historical-execution-plan.yml"
        ),
        "proof_run_id": 40000000001,
        "proof_head_sha": HEAD,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "proof_job_id": 50000000001,
        "proof_artifact_id": 60000000001,
        "proof_artifact_name": (
            "exp062-dec314-historical-execution-plan-" + HEAD
        ),
        "proof_artifact_digest": "sha256:" + ("1" * 64),
        "plan_raw_sha256": "2" * 64,
        "plan_canonical_sha256": "3" * 64,
        "plan_decision": "DEC-313",
        "plan_operator_version": (
            "fmp-exp062-historical-execution-operator-v1"
        ),
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "historical_execution_source_authorized": True,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "historical_result_dispatch_authorized": False,
        "historical_execute_mode_available": False,
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
            "plan_proof_workflow": (
                "d2b2e4fcc2a39e614dda98c890ec13b6387725e8"
            ),
            "execution_operator": (
                "7f21ccf59de9605c7fab45b4506f947ffae69cab"
            ),
            "execution_operator_cli": (
                "9ecb3f47d7e68461e4a7d893ad5862d7e78a1fc8"
            ),
            "execution_authorization": (
                "aa8cfb25e3d78c0c72da4b22898c1263a42548ba"
            ),
            "activated_cli": (
                "773784d0770d54b1d3e41fba2057b9314a090034"
            ),
            "active_discovery_workflow": (
                "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
            ),
            "historical_plan_freeze": (
                "e3274118b37066efe2869d554e78e6b68e64b32a"
            ),
        },
        "next_gate": (
            "IMMUTABLE_HISTORICAL_EXECUTION_PLAN_PROOF_FREEZE_BEFORE_DISPATCH_AUTHORIZATION"
        ),
    }


class Exp062HistoricalExecutionPlanFreezeTests(unittest.TestCase):
    def test_reviewed_plan_freezes_deterministically(self) -> None:
        first = freeze_reviewed_historical_execution_plan(
            _reviewed(),
            expected_head_sha=HEAD,
        )
        second = freeze_reviewed_historical_execution_plan(
            _reviewed(),
            expected_head_sha=HEAD,
        )
        self.assertEqual(first, second)
        self.assertEqual(
            first["decision"],
            EXP062_REVIEWED_HISTORICAL_EXECUTION_PLAN_FREEZE_DECISION,
        )
        self.assertEqual(
            first["stage"],
            "EXP062_HISTORICAL_EXECUTION_PLAN_REVIEWED_AND_FROZEN",
        )
        self.assertTrue(first["historical_result_slot_verified_available"])
        self.assertFalse(first["historical_result_slot_consumed"])
        self.assertEqual(first["expected_target_run_number"], 2)
        self.assertEqual(first["expected_target_run_attempt"], 1)
        self.assertTrue(first["historical_discovery_execution_authorized"])
        self.assertTrue(first["discovery_result_authorized"])
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
            freeze_reviewed_historical_execution_plan(
                reviewed,
                expected_head_sha=HEAD,
            )

    def test_dispatch_authority_escalation_is_rejected(self) -> None:
        reviewed = _reviewed()
        reviewed["historical_result_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_dispatch_authorized must remain false",
        ):
            freeze_reviewed_historical_execution_plan(
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
            freeze_reviewed_historical_execution_plan(
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
            freeze_reviewed_historical_execution_plan(
                reviewed,
                expected_head_sha=HEAD,
            )

    def test_plan_hash_drift_is_rejected(self) -> None:
        reviewed = _reviewed()
        reviewed["plan_raw_sha256"] = "not-a-hash"
        with self.assertRaisesRegex(
            ValueError,
            "plan_raw_sha256",
        ):
            freeze_reviewed_historical_execution_plan(
                reviewed,
                expected_head_sha=HEAD,
            )

    def test_review_source_blob_drift_is_rejected(self) -> None:
        reviewed = _reviewed()
        blobs = reviewed["review_source_blobs"]
        assert isinstance(blobs, dict)
        blobs["execution_operator"] = "f" * 40
        with self.assertRaisesRegex(
            ValueError,
            "review_source_blobs mismatch",
        ):
            freeze_reviewed_historical_execution_plan(
                reviewed,
                expected_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
