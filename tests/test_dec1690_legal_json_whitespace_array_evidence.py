"""DEC-1690: legal ASCII JSON whitespace inside nested evidence dictionaries.

Offline synthetic review parity; no protected data or authorization.
"""
import copy
import io
import json
import unittest

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli


class ArrayEvidenceJsonWhitespaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_json_whitespace_preserves_review(self, category, path,
                                                 around_colon):
        self.assertIn(category, source.REQUIRED)
        self.assertTrue(around_colon.count(":") == 1)
        self.assertTrue(all(c in " \t\r\n:" for c in around_colon))
        before = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        cursor = copied[category]
        for segment in path:
            cursor = cursor[segment]
        self.assertIs(type(cursor), dict)
        cursor["synthetic_ws"] = True
        encoded = json.dumps(copied, separators=(",", ":"), sort_keys=True)
        key = json.dumps("synthetic_ws")
        needle = key + ":true"
        self.assertEqual(encoded.count(needle), 1)
        spaced = encoded.replace(needle, key + around_colon + "true", 1)
        parsed_doc = json.loads(spaced)
        target = parsed_doc[category]
        for segment in path:
            target = target[segment]
        self.assertIs(target["synthetic_ws"], True)
        direct = source.review_bundle_envelope(copied)
        parsed = source.review_bundle_json_text(spaced)
        self.assertEqual(parsed, direct)
        self.assertNotIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED",
                         parsed["diagnostics"])
        self.assertNotIn("BUNDLE_JSON_UNICODE_UNREVIEWED",
                         parsed["diagnostics"])
        out = io.StringIO()
        rc = cli.run_stdin_review(io.StringIO(spaced), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(before, self.fixture._portable_top_level_members_json())
        self.assertEqual(rc, 0 if direct["source_consistency"] else 2)
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        self.assertEqual(emitted["source_consistency"],
                         direct["source_consistency"])
        self.assertEqual(emitted["diagnostics"], list(direct["diagnostics"]))
        self.assertNotIn("tests/sample.py", out.getvalue())
        self.assertNotIn("docs/sample.md", out.getvalue())
        for verdict in (direct, parsed, emitted):
            self.assertFalse(verdict["independent_original_os_proof"])
            self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(verdict["can_authorize_annual_run"])

    def test_json_whitespace_runs_spaces(self):
        self._assert_json_whitespace_preserves_review(
            "runs", (0,), " : ")

    def test_json_whitespace_runs_tabs(self):
        self._assert_json_whitespace_preserves_review(
            "runs", (0,), "\t:\t")

    def test_json_whitespace_runs_newlines(self):
        self._assert_json_whitespace_preserves_review(
            "runs", (0,), "\n:\n")

    def test_json_whitespace_runs_carriage_returns(self):
        self._assert_json_whitespace_preserves_review(
            "runs", (0,), "\r:\r")

    def test_json_whitespace_runs_crlf(self):
        self._assert_json_whitespace_preserves_review(
            "runs", (0,), "\r\n:\r\n")

    def test_json_whitespace_runs_mixed(self):
        self._assert_json_whitespace_preserves_review(
            "runs", (0,), " \t\r\n:\n\t ")

    def test_json_whitespace_comparison_files_spaces(self):
        self._assert_json_whitespace_preserves_review(
            "compare", ("files", 0), " : ")

    def test_json_whitespace_comparison_files_tabs(self):
        self._assert_json_whitespace_preserves_review(
            "compare", ("files", 0), "\t:\t")

    def test_json_whitespace_comparison_files_newlines(self):
        self._assert_json_whitespace_preserves_review(
            "compare", ("files", 0), "\n:\n")

    def test_json_whitespace_comparison_files_carriage_returns(self):
        self._assert_json_whitespace_preserves_review(
            "compare", ("files", 0), "\r:\r")

    def test_json_whitespace_comparison_files_crlf(self):
        self._assert_json_whitespace_preserves_review(
            "compare", ("files", 0), "\r\n:\r\n")

    def test_json_whitespace_comparison_files_mixed(self):
        self._assert_json_whitespace_preserves_review(
            "compare", ("files", 0), " \t\r\n:\n\t ")

    def test_json_whitespace_jobs_by_run_spaces(self):
        self._assert_json_whitespace_preserves_review(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), " : ")

    def test_json_whitespace_jobs_by_run_tabs(self):
        self._assert_json_whitespace_preserves_review(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\t:\t")

    def test_json_whitespace_jobs_by_run_newlines(self):
        self._assert_json_whitespace_preserves_review(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\n:\n")

    def test_json_whitespace_jobs_by_run_carriage_returns(self):
        self._assert_json_whitespace_preserves_review(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\r:\r")

    def test_json_whitespace_jobs_by_run_crlf(self):
        self._assert_json_whitespace_preserves_review(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\r\n:\r\n")

    def test_json_whitespace_jobs_by_run_mixed(self):
        self._assert_json_whitespace_preserves_review(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), " \t\r\n:\n\t ")

    def test_json_whitespace_phase3_scenarios_spaces(self):
        self._assert_json_whitespace_preserves_review(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), " : ")

    def test_json_whitespace_phase3_scenarios_tabs(self):
        self._assert_json_whitespace_preserves_review(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\t:\t")

    def test_json_whitespace_phase3_scenarios_newlines(self):
        self._assert_json_whitespace_preserves_review(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\n:\n")

    def test_json_whitespace_phase3_scenarios_carriage_returns(self):
        self._assert_json_whitespace_preserves_review(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\r:\r")

    def test_json_whitespace_phase3_scenarios_crlf(self):
        self._assert_json_whitespace_preserves_review(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\r\n:\r\n")

    def test_json_whitespace_phase3_scenarios_mixed(self):
        self._assert_json_whitespace_preserves_review(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), " \t\r\n:\n\t ")

    def test_json_whitespace_full_tree_entries_spaces(self):
        self._assert_json_whitespace_preserves_review(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), " : ")

    def test_json_whitespace_full_tree_entries_tabs(self):
        self._assert_json_whitespace_preserves_review(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\t:\t")

    def test_json_whitespace_full_tree_entries_newlines(self):
        self._assert_json_whitespace_preserves_review(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\n:\n")

    def test_json_whitespace_full_tree_entries_carriage_returns(self):
        self._assert_json_whitespace_preserves_review(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\r:\r")

    def test_json_whitespace_full_tree_entries_crlf(self):
        self._assert_json_whitespace_preserves_review(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\r\n:\r\n")

    def test_json_whitespace_full_tree_entries_mixed(self):
        self._assert_json_whitespace_preserves_review(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), " \t\r\n:\n\t ")

    def test_json_whitespace_merge_parents_spaces(self):
        self._assert_json_whitespace_preserves_review(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), " : ")

    def test_json_whitespace_merge_parents_tabs(self):
        self._assert_json_whitespace_preserves_review(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\t:\t")

    def test_json_whitespace_merge_parents_newlines(self):
        self._assert_json_whitespace_preserves_review(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\n:\n")

    def test_json_whitespace_merge_parents_carriage_returns(self):
        self._assert_json_whitespace_preserves_review(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\r:\r")

    def test_json_whitespace_merge_parents_crlf(self):
        self._assert_json_whitespace_preserves_review(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\r\n:\r\n")

    def test_json_whitespace_merge_parents_mixed(self):
        self._assert_json_whitespace_preserves_review(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), " \t\r\n:\n\t ")

    def test_json_whitespace_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
