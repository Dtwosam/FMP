from __future__ import annotations

import re
import unittest
from pathlib import Path


WORKFLOW = Path(".github/workflows/phase6-ml-filter.yml")


class Phase6WorkflowTests(unittest.TestCase):
    def test_workflow_is_manual_read_only_and_exact_two_cell_matrix(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        lower = text.lower()
        self.assertIn("name: phase6-ml-filter", text)
        self.assertRegex(text, r"on:\s*\n\s*workflow_dispatch:\s*\n")
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("push:", text)
        self.assertNotIn("schedule:", text)
        self.assertNotIn("inputs:", text)
        self.assertIn("contents: read", text)
        self.assertIn("actions: read", text)
        self.assertNotIn("id-token", lower)
        self.assertEqual(len(re.findall(r"^\s*- strategy:\s*", text, re.MULTILINE)), 2)
        self.assertIn("strategy: session_breakout", text)
        self.assertRegex(text, r"strategy:\s*session_breakout[\s\S]{0,180}timeframe:\s*15m")
        self.assertIn("strategy: volatility_breakout", text)
        self.assertRegex(text, r"strategy:\s*volatility_breakout[\s\S]{0,180}timeframe:\s*1h")
        self.assertNotIn("EURUSD", text)
        self.assertNotIn("GBPUSD", text)
        self.assertNotRegex(text, r"timeframe:\s*1m\b")
        self.assertNotIn("--split", text)
        self.assertNotIn("--start", text)
        self.assertNotIn("--end", text)

    def test_workflow_pins_accepted_phase2_and_phase5_artifacts(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        for value in (
            "10327600628",
            "6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72",
            "e47ee5339868a741097404bed49411cca36b03609ebe395261bb70b6e63bdd3d",
            "10374600839",
            "2e9b19935fc2699c94e5c3b91675c332892da9448e994438e479cf501e3c6215",
            "10374645600",
            "3db4d9d4fd4613c9e91f4c3fc1d815750038e33ea993608513066cec53aa617f",
        ):
            self.assertIn(value, text)
        self.assertGreaterEqual(text.count("sha256sum"), 3)
        self.assertIn("actions/artifacts/${ARTIFACT_ID}/zip", text)
        self.assertIn("actions/artifacts/${PHASE5_ARTIFACT_ID}/zip", text)

    def test_workflow_double_executes_compares_and_uploads_only_pre2024_evidence(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        lower = text.lower()
        self.assertGreaterEqual(text.count("scripts/phase6_ml_filter.py"), 2)
        self.assertIn(".phase6-a", text)
        self.assertIn(".phase6-b", text)
        self.assertIn("GITHUB_SHA", text)
        self.assertIn("cmp", text)
        for name in ("selection.json", "result.json", "manifest.json"):
            self.assertIn(name, text)
        self.assertIn("2024", text)
        self.assertIn("actions/upload-artifact@v6", text)
        for token in (
            "dukascopy",
            "supabase",
            "broker",
            "oanda",
            "real-money",
            "demo trading",
            "fmp-raw",
        ):
            self.assertNotIn(token, lower)


if __name__ == "__main__":
    unittest.main()
