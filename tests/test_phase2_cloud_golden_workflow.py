from __future__ import annotations

import unittest
from pathlib import Path


class Phase2CloudGoldenWorkflowTests(unittest.TestCase):
    def test_workflow_is_manual_source_free_and_oidc_minimal(self) -> None:
        path = Path(".github/workflows/phase2-cloud-golden.yml")
        text = path.read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("push:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("contents: read", text)
        self.assertIn("id-token: write", text)
        self.assertIn(
            "https://htjqqzlezyguveuajuat.supabase.co/functions/v1/fmp-raw-read",
            text,
        )
        self.assertIn("python -m fmp.data.phase2.cloud_golden", text)
        self.assertIn("actions/checkout@v6", text)
        self.assertIn("actions/setup-python@v6", text)
        self.assertIn("actions/upload-artifact@v6", text)
        self.assertIn("include-hidden-files: true", text)
        lowered = text.lower()
        for forbidden in (
            "fmp.data.cli fetch",
            "fetch-plan",
            "phase1-full-acquisition",
            "phase1-golden-sample",
            "acquire_chunk",
            "repair",
            "datafeed.dukascopy.com",
        ):
            self.assertNotIn(forbidden, lowered)

    def test_cloud_golden_module_has_fixed_bounded_pair_scope(self) -> None:
        text = Path("src/fmp/data/phase2/cloud_golden.py").read_text(encoding="utf-8")
        self.assertIn('GOLDEN_PAIRS = ("EURUSD", "USDJPY")', text)
        self.assertIn("GOLDEN_DAY = date(2024, 1, 2)", text)
        self.assertNotIn("_iter_days", text)
        self.assertNotIn("DukascopySource", text)
        self.assertNotIn("acquire_chunk", text)


if __name__ == "__main__":
    unittest.main()
