from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_install_authorization_contract import (
    ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZATION_SOURCE_AUTHORIZED,
    DEC371_RUNTIME_FREEZE_FINGERPRINT_SHA256,
    HISTORICAL_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED,
    HISTORICAL_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    build_active_one_shot_historical_executor_workflow_install_authorization_contract,
    validate_active_one_shot_historical_executor_workflow_install_authorization_contract_sources,
)


def _runtime_freeze() -> dict[str, object]:
    return {
        "decision": "DEC-371",
        "version": (
            "fmp-exp062-active-one-shot-historical-executor-workflow-"
            "installation-preflight-proof-runtime-freeze-v1"
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALLATION_"
            "PREFLIGHT_PROOF_RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "active_installation_preflight_proof_head_sha": (
            "035c0ee8190a7eb1e2c8ac80771e6eeb19d1e8e1"
        ),
        "active_installation_preflight_proof_run_id": 36484309283,
        "active_installation_preflight_proof_run_number": 1,
        "active_installation_preflight_proof_run_attempt": 1,
        "active_installation_preflight_proof_run_conclusion": "success",
        "active_installation_preflight_proof_job_id": 109137344254,
        "active_installation_preflight_proof_artifact_id": 10997847720,
        "active_installation_preflight_proof_artifact_name": (
            "exp062-dec368-active-one-shot-historical-executor-"
            "workflow-installation-preflight-"
            "035c0ee8190a7eb1e2c8ac80771e6eeb19d1e8e1"
        ),
        "active_installation_preflight_proof_artifact_digest": (
            "sha256:d122e474752f1ec8127eb610b55321dbf94cc7dcb339eca43eafb7e429ef4a07"
        ),
        "active_installation_preflight_proof_artifact_zip_sha256": (
            "d122e474752f1ec8127eb610b55321dbf94cc7dcb339eca43eafb7e429ef4a07"
        ),
        "active_installation_preflight_raw_sha256": (
            "5bf7760c7ad36e642eeeaf9e29b5fb0e5108a4059207ff2d7d75bd4c9f6bcf3b"
        ),
        "active_installation_preflight_canonical_sha256": (
            "30de670f8483139b23fbd51bd05444677278fd7d1ba1f1eb8f0cc33409cf3a74"
        ),
        "dec369_review_decision": "DEC-369",
        "dec369_review_version": (
            "fmp-exp062-active-one-shot-historical-executor-workflow-"
            "installation-preflight-proof-review-v1"
        ),
        "dec370_freeze_decision": "DEC-370",
        "dec370_freeze_version": (
            "fmp-exp062-active-one-shot-historical-executor-workflow-"
            "installation-preflight-proof-freeze-v1"
        ),
        "dec370_freeze_fingerprint_sha256": (
            "51e47a3d6d2876b52e2090714e6f89b4c2ce0ae2d869d79e5b2cd4586c774af6"
        ),
        "dec334_terminal_review_decision": "DEC-334",
        "dec334_terminal_review_version": (
            "fmp-exp062-historical-terminal-review-contract-v1"
        ),
        "dec369_reviewer_blob_sha": (
            "72ef4162a88efc14727f1b8227c78e45532971d6"
        ),
        "dec370_freeze_builder_blob_sha": (
            "8a382cf527fee7d88f9940b816d8e5889dabe9f2"
        ),
        "dec334_terminal_review_contract_blob_sha": (
            "fda2a45f74b101303467cf7b8527bec1bfc5e168"
        ),
        "review_source_blobs": {
            "dec368_workflow": (
                "e7e1bc2b5f9f80a2aed2ad8f3669cce0b324ffae"
            ),
            "dec367_preflight": (
                "57ad54f5c9a472e7eb878728815cf62a80e91bf3"
            ),
            "dec367_preflight_cli": (
                "20816d21f4ebe08bc8ac5b90fce6d347c2ff018c"
            ),
            "dec366_installation_contract": (
                "321b60953384fcc0fe77e758fed25b7a154dda3e"
            ),
            "dormant_executor_workflow_template": (
                "51ce87584369be957482460d81649adb1cb9f05d"
            ),
            "active_discovery_workflow": (
                "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
            ),
        },
        "dormant_executor_workflow_template_blob_sha": (
            "51ce87584369be957482460d81649adb1cb9f05d"
        ),
        "expected_executor_workflow_path": (
            ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
        ),
        "executor_workflow_path_exists": False,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "active_one_shot_historical_executor_workflow_installation_source_authorized": True,
        "historical_executor_workflow_install_authorized": False,
        "historical_executor_workflow_installed": False,
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
            "SOURCE_ONLY_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_"
            "WORKFLOW_INSTALL_AUTHORIZATION_CONTRACT"
        ),
        "runtime_freeze_fingerprint_sha256": (
            "a498bf1cae3c6e92803fc750331c3090c35bb3af13bf01a62866831d29bb95f8"
        ),
    }


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallAuthorizationContractTests(
    unittest.TestCase
):
    def test_contract_authorizes_only_authorization_source(self) -> None:
        source = (
            validate_active_one_shot_historical_executor_workflow_install_authorization_contract_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            source["dec371_runtime_freeze"],
            "fb9f968fcfc953217234f7484b14d98293087f02",
        )

        report = (
            build_active_one_shot_historical_executor_workflow_install_authorization_contract(
                repository_root=Path("."),
                runtime_freeze=_runtime_freeze(),
            )
        )
        self.assertEqual(report["decision"], "DEC-372")
        self.assertEqual(
            report["stage"],
            (
                "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "AUTHORIZATION_SOURCE_AUTHORIZED_INSTALL_LOCKED"
            ),
        )
        self.assertTrue(
            report[
                "active_one_shot_historical_executor_workflow_"
                "install_authorization_source_authorized"
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

    def test_public_constants_keep_runtime_locked(self) -> None:
        self.assertTrue(
            ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZATION_SOURCE_AUTHORIZED
        )
        self.assertFalse(HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED)
        self.assertFalse(HISTORICAL_EXECUTOR_AVAILABLE)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTE_MODE_AVAILABLE)
        self.assertEqual(
            DEC371_RUNTIME_FREEZE_FINGERPRINT_SHA256,
            "a498bf1cae3c6e92803fc750331c3090c35bb3af13bf01a62866831d29bb95f8",
        )

    def test_runtime_freeze_fingerprint_drift_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["runtime_freeze_fingerprint_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            build_active_one_shot_historical_executor_workflow_install_authorization_contract(
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
            build_active_one_shot_historical_executor_workflow_install_authorization_contract(
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
            build_active_one_shot_historical_executor_workflow_install_authorization_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )


if __name__ == "__main__":
    unittest.main()
