from __future__ import annotations

import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_install_action_contract import (
    ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_ACTION_CONTRACT_SOURCE_AUTHORIZED,
    DEC416_RUNTIME_FREEZE_FINGERPRINT_SHA256,
    HISTORICAL_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED,
    HISTORICAL_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    build_active_one_shot_historical_executor_workflow_install_action_contract,
    validate_active_one_shot_historical_executor_workflow_install_action_contract_sources,
)


_RUNTIME_FREEZE_JSON = r"""{
  "active_install_final_authorization_preflight_canonical_sha256": "cca954fa188bf34ed308668563de0fa58226e50e242e65b0b33fac581dc5290c",
  "active_install_final_authorization_preflight_proof_artifact_digest": "sha256:8303140ebc7a5e37922080051ab634bc7a6c9f13940d52f3802b1017fd658c7a",
  "active_install_final_authorization_preflight_proof_artifact_id": 11058592607,
  "active_install_final_authorization_preflight_proof_artifact_name": "exp062-dec413-active-one-shot-historical-executor-workflow-install-final-authorization-preflight-8c7598348ade4ed8ea23458eef958add378c3e6d",
  "active_install_final_authorization_preflight_proof_artifact_zip_sha256": "8303140ebc7a5e37922080051ab634bc7a6c9f13940d52f3802b1017fd658c7a",
  "active_install_final_authorization_preflight_proof_head_sha": "8c7598348ade4ed8ea23458eef958add378c3e6d",
  "active_install_final_authorization_preflight_proof_job_id": 109592333745,
  "active_install_final_authorization_preflight_proof_run_attempt": 1,
  "active_install_final_authorization_preflight_proof_run_conclusion": "success",
  "active_install_final_authorization_preflight_proof_run_id": 36622849087,
  "active_install_final_authorization_preflight_proof_run_number": 1,
  "active_install_final_authorization_preflight_raw_sha256": "c265d3b6f1d9cc60946438d8fd7bd6d96ad4c976133293558ce0df548a09f730",
  "active_one_shot_historical_executor_workflow_install_activation_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_authorization_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_decision_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_execution_authorization_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_execution_contract_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_final_authorization_contract_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_source_authorized": true,
  "broker_mutation_authorized": false,
  "candidate_compilation_authorized": false,
  "dec334_terminal_review_contract_blob_sha": "fda2a45f74b101303467cf7b8527bec1bfc5e168",
  "dec334_terminal_review_decision": "DEC-334",
  "dec334_terminal_review_version": "fmp-exp062-historical-terminal-review-contract-v1",
  "dec414_review_decision": "DEC-414",
  "dec414_review_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-final-authorization-preflight-proof-review-v1",
  "dec414_reviewer_blob_sha": "331ebd4e6871bbf3dc81df3c76b40b5831048736",
  "dec415_freeze_builder_blob_sha": "1c5e61ae1602e249c3888e8fa58532cb81fef1aa",
  "dec415_freeze_decision": "DEC-415",
  "dec415_freeze_fingerprint_sha256": "4a71a6b29ccea4d5415ce64ca84fc0c43988a2daf98cbe912f4654868b907ffa",
  "dec415_freeze_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-final-authorization-preflight-proof-freeze-v1",
  "decision": "DEC-416",
  "demo_order_authorized": false,
  "discovery_result_authorized": true,
  "dormant_executor_workflow_template_blob_sha": "51ce87584369be957482460d81649adb1cb9f05d",
  "executor_workflow_path_exists": false,
  "expected_executor_workflow_path": ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml",
  "expected_target_run_attempt": 1,
  "expected_target_run_number": 2,
  "historical_discovery_execution_authorized": true,
  "historical_execute_mode_available": false,
  "historical_executor_available": false,
  "historical_executor_workflow_install_authorized": false,
  "historical_executor_workflow_installed": false,
  "historical_gate_proof_run_id": 36358289723,
  "historical_result_attempt_count": 0,
  "historical_result_dispatch_authorized": false,
  "historical_result_slot_consumed": false,
  "historical_result_slot_verified_available": true,
  "live_order_authorized": false,
  "next_gate": "SOURCE_ONLY_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_ACTION_CONTRACT_BEFORE_INSTALL",
  "phase8b_authorized": false,
  "promotion_authorized": false,
  "real_money_authorized": false,
  "replacement_run_authorized": false,
  "rerun_authorized": false,
  "reserved_robustness_access_authorized": false,
  "retry_authorized": false,
  "review_source_blobs": {
    "active_discovery_workflow": "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50",
    "dec411_final_authorization_contract": "30493981eb2e5663e1fe620026c2c0af0cc03dd9",
    "dec412_preflight": "89c6a606703ce72916451e0168e1b58bb765baaa",
    "dec412_preflight_cli": "6ab0b9bbecec471cfabc67b50906b2213626296b",
    "dec413_workflow": "dace2b0752937b2d15349f5564b88ed9aea82bf1",
    "dormant_executor_workflow_template": "51ce87584369be957482460d81649adb1cb9f05d"
  },
  "runtime_freeze_fingerprint_sha256": "3f90062e42cc36c61286b31fcd625a7e511140819c19f268e283be1807e2f0c7",
  "stage": "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT_PROOF_RUNTIME_EVIDENCE_BOUND_AND_FROZEN",
  "trading_authorized": false,
  "version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-final-authorization-preflight-proof-runtime-freeze-v1"
}"""


