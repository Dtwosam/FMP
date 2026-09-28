from __future__ import annotations

import unittest

from fmp.discovery.exp062_connector_proof_bootstrap import (
    EXPECTED_MAIN_SHA,
    EXP062_CONNECTOR_PROOF_BOOTSTRAP_DECISION,
    REQUIRED_BASE_REF,
    REQUIRED_EVENT_NAME,
    REQUIRED_HEAD_REF,
    build_connector_proof_bootstrap_evidence,
)


def _plan() -> dict[str, object]:
    command = "gh workflow run phase8a-exp062-discovery.yml --ref main"
    return {
        "decision": "DEC-302",
        "operator_version": "fmp-exp062-proof-operator-v1",
        "proof_contract_version": "fmp-exp062-gate-proof-contract-v1",
        "expected_head_sha": EXPECTED_MAIN_SHA,
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
    }


class Exp062ConnectorProofBootstrapTests(unittest.TestCase):
    def _build(
        self,
        first: dict[str, object] | None = None,
        second: dict[str, object] | None = None,
        **overrides: object,
    ) -> dict[str, object]:
        kwargs: dict[str, object] = {
            "main_head_sha": EXPECTED_MAIN_SHA,
            "event_name": REQUIRED_EVENT_NAME,
            "base_ref": REQUIRED_BASE_REF,
            "head_ref": REQUIRED_HEAD_REF,
            "run_attempt": 1,
        }
        kwargs.update(overrides)
        return build_connector_proof_bootstrap_evidence(
            _plan() if first is None else first,
            _plan() if second is None else second,
            **kwargs,
        )

    def test_exact_recovery_context_reuses_dec303_evidence(self) -> None:
        evidence = self._build()
        self.assertEqual(
            evidence["bootstrap_decision"],
            EXP062_CONNECTOR_PROOF_BOOTSTRAP_DECISION,
        )
        self.assertEqual(evidence["executor_decision"], "DEC-303")
        self.assertEqual(
            evidence["executor_head_sha"],
            EXPECTED_MAIN_SHA,
        )
        self.assertTrue(evidence["proof_dispatch_authorized_by_dec303"])
        self.assertTrue(evidence["proof_dispatch_submitted"])
        self.assertTrue(evidence["connector_recovery_path"])
        self.assertFalse(evidence["historical_result_slot_consumed"])
        self.assertFalse(evidence["historical_result_dispatch_authorized"])
        self.assertFalse(evidence["historical_discovery_execution_authorized"])
        self.assertFalse(evidence["demo_order_authorized"])
        self.assertFalse(evidence["live_order_authorized"])
        self.assertFalse(evidence["real_money_authorized"])
        self.assertFalse(evidence["trading_authorized"])

    def test_main_head_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "exact main head mismatch"):
            self._build(main_head_sha="a" * 40)

    def test_non_pull_request_event_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires pull_request event"):
            self._build(event_name="push")

    def test_wrong_activation_branch_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "activation branch mismatch"):
            self._build(head_ref="other")

    def test_workflow_rerun_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "refuses workflow reruns"):
            self._build(run_attempt=2)

    def test_plan_drift_is_rejected(self) -> None:
        second = _plan()
        second["planned_dispatch_command"] = "other"
        with self.assertRaisesRegex(
            ValueError,
            "proof plans changed before dispatch",
        ):
            self._build(second=second)

    def test_existing_proof_run_is_rejected_by_dec303_guard(self) -> None:
        first = _plan()
        second = _plan()
        for value in (first, second):
            value["stage"] = "EXP062_PROOF_RUN_PRESENT_REVIEW_REQUIRED"
            value["run_present"] = True
            value["run_id"] = 123
            value["run_head_sha"] = EXPECTED_MAIN_SHA
            value["run_status"] = "completed"
            value["run_conclusion"] = "failure"
            value["matching_manual_main_run_count"] = 1
            value["planned_dispatch_command"] = None
        with self.assertRaisesRegex(
            ValueError,
            "requires a fresh zero-run proof plan",
        ):
            self._build(first=first, second=second)


if __name__ == "__main__":
    unittest.main()
