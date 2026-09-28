from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_execution_runtime_freeze import (
    DEC316_FREEZE_FINGERPRINT_SHA256,
    PLAN_CANONICAL_SHA256,
    PLAN_PROOF_ARTIFACT_DIGEST,
    PLAN_PROOF_ARTIFACT_ID,
    PLAN_PROOF_HEAD_SHA,
    PLAN_PROOF_JOB_ID,
    PLAN_PROOF_RUN_ID,
    PLAN_RAW_SHA256,
    freeze_historical_execution_runtime_evidence,
    validate_historical_execution_runtime_freeze_sources,
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
        "activated_cli_blob_sha": "773784d0770d54b1d3e41fba2057b9314a090034",
        "active_workflow_blob_sha": "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50",
        "authorization_decision": "DEC-312",
        "authorization_version": (
            "fmp-exp062-historical-execution-authorization-v1"
        ),
        "broker_mutation_authorized": False,
        "candidate_compilation_authorized": False,
        "decision": "DEC-313",
        "demo_order_authorized": False,
        "discovery_result_authorized": True,
        "expected_head_sha": PLAN_PROOF_HEAD_SHA,
        "expected_repository": "Dtwosam/FMP",
        "expected_target_run_attempt": 1,
        "expected_target_run_number": 2,
        "expected_workflow_event": "workflow_dispatch",
        "expected_workflow_name": "phase8a-exp062-discovery",
        "expected_workflow_ref": "refs/heads/main",
        "expected_workflow_run_attempt": 1,
        "expected_workflow_run_number": 2,
        "historical_data_end_exclusive": "2023-01-01T00:00:00Z",
        "historical_data_start": "2015-01-01T00:00:00Z",
        "historical_discovery_execution_authorized": True,
        "historical_execute_mode_available": False,
        "historical_execution_source_authorized": True,
        "historical_result_attempt_count": 0,
        "historical_result_dispatch_authorized": False,
        "historical_result_run_conclusion": None,
        "historical_result_run_id": None,
        "historical_result_run_status": None,
        "historical_result_slot_consumed": False,
        "historical_result_slot_source_authorized": True,
        "legacy_workflow_source_blob_sha": (
            "e20ded13de24f99e8ea6cfdc6cb0d1309d984f24"
        ),
        "legacy_workflow_source_execution_authorized": False,
        "live_order_authorized": False,
        "market_learning_adapter_blob_sha": (
            "978a33554fad7e9d78b002778c4896be0af3333a"
        ),
        "operator_version": "fmp-exp062-historical-execution-operator-v1",
        "pattern_miner_blob_sha": "495a67699eb5014e52129f0238a2737049fe38e6",
        "pattern_protocol_blob_sha": "63b3f0121d6a50eb9e8e62ab666d70eb91791621",
        "phase8b_authorized": False,
        "planned_dispatch_command": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "promotion_authorized": False,
        "proof_run_count": 1,
        "proof_run_id": 36358289723,
        "proof_run_number": 1,
        "range_limited_loader_blob_sha": (
            "df1d029a6f8b8d3862ebbf990ed1170a5982e1ea"
        ),
        "real_money_authorized": False,
        "repaired_adapter_blob_sha": (
            "491ba8c92cb6e6e4c715bfb1ecb934b6949e1596"
        ),
        "replacement_run_authorized": False,
        "rerun_authorized": False,
        "reserved_robustness_access_authorized": False,
        "reserved_robustness_end_exclusive": "2026-08-21T00:00:00Z",
        "reserved_robustness_start": "2023-01-01T00:00:00Z",
        "retry_authorized": False,
        "reviewed_plan_decision": "DEC-311",
        "reviewed_plan_source_blob_sha": (
            "e3274118b37066efe2869d554e78e6b68e64b32a"
        ),
        "reviewed_plan_version": (
            "fmp-exp062-historical-plan-proof-freeze-v1"
        ),
        "run_contract_blob_sha": "d304c8fafcff64f967f6777b1c494819f69d4a03",
        "runtime_requirements_blob_sha": (
            "1ff32214dee10d877a067e750cd69ffad96d5fe5"
        ),
        "stage": "EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE",
        "trading_authorized": False,
        "version": "fmp-exp062-historical-execution-authorization-v1",
    }


