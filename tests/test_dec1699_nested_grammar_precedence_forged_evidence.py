"""DEC-1699: strict JSON grammar outranks forged root evidence inventory.

Offline synthetic tests only. No annual-run authority or external action.
"""
import copy
import io
import json
import unittest

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli


class NestedGrammarPrecedesForgedEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_ingress_precedes_forgery(self, category, path, fault, token):
        self.assertIn(category, source.REQUIRED)
        self.assertIn(fault, ("forged_schema", "missing_schema",
                              "approval", "pr_null"))
        self.assertIn(token, ("True", "01", "1e", "Infinity"))
        before = self.fixture._portable_top_level_members_json()
        copied = copy.deepcopy(self.fixture.envelope)
        target = copied[category]
        for segment in path:
            target = target[segment]
        self.assertIs(type(target), dict)
        target["zz_dec1699_bad"] = "DEC1699_BAD_TOKEN"
        if fault == "forged_schema":
            copied["schema"] = "unreviewed-synthetic-v2"
        elif fault == "missing_schema":
            copied.pop("schema")
        elif fault == "approval":
            copied["can_authorize_annual_run"] = True
        elif fault == "pr_null":
            copied["pr"] = None
        encoded = json.dumps(copied, sort_keys=True, separators=(",", ":"))
        needle = '"zz_dec1699_bad":"DEC1699_BAD_TOKEN"'
        self.assertEqual(encoded.count(needle), 1)
        corrupted = encoded.replace(needle,
                                    '"zz_dec1699_bad":' + token, 1)
        parsed = source.review_bundle_json_text(corrupted)
        out = io.StringIO()
        status = cli.run_stdin_review(io.StringIO(corrupted), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(before, self.fixture._portable_top_level_members_json())
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(status, 2)
        self.assertEqual(parsed["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        self.assertEqual(emitted["diagnostics"],
                         ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        self.assertNotIn("DEC1699_BAD_TOKEN", out.getvalue())
        self.assertNotIn("tests/sample.py", out.getvalue())
        self.assertNotIn("docs/sample.md", out.getvalue())
        for verdict in (parsed, emitted):
            self.assertFalse(verdict["source_consistency"])
            self.assertFalse(verdict["independent_original_os_proof"])
            self.assertFalse(verdict["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(verdict["can_authorize_annual_run"])

    def test_nested_grammar_runs_forged_schema_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "runs", (0,), "forged_schema", "True")

    def test_nested_grammar_runs_forged_schema_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "runs", (0,), "forged_schema", "01")

    def test_nested_grammar_runs_forged_schema_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "runs", (0,), "forged_schema", "1e")

    def test_nested_grammar_runs_forged_schema_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "runs", (0,), "forged_schema", "Infinity")

    def test_nested_grammar_runs_missing_schema_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "runs", (0,), "missing_schema", "True")

    def test_nested_grammar_runs_missing_schema_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "runs", (0,), "missing_schema", "01")

    def test_nested_grammar_runs_missing_schema_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "runs", (0,), "missing_schema", "1e")

    def test_nested_grammar_runs_missing_schema_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "runs", (0,), "missing_schema", "Infinity")

    def test_nested_grammar_runs_approval_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "runs", (0,), "approval", "True")

    def test_nested_grammar_runs_approval_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "runs", (0,), "approval", "01")

    def test_nested_grammar_runs_approval_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "runs", (0,), "approval", "1e")

    def test_nested_grammar_runs_approval_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "runs", (0,), "approval", "Infinity")

    def test_nested_grammar_runs_pr_null_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "runs", (0,), "pr_null", "True")

    def test_nested_grammar_runs_pr_null_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "runs", (0,), "pr_null", "01")

    def test_nested_grammar_runs_pr_null_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "runs", (0,), "pr_null", "1e")

    def test_nested_grammar_runs_pr_null_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "runs", (0,), "pr_null", "Infinity")

    def test_nested_grammar_compare_files_forged_schema_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "compare", ("files", 0), "forged_schema", "True")

    def test_nested_grammar_compare_files_forged_schema_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "compare", ("files", 0), "forged_schema", "01")

    def test_nested_grammar_compare_files_forged_schema_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "compare", ("files", 0), "forged_schema", "1e")

    def test_nested_grammar_compare_files_forged_schema_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "compare", ("files", 0), "forged_schema", "Infinity")

    def test_nested_grammar_compare_files_missing_schema_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "compare", ("files", 0), "missing_schema", "True")

    def test_nested_grammar_compare_files_missing_schema_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "compare", ("files", 0), "missing_schema", "01")

    def test_nested_grammar_compare_files_missing_schema_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "compare", ("files", 0), "missing_schema", "1e")

    def test_nested_grammar_compare_files_missing_schema_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "compare", ("files", 0), "missing_schema", "Infinity")

    def test_nested_grammar_compare_files_approval_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "compare", ("files", 0), "approval", "True")

    def test_nested_grammar_compare_files_approval_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "compare", ("files", 0), "approval", "01")

    def test_nested_grammar_compare_files_approval_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "compare", ("files", 0), "approval", "1e")

    def test_nested_grammar_compare_files_approval_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "compare", ("files", 0), "approval", "Infinity")

    def test_nested_grammar_compare_files_pr_null_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "compare", ("files", 0), "pr_null", "True")

    def test_nested_grammar_compare_files_pr_null_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "compare", ("files", 0), "pr_null", "01")

    def test_nested_grammar_compare_files_pr_null_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "compare", ("files", 0), "pr_null", "1e")

    def test_nested_grammar_compare_files_pr_null_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "compare", ("files", 0), "pr_null", "Infinity")

    def test_nested_grammar_jobs_forged_schema_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "forged_schema", "True")

    def test_nested_grammar_jobs_forged_schema_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "forged_schema", "01")

    def test_nested_grammar_jobs_forged_schema_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "forged_schema", "1e")

    def test_nested_grammar_jobs_forged_schema_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "forged_schema", "Infinity")

    def test_nested_grammar_jobs_missing_schema_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "missing_schema", "True")

    def test_nested_grammar_jobs_missing_schema_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "missing_schema", "01")

    def test_nested_grammar_jobs_missing_schema_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "missing_schema", "1e")

    def test_nested_grammar_jobs_missing_schema_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "missing_schema", "Infinity")

    def test_nested_grammar_jobs_approval_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "approval", "True")

    def test_nested_grammar_jobs_approval_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "approval", "01")

    def test_nested_grammar_jobs_approval_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "approval", "1e")

    def test_nested_grammar_jobs_approval_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "approval", "Infinity")

    def test_nested_grammar_jobs_pr_null_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "pr_null", "True")

    def test_nested_grammar_jobs_pr_null_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "pr_null", "01")

    def test_nested_grammar_jobs_pr_null_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "pr_null", "1e")

    def test_nested_grammar_jobs_pr_null_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "jobs_by_run", (sorted(self.fixture.envelope["jobs_by_run"])[0], 0), "pr_null", "Infinity")

    def test_nested_grammar_phase3_scenarios_forged_schema_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "forged_schema", "True")

    def test_nested_grammar_phase3_scenarios_forged_schema_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "forged_schema", "01")

    def test_nested_grammar_phase3_scenarios_forged_schema_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "forged_schema", "1e")

    def test_nested_grammar_phase3_scenarios_forged_schema_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "forged_schema", "Infinity")

    def test_nested_grammar_phase3_scenarios_missing_schema_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "missing_schema", "True")

    def test_nested_grammar_phase3_scenarios_missing_schema_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "missing_schema", "01")

    def test_nested_grammar_phase3_scenarios_missing_schema_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "missing_schema", "1e")

    def test_nested_grammar_phase3_scenarios_missing_schema_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "missing_schema", "Infinity")

    def test_nested_grammar_phase3_scenarios_approval_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "approval", "True")

    def test_nested_grammar_phase3_scenarios_approval_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "approval", "01")

    def test_nested_grammar_phase3_scenarios_approval_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "approval", "1e")

    def test_nested_grammar_phase3_scenarios_approval_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "approval", "Infinity")

    def test_nested_grammar_phase3_scenarios_pr_null_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "pr_null", "True")

    def test_nested_grammar_phase3_scenarios_pr_null_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "pr_null", "01")

    def test_nested_grammar_phase3_scenarios_pr_null_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "pr_null", "1e")

    def test_nested_grammar_phase3_scenarios_pr_null_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "phase3_evidence_snapshot", ("index", "scenarios", 0), "pr_null", "Infinity")

    def test_nested_grammar_full_tree_entries_forged_schema_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "forged_schema", "True")

    def test_nested_grammar_full_tree_entries_forged_schema_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "forged_schema", "01")

    def test_nested_grammar_full_tree_entries_forged_schema_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "forged_schema", "1e")

    def test_nested_grammar_full_tree_entries_forged_schema_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "forged_schema", "Infinity")

    def test_nested_grammar_full_tree_entries_missing_schema_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "missing_schema", "True")

    def test_nested_grammar_full_tree_entries_missing_schema_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "missing_schema", "01")

    def test_nested_grammar_full_tree_entries_missing_schema_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "missing_schema", "1e")

    def test_nested_grammar_full_tree_entries_missing_schema_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "missing_schema", "Infinity")

    def test_nested_grammar_full_tree_entries_approval_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "approval", "True")

    def test_nested_grammar_full_tree_entries_approval_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "approval", "01")

    def test_nested_grammar_full_tree_entries_approval_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "approval", "1e")

    def test_nested_grammar_full_tree_entries_approval_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "approval", "Infinity")

    def test_nested_grammar_full_tree_entries_pr_null_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "pr_null", "True")

    def test_nested_grammar_full_tree_entries_pr_null_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "pr_null", "01")

    def test_nested_grammar_full_tree_entries_pr_null_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "pr_null", "1e")

    def test_nested_grammar_full_tree_entries_pr_null_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "full_tree_snapshots", (sorted(self.fixture.envelope["full_tree_snapshots"])[0], "tree", 0), "pr_null", "Infinity")

    def test_nested_grammar_merge_parents_forged_schema_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "forged_schema", "True")

    def test_nested_grammar_merge_parents_forged_schema_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "forged_schema", "01")

    def test_nested_grammar_merge_parents_forged_schema_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "forged_schema", "1e")

    def test_nested_grammar_merge_parents_forged_schema_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "forged_schema", "Infinity")

    def test_nested_grammar_merge_parents_missing_schema_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "missing_schema", "True")

    def test_nested_grammar_merge_parents_missing_schema_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "missing_schema", "01")

    def test_nested_grammar_merge_parents_missing_schema_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "missing_schema", "1e")

    def test_nested_grammar_merge_parents_missing_schema_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "missing_schema", "Infinity")

    def test_nested_grammar_merge_parents_approval_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "approval", "True")

    def test_nested_grammar_merge_parents_approval_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "approval", "01")

    def test_nested_grammar_merge_parents_approval_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "approval", "1e")

    def test_nested_grammar_merge_parents_approval_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "approval", "Infinity")

    def test_nested_grammar_merge_parents_pr_null_capital_true(self):
        self._assert_ingress_precedes_forgery(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "pr_null", "True")

    def test_nested_grammar_merge_parents_pr_null_leading_zero(self):
        self._assert_ingress_precedes_forgery(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "pr_null", "01")

    def test_nested_grammar_merge_parents_pr_null_incomplete_exponent(self):
        self._assert_ingress_precedes_forgery(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "pr_null", "1e")

    def test_nested_grammar_merge_parents_pr_null_nonfinite_constant(self):
        self._assert_ingress_precedes_forgery(
            "merge_checkout_snapshot", ("merge_commit", "parents", 0), "pr_null", "Infinity")

    def test_nested_grammar_clean_control(self):
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
