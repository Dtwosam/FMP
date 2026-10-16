"""DEC-1433: offline strict one-commit draft ancestry and change-path audit.

Synthetic dicts only. No GitHub API requests, protected originals/archives,
real annual workflow, repository policy changes, or trading.
"""
from __future__ import annotations

import re
import unittest

REPO = "Dtwosam/FMP"


def review_draft_source_lineage(pr: object, compare: object,
                               commit: object) -> tuple[str, ...]:
    """Fail closed on non-one-commit, non test/docs draft lineage."""
    if any(type(x) is not dict for x in (pr, compare, commit)):
        return ("LINEAGE_INPUT_UNREVIEWED",)
    issues = []
    base, head = pr.get("base_sha"), pr.get("head_sha")
    if any(type(s) is not str or not re.fullmatch("[0-9a-f]{40}", s)
           for s in (base, head)):
        return ("LINEAGE_PR_SHA_UNREVIEWED",)
    if pr.get("state") != "open" or pr.get("draft") is not True or pr.get("merged") is not False:
        issues.append("PR_DRAFT_ONLY_UNREVIEWED")
    if type(pr.get("commits")) is not int or pr["commits"] != 1:
        issues.append("PR_ONE_COMMIT_UNREVIEWED")
    if compare.get("repository_full_name") != REPO:
        issues.append("COMPARE_REPOSITORY_UNREVIEWED")
    if compare.get("base") != base or compare.get("head") != head:
        issues.append("COMPARE_REFS_MISMATCH")
    if compare.get("status") != "ahead":
        issues.append("COMPARE_STATUS_UNREVIEWED")
    if any(type(compare.get(key)) is not int or compare[key] != expected
           for key, expected in (("ahead_by", 1), ("behind_by", 0),
                                 ("total_commits", 1))):
        issues.append("COMPARE_NOT_STRICT_ONE_COMMIT_CHILD")
    for key in ("base_commit", "merge_base_commit"):
        value = compare.get(key)
        if type(value) is not dict or value.get("sha") != base:
            issues.append(key.upper() + "_UNREVIEWED")
    if compare.get("too_large") not in (None, False):
        issues.append("COMPARE_TRUNCATED_UNREVIEWED")
    if commit.get("sha") != head:
        issues.append("COMMIT_HEAD_SHA_MISMATCH")
    parents = commit.get("parents")
    if type(parents) is not list or len(parents) != 1 or (
            type(parents[0]) is not dict or parents[0].get("sha") != base):
        issues.append("COMMIT_IMMEDIATE_PARENT_UNREVIEWED")
    files = compare.get("files")
    if type(files) is not list or not files:
        issues.append("CHANGED_FILE_INVENTORY_UNREVIEWED")
    else:
        paths = []
        for file in files:
            if type(file) is not dict:
                issues.append("CHANGED_FILE_METADATA_UNREVIEWED")
                continue
            path, previous = file.get("filename"), file.get("previous_filename")
            if type(path) is not str or not path.startswith(("docs/", "tests/")):
                issues.append("PRODUCTION_OR_WORKFLOW_PATH_UNREVIEWED")
            else:
                paths.append(path)
            if previous is not None and (
                    type(previous) is not str or
                    not previous.startswith(("docs/", "tests/"))):
                issues.append("RENAMED_FROM_PRODUCTION_PATH_UNREVIEWED")
            if file.get("status") not in ("added", "modified", "removed", "renamed"):
                issues.append("FILE_STATUS_UNREVIEWED")
        if len(paths) != len(set(paths)):
            issues.append("DUPLICATE_CHANGED_PATH_UNREVIEWED")
    return tuple(sorted(set(issues)))


