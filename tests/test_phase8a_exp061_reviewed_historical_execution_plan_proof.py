from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from fmp.discovery.historical_execution_plan_result_decision import (
    DEC287_PLAN_CANONICAL_SHA256,
    DEC287_PLAN_RAW_SHA256,
    DEC287_PROOF_ARTIFACT_DIGEST,
    DEC287_PROOF_ARTIFACT_ID,
    DEC287_PROOF_RUN_ID,
    EXP061_REVIEWED_HISTORICAL_EXECUTION_PLAN_DECISION,
    freeze_reviewed_historical_execution_plan_proof,
    validate_reviewed_historical_execution_plan_sources,
)


def _run() -> dict[str, object]:
    return {
        "id": DEC287_PROOF_RUN_ID,
        "name": "phase8a-exp061-historical-execution-plan",
        "path": ".github/workflows/phase8a-exp061-historical-execution-plan.yml",
        "event": "push",
        "head_branch": "main",
        "head_sha": "958a0b830bb867d1c11e2a82be7fc301a6a75474",
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": DEC287_PROOF_ARTIFACT_ID,
                "name": (
                    "exp061-dec287-historical-execution-plan-"
                    "958a0b830bb867d1c11e2a82be7fc301a6a75474"
                ),
                "digest": DEC287_PROOF_ARTIFACT_DIGEST,
                "expired": False,
            }
        ]
    }


def _plan() -> dict[str, object]:
    return {
        "activated_cli_blob_sha": "477aa9e8de4452e6444d1ee4361218aca445180d",
        "active_workflow_blob_sha": "d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9",
        "authorization_decision": "DEC-285",
        "authorization_version": (
            "fmp-exp061-historical-execution-authorization-v1"
        ),
        "broker_mutation_authorized": False,
        "candidate_compilation_authorized": False,
        "decision": "DEC-286",
        "demo_order_authorized": False,
        "discovery_result_authorized": True,
        "expected_head_sha": "958a0b830bb867d1c11e2a82be7fc301a6a75474",
        "expected_repository": "Dtwosam/FMP",
        "expected_target_run_attempt": 1,
        "expected_target_run_number": 2,
        "expected_workflow_event": "workflow_dispatch",
        "expected_workflow_name": "phase8a-exp061-discovery",
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
            "68566fc86ff3470cc8b6ebef606becaff9f3450b"
        ),
        "legacy_workflow_source_execution_authorized": False,
        "live_order_authorized": False,
        "market_learning_adapter_blob_sha": (
            "978a33554fad7e9d78b002778c4896be0af3333a"
        ),
        "operator_version": "fmp-exp061-historical-execution-operator-v1",
        "pattern_miner_blob_sha": "495a67699eb5014e52129f0238a2737049fe38e6",
        "pattern_protocol_blob_sha": "63b3f0121d6a50eb9e8e62ab666d70eb91791621",
        "phase8b_authorized": False,
        "planned_dispatch_command": (
            "gh workflow run phase8a-exp061-discovery.yml --ref main"
        ),
        "promotion_authorized": False,
        "proof_run_count": 1,
        "proof_run_id": 36319888985,
        "proof_run_number": 1,
        "range_limited_loader_blob_sha": (
            "df1d029a6f8b8d3862ebbf990ed1170a5982e1ea"
        ),
        "real_money_authorized": False,
        "replacement_run_authorized": False,
        "rerun_authorized": False,
        "reserved_robustness_access_authorized": False,
        "reserved_robustness_end_exclusive": "2026-08-21T00:00:00Z",
        "reserved_robustness_start": "2023-01-01T00:00:00Z",
        "retry_authorized": False,
        "reviewed_plan_decision": "DEC-284",
        "reviewed_plan_source_blob_sha": (
            "14d9c559eaa33e5cb217baaf3ed2597091735b18"
        ),
        "reviewed_plan_version": (
            "fmp-exp061-reviewed-historical-plan-proof-v1"
        ),
        "run_contract_blob_sha": "260eb6930673427266463517546969635188b143",
        "runtime_requirements_blob_sha": (
            "1ff32214dee10d877a067e750cd69ffad96d5fe5"
        ),
        "stage": "EXP061_HISTORICAL_RESULT_SLOT_AVAILABLE",
        "trading_authorized": False,
        "version": "fmp-exp061-historical-execution-authorization-v1",
    }


