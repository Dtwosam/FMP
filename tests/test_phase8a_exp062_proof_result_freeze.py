from __future__ import annotations

import hashlib
import json
import unittest

from fmp.discovery.exp062_proof_result_freeze import (
    EXP062_REVIEWED_GATE_PROOF_FREEZE_DECISION,
    freeze_reviewed_gate_proof_result,
)


HEAD = "a" * 40


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


def _reviewed() -> dict[str, object]:
    placeholder = (
        "exp062-cell-" + "$" + "{{ matrix.dataset.symbol }}-"
        + "$" + "{{ matrix.dataset.timeframe }}-"
        + "$" + "{{ matrix.dataset.horizon }}m"
    )
    return {
        "decision": "DEC-304",
        "version": "fmp-exp062-proof-result-review-v1",
        "stage": "EXP062_GATE_PROOF_RESULT_REVIEWED_FAIL_CLOSED",
        "proof_contract_decision": "DEC-301",
        "proof_contract_version": "fmp-exp062-gate-proof-contract-v1",
        "proof_executor_decision": "DEC-303",
        "proof_executor_version": "fmp-exp062-proof-one-shot-executor-v1",
        "proof_run_id": 40000000000,
        "proof_head_sha": HEAD,
        "proof_run_number": 1,
        "proof_run_attempt": 1,
        "proof_run_conclusion": "failure",
        "preflight_artifact_id": 50000000000,
        "preflight_artifact_digest": "sha256:" + ("1" * 64),
        "materialized_job_count": 3,
        "materialized_downstream_job_count": 2,
        "materialized_downstream_job_names": [
            "exp062-aggregate",
            placeholder,
        ],
        "github_unexpanded_matrix_placeholder_present": True,
        "historical_result_slot_consumed": False,
        "historical_result_slot_open_authorized": False,
        "historical_discovery_execution_occurred": False,
        "cell_result_artifact_count": 0,
        "aggregate_result_artifact_count": 0,
        "proof_dispatch_submitted": True,
        "proof_dispatch_authorized": False,
        "historical_result_dispatch_authorized": False,
        "historical_discovery_execution_authorized": False,
        "discovery_result_authorized": False,
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
            "IMMUTABLE_PROOF_RESULT_FREEZE_BEFORE_HISTORICAL_SLOT"
        ),
    }


class Exp062ProofResultFreezeTests(unittest.TestCase):
    def test_reviewed_result_freezes_deterministically_without_authority(
        self,
    ) -> None:
        first = freeze_reviewed_gate_proof_result(
            _reviewed(),
            expected_head_sha=HEAD,
        )
        second = freeze_reviewed_gate_proof_result(
            _reviewed(),
            expected_head_sha=HEAD,
        )
        self.assertEqual(first, second)
        self.assertEqual(
            first["decision"],
            EXP062_REVIEWED_GATE_PROOF_FREEZE_DECISION,
        )
        self.assertEqual(
            first["stage"],
            "EXP062_GATE_PROOF_REVIEWED_FAIL_CLOSED_AND_FROZEN",
        )
        self.assertEqual(
            first["proof_outcome"],
            "EXPECTED_FAIL_CLOSED_EXECUTION_GATE",
        )
        self.assertTrue(first["fail_closed_semantics_verified"])
        self.assertFalse(first["historical_result_slot_consumed"])
        self.assertFalse(first["historical_result_slot_open_authorized"])
        self.assertFalse(first["historical_result_dispatch_authorized"])
        self.assertFalse(first["demo_order_authorized"])
        self.assertFalse(first["live_order_authorized"])
        self.assertFalse(first["trading_authorized"])
        self.assertEqual(
            first["next_gate"],
            "SOURCE_ONLY_HISTORICAL_RUN_AUTHORIZATION_CONTRACT",
        )

        unsigned = dict(first)
        fingerprint = unsigned.pop("freeze_fingerprint_sha256")
        self.assertEqual(
            fingerprint,
            hashlib.sha256(_canonical_json(unsigned)).hexdigest(),
        )

    def test_head_drift_is_rejected(self) -> None:
        reviewed = _reviewed()
        reviewed["proof_head_sha"] = "b" * 40
        with self.assertRaisesRegex(
            ValueError,
            "reviewed result proof_head_sha mismatch",
        ):
            freeze_reviewed_gate_proof_result(
                reviewed,
                expected_head_sha=HEAD,
            )

    def test_slot_opening_is_rejected(self) -> None:
        reviewed = _reviewed()
        reviewed["historical_result_slot_open_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_slot_open_authorized must remain false",
        ):
            freeze_reviewed_gate_proof_result(
                reviewed,
                expected_head_sha=HEAD,
            )

    def test_malformed_artifact_digest_is_rejected(self) -> None:
        reviewed = _reviewed()
        reviewed["preflight_artifact_digest"] = "sha256:not-a-digest"
        with self.assertRaisesRegex(
            ValueError,
            "preflight_artifact_digest",
        ):
            freeze_reviewed_gate_proof_result(
                reviewed,
                expected_head_sha=HEAD,
            )

    def test_downstream_job_count_mismatch_is_rejected(self) -> None:
        reviewed = _reviewed()
        reviewed["materialized_downstream_job_count"] = 1
        with self.assertRaisesRegex(
            ValueError,
            "downstream job count mismatch",
        ):
            freeze_reviewed_gate_proof_result(
                reviewed,
                expected_head_sha=HEAD,
            )

    def test_invalid_runtime_identity_is_rejected(self) -> None:
        reviewed = _reviewed()
        reviewed["proof_run_id"] = 0
        with self.assertRaisesRegex(
            ValueError,
            "proof_run_id must be a positive integer",
        ):
            freeze_reviewed_gate_proof_result(
                reviewed,
                expected_head_sha=HEAD,
            )


if __name__ == "__main__":
    unittest.main()
