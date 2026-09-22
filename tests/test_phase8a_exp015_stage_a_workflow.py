from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "phase8a-exp015-stage-a.yml"


class Exp015StageAWorkflowTests(unittest.TestCase):
    def test_workflow_is_manual_frozen_and_covers_exact_nine_cells(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("inputs:", text)
        self.assertNotIn("schedule:", text)
        self.assertNotIn("pull_request:", text)
        for symbol in ("EURUSD", "GBPUSD", "USDJPY"):
            self.assertIn(symbol, text)
        self.assertIn("timeframe: [5m, 15m, 1h]", text)
        self.assertIn("10325737935", text)
        self.assertIn("db0e65490bc1ff80f6d7a0498dd64322563f838a7f70c740617c41bd19e423c3", text)
        self.assertIn("10326096831", text)
        self.assertIn("fe42669ed46788d8c7db33b903db79c29034a666acd52213c3c28ec7d4ea88c2", text)
        self.assertIn("10327600628", text)
        self.assertIn("6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72", text)
        self.assertIn("scripts/phase8a_exp015.py catalog", text)
        self.assertIn("scripts/phase8a_exp015.py stage-a-cell", text)
        self.assertIn("scripts/phase8a_exp015.py stage-a-authorize", text)
        self.assertIn("catalog-freeze:", text)
        self.assertIn("needs: catalog-freeze", text)
        self.assertIn("phase8a-exp015-catalog-${{ github.sha }}", text)
        self.assertIn("actions/download-artifact", text)
        self.assertIn("actions/upload-artifact", text)
        self.assertNotIn("2023-01-01", text)
        self.assertNotIn("2026-08-21", text)
        self.assertNotIn("stage-b", text.lower())
        self.assertNotIn("stage-c", text.lower())

    def test_workflow_verifies_exact_stage_a_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("'2015-01-01'", text)
        self.assertIn("'2019-01-01'", text)
        self.assertIn("'RETROSPECTIVE_ALREADY_SEEN'", text)
        self.assertIn("catalog_identity_sha256", text)
        self.assertIn("strategy_identity_count", text)
        self.assertIn("scenario_run_count", text)
        self.assertIn("ranking_cell_count", text)
        self.assertIn("maximum_stage_a_survivors", text)
        self.assertIn("stage_b_source_open_authorized", text)
        self.assertIn("promotion_authorized", text)
        self.assertIn("historical_status_mutation_authorized", text)


if __name__ == "__main__":
    unittest.main()
