from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_run_authorization import (
    EXP062_HISTORICAL_RUN_AUTHORIZATION_DECISION,
    HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED,
    build_historical_run_authorization_contract,
    classify_historical_run_inventory,
    validate_historical_run_authorization_sources,
)
from fmp.discovery.exp062_runtime_proof_freeze import (
    PROOF_HEAD_SHA,
    PROOF_RUN_ID,
)


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


def _historical_run(
    *,
    run_id: int = 40000000001,
    run_number: int = 2,
    run_attempt: int = 1,
    status: str = "queued",
    conclusion: str | None = None,
) -> dict[str, object]:
    return {
        "id": run_id,
        "name": "phase8a-exp062-discovery",
        "path": ".github/workflows/phase8a-exp062-discovery.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": "b" * 40,
        "run_number": run_number,
        "run_attempt": run_attempt,
        "status": status,
        "conclusion": conclusion,
    }


class Exp062HistoricalRunAuthorizationTests(unittest.TestCase):
    def test_sources_bind_runtime_freeze_and_keep_execution_locked(self) -> None:
        source = validate_historical_run_authorization_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["decision"],
            EXP062_HISTORICAL_RUN_AUTHORIZATION_DECISION,
        )
        self.assertTrue(source["historical_result_slot_source_authorized"])
        self.assertFalse(source["historical_result_dispatch_authorized"])
        self.assertFalse(source["historical_discovery_execution_authorized"])
        self.assertFalse(source["discovery_result_authorized"])
        self.assertFalse(source["reserved_robustness_access_authorized"])
        self.assertFalse(source["demo_order_authorized"])
        self.assertFalse(source["live_order_authorized"])
        self.assertFalse(source["trading_authorized"])
        self.assertEqual(source["expected_cell_count"], 18)
        self.assertEqual(
            source["historical_data_end_exclusive"],
            "2023-01-01T00:00:00Z",
        )
        self.assertEqual(
            source["reserved_robustness_start"],
            "2023-01-01T00:00:00Z",
        )

    def test_only_frozen_proof_leaves_slot_available(self) -> None:
        report = classify_historical_run_inventory(
            {"workflow_runs": [_proof_run()]}
        )
        self.assertEqual(
            report["stage"],
            "EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE",
        )
        self.assertEqual(report["proof_run_count"], 1)
        self.assertEqual(report["historical_result_attempt_count"], 0)
        self.assertFalse(report["historical_result_slot_consumed"])
        self.assertTrue(report["historical_result_slot_source_authorized"])
        self.assertFalse(report["historical_result_dispatch_authorized"])

    def test_first_later_run_consumes_slot_immediately(self) -> None:
        report = classify_historical_run_inventory(
            {"workflow_runs": [_proof_run(), _historical_run()]}
        )
        self.assertEqual(
            report["stage"],
            "EXP062_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED",
        )
        self.assertEqual(report["historical_result_attempt_count"], 1)
        self.assertTrue(report["historical_result_slot_consumed"])
        self.assertEqual(report["historical_result_run_status"], "queued")
        self.assertIsNone(report["historical_result_run_conclusion"])
        self.assertFalse(report["historical_result_dispatch_authorized"])

    def test_completed_historical_run_requires_conclusion(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "requires a conclusion",
        ):
            classify_historical_run_inventory(
                {
                    "workflow_runs": [
                        _proof_run(),
                        _historical_run(status="completed"),
                    ]
                }
            )

    def test_multiple_historical_attempts_are_rejected(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "slot has multiple attempts",
        ):
            classify_historical_run_inventory(
                {
                    "workflow_runs": [
                        _proof_run(),
                        _historical_run(run_id=40000000001),
                        _historical_run(run_id=40000000002),
                    ]
                }
            )

    def test_historical_run_number_or_attempt_drift_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "run number must be 2"):
            classify_historical_run_inventory(
                {
                    "workflow_runs": [
                        _proof_run(),
                        _historical_run(run_number=3),
                    ]
                }
            )

        with self.assertRaisesRegex(ValueError, "attempt must remain 1"):
            classify_historical_run_inventory(
                {
                    "workflow_runs": [
                        _proof_run(),
                        _historical_run(run_attempt=2),
                    ]
                }
            )

    def test_proof_drift_is_rejected(self) -> None:
        proof = _proof_run()
        proof["conclusion"] = "success"
        with self.assertRaisesRegex(
            ValueError,
            "frozen proof run conclusion mismatch",
        ):
            classify_historical_run_inventory({"workflow_runs": [proof]})

    def test_source_contract_opens_only_governance_slot(self) -> None:
        contract = build_historical_run_authorization_contract(
            repository_root=Path("."),
            workflow_runs_payload={"workflow_runs": [_proof_run()]},
        )
        self.assertEqual(
            contract["stage"],
            "EXP062_HISTORICAL_RESULT_SOURCE_AUTHORIZED_DISPATCH_LOCKED",
        )
        self.assertIs(
            contract["historical_result_slot_source_authorized"],
            HISTORICAL_RESULT_SLOT_SOURCE_AUTHORIZED,
        )
        self.assertTrue(contract["terminal_outcome_consumes_slot"])
        self.assertFalse(contract["proof_retry_or_replacement_authorized"])
        self.assertFalse(contract["historical_result_dispatch_authorized"])
        self.assertFalse(contract["historical_discovery_execution_authorized"])
        self.assertFalse(contract["discovery_result_authorized"])
        self.assertFalse(contract["reserved_robustness_access_authorized"])
        self.assertFalse(contract["candidate_compilation_authorized"])
        self.assertFalse(contract["phase8b_authorized"])
        self.assertFalse(contract["demo_order_authorized"])
        self.assertFalse(contract["live_order_authorized"])
        self.assertFalse(contract["trading_authorized"])


if __name__ == "__main__":
    unittest.main()
