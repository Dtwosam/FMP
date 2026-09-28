from __future__ import annotations

import unittest

from fmp.discovery.exp062_historical_operator import (
    EXP062_HISTORICAL_OPERATOR_DECISION,
    build_historical_plan,
    historical_dispatch_command,
    shell_join,
    validate_historical_plan,
)
from fmp.discovery.exp062_runtime_proof_freeze import (
    PROOF_HEAD_SHA,
    PROOF_RUN_ID,
)


EXPECTED_HEAD = "a" * 40


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": EXPECTED_HEAD}}


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


def _historical_run() -> dict[str, object]:
    return {
        "id": 40000000001,
        "name": "phase8a-exp062-discovery",
        "path": ".github/workflows/phase8a-exp062-discovery.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": EXPECTED_HEAD,
        "run_number": 2,
        "run_attempt": 1,
        "status": "in_progress",
        "conclusion": None,
    }


class Exp062HistoricalOperatorTests(unittest.TestCase):
    def test_empty_slot_exposes_command_as_plan_only(self) -> None:
        plan = build_historical_plan(
            main_branch=_main(),
            workflow_runs={"workflow_runs": [_proof_run()]},
            expected_head_sha=EXPECTED_HEAD,
        )
        self.assertEqual(plan["decision"], EXP062_HISTORICAL_OPERATOR_DECISION)
        self.assertEqual(
            plan["stage"],
            "EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE",
        )
        self.assertEqual(
            plan["planned_dispatch_command"],
            shell_join(historical_dispatch_command()),
        )
        self.assertTrue(plan["historical_result_slot_source_authorized"])
        self.assertFalse(plan["historical_result_slot_consumed"])
        self.assertFalse(plan["historical_result_dispatch_authorized"])
        self.assertFalse(plan["historical_execute_mode_available"])
        self.assertFalse(plan["historical_discovery_execution_authorized"])
        self.assertFalse(plan["discovery_result_authorized"])
        self.assertFalse(plan["reserved_robustness_access_authorized"])
        self.assertFalse(plan["candidate_compilation_authorized"])
        self.assertFalse(plan["promotion_authorized"])
        self.assertFalse(plan["phase8b_authorized"])
        self.assertFalse(plan["demo_order_authorized"])
        self.assertFalse(plan["live_order_authorized"])
        self.assertFalse(plan["trading_authorized"])
        self.assertIs(validate_historical_plan(plan), plan)

    def test_present_run_consumes_slot_and_removes_command(self) -> None:
        plan = build_historical_plan(
            main_branch=_main(),
            workflow_runs={"workflow_runs": [_proof_run(), _historical_run()]},
            expected_head_sha=EXPECTED_HEAD,
        )
        self.assertEqual(
            plan["stage"],
            "EXP062_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED",
        )
        self.assertTrue(plan["historical_result_slot_consumed"])
        self.assertEqual(plan["historical_result_attempt_count"], 1)
        self.assertEqual(plan["historical_result_run_id"], 40000000001)
        self.assertIsNone(plan["planned_dispatch_command"])
        self.assertIs(validate_historical_plan(plan), plan)

    def test_main_head_drift_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_historical_plan(
                main_branch=_main(),
                workflow_runs={"workflow_runs": [_proof_run()]},
                expected_head_sha="b" * 40,
            )

    def test_non_main_metadata_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires main branch metadata"):
            build_historical_plan(
                main_branch={
                    "name": "feature",
                    "commit": {"sha": EXPECTED_HEAD},
                },
                workflow_runs={"workflow_runs": [_proof_run()]},
                expected_head_sha=EXPECTED_HEAD,
            )

    def test_validator_rejects_execute_or_dispatch_authority(self) -> None:
        plan = build_historical_plan(
            main_branch=_main(),
            workflow_runs={"workflow_runs": [_proof_run()]},
            expected_head_sha=EXPECTED_HEAD,
        )
        for field in (
            "historical_result_dispatch_authorized",
            "historical_execute_mode_available",
            "historical_discovery_execution_authorized",
            "discovery_result_authorized",
            "reserved_robustness_access_authorized",
            "candidate_compilation_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            mutated = dict(plan)
            mutated[field] = True
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, f"{field} must remain false"):
                    validate_historical_plan(mutated)

    def test_validator_rejects_command_after_slot_consumption(self) -> None:
        plan = build_historical_plan(
            main_branch=_main(),
            workflow_runs={"workflow_runs": [_proof_run(), _historical_run()]},
            expected_head_sha=EXPECTED_HEAD,
        )
        plan["planned_dispatch_command"] = shell_join(
            historical_dispatch_command()
        )
        with self.assertRaisesRegex(
            ValueError,
            "cannot plan a second historical run",
        ):
            validate_historical_plan(plan)


if __name__ == "__main__":
    unittest.main()
