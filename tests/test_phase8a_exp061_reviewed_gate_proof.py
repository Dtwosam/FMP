from __future__ import annotations

import hashlib
import json
import unittest

from fmp.discovery.proof_result_decision import (
    DEC279_EXECUTOR_ARTIFACT_DIGEST,
    DEC279_EXECUTOR_ARTIFACT_ID,
    DEC279_EXECUTOR_RUN_ID,
    EXP061_GATE_PROOF_HEAD_SHA,
    EXP061_GATE_PROOF_PREFLIGHT_ARTIFACT_DIGEST,
    EXP061_GATE_PROOF_PREFLIGHT_ARTIFACT_ID,
    EXP061_GATE_PROOF_RUN_ID,
    EXP061_REVIEWED_GATE_PROOF_DECISION,
    freeze_reviewed_gate_proof,
)
from fmp.discovery.workflow_source import (
    EXP061_DORMANT_WORKFLOW_SOURCE_DECISION,
    EXP061_DORMANT_WORKFLOW_SOURCE_VERSION,
    FEATURE_EVIDENCE_ARTIFACT,
    FEATURE_RUN,
    OUTCOME_EVIDENCE_ARTIFACT,
    OUTCOME_RUN,
    workflow_source_payload,
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
        "id": DEC279_EXECUTOR_RUN_ID,
        "name": "phase8a-exp061-proof-one-shot-execute",
        "path": ".github/workflows/phase8a-exp061-proof-one-shot-execute.yml",
        "event": "push",
        "head_branch": "main",
        "head_sha": EXP061_GATE_PROOF_HEAD_SHA,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "success",
    }


def _executor_artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": DEC279_EXECUTOR_ARTIFACT_ID,
                "name": (
                    "exp061-dec279-proof-dispatch-evidence-"
                    + EXP061_GATE_PROOF_HEAD_SHA
                ),
                "digest": DEC279_EXECUTOR_ARTIFACT_DIGEST,
                "expired": False,
            }
        ]
    }


def _executor_evidence() -> dict[str, object]:
    command = "gh workflow run phase8a-exp061-discovery.yml --ref main"
    return {
        "decision": "DEC-278",
        "executor_decision": "DEC-279",
        "executor_version": "fmp-exp061-proof-one-shot-executor-v1",
        "expected_head_sha": EXP061_GATE_PROOF_HEAD_SHA,
        "executor_head_sha": EXP061_GATE_PROOF_HEAD_SHA,
        "fresh_plan_rechecked_twice": True,
        "matching_manual_main_run_count": 0,
        "planned_dispatch_command": command,
        "dispatch_command": command,
        "proof_contract_version": "fmp-exp061-gate-proof-contract-v1",
        "proof_dispatch_authorized": False,
        "proof_dispatch_authorized_by_dec279": True,
        "proof_dispatch_submitted": True,
        "proof_execute_mode_available": False,
        "historical_result_claimed": False,
        "historical_result_dispatch_authorized": False,
        "historical_result_slot_consumed": False,
        "historical_discovery_execution_authorized": False,
        "discovery_result_authorized": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }


def _proof_run() -> dict[str, object]:
    return {
        "id": EXP061_GATE_PROOF_RUN_ID,
        "name": "phase8a-exp061-discovery",
        "path": ".github/workflows/phase8a-exp061-discovery.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": EXP061_GATE_PROOF_HEAD_SHA,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "failure",
    }


def _jobs() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": 108621570094,
                "name": "exp061-preflight",
                "status": "completed",
                "conclusion": "failure",
            },
            {
                "id": 108621636801,
                "name": (
                    "exp061-cell-${{ matrix.dataset.symbol }}-"
                    "${{ matrix.dataset.timeframe }}-"
                    "${{ matrix.dataset.horizon }}m"
                ),
                "status": "completed",
                "conclusion": "skipped",
            },
            {
                "id": 108621637326,
                "name": "exp061-aggregate",
                "status": "completed",
                "conclusion": "skipped",
            },
        ]
    }


def _proof_artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": EXP061_GATE_PROOF_PREFLIGHT_ARTIFACT_ID,
                "name": "phase8a-exp061-preflight-" + EXP061_GATE_PROOF_HEAD_SHA,
                "digest": EXP061_GATE_PROOF_PREFLIGHT_ARTIFACT_DIGEST,
                "expired": False,
            }
        ]
    }


def _preflight() -> dict[str, object]:
    value: dict[str, object] = {
        "decision": EXP061_DORMANT_WORKFLOW_SOURCE_DECISION,
        "source_version": EXP061_DORMANT_WORKFLOW_SOURCE_VERSION,
        "feature_run_id": FEATURE_RUN["id"],
        "feature_head_sha": FEATURE_RUN["head_sha"],
        "outcome_run_id": OUTCOME_RUN["id"],
        "outcome_head_sha": OUTCOME_RUN["head_sha"],
        "feature_evidence_artifact_id": FEATURE_EVIDENCE_ARTIFACT["id"],
        "outcome_evidence_artifact_id": OUTCOME_EVIDENCE_ARTIFACT["id"],
        "verified_pair_timeframe_source_count": 9,
        "source_ready": True,
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
    }
    value["source_fingerprint"] = hashlib.sha256(
        _canonical_json(value)
    ).hexdigest()
    value["code_commit"] = EXP061_GATE_PROOF_HEAD_SHA
    value["workflow_source"] = workflow_source_payload(
        code_commit=EXP061_GATE_PROOF_HEAD_SHA
    )
    return value


