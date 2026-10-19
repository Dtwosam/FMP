"""DEC-1697: malformed separators and brackets in required evidence arrays.

Strict JSON grammar, before category and source-review validation.
"""
import copy
import io
import json
import unittest

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli


class EvidenceArrayStructuralGrammarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_invalid_array_delimiter(self, category, path, bad_end):
        self.assertIn(category, source.REQUIRED)
        self.assertIn(bad_end, (
            '"DEC1697_ARRAY_MARKER"]',
            ',,"DEC1697_ARRAY_MARKER"]',
            ',"DEC1697_ARRAY_MARKER",]',
            ';"DEC1697_ARRAY_MARKER"]',
            ':"DEC1697_ARRAY_MARKER"]',
            ',"DEC1697_ARRAY_MARKER"',
            ',"DEC1697_ARRAY_MARKER"]]',
            ',/*invalid*/"DEC1697_ARRAY_MARKER"]'))
        before = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        target = copied[category]
        for part in path:
            target = target[part]
        self.assertIs(type(target), list)
        self.assertGreater(len(target), 0)
        target.append("DEC1697_ARRAY_MARKER")
        encoded = json.dumps(copied, sort_keys=True, separators=(",", ":"))
        end = ',"DEC1697_ARRAY_MARKER"]'
        self.assertEqual(encoded.count(end), 1)
        malformed = encoded.replace(end, bad_end, 1)
        with self.assertRaises(json.JSONDecodeError):
            json.loads(malformed)
        parsed = source.review_bundle_json_text(malformed)
        output = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(malformed), output)
        emitted = json.loads(output.getvalue())
        self.assertEqual(before, self.fixture._portable_top_level_members_json())
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(status, 2)
        self.assertEqual(parsed["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        self.assertEqual(emitted["diagnostics"],
                         ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        self.assertNotIn("DEC1697_ARRAY_MARKER", output.getvalue())
        self.assertNotIn("tests/sample.py", output.getvalue())
        self.assertNotIn("docs/sample.md", output.getvalue())
        for verdict in (parsed, emitted):
            self.assertFalse(verdict["source_consistency"])
            self.assertFalse(verdict["independent_original_os_proof"])
            self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(verdict["can_authorize_annual_run"])

    def test_invalid_array_delimiter_runs_missing_comma(self):
        self._assert_invalid_array_delimiter(
            "runs", (), "\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_runs_double_comma(self):
        self._assert_invalid_array_delimiter(
            "runs", (), ",,\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_runs_trailing_comma(self):
        self._assert_invalid_array_delimiter(
            "runs", (), ",\"DEC1697_ARRAY_MARKER\",]")

    def test_invalid_array_delimiter_runs_semicolon(self):
        self._assert_invalid_array_delimiter(
            "runs", (), ";\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_runs_colon(self):
        self._assert_invalid_array_delimiter(
            "runs", (), ":\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_runs_missing_closing_bracket(self):
        self._assert_invalid_array_delimiter(
            "runs", (), ",\"DEC1697_ARRAY_MARKER\"")

    def test_invalid_array_delimiter_runs_extra_closing_bracket(self):
        self._assert_invalid_array_delimiter(
            "runs", (), ",\"DEC1697_ARRAY_MARKER\"]]")

    def test_invalid_array_delimiter_runs_javascript_comment(self):
        self._assert_invalid_array_delimiter(
            "runs", (), ",/*invalid*/\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_jobs_missing_comma(self):
        self._assert_invalid_array_delimiter(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0],), "\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_jobs_double_comma(self):
        self._assert_invalid_array_delimiter(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0],), ",,\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_jobs_trailing_comma(self):
        self._assert_invalid_array_delimiter(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0],), ",\"DEC1697_ARRAY_MARKER\",]")

    def test_invalid_array_delimiter_jobs_semicolon(self):
        self._assert_invalid_array_delimiter(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0],), ";\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_jobs_colon(self):
        self._assert_invalid_array_delimiter(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0],), ":\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_jobs_missing_closing_bracket(self):
        self._assert_invalid_array_delimiter(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0],), ",\"DEC1697_ARRAY_MARKER\"")

    def test_invalid_array_delimiter_jobs_extra_closing_bracket(self):
        self._assert_invalid_array_delimiter(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0],), ",\"DEC1697_ARRAY_MARKER\"]]")

    def test_invalid_array_delimiter_jobs_javascript_comment(self):
        self._assert_invalid_array_delimiter(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0],), ",/*invalid*/\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_compare_files_missing_comma(self):
        self._assert_invalid_array_delimiter(
            "compare", ("files",), "\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_compare_files_double_comma(self):
        self._assert_invalid_array_delimiter(
            "compare", ("files",), ",,\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_compare_files_trailing_comma(self):
        self._assert_invalid_array_delimiter(
            "compare", ("files",), ",\"DEC1697_ARRAY_MARKER\",]")

    def test_invalid_array_delimiter_compare_files_semicolon(self):
        self._assert_invalid_array_delimiter(
            "compare", ("files",), ";\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_compare_files_colon(self):
        self._assert_invalid_array_delimiter(
            "compare", ("files",), ":\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_compare_files_missing_closing_bracket(self):
        self._assert_invalid_array_delimiter(
            "compare", ("files",), ",\"DEC1697_ARRAY_MARKER\"")

    def test_invalid_array_delimiter_compare_files_extra_closing_bracket(self):
        self._assert_invalid_array_delimiter(
            "compare", ("files",), ",\"DEC1697_ARRAY_MARKER\"]]")

    def test_invalid_array_delimiter_compare_files_javascript_comment(self):
        self._assert_invalid_array_delimiter(
            "compare", ("files",), ",/*invalid*/\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_phase3_scenarios_missing_comma(self):
        self._assert_invalid_array_delimiter(
            "phase3_evidence_snapshot", ("index", "scenarios"), "\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_phase3_scenarios_double_comma(self):
        self._assert_invalid_array_delimiter(
            "phase3_evidence_snapshot", ("index", "scenarios"), ",,\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_phase3_scenarios_trailing_comma(self):
        self._assert_invalid_array_delimiter(
            "phase3_evidence_snapshot", ("index", "scenarios"), ",\"DEC1697_ARRAY_MARKER\",]")

    def test_invalid_array_delimiter_phase3_scenarios_semicolon(self):
        self._assert_invalid_array_delimiter(
            "phase3_evidence_snapshot", ("index", "scenarios"), ";\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_phase3_scenarios_colon(self):
        self._assert_invalid_array_delimiter(
            "phase3_evidence_snapshot", ("index", "scenarios"), ":\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_phase3_scenarios_missing_closing_bracket(self):
        self._assert_invalid_array_delimiter(
            "phase3_evidence_snapshot", ("index", "scenarios"), ",\"DEC1697_ARRAY_MARKER\"")

    def test_invalid_array_delimiter_phase3_scenarios_extra_closing_bracket(self):
        self._assert_invalid_array_delimiter(
            "phase3_evidence_snapshot", ("index", "scenarios"), ",\"DEC1697_ARRAY_MARKER\"]]")

    def test_invalid_array_delimiter_phase3_scenarios_javascript_comment(self):
        self._assert_invalid_array_delimiter(
            "phase3_evidence_snapshot", ("index", "scenarios"), ",/*invalid*/\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_tree_entries_missing_comma(self):
        self._assert_invalid_array_delimiter(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree"), "\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_tree_entries_double_comma(self):
        self._assert_invalid_array_delimiter(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree"), ",,\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_tree_entries_trailing_comma(self):
        self._assert_invalid_array_delimiter(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree"), ",\"DEC1697_ARRAY_MARKER\",]")

    def test_invalid_array_delimiter_tree_entries_semicolon(self):
        self._assert_invalid_array_delimiter(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree"), ";\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_tree_entries_colon(self):
        self._assert_invalid_array_delimiter(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree"), ":\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_tree_entries_missing_closing_bracket(self):
        self._assert_invalid_array_delimiter(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree"), ",\"DEC1697_ARRAY_MARKER\"")

    def test_invalid_array_delimiter_tree_entries_extra_closing_bracket(self):
        self._assert_invalid_array_delimiter(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree"), ",\"DEC1697_ARRAY_MARKER\"]]")

    def test_invalid_array_delimiter_tree_entries_javascript_comment(self):
        self._assert_invalid_array_delimiter(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree"), ",/*invalid*/\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_merge_parents_missing_comma(self):
        self._assert_invalid_array_delimiter(
            "merge_checkout_snapshot", ("merge_commit", "parents"), "\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_merge_parents_double_comma(self):
        self._assert_invalid_array_delimiter(
            "merge_checkout_snapshot", ("merge_commit", "parents"), ",,\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_merge_parents_trailing_comma(self):
        self._assert_invalid_array_delimiter(
            "merge_checkout_snapshot", ("merge_commit", "parents"), ",\"DEC1697_ARRAY_MARKER\",]")

    def test_invalid_array_delimiter_merge_parents_semicolon(self):
        self._assert_invalid_array_delimiter(
            "merge_checkout_snapshot", ("merge_commit", "parents"), ";\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_merge_parents_colon(self):
        self._assert_invalid_array_delimiter(
            "merge_checkout_snapshot", ("merge_commit", "parents"), ":\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_merge_parents_missing_closing_bracket(self):
        self._assert_invalid_array_delimiter(
            "merge_checkout_snapshot", ("merge_commit", "parents"), ",\"DEC1697_ARRAY_MARKER\"")

    def test_invalid_array_delimiter_merge_parents_extra_closing_bracket(self):
        self._assert_invalid_array_delimiter(
            "merge_checkout_snapshot", ("merge_commit", "parents"), ",\"DEC1697_ARRAY_MARKER\"]]")

    def test_invalid_array_delimiter_merge_parents_javascript_comment(self):
        self._assert_invalid_array_delimiter(
            "merge_checkout_snapshot", ("merge_commit", "parents"), ",/*invalid*/\"DEC1697_ARRAY_MARKER\"]")

    def test_invalid_array_delimiter_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
