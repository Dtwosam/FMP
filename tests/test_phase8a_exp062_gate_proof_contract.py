from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from fmp.discovery.exp062_proof_contract import (
    MATRIX_TEMPLATE_JOB_NAME,
    proof_contract_payload,
    validate_gate_proof_terminal,
)
from fmp.discovery.exp062_run_contract import (
    AGGREGATE_JOB_NAME,
    PREFLIGHT_JOB_NAME,
    expected_cell_job_name,
    expected_preflight_artifact_name,
)
from fmp.discovery.exp062_workflow_source import (
    validate_exp062_workflow_source_dependencies,
    workflow_source_payload,
)


HEAD = "a" * 40
ROOT = Path(__file__).resolve().parents[1]


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


def _run(*, run_number: int = 1) -> dict[str, object]:
    return {
        "id": 123456,
        "name": "phase8a-exp062-discovery",
        "path": ".github/workflows/phase8a-exp062-discovery.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": HEAD,
        "run_number": run_number,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "failure",
    }


def _jobs_placeholder() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": 1,
                "name": PREFLIGHT_JOB_NAME,
                "status": "completed",
                "conclusion": "failure",
            },
            {
                "id": 2,
                "name": MATRIX_TEMPLATE_JOB_NAME,
                "status": "completed",
                "conclusion": "skipped",
            },
            {
                "id": 3,
                "name": AGGREGATE_JOB_NAME,
                "status": "completed",
                "conclusion": "skipped",
            },
        ]
    }


def _jobs_expanded() -> dict[str, object]:
    return {
        "jobs": [
            {
                "id": 1,
                "name": PREFLIGHT_JOB_NAME,
                "status": "completed",
                "conclusion": "failure",
            },
            {
                "id": 2,
                "name": expected_cell_job_name("EURUSD", "5m", 60),
                "status": "completed",
                "conclusion": "skipped",
            },
            {
                "id": 3,
                "name": AGGREGATE_JOB_NAME,
                "status": "completed",
                "conclusion": "skipped",
            },
        ]
    }


def _artifacts() -> dict[str, object]:
    return {
        "artifacts": [
            {
                "id": 999,
                "name": expected_preflight_artifact_name(
                    code_commit=HEAD
                ),
                "digest": "sha256:" + ("b" * 64),
                "expired": False,
            }
        ]
    }


