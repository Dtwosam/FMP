"""DEC-1688: valid escaped JSON object member names in evidence arrays.

Offline synthetic tests; parsed and direct-memory reviews must match.
"""
import copy
import io
import json
import unittest

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli


class ArrayEvidenceEscapedObjectKeysTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_valid_escaped_key_has_review_parity(self, category, path,
                                                    encoded_key, key):
        self.assertIn(category, source.REQUIRED)
        self.assertEqual(json.loads(encoded_key), key)
        clean = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        cursor = copied[category]
        for part in path:
            cursor = cursor[part]
        self.assertIs(type(cursor), dict)
        self.assertNotIn(key, cursor)
        cursor[key] = "synthetic_value"
        encoded = json.dumps(copied, sort_keys=True, separators=(",", ":"))
        quoted = json.dumps(key)
        self.assertEqual(encoded.count(quoted + ":"), 1)
        escaped = encoded.replace(quoted + ":", encoded_key + ":", 1)
        decoded = json.loads(escaped)
        target = decoded[category]
        for part in path:
            target = target[part]
        self.assertEqual(target[key], "synthetic_value")
        direct = source.review_bundle_envelope(copied)
        parsed = source.review_bundle_json_text(escaped)
        self.assertEqual(direct, parsed)
        self.assertNotIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED",
                         parsed["diagnostics"])
        self.assertNotIn("BUNDLE_JSON_UNICODE_UNREVIEWED",
                         parsed["diagnostics"])
        out = io.StringIO()
        rc = cli.run_stdin_review(io.StringIO(escaped), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(clean, self.fixture._portable_top_level_members_json())
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

    def test_escaped_key_runs_unicode_head(self):
        self._assert_valid_escaped_key_has_review_parity(
            "runs", (0,), "\"\\u0073ynthetic_key\"", "synthetic_key")

    def test_escaped_key_runs_unicode_middle(self):
        self._assert_valid_escaped_key_has_review_parity(
            "runs", (0,), "\"synthetic\\u005fkey\"", "synthetic_key")

    def test_escaped_key_runs_unicode_end(self):
        self._assert_valid_escaped_key_has_review_parity(
            "runs", (0,), "\"synthetic_ke\\u0079\"", "synthetic_key")

    def test_escaped_key_runs_escaped_solidus(self):
        self._assert_valid_escaped_key_has_review_parity(
            "runs", (0,), "\"synthetic\\/key\"", "synthetic/key")

    def test_escaped_key_runs_escaped_quote(self):
        self._assert_valid_escaped_key_has_review_parity(
            "runs", (0,), "\"synthetic\\\"key\"", "synthetic\"key")

    def test_escaped_key_runs_escaped_backslash(self):
        self._assert_valid_escaped_key_has_review_parity(
            "runs", (0,), "\"synthetic\\\\key\"", "synthetic\\key")

    def test_escaped_key_runs_escaped_surrogate_pair(self):
        self._assert_valid_escaped_key_has_review_parity(
            "runs", (0,), "\"\\uD83D\\uDE00_synthetic\"", "😀_synthetic")

    def test_escaped_key_runs_escaped_newline(self):
        self._assert_valid_escaped_key_has_review_parity(
            "runs", (0,), "\"synthetic\\nkey\"", "synthetic\nkey")

    def test_escaped_key_comparison_files_unicode_head(self):
        self._assert_valid_escaped_key_has_review_parity(
            "compare", ("files", 0), "\"\\u0073ynthetic_key\"", "synthetic_key")

    def test_escaped_key_comparison_files_unicode_middle(self):
        self._assert_valid_escaped_key_has_review_parity(
            "compare", ("files", 0), "\"synthetic\\u005fkey\"", "synthetic_key")

    def test_escaped_key_comparison_files_unicode_end(self):
        self._assert_valid_escaped_key_has_review_parity(
            "compare", ("files", 0), "\"synthetic_ke\\u0079\"", "synthetic_key")

    def test_escaped_key_comparison_files_escaped_solidus(self):
        self._assert_valid_escaped_key_has_review_parity(
            "compare", ("files", 0), "\"synthetic\\/key\"", "synthetic/key")

    def test_escaped_key_comparison_files_escaped_quote(self):
        self._assert_valid_escaped_key_has_review_parity(
            "compare", ("files", 0), "\"synthetic\\\"key\"", "synthetic\"key")

    def test_escaped_key_comparison_files_escaped_backslash(self):
        self._assert_valid_escaped_key_has_review_parity(
            "compare", ("files", 0), "\"synthetic\\\\key\"", "synthetic\\key")

    def test_escaped_key_comparison_files_escaped_surrogate_pair(self):
        self._assert_valid_escaped_key_has_review_parity(
            "compare", ("files", 0), "\"\\uD83D\\uDE00_synthetic\"", "😀_synthetic")

    def test_escaped_key_comparison_files_escaped_newline(self):
        self._assert_valid_escaped_key_has_review_parity(
            "compare", ("files", 0), "\"synthetic\\nkey\"", "synthetic\nkey")

    def test_escaped_key_jobs_by_run_unicode_head(self):
        self._assert_valid_escaped_key_has_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"\\u0073ynthetic_key\"", "synthetic_key")

    def test_escaped_key_jobs_by_run_unicode_middle(self):
        self._assert_valid_escaped_key_has_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"synthetic\\u005fkey\"", "synthetic_key")

    def test_escaped_key_jobs_by_run_unicode_end(self):
        self._assert_valid_escaped_key_has_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"synthetic_ke\\u0079\"", "synthetic_key")

    def test_escaped_key_jobs_by_run_escaped_solidus(self):
        self._assert_valid_escaped_key_has_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"synthetic\\/key\"", "synthetic/key")

    def test_escaped_key_jobs_by_run_escaped_quote(self):
        self._assert_valid_escaped_key_has_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"synthetic\\\"key\"", "synthetic\"key")

    def test_escaped_key_jobs_by_run_escaped_backslash(self):
        self._assert_valid_escaped_key_has_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"synthetic\\\\key\"", "synthetic\\key")

    def test_escaped_key_jobs_by_run_escaped_surrogate_pair(self):
        self._assert_valid_escaped_key_has_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"\\uD83D\\uDE00_synthetic\"", "😀_synthetic")

    def test_escaped_key_jobs_by_run_escaped_newline(self):
        self._assert_valid_escaped_key_has_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"synthetic\\nkey\"", "synthetic\nkey")

    def test_escaped_key_phase3_scenarios_unicode_head(self):
        self._assert_valid_escaped_key_has_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"\\u0073ynthetic_key\"", "synthetic_key")

    def test_escaped_key_phase3_scenarios_unicode_middle(self):
        self._assert_valid_escaped_key_has_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"synthetic\\u005fkey\"", "synthetic_key")

    def test_escaped_key_phase3_scenarios_unicode_end(self):
        self._assert_valid_escaped_key_has_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"synthetic_ke\\u0079\"", "synthetic_key")

    def test_escaped_key_phase3_scenarios_escaped_solidus(self):
        self._assert_valid_escaped_key_has_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"synthetic\\/key\"", "synthetic/key")

    def test_escaped_key_phase3_scenarios_escaped_quote(self):
        self._assert_valid_escaped_key_has_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"synthetic\\\"key\"", "synthetic\"key")

    def test_escaped_key_phase3_scenarios_escaped_backslash(self):
        self._assert_valid_escaped_key_has_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"synthetic\\\\key\"", "synthetic\\key")

    def test_escaped_key_phase3_scenarios_escaped_surrogate_pair(self):
        self._assert_valid_escaped_key_has_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"\\uD83D\\uDE00_synthetic\"", "😀_synthetic")

    def test_escaped_key_phase3_scenarios_escaped_newline(self):
        self._assert_valid_escaped_key_has_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"synthetic\\nkey\"", "synthetic\nkey")

    def test_escaped_key_full_tree_entries_unicode_head(self):
        self._assert_valid_escaped_key_has_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"\\u0073ynthetic_key\"", "synthetic_key")

    def test_escaped_key_full_tree_entries_unicode_middle(self):
        self._assert_valid_escaped_key_has_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"synthetic\\u005fkey\"", "synthetic_key")

    def test_escaped_key_full_tree_entries_unicode_end(self):
        self._assert_valid_escaped_key_has_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"synthetic_ke\\u0079\"", "synthetic_key")

    def test_escaped_key_full_tree_entries_escaped_solidus(self):
        self._assert_valid_escaped_key_has_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"synthetic\\/key\"", "synthetic/key")

    def test_escaped_key_full_tree_entries_escaped_quote(self):
        self._assert_valid_escaped_key_has_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"synthetic\\\"key\"", "synthetic\"key")

    def test_escaped_key_full_tree_entries_escaped_backslash(self):
        self._assert_valid_escaped_key_has_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"synthetic\\\\key\"", "synthetic\\key")

    def test_escaped_key_full_tree_entries_escaped_surrogate_pair(self):
        self._assert_valid_escaped_key_has_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"\\uD83D\\uDE00_synthetic\"", "😀_synthetic")

    def test_escaped_key_full_tree_entries_escaped_newline(self):
        self._assert_valid_escaped_key_has_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"synthetic\\nkey\"", "synthetic\nkey")

    def test_escaped_key_merge_parents_unicode_head(self):
        self._assert_valid_escaped_key_has_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"\\u0073ynthetic_key\"", "synthetic_key")

    def test_escaped_key_merge_parents_unicode_middle(self):
        self._assert_valid_escaped_key_has_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"synthetic\\u005fkey\"", "synthetic_key")

    def test_escaped_key_merge_parents_unicode_end(self):
        self._assert_valid_escaped_key_has_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"synthetic_ke\\u0079\"", "synthetic_key")

    def test_escaped_key_merge_parents_escaped_solidus(self):
        self._assert_valid_escaped_key_has_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"synthetic\\/key\"", "synthetic/key")

    def test_escaped_key_merge_parents_escaped_quote(self):
        self._assert_valid_escaped_key_has_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"synthetic\\\"key\"", "synthetic\"key")

    def test_escaped_key_merge_parents_escaped_backslash(self):
        self._assert_valid_escaped_key_has_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"synthetic\\\\key\"", "synthetic\\key")

    def test_escaped_key_merge_parents_escaped_surrogate_pair(self):
        self._assert_valid_escaped_key_has_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"\\uD83D\\uDE00_synthetic\"", "😀_synthetic")

    def test_escaped_key_merge_parents_escaped_newline(self):
        self._assert_valid_escaped_key_has_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"synthetic\\nkey\"", "synthetic\nkey")

    def test_escaped_key_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
