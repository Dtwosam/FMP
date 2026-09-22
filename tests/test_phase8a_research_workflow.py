from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "phase8a-retrospective-baseline.yml"


class Phase8ARetrospectiveWorkflowTests(unittest.TestCase):
    def test_workflow_is_manual_source_free_and_covers_all_three_pairs_and_timeframes(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)
        self.assertNotIn("pull_request:", text)
        self.assertIn("EURUSD", text)
        self.assertIn("GBPUSD", text)
        self.assertIn("USDJPY", text)
        self.assertIn("5m", text)
        self.assertIn("15m", text)
        self.assertIn("1h", text)

        self.assertIn("10325737935", text)
        self.assertIn("db0e65490bc1ff80f6d7a0498dd64322563f838a7f70c740617c41bd19e423c3", text)
        self.assertIn("10326096831", text)
        self.assertIn("fe42669ed46788d8c7db33b903db79c29034a666acd52213c3c28ec7d4ea88c2", text)
        self.assertIn("10327600628", text)
        self.assertIn("6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72", text)

        self.assertIn("scripts/phase8a_research.py inventory", text)
        self.assertIn("scripts/phase8a_research.py batch", text)
        self.assertIn("--code-commit \"\${GITHUB_SHA}\"", text)
        self.assertIn("--start \"\${RESEARCH_START}\"", text)
        self.assertIn("--end-exclusive \"\${RESEARCH_END_EXCLUSIVE}\"", text)
        self.assertIn("promotion_authorized", text)
        self.assertIn("upload-artifact", text)


if __name__ == "__main__":
    unittest.main()