def _review() -> dict[str, object]:
    return freeze_reviewed_gate_proof(
        executor_run=_executor_run(),
        executor_artifacts_payload=_executor_artifacts(),
        executor_evidence=_executor_evidence(),
        proof_run=_proof_run(),
        jobs_payload=_jobs(),
        proof_artifacts_payload=_proof_artifacts(),
        preflight_evidence=_preflight(),
    )


class Exp061ReviewedGateProofTests(unittest.TestCase):
    def test_exact_real_proof_is_frozen_fail_closed(self) -> None:
        report = _review()
        self.assertEqual(report["decision"], EXP061_REVIEWED_GATE_PROOF_DECISION)
        self.assertEqual(
            report["stage"],
            "EXP061_GATE_PROOF_REVIEWED_FAIL_CLOSED_AND_FROZEN",
        )
        self.assertEqual(report["proof_outcome"], "EXPECTED_FAIL_CLOSED_EXECUTION_GATE")
        self.assertFalse(report["dec277_exact_downstream_job_name_compatible"])
        self.assertTrue(report["fail_closed_semantics_verified"])
        self.assertFalse(report["historical_result_slot_consumed"])
        self.assertFalse(report["historical_discovery_execution_occurred"])
        self.assertEqual(report["cell_result_artifact_count"], 0)
        self.assertEqual(report["aggregate_result_artifact_count"], 0)
        for field in (
            "proof_rerun_authorized",
            "proof_retry_authorized",
            "proof_replacement_authorized",
            "historical_result_dispatch_authorized",
            "historical_discovery_execution_authorized",
            "discovery_result_authorized",
            "reserved_robustness_access_authorized",
            "candidate_compilation_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(report[field])

    def test_expanding_the_skipped_matrix_name_after_the_fact_is_rejected(self) -> None:
        jobs = _jobs()
        rows = jobs["jobs"]
        assert isinstance(rows, list)
        rows[1]["name"] = "exp061-cell-EURUSD-5m-60m"
        with self.assertRaisesRegex(ValueError, "proof job 108621636801 name mismatch"):
            freeze_reviewed_gate_proof(
                executor_run=_executor_run(),
                executor_artifacts_payload=_executor_artifacts(),
                executor_evidence=_executor_evidence(),
                proof_run=_proof_run(),
                jobs_payload=jobs,
                proof_artifacts_payload=_proof_artifacts(),
                preflight_evidence=_preflight(),
            )

    def test_any_downstream_execution_is_rejected(self) -> None:
        jobs = _jobs()
        rows = jobs["jobs"]
        assert isinstance(rows, list)
        rows[1]["conclusion"] = "success"
        with self.assertRaisesRegex(
            ValueError,
            "proof job 108621636801 conclusion mismatch",
        ):
            freeze_reviewed_gate_proof(
                executor_run=_executor_run(),
                executor_artifacts_payload=_executor_artifacts(),
                executor_evidence=_executor_evidence(),
                proof_run=_proof_run(),
                jobs_payload=jobs,
                proof_artifacts_payload=_proof_artifacts(),
                preflight_evidence=_preflight(),
            )

    def test_executor_or_artifact_identity_drift_is_rejected(self) -> None:
        artifacts = _executor_artifacts()
        rows = artifacts["artifacts"]
        assert isinstance(rows, list)
        rows[0]["digest"] = "sha256:" + ("0" * 64)
        with self.assertRaisesRegex(ValueError, "executor artifact digest mismatch"):
            freeze_reviewed_gate_proof(
                executor_run=_executor_run(),
                executor_artifacts_payload=artifacts,
                executor_evidence=_executor_evidence(),
                proof_run=_proof_run(),
                jobs_payload=_jobs(),
                proof_artifacts_payload=_proof_artifacts(),
                preflight_evidence=_preflight(),
            )

    def test_preflight_tamper_is_rejected_even_if_refingerprinted(self) -> None:
        preflight = _preflight()
        preflight["source_ready"] = False
        unsigned = dict(preflight)
        unsigned.pop("source_fingerprint", None)
        unsigned.pop("code_commit", None)
        unsigned.pop("workflow_source", None)
        preflight["source_fingerprint"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(ValueError, "preflight evidence source_ready mismatch"):
            freeze_reviewed_gate_proof(
                executor_run=_executor_run(),
                executor_artifacts_payload=_executor_artifacts(),
                executor_evidence=_executor_evidence(),
                proof_run=_proof_run(),
                jobs_payload=_jobs(),
                proof_artifacts_payload=_proof_artifacts(),
                preflight_evidence=preflight,
            )


if __name__ == "__main__":
    unittest.main()
