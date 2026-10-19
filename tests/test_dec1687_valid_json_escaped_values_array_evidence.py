"""DEC-1687: legal JSON escapes within evidence arrays retain review parity.

Offline synthetic test-only inputs; no remote or protected access.
"""
import copy
import io
import json
import unittest

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli

SENTINEL = "DEC1687_ESCAPED_VALUE_SENTINEL"


class ArrayEvidenceLegalJsonEscapesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_valid_escape_has_direct_review_parity(self, category, path,
                                                      token, expected):
        self.assertIn(category, source.REQUIRED)
        self.assertEqual(json.loads(token), expected)
        before = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        cursor = copied[category]
        for part in path:
            cursor = cursor[part]
        self.assertIs(type(cursor), dict)
        cursor["synthetic_escape"] = SENTINEL
        encoded = json.dumps(copied, sort_keys=True, separators=(",", ":"))
        quoted = json.dumps(SENTINEL)
        self.assertEqual(encoded.count(quoted), 1)
        escaped = encoded.replace(quoted, token, 1)
        decoded = json.loads(escaped)
        target = decoded[category]
        for part in path:
            target = target[part]
        self.assertEqual(target["synthetic_escape"], expected)
        cursor["synthetic_escape"] = expected
        direct = source.review_bundle_envelope(copied)
        parsed = source.review_bundle_json_text(escaped)
        self.assertEqual(parsed, direct)
        self.assertNotIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED",
                         parsed["diagnostics"])
        self.assertNotIn("BUNDLE_JSON_UNICODE_UNREVIEWED",
                         parsed["diagnostics"])
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(escaped), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(before, self.fixture._portable_top_level_members_json())
        self.assertEqual(status, 0 if direct["source_consistency"] else 2)
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        self.assertEqual(emitted["source_consistency"],
                         direct["source_consistency"])
        self.assertEqual(emitted["diagnostics"], list(direct["diagnostics"]))
        self.assertNotIn(SENTINEL, out.getvalue())
        self.assertNotIn("tests/sample.py", out.getvalue())
        self.assertNotIn("docs/sample.md", out.getvalue())
        for verdict in (direct, parsed, emitted):
            self.assertFalse(verdict["independent_original_os_proof"])
            self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(verdict["can_authorize_annual_run"])

    def test_legal_escape_runs_escaped_solidus(self):
        self._assert_valid_escape_has_direct_review_parity(
            "runs", (0,), "\"a\\/b\"", "a/b")

    def test_legal_escape_runs_escaped_ascii_unicode(self):
        self._assert_valid_escape_has_direct_review_parity(
            "runs", (0,), "\"\\u0061\"", "a")

    def test_legal_escape_runs_escaped_tab(self):
        self._assert_valid_escape_has_direct_review_parity(
            "runs", (0,), "\"a\\tb\"", "a\tb")

    def test_legal_escape_runs_escaped_newline(self):
        self._assert_valid_escape_has_direct_review_parity(
            "runs", (0,), "\"a\\nb\"", "a\nb")

    def test_legal_escape_runs_escaped_bmp_unicode(self):
        self._assert_valid_escape_has_direct_review_parity(
            "runs", (0,), "\"\\u03B1\"", "α")

    def test_legal_escape_runs_escaped_surrogate_pair(self):
        self._assert_valid_escape_has_direct_review_parity(
            "runs", (0,), "\"\\uD83D\\uDE00\"", "😀")

    def test_legal_escape_runs_escaped_quote(self):
        self._assert_valid_escape_has_direct_review_parity(
            "runs", (0,), "\"a\\\"b\"", "a\"b")

    def test_legal_escape_runs_escaped_backslash(self):
        self._assert_valid_escape_has_direct_review_parity(
            "runs", (0,), "\"a\\\\b\"", "a\\b")

    def test_legal_escape_comparison_files_escaped_solidus(self):
        self._assert_valid_escape_has_direct_review_parity(
            "compare", ("files", 0), "\"a\\/b\"", "a/b")

    def test_legal_escape_comparison_files_escaped_ascii_unicode(self):
        self._assert_valid_escape_has_direct_review_parity(
            "compare", ("files", 0), "\"\\u0061\"", "a")

    def test_legal_escape_comparison_files_escaped_tab(self):
        self._assert_valid_escape_has_direct_review_parity(
            "compare", ("files", 0), "\"a\\tb\"", "a\tb")

    def test_legal_escape_comparison_files_escaped_newline(self):
        self._assert_valid_escape_has_direct_review_parity(
            "compare", ("files", 0), "\"a\\nb\"", "a\nb")

    def test_legal_escape_comparison_files_escaped_bmp_unicode(self):
        self._assert_valid_escape_has_direct_review_parity(
            "compare", ("files", 0), "\"\\u03B1\"", "α")

    def test_legal_escape_comparison_files_escaped_surrogate_pair(self):
        self._assert_valid_escape_has_direct_review_parity(
            "compare", ("files", 0), "\"\\uD83D\\uDE00\"", "😀")

    def test_legal_escape_comparison_files_escaped_quote(self):
        self._assert_valid_escape_has_direct_review_parity(
            "compare", ("files", 0), "\"a\\\"b\"", "a\"b")

    def test_legal_escape_comparison_files_escaped_backslash(self):
        self._assert_valid_escape_has_direct_review_parity(
            "compare", ("files", 0), "\"a\\\\b\"", "a\\b")

    def test_legal_escape_jobs_by_run_escaped_solidus(self):
        self._assert_valid_escape_has_direct_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"a\\/b\"", "a/b")

    def test_legal_escape_jobs_by_run_escaped_ascii_unicode(self):
        self._assert_valid_escape_has_direct_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"\\u0061\"", "a")

    def test_legal_escape_jobs_by_run_escaped_tab(self):
        self._assert_valid_escape_has_direct_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"a\\tb\"", "a\tb")

    def test_legal_escape_jobs_by_run_escaped_newline(self):
        self._assert_valid_escape_has_direct_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"a\\nb\"", "a\nb")

    def test_legal_escape_jobs_by_run_escaped_bmp_unicode(self):
        self._assert_valid_escape_has_direct_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"\\u03B1\"", "α")

    def test_legal_escape_jobs_by_run_escaped_surrogate_pair(self):
        self._assert_valid_escape_has_direct_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"\\uD83D\\uDE00\"", "😀")

    def test_legal_escape_jobs_by_run_escaped_quote(self):
        self._assert_valid_escape_has_direct_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"a\\\"b\"", "a\"b")

    def test_legal_escape_jobs_by_run_escaped_backslash(self):
        self._assert_valid_escape_has_direct_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"a\\\\b\"", "a\\b")

    def test_legal_escape_phase3_scenarios_escaped_solidus(self):
        self._assert_valid_escape_has_direct_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"a\\/b\"", "a/b")

    def test_legal_escape_phase3_scenarios_escaped_ascii_unicode(self):
        self._assert_valid_escape_has_direct_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"\\u0061\"", "a")

    def test_legal_escape_phase3_scenarios_escaped_tab(self):
        self._assert_valid_escape_has_direct_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"a\\tb\"", "a\tb")

    def test_legal_escape_phase3_scenarios_escaped_newline(self):
        self._assert_valid_escape_has_direct_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"a\\nb\"", "a\nb")

    def test_legal_escape_phase3_scenarios_escaped_bmp_unicode(self):
        self._assert_valid_escape_has_direct_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"\\u03B1\"", "α")

    def test_legal_escape_phase3_scenarios_escaped_surrogate_pair(self):
        self._assert_valid_escape_has_direct_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"\\uD83D\\uDE00\"", "😀")

    def test_legal_escape_phase3_scenarios_escaped_quote(self):
        self._assert_valid_escape_has_direct_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"a\\\"b\"", "a\"b")

    def test_legal_escape_phase3_scenarios_escaped_backslash(self):
        self._assert_valid_escape_has_direct_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"a\\\\b\"", "a\\b")

    def test_legal_escape_full_tree_entries_escaped_solidus(self):
        self._assert_valid_escape_has_direct_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"a\\/b\"", "a/b")

    def test_legal_escape_full_tree_entries_escaped_ascii_unicode(self):
        self._assert_valid_escape_has_direct_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"\\u0061\"", "a")

    def test_legal_escape_full_tree_entries_escaped_tab(self):
        self._assert_valid_escape_has_direct_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"a\\tb\"", "a\tb")

    def test_legal_escape_full_tree_entries_escaped_newline(self):
        self._assert_valid_escape_has_direct_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"a\\nb\"", "a\nb")

    def test_legal_escape_full_tree_entries_escaped_bmp_unicode(self):
        self._assert_valid_escape_has_direct_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"\\u03B1\"", "α")

    def test_legal_escape_full_tree_entries_escaped_surrogate_pair(self):
        self._assert_valid_escape_has_direct_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"\\uD83D\\uDE00\"", "😀")

    def test_legal_escape_full_tree_entries_escaped_quote(self):
        self._assert_valid_escape_has_direct_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"a\\\"b\"", "a\"b")

    def test_legal_escape_full_tree_entries_escaped_backslash(self):
        self._assert_valid_escape_has_direct_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"a\\\\b\"", "a\\b")

    def test_legal_escape_merge_parents_escaped_solidus(self):
        self._assert_valid_escape_has_direct_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"a\\/b\"", "a/b")

    def test_legal_escape_merge_parents_escaped_ascii_unicode(self):
        self._assert_valid_escape_has_direct_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"\\u0061\"", "a")

    def test_legal_escape_merge_parents_escaped_tab(self):
        self._assert_valid_escape_has_direct_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"a\\tb\"", "a\tb")

    def test_legal_escape_merge_parents_escaped_newline(self):
        self._assert_valid_escape_has_direct_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"a\\nb\"", "a\nb")

    def test_legal_escape_merge_parents_escaped_bmp_unicode(self):
        self._assert_valid_escape_has_direct_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"\\u03B1\"", "α")

    def test_legal_escape_merge_parents_escaped_surrogate_pair(self):
        self._assert_valid_escape_has_direct_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"\\uD83D\\uDE00\"", "😀")

    def test_legal_escape_merge_parents_escaped_quote(self):
        self._assert_valid_escape_has_direct_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"a\\\"b\"", "a\"b")

    def test_legal_escape_merge_parents_escaped_backslash(self):
        self._assert_valid_escape_has_direct_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"a\\\\b\"", "a\\b")

    def test_legal_escape_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
