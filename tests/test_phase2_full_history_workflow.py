from __future__ import annotations

import re
import unittest
from pathlib import Path


class FullHistoryWorkflowTests(unittest.TestCase):
    def test_workflow_is_manual_fixed_and_source_free(self) -> None:
        text = Path(".github/workflows/phase2-full-history.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("push:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("contents: read", text)
        self.assertIn("id-token: write", text)
        for pair in ("EURUSD", "GBPUSD", "USDJPY"):
            self.assertIn(pair, text)
        self.assertIn("python -m fmp.data.phase2.full_history_cli", text)
        self.assertIn("--workers 4", text)
        self.assertIn("https://htjqqzlezyguveuajuat.supabase.co/functions/v1/fmp-raw-read", text)
        for action in ("actions/checkout@v6", "actions/setup-python@v6", "actions/upload-artifact@v6"):
            self.assertIn(action, text)
        self.assertIn("include-hidden-files: true", text)
        self.assertIn("if-no-files-found: error", text)
        lowered = text.lower()
        for forbidden in (
            "datafeed.dukascopy.com", "fmp.data.cli fetch", "fetch-plan",
            "acquire_chunk", "repair", "phase1-full-acquisition",
        ):
            self.assertNotIn(forbidden, lowered)
        self.assertIsNone(re.search(r"(^|\s)--start(?:\s|=)", lowered))
        self.assertIsNone(re.search(r"(^|\s)--end(?:\s|=)", lowered))


if __name__ == "__main__":
    unittest.main()
