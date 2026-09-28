from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_one_shot_executor_workflow_preflight_proof_runtime_freeze import (
    DEC346_FREEZE_FINGERPRINT_SHA256,
    WORKFLOW_PREFLIGHT_CANONICAL_SHA256,
    WORKFLOW_PREFLIGHT_PROOF_ARTIFACT_DIGEST,
    WORKFLOW_PREFLIGHT_PROOF_ARTIFACT_ID,
    WORKFLOW_PREFLIGHT_PROOF_HEAD_SHA,
    WORKFLOW_PREFLIGHT_PROOF_JOB_ID,
    WORKFLOW_PREFLIGHT_PROOF_RUN_ID,
    WORKFLOW_PREFLIGHT_RAW_SHA256,
    freeze_one_shot_historical_executor_workflow_preflight_proof_runtime_evidence,
    validate_one_shot_historical_executor_workflow_preflight_proof_runtime_freeze_sources,
)


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


def _preflight() -> dict[str, object]:
    return {
        "broker_mutation_authorized": False,
        "candidate_compilation_authorized": False,
        "dec342_workflow_contract_blob_sha": (
            "d87bf8f4fc3ad8fc081760c1250dc0f8dc9ffadc"
        ),
        "decision": "DEC-343",
        "demo_order_authorized": False,
        "discovery_result_authorized": True,
        "expected_head_sha": WORKFLOW_PREFLIGHT_PROOF_HEAD_SHA,
        "expected_target_run_attempt": 1,
        "expected_target_run_number": 2,
        "historical_discovery_execution_authorized": True,
        "historical_execute_mode_available": False,
        "historical_executor_available": False,
        "historical_result_attempt_count": 0,
        "historical_result_dispatch_authorized": False,
        "historical_result_run_conclusion": None,
        "historical_result_run_id": None,
        "historical_result_run_status": None,
        "historical_result_slot_consumed": False,
        "live_order_authorized": False,
        "next_gate": (
            "REPOSITORY_HOSTED_READ_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "WORKFLOW_PREFLIGHT_PROOF"
        ),
        "one_shot_historical_executor_source_authorized": True,
        "one_shot_historical_executor_workflow_source_authorized": True,
        "phase8b_authorized": False,
        "planned_dispatch_command": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "promotion_authorized": False,
        "proof_run_count": 1,
        "proof_run_id": 36358289723,
        "real_money_authorized": False,
        "replacement_run_authorized": False,
        "rerun_authorized": False,
        "reserved_robustness_access_authorized": False,
        "retry_authorized": False,
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_"
            "PREFLIGHT_SLOT_AVAILABLE"
        ),
        "trading_authorized": False,
        "version": (
            "fmp-exp062-one-shot-historical-executor-workflow-preflight-v1"
        ),
        "workflow_contract_decision": "DEC-342",
        "workflow_contract_version": (
            "fmp-exp062-one-shot-historical-executor-workflow-contract-v1"
        ),
    }


def _preflight_bytes(value: dict[str, object] | None = None) -> bytes:
    payload = _preflight() if value is None else value
    return (
        json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def _run() -> dict[str, object]:
    return {
        "id": WORKFLOW_PREFLIGHT_PROOF_RUN_ID,
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
        "head_sha": WORKFLOW_PREFLIGHT_PROOF_HEAD_SHA,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": WORKFLOW_PREFLIGHT_PROOF_JOB_ID,
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
                "id": WORKFLOW_PREFLIGHT_PROOF_ARTIFACT_ID,
                "name": (
                    "exp062-dec344-one-shot-historical-executor-"
                    "workflow-preflight-" + WORKFLOW_PREFLIGHT_PROOF_HEAD_SHA
                ),
                "digest": WORKFLOW_PREFLIGHT_PROOF_ARTIFACT_DIGEST,
                "expired": False,
            }
        ]
    }


