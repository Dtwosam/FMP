from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_execution_operator import (
    HISTORICAL_EXECUTE_MODE_AVAILABLE,
    build_historical_execution_plan,
    historical_execution_dispatch_command,
    shell_join,
    validate_historical_execution_plan,
)
from fmp.discovery.exp062_runtime_proof_freeze import (
    PROOF_HEAD_SHA,
    PROOF_RUN_ID,
)


HEAD = "a" * 40


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _proof(*, run_number: int = 1) -> dict[str, object]:
    return {
        "id": PROOF_RUN_ID,
        "name": "phase8a-exp062-discovery",
        "path": ".github/workflows/phase8a-exp062-discovery.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": PROOF_HEAD_SHA,
        "run_number": run_number,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "failure",
    }


def _historical(
    *,
    run_id: int = 40000000000,
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
        "head_sha": HEAD,
        "run_number": run_number,
        "run_attempt": run_attempt,
        "status": status,
        "conclusion": conclusion,
    }


def _runs(*extra: dict[str, object]) -> dict[str, object]:
    return {"workflow_runs": [_proof(), *extra]}


class Exp062HistoricalExecutionOperatorTests(unittest.TestCase):
    def test_empty_slot_exposes_read_only_run_two_plan(self) -> None:
        plan = build_historical_execution_plan(
            repository_root=Path("."),
            main_branch=_main(),
            workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_historical_execution_plan(plan), plan)
        self.assertEqual(
            plan["stage"],
            "EXP062_HISTORICAL_RESULT_SLOT_AVAILABLE",
        )
        self.assertEqual(plan["proof_run_number"], 1)
        self.assertEqual(plan["historical_result_attempt_count"], 0)
        self.assertEqual(plan["expected_target_run_number"], 2)
        self.assertEqual(plan["expected_target_run_attempt"], 1)
        self.assertEqual(
            plan["planned_dispatch_command"],
            shell_join(historical_execution_dispatch_command()),
        )
        self.assertTrue(plan["historical_execution_source_authorized"])
        self.assertTrue(plan["historical_discovery_execution_authorized"])
        self.assertTrue(plan["discovery_result_authorized"])
        self.assertFalse(plan["historical_result_dispatch_authorized"])
        self.assertFalse(plan["historical_execute_mode_available"])
        self.assertFalse(HISTORICAL_EXECUTE_MODE_AVAILABLE)

    def test_present_run_two_consumes_slot_and_removes_command(self) -> None:
        plan = build_historical_execution_plan(
            repository_root=Path("."),
            main_branch=_main(),
            workflow_runs=_runs(_historical(status="in_progress")),
            expected_head_sha=HEAD,
        )
        self.assertEqual(
            plan["stage"],
            "EXP062_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED",
        )
        self.assertEqual(plan["historical_result_attempt_count"], 1)
        self.assertTrue(plan["historical_result_slot_consumed"])
        self.assertEqual(plan["historical_result_run_id"], 40000000000)
        self.assertIsNone(plan["planned_dispatch_command"])

    def test_proof_must_remain_workflow_run_one(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "proof must remain workflow run number 1|frozen proof run run_number mismatch",
        ):
            build_historical_execution_plan(
                repository_root=Path("."),
                main_branch=_main(),
                workflow_runs={"workflow_runs": [_proof(run_number=2)]},
                expected_head_sha=HEAD,
            )

    def test_present_historical_run_must_be_run_two_attempt_one(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "historical run must be workflow run number 2|historical-result run number must be 2",
        ):
            build_historical_execution_plan(
                repository_root=Path("."),
                main_branch=_main(),
                workflow_runs=_runs(_historical(run_number=3)),
                expected_head_sha=HEAD,
            )

        with self.assertRaisesRegex(
            ValueError,
            "run attempt must remain 1",
        ):
            build_historical_execution_plan(
                repository_root=Path("."),
                main_branch=_main(),
                workflow_runs=_runs(_historical(run_attempt=2)),
                expected_head_sha=HEAD,
            )

    def test_main_head_drift_fails_closed(self) -> None:
        main = _main()
        main["commit"] = {"sha": "b" * 40}
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_historical_execution_plan(
                repository_root=Path("."),
                main_branch=main,
                workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )

    def test_second_historical_attempt_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "multiple attempts"):
            build_historical_execution_plan(
                repository_root=Path("."),
                main_branch=_main(),
                workflow_runs=_runs(
                    _historical(run_id=40000000001),
                    _historical(run_id=40000000002),
                ),
                expected_head_sha=HEAD,
            )

    def test_validator_rejects_execute_or_dispatch_authority(self) -> None:
        plan = build_historical_execution_plan(
            repository_root=Path("."),
            main_branch=_main(),
            workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        plan["historical_execute_mode_available"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_execute_mode_available must remain false",
        ):
            validate_historical_execution_plan(plan)

        plan = build_historical_execution_plan(
            repository_root=Path("."),
            main_branch=_main(),
            workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        plan["historical_result_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_dispatch_authorized must remain false",
        ):
            validate_historical_execution_plan(plan)

    def test_present_run_cannot_retain_dispatch_command(self) -> None:
        plan = build_historical_execution_plan(
            repository_root=Path("."),
            main_branch=_main(),
            workflow_runs=_runs(_historical(status="in_progress")),
            expected_head_sha=HEAD,
        )
        plan["planned_dispatch_command"] = shell_join(
            historical_execution_dispatch_command()
        )
        with self.assertRaisesRegex(
            ValueError,
            "cannot plan a second historical run",
        ):
            validate_historical_execution_plan(plan)


if __name__ == "__main__":
    unittest.main()
