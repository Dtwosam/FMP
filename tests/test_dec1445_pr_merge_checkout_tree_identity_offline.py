"""DEC-1445: distinguish PR head SHA, checkout merge SHA and source tree.

No GitHub API, network, annual workflow dispatch, protected originals,
repository settings changes, merge, broker or trading.
"""
from __future__ import annotations

import re
import unittest

HEX = re.compile(r"[0-9a-f]{40}\Z")


def review_pr_merge_checkout(pr, run, merge_ref, merge_commit, head_commit,
                             checkout_ref, checkout_sha_prefix,
                             checkout_fetch_sha):
    """Consistency-only review of caller-supplied REST and runner log fields."""
    snapshots = (pr, run, merge_ref, merge_commit, head_commit)
    if not all(type(x) is dict for x in snapshots):
        return ("MERGE_CHECKOUT_INPUT_UNREVIEWED",)
    issues = []
    number, base, head = (
        pr.get("number"), pr.get("base_sha"), pr.get("head_sha"))
    if type(number) is not int or number <= 0:
        issues.append("PR_NUMBER_UNREVIEWED")
    if any(type(sha) is not str or HEX.fullmatch(sha) is None
           for sha in (base, head)):
        issues.append("PR_HEAD_BASE_SHA_UNREVIEWED")
    merge_sha = merge_commit.get("sha")
    if type(merge_sha) is not str or HEX.fullmatch(merge_sha) is None:
        issues.append("MERGE_COMMIT_SHA_UNREVIEWED")
    if run.get("event") != "pull_request" or run.get("head_sha") != head:
        issues.append("RUN_HEAD_ASSOCIATION_UNREVIEWED")
    if run.get("status") != "completed" or run.get("conclusion") != "success":
        issues.append("RUN_NOT_COMPLETED_SUCCESS")
    expected_ref = ("refs/pull/" + str(number) + "/merge"
                    if type(number) is int and number > 0 else None)
    if merge_ref.get("ref") != expected_ref:
        issues.append("GITHUB_MERGE_REF_UNREVIEWED")
    ref_object = merge_ref.get("object")
    if not (type(ref_object) is dict and
            ref_object.get("type") == "commit" and
            ref_object.get("sha") == merge_sha):
        issues.append("GITHUB_MERGE_REF_SHA_MISMATCH")
    if head_commit.get("sha") != head:
        issues.append("HEAD_COMMIT_SHA_MISMATCH")
    head_tree = head_commit.get("tree")
    merge_tree = merge_commit.get("tree")
    if not (type(head_tree) is dict and type(merge_tree) is dict and
            type(head_tree.get("sha")) is str and
            HEX.fullmatch(head_tree["sha"]) is not None and
            merge_tree.get("sha") == head_tree["sha"]):
        issues.append("MERGE_AND_HEAD_FILE_TREE_MISMATCH")
    parents = merge_commit.get("parents")
    if not (type(parents) is list and len(parents) == 2 and
            all(type(p) is dict for p in parents) and
            parents[0].get("sha") == base and
            parents[1].get("sha") == head):
        issues.append("MERGE_COMMIT_PARENT_PAIR_UNREVIEWED")
    expected_checkout_ref = ("refs/remotes/pull/" + str(number) + "/merge"
                             if type(number) is int and number > 0 else None)
    if checkout_ref != expected_checkout_ref:
        issues.append("RUNNER_CHECKOUT_REF_UNREVIEWED")
    if not (type(checkout_sha_prefix) is str and
            re.fullmatch(r"[0-9a-f]{7,40}", checkout_sha_prefix) and
            type(merge_sha) is str and
            merge_sha.startswith(checkout_sha_prefix)):
        issues.append("RUNNER_CHECKOUT_SHA_PREFIX_MISMATCH")
    if type(checkout_fetch_sha) is not str or HEX.fullmatch(
            checkout_fetch_sha) is None:
        issues.append("RUNNER_FETCH_FULL_SHA_UNREVIEWED")
    elif checkout_fetch_sha != merge_sha:
        issues.append("RUNNER_FETCH_FULL_SHA_MISMATCH")
    if head == merge_sha:
        issues.append("HEAD_AND_MERGE_COMMIT_UNEXPECTEDLY_EQUAL")
    return tuple(sorted(set(issues)))


