from __future__ import annotations

from pathlib import Path
import unittest

from fmp.portfolio.exp015_stage_a_operator import (
    DEC264_MERGED_COMMIT,
    DEC264_TERMINAL_REVIEW_BLOB_SHA,
    EXP015_STAGE_A_WORKFLOW_FILE,
    EXP015_STAGE_A_WORKFLOW_NAME,
    EXP015_STAGE_A_WORKFLOW_PATH,
    REPOSITORY,
    build_exp015_stage_a_operator_report,
    classify_exp015_stage_a_run,
    exp015_stage_a_planned_dispatch_command,
    exp015_stage_a_runs_endpoint,
    select_exp015_stage_a_manual_main_run,
    shell_join,
    validate_exp015_stage_a_operator_checkout,
    validate_exp015_stage_a_operator_report,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/phase8a_exp015_stage_a_operator.py"
SHA = "a" * 40


def _run(
    *,
    status: str = "completed",
    conclusion: str | None = "success",
    run_id: int = 123,
    attempt: int = 1,
) -> dict[str, object]:
    return {
        "id": run_id,
        "name": EXP015_STAGE_A_WORKFLOW_NAME,
        "path": EXP015_STAGE_A_WORKFLOW_PATH,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": SHA,
        "run_attempt": attempt,
        "status": status,
        "conclusion": conclusion,
    }


def _checkout() -> dict[str, object]:
    return {
        "repository": REPOSITORY,
        "dec264_merged_commit": DEC264_MERGED_COMMIT,
        "dec264_guarded_workflow_blob_sha": (
            "ae8bdfbdb1bcfd62204a1bd0ec32dddfd9938930"
        ),
        "dec264_terminal_review_blob_sha": DEC264_TERMINAL_REVIEW_BLOB_SHA,
        "branch": "main",
        "head_sha": SHA,
        "clean_worktree": True,
        "origin_verified": True,
    }


class Exp015StageAOperatorTests(unittest.TestCase):
    def test_predecessor_identities_are_frozen(self) -> None:
        self.assertEqual(
            DEC264_MERGED_COMMIT,
            "92ef2668b1a0cb416e7f772a8a061d2f280005a1",
        )
        self.assertEqual(
            DEC264_TERMINAL_REVIEW_BLOB_SHA,
            "751c886f2d00e46d3c0a20fabbe0db4231db0d5d",
        )

    def test_checkout_requires_clean_exact_main(self) -> None:
        report = validate_exp015_stage_a_operator_checkout(
            branch="main",
            head_sha=SHA,
            origin_main_sha=SHA,
            porcelain_status="",
            origin_url="https://github.com/Dtwosam/FMP.git",
        )
        self.assertEqual(report["head_sha"], SHA)
        self.assertEqual(report["dec264_merged_commit"], DEC264_MERGED_COMMIT)

        with self.assertRaisesRegex(ValueError, "local main branch"):
            validate_exp015_stage_a_operator_checkout(
                branch="feature",
                head_sha=SHA,
                origin_main_sha=SHA,
                porcelain_status="",
                origin_url="https://github.com/Dtwosam/FMP.git",
            )
        with self.assertRaisesRegex(
            ValueError,
            "exactly match fetched origin/main",
        ):
            validate_exp015_stage_a_operator_checkout(
                branch="main",
                head_sha=SHA,
                origin_main_sha="b" * 40,
                porcelain_status="",
                origin_url="https://github.com/Dtwosam/FMP.git",
            )
        with self.assertRaisesRegex(ValueError, "clean working tree"):
            validate_exp015_stage_a_operator_checkout(
                branch="main",
                head_sha=SHA,
                origin_main_sha=SHA,
                porcelain_status=" M changed.py",
                origin_url="https://github.com/Dtwosam/FMP.git",
            )

    def test_exact_run_endpoint_and_planned_dispatch(self) -> None:
        endpoint = exp015_stage_a_runs_endpoint()
        self.assertIn(
            "phase8a-exp015-stage-a.yml/runs",
            endpoint,
        )
        self.assertIn("branch=main", endpoint)
        self.assertIn("event=workflow_dispatch", endpoint)

        command = exp015_stage_a_planned_dispatch_command()
        self.assertEqual(
            command,
            (
                "gh",
                "workflow",
                "run",
                EXP015_STAGE_A_WORKFLOW_FILE,
                "--ref",
                "main",
                "-R",
                REPOSITORY,
            ),
        )
        self.assertEqual(
            shell_join(command),
            "gh workflow run phase8a-exp015-stage-a.yml "
            "--ref main -R Dtwosam/FMP",
        )

    def test_run_selection_ignores_old_push_history(self) -> None:
        selected = select_exp015_stage_a_manual_main_run(
            {
                "workflow_runs": [
                    {
                        **_run(),
                        "id": 10,
                        "event": "push",
                        "head_branch": "phase8a/exp015-stage-a",
                        "run_attempt": 1,
                    }
                ]
            }
        )
        self.assertIsNone(selected)

    def test_run_selection_forbids_second_authoritative_run(self) -> None:
        selected = select_exp015_stage_a_manual_main_run(
            {"workflow_runs": [_run()]}
        )
        assert selected is not None
        self.assertEqual(selected["id"], 123)

        with self.assertRaisesRegex(ValueError, "must be attempt 1"):
            select_exp015_stage_a_manual_main_run(
                {"workflow_runs": [_run(attempt=2)]}
            )

        with self.assertRaisesRegex(ValueError, "multiple authoritative"):
            select_exp015_stage_a_manual_main_run(
                {
                    "workflow_runs": [
                        _run(run_id=123),
                        _run(run_id=124),
                    ]
                }
            )

    def test_run_classification_is_one_way(self) -> None:
        self.assertEqual(
            classify_exp015_stage_a_run(None)["run_state"],
            "MISSING",
        )
        self.assertEqual(
            classify_exp015_stage_a_run(
                _run(status="in_progress", conclusion=None)
            )["run_state"],
            "IN_PROGRESS",
        )
        self.assertEqual(
            classify_exp015_stage_a_run(
                _run(conclusion="failure")
            )["run_state"],
            "TERMINAL",
        )

    def test_missing_state_requires_read_only_proof_not_dispatch(self) -> None:
        report = validate_exp015_stage_a_operator_report(
            build_exp015_stage_a_operator_report(
                checkout=_checkout(),
                run=None,
            )
        )
        self.assertEqual(
            report["stage"],
            "EXP015_STAGE_A_READ_ONLY_PROOF_REQUIRED",
        )
        self.assertEqual(report["run_state"], "MISSING")
        self.assertTrue(report["authoritative_slot_available"])
        self.assertTrue(report["read_only_proof_required"])
        self.assertFalse(report["stage_a_dispatch_authorized"])
        self.assertFalse(report["stage_a_executor_authorized"])
        self.assertEqual(
            report["planned_dispatch_command"],
            "gh workflow run phase8a-exp015-stage-a.yml "
            "--ref main -R Dtwosam/FMP",
        )

    def test_in_progress_and_terminal_states_expose_no_dispatch_plan(self) -> None:
        active = validate_exp015_stage_a_operator_report(
            build_exp015_stage_a_operator_report(
                checkout=_checkout(),
                run=_run(status="in_progress", conclusion=None),
            )
        )
        self.assertEqual(active["stage"], "EXP015_STAGE_A_RUN_IN_PROGRESS")
        self.assertNotIn("planned_dispatch_command", active)
        self.assertFalse(active["authoritative_slot_available"])

        terminal = validate_exp015_stage_a_operator_report(
            build_exp015_stage_a_operator_report(
                checkout=_checkout(),
                run=_run(conclusion="failure"),
            )
        )
        self.assertEqual(
            terminal["stage"],
            "EXP015_STAGE_A_TERMINAL_REVIEW_REQUIRED",
        )
        self.assertNotIn("planned_dispatch_command", terminal)
        self.assertIn("DEC-264", terminal["next_action"])
        self.assertFalse(terminal["stage_a_retry_authorized"])
        self.assertFalse(terminal["stage_a_replacement_authorized"])

    def test_report_tamper_fails_closed(self) -> None:
        report = build_exp015_stage_a_operator_report(
            checkout=_checkout(),
            run=None,
        )
        tampered = dict(report)
        tampered["stage_a_dispatch_authorized"] = True
        with self.assertRaisesRegex(
            ValueError,
            "stage_a_dispatch_authorized must remain false",
        ):
            validate_exp015_stage_a_operator_report(tampered)

        wrong_command = dict(report)
        wrong_command["planned_dispatch_command"] = "gh workflow run wrong.yml"
        with self.assertRaisesRegex(
            ValueError,
            "planned dispatch command mismatch",
        ):
            validate_exp015_stage_a_operator_report(wrong_command)

        active = build_exp015_stage_a_operator_report(
            checkout=_checkout(),
            run=_run(status="in_progress", conclusion=None),
        )
        wrong_stage = dict(active)
        wrong_stage["stage"] = "EXP015_STAGE_A_TERMINAL_REVIEW_REQUIRED"
        with self.assertRaisesRegex(
            ValueError,
            "in-progress report stage mismatch",
        ):
            validate_exp015_stage_a_operator_report(wrong_stage)

    def test_public_cli_is_next_only_and_non_executing(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('OPERATOR_DECISION = "DEC-265"', text)
        self.assertIn('sub.add_parser(', text)
        self.assertIn('"next"', text)
        self.assertNotIn('"advance"', text)
        self.assertNotIn("--execute", text)
        self.assertNotIn("gh workflow run", text)
        self.assertNotIn("/dispatches", text)
        self.assertNotIn("gh run rerun", text)


if __name__ == "__main__":
    unittest.main()
