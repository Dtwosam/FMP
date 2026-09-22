from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from fmp.portfolio.exp015_cli import main


COMMIT = "a" * 40


def _cell(symbol: str, timeframe: str) -> dict[str, object]:
    return {
        "protocol": "fmp-phase8a-exp015-stage-a-cell-v1",
        "experiment_id": "EXP-20260922-015",
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "symbol": symbol,
        "timeframe": timeframe,
        "runner_code_commit": COMMIT,
        "strategy_source_sha256": "d" * 64,
        "range_start": "2015-01-01",
        "range_end_exclusive": "2019-01-01",
        "strategy_identity_count": 63,
        "scenario_run_count": 189,
        "slippage_scenarios": [0.2, 0.5, 1.0],
        "strategy_fingerprints": [],
        "rows": [],
    }


def _gate(symbol: str, timeframe: str) -> dict[str, object]:
    return {
        "protocol": "fmp-phase8a-exp015-stage-a-gate-v1",
        "experiment_id": "EXP-20260922-015",
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "symbol": symbol,
        "timeframe": timeframe,
        "runner_code_commit": COMMIT,
        "strategy_source_sha256": "d" * 64,
        "strategy_fingerprints": [],
        "survivor_fingerprints": [],
        "family_rankings": {},
        "strategy_gates": {},
    }


class Exp015CliTests(unittest.TestCase):

    def test_catalog_freezes_exact_567_identities_before_stage_a(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            out_dir = root / "catalog"
            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "catalog",
                        "--code-commit",
                        COMMIT,
                        "--out",
                        str(out_dir),
                    ]
                )
            self.assertEqual(code, 0)
            stored = json.loads(
                (out_dir / "catalog.json").read_text(encoding="utf-8")
            )
            self.assertEqual(stored["protocol"], "fmp-phase8a-exp015-catalog-v1")
            self.assertEqual(stored["strategy_identity_count"], 567)
            self.assertEqual(len(stored["strategies"]), 567)
            self.assertEqual(len(stored["catalog_identity_sha256"]), 64)
            self.assertFalse(stored["promotion_authorized"])
            printed = json.loads(stdout.getvalue())
            self.assertEqual(printed["catalog"], str(out_dir / "catalog.json"))

    def test_stage_a_cell_wires_fixed_cell_and_writes_artifacts(self) -> None:
        captured = {}

        def fake_run(**kwargs):
            captured.update(kwargs)
            return _cell(kwargs["symbol"], kwargs["timeframe"])

        def fake_eval(cell):
            self.assertEqual(cell["symbol"], "GBPUSD")
            self.assertEqual(cell["timeframe"], "1h")
            return _gate("GBPUSD", "1h")

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            out_dir = root / "out"
            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "stage-a-cell",
                        "--dataset-root",
                        str(root / "data"),
                        "--manifest",
                        str(root / "manifest.json"),
                        "--symbol",
                        "GBPUSD",
                        "--timeframe",
                        "1h",
                        "--code-commit",
                        COMMIT,
                        "--out",
                        str(out_dir),
                    ],
                    stage_a_cell_command=fake_run,
                    stage_a_gate_command=fake_eval,
                )
            self.assertEqual(code, 0)
            self.assertEqual(captured["symbol"], "GBPUSD")
            self.assertEqual(captured["timeframe"], "1h")
            self.assertEqual(captured["code_commit"], COMMIT)
            self.assertTrue((out_dir / "cell.json").is_file())
            self.assertTrue((out_dir / "gate.json").is_file())
            printed = json.loads(stdout.getvalue())
            self.assertEqual(printed["gate"], str(out_dir / "gate.json"))

    def test_stage_a_authorize_aggregates_exactly_nine_gate_files(self) -> None:
        captured = {}

        def fake_aggregate(gates):
            captured["count"] = len(gates)
            return {
                "protocol": "fmp-phase8a-exp015-stage-a-authorization-v1",
                "experiment_id": "EXP-20260922-015",
                "promotion_authorized": False,
                "historical_status_mutation_authorized": False,
                "stage_b_source_open_authorized": False,
                "survivor_fingerprints": [],
            }

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for symbol in ("EURUSD", "GBPUSD", "USDJPY"):
                for timeframe in ("5m", "15m", "1h"):
                    cell = root / f"{symbol}-{timeframe}"
                    cell.mkdir(parents=True)
                    (cell / "gate.json").write_text(
                        json.dumps(_gate(symbol, timeframe)),
                        encoding="utf-8",
                    )
            out_dir = root / "authorization"
            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "stage-a-authorize",
                        "--inputs-root",
                        str(root),
                        "--out",
                        str(out_dir),
                    ],
                    stage_a_aggregate_command=fake_aggregate,
                )
            self.assertEqual(code, 0)
            self.assertEqual(captured["count"], 9)
            self.assertTrue((out_dir / "authorization.json").is_file())

    def test_cli_exposes_no_stage_b_command(self) -> None:
        with self.assertRaises(SystemExit):
            main(["stage-b-run"])


if __name__ == "__main__":
    unittest.main()
