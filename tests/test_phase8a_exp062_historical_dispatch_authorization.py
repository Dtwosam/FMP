from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_dispatch_authorization import (
    HISTORICAL_EXECUTOR_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    ONE_SHOT_DISPATCH_SOURCE_AUTHORIZED,
    build_historical_dispatch_authorization_contract,
    validate_historical_dispatch_authorization_sources,
)


def _runtime_freeze() -> dict[str, object]:
    return {
        "decision": "DEC-317",
        "version": "fmp-exp062-historical-execution-runtime-freeze-v1",
        "stage": (
            "EXP062_HISTORICAL_EXECUTION_PLAN_RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "plan_proof_head_sha": "ea69e82c9f653facba8ed6589fe4243848187ad3",
        "plan_proof_run_id": 36414282818,
        "plan_proof_run_number": 1,
        "plan_proof_run_attempt": 1,
        "plan_proof_run_conclusion": "success",
        "plan_proof_job_id": 108901556593,
        "plan_proof_artifact_id": 10966632240,
        "plan_proof_artifact_name": (
            "exp062-dec314-historical-execution-plan-"
            "ea69e82c9f653facba8ed6589fe4243848187ad3"
        ),
        "plan_proof_artifact_digest": (
            "sha256:9299ebfd344c0bd2a66ccd6e29339e035840c8b4204cbfc16bb6d3e938a53254"
        ),
        "plan_proof_artifact_zip_sha256": (
            "9299ebfd344c0bd2a66ccd6e29339e035840c8b4204cbfc16bb6d3e938a53254"
        ),
        "plan_raw_sha256": (
            "594b5bd129a93ad7b07f69e00826251dd693f1bb388e6b4dff64eda0b34a7c72"
        ),
        "plan_canonical_sha256": (
            "152bbb90efe3941f1338c73cf24f91f10a877cda3ee5c46f08c4f556d653a12f"
        ),
        "dec315_review_decision": "DEC-315",
        "dec315_review_version": (
            "fmp-exp062-historical-execution-plan-proof-review-v1"
        ),
        "dec316_freeze_decision": "DEC-316",
        "dec316_freeze_version": (
            "fmp-exp062-reviewed-historical-execution-plan-freeze-v1"
        ),
        "dec316_freeze_fingerprint_sha256": (
            "7c7d99f4c89aac4e11d27536b9f8d2d39322672a9a0332f141d1d86f93b19be3"
        ),
        "dec315_reviewer_blob_sha": (
            "284789801505b9391be19ebb1a19c4fae28e2444"
        ),
        "dec316_freeze_builder_blob_sha": (
            "2867bc05986bf93dc531d152760bbbac604854fe"
        ),
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "historical_execution_source_authorized": True,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "historical_result_dispatch_authorized": False,
        "historical_execute_mode_available": False,
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
            "SOURCE_ONLY_ONE_SHOT_HISTORICAL_DISPATCH_AUTHORIZATION_CONTRACT"
        ),
        "runtime_freeze_fingerprint_sha256": (
            "eeac1b77b7bd77b14880aeb192ea1df664c15b91e440e3938b8cba0a67b95619"
        ),
    }


class Exp062HistoricalDispatchAuthorizationTests(unittest.TestCase):
    def test_source_contract_authorizes_only_future_contract(self) -> None:
        sources = validate_historical_dispatch_authorization_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            sources["dec317_runtime_freeze_blob_sha"],
            "9626f6cd1c66a67d91dd3acf743e120ea8d2e9c0",
        )

        report = build_historical_dispatch_authorization_contract(
            repository_root=Path("."),
            runtime_freeze=_runtime_freeze(),
        )
        self.assertEqual(report["decision"], "DEC-318")
        self.assertEqual(
            report["stage"],
            "EXP062_ONE_SHOT_HISTORICAL_DISPATCH_SOURCE_AUTHORIZED_RUNTIME_LOCKED",
        )
        self.assertTrue(report["one_shot_dispatch_source_authorized"])
        self.assertFalse(report["historical_result_dispatch_authorized"])
        self.assertFalse(report["historical_executor_available"])
        self.assertFalse(report["historical_result_slot_consumed"])
        self.assertTrue(report["historical_result_slot_verified_available"])
        self.assertEqual(report["expected_target_run_number"], 2)
        self.assertEqual(report["expected_target_run_attempt"], 1)
        self.assertFalse(report["reserved_robustness_access_authorized"])
        self.assertFalse(report["demo_order_authorized"])
        self.assertFalse(report["live_order_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_public_constants_keep_runtime_locked(self) -> None:
        self.assertTrue(ONE_SHOT_DISPATCH_SOURCE_AUTHORIZED)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTOR_AVAILABLE)

    def test_runtime_freeze_fingerprint_drift_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["runtime_freeze_fingerprint_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            build_historical_dispatch_authorization_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )

    def test_consumed_slot_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["historical_result_slot_consumed"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_slot_consumed mismatch",
        ):
            build_historical_dispatch_authorization_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )

    def test_dispatch_authority_escalation_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["historical_result_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_dispatch_authorized mismatch",
        ):
            build_historical_dispatch_authorization_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )

    def test_target_run_drift_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["expected_target_run_number"] = 3
        with self.assertRaisesRegex(
            ValueError,
            "expected_target_run_number mismatch",
        ):
            build_historical_dispatch_authorization_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )


if __name__ == "__main__":
    unittest.main()
