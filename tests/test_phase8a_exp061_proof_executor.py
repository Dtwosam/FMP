from __future__ import annotations

import copy
from pathlib import Path
import unittest

from fmp.discovery.proof_executor import (
    DISCOVERY_RESULT_AUTHORIZED,
    EXP061_PROOF_EXECUTOR_DECISION,
    HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    PROOF_DISPATCH_AUTHORIZED,
    REPLACEMENT_RUN_AUTHORIZED,
    RERUN_AUTHORIZED,
    RETRY_AUTHORIZED,
    proof_execution_evidence,
    validate_fresh_proof_execution_plan,
)
from fmp.discovery.proof_operator import build_proof_plan


HEAD = "a" * 40


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _runs() -> dict[str, object]:
    return {"workflow_runs": []}


class Exp061ProofExecutorTests(unittest.TestCase):
    def test_fresh_double_check_shape_authorizes_proof_only(self) -> None:
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
                "phase8a-exp061-discovery.yml",
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
            EXP061_PROOF_EXECUTOR_DECISION,
        )
        self.assertTrue(evidence["fresh_plan_rechecked_twice"])
        self.assertTrue(evidence["proof_dispatch_authorized_by_dec279"])
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
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertFalse(evidence[field], field)

    def test_existing_proof_run_blocks_executor(self) -> None:
        runs = {
            "workflow_runs": [
                {
                    "id": 123,
                    "name": "phase8a-exp061-discovery",
                    "path": ".github/workflows/phase8a-exp061-discovery.yml",
                    "event": "workflow_dispatch",
                    "head_branch": "main",
                    "head_sha": HEAD,
                    "status": "completed",
                    "conclusion": "failure",
                }
            ]
        }
        plan = build_proof_plan(
            main_branch=_main(),
            workflow_runs=runs,
            expected_head_sha=HEAD,
        )
        with self.assertRaisesRegex(ValueError, "fresh missing-run plan"):
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
        with self.assertRaisesRegex(ValueError, "must remain false"):
            validate_fresh_proof_execution_plan(
                tampered,
                expected_head_sha=HEAD,
            )

    def test_authority_constants_are_narrow(self) -> None:
        self.assertTrue(PROOF_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertFalse(HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED)
        self.assertFalse(DISCOVERY_RESULT_AUTHORIZED)
        self.assertFalse(RERUN_AUTHORIZED)
        self.assertFalse(RETRY_AUTHORIZED)
        self.assertFalse(REPLACEMENT_RUN_AUTHORIZED)

    def test_executor_surfaces_have_no_historical_cell_or_retry_path(self) -> None:
        root = Path(__file__).resolve().parents[1]
        cli = (root / "scripts/phase8a_exp061_proof_executor.py").read_text()
        workflow = (
            root
            / ".github/workflows/phase8a-exp061-proof-one-shot-execute.yml"
        ).read_text()

        for text in (cli, workflow):
            self.assertNotIn("phase8a_exp061.py cell", text)
            self.assertNotIn("phase8a_exp061.py aggregate", text)
            self.assertNotIn("rerun", text.lower())
            self.assertNotIn("retry", text.lower())

        self.assertNotIn("gh workflow run", cli)
        self.assertIn('actions: write', workflow)
        self.assertIn(
            'test "$(git hash-object .github/workflows/phase8a-exp061-discovery.yml)" = "d4eb02d380ae8c9a5b95e6520cbb7ca192254cb9"',
            workflow,
        )
        self.assertIn(
            'test "$(git hash-object src/fmp/discovery/proof_operator.py)" = "b8af93555656d4da57ead8fc4b66ae66e62a2de7"',
            workflow,
        )


if __name__ == "__main__":
    unittest.main()
