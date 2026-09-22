from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "phase8a-exp016-acceptance.yml"


class Phase8AAcceptanceWorkflowTests(unittest.TestCase):
    def test_workflow_is_manual_main_only_and_source_free(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("selection_run_id:", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("Require main workflow dispatch", text)
        self.assertIn("refs/heads/main", text)
        self.assertIn("phase8a-exp014-selection", text)
        self.assertIn(".github/workflows/phase8a-exp014-selection.yml", text)
        self.assertIn("head_branch", text)
        self.assertNotIn("10325737935", text)
        self.assertNotIn("10326096831", text)
        self.assertNotIn("10327600628", text)
        self.assertNotIn(".phase2-accepted", text)

    def test_acceptance_is_written_only_after_repo_and_phase3_checks(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        review_index = text.index("Compile Phase 8A acceptance review")
        self.assertLess(text.index("Validate repository workflow YAML"), review_index)
        self.assertLess(text.index("Run repository unit tests"), review_index)
        self.assertLess(text.index("Compile package"), review_index)
        self.assertLess(text.index("Verify Phase 3 acceptance evidence"), review_index)
        self.assertIn("scripts/phase8a_acceptance.py review", text)
        self.assertIn('--code-commit "${GITHUB_SHA}"', text)

    def test_exact_upstream_artifacts_and_safety_flags_are_verified(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("phase8a-exp014-selection-preflight-${{ steps.selection_run.outputs.head_sha }}", text)
        self.assertIn("phase8a-exp014-selection-${{ steps.selection_run.outputs.head_sha }}", text)
        self.assertIn("PHASE8A_SHADOW_CANDIDATE_ACCEPTED", text)
        self.assertIn("PHASE8A_RESEARCH_REJECTED", text)
        for field in (
            "promotion_authorized",
            "demo_order_authorized",
            "live_order_authorized",
            "broker_mutation_authorized",
            "real_money_authorized",
            "phase9_authorized",
        ):
            self.assertIn(field, text)


if __name__ == "__main__":
    unittest.main()
