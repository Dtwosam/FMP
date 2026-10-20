"""DEC-1816 seven-source source-only owner parity stays BLOCKED."""
import contextlib
import io
import json
from pathlib import Path
import runpy
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MOD = runpy.run_path(
    str(ROOT / "scripts" / "dec1816_offline_security_review_bundle.py")
)
SIX = runpy.run_path(str(MOD["SIX"]))
BLANK = runpy.run_path(str(MOD["BLANK"]))
BUILD = MOD["compile_blocked_review_bundle"]


class Phase8ABlockedSevenSourceIndexTests(unittest.TestCase):
    def test_exact_missing_owner_identity_matches_both_reports(self):
        report = BUILD()
        self.assertEqual(report["eight_missing_independent_proofs"],
                         SIX["compile_blocked_handoff"]()[
                             "eight_missing_independent_proofs"])
        self.assertEqual(report["eight_missing_independent_proofs"],
                         BLANK["report_blocked_blank_worksheet"]()[
                             "eight_independent_proofs"])
        self.assertEqual(len(report["eight_missing_independent_proofs"]), 8)

    def test_historical_fingerprints_do_not_claim_current_main(self):
        report = BUILD()
        self.assertEqual(len(report["five_documentary_source_sha256"]), 5)
        self.assertEqual(len(report["historical_workflow_sha256"]), 64)
        self.assertEqual(
            report["blank_worksheet_git_blob_sha1"],
            BLANK["PINNED_BLANK_WORKSHEET_GIT_BLOB_SHA1"])
        self.assertIn("observed_main_sha_not_live_ref", report)

    def test_no_review_index_would_grant_protected_or_broker_action(self):
        report = BUILD()
        self.assertEqual(report["disposition"], "BLOCKED_NO_EXECUTION_PERMISSION")
        self.assertFalse(report["independent_external_admin_runner_proof_verified"])
        self.assertFalse(report["2023_run385_attempt1_authorized"])
        self.assertFalse(report["broker_demo_live_or_real_money_authorized"])
        self.assertEqual(report["allowed_actions"], [])
        self.assertTrue(report["no_external_actions_performed"])

    def test_forged_worksheet_rejects_seven_source_index(self):
        with tempfile.TemporaryDirectory() as folder:
            edited = Path(folder) / "worksheet.md"
            edited.write_bytes(BLANK["WORKSHEET"].read_bytes() + b"APPROVED")
            with self.assertRaises((OSError, ValueError)):
                BUILD(worksheet=edited)

    def test_cli_success_is_blocked_and_invalid_has_no_stdout(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = MOD["main"]([])
        self.assertEqual(code, 3)
        self.assertEqual(err.getvalue(), "")
        self.assertEqual(json.loads(out.getvalue())["disposition"],
                         "BLOCKED_NO_EXECUTION_PERMISSION")
        with tempfile.TemporaryDirectory() as folder:
            edited = Path(folder) / "worksheet.md"
            edited.write_bytes(b"READY")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = MOD["main"](["--worksheet", str(edited)])
        self.assertEqual(code, 2)
        self.assertEqual(out.getvalue(), "")
        self.assertIn("BLOCKED:", err.getvalue())


if __name__ == "__main__":
    unittest.main()