class PassingPRCIIsTestedMergeTreeNotStandaloneHead(unittest.TestCase):
    def setUp(self):
        self.head = "7eb566a3448f9fc01ed6a1433714304c19e4568c"
        self.base = "624b002f0de79174b2b9aecb3343f64d5f3e658f"
        self.merge = "5857e06c3cff50243d2ad87c31c55e86a636ea50"
        self.tree = "3ba450896e89baad327a73ca4523b5e0db298ad1"
        self.pr = {"number": 1664, "head_sha": self.head,
                   "base_sha": self.base}
        self.run = {"event": "pull_request", "head_sha": self.head,
                    "status": "completed", "conclusion": "success"}
        self.merge_ref = {
            "ref": "refs/pull/1664/merge",
            "object": {"type": "commit", "sha": self.merge},
        }
        self.merge_commit = {
            "sha": self.merge, "tree": {"sha": self.tree},
            "parents": [{"sha": self.base}, {"sha": self.head}],
        }
        self.head_commit = {"sha": self.head, "tree": {"sha": self.tree}}
        self.checkout_ref = "refs/remotes/pull/1664/merge"
        self.checkout_sha_prefix = "5857e06"
        self.checkout_fetch_sha = self.merge

    def verdict(self):
        return review_pr_merge_checkout(
            self.pr, self.run, self.merge_ref,
            self.merge_commit, self.head_commit, self.checkout_ref,
            self.checkout_sha_prefix, self.checkout_fetch_sha)

    def test_observed_real_1664_merge_tree_and_commit_shape(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotEqual(self.head, self.merge)
        self.assertEqual(self.head_commit["tree"]["sha"],
                         self.merge_commit["tree"]["sha"])

    def test_runner_checkout_wrong_pr_ref_fails(self):
        self.checkout_ref = "refs/remotes/pull/1663/merge"
        self.assertIn("RUNNER_CHECKOUT_REF_UNREVIEWED", self.verdict())

    def test_runner_checkout_head_ref_does_not_pass_merge_proof(self):
        self.checkout_ref = "refs/heads/draft"
        self.assertIn("RUNNER_CHECKOUT_REF_UNREVIEWED", self.verdict())

    def test_runner_checkout_wrong_commit_prefix_fails(self):
        self.checkout_sha_prefix = "7eb566a"
        self.assertIn("RUNNER_CHECKOUT_SHA_PREFIX_MISMATCH", self.verdict())

    def test_unreviewed_short_commit_prefix_fails(self):
        self.checkout_sha_prefix = "585"
        self.assertIn("RUNNER_CHECKOUT_SHA_PREFIX_MISMATCH", self.verdict())

    def test_stale_head_commit_source_tree_fails(self):
        self.head_commit["tree"]["sha"] = "a"*40
        self.assertIn("MERGE_AND_HEAD_FILE_TREE_MISMATCH", self.verdict())

    def test_stale_merge_commit_source_tree_fails(self):
        self.merge_commit["tree"]["sha"] = "b"*40
        self.assertIn("MERGE_AND_HEAD_FILE_TREE_MISMATCH", self.verdict())

    def test_other_pr_head_association_fails(self):
        self.run["head_sha"] = "c"*40
        self.assertIn("RUN_HEAD_ASSOCIATION_UNREVIEWED", self.verdict())

    def test_failed_workflow_is_not_verified(self):
        self.run["conclusion"] = "failure"
        self.assertIn("RUN_NOT_COMPLETED_SUCCESS", self.verdict())

    def test_missing_merge_ref_object_fails(self):
        self.merge_ref.pop("object")
        self.assertIn("GITHUB_MERGE_REF_SHA_MISMATCH", self.verdict())

    def test_merge_ref_wrong_number_fails(self):
        self.merge_ref["ref"] = "refs/pull/1665/merge"
        self.assertIn("GITHUB_MERGE_REF_UNREVIEWED", self.verdict())

    def test_merge_ref_wrong_sha_fails(self):
        self.merge_ref["object"]["sha"] = "d"*40
        self.assertIn("GITHUB_MERGE_REF_SHA_MISMATCH", self.verdict())

    def test_merge_parent_order_swap_fails(self):
        self.merge_commit["parents"].reverse()
        self.assertIn("MERGE_COMMIT_PARENT_PAIR_UNREVIEWED", self.verdict())

    def test_one_parent_commit_is_not_a_pr_merge_commit(self):
        self.merge_commit["parents"].pop()
        self.assertIn("MERGE_COMMIT_PARENT_PAIR_UNREVIEWED", self.verdict())

    def test_bad_head_commit_id_fails(self):
        self.head_commit["sha"] = "e"*40
        self.assertIn("HEAD_COMMIT_SHA_MISMATCH", self.verdict())

    def test_boolean_pr_number_fails(self):
        self.pr["number"] = True
        self.assertIn("PR_NUMBER_UNREVIEWED", self.verdict())

    def test_unknown_snapshot_shape_fails(self):
        self.assertEqual(
            review_pr_merge_checkout([], self.run, self.merge_ref,
                                     self.merge_commit, self.head_commit,
                                     self.checkout_ref,
                                     self.checkout_sha_prefix, self.checkout_fetch_sha),
            ("MERGE_CHECKOUT_INPUT_UNREVIEWED",))

    def test_matching_merge_tree_is_never_a_protected_execution_gate(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict())

    def test_full_fetch_sha_and_merge_object_match(self):
        self.assertEqual(self.checkout_fetch_sha, self.merge)
        self.assertEqual(self.verdict(), ())

    def test_absent_full_fetch_sha_is_rejected(self):
        self.checkout_fetch_sha = None
        self.assertIn("RUNNER_FETCH_FULL_SHA_UNREVIEWED", self.verdict())

    def test_wrong_full_fetched_sha_is_rejected(self):
        self.checkout_fetch_sha = self.head
        self.assertIn("RUNNER_FETCH_FULL_SHA_MISMATCH", self.verdict())

    def test_abbreviated_head_line_alone_is_not_full_identity(self):
        self.checkout_sha_prefix = self.merge[:7]
        self.checkout_fetch_sha = ""
        self.assertIn("RUNNER_FETCH_FULL_SHA_UNREVIEWED", self.verdict())
