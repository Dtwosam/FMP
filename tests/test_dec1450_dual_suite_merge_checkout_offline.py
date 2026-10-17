"""DEC-1450: require both PR workflow runners to fetch the same merge commit.

No network, GitHub mutation, annual execution, protected original/artifact
access, or broker/trading. Caller must authenticate original CI log records.
"""
from __future__ import annotations
import unittest
import test_dec1445_pr_merge_checkout_tree_identity_offline as checkout_review
import test_dec1422_offline_exact_head_ci_evidence_review as workflow_policy


def review_dual_suite_merge_checkouts(pr, runs, checkouts, merge_ref,
                                      merge_commit, head_commit):
    """Synthetic evidence consistency only; never authorize annual run385."""
    if (type(pr) is not dict or type(runs) is not list or
            type(checkouts) is not dict or
            not all(type(run) is dict for run in runs)):
        return ("DUAL_CHECKOUT_INPUT_UNREVIEWED",)
    issues = []
    required = frozenset(("tests", "phase3-acceptance"))
    names = [r.get("name") for r in runs]
    if len(runs) != 2 or set(names) != required:
        issues.append("DUAL_CHECKOUT_WORKFLOW_INVENTORY_UNREVIEWED")
    run_ids = []
    for name in sorted(required):
        found = [r for r in runs if r.get("name") == name]
        if len(found) != 1:
            issues.append(name + "_RUN_CARDINALITY_UNREVIEWED")
            continue
        run = found[0]
        run_id = run.get("id")
        if type(run_id) is not int or run_id <= 0:
            issues.append(name + "_RUN_ID_UNREVIEWED")
            continue
        run_ids.append(run_id)
        expected = workflow_policy.WORKFLOWS.get(name)
        if (type(expected) is not tuple or
                run.get("workflow_id") != expected[0] or
                run.get("path") != expected[1] or
                type(run.get("run_attempt")) is not int or
                run.get("run_attempt") != 1):
            issues.append(name + "_WORKFLOW_IDENTITY_UNREVIEWED")
        obs = checkouts.get(run_id)
        if type(obs) is not dict:
            issues.append(name + "_RUNNER_LOG_SNAPSHOT_UNREVIEWED")
            continue
        if obs.get("run_id") != run_id:
            issues.append(name + "_RUNNER_LOG_RUN_ASSOCIATION_MISMATCH")
        sub = checkout_review.review_pr_merge_checkout(
            pr, run, merge_ref, merge_commit, head_commit,
            obs.get("checkout_ref"), obs.get("checkout_sha_prefix"),
            obs.get("checkout_fetch_sha"))
        issues.extend(name + "_" + reason for reason in sub)
    if len(run_ids) != 2 or len(set(run_ids)) != 2:
        issues.append("DUAL_CHECKOUT_RUN_ID_UNIQUENESS_UNREVIEWED")
    if set(checkouts) != set(run_ids):
        issues.append("DUAL_CHECKOUT_RUNNER_LOG_INVENTORY_UNREVIEWED")
    if len(run_ids) == 2 and all(type(checkouts.get(run_id)) is dict for run_id in run_ids):
        first, second = (checkouts[run_ids[0]], checkouts[run_ids[1]])
        if first.get("checkout_fetch_sha") != second.get("checkout_fetch_sha"):
            issues.append("DUAL_CHECKOUT_TESTED_MERGE_SHA_DIFFERENT")
    return tuple(sorted(set(issues)))