def _plan_bytes(plan: dict[str, object] | None = None) -> bytes:
    value = _plan() if plan is None else plan
    return (
        json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def _run() -> dict[str, object]:
    return {
        "id": PLAN_PROOF_RUN_ID,
        "name": "phase8a-exp062-historical-execution-plan",
        "path": ".github/workflows/phase8a-exp062-historical-execution-plan.yml",
        "event": "push",
        "head_branch": "main",
        "head_sha": PLAN_PROOF_HEAD_SHA,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": PLAN_PROOF_JOB_ID,
                "name": "read-only-historical-execution-plan",
                "status": "completed",
                "conclusion": "success",
            }
        ]
    }


def _artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": PLAN_PROOF_ARTIFACT_ID,
                "name": (
                    "exp062-dec314-historical-execution-plan-"
                    + PLAN_PROOF_HEAD_SHA
                ),
                "digest": PLAN_PROOF_ARTIFACT_DIGEST,
                "expired": False,
            }
        ]
    }


class Exp062HistoricalExecutionRuntimeFreezeTests(unittest.TestCase):
    def _freeze(
        self,
        *,
        run: dict[str, object] | None = None,
        jobs: dict[str, object] | None = None,
        artifacts: dict[str, object] | None = None,
        plan_bytes: bytes | None = None,
        artifact_zip_sha256: str | None = None,
    ) -> dict[str, object]:
        return freeze_historical_execution_runtime_evidence(
            repository_root=Path("."),
            proof_run=_run() if run is None else run,
            proof_jobs_payload=_jobs() if jobs is None else jobs,
            proof_artifacts_payload=(
                _artifacts() if artifacts is None else artifacts
            ),
            plan_bytes=_plan_bytes() if plan_bytes is None else plan_bytes,
            artifact_zip_sha256=(
                PLAN_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:")
                if artifact_zip_sha256 is None
                else artifact_zip_sha256
            ),
        )

    def test_source_bindings_pin_dec315_and_dec316(self) -> None:
        report = validate_historical_execution_runtime_freeze_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            report["dec315_reviewer"],
            "284789801505b9391be19ebb1a19c4fae28e2444",
        )
        self.assertEqual(
            report["dec316_freeze_builder"],
            "2867bc05986bf93dc531d152760bbbac604854fe",
        )

    def test_exact_real_evidence_freezes_deterministically(self) -> None:
        first = self._freeze()
        second = self._freeze()
        self.assertEqual(first, second)
        self.assertEqual(
            first["stage"],
            "EXP062_HISTORICAL_EXECUTION_PLAN_RUNTIME_EVIDENCE_BOUND_AND_FROZEN",
        )
        self.assertEqual(first["plan_proof_run_id"], PLAN_PROOF_RUN_ID)
        self.assertEqual(first["plan_proof_job_id"], PLAN_PROOF_JOB_ID)
        self.assertEqual(
            first["plan_proof_artifact_id"],
            PLAN_PROOF_ARTIFACT_ID,
        )
        self.assertEqual(
            first["dec316_freeze_fingerprint_sha256"],
            DEC316_FREEZE_FINGERPRINT_SHA256,
        )
        self.assertTrue(first["historical_result_slot_verified_available"])
        self.assertFalse(first["historical_result_slot_consumed"])
        self.assertEqual(first["expected_target_run_number"], 2)
        self.assertEqual(first["expected_target_run_attempt"], 1)
        self.assertTrue(first["historical_discovery_execution_authorized"])
        self.assertTrue(first["discovery_result_authorized"])
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

    def test_plan_fixture_matches_real_raw_and_canonical_hashes(self) -> None:
        raw = _plan_bytes()
        canonical = _canonical_json(_plan())
        self.assertEqual(hashlib.sha256(raw).hexdigest(), PLAN_RAW_SHA256)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            PLAN_CANONICAL_SHA256,
        )

    def test_wrong_run_id_is_rejected(self) -> None:
        run = _run()
        run["id"] = PLAN_PROOF_RUN_ID + 1
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result proof_run_id mismatch",
        ):
            self._freeze(run=run)

    def test_wrong_job_id_is_rejected(self) -> None:
        jobs = _jobs()
        jobs["jobs"][0]["id"] = PLAN_PROOF_JOB_ID + 1
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result proof_job_id mismatch",
        ):
            self._freeze(jobs=jobs)

    def test_wrong_artifact_id_is_rejected(self) -> None:
        artifacts = _artifacts()
        artifacts["artifacts"][0]["id"] = PLAN_PROOF_ARTIFACT_ID + 1
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

    def test_plan_authority_escalation_is_rejected(self) -> None:
        plan = _plan()
        plan["historical_result_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_dispatch_authorized must remain false",
        ):
            self._freeze(plan_bytes=_plan_bytes(plan))


if __name__ == "__main__":
    unittest.main()