def _preflight() -> dict[str, object]:
    value: dict[str, object] = {
        "decision": "DEC-299",
        "source_version": "fmp-exp062-dormant-workflow-source-v1",
        "experiment_id": "EXP-20260927-062",
        "predecessor_source_decision": "DEC-275",
        "predecessor_source_version": (
            "fmp-exp061-dormant-workflow-source-v1"
        ),
        "predecessor_source_fingerprint": "c" * 64,
        "feature_run_id": 35867307338,
        "feature_head_sha": "b71912e254d2a597c0ef55b5e1b3b87b052039ea",
        "outcome_run_id": 35876715434,
        "outcome_head_sha": "edeb43bb4de88923e3349caa8ace36350839ccb8",
        "feature_evidence_artifact_id": 10753455784,
        "outcome_evidence_artifact_id": 10758027876,
        "verified_pair_timeframe_source_count": 9,
        "source_ready": True,
        "nonfinite_to_null_repair_required": True,
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
    value["code_commit"] = HEAD
    value["workflow_source"] = workflow_source_payload(
        code_commit=HEAD
    )
    value["source_dependencies"] = (
        validate_exp062_workflow_source_dependencies(
            repository_root=ROOT,
        )
    )
    return value


class Exp062GateProofContractTests(unittest.TestCase):
    def test_contract_authorizes_nothing_and_consumes_no_slot(self) -> None:
        value = proof_contract_payload(expected_head_sha=HEAD)
        self.assertEqual(value["expected_proof_run_number"], 1)
        self.assertEqual(
            value["expected_terminal_run_conclusion"],
            "failure",
        )
        self.assertFalse(value["historical_result_slot_consumed"])
        for flag in value["authorizations"].values():
            self.assertFalse(flag)

    def test_placeholder_fail_closed_shape_is_reviewable(self) -> None:
        report = validate_gate_proof_terminal(
            run=_run(),
            jobs_payload=_jobs_placeholder(),
            artifacts_payload=_artifacts(),
            preflight_evidence=_preflight(),
            expected_head_sha=HEAD,
            repository_root=ROOT,
        )
        self.assertEqual(
            report["stage"],
            "EXP062_GATE_PROOF_REVIEWED_FAIL_CLOSED",
        )
        self.assertEqual(report["proof_run_number"], 1)
        self.assertTrue(
            report["github_unexpanded_matrix_placeholder_present"]
        )
        self.assertFalse(report["historical_result_slot_consumed"])
        self.assertFalse(
            report["historical_discovery_execution_occurred"]
        )
        self.assertEqual(report["cell_result_artifact_count"], 0)
        self.assertEqual(report["aggregate_result_artifact_count"], 0)

    def test_expanded_skipped_downstream_shape_is_reviewable(self) -> None:
        report = validate_gate_proof_terminal(
            run=_run(),
            jobs_payload=_jobs_expanded(),
            artifacts_payload=_artifacts(),
            preflight_evidence=_preflight(),
            expected_head_sha=HEAD,
            repository_root=ROOT,
        )
        self.assertFalse(
            report["github_unexpanded_matrix_placeholder_present"]
        )
        self.assertEqual(report["materialized_downstream_job_count"], 2)

    def test_run_number_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "run_number mismatch"):
            validate_gate_proof_terminal(
                run=_run(run_number=2),
                jobs_payload=_jobs_placeholder(),
                artifacts_payload=_artifacts(),
                preflight_evidence=_preflight(),
                expected_head_sha=HEAD,
                repository_root=ROOT,
            )

    def test_downstream_execution_is_rejected(self) -> None:
        jobs = _jobs_expanded()
        rows = jobs["jobs"]
        assert isinstance(rows, list)
        rows[1]["conclusion"] = "success"
        with self.assertRaisesRegex(
            ValueError,
            "downstream jobs must be skipped",
        ):
            validate_gate_proof_terminal(
                run=_run(),
                jobs_payload=jobs,
                artifacts_payload=_artifacts(),
                preflight_evidence=_preflight(),
                expected_head_sha=HEAD,
                repository_root=ROOT,
            )

    def test_placeholder_cannot_mix_with_expanded_cells(self) -> None:
        jobs = _jobs_placeholder()
        rows = jobs["jobs"]
        assert isinstance(rows, list)
        rows.insert(
            2,
            {
                "id": 4,
                "name": expected_cell_job_name("EURUSD", "5m", 60),
                "status": "completed",
                "conclusion": "skipped",
            },
        )
        with self.assertRaisesRegex(
            ValueError,
            "cannot mix matrix placeholder",
        ):
            validate_gate_proof_terminal(
                run=_run(),
                jobs_payload=jobs,
                artifacts_payload=_artifacts(),
                preflight_evidence=_preflight(),
                expected_head_sha=HEAD,
                repository_root=ROOT,
            )

    def test_source_dependency_tamper_is_rejected(self) -> None:
        preflight = _preflight()
        deps = dict(preflight["source_dependencies"])
        deps["experiment_id"] = "EXP-TAMPERED"
        preflight["source_dependencies"] = deps
        with self.assertRaisesRegex(
            ValueError,
            "source-dependency payload mismatch",
        ):
            validate_gate_proof_terminal(
                run=_run(),
                jobs_payload=_jobs_placeholder(),
                artifacts_payload=_artifacts(),
                preflight_evidence=preflight,
                expected_head_sha=HEAD,
                repository_root=ROOT,
            )


if __name__ == "__main__":
    unittest.main()
