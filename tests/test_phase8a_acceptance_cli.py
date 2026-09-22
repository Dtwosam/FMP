from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import unittest
from unittest.mock import patch

from fmp.portfolio.acceptance_cli import main


COMMIT = "a" * 40


class Phase8AAcceptanceCliTests(unittest.TestCase):
    def test_review_hashes_exact_input_bytes_and_writes_artifacts(self) -> None:
        preflight = {"protocol": "preflight-fixture"}
        selection = {"protocol": "selection-fixture"}
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight_path = root / "preflight.json"
            selection_path = root / "selection.json"
            preflight_path.write_text(
                json.dumps(preflight, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            selection_path.write_text(
                json.dumps(selection, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            out = root / "out"
            captured = {}

            def fake_review(**kwargs):
                captured.update(kwargs)
                return {
                    "protocol": "fmp-phase8a-acceptance-v1",
                    "experiment_id": "EXP-20260922-016",
                    "promotion_authorized": False,
                    "demo_order_authorized": False,
                    "live_order_authorized": False,
                    "broker_mutation_authorized": False,
                    "real_money_authorized": False,
                    "outcome": "PHASE8A_RESEARCH_REJECTED",
                    "shadow_candidate_authorized": False,
                    "phase8b_design_authorized": False,
                }

            stdout = StringIO()
            with patch(
                "fmp.portfolio.acceptance_cli.review_phase8a_acceptance",
                side_effect=fake_review,
            ):
                with redirect_stdout(stdout):
                    code = main(
                        [
                            "review",
                            "--preflight",
                            str(preflight_path),
                            "--selection",
                            str(selection_path),
                            "--code-commit",
                            COMMIT,
                            "--out",
                            str(out),
                        ]
                    )

            self.assertEqual(code, 0)
            self.assertEqual(captured["preflight"], preflight)
            self.assertEqual(captured["selection"], selection)
            self.assertEqual(captured["code_commit"], COMMIT)
            self.assertEqual(
                captured["preflight_sha256"],
                hashlib.sha256(preflight_path.read_bytes()).hexdigest(),
            )
            self.assertEqual(
                captured["selection_sha256"],
                hashlib.sha256(selection_path.read_bytes()).hexdigest(),
            )
            self.assertTrue((out / "acceptance.json").is_file())
            self.assertTrue((out / "manifest.json").is_file())
            printed = json.loads(stdout.getvalue())
            self.assertEqual(
                printed["outcome"],
                "PHASE8A_RESEARCH_REJECTED",
            )

    def test_cli_exposes_no_market_data_or_backtest_arguments(self) -> None:
        with self.assertRaises(SystemExit):
            main(["review", "--dataset-root", "/tmp/data"])


if __name__ == "__main__":
    unittest.main()
