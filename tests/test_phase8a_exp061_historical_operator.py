from __future__ import annotations

import unittest

from fmp.discovery.historical_operator import (
    HISTORICAL_EXECUTE_MODE_AVAILABLE,
    build_historical_plan,
    historical_dispatch_command,
    shell_join,
    validate_historical_plan,
)
from fmp.discovery.historical_run_authorization import EXPECTED_PROOF_RUN


HEAD = "a" * 40


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _proof() -> dict[str, object]:
    return dict(EXPECTED_PROOF_RUN)


def _runs(*extra: dict[str, object]) -> dict[str, object]:
    return {"workflow_runs": [_proof(), *extra]}


def _historical(
    *,
    run_id: int = 40000000000,
    status: str = "queued",
    conclusion: str | None = None,
) -> dict[str, object]:
    return {
        "id": run_id,
        "name": "phase8a-exp061-discovery",
        "path": ".github/workflows/phase8a-exp061-discovery.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": HEAD,
        "run_attempt": 1,
        "status": status,
        "conclusion": conclusion,
    }


class Exp061HistoricalOperatorTests(unittest.TestCase):
    def test_unused_slot_exposes_one_read_only_command(self) -> None:
        plan = build_historical_plan(
            main_branch=_main(),
            workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_historical_plan(plan), plan)
        self.assertEqual(
            plan["stage"],
            "EXP061_HISTORICAL_RESULT_SLOT_AVAILABLE",
        )
        self.assertEqual(plan["proof_run_count"], 1)
        self.assertEqual(plan["historical_result_attempt_count"], 0)
        self.assertFalse(plan["historical_result_slot_consumed"])
        self.assertEqual(
            plan["planned_dispatch_command"],
            shell_join(historical_dispatch_command()),
        )
        self.assertTrue(plan["historical_result_slot_source_authorized"])
        self.assertFalse(plan["historical_result_dispatch_authorized"])
        self.assertFalse(plan["historical_execute_mode_available"])
        self.assertFalse(HISTORICAL_EXECUTE_MODE_AVAILABLE)

    def test_present_historical_run_removes_command(self) -> None:
        plan = build_historical_plan(
            main_branch=_main(),
            workflow_runs=_runs(_historical(status="in_progress")),
            expected_head_sha=HEAD,
        )
        self.assertEqual(
            plan["stage"],
            "EXP061_HISTORICAL_RESULT_RUN_PRESENT_REVIEW_REQUIRED",
        )
        self.assertEqual(plan["historical_result_attempt_count"], 1)
        self.assertTrue(plan["historical_result_slot_consumed"])
        self.assertEqual(plan["historical_result_run_id"], 40000000000)
        self.assertIsNone(plan["planned_dispatch_command"])

    def test_main_head_drift_fails_closed(self) -> None:
        main = _main()
        main["commit"] = {"sha": "b" * 40}
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_historical_plan(
                main_branch=main,
                workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )

    def test_changed_proof_fails_closed(self) -> None:
        proof = _proof()
        proof["conclusion"] = "success"
        with self.assertRaisesRegex(ValueError, "frozen proof run conclusion mismatch"):
            build_historical_plan(
                main_branch=_main(),
                workflow_runs={"workflow_runs": [proof]},
                expected_head_sha=HEAD,
            )

    def test_second_historical_attempt_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "multiple attempts"):
            build_historical_plan(
                main_branch=_main(),
                workflow_runs=_runs(
                    _historical(run_id=40000000001),
                    _historical(run_id=40000000002),
                ),
                expected_head_sha=HEAD,
            )

    def test_validator_rejects_execute_or_second_dispatch(self) -> None:
        plan = build_historical_plan(
            main_branch=_main(),
            workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        plan["historical_execute_mode_available"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_execute_mode_available must remain false",
        ):
            validate_historical_plan(plan)

        present = build_historical_plan(
            main_branch=_main(),
            workflow_runs=_runs(_historical(status="in_progress")),
            expected_head_sha=HEAD,
        )
        present["planned_dispatch_command"] = shell_join(
            historical_dispatch_command()
        )
        with self.assertRaisesRegex(
            ValueError,
            "cannot plan a second historical run",
        ):
            validate_historical_plan(present)


if __name__ == "__main__":
    unittest.main()
