from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github/workflows/"
    "phase8a-exp062-dormant-one-shot-historical-executor-workflow-source-proof.yml"
)


class Exp062DormantOneShotHistoricalExecutorWorkflowSourceProofTests(
    unittest.TestCase
):
    def test_workflow_is_push_main_read_only_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-exp062-dormant-one-shot-historical-executor-workflow-source-proof",
            text,
        )
        self.assertIn("push:", text)
        self.assertIn("- main", text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("contents: read", text)
        self.assertIn("actions: read", text)
        self.assertNotIn("actions: write", text)

    def test_workflow_pins_dec354_dec355_and_template_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = {
            "src/fmp/discovery/exp062_historical_one_shot_executor_workflow_installation_source_contract.py": (
                "e4fc6a7d1faaca50bc6936597f0e8b66fe096985"
            ),
            "src/fmp/discovery/exp062_historical_one_shot_executor_dormant_workflow_source.py": (
                "003e44126d9d6a807efd51b5a589128f6d4b5aac"
            ),
            "docs/superpowers/templates/phase8a-exp062-one-shot-historical-executor.yml.disabled": (
                "51ce87584369be957482460d81649adb1cb9f05d"
            ),
            ".github/workflows/phase8a-exp062-discovery.yml": (
                "1a7d42fd8d03d6ca3eae722209b1ad2a5dd2bc50"
            ),
        }
        for path, blob in expected.items():
            with self.subTest(path=path):
                self.assertIn(f"git hash-object {path}", text)
                self.assertIn(blob, text)

    def test_workflow_requires_active_executor_path_absent(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "test ! -e .github/workflows/phase8a-exp062-one-shot-historical-executor.yml",
            text,
        )

    def test_workflow_uses_direct_source_validation_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("importlib.util.spec_from_file_location", text)
        self.assertIn(
            "build_one_shot_historical_executor_dormant_workflow_source",
            text,
        )
        shell_dispatches = [
            line.strip()
            for line in text.splitlines()
            if line.strip().startswith("gh workflow run ")
        ]
        self.assertEqual(shell_dispatches, [])
        self.assertNotIn("gh workflow enable", text)
        self.assertNotIn("cp docs/superpowers/templates", text)

    def test_workflow_requires_first_exact_main(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertIn('test "$GITHUB_REF" = "refs/heads/main"', text)
        self.assertIn('test "$(git rev-parse HEAD)" = "$GITHUB_SHA"', text)
        self.assertIn(
            'test "$(git rev-parse origin/main)" = "$GITHUB_SHA"',
            text,
        )

    def test_workflow_proves_dormant_source_and_runtime_locks(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('assert report["decision"] == "DEC-355"', text)
        self.assertIn(
            'assert report["dormant_executor_workflow_template_present"] is True',
            text,
        )
        self.assertIn(
            'assert report["dormant_template_dispatch_capable_if_installed"] is True',
            text,
        )
        self.assertIn(
            'assert report["historical_result_attempt_count"] == 0',
            text,
        )
        self.assertIn(
            'assert report["expected_target_run_number"] == 2',
            text,
        )
        for field in (
            "historical_executor_workflow_install_authorized",
            "historical_executor_workflow_installed",
            "historical_executor_available",
            "historical_result_dispatch_authorized",
            "historical_execute_mode_available",
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
                self.assertIn(field, text)

    def test_workflow_persists_only_dormant_source_artifact(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "exp062-dec356-dormant-one-shot-historical-executor-source-${{ github.sha }}",
            text,
        )
        self.assertIn(
            "path: dormant-one-shot-historical-executor-workflow-source.json",
            text,
        )
        self.assertNotIn("one-shot-historical-executor-receipt.json", text)


if __name__ == "__main__":
    unittest.main()
