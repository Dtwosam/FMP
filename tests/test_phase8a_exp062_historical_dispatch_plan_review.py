from __future__ import annotations

import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_dispatch_operator import (
    build_historical_dispatch_plan,
)
from fmp.discovery.exp062_historical_dispatch_plan_review import (
    EXP062_HISTORICAL_DISPATCH_PLAN_REVIEW_DECISION,
    review_historical_dispatch_plan_proof,
)
from fmp.discovery.exp062_runtime_proof_freeze import (
    PROOF_HEAD_SHA,
    PROOF_RUN_ID,
)


HEAD = "a" * 40


def _gate_proof() -> dict[str, object]:
    return {
        "id": PROOF_RUN_ID,
        "name": "phase8a-exp062-discovery",
        "path": ".github/workflows/phase8a-exp062-discovery.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": PROOF_HEAD_SHA,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "failure",
    }


def _plan() -> dict[str, object]:
    return build_historical_dispatch_plan(
        repository_root=Path("."),
        main_branch={"name": "main", "commit": {"sha": HEAD}},
        workflow_runs={"workflow_runs": [_gate_proof()]},
        expected_head_sha=HEAD,
    )


def _plan_bytes(plan: dict[str, object] | None = None) -> bytes:
    value = _plan() if plan is None else plan
    return (
        json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def _run() -> dict[str, object]:
    return {
        "id": 40000000001,
        "name": "phase8a-exp062-historical-dispatch-plan",
        "path": ".github/workflows/phase8a-exp062-historical-dispatch-plan.yml",
        "event": "push",
        "head_branch": "main",
        "head_sha": HEAD,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": 50000000001,
                "name": "read-only-historical-dispatch-plan",
                "status": "completed",
                "conclusion": "success",
            }
        ]
    }


def _artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": 60000000001,
                "name": f"exp062-dec320-historical-dispatch-plan-{HEAD}",
                "digest": "sha256:" + ("1" * 64),
                "expired": False,
            }
        ]
    }


class Exp062HistoricalDispatchPlanReviewTests(unittest.TestCase):
    def _review(
        self,
        *,
        run: dict[str, object] | None = None,
        jobs: dict[str, object] | None = None,
        artifacts: dict[str, object] | None = None,
        plan_bytes: bytes | None = None,
    ) -> dict[str, object]:
        return review_historical_dispatch_plan_proof(
            run=_run() if run is None else run,
            jobs_payload=_jobs() if jobs is None else jobs,
            artifacts_payload=_artifacts() if artifacts is None else artifacts,
            plan_bytes=_plan_bytes() if plan_bytes is None else plan_bytes,
            expected_head_sha=HEAD,
            repository_root=Path("."),
        )

    def test_valid_proof_reviews_without_runtime_dispatch(self) -> None:
        report = self._review()
        self.assertEqual(
            report["decision"],
            EXP062_HISTORICAL_DISPATCH_PLAN_REVIEW_DECISION,
        )
        self.assertEqual(
            report["stage"],
            "EXP062_HISTORICAL_DISPATCH_PLAN_PROOF_REVIEWED_SLOT_AVAILABLE",
        )
        self.assertEqual(report["historical_gate_proof_run_id"], PROOF_RUN_ID)
        self.assertEqual(report["historical_result_attempt_count"], 0)
        self.assertFalse(report["historical_result_slot_consumed"])
        self.assertTrue(report["historical_result_slot_verified_available"])
        self.assertEqual(report["expected_target_run_number"], 2)
        self.assertTrue(report["one_shot_dispatch_source_authorized"])
        self.assertFalse(report["historical_result_dispatch_authorized"])
        self.assertFalse(report["historical_executor_available"])
        self.assertFalse(report["historical_execute_mode_available"])
        self.assertFalse(report["reserved_robustness_access_authorized"])
        self.assertFalse(report["demo_order_authorized"])
        self.assertFalse(report["live_order_authorized"])
        self.assertFalse(report["trading_authorized"])
        self.assertEqual(len(report["plan_raw_sha256"]), 64)
        self.assertEqual(len(report["plan_canonical_sha256"]), 64)

    def test_run_head_drift_is_rejected(self) -> None:
        run = _run()
        run["head_sha"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "run head_sha mismatch"):
            self._review(run=run)

    def test_failed_job_is_rejected(self) -> None:
        jobs = _jobs()
        jobs["jobs"][0]["conclusion"] = "failure"
        with self.assertRaisesRegex(ValueError, "job conclusion mismatch"):
            self._review(jobs=jobs)

    def test_expired_artifact_is_rejected(self) -> None:
        artifacts = _artifacts()
        artifacts["artifacts"][0]["expired"] = True
        with self.assertRaisesRegex(ValueError, "must be non-expired"):
            self._review(artifacts=artifacts)

    def test_dispatch_authority_escalation_is_rejected(self) -> None:
        plan = _plan()
        plan["historical_result_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_dispatch_authorized mismatch",
        ):
            self._review(plan_bytes=_plan_bytes(plan))

    def test_executor_availability_escalation_is_rejected(self) -> None:
        plan = _plan()
        plan["historical_executor_available"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_available mismatch",
        ):
            self._review(plan_bytes=_plan_bytes(plan))

    def test_invalid_plan_json_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            self._review(plan_bytes=b"{not-json")


if __name__ == "__main__":
    unittest.main()
