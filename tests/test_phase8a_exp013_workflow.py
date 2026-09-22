from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "phase8a-exp013-stage-a.yml"


class Phase8AExp013WorkflowTests(unittest.TestCase):
    def test_workflow_is_manual_main_only_and_covers_all_nine_cells(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("refs/heads/main", text)

        self.assertIn("EURUSD", text)
        self.assertIn("GBPUSD", text)
        self.assertIn("USDJPY", text)
        self.assertIn("timeframe: [5m, 15m, 1h]", text)

        self.assertIn("10325737935", text)
        self.assertIn(
            "db0e65490bc1ff80f6d7a0498dd64322563f838a7f70c740617c41bd19e423c3",
            text,
        )
        self.assertIn("10326096831", text)
        self.assertIn(
            "fe42669ed46788d8c7db33b903db79c29034a666acd52213c3c28ec7d4ea88c2",
            text,
        )
        self.assertIn("10327600628", text)
        self.assertIn(
            "6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72",
            text,
        )

        self.assertIn("scripts/phase8a_exp013.py cell", text)
        self.assertIn(' --code-commit "${GITHUB_SHA}"', text)
        self.assertIn("phase8a-exp013-stage-a-cell-", text)
        self.assertIn("actions/upload-artifact", text)

    def test_authorization_job_requires_all_cell_artifacts_and_never_runs_stage_b(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("needs: stage-a-cell", text)
        self.assertIn("actions/download-artifact", text)
        self.assertIn("phase8a-exp013-stage-a-cell-*", text)
        self.assertIn("scripts/phase8a_exp013.py authorize", text)
        self.assertIn("stage-a-authorization.json", text)
        self.assertIn('"strategy_identity_count"] == 36', text)
        self.assertIn('"cell_count"] == 9', text)
        self.assertIn('"promotion_authorized"] is False', text)
        self.assertIn("stage_b_source_open_authorized", text)

        self.assertNotIn("stage-b", text.lower())
        self.assertNotIn("2026-08-21", text)


if __name__ == "__main__":
    unittest.main()
