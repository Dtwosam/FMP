from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from fmp.discovery.historical_plan_result_decision import (
    DEC283_PLAN_CANONICAL_SHA256,
    DEC283_PLAN_RAW_SHA256,
    DEC283_PROOF_ARTIFACT_DIGEST,
    DEC283_PROOF_ARTIFACT_ID,
    DEC283_PROOF_RUN_ID,
    EXP061_REVIEWED_HISTORICAL_PLAN_DECISION,
    freeze_reviewed_historical_plan_proof,
    validate_reviewed_historical_plan_sources,
)


def _run() -> dict[str, object]:
    return {
        "id": DEC283_PROOF_RUN_ID,
        "name": "phase8a-exp061-historical-plan",
        "path": ".github/workflows/phase8a-exp061-historical-plan.yml",
        "event": "push",
        "head_branch": "main",
        "head_sha": "7fd3a9e878bf2760850037548e93dc1e8173c0c1",
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": DEC283_PROOF_ARTIFACT_ID,
                "name": (
                    "exp061-dec283-historical-plan-"
                    "7fd3a9e878bf2760850037548e93dc1e8173c0c1"
                ),
                "digest": DEC283_PROOF_ARTIFACT_DIGEST,
                "expired": False,
            }
        ]
    }


def _plan() -> dict[str, object]:
    return {
        "authorization_decision": "DEC-281",
        "authorization_version": (
            "fmp-exp061-historical-run-authorization-v1"
        ),
        "broker_mutation_authorized": False,
        "candidate_compilation_authorized": False,
        "decision": "DEC-282",
        "demo_order_authorized": False,
        "discovery_result_authorized": False,
        "expected_head_sha": "7fd3a9e878bf2760850037548e93dc1e8173c0c1",
        "historical_discovery_execution_authorized": False,
        "historical_execute_mode_available": False,
        "historical_result_attempt_count": 0,
        "historical_result_dispatch_authorized": False,
        "historical_result_head_sha": None,
        "historical_result_run_conclusion": None,
        "historical_result_run_id": None,
        "historical_result_run_status": None,
        "historical_result_slot_consumed": False,
        "historical_result_slot_source_authorized": True,
        "live_order_authorized": False,
        "operator_version": "fmp-exp061-historical-operator-v1",
        "phase8b_authorized": False,
        "planned_dispatch_command": (
            "gh workflow run phase8a-exp061-discovery.yml --ref main"
        ),
        "proof_head_sha": "041b7b2f5aac8821156fab346df8ab30f4be2a7b",
        "proof_run_count": 1,
        "proof_run_id": 36319888985,
        "real_money_authorized": False,
        "replacement_run_authorized": False,
        "rerun_authorized": False,
        "reserved_robustness_access_authorized": False,
        "retry_authorized": False,
        "stage": "EXP061_HISTORICAL_RESULT_SLOT_AVAILABLE",
        "trading_authorized": False,
    }


class Exp061ReviewedHistoricalPlanProofTests(unittest.TestCase):
    def test_sources_bind_exact_dec281_282_283_stack(self) -> None:
        report = validate_reviewed_historical_plan_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            report["decision"],
            EXP061_REVIEWED_HISTORICAL_PLAN_DECISION,
        )
        self.assertEqual(
            report["dec283_merged_commit"],
            "7fd3a9e878bf2760850037548e93dc1e8173c0c1",
        )
        for field in (
            "historical_result_dispatch_authorized",
            "historical_discovery_execution_authorized",
            "discovery_result_authorized",
            "reserved_robustness_access_authorized",
            "candidate_compilation_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(report[field], field)

    def test_exact_real_plan_proof_freezes_slot_available(self) -> None:
        report = freeze_reviewed_historical_plan_proof(
            repository_root=Path("."),
            proof_run=_run(),
            proof_artifacts_payload=_artifacts(),
            plan=_plan(),
            artifact_zip_sha256=DEC283_PROOF_ARTIFACT_DIGEST.removeprefix(
                "sha256:"
            ),
            plan_raw_sha256=DEC283_PLAN_RAW_SHA256,
        )
        self.assertEqual(
            report["stage"],
            "EXP061_HISTORICAL_PLAN_PROOF_REVIEWED_AND_FROZEN",
        )
        self.assertTrue(report["historical_result_slot_verified_available"])
        self.assertFalse(report["historical_result_slot_consumed"])
        self.assertEqual(report["historical_result_attempt_count"], 0)
        self.assertEqual(
            report["plan_canonical_sha256"],
            DEC283_PLAN_CANONICAL_SHA256,
        )
        self.assertFalse(report["historical_result_dispatch_authorized"])
        self.assertFalse(report["historical_discovery_execution_authorized"])

    def test_plan_tamper_is_rejected(self) -> None:
        plan = _plan()
        plan["historical_result_attempt_count"] = 1
        with self.assertRaisesRegex(
            ValueError,
            "historical operator empty-slot count mismatch|historical plan",
        ):
            freeze_reviewed_historical_plan_proof(
                repository_root=Path("."),
                proof_run=_run(),
                proof_artifacts_payload=_artifacts(),
                plan=plan,
                artifact_zip_sha256=(
                    DEC283_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:")
                ),
                plan_raw_sha256=DEC283_PLAN_RAW_SHA256,
            )

    def test_artifact_identity_or_digest_drift_is_rejected(self) -> None:
        artifacts = _artifacts()
        rows = artifacts["artifacts"]
        assert isinstance(rows, list)
        rows[0]["id"] = DEC283_PROOF_ARTIFACT_ID + 1
        with self.assertRaisesRegex(ValueError, "artifact id mismatch"):
            freeze_reviewed_historical_plan_proof(
                repository_root=Path("."),
                proof_run=_run(),
                proof_artifacts_payload=artifacts,
                plan=_plan(),
                artifact_zip_sha256=(
                    DEC283_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:")
                ),
                plan_raw_sha256=DEC283_PLAN_RAW_SHA256,
            )

        with self.assertRaisesRegex(ValueError, "artifact ZIP sha256 mismatch"):
            freeze_reviewed_historical_plan_proof(
                repository_root=Path("."),
                proof_run=_run(),
                proof_artifacts_payload=_artifacts(),
                plan=_plan(),
                artifact_zip_sha256="0" * 64,
                plan_raw_sha256=DEC283_PLAN_RAW_SHA256,
            )

    def test_raw_plan_hash_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "plan raw sha256 mismatch"):
            freeze_reviewed_historical_plan_proof(
                repository_root=Path("."),
                proof_run=_run(),
                proof_artifacts_payload=_artifacts(),
                plan=_plan(),
                artifact_zip_sha256=(
                    DEC283_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:")
                ),
                plan_raw_sha256="0" * 64,
            )

    def test_expected_plan_fixture_matches_frozen_canonical_hash(self) -> None:
        raw = (
            json.dumps(
                _plan(),
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            DEC283_PLAN_CANONICAL_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
