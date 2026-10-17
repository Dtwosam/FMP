"""DEC-1441: bind each changed Git blob to exact parent-child tree entries.

Caller-supplied full Git tree snapshots and bytes only. No networking, annual
workflow execution, protected historical sources, or trading action.
"""
from __future__ import annotations

import re
import unittest

from test_dec1433_strict_draft_ancestry_paths_offline import (
    reviewed_tests_docs_path,
)
from test_dec1430_reviewed_ci_workflow_blob_source_identity import git_blob_id
from test_dec1443_git_tree_object_wire_identity import reviewed_git_tree_sha

SHA = re.compile(r"[0-9a-f]{40}\Z")


def review_exact_changed_tree_chain(commit, compare, tree_snapshots,
                                    source_bytes) -> tuple[str, ...]:
    """Conservative tree entry-to-subtree SHA continuity and final bytes."""
    if any(type(x) is not dict for x in (
            commit, compare, tree_snapshots, source_bytes)):
        return ("TREE_CHAIN_INPUT_UNREVIEWED",)
    root = commit.get("tree")
    if type(root) is not dict or type(root.get("sha")) is not str or (
            SHA.fullmatch(root["sha"]) is None):
        return ("TREE_CHAIN_ROOT_SHA_UNREVIEWED",)
    files = compare.get("files")
    if type(files) is not list or not files or not all(
            type(f) is dict for f in files):
        return ("TREE_CHAIN_CHANGED_FILES_UNREVIEWED",)
    issues = []
    observed_paths = []
    used_trees = set()
    for file in files:
        path = file.get("filename")
        if not reviewed_tests_docs_path(path):
            issues.append("TREE_CHAIN_CHANGED_PATH_UNREVIEWED")
            continue
        if file.get("status") not in ("added", "modified", "renamed"):
            issues.append("TREE_CHAIN_CHANGE_STATUS_UNREVIEWED")
            continue
        observed_paths.append(path)
        sha = root["sha"]
        for index, part in enumerate(path.split("/")):
            used_trees.add(sha)
            snapshot = tree_snapshots.get(sha)
            if (type(snapshot) is not dict or snapshot.get("sha") != sha or
                    snapshot.get("truncated") is not False):
                issues.append("TREE_CHAIN_TREE_OBJECT_UNREVIEWED")
                break
            entries = snapshot.get("tree")
            if type(entries) is not list or not all(
                    type(entry) is dict for entry in entries):
                issues.append("TREE_CHAIN_TREE_ENTRIES_UNREVIEWED")
                break
            if reviewed_git_tree_sha(entries) != sha:
                issues.append("TREE_CHAIN_OBJECT_BYTES_SHA_MISMATCH")
            found = [entry for entry in entries if entry.get("path") == part]
            if len(found) != 1:
                issues.append("TREE_CHAIN_ENTRY_CARDINALITY_UNREVIEWED")
                break
            entry = found[0]
            entry_sha = entry.get("sha")
            if type(entry_sha) is not str or SHA.fullmatch(entry_sha) is None:
                issues.append("TREE_CHAIN_ENTRY_SHA_UNREVIEWED")
                break
            last = index == len(path.split("/")) - 1
            if not last:
                if entry.get("type") != "tree" or entry.get("mode") != "040000":
                    issues.append("TREE_CHAIN_PARENT_NOT_REGULAR_TREE")
                    break
                sha = entry_sha
            else:
                if entry.get("type") != "blob" or entry.get("mode") != "100644":
                    issues.append("TREE_CHAIN_LEAF_NOT_REGULAR_BLOB")
                data = source_bytes.get(path)
                if type(data) is not bytes:
                    issues.append("TREE_CHAIN_CHANGED_BYTES_UNREVIEWED")
                elif git_blob_id(data) != entry_sha:
                    issues.append("TREE_CHAIN_LEAF_BYTES_SHA_MISMATCH")
    if len(observed_paths) != len(set(observed_paths)):
        issues.append("TREE_CHAIN_DUPLICATE_CHANGED_PATH")
    if set(source_bytes) != set(observed_paths):
        issues.append("TREE_CHAIN_SOURCE_BYTE_INVENTORY_UNREVIEWED")
    if set(tree_snapshots) != used_trees:
        issues.append("TREE_CHAIN_TREE_SNAPSHOT_INVENTORY_UNREVIEWED")
    return tuple(sorted(set(issues)))


