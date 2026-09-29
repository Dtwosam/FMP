from __future__ import annotations

import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_install_final_authorization_contract import (
    ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_FINAL_AUTHORIZATION_CONTRACT_SOURCE_AUTHORIZED,
    DEC410_RUNTIME_FREEZE_FINGERPRINT_SHA256,
    HISTORICAL_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED,
    HISTORICAL_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    build_active_one_shot_historical_executor_workflow_install_final_authorization_contract,
    validate_active_one_shot_historical_executor_workflow_install_final_authorization_contract_sources,
)


_RUNTIME_FREEZE_JSON = r"""{
  "active_one_shot_historical_executor_workflow_install_activation_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_authorization_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_decision_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_execution_authorization_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_execution_contract_source_authorized": true,
  "active_one_shot_historical_executor_workflow_install_source_authorized": true,
  "broker_mutation_authorized": false,
  "candidate_compilation_authorized": false,
  "dec334_terminal_review_contract_blob_sha": "fda2a45f74b101303467cf7b8527bec1bfc5e168",
  "dec334_terminal_review_decision": "DEC-334",
  "dec334_terminal_review_version": "fmp-exp062-historical-terminal-review-contract-v1",
  "dec408_review_decision": "DEC-408",
  "dec408_review_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-source-preflight-proof-recovery-review-v1",
  "dec408_reviewer_blob_sha": "b7c28510824b234337318042d8bc8714b7a1c230",
  "dec409_freeze_builder_blob_sha": "18fdeb4700cb9233c66ed09dab81b8b61ce4272c",
  "dec409_freeze_decision": "DEC-409",
  "dec409_freeze_fingerprint_sha256": "c0c04735c57638fde0a57122c240ea6c9aacd86fc7e43cdc532aaf8ba54cd9d3",
  "dec409_freeze_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-source-preflight-proof-recovery-freeze-v1",
  "decision": "DEC-410",
  "demo_order_authorized": false,
  "discovery_result_authorized": true,
  "dormant_executor_workflow_template_blob_sha": "51ce87584369be957482460d81649adb1cb9f05d",
  "executor_workflow_path_exists": false,
  "expected_executor_workflow_path": ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml",
  "expected_target_run_attempt": 1,
  "expected_target_run_number": 2,
  "failed_proof_head_sha": "0db04ae49b3533778b08afa31e9ef9a26576b80c",
  "failed_proof_job_id": 109561121322,
  "failed_proof_run_attempt": 1,
  "failed_proof_run_conclusion": "failure",
  "failed_proof_run_id": 36613664506,
  "failed_proof_run_number": 1,
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
  "next_gate": "SOURCE_ONLY_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_FINAL_AUTHORIZATION_CONTRACT_BEFORE_INSTALL",
  "phase8b_authorized": false,
  "promotion_authorized": false,
  "real_money_authorized": false,
  "recovery_preflight_canonical_sha256": "4f96d9df7e7e4fba224a376b500539e4581bc34d852178f00796ee7be66f6c6b",
  "recovery_preflight_raw_sha256": "aea9a6f510ee7f5147adb7aea4cba2e9662093dfc2a8465adc9b7aec61556639",
  "recovery_proof_artifact_digest": "sha256:e71ad4c19602bec2c3fa71ad6f76e41eadea53edd5ef310ea2110d251002da25",
  "recovery_proof_artifact_id": 11054938805,
  "recovery_proof_artifact_name": "exp062-dec407-active-one-shot-historical-executor-workflow-install-source-preflight-recovery-3ea7d3f7bfe8f1dfb3bbac612f74255da4fee432",
  "recovery_proof_artifact_zip_sha256": "e71ad4c19602bec2c3fa71ad6f76e41eadea53edd5ef310ea2110d251002da25",
  "recovery_proof_head_sha": "3ea7d3f7bfe8f1dfb3bbac612f74255da4fee432",
  "recovery_proof_job_id": 109569478100,
  "recovery_proof_run_attempt": 1,
  "recovery_proof_run_conclusion": "success",
  "recovery_proof_run_id": 36616131587,
  "recovery_proof_run_number": 2,
  "replacement_run_authorized": false,
  "rerun_authorized": false,
  "reserved_robustness_access_authorized": false,
  "retry_authorized": false,
  "review_source_blobs": {
    "active_discovery_workflow": "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50",
    "dec402_install_source_contract": "a09eca21a8b5e7b88182040ada5d9298eb922282",
    "dec403_preflight": "cb8ca1ca5b65e9703844d3df9b0a622e2e3ed1bc",
    "dec403_preflight_cli": "1c9615b7ee55ff1387cd95464abf2202f8dd9d3f",
    "dec407_recovery_workflow": "2adfc7bd1ccacd158a78532d31ff38f4f175229f",
    "dormant_executor_workflow_template": "51ce87584369be957482460d81649adb1cb9f05d"
  },
  "runtime_freeze_fingerprint_sha256": "77fa5c98293226176d71a759af44f23e434987a57c66d343c13f7f727202e853",
  "stage": "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_RECOVERY_PROOF_RUNTIME_EVIDENCE_BOUND_AND_FROZEN",
  "trading_authorized": false,
  "version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-source-preflight-proof-recovery-runtime-freeze-v1"
}"""