def _runtime_freeze() -> dict[str, object]:
    value = json.loads(_RUNTIME_FREEZE_JSON)
    assert isinstance(value, dict)
    return value


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallActionContractTests(
    unittest.TestCase
):
    def test_contract_authorizes_only_action_contract_source(self) -> None:
        source = (
            validate_active_one_shot_historical_executor_workflow_install_action_contract_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            source["dec416_runtime_freeze"],
            "1a4accb526aa5e0657ea9ad953fe2cefd564d8be",
        )

        report = build_active_one_shot_historical_executor_workflow_install_action_contract(
            repository_root=Path("."),
            runtime_freeze=_runtime_freeze(),
        )
        self.assertEqual(report["decision"], "DEC-417")
        self.assertEqual(
            report["stage"],
            (
                "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "ACTION_CONTRACT_SOURCE_AUTHORIZED_INSTALL_LOCKED"
            ),
        )
        for field in (
            "active_one_shot_historical_executor_workflow_install_authorization_source_authorized",
            "active_one_shot_historical_executor_workflow_install_decision_source_authorized",
            "active_one_shot_historical_executor_workflow_install_execution_authorization_source_authorized",
            "active_one_shot_historical_executor_workflow_install_execution_contract_source_authorized",
            "active_one_shot_historical_executor_workflow_install_activation_source_authorized",
            "active_one_shot_historical_executor_workflow_install_source_authorized",
            "active_one_shot_historical_executor_workflow_install_final_authorization_contract_source_authorized",
            "active_one_shot_historical_executor_workflow_install_action_contract_source_authorized",
        ):
            self.assertTrue(report[field], field)

        self.assertFalse(report["historical_executor_workflow_install_authorized"])
        self.assertFalse(report["historical_executor_workflow_installed"])
        self.assertFalse(report["historical_executor_available"])
        self.assertFalse(report["historical_result_dispatch_authorized"])
        self.assertFalse(report["historical_execute_mode_available"])
        self.assertFalse(report["historical_result_slot_consumed"])
        self.assertTrue(report["historical_result_slot_verified_available"])
        self.assertEqual(report["expected_target_run_number"], 2)
        self.assertEqual(report["expected_target_run_attempt"], 1)
        self.assertFalse(report["trading_authorized"])
        self.assertEqual(
            report["next_gate"],
            (
                "READ_ONLY_CURRENT_MAIN_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
                "WORKFLOW_INSTALL_ACTION_PREFLIGHT"
            ),
        )

    def test_public_constants_keep_install_locked(self) -> None:
        self.assertTrue(
            ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_ACTION_CONTRACT_SOURCE_AUTHORIZED
        )
        self.assertFalse(HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED)
        self.assertFalse(HISTORICAL_EXECUTOR_AVAILABLE)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTE_MODE_AVAILABLE)
        self.assertEqual(
            DEC416_RUNTIME_FREEZE_FINGERPRINT_SHA256,
            "3f90062e42cc36c61286b31fcd625a7e511140819c19f268e283be1807e2f0c7",
        )

    def test_runtime_freeze_fingerprint_drift_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["runtime_freeze_fingerprint_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            build_active_one_shot_historical_executor_workflow_install_action_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )

    def test_final_authorization_evidence_drift_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["active_install_final_authorization_preflight_proof_run_id"] = 1
        with self.assertRaisesRegex(
            ValueError,
            "active_install_final_authorization_preflight_proof_run_id mismatch",
        ):
            build_active_one_shot_historical_executor_workflow_install_action_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )

    def test_install_authority_escalation_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["historical_executor_workflow_install_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_workflow_install_authorized",
        ):
            build_active_one_shot_historical_executor_workflow_install_action_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )


if __name__ == "__main__":
    unittest.main()
