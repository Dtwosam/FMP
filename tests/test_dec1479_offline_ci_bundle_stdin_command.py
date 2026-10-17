"""DEC-1479: explicitly supplied stdin-only offline CI source review command.

Usage: python tests/test_dec1479_offline_ci_bundle_stdin_command.py < bundle.json

Exit 0 means caller-supplied records passed shape/source consistency checks,
NOT that a protected annual workflow is authorized. No GitHub client, browser,
protected original/archive, annual dispatch, merge, or broker interaction.
"""
from __future__ import annotations

import io
import json
import sys
import unittest

import test_dec1478_portable_ci_source_bundle_envelope as envelope


def run_stdin_review(input_stream, output_stream):
    """Read at most capped text from supplied stdin, print structured result."""
    try:
        raw = input_stream.read(envelope.MAX_TEXT_CHARS + 1)
    except (OSError, UnicodeError, ValueError):
        verdict = envelope.fail_closed("BUNDLE_STDIN_READ_UNREVIEWED")
    else:
        verdict = envelope.review_bundle_json_text(raw)
    # Never echo supplied evidence. Only machine-readable verdict fields.
    output_stream.write(json.dumps(verdict, sort_keys=True,
                                   ensure_ascii=True,
                                   separators=(",", ":")) + "\n")
    # Zero is merely *offline source consistency*, never execution consent.
    return 0 if verdict["source_consistency"] is True else 2


def main():
    # No positional filenames, network URLs, auth tokens or workflow actions.
    if len(sys.argv) != 1:
        verdict = envelope.fail_closed("BUNDLE_STDIN_ONLY_INVOCATION_REQUIRED")
        sys.stdout.write(json.dumps(verdict, sort_keys=True) + "\n")
        return 2
    return run_stdin_review(sys.stdin, sys.stdout)


class ExplicitStdinReviewIsNotAnnualWorkflowAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        envelope.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        fixture = envelope.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        fixture.setUp()
        self.bundle = fixture.envelope
        self.stdout = io.StringIO()

    def run_raw(self, raw):
        status = run_stdin_review(io.StringIO(raw), self.stdout)
        record = json.loads(self.stdout.getvalue())
        return status, record

    def run_fixture(self):
        return self.run_raw(json.dumps(self.bundle))

    def test_consistent_bundle_reports_source_consistency_only(self):
        status, record = self.run_fixture()
        self.assertEqual(status, 0)
        self.assertTrue(record["source_consistency"])
        self.assertEqual(record["diagnostics"], [])
        self.assertFalse(record["can_authorize_annual_run"])

    def test_output_contains_no_caller_original_evidence(self):
        status, record = self.run_fixture()
        self.assertEqual(status, 0)
        self.assertNotIn("changed_bytes_b64", self.stdout.getvalue())
        self.assertNotIn("phase3-backtester-acceptance-", self.stdout.getvalue())
        self.assertEqual(len(record), 5)

    def test_invalid_json_has_nonzero_exit_and_diagnostic(self):
        status, record = self.run_raw('{"schema":')
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED", record["diagnostics"])

    def test_null_stdin_object_never_passes(self):
        status, record = self.run_raw("null")
        self.assertEqual(status, 2)
        self.assertFalse(record["source_consistency"])

    def test_empty_stdin_never_passes(self):
        status, record = self.run_raw("")
        self.assertEqual(status, 2)
        self.assertFalse(record["can_authorize_annual_run"])

    def test_missing_evidence_category_has_nonzero_exit(self):
        self.bundle.pop("full_tree_snapshots")
        status, record = self.run_fixture()
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_KEY_INVENTORY_UNREVIEWED",
                      record["diagnostics"])

    def test_tampered_source_bytes_cannot_pass(self):
        import base64
        self.bundle["changed_bytes_b64"]["tests/sample.py"] = (
            base64.b64encode(b"other code\n").decode("ascii"))
        status, record = self.run_fixture()
        self.assertEqual(status, 2)
        self.assertFalse(record["source_consistency"])

    def test_job_log_text_changed_without_digest_cannot_pass(self):
        self.bundle["raw_ci_runner_logs"]["8000"] += "\nadded record"
        status, record = self.run_fixture()
        self.assertEqual(status, 2)
        self.assertFalse(record["source_consistency"])

    def test_excessive_stdin_is_rejected_without_processing(self):
        status, record = self.run_raw(" "*(envelope.MAX_TEXT_CHARS+1))
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_JSON_TEXT_UNREVIEWED",
                      record["diagnostics"])

    def test_source_consistency_never_enables_any_annual_gate(self):
        _, record = self.run_fixture()
        self.assertFalse(record["independent_original_os_proof"])
        self.assertFalse(record["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(record["can_authorize_annual_run"])

    def test_duplicate_json_keys_have_nonzero_exit(self):
        status, record = self.run_raw('{"schema":1,"schema":2}')
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED",
                      record["diagnostics"])

    def test_malformed_run_map_key_is_rejected(self):
        item = self.bundle["jobs_by_run"].pop("8000")
        self.bundle["jobs_by_run"]["08000"] = item
        status, record = self.run_fixture()
        self.assertEqual(status, 2)
        self.assertIn("BUNDLE_RUN_KEY_UNREVIEWED", record["diagnostics"])


if __name__ == "__main__":
    raise SystemExit(main())
