from __future__ import annotations

import os
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_one_shot_executor_recovery_authorization import (
    FAILED_EXECUTOR_HEAD_SHA,
    FAILED_EXECUTOR_JOB_ID,
    FAILED_EXECUTOR_RUN_ID,
    build_one_shot_executor_recovery_authorization,
    validate_one_shot_executor_recovery_authorization_sources,
)


WORKFLOW = Path(
    ".github/workflows/"
    "phase8a-exp062-one-shot-historical-executor-recovery.yml"
)


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-436 recovery exists only after the installed executor failure",
)
class Exp062OneShotHistoricalExecutorRecoveryTests(unittest.TestCase):
    def test_authorization_pins_failed_run_and_all_locks(self) -> None:
        value = build_one_shot_executor_recovery_authorization(
            repository_root=Path("."),
        )
        self.assertEqual(value["decision"], "DEC-436")
        self.assertEqual(value["failed_executor_run_id"], FAILED_EXECUTOR_RUN_ID)
        self.assertEqual(value["failed_executor_job_id"], FAILED_EXECUTOR_JOB_ID)
        self.assertEqual(
            value["failed_executor_head_sha"],
            FAILED_EXECUTOR_HEAD_SHA,
        )
        self.assertEqual(value["failed_executor_run_number"], 2)
        self.assertEqual(value["failed_executor_run_attempt"], 1)
        self.assertEqual(value["failed_executor_run_conclusion"], "failure")
        self.assertFalse(value["failed_executor_dispatched_historical_result"])
        self.assertEqual(value["historical_result_attempt_count"], 0)
        self.assertFalse(value["historical_result_slot_consumed"])
        self.assertTrue(value["historical_result_slot_verified_available"])
        self.assertEqual(value["expected_recovery_run_number"], 1)
        self.assertEqual(value["expected_recovery_run_attempt"], 1)
        self.assertEqual(value["expected_target_run_number"], 2)
        self.assertEqual(value["expected_target_run_attempt"], 1)
        self.assertTrue(
            value["explicit_one_shot_executor_recovery_dispatch_authorized"]
        )
        self.assertFalse(value["historical_execute_mode_available"])
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
            with self.subTest(field=field):
                self.assertFalse(value[field])

    def test_authorization_sources_preserve_original_executor(self) -> None:
        source = validate_one_shot_executor_recovery_authorization_sources(
            repository_root=Path("."),
        )
        self.assertEqual(
            source["original_executor_workflow"],
            "51ce87584369be957482460d81649adb1cb9f05d",
        )
        self.assertEqual(
            source["discovery_workflow"],
            "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50",
        )
        self.assertEqual(
            source["dec435_runtime_freeze"],
            "d70fb2ef8f55462be278dd22e42a733b5e03fc67",
        )

    def test_recovery_workflow_is_exact_manual_run_one(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("push:", text)
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn('test "$GITHUB_REF" = "refs/heads/main"', text)
        self.assertIn(
            'test "$(git rev-parse origin/main)" = "$GITHUB_SHA"',
            text,
        )

    def test_recovery_workflow_pins_failed_executor_provenance(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("36702494195", text)
        self.assertIn("109844958600", text)
        self.assertIn(
            "59b55d519449e20cf396d70ed9a5722b989d933a",
            text,
        )
        self.assertIn('assert run["run_number"] == 2', text)
        self.assertIn('assert run["run_attempt"] == 1', text)
        self.assertIn('assert run["conclusion"] == "failure"', text)
        self.assertIn(
            'assert steps["Dispatch the sole historical result run"] == "skipped"',
            text,
        )
        self.assertIn("assert artifacts == []", text)

    def test_recovery_workflow_dispatches_only_historical_target(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        command = (
            "gh workflow run phase8a-exp062-discovery.yml --ref main"
        )
        self.assertEqual(text.count(command), 2)
        self.assertIn('row.get("run_number") == 2', text)
        self.assertIn('row.get("run_attempt") == 1', text)
        self.assertEqual(
            text.count('row.get("head_sha") == os.environ["GITHUB_SHA"]'),
            2,
        )
        self.assertNotIn("gh workflow run phase8b", text.lower())
        self.assertNotIn("gh workflow run phase9", text.lower())

    def test_recovery_receipt_keeps_broad_authority_false(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('"decision": "DEC-436"', text)
        for field in (
            "rerun_authorized",
            "retry_authorized",
            "replacement_run_authorized",
            "reserved_robustness_access_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "demo_order_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            with self.subTest(field=field):
                self.assertIn(f'"{field}": False', text)


if __name__ == "__main__":
    unittest.main()
