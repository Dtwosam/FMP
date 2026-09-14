from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCENARIOS = [
    "ambiguity",
    "daily-halt-reset",
    "long-cost",
    "short-target",
    "simultaneous-risk",
]
ARTIFACTS = [
    "summary.json",
    "trades.jsonl",
    "rejections.jsonl",
    "metrics.json",
    "manifest.json",
]


class Phase3AcceptanceRunnerTests(unittest.TestCase):
    def test_runner_emits_fixed_deterministic_acceptance_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "evidence"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/phase3_acceptance_fixture.py",
                    "--out",
                    str(out),
                    "--code-commit",
                    "phase3-acceptance-test-commit",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)

            index = json.loads((out / "acceptance-index.json").read_text(encoding="utf-8"))
            self.assertEqual(index["protocol"], "fmp-phase3-acceptance-fixture-v1")
            self.assertEqual(index["code_commit"], "phase3-acceptance-test-commit")
            self.assertEqual(index["scenario_count"], len(SCENARIOS))
            self.assertEqual([item["name"] for item in index["scenarios"]], SCENARIOS)
            self.assertTrue(all(item["bytes_equal"] for item in index["scenarios"]))

            for scenario in SCENARIOS:
                for artifact in ARTIFACTS:
                    primary = out / "primary" / scenario / artifact
                    repeat = out / "repeat" / scenario / artifact
                    self.assertTrue(primary.is_file(), primary)
                    self.assertTrue(repeat.is_file(), repeat)
                    self.assertEqual(primary.read_bytes(), repeat.read_bytes())

            long_trade = json.loads(
                (out / "primary" / "long-cost" / "trades.jsonl")
                .read_text(encoding="utf-8")
                .strip()
            )
            self.assertAlmostEqual(long_trade["gross_pnl_usd"], 25.0)
            self.assertAlmostEqual(long_trade["slippage_cost_usd"], 5.0)
            self.assertAlmostEqual(long_trade["commission_cost_usd"], 1.5)
            self.assertAlmostEqual(long_trade["net_pnl_usd"], 18.5)

            ambiguity_trade = json.loads(
                (out / "primary" / "ambiguity" / "trades.jsonl")
                .read_text(encoding="utf-8")
                .strip()
            )
            self.assertEqual(ambiguity_trade["exit_reason"], "STOP")
            self.assertTrue(ambiguity_trade["intrabar_ambiguous"])

            simultaneous_rejections = [
                json.loads(line)
                for line in (out / "primary" / "simultaneous-risk" / "rejections.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
                if line
            ]
            self.assertEqual(
                [(item["decision_id"], item["code"]) for item in simultaneous_rejections],
                [("C", "SIMULTANEOUS_RISK")],
            )

            daily_rejections = [
                json.loads(line)
                for line in (out / "primary" / "daily-halt-reset" / "rejections.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
                if line
            ]
            self.assertEqual(
                [(item["decision_id"], item["code"]) for item in daily_rejections],
                [("HALTED", "DAILY_HALT")],
            )
            daily_trades = [
                json.loads(line)
                for line in (out / "primary" / "daily-halt-reset" / "trades.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
                if line
            ]
            self.assertEqual(
                [item["decision_id"] for item in daily_trades],
                ["LOSS-1", "LOSS-2", "LOSS-3", "LOSS-4", "NEXT-DAY"],
            )


if __name__ == "__main__":
    unittest.main()
