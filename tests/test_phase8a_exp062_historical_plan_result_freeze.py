from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_plan_result_freeze import (
    DEC309_ARTIFACT_ZIP_SHA256,
    DEC309_MERGED_COMMIT,
    DEC309_PLAN_CANONICAL_SHA256,
    DEC309_PLAN_PROOF_ARTIFACT_DIGEST,
    DEC309_PLAN_PROOF_ARTIFACT_ID,
    DEC309_PLAN_PROOF_JOB_ID,
    DEC309_PLAN_PROOF_RUN_ID,
    DEC309_PLAN_RAW_SHA256,
    EXP062_HISTORICAL_PLAN_PROOF_FREEZE_DECISION,
    freeze_historical_plan_proof,
    validate_historical_plan_freeze_sources,
)
from fmp.discovery.exp062_runtime_proof_freeze import (
    PROOF_HEAD_SHA,
    PROOF_RUN_ID,
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
        "decision": "DEC-308",
        "operator_version": "fmp-exp062-historical-operator-v1",
        "authorization_decision": "DEC-307",
        "authorization_version": (
            "fmp-exp062-historical-run-authorization-v1"
        ),
        "expected_head_sha": DEC309_MERGED_COMMIT,
        "stage": "EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE",
        "proof_run_id": PROOF_RUN_ID,
        "proof_head_sha": PROOF_HEAD_SHA,
        "proof_run_count": 1,
        "historical_result_attempt_count": 0,
        "historical_result_run_id": None,
        "historical_result_head_sha": None,
        "historical_result_run_status": None,
        "historical_result_run_conclusion": None,
        "historical_result_slot_consumed": False,
        "planned_dispatch_command": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "historical_result_slot_source_authorized": True,
        "historical_result_dispatch_authorized": False,
        "historical_execute_mode_available": False,
        "historical_discovery_execution_authorized": False,
        "discovery_result_authorized": False,
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


def _plan_bytes(plan: dict[str, object] | None = None) -> bytes:
    value = _plan() if plan is None else plan
    return (
        json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def _run() -> dict[str, object]:
    return {
        "id": DEC309_PLAN_PROOF_RUN_ID,
        "name": "phase8a-exp062-historical-plan",
        "path": ".github/workflows/phase8a-exp062-historical-plan.yml",
        "event": "push",
        "head_branch": "main",
        "head_sha": DEC309_MERGED_COMMIT,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": DEC309_PLAN_PROOF_JOB_ID,
                "name": "read-only-historical-plan",
                "status": "completed",
                "conclusion": "success",
            }
        ]
    }


def _artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": DEC309_PLAN_PROOF_ARTIFACT_ID,
                "name": (
                    "exp062-dec309-historical-plan-" + DEC309_MERGED_COMMIT
                ),
                "digest": DEC309_PLAN_PROOF_ARTIFACT_DIGEST,
                "expired": False,
            }
        ]
    }


