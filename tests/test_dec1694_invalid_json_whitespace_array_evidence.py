"""DEC-1694: non-JSON whitespace between nested object tokens.

Only four ASCII whitespace characters are legal between JSON tokens.
"""
import copy
import io
import json
import unittest

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli


class NestedNonJsonWhitespaceRefusalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_invalid_whitespace_refused(self, category, path, separator):
        self.assertIn(category, source.REQUIRED)
        self.assertIn(separator, (
            "\v", "\f", "\x00", "\u00a0",
            "\u2003", "\u2028", "\u2029", "\ufeff"))
        clean = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        node = copied[category]
        for segment in path:
            node = node[segment]
        self.assertIs(type(node), dict)
        node["zz_dec1694_member"] = True
        encoded = json.dumps(copied, separators=(",", ":"), sort_keys=True)
        needle = '"zz_dec1694_member":true'
        self.assertEqual(encoded.count(needle), 1)
        malformed = encoded.replace(needle,
                                    '"zz_dec1694_member":' + separator + 'true',
                                    1)
        with self.assertRaises(json.JSONDecodeError):
            json.loads(malformed)
        parsed = source.review_bundle_json_text(malformed)
        output = io.StringIO()
        rc = cli.run_stdin_review(io.StringIO(malformed), output)
        emitted = json.loads(output.getvalue())
        self.assertEqual(clean, self.fixture._portable_top_level_members_json())
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(rc, 2)
        self.assertEqual(parsed["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        self.assertEqual(emitted["diagnostics"],
                         ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        self.assertNotIn("zz_dec1694_member", output.getvalue())
        self.assertNotIn("tests/sample.py", output.getvalue())
        self.assertNotIn("docs/sample.md", output.getvalue())
        for verdict in (parsed, emitted):
            self.assertFalse(verdict["source_consistency"])
            self.assertFalse(verdict["independent_original_os_proof"])
            self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(verdict["can_authorize_annual_run"])

    def test_invalid_whitespace_runs_vertical_tab(self):
        self._assert_invalid_whitespace_refused(
            "runs", (0,), "\u000b")

    def test_invalid_whitespace_runs_form_feed(self):
        self._assert_invalid_whitespace_refused(
            "runs", (0,), "\f")

    def test_invalid_whitespace_runs_nul(self):
        self._assert_invalid_whitespace_refused(
            "runs", (0,), "\u0000")

    def test_invalid_whitespace_runs_no_break_space(self):
        self._assert_invalid_whitespace_refused(
            "runs", (0,), " ")

    def test_invalid_whitespace_runs_em_space(self):
        self._assert_invalid_whitespace_refused(
            "runs", (0,), " ")

    def test_invalid_whitespace_runs_line_separator(self):
        self._assert_invalid_whitespace_refused(
            "runs", (0,), " ")

    def test_invalid_whitespace_runs_paragraph_separator(self):
        self._assert_invalid_whitespace_refused(
            "runs", (0,), " ")

    def test_invalid_whitespace_runs_byte_order_mark(self):
        self._assert_invalid_whitespace_refused(
            "runs", (0,), "﻿")

    def test_invalid_whitespace_compare_files_vertical_tab(self):
        self._assert_invalid_whitespace_refused(
            "compare", ("files", 0), "\u000b")

    def test_invalid_whitespace_compare_files_form_feed(self):
        self._assert_invalid_whitespace_refused(
            "compare", ("files", 0), "\f")

    def test_invalid_whitespace_compare_files_nul(self):
        self._assert_invalid_whitespace_refused(
            "compare", ("files", 0), "\u0000")

    def test_invalid_whitespace_compare_files_no_break_space(self):
        self._assert_invalid_whitespace_refused(
            "compare", ("files", 0), " ")

    def test_invalid_whitespace_compare_files_em_space(self):
        self._assert_invalid_whitespace_refused(
            "compare", ("files", 0), " ")

    def test_invalid_whitespace_compare_files_line_separator(self):
        self._assert_invalid_whitespace_refused(
            "compare", ("files", 0), " ")

    def test_invalid_whitespace_compare_files_paragraph_separator(self):
        self._assert_invalid_whitespace_refused(
            "compare", ("files", 0), " ")

    def test_invalid_whitespace_compare_files_byte_order_mark(self):
        self._assert_invalid_whitespace_refused(
            "compare", ("files", 0), "﻿")

    def test_invalid_whitespace_jobs_vertical_tab(self):
        self._assert_invalid_whitespace_refused(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\u000b")

    def test_invalid_whitespace_jobs_form_feed(self):
        self._assert_invalid_whitespace_refused(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\f")

    def test_invalid_whitespace_jobs_nul(self):
        self._assert_invalid_whitespace_refused(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\u0000")

    def test_invalid_whitespace_jobs_no_break_space(self):
        self._assert_invalid_whitespace_refused(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), " ")

    def test_invalid_whitespace_jobs_em_space(self):
        self._assert_invalid_whitespace_refused(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), " ")

    def test_invalid_whitespace_jobs_line_separator(self):
        self._assert_invalid_whitespace_refused(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), " ")

    def test_invalid_whitespace_jobs_paragraph_separator(self):
        self._assert_invalid_whitespace_refused(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), " ")

    def test_invalid_whitespace_jobs_byte_order_mark(self):
        self._assert_invalid_whitespace_refused(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "﻿")

    def test_invalid_whitespace_phase3_scenarios_vertical_tab(self):
        self._assert_invalid_whitespace_refused(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\u000b")

    def test_invalid_whitespace_phase3_scenarios_form_feed(self):
        self._assert_invalid_whitespace_refused(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\f")

    def test_invalid_whitespace_phase3_scenarios_nul(self):
        self._assert_invalid_whitespace_refused(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\u0000")

    def test_invalid_whitespace_phase3_scenarios_no_break_space(self):
        self._assert_invalid_whitespace_refused(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), " ")

    def test_invalid_whitespace_phase3_scenarios_em_space(self):
        self._assert_invalid_whitespace_refused(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), " ")

    def test_invalid_whitespace_phase3_scenarios_line_separator(self):
        self._assert_invalid_whitespace_refused(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), " ")

    def test_invalid_whitespace_phase3_scenarios_paragraph_separator(self):
        self._assert_invalid_whitespace_refused(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), " ")

    def test_invalid_whitespace_phase3_scenarios_byte_order_mark(self):
        self._assert_invalid_whitespace_refused(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "﻿")

    def test_invalid_whitespace_full_tree_entries_vertical_tab(self):
        self._assert_invalid_whitespace_refused(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\u000b")

    def test_invalid_whitespace_full_tree_entries_form_feed(self):
        self._assert_invalid_whitespace_refused(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\f")

    def test_invalid_whitespace_full_tree_entries_nul(self):
        self._assert_invalid_whitespace_refused(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\u0000")

    def test_invalid_whitespace_full_tree_entries_no_break_space(self):
        self._assert_invalid_whitespace_refused(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), " ")

    def test_invalid_whitespace_full_tree_entries_em_space(self):
        self._assert_invalid_whitespace_refused(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), " ")

    def test_invalid_whitespace_full_tree_entries_line_separator(self):
        self._assert_invalid_whitespace_refused(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), " ")

    def test_invalid_whitespace_full_tree_entries_paragraph_separator(self):
        self._assert_invalid_whitespace_refused(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), " ")

    def test_invalid_whitespace_full_tree_entries_byte_order_mark(self):
        self._assert_invalid_whitespace_refused(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "﻿")

    def test_invalid_whitespace_merge_parents_vertical_tab(self):
        self._assert_invalid_whitespace_refused(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\u000b")

    def test_invalid_whitespace_merge_parents_form_feed(self):
        self._assert_invalid_whitespace_refused(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\f")

    def test_invalid_whitespace_merge_parents_nul(self):
        self._assert_invalid_whitespace_refused(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\u0000")

    def test_invalid_whitespace_merge_parents_no_break_space(self):
        self._assert_invalid_whitespace_refused(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), " ")

    def test_invalid_whitespace_merge_parents_em_space(self):
        self._assert_invalid_whitespace_refused(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), " ")

    def test_invalid_whitespace_merge_parents_line_separator(self):
        self._assert_invalid_whitespace_refused(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), " ")

    def test_invalid_whitespace_merge_parents_paragraph_separator(self):
        self._assert_invalid_whitespace_refused(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), " ")

    def test_invalid_whitespace_merge_parents_byte_order_mark(self):
        self._assert_invalid_whitespace_refused(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "﻿")

    def test_invalid_whitespace_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
