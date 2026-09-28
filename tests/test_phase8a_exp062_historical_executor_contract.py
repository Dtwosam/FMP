from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_executor_contract import (
    HISTORICAL_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    ONE_SHOT_EXECUTOR_SOURCE_AUTHORIZED,
    build_historical_executor_contract,
    validate_historical_executor_contract_sources,
)


def _runtime_freeze() -> dict[str, object]:
    return {
        "decision": "DEC-323",
        "version": "fmp-exp062-historical-dispatch-runtime-freeze-v1",
        "stage": (
            "EXP062_HISTORICAL_DISPATCH_PLAN_RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "dispatch_plan_proof_head_sha": (
            "fee1a78168254e7e8fecc104859d1a231b727243"
        ),
        "dispatch_plan_proof_run_id": 36418793172,
        "dispatch_plan_proof_run_number": 1,
        "dispatch_plan_proof_run_attempt": 1,
        "dispatch_plan_proof_run_conclusion": "success",
        "dispatch_plan_proof_job_id": 108916232597,
        "dispatch_plan_proof_artifact_id": 10967344018,
        "dispatch_plan_proof_artifact_name": (
            "exp062-dec320-historical-dispatch-plan-"
            "fee1a78168254e7e8fecc104859d1a231b727243"
        ),
        "dispatch_plan_proof_artifact_digest": (
            "sha256:ca0f1156fab234327bbcdd9c3150cb7904ed6def230f035019b2139c4c523adf"
        ),
        "dispatch_plan_proof_artifact_zip_sha256": (
            "ca0f1156fab234327bbcdd9c3150cb7904ed6def230f035019b2139c4c523adf"
        ),
        "dispatch_plan_raw_sha256": (
            "a6fa5f3a7f3f45df5d64efe1661a5b17887f88fded31e1cbb1620df5b18a95d1"
        ),
        "dispatch_plan_canonical_sha256": (
            "41ca6c710d8750851350c2108b42970501a5efa14481cff61e2a66877ee90f6d"
        ),
        "dec321_review_decision": "DEC-321",
        "dec321_review_version": (
            "fmp-exp062-historical-dispatch-plan-proof-review-v1"
        ),
        "dec322_freeze_decision": "DEC-322",
        "dec322_freeze_version": (
            "fmp-exp062-reviewed-historical-dispatch-plan-freeze-v1"
        ),
        "dec322_freeze_fingerprint_sha256": (
            "b7d3e5461511c8e14dd4402028ad24daefcf431cece3b59575588ba915db510e"
        ),
        "dec321_reviewer_blob_sha": (
            "8dee8008204ed816df211861ff4a7fb9e952d781"
        ),
        "dec322_freeze_builder_blob_sha": (
            "6b7ab36c939fca7a9d53569e4617ebe6584e5b7c"
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
        "one_shot_dispatch_source_authorized": True,
        "historical_result_dispatch_authorized": False,
        "historical_executor_available": False,
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
        "next_gate": "SOURCE_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_CONTRACT",
        "runtime_freeze_fingerprint_sha256": (
            "d412cc0fe115f7c10da6b0cfee092de718539ade041c8476659f6c30f8adc8c3"
        ),
    }


class Exp062HistoricalExecutorContractTests(unittest.TestCase):
    def test_contract_authorizes_source_only(self) -> None:
        source = validate_historical_executor_contract_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["dec323_runtime_freeze_blob_sha"],
            "44815c9ff23fcd022346558e8c043673154ca0b3",
        )

        report = build_historical_executor_contract(
            repository_root=Path("."),
            runtime_freeze=_runtime_freeze(),
        )
        self.assertEqual(report["decision"], "DEC-324")
        self.assertEqual(
            report["stage"],
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_AUTHORIZED_RUNTIME_LOCKED",
        )
        self.assertTrue(report["one_shot_executor_source_authorized"])
        self.assertFalse(report["historical_executor_available"])
        self.assertFalse(report["historical_result_dispatch_authorized"])
        self.assertFalse(report["historical_execute_mode_available"])
        self.assertFalse(report["historical_result_slot_consumed"])
        self.assertTrue(report["historical_result_slot_verified_available"])
        self.assertEqual(report["expected_target_run_number"], 2)
        self.assertEqual(report["expected_target_run_attempt"], 1)
        self.assertFalse(report["reserved_robustness_access_authorized"])
        self.assertFalse(report["demo_order_authorized"])
        self.assertFalse(report["live_order_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_public_constants_keep_runtime_locked(self) -> None:
        self.assertTrue(ONE_SHOT_EXECUTOR_SOURCE_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTOR_AVAILABLE)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTE_MODE_AVAILABLE)

    def test_runtime_freeze_fingerprint_drift_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["runtime_freeze_fingerprint_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            build_historical_executor_contract(
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
            build_historical_executor_contract(
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
            build_historical_executor_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )

    def test_executor_availability_escalation_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["historical_executor_available"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_available mismatch",
        ):
            build_historical_executor_contract(
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
            build_historical_executor_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )


if __name__ == "__main__":
    unittest.main()
