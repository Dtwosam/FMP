from __future__ import annotations

import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_install_source_contract import (
    ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_AUTHORIZED,
    DEC401_RUNTIME_FREEZE_FINGERPRINT_SHA256,
    HISTORICAL_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED,
    HISTORICAL_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    build_active_one_shot_historical_executor_workflow_install_source_contract,
    validate_active_one_shot_historical_executor_workflow_install_source_contract_sources,
)


_RUNTIME_FREEZE_JSON = r"""{
  "decision": "DEC-401",
  "version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-activation-preflight-proof-runtime-freeze-v1",
  "stage": "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_PREFLIGHT_PROOF_RUNTIME_EVIDENCE_BOUND_AND_FROZEN",
  "active_install_activation_preflight_proof_head_sha": "9dd433b406bef6dc8660d897ccab5bcb1b0da99b",
  "active_install_activation_preflight_proof_run_id": 36579901387,
  "active_install_activation_preflight_proof_run_number": 1,
  "active_install_activation_preflight_proof_run_attempt": 1,
  "active_install_activation_preflight_proof_run_conclusion": "success",
  "active_install_activation_preflight_proof_job_id": 109445012411,
  "active_install_activation_preflight_proof_artifact_id": 11039017180,
  "active_install_activation_preflight_proof_artifact_name": "exp062-dec398-active-one-shot-historical-executor-workflow-install-activation-preflight-9dd433b406bef6dc8660d897ccab5bcb1b0da99b",
  "active_install_activation_preflight_proof_artifact_digest": "sha256:c19012d3e4fc794e40a930e0eac82d799773f6a9050bf56adc75a0b0f2245b85",
  "active_install_activation_preflight_proof_artifact_zip_sha256": "c19012d3e4fc794e40a930e0eac82d799773f6a9050bf56adc75a0b0f2245b85",
  "active_install_activation_preflight_raw_sha256": "8db03c11f255bcc724c4d7c18df7e5a8f539039032dbb5787291ca8810427116",
  "active_install_activation_preflight_canonical_sha256": "229fec80d76273f5320966acb63d0661ff7aa03c04ded8d953bb3e9e3f363ceb",
  "dec399_review_decision": "DEC-393",
  "dec399_review_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-execution-preflight-proof-review-v1",
  "dec400_freeze_decision": "DEC-394",
  "dec400_freeze_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-execution-preflight-proof-freeze-v1",
  "dec400_freeze_fingerprint_sha256": "441c508902f816faee66c58768552a7d3ab05f0b145193a3e6349f18c9062808",
  "dec334_terminal_review_decision": "DEC-334",
  "dec334_terminal_review_version": "fmp-exp062-historical-terminal-review-contract-v1",
  "dec399_reviewer_blob_sha": "04fb717f6b33f95b0de5dbd881709358a7482578",
  "dec400_freeze_builder_blob_sha": "a3abde9d5022cd4c83122fa05e3d55f4316d2f9a",
  "dec334_terminal_review_contract_blob_sha": "fda2a45f74b101303467cf7b8527bec1bfc5e168",
  "review_source_blobs": {
    "dec398_workflow": "0e9b24bb209a610dc56f4a447e691f35ee351f2a",
    "dec397_preflight": "bffa1c2cf26bdbd8c0428beb682439b1312b1115",
    "dec397_preflight_cli": "271f0fde0162b40c96f63bbc7eddaf100f0575ce",
    "dec396_install_activation_contract": "e212b776a04aef6978a4ffad378d2b9c4aac2ec5",
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
  "active_one_shot_historical_executor_workflow_install_activation_source_authorized": true,
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
  "runtime_freeze_fingerprint_sha256": "e2ee9e46bfe0a0fc132c5ce3f06bbad343ddb739ccaf0d22893886d1f41fbd2c"
}"""


def _runtime_freeze() -> dict[str, object]:
    value = json.loads(_RUNTIME_FREEZE_JSON)
    assert isinstance(value, dict)
    return value


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallSourceContractTests(
    unittest.TestCase
):
    def test_contract_authorizes_only_install_source(self) -> None:
        source = validate_active_one_shot_historical_executor_workflow_install_source_contract_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["dec401_runtime_freeze"],
            "bc18c1970e1927aa57a24c578351a5a4a797b7d8",
        )
        report = build_active_one_shot_historical_executor_workflow_install_source_contract(
            repository_root=Path("."),
            runtime_freeze=_runtime_freeze(),
        )
        self.assertEqual(report["decision"], "DEC-402")
        self.assertEqual(
            report["stage"],
            (
                "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "SOURCE_CONTRACT_AUTHORIZED_ACTIVE_WORKFLOW_ABSENT"
            ),
        )
        for field in (
            "active_one_shot_historical_executor_workflow_install_authorization_source_authorized",
            "active_one_shot_historical_executor_workflow_install_decision_source_authorized",
            "active_one_shot_historical_executor_workflow_install_execution_authorization_source_authorized",
            "active_one_shot_historical_executor_workflow_install_execution_contract_source_authorized",
            "active_one_shot_historical_executor_workflow_install_activation_source_authorized",
            "active_one_shot_historical_executor_workflow_install_source_authorized",
            "active_one_shot_historical_executor_workflow_install_activation_source_authorized",
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
        self.assertEqual(
            report["next_gate"],
            (
                "READ_ONLY_CURRENT_MAIN_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
                "WORKFLOW_INSTALL_SOURCE_PREFLIGHT"
            ),
        )

    def test_public_constants_keep_install_locked(self) -> None:
        self.assertTrue(
            ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_AUTHORIZED
        )
        self.assertFalse(HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED)
        self.assertFalse(HISTORICAL_EXECUTOR_AVAILABLE)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTE_MODE_AVAILABLE)
        self.assertEqual(
            DEC401_RUNTIME_FREEZE_FINGERPRINT_SHA256,
            "e2ee9e46bfe0a0fc132c5ce3f06bbad343ddb739ccaf0d22893886d1f41fbd2c",
        )

    def test_runtime_freeze_fingerprint_drift_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["runtime_freeze_fingerprint_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            build_active_one_shot_historical_executor_workflow_install_source_contract(
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
            build_active_one_shot_historical_executor_workflow_install_source_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )


if __name__ == "__main__":
    unittest.main()
