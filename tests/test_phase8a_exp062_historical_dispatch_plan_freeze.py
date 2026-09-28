from __future__ import annotations

import hashlib
import json
import unittest

from fmp.discovery.exp062_historical_dispatch_plan_freeze import (
    EXP062_REVIEWED_HISTORICAL_DISPATCH_PLAN_FREEZE_DECISION,
    freeze_reviewed_historical_dispatch_plan,
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
        "decision": "DEC-321",
        "version": "fmp-exp062-historical-dispatch-plan-proof-review-v1",
        "stage": "EXP062_HISTORICAL_DISPATCH_PLAN_PROOF_REVIEWED_SLOT_AVAILABLE",
        "proof_workflow_name": "phase8a-exp062-historical-dispatch-plan",
        "proof_workflow_path": (
            ".github/workflows/phase8a-exp062-historical-dispatch-plan.yml"
        ),
        "proof_run_id": 40000000001,
        "proof_head_sha": HEAD,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "success",
        "proof_job_id": 50000000001,
        "proof_artifact_id": 60000000001,
        "proof_artifact_name": (
            "exp062-dec320-historical-dispatch-plan-" + HEAD
        ),
        "proof_artifact_digest": "sha256:" + ("1" * 64),
        "plan_raw_sha256": "2" * 64,
        "plan_canonical_sha256": "3" * 64,
        "plan_decision": "DEC-319",
        "plan_operator_version": (
            "fmp-exp062-historical-dispatch-operator-v1"
        ),
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "one_shot_dispatch_source_authorized": True,
        "historical_result_dispatch_authorized": False,
        "historical_executor_available": False,
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
            "dec320_workflow": "259900792ff7b2126b7bee4577f05ba7abdb0f25",
            "dec317_runtime_freeze": (
                "9626f6cd1c66a67d91dd3acf743e120ea8d2e9c0"
            ),
            "dec318_authorization": (
                "b5360751459212cfabb37a3dd7758fe0cc28c4a6"
            ),
            "dec319_operator": (
                "72c1cd881c004c91c2cf7c3797e00d68e3a27056"
            ),
            "dec319_operator_cli": (
                "9f41465f287daccc5f7685453129bc20916bec17"
            ),
            "active_discovery_workflow": (
                "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
            ),
        },
        "next_gate": (
            "IMMUTABLE_HISTORICAL_DISPATCH_PLAN_PROOF_FREEZE_BEFORE_ONE_SHOT_EXECUTOR"
        ),
    }


class Exp062HistoricalDispatchPlanFreezeTests(unittest.TestCase):
    def test_reviewed_plan_freezes_deterministically(self) -> None:
        first = freeze_reviewed_historical_dispatch_plan(
            _reviewed(),
            expected_head_sha=HEAD,
        )
        second = freeze_reviewed_historical_dispatch_plan(
            _reviewed(),
            expected_head_sha=HEAD,
        )
        self.assertEqual(first, second)
        self.assertEqual(
            first["decision"],
            EXP062_REVIEWED_HISTORICAL_DISPATCH_PLAN_FREEZE_DECISION,
        )
        self.assertEqual(
            first["stage"],
            "EXP062_HISTORICAL_DISPATCH_PLAN_REVIEWED_AND_FROZEN",
        )
        self.assertFalse(first["historical_result_slot_consumed"])
        self.assertTrue(first["historical_result_slot_verified_available"])
        self.assertTrue(first["one_shot_dispatch_source_authorized"])
        self.assertFalse(first["historical_result_dispatch_authorized"])
        self.assertFalse(first["historical_executor_available"])
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
        value = _reviewed()
        value["proof_head_sha"] = "b" * 40
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result proof_head_sha mismatch",
        ):
            freeze_reviewed_historical_dispatch_plan(
                value,
                expected_head_sha=HEAD,
            )

    def test_dispatch_authority_escalation_is_rejected(self) -> None:
        value = _reviewed()
        value["historical_result_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_dispatch_authorized mismatch",
        ):
            freeze_reviewed_historical_dispatch_plan(
                value,
                expected_head_sha=HEAD,
            )

    def test_executor_availability_escalation_is_rejected(self) -> None:
        value = _reviewed()
        value["historical_executor_available"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_available mismatch",
        ):
            freeze_reviewed_historical_dispatch_plan(
                value,
                expected_head_sha=HEAD,
            )

    def test_source_blob_drift_is_rejected(self) -> None:
        value = _reviewed()
        blobs = value["review_source_blobs"]
        assert isinstance(blobs, dict)
        blobs["dec319_operator"] = "f" * 40
        with self.assertRaisesRegex(
            ValueError,
            "review_source_blobs mismatch",
        ):
            freeze_reviewed_historical_dispatch_plan(
                value,
                expected_head_sha=HEAD,
            )

    def test_malformed_artifact_digest_is_rejected(self) -> None:
        value = _reviewed()
        value["proof_artifact_digest"] = "sha256:not-a-digest"
        with self.assertRaisesRegex(
            ValueError,
            "proof_artifact_digest",
        ):
            freeze_reviewed_historical_dispatch_plan(
                value,
                expected_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
