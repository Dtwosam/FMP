"""DEC-1425: offline exact PR association of the two required CI runs.

Only test-created Python dicts are examined. No network, protected artifacts,
annual workflow dispatch, credentials, GitHub settings, or broker/trading.
"""
from __future__ import annotations

import re
import unittest

from test_dec1422_offline_exact_head_ci_evidence_review import (
    WORKFLOWS, REQUIRED, review_exact_head_ci,
)

REPO = "Dtwosam/FMP"


def review_exact_pr_ci(pr: object, runs: object) -> tuple[str, ...]:
    """Fail-closed inspection of caller-supplied PR and full-run JSON shapes.

    This is consistency checking, not authentication or execution authority.
    """
    if type(pr) is not dict:
        return ("PR_SNAPSHOT_UNREVIEWED",)
    sha = pr.get("head_sha")
    if type(sha) is not str or not re.fullmatch(r"[0-9a-f]{40}", sha):
        return ("PR_HEAD_SHA_UNREVIEWED",)
    issues = []
    number = pr.get("number")
    if type(number) is not int or number <= 0:
        issues.append("PR_NUMBER_UNREVIEWED")
    branch = pr.get("head_branch")
    if type(branch) is not str or not branch.startswith("draft/"):
        issues.append("PR_HEAD_BRANCH_UNREVIEWED")
    base_sha = pr.get("base_sha")
    if type(base_sha) is not str or not re.fullmatch(r"[0-9a-f]{40}", base_sha):
        issues.append("PR_BASE_SHA_UNREVIEWED")
    if pr.get("repository") != REPO:
        issues.append("PR_REPOSITORY_UNREVIEWED")
    if pr.get("state") != "open" or pr.get("draft") is not True or pr.get("merged") is not False:
        issues.append("PR_DRAFT_STATE_UNREVIEWED")
    if type(pr.get("commits")) is not int or pr["commits"] != 1:
        issues.append("PR_COMMIT_COUNT_UNREVIEWED")
    issues.extend(review_exact_head_ci(sha, runs))
    if type(runs) is not list or not all(type(r) is dict for r in runs):
        return tuple(sorted(set(issues)))
    for name in REQUIRED:
        matched = [r for r in runs if r.get("name") == name]
        if len(matched) != 1:
            continue
        run = matched[0]
        if not (type(run.get("repository")) is dict and
                run["repository"].get("full_name") == REPO):
            issues.append(name + "_REPOSITORY_UNREVIEWED")
        if not (type(run.get("head_repository")) is dict and
                run["head_repository"].get("full_name") == REPO):
            issues.append(name + "_HEAD_REPOSITORY_UNREVIEWED")
        if run.get("head_branch") != branch:
            issues.append(name + "_HEAD_BRANCH_MISMATCH")
        linked = run.get("pull_requests")
        if type(linked) is not list or len(linked) != 1 or type(linked[0]) is not dict:
            issues.append(name + "_PR_ASSOCIATION_UNREVIEWED")
            continue
        assoc = linked[0]
        if type(assoc.get("number")) is not int or assoc["number"] != number:
            issues.append(name + "_PR_NUMBER_MISMATCH")
        head = assoc.get("head")
        base = assoc.get("base")
        if not (type(head) is dict and head.get("sha") == sha):
            issues.append(name + "_PR_HEAD_ASSOCIATION_MISMATCH")
        if not (type(base) is dict and base.get("sha") == base_sha):
            issues.append(name + "_PR_BASE_ASSOCIATION_MISMATCH")
    return tuple(sorted(set(issues)))


