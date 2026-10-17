"""DEC-1440: compose independently supplied offline draft/CI evidence shapes.

Absolutely no network, workflow dispatch, protected-original read/write,
GitHub settings change or trading. Consistency is NOT source authentication.
"""
from __future__ import annotations

import unittest
import test_dec1426_exact_ci_job_critical_steps_offline as jobs_review
import test_dec1436_pr_compare_file_count_offline as file_review
import test_dec1435_git_tree_regular_blob_review as modes_review
import test_dec1439_changed_git_blob_source_bytes_offline as bytes_review
import test_dec1430_reviewed_ci_workflow_blob_source_identity as ci_source
import test_dec1441_git_tree_sha_chain_source_review as tree_chain


def review_stacked_draft_evidence(pr, runs, jobs_by_run, compare, commit,
                                  tree, nodes, changed_bytes, ci_workflow_bytes,
                                  full_tree_snapshots):
    """Return diagnostic shape only; never authorization or authenticated proof."""
    checks = (
        jobs_review.review_exact_pr_ci_jobs(pr, runs, jobs_by_run),
        file_review.review_draft_file_inventory_counts(pr, compare, commit),
        modes_review.review_source_tree_mode(pr, compare, commit, tree, nodes),
        bytes_review.review_changed_blob_byte_identity(
            compare, nodes, changed_bytes),
        ci_source.review_ci_workflow_blobs(ci_workflow_bytes),
        tree_chain.review_exact_changed_tree_chain(
            commit, compare, full_tree_snapshots, changed_bytes),
    )
    diagnostics = tuple(sorted({reason for check in checks for reason in check}))
    return {
        "source_consistency": not diagnostics,
        "diagnostics": diagnostics,
        "independent_original_os_proof": False,
        "exclusive_server_dispatch_gate_proven": False,
        "can_authorize_annual_run": False,
    }


