from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "phase8b-exp017-design.yml"


class Phase8BDesignWorkflowTests(unittest.TestCase):
    def test_workflow_is_manual_main_only_and_requires_accepted_dec045(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("acceptance_run_id:", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("Require main workflow dispatch", text)
        self.assertIn("refs/heads/main", text)
        self.assertIn("phase8a-exp016-acceptance", text)
        self.assertIn(".github/workflows/phase8a-exp016-acceptance.yml", text)
        self.assertIn("PHASE8A_SHADOW_CANDIDATE_ACCEPTED", text)
        self.assertIn("phase8b_design_authorized", text)

    def test_workflow_is_source_free_and_does_not_register_or_start_campaign(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("10325737935", text)
        self.assertNotIn("10326096831", text)
        self.assertNotIn("10327600628", text)
        self.assertNotIn(".phase2-accepted", text)
        self.assertNotIn("phase8_shadow.py run", text)
        self.assertNotIn("phase8_shadow.py register", text)
        self.assertNotIn("MetaTrader5", text)
        self.assertIn("scripts/phase8b_shadow.py design", text)
        self.assertIn("campaign_registration_authorized", text)
        self.assertIn("campaign_start_authorized", text)

    def test_workflow_pins_exact_acceptance_artifact_by_upstream_head_sha(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("head_branch", text)
        self.assertIn("head_sha", text)
        self.assertIn("phase8a-exp016-acceptance-${{ steps.acceptance_run.outputs.head_sha }}", text)
        self.assertIn('--code-commit "${GITHUB_SHA}"', text)


if __name__ == "__main__":
    unittest.main()
