from __future__ import annotations

import unittest

from fmp.discovery.exp062_proof_operator import (
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


def _proof_run(
    run_id: int,
    *,
    run_number: int = 1,
    run_attempt: int = 1,
    status: str = "completed",
    conclusion: str | None = "failure",
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


class Exp062ProofOperatorTests(unittest.TestCase):
    def test_missing_run_yields_read_only_proof_plan(self) -> None:
        plan = build_proof_plan(
            main_branch=_main(),
            workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        self.assertIs(validate_proof_plan(plan), plan)
        self.assertEqual(
            plan["stage"],
            "EXP062_PROOF_DISPATCH_AUTHORIZATION_REQUIRED",
        )
        self.assertFalse(plan["run_present"])
        self.assertEqual(
            plan["planned_dispatch_command"],
            shell_join(proof_dispatch_command()),
        )
        self.assertFalse(plan["proof_dispatch_authorized"])
        self.assertFalse(plan["proof_execute_mode_available"])
        self.assertFalse(PROOF_EXECUTE_MODE_AVAILABLE)

    def test_existing_run_removes_command_and_routes_review(self) -> None:
        plan = build_proof_plan(
            main_branch=_main(),
            workflow_runs=_runs(_proof_run(10)),
            expected_head_sha=HEAD,
        )
        self.assertEqual(
            plan["stage"],
            "EXP062_PROOF_RUN_PRESENT_REVIEW_REQUIRED",
        )
        self.assertEqual(plan["matching_manual_main_run_count"], 1)
        self.assertEqual(plan["run_id"], 10)
        self.assertIsNone(plan["planned_dispatch_command"])

    def test_multiple_matching_runs_fail_closed(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "multiple EXP-062 proof/history runs",
        ):
            build_proof_plan(
                main_branch=_main(),
                workflow_runs=_runs(_proof_run(10), _proof_run(11)),
                expected_head_sha=HEAD,
            )

    def test_first_run_must_be_run_one_attempt_one(self) -> None:
        with self.assertRaisesRegex(ValueError, "workflow run #1"):
            build_proof_plan(
                main_branch=_main(),
                workflow_runs=_runs(_proof_run(10, run_number=2)),
                expected_head_sha=HEAD,
            )

        with self.assertRaisesRegex(ValueError, "attempt must be 1"):
            build_proof_plan(
                main_branch=_main(),
                workflow_runs=_runs(_proof_run(10, run_attempt=2)),
                expected_head_sha=HEAD,
            )

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
        with self.assertRaisesRegex(ValueError, "duplicate workflow-run id"):
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
            "EXP062_PROOF_DISPATCH_AUTHORIZATION_REQUIRED",
        )
        self.assertEqual(plan["matching_manual_main_run_count"], 0)

    def test_validator_rejects_any_execute_or_dispatch_authority(self) -> None:
        plan = build_proof_plan(
            main_branch=_main(),
            workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        plan["proof_execute_mode_available"] = True
        with self.assertRaisesRegex(
            ValueError,
            "proof_execute_mode_available must remain false",
        ):
            validate_proof_plan(plan)

        plan = build_proof_plan(
            main_branch=_main(),
            workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        plan["historical_result_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "historical_result_dispatch_authorized must remain false",
        ):
            validate_proof_plan(plan)


if __name__ == "__main__":
    unittest.main()