class BothCIJobsMustTestOneIdenticalMergeCommit(unittest.TestCase):
    def setUp(self):
        self.head = "a"*40
        self.base = "b"*40
        self.merge = "c"*40
        self.tree = "d"*40
        self.pr = {"number": 1674, "head_sha": self.head,
                   "base_sha": self.base}
        self.merge_ref = {"ref": "refs/pull/1674/merge",
                          "object": {"type": "commit", "sha": self.merge}}
        self.head_commit = {"sha": self.head, "tree": {"sha": self.tree}}
        self.merge_commit = {
            "sha": self.merge, "tree": {"sha": self.tree},
            "parents": [{"sha": self.base}, {"sha": self.head}],
        }
        self.runs = [
            {
                "name": name, "id": 4000+i, "run_attempt": 1,
                "workflow_id": workflow_policy.WORKFLOWS[name][0],
                "path": workflow_policy.WORKFLOWS[name][1],
                "head_sha": self.head, "event": "pull_request",
                "status": "completed", "conclusion": "success",
            }
            for i, name in enumerate(("tests", "phase3-acceptance"))
        ]
        self.checkouts = {
            run["id"]: {
                "run_id": run["id"],
                "checkout_ref": "refs/remotes/pull/1674/merge",
                "checkout_sha_prefix": self.merge[:7],
                "checkout_fetch_sha": self.merge,
            }
            for run in self.runs
        }

    def verdict(self):
        return review_dual_suite_merge_checkouts(
            self.pr, self.runs, self.checkouts, self.merge_ref,
            self.merge_commit, self.head_commit)

    def test_both_successful_workflows_fetched_identical_tested_merge(self):
        self.assertEqual(self.verdict(), ())

    def test_phase3_fetching_another_merge_sha_fails(self):
        self.checkouts[4001]["checkout_fetch_sha"] = "e"*40
        self.assertIn("DUAL_CHECKOUT_TESTED_MERGE_SHA_DIFFERENT", self.verdict())

    def test_historical_fetching_another_merge_sha_fails(self):
        self.checkouts[4000]["checkout_fetch_sha"] = "f"*40
        self.assertIn("DUAL_CHECKOUT_TESTED_MERGE_SHA_DIFFERENT", self.verdict())

    def test_full_sha_absent_from_phase3_runner_log_fails(self):
        self.checkouts[4001].pop("checkout_fetch_sha")
        self.assertIn("phase3-acceptance_RUNNER_FETCH_FULL_SHA_UNREVIEWED",
                      self.verdict())

    def test_short_prefix_cannot_replace_full_sha(self):
        self.checkouts[4000]["checkout_fetch_sha"] = None
        self.assertIn("tests_RUNNER_FETCH_FULL_SHA_UNREVIEWED", self.verdict())

    def test_unknown_phase3_checkout_ref_fails(self):
        self.checkouts[4001]["checkout_ref"] = "refs/remotes/pull/1675/merge"
        self.assertIn("phase3-acceptance_RUNNER_CHECKOUT_REF_UNREVIEWED",
                      self.verdict())

    def test_historical_checkout_sha_prefix_wrong_fails(self):
        self.checkouts[4000]["checkout_sha_prefix"] = "eeeeeee"
        self.assertIn("tests_RUNNER_CHECKOUT_SHA_PREFIX_MISMATCH",
                      self.verdict())

    def test_only_one_workflow_run_cannot_pass(self):
        self.runs.pop()
        self.assertIn("DUAL_CHECKOUT_WORKFLOW_INVENTORY_UNREVIEWED",
                      self.verdict())

    def test_duplicate_workflow_names_cannot_pass(self):
        self.runs[1]["name"] = "tests"
        self.assertIn("tests_RUN_CARDINALITY_UNREVIEWED", self.verdict())

    def test_duplicate_run_ids_cannot_pass(self):
        self.runs[1]["id"] = self.runs[0]["id"]
        self.assertIn("DUAL_CHECKOUT_RUN_ID_UNIQUENESS_UNREVIEWED",
                      self.verdict())

    def test_extra_unaudited_runner_log_snapshot_cannot_pass(self):
        self.checkouts[9999] = dict(self.checkouts[4001])
        self.assertIn("DUAL_CHECKOUT_RUNNER_LOG_INVENTORY_UNREVIEWED",
                      self.verdict())

    def test_missing_historical_runner_log_fails(self):
        self.checkouts.pop(4000)
        self.assertIn("tests_RUNNER_LOG_SNAPSHOT_UNREVIEWED",
                      self.verdict())

    def test_phase3_run_id_in_log_mismatch_fails(self):
        self.checkouts[4001]["run_id"] = 4000
        self.assertIn("phase3-acceptance_RUNNER_LOG_RUN_ASSOCIATION_MISMATCH",
                      self.verdict())

    def test_phase3_workflow_id_impostor_fails(self):
        self.runs[1]["workflow_id"] = 1
        self.assertIn("phase3-acceptance_WORKFLOW_IDENTITY_UNREVIEWED",
                      self.verdict())

    def test_historical_workflow_path_impostor_fails(self):
        self.runs[0]["path"] = ".github/workflows/other.yml"
        self.assertIn("tests_WORKFLOW_IDENTITY_UNREVIEWED", self.verdict())

    def test_retry_attempt_requires_independent_review(self):
        self.runs[1]["run_attempt"] = 2
        self.assertIn("phase3-acceptance_WORKFLOW_IDENTITY_UNREVIEWED",
                      self.verdict())

    def test_failed_historical_run_is_never_trusted(self):
        self.runs[0]["conclusion"] = "failure"
        self.assertIn("tests_RUN_NOT_COMPLETED_SUCCESS", self.verdict())

    def test_changed_merge_commit_tree_is_rejected(self):
        self.merge_commit["tree"]["sha"] = "e"*40
        self.assertIn("tests_MERGE_AND_HEAD_FILE_TREE_MISMATCH",
                      self.verdict())

    def test_absent_historical_head_commit_data_is_rejected(self):
        self.head_commit = None
        self.assertIn("tests_MERGE_CHECKOUT_INPUT_UNREVIEWED", self.verdict())

    def test_consistent_synthetic_dual_checkout_does_not_authorize_2023_run(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict())
