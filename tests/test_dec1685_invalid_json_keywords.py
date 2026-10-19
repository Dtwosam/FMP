"""DEC-1685: invalid JSON keywords must fail at grammar ingress.

Synthetic, offline, source-only. This suite never authorizes annual runs,
loads protected artifacts, dispatches CI workflows, merges or trades.
"""
import io
import json
import unittest

import test_dec1478_portable_ci_source_bundle_envelope as source
import test_dec1479_offline_ci_bundle_stdin_command as cli


class MalformedJsonKeywordIngressTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source.PortableSourceBundleNeverGrantsAnnualRunAdmission.setUpClass()

    def setUp(self):
        self.fixture = source.PortableSourceBundleNeverGrantsAnnualRunAdmission(
            "test_valid_portable_synthetic_bundle_returns_consistency_only")
        self.fixture.setUp()

    def _assert_keyword_fails_at_json_grammar(self, category, token):
        self.assertIn(category, source.REQUIRED)
        self.assertIn(token, ("True", "FALSE", "Null", "None",
                              "undefined", "tru"))
        clean = self.fixture._portable_top_level_members_json()
        encoded = self.fixture._portable_top_level_members_json({
            category: json.dumps(category) + ":" + token})
        self.assertNotEqual(encoded, clean)
        with self.assertRaises(json.JSONDecodeError):
            json.loads(encoded)
        parsed = source.review_bundle_json_text(encoded)
        out = io.StringIO()
        exit_code = cli.run_stdin_review(io.StringIO(encoded), out)
        emitted = json.loads(out.getvalue())
        self.assertEqual(clean, self.fixture._portable_top_level_members_json())
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertEqual(exit_code, 2)
        self.assertEqual(parsed["diagnostics"],
                         ("BUNDLE_JSON_GRAMMAR_UNREVIEWED",))
        self.assertEqual(set(emitted), source.VERDICT_FIELDS)
        self.assertEqual(emitted["diagnostics"],
                         ["BUNDLE_JSON_GRAMMAR_UNREVIEWED"])
        self.assertNotIn("tests/sample.py", out.getvalue())
        self.assertNotIn("docs/sample.md", out.getvalue())
        for result in (parsed, emitted):
            self.assertFalse(result["source_consistency"])
            self.assertFalse(result["independent_original_os_proof"])
            self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
            self.assertFalse(result["can_authorize_annual_run"])

    def test_invalid_keyword_schema_capital_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "schema", "True")

    def test_invalid_keyword_schema_uppercase_false(self):
        self._assert_keyword_fails_at_json_grammar(
            "schema", "FALSE")

    def test_invalid_keyword_schema_mixed_null(self):
        self._assert_keyword_fails_at_json_grammar(
            "schema", "Null")

    def test_invalid_keyword_schema_python_none(self):
        self._assert_keyword_fails_at_json_grammar(
            "schema", "None")

    def test_invalid_keyword_schema_undefined(self):
        self._assert_keyword_fails_at_json_grammar(
            "schema", "undefined")

    def test_invalid_keyword_schema_truncated_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "schema", "tru")

    def test_invalid_keyword_pr_capital_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "pr", "True")

    def test_invalid_keyword_pr_uppercase_false(self):
        self._assert_keyword_fails_at_json_grammar(
            "pr", "FALSE")

    def test_invalid_keyword_pr_mixed_null(self):
        self._assert_keyword_fails_at_json_grammar(
            "pr", "Null")

    def test_invalid_keyword_pr_python_none(self):
        self._assert_keyword_fails_at_json_grammar(
            "pr", "None")

    def test_invalid_keyword_pr_undefined(self):
        self._assert_keyword_fails_at_json_grammar(
            "pr", "undefined")

    def test_invalid_keyword_pr_truncated_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "pr", "tru")

    def test_invalid_keyword_runs_capital_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "runs", "True")

    def test_invalid_keyword_runs_uppercase_false(self):
        self._assert_keyword_fails_at_json_grammar(
            "runs", "FALSE")

    def test_invalid_keyword_runs_mixed_null(self):
        self._assert_keyword_fails_at_json_grammar(
            "runs", "Null")

    def test_invalid_keyword_runs_python_none(self):
        self._assert_keyword_fails_at_json_grammar(
            "runs", "None")

    def test_invalid_keyword_runs_undefined(self):
        self._assert_keyword_fails_at_json_grammar(
            "runs", "undefined")

    def test_invalid_keyword_runs_truncated_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "runs", "tru")

    def test_invalid_keyword_jobs_by_run_capital_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "jobs_by_run", "True")

    def test_invalid_keyword_jobs_by_run_uppercase_false(self):
        self._assert_keyword_fails_at_json_grammar(
            "jobs_by_run", "FALSE")

    def test_invalid_keyword_jobs_by_run_mixed_null(self):
        self._assert_keyword_fails_at_json_grammar(
            "jobs_by_run", "Null")

    def test_invalid_keyword_jobs_by_run_python_none(self):
        self._assert_keyword_fails_at_json_grammar(
            "jobs_by_run", "None")

    def test_invalid_keyword_jobs_by_run_undefined(self):
        self._assert_keyword_fails_at_json_grammar(
            "jobs_by_run", "undefined")

    def test_invalid_keyword_jobs_by_run_truncated_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "jobs_by_run", "tru")

    def test_invalid_keyword_compare_capital_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "compare", "True")

    def test_invalid_keyword_compare_uppercase_false(self):
        self._assert_keyword_fails_at_json_grammar(
            "compare", "FALSE")

    def test_invalid_keyword_compare_mixed_null(self):
        self._assert_keyword_fails_at_json_grammar(
            "compare", "Null")

    def test_invalid_keyword_compare_python_none(self):
        self._assert_keyword_fails_at_json_grammar(
            "compare", "None")

    def test_invalid_keyword_compare_undefined(self):
        self._assert_keyword_fails_at_json_grammar(
            "compare", "undefined")

    def test_invalid_keyword_compare_truncated_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "compare", "tru")

    def test_invalid_keyword_commit_capital_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "commit", "True")

    def test_invalid_keyword_commit_uppercase_false(self):
        self._assert_keyword_fails_at_json_grammar(
            "commit", "FALSE")

    def test_invalid_keyword_commit_mixed_null(self):
        self._assert_keyword_fails_at_json_grammar(
            "commit", "Null")

    def test_invalid_keyword_commit_python_none(self):
        self._assert_keyword_fails_at_json_grammar(
            "commit", "None")

    def test_invalid_keyword_commit_undefined(self):
        self._assert_keyword_fails_at_json_grammar(
            "commit", "undefined")

    def test_invalid_keyword_commit_truncated_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "commit", "tru")

    def test_invalid_keyword_tree_capital_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "tree", "True")

    def test_invalid_keyword_tree_uppercase_false(self):
        self._assert_keyword_fails_at_json_grammar(
            "tree", "FALSE")

    def test_invalid_keyword_tree_mixed_null(self):
        self._assert_keyword_fails_at_json_grammar(
            "tree", "Null")

    def test_invalid_keyword_tree_python_none(self):
        self._assert_keyword_fails_at_json_grammar(
            "tree", "None")

    def test_invalid_keyword_tree_undefined(self):
        self._assert_keyword_fails_at_json_grammar(
            "tree", "undefined")

    def test_invalid_keyword_tree_truncated_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "tree", "tru")

    def test_invalid_keyword_nodes_capital_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "nodes", "True")

    def test_invalid_keyword_nodes_uppercase_false(self):
        self._assert_keyword_fails_at_json_grammar(
            "nodes", "FALSE")

    def test_invalid_keyword_nodes_mixed_null(self):
        self._assert_keyword_fails_at_json_grammar(
            "nodes", "Null")

    def test_invalid_keyword_nodes_python_none(self):
        self._assert_keyword_fails_at_json_grammar(
            "nodes", "None")

    def test_invalid_keyword_nodes_undefined(self):
        self._assert_keyword_fails_at_json_grammar(
            "nodes", "undefined")

    def test_invalid_keyword_nodes_truncated_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "nodes", "tru")

    def test_invalid_keyword_changed_bytes_b64_capital_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "changed_bytes_b64", "True")

    def test_invalid_keyword_changed_bytes_b64_uppercase_false(self):
        self._assert_keyword_fails_at_json_grammar(
            "changed_bytes_b64", "FALSE")

    def test_invalid_keyword_changed_bytes_b64_mixed_null(self):
        self._assert_keyword_fails_at_json_grammar(
            "changed_bytes_b64", "Null")

    def test_invalid_keyword_changed_bytes_b64_python_none(self):
        self._assert_keyword_fails_at_json_grammar(
            "changed_bytes_b64", "None")

    def test_invalid_keyword_changed_bytes_b64_undefined(self):
        self._assert_keyword_fails_at_json_grammar(
            "changed_bytes_b64", "undefined")

    def test_invalid_keyword_changed_bytes_b64_truncated_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "changed_bytes_b64", "tru")

    def test_invalid_keyword_ci_workflow_bytes_b64_capital_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "ci_workflow_bytes_b64", "True")

    def test_invalid_keyword_ci_workflow_bytes_b64_uppercase_false(self):
        self._assert_keyword_fails_at_json_grammar(
            "ci_workflow_bytes_b64", "FALSE")

    def test_invalid_keyword_ci_workflow_bytes_b64_mixed_null(self):
        self._assert_keyword_fails_at_json_grammar(
            "ci_workflow_bytes_b64", "Null")

    def test_invalid_keyword_ci_workflow_bytes_b64_python_none(self):
        self._assert_keyword_fails_at_json_grammar(
            "ci_workflow_bytes_b64", "None")

    def test_invalid_keyword_ci_workflow_bytes_b64_undefined(self):
        self._assert_keyword_fails_at_json_grammar(
            "ci_workflow_bytes_b64", "undefined")

    def test_invalid_keyword_ci_workflow_bytes_b64_truncated_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "ci_workflow_bytes_b64", "tru")

    def test_invalid_keyword_full_tree_snapshots_capital_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "full_tree_snapshots", "True")

    def test_invalid_keyword_full_tree_snapshots_uppercase_false(self):
        self._assert_keyword_fails_at_json_grammar(
            "full_tree_snapshots", "FALSE")

    def test_invalid_keyword_full_tree_snapshots_mixed_null(self):
        self._assert_keyword_fails_at_json_grammar(
            "full_tree_snapshots", "Null")

    def test_invalid_keyword_full_tree_snapshots_python_none(self):
        self._assert_keyword_fails_at_json_grammar(
            "full_tree_snapshots", "None")

    def test_invalid_keyword_full_tree_snapshots_undefined(self):
        self._assert_keyword_fails_at_json_grammar(
            "full_tree_snapshots", "undefined")

    def test_invalid_keyword_full_tree_snapshots_truncated_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "full_tree_snapshots", "tru")

    def test_invalid_keyword_merge_checkout_snapshot_capital_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "merge_checkout_snapshot", "True")

    def test_invalid_keyword_merge_checkout_snapshot_uppercase_false(self):
        self._assert_keyword_fails_at_json_grammar(
            "merge_checkout_snapshot", "FALSE")

    def test_invalid_keyword_merge_checkout_snapshot_mixed_null(self):
        self._assert_keyword_fails_at_json_grammar(
            "merge_checkout_snapshot", "Null")

    def test_invalid_keyword_merge_checkout_snapshot_python_none(self):
        self._assert_keyword_fails_at_json_grammar(
            "merge_checkout_snapshot", "None")

    def test_invalid_keyword_merge_checkout_snapshot_undefined(self):
        self._assert_keyword_fails_at_json_grammar(
            "merge_checkout_snapshot", "undefined")

    def test_invalid_keyword_merge_checkout_snapshot_truncated_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "merge_checkout_snapshot", "tru")

    def test_invalid_keyword_checkout_by_run_capital_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "checkout_by_run", "True")

    def test_invalid_keyword_checkout_by_run_uppercase_false(self):
        self._assert_keyword_fails_at_json_grammar(
            "checkout_by_run", "FALSE")

    def test_invalid_keyword_checkout_by_run_mixed_null(self):
        self._assert_keyword_fails_at_json_grammar(
            "checkout_by_run", "Null")

    def test_invalid_keyword_checkout_by_run_python_none(self):
        self._assert_keyword_fails_at_json_grammar(
            "checkout_by_run", "None")

    def test_invalid_keyword_checkout_by_run_undefined(self):
        self._assert_keyword_fails_at_json_grammar(
            "checkout_by_run", "undefined")

    def test_invalid_keyword_checkout_by_run_truncated_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "checkout_by_run", "tru")

    def test_invalid_keyword_phase3_evidence_snapshot_capital_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "phase3_evidence_snapshot", "True")

    def test_invalid_keyword_phase3_evidence_snapshot_uppercase_false(self):
        self._assert_keyword_fails_at_json_grammar(
            "phase3_evidence_snapshot", "FALSE")

    def test_invalid_keyword_phase3_evidence_snapshot_mixed_null(self):
        self._assert_keyword_fails_at_json_grammar(
            "phase3_evidence_snapshot", "Null")

    def test_invalid_keyword_phase3_evidence_snapshot_python_none(self):
        self._assert_keyword_fails_at_json_grammar(
            "phase3_evidence_snapshot", "None")

    def test_invalid_keyword_phase3_evidence_snapshot_undefined(self):
        self._assert_keyword_fails_at_json_grammar(
            "phase3_evidence_snapshot", "undefined")

    def test_invalid_keyword_phase3_evidence_snapshot_truncated_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "phase3_evidence_snapshot", "tru")

    def test_invalid_keyword_raw_ci_runner_logs_capital_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "raw_ci_runner_logs", "True")

    def test_invalid_keyword_raw_ci_runner_logs_uppercase_false(self):
        self._assert_keyword_fails_at_json_grammar(
            "raw_ci_runner_logs", "FALSE")

    def test_invalid_keyword_raw_ci_runner_logs_mixed_null(self):
        self._assert_keyword_fails_at_json_grammar(
            "raw_ci_runner_logs", "Null")

    def test_invalid_keyword_raw_ci_runner_logs_python_none(self):
        self._assert_keyword_fails_at_json_grammar(
            "raw_ci_runner_logs", "None")

    def test_invalid_keyword_raw_ci_runner_logs_undefined(self):
        self._assert_keyword_fails_at_json_grammar(
            "raw_ci_runner_logs", "undefined")

    def test_invalid_keyword_raw_ci_runner_logs_truncated_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "raw_ci_runner_logs", "tru")

    def test_invalid_keyword_raw_ci_log_receipts_capital_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "raw_ci_log_receipts", "True")

    def test_invalid_keyword_raw_ci_log_receipts_uppercase_false(self):
        self._assert_keyword_fails_at_json_grammar(
            "raw_ci_log_receipts", "FALSE")

    def test_invalid_keyword_raw_ci_log_receipts_mixed_null(self):
        self._assert_keyword_fails_at_json_grammar(
            "raw_ci_log_receipts", "Null")

    def test_invalid_keyword_raw_ci_log_receipts_python_none(self):
        self._assert_keyword_fails_at_json_grammar(
            "raw_ci_log_receipts", "None")

    def test_invalid_keyword_raw_ci_log_receipts_undefined(self):
        self._assert_keyword_fails_at_json_grammar(
            "raw_ci_log_receipts", "undefined")

    def test_invalid_keyword_raw_ci_log_receipts_truncated_true(self):
        self._assert_keyword_fails_at_json_grammar(
            "raw_ci_log_receipts", "tru")

    def test_invalid_keyword_clean_control(self):
        self.assertEqual(self.fixture.verdict()["diagnostics"], ())
        self.assertTrue(self.fixture.verdict()["source_consistency"])
        self.assertFalse(self.fixture.verdict()["can_authorize_annual_run"])