def _runtime_freeze() -> dict[str, object]:
    value = json.loads(_RUNTIME_FREEZE_JSON)
    assert isinstance(value, dict)
    return value


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallFinalAuthorizationContractTests(
    unittest.TestCase
):
    def test_contract_authorizes_only_final_authorization_source(self) -> None:
        source = (
            validate_active_one_shot_historical_executor_workflow_install_final_authorization_contract_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            source["dec410_runtime_freeze"],
            "705c08d50a8dfcae5391a0b240d78fea5716a8de",
        )

        report = build_active_one_shot_historical_executor_workflow_install_final_authorization_contract(
            repository_root=Path("."),
            runtime_freeze=_runtime_freeze(),
        )
        self.assertEqual(report["decision"], "DEC-411")
        self.assertEqual(
            report["stage"],
            (
                "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "FINAL_AUTHORIZATION_CONTRACT_SOURCE_AUTHORIZED_INSTALL_LOCKED"
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
        ):
            self.assertTrue(report[field], field)

        self.assertEqual(report["failed_proof_run_id"], 36613664506)
        self.assertEqual(report["recovery_proof_run_id"], 36616131587)
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
                "WORKFLOW_INSTALL_FINAL_AUTHORIZATION_PREFLIGHT"
            ),
        )

    def test_public_constants_keep_install_locked(self) -> None:
        self.assertTrue(
            ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_FINAL_AUTHORIZATION_CONTRACT_SOURCE_AUTHORIZED
        )
        self.assertFalse(HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED)
        self.assertFalse(HISTORICAL_EXECUTOR_AVAILABLE)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTE_MODE_AVAILABLE)
        self.assertEqual(
            DEC410_RUNTIME_FREEZE_FINGERPRINT_SHA256,
            "77fa5c98293226176d71a759af44f23e434987a57c66d343c13f7f727202e853",
        )

    def test_failed_proof_provenance_drift_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["failed_proof_run_id"] = 1
        with self.assertRaisesRegex(ValueError, "failed_proof_run_id mismatch"):
            build_active_one_shot_historical_executor_workflow_install_final_authorization_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )

    def test_recovery_proof_drift_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["recovery_proof_run_id"] = 1
        with self.assertRaisesRegex(ValueError, "recovery_proof_run_id mismatch"):
            build_active_one_shot_historical_executor_workflow_install_final_authorization_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )

    def test_runtime_freeze_fingerprint_drift_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["runtime_freeze_fingerprint_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            build_active_one_shot_historical_executor_workflow_install_final_authorization_contract(
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
            build_active_one_shot_historical_executor_workflow_install_final_authorization_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )


if __name__ == "__main__":
    unittest.main()
