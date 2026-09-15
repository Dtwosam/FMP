from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


class Phase6CliTests(unittest.TestCase):
    def test_help_exposes_only_frozen_strategy_and_no_split_date_or_final_surface(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/phase6_ml_filter.py", "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        help_text = completed.stdout
        self.assertIn("session_breakout", help_text)
        self.assertIn("volatility_breakout", help_text)
        self.assertNotIn("--split", help_text)
        self.assertNotIn("--start", help_text)
        self.assertNotIn("--end", help_text)
        self.assertNotIn("final", help_text.lower())
        self.assertNotIn("EURUSD", help_text)
        self.assertNotIn("GBPUSD", help_text)

    def test_cli_delegates_to_fixed_pipeline_and_artifact_writer(self) -> None:
        from fmp.models import cli

        pipeline_result = {
            "experiment_id": "EXP-20260915-007",
            "strategy_id": "session_breakout",
            "code_commit": "abc123",
            "selection": {},
            "validation": {},
        }
        with (
            patch.object(cli, "run_phase6_strategy_cell", return_value=pipeline_result) as run,
            patch.object(cli, "write_phase6_artifacts", return_value={"artifacts": []}) as write,
        ):
            code = cli.main(
                [
                    "--dataset-root", "/processed",
                    "--processed-manifest", "/processed/manifest.json",
                    "--feature-root", "/features",
                    "--feature-manifest", "/features/manifest.json",
                    "--strategy", "session_breakout",
                    "--out", "/out",
                    "--code-commit", "abc123",
                ]
            )
        self.assertEqual(code, 0)
        run.assert_called_once_with(
            dataset_root=Path("/processed"),
            processed_manifest_path=Path("/processed/manifest.json"),
            feature_root=Path("/features"),
            feature_manifest_path=Path("/features/manifest.json"),
            strategy_id="session_breakout",
            out_dir=Path("/out"),
            code_commit="abc123",
        )
        write.assert_called_once_with(pipeline_result, Path("/out"))

    def test_strategy_choices_are_exact(self) -> None:
        from fmp.models.cli import build_parser

        parser = build_parser()
        strategy_action = next(action for action in parser._actions if action.dest == "strategy")
        self.assertEqual(tuple(strategy_action.choices), ("session_breakout", "volatility_breakout"))


if __name__ == "__main__":
    unittest.main()
