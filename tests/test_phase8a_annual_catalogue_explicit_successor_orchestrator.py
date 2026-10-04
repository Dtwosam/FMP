from __future__ import annotations

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    REPOSITORY_ROOT
    / ".github/workflows/phase8a-annual-catalogue-explicit-successor-orchestrator.yml"
)


class AnnualCatalogueExplicitSuccessorOrchestratorTests(unittest.TestCase):
    def test_orchestrator_is_second_path_scoped_recovery(self) -> None:
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
        self.assertIn('test "$GITHUB_RUN_NUMBER" = "2"', text)
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

    def test_orchestrator_proves_failed_first_attempt_before_retry(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for run_id in (
            "37200339487",
            "37200350839",
            "37200374023",
            "37200408776",
        ):
            self.assertIn(run_id, text)
        self.assertIn(
            '"head_sha": "66b0a9ba46ac0350abe635c5b8d1a6de60559648"',
            text,
        )
        self.assertIn('"conclusion": "failure"', text)
        self.assertIn('"conclusion": "success"', text)

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
            "052486811893386d3f3f6a24bf53be93b71df9d5",
            "601ee6aeb1db10cee01d5b9b6a084c3780b4076f",
            "0903d7ea67f45aa16522d43b60c2ea07fba13334",
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
        self.assertIn('"decision": "DEC-530"', text)
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
