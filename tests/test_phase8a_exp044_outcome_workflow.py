from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "phase8a-exp044-market-outcomes.yml"


class Exp044OutcomeWorkflowTests(unittest.TestCase):
    def test_workflow_is_manual_main_only_and_requires_feature_run(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("feature_run_id:", text)
        self.assertNotIn("schedule:", text)
        self.assertNotIn("pull_request:", text)
        self.assertIn('test "$GITHUB_REF" = "refs/heads/main"', text)
        self.assertIn('run["name"] == "phase8a-exp044-market-features"', text)
        self.assertIn(
            'run["path"] == ".github/workflows/phase8a-exp044-market-features.yml"',
            text,
        )
        self.assertIn('run["event"] == "workflow_dispatch"', text)
        self.assertIn('run["head_branch"] == "main"', text)
        self.assertIn('run["conclusion"] == "success"', text)

    def test_workflow_covers_exact_nine_cells_and_existing_phase2_sources(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for symbol in ("EURUSD", "GBPUSD", "USDJPY"):
            self.assertIn(symbol, text)
        self.assertIn("timeframe: [5m, 15m, 1h]", text)
        self.assertIn("10325737935", text)
        self.assertIn("db0e65490bc1ff80f6d7a0498dd64322563f838a7f70c740617c41bd19e423c3", text)
        self.assertIn("10326096831", text)
        self.assertIn("fe42669ed46788d8c7db33b903db79c29034a666acd52213c3c28ec7d4ea88c2", text)
        self.assertIn("10327600628", text)
        self.assertIn("6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72", text)
        self.assertIn("scripts/phase8a_market_outcomes.py", text)
        self.assertIn("scripts/phase8a_market_outcome_evidence.py", text)

    def test_workflow_revalidates_feature_evidence_and_keeps_model_locked(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("load_feature_evidence_index", text)
        self.assertIn("feature_evidence_fingerprint", text)
        self.assertIn('manifest["model_fit_authorized"] is False', text)
        self.assertIn('manifest["promotion_authorized"] is False', text)
        self.assertIn('evidence["outcome_evidence_complete"] is True', text)
        self.assertIn('evidence["model_fit_authorized"] is False', text)
        self.assertIn('evidence["demo_order_authorized"] is False', text)
        self.assertIn('evidence["broker_mutation_authorized"] is False', text)
        self.assertIn('evidence["live_order_authorized"] is False', text)
        self.assertIn('evidence["real_money_authorized"] is False', text)


if __name__ == "__main__":
    unittest.main()
