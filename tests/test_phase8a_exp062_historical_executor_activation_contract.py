from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_executor_activation_contract import (
    HISTORICAL_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    ONE_SHOT_EXECUTOR_ACTIVATION_SOURCE_AUTHORIZED,
    build_historical_executor_activation_contract,
    validate_historical_executor_activation_contract_sources,
)


def _runtime_freeze() -> dict[str, object]:
    return {
        "decision": "DEC-329",
        "version": (
            "fmp-exp062-historical-executor-preflight-runtime-freeze-v1"
        ),
        "stage": (
            "EXP062_HISTORICAL_EXECUTOR_PREFLIGHT_RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "preflight_proof_head_sha": (
            "a811aacaae82e15b18267b6e4ba659054abb0341"
        ),
        "preflight_proof_run_id": 36422936991,
        "preflight_proof_run_number": 1,
        "preflight_proof_run_attempt": 1,
        "preflight_proof_run_conclusion": "success",
        "preflight_proof_job_id": 108929843306,
        "preflight_proof_artifact_id": 10970303347,
        "preflight_proof_artifact_name": (
            "exp062-dec326-historical-executor-preflight-"
            "a811aacaae82e15b18267b6e4ba659054abb0341"
        ),
        "preflight_proof_artifact_digest": (
            "sha256:fe116a7fff7ffdec27e787d3cd7981ac67772276efb12a5b434b04ee3855c74c"
        ),
        "preflight_proof_artifact_zip_sha256": (
            "fe116a7fff7ffdec27e787d3cd7981ac67772276efb12a5b434b04ee3855c74c"
        ),
        "preflight_raw_sha256": (
            "5dfa7800a8dcbe4537910690a0ba70b3c93467c685d7c5c99898d0b6d111f9d8"
        ),
        "preflight_canonical_sha256": (
            "9970dcbf44241a3b9ffc6aab01d8a3bab6749813f88d0771dee101ea640aec3d"
        ),
        "dec327_review_decision": "DEC-327",
        "dec327_review_version": (
            "fmp-exp062-historical-executor-preflight-proof-review-v1"
        ),
        "dec328_freeze_decision": "DEC-328",
        "dec328_freeze_version": (
            "fmp-exp062-reviewed-historical-executor-preflight-freeze-v1"
        ),
        "dec328_freeze_fingerprint_sha256": (
            "2e295d03066fcfa4dcea300c3f263bcf6a67cb96d6b356410821af493b2d5675"
        ),
        "dec327_reviewer_blob_sha": (
            "da3febc87e69a81f88088c0b34ba0650956d1873"
        ),
        "dec328_freeze_builder_blob_sha": (
            "ce37dd70c167182441b503c38b1197223917ff72"
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
        "one_shot_executor_source_authorized": True,
        "historical_executor_available": False,
        "historical_result_dispatch_authorized": False,
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
        "next_gate": (
            "SOURCE_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_ACTIVATION_CONTRACT"
        ),
        "runtime_freeze_fingerprint_sha256": (
            "5c4e081fca4848cf18f8ed03c68e5d7854723e92368eded03fb5e9b54756ab61"
        ),
    }


class Exp062HistoricalExecutorActivationContractTests(unittest.TestCase):
    def test_contract_authorizes_activation_source_only(self) -> None:
        source = validate_historical_executor_activation_contract_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["dec329_runtime_freeze_blob_sha"],
            "f9f727ae23b88fe52ca9c41739f04ab26bec0b4e",
        )

        report = build_historical_executor_activation_contract(
            repository_root=Path("."),
            runtime_freeze=_runtime_freeze(),
        )
        self.assertEqual(report["decision"], "DEC-330")
        self.assertEqual(
            report["stage"],
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_ACTIVATION_SOURCE_AUTHORIZED_RUNTIME_LOCKED",
        )
        self.assertTrue(
            report["one_shot_executor_activation_source_authorized"]
        )
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
        self.assertTrue(ONE_SHOT_EXECUTOR_ACTIVATION_SOURCE_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTOR_AVAILABLE)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTE_MODE_AVAILABLE)

    def test_runtime_freeze_fingerprint_drift_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["runtime_freeze_fingerprint_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            build_historical_executor_activation_contract(
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
            build_historical_executor_activation_contract(
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
            build_historical_executor_activation_contract(
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
            build_historical_executor_activation_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )


if __name__ == "__main__":
    unittest.main()
