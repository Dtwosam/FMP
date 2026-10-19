"""DEC-1779 static-only installed annual workflow admission diagnostics."""
import contextlib
import copy
import io
import json
from pathlib import Path
import runpy
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "dec1779_annual_workflow_admission_audit.py"
MOD = runpy.run_path(str(SCRIPT))
REPORT = MOD["report_blocked_admission"]
WORKFLOW = ROOT / ".github" / "workflows" / "phase8a-annual-pattern-catalogue.yml"


class InstalledAnnualWorkflowNonAdmissionTests(unittest.TestCase):
    def test_reviewed_workflow_blob_identity_is_fixed(self):
        result = REPORT()
        self.assertEqual(
            result["historical_source_git_blob_sha1"],
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1")

    def test_all_three_real_installed_jobs_are_identified(self):
        report = REPORT()
        self.assertEqual(tuple(report["observed_jobs"]),
                         ("annual_preflight", "annual_cell", "annual_freeze"))
        self.assertEqual(report["job_count"], 3)

    def test_checkout_before_any_required_runtime_gate(self):
        jobs = REPORT()["observed_jobs"]
        self.assertEqual(
            {job: value["zero_based_in_job_gate_index"]
             for job, value in jobs.items()},
            {"annual_preflight": 7, "annual_cell": 4, "annual_freeze": 4})
        self.assertTrue(all(value["checkout_before_runtime_gate"]
                            for value in jobs.values()))

    def test_installed_python_and_runtime_setup_appear_before_gate(self):
        report = REPORT()
        self.assertTrue(all(
            set(value["risky_setup_before_gate"]) == {
                "Checkout", "Set up Python",
                "Install pinned annual catalogue runtime"}
            for value in report["observed_jobs"].values()
        ))

    def test_annual_preflight_fetches_source_metadata_before_runtime_gate(self):
        report = REPORT()
        self.assertIs(
            report["observed_jobs"]["annual_preflight"][
                "source_snapshot_metadata_fetch_before_gate"], True)
        self.assertEqual(report["observed_jobs"]["annual_preflight"][
            "zero_based_in_job_gate_index"], 7)

    def test_all_jobs_still_use_mutable_main_after_checkout(self):
        report = REPORT()
        self.assertTrue(all(
            value["requires_mutable_main_ref_in_job"]
            and value["main_ref_check_after_checkout"]
            for value in report["observed_jobs"].values()
        ))

    def test_report_never_claims_pre_checkout_pre_install_or_dispatch(self):
        report = REPORT()
        for key in (
            "precheckout_admission_proven", "preinstall_admission_proven",
            "authoritative_pre_dispatch_ref_lock_proven",
            "protected_2023_run385_attempt1_authorized",
            "annual_research_dispatch_authorized", "broker_or_trading_authorized",
        ):
            with self.subTest(flag=key):
                self.assertIs(report[key], False)
        self.assertEqual(report["allowed_actions"], [])

    def test_static_parser_denies_synthetic_gate_moved_before_checkout(self):
        contents = WORKFLOW.read_text(encoding="utf-8")
        changed = contents.replace(
            "      - name: Checkout",
            "      - name: Modified checkout",
            1)
        self.assertNotEqual(changed, contents)
        with self.assertRaisesRegex(MOD["InvalidStaticEvidence"],
                                    "reviewed pre-gate sequence"):
            MOD["classify_reviewed_step_order"](changed)

    def test_static_parser_denies_missing_first_job_gate(self):
        contents = WORKFLOW.read_text(encoding="utf-8")
        changed = contents.replace(
            "      - name: Require separately authorized annual catalogue execution",
            "      - name: Legacy optional check", 1)
        self.assertNotEqual(changed, contents)
        with self.assertRaisesRegex(MOD["InvalidStaticEvidence"],
                                    "reviewed pre-gate sequence"):
            MOD["classify_reviewed_step_order"](changed)

    def test_static_parser_denies_duplicate_job_block(self):
        contents = WORKFLOW.read_text(encoding="utf-8")
        changed = contents + "\n  annual_freeze:\n    steps:\n      - name: Checkout\n"
        with self.assertRaisesRegex(MOD["InvalidStaticEvidence"],
                                    "missing or duplicate annual job"):
            MOD["extract_job_steps"](changed)

    def test_modified_workflow_source_never_produces_a_complete_report(self):
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "workflow.yml"
            changed.write_bytes(WORKFLOW.read_bytes() + b"\n# editorial drift\n")
            with self.assertRaisesRegex(MOD["InvalidStaticEvidence"],
                                        "reviewed historical source"):
                REPORT(changed)

    def test_valid_blocked_report_cli_exits_three_and_not_zero(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = MOD["main"]([])
        self.assertEqual(status, 3)
        self.assertEqual(stderr.getvalue(), "")
        report = json.loads(stdout.getvalue())
        self.assertFalse(report["annual_research_dispatch_authorized"])

    def test_modified_source_cli_exits_two_without_report(self):
        with tempfile.TemporaryDirectory() as directory:
            bad = Path(directory) / "annual.yml"
            bad.write_bytes(WORKFLOW.read_bytes() + b"\n# fake approval")
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                status = MOD["main"](["--workflow", str(bad)])
            self.assertEqual(status, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("BLOCKED:", stderr.getvalue())

    def test_no_workflow_dispatch_or_broker_is_needed(self):
        report = REPORT()
        self.assertIn("Independent administrator/security", report["next_external_review"])
        self.assertEqual(report["disposition"],
                         "BLOCKED_NOT_EXECUTABLE_AND_NOT_ADMIN_ATTESTED")
        self.assertTrue(report["source_sha_and_live_ref_at_dispatch_not_authenticated"])
