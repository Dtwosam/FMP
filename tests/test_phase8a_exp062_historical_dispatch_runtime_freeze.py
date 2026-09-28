from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_dispatch_runtime_freeze import (
    DEC322_FREEZE_FINGERPRINT_SHA256,
    DISPATCH_PLAN_CANONICAL_SHA256,
    DISPATCH_PLAN_PROOF_ARTIFACT_DIGEST,
    DISPATCH_PLAN_PROOF_ARTIFACT_ID,
    DISPATCH_PLAN_PROOF_HEAD_SHA,
    DISPATCH_PLAN_PROOF_JOB_ID,
    DISPATCH_PLAN_PROOF_RUN_ID,
    DISPATCH_PLAN_RAW_SHA256,
    freeze_historical_dispatch_runtime_evidence,
    validate_historical_dispatch_runtime_freeze_sources,
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


def _plan() -> dict[str, object]:
    return {
        "authorization_decision": "DEC-318",
        "authorization_version": (
            "fmp-exp062-historical-dispatch-authorization-v1"
        ),
        "broker_mutation_authorized": False,
        "candidate_compilation_authorized": False,
        "dec318_dispatch_authorization_blob_sha": (
            "b5360751459212cfabb37a3dd7758fe0cc28c4a6"
        ),
        "decision": "DEC-319",
        "demo_order_authorized": False,
        "discovery_result_authorized": True,
        "expected_head_sha": DISPATCH_PLAN_PROOF_HEAD_SHA,
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
        "next_gate": "REPOSITORY_HOSTED_READ_ONLY_DISPATCH_PLAN_PROOF",
        "one_shot_dispatch_source_authorized": True,
        "operator_version": "fmp-exp062-historical-dispatch-operator-v1",
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
        "stage": "EXP062_ONE_SHOT_DISPATCH_SLOT_AVAILABLE",
        "trading_authorized": False,
    }


def _plan_bytes(plan: dict[str, object] | None = None) -> bytes:
    value = _plan() if plan is None else plan
    return (
        json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def _run() -> dict[str, object]:
    return {
        "id": DISPATCH_PLAN_PROOF_RUN_ID,
        "name": "phase8a-exp062-historical-dispatch-plan",
        "path": ".github/workflows/phase8a-exp062-historical-dispatch-plan.yml",
        "event": "push",
        "head_branch": "main",
        "head_sha": DISPATCH_PLAN_PROOF_HEAD_SHA,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": DISPATCH_PLAN_PROOF_JOB_ID,
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
                "id": DISPATCH_PLAN_PROOF_ARTIFACT_ID,
                "name": (
                    "exp062-dec320-historical-dispatch-plan-"
                    + DISPATCH_PLAN_PROOF_HEAD_SHA
                ),
                "digest": DISPATCH_PLAN_PROOF_ARTIFACT_DIGEST,
                "expired": False,
            }
        ]
    }


class Exp062HistoricalDispatchRuntimeFreezeTests(unittest.TestCase):
    def _freeze(
        self,
        *,
        run: dict[str, object] | None = None,
        jobs: dict[str, object] | None = None,
        artifacts: dict[str, object] | None = None,
        plan_bytes: bytes | None = None,
        artifact_zip_sha256: str | None = None,
    ) -> dict[str, object]:
        return freeze_historical_dispatch_runtime_evidence(
            repository_root=Path("."),
            proof_run=_run() if run is None else run,
            proof_jobs_payload=_jobs() if jobs is None else jobs,
            proof_artifacts_payload=(
                _artifacts() if artifacts is None else artifacts
            ),
            plan_bytes=_plan_bytes() if plan_bytes is None else plan_bytes,
            artifact_zip_sha256=(
                DISPATCH_PLAN_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:")
                if artifact_zip_sha256 is None
                else artifact_zip_sha256
            ),
        )

    def test_source_bindings_pin_dec321_and_dec322(self) -> None:
        report = validate_historical_dispatch_runtime_freeze_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            report["dec321_reviewer"],
            "8dee8008204ed816df211861ff4a7fb9e952d781",
        )
        self.assertEqual(
            report["dec322_freeze_builder"],
            "6b7ab36c939fca7a9d53569e4617ebe6584e5b7c",
        )

    def test_exact_real_evidence_freezes_deterministically(self) -> None:
        first = self._freeze()
        second = self._freeze()
        self.assertEqual(first, second)
        self.assertEqual(
            first["stage"],
            "EXP062_HISTORICAL_DISPATCH_PLAN_RUNTIME_EVIDENCE_BOUND_AND_FROZEN",
        )
        self.assertEqual(
            first["dispatch_plan_proof_run_id"],
            DISPATCH_PLAN_PROOF_RUN_ID,
        )
        self.assertEqual(
            first["dispatch_plan_proof_job_id"],
            DISPATCH_PLAN_PROOF_JOB_ID,
        )
        self.assertEqual(
            first["dispatch_plan_proof_artifact_id"],
            DISPATCH_PLAN_PROOF_ARTIFACT_ID,
        )
        self.assertEqual(
            first["dec322_freeze_fingerprint_sha256"],
            DEC322_FREEZE_FINGERPRINT_SHA256,
        )
        self.assertTrue(first["historical_result_slot_verified_available"])
        self.assertFalse(first["historical_result_slot_consumed"])
        self.assertEqual(first["expected_target_run_number"], 2)
        self.assertEqual(first["expected_target_run_attempt"], 1)
        self.assertTrue(first["one_shot_dispatch_source_authorized"])
        self.assertFalse(first["historical_result_dispatch_authorized"])
        self.assertFalse(first["historical_executor_available"])
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

    def test_plan_fixture_matches_real_raw_and_canonical_hashes(self) -> None:
        raw = _plan_bytes()
        canonical = _canonical_json(_plan())
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            DISPATCH_PLAN_RAW_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            DISPATCH_PLAN_CANONICAL_SHA256,
        )

    def test_wrong_run_id_is_rejected(self) -> None:
        run = _run()
        run["id"] = DISPATCH_PLAN_PROOF_RUN_ID + 1
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result proof_run_id mismatch",
        ):
            self._freeze(run=run)

    def test_wrong_job_id_is_rejected(self) -> None:
        jobs = _jobs()
        jobs["jobs"][0]["id"] = DISPATCH_PLAN_PROOF_JOB_ID + 1
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result proof_job_id mismatch",
        ):
            self._freeze(jobs=jobs)

    def test_wrong_artifact_id_is_rejected(self) -> None:
        artifacts = _artifacts()
        artifacts["artifacts"][0]["id"] = (
            DISPATCH_PLAN_PROOF_ARTIFACT_ID + 1
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

    def test_dispatch_authority_escalation_is_rejected(self) -> None:
        plan = _plan()
        plan["historical_result_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_dispatch_authorized",
        ):
            self._freeze(plan_bytes=_plan_bytes(plan))


if __name__ == "__main__":
    unittest.main()
