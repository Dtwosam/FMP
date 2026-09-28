from __future__ import annotations

import hashlib
import json
import unittest

from fmp.discovery.exp062_runtime_proof_freeze import (
    DEC305_FREEZE_FINGERPRINT_SHA256,
    EXECUTOR_ARTIFACT_DIGEST,
    EXECUTOR_ARTIFACT_ID,
    EXECUTOR_ARTIFACT_NAME,
    EXECUTOR_RUN_ID,
    EXPECTED_EVIDENCE_HASHES,
    EXP062_RUNTIME_GATE_PROOF_FREEZE_DECISION,
    PROOF_AGGREGATE_JOB_ID,
    PROOF_HEAD_SHA,
    PROOF_MATRIX_JOB_ID,
    PROOF_MATRIX_JOB_NAME,
    PROOF_PREFLIGHT_ARTIFACT_DIGEST,
    PROOF_PREFLIGHT_ARTIFACT_ID,
    PROOF_PREFLIGHT_ARTIFACT_NAME,
    PROOF_PREFLIGHT_JOB_ID,
    PROOF_RUN_ID,
    freeze_runtime_gate_proof_evidence,
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


def _executor_run() -> dict[str, object]:
    return {
        "id": EXECUTOR_RUN_ID,
        "name": "phase8a-exp062-proof-one-shot-execute",
        "path": ".github/workflows/phase8a-exp062-proof-one-shot-execute.yml",
        "event": "push",
        "head_branch": "main",
        "head_sha": PROOF_HEAD_SHA,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _executor_artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": EXECUTOR_ARTIFACT_ID,
                "name": EXECUTOR_ARTIFACT_NAME,
                "digest": EXECUTOR_ARTIFACT_DIGEST,
                "expired": False,
            }
        ]
    }


def _proof_run() -> dict[str, object]:
    return {
        "id": PROOF_RUN_ID,
        "name": "phase8a-exp062-discovery",
        "path": ".github/workflows/phase8a-exp062-discovery.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": PROOF_HEAD_SHA,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "failure",
    }


def _proof_jobs() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": PROOF_PREFLIGHT_JOB_ID,
                "name": "exp062-preflight",
                "status": "completed",
                "conclusion": "failure",
            },
            {
                "id": PROOF_MATRIX_JOB_ID,
                "name": PROOF_MATRIX_JOB_NAME,
                "status": "completed",
                "conclusion": "skipped",
            },
            {
                "id": PROOF_AGGREGATE_JOB_ID,
                "name": "exp062-aggregate",
                "status": "completed",
                "conclusion": "skipped",
            },
        ]
    }


def _proof_artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": PROOF_PREFLIGHT_ARTIFACT_ID,
                "name": PROOF_PREFLIGHT_ARTIFACT_NAME,
                "digest": PROOF_PREFLIGHT_ARTIFACT_DIGEST,
                "expired": False,
            }
        ]
    }


def _dec305_freeze() -> dict[str, object]:
    return {
        "decision": "DEC-305",
        "version": "fmp-exp062-reviewed-gate-proof-freeze-v1",
        "stage": "EXP062_GATE_PROOF_REVIEWED_FAIL_CLOSED_AND_FROZEN",
        "source_review_decision": "DEC-304",
        "source_review_version": "fmp-exp062-proof-result-review-v1",
        "proof_contract_decision": "DEC-301",
        "proof_contract_version": "fmp-exp062-gate-proof-contract-v1",
        "proof_executor_decision": "DEC-303",
        "proof_executor_version": "fmp-exp062-proof-one-shot-executor-v1",
        "proof_outcome": "EXPECTED_FAIL_CLOSED_EXECUTION_GATE",
        "proof_run_id": PROOF_RUN_ID,
        "proof_head_sha": PROOF_HEAD_SHA,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "failure",
        "preflight_artifact_id": PROOF_PREFLIGHT_ARTIFACT_ID,
        "preflight_artifact_digest": PROOF_PREFLIGHT_ARTIFACT_DIGEST,
        "materialized_job_count": 3,
        "materialized_downstream_job_count": 2,
        "materialized_downstream_job_names": [
            "exp062-aggregate",
            PROOF_MATRIX_JOB_NAME,
        ],
        "github_unexpanded_matrix_placeholder_present": True,
        "fail_closed_semantics_verified": True,
        "cell_result_artifact_count": 0,
        "aggregate_result_artifact_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_open_authorized": False,
        "historical_discovery_execution_occurred": False,
        "proof_rerun_authorized": False,
        "proof_retry_authorized": False,
        "proof_replacement_authorized": False,
        "historical_result_dispatch_authorized": False,
        "historical_discovery_execution_authorized": False,
        "discovery_result_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "freeze_fingerprint_sha256": DEC305_FREEZE_FINGERPRINT_SHA256,
        "next_gate": "SOURCE_ONLY_HISTORICAL_RUN_AUTHORIZATION_CONTRACT",
    }


def _freeze() -> dict[str, object]:
    return freeze_runtime_gate_proof_evidence(
        executor_run=_executor_run(),
        executor_artifacts_payload=_executor_artifacts(),
        proof_run=_proof_run(),
        proof_jobs_payload=_proof_jobs(),
        proof_artifacts_payload=_proof_artifacts(),
        evidence_hashes=dict(EXPECTED_EVIDENCE_HASHES),
        reviewed_freeze=_dec305_freeze(),
    )


