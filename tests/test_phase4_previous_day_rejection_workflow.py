from __future__ import annotations

import re
import unittest
from pathlib import Path


WORKFLOW = Path(".github/workflows/phase4-previous-day-rejection.yml")


class Phase4PreviousDayRejectionWorkflowTests(unittest.TestCase):
    def test_workflow_is_source_free_fixed_matrix_and_fail_closed(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        lowered = text.lower()
        self.assertIn("name: phase4-previous-day-rejection", text)
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("push:", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("schedule:", text)
        self.assertIn("timeout-minutes: 90", text)
        self.assertIn("fail-fast: false", text)

        permissions = re.search(
            r"permissions:\s*\n\s*contents:\s*read\s*\n\s*actions:\s*read\s*\n",
            text,
        )
        self.assertIsNotNone(permissions)
        self.assertNotIn("id-token", lowered)

        for value in ("EURUSD", "GBPUSD", "USDJPY", "5m", "15m", "1h", "development", "validation"):
            self.assertIn(value, text)
        self.assertNotRegex(lowered, r"\bfinal\b")

        expected = {
            "EURUSD": ("10325737935", "db0e65490bc1ff80f6d7a0498dd64322563f838a7f70c740617c41bd19e423c3"),
            "GBPUSD": ("10326096831", "fe42669ed46788d8c7db33b903db79c29034a666acd52213c3c28ec7d4ea88c2"),
            "USDJPY": ("10327600628", "6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72"),
        }
        for artifact_id, digest in expected.values():
            self.assertIn(artifact_id, text)
            self.assertIn(digest, text)

        self.assertIn("GH_TOKEN: ${{ github.token }}", text)
        self.assertIn("actions/artifacts/", text)
        self.assertRegex(lowered, r"sha256(sum)?")
        self.assertLess(lowered.index("sha256"), lowered.index("unzip"))
        self.assertIn("python scripts/phase4_previous_day_rejection.py", text)
        self.assertIn('--code-commit "${GITHUB_SHA}"', text)
        self.assertIn("fmp-phase4-previous-day-rejection-grid-v1", text)
        self.assertIn("len(benchmark['configuration_rows']) == 9", text)
        self.assertIn("actions/upload-artifact@v6", text)
        self.assertIn("include-hidden-files: true", text)
        self.assertIn("if-no-files-found: error", text)

        for forbidden in (
            "dukascopy", "datafeed.dukascopy.com", "supabase", "fmp.data.cli fetch",
            "fetch-plan", "acquire_chunk", "phase1-full-acquisition", "fmp-raw",
        ):
            self.assertNotIn(forbidden, lowered)

    def test_push_paths_are_scoped_to_previous_day_rejection_surface(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("paths:", text)
        for path in (
            "src/fmp/research/previous_day_rejection.py",
            "src/fmp/strategies/previous_day_rejection.py",
            "scripts/phase4_previous_day_rejection.py",
            ".github/workflows/phase4-previous-day-rejection.yml",
        ):
            self.assertIn(path, text)


if __name__ == "__main__":
    unittest.main()
