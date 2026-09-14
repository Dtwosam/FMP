from __future__ import annotations

import re
import unittest
from pathlib import Path


WORKFLOW = Path(".github/workflows/phase4-session-breakout.yml")


class Phase4SessionBreakoutWorkflowTests(unittest.TestCase):
    def test_workflow_is_source_free_fixed_matrix_and_fail_closed(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        lowered = text.lower()

        self.assertIn("name: phase4-session-breakout", text)
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("push:", text)
        self.assertIn("branches:", text)
        self.assertIn("- main", text)
        self.assertNotIn("pull_request:", text)
        self.assertNotIn("schedule:", text)

        permissions_match = re.search(
            r"permissions:\s*\n\s*contents:\s*read\s*\n\s*actions:\s*read\s*\n",
            text,
        )
        self.assertIsNotNone(permissions_match)
        self.assertNotIn("id-token", lowered)

        for symbol in ("EURUSD", "GBPUSD", "USDJPY"):
            self.assertIn(symbol, text)
        for timeframe in ("5m", "15m", "1h"):
            self.assertIn(timeframe, text)
        for split in ("development", "validation"):
            self.assertIn(split, text)
        self.assertNotRegex(lowered, r"\bfinal\b")

        expected_artifacts = {
            "EURUSD": (
                "10325737935",
                "db0e65490bc1ff80f6d7a0498dd64322563f838a7f70c740617c41bd19e423c3",
            ),
            "GBPUSD": (
                "10326096831",
                "fe42669ed46788d8c7db33b903db79c29034a666acd52213c3c28ec7d4ea88c2",
            ),
            "USDJPY": (
                "10327600628",
                "6ee632b38d45a26dcc58be6d6c9555606605e356aee25b135c089b4969426b72",
            ),
        }
        for artifact_id, digest in expected_artifacts.values():
            self.assertIn(artifact_id, text)
            self.assertIn(digest, text)

        self.assertIn("GH_TOKEN: ${{ github.token }}", text)
        self.assertIn("actions/artifacts/", text)
        self.assertRegex(lowered, r"sha256(sum)?")
        sha_position = lowered.index("sha256")
        unzip_position = lowered.index("unzip")
        self.assertLess(sha_position, unzip_position)

        self.assertIn("python scripts/phase4_session_breakout.py", text)
        self.assertIn('--code-commit "${GITHUB_SHA}"', text)
        self.assertIn("actions/checkout@v6", text)
        self.assertIn("actions/setup-python@v6", text)
        self.assertIn("actions/upload-artifact@v6", text)
        self.assertIn("include-hidden-files: true", text)
        self.assertIn("if-no-files-found: error", text)

        for forbidden in (
            "dukascopy",
            "datafeed.dukascopy.com",
            "supabase",
            "fmp.data.cli fetch",
            "fetch-plan",
            "acquire_chunk",
            "phase1-full-acquisition",
            "fmp-raw",
        ):
            self.assertNotIn(forbidden, lowered)

    def test_push_paths_are_scoped_to_phase4_research_implementation(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("paths:", text)
        for path in (
            "src/fmp/research/**",
            "src/fmp/strategies/**",
            "scripts/phase4_session_breakout.py",
            ".github/workflows/phase4-session-breakout.yml",
        ):
            self.assertIn(path, text)


if __name__ == "__main__":
    unittest.main()
