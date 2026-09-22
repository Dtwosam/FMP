from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from fmp.portfolio.historical_inventory import build_phase4_baseline_inventory
from fmp.portfolio.joint_cli import main


COMMIT = "a" * 40


class Phase8AJointCliTests(unittest.TestCase):
    def test_resolve_reports_exact_historical_status_without_promotion(self) -> None:
        record = build_phase4_baseline_inventory()[0]
        out = StringIO()
        with redirect_stdout(out):
            code = main(
                [
                    "resolve",
                    "--strategy-fingerprint",
                    record.strategy.fingerprint,
                ]
            )
        self.assertEqual(code, 0)
        payload = json.loads(out.getvalue())
        self.assertEqual(payload["protocol"], "fmp-phase8a-joint-resolve-v1")
        self.assertFalse(payload["promotion_authorized"])
        self.assertEqual(payload["strategy_count"], 1)
        self.assertEqual(
            payload["strategies"][0]["fingerprint"],
            record.strategy.fingerprint,
        )
        self.assertEqual(
            payload["strategies"][0]["lifecycle"],
            record.lifecycle.value,
        )

    def test_run_wires_explicit_strategy_range_cost_and_dataset_source(self) -> None:
        record = build_phase4_baseline_inventory()[0]
        captured = {}

        def fake_joint(**kwargs):
            captured["plan"] = kwargs["plan"]
            captured["dataset_sources"] = kwargs["dataset_sources"]
            return {
                "protocol": "fmp-phase8a-joint-portfolio-v1",
                "strategy_fingerprints": [
                    item.fingerprint for item in kwargs["plan"].strategies
                ],
                "promotion_authorized": False,
                "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
                "untouched_oos": False,
                "run_identity": {},
            }

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            out_dir = root / "out"
            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "run",
                        "--strategy-fingerprint",
                        record.strategy.fingerprint,
                        "--dataset-source",
                        f"{record.strategy.symbol}={root / 'data'}::{root / 'manifest.json'}",
                        "--start",
                        "2024-01-01",
                        "--end-exclusive",
                        "2024-04-01",
                        "--slippage-pips",
                        "0.5",
                        "--code-commit",
                        COMMIT,
                        "--out",
                        str(out_dir),
                    ],
                    joint_command=fake_joint,
                )

            self.assertEqual(code, 0)
            plan = captured["plan"]
            self.assertEqual(plan.slippage_pips, 0.5)
            self.assertEqual(plan.research_range.start.isoformat(), "2024-01-01")
            self.assertEqual(
                plan.research_range.end_exclusive.isoformat(),
                "2024-04-01",
            )
            self.assertEqual(plan.runner_code_commit, COMMIT)
            self.assertEqual(
                tuple(item.fingerprint for item in plan.strategies),
                (record.strategy.fingerprint,),
            )
            self.assertIn(record.strategy.symbol, captured["dataset_sources"])

            printed = json.loads(stdout.getvalue())
            self.assertEqual(
                printed["result"],
                str(out_dir / "joint-evidence.json"),
            )
            self.assertEqual(
                printed["manifest"],
                str(out_dir / "manifest.json"),
            )
            stored = json.loads(
                (out_dir / "joint-evidence.json").read_text(encoding="utf-8")
            )
            self.assertFalse(stored["promotion_authorized"])
            self.assertFalse(stored["historical_status_mutation_authorized"])

    def test_run_rejects_malformed_or_duplicate_dataset_sources(self) -> None:
        record = build_phase4_baseline_inventory()[0]
        base = [
            "run",
            "--strategy-fingerprint",
            record.strategy.fingerprint,
            "--start",
            "2024-01-01",
            "--end-exclusive",
            "2024-04-01",
            "--slippage-pips",
            "0.2",
            "--code-commit",
            COMMIT,
            "--out",
            "/tmp/out",
        ]
        with self.assertRaises(ValueError):
            main(base + ["--dataset-source", "bad"])
        with self.assertRaises(ValueError):
            main(
                base
                + [
                    "--dataset-source",
                    "EURUSD=/a::/b",
                    "--dataset-source",
                    "EURUSD=/c::/d",
                ]
            )


if __name__ == "__main__":
    unittest.main()
