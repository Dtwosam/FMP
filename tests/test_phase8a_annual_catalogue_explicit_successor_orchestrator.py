from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-explicit-successor-orchestrator.yml"
)


class AnnualCatalogueExplicitSuccessorOrchestratorTests(unittest.TestCase):
    def test_orchestrator_is_one_shot_path_scoped_push_recovery(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "name: phase8a-annual-catalogue-explicit-successor-orchestrator",
            text,
        )
        self.assertIn("  push:", text)
        self.assertIn("      - main", text)
        self.assertIn(
            "      - .github/workflows/"
            "phase8a-annual-catalogue-explicit-successor-orchestrator.yml",
            text,
        )
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "1"', text)
        self.assertIn('test "$GITHUB_RUN_ATTEMPT" = "1"', text)
        self.assertNotIn("workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)

    def test_orchestrator_pins_successful_run377_and_no_run378(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('RUN377_ID: "37198002653"', text)
        self.assertIn(
            'RUN377_HEAD_SHA: "a89db974be9a94481e7ed0990476bc661012f1e4"',
            text,
        )
        self.assertIn("assert set(by_number) == {1, 376, 377}", text)
        self.assertIn("37191637168", text)
        self.assertIn("37126711695", text)

    def test_orchestrator_uses_explicit_successor_workflows_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        workflows = (
            "phase8a-annual-catalogue-2015-replacement-runtime-evidence.yml",
            "phase8a-annual-catalogue-2016-activation-plan.yml",
            "phase8a-annual-catalogue-2016-runtime-install-executor.yml",
            "phase8a-annual-catalogue-2016-run377-runtime-evidence.yml",
        )
        for workflow in workflows:
            self.assertIn(workflow, text)
        self.assertEqual(text.count("gh workflow run"), 4)
        self.assertNotIn(
            "gh workflow run phase8a-annual-pattern-catalogue.yml",
            text,
        )
        self.assertNotIn("gh run rerun", text)
        self.assertNotIn("rerun-failed-jobs", text)

    def test_orchestrator_pins_recovered_source_chain(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for blob in (
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
            "b259e4013a7e74eb8df864acad04a31b7a1eac09",
            "1893cd0d96e342ad30e8d5bdfc58b81781d28be6",
            "1a4d9c975f79140f9d7e2173a4e102e4d07b2a6c",
            "dcc4d71990e113acc25fd607ef9919734f2c0731",
            "2a51f6d5a15ee6edf212009bd646047a3ec2546c",
        ):
            self.assertIn(blob, text)

    def test_run378_and_dec522_must_complete_successfully(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(".run_number == 378 and .run_attempt == 1", text)
        self.assertIn('test "$conclusion" = "success"', text)
        self.assertIn("Recover DEC-522 only if automatic reviewer is absent", text)
        self.assertIn("-f target_run_number=378", text)
        self.assertIn(
            "annual-catalogue-2016-dec522-runtime-binding-$run378_id",
            text,
        )

    def test_receipt_keeps_later_authority_locked(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('"decision": "DEC-529"', text)
        for field in (
            "run379_or_later_authorized",
            "next_segment_execution_authorized",
            "strategy_v1_synthesis_authorized",
            "promotion_authorized",
            "phase8b_authorized",
            "broker_mutation_authorized",
            "live_order_authorized",
            "real_money_authorized",
            "trading_authorized",
        ):
            self.assertIn(f'"{field}": False', text)


if __name__ == "__main__":
    unittest.main()
