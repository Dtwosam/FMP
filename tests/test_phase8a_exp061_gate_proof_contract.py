from __future__ import annotations

import hashlib
import json
import unittest

from fmp.discovery.proof_contract import (
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    PROOF_DISPATCH_AUTHORIZED,
    proof_contract_payload,
    validate_gate_proof_terminal,
)
from fmp.discovery.run_contract import (
    AGGREGATE_JOB_NAME,
    PREFLIGHT_JOB_NAME,
    expected_cell_job_name,
    expected_preflight_artifact_name,
)
from fmp.discovery.workflow_source import (
    FEATURE_EVIDENCE_ARTIFACT,
    FEATURE_RUN,
    OUTCOME_EVIDENCE_ARTIFACT,
    OUTCOME_RUN,
    workflow_source_payload,
)


HEAD = "a" * 40
RUN_ID = 123456


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


def _run() -> dict[str, object]:
    return {
        "id": RUN_ID,
        "name": "phase8a-exp061-discovery",
        "path": ".github/workflows/phase8a-exp061-discovery.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": HEAD,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "failure",
    }


def _jobs() -> dict[str, object]:
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
                "name": expected_preflight_artifact_name(code_commit=HEAD),
                "digest": "sha256:" + ("b" * 64),
                "expired": False,
            }
        ]
    }


def _preflight() -> dict[str, object]:
    value: dict[str, object] = {
        "decision": "DEC-275",
        "source_version": "fmp-exp061-dormant-workflow-source-v1",
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
    value["code_commit"] = HEAD
    value["workflow_source"] = workflow_source_payload(code_commit=HEAD)
    return value


class Exp061GateProofContractTests(unittest.TestCase):
    def test_contract_authorizes_nothing(self) -> None:
        payload = proof_contract_payload(expected_head_sha=HEAD)
        self.assertEqual(payload["expected_terminal_run_conclusion"], "failure")
        self.assertFalse(payload["historical_result_slot_consumed"])
        for value in payload["authorizations"].values():
            self.assertFalse(value)
        self.assertFalse(PROOF_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)

    def test_fail_closed_terminal_shape_is_reviewable(self) -> None:
        report = validate_gate_proof_terminal(
            run=_run(),
            jobs_payload=_jobs(),
            artifacts_payload=_artifacts(),
            preflight_evidence=_preflight(),
            expected_head_sha=HEAD,
        )
        self.assertEqual(
            report["stage"],
            "EXP061_GATE_PROOF_REVIEWED_FAIL_CLOSED",
        )
        self.assertFalse(report["historical_result_slot_consumed"])
        self.assertFalse(report["historical_discovery_execution_occurred"])
        self.assertEqual(report["cell_result_artifact_count"], 0)
        self.assertEqual(report["aggregate_result_artifact_count"], 0)
        self.assertEqual(report["materialized_downstream_job_count"], 2)

    def test_any_downstream_execution_fails_proof(self) -> None:
        jobs = _jobs()
        rows = jobs["jobs"]
        assert isinstance(rows, list)
        rows[1]["conclusion"] = "success"
        with self.assertRaisesRegex(ValueError, "downstream jobs must be skipped"):
            validate_gate_proof_terminal(
                run=_run(),
                jobs_payload=jobs,
                artifacts_payload=_artifacts(),
                preflight_evidence=_preflight(),
                expected_head_sha=HEAD,
            )

    def test_cell_or_aggregate_artifact_fails_proof(self) -> None:
        artifacts = _artifacts()
        rows = artifacts["artifacts"]
        assert isinstance(rows, list)
        rows.append(
            {
                "id": 1000,
                "name": f"phase8a-exp061-cell-EURUSD-5m-60m-{HEAD}",
                "digest": "sha256:" + ("c" * 64),
                "expired": False,
            }
        )
        with self.assertRaisesRegex(ValueError, "exactly one preflight artifact"):
            validate_gate_proof_terminal(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=artifacts,
                preflight_evidence=_preflight(),
                expected_head_sha=HEAD,
            )

    def test_re_fingerprinted_or_changed_preflight_fails(self) -> None:
        preflight = _preflight()
        preflight["source_ready"] = False
        unsigned = dict(preflight)
        unsigned.pop("source_fingerprint", None)
        unsigned.pop("code_commit", None)
        unsigned.pop("workflow_source", None)
        preflight["source_fingerprint"] = hashlib.sha256(
            _canonical_json(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(ValueError, "source preflight must be ready"):
            validate_gate_proof_terminal(
                run=_run(),
                jobs_payload=_jobs(),
                artifacts_payload=_artifacts(),
                preflight_evidence=preflight,
                expected_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
