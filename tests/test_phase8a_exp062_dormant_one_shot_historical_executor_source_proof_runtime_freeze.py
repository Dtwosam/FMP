from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_dormant_one_shot_executor_source_proof_runtime_freeze import (
    DEC358_FREEZE_FINGERPRINT_SHA256,
    DORMANT_SOURCE_CANONICAL_SHA256,
    DORMANT_SOURCE_PROOF_ARTIFACT_DIGEST,
    DORMANT_SOURCE_PROOF_ARTIFACT_ID,
    DORMANT_SOURCE_PROOF_HEAD_SHA,
    DORMANT_SOURCE_PROOF_JOB_ID,
    DORMANT_SOURCE_PROOF_RUN_ID,
    DORMANT_SOURCE_RAW_SHA256,
    freeze_dormant_one_shot_historical_executor_source_proof_runtime_evidence,
    validate_dormant_one_shot_historical_executor_source_proof_runtime_freeze_sources,
)


def _canonical_json(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _source_report() -> dict[str, object]:
    return {
        "active_discovery_workflow_blob_sha": (
            "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
        ),
        "active_discovery_workflow_path": (
            ".github/workflows/phase8a-exp062-discovery.yml"
        ),
        "broker_mutation_authorized": False,
        "candidate_compilation_authorized": False,
        "decision": "DEC-355",
        "demo_order_authorized": False,
        "discovery_result_authorized": True,
        "dormant_executor_workflow_template_blob_sha": (
            "51ce87584369be957482460d81649adb1cb9f05d"
        ),
        "dormant_executor_workflow_template_path": (
            "docs/superpowers/templates/"
            "phase8a-exp062-one-shot-historical-executor.yml.disabled"
        ),
        "dormant_executor_workflow_template_present": True,
        "dormant_template_actions_write_required_if_installed": True,
        "dormant_template_dispatch_capable_if_installed": True,
        "expected_executor_workflow_path": (
            ".github/workflows/phase8a-exp062-one-shot-historical-executor.yml"
        ),
        "expected_target_run_attempt": 1,
        "expected_target_run_number": 2,
        "historical_discovery_execution_authorized": True,
        "historical_execute_mode_available": False,
        "historical_executor_available": False,
        "historical_executor_workflow_install_authorized": False,
        "historical_executor_workflow_installed": False,
        "historical_gate_proof_run_id": 36358289723,
        "historical_result_attempt_count": 0,
        "historical_result_dispatch_authorized": False,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "installation_source_contract_decision": "DEC-354",
        "live_order_authorized": False,
        "next_gate": (
            "REPOSITORY_HOSTED_READ_ONLY_DORMANT_ONE_SHOT_HISTORICAL_"
            "EXECUTOR_WORKFLOW_SOURCE_PROOF"
        ),
        "phase8b_authorized": False,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ),
        "promotion_authorized": False,
        "real_money_authorized": False,
        "replacement_run_authorized": False,
        "rerun_authorized": False,
        "reserved_robustness_access_authorized": False,
        "retry_authorized": False,
        "source_blobs": {
            "active_discovery_workflow": (
                "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
            ),
            "dec354_installation_source_contract": (
                "e4fc6a7d1faaca50bc6936597f0e8b66fe096985"
            ),
            "dormant_executor_workflow_template": (
                "51ce87584369be957482460d81649adb1cb9f05d"
            ),
        },
        "stage": (
            "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_DORMANT_TEMPLATE_SOURCE_"
            "FROZEN_ACTIVE_WORKFLOW_UNINSTALLED"
        ),
        "trading_authorized": False,
        "version": (
            "fmp-exp062-one-shot-historical-executor-dormant-workflow-source-v1"
        ),
    }


def _source_bytes(value: dict[str, object] | None = None) -> bytes:
    payload = _source_report() if value is None else value
    return (
        json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def _run() -> dict[str, object]:
    return {
        "id": DORMANT_SOURCE_PROOF_RUN_ID,
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
        "head_sha": DORMANT_SOURCE_PROOF_HEAD_SHA,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _jobs() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": DORMANT_SOURCE_PROOF_JOB_ID,
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
                "id": DORMANT_SOURCE_PROOF_ARTIFACT_ID,
                "name": (
                    "exp062-dec356-dormant-one-shot-historical-executor-source-"
                    + DORMANT_SOURCE_PROOF_HEAD_SHA
                ),
                "digest": DORMANT_SOURCE_PROOF_ARTIFACT_DIGEST,
                "expired": False,
            }
        ]
    }


