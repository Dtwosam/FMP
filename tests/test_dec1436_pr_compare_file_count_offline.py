"""DEC-1436: offline PR changed-file counts vs exact one-commit compare.

Synthetic source evidence only. No network, protected annual execution,
historical originals or brokerage/trading interactions.
"""
import unittest
from test_dec1433_strict_draft_ancestry_paths_offline import (
    review_draft_source_lineage,
)


def review_draft_file_inventory_counts(pr, compare, commit):
    issues = list(review_draft_source_lineage(pr, compare, commit))
    if type(pr) is not dict or type(compare) is not dict:
        return tuple(sorted(set(issues + ["DIFF_COUNT_INPUT_UNREVIEWED"])))
    files = compare.get("files")
    expected = pr.get("changed_files")
    if type(expected) is not int or expected <= 0:
        issues.append("PR_CHANGED_FILE_COUNT_UNREVIEWED")
    if type(files) is not list or not all(type(f) is dict for f in files):
        return tuple(sorted(set(issues + ["COMPARE_FILE_LIST_UNREVIEWED"])))
    if type(expected) is int and expected != len(files):
        issues.append("PR_COMPARE_FILE_COUNT_MISMATCH")
    added = deleted = 0
    for file in files:
        additions, deletions, changes = (
            file.get("additions"), file.get("deletions"), file.get("changes"))
        if any(type(n) is not int or n < 0
               for n in (additions, deletions, changes)):
            issues.append("COMPARE_FILE_LINE_COUNTS_UNREVIEWED")
            continue
        if changes != additions + deletions:
            issues.append("COMPARE_FILE_TOTAL_LINES_MISMATCH")
        added += additions
        deleted += deletions
    for name, actual in (("additions", added), ("deletions", deleted)):
        claimed = pr.get(name)
        if type(claimed) is not int or claimed < 0:
            issues.append("PR_" + name.upper() + "_UNREVIEWED")
        elif claimed != actual:
            issues.append("PR_COMPARE_" + name.upper() + "_MISMATCH")
    return tuple(sorted(set(issues)))


class ExactDiffNoHiddenFilesOrCounts(unittest.TestCase):
    def setUp(self):
        self.base, self.head = "a" * 40, "b" * 40
        self.pr = {
            "base_sha": self.base, "head_sha": self.head,
            "state": "open", "draft": True, "merged": False,
            "commits": 1, "changed_files": 2,
            "additions": 23, "deletions": 3,
        }
        self.compare = {
            "repository_full_name": "Dtwosam/FMP",
            "base": self.base, "head": self.head,
            "status": "ahead", "ahead_by": 1, "behind_by": 0,
            "total_commits": 1, "too_large": None,
            "base_commit": {"sha": self.base},
            "merge_base_commit": {"sha": self.base},
            "files": [
                {"filename": "tests/unit.py", "status": "modified",
                 "previous_filename": None,
                 "additions": 19, "deletions": 3, "changes": 22},
                {"filename": "docs/handoff.md", "status": "added",
                 "previous_filename": None,
                 "additions": 4, "deletions": 0, "changes": 4},
            ],
        }
        self.commit = {"sha": self.head, "parents": [{"sha": self.base}]}

    def verdict(self):
        return review_draft_file_inventory_counts(
            self.pr, self.compare, self.commit)

    def test_exact_two_file_source_diff_is_consistent(self):
        self.assertEqual(self.verdict(), ())

    def test_pr_claims_one_fewer_changed_file_is_blocked(self):
        self.pr["changed_files"] = 1
        self.assertIn("PR_COMPARE_FILE_COUNT_MISMATCH", self.verdict())

    def test_pr_claims_one_more_changed_file_is_blocked(self):
        self.pr["changed_files"] = 3
        self.assertIn("PR_COMPARE_FILE_COUNT_MISMATCH", self.verdict())

    def test_missing_file_count_is_blocked(self):
        self.pr.pop("changed_files")
        self.assertIn("PR_CHANGED_FILE_COUNT_UNREVIEWED", self.verdict())

    def test_boolean_file_count_is_not_integer_evidence(self):
        self.pr["changed_files"] = True
        self.assertIn("PR_CHANGED_FILE_COUNT_UNREVIEWED", self.verdict())

    def test_missing_compare_file_entry_is_blocked(self):
        self.compare["files"].pop()
        self.assertIn("PR_COMPARE_FILE_COUNT_MISMATCH", self.verdict())

    def test_pr_additions_mismatch_is_blocked(self):
        self.pr["additions"] += 1
        self.assertIn("PR_COMPARE_ADDITIONS_MISMATCH", self.verdict())

    def test_pr_deletions_mismatch_is_blocked(self):
        self.pr["deletions"] += 1
        self.assertIn("PR_COMPARE_DELETIONS_MISMATCH", self.verdict())

    def test_boolean_pr_line_total_is_blocked(self):
        self.pr["additions"] = False
        self.assertIn("PR_ADDITIONS_UNREVIEWED", self.verdict())

    def test_file_changes_must_equal_additions_plus_deletions(self):
        self.compare["files"][0]["changes"] += 1
        self.assertIn("COMPARE_FILE_TOTAL_LINES_MISMATCH", self.verdict())

    def test_negative_file_line_count_is_blocked(self):
        self.compare["files"][0]["deletions"] = -3
        self.assertIn("COMPARE_FILE_LINE_COUNTS_UNREVIEWED", self.verdict())

    def test_missing_file_line_count_is_blocked(self):
        self.compare["files"][1].pop("additions")
        self.assertIn("COMPARE_FILE_LINE_COUNTS_UNREVIEWED", self.verdict())

    def test_boolean_file_line_count_is_blocked(self):
        self.compare["files"][0]["changes"] = True
        self.assertIn("COMPARE_FILE_LINE_COUNTS_UNREVIEWED", self.verdict())

    def test_non_source_file_still_blocked_by_parent_reviewer(self):
        self.compare["files"][0]["filename"] = "src/fmp/runtime.py"
        self.assertIn("PRODUCTION_OR_WORKFLOW_PATH_UNREVIEWED", self.verdict())

    def test_two_commit_compare_still_blocked(self):
        self.compare["total_commits"] = 2
        self.assertIn("COMPARE_NOT_STRICT_ONE_COMMIT_CHILD", self.verdict())

    def test_a_synthetic_matching_diff_never_authorizes_annual_run(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict())
