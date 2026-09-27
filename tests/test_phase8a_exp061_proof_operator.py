from __future__ import annotations

import unittest

from fmp.discovery.proof_operator import (
    PROOF_EXECUTE_MODE_AVAILABLE,
    build_proof_plan,
    proof_dispatch_command,
    shell_join,
    validate_proof_plan,
)


HEAD = "a" * 40


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _runs(*rows: dict[str, object]) -> dict[str, object]:
    return {"workflow_runs": list(rows)}


def _proof_run(run_id: int, *, status: str = "completed", conclusion: str | None = "failure") -> dict[str, object]:
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


class Exp061ProofOperatorTests(unittest.TestCase):
    def test_missing_run_yields_read_only_authorization_required_plan(self) -> None:
        plan = build_proof_plan(
            main_branch=_main(),
            workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_proof_plan(plan), plan)
        self.assertEqual(
            plan["stage"],
            "EXP061_PROOF_DISPATCH_AUTHORIZATION_REQUIRED",
        )
        self.assertFalse(plan["run_present"])
        self.assertEqual(
            plan["planned_dispatch_command"],
            shell_join(proof_dispatch_command()),
        )
        self.assertFalse(plan["proof_dispatch_authorized"])
        self.assertFalse(plan["proof_execute_mode_available"])
        self.assertFalse(PROOF_EXECUTE_MODE_AVAILABLE)

    def test_existing_run_removes_dispatch_command(self) -> None:
        plan = build_proof_plan(
            main_branch=_main(),
            workflow_runs=_runs(_proof_run(10)),
            expected_head_sha=HEAD,
        )
        self.assertEqual(
            plan["stage"],
            "EXP061_PROOF_RUN_PRESENT_REVIEW_REQUIRED",
        )
        self.assertTrue(plan["run_present"])
        self.assertEqual(plan["run_id"], 10)
        self.assertIsNone(plan["planned_dispatch_command"])
        self.assertEqual(plan["matching_manual_main_run_count"], 1)

    def test_main_head_drift_fails_closed(self) -> None:
        main = _main()
        main["commit"] = {"sha": "b" * 40}
        with self.assertRaisesRegex(ValueError, "main head mismatch"):
            build_proof_plan(
                main_branch=main,
                workflow_runs=_runs(),
                expected_head_sha=HEAD,
            )

    def test_duplicate_run_ids_fail_closed(self) -> None:
        row = _proof_run(10)
        with self.assertRaisesRegex(ValueError, "duplicate run id"):
            build_proof_plan(
                main_branch=_main(),
                workflow_runs=_runs(row, dict(row)),
                expected_head_sha=HEAD,
            )

    def test_unrelated_runs_do_not_consume_proof_state(self) -> None:
        unrelated = {
            "id": 5,
            "name": "tests",
            "path": ".github/workflows/tests.yml",
            "event": "push",
            "head_branch": "main",
        }
        plan = build_proof_plan(
            main_branch=_main(),
            workflow_runs=_runs(unrelated),
            expected_head_sha=HEAD,
        )
        self.assertEqual(
            plan["stage"],
            "EXP061_PROOF_DISPATCH_AUTHORIZATION_REQUIRED",
        )
        self.assertEqual(plan["matching_manual_main_run_count"], 0)


if __name__ == "__main__":
    unittest.main()
