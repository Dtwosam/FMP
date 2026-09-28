from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_one_shot_executor_source import (
    DEC336_RUNTIME_FREEZE_FINGERPRINT_SHA256,
    EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_DECISION,
    build_one_shot_historical_executor_source_contract,
    validate_one_shot_historical_executor_source_dependencies,
)


HEAD = "a" * 40


def _runtime_freeze() -> dict[str, object]:
    return {
        "decision": "DEC-336",
        "version": (
            "fmp-exp062-historical-executor-activation-preflight-"
            "runtime-freeze-v1"
        ),
        "stage": (
            "EXP062_HISTORICAL_EXECUTOR_ACTIVATION_PREFLIGHT_"
            "RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "activation_preflight_proof_head_sha": (
            "12d11320ae302902df0a0deb7343408922deee83"
        ),
        "activation_preflight_proof_run_id": 36431469794,
        "activation_preflight_proof_run_number": 1,
        "activation_preflight_proof_run_attempt": 1,
        "activation_preflight_proof_run_conclusion": "success",
        "activation_preflight_proof_job_id": 108958446980,
        "activation_preflight_proof_artifact_id": 10973597441,
        "activation_preflight_proof_artifact_name": (
            "exp062-dec332-historical-executor-activation-preflight-"
            "12d11320ae302902df0a0deb7343408922deee83"
        ),
        "activation_preflight_proof_artifact_digest": (
            "sha256:ee6e7ac2e8c18e1f8d276bba14ca942e20615143316ac185f4b814333804c2d5"
        ),
        "activation_preflight_proof_artifact_zip_sha256": (
            "ee6e7ac2e8c18e1f8d276bba14ca942e20615143316ac185f4b814333804c2d5"
        ),
        "activation_preflight_raw_sha256": (
            "775010a0c3d4afe11191adb53d8ad54e7cf0d5de85b1a0b5adcb28c470e9a4a5"
        ),
        "activation_preflight_canonical_sha256": (
            "98b9180ae3b438b3c372ba34cbab9473d7f38ba5c1eb1add2dee988df4e09ad8"
        ),
        "dec333_review_decision": "DEC-333",
        "dec333_review_version": (
            "fmp-exp062-historical-executor-activation-preflight-"
            "proof-review-v1"
        ),
        "dec334_terminal_review_decision": "DEC-334",
        "dec334_terminal_review_version": (
            "fmp-exp062-historical-terminal-review-contract-v1"
        ),
        "dec335_freeze_decision": "DEC-335",
        "dec335_freeze_version": (
            "fmp-exp062-reviewed-historical-executor-activation-"
            "preflight-freeze-v1"
        ),
        "dec335_freeze_fingerprint_sha256": (
            "567320a598f245a8e7521281ddde3a1acaa0e3f294aebe12554688d2258f020b"
        ),
        "dec333_reviewer_blob_sha": (
            "c540fb14c7048de2e6f368b0c96b51715c83e9a5"
        ),
        "dec334_terminal_review_contract_blob_sha": (
            "fda2a45f74b101303467cf7b8527bec1bfc5e168"
        ),
        "dec335_freeze_builder_blob_sha": (
            "9cb660f06fc9da8a8d4927d8ff953413a6df13fe"
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
        "one_shot_executor_activation_source_authorized": True,
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
            "SOURCE_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_BEFORE_DISPATCH"
        ),
        "runtime_freeze_fingerprint_sha256": (
            DEC336_RUNTIME_FREEZE_FINGERPRINT_SHA256
        ),
    }


