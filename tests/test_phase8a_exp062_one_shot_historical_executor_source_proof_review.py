from __future__ import annotations

import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_one_shot_executor_source_proof_review import (
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_DECISION,
    review_one_shot_historical_executor_source_proof,
    validate_one_shot_historical_executor_source_proof_review_sources,
)


HEAD = "a" * 40


def _contract() -> dict[str, object]:
    return {
        "decision": "DEC-337",
        "version": "fmp-exp062-one-shot-historical-executor-source-v1",
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_AUTHORIZED_"
            "RUNTIME_DISPATCH_LOCKED"
        ),
        "dec336_runtime_freeze_blob_sha": (
            "9673e115eeb373c4881d36a8b5d91a2801cd8ad1"
        ),
        "runtime_freeze_decision": "DEC-336",
        "runtime_freeze_version": (
            "fmp-exp062-historical-executor-activation-preflight-"
            "runtime-freeze-v1"
        ),
        "runtime_freeze_fingerprint_sha256": (
            "147ab77116979afa8d0d07c3c748fb80e02865a382317824320f6af534bfc374"
        ),
        "terminal_review_decision": "DEC-334",
        "terminal_review_version": (
            "fmp-exp062-historical-terminal-review-contract-v1"
        ),
        "expected_head_sha": HEAD,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
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
        "next_gate": (
            "REPOSITORY_HOSTED_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_SOURCE_PROOF"
        ),
    }


def _contract_bytes(value: dict[str, object] | None = None) -> bytes:
    payload = _contract() if value is None else value
    return (
        json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def _run() -> dict[str, object]:
    return {
        "id": 40000000001,
        "name": "phase8a-exp062-one-shot-historical-executor-source-proof",
        "path": (
            ".github/workflows/"
            "phase8a-exp062-one-shot-historical-executor-source-proof.yml"
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
                "name": "read-only-one-shot-historical-executor-source-proof",
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
                    "exp062-dec338-one-shot-historical-executor-source-" + HEAD
                ),
                "digest": "sha256:" + ("1" * 64),
                "expired": False,
            }
        ]
    }


class Exp062OneShotHistoricalExecutorSourceProofReviewTests(
    unittest.TestCase
):
    def _review(
        self,
        *,
        run: dict[str, object] | None = None,
        jobs: dict[str, object] | None = None,
        artifacts: dict[str, object] | None = None,
        contract_bytes: bytes | None = None,
    ) -> dict[str, object]:
        return review_one_shot_historical_executor_source_proof(
            run=_run() if run is None else run,
            jobs_payload=_jobs() if jobs is None else jobs,
            artifacts_payload=_artifacts() if artifacts is None else artifacts,
            contract_bytes=(
                _contract_bytes()
                if contract_bytes is None
                else contract_bytes
            ),
            expected_head_sha=HEAD,
            repository_root=Path("."),
        )

    def test_source_bindings_pin_dec338_and_executor_chain(self) -> None:
        report = (
            validate_one_shot_historical_executor_source_proof_review_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            report["dec338_workflow"],
            "3104d6521e1c11f0c8be92eab0eef21c5e9eb80c",
        )
        self.assertEqual(
            report["dec337_source"],
            "26ee48241550d6e52501fc901ab88aaa3f42e755",
        )
        self.assertEqual(
            report["dec336_runtime_freeze"],
            "9673e115eeb373c4881d36a8b5d91a2801cd8ad1",
        )
        self.assertEqual(
            report["dec334_terminal_review"],
            "fda2a45f74b101303467cf7b8527bec1bfc5e168",
        )

    def test_valid_proof_reviews_without_runtime_authority(self) -> None:
        first = self._review()
        second = self._review()
        self.assertEqual(first, second)
        self.assertEqual(
            first["decision"],
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_DECISION,
        )
        self.assertEqual(
            first["stage"],
            (
                "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
                "REVIEWED_SLOT_AVAILABLE"
            ),
        )
        self.assertEqual(first["historical_result_attempt_count"], 0)
        self.assertFalse(first["historical_result_slot_consumed"])
        self.assertTrue(first["historical_result_slot_verified_available"])
        self.assertEqual(first["expected_target_run_number"], 2)
        self.assertEqual(first["expected_target_run_attempt"], 1)
        self.assertTrue(
            first["one_shot_historical_executor_source_authorized"]
        )
        self.assertFalse(first["historical_executor_available"])
        self.assertFalse(first["historical_result_dispatch_authorized"])
        self.assertFalse(first["historical_execute_mode_available"])
        self.assertFalse(first["reserved_robustness_access_authorized"])
        self.assertFalse(first["demo_order_authorized"])
        self.assertFalse(first["live_order_authorized"])
        self.assertFalse(first["trading_authorized"])
        self.assertEqual(len(first["contract_raw_sha256"]), 64)
        self.assertEqual(len(first["contract_canonical_sha256"]), 64)

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
        contract = _contract()
        contract["historical_executor_available"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_available",
        ):
            self._review(contract_bytes=_contract_bytes(contract))

    def test_dispatch_authority_escalation_is_rejected(self) -> None:
        contract = _contract()
        contract["historical_result_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_dispatch_authorized",
        ):
            self._review(contract_bytes=_contract_bytes(contract))

    def test_invalid_json_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            self._review(contract_bytes=b"{not-json")


if __name__ == "__main__":
    unittest.main()
