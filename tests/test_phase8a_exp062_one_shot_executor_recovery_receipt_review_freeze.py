from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_one_shot_executor_recovery_receipt_freeze import (
    freeze_reviewed_one_shot_executor_recovery_receipt,
)
from fmp.discovery.exp062_historical_one_shot_executor_recovery_receipt_review import (
    review_one_shot_executor_recovery_receipt,
    validate_one_shot_executor_recovery_receipt_review_sources,
)


_HEAD = "a" * 40
_RUN_ID = 777
_JOB_ID = 888
_ARTIFACT_ID = 999


def _receipt() -> dict[str, object]:
    return {
        "decision": "DEC-436",
        "recovery_workflow": (
            "phase8a-exp062-one-shot-historical-executor-recovery"
        ),
        "recovery_run_id": _RUN_ID,
        "recovery_run_number": 1,
        "recovery_run_attempt": 1,
        "recovery_head_sha": _HEAD,
        "failed_original_executor_run_id": 36702494195,
        "failed_original_executor_job_id": 109844958600,
        "failed_original_executor_run_number": 2,
        "failed_original_executor_run_attempt": 1,
        "failed_original_executor_conclusion": "failure",
        "failed_original_executor_dispatched_historical_result": False,
        "historical_result_run_id": 123456789,
        "historical_result_run_number": 2,
        "historical_result_run_attempt": 1,
        "historical_result_head_sha": _HEAD,
        "dispatch_command": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
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
    }


def _receipt_bytes(value: dict[str, object] | None = None) -> bytes:
    payload = _receipt() if value is None else value
    return (
        json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def _run() -> dict[str, object]:
    return {
        "id": _RUN_ID,
        "name": "phase8a-exp062-one-shot-historical-executor-recovery",
        "path": (
            ".github/workflows/"
            "phase8a-exp062-one-shot-historical-executor-recovery.yml"
        ),
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": _HEAD,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": _JOB_ID,
                "name": "one-shot-historical-executor-recovery",
                "status": "completed",
                "conclusion": "success",
            }
        ]
    }


def _artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": _ARTIFACT_ID,
                "name": (
                    "exp062-dec436-one-shot-historical-executor-"
                    "recovery-receipt-" + _HEAD
                ),
                "digest": "sha256:" + ("1" * 64),
                "expired": False,
            }
        ]
    }


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-437/438 require the installed DEC-436 recovery source",
)
class Exp062OneShotExecutorRecoveryReceiptReviewFreezeTests(unittest.TestCase):
    def _review(
        self,
        *,
        run: dict[str, object] | None = None,
        jobs: dict[str, object] | None = None,
        artifacts: dict[str, object] | None = None,
        receipt: bytes | None = None,
    ) -> dict[str, object]:
        return review_one_shot_executor_recovery_receipt(
            run=_run() if run is None else run,
            jobs_payload=_jobs() if jobs is None else jobs,
            artifacts_payload=_artifacts() if artifacts is None else artifacts,
            receipt_bytes=_receipt_bytes() if receipt is None else receipt,
            expected_head_sha=_HEAD,
            repository_root=Path("."),
        )

    def test_source_bindings_pin_dec436_and_frozen_workflows(self) -> None:
        source = validate_one_shot_executor_recovery_receipt_review_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["dec436_recovery_workflow"],
            "a2520a108373d25d67dd470794eeb4f0fc9e3187",
        )
        self.assertEqual(
            source["dec436_recovery_authorization"],
            "481fbfbb43557b1b42c0d9bc84ded0775816714e",
        )
        self.assertEqual(
            source["original_executor_workflow"],
            "51ce87584369be957482460d81649adb1cb9f05d",
        )
        self.assertEqual(
            source["active_discovery_workflow"],
            "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50",
        )

    def test_exact_receipt_reviews_and_freezes_deterministically(self) -> None:
        reviewed = self._review()
        self.assertEqual(reviewed["decision"], "DEC-437")
        self.assertEqual(reviewed["recovery_run_id"], _RUN_ID)
        self.assertEqual(reviewed["historical_result_run_id"], 123456789)
        self.assertEqual(reviewed["historical_result_run_number"], 2)
        self.assertEqual(reviewed["historical_result_run_attempt"], 1)
        self.assertEqual(reviewed["historical_result_head_sha"], _HEAD)
        self.assertTrue(reviewed["historical_result_dispatched"])
        self.assertFalse(reviewed["historical_execute_mode_available"])
        self.assertFalse(reviewed["rerun_authorized"])
        self.assertFalse(reviewed["trading_authorized"])

        frozen_a = freeze_reviewed_one_shot_executor_recovery_receipt(
            reviewed,
            expected_head_sha=_HEAD,
        )
        frozen_b = freeze_reviewed_one_shot_executor_recovery_receipt(
            reviewed,
            expected_head_sha=_HEAD,
        )
        self.assertEqual(frozen_a, frozen_b)
        self.assertEqual(frozen_a["decision"], "DEC-438")
        self.assertEqual(frozen_a["source_review_decision"], "DEC-437")
        self.assertEqual(frozen_a["historical_result_run_id"], 123456789)
        self.assertFalse(frozen_a["historical_execute_mode_available"])
        self.assertFalse(frozen_a["replacement_run_authorized"])
        self.assertFalse(frozen_a["trading_authorized"])

        unsigned = dict(frozen_a)
        fingerprint = unsigned.pop("freeze_fingerprint_sha256")
        canonical = (
            json.dumps(
                unsigned,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
        self.assertEqual(
            fingerprint,
            hashlib.sha256(canonical).hexdigest(),
        )

    def test_receipt_target_head_drift_is_rejected(self) -> None:
        receipt = _receipt()
        receipt["historical_result_head_sha"] = "b" * 40
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_head_sha mismatch",
        ):
            self._review(receipt=_receipt_bytes(receipt))

    def test_recovery_run_attempt_drift_is_rejected(self) -> None:
        run = _run()
        run["run_attempt"] = 2
        with self.assertRaisesRegex(
            ValueError,
            "recovery run run_attempt mismatch",
        ):
            self._review(run=run)

    def test_receipt_authority_escalation_is_rejected(self) -> None:
        receipt = _receipt()
        receipt["trading_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "trading_authorized must remain false",
        ):
            self._review(receipt=_receipt_bytes(receipt))


if __name__ == "__main__":
    unittest.main()