def _preflight() -> dict[str, object]:
    return {
        "decision": "DEC-331",
        "version": (
            "fmp-exp062-historical-executor-activation-preflight-v1"
        ),
        "activation_contract_decision": "DEC-330",
        "activation_contract_version": (
            "fmp-exp062-historical-executor-activation-contract-v1"
        ),
        "dec330_activation_contract_blob_sha": (
            "35edfdfed85e52ebd723f2637060f4f102e7920b"
        ),
        "expected_head_sha": HEAD,
        "stage": (
            "EXP062_ONE_SHOT_EXECUTOR_ACTIVATION_PREFLIGHT_SLOT_AVAILABLE"
        ),
        "proof_run_id": 36358289723,
        "proof_run_count": 1,
        "historical_result_attempt_count": 0,
        "historical_result_run_id": None,
        "historical_result_run_status": None,
        "historical_result_run_conclusion": None,
        "historical_result_slot_consumed": False,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "one_shot_executor_activation_source_authorized": True,
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
            "REPOSITORY_HOSTED_READ_ONLY_EXECUTOR_ACTIVATION_PREFLIGHT_PROOF"
        ),
    }


class Exp062OneShotHistoricalExecutorSourceTests(unittest.TestCase):
    def test_source_dependency_pins_dec336(self) -> None:
        result = validate_one_shot_historical_executor_source_dependencies(
            repository_root=Path("."),
        )
        self.assertEqual(
            result["dec336_runtime_freeze_blob_sha"],
            "9673e115eeb373c4881d36a8b5d91a2801cd8ad1",
        )

    def test_valid_sources_authorize_source_only_not_dispatch(self) -> None:
        value = build_one_shot_historical_executor_source_contract(
            repository_root=Path("."),
            runtime_freeze=_runtime_freeze(),
            fresh_activation_preflight=_preflight(),
            expected_head_sha=HEAD,
        )
        self.assertEqual(
            value["decision"],
            EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_DECISION,
        )
        self.assertEqual(
            value["stage"],
            (
                "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_AUTHORIZED_"
                "RUNTIME_DISPATCH_LOCKED"
            ),
        )
        self.assertTrue(
            value["one_shot_historical_executor_source_authorized"]
        )
        self.assertFalse(value["historical_executor_available"])
        self.assertFalse(value["historical_result_dispatch_authorized"])
        self.assertFalse(value["historical_execute_mode_available"])
        self.assertEqual(value["expected_target_run_number"], 2)
        self.assertEqual(value["expected_target_run_attempt"], 1)
        self.assertFalse(value["historical_result_slot_consumed"])
        self.assertFalse(value["candidate_compilation_authorized"])
        self.assertFalse(value["demo_order_authorized"])
        self.assertFalse(value["live_order_authorized"])
        self.assertFalse(value["trading_authorized"])

    def test_runtime_freeze_drift_is_rejected(self) -> None:
        runtime = _runtime_freeze()
        runtime["activation_preflight_proof_run_id"] += 1
        with self.assertRaisesRegex(
            ValueError,
            "runtime freeze activation_preflight_proof_run_id mismatch",
        ):
            build_one_shot_historical_executor_source_contract(
                repository_root=Path("."),
                runtime_freeze=runtime,
                fresh_activation_preflight=_preflight(),
                expected_head_sha=HEAD,
            )

    def test_consumed_slot_is_rejected(self) -> None:
        preflight = _preflight()
        preflight["stage"] = (
            "EXP062_ONE_SHOT_EXECUTOR_ACTIVATION_PREFLIGHT_"
            "SLOT_CONSUMED_REVIEW_REQUIRED"
        )
        preflight["historical_result_attempt_count"] = 1
        preflight["historical_result_slot_consumed"] = True
        preflight["historical_result_run_id"] = 40000000000
        preflight["historical_result_run_status"] = "completed"
        preflight["historical_result_run_conclusion"] = "success"
        preflight["planned_dispatch_command"] = None
        with self.assertRaisesRegex(
            ValueError,
            "fresh preflight stage mismatch",
        ):
            build_one_shot_historical_executor_source_contract(
                repository_root=Path("."),
                runtime_freeze=_runtime_freeze(),
                fresh_activation_preflight=preflight,
                expected_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
