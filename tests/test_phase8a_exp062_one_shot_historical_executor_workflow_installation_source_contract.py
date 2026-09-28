from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_one_shot_executor_workflow_installation_source_contract import (
    DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH,
    EXPECTED_EXECUTOR_WORKFLOW_PATH,
    HISTORICAL_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_AUTHORIZED,
    HISTORICAL_EXECUTOR_WORKFLOW_INSTALLED,
    HISTORICAL_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALLATION_SOURCE_AUTHORIZED,
    build_one_shot_historical_executor_workflow_installation_source_contract,
    validate_one_shot_historical_executor_workflow_installation_source_contract_sources,
)


def _runtime_freeze() -> dict[str, object]:
    return {
        "decision": "DEC-353",
        "version": (
            "fmp-exp062-one-shot-historical-executor-workflow-install-"
            "preflight-proof-runtime-freeze-v1"
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALL_PREFLIGHT_PROOF_"
            "RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "workflow_install_preflight_proof_head_sha": (
            "bef60cd8656f0db48293570c13f91e2e09fe5be8"
        ),
        "workflow_install_preflight_proof_run_id": 36461898040,
        "workflow_install_preflight_proof_run_number": 1,
        "workflow_install_preflight_proof_run_attempt": 1,
        "workflow_install_preflight_proof_run_conclusion": "success",
        "workflow_install_preflight_proof_job_id": 109062250103,
        "workflow_install_preflight_proof_artifact_id": 10987972547,
        "workflow_install_preflight_proof_artifact_name": (
            "exp062-dec350-one-shot-historical-executor-workflow-install-"
            "preflight-bef60cd8656f0db48293570c13f91e2e09fe5be8"
        ),
        "workflow_install_preflight_proof_artifact_digest": (
            "sha256:60a723a55502ee9b8145258c5482ce71b82b2331c572378536b14d78f6ef2f91"
        ),
        "workflow_install_preflight_proof_artifact_zip_sha256": (
            "60a723a55502ee9b8145258c5482ce71b82b2331c572378536b14d78f6ef2f91"
        ),
        "workflow_install_preflight_raw_sha256": (
            "ee754581b87576c3c23228a2371b88b3b8a38fdcd9c20ebd2c222c18f7c65e0d"
        ),
        "workflow_install_preflight_canonical_sha256": (
            "5c1893ea24a627ea421f05564d6d0cc490215201c01162fbe0b6ab519a323c8b"
        ),
        "dec351_review_decision": "DEC-351",
        "dec351_review_version": (
            "fmp-exp062-one-shot-historical-executor-workflow-install-"
            "preflight-proof-review-v1"
        ),
        "dec352_freeze_decision": "DEC-352",
        "dec352_freeze_version": (
            "fmp-exp062-one-shot-historical-executor-workflow-install-"
            "preflight-proof-freeze-v1"
        ),
        "dec352_freeze_fingerprint_sha256": (
            "75fad6795f4046d83f5ae29f08475c969e29d3fe3af0e3448dde46292a959f4a"
        ),
        "dec334_terminal_review_decision": "DEC-334",
        "dec334_terminal_review_version": (
            "fmp-exp062-historical-terminal-review-contract-v1"
        ),
        "dec351_reviewer_blob_sha": (
            "704877e4a0440744c29dd4338173fb8818f6c0d6"
        ),
        "dec352_freeze_builder_blob_sha": (
            "60256d2fa9201f666dd8e330c98b3d080ffe6b43"
        ),
        "dec334_terminal_review_contract_blob_sha": (
            "fda2a45f74b101303467cf7b8527bec1bfc5e168"
        ),
        "expected_executor_workflow_path": EXPECTED_EXECUTOR_WORKFLOW_PATH,
        "executor_workflow_path_exists": False,
        "workflow_install_slot_verified_available": True,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "one_shot_historical_executor_workflow_install_source_authorized": True,
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
            "SOURCE_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_"
            "INSTALLATION_SOURCE_CONTRACT"
        ),
        "runtime_freeze_fingerprint_sha256": (
            "aa2eafcf48f19f694ac9acac08b91174b2ca1282c2a2b6ea2a33cb16aa2d4385"
        ),
    }


class Exp062OneShotHistoricalExecutorWorkflowInstallationSourceContractTests(
    unittest.TestCase
):
    def test_contract_authorizes_dormant_source_only(self) -> None:
        source = (
            validate_one_shot_historical_executor_workflow_installation_source_contract_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            source["dec353_runtime_freeze_blob_sha"],
            "2183798aa137e234849f92a0aee13e14a76876e2",
        )

        report = (
            build_one_shot_historical_executor_workflow_installation_source_contract(
                repository_root=Path("."),
                runtime_freeze=_runtime_freeze(),
            )
        )
        self.assertEqual(report["decision"], "DEC-354")
        self.assertEqual(
            report["stage"],
            (
                "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALLATION_"
                "SOURCE_AUTHORIZED_TEMPLATE_ABSENT_RUNTIME_LOCKED"
            ),
        )
        self.assertEqual(
            report["dormant_executor_workflow_template_path"],
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH,
        )
        self.assertEqual(
            report["expected_executor_workflow_path"],
            EXPECTED_EXECUTOR_WORKFLOW_PATH,
        )
        self.assertTrue(
            report[
                "one_shot_historical_executor_workflow_installation_source_authorized"
            ]
        )
        self.assertFalse(report["dormant_executor_workflow_template_present"])
        self.assertFalse(
            report["historical_executor_workflow_install_authorized"]
        )
        self.assertFalse(report["historical_executor_workflow_installed"])
        self.assertFalse(report["historical_executor_available"])
        self.assertFalse(report["historical_result_dispatch_authorized"])
        self.assertFalse(report["historical_execute_mode_available"])

    def test_public_constants_keep_runtime_locked(self) -> None:
        self.assertTrue(
            ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_INSTALLATION_SOURCE_AUTHORIZED
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
            build_one_shot_historical_executor_workflow_installation_source_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )

    def test_installed_state_escalation_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["historical_executor_workflow_installed"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_workflow_installed mismatch",
        ):
            build_one_shot_historical_executor_workflow_installation_source_contract(
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
            build_one_shot_historical_executor_workflow_installation_source_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )


if __name__ == "__main__":
    unittest.main()
