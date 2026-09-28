from __future__ import annotations

import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_dormant_one_shot_executor_source_proof_review import (
    EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_DECISION,
    review_dormant_one_shot_historical_executor_source_proof,
    validate_dormant_one_shot_historical_executor_source_proof_review_sources,
)


HEAD = "a" * 40


def _source() -> dict[str, object]:
    return {
        "decision": "DEC-355",
        "version": (
            "fmp-exp062-one-shot-historical-executor-dormant-workflow-source-v1"
        ),
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_DORMANT_TEMPLATE_SOURCE_"
            "FROZEN_ACTIVE_WORKFLOW_UNINSTALLED"
        ),
        "source_blobs": {
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
        "installation_source_contract_decision": "DEC-354",
        "dormant_executor_workflow_template_path": (
            "docs/superpowers/templates/"
            "phase8a-exp062-one-shot-historical-executor.yml.disabled"
        ),
        "dormant_executor_workflow_template_blob_sha": (
            "51ce87584369be957482460d81649adb1cb9f05d"
        ),
        "expected_executor_workflow_path": (
            ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
        ),
        "active_discovery_workflow_path": (
            ".github/workflows/phase8a-exp062-discovery.yml"
        ),
        "active_discovery_workflow_blob_sha": (
            "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
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
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
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
            "REPOSITORY_HOSTED_READ_ONLY_DORMANT_ONE_SHOT_HISTORICAL_"
            "EXECUTOR_WORKFLOW_SOURCE_PROOF"
        ),
    }


def _source_bytes(value: dict[str, object] | None = None) -> bytes:
    payload = _source() if value is None else value
    return (
        json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def _run() -> dict[str, object]:
    return {
        "id": 40000000001,
        "name": (
            "phase8a-exp062-dormant-one-shot-historical-executor-"
            "workflow-source-proof"
        ),
        "path": (
            ".github/workflows/"
            "phase8a-exp062-dormant-one-shot-historical-executor-"
            "workflow-source-proof.yml"
        ),
        "event": "push",
        "head_branch": "main",
        "head_sha": HEAD,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": 50000000001,
                "name": (
                    "read-only-dormant-one-shot-historical-executor-"
                    "workflow-source-proof"
                ),
                "status": "completed",
                "conclusion": "success",
            }
        ]
    }


def _artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": 60000000001,
                "name": (
                    "exp062-dec356-dormant-one-shot-historical-executor-source-"
                    + HEAD
                ),
                "digest": "sha256:" + ("1" * 64),
                "expired": False,
            }
        ]
    }


class Exp062DormantOneShotHistoricalExecutorSourceProofReviewTests(
    unittest.TestCase
):
    def _review(
        self,
        *,
        run: dict[str, object] | None = None,
        jobs: dict[str, object] | None = None,
        artifacts: dict[str, object] | None = None,
        source_bytes: bytes | None = None,
    ) -> dict[str, object]:
        return review_dormant_one_shot_historical_executor_source_proof(
            run=_run() if run is None else run,
            jobs_payload=_jobs() if jobs is None else jobs,
            artifacts_payload=_artifacts() if artifacts is None else artifacts,
            source_bytes=(
                _source_bytes() if source_bytes is None else source_bytes
            ),
            expected_head_sha=HEAD,
            repository_root=Path("."),
        )

    def test_source_bindings_pin_dec356_and_dormant_chain(self) -> None:
        report = (
            validate_dormant_one_shot_historical_executor_source_proof_review_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            report["dec356_workflow"],
            "1cf665417e32c6810bf8ff62e5bc4a3b7a1ac598",
        )
        self.assertEqual(
            report["dec355_source"],
            "0672310946ab6bb3b77d2de5c4ea5d68e41f810a",
        )
        self.assertEqual(
            report["dormant_executor_workflow_template"],
            "51ce87584369be957482460d81649adb1cb9f05d",
        )

    def test_valid_proof_reviews_without_install_or_runtime_authority(self) -> None:
        first = self._review()
        second = self._review()
        self.assertEqual(first, second)
        self.assertEqual(
            first["decision"],
            EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_REVIEW_DECISION,
        )
        self.assertTrue(first["dormant_executor_workflow_template_present"])
        self.assertTrue(
            first["dormant_template_dispatch_capable_if_installed"]
        )
        self.assertFalse(
            first["historical_executor_workflow_install_authorized"]
        )
        self.assertFalse(first["historical_executor_workflow_installed"])
        self.assertFalse(first["historical_executor_available"])
        self.assertFalse(first["historical_result_dispatch_authorized"])
        self.assertFalse(first["historical_execute_mode_available"])
        self.assertEqual(first["historical_result_attempt_count"], 0)
        self.assertFalse(first["historical_result_slot_consumed"])

    def test_wrong_run_head_is_rejected(self) -> None:
        run = _run()
        run["head_sha"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "run head_sha mismatch"):
            self._review(run=run)

    def test_expired_artifact_is_rejected(self) -> None:
        artifacts = _artifacts()
        artifacts["artifacts"][0]["expired"] = True
        with self.assertRaisesRegex(ValueError, "must be non-expired"):
            self._review(artifacts=artifacts)

    def test_installed_state_escalation_is_rejected(self) -> None:
        source = _source()
        source["historical_executor_workflow_installed"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_workflow_installed",
        ):
            self._review(source_bytes=_source_bytes(source))

    def test_dispatch_authority_escalation_is_rejected(self) -> None:
        source = _source()
        source["historical_result_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_dispatch_authorized",
        ):
            self._review(source_bytes=_source_bytes(source))

    def test_invalid_json_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            self._review(source_bytes=b"{not-json")


if __name__ == "__main__":
    unittest.main()
