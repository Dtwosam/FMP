from __future__ import annotations

import copy
from pathlib import Path
import unittest

from fmp.portfolio.exp015_stage_a_executor import (
    EXECUTOR_DECISION,
    validate_exp015_stage_a_fresh_execution_plan,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/phase8a_exp015_stage_a_executor.py"
HEAD = "a" * 40


def _plan() -> dict[str, object]:
    return {
        "repository": "Dtwosam/FMP",
        "dec264_merged_commit": "92ef2668b1a0cb416e7f772a8a061d2f280005a1",
        "dec264_guarded_workflow_blob_sha": "ae8bdfbdb1bcfd62204a1bd0ec32dddfd9938930",
        "dec264_terminal_review_blob_sha": "751c886f2d00e46d3c0a20fabbe0db4231db0d5d",
        "branch": "main",
        "head_sha": HEAD,
        "clean_worktree": True,
        "origin_verified": True,
        "run_present": False,
        "run_state": "MISSING",
        "run_id": None,
        "operator_read_only": True,
        "stage_a_dispatch_authorized": False,
        "stage_a_executor_authorized": False,
        "stage_a_retry_authorized": False,
        "stage_a_replacement_authorized": False,
        "stage_b_execution_authorized": False,
        "stage_c_execution_authorized": False,
        "portfolio_selection_authorized": False,
        "phase8a_acceptance_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
        "stage": "EXP015_STAGE_A_READ_ONLY_PROOF_REQUIRED",
        "next_action": "proof complete",
        "authoritative_slot_available": True,
        "read_only_proof_required": True,
        "planned_dispatch_command": (
            "gh workflow run phase8a-exp015-stage-a.yml "
            "--ref main -R Dtwosam/FMP"
        ),
        "operator_decision": "DEC-265",
    }


class Exp015StageAExecutorTests(unittest.TestCase):
    def test_validator_returns_only_frozen_stage_a_dispatch_tuple(self) -> None:
        self.assertEqual(EXECUTOR_DECISION, "DEC-267")
        self.assertEqual(
            validate_exp015_stage_a_fresh_execution_plan(
                _plan(),
                expected_head_sha=HEAD,
            ),
            (
                "gh",
                "workflow",
                "run",
                "phase8a-exp015-stage-a.yml",
                "--ref",
                "main",
                "-R",
                "Dtwosam/FMP",
            ),
        )

    def test_validator_fails_closed_on_identity_or_slot_tamper(self) -> None:
        cases = (
            ("operator_decision", "DEC-264"),
            ("head_sha", "b" * 40),
            ("run_present", True),
            ("run_state", "IN_PROGRESS"),
            ("run_id", 1),
            ("stage", "EXP015_STAGE_A_RUN_IN_PROGRESS"),
            ("authoritative_slot_available", False),
            ("read_only_proof_required", False),
            ("planned_dispatch_command", "gh workflow run wrong.yml"),
            ("stage_a_retry_authorized", True),
            ("trading_authorized", True),
        )
        for field, value in cases:
            with self.subTest(field=field):
                plan = copy.deepcopy(_plan())
                plan[field] = value
                with self.assertRaises(ValueError):
                    validate_exp015_stage_a_fresh_execution_plan(
                        plan,
                        expected_head_sha=HEAD,
                    )

    def test_public_executor_double_checks_fresh_plan_before_submission(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertGreaterEqual(text.count("_fresh_plan()"), 3)
        self.assertIn("if first != second", text)
        self.assertIn("if first_command != second_command", text)
        self.assertIn("fresh_plan_rechecked_twice", text)
        self.assertIn("dispatch_submitted", text)
        self.assertIn("result_claimed", text)
        self.assertIn('GITHUB_RUN_ATTEMPT") != "1"', text)
        self.assertNotIn(
            "gh workflow run phase8a-exp015-stage-a.yml",
            text,
        )
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("replacement", text.lower())


if __name__ == "__main__":
    unittest.main()
