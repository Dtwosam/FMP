"""DEC-1695: nonfinite and overflowing numeric JSON inside evidence arrays.

Synthetic offline evidence only, without remote action or annual authority.
"""
import copy
import io
import json
import unittest

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli


class ArrayEvidenceNonfiniteTokenRefusalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_nonfinite_grammar_refusal(self, category, path, number_token):
        self.assertIn(category, source.REQUIRED)
        self.assertIn(number_token, (
            "NaN", "Infinity", "-Infinity", "+Infinity", "1e309",
            "-1e309", "9e999", "-9e999"))
        before = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        target = copied[category]
        for part in path:
            target = target[part]
        self.assertIs(type(target), dict)
        target["zz_dec1695_number"] = "DEC1695_NUMBER_MARKER"
        encoded = json.dumps(copied, sort_keys=True, separators=(",", ":"))
        needle = '"zz_dec1695_number":"DEC1695_NUMBER_MARKER"'
        self.assertEqual(encoded.count(needle), 1)
        corrupted = encoded.replace(needle,
                                    '"zz_dec1695_number":' + number_token, 1)
        with self.assertRaises(ValueError):
            json.loads(corrupted, parse_constant=source._no_nonfinite,
                       parse_float=source._finite_json_float)
        parsed = source.review_bundle_json_text(corrupted)
        out = io.StringIO()
        rc = cli.run_stdin_review(io.StringIO(corrupted), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(before, self.fixture._portable_top_level_members_json())
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(rc, 2)
        self.assertEqual(parsed["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        self.assertEqual(emitted["diagnostics"],
                         ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        self.assertNotIn("DEC1695_NUMBER_MARKER", out.getvalue())
        self.assertNotIn("tests/sample.py", out.getvalue())
        self.assertNotIn("docs/sample.md", out.getvalue())
        for verdict in (parsed, emitted):
            self.assertFalse(verdict["source_consistency"])
            self.assertFalse(verdict["independent_original_os_proof"])
            self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(verdict["can_authorize_annual_run"])

    def test_nonfinite_runs_nan(self):
        self._assert_nonfinite_grammar_refusal(
            "runs", (0,), "NaN")

    def test_nonfinite_runs_positive_infinity(self):
        self._assert_nonfinite_grammar_refusal(
            "runs", (0,), "Infinity")

    def test_nonfinite_runs_negative_infinity(self):
        self._assert_nonfinite_grammar_refusal(
            "runs", (0,), "-Infinity")

    def test_nonfinite_runs_plus_infinity(self):
        self._assert_nonfinite_grammar_refusal(
            "runs", (0,), "+Infinity")

    def test_nonfinite_runs_overflow_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "runs", (0,), "1e309")

    def test_nonfinite_runs_negative_overflow_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "runs", (0,), "-1e309")

    def test_nonfinite_runs_huge_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "runs", (0,), "9e999")

    def test_nonfinite_runs_negative_huge_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "runs", (0,), "-9e999")

    def test_nonfinite_compare_files_nan(self):
        self._assert_nonfinite_grammar_refusal(
            "compare", ("files", 0), "NaN")

    def test_nonfinite_compare_files_positive_infinity(self):
        self._assert_nonfinite_grammar_refusal(
            "compare", ("files", 0), "Infinity")

    def test_nonfinite_compare_files_negative_infinity(self):
        self._assert_nonfinite_grammar_refusal(
            "compare", ("files", 0), "-Infinity")

    def test_nonfinite_compare_files_plus_infinity(self):
        self._assert_nonfinite_grammar_refusal(
            "compare", ("files", 0), "+Infinity")

    def test_nonfinite_compare_files_overflow_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "compare", ("files", 0), "1e309")

    def test_nonfinite_compare_files_negative_overflow_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "compare", ("files", 0), "-1e309")

    def test_nonfinite_compare_files_huge_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "compare", ("files", 0), "9e999")

    def test_nonfinite_compare_files_negative_huge_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "compare", ("files", 0), "-9e999")

    def test_nonfinite_jobs_nan(self):
        self._assert_nonfinite_grammar_refusal(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "NaN")

    def test_nonfinite_jobs_positive_infinity(self):
        self._assert_nonfinite_grammar_refusal(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "Infinity")

    def test_nonfinite_jobs_negative_infinity(self):
        self._assert_nonfinite_grammar_refusal(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "-Infinity")

    def test_nonfinite_jobs_plus_infinity(self):
        self._assert_nonfinite_grammar_refusal(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "+Infinity")

    def test_nonfinite_jobs_overflow_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "1e309")

    def test_nonfinite_jobs_negative_overflow_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "-1e309")

    def test_nonfinite_jobs_huge_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "9e999")

    def test_nonfinite_jobs_negative_huge_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "-9e999")

    def test_nonfinite_phase3_scenarios_nan(self):
        self._assert_nonfinite_grammar_refusal(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "NaN")

    def test_nonfinite_phase3_scenarios_positive_infinity(self):
        self._assert_nonfinite_grammar_refusal(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "Infinity")

    def test_nonfinite_phase3_scenarios_negative_infinity(self):
        self._assert_nonfinite_grammar_refusal(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "-Infinity")

    def test_nonfinite_phase3_scenarios_plus_infinity(self):
        self._assert_nonfinite_grammar_refusal(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "+Infinity")

    def test_nonfinite_phase3_scenarios_overflow_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "1e309")

    def test_nonfinite_phase3_scenarios_negative_overflow_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "-1e309")

    def test_nonfinite_phase3_scenarios_huge_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "9e999")

    def test_nonfinite_phase3_scenarios_negative_huge_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "-9e999")

    def test_nonfinite_full_tree_entries_nan(self):
        self._assert_nonfinite_grammar_refusal(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "NaN")

    def test_nonfinite_full_tree_entries_positive_infinity(self):
        self._assert_nonfinite_grammar_refusal(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "Infinity")

    def test_nonfinite_full_tree_entries_negative_infinity(self):
        self._assert_nonfinite_grammar_refusal(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "-Infinity")

    def test_nonfinite_full_tree_entries_plus_infinity(self):
        self._assert_nonfinite_grammar_refusal(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "+Infinity")

    def test_nonfinite_full_tree_entries_overflow_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "1e309")

    def test_nonfinite_full_tree_entries_negative_overflow_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "-1e309")

    def test_nonfinite_full_tree_entries_huge_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "9e999")

    def test_nonfinite_full_tree_entries_negative_huge_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "-9e999")

    def test_nonfinite_merge_parents_nan(self):
        self._assert_nonfinite_grammar_refusal(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "NaN")

    def test_nonfinite_merge_parents_positive_infinity(self):
        self._assert_nonfinite_grammar_refusal(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "Infinity")

    def test_nonfinite_merge_parents_negative_infinity(self):
        self._assert_nonfinite_grammar_refusal(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "-Infinity")

    def test_nonfinite_merge_parents_plus_infinity(self):
        self._assert_nonfinite_grammar_refusal(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "+Infinity")

    def test_nonfinite_merge_parents_overflow_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "1e309")

    def test_nonfinite_merge_parents_negative_overflow_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "-1e309")

    def test_nonfinite_merge_parents_huge_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "9e999")

    def test_nonfinite_merge_parents_negative_huge_exponent(self):
        self._assert_nonfinite_grammar_refusal(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "-9e999")

    def test_nonfinite_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
