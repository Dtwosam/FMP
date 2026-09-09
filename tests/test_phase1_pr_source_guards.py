from __future__ import annotations

import unittest
from pathlib import Path


class Phase1PullRequestSourceGuardTests(unittest.TestCase):
    def test_golden_sample_skips_no_source_pull_requests(self) -> None:
        workflow = Path(".github/workflows/phase1-golden-sample.yml").read_text(encoding="utf-8")

        self.assertIn("[phase1-no-source]", workflow)
        self.assertIn("github.event.pull_request.title", workflow)

    def test_network_smoke_skips_no_source_pull_requests(self) -> None:
        workflow = Path(".github/workflows/phase1-network-smoke.yml").read_text(encoding="utf-8")

        self.assertIn("[phase1-no-source]", workflow)
        self.assertIn("github.event.pull_request.title", workflow)


if __name__ == "__main__":
    unittest.main()
