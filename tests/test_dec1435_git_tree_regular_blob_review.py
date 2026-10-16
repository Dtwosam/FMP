"""DEC-1435: offline proof shape for strict changed-file Git modes.

No network, actual annual workflow, archives, source modifications or trading.
Input snapshots must be independently authenticated by another reviewer.
"""
import unittest
from test_dec1433_strict_draft_ancestry_paths_offline import (
    review_draft_source_lineage, reviewed_tests_docs_path,
)


def review_source_tree_mode(pr, compare, commit, root_tree, nodes):
    issues = list(review_draft_source_lineage(pr, compare, commit))
    if type(commit) is not dict or type(root_tree) is not dict:
        return tuple(sorted(set(issues + ["GIT_TREE_SNAPSHOT_UNREVIEWED"])))
    tree = commit.get("tree")
    if not (type(tree) is dict and type(tree.get("sha")) is str and
            root_tree.get("sha") == tree["sha"] and
            root_tree.get("truncated") is False):
        issues.append("COMMIT_TREE_ROOT_UNREVIEWED")
    if type(nodes) is not dict:
        return tuple(sorted(set(issues + ["GIT_TREE_NODES_UNREVIEWED"])))
    files = compare.get("files") if type(compare) is dict else None
    if type(files) is not list:
        return tuple(sorted(set(issues)))
    for f in files:
        if type(f) is not dict:
            continue
        path = f.get("filename")
        if not reviewed_tests_docs_path(path):
            continue
        if f.get("status") not in ("added", "modified", "renamed"):
            issues.append("DELETED_OR_UNREVIEWED_SOURCE_FILE")
            continue
        parts = path.split("/")
        for depth in range(1, len(parts) + 1):
            name = "/".join(parts[:depth])
            node = nodes.get(name)
            if type(node) is not dict:
                issues.append("GIT_TREE_PATH_MISSING")
            elif depth < len(parts):
                if node.get("mode") != "040000" or node.get("type") != "tree":
                    issues.append("GIT_TREE_DIRECTORY_MODE_DRIFT")
            elif node.get("mode") != "100644" or node.get("type") != "blob":
                issues.append("GIT_TREE_LEAF_MODE_DRIFT")
    return tuple(sorted(set(issues)))


class GitObjectTypeIsPartOfSourceOnlyReview(unittest.TestCase):
    def setUp(self):
        self.base, self.head, self.tree = "a"*40, "b"*40, "c"*40
        self.pr = {"base_sha": self.base, "head_sha": self.head,
                   "state": "open", "draft": True, "merged": False, "commits": 1}
        self.compare = {
            "repository_full_name": "Dtwosam/FMP",
            "base": self.base, "head": self.head, "status": "ahead",
            "ahead_by": 1, "behind_by": 0, "total_commits": 1,
            "base_commit": {"sha": self.base},
            "merge_base_commit": {"sha": self.base},
            "too_large": None,
            "files": [{"filename": "tests/reviews/unit.py", "status": "added",
                       "previous_filename": None},
                      {"filename": "docs/receipt.md", "status": "added",
                       "previous_filename": None}],
        }
        self.commit = {"sha": self.head, "parents": [{"sha": self.base}],
                       "tree": {"sha": self.tree}}
        self.root = {"sha": self.tree, "truncated": False}
        self.nodes = {
            "tests": {"mode": "040000", "type": "tree"},
            "tests/reviews": {"mode": "040000", "type": "tree"},
            "tests/reviews/unit.py": {"mode": "100644", "type": "blob"},
            "docs": {"mode": "040000", "type": "tree"},
            "docs/receipt.md": {"mode": "100644", "type": "blob"},
        }

    def verdict(self):
        return review_source_tree_mode(self.pr, self.compare,
                                       self.commit, self.root, self.nodes)

    def test_canonical_regular_changed_files(self):
        self.assertEqual(self.verdict(), ())

    def test_test_symlink_leaf_denied(self):
        self.nodes["tests/reviews/unit.py"]["mode"] = "120000"
        self.assertIn("GIT_TREE_LEAF_MODE_DRIFT", self.verdict())

    def test_submodule_gitlink_denied(self):
        self.nodes["tests/reviews/unit.py"] = {"mode": "160000",
                                               "type": "commit"}
        self.assertIn("GIT_TREE_LEAF_MODE_DRIFT", self.verdict())

    def test_executable_leaf_denied(self):
        self.nodes["tests/reviews/unit.py"]["mode"] = "100755"
        self.assertIn("GIT_TREE_LEAF_MODE_DRIFT", self.verdict())

    def test_symlinked_parent_directory_denied(self):
        self.nodes["docs"] = {"mode": "120000", "type": "blob"}
        self.assertIn("GIT_TREE_DIRECTORY_MODE_DRIFT", self.verdict())

    def test_missing_parent_denied(self):
        self.nodes.pop("tests/reviews")
        self.assertIn("GIT_TREE_PATH_MISSING", self.verdict())

    def test_missing_leaf_denied(self):
        self.nodes.pop("docs/receipt.md")
        self.assertIn("GIT_TREE_PATH_MISSING", self.verdict())

    def test_root_sha_mismatch_denied(self):
        self.root["sha"] = "d"*40
        self.assertIn("COMMIT_TREE_ROOT_UNREVIEWED", self.verdict())

    def test_truncated_tree_denied(self):
        self.root["truncated"] = True
        self.assertIn("COMMIT_TREE_ROOT_UNREVIEWED", self.verdict())

    def test_missing_tree_snapshot_denied(self):
        self.assertIn("GIT_TREE_SNAPSHOT_UNREVIEWED",
                      review_source_tree_mode(self.pr, self.compare,
                                              self.commit, None, self.nodes))

    def test_missing_node_inventory_denied(self):
        self.assertIn("GIT_TREE_NODES_UNREVIEWED",
                      review_source_tree_mode(self.pr, self.compare,
                                              self.commit, self.root, None))

    def test_removed_test_file_requires_special_review(self):
        self.compare["files"][0]["status"] = "removed"
        self.assertIn("DELETED_OR_UNREVIEWED_SOURCE_FILE", self.verdict())

    def test_renamed_production_path_already_denied(self):
        self.compare["files"][0]["status"] = "renamed"
        self.compare["files"][0]["previous_filename"] = "src/fmp/annual.py"
        self.assertIn("RENAMED_FROM_PRODUCTION_PATH_UNREVIEWED", self.verdict())

    def test_backtracking_filename_already_denied(self):
        self.compare["files"][0]["filename"] = "tests/../src/runtime.py"
        self.assertIn("PRODUCTION_OR_WORKFLOW_PATH_UNREVIEWED", self.verdict())

    def test_nonmatching_commit_root_denied(self):
        self.commit["tree"]["sha"] = "d"*40
        self.assertIn("COMMIT_TREE_ROOT_UNREVIEWED", self.verdict())

    def test_passing_source_fixtures_are_not_execution_permission(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict())
