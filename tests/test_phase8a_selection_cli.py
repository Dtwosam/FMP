from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import unittest

from fmp.portfolio.selection_cli import main


COMMIT = "a" * 40


class Dec042SelectionCliTests(unittest.TestCase):
    def test_preflight_hashes_exact_final_artifact_and_writes_output(self) -> None:
        captured = {}

        def fake_preflight(**kwargs):
            captured.update(kwargs)
            return {
                "protocol": "fmp-phase8a-dec042-selection-preflight-v1",
                "experiment_id": "EXP-20260922-014",
                "promotion_authorized": False,
            }

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            final_path = root / "final.json"
            payload = b'{"protocol":"final"}\n'
            final_path.write_bytes(payload)
            out = root / "out"
            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "preflight",
                        "--exp015-final",
                        str(final_path),
                        "--code-commit",
                        COMMIT,
                        "--out",
                        str(out),
                    ],
                    preflight_command=fake_preflight,
                )
            self.assertEqual(code, 0)
            self.assertEqual(
                captured["exp015_final_sha256"],
                hashlib.sha256(payload).hexdigest(),
            )
            self.assertEqual(captured["runner_code_commit"], COMMIT)
            self.assertTrue((out / "preflight.json").is_file())

    def test_run_hashes_exact_preflight_and_parses_dataset_sources(self) -> None:
        captured = {}

        def fake_run(**kwargs):
            captured.update(kwargs)
            return {
                "protocol": "fmp-phase8a-dec042-selection-v1",
                "experiment_id": "EXP-20260922-014",
                "promotion_authorized": False,
                "shadow_candidate_authorized": False,
            }

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight_path = root / "preflight.json"
            payload = b'{"protocol":"preflight"}\n'
            preflight_path.write_bytes(payload)
            out = root / "out"
            stdout = StringIO()
            with redirect_stdout(stdout):
                code = main(
                    [
                        "run",
                        "--preflight",
                        str(preflight_path),
                        "--dataset-source",
                        "EURUSD=/eur::/eur.json",
                        "--dataset-source",
                        "USDJPY=/jpy::/jpy.json",
                        "--code-commit",
                        COMMIT,
                        "--out",
                        str(out),
                    ],
                    selection_command=fake_run,
                )
            self.assertEqual(code, 0)
            self.assertEqual(
                captured["preflight_sha256"],
                hashlib.sha256(payload).hexdigest(),
            )
            self.assertEqual(
                captured["dataset_sources"]["EURUSD"],
                (Path("/eur"), Path("/eur.json")),
            )
            self.assertEqual(
                captured["dataset_sources"]["USDJPY"],
                (Path("/jpy"), Path("/jpy.json")),
            )
            self.assertTrue((out / "selection.json").is_file())

    def test_cli_has_no_combined_preflight_and_run_command(self) -> None:
        with self.assertRaises(SystemExit):
            main(["search"])


if __name__ == "__main__":
    unittest.main()