class Exp062HistoricalPlanResultFreezeTests(unittest.TestCase):
    def _freeze(
        self,
        *,
        run: dict[str, object] | None = None,
        jobs: dict[str, object] | None = None,
        artifacts: dict[str, object] | None = None,
        plan_bytes: bytes | None = None,
        artifact_zip_sha256: str = DEC309_ARTIFACT_ZIP_SHA256,
    ) -> dict[str, object]:
        return freeze_historical_plan_proof(
            repository_root=Path("."),
            proof_run=_run() if run is None else run,
            proof_jobs_payload=_jobs() if jobs is None else jobs,
            proof_artifacts_payload=(
                _artifacts() if artifacts is None else artifacts
            ),
            plan_bytes=_plan_bytes() if plan_bytes is None else plan_bytes,
            artifact_zip_sha256=artifact_zip_sha256,
        )

    def test_sources_pin_dec310_reviewer(self) -> None:
        sources = validate_historical_plan_freeze_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            sources["dec310_review_source_blob_sha"],
            "5c8870c10e86122342bb181cb5a15ebc709924ce",
        )

    def test_exact_runtime_evidence_freezes_deterministically(self) -> None:
        first = self._freeze()
        second = self._freeze()
        self.assertEqual(first, second)
        self.assertEqual(
            first["decision"],
            EXP062_HISTORICAL_PLAN_PROOF_FREEZE_DECISION,
        )
        self.assertEqual(
            first["stage"],
            "EXP062_HISTORICAL_PLAN_PROOF_REVIEWED_AND_FROZEN",
        )
        self.assertEqual(first["proof_run_id"], DEC309_PLAN_PROOF_RUN_ID)
        self.assertEqual(first["proof_job_id"], DEC309_PLAN_PROOF_JOB_ID)
        self.assertEqual(
            first["proof_artifact_id"],
            DEC309_PLAN_PROOF_ARTIFACT_ID,
        )
        self.assertEqual(first["plan_raw_sha256"], DEC309_PLAN_RAW_SHA256)
        self.assertEqual(
            first["plan_canonical_sha256"],
            DEC309_PLAN_CANONICAL_SHA256,
        )
        self.assertTrue(first["historical_result_slot_verified_available"])
        self.assertFalse(first["historical_result_slot_consumed"])
        self.assertFalse(first["historical_result_dispatch_authorized"])
        self.assertFalse(first["historical_execute_mode_available"])
        self.assertFalse(
            first["historical_discovery_execution_authorized"]
        )
        self.assertFalse(first["demo_order_authorized"])
        self.assertFalse(first["live_order_authorized"])
        self.assertFalse(first["trading_authorized"])
        self.assertEqual(
            first["next_gate"],
            "SOURCE_ONLY_HISTORICAL_EXECUTION_AUTHORIZATION_CONTRACT",
        )

        unsigned = dict(first)
        fingerprint = unsigned.pop("freeze_fingerprint_sha256")
        self.assertEqual(
            fingerprint,
            hashlib.sha256(_canonical_json(unsigned)).hexdigest(),
        )

    def test_fixture_hashes_match_frozen_real_plan(self) -> None:
        raw = _plan_bytes()
        canonical = _canonical_json(_plan())
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            DEC309_PLAN_RAW_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            DEC309_PLAN_CANONICAL_SHA256,
        )

    def test_wrong_concrete_run_id_is_rejected(self) -> None:
        run = _run()
        run["id"] = DEC309_PLAN_PROOF_RUN_ID + 1
        with self.assertRaisesRegex(
            ValueError,
            "reviewed plan proof proof_run_id mismatch",
        ):
            self._freeze(run=run)

    def test_wrong_concrete_job_id_is_rejected(self) -> None:
        jobs = _jobs()
        jobs["jobs"][0]["id"] = DEC309_PLAN_PROOF_JOB_ID + 1
        with self.assertRaisesRegex(
            ValueError,
            "reviewed plan proof proof_job_id mismatch",
        ):
            self._freeze(jobs=jobs)

    def test_wrong_concrete_artifact_id_is_rejected(self) -> None:
        artifacts = _artifacts()
        artifacts["artifacts"][0]["id"] = (
            DEC309_PLAN_PROOF_ARTIFACT_ID + 1
        )
        with self.assertRaisesRegex(
            ValueError,
            "reviewed plan proof proof_artifact_id mismatch",
        ):
            self._freeze(artifacts=artifacts)

    def test_artifact_zip_hash_mismatch_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "artifact ZIP sha256 mismatch",
        ):
            self._freeze(artifact_zip_sha256="1" * 64)

    def test_plan_authority_escalation_is_rejected(self) -> None:
        plan = _plan()
        plan["historical_result_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_dispatch_authorized must remain false",
        ):
            self._freeze(plan_bytes=_plan_bytes(plan))

    def test_plan_slot_consumption_drift_is_rejected(self) -> None:
        plan = _plan()
        plan["historical_result_slot_consumed"] = True
        with self.assertRaisesRegex(
            ValueError,
            "empty slot marked consumed",
        ):
            self._freeze(plan_bytes=_plan_bytes(plan))


if __name__ == "__main__":
    unittest.main()
