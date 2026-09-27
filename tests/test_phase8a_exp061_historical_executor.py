from __future__ import annotations

import copy
from pathlib import Path
import unittest

from fmp.discovery.historical_execution_operator import (
    build_historical_execution_plan,
)
from fmp.discovery.historical_executor import (
    DISCOVERY_RESULT_AUTHORIZED,
    EXP061_HISTORICAL_EXECUTOR_DECISION,
    HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED,
    HISTORICAL_RESULT_DISPATCH_AUTHORIZED,
    REPLACEMENT_RUN_AUTHORIZED,
    RERUN_AUTHORIZED,
    RETRY_AUTHORIZED,
    historical_execution_evidence,
    validate_fresh_historical_execution_plan,
    validate_reviewed_execution_plan,
)


HEAD = "a" * 40
ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp061-historical-one-shot-execute.yml"
)
CLI = ROOT / "scripts/phase8a_exp061_historical_executor.py"


def _main() -> dict[str, object]:
    return {"name": "main", "commit": {"sha": HEAD}}


def _proof() -> dict[str, object]:
    return {
        "id": 36319888985,
        "name": "phase8a-exp061-discovery",
        "path": ".github/workflows/phase8a-exp061-discovery.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": "041b7b2f5aac8821156fab346df8ab30f4be2a7b",
        "run_number": 1,
        "run_attempt": 1,
        "status": "completed",
        "conclusion": "failure",
    }


def _historical() -> dict[str, object]:
    return {
        "id": 40000000000,
        "name": "phase8a-exp061-discovery",
        "path": ".github/workflows/phase8a-exp061-discovery.yml",
        "event": "workflow_dispatch",
        "head_branch": "main",
        "head_sha": HEAD,
        "run_number": 2,
        "run_attempt": 1,
        "status": "queued",
        "conclusion": None,
    }


def _runs(*extra: dict[str, object]) -> dict[str, object]:
    return {"workflow_runs": [_proof(), *extra]}


def _reviewed() -> dict[str, object]:
    return {
        "decision": "DEC-288",
        "version": (
            "fmp-exp061-reviewed-historical-execution-plan-proof-v1"
        ),
        "stage": (
            "EXP061_HISTORICAL_EXECUTION_PLAN_PROOF_REVIEWED_AND_FROZEN"
        ),
        "proof_run_id": 36329787371,
        "proof_artifact_id": 10935233025,
        "proof_artifact_digest": (
            "sha256:bb81bd8f0cb1adfc0054db4f5c16f13808793c520d443a0f05a89a90f92a415d"
        ),
        "plan_raw_sha256": (
            "2ca76921e17096b444202573a950825244e07c27e0f476cecfb510ad5e0a95e5"
        ),
        "plan_canonical_sha256": (
            "86b37433e183bfd9199822da0212b79fe11950461206335fc53e6f783210a74e"
        ),
        "historical_result_attempt_count": 0,
        "historical_result_slot_consumed": False,
        "historical_result_slot_verified_available": True,
        "expected_target_run_number": 2,
        "expected_target_run_attempt": 1,
        "planned_dispatch_command_frozen": (
            "gh workflow run phase8a-exp061-discovery.yml --ref main"
        ),
        "historical_execution_source_authorized": True,
        "historical_discovery_execution_authorized": True,
        "discovery_result_authorized": True,
        "historical_result_dispatch_authorized": False,
        "historical_execute_mode_available": False,
        "rerun_authorized": False,
        "retry_authorized": False,
        "replacement_run_authorized": False,
        "reserved_robustness_access_authorized": False,
        "candidate_compilation_authorized": False,
        "promotion_authorized": False,
        "phase8b_authorized": False,
        "demo_order_authorized": False,
        "broker_mutation_authorized": False,
        "live_order_authorized": False,
        "real_money_authorized": False,
        "trading_authorized": False,
    }


