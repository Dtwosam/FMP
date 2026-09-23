from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "phase8a-exp044-market-features.yml"


class Exp044FeatureWorkflowTests(unittest.TestCase):
    def test_workflow_is_manual_main_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("schedule:", text)
        self.assertNotIn("pull_request:", text)
        self.assertIn('test "$GITHUB_REF" = "refs/heads/main"', text)

    def test_workflow_batches_by_pair_but_preserves_nine_cell_outputs(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("matrix.timeframe", text)
        self.assertNotIn("timeframe: [5m, 15m, 1h]", text)
        self.assertGreaterEqual(text.count("for timeframe in 5m 15m 1h; do"), 2)
        self.assertEqual(text.count("ARTIFACT_ID:"), 1)
        for symbol in ("EURUSD", "GBPUSD", "USDJPY"):
            self.assertIn(symbol, text)
        for timeframe in ("5m", "15m", "1h"):
            expected = (
                "exp044-market-features-${{ matrix.dataset.symbol }}-"
                + timeframe
                + "-${{ github.sha }}"
            )
            self.assertIn(expected, text)
        self.assertIn(
            "pattern: exp044-market-features-*-*-${{ github.sha }}",
            text,
        )
        self.assertIn('evidence["verified_cell_count"] == 9', text)

    def test_existing_accepted_phase2_identities_are_unchanged(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        expected = (
            ("10325737935", "db0e65490bc1ff80f6d7a0498dd64322563f838a7f70c740617c41bd19e423c3"),
            ("10326096831", "fe42669ed46788d8c7db33b903db79c29034a666acd52213c3c28ec7d4ea88c2"),
            ("10327600628", "6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72"),
        )
        for artifact_id, digest in expected:
            self.assertIn(artifact_id, text)
            self.assertIn(digest, text)
        self.assertIn("scripts/phase8a_market_features.py", text)
        self.assertIn("scripts/phase8a_market_feature_evidence.py", text)

    def test_research_only_locks_are_preserved(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('manifest["model_training_authorized"] is False', text)
        self.assertIn('manifest["promotion_authorized"] is False', text)
        self.assertIn('evidence["model_fit_authorized"] is False', text)
        self.assertIn('evidence["shadow_authorized"] is False', text)
        self.assertIn('evidence["demo_order_authorized"] is False', text)
        self.assertIn('evidence["broker_mutation_authorized"] is False', text)
        self.assertIn('evidence["live_order_authorized"] is False', text)
        self.assertIn('evidence["real_money_authorized"] is False', text)


if __name__ == "__main__":
    unittest.main()
