from __future__ import annotations

import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_install_execution_contract import (
    ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_CONTRACT_SOURCE_AUTHORIZED,
    DEC389_RUNTIME_FREEZE_FINGERPRINT_SHA256,
    HISTORICAL_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED,
    HISTORICAL_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    build_active_one_shot_historical_executor_workflow_install_execution_contract,
    validate_active_one_shot_historical_executor_workflow_install_execution_contract_sources,
)


_RUNTIME_FREEZE_JSON = r"""{
  "decision": "DEC-389",
  "version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-execution-authorization-preflight-proof-runtime-freeze-v1",
  "stage": "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_PREFLIGHT_PROOF_RUNTIME_EVIDENCE_BOUND_AND_FROZEN",
  "active_install_execution_authorization_preflight_proof_head_sha": "cdbef40d1c9908650155933ae5073909ad9be24d",
  "active_install_execution_authorization_preflight_proof_run_id": 36558750341,
  "active_install_execution_authorization_preflight_proof_run_number": 1,
  "active_install_execution_authorization_preflight_proof_run_attempt": 1,
  "active_install_execution_authorization_preflight_proof_run_conclusion": "success",
  "active_install_execution_authorization_preflight_proof_job_id": 109374198795,
  "active_install_execution_authorization_preflight_proof_artifact_id": 11029316948,
  "active_install_execution_authorization_preflight_proof_artifact_name": "exp062-dec386-active-one-shot-historical-executor-workflow-install-execution-authorization-preflight-cdbef40d1c9908650155933ae5073909ad9be24d",
  "active_install_execution_authorization_preflight_proof_artifact_digest": "sha256:5908aff795243b98d8dc0f2b15b603df77ec1b1313c03d76b63452c181bf8d02",
  "active_install_execution_authorization_preflight_proof_artifact_zip_sha256": "5908aff795243b98d8dc0f2b15b603df77ec1b1313c03d76b63452c181bf8d02",
  "active_install_execution_authorization_preflight_raw_sha256": "ff645bc0c6742cf05f1edbbb8438b2659ccbf00cd6d40edef284acf1e03c8dd2",
  "active_install_execution_authorization_preflight_canonical_sha256": "6fe2e118136351ffd4d72d6aad7093e83758905378c654a6df0eb927d7ab43e6",
  "dec387_review_decision": "DEC-387",
  "dec387_review_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-execution-authorization-preflight-proof-review-v1",
  "dec388_freeze_decision": "DEC-388",
  "dec388_freeze_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-execution-authorization-preflight-proof-freeze-v1",
  "dec388_freeze_fingerprint_sha256": "594b2db3aa50b5c09d7f53a4635cea40b4e566fddd0d16a6574e1322ef8a48af",
  "dec334_terminal_review_decision": "DEC-334",
  "dec334_terminal_review_version": "fmp-exp062-historical-terminal-review-contract-v1",
  "dec387_reviewer_blob_sha": "fca554b9288dbfe9482d1e8f7c35fadc04d82395",
  "dec388_freeze_builder_blob_sha": "0a56c2a48b1552669aa5e6c1882eae4dcef7c58b",
  "dec334_terminal_review_contract_blob_sha": "fda2a45f74b101303467cf7b8527bec1bfc5e168",
  "review_source_blobs": {
    "dec386_workflow": "6f620587ec85d5b24c5b3921cb9f5ddabdfb5940",
    "dec385_preflight": "595450a3f160bcaa374d16844252f96885b0e670",
    "dec385_preflight_cli": "325eb3dbf1c5ae874f456b385c617d7bbe377e27",
    "dec384_install_execution_authorization_contract": "40a3164fe713baf4289099e829527abc3da94c6e",
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
  "next_gate": "SOURCE_ONLY_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_CONTRACT",
  "runtime_freeze_fingerprint_sha256": "3517e83d30097041e7a8a74219d6da8b6fe77cf6ae3f048bffec923913826bc1"
}"""


def _runtime_freeze() -> dict[str, object]:
    value = json.loads(_RUNTIME_FREEZE_JSON)
    assert isinstance(value, dict)
    return value


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallExecutionContractTests(
    unittest.TestCase
):
    def test_contract_authorizes_only_install_execution_contract_source(self) -> None:
        source = (
            validate_active_one_shot_historical_executor_workflow_install_execution_contract_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            source["dec389_runtime_freeze"],
            "fada14bd598265f374eaa9ddeff39393bec80ddb",
        )

        report = build_active_one_shot_historical_executor_workflow_install_execution_contract(
            repository_root=Path("."),
            runtime_freeze=_runtime_freeze(),
        )
        self.assertEqual(report["decision"], "DEC-390")
        self.assertEqual(
            report["stage"],
            (
                "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "EXECUTION_CONTRACT_SOURCE_AUTHORIZED_INSTALL_LOCKED"
            ),
        )
        for field in (
            "active_one_shot_historical_executor_workflow_install_authorization_source_authorized",
            "active_one_shot_historical_executor_workflow_install_decision_source_authorized",
            "active_one_shot_historical_executor_workflow_install_execution_authorization_source_authorized",
            "active_one_shot_historical_executor_workflow_install_execution_contract_source_authorized",
        ):
            self.assertTrue(report[field], field)

        for field in (
            "historical_executor_workflow_install_authorized",
            "historical_executor_workflow_installed",
            "historical_executor_available",
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

        self.assertFalse(report["historical_result_slot_consumed"])
        self.assertTrue(report["historical_result_slot_verified_available"])
        self.assertEqual(report["expected_target_run_number"], 2)
        self.assertEqual(report["expected_target_run_attempt"], 1)
        self.assertEqual(
            report["next_gate"],
            (
                "READ_ONLY_CURRENT_MAIN_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
                "WORKFLOW_INSTALL_EXECUTION_PREFLIGHT"
            ),
        )

    def test_public_constants_keep_install_locked(self) -> None:
        self.assertTrue(
            ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_CONTRACT_SOURCE_AUTHORIZED
        )
        self.assertFalse(HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED)
        self.assertFalse(HISTORICAL_EXECUTOR_AVAILABLE)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTE_MODE_AVAILABLE)
        self.assertEqual(
            DEC389_RUNTIME_FREEZE_FINGERPRINT_SHA256,
            "3517e83d30097041e7a8a74219d6da8b6fe77cf6ae3f048bffec923913826bc1",
        )

    def test_runtime_freeze_fingerprint_drift_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["runtime_freeze_fingerprint_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            build_active_one_shot_historical_executor_workflow_install_execution_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )

    def test_wrong_real_head_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["active_install_execution_authorization_preflight_proof_head_sha"] = (
            "fa96bc731ed8d21cec883451f7ec5e984b74df40"
        )
        with self.assertRaisesRegex(
            ValueError,
            "active_install_execution_authorization_preflight_proof_head_sha mismatch",
        ):
            build_active_one_shot_historical_executor_workflow_install_execution_contract(
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
            build_active_one_shot_historical_executor_workflow_install_execution_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )


if __name__ == "__main__":
    unittest.main()
