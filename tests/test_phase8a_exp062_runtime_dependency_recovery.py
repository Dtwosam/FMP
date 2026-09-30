from __future__ import annotations

import os
from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_one_shot_executor_recovery_runtime_dependency_authorization import (
    build_recovery_runtime_dependency_recovery_authorization,
    validate_recovery_runtime_dependency_recovery_authorization_sources,
)


WORKFLOW = Path(
    ".github/workflows/"
    "phase8a-exp062-one-shot-historical-executor-recovery-runtime-dependency.yml"
)


@unittest.skipIf(
    os.environ.get("FMP_PREINSTALL_SNAPSHOT") == "1",
    "DEC-439 runtime-dependency recovery exists only after both executor failures",
)
class Exp062RuntimeDependencyRecoveryTests(unittest.TestCase):
    def test_authorization_pins_both_failures_and_all_locks(self) -> None:
        value = build_recovery_runtime_dependency_recovery_authorization(
            repository_root=Path("."),
        )
        self.assertEqual(value["decision"], "DEC-439")
        self.assertEqual(value["failed_original_executor_run_id"], 36702494195)
        self.assertEqual(value["failed_original_executor_run_number"], 2)
        self.assertFalse(
            value["failed_original_executor_dispatched_historical_result"]
        )
        self.assertEqual(value["failed_dec436_recovery_run_id"], 36707978889)
        self.assertEqual(value["failed_dec436_recovery_run_number"], 1)
        self.assertEqual(value["failed_dec436_recovery_run_attempt"], 1)
        self.assertEqual(
            value["failed_dec436_recovery_error_type"],
            "ModuleNotFoundError",
        )
        self.assertEqual(
            value["failed_dec436_recovery_missing_dependency"],
            "polars",
        )
        self.assertFalse(
            value["failed_dec436_recovery_dispatched_historical_result"]
        )
        self.assertEqual(value["historical_result_attempt_count"], 0)
        self.assertFalse(value["historical_result_slot_consumed"])
        self.assertTrue(value["historical_result_slot_verified_available"])
        self.assertEqual(value["expected_second_recovery_run_number"], 1)
        self.assertEqual(value["expected_second_recovery_run_attempt"], 1)
        self.assertEqual(value["expected_target_run_number"], 2)
        self.assertEqual(value["expected_target_run_attempt"], 1)
        self.assertTrue(
            value[
                "explicit_one_shot_runtime_dependency_recovery_dispatch_authorized"
            ]
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

    def test_source_bindings_pin_failed_recovery_and_runtime(self) -> None:
        source = (
            validate_recovery_runtime_dependency_recovery_authorization_sources(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            source["dec436_recovery_authorization"],
            "481fbfbb43557b1b42c0d9bc84ded0775816714e",
        )
        self.assertEqual(
            source["dec436_recovery_workflow"],
            "a2520a108373d25d67dd470794eeb4f0fc9e3187",
        )
        self.assertEqual(
            source["pinned_planning_runtime"],
            "1ff32214dee10d877a067e750cd69ffad96d5fe5",
        )
        self.assertEqual(
            source["active_discovery_workflow"],
            "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50",
        )

    def test_workflow_is_exact_manual_run_one(self) -> None:
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

    def test_workflow_pins_both_failed_run_provenances(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("36702494195", text)
        self.assertIn("109844958600", text)
        self.assertIn("36707978889", text)
        self.assertIn("109862691026", text)
        self.assertIn(
            'assert steps["Require exact DEC-436 recovery authorization"] == "failure"',
            text,
        )
        self.assertIn(
            'assert steps["Dispatch the sole historical result run"] == "skipped"',
            text,
        )
        self.assertGreaterEqual(text.count("assert artifacts == []"), 2)

    def test_pinned_runtime_is_installed_before_authorization_import(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        install = (
            "python -m pip install -r requirements/exp061-discovery-run.txt"
        )
        imported = (
            "from fmp.discovery."
            "exp062_historical_one_shot_executor_recovery_runtime_dependency_authorization "
            "import ("
        )
        self.assertIn('python-version: "3.12.14"', text)
        self.assertIn(install, text)
        self.assertIn(imported, text)
        self.assertLess(text.index(install), text.index(imported))
        self.assertIn(
            'test "$(git hash-object requirements/exp061-discovery-run.txt)" = '
            '"1ff32214dee10d877a067e750cd69ffad96d5fe5"',
            text,
        )

    def test_workflow_dispatches_only_exact_historical_target(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        command = "gh workflow run phase8a-exp062-discovery.yml --ref main"
        self.assertEqual(text.count(command), 2)
        self.assertIn('row.get("run_number") == 2', text)
        self.assertIn('row.get("run_attempt") == 1', text)
        self.assertEqual(
            text.count('row.get("head_sha") == os.environ["GITHUB_SHA"]'),
            2,
        )
        self.assertNotIn("gh workflow run phase8b", text.lower())
        self.assertNotIn("gh workflow run phase9", text.lower())

    def test_receipt_keeps_broad_authority_false(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('"decision": "DEC-439"', text)
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