class DraftNeverMergeOnlySourceChanges(unittest.TestCase):
    def setUp(self):
        self.base, self.head = "a" * 40, "b" * 40
        self.pr = {
            "base_sha": self.base, "head_sha": self.head, "commits": 1,
            "state": "open", "draft": True, "merged": False,
        }
        self.compare = {
            "repository_full_name": REPO, "base": self.base,
            "head": self.head, "status": "ahead", "ahead_by": 1,
            "behind_by": 0, "total_commits": 1,
            "base_commit": {"sha": self.base},
            "merge_base_commit": {"sha": self.base},
            "too_large": None,
            "files": [
                {"filename": "tests/test_fixture.py", "status": "added",
                 "previous_filename": None},
                {"filename": "docs/review.md", "status": "added",
                 "previous_filename": None},
            ],
        }
        self.commit = {"sha": self.head, "parents": [{"sha": self.base}]}

    def verdict(self):
        return review_draft_source_lineage(self.pr, self.compare, self.commit)

    def test_exact_one_commit_source_only_draft_is_reviewable(self):
        self.assertEqual(self.verdict(), ())

    def test_two_commit_compare_does_not_pass(self):
        self.compare["ahead_by"] = 2
        self.assertIn("COMPARE_NOT_STRICT_ONE_COMMIT_CHILD", self.verdict())

    def test_stale_pr_base_does_not_pass(self):
        self.pr["base_sha"] = "c" * 40
        self.assertIn("COMPARE_REFS_MISMATCH", self.verdict())

    def test_commit_immediate_parent_must_match_pr_base(self):
        self.commit["parents"][0]["sha"] = "c" * 40
        self.assertIn("COMMIT_IMMEDIATE_PARENT_UNREVIEWED", self.verdict())

    def test_merge_commit_cannot_be_strict_one_parent(self):
        self.commit["parents"].append({"sha": "c" * 40})
        self.assertIn("COMMIT_IMMEDIATE_PARENT_UNREVIEWED", self.verdict())

    def test_unreviewed_diff_base_is_rejected(self):
        self.compare["merge_base_commit"]["sha"] = "c" * 40
        self.assertIn("MERGE_BASE_COMMIT_UNREVIEWED", self.verdict())

    def test_unreviewed_compare_repository_is_rejected(self):
        self.compare["repository_full_name"] = "other/FMP"
        self.assertIn("COMPARE_REPOSITORY_UNREVIEWED", self.verdict())

    def test_modified_production_code_path_is_rejected(self):
        self.compare["files"].append({
            "filename": "src/fmp/trading/engine.py", "status": "modified"})
        self.assertIn("PRODUCTION_OR_WORKFLOW_PATH_UNREVIEWED", self.verdict())

    def test_installed_annual_workflow_edit_is_rejected(self):
        self.compare["files"].append({
            "filename": ".github/workflows/phase8a-annual-pattern-catalogue.yml",
            "status": "modified"})
        self.assertIn("PRODUCTION_OR_WORKFLOW_PATH_UNREVIEWED", self.verdict())

    def test_renamed_production_file_into_docs_is_rejected(self):
        self.compare["files"][1] = {
            "filename": "docs/renamed.py", "status": "renamed",
            "previous_filename": "scripts/trading.py"}
        self.assertIn("RENAMED_FROM_PRODUCTION_PATH_UNREVIEWED",
                      self.verdict())

    def test_duplicate_changed_file_paths_are_rejected(self):
        self.compare["files"].append(dict(self.compare["files"][0]))
        self.assertIn("DUPLICATE_CHANGED_PATH_UNREVIEWED", self.verdict())

    def test_non_draft_pr_is_rejected(self):
        self.pr["draft"] = False
        self.assertIn("PR_DRAFT_ONLY_UNREVIEWED", self.verdict())

    def test_missing_changed_file_list_is_rejected(self):
        self.compare.pop("files")
        self.assertIn("CHANGED_FILE_INVENTORY_UNREVIEWED", self.verdict())

    def test_unreviewed_source_type_is_rejected(self):
        self.assertEqual(review_draft_source_lineage([], {}, {}),
                         ("LINEAGE_INPUT_UNREVIEWED",))

    def test_committed_sha_cannot_differ_from_pr_head(self):
        self.commit["sha"] = "c" * 40
        self.assertIn("COMMIT_HEAD_SHA_MISMATCH", self.verdict())

    def test_diff_truncation_is_rejected(self):
        self.compare["too_large"] = True
        self.assertIn("COMPARE_TRUNCATED_UNREVIEWED", self.verdict())

    def test_no_synthetic_lineage_result_grants_annual_dispatch(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict())
