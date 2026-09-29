from __future__ import annotations

import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_install_decision_contract import (
    ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_DECISION_SOURCE_AUTHORIZED,
    DEC377_RUNTIME_FREEZE_FINGERPRINT_SHA256,
    HISTORICAL_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED,
    HISTORICAL_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    build_active_one_shot_historical_executor_workflow_install_decision_contract,
    validate_active_one_shot_historical_executor_workflow_install_decision_contract_sources,
)


_RUNTIME_FREEZE_JSON = r"""{
  "decision": "DEC-377",
  "version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-authorization-preflight-proof-runtime-freeze-v1",
  "stage": "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZATION_PREFLIGHT_PROOF_RUNTIME_EVIDENCE_BOUND_AND_FROZEN",
  "active_install_authorization_preflight_proof_head_sha": "c23ba694fcf60e2a73280f59fe0bf13d90ffa229",
  "active_install_authorization_preflight_proof_run_id": 36542684978,
  "active_install_authorization_preflight_proof_run_number": 1,
  "active_install_authorization_preflight_proof_run_attempt": 1,
  "active_install_authorization_preflight_proof_run_conclusion": "success",
  "active_install_authorization_preflight_proof_job_id": 109321600936,
  "active_install_authorization_preflight_proof_artifact_id": 11020419084,
  "active_install_authorization_preflight_proof_artifact_name": "exp062-dec374-active-one-shot-historical-executor-workflow-install-authorization-preflight-c23ba694fcf60e2a73280f59fe0bf13d90ffa229",
  "active_install_authorization_preflight_proof_artifact_digest": "sha256:f7829f71c481143517b918c7d54b1cb43136edcd50ea9076e3795935bd994384",
  "active_install_authorization_preflight_proof_artifact_zip_sha256": "f7829f71c481143517b918c7d54b1cb43136edcd50ea9076e3795935bd994384",
  "active_install_authorization_preflight_raw_sha256": "e5de1145a6f39ca42413fb5ce1eed297d8bdcf572923e296d2b6d773e945e45f",
  "active_install_authorization_preflight_canonical_sha256": "994b96d76cf50cfae019d21b4b478d6e0b6ffc0c99fda9efa7c7aa4bf50263dc",
  "dec375_review_decision": "DEC-375",
  "dec375_review_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-authorization-preflight-proof-review-v1",
  "dec376_freeze_decision": "DEC-376",
  "dec376_freeze_version": "fmp-exp062-active-one-shot-historical-executor-workflow-install-authorization-preflight-proof-freeze-v1",
  "dec376_freeze_fingerprint_sha256": "fb4c445610884db868a516f9a2086c8d0a6f22d397cb7e8d39806548101c1595",
  "dec334_terminal_review_decision": "DEC-334",
  "dec334_terminal_review_version": "fmp-exp062-historical-terminal-review-contract-v1",
  "dec375_reviewer_blob_sha": "360e3a8aaefd8ff10bab39f4e836508aa7a0b51b",
  "dec376_freeze_builder_blob_sha": "b1c4e4e1dc079fcc19273ed13f37c2b3ff0bf253",
  "dec334_terminal_review_contract_blob_sha": "fda2a45f74b101303467cf7b8527bec1bfc5e168",
  "review_source_blobs": {
    "dec374_workflow": "e68a4c60d4411431b0c7fdfad0fa564fc4e5ccf6",
    "dec373_preflight": "8f6a1523bddf419a915bc797e310a5c520baf62a",
    "dec373_preflight_cli": "64e205c12882e9d14a84fd719ef94907a2bb2ad0",
    "dec372_install_authorization_contract": "ac4876d6b544567c238d9241ee050b763c2ed630",
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
  "next_gate": "SOURCE_ONLY_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_DECISION_CONTRACT",
  "runtime_freeze_fingerprint_sha256": "24619aed5578085ee3e2d3555e1b109817d9816042f646446dbc406b20f13593"
}"""


def _runtime_freeze() -> dict[str, object]:
    value = json.loads(_RUNTIME_FREEZE_JSON)
    assert isinstance(value, dict)
    return value


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallDecisionContractTests(
    unittest.TestCase
):
    def test_contract_authorizes_only_install_decision_source(self) -> None:
        source = (
            validate_active_one_shot_historical_executor_workflow_install_decision_contract_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            source["dec377_runtime_freeze"],
            "0caa3b69f537f92bb13a41c6f28275f5513c9a07",
        )

        report = (
            build_active_one_shot_historical_executor_workflow_install_decision_contract(
                repository_root=Path("."),
                runtime_freeze=_runtime_freeze(),
            )
        )
        self.assertEqual(report["decision"], "DEC-378")
        self.assertEqual(
            report["stage"],
            (
                "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "DECISION_SOURCE_AUTHORIZED_INSTALL_LOCKED"
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
                "WORKFLOW_INSTALL_DECISION_PREFLIGHT"
            ),
        )

    def test_public_constants_keep_install_locked(self) -> None:
        self.assertTrue(
            ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_DECISION_SOURCE_AUTHORIZED
        )
        self.assertFalse(HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED)
        self.assertFalse(HISTORICAL_EXECUTOR_AVAILABLE)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTE_MODE_AVAILABLE)
        self.assertEqual(
            DEC377_RUNTIME_FREEZE_FINGERPRINT_SHA256,
            "24619aed5578085ee3e2d3555e1b109817d9816042f646446dbc406b20f13593",
        )

    def test_runtime_freeze_fingerprint_drift_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["runtime_freeze_fingerprint_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            build_active_one_shot_historical_executor_workflow_install_decision_contract(
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
            build_active_one_shot_historical_executor_workflow_install_decision_contract(
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
            build_active_one_shot_historical_executor_workflow_install_decision_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )


if __name__ == "__main__":
    unittest.main()
