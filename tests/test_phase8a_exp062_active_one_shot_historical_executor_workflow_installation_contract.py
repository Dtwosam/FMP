from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_installation_contract import (
    ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALLATION_SOURCE_AUTHORIZED,
    DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA,
    EXPECTED_EXECUTOR_WORKFLOW_PATH,
    HISTORICAL_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED,
    HISTORICAL_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    build_active_one_shot_historical_executor_workflow_installation_contract,
    validate_active_one_shot_historical_executor_workflow_installation_contract_sources,
)


def _runtime_freeze() -> dict[str, object]:
    return {
        "decision": "DEC-365",
        "version": (
            "fmp-exp062-active-one-shot-historical-executor-workflow-install-"
            "preflight-proof-runtime-freeze-v1"
        ),
        "stage": (
            "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
            "PREFLIGHT_PROOF_RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "active_install_preflight_proof_head_sha": (
            "8e74ca94237963253b4fd6e42c42965cabec3ab1"
        ),
        "active_install_preflight_proof_run_id": 36478916362,
        "active_install_preflight_proof_run_number": 1,
        "active_install_preflight_proof_run_attempt": 1,
        "active_install_preflight_proof_run_conclusion": "success",
        "active_install_preflight_proof_job_id": 109119455390,
        "active_install_preflight_proof_artifact_id": 10996155764,
        "active_install_preflight_proof_artifact_name": (
            "exp062-dec362-active-one-shot-historical-executor-"
            "workflow-install-preflight-"
            "8e74ca94237963253b4fd6e42c42965cabec3ab1"
        ),
        "active_install_preflight_proof_artifact_digest": (
            "sha256:5554cabdf72e87c6c860746f1d76d0816a3dd3ebdf2b443b911b5027e81f070a"
        ),
        "active_install_preflight_proof_artifact_zip_sha256": (
            "5554cabdf72e87c6c860746f1d76d0816a3dd3ebdf2b443b911b5027e81f070a"
        ),
        "active_install_preflight_raw_sha256": (
            "c70cbdb3f593de110a21d6501d867ed23f6be70b7815993ef1b62fea1d2477fc"
        ),
        "active_install_preflight_canonical_sha256": (
            "010f1bcdd595de78ebe55ad3729e641345f3c486e3a46e38a60a7072555ad30b"
        ),
        "dec363_review_decision": "DEC-363",
        "dec363_review_version": (
            "fmp-exp062-active-one-shot-historical-executor-workflow-install-"
            "preflight-proof-review-v1"
        ),
        "dec364_freeze_decision": "DEC-364",
        "dec364_freeze_version": (
            "fmp-exp062-active-one-shot-historical-executor-workflow-install-"
            "preflight-proof-freeze-v1"
        ),
        "dec364_freeze_fingerprint_sha256": (
            "2e8c36e891b20dc1811301a4b461d51c9fa46e34b098cbe5af1e3a27bc129932"
        ),
        "dec334_terminal_review_decision": "DEC-334",
        "dec334_terminal_review_version": (
            "fmp-exp062-historical-terminal-review-contract-v1"
        ),
        "dec363_reviewer_blob_sha": (
            "e54284e45340ce4f3ca48901e08fcded10bd8d84"
        ),
        "dec364_freeze_builder_blob_sha": (
            "afaebd7144e2e4820512483338eadc6adabbbbe3"
        ),
        "dec334_terminal_review_contract_blob_sha": (
            "fda2a45f74b101303467cf7b8527bec1bfc5e168"
        ),
        "review_source_blobs": {
            "dec362_workflow": (
                "57b9ea6a4025ee3883a104608f61dd840990801b"
            ),
            "dec361_preflight": (
                "e7a40563e173709e04a63f4d08ac73aa7224a15d"
            ),
            "dec361_preflight_cli": (
                "f8c5f2d892fe9b3ac8492d6e142fbf698cd2bcdf"
            ),
            "dec360_install_contract": (
                "63d645115dec87a4ec2bbec8448a26ea7cdded34"
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
        "active_one_shot_historical_executor_workflow_install_source_authorized": True,
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
            "WORKFLOW_INSTALLATION_CONTRACT"
        ),
        "runtime_freeze_fingerprint_sha256": (
            "84e237e8b2996c69efdc0d7c11c1931fc917d2bc3c0bb8ba74c26c84b4aea301"
        ),
    }


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallationContractTests(
    unittest.TestCase
):
    def test_contract_authorizes_installation_source_only(self) -> None:
        source = (
            validate_active_one_shot_historical_executor_workflow_installation_contract_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            source["dec365_runtime_freeze"],
            "d999c4a1929fae9469c66e81663fe19e8fb19dc2",
        )
        self.assertEqual(
            source["dormant_executor_workflow_template"],
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA,
        )

        report = build_active_one_shot_historical_executor_workflow_installation_contract(
            repository_root=Path("."),
            runtime_freeze=_runtime_freeze(),
        )
        self.assertEqual(report["decision"], "DEC-366")
        self.assertEqual(
            report["expected_executor_workflow_path"],
            EXPECTED_EXECUTOR_WORKFLOW_PATH,
        )
        self.assertTrue(
            report[
                "active_one_shot_historical_executor_workflow_installation_source_authorized"
            ]
        )
        self.assertFalse(report["executor_workflow_path_exists"])
        self.assertFalse(
            report["historical_executor_workflow_install_authorized"]
        )
        self.assertFalse(report["historical_executor_workflow_installed"])
        self.assertFalse(report["historical_executor_available"])
        self.assertFalse(report["historical_result_dispatch_authorized"])
        self.assertFalse(report["historical_execute_mode_available"])
        self.assertFalse(report["trading_authorized"])

    def test_public_constants_keep_runtime_locked(self) -> None:
        self.assertTrue(
            ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALLATION_SOURCE_AUTHORIZED
        )
        self.assertFalse(HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED)
        self.assertFalse(HISTORICAL_EXECUTOR_AVAILABLE)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTE_MODE_AVAILABLE)

    def test_runtime_freeze_fingerprint_drift_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["runtime_freeze_fingerprint_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            build_active_one_shot_historical_executor_workflow_installation_contract(
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
            build_active_one_shot_historical_executor_workflow_installation_contract(
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
            build_active_one_shot_historical_executor_workflow_installation_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )


if __name__ == "__main__":
    unittest.main()
