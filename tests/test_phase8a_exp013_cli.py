from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fmp.portfolio.challenger_round1_cli import main


COMMIT = "a" * 40


class Phase8AExp013CliTests(unittest.TestCase):
    def test_cell_command_runs_both_splits_and_writes_evidence(self) -> None:
        calls: list[str] = []
        written: dict[str, object] = {}

        def fake_runner(**kwargs):
            calls.append(kwargs["split_name"])
            return {
                "split_name": kwargs["split_name"],
                "symbol": kwargs["symbol"],
                "timeframe": kwargs["timeframe"],
            }

        def fake_gate(**kwargs):
            self.assertEqual(kwargs["development"]["split_name"], "development")
            self.assertEqual(kwargs["validation"]["split_name"], "validation")
            return {"protocol": "gate"}

        def fake_builder(**kwargs):
            self.assertEqual(kwargs["gate"], {"protocol": "gate"})
            return {
                "protocol": "cell-evidence",
                "symbol": kwargs["development"]["symbol"],
                "timeframe": kwargs["development"]["timeframe"],
            }

        def fake_writer(value, out_dir):
            written["value"] = value
            written["out_dir"] = Path(out_dir)
            Path(out_dir).mkdir(parents=True, exist_ok=True)
            (Path(out_dir) / "cell-evidence.json").write_text(
                json.dumps(value),
                encoding="utf-8",
            )
            (Path(out_dir) / "manifest.json").write_text("{}", encoding="utf-8")
            return {"protocol": "manifest"}

        with TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "out"
            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "cell",
                        "--dataset-root",
                        str(Path(tmp) / "data"),
                        "--manifest",
                        str(Path(tmp) / "USDJPY.json"),
                        "--symbol",
                        "USDJPY",
                        "--timeframe",
                        "15m",
                        "--code-commit",
                        COMMIT,
                        "--out",
                        str(out_dir),
                    ],
                    cell_runner=fake_runner,
                    gate_evaluator=fake_gate,
                    cell_evidence_builder=fake_builder,
                    cell_writer=fake_writer,
                )

            self.assertEqual(code, 0)
            self.assertEqual(calls, ["development", "validation"])
            self.assertEqual(written["out_dir"], out_dir)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(
                payload["result"],
                str(out_dir / "cell-evidence.json"),
            )
            self.assertEqual(
                payload["manifest"],
                str(out_dir / "manifest.json"),
            )

    def test_authorize_command_requires_exactly_nine_cell_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "cells"
            out = Path(tmp) / "authorization"
            root.mkdir()
            for index in range(8):
                cell = root / f"cell-{index}"
                cell.mkdir()
                (cell / "cell-evidence.json").write_text(
                    json.dumps({"index": index}),
                    encoding="utf-8",
                )

            with self.assertRaisesRegex(ValueError, "exactly nine"):
                main(
                    [
                        "authorize",
                        "--cells-root",
                        str(root),
                        "--out",
                        str(out),
                    ],
                    authorization_builder=lambda cells: {"cells": len(cells)},
                    authorization_writer=lambda value, path: {},
                )

    def test_authorize_command_loads_nine_cells_and_writes_authorization(self) -> None:
        captured: dict[str, object] = {}

        def fake_builder(cells):
            captured["cells"] = cells
            return {
                "protocol": "authorization",
                "cell_count": len(cells),
            }

        def fake_writer(value, out_dir):
            captured["authorization"] = value
            root = Path(out_dir)
            root.mkdir(parents=True, exist_ok=True)
            (root / "stage-a-authorization.json").write_text(
                json.dumps(value),
                encoding="utf-8",
            )
            (root / "manifest.json").write_text("{}", encoding="utf-8")
            return {"protocol": "manifest"}

        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "cells"
            out_dir = Path(tmp) / "authorization"
            root.mkdir()
            for index in range(9):
                cell = root / f"cell-{index}"
                cell.mkdir()
                (cell / "cell-evidence.json").write_text(
                    json.dumps({"index": index}),
                    encoding="utf-8",
                )

            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "authorize",
                        "--cells-root",
                        str(root),
                        "--out",
                        str(out_dir),
                    ],
                    authorization_builder=fake_builder,
                    authorization_writer=fake_writer,
                )

            self.assertEqual(code, 0)
            self.assertEqual(len(captured["cells"]), 9)
            self.assertEqual(
                captured["authorization"],
                {"protocol": "authorization", "cell_count": 9},
            )
            payload = json.loads(stdout.getvalue())
            self.assertEqual(
                payload["result"],
                str(out_dir / "stage-a-authorization.json"),
            )


if __name__ == "__main__":
    unittest.main()
