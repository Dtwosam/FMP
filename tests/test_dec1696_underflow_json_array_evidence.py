"""DEC-1696: finite float underflow JSON values preserve nested review parity.

No network, mutation of protected evidence, dispatch, trade or annual authority.
"""
import copy
import io
import json
import math
import unittest

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli


class ArrayEvidenceFiniteUnderflowParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_finite_underflow_review_parity(self, category, path, token):
        self.assertIn(category, source.REQUIRED)
        self.assertIn(token, (
            "0e-9999", "-0e-9999", "1e-9999", "-1e-9999",
            "1e-500", "-1e-500", "0.000e+5", "-0.000e+5"))
        parsed_value = json.loads(token)
        self.assertIs(type(parsed_value), float)
        self.assertTrue(math.isfinite(parsed_value))
        self.assertEqual(parsed_value, 0.0)
        before = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        target = copied[category]
        for part in path:
            target = target[part]
        self.assertIs(type(target), dict)
        target["zz_dec1696_number"] = "DEC1696_NUMERIC_MARKER"
        encoded = json.dumps(copied, sort_keys=True, separators=(",", ":"))
        needle = '"zz_dec1696_number":"DEC1696_NUMERIC_MARKER"'
        self.assertEqual(encoded.count(needle), 1)
        changed = encoded.replace(
            needle, '"zz_dec1696_number":' + token, 1)
        decoded = json.loads(changed)
        cursor = decoded[category]
        for part in path:
            cursor = cursor[part]
        self.assertEqual(cursor["zz_dec1696_number"], parsed_value)
        target["zz_dec1696_number"] = parsed_value
        direct = source.review_bundle_envelope(copied)
        parsed = source.review_bundle_json_text(changed)
        self.assertEqual(parsed, direct)
        self.assertNotIn("BUNDLE_JSON_GRAMMAR_UNREVIEWED",
                         parsed["diagnostics"])
        self.assertNotIn("BUNDLE_JSON_UNICODE_UNREVIEWED",
                         parsed["diagnostics"])
        output = io.StringIO()
        rc = cli.run_stdin_review(io.StringIO(changed), output)
        emitted = json.loads(output.getvalue())
        self.assertEqual(before, self.fixture._portable_top_level_members_json())
        self.assertEqual(rc, 0 if direct["source_consistency"] else 2)
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        self.assertEqual(emitted["source_consistency"],
                         direct["source_consistency"])
        self.assertEqual(emitted["diagnostics"], list(direct["diagnostics"]))
        self.assertNotIn("DEC1696_NUMERIC_MARKER", output.getvalue())
        self.assertNotIn("tests/sample.py", output.getvalue())
        self.assertNotIn("docs/sample.md", output.getvalue())
        for verdict in (direct, parsed, emitted):
            self.assertFalse(verdict["independent_original_os_proof"])
            self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(verdict["can_authorize_annual_run"])

    def test_finite_underflow_runs_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "runs", (0,), "0e-9999")

    def test_finite_underflow_runs_negative_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "runs", (0,), "-0e-9999")

    def test_finite_underflow_runs_positive_underflow(self):
        self._assert_finite_underflow_review_parity(
            "runs", (0,), "1e-9999")

    def test_finite_underflow_runs_negative_underflow(self):
        self._assert_finite_underflow_review_parity(
            "runs", (0,), "-1e-9999")

    def test_finite_underflow_runs_positive_small_underflow(self):
        self._assert_finite_underflow_review_parity(
            "runs", (0,), "1e-500")

    def test_finite_underflow_runs_negative_small_underflow(self):
        self._assert_finite_underflow_review_parity(
            "runs", (0,), "-1e-500")

    def test_finite_underflow_runs_decimal_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "runs", (0,), "0.000e+5")

    def test_finite_underflow_runs_negative_decimal_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "runs", (0,), "-0.000e+5")

    def test_finite_underflow_compare_files_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "compare", ("files", 0), "0e-9999")

    def test_finite_underflow_compare_files_negative_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "compare", ("files", 0), "-0e-9999")

    def test_finite_underflow_compare_files_positive_underflow(self):
        self._assert_finite_underflow_review_parity(
            "compare", ("files", 0), "1e-9999")

    def test_finite_underflow_compare_files_negative_underflow(self):
        self._assert_finite_underflow_review_parity(
            "compare", ("files", 0), "-1e-9999")

    def test_finite_underflow_compare_files_positive_small_underflow(self):
        self._assert_finite_underflow_review_parity(
            "compare", ("files", 0), "1e-500")

    def test_finite_underflow_compare_files_negative_small_underflow(self):
        self._assert_finite_underflow_review_parity(
            "compare", ("files", 0), "-1e-500")

    def test_finite_underflow_compare_files_decimal_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "compare", ("files", 0), "0.000e+5")

    def test_finite_underflow_compare_files_negative_decimal_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "compare", ("files", 0), "-0.000e+5")

    def test_finite_underflow_jobs_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "0e-9999")

    def test_finite_underflow_jobs_negative_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "-0e-9999")

    def test_finite_underflow_jobs_positive_underflow(self):
        self._assert_finite_underflow_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "1e-9999")

    def test_finite_underflow_jobs_negative_underflow(self):
        self._assert_finite_underflow_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "-1e-9999")

    def test_finite_underflow_jobs_positive_small_underflow(self):
        self._assert_finite_underflow_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "1e-500")

    def test_finite_underflow_jobs_negative_small_underflow(self):
        self._assert_finite_underflow_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "-1e-500")

    def test_finite_underflow_jobs_decimal_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "0.000e+5")

    def test_finite_underflow_jobs_negative_decimal_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "-0.000e+5")

    def test_finite_underflow_phase3_scenarios_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "0e-9999")

    def test_finite_underflow_phase3_scenarios_negative_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "-0e-9999")

    def test_finite_underflow_phase3_scenarios_positive_underflow(self):
        self._assert_finite_underflow_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "1e-9999")

    def test_finite_underflow_phase3_scenarios_negative_underflow(self):
        self._assert_finite_underflow_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "-1e-9999")

    def test_finite_underflow_phase3_scenarios_positive_small_underflow(self):
        self._assert_finite_underflow_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "1e-500")

    def test_finite_underflow_phase3_scenarios_negative_small_underflow(self):
        self._assert_finite_underflow_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "-1e-500")

    def test_finite_underflow_phase3_scenarios_decimal_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "0.000e+5")

    def test_finite_underflow_phase3_scenarios_negative_decimal_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "-0.000e+5")

    def test_finite_underflow_full_tree_entries_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "0e-9999")

    def test_finite_underflow_full_tree_entries_negative_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "-0e-9999")

    def test_finite_underflow_full_tree_entries_positive_underflow(self):
        self._assert_finite_underflow_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "1e-9999")

    def test_finite_underflow_full_tree_entries_negative_underflow(self):
        self._assert_finite_underflow_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "-1e-9999")

    def test_finite_underflow_full_tree_entries_positive_small_underflow(self):
        self._assert_finite_underflow_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "1e-500")

    def test_finite_underflow_full_tree_entries_negative_small_underflow(self):
        self._assert_finite_underflow_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "-1e-500")

    def test_finite_underflow_full_tree_entries_decimal_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "0.000e+5")

    def test_finite_underflow_full_tree_entries_negative_decimal_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "-0.000e+5")

    def test_finite_underflow_merge_parents_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "0e-9999")

    def test_finite_underflow_merge_parents_negative_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "-0e-9999")

    def test_finite_underflow_merge_parents_positive_underflow(self):
        self._assert_finite_underflow_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "1e-9999")

    def test_finite_underflow_merge_parents_negative_underflow(self):
        self._assert_finite_underflow_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "-1e-9999")

    def test_finite_underflow_merge_parents_positive_small_underflow(self):
        self._assert_finite_underflow_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "1e-500")

    def test_finite_underflow_merge_parents_negative_small_underflow(self):
        self._assert_finite_underflow_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "-1e-500")

    def test_finite_underflow_merge_parents_decimal_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "0.000e+5")

    def test_finite_underflow_merge_parents_negative_decimal_zero_exponent(self):
        self._assert_finite_underflow_review_parity(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "-0.000e+5")

    def test_finite_underflow_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