class Exp062OneShotHistoricalExecutorWorkflowPreflightProofRuntimeFreezeTests(
    unittest.TestCase
):
    def _freeze(
        self,
        *,
        run: dict[str, object] | None = None,
        jobs: dict[str, object] | None = None,
        artifacts: dict[str, object] | None = None,
        preflight_bytes: bytes | None = None,
        artifact_zip_sha256: str | None = None,
    ) -> dict[str, object]:
        return freeze_one_shot_historical_executor_workflow_preflight_proof_runtime_evidence(
            repository_root=Path("."),
            proof_run=_run() if run is None else run,
            proof_jobs_payload=_jobs() if jobs is None else jobs,
            proof_artifacts_payload=(
                _artifacts() if artifacts is None else artifacts
            ),
            preflight_bytes=(
                _preflight_bytes()
                if preflight_bytes is None
                else preflight_bytes
            ),
            artifact_zip_sha256=(
                WORKFLOW_PREFLIGHT_PROOF_ARTIFACT_DIGEST.removeprefix(
                    "sha256:"
                )
                if artifact_zip_sha256 is None
                else artifact_zip_sha256
            ),
        )

    def test_source_bindings_pin_dec345_dec346_and_terminal_contract(self) -> None:
        report = (
            validate_one_shot_historical_executor_workflow_preflight_proof_runtime_freeze_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            report["dec345_reviewer"],
            "ebd5bc2943675ba4276374cf339aa120aaf3b257",
        )
        self.assertEqual(
            report["dec346_freeze_builder"],
            "02b294aea02932a465913f6e5ed993e2cb45d441",
        )
        self.assertEqual(
            report["dec334_terminal_review_contract"],
            "fda2a45f74b101303467cf7b8527bec1bfc5e168",
        )

    def test_exact_real_evidence_freezes_deterministically(self) -> None:
        first = self._freeze()
        second = self._freeze()
        self.assertEqual(first, second)
        self.assertEqual(
            first["stage"],
            (
                "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_PREFLIGHT_"
                "PROOF_RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
            ),
        )
        self.assertEqual(
            first["workflow_preflight_proof_run_id"],
            WORKFLOW_PREFLIGHT_PROOF_RUN_ID,
        )
        self.assertEqual(
            first["workflow_preflight_proof_job_id"],
            WORKFLOW_PREFLIGHT_PROOF_JOB_ID,
        )
        self.assertEqual(
            first["workflow_preflight_proof_artifact_id"],
            WORKFLOW_PREFLIGHT_PROOF_ARTIFACT_ID,
        )
        self.assertEqual(
            first["dec346_freeze_fingerprint_sha256"],
            DEC346_FREEZE_FINGERPRINT_SHA256,
        )
        self.assertEqual(first["dec334_terminal_review_decision"], "DEC-334")
        self.assertTrue(first["historical_result_slot_verified_available"])
        self.assertFalse(first["historical_result_slot_consumed"])
        self.assertEqual(first["expected_target_run_number"], 2)
        self.assertEqual(first["expected_target_run_attempt"], 1)
        self.assertFalse(first["historical_executor_available"])
        self.assertFalse(first["historical_result_dispatch_authorized"])
        self.assertFalse(first["historical_execute_mode_available"])
        self.assertFalse(first["demo_order_authorized"])
        self.assertFalse(first["live_order_authorized"])
        self.assertFalse(first["trading_authorized"])

        unsigned = dict(first)
        fingerprint = unsigned.pop("runtime_freeze_fingerprint_sha256")
        self.assertEqual(
            fingerprint,
            hashlib.sha256(_canonical_json(unsigned)).hexdigest(),
        )

    def test_preflight_fixture_matches_real_hashes(self) -> None:
        raw = _preflight_bytes()
        canonical = _canonical_json(_preflight())
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            WORKFLOW_PREFLIGHT_RAW_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            WORKFLOW_PREFLIGHT_CANONICAL_SHA256,
        )

    def test_wrong_run_id_is_rejected(self) -> None:
        run = _run()
        run["id"] = WORKFLOW_PREFLIGHT_PROOF_RUN_ID + 1
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result proof_run_id mismatch",
        ):
            self._freeze(run=run)

    def test_wrong_job_id_is_rejected(self) -> None:
        jobs = _jobs()
        jobs["jobs"][0]["id"] = WORKFLOW_PREFLIGHT_PROOF_JOB_ID + 1
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result proof_job_id mismatch",
        ):
            self._freeze(jobs=jobs)

    def test_wrong_artifact_id_is_rejected(self) -> None:
        artifacts = _artifacts()
        artifacts["artifacts"][0]["id"] = (
            WORKFLOW_PREFLIGHT_PROOF_ARTIFACT_ID + 1
        )
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result proof_artifact_id mismatch",
        ):
            self._freeze(artifacts=artifacts)

    def test_artifact_zip_hash_mismatch_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "artifact ZIP sha256 mismatch",
        ):
            self._freeze(artifact_zip_sha256="0" * 64)

    def test_executor_authority_escalation_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["historical_executor_available"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_available",
        ):
            self._freeze(preflight_bytes=_preflight_bytes(preflight))


if __name__ == "__main__":
    unittest.main()
