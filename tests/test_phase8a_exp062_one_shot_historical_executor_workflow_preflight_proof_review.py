from __future__ import annotations

import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_one_shot_executor_workflow_preflight_proof_review import (
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_PREFLIGHT_PROOF_REVIEW_DECISION,
    review_one_shot_historical_executor_workflow_preflight_proof,
    validate_one_shot_historical_executor_workflow_preflight_proof_review_sources,
)


HEAD = "a" * 40


def _preflight() -> dict[str, object]:
    return {
        "decision": "DEC-343",
        "version": (
            "fmp-exp062-one-shot-historical-executor-workflow-preflight-v1"
        ),
        "workflow_contract_decision": "DEC-342",
        "workflow_contract_version": (
            "fmp-exp062-one-shot-historical-executor-workflow-contract-v1"
        ),
        "dec342_workflow_contract_blob_sha": (
            "d87bf8f4fc3ad8fc081760c1250dc0f8dc9ffadc"
        ),
        "expected_head_sha": HEAD,
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_"
            "PREFLIGHT_SLOT_AVAILABLE"
        ),
        "proof_run_id": 36358289723,
        "proof_run_count": 1,
        "historical_result_attempt_count": 0,
        "historical_result_run_id": None,
        "historical_result_run_status": None,
        "historical_result_run_conclusion": None,
        "historical_result_slot_consumed": False,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "one_shot_historical_executor_source_authorized": True,
        "one_shot_historical_executor_workflow_source_authorized": True,
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
        "next_gate": (
            "REPOSITORY_HOSTED_READ_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "WORKFLOW_PREFLIGHT_PROOF"
        ),
    }


def _preflight_bytes(value: dict[str, object] | None = None) -> bytes:
    payload = _preflight() if value is None else value
    return (
        json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def _run() -> dict[str, object]:
    return {
        "id": 40000000001,
        "name": (
            "phase8a-exp062-one-shot-historical-executor-"
            "workflow-preflight-proof"
        ),
        "path": (
            ".github/workflows/"
            "phase8a-exp062-one-shot-historical-executor-"
            "workflow-preflight-proof.yml"
        ),
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
                "name": (
                    "read-only-one-shot-historical-executor-"
                    "workflow-preflight"
                ),
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
                "name": (
                    "exp062-dec344-one-shot-historical-executor-"
                    "workflow-preflight-" + HEAD
                ),
                "digest": "sha256:" + ("1" * 64),
                "expired": False,
            }
        ]
    }


class Exp062OneShotHistoricalExecutorWorkflowPreflightProofReviewTests(
    unittest.TestCase
):
    def _review(
        self,
        *,
        run: dict[str, object] | None = None,
        jobs: dict[str, object] | None = None,
        artifacts: dict[str, object] | None = None,
        preflight_bytes: bytes | None = None,
    ) -> dict[str, object]:
        return review_one_shot_historical_executor_workflow_preflight_proof(
            run=_run() if run is None else run,
            jobs_payload=_jobs() if jobs is None else jobs,
            artifacts_payload=_artifacts() if artifacts is None else artifacts,
            preflight_bytes=(
                _preflight_bytes()
                if preflight_bytes is None
                else preflight_bytes
            ),
            expected_head_sha=HEAD,
            repository_root=Path("."),
        )

    def test_source_bindings_pin_dec344_and_preflight_chain(self) -> None:
        report = (
            validate_one_shot_historical_executor_workflow_preflight_proof_review_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            report["dec344_workflow"],
            "b070aa25d11ef481602686fb85da9a8bd5c8c1cc",
        )
        self.assertEqual(
            report["dec343_preflight"],
            "1339dd02256b9d3fc51b2a312a2272fd5d949796",
        )
        self.assertEqual(
            report["dec343_preflight_cli"],
            "8b2e190e75f378a52fa66ad61b0e1bbadacb343b",
        )
        self.assertEqual(
            report["dec342_workflow_contract"],
            "d87bf8f4fc3ad8fc081760c1250dc0f8dc9ffadc",
        )

    def test_valid_proof_reviews_without_runtime_authority(self) -> None:
        first = self._review()
        second = self._review()
        self.assertEqual(first, second)
        self.assertEqual(
            first["decision"],
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_PREFLIGHT_PROOF_REVIEW_DECISION,
        )
        self.assertEqual(
            first["stage"],
            (
                "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_PREFLIGHT_"
                "PROOF_REVIEWED_SLOT_AVAILABLE"
            ),
        )
        self.assertEqual(first["historical_result_attempt_count"], 0)
        self.assertFalse(first["historical_result_slot_consumed"])
        self.assertTrue(first["historical_result_slot_verified_available"])
        self.assertEqual(first["expected_target_run_number"], 2)
        self.assertEqual(first["expected_target_run_attempt"], 1)
        self.assertTrue(
            first["one_shot_historical_executor_workflow_source_authorized"]
        )
        self.assertFalse(first["historical_executor_available"])
        self.assertFalse(first["historical_result_dispatch_authorized"])
        self.assertFalse(first["historical_execute_mode_available"])
        self.assertFalse(first["reserved_robustness_access_authorized"])
        self.assertFalse(first["demo_order_authorized"])
        self.assertFalse(first["live_order_authorized"])
        self.assertFalse(first["trading_authorized"])
        self.assertEqual(len(first["preflight_raw_sha256"]), 64)
        self.assertEqual(len(first["preflight_canonical_sha256"]), 64)

    def test_wrong_run_head_is_rejected(self) -> None:
        run = _run()
        run["head_sha"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "run head_sha mismatch"):
            self._review(run=run)

    def test_wrong_job_shape_is_rejected(self) -> None:
        jobs = _jobs()
        jobs["jobs"][0]["conclusion"] = "failure"
        with self.assertRaisesRegex(ValueError, "job conclusion mismatch"):
            self._review(jobs=jobs)

    def test_expired_artifact_is_rejected(self) -> None:
        artifacts = _artifacts()
        artifacts["artifacts"][0]["expired"] = True
        with self.assertRaisesRegex(ValueError, "must be non-expired"):
            self._review(artifacts=artifacts)

    def test_executor_authority_escalation_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["historical_executor_available"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_available",
        ):
            self._review(preflight_bytes=_preflight_bytes(preflight))

    def test_dispatch_authority_escalation_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["historical_result_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_dispatch_authorized",
        ):
            self._review(preflight_bytes=_preflight_bytes(preflight))

    def test_consumed_slot_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["historical_result_attempt_count"] = 1
        preflight["historical_result_slot_consumed"] = True
        preflight["historical_result_run_id"] = 40000000000
        preflight["planned_dispatch_command"] = None
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_attempt_count mismatch",
        ):
            self._review(preflight_bytes=_preflight_bytes(preflight))

    def test_invalid_json_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            self._review(preflight_bytes=b"{not-json")


if __name__ == "__main__":
    unittest.main()
