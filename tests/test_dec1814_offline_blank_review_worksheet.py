"""DEC-1814 pinned blank human proof worksheet stays non-authorizing."""
import contextlib
import io
from pathlib import Path
import runpy
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MOD = runpy.run_path(
    str(ROOT / "scripts" / "dec1814_offline_blank_review_worksheet.py")
)
AUDIT = MOD["report_blocked_blank_worksheet"]
WORKSHEET = MOD["WORKSHEET"]


class Phase8ABlankWorksheetIntegrityTests(unittest.TestCase):
    def test_pinned_eight_owner_worksheet_is_only_blocked(self):
        report = AUDIT()
        self.assertEqual(report["disposition"], "BLOCKED_NO_EXECUTION_PERMISSION")
        self.assertEqual(len(report["eight_independent_proofs"]), 8)
        self.assertTrue(all(
            row["status"] == "MISSING"
            for row in report["eight_independent_proofs"]
        ))
        self.assertEqual(report["allowed_actions"], [])
        self.assertFalse(report["2023_run385_attempt1_authorized"])
        self.assertFalse(report["broker_demo_live_or_real_money_authorized"])

    def test_external_ready_or_approved_claim_is_not_this_blank_worksheet(self):
        with tempfile.TemporaryDirectory() as folder:
            source = WORKSHEET.read_bytes()
            forged = Path(folder) / "worksheet.md"
            forged.write_bytes(source + bytes((10,)) + b"APPROVED: dispatch run385" + bytes((10,)))
            with self.assertRaisesRegex(MOD["InvalidBlankWorksheet"],
                                        "pinned MISSING-only"):
                AUDIT(forged)

    def test_rewriting_missing_marker_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            source = WORKSHEET.read_bytes()
            forged = Path(folder) / "worksheet.md"
            marker = "**Status: MISSING — not authorization.**".encode("utf-8")
            self.assertIn(marker, source)
            forged.write_bytes(source.replace(marker, b"STATUS APPROVED", 1))
            with self.assertRaises(MOD["InvalidBlankWorksheet"]):
                AUDIT(forged)

    def test_cli_nonzero_success_and_empty_stdout_on_forgery(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = MOD["main"]([])
        self.assertEqual(code, 3)
        self.assertIn("BLOCKED_NO_EXECUTION_PERMISSION", out.getvalue())
        self.assertEqual(err.getvalue(), "")
        with tempfile.TemporaryDirectory() as folder:
            forged = Path(folder) / "worksheet.md"
            forged.write_bytes(WORKSHEET.read_bytes() + b"INVALID APPROVAL")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = MOD["main"](["--worksheet", str(forged)])
        self.assertEqual(code, 2)
        self.assertEqual(out.getvalue(), "")
        self.assertIn("BLOCKED:", err.getvalue())

    def test_symlinked_worksheet_is_not_followed(self):
        with tempfile.TemporaryDirectory() as folder:
            linked = Path(folder) / "worksheet.md"
            linked.symlink_to(WORKSHEET)
            with self.assertRaises((OSError, ValueError)):
                AUDIT(linked)


if __name__ == "__main__":
    unittest.main()
