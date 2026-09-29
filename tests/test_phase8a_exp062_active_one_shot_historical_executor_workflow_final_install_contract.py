from __future__ import annotations

import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_final_install_contract import (
    ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_FINAL_INSTALL_CONTRACT_SOURCE_AUTHORIZED,
    DEC395_RUNTIME_FREEZE_FINGERPRINT_SHA256,
    HISTORICAL_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED,
    HISTORICAL_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    build_active_one_shot_historical_executor_workflow_final_install_contract,
    validate_active_one_shot_historical_executor_workflow_final_install_contract_sources,
)


_RUNTIME_FREEZE_JSON = r"""{
  "decision": "DEC-395",
  "version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-execution-preflight-proof-runtime-freeze-v1",
  "stage": "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_PREFLIGHT_PROOF_RUNTIME_EVIDENCE_BOUND_AND_FROZEN",
  "active_install_execution_preflight_proof_head_sha": "dc1a2cfd5a11595f2ad943277f79e043625bd3e9",
  "active_install_execution_preflight_proof_run_id": 36568114050,
  "active_install_execution_preflight_proof_run_number": 1,
  "active_install_execution_preflight_proof_run_attempt": 1,
  "active_install_execution_preflight_proof_run_conclusion": "success",
  "active_install_execution_preflight_proof_job_id": 109405007879,
  "active_install_execution_preflight_proof_artifact_id": 11032917944,
  "active_install_execution_preflight_proof_artifact_name": "exp062-dec392-active-one-shot-historical-executor-workflow-install-execution-preflight-dc1a2cfd5a11595f2ad943277f79e043625bd3e9",
  "active_install_execution_preflight_proof_artifact_digest": "sha256:f8119b5845f9ba824caebaa48012d19f41668767b71773d94d305f4f78f5c103",
  "active_install_execution_preflight_proof_artifact_zip_sha256": "f8119b5845f9ba824caebaa48012d19f41668767b71773d94d305f4f78f5c103",
  "active_install_execution_preflight_raw_sha256": "a9fd545df8c2dc2f05813df5e827f5e9685d5c7c6ea521ca07b6a709ca188601",
  "active_install_execution_preflight_canonical_sha256": "bd91ae808a6ed1fdc24c4fb5b64b8744a13a53fbe3a6d58d0f5062ba26eea78b",
  "dec393_review_decision": "DEC-393",
  "dec393_review_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-execution-preflight-proof-review-v1",
  "dec394_freeze_decision": "DEC-394",
  "dec394_freeze_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-execution-preflight-proof-freeze-v1",
  "dec394_freeze_fingerprint_sha256": "9357b1c6591a801237acacf7cb7eab1f5302608770ad7b3033566bda39cb3548",
  "dec334_terminal_review_decision": "DEC-334",
  "dec334_terminal_review_version": "fmp-exp062-historical-terminal-review-contract-v1",
  "dec393_reviewer_blob_sha": "2c96854c6dd8197ef457485bf6b5450cae1341ad",
  "dec394_freeze_builder_blob_sha": "42dcc4b124b968164ccdf384e1ec46f780c16cdc",
  "dec334_terminal_review_contract_blob_sha": "fda2a45f74b101303467cf7b8527bec1bfc5e168",
  "review_source_blobs": {
    "dec392_workflow": "cf6003478eb0a4a7a5dbe11d03a7c5dae1d3b9ac",
    "dec391_preflight": "d3f38e26b71ff09590cc4c76632c9fbfa30e45a3",
    "dec391_preflight_cli": "4871c17989845989bb29f03015a81e0187ffa994",
    "dec390_install_execution_contract": "a48fc70ae1c40e32dbba7fc24922c92b6051fd1e",
    "dormant_executor_workflow_template": "51ce87584369be957482460d81649adb1cb9f05d",
    "active_discovery_workflow": "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
  },
  "dormant_executor_workflow_template_blob_sha": "51ce87584369be957482460d81649adb1cb9f05d",
  "expected_executor_workflow_path": ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml",
  "executor_workflow_path_exists": false,
  "historical_gate_proof_run_id": 36358289723,
  "historical_result_attempt_count": 0,
  "historical_result_slot_consumed": false,
  "historical_result_slot_verified_available": true,
  "expected_target_run_number": 2,
  "expected_target_run_attempt": 1,
  "active_one_shot_historical_executor_workflow_install_authorization_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_decision_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_execution_authorization_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_execution_contract_source_authorized": true,
  "historical_executor_workflow_install_authorized": false,
  "historical_executor_workflow_installed": false,
  "historical_executor_available": false,
  "historical_result_dispatch_authorized": false,
  "historical_execute_mode_available": false,
  "historical_discovery_execution_authorized": true,
  "discovery_result_authorized": true,
  "rerun_authorized": false,
  "retry_authorized": false,
  "replacement_run_authorized": false,
  "reserved_robustness_access_authorized": false,
  "candidate_compilation_authorized": false,
  "promotion_authorized": false,
  "phase8b_authorized": false,
  "demo_order_authorized": false,
  "broker_mutation_authorized": false,
  "live_order_authorized": false,
  "real_money_authorized": false,
  "trading_authorized": false,
  "next_gate": "SOURCE_ONLY_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_CONTRACT",
  "runtime_freeze_fingerprint_sha256": "9c44d78327d4467d4eb0717ae28d410f2543476b518eeecfea9bb2db9ba2682c"
}"""


