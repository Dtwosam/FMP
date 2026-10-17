"""DEC-1469: composite reviewer must fail closed on malformed top-level inputs.

Only synthetic in-memory evidence; no network, annual dispatch, protected
originals/archives, repository changes or brokerage/trading.
"""
import unittest
import test_dec1440_stacked_source_evidence_offline as composite


class AllSourceInputsAreMandatoryEvenUnderMalformedData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        composite.CombinedSourceChecksRemainNonAuthorizing.setUpClass()

    def setUp(self):
        f = composite.CombinedSourceChecksRemainNonAuthorizing(
            "test_consistent_synthetic_bundle_passes_only_source_consistency")
        f.setUp()
        self.args = {
            "pr": f.pr,
            "runs": f.runs,
            "jobs_by_run": f.jobs,
            "compare": f.compare,
            "commit": f.commit,
            "tree": f.tree,
            "nodes": f.nodes,
            "changed_bytes": f.changed,
            "ci_workflow_bytes": f.ci_bytes,
            "full_tree_snapshots": f.full_trees,
            "merge_checkout_snapshot": f.merge_checkout,
            "checkout_by_run": f.runner_checks,
            "phase3_evidence_snapshot": f.phase3_evidence,
            "raw_ci_runner_logs": f.raw_ci_runner_logs,
            "raw_ci_log_receipts": f.raw_log_receipts,
        }

    def verdict(self):
        return composite.review_stacked_draft_evidence(**self.args)

    def assert_failed_closed(self):
        verdict = self.verdict()
        self.assertIs(type(verdict), dict)
        self.assertIs(verdict["source_consistency"], False)
        self.assertTrue(verdict["diagnostics"])
        self.assertIs(verdict["can_authorize_annual_run"], False)
        self.assertIs(verdict["independent_original_os_proof"], False)
        self.assertIs(verdict["exclusive_server_dispatch_gate_proven"], False)

    def test_all_synthetic_sources_consistent_but_never_annual_consent(self):
        verdict = self.verdict()
        self.assertEqual(verdict["diagnostics"], ())
        self.assertFalse(verdict["can_authorize_annual_run"])

    def test_null_pr_metadata_is_diagnostic_not_exception(self):
        self.args["pr"] = None
        self.assert_failed_closed()

    def test_null_workflow_run_inventory_is_diagnostic(self):
        self.args["runs"] = None
        self.assert_failed_closed()

    def test_null_ci_job_inventory_is_diagnostic(self):
        self.args["jobs_by_run"] = None
        self.assert_failed_closed()

    def test_null_commit_comparison_is_diagnostic(self):
        self.args["compare"] = None
        self.assert_failed_closed()

    def test_null_exact_git_commit_object_is_diagnostic(self):
        self.args["commit"] = None
        self.assert_failed_closed()

    def test_null_git_root_tree_is_diagnostic(self):
        self.args["tree"] = None
        self.assert_failed_closed()

    def test_null_git_path_nodes_are_diagnostic(self):
        self.args["nodes"] = None
        self.assert_failed_closed()

    def test_null_changed_source_bytes_are_diagnostic(self):
        self.args["changed_bytes"] = None
        self.assert_failed_closed()

    def test_null_ci_yaml_sources_are_diagnostic(self):
        self.args["ci_workflow_bytes"] = None
        self.assert_failed_closed()

    def test_null_full_git_tree_snapshots_are_diagnostic(self):
        self.args["full_tree_snapshots"] = None
        self.assert_failed_closed()

    def test_null_merge_checkout_evidence_is_diagnostic(self):
        self.args["merge_checkout_snapshot"] = None
        self.assert_failed_closed()

    def test_null_runner_checkout_inventory_is_diagnostic(self):
        self.args["checkout_by_run"] = None
        self.assert_failed_closed()

    def test_null_phase3_acceptance_index_is_diagnostic(self):
        self.args["phase3_evidence_snapshot"] = None
        self.assert_failed_closed()

    def test_null_raw_ci_log_text_is_diagnostic(self):
        self.args["raw_ci_runner_logs"] = None
        self.assert_failed_closed()

    def test_null_raw_ci_log_receipts_are_diagnostic(self):
        self.args["raw_ci_log_receipts"] = None
        self.assert_failed_closed()

    def test_unhashable_phase3_run_id_does_not_throw_typeerror(self):
        phase3 = next(x for x in self.args["runs"]
                      if x["name"] == "phase3-acceptance")
        phase3["id"] = [8000]
        self.assert_failed_closed()

    def test_nonboolean_draft_state_cannot_pass_source_review(self):
        self.args["pr"]["draft"] = 1
        self.assert_failed_closed()

    def test_unexpected_prod_path_cannot_pass_source_review(self):
        self.args["compare"]["files"][0]["filename"] = "src/trading.py"
        self.assert_failed_closed()
