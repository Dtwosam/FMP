from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_one_shot_executor_workflow_preflight import (
    build_one_shot_historical_executor_workflow_preflight,
    historical_executor_workflow_dispatch_command,
    shell_join,
    validate_one_shot_historical_executor_workflow_preflight,
)
from fmp.discovery.exp062_runtime_proof_freeze import (
    PROOF_HEAD_SHA,
    PROOF_RUN_ID,
)


HEAD = "a" * 40


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _proof() -> dict[str, object]:
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


def _historical(
    *,
    run_id: int = 40000000000,
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
        "run_number": 2,
        "run_attempt": 1,
        "status": status,
        "conclusion": conclusion,
    }


def _runs(*extra: dict[str, object]) -> dict[str, object]:
    return {"workflow_runs": [_proof(), *extra]}


class Exp062OneShotHistoricalExecutorWorkflowPreflightTests(
    unittest.TestCase
):
    def test_empty_slot_exposes_read_only_workflow_command(self) -> None:
        plan = build_one_shot_historical_executor_workflow_preflight(
            repository_root=Path("."),
            main_branch=_main(),
            workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        self.assertIs(
            validate_one_shot_historical_executor_workflow_preflight(plan),
            plan,
        )
        self.assertEqual(plan["decision"], "DEC-343")
        self.assertEqual(
            plan["stage"],
            (
                "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_"
                "PREFLIGHT_SLOT_AVAILABLE"
            ),
        )
        self.assertEqual(plan["historical_result_attempt_count"], 0)
        self.assertFalse(plan["historical_result_slot_consumed"])
        self.assertEqual(
            plan["planned_dispatch_command"],
            shell_join(historical_executor_workflow_dispatch_command()),
        )
        self.assertTrue(
            plan["one_shot_historical_executor_workflow_source_authorized"]
        )
        self.assertFalse(plan["historical_executor_available"])
        self.assertFalse(plan["historical_result_dispatch_authorized"])
        self.assertFalse(plan["historical_execute_mode_available"])

    def test_existing_run_consumes_slot_and_removes_command(self) -> None:
        plan = build_one_shot_historical_executor_workflow_preflight(
            repository_root=Path("."),
            main_branch=_main(),
            workflow_runs=_runs(_historical(status="in_progress")),
            expected_head_sha=HEAD,
        )
        self.assertEqual(
            plan["stage"],
            (
                "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_WORKFLOW_"
                "PREFLIGHT_SLOT_CONSUMED_REVIEW_REQUIRED"
            ),
        )
        self.assertEqual(plan["historical_result_attempt_count"], 1)
        self.assertTrue(plan["historical_result_slot_consumed"])
        self.assertEqual(plan["historical_result_run_id"], 40000000000)
        self.assertIsNone(plan["planned_dispatch_command"])

    def test_main_head_drift_is_rejected(self) -> None:
        main = _main()
        main["commit"] = {"sha": "b" * 40}
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_one_shot_historical_executor_workflow_preflight(
                repository_root=Path("."),
                main_branch=main,
                workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )

    def test_second_historical_attempt_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "multiple attempts"):
            build_one_shot_historical_executor_workflow_preflight(
                repository_root=Path("."),
                main_branch=_main(),
                workflow_runs=_runs(
                    _historical(run_id=40000000001),
                    _historical(run_id=40000000002),
                ),
                expected_head_sha=HEAD,
            )

    def test_validator_rejects_runtime_authority(self) -> None:
        plan = build_one_shot_historical_executor_workflow_preflight(
            repository_root=Path("."),
            main_branch=_main(),
            workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        plan["historical_executor_available"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_executor_available mismatch",
        ):
            validate_one_shot_historical_executor_workflow_preflight(plan)

        plan = build_one_shot_historical_executor_workflow_preflight(
            repository_root=Path("."),
            main_branch=_main(),
            workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        plan["historical_result_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_dispatch_authorized mismatch",
        ):
            validate_one_shot_historical_executor_workflow_preflight(plan)

    def test_cli_has_plan_only_no_execute_surface(self) -> None:
        text = Path(
            "scripts/"
            "phase8a_exp062_one_shot_historical_executor_workflow_preflight.py"
        ).read_text(encoding="utf-8")
        self.assertIn('sub.add_parser("plan")', text)
        self.assertNotIn('sub.add_parser("execute")', text)
        self.assertNotIn('sub.add_parser("advance")', text)
        self.assertNotIn("gh workflow run ", text)


if __name__ == "__main__":
    unittest.main()