class CombinedSourceChecksRemainNonAuthorizing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_ci_bytes = ci_source.checked_in_ci_sources()

    def setUp(self):
        fixture = jobs_review.ActualRequiredStepEvidenceIsNotProtectedExecutionConsent(
            "test_exact_successful_job_and_step_evidence_is_consistent")
        fixture.setUp()
        self.pr = dict(fixture.pr)
        self.pr.update({"changed_files": 2, "additions": 10, "deletions": 0})
        self.runs = fixture.runs
        self.jobs = fixture.jobs_by_run
        base, head = self.pr["base_sha"], self.pr["head_sha"]
        self.compare = {
            "repository_full_name": "Dtwosam/FMP",
            "base": base, "head": head, "status": "ahead",
            "ahead_by": 1, "behind_by": 0, "total_commits": 1,
            "base_commit": {"sha": base},
            "merge_base_commit": {"sha": base},
            "too_large": None,
            "files": [
                {"filename": "tests/sample.py", "status": "added",
                 "previous_filename": None, "additions": 6,
                 "deletions": 0, "changes": 6},
                {"filename": "docs/sample.md", "status": "added",
                 "previous_filename": None, "additions": 4,
                 "deletions": 0, "changes": 4},
            ],
        }
        tree_sha = "c" * 40
        self.commit = {"sha": head, "parents": [{"sha": base}],
                       "tree": {"sha": tree_sha}}
        self.tree = {"sha": tree_sha, "truncated": False}
        self.changed = {
            "tests/sample.py": b"pass\n",
            "docs/sample.md": b"# Source-only\n",
        }
        self.nodes = {
            "tests": {"mode": "040000", "type": "tree"},
            "docs": {"mode": "040000", "type": "tree"},
        }
        self.nodes.update({
            path: {"mode": "100644", "type": "blob",
                   "sha": ci_source.git_blob_id(payload)}
            for path, payload in self.changed.items()
        })
        self.full_trees = {
            tree_sha: {
                "sha": tree_sha, "truncated": False,
                "tree": [
                    {"path": "tests", "mode": "040000", "type": "tree", "sha": "d"*40},
                    {"path": "docs", "mode": "040000", "type": "tree", "sha": "e"*40},
                ],
            },
            "d"*40: {
                "sha": "d"*40, "truncated": False,
                "tree": [{"path": "sample.py", "mode": "100644",
                          "type": "blob",
                          "sha": ci_source.git_blob_id(self.changed["tests/sample.py"])}],
            },
            "e"*40: {
                "sha": "e"*40, "truncated": False,
                "tree": [{"path": "sample.md", "mode": "100644",
                          "type": "blob",
                          "sha": ci_source.git_blob_id(self.changed["docs/sample.md"])}],
            },
        }
        self.ci_bytes = dict(self.original_ci_bytes)

    def verdict(self):
        return review_stacked_draft_evidence(
            self.pr, self.runs, self.jobs, self.compare, self.commit,
            self.tree, self.nodes, self.changed, self.ci_bytes,
            self.full_trees)

    def test_consistent_synthetic_bundle_passes_only_source_consistency(self):
        result = self.verdict()
        self.assertTrue(result["source_consistency"], result["diagnostics"])
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["can_authorize_annual_run"])

    def test_missing_historical_job_fails_the_composite(self):
        self.jobs.pop(8001)
        self.assertFalse(self.verdict()["source_consistency"])

    def test_failed_phase3_step_fails_the_composite(self):
        self.jobs[8000][0]["steps"][1]["conclusion"] = "failure"
        self.assertFalse(self.verdict()["source_consistency"])

    def test_wrong_pr_link_fails_the_composite(self):
        self.runs[1]["pull_requests"][0]["number"] = 10
        self.assertFalse(self.verdict()["source_consistency"])

    def test_two_commit_lineage_fails_the_composite(self):
        self.compare["ahead_by"] = 2
        self.assertFalse(self.verdict()["source_consistency"])

    def test_hidden_change_count_fails_the_composite(self):
        self.pr["changed_files"] = 3
        self.assertFalse(self.verdict()["source_consistency"])

    def test_production_file_path_fails_the_composite(self):
        self.compare["files"][0]["filename"] = "src/fmp/runtime.py"
        self.assertFalse(self.verdict()["source_consistency"])

    def test_symlink_leaf_fails_the_composite(self):
        self.nodes["tests/sample.py"]["mode"] = "120000"
        self.assertFalse(self.verdict()["source_consistency"])

    def test_wrong_git_object_bytes_fail_the_composite(self):
        self.changed["docs/sample.md"] += b"tampered"
        self.assertFalse(self.verdict()["source_consistency"])

    def test_missing_changed_source_bytes_fail_the_composite(self):
        self.changed.pop("tests/sample.py")
        self.assertFalse(self.verdict()["source_consistency"])

    def test_mismatched_commit_tree_sha_fails_the_composite(self):
        self.tree["sha"] = "d" * 40
        self.assertFalse(self.verdict()["source_consistency"])

    def test_modified_historical_ci_workflow_fails_the_composite(self):
        key = ".github/workflows/tests.yml"
        self.ci_bytes[key] += b"\n"
        self.assertFalse(self.verdict()["source_consistency"])

    def test_missing_ci_workflow_source_fails_the_composite(self):
        self.ci_bytes.pop(".github/workflows/tests.yml")
        self.assertFalse(self.verdict()["source_consistency"])

    def test_multiple_failures_accumulate_diagnostics(self):
        self.pr["changed_files"] = 3
        self.nodes["tests/sample.py"]["mode"] = "120000"
        result = self.verdict()
        self.assertFalse(result["source_consistency"])
        self.assertIn("PR_COMPARE_FILE_COUNT_MISMATCH",
                      result["diagnostics"])
        self.assertIn("BLOB_LEAF_TYPE_UNREVIEWED",
                      result["diagnostics"])

    def test_external_os_original_integrity_is_never_inferred(self):
        result = self.verdict()
        self.assertFalse(result["independent_original_os_proof"])

    def test_exclusive_2023_dispatch_admission_is_never_inferred(self):
        result = self.verdict()
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])

    def test_no_combination_of_offline_snapshots_can_grant_run385(self):
        result = self.verdict()
        self.assertFalse(result["can_authorize_annual_run"])
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", result["diagnostics"])

    def test_mismatched_parent_git_tree_sha_rejected(self):
        self.full_trees["c"*40]["tree"][0]["sha"] = "f"*40
        self.assertIn("TREE_CHAIN_TREE_OBJECT_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_missing_subtree_snapshot_rejected(self):
        self.full_trees.pop("d"*40)
        self.assertIn("TREE_CHAIN_TREE_OBJECT_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_duplicate_root_tree_entry_rejected(self):
        root = self.full_trees["c"*40]["tree"]
        root.append(dict(root[0]))
        self.assertIn("TREE_CHAIN_ENTRY_CARDINALITY_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_truncated_child_tree_rejected(self):
        self.full_trees["e"*40]["truncated"] = True
        self.assertIn("TREE_CHAIN_TREE_OBJECT_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_leaf_tree_sha_not_matched_to_source_rejected(self):
        self.full_trees["e"*40]["tree"][0]["sha"] = "f"*40
        self.assertIn("TREE_CHAIN_LEAF_BYTES_SHA_MISMATCH",
                      self.verdict()["diagnostics"])

    def test_extra_unlinked_tree_snapshot_rejected(self):
        self.full_trees["f"*40] = {
            "sha": "f"*40, "truncated": False, "tree": []}
        self.assertIn("TREE_CHAIN_TREE_SNAPSHOT_INVENTORY_UNREVIEWED",
                      self.verdict()["diagnostics"])

    def test_flat_regular_leaf_cannot_override_symlinked_chain(self):
        self.full_trees["d"*40]["tree"][0]["mode"] = "120000"
        self.assertEqual(self.nodes["tests/sample.py"]["mode"], "100644")
        self.assertIn("TREE_CHAIN_LEAF_NOT_REGULAR_BLOB",
                      self.verdict()["diagnostics"])

    def test_fully_consistent_composite_remains_non_authorizing(self):
        result = self.verdict()
        self.assertEqual(result["diagnostics"], ())
        self.assertFalse(result["independent_original_os_proof"])
        self.assertFalse(result["exclusive_server_dispatch_gate_proven"])
        self.assertFalse(result["can_authorize_annual_run"])