def _runtime_freeze() -> dict[str, object]:
    value = json.loads(_RUNTIME_FREEZE_JSON)
    assert isinstance(value, dict)
    return value


class Exp062ActiveOneShotHistoricalExecutorWorkflowFinalInstallContractTests(
    unittest.TestCase
):
    def test_contract_authorizes_only_final_install_contract_source(self) -> None:
        source = validate_active_one_shot_historical_executor_workflow_final_install_contract_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["dec395_runtime_freeze"],
            "a941ec672cc5249401f4208435f0de3c6e6f6a4c",
        )

        report = build_active_one_shot_historical_executor_workflow_final_install_contract(
            repository_root=Path("."),
            runtime_freeze=_runtime_freeze(),
        )
        self.assertEqual(report["decision"], "DEC-396")
        self.assertEqual(
            report["stage"],
            (
                "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_"
                "FINAL_INSTALL_CONTRACT_SOURCE_AUTHORIZED_ACTIVE_WORKFLOW_ABSENT"
            ),
        )
        for field in (
            "active_one_shot_historical_executor_workflow_install_authorization_source_authorized",
            "active_one_shot_historical_executor_workflow_install_decision_source_authorized",
            "active_one_shot_historical_executor_workflow_install_execution_authorization_source_authorized",
            "active_one_shot_historical_executor_workflow_install_execution_contract_source_authorized",
            "active_one_shot_historical_executor_workflow_final_install_contract_source_authorized",
        ):
            self.assertTrue(report[field], field)

        for field in (
            "historical_executor_workflow_install_authorized",
            "historical_executor_workflow_installed",
            "historical_executor_available",
            "historical_result_dispatch_authorized",
            "historical_execute_mode_available",
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

        self.assertFalse(report["historical_result_slot_consumed"])
        self.assertTrue(report["historical_result_slot_verified_available"])
        self.assertEqual(report["expected_target_run_number"], 2)
        self.assertEqual(report["expected_target_run_attempt"], 1)
        self.assertEqual(
            report["next_gate"],
            (
                "READ_ONLY_CURRENT_MAIN_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
                "WORKFLOW_FINAL_INSTALL_PREFLIGHT"
            ),
        )

    def test_public_constants_keep_install_locked(self) -> None:
        self.assertTrue(
            ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_FINAL_INSTALL_CONTRACT_SOURCE_AUTHORIZED
        )
        self.assertFalse(HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED)
        self.assertFalse(HISTORICAL_EXECUTOR_AVAILABLE)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTE_MODE_AVAILABLE)
        self.assertEqual(
            DEC395_RUNTIME_FREEZE_FINGERPRINT_SHA256,
            "9c44d78327d4467d4eb0717ae28d410f2543476b518eeecfea9bb2db9ba2682c",
        )

    def test_runtime_freeze_fingerprint_drift_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["runtime_freeze_fingerprint_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            build_active_one_shot_historical_executor_workflow_final_install_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )

    def test_install_authority_escalation_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["historical_executor_workflow_install_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_workflow_install_authorized mismatch",
        ):
            build_active_one_shot_historical_executor_workflow_final_install_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )


if __name__ == "__main__":
    unittest.main()
