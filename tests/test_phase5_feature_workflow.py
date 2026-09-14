from __future__ import annotations

import re
import unittest
from pathlib import Path


class Phase5FeatureWorkflowTests(unittest.TestCase):
    def test_workflow_is_exact_source_free_nine_cell_matrix(self) -> None:
        text = Path(".github/workflows/phase5-features.yml").read_text(encoding="utf-8")
        self.assertIn("name: phase5-features", text)
        for symbol, artifact, digest in (
            ("EURUSD", "10325737935", "db0e65490bc1ff80f6d7a0498dd64322563f838a7f70c740617c41bd19e423c3"),
            ("GBPUSD", "10326096831", "fe42669ed46788d8c7db33b903db79c29034a666acd52213c3c28ec7d4ea88c2"),
            ("USDJPY", "10327600628", "6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72"),
        ):
            self.assertIn(symbol, text)
            self.assertIn(artifact, text)
            self.assertIn(digest, text)
        self.assertRegex(text, r"timeframe:\s*\[5m, 15m, 1h\]")
        self.assertIn("2015-01-01", text)
        self.assertIn("2024-01-01", text)
        self.assertNotIn("2026-08-20", text)
        self.assertNotIn("final", text.lower())

    def test_workflow_is_read_only_and_does_not_call_raw_or_live_paths(self) -> None:
        text = Path(".github/workflows/phase5-features.yml").read_text(encoding="utf-8")
        self.assertIn("contents: read", text)
        self.assertIn("actions: read", text)
        forbidden = ("dukascopy", "supabase", "broker", "oanda", "real-money", "fmp-raw")
        lower = text.lower()
        for token in forbidden:
            self.assertNotIn(token, lower)
        self.assertIn("scripts/phase5_features.py", text)
        self.assertIn("actions/upload-artifact@v6", text)
        self.assertGreaterEqual(text.count("phase5_features.py"), 2)
        self.assertIn("determin", lower)


if __name__ == "__main__":
    unittest.main()
