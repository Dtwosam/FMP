from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from fmp.portfolio.research_cli import main


class Phase8AResearchCliTests(unittest.TestCase):
    def test_inventory_reports_exact_cell_without_promotion(self) -> None:
        out = StringIO()
        with redirect_stdout(out):
            code = main(["inventory", "--symbol", "EURUSD", "--timeframe", "15m"])
        self.assertEqual(code, 0)
        payload = json.loads(out.getvalue())
        self.assertEqual(payload["protocol"], "fmp-phase8a-inventory-v1")
        self.assertEqual(payload["symbol"], "EURUSD")
        self.assertEqual(payload["timeframe"], "15m")
        self.assertEqual(payload["strategy_identity_count"], 30)
        self.assertFalse(payload["promotion_authorized"])
        self.assertTrue(
            all(row["historical_lifecycle"] == "RETIRED" for row in payload["strategies"])
        )

    def test_inventory_family_filter_is_explicit(self) -> None:
        out = StringIO()
        with redirect_stdout(out):
            code = main(
                [
                    "inventory",
                    "--symbol",
                    "USDJPY",
                    "--timeframe",
                    "15m",
                    "--family",
                    "session_breakout",
                ]
            )
        self.assertEqual(code, 0)
        payload = json.loads(out.getvalue())
        self.assertEqual(payload["strategy_identity_count"], 9)
        self.assertEqual(payload["families"], ["session_breakout"])

    def test_batch_wires_frozen_range_and_writes_artifact_manifest(self) -> None:
        captured = {}

        def fake_batch(**kwargs):
            captured["plan"] = kwargs["plan"]
            return {
                "protocol": "fmp-phase8a-retrospective-batch-v1",
                "promotion_authorized": False,
                "results": [],
            }

        with TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            out = StringIO()
            with redirect_stdout(out):
                code = main(
                    [
                        "batch",
                        "--dataset-root",
                        str(Path(tmp) / "data"),
                        "--manifest",
                        str(Path(tmp) / "manifest.json"),
                        "--symbol",
                        "GBPUSD",
                        "--timeframe",
                        "1h",
                        "--start",
                        "2024-01-01",
                        "--end-exclusive",
                        "2026-08-21",
                        "--out",
                        str(out_dir),
                        "--code-commit",
                        "a" * 40,
                    ],
                    batch_command=fake_batch,
                )
            self.assertEqual(code, 0)
            plan = captured["plan"]
            self.assertEqual(plan.symbol, "GBPUSD")
            self.assertEqual(plan.timeframe, "1h")
            self.assertEqual(plan.research_range.start.isoformat(), "2024-01-01")
            self.assertEqual(plan.research_range.end_exclusive.isoformat(), "2026-08-21")
            self.assertEqual(plan.runner_code_commit, "a" * 40)

            printed = json.loads(out.getvalue())
            self.assertEqual(printed["result"], str(out_dir / "batch.json"))
            self.assertEqual(printed["manifest"], str(out_dir / "manifest.json"))
            stored = json.loads((out_dir / "batch.json").read_text(encoding="utf-8"))
            self.assertFalse(stored["promotion_authorized"])


if __name__ == "__main__":
    unittest.main()
