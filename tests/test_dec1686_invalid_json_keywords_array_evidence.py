"""DEC-1686: invalid JSON keywords inside array-contained evidence objects.

Synthetic offline test-only coverage; no protected-source access or annual authority.
"""
import copy
import io
import json
import unittest

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli

SENTINEL = "DEC1686_INVALID_JSON_KEYWORD_SENTINEL"


class ArrayEvidenceMalformedKeywordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_nested_keyword_grammar(self, category, path, token):
        self.assertIn(category, source.REQUIRED)
        self.assertIn(token, ("True", "FALSE", "Null", "None",
                              "undefined", "tru"))
        clean = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        cursor = copied[category]
        for part in path:
            cursor = cursor[part]
        self.assertIs(type(cursor), dict)
        cursor["synthetic_keyword"] = SENTINEL
        encoded = json.dumps(copied, separators=(",", ":"), sort_keys=True)
        quoted = json.dumps(SENTINEL)
        self.assertEqual(encoded.count(quoted), 1)
        malformed = encoded.replace(quoted, token, 1)
        with self.assertRaises(json.JSONDecodeError):
            json.loads(malformed)
        parsed = source.review_bundle_json_text(malformed)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(malformed), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(clean, self.fixture._portable_top_level_members_json())
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(status, 2)
        self.assertEqual(parsed["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        self.assertEqual(emitted["diagnostics"],
                         ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        self.assertNotIn(SENTINEL, out.getvalue())
        self.assertNotIn("tests/sample.py", out.getvalue())
        self.assertNotIn("docs/sample.md", out.getvalue())
        for result in (parsed, emitted):
            self.assertFalse(result["source_consistency"])
            self.assertFalse(result["independent_original_os_proof"])
            self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(result["can_authorize_annual_run"])

    def test_invalid_array_keyword_runs_capital_true(self):
        self._assert_nested_keyword_grammar(
            "runs", (0,), "True")

    def test_invalid_array_keyword_runs_uppercase_false(self):
        self._assert_nested_keyword_grammar(
            "runs", (0,), "FALSE")

    def test_invalid_array_keyword_runs_mixed_null(self):
        self._assert_nested_keyword_grammar(
            "runs", (0,), "Null")

    def test_invalid_array_keyword_runs_python_none(self):
        self._assert_nested_keyword_grammar(
            "runs", (0,), "None")

    def test_invalid_array_keyword_runs_undefined(self):
        self._assert_nested_keyword_grammar(
            "runs", (0,), "undefined")

    def test_invalid_array_keyword_runs_truncated_true(self):
        self._assert_nested_keyword_grammar(
            "runs", (0,), "tru")

    def test_invalid_array_keyword_comparison_files_capital_true(self):
        self._assert_nested_keyword_grammar(
            "compare", ("files", 0), "True")

    def test_invalid_array_keyword_comparison_files_uppercase_false(self):
        self._assert_nested_keyword_grammar(
            "compare", ("files", 0), "FALSE")

    def test_invalid_array_keyword_comparison_files_mixed_null(self):
        self._assert_nested_keyword_grammar(
            "compare", ("files", 0), "Null")

    def test_invalid_array_keyword_comparison_files_python_none(self):
        self._assert_nested_keyword_grammar(
            "compare", ("files", 0), "None")

    def test_invalid_array_keyword_comparison_files_undefined(self):
        self._assert_nested_keyword_grammar(
            "compare", ("files", 0), "undefined")

    def test_invalid_array_keyword_comparison_files_truncated_true(self):
        self._assert_nested_keyword_grammar(
            "compare", ("files", 0), "tru")

    def test_invalid_array_keyword_jobs_by_run_capital_true(self):
        self._assert_nested_keyword_grammar(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "True")

    def test_invalid_array_keyword_jobs_by_run_uppercase_false(self):
        self._assert_nested_keyword_grammar(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "FALSE")

    def test_invalid_array_keyword_jobs_by_run_mixed_null(self):
        self._assert_nested_keyword_grammar(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "Null")

    def test_invalid_array_keyword_jobs_by_run_python_none(self):
        self._assert_nested_keyword_grammar(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "None")

    def test_invalid_array_keyword_jobs_by_run_undefined(self):
        self._assert_nested_keyword_grammar(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "undefined")

    def test_invalid_array_keyword_jobs_by_run_truncated_true(self):
        self._assert_nested_keyword_grammar(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "tru")

    def test_invalid_array_keyword_phase3_scenarios_capital_true(self):
        self._assert_nested_keyword_grammar(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "True")

    def test_invalid_array_keyword_phase3_scenarios_uppercase_false(self):
        self._assert_nested_keyword_grammar(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "FALSE")

    def test_invalid_array_keyword_phase3_scenarios_mixed_null(self):
        self._assert_nested_keyword_grammar(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "Null")

    def test_invalid_array_keyword_phase3_scenarios_python_none(self):
        self._assert_nested_keyword_grammar(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "None")

    def test_invalid_array_keyword_phase3_scenarios_undefined(self):
        self._assert_nested_keyword_grammar(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "undefined")

    def test_invalid_array_keyword_phase3_scenarios_truncated_true(self):
        self._assert_nested_keyword_grammar(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "tru")

    def test_invalid_array_keyword_full_tree_entries_capital_true(self):
        self._assert_nested_keyword_grammar(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "True")

    def test_invalid_array_keyword_full_tree_entries_uppercase_false(self):
        self._assert_nested_keyword_grammar(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "FALSE")

    def test_invalid_array_keyword_full_tree_entries_mixed_null(self):
        self._assert_nested_keyword_grammar(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "Null")

    def test_invalid_array_keyword_full_tree_entries_python_none(self):
        self._assert_nested_keyword_grammar(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "None")

    def test_invalid_array_keyword_full_tree_entries_undefined(self):
        self._assert_nested_keyword_grammar(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "undefined")

    def test_invalid_array_keyword_full_tree_entries_truncated_true(self):
        self._assert_nested_keyword_grammar(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "tru")

    def test_invalid_array_keyword_merge_parents_capital_true(self):
        self._assert_nested_keyword_grammar(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "True")

    def test_invalid_array_keyword_merge_parents_uppercase_false(self):
        self._assert_nested_keyword_grammar(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "FALSE")

    def test_invalid_array_keyword_merge_parents_mixed_null(self):
        self._assert_nested_keyword_grammar(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "Null")

    def test_invalid_array_keyword_merge_parents_python_none(self):
        self._assert_nested_keyword_grammar(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "None")

    def test_invalid_array_keyword_merge_parents_undefined(self):
        self._assert_nested_keyword_grammar(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "undefined")

    def test_invalid_array_keyword_merge_parents_truncated_true(self):
        self._assert_nested_keyword_grammar(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "tru")

    def test_invalid_array_keyword_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
