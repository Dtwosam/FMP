from __future__ import annotations

from pathlib import Path
from unittest.mock import patch
import unittest

from fmp.discovery.exp062_proof_result_review import (
    EXP062_PROOF_RESULT_REVIEW_DECISION,
    review_gate_proof_result,
)


HEAD = "a" * 40


def _terminal() -> dict[str, object]:
    placeholder = (
        "exp062-cell-" + "$" + "{{ matrix.dataset.symbol }}-"
        + "$" + "{{ matrix.dataset.timeframe }}-"
        + "$" + "{{ matrix.dataset.horizon }}m"
    )
    return {
        "decision": "DEC-301",
        "contract_version": "fmp-exp062-gate-proof-contract-v1",
        "stage": "EXP062_GATE_PROOF_REVIEWED_FAIL_CLOSED",
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
        "historical_discovery_execution_occurred": False,
        "cell_result_artifact_count": 0,
        "aggregate_result_artifact_count": 0,
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
    }


def _executor() -> dict[str, object]:
    command = "gh workflow run phase8a-exp062-discovery.yml --ref main"
    return {
        "decision": "DEC-302",
        "operator_version": "fmp-exp062-proof-operator-v1",
        "proof_contract_version": "fmp-exp062-gate-proof-contract-v1",
        "expected_head_sha": HEAD,
        "stage": "EXP062_PROOF_DISPATCH_AUTHORIZATION_REQUIRED",
        "run_present": False,
        "run_id": None,
        "run_head_sha": None,
        "run_status": None,
        "run_conclusion": None,
        "matching_manual_main_run_count": 0,
        "planned_dispatch_command": command,
        "proof_dispatch_authorized": False,
        "proof_execute_mode_available": False,
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
        "executor_decision": "DEC-303",
        "executor_version": "fmp-exp062-proof-one-shot-executor-v1",
        "executor_head_sha": HEAD,
        "fresh_plan_rechecked_twice": True,
        "dispatch_command": command,
        "proof_dispatch_authorized_by_dec303": True,
        "proof_dispatch_submitted": True,
        "historical_result_slot_consumed": False,
        "historical_result_claimed": False,
    }


class Exp062ProofResultReviewTests(unittest.TestCase):
    def _review(
        self,
        *,
        terminal: dict[str, object] | None = None,
        executor: dict[str, object] | None = None,
    ) -> dict[str, object]:
        terminal = _terminal() if terminal is None else terminal
        executor = _executor() if executor is None else executor
        with patch(
            "fmp.discovery.exp062_proof_result_review.validate_gate_proof_terminal",
            return_value=terminal,
        ):
            return review_gate_proof_result(
                run={},
                jobs_payload={},
                artifacts_payload={},
                preflight_evidence={},
                executor_evidence=executor,
                expected_head_sha=HEAD,
                repository_root=Path("."),
            )

    def test_fail_closed_proof_is_reviewed_without_opening_slot(self) -> None:
        report = self._review()
        self.assertEqual(
            report["decision"],
            EXP062_PROOF_RESULT_REVIEW_DECISION,
        )
        self.assertEqual(
            report["stage"],
            "EXP062_GATE_PROOF_RESULT_REVIEWED_FAIL_CLOSED",
        )
        self.assertEqual(report["proof_run_number"], 1)
        self.assertEqual(report["proof_run_attempt"], 1)
        self.assertEqual(report["proof_run_conclusion"], "failure")
        self.assertTrue(report["proof_dispatch_submitted"])
        self.assertFalse(report["historical_result_slot_consumed"])
        self.assertFalse(report["historical_result_slot_open_authorized"])
        self.assertFalse(report["historical_result_dispatch_authorized"])
        self.assertFalse(report["historical_discovery_execution_authorized"])
        self.assertEqual(
            report["next_gate"],
            "IMMUTABLE_PROOF_RESULT_FREEZE_BEFORE_HISTORICAL_SLOT",
        )

    def test_executor_head_drift_is_rejected(self) -> None:
        executor = _executor()
        executor["executor_head_sha"] = "b" * 40
        with self.assertRaisesRegex(
            ValueError,
            "executor evidence executor_head_sha mismatch",
        ):
            self._review(executor=executor)

    def test_executor_cannot_claim_historical_result(self) -> None:
        executor = _executor()
        executor["historical_result_claimed"] = True
        with self.assertRaisesRegex(
            ValueError,
            "executor evidence historical_result_claimed mismatch",
        ):
            self._review(executor=executor)

    def test_terminal_slot_consumption_is_rejected(self) -> None:
        terminal = _terminal()
        terminal["historical_result_slot_consumed"] = True
        with self.assertRaisesRegex(
            ValueError,
            "terminal historical_result_slot_consumed must remain false",
        ):
            self._review(terminal=terminal)

    def test_terminal_historical_execution_is_rejected(self) -> None:
        terminal = _terminal()
        terminal["historical_discovery_execution_occurred"] = True
        with self.assertRaisesRegex(
            ValueError,
            "terminal historical_discovery_execution_occurred must remain false",
        ):
            self._review(terminal=terminal)

    def test_terminal_stage_or_head_drift_is_rejected(self) -> None:
        terminal = _terminal()
        terminal["stage"] = "other"
        with self.assertRaisesRegex(
            ValueError,
            "terminal proof stage mismatch",
        ):
            self._review(terminal=terminal)

        terminal = _terminal()
        terminal["proof_head_sha"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "proof head mismatch"):
            self._review(terminal=terminal)


if __name__ == "__main__":
    unittest.main()
