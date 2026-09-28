from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_active_one_shot_executor_workflow_install_contract import (
    ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_AUTHORIZED,
    EXPECTED_EXECUTOR_WORKFLOW_PATH,
    HISTORICAL_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED,
    HISTORICAL_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    build_active_one_shot_historical_executor_workflow_install_contract,
    validate_active_one_shot_historical_executor_workflow_install_contract_sources,
)


def _runtime_freeze() -> dict[str, object]:
    return {
        "decision": "DEC-359",
        "version": (
            "fmp-exp062-dormant-one-shot-historical-executor-"
            "source-proof-runtime-freeze-v1"
        ),
        "stage": (
            "EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
            "RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "dormant_source_proof_head_sha": (
            "67337de4b21efab0cbafb3c9237397f0a98d524e"
        ),
        "dormant_source_proof_run_id": 36473192632,
        "dormant_source_proof_run_number": 1,
        "dormant_source_proof_run_attempt": 1,
        "dormant_source_proof_run_conclusion": "success",
        "dormant_source_proof_job_id": 109100293950,
        "dormant_source_proof_artifact_id": 10991479562,
        "dormant_source_proof_artifact_name": (
            "exp062-dec356-dormant-one-shot-historical-executor-source-"
            "67337de4b21efab0cbafb3c9237397f0a98d524e"
        ),
        "dormant_source_proof_artifact_digest": (
            "sha256:092e1daebf889560d27ebe57242772c3806322627dab03e64a2ff400d9b4b1d1"
        ),
        "dormant_source_proof_artifact_zip_sha256": (
            "092e1daebf889560d27ebe57242772c3806322627dab03e64a2ff400d9b4b1d1"
        ),
        "dormant_source_raw_sha256": (
            "1dfae5078e400fc2dbf0b10ef6d4297dc4d3c0660386ebb8c46b63c6dbe69060"
        ),
        "dormant_source_canonical_sha256": (
            "4d6cf8999ecb5346a10ecb31cdc1b669736d4d466e6b31c503b3fbf1a5e633a7"
        ),
        "dec357_review_decision": "DEC-357",
        "dec357_review_version": (
            "fmp-exp062-dormant-one-shot-historical-executor-"
            "source-proof-review-v1"
        ),
        "dec358_freeze_decision": "DEC-358",
        "dec358_freeze_version": (
            "fmp-exp062-dormant-one-shot-historical-executor-"
            "source-proof-freeze-v1"
        ),
        "dec358_freeze_fingerprint_sha256": (
            "8ba4411b8c7468a1f0eecc0352490e00577452ce96a81710fca6457e779e9897"
        ),
        "dec334_terminal_review_decision": "DEC-334",
        "dec334_terminal_review_version": (
            "fmp-exp062-historical-terminal-review-contract-v1"
        ),
        "dec357_reviewer_blob_sha": (
            "4c921577253fe7dcb74451299aecec4ad27fd522"
        ),
        "dec358_freeze_builder_blob_sha": (
            "878fa9e9be9d93c3ebd4c214a192cfb8ecdcc368"
        ),
        "dec334_terminal_review_contract_blob_sha": (
            "fda2a45f74b101303467cf7b8527bec1bfc5e168"
        ),
        "review_source_blobs": {
            "dec356_workflow": (
                "0522e443eda017759c78ccbc718f453cdb0bf8f9"
            ),
            "dec355_source": (
                "003e44126d9d6a807efd51b5a589128f6d4b5aac"
            ),
            "dec354_installation_source_contract": (
                "e4fc6a7d1faaca50bc6936597f0e8b66fe096985"
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
        "dormant_executor_workflow_template_present": True,
        "dormant_template_dispatch_capable_if_installed": True,
        "dormant_template_actions_write_required_if_installed": True,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
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
            "WORKFLOW_INSTALL_CONTRACT"
        ),
        "runtime_freeze_fingerprint_sha256": (
            "f7e1a6d1946dd42a5f72fbd9c154d1efa448db5d4e38b7469cbf0d0485fde84f"
        ),
    }


class Exp062ActiveOneShotHistoricalExecutorWorkflowInstallContractTests(
    unittest.TestCase
):
    def test_source_bindings_pin_dec359_and_dormant_template(self) -> None:
        report = (
            validate_active_one_shot_historical_executor_workflow_install_contract_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            report["dec359_runtime_freeze"],
            "3d4b7912396fbf7d51b6de4b30138bcd75566387",
        )
        self.assertEqual(
            report["dormant_executor_workflow_template"],
            "51ce87584369be957482460d81649adb1cb9f05d",
        )

    def test_contract_authorizes_source_only_with_active_path_absent(self) -> None:
        report = build_active_one_shot_historical_executor_workflow_install_contract(
            repository_root=Path("."),
            runtime_freeze=_runtime_freeze(),
        )
        self.assertEqual(report["decision"], "DEC-360")
        self.assertEqual(
            report["stage"],
            (
                "EXP062_ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_"
                "SOURCE_AUTHORIZED_ACTIVE_WORKFLOW_ABSENT"
            ),
        )
        self.assertEqual(
            report["expected_executor_workflow_path"],
            EXPECTED_EXECUTOR_WORKFLOW_PATH,
        )
        self.assertTrue(
            report[
                "active_one_shot_historical_executor_workflow_install_source_authorized"
            ]
        )
        self.assertTrue(report["dormant_executor_workflow_template_present"])
        self.assertFalse(report["executor_workflow_path_exists"])
        self.assertFalse(
            report["historical_executor_workflow_install_authorized"]
        )
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
            ACTIVE_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_SOURCE_AUTHORIZED
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
            build_active_one_shot_historical_executor_workflow_install_contract(
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
            build_active_one_shot_historical_executor_workflow_install_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )

    def test_dispatch_authority_escalation_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["historical_result_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_dispatch_authorized mismatch",
        ):
            build_active_one_shot_historical_executor_workflow_install_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )


if __name__ == "__main__":
    unittest.main()
