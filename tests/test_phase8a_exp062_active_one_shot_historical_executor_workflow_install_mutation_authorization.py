from __future__ import annotations

import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_install_mutation_authorization import (
    DEC422_RUNTIME_FREEZE_FINGERPRINT_SHA256,
    EXPLICIT_REPOSITORY_MUTATION_AUTHORIZED,
    HISTORICAL_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED,
    HISTORICAL_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    build_active_one_shot_historical_executor_workflow_install_mutation_authorization,
    validate_active_one_shot_historical_executor_workflow_install_mutation_authorization_sources,
)


_RUNTIME_FREEZE_JSON = r"""{
  "active_install_action_preflight_canonical_sha256": "66ebc48ff1e6ee8d24e19b0641c012244f93ddfb1e02baf343bec3df6a4f9c26",
  "active_install_action_preflight_proof_artifact_digest": "sha256:1f06c7b589f46ca7a473bae5a0666b79b1b627dc6a8eaf85804211424e09f0be",
  "active_install_action_preflight_proof_artifact_id": 11063264562,
  "active_install_action_preflight_proof_artifact_name": "exp062-dec419-active-one-shot-historical-executor-workflow-install-action-preflight-51a49397e1eddc5b9e342d50b588f774e783a5e7",
  "active_install_action_preflight_proof_artifact_zip_sha256": "1f06c7b589f46ca7a473bae5a0666b79b1b627dc6a8eaf85804211424e09f0be",
  "active_install_action_preflight_proof_head_sha": "51a49397e1eddc5b9e342d50b588f774e783a5e7",
  "active_install_action_preflight_proof_job_id": 109632428957,
  "active_install_action_preflight_proof_run_attempt": 1,
  "active_install_action_preflight_proof_run_conclusion": "success",
  "active_install_action_preflight_proof_run_id": 36634716243,
  "active_install_action_preflight_proof_run_number": 1,
  "active_install_action_preflight_raw_sha256": "567af303b2e37131b83c7f316424174632dd34854a38660f910c3072fbd893da",
  "active_one_shot_historical_executor_workflow_install_action_contract_source_authorized": true,
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
  "dec420_review_decision": "DEC-420",
  "dec420_review_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-action-preflight-proof-review-v1",
  "dec420_reviewer_blob_sha": "55b3fddd0ec55a0813f4f36698afc342c1c3d5f0",
  "dec421_freeze_builder_blob_sha": "7e0c9d361eecce2917147db2c62884de9722bc7a",
  "dec421_freeze_decision": "DEC-421",
  "dec421_freeze_fingerprint_sha256": "78bcceaf580672b97858ec972c590300316f8b7b369137ca96e957c39d1d9a5d",
  "dec421_freeze_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-action-preflight-proof-freeze-v1",
  "decision": "DEC-422",
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
  "next_gate": "EXPLICIT_REPOSITORY_MUTATION_AUTHORIZATION_BEFORE_ACTIVE_WORKFLOW_INSTALL",
  "phase8b_authorized": false,
  "promotion_authorized": false,
  "real_money_authorized": false,
  "replacement_run_authorized": false,
  "rerun_authorized": false,
  "reserved_robustness_access_authorized": false,
  "retry_authorized": false,
  "review_source_blobs": {
    "active_discovery_workflow": "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50",
    "dec417_install_action_contract": "7d65e3b4359726d6cd920f31ceab84fdba88e922",
    "dec418_preflight": "2d499f52b423bce5771c932e75a8196e0428304d",
    "dec418_preflight_cli": "9bd7815b58b9f057cf560f2c1d8874ee46bbd44a",
    "dec419_workflow": "6d22ffb3d93e7860033887987aff56f8870741c2",
    "dormant_executor_workflow_template": "51ce87584369be957482460d81649adb1cb9f05d"
  },
  "runtime_freeze_fingerprint_sha256": "cce3b8900f630ddf0e651af10ceba39311f1e00485f6bca99af28252195aae0f",
  "stage": "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_ACTION_PREFLIGHT_PROOF_RUNTIME_EVIDENCE_BOUND_AND_FROZEN",
  "trading_authorized": false,
  "version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-action-preflight-proof-runtime-freeze-v1"
}"""


def _runtime_freeze() -> dict[str, object]:
    value = json.loads(_RUNTIME_FREEZE_JSON)
    assert isinstance(value, dict)
    return value


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallMutationAuthorizationTests(
    unittest.TestCase
):
    def test_source_bindings_pin_dec422_and_dormant_template(self) -> None:
        source = validate_active_one_shot_historical_executor_workflow_install_mutation_authorization_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["dec422_runtime_freeze"],
            "65108857f15b6ab084bbb5f8a0358b7bbd4aaa59",
        )
        self.assertEqual(
            source["dormant_executor_workflow_template"],
            "51ce87584369be957482460d81649adb1cb9f05d",
        )

    def test_authorization_opens_only_repository_install_mutation(self) -> None:
        result = build_active_one_shot_historical_executor_workflow_install_mutation_authorization(
            repository_root=Path("."),
            runtime_freeze=_runtime_freeze(),
        )
        self.assertEqual(result["decision"], "DEC-423")
        self.assertTrue(result["explicit_repository_mutation_authorized"])
        self.assertTrue(result["historical_executor_workflow_install_authorized"])
        self.assertFalse(result["executor_workflow_path_exists"])
        self.assertFalse(result["historical_executor_workflow_installed"])
        self.assertFalse(result["historical_executor_available"])
        self.assertFalse(result["historical_result_dispatch_authorized"])
        self.assertFalse(result["historical_execute_mode_available"])
        self.assertFalse(result["trading_authorized"])
        self.assertEqual(
            result["next_gate"],
            "ACTIVE_WORKFLOW_INSTALL_REPOSITORY_MUTATION",
        )

    def test_public_constants_keep_dispatch_and_trading_locked(self) -> None:
        self.assertTrue(EXPLICIT_REPOSITORY_MUTATION_AUTHORIZED)
        self.assertTrue(HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED)
        self.assertFalse(HISTORICAL_EXECUTOR_AVAILABLE)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTE_MODE_AVAILABLE)
        self.assertEqual(
            DEC422_RUNTIME_FREEZE_FINGERPRINT_SHA256,
            "cce3b8900f630ddf0e651af10ceba39311f1e00485f6bca99af28252195aae0f",
        )

    def test_runtime_fingerprint_drift_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["runtime_freeze_fingerprint_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            build_active_one_shot_historical_executor_workflow_install_mutation_authorization(
                repository_root=Path("."),
                runtime_freeze=value,
            )

    def test_dispatch_authority_escalation_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["historical_result_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_dispatch_authorized",
        ):
            build_active_one_shot_historical_executor_workflow_install_mutation_authorization(
                repository_root=Path("."),
                runtime_freeze=value,
            )


if __name__ == "__main__":
    unittest.main()
