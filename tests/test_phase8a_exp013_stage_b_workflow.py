from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
WORKFLOW=ROOT/".github"/"workflows"/"phase8a-exp013-stage-b.yml"

class Exp013StageBWorkflowTests(unittest.TestCase):
    def test_stage_b_requires_stage_a_run_and_verifies_before_source_download(self):
        text=WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("stage_a_run_id:", text)
        self.assertIn("phase8a-exp013-stage-a", text)
        self.assertIn("stage_b_source_open_authorized", text)
        self.assertIn("scripts/phase8a_exp013.py stage-b-run", text)
        self.assertIn("10325737935", text)
        self.assertIn("10326096831", text)
        self.assertIn("10327600628", text)
        guard=text.index("Verify exact Stage A authorization")
        source=text.index("Download required accepted Phase 2 artifacts")
        self.assertLess(guard, source)
        self.assertNotIn("research_start:", text)
        self.assertNotIn("research_end", text)
        self.assertIn('"2024-01-01"', text)
        self.assertIn('"2026-08-21"', text)
        self.assertIn("historical_qualification_review_authorized", text)
        self.assertIn("promotion_authorized", text)

if __name__=="__main__":
    unittest.main()
