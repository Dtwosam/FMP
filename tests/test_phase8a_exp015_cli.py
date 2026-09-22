from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
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

    def test_stage_b_stage_c_and_finalize_bind_upstream_file_hashes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            authorization_path = root / "authorization.json"
            stage_b_path = root / "stage-b.json"
            stage_c_path = root / "stage-c.json"
            authorization_payload = b'{"protocol":"authorization"}\n'
            stage_b_payload = b'{"protocol":"stage-b"}\n'
            stage_c_payload = b'{"protocol":"stage-c"}\n'
            authorization_path.write_bytes(authorization_payload)
            stage_b_path.write_bytes(stage_b_payload)
            stage_c_path.write_bytes(stage_c_payload)

            captured = {}

            def fake_stage_b(**kwargs):
                captured["stage_b"] = kwargs
                return {
                    "protocol": "fmp-phase8a-exp015-stage-b-v1",
                    "promotion_authorized": False,
                }

            def fake_stage_c(**kwargs):
                captured["stage_c"] = kwargs
                return {
                    "protocol": "fmp-phase8a-exp015-stage-c-v1",
                    "promotion_authorized": False,
                }

            def fake_finalize(**kwargs):
                captured["finalize"] = kwargs
                return {
                    "protocol": "fmp-phase8a-exp015-final-shortlist-v1",
                    "promotion_authorized": False,
                }

            stage_b_out = root / "stage-b-out"
            self.assertEqual(
                main(
                    [
                        "stage-b-run",
                        "--authorization",
                        str(authorization_path),
                        "--dataset-source",
                        "EURUSD=/data::/manifest.json",
                        "--code-commit",
                        COMMIT,
                        "--out",
                        str(stage_b_out),
                    ],
                    stage_b_command=fake_stage_b,
                ),
                0,
            )
            self.assertEqual(
                captured["stage_b"]["stage_a_authorization_sha256"],
                hashlib.sha256(authorization_payload).hexdigest(),
            )
            self.assertEqual(
                captured["stage_b"]["dataset_sources"]["EURUSD"],
                (Path("/data"), Path("/manifest.json")),
            )

            stage_c_out = root / "stage-c-out"
            self.assertEqual(
                main(
                    [
                        "stage-c-run",
                        "--authorization",
                        str(authorization_path),
                        "--stage-b",
                        str(stage_b_path),
                        "--dataset-source",
                        "EURUSD=/data::/manifest.json",
                        "--code-commit",
                        COMMIT,
                        "--out",
                        str(stage_c_out),
                    ],
                    stage_c_command=fake_stage_c,
                ),
                0,
            )
            self.assertEqual(
                captured["stage_c"]["stage_a_authorization_sha256"],
                hashlib.sha256(authorization_payload).hexdigest(),
            )
            self.assertEqual(
                captured["stage_c"]["stage_b_result_sha256"],
                hashlib.sha256(stage_b_payload).hexdigest(),
            )

            final_out = root / "final-out"
            self.assertEqual(
                main(
                    [
                        "finalize",
                        "--authorization",
                        str(authorization_path),
                        "--stage-b",
                        str(stage_b_path),
                        "--stage-c",
                        str(stage_c_path),
                        "--out",
                        str(final_out),
                    ],
                    finalize_command=fake_finalize,
                ),
                0,
            )
            self.assertEqual(
                captured["finalize"]["stage_a_authorization_sha256"],
                hashlib.sha256(authorization_payload).hexdigest(),
            )
            self.assertEqual(
                captured["finalize"]["stage_b_result_sha256"],
                hashlib.sha256(stage_b_payload).hexdigest(),
            )
            self.assertEqual(
                captured["finalize"]["stage_c_result_sha256"],
                hashlib.sha256(stage_c_payload).hexdigest(),
            )


if __name__ == "__main__":
    unittest.main()