class Exp061HistoricalExecutorTests(unittest.TestCase):
    def _fresh_plan(self) -> dict[str, object]:
        return build_historical_execution_plan(
            repository_root=ROOT,
            main_branch=_main(),
            workflow_runs=_runs(),
            expected_head_sha=HEAD,
        )

    def test_fresh_plan_authorizes_exactly_one_dispatch(self) -> None:
        plan = self._fresh_plan()
        command = validate_fresh_historical_execution_plan(
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

        evidence = historical_execution_evidence(
            plan=plan,
            reviewed_predecessor=_reviewed(),
            executor_head_sha=HEAD,
        )
        self.assertEqual(
            evidence["executor_decision"],
            EXP061_HISTORICAL_EXECUTOR_DECISION,
        )
        self.assertTrue(evidence["fresh_plan_rechecked_twice"])
        self.assertTrue(
            evidence["historical_result_dispatch_authorized_by_dec289"]
        )
        self.assertTrue(evidence["historical_result_dispatch_submitted"])
        self.assertTrue(
            evidence["historical_result_slot_consumed_on_submission"]
        )
        self.assertEqual(
            evidence["pre_dispatch_historical_result_attempt_count"],
            0,
        )
        self.assertFalse(
            evidence["pre_dispatch_historical_result_slot_consumed"]
        )
        self.assertEqual(evidence["historical_result_attempt_count"], 1)
        self.assertTrue(evidence["historical_result_slot_consumed"])
        self.assertEqual(evidence["expected_target_run_number"], 2)
        self.assertEqual(evidence["expected_target_run_attempt"], 1)
        self.assertEqual(
            evidence["reviewed_proof_artifact_id"],
            10935233025,
        )
        self.assertEqual(
            evidence["reviewed_plan_raw_sha256"],
            _reviewed()["plan_raw_sha256"],
        )
        self.assertEqual(
            evidence["reviewed_plan_canonical_sha256"],
            _reviewed()["plan_canonical_sha256"],
        )

    def test_existing_historical_run_blocks_executor(self) -> None:
        plan = build_historical_execution_plan(
            repository_root=ROOT,
            main_branch=_main(),
            workflow_runs=_runs(_historical()),
            expected_head_sha=HEAD,
        )
        with self.assertRaisesRegex(
            ValueError,
            "fresh unused historical slot",
        ):
            validate_fresh_historical_execution_plan(
                plan,
                expected_head_sha=HEAD,
            )

    def test_head_drift_blocks_executor(self) -> None:
        plan = self._fresh_plan()
        with self.assertRaisesRegex(ValueError, "plan head mismatch"):
            validate_fresh_historical_execution_plan(
                plan,
                expected_head_sha="b" * 40,
            )

    def test_tampered_target_or_dispatch_lock_is_rejected(self) -> None:
        plan = self._fresh_plan()
        tampered = copy.deepcopy(plan)
        tampered["expected_target_run_number"] = 3
        with self.assertRaises(ValueError):
            validate_fresh_historical_execution_plan(
                tampered,
                expected_head_sha=HEAD,
            )

        tampered = copy.deepcopy(plan)
        tampered["historical_result_dispatch_authorized"] = True
        with self.assertRaises(ValueError):
            validate_fresh_historical_execution_plan(
                tampered,
                expected_head_sha=HEAD,
            )

    def test_reviewed_predecessor_identity_is_exact(self) -> None:
        reviewed = validate_reviewed_execution_plan(_reviewed())
        self.assertEqual(reviewed["decision"], "DEC-288")

        tampered = _reviewed()
        tampered["proof_artifact_id"] = 10935233026
        with self.assertRaisesRegex(
            ValueError,
            "reviewed predecessor proof_artifact_id mismatch",
        ):
            validate_reviewed_execution_plan(tampered)

    def test_executor_authority_is_narrow(self) -> None:
        self.assertTrue(HISTORICAL_RESULT_DISPATCH_AUTHORIZED)
        self.assertTrue(HISTORICAL_DISCOVERY_EXECUTION_AUTHORIZED)
        self.assertTrue(DISCOVERY_RESULT_AUTHORIZED)
        self.assertFalse(RERUN_AUTHORIZED)
        self.assertFalse(RETRY_AUTHORIZED)
        self.assertFalse(REPLACEMENT_RUN_AUTHORIZED)

        evidence = historical_execution_evidence(
            plan=self._fresh_plan(),
            reviewed_predecessor=_reviewed(),
            executor_head_sha=HEAD,
        )
        for field in (
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

    def test_cli_revalidates_reviewed_artifact_and_double_checks_plan(self) -> None:
        text = CLI.read_text(encoding="utf-8")
        self.assertIn(
            "freeze_reviewed_historical_execution_plan_proof",
            text,
        )
        self.assertIn("DEC287_PROOF_ARTIFACT_ID", text)
        self.assertIn("DEC287_PLAN_RAW_SHA256", text)
        self.assertGreaterEqual(text.count("_fresh_plan(expected_head_sha=head_sha)"), 2)
        self.assertIn("if first != second:", text)
        self.assertNotIn("gh run rerun", text.lower())
        self.assertNotIn("gh run retry", text.lower())

    def test_workflow_is_first_push_one_shot_and_pins_exact_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-exp061-historical-one-shot-execute",
            text,
        )
        self.assertIn("actions: write", text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn(
            "Require this one-shot executor has never run before",
            text,
        )
        self.assertIn(
            'assert run["run_number"] == 1',
            text,
        )
        self.assertIn(
            'src/fmp/discovery/historical_execution_plan_result_decision.py)" = "b01ee28b7ab636cb6729423504ff8e2038ce4375"',
            text,
        )
        self.assertIn(
            'src/fmp/discovery/historical_executor.py)" = "82dbec289ed69e7333a90fd28ce430b024a99936"',
            text,
        )
        self.assertIn(
            'scripts/phase8a_exp061_historical_executor.py)" = "a899b71c1054e4ccd5639f4487dad038b2e1f55f"',
            text,
        )
        self.assertIn(
            'assert proof["run_number"] == 1',
            text,
        )
        self.assertIn(
            'assert run["run_number"] == 2',
            text,
        )
        self.assertIn(
            'assert run["run_attempt"] == 1',
            text,
        )
        self.assertIn(
            'assert run["head_sha"] == os.environ["GITHUB_SHA"]',
            text,
        )
        self.assertNotIn("gh run rerun", text.lower())
        self.assertNotIn("gh run retry", text.lower())
        self.assertNotIn("phase8a_exp061.py cell", text)
        self.assertNotIn("phase8a_exp061.py aggregate", text)


if __name__ == "__main__":
    unittest.main()
