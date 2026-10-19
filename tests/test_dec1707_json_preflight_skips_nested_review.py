"""DEC-1707: malformed JSON ingress cannot invoke nested evidence review.

All fixtures are synthetic. No protected artifacts or workflow dispatch.
"""
import copy
import io
import json
import unittest
from unittest import mock

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli


class InvalidJsonPreflightSkipsNestedReviewerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_invalid_json_skips_nested_review(self, category, path, token):
        self.assertIn(category, source.REQUIRED)
        self.assertIn(token, ("True", "01", "1e", "+1", "NaN", "Infinity"))
        before = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        target = copied[category]
        for part in path:
            target = target[part]
        self.assertIs(type(target), dict)
        target["zz_dec1707_bad"] = "DEC1707_UNREVIEWED_MARKER"
        encoded = json.dumps(copied, sort_keys=True, separators=(",", ":"))
        placeholder = '"zz_dec1707_bad":"DEC1707_UNREVIEWED_MARKER"'
        self.assertEqual(encoded.count(placeholder), 1)
        invalid = encoded.replace(placeholder, '"zz_dec1707_bad":' + token, 1)
        with mock.patch.object(
            source.composite, "review_stacked_draft_evidence",
            side_effect=AssertionError("NESTED_REVIEW_MUST_NOT_RUN"),
        ) as nested:
            parsed = source.review_bundle_json_text(invalid)
            out = io.StringIO()
            status = cli.run_stdin_review(io.StringIO(invalid), out)
            nested.assert_not_called()
        emitted = json.loads(out.getvalue())
        self.assertEqual(before, self.fixture._portable_top_level_members_json())
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(status, 2)
        self.assertEqual(parsed["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        self.assertEqual(emitted["diagnostics"],
                         ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        self.assertNotIn("DEC1707_UNREVIEWED_MARKER", out.getvalue())
        self.assertNotIn("NESTED_REVIEW_MUST_NOT_RUN", out.getvalue())
        self.assertNotIn("tests/sample.py", out.getvalue())
        self.assertNotIn("docs/sample.md", out.getvalue())
        for result in (parsed, emitted):
            self.assertFalse(result["source_consistency"])
            self.assertFalse(result["independent_original_os_proof"])
            self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(result["can_authorize_annual_run"])

    def test_grammar_preflight_runs_capital_boolean(self):
        self._assert_invalid_json_skips_nested_review(
            "runs", (0,), "True")

    def test_grammar_preflight_runs_leading_zero(self):
        self._assert_invalid_json_skips_nested_review(
            "runs", (0,), "01")

    def test_grammar_preflight_runs_incomplete_exponent(self):
        self._assert_invalid_json_skips_nested_review(
            "runs", (0,), "1e")

    def test_grammar_preflight_runs_plus_sign(self):
        self._assert_invalid_json_skips_nested_review(
            "runs", (0,), "+1")

    def test_grammar_preflight_runs_nan_constant(self):
        self._assert_invalid_json_skips_nested_review(
            "runs", (0,), "NaN")

    def test_grammar_preflight_runs_infinity_constant(self):
        self._assert_invalid_json_skips_nested_review(
            "runs", (0,), "Infinity")

    def test_grammar_preflight_compare_files_capital_boolean(self):
        self._assert_invalid_json_skips_nested_review(
            "compare", ("files", 0), "True")

    def test_grammar_preflight_compare_files_leading_zero(self):
        self._assert_invalid_json_skips_nested_review(
            "compare", ("files", 0), "01")

    def test_grammar_preflight_compare_files_incomplete_exponent(self):
        self._assert_invalid_json_skips_nested_review(
            "compare", ("files", 0), "1e")

    def test_grammar_preflight_compare_files_plus_sign(self):
        self._assert_invalid_json_skips_nested_review(
            "compare", ("files", 0), "+1")

    def test_grammar_preflight_compare_files_nan_constant(self):
        self._assert_invalid_json_skips_nested_review(
            "compare", ("files", 0), "NaN")

    def test_grammar_preflight_compare_files_infinity_constant(self):
        self._assert_invalid_json_skips_nested_review(
            "compare", ("files", 0), "Infinity")

    def test_grammar_preflight_jobs_capital_boolean(self):
        self._assert_invalid_json_skips_nested_review(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "True")

    def test_grammar_preflight_jobs_leading_zero(self):
        self._assert_invalid_json_skips_nested_review(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "01")

    def test_grammar_preflight_jobs_incomplete_exponent(self):
        self._assert_invalid_json_skips_nested_review(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "1e")

    def test_grammar_preflight_jobs_plus_sign(self):
        self._assert_invalid_json_skips_nested_review(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "+1")

    def test_grammar_preflight_jobs_nan_constant(self):
        self._assert_invalid_json_skips_nested_review(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "NaN")

    def test_grammar_preflight_jobs_infinity_constant(self):
        self._assert_invalid_json_skips_nested_review(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "Infinity")

    def test_grammar_preflight_phase3_scenarios_capital_boolean(self):
        self._assert_invalid_json_skips_nested_review(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "True")

    def test_grammar_preflight_phase3_scenarios_leading_zero(self):
        self._assert_invalid_json_skips_nested_review(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "01")

    def test_grammar_preflight_phase3_scenarios_incomplete_exponent(self):
        self._assert_invalid_json_skips_nested_review(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "1e")

    def test_grammar_preflight_phase3_scenarios_plus_sign(self):
        self._assert_invalid_json_skips_nested_review(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "+1")

    def test_grammar_preflight_phase3_scenarios_nan_constant(self):
        self._assert_invalid_json_skips_nested_review(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "NaN")

    def test_grammar_preflight_phase3_scenarios_infinity_constant(self):
        self._assert_invalid_json_skips_nested_review(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "Infinity")

    def test_grammar_preflight_full_tree_entries_capital_boolean(self):
        self._assert_invalid_json_skips_nested_review(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "True")

    def test_grammar_preflight_full_tree_entries_leading_zero(self):
        self._assert_invalid_json_skips_nested_review(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "01")

    def test_grammar_preflight_full_tree_entries_incomplete_exponent(self):
        self._assert_invalid_json_skips_nested_review(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "1e")

    def test_grammar_preflight_full_tree_entries_plus_sign(self):
        self._assert_invalid_json_skips_nested_review(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "+1")

    def test_grammar_preflight_full_tree_entries_nan_constant(self):
        self._assert_invalid_json_skips_nested_review(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "NaN")

    def test_grammar_preflight_full_tree_entries_infinity_constant(self):
        self._assert_invalid_json_skips_nested_review(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "Infinity")

    def test_grammar_preflight_merge_parents_capital_boolean(self):
        self._assert_invalid_json_skips_nested_review(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "True")

    def test_grammar_preflight_merge_parents_leading_zero(self):
        self._assert_invalid_json_skips_nested_review(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "01")

    def test_grammar_preflight_merge_parents_incomplete_exponent(self):
        self._assert_invalid_json_skips_nested_review(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "1e")

    def test_grammar_preflight_merge_parents_plus_sign(self):
        self._assert_invalid_json_skips_nested_review(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "+1")

    def test_grammar_preflight_merge_parents_nan_constant(self):
        self._assert_invalid_json_skips_nested_review(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "NaN")

    def test_grammar_preflight_merge_parents_infinity_constant(self):
        self._assert_invalid_json_skips_nested_review(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "Infinity")

    def test_grammar_preflight_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
