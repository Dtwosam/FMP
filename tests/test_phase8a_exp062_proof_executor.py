from __future__ import annotations

import copy
from pathlib import Path
import unittest

from fmp.discovery.exp062_proof_executor import (
    EXP062_PROOF_EXECUTOR_DECISION,
    PROOF_DISPATCH_AUTHORIZED,
    proof_execution_evidence,
    validate_fresh_proof_execution_plan,
)
from fmp.discovery.exp062_proof_operator import build_proof_plan


HEAD = "a" * 40
ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/phase8a-exp062-proof-one-shot-execute.yml"
CLI = ROOT / "scripts/phase8a_exp062_proof_executor.py"


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _runs(*rows: dict[str, object]) -> dict[str, object]:
    return {"workflow_runs": list(rows)}


def _proof_run() -> dict[str, object]:
    return {
        "id": 123,
        "name": "phase8a-exp062-discovery",
        "path": ".github/workflows/phase8a-exp062-discovery.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": HEAD,
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "failure",
    }


class Exp062ProofExecutorTests(unittest.TestCase):
    def test_fresh_plan_authorizes_proof_only(self) -> None:
        plan = build_proof_plan(
            main_branch=_main(),
            workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        command = validate_fresh_proof_execution_plan(
            plan,
            expected_head_sha=HEAD,
        )
        self.assertEqual(
            command,
            (
                "gh",
                "workflow",
                "run",
                "phase8a-exp062-discovery.yml",
                "--ref",
                "main",
            ),
        )

        evidence = proof_execution_evidence(
            plan=plan,
            executor_head_sha=HEAD,
        )
        self.assertEqual(
            evidence["executor_decision"],
            EXP062_PROOF_EXECUTOR_DECISION,
        )
        self.assertTrue(PROOF_DISPATCH_AUTHORIZED)
        self.assertTrue(evidence["proof_dispatch_authorized_by_dec303"])
        self.assertTrue(evidence["proof_dispatch_submitted"])
        self.assertFalse(evidence["historical_result_slot_consumed"])
        self.assertFalse(evidence["historical_result_claimed"])

        for field in (
            "historical_result_dispatch_authorized",
            "historical_discovery_execution_authorized",
            "discovery_result_authorized",
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
            "reserved_robustness_access_authorized",
            "candidate_compilation_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(evidence[field], field)

    def test_existing_run_blocks_executor(self) -> None:
        plan = build_proof_plan(
            main_branch=_main(),
            workflow_runs=_runs(_proof_run()),
            expected_head_sha=HEAD,
        )
        with self.assertRaisesRegex(
            ValueError,
            "fresh zero-run proof plan",
        ):
            validate_fresh_proof_execution_plan(
                plan,
                expected_head_sha=HEAD,
            )

    def test_head_drift_blocks_executor(self) -> None:
        plan = build_proof_plan(
            main_branch=_main(),
            workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        with self.assertRaisesRegex(ValueError, "plan head mismatch"):
            validate_fresh_proof_execution_plan(
                plan,
                expected_head_sha="b" * 40,
            )

    def test_tampered_read_only_plan_is_rejected(self) -> None:
        plan = build_proof_plan(
            main_branch=_main(),
            workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )
        tampered = copy.deepcopy(plan)
        tampered["proof_dispatch_authorized"] = True
        with self.assertRaisesRegex(ValueError, "dispatch-read-only"):
            validate_fresh_proof_execution_plan(
                tampered,
                expected_head_sha=HEAD,
            )

        tampered = copy.deepcopy(plan)
        tampered["historical_result_dispatch_authorized"] = True
        with self.assertRaises(ValueError):
            validate_fresh_proof_execution_plan(
                tampered,
                expected_head_sha=HEAD,
            )

    def test_cli_double_checks_fresh_plan(self) -> None:
        text = CLI.read_text(encoding="utf-8")
        self.assertGreaterEqual(
            text.count("_fresh_plan(expected_head_sha=head_sha)"),
            2,
        )
        self.assertIn("if first != second:", text)
        self.assertIn("if first_command != second_command:", text)
        self.assertNotIn("phase8a_exp062.py cell", text)
        self.assertNotIn("phase8a_exp062.py aggregate", text)
        self.assertNotIn("gh run rerun", text.lower())
        self.assertNotIn("gh run retry", text.lower())

    def test_workflow_is_first_run_one_shot_and_proof_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-exp062-proof-one-shot-execute",
            text,
        )
        self.assertIn("actions: write", text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn(
            'assert run["run_number"] == 1',
            text,
        )
        self.assertIn(
            'assert run["run_attempt"] == 1',
            text,
        )
        self.assertIn(
            'phase8a-exp062-discovery.yml/runs?branch=main&event=workflow_dispatch',
            text,
        )
        self.assertIn(
            'assert relevant == []',
            text,
        )
        self.assertIn(
            'assert run["head_sha"] == os.environ["GITHUB_SHA"]',
            text,
        )
        self.assertNotIn("phase8a_exp062.py cell", text)
        self.assertNotIn("phase8a_exp062.py aggregate", text)
        self.assertNotIn("gh run rerun", text.lower())
        self.assertNotIn("gh run retry", text.lower())


if __name__ == "__main__":
    unittest.main()
