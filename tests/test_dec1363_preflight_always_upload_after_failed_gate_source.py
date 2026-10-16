"""DEC-1363: committed workflow SOURCE inspection, never protected execution.

No annual workflow job is run, dispatched, installed, or authorized here.
The git read is confined to the commit's own tracked YAML object.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_BLOB = "HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml"


class PreflightArtifactAlwaysUploadCannotStandInForAnnualAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = subprocess.check_output(
            ["git", "show", WORKFLOW_BLOB], cwd=ROOT, text=True
        )
        cls.preflight = source.split("  annual_preflight:\n", 1)[1].split(
            "  annual_cell:\n", 1
        )[0]
        cls.cell = source.split("  annual_cell:\n", 1)[1].split(
            "  annual_freeze:\n", 1
        )[0]
        cls.freeze = source.split("  annual_freeze:\n", 1)[1]

    def test_preflight_checkout_and_metadata_fetch_precede_authorization(self):
        s = self.preflight
        self.assertLess(s.index("- name: Checkout"),
                        s.index("Fetch exact accepted EXP-044 source snapshots"))
        self.assertLess(s.index("Fetch exact accepted EXP-044 source snapshots"),
                        s.index("Require separately authorized annual catalogue execution"))

    def test_authentication_reads_write_checkout_relative_metadata_before_gate(self):
        s = self.preflight
        fetch = s.split("- name: Fetch exact accepted EXP-044 source snapshots", 1)[1].split(
            "- name: Validate exact accepted EXP-044 source snapshots", 1
        )[0]
        self.assertIn("GH_TOKEN: ${{ github.token }}", fetch)
        self.assertIn("mkdir -p .preflight", fetch)
        for name in ("feature-run.json", "feature-artifacts.json",
                     "outcome-run.json", "outcome-artifacts.json"):
            with self.subTest(name=name):
                self.assertIn("gh api", fetch)
                self.assertIn("> .preflight/" + name, fetch)

    def test_preflight_validation_output_is_written_before_separate_execution_check(self):
        s = self.preflight
        self.assertLess(s.index("- name: Validate exact accepted EXP-044 source snapshots"),
                        s.index("- name: Require separately authorized annual catalogue execution"))
        self.assertLess(s.index("--out .preflight/preflight.json"),
                        s.index("- name: Require separately authorized annual catalogue execution"))

    def test_preflight_upload_is_unconditional_even_when_prior_steps_failed(self):
        s = self.preflight
        upload = s.split("- name: Upload annual catalogue preflight evidence", 1)[1]
        self.assertIn("if: always()", upload)
        self.assertIn("uses: actions/upload-artifact@v6", upload)
        self.assertIn("path: .preflight", upload)
        self.assertIn("include-hidden-files: true", upload)
        self.assertIn("if-no-files-found: error", upload)

    def test_preflight_execution_gate_occurs_before_always_upload_not_before_metadata(self):
        s = self.preflight
        gate = s.index("- name: Require separately authorized annual catalogue execution")
        fetch = s.index("- name: Fetch exact accepted EXP-044 source snapshots")
        upload = s.index("- name: Upload annual catalogue preflight evidence")
        self.assertLess(fetch, gate)
        self.assertLess(gate, upload)
        self.assertNotIn("if: success()", s[upload:])

    def test_cell_and_freeze_upload_do_not_expose_same_always_path(self):
        for section, step, output in (
            (self.cell, "- name: Upload annual catalogue cell product", "path: .result"),
            (self.freeze, "- name: Upload annual segment freeze evidence",
             "path: .annual-freeze/annual-freeze.json"),
        ):
            with self.subTest(step=step):
                upload = section.split(step, 1)[1]
                self.assertIn("uses: actions/upload-artifact@v6", upload)
                self.assertIn(output, upload)
                self.assertNotIn("if: always()", upload)
