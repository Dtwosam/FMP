from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_one_shot_executor_workflow_contract import (
    HISTORICAL_EXECUTOR_AVAILABLE,
    HISTORICAL_EXECUTE_MODE_AVAILABLE,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_SOURCE_AUTHORIZED,
    build_one_shot_historical_executor_workflow_contract,
    validate_one_shot_historical_executor_workflow_contract_sources,
)


def _runtime_freeze() -> dict[str, object]:
    return {
        "decision": "DEC-341",
        "version": (
            "fmp-exp062-one-shot-historical-executor-source-proof-"
            "runtime-freeze-v1"
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
            "RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
        ),
        "source_proof_head_sha": (
            "e9dfbf034614b54598d31653da3868ed66aa90ba"
        ),
        "source_proof_run_id": 36442399041,
        "source_proof_run_number": 1,
        "source_proof_run_attempt": 1,
        "source_proof_run_conclusion": "success",
        "source_proof_job_id": 108995955292,
        "source_proof_artifact_id": 10979242048,
        "source_proof_artifact_name": (
            "exp062-dec338-one-shot-historical-executor-source-"
            "e9dfbf034614b54598d31653da3868ed66aa90ba"
        ),
        "source_proof_artifact_digest": (
            "sha256:7dff775fc559cf9dbd754f45c24fbc814035b1602b59ca5eb9f82678af4e8b88"
        ),
        "source_proof_artifact_zip_sha256": (
            "7dff775fc559cf9dbd754f45c24fbc814035b1602b59ca5eb9f82678af4e8b88"
        ),
        "source_contract_raw_sha256": (
            "484ad49fa3b3e925ae4a3576af840a8736c9b25ef439b619e8b60e8011f94d63"
        ),
        "source_contract_canonical_sha256": (
            "cb650b81c2549bfb5bfa62f6609bec9b39e4ed118f3e54c302a48a3a27a11616"
        ),
        "dec339_review_decision": "DEC-339",
        "dec339_review_version": (
            "fmp-exp062-one-shot-historical-executor-source-proof-review-v1"
        ),
        "dec340_freeze_decision": "DEC-340",
        "dec340_freeze_version": (
            "fmp-exp062-one-shot-historical-executor-source-proof-freeze-v1"
        ),
        "dec340_freeze_fingerprint_sha256": (
            "e340394fb987c68d9203a57c9cd363f255729b3424a9600ec03533ff421960a8"
        ),
        "dec334_terminal_review_decision": "DEC-334",
        "dec334_terminal_review_version": (
            "fmp-exp062-historical-terminal-review-contract-v1"
        ),
        "dec339_reviewer_blob_sha": (
            "673bfc55bffa908f793a9dbc36d7aed1f4a13784"
        ),
        "dec340_freeze_builder_blob_sha": (
            "804e9a57be2a114f8754334f89f9f5b883d1cee5"
        ),
        "dec334_terminal_review_contract_blob_sha": (
            "fda2a45f74b101303467cf7b8527bec1bfc5e168"
        ),
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "one_shot_historical_executor_source_authorized": True,
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
            "SOURCE_ONLY_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_CONTRACT"
        ),
        "runtime_freeze_fingerprint_sha256": (
            "7375b8fa30a425d660e6a0c392eb6c0084d9f0bb65c7b141d5ef11a6459650da"
        ),
    }


class Exp062OneShotHistoricalExecutorWorkflowContractTests(unittest.TestCase):
    def test_contract_authorizes_workflow_source_only(self) -> None:
        source = validate_one_shot_historical_executor_workflow_contract_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["dec341_runtime_freeze_blob_sha"],
            "b99a2f453423734a92d79d8f8d1c2fa1fa20d45f",
        )

        report = build_one_shot_historical_executor_workflow_contract(
            repository_root=Path("."),
            runtime_freeze=_runtime_freeze(),
        )
        self.assertEqual(report["decision"], "DEC-342")
        self.assertEqual(
            report["stage"],
            (
                "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_SOURCE_"
                "AUTHORIZED_RUNTIME_LOCKED"
            ),
        )
        self.assertTrue(
            report["one_shot_historical_executor_workflow_source_authorized"]
        )
        self.assertTrue(
            report["one_shot_historical_executor_source_authorized"]
        )
        self.assertFalse(report["historical_executor_available"])
        self.assertFalse(report["historical_result_dispatch_authorized"])
        self.assertFalse(report["historical_execute_mode_available"])
        self.assertFalse(report["historical_result_slot_consumed"])
        self.assertTrue(report["historical_result_slot_verified_available"])
        self.assertEqual(report["expected_target_run_number"], 2)
        self.assertEqual(report["expected_target_run_attempt"], 1)
        self.assertFalse(report["candidate_compilation_authorized"])
        self.assertFalse(report["demo_order_authorized"])
        self.assertFalse(report["live_order_authorized"])
        self.assertFalse(report["trading_authorized"])

    def test_public_constants_keep_runtime_locked(self) -> None:
        self.assertTrue(ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_SOURCE_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTOR_AVAILABLE)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_EXECUTE_MODE_AVAILABLE)

    def test_runtime_freeze_fingerprint_drift_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["runtime_freeze_fingerprint_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint mismatch"):
            build_one_shot_historical_executor_workflow_contract(
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
            build_one_shot_historical_executor_workflow_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )

    def test_executor_availability_escalation_is_rejected(self) -> None:
        value = _runtime_freeze()
        value["historical_executor_available"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_available mismatch",
        ):
            build_one_shot_historical_executor_workflow_contract(
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
            build_one_shot_historical_executor_workflow_contract(
                repository_root=Path("."),
                runtime_freeze=value,
            )


if __name__ == "__main__":
    unittest.main()
