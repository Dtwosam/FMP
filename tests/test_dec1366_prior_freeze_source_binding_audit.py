"""Read-only DEC-1366 source boundary review; NEVER annual execution.

Git show is local and returns only the committed workflow YAML. No GH API,
annual CLI invocation, historical artifacts, privileged operations or dispatch.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PriorAnnualFreezeIntegrityStillNeedsIndependentAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        workflow = subprocess.check_output(
            ["git", "show",
             "HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml"],
            cwd=ROOT, text=True,
        )
        cls.source = workflow.split("  annual_preflight:\n", 1)[1].split(
            "  annual_cell:\n", 1)[0]

    def test_prior_segment_switch_has_2015_no_predecessor_and_2023_2022(self):
        s = self.source
        self.assertIn('2015)\n              test -z "$PREVIOUS_RUN_ID"', s)
        self.assertIn('2023) previous_segment="2022" ;;', s)
        for earlier, prior in ((2016, 2015), (2017, 2016), (2018, 2017),
                               (2019, 2018), (2020, 2019), (2021, 2020),
                               (2022, 2021)):
            with self.subTest(segment=earlier):
                self.assertIn(f'{earlier}) previous_segment="{prior}" ;;', s)

    def test_previous_run_identifier_is_required_numeric_positive_in_source(self):
        s = self.source
        self.assertIn('test -n "$PREVIOUS_RUN_ID"', s)
        self.assertIn('case "$PREVIOUS_RUN_ID" in', s)
        self.assertIn('*[!0-9]*|"") exit 1 ;;', s)
        self.assertIn('test "$PREVIOUS_RUN_ID" -gt 0', s)

    def test_prior_metadata_fetch_runs_only_after_execution_recheck_step(self):
        s = self.source
        self.assertLess(
            s.index("- name: Require separately authorized annual catalogue execution"),
            s.index("- name: Fetch exact prior annual freeze evidence"))
        self.assertIn("if: steps.prior.outputs.required == 'true'", s)

    def test_prior_fetch_uses_input_id_but_not_independently_attested_id(self):
        s = self.source
        fragment = s.split("- name: Fetch exact prior annual freeze evidence", 1)[1].split(
            "- name: Require immediately prior annual freeze", 1)[0]
        self.assertIn("PREVIOUS_RUN_ID: ", fragment)
        self.assertIn("inputs.previous_annual_freeze_run_id", fragment)
        self.assertIn('actions/runs/$PREVIOUS_RUN_ID', fragment)
        self.assertIn('actions/runs/$PREVIOUS_RUN_ID/artifacts?per_page=100', fragment)

    def test_prior_freeze_expected_name_uses_predecessor_head_sha(self):
        s = self.source
        self.assertIn("previous_head=", s)
        self.assertIn(".head_sha", s)
        self.assertIn('expected_name="phase8a-annual-catalogue-freeze-', s)
        self.assertIn('$PREVIOUS_SEGMENT-$previous_head"', s)
        self.assertIn("select(.name == $name and .expired == false)", s)
        self.assertIn('test "$matches" = "1"', s)

    def test_prior_archive_sha256_digest_is_checked_before_extraction(self):
        s = self.source
        self.assertIn('case "$expected_digest" in sha256:*) ;; *) exit 1 ;; esac', s)
        self.assertLess(
            s.index('actual_sha="$(sha256sum .prior-freeze/freeze.zip'),
            s.index('test "$actual_sha" = "$expected_sha"'))
        self.assertLess(
            s.index('test "$actual_sha" = "$expected_sha"'),
            s.index("unzip -q .prior-freeze/freeze.zip"))

    def test_prior_archive_requires_exactly_one_freeze_json(self):
        s = self.source
        self.assertIn("find .prior-freeze/artifact -type f -name annual-freeze.json", s)
        self.assertIn('test "$(printf', s)
        self.assertIn('"$freeze_evidence" .prior-freeze/annual-freeze.json', s)

    def test_predecessor_validation_binds_run_id_and_saved_evidence_path(self):
        s = self.source
        self.assertIn("- name: Require immediately prior annual freeze", s)
        self.assertIn("--expected-previous-run-id \"$PREVIOUS_RUN_ID\"", s)
        self.assertIn("--previous-run-json .prior-freeze/run.json", s)
        self.assertIn("--previous-freeze-evidence .prior-freeze/annual-freeze.json", s)
        self.assertIn("--out .preflight/prior-freeze.json", s)

    def test_preflight_still_uploads_partial_metadata_on_always_path(self):
        s = self.source
        uploader = s.split("- name: Upload annual catalogue preflight evidence", 1)[1]
        self.assertIn("if: always()", uploader)
        self.assertIn("path: .preflight", uploader)
        self.assertIn("include-hidden-files: true", uploader)
