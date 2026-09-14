from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = Path("scripts/phase4_trend_continuation.py")


class Phase4TrendContinuationCliTests(unittest.TestCase):
    def test_help_exposes_only_development_validation_research_surface(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        help_text = completed.stdout
        for flag in (
            "--dataset-root", "--manifest", "--symbol", "--timeframe",
            "--split", "--out", "--code-commit",
        ):
            self.assertIn(flag, help_text)
        self.assertIn("{EURUSD,GBPUSD,USDJPY}", help_text)
        self.assertIn("{5m,15m,1h}", help_text)
        self.assertIn("{development,validation}", help_text)
        self.assertNotIn("final", help_text.lower())

    def test_final_split_is_rejected_by_parser_before_data_access(self) -> None:
        completed = subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--dataset-root", "/definitely/not/read",
                "--manifest", "/definitely/not/read/manifest.json",
                "--symbol", "EURUSD",
                "--timeframe", "1h",
                "--split", "final",
                "--out", "/tmp/phase4-trend-final-must-not-run",
                "--code-commit", "test-commit",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("invalid choice", completed.stderr)
        self.assertIn("final", completed.stderr)
        self.assertNotIn("No such file or directory", completed.stderr)

    def test_script_delegates_to_frozen_runner_and_writer_and_is_source_free(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("run_trend_continuation_grid", text)
        self.assertIn("write_benchmark_artifacts", text)
        lowered = text.lower()
        for forbidden in (
            "dukascopy", "datafeed.dukascopy.com", "supabase", "fmp.data.cli",
            "fetch-plan", "fmp-raw", "github_oidc",
        ):
            self.assertNotIn(forbidden, lowered)


if __name__ == "__main__":
    unittest.main()
