from __future__ import annotations

import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_install_execution_authorization_contract import (
    ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_SOURCE_AUTHORIZED,
    DEC383_RUNTIME_FREEZE_FINGERPRINT_SHA256,
    HISTORICAL_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED,
    HISTORICAL_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    build_active_one_shot_historical_executor_workflow_install_execution_authorization_contract,
    validate_active_one_shot_historical_executor_workflow_install_execution_authorization_contract_sources,
)


_RUNTIME_FREEZE_JSON = r"""{
  "decision": "DEC-383",
  "version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-decision-preflight-proof-runtime-freeze-v1",
  "stage": "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_DECISION_PREFLIGHT_PROOF_RUNTIME_EVIDENCE_BOUND_AND_FROZEN",
  "active_install_decision_preflight_proof_head_sha": "fa96bc731ed8d21cec883451f7ec5e984b74df40",
  "active_install_decision_preflight_proof_run_id": 36553935570,
  "active_install_decision_preflight_proof_run_number": 1,
  "active_install_decision_preflight_proof_run_attempt": 1,
  "active_install_decision_preflight_proof_run_conclusion": "success",
  "active_install_decision_preflight_proof_job_id": 109358450875,
  "active_install_decision_preflight_proof_artifact_id": 11025737149,
  "active_install_decision_preflight_proof_artifact_name": "exp062-dec380-active-one-shot-historical-executor-workflow-install-decision-preflight-fa96bc731ed8d21cec883451f7ec5e984b74df40",
  "active_install_decision_preflight_proof_artifact_digest": "sha256:f863ea57b45e2c0e12892732747094f8f4f63793cf212be018d7d6cbade6555b",
  "active_install_decision_preflight_proof_artifact_zip_sha256": "f863ea57b45e2c0e12892732747094f8f4f63793cf212be018d7d6cbade6555b",
  "active_install_decision_preflight_raw_sha256": "05bb0e78cd14d22ba84a2bd46bc2fde894e088ad4e96fdd463a040ea91718ed0",
  "active_install_decision_preflight_canonical_sha256": "27e6ef7221062844b1f4b12f6fae55c9de2d933c4f606411cd676e982201487f",
  "dec381_review_decision": "DEC-381",
  "dec381_review_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-decision-preflight-proof-review-v1",
  "dec382_freeze_decision": "DEC-382",
  "dec382_freeze_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-decision-preflight-proof-freeze-v1",
  "dec382_freeze_fingerprint_sha256": "be15d3ffe0a66befeec91694e5c412e0d7678818835774361258edf06b06b6f8",
  "dec334_terminal_review_decision": "DEC-334",
  "dec334_terminal_review_version": "fmp-exp062-historical-terminal-review-contract-v1",
  "dec381_reviewer_blob_sha": "2358d8fe3a54d9dbe86a51d3f97275b6557c0865",
  "dec382_freeze_builder_blob_sha": "4a5691e0467b0ad1a272beb2333e4a987fa0806d",
  "dec334_terminal_review_contract_blob_sha": "fda2a45f74b101303467cf7b8527bec1bfc5e168",
  "review_source_blobs": {
    "dec380_workflow": "45129f3ef81348a344e2e88108ebae7b6506b10f",
    "dec379_preflight": "87e86b9c424e72ca67d39c230c038704523d3adc",
    "dec379_preflight_cli": "6aee1bc7f230567d403eeb1d3f8fea9751c9a20d",
    "dec378_install_decision_contract": "4bdaa6f48b2a0d8ea467c7cbd1869358749660e5",
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
  "next_gate": "SOURCE_ONLY_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_CONTRACT",
  "runtime_freeze_fingerprint_sha256": "e4369f71272b8fd8a3ef4104f12aaf748bd7c938e4feb648a87c6aadd14e2e19"
}"""


def _runtime_freeze() -> dict[str, object]:
    value = json.loads(_RUNTIME_FREEZE_JSON)
    assert isinstance(value, dict)
    return value


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallExecutionAuthorizationContractTests(
    unittest.TestCase
):
    def test_contract_authorizes_only_execution_authorization_source(self) -> None:
        source = (
            validate_active_one_shot_historical_executor_workflow_install_execution_authorization_contract_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            source["dec383_runtime_freeze"],
            "b946d5b3d390d008634d49a2a0b560211d18aa2b",
        )

        report = (
            build_active_one_shot_historical_executor_workflow_install_execution_authorization_contract(
                repository_root=Path("."),
                runtime_freeze=_runtime_freeze(),
            )
        )
        self.assertEqual(report["decision"], "DEC-384")
        self.assertEqual(
            report["stage"],
            (
                "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "EXECUTION_AUTHORIZATION_SOURCE_AUTHORIZED_INSTALL_LOCKED"
            ),
        )
        self.assertTrue(
            report[
                "active_one_shot_historical_executor_workflow_"
                "install_authorization_source_authorized"
            ]
        )
        self.assertTrue(
            report[
                "active_one_shot_historical_executor_workflow_"
                "install_decision_source_authorized"
            ]
        )
        self.assertTrue(
            report[
                "active_one_shot_historical_executor_workflow_"
                "install_execution_authorization_source_authorized"
            ]
        )
        self.assertFalse(report["historical_executor_workflow_install_authorized"])
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
        self.assertEqual(
            report["next_gate"],
            (
                "READ_ONLY_CURRENT_MAIN_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
                "WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_PREFLIGHT"
            ),
        )

    def test_public_constants_keep_install_locked(self) -> None:
        self.assertTrue(
            ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_EXECUTION_AUTHORIZATION_SOURCE_AUTHORIZED
        )
        self.assertFalse(HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED)
        self.assertFalse(HISTORICAL_EXECUTOR_AVAILABLE)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTE_MODE_AVAILABLE)
        self.assertEqual(
            DEC383_RUNTIME_FREEZE_FINGERPRINT_SHA256,
            "e4369f71272b8fd8a3ef4104f12aaf748bd7c938e4feb648a87c6aadd14e2e19",
        )

    def test_runtime_freeze_fingerprint_drift_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["runtime_freeze_fingerprint_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            build_active_one_shot_historical_executor_workflow_install_execution_authorization_contract(
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
            build_active_one_shot_historical_executor_workflow_install_execution_authorization_contract(
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
            build_active_one_shot_historical_executor_workflow_install_execution_authorization_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )


if __name__ == "__main__":
    unittest.main()