class Exp061ReviewedHistoricalExecutionPlanProofTests(unittest.TestCase):
    def test_sources_bind_exact_dec285_286_287_stack(self) -> None:
        report = validate_reviewed_historical_execution_plan_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            report["decision"],
            EXP061_REVIEWED_HISTORICAL_EXECUTION_PLAN_DECISION,
        )
        self.assertEqual(
            report["dec287_merged_commit"],
            "958a0b830bb867d1c11e2a82be7fc301a6a75474",
        )
        for field in (
            "historical_result_dispatch_authorized",
            "historical_execute_mode_available",
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
            "reserved_robustness_access_authorized",
            "candidate_compilation_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(report[field], field)

    def test_exact_real_execution_plan_proof_freezes_run_two_target(self) -> None:
        report = freeze_reviewed_historical_execution_plan_proof(
            repository_root=Path("."),
            proof_run=_run(),
            proof_artifacts_payload=_artifacts(),
            plan=_plan(),
            artifact_zip_sha256=DEC287_PROOF_ARTIFACT_DIGEST.removeprefix(
                "sha256:"
            ),
            plan_raw_sha256=DEC287_PLAN_RAW_SHA256,
        )
        self.assertEqual(
            report["stage"],
            "EXP061_HISTORICAL_EXECUTION_PLAN_PROOF_REVIEWED_AND_FROZEN",
        )
        self.assertTrue(report["historical_result_slot_verified_available"])
        self.assertFalse(report["historical_result_slot_consumed"])
        self.assertEqual(report["historical_result_attempt_count"], 0)
        self.assertEqual(report["expected_target_run_number"], 2)
        self.assertEqual(report["expected_target_run_attempt"], 1)
        self.assertEqual(
            report["plan_canonical_sha256"],
            DEC287_PLAN_CANONICAL_SHA256,
        )
        self.assertTrue(report["historical_discovery_execution_authorized"])
        self.assertTrue(report["discovery_result_authorized"])
        self.assertFalse(report["historical_result_dispatch_authorized"])

    def test_run_identity_tamper_is_rejected(self) -> None:
        run = _run()
        run["head_sha"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "proof run head_sha mismatch"):
            freeze_reviewed_historical_execution_plan_proof(
                repository_root=Path("."),
                proof_run=run,
                proof_artifacts_payload=_artifacts(),
                plan=_plan(),
                artifact_zip_sha256=(
                    DEC287_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:")
                ),
                plan_raw_sha256=DEC287_PLAN_RAW_SHA256,
            )

    def test_plan_run_two_target_tamper_is_rejected(self) -> None:
        plan = _plan()
        plan["expected_target_run_number"] = 3
        with self.assertRaisesRegex(
            ValueError,
            "target run number must remain 2|historical execution plan",
        ):
            freeze_reviewed_historical_execution_plan_proof(
                repository_root=Path("."),
                proof_run=_run(),
                proof_artifacts_payload=_artifacts(),
                plan=plan,
                artifact_zip_sha256=(
                    DEC287_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:")
                ),
                plan_raw_sha256=DEC287_PLAN_RAW_SHA256,
            )

    def test_dispatch_or_trading_tamper_is_rejected(self) -> None:
        for field in (
            "historical_result_dispatch_authorized",
            "trading_authorized",
        ):
            with self.subTest(field=field):
                plan = _plan()
                plan[field] = True
                with self.assertRaises(ValueError):
                    freeze_reviewed_historical_execution_plan_proof(
                        repository_root=Path("."),
                        proof_run=_run(),
                        proof_artifacts_payload=_artifacts(),
                        plan=plan,
                        artifact_zip_sha256=(
                            DEC287_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:")
                        ),
                        plan_raw_sha256=DEC287_PLAN_RAW_SHA256,
                    )

    def test_artifact_identity_or_zip_digest_drift_is_rejected(self) -> None:
        artifacts = _artifacts()
        rows = artifacts["artifacts"]
        assert isinstance(rows, list)
        rows[0]["id"] = DEC287_PROOF_ARTIFACT_ID + 1
        with self.assertRaisesRegex(ValueError, "artifact id mismatch"):
            freeze_reviewed_historical_execution_plan_proof(
                repository_root=Path("."),
                proof_run=_run(),
                proof_artifacts_payload=artifacts,
                plan=_plan(),
                artifact_zip_sha256=(
                    DEC287_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:")
                ),
                plan_raw_sha256=DEC287_PLAN_RAW_SHA256,
            )

        with self.assertRaisesRegex(ValueError, "artifact ZIP sha256 mismatch"):
            freeze_reviewed_historical_execution_plan_proof(
                repository_root=Path("."),
                proof_run=_run(),
                proof_artifacts_payload=_artifacts(),
                plan=_plan(),
                artifact_zip_sha256="0" * 64,
                plan_raw_sha256=DEC287_PLAN_RAW_SHA256,
            )

    def test_raw_plan_hash_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "plan raw sha256 mismatch"):
            freeze_reviewed_historical_execution_plan_proof(
                repository_root=Path("."),
                proof_run=_run(),
                proof_artifacts_payload=_artifacts(),
                plan=_plan(),
                artifact_zip_sha256=(
                    DEC287_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:")
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
            DEC287_PLAN_CANONICAL_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