class ExactTreeParentChildBindingCannotConferAnnualPermission(unittest.TestCase):
    def setUp(self):
        self.root = "a"*40
        self.tests = "b"*40
        self.nested = "c"*40
        self.docs = "d"*40
        self.commit = {"tree": {"sha": self.root}}
        self.file_names = ["tests/unit/check.py", "docs/review.md"]
        self.contents = {
            self.file_names[0]: b"def test_synthetic():\n    assert True\n",
            self.file_names[1]: b"# synthetic\n",
        }
        self.compare = {"files": [
            {"filename": name, "status": "added"} for name in self.file_names
        ]}
        self.trees = {
            self.root: {
                "sha": self.root, "truncated": False,
                "tree": [
                    {"path": "tests", "type": "tree", "mode": "040000",
                     "sha": self.tests},
                    {"path": "docs", "type": "tree", "mode": "040000",
                     "sha": self.docs},
                ],
            },
            self.tests: {
                "sha": self.tests, "truncated": False,
                "tree": [{"path": "unit", "type": "tree", "mode": "040000",
                          "sha": self.nested}],
            },
            self.nested: {
                "sha": self.nested, "truncated": False,
                "tree": [{"path": "check.py", "type": "blob", "mode": "100644",
                          "sha": git_blob_id(self.contents[self.file_names[0]])}],
            },
            self.docs: {
                "sha": self.docs, "truncated": False,
                "tree": [{"path": "review.md", "type": "blob", "mode": "100644",
                          "sha": git_blob_id(self.contents[self.file_names[1]])}],
            },
        }

        # Build true Git hashes for every fixture tree, bottom-up.
        nested = self.trees.pop(self.nested)
        self.nested = reviewed_git_tree_sha(nested["tree"])
        nested["sha"] = self.nested
        self.trees[self.nested] = nested
        docs = self.trees.pop(self.docs)
        self.docs = reviewed_git_tree_sha(docs["tree"])
        docs["sha"] = self.docs
        self.trees[self.docs] = docs
        tests = self.trees.pop(self.tests)
        tests["tree"][0]["sha"] = self.nested
        self.tests = reviewed_git_tree_sha(tests["tree"])
        tests["sha"] = self.tests
        self.trees[self.tests] = tests
        root = self.trees.pop(self.root)
        for entry in root["tree"]:
            entry["sha"] = self.tests if entry["path"] == "tests" else self.docs
        root["tree"].sort(key=lambda e: e["path"].encode("utf-8") +
                          (b"/" if e["mode"] == "040000" else b""))
        self.root = reviewed_git_tree_sha(root["tree"])
        root["sha"] = self.root
        self.trees[self.root] = root
        self.commit["tree"]["sha"] = self.root

    def verdict(self):
        return review_exact_changed_tree_chain(
            self.commit, self.compare, self.trees, self.contents)

    def test_matching_multilevel_parent_child_git_tree_chain(self):
        self.assertEqual(self.verdict(), ())

    def test_root_commit_tree_pointer_mismatch(self):
        self.commit["tree"]["sha"] = "f"*40
        self.assertIn("TREE_CHAIN_TREE_OBJECT_UNREVIEWED", self.verdict())

    def test_root_parent_tree_symlink_mode(self):
        self.trees[self.root]["tree"][0]["mode"] = "120000"
        self.assertIn("TREE_CHAIN_PARENT_NOT_REGULAR_TREE", self.verdict())

    def test_nested_parent_tree_gitlink_mode(self):
        self.trees[self.tests]["tree"][0]["mode"] = "160000"
        self.assertIn("TREE_CHAIN_PARENT_NOT_REGULAR_TREE", self.verdict())

    def test_nested_tree_sha_pointer_forgery(self):
        self.trees[self.tests]["tree"][0]["sha"] = "e"*40
        self.assertIn("TREE_CHAIN_TREE_OBJECT_UNREVIEWED", self.verdict())

    def test_missing_nested_tree_snapshot(self):
        self.trees.pop(self.nested)
        self.assertIn("TREE_CHAIN_TREE_OBJECT_UNREVIEWED", self.verdict())

    def test_truncated_subtree_is_not_accepted(self):
        self.trees[self.tests]["truncated"] = True
        self.assertIn("TREE_CHAIN_TREE_OBJECT_UNREVIEWED", self.verdict())

    def test_wrong_tree_object_self_sha_is_not_accepted(self):
        self.trees[self.docs]["sha"] = "e"*40
        self.assertIn("TREE_CHAIN_TREE_OBJECT_UNREVIEWED", self.verdict())

    def test_duplicate_directory_entry_is_rejected(self):
        self.trees[self.root]["tree"].append(
            dict(self.trees[self.root]["tree"][0]))
        self.assertIn("TREE_CHAIN_ENTRY_CARDINALITY_UNREVIEWED",
                      self.verdict())

    def test_symlink_leaf_is_not_accepted(self):
        self.trees[self.nested]["tree"][0]["mode"] = "120000"
        self.assertIn("TREE_CHAIN_LEAF_NOT_REGULAR_BLOB", self.verdict())

    def test_gitlink_leaf_is_not_accepted(self):
        self.trees[self.docs]["tree"][0]["type"] = "commit"
        self.assertIn("TREE_CHAIN_LEAF_NOT_REGULAR_BLOB", self.verdict())

    def test_source_one_byte_mutation_is_rejected(self):
        self.contents[self.file_names[0]] += b" "
        self.assertIn("TREE_CHAIN_LEAF_BYTES_SHA_MISMATCH", self.verdict())

    def test_missing_changed_bytes_are_rejected(self):
        self.contents.pop(self.file_names[1])
        self.assertIn("TREE_CHAIN_CHANGED_BYTES_UNREVIEWED",
                      self.verdict())

    def test_extra_tree_snapshots_are_rejected(self):
        self.trees["e"*40] = {
            "sha": "e"*40, "truncated": False, "tree": []}
        self.assertIn("TREE_CHAIN_TREE_SNAPSHOT_INVENTORY_UNREVIEWED",
                      self.verdict())

    def test_duplicate_changed_paths_are_rejected(self):
        self.compare["files"].append(dict(self.compare["files"][0]))
        self.assertIn("TREE_CHAIN_DUPLICATE_CHANGED_PATH", self.verdict())

    def test_unreviewed_dotdot_path_is_rejected(self):
        self.compare["files"][0]["filename"] = "tests/../src/trading.py"
        self.assertIn("TREE_CHAIN_CHANGED_PATH_UNREVIEWED", self.verdict())

    def test_renamed_and_modified_source_files_are_eligible(self):
        self.compare["files"][0]["status"] = "modified"
        self.compare["files"][1]["status"] = "renamed"
        self.assertEqual(self.verdict(), ())

    def test_synthetically_consistent_chain_never_authorizes_run385(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict())

    def test_altered_full_subtree_contents_cannot_keep_claimed_sha(self):
        self.trees[self.nested]["tree"][0]["path"] = "forged.py"
        self.assertIn("TREE_CHAIN_OBJECT_BYTES_SHA_MISMATCH",
                      self.verdict())

    def test_reordered_root_entries_cannot_keep_claimed_sha(self):
        self.trees[self.root]["tree"].reverse()
        self.assertIn("TREE_CHAIN_OBJECT_BYTES_SHA_MISMATCH",
                      self.verdict())

    def test_new_sibling_object_requires_recomputed_parent_hash(self):
        self.trees[self.docs]["tree"].append({
            "path": "z-extra.md", "mode": "100644", "type": "blob",
            "sha": "e"*40})
        self.assertIn("TREE_CHAIN_OBJECT_BYTES_SHA_MISMATCH",
                      self.verdict())