class Exp062RuntimeProofFreezeTests(unittest.TestCase):
    def test_exact_runtime_evidence_freezes_without_authority(self) -> None:
        first = _freeze()
        second = _freeze()
        self.assertEqual(first, second)
        self.assertEqual(
            first["decision"],
            EXP062_RUNTIME_GATE_PROOF_FREEZE_DECISION,
        )
        self.assertEqual(
            first["stage"],
            "EXP062_GATE_PROOF_RUNTIME_EVIDENCE_BOUND_AND_FROZEN",
        )
        self.assertEqual(first["executor_run_id"], EXECUTOR_RUN_ID)
        self.assertEqual(first["proof_run_id"], PROOF_RUN_ID)
        self.assertTrue(first["fail_closed_semantics_verified"])
        self.assertFalse(first["historical_result_slot_open_authorized"])
        self.assertFalse(first["historical_result_dispatch_authorized"])
        self.assertFalse(first["historical_discovery_execution_authorized"])
        self.assertFalse(first["reserved_robustness_access_authorized"])
        self.assertFalse(first["demo_order_authorized"])
        self.assertFalse(first["live_order_authorized"])
        self.assertFalse(first["trading_authorized"])
        self.assertEqual(
            first["next_gate"],
            "SOURCE_ONLY_HISTORICAL_RUN_AUTHORIZATION_CONTRACT",
        )

        unsigned = dict(first)
        fingerprint = unsigned.pop("runtime_freeze_fingerprint_sha256")
        self.assertEqual(
            fingerprint,
            hashlib.sha256(_canonical_json(unsigned)).hexdigest(),
        )

    def test_wrong_executor_artifact_is_rejected(self) -> None:
        artifacts = _executor_artifacts()
        artifacts["artifacts"][0]["id"] = EXECUTOR_ARTIFACT_ID + 1
        with self.assertRaisesRegex(ValueError, "executor artifact id mismatch"):
            freeze_runtime_gate_proof_evidence(
                executor_run=_executor_run(),
                executor_artifacts_payload=artifacts,
                proof_run=_proof_run(),
                proof_jobs_payload=_proof_jobs(),
                proof_artifacts_payload=_proof_artifacts(),
                evidence_hashes=dict(EXPECTED_EVIDENCE_HASHES),
                reviewed_freeze=_dec305_freeze(),
            )

    def test_wrong_proof_job_shape_is_rejected(self) -> None:
        jobs = _proof_jobs()
        jobs["jobs"][2]["conclusion"] = "success"
        with self.assertRaisesRegex(
            ValueError,
            "proof job .* conclusion mismatch",
        ):
            freeze_runtime_gate_proof_evidence(
                executor_run=_executor_run(),
                executor_artifacts_payload=_executor_artifacts(),
                proof_run=_proof_run(),
                proof_jobs_payload=jobs,
                proof_artifacts_payload=_proof_artifacts(),
                evidence_hashes=dict(EXPECTED_EVIDENCE_HASHES),
                reviewed_freeze=_dec305_freeze(),
            )

    def test_wrong_evidence_hash_is_rejected(self) -> None:
        hashes = dict(EXPECTED_EVIDENCE_HASHES)
        hashes["preflight_raw_sha256"] = "0" * 64
        with self.assertRaisesRegex(
            ValueError,
            "evidence preflight_raw_sha256 mismatch",
        ):
            freeze_runtime_gate_proof_evidence(
                executor_run=_executor_run(),
                executor_artifacts_payload=_executor_artifacts(),
                proof_run=_proof_run(),
                proof_jobs_payload=_proof_jobs(),
                proof_artifacts_payload=_proof_artifacts(),
                evidence_hashes=hashes,
                reviewed_freeze=_dec305_freeze(),
            )

    def test_wrong_dec305_fingerprint_is_rejected(self) -> None:
        frozen = _dec305_freeze()
        frozen["freeze_fingerprint_sha256"] = "0" * 64
        with self.assertRaisesRegex(
            ValueError,
            "freeze freeze_fingerprint_sha256 mismatch",
        ):
            freeze_runtime_gate_proof_evidence(
                executor_run=_executor_run(),
                executor_artifacts_payload=_executor_artifacts(),
                proof_run=_proof_run(),
                proof_jobs_payload=_proof_jobs(),
                proof_artifacts_payload=_proof_artifacts(),
                evidence_hashes=dict(EXPECTED_EVIDENCE_HASHES),
                reviewed_freeze=frozen,
            )

    def test_authority_escalation_is_rejected(self) -> None:
        frozen = _dec305_freeze()
        frozen["historical_result_slot_open_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_slot_open_authorized must remain false",
        ):
            freeze_runtime_gate_proof_evidence(
                executor_run=_executor_run(),
                executor_artifacts_payload=_executor_artifacts(),
                proof_run=_proof_run(),
                proof_jobs_payload=_proof_jobs(),
                proof_artifacts_payload=_proof_artifacts(),
                evidence_hashes=dict(EXPECTED_EVIDENCE_HASHES),
                reviewed_freeze=frozen,
            )


if __name__ == "__main__":
    unittest.main()
