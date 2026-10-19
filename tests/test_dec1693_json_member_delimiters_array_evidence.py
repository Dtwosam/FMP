"""DEC-1693: JSON member delimiter grammar inside array-contained evidence.

Offline and synthetic only; invalid token ingress must refuse before review.
"""
import copy
import io
import json
import unittest

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli


class NestedJsonMemberDelimiterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_invalid_member_delimiter(self, category, path, bad_fragment):
        self.assertIn(category, source.REQUIRED)
        self.assertIn(bad_fragment, (
            ',"zz_dec1693_member"true',
            ',"zz_dec1693_member"=true',
            ',"zz_dec1693_member"::true',
            ',,"zz_dec1693_member":true',
            '"zz_dec1693_member":true',
            ';"zz_dec1693_member":true',
            ',"zz_dec1693_member":true,',
            ',:"zz_dec1693_member":true'))
        before = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        target = copied[category]
        for key in path:
            target = target[key]
        self.assertIs(type(target), dict)
        self.assertNotIn("zz_dec1693_member", target)
        target["zz_dec1693_member"] = True
        encoded = json.dumps(copied, sort_keys=True, separators=(",", ":"))
        fragment = ',"zz_dec1693_member":true'
        self.assertEqual(encoded.count(fragment), 1)
        self.assertEqual(encoded[encoded.index(fragment) + len(fragment)], "}")
        bad = encoded.replace(fragment, bad_fragment, 1)
        with self.assertRaises(json.JSONDecodeError):
            json.loads(bad)
        parsed = source.review_bundle_json_text(bad)
        out = io.StringIO()
        rc = cli.run_stdin_review(io.StringIO(bad), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(before, self.fixture._portable_top_level_members_json())
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(rc, 2)
        self.assertEqual(parsed["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        self.assertEqual(emitted["diagnostics"],
                         ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        self.assertNotIn("zz_dec1693_member", out.getvalue())
        self.assertNotIn("tests/sample.py", out.getvalue())
        self.assertNotIn("docs/sample.md", out.getvalue())
        for verdict in (parsed, emitted):
            self.assertFalse(verdict["source_consistency"])
            self.assertFalse(verdict["independent_original_os_proof"])
            self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(verdict["can_authorize_annual_run"])

    def test_invalid_delimiter_runs_missing_colon(self):
        self._assert_invalid_member_delimiter(
            "runs", (0,), ",\"zz_dec1693_member\"true")

    def test_invalid_delimiter_runs_equals_separator(self):
        self._assert_invalid_member_delimiter(
            "runs", (0,), ",\"zz_dec1693_member\"=true")

    def test_invalid_delimiter_runs_double_colon(self):
        self._assert_invalid_member_delimiter(
            "runs", (0,), ",\"zz_dec1693_member\"::true")

    def test_invalid_delimiter_runs_duplicate_comma(self):
        self._assert_invalid_member_delimiter(
            "runs", (0,), ",,\"zz_dec1693_member\":true")

    def test_invalid_delimiter_runs_missing_comma(self):
        self._assert_invalid_member_delimiter(
            "runs", (0,), "\"zz_dec1693_member\":true")

    def test_invalid_delimiter_runs_semicolon_separator(self):
        self._assert_invalid_member_delimiter(
            "runs", (0,), ";\"zz_dec1693_member\":true")

    def test_invalid_delimiter_runs_trailing_comma(self):
        self._assert_invalid_member_delimiter(
            "runs", (0,), ",\"zz_dec1693_member\":true,")

    def test_invalid_delimiter_runs_colon_before_key(self):
        self._assert_invalid_member_delimiter(
            "runs", (0,), ",:\"zz_dec1693_member\":true")

    def test_invalid_delimiter_compare_files_missing_colon(self):
        self._assert_invalid_member_delimiter(
            "compare", ("files", 0), ",\"zz_dec1693_member\"true")

    def test_invalid_delimiter_compare_files_equals_separator(self):
        self._assert_invalid_member_delimiter(
            "compare", ("files", 0), ",\"zz_dec1693_member\"=true")

    def test_invalid_delimiter_compare_files_double_colon(self):
        self._assert_invalid_member_delimiter(
            "compare", ("files", 0), ",\"zz_dec1693_member\"::true")

    def test_invalid_delimiter_compare_files_duplicate_comma(self):
        self._assert_invalid_member_delimiter(
            "compare", ("files", 0), ",,\"zz_dec1693_member\":true")

    def test_invalid_delimiter_compare_files_missing_comma(self):
        self._assert_invalid_member_delimiter(
            "compare", ("files", 0), "\"zz_dec1693_member\":true")

    def test_invalid_delimiter_compare_files_semicolon_separator(self):
        self._assert_invalid_member_delimiter(
            "compare", ("files", 0), ";\"zz_dec1693_member\":true")

    def test_invalid_delimiter_compare_files_trailing_comma(self):
        self._assert_invalid_member_delimiter(
            "compare", ("files", 0), ",\"zz_dec1693_member\":true,")

    def test_invalid_delimiter_compare_files_colon_before_key(self):
        self._assert_invalid_member_delimiter(
            "compare", ("files", 0), ",:\"zz_dec1693_member\":true")

    def test_invalid_delimiter_jobs_missing_colon(self):
        self._assert_invalid_member_delimiter(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), ",\"zz_dec1693_member\"true")

    def test_invalid_delimiter_jobs_equals_separator(self):
        self._assert_invalid_member_delimiter(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), ",\"zz_dec1693_member\"=true")

    def test_invalid_delimiter_jobs_double_colon(self):
        self._assert_invalid_member_delimiter(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), ",\"zz_dec1693_member\"::true")

    def test_invalid_delimiter_jobs_duplicate_comma(self):
        self._assert_invalid_member_delimiter(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), ",,\"zz_dec1693_member\":true")

    def test_invalid_delimiter_jobs_missing_comma(self):
        self._assert_invalid_member_delimiter(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "\"zz_dec1693_member\":true")

    def test_invalid_delimiter_jobs_semicolon_separator(self):
        self._assert_invalid_member_delimiter(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), ";\"zz_dec1693_member\":true")

    def test_invalid_delimiter_jobs_trailing_comma(self):
        self._assert_invalid_member_delimiter(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), ",\"zz_dec1693_member\":true,")

    def test_invalid_delimiter_jobs_colon_before_key(self):
        self._assert_invalid_member_delimiter(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), ",:\"zz_dec1693_member\":true")

    def test_invalid_delimiter_phase3_scenarios_missing_colon(self):
        self._assert_invalid_member_delimiter(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), ",\"zz_dec1693_member\"true")

    def test_invalid_delimiter_phase3_scenarios_equals_separator(self):
        self._assert_invalid_member_delimiter(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), ",\"zz_dec1693_member\"=true")

    def test_invalid_delimiter_phase3_scenarios_double_colon(self):
        self._assert_invalid_member_delimiter(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), ",\"zz_dec1693_member\"::true")

    def test_invalid_delimiter_phase3_scenarios_duplicate_comma(self):
        self._assert_invalid_member_delimiter(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), ",,\"zz_dec1693_member\":true")

    def test_invalid_delimiter_phase3_scenarios_missing_comma(self):
        self._assert_invalid_member_delimiter(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "\"zz_dec1693_member\":true")

    def test_invalid_delimiter_phase3_scenarios_semicolon_separator(self):
        self._assert_invalid_member_delimiter(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), ";\"zz_dec1693_member\":true")

    def test_invalid_delimiter_phase3_scenarios_trailing_comma(self):
        self._assert_invalid_member_delimiter(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), ",\"zz_dec1693_member\":true,")

    def test_invalid_delimiter_phase3_scenarios_colon_before_key(self):
        self._assert_invalid_member_delimiter(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), ",:\"zz_dec1693_member\":true")

    def test_invalid_delimiter_full_tree_entries_missing_colon(self):
        self._assert_invalid_member_delimiter(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), ",\"zz_dec1693_member\"true")

    def test_invalid_delimiter_full_tree_entries_equals_separator(self):
        self._assert_invalid_member_delimiter(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), ",\"zz_dec1693_member\"=true")

    def test_invalid_delimiter_full_tree_entries_double_colon(self):
        self._assert_invalid_member_delimiter(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), ",\"zz_dec1693_member\"::true")

    def test_invalid_delimiter_full_tree_entries_duplicate_comma(self):
        self._assert_invalid_member_delimiter(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), ",,\"zz_dec1693_member\":true")

    def test_invalid_delimiter_full_tree_entries_missing_comma(self):
        self._assert_invalid_member_delimiter(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "\"zz_dec1693_member\":true")

    def test_invalid_delimiter_full_tree_entries_semicolon_separator(self):
        self._assert_invalid_member_delimiter(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), ";\"zz_dec1693_member\":true")

    def test_invalid_delimiter_full_tree_entries_trailing_comma(self):
        self._assert_invalid_member_delimiter(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), ",\"zz_dec1693_member\":true,")

    def test_invalid_delimiter_full_tree_entries_colon_before_key(self):
        self._assert_invalid_member_delimiter(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), ",:\"zz_dec1693_member\":true")

    def test_invalid_delimiter_merge_parents_missing_colon(self):
        self._assert_invalid_member_delimiter(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), ",\"zz_dec1693_member\"true")

    def test_invalid_delimiter_merge_parents_equals_separator(self):
        self._assert_invalid_member_delimiter(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), ",\"zz_dec1693_member\"=true")

    def test_invalid_delimiter_merge_parents_double_colon(self):
        self._assert_invalid_member_delimiter(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), ",\"zz_dec1693_member\"::true")

    def test_invalid_delimiter_merge_parents_duplicate_comma(self):
        self._assert_invalid_member_delimiter(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), ",,\"zz_dec1693_member\":true")

    def test_invalid_delimiter_merge_parents_missing_comma(self):
        self._assert_invalid_member_delimiter(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "\"zz_dec1693_member\":true")

    def test_invalid_delimiter_merge_parents_semicolon_separator(self):
        self._assert_invalid_member_delimiter(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), ";\"zz_dec1693_member\":true")

    def test_invalid_delimiter_merge_parents_trailing_comma(self):
        self._assert_invalid_member_delimiter(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), ",\"zz_dec1693_member\":true,")

    def test_invalid_delimiter_merge_parents_colon_before_key(self):
        self._assert_invalid_member_delimiter(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), ",:\"zz_dec1693_member\":true")

    def test_invalid_delimiter_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
