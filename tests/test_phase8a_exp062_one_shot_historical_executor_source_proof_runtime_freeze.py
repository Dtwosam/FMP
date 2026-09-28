from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_one_shot_executor_source_proof_runtime_freeze import (
    DEC340_FREEZE_FINGERPRINT_SHA256,
    SOURCE_CONTRACT_CANONICAL_SHA256,
    SOURCE_CONTRACT_RAW_SHA256,
    SOURCE_PROOF_ARTIFACT_DIGEST,
    SOURCE_PROOF_ARTIFACT_ID,
    SOURCE_PROOF_HEAD_SHA,
    SOURCE_PROOF_JOB_ID,
    SOURCE_PROOF_RUN_ID,
    freeze_one_shot_historical_executor_source_proof_runtime_evidence,
    validate_one_shot_historical_executor_source_proof_runtime_freeze_sources,
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


def _contract() -> dict[str, object]:
    return {
        "broker_mutation_authorized": False,
        "candidate_compilation_authorized": False,
        "dec336_runtime_freeze_blob_sha": (
            "9673e115eeb373c4881d36a8b5d91a2801cd8ad1"
        ),
        "decision": "DEC-337",
        "demo_order_authorized": False,
        "discovery_result_authorized": True,
        "expected_head_sha": SOURCE_PROOF_HEAD_SHA,
        "expected_target_run_attempt": 1,
        "expected_target_run_number": 2,
        "historical_discovery_execution_authorized": True,
        "historical_execute_mode_available": False,
        "historical_executor_available": False,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_dispatch_authorized": False,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "live_order_authorized": False,
        "next_gate": (
            "REPOSITORY_HOSTED_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_SOURCE_PROOF"
        ),
        "one_shot_historical_executor_source_authorized": True,
        "phase8b_authorized": False,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "promotion_authorized": False,
        "real_money_authorized": False,
        "replacement_run_authorized": False,
        "rerun_authorized": False,
        "reserved_robustness_access_authorized": False,
        "retry_authorized": False,
        "runtime_freeze_decision": "DEC-336",
        "runtime_freeze_fingerprint_sha256": (
            "147ab77116979afa8d0d07c3c748fb80e02865a382317824320f6af534bfc374"
        ),
        "runtime_freeze_version": (
            "fmp-exp062-historical-executor-activation-preflight-runtime-freeze-v1"
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_AUTHORIZED_"
            "RUNTIME_DISPATCH_LOCKED"
        ),
        "terminal_review_decision": "DEC-334",
        "terminal_review_version": (
            "fmp-exp062-historical-terminal-review-contract-v1"
        ),
        "trading_authorized": False,
        "version": "fmp-exp062-one-shot-historical-executor-source-v1",
    }


def _contract_bytes(value: dict[str, object] | None = None) -> bytes:
    payload = _contract() if value is None else value
    return (
        json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def _run() -> dict[str, object]:
    return {
        "id": SOURCE_PROOF_RUN_ID,
        "name": "phase8a-exp062-one-shot-historical-executor-source-proof",
        "path": (
            ".github/workflows/"
            "phase8a-exp062-one-shot-historical-executor-source-proof.yml"
        ),
        "event": "push",
        "head_branch": "main",
        "head_sha": SOURCE_PROOF_HEAD_SHA,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": SOURCE_PROOF_JOB_ID,
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
                "id": SOURCE_PROOF_ARTIFACT_ID,
                "name": (
                    "exp062-dec338-one-shot-historical-executor-source-"
                    + SOURCE_PROOF_HEAD_SHA
                ),
                "digest": SOURCE_PROOF_ARTIFACT_DIGEST,
                "expired": False,
            }
        ]
    }


class Exp062OneShotHistoricalExecutorSourceProofRuntimeFreezeTests(
    unittest.TestCase
):
    def _freeze(
        self,
        *,
        run: dict[str, object] | None = None,
        jobs: dict[str, object] | None = None,
        artifacts: dict[str, object] | None = None,
        contract_bytes: bytes | None = None,
        artifact_zip_sha256: str | None = None,
    ) -> dict[str, object]:
        return freeze_one_shot_historical_executor_source_proof_runtime_evidence(
            repository_root=Path("."),
            proof_run=_run() if run is None else run,
            proof_jobs_payload=_jobs() if jobs is None else jobs,
            proof_artifacts_payload=(
                _artifacts() if artifacts is None else artifacts
            ),
            contract_bytes=(
                _contract_bytes()
                if contract_bytes is None
                else contract_bytes
            ),
            artifact_zip_sha256=(
                SOURCE_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:")
                if artifact_zip_sha256 is None
                else artifact_zip_sha256
            ),
        )

    def test_source_bindings_pin_dec339_dec340_and_terminal_contract(self) -> None:
        report = (
            validate_one_shot_historical_executor_source_proof_runtime_freeze_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            report["dec339_reviewer"],
            "673bfc55bffa908f793a9dbc36d7aed1f4a13784",
        )
        self.assertEqual(
            report["dec340_freeze_builder"],
            "804e9a57be2a114f8754334f89f9f5b883d1cee5",
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
                "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
                "RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
            ),
        )
        self.assertEqual(first["source_proof_run_id"], SOURCE_PROOF_RUN_ID)
        self.assertEqual(first["source_proof_job_id"], SOURCE_PROOF_JOB_ID)
        self.assertEqual(
            first["source_proof_artifact_id"],
            SOURCE_PROOF_ARTIFACT_ID,
        )
        self.assertEqual(
            first["dec340_freeze_fingerprint_sha256"],
            DEC340_FREEZE_FINGERPRINT_SHA256,
        )
        self.assertEqual(first["dec334_terminal_review_decision"], "DEC-334")
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
        fingerprint = unsigned.pop("runtime_freeze_fingerprint_sha256")
        self.assertEqual(
            fingerprint,
            hashlib.sha256(_canonical_json(unsigned)).hexdigest(),
        )

    def test_contract_fixture_matches_real_hashes(self) -> None:
        raw = _contract_bytes()
        canonical = _canonical_json(_contract())
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            SOURCE_CONTRACT_RAW_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            SOURCE_CONTRACT_CANONICAL_SHA256,
        )

    def test_wrong_run_id_is_rejected(self) -> None:
        run = _run()
        run["id"] = SOURCE_PROOF_RUN_ID + 1
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result proof_run_id mismatch",
        ):
            self._freeze(run=run)

    def test_wrong_job_id_is_rejected(self) -> None:
        jobs = _jobs()
        jobs["jobs"][0]["id"] = SOURCE_PROOF_JOB_ID + 1
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result proof_job_id mismatch",
        ):
            self._freeze(jobs=jobs)

    def test_wrong_artifact_id_is_rejected(self) -> None:
        artifacts = _artifacts()
        artifacts["artifacts"][0]["id"] = SOURCE_PROOF_ARTIFACT_ID + 1
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
        contract = _contract()
        contract["historical_executor_available"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_available",
        ):
            self._freeze(contract_bytes=_contract_bytes(contract))


if __name__ == "__main__":
    unittest.main()
