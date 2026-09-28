from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_executor_preflight_runtime_freeze import (
    DEC328_FREEZE_FINGERPRINT_SHA256,
    PREFLIGHT_CANONICAL_SHA256,
    PREFLIGHT_PROOF_ARTIFACT_DIGEST,
    PREFLIGHT_PROOF_ARTIFACT_ID,
    PREFLIGHT_PROOF_HEAD_SHA,
    PREFLIGHT_PROOF_JOB_ID,
    PREFLIGHT_PROOF_RUN_ID,
    PREFLIGHT_RAW_SHA256,
    freeze_historical_executor_preflight_runtime_evidence,
    validate_historical_executor_preflight_runtime_freeze_sources,
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
        "dec324_executor_contract_blob_sha": (
            "12d514e86a2b458dd692810450e69b30f554a6bd"
        ),
        "decision": "DEC-325",
        "demo_order_authorized": False,
        "discovery_result_authorized": True,
        "executor_contract_decision": "DEC-324",
        "executor_contract_version": (
            "fmp-exp062-historical-executor-contract-v1"
        ),
        "expected_head_sha": PREFLIGHT_PROOF_HEAD_SHA,
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
        "next_gate": "REPOSITORY_HOSTED_READ_ONLY_EXECUTOR_PREFLIGHT_PROOF",
        "one_shot_executor_source_authorized": True,
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
        "stage": "EXP062_ONE_SHOT_EXECUTOR_PREFLIGHT_SLOT_AVAILABLE",
        "trading_authorized": False,
        "version": "fmp-exp062-historical-executor-preflight-v1",
    }


def _preflight_bytes(
    value: dict[str, object] | None = None,
) -> bytes:
    payload = _preflight() if value is None else value
    return (
        json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def _run() -> dict[str, object]:
    return {
        "id": PREFLIGHT_PROOF_RUN_ID,
        "name": "phase8a-exp062-historical-executor-preflight",
        "path": ".github/workflows/phase8a-exp062-historical-executor-preflight.yml",
        "event": "push",
        "head_branch": "main",
        "head_sha": PREFLIGHT_PROOF_HEAD_SHA,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": PREFLIGHT_PROOF_JOB_ID,
                "name": "read-only-historical-executor-preflight",
                "status": "completed",
                "conclusion": "success",
            }
        ]
    }


def _artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": PREFLIGHT_PROOF_ARTIFACT_ID,
                "name": (
                    "exp062-dec326-historical-executor-preflight-"
                    + PREFLIGHT_PROOF_HEAD_SHA
                ),
                "digest": PREFLIGHT_PROOF_ARTIFACT_DIGEST,
                "expired": False,
            }
        ]
    }


class Exp062HistoricalExecutorPreflightRuntimeFreezeTests(unittest.TestCase):
    def _freeze(
        self,
        *,
        run: dict[str, object] | None = None,
        jobs: dict[str, object] | None = None,
        artifacts: dict[str, object] | None = None,
        preflight_bytes: bytes | None = None,
        artifact_zip_sha256: str | None = None,
    ) -> dict[str, object]:
        return freeze_historical_executor_preflight_runtime_evidence(
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
                PREFLIGHT_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:")
                if artifact_zip_sha256 is None
                else artifact_zip_sha256
            ),
        )

    def test_source_bindings_pin_dec327_and_dec328(self) -> None:
        report = (
            validate_historical_executor_preflight_runtime_freeze_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            report["dec327_reviewer"],
            "da3febc87e69a81f88088c0b34ba0650956d1873",
        )
        self.assertEqual(
            report["dec328_freeze_builder"],
            "ce37dd70c167182441b503c38b1197223917ff72",
        )

    def test_exact_real_evidence_freezes_deterministically(self) -> None:
        first = self._freeze()
        second = self._freeze()
        self.assertEqual(first, second)
        self.assertEqual(
            first["stage"],
            "EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_RUNTIME_EVIDENCE_BOUND_AND_FROZEN",
        )
        self.assertEqual(
            first["preflight_proof_run_id"],
            PREFLIGHT_PROOF_RUN_ID,
        )
        self.assertEqual(
            first["preflight_proof_job_id"],
            PREFLIGHT_PROOF_JOB_ID,
        )
        self.assertEqual(
            first["preflight_proof_artifact_id"],
            PREFLIGHT_PROOF_ARTIFACT_ID,
        )
        self.assertEqual(
            first["dec328_freeze_fingerprint_sha256"],
            DEC328_FREEZE_FINGERPRINT_SHA256,
        )
        self.assertTrue(first["historical_result_slot_verified_available"])
        self.assertFalse(first["historical_result_slot_consumed"])
        self.assertEqual(first["expected_target_run_number"], 2)
        self.assertEqual(first["expected_target_run_attempt"], 1)
        self.assertTrue(first["one_shot_executor_source_authorized"])
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
        self.assertEqual(hashlib.sha256(raw).hexdigest(), PREFLIGHT_RAW_SHA256)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            PREFLIGHT_CANONICAL_SHA256,
        )

    def test_wrong_run_id_is_rejected(self) -> None:
        run = _run()
        run["id"] = PREFLIGHT_PROOF_RUN_ID + 1
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result proof_run_id mismatch",
        ):
            self._freeze(run=run)

    def test_wrong_job_id_is_rejected(self) -> None:
        jobs = _jobs()
        jobs["jobs"][0]["id"] = PREFLIGHT_PROOF_JOB_ID + 1
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result proof_job_id mismatch",
        ):
            self._freeze(jobs=jobs)

    def test_wrong_artifact_id_is_rejected(self) -> None:
        artifacts = _artifacts()
        artifacts["artifacts"][0]["id"] = PREFLIGHT_PROOF_ARTIFACT_ID + 1
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
