from __future__ import annotations

from pathlib import Path
import unittest

from fmp.discovery.exp062_historical_one_shot_executor_dormant_workflow_source import (
    ACTIVE_DISCOVERY_WORKFLOW_BLOB_SHA,
    DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA,
    DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH,
    EXPECTED_EXECUTOR_WORKFLOW_PATH,
    build_one_shot_historical_executor_dormant_workflow_source,
    validate_dormant_one_shot_historical_executor_workflow_template,
    validate_one_shot_historical_executor_dormant_workflow_source_dependencies,
)


class Exp062OneShotHistoricalExecutorDormantWorkflowSourceTests(
    unittest.TestCase
):
    def test_source_dependencies_are_exactly_pinned(self) -> None:
        report = (
            validate_one_shot_historical_executor_dormant_workflow_source_dependencies(
                repository_root=Path("."),
            )
        )
        self.assertEqual(
            report["dec354_installation_source_contract"],
            "e4fc6a7d1faaca50bc6936597f0e8b66fe096985",
        )
        self.assertEqual(
            report["dormant_executor_workflow_template"],
            DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_BLOB_SHA,
        )
        self.assertEqual(
            report["active_discovery_workflow"],
            ACTIVE_DISCOVERY_WORKFLOW_BLOB_SHA,
        )

    def test_dormant_template_validates_and_remains_uninstalled(self) -> None:
        text = Path(DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH).read_text(
            encoding="utf-8"
        )
        validate_dormant_one_shot_historical_executor_workflow_template(text)

        report = build_one_shot_historical_executor_dormant_workflow_source(
            repository_root=Path("."),
        )
        self.assertEqual(report["decision"], "DEC-355")
        self.assertEqual(
            report["stage"],
            (
                "EXP062_ONE_SHOT_HISTORICAL_EXECUTOR_DORMANT_TEMPLATE_SOURCE_"
                "FROZEN_ACTIVE_WORKFLOW_UNINSTALLED"
            ),
        )
        self.assertEqual(
            report["expected_executor_workflow_path"],
            EXPECTED_EXECUTOR_WORKFLOW_PATH,
        )
        self.assertTrue(report["dormant_executor_workflow_template_present"])
        self.assertTrue(
            report["dormant_template_dispatch_capable_if_installed"]
        )
        self.assertTrue(
            report["dormant_template_actions_write_required_if_installed"]
        )
        self.assertFalse(
            report["historical_executor_workflow_install_authorized"]
        )
        self.assertFalse(report["historical_executor_workflow_installed"])
        self.assertFalse(report["historical_executor_available"])
        self.assertFalse(report["historical_result_dispatch_authorized"])
        self.assertFalse(report["historical_execute_mode_available"])
        self.assertEqual(report["historical_result_attempt_count"], 0)
        self.assertFalse(report["historical_result_slot_consumed"])
        self.assertEqual(report["expected_target_run_number"], 2)
        self.assertEqual(report["expected_target_run_attempt"], 1)

    def test_template_has_exactly_one_shell_dispatch(self) -> None:
        text = Path(DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH).read_text(
            encoding="utf-8"
        )
        dispatches = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
            == "gh workflow run phase8a-exp062-discovery.yml --ref main"
        ]
        self.assertEqual(
            dispatches,
            ["gh workflow run phase8a-exp062-discovery.yml --ref main"],
        )

    def test_template_rejects_push_trigger(self) -> None:
        text = Path(DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH).read_text(
            encoding="utf-8"
        )
        mutated = text.replace(
            "on:\n  workflow_dispatch:\n",
            "on:\n  push:\n    branches: [main]\n  workflow_dispatch:\n",
        )
        with self.assertRaisesRegex(ValueError, "forbidden token: push:"):
            validate_dormant_one_shot_historical_executor_workflow_template(
                mutated
            )

    def test_template_rejects_second_shell_dispatch(self) -> None:
        text = Path(DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH).read_text(
            encoding="utf-8"
        )
        marker = (
            "          gh workflow run "
            "phase8a-exp062-discovery.yml --ref main\n"
        )
        mutated = text.replace(marker, marker + marker, 1)
        with self.assertRaisesRegex(ValueError, "exactly one shell dispatch"):
            validate_dormant_one_shot_historical_executor_workflow_template(
                mutated
            )

    def test_template_rejects_rerun_command(self) -> None:
        text = Path(DORMANT_EXECUTOR_WORKFLOW_TEMPLATE_PATH).read_text(
            encoding="utf-8"
        )
        mutated = text + "\n# gh run rerun 123\n"
        with self.assertRaisesRegex(ValueError, "forbidden token: gh run rerun"):
            validate_dormant_one_shot_historical_executor_workflow_template(
                mutated
            )


if __name__ == "__main__":
    unittest.main()
