from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_one_shot_executor_workflow_install_contract import (
    EXPECTED_EXECUTOR_WORKFLOW_PATH,
    HISTORICAL_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED,
    HISTORICAL_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_AUTHORIZED,
    build_one_shot_historical_executor_workflow_install_contract,
    validate_one_shot_historical_executor_workflow_install_contract_sources,
)


def _runtime_freeze() -> dict[str, object]:
    return {
        "decision": "DEC-347",
        "version": (
            "fmp-exp062-one-shot-historical-executor-workflow-preflight-"
            "proof-runtime-freeze-v1"
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_PREFLIGHT_PROOF_"
            "RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "workflow_preflight_proof_head_sha": (
            "c43a1701cadd57c25903d3b637f2af70b28d1065"
        ),
        "workflow_preflight_proof_run_id": 36455684780,
        "workflow_preflight_proof_run_number": 1,
        "workflow_preflight_proof_run_attempt": 1,
        "workflow_preflight_proof_run_conclusion": "success",
        "workflow_preflight_proof_job_id": 109041310360,
        "workflow_preflight_proof_artifact_id": 10984953455,
        "workflow_preflight_proof_artifact_name": (
            "exp062-dec344-one-shot-historical-executor-workflow-preflight-"
            "c43a1701cadd57c25903d3b637f2af70b28d1065"
        ),
        "workflow_preflight_proof_artifact_digest": (
            "sha256:eec64c9bb1f6688dca010825e83e191c6a423d21bf6522396d7f650ec2db675f"
        ),
        "workflow_preflight_proof_artifact_zip_sha256": (
            "eec64c9bb1f6688dca010825e83e191c6a423d21bf6522396d7f650ec2db675f"
        ),
        "workflow_preflight_raw_sha256": (
            "56981ba62638129f39693239d22b76c65cb3a8e0b236741b3a80984137c2c0d7"
        ),
        "workflow_preflight_canonical_sha256": (
            "d6bf96a73b1377ad65887c6ba001c2c2d39812d58205e59e304c1c88e3ef22dc"
        ),
        "dec345_review_decision": "DEC-345",
        "dec345_review_version": (
            "fmp-exp062-one-shot-historical-executor-workflow-"
            "preflight-proof-review-v1"
        ),
        "dec346_freeze_decision": "DEC-346",
        "dec346_freeze_version": (
            "fmp-exp062-one-shot-historical-executor-workflow-"
            "preflight-proof-freeze-v1"
        ),
        "dec346_freeze_fingerprint_sha256": (
            "3ba4b6aba0cafab3989c1f20536ad36603786efdcef49964a31bc99b73a79988"
        ),
        "dec334_terminal_review_decision": "DEC-334",
        "dec334_terminal_review_version": (
            "fmp-exp062-historical-terminal-review-contract-v1"
        ),
        "dec345_reviewer_blob_sha": (
            "ebd5bc2943675ba4276374cf339aa120aaf3b257"
        ),
        "dec346_freeze_builder_blob_sha": (
            "02b294aea02932a465913f6e5ed993e2cb45d441"
        ),
        "dec334_terminal_review_contract_blob_sha": (
            "fda2a45f74b101303467cf7b8527bec1bfc5e168"
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
        "one_shot_historical_executor_source_authorized": True,
        "one_shot_historical_executor_workflow_source_authorized": True,
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
            "SOURCE_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_CONTRACT"
        ),
        "runtime_freeze_fingerprint_sha256": (
            "b714ceec4a30fde0693db5c21eab2ce62d7a63c1c724c55321bc8cb13b423e03"
        ),
    }


class Exp062OneShotHistoricalExecutorWorkflowInstallContractTests(
    unittest.TestCase
):
    def test_contract_authorizes_install_source_only(self) -> None:
        source = (
            validate_one_shot_historical_executor_workflow_install_contract_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            source["dec347_runtime_freeze_blob_sha"],
            "4781dae661a78d7b50e2070e87b8d7e34ea49f3c",
        )

        report = build_one_shot_historical_executor_workflow_install_contract(
            repository_root=Path("."),
            runtime_freeze=_runtime_freeze(),
        )
        self.assertEqual(report["decision"], "DEC-348")
        self.assertEqual(
            report["stage"],
            (
                "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "SOURCE_AUTHORIZED_RUNTIME_LOCKED"
            ),
        )
        self.assertEqual(
            report["expected_executor_workflow_path"],
            EXPECTED_EXECUTOR_WORKFLOW_PATH,
        )
        self.assertTrue(
            report[
                "one_shot_historical_executor_workflow_install_source_authorized"
            ]
        )
        self.assertFalse(report["historical_executor_workflow_installed"])
        self.assertFalse(report["historical_executor_available"])
        self.assertFalse(report["historical_result_dispatch_authorized"])
        self.assertFalse(report["historical_execute_mode_available"])
        self.assertFalse(report["historical_result_slot_consumed"])
        self.assertTrue(report["historical_result_slot_verified_available"])
        self.assertEqual(report["expected_target_run_number"], 2)
        self.assertEqual(report["expected_target_run_attempt"], 1)
        self.assertFalse(report["demo_order_authorized"])
        self.assertFalse(report["live_order_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_public_constants_keep_runtime_locked(self) -> None:
        self.assertTrue(
            ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_AUTHORIZED
        )
        self.assertFalse(HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED)
        self.assertFalse(HISTORICAL_EXECUTOR_AVAILABLE)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTE_MODE_AVAILABLE)

    def test_runtime_freeze_fingerprint_drift_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["runtime_freeze_fingerprint_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            build_one_shot_historical_executor_workflow_install_contract(
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
            build_one_shot_historical_executor_workflow_install_contract(
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
            build_one_shot_historical_executor_workflow_install_contract(
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
            build_one_shot_historical_executor_workflow_install_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )


if __name__ == "__main__":
    unittest.main()