class Exp062DormantOneShotHistoricalExecutorSourceProofRuntimeFreezeTests(
    unittest.TestCase
):
    def _freeze(
        self,
        *,
        run: dict[str, object] | None = None,
        jobs: dict[str, object] | None = None,
        artifacts: dict[str, object] | None = None,
        source_bytes: bytes | None = None,
        artifact_zip_sha256: str | None = None,
    ) -> dict[str, object]:
        return freeze_dormant_one_shot_historical_executor_source_proof_runtime_evidence(
            repository_root=Path("."),
            proof_run=_run() if run is None else run,
            proof_jobs_payload=_jobs() if jobs is None else jobs,
            proof_artifacts_payload=(
                _artifacts() if artifacts is None else artifacts
            ),
            source_bytes=(
                _source_bytes() if source_bytes is None else source_bytes
            ),
            artifact_zip_sha256=(
                DORMANT_SOURCE_PROOF_ARTIFACT_DIGEST.removeprefix("sha256:")
                if artifact_zip_sha256 is None
                else artifact_zip_sha256
            ),
        )

    def test_source_bindings_pin_dec357_dec358_and_terminal_contract(self) -> None:
        report = (
            validate_dormant_one_shot_historical_executor_source_proof_runtime_freeze_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            report["dec357_reviewer"],
            "4c921577253fe7dcb74451299aecec4ad27fd522",
        )
        self.assertEqual(
            report["dec358_freeze_builder"],
            "878fa9e9be9d93c3ebd4c214a192cfb8ecdcc368",
        )
        self.assertEqual(
            report["dec334_terminal_review_contract"],
            "fda2a45f74b101303467cf7b8527bec1bfc5e168",
        )

    def test_exact_real_evidence_freezes_deterministically(self) -> None:
        first = self._freeze()
        second = self._freeze()
        self.assertEqual(first, second)
        self.assertEqual(
            first["stage"],
            (
                "EXP062_DORMANT_ONE_SHOT_HISTORICAL_EXECUTOR_SOURCE_PROOF_"
                "RUNTIME_EVIDENCE_BOUND_AND_FROZEN"
            ),
        )
        self.assertEqual(
            first["dormant_source_proof_run_id"],
            DORMANT_SOURCE_PROOF_RUN_ID,
        )
        self.assertEqual(
            first["dormant_source_proof_job_id"],
            DORMANT_SOURCE_PROOF_JOB_ID,
        )
        self.assertEqual(
            first["dormant_source_proof_artifact_id"],
            DORMANT_SOURCE_PROOF_ARTIFACT_ID,
        )
        self.assertEqual(
            first["dec358_freeze_fingerprint_sha256"],
            DEC358_FREEZE_FINGERPRINT_SHA256,
        )
        self.assertEqual(first["dec334_terminal_review_decision"], "DEC-334")
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
        self.assertFalse(first["demo_order_authorized"])
        self.assertFalse(first["live_order_authorized"])
        self.assertFalse(first["trading_authorized"])

        unsigned = dict(first)
        fingerprint = unsigned.pop("runtime_freeze_fingerprint_sha256")
        self.assertEqual(
            fingerprint,
            hashlib.sha256(_canonical_json(unsigned)).hexdigest(),
        )

    def test_source_fixture_matches_real_hashes(self) -> None:
        raw = _source_bytes()
        canonical = _canonical_json(_source_report())
        self.assertEqual(
            hashlib.sha256(raw).hexdigest(),
            DORMANT_SOURCE_RAW_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            DORMANT_SOURCE_CANONICAL_SHA256,
        )

    def test_wrong_run_id_is_rejected(self) -> None:
        run = _run()
        run["id"] = DORMANT_SOURCE_PROOF_RUN_ID + 1
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result proof_run_id mismatch",
        ):
            self._freeze(run=run)

    def test_wrong_job_id_is_rejected(self) -> None:
        jobs = _jobs()
        jobs["jobs"][0]["id"] = DORMANT_SOURCE_PROOF_JOB_ID + 1
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result proof_job_id mismatch",
        ):
            self._freeze(jobs=jobs)

    def test_wrong_artifact_id_is_rejected(self) -> None:
        artifacts = _artifacts()
        artifacts["artifacts"][0]["id"] = DORMANT_SOURCE_PROOF_ARTIFACT_ID + 1
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result proof_artifact_id mismatch",
        ):
            self._freeze(artifacts=artifacts)

    def test_artifact_zip_hash_mismatch_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "artifact ZIP sha256 mismatch",
        ):
            self._freeze(artifact_zip_sha256="0" * 64)

    def test_install_authority_escalation_is_rejected(self) -> None:
        source = _source_report()
        source["historical_executor_workflow_install_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_workflow_install_authorized",
        ):
            self._freeze(source_bytes=_source_bytes(source))

    def test_dispatch_authority_escalation_is_rejected(self) -> None:
        source = _source_report()
        source["historical_result_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_dispatch_authorized",
        ):
            self._freeze(source_bytes=_source_bytes(source))


if __name__ == "__main__":
    unittest.main()