class ExactCommitCIIsNotRun385Permission(unittest.TestCase):
    def setUp(self):
        self.sha = "a" * 40
        self.base = "b" * 40
        self.branch = "draft/dec1425-synthetic"
        self.pr = {
            "number": 1649, "head_sha": self.sha, "base_sha": self.base,
            "head_branch": self.branch, "repository": REPO,
            "state": "open", "draft": True, "merged": False, "commits": 1,
        }
        self.runs = [
            {
                "name": name, "id": 8000+i, "run_number": 300+i,
                "head_sha": self.sha, "head_branch": self.branch,
                "event": "pull_request", "status": "completed",
                "conclusion": "success", "workflow_id": WORKFLOWS[name][0],
                "path": WORKFLOWS[name][1], "run_attempt": 1,
                "repository": {"full_name": REPO},
                "head_repository": {"full_name": REPO},
                "pull_requests": [
                    {"number": 1649, "head": {"sha": self.sha},
                     "base": {"sha": self.base}}
                ],
            }
            for i, name in enumerate(REQUIRED)
        ]

    def test_matching_two_full_runs_and_draft_pr(self):
        self.assertEqual(review_exact_pr_ci(self.pr, self.runs), ())

    def test_wrong_pr_number_association(self):
        self.runs[1]["pull_requests"][0]["number"] = 999
        self.assertIn("tests_PR_NUMBER_MISMATCH", review_exact_pr_ci(self.pr, self.runs))

    def test_stale_pr_head_sha_association(self):
        self.runs[0]["pull_requests"][0]["head"]["sha"] = "c" * 40
        self.assertIn("phase3-acceptance_PR_HEAD_ASSOCIATION_MISMATCH",
                      review_exact_pr_ci(self.pr, self.runs))

    def test_stale_pr_base_sha_association(self):
        self.runs[1]["pull_requests"][0]["base"]["sha"] = "c" * 40
        self.assertIn("tests_PR_BASE_ASSOCIATION_MISMATCH",
                      review_exact_pr_ci(self.pr, self.runs))

    def test_other_repo_full_run_is_not_green(self):
        self.runs[0]["repository"]["full_name"] = "other/FMP"
        self.assertIn("phase3-acceptance_REPOSITORY_UNREVIEWED",
                      review_exact_pr_ci(self.pr, self.runs))

    def test_fork_or_unreviewed_head_repository_is_not_green(self):
        self.runs[1]["head_repository"]["full_name"] = "other/FMP"
        self.assertIn("tests_HEAD_REPOSITORY_UNREVIEWED",
                      review_exact_pr_ci(self.pr, self.runs))

    def test_changed_run_branch_is_not_green(self):
        self.runs[1]["head_branch"] = "main"
        self.assertIn("tests_HEAD_BRANCH_MISMATCH",
                      review_exact_pr_ci(self.pr, self.runs))

    def test_empty_pr_association_is_not_green(self):
        self.runs[0]["pull_requests"] = []
        self.assertIn("phase3-acceptance_PR_ASSOCIATION_UNREVIEWED",
                      review_exact_pr_ci(self.pr, self.runs))

    def test_duplicate_pr_associations_are_unreviewed(self):
        self.runs[1]["pull_requests"].append(
            dict(self.runs[1]["pull_requests"][0]))
        self.assertIn("tests_PR_ASSOCIATION_UNREVIEWED",
                      review_exact_pr_ci(self.pr, self.runs))

    def test_non_draft_pr_is_not_valid_lineage_evidence(self):
        self.pr["draft"] = False
        self.assertIn("PR_DRAFT_STATE_UNREVIEWED",
                      review_exact_pr_ci(self.pr, self.runs))

    def test_two_commit_pr_is_not_one_commit_child(self):
        self.pr["commits"] = 2
        self.assertIn("PR_COMMIT_COUNT_UNREVIEWED",
                      review_exact_pr_ci(self.pr, self.runs))

    def test_wrong_pr_repository_is_rejected(self):
        self.pr["repository"] = "other/FMP"
        self.assertIn("PR_REPOSITORY_UNREVIEWED",
                      review_exact_pr_ci(self.pr, self.runs))

    def test_wrong_pr_head_branch_is_rejected(self):
        self.pr["head_branch"] = "main"
        self.assertIn("PR_HEAD_BRANCH_UNREVIEWED",
                      review_exact_pr_ci(self.pr, self.runs))

    def test_wrong_pr_snapshot_type_is_rejected(self):
        self.assertEqual(review_exact_pr_ci([], self.runs),
                         ("PR_SNAPSHOT_UNREVIEWED",))

    def test_unknown_run_snapshot_is_rejected(self):
        self.assertIn("RUN_SNAPSHOT_UNREVIEWED",
                      review_exact_pr_ci(self.pr, {}))

    def test_invalid_pr_number_does_not_become_valid(self):
        self.pr["number"] = True
        self.assertIn("PR_NUMBER_UNREVIEWED",
                      review_exact_pr_ci(self.pr, self.runs))

    def test_missing_pr_association_base_does_not_become_valid(self):
        self.runs[0]["pull_requests"][0].pop("base")
        self.assertIn("phase3-acceptance_PR_BASE_ASSOCIATION_MISMATCH",
                      review_exact_pr_ci(self.pr, self.runs))

    def test_successful_synthetic_pr_approval_never_authorizes_execution(self):
        self.assertEqual(review_exact_pr_ci(self.pr, self.runs), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED",
                         review_exact_pr_ci(self.pr, self.runs))
