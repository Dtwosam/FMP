from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from fmp.portfolio.exp013_cli import main


COMMIT = "a" * 40
SOURCE_SHA = "f" * 64


def _cell_payload(symbol: str, timeframe: str, split_name: str) -> dict[str, object]:
    return {
        "protocol": "fmp-phase8a-exp013-stage-a-cell-v1",
        "experiment_id": "EXP-20260922-013",
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "symbol": symbol,
        "timeframe": timeframe,
        "split_name": split_name,
        "range_start": "2015-01-01" if split_name == "development" else "2021-01-01",
        "range_end_exclusive": "2021-01-01" if split_name == "development" else "2024-01-01",
        "runner_code_commit": COMMIT,
        "strategy_source_sha256": SOURCE_SHA,
        "processed_manifest_sha256": "e" * 64,
        "opened_artifact_months": [],
        "strategy_identity_count": 4,
        "scenario_run_count": 12,
        "slippage_scenarios": [0.2, 0.5, 1.0],
        "rows": [],
    }


def _gate(symbol: str, timeframe: str) -> dict[str, object]:
    cell_index = (
        ("EURUSD", "GBPUSD", "USDJPY").index(symbol) * 3
        + ("5m", "15m", "1h").index(timeframe)
    )
    fps = [f"{cell_index * 10 + index:064x}" for index in range(1, 5)]
    return {
        "protocol": "fmp-phase8a-exp013-stage-a-gate-v1",
        "experiment_id": "EXP-20260922-013",
        "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
        "untouched_oos": False,
        "promotion_authorized": False,
        "historical_status_mutation_authorized": False,
        "symbol": symbol,
        "timeframe": timeframe,
        "runner_code_commit": COMMIT,
        "strategy_source_sha256": SOURCE_SHA,
        "survivor_fingerprints": [],
        "config_gates": {
            fingerprint: {
                "parameters": {
                    "body_fraction_threshold": 0.5,
                    "target_r_multiple": 1.0,
                },
                "mandatory_profitability_drawdown_pass": False,
                "sample_pass": False,
                "neighbor_pass": False,
                "passing_neighbor_fingerprints": [],
                "stage_a_survivor": False,
            }
            for fingerprint in fps
        },
    }


class Exp013CliTests(unittest.TestCase):
    def test_stage_a_cell_runs_both_frozen_splits_and_writes_gate(self) -> None:
        calls = []

        def fake_run(**kwargs):
            calls.append((kwargs["split_name"], kwargs["symbol"], kwargs["timeframe"]))
            return _cell_payload(
                kwargs["symbol"],
                kwargs["timeframe"],
                kwargs["split_name"],
            )

        def fake_eval(**kwargs):
            self.assertEqual(kwargs["development"]["split_name"], "development")
            self.assertEqual(kwargs["validation"]["split_name"], "validation")
            return _gate("EURUSD", "15m")

        with TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "stage-a-cell",
                        "--dataset-root",
                        str(Path(tmp) / "data"),
                        "--manifest",
                        str(Path(tmp) / "manifest.json"),
                        "--symbol",
                        "EURUSD",
                        "--timeframe",
                        "15m",
                        "--code-commit",
                        COMMIT,
                        "--out",
                        str(out_dir),
                    ],
                    stage_a_cell_command=fake_run,
                    stage_a_gate_command=fake_eval,
                )

            self.assertEqual(code, 0)
            self.assertEqual(
                calls,
                [
                    ("development", "EURUSD", "15m"),
                    ("validation", "EURUSD", "15m"),
                ],
            )
            self.assertTrue((out_dir / "development.json").is_file())
            self.assertTrue((out_dir / "validation.json").is_file())
            self.assertTrue((out_dir / "gate.json").is_file())
            printed = json.loads(stdout.getvalue())
            self.assertEqual(printed["gate"], str(out_dir / "gate.json"))

    def test_stage_a_authorize_requires_gate_files_and_never_opens_source(self) -> None:
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
                    ]
                )

            self.assertEqual(code, 0)
            authorization = json.loads(
                (out_dir / "authorization.json").read_text(encoding="utf-8")
            )
            self.assertEqual(authorization["cell_count"], 9)
            self.assertFalse(authorization["stage_b_source_open_authorized"])
            self.assertFalse(authorization["promotion_authorized"])
            printed = json.loads(stdout.getvalue())
            self.assertEqual(
                printed["authorization"],
                str(out_dir / "authorization.json"),
            )

    def test_stage_b_run_wires_exact_authorization_and_dataset_sources(self) -> None:
        captured = {}

        def fake_stage_b(**kwargs):
            captured.update(kwargs)
            return {
                "protocol": "fmp-phase8a-exp013-stage-b-v1",
                "experiment_id": "EXP-20260922-013",
                "evidence_label": "RETROSPECTIVE_ALREADY_SEEN",
                "untouched_oos": False,
                "promotion_authorized": False,
                "historical_status_mutation_authorized": False,
                "historical_qualification_review_authorized": False,
                "historical_qualification_candidate_fingerprints": [],
            }

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            authorization_path = root / "authorization.json"
            authorization_path.write_text(
                json.dumps({"protocol": "fixture"}),
                encoding="utf-8",
            )
            out_dir = root / "stage-b"
            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "stage-b-run",
                        "--authorization",
                        str(authorization_path),
                        "--dataset-source",
                        f"EURUSD={root / 'eur'}::{root / 'eur.json'}",
                        "--code-commit",
                        COMMIT,
                        "--out",
                        str(out_dir),
                    ],
                    stage_b_command=fake_stage_b,
                )

            self.assertEqual(code, 0)
            self.assertEqual(captured["code_commit"], COMMIT)
            self.assertEqual(
                captured["dataset_sources"]["EURUSD"],
                (root / "eur", root / "eur.json"),
            )
            self.assertEqual(
                len(captured["stage_a_authorization_sha256"]),
                64,
            )
            self.assertTrue((out_dir / "stage-b.json").is_file())
            printed = json.loads(stdout.getvalue())
            self.assertEqual(printed["result"], str(out_dir / "stage-b.json"))

    def test_stage_b_run_rejects_malformed_dataset_source(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            authorization_path = root / "authorization.json"
            authorization_path.write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                main(
                    [
                        "stage-b-run",
                        "--authorization",
                        str(authorization_path),
                        "--dataset-source",
                        "bad",
                        "--code-commit",
                        COMMIT,
                        "--out",
                        str(root / "out"),
                    ]
                )


if __name__ == "__main__":
    unittest.main()
