"""DEC-1439: offline changed Git blob SHA versus exact supplied source bytes.

No network, runner, GitHub settings, annual execution, protected data,
brokerage or trading. Snapshots/bytes require external authentication.
"""
from __future__ import annotations
import re
import unittest

from test_dec1430_reviewed_ci_workflow_blob_source_identity import git_blob_id
from test_dec1433_strict_draft_ancestry_paths_offline import reviewed_tests_docs_path


def review_changed_blob_byte_identity(compare, nodes, source_bytes):
    if type(compare) is not dict or type(nodes) is not dict or type(source_bytes) is not dict:
        return ("BLOB_REVIEW_INPUT_UNREVIEWED",)
    files = compare.get("files")
    if type(files) is not list or not files or not all(type(f) is dict for f in files):
        return ("BLOB_CHANGED_FILES_UNREVIEWED",)
    issues = []
    paths = []
    for f in files:
        path = f.get("filename")
        if not reviewed_tests_docs_path(path):
            issues.append("BLOB_PATH_UNREVIEWED")
            continue
        if f.get("status") not in ("added", "modified", "renamed"):
            issues.append("BLOB_DELETION_UNREVIEWED")
            continue
        paths.append(path)
        node = nodes.get(path)
        if type(node) is not dict or node.get("type") != "blob" or node.get("mode") != "100644":
            issues.append("BLOB_LEAF_TYPE_UNREVIEWED")
            continue
        sha = node.get("sha")
        if type(sha) is not str or re.fullmatch(r"[0-9a-f]{40}", sha) is None:
            issues.append("BLOB_SHA_UNREVIEWED")
            continue
        data = source_bytes.get(path)
        if type(data) is not bytes:
            issues.append("BLOB_SOURCE_BYTES_UNREVIEWED")
            continue
        if git_blob_id(data) != sha:
            issues.append("BLOB_SOURCE_BYTES_SHA_MISMATCH")
    if len(paths) != len(set(paths)) or set(source_bytes) != set(paths):
        issues.append("BLOB_SOURCE_INVENTORY_UNREVIEWED")
    return tuple(sorted(set(issues)))


class ExactGitObjectBytesAreDistinctFromFilenameChecks(unittest.TestCase):
    def setUp(self):
        self.paths = ["tests/test_review.py", "docs/report.md"]
        self.contents = {
            self.paths[0]: b"def test_gate():\n    assert True\n",
            self.paths[1]: b"# Reviewer evidence\n",
        }
        self.files = [{"filename": p, "status": "added"} for p in self.paths]
        self.nodes = {p: {"mode": "100644", "type": "blob",
                          "sha": git_blob_id(data)}
                      for p, data in self.contents.items()}

    def verdict(self):
        return review_changed_blob_byte_identity(
            {"files": self.files}, self.nodes, self.contents)

    def test_exact_source_bytes_match_reviewed_leaf_objects(self):
        self.assertEqual(self.verdict(), ())

    def test_one_byte_modified_test_source_detected(self):
        self.contents[self.paths[0]] += b"\n"
        self.assertIn("BLOB_SOURCE_BYTES_SHA_MISMATCH", self.verdict())

    def test_one_byte_modified_document_detected(self):
        self.contents[self.paths[1]] += b"x"
        self.assertIn("BLOB_SOURCE_BYTES_SHA_MISMATCH", self.verdict())

    def test_missing_changed_blob_content_detected(self):
        self.contents.pop(self.paths[1])
        self.assertIn("BLOB_SOURCE_BYTES_UNREVIEWED", self.verdict())
        self.assertIn("BLOB_SOURCE_INVENTORY_UNREVIEWED", self.verdict())

    def test_extra_unlisted_source_bytes_detected(self):
        self.contents["tests/unlisted.py"] = b"surprise"
        self.assertIn("BLOB_SOURCE_INVENTORY_UNREVIEWED", self.verdict())

    def test_wrong_node_sha_detected(self):
        self.nodes[self.paths[0]]["sha"] = "a" * 40
        self.assertIn("BLOB_SOURCE_BYTES_SHA_MISMATCH", self.verdict())

    def test_boolean_sha_instead_of_string_detected(self):
        self.nodes[self.paths[0]]["sha"] = True
        self.assertIn("BLOB_SHA_UNREVIEWED", self.verdict())

    def test_symlink_git_mode_detected(self):
        self.nodes[self.paths[0]]["mode"] = "120000"
        self.assertIn("BLOB_LEAF_TYPE_UNREVIEWED", self.verdict())

    def test_gitlink_type_detected(self):
        self.nodes[self.paths[1]]["type"] = "commit"
        self.assertIn("BLOB_LEAF_TYPE_UNREVIEWED", self.verdict())

    def test_source_string_instead_of_bytes_detected(self):
        self.contents[self.paths[0]] = "not reviewed bytes"
        self.assertIn("BLOB_SOURCE_BYTES_UNREVIEWED", self.verdict())

    def test_noncanonical_path_detected(self):
        self.files[0]["filename"] = "tests/../src/fmp/engine.py"
        self.assertIn("BLOB_PATH_UNREVIEWED", self.verdict())

    def test_deleted_file_requires_separate_review(self):
        self.files[0]["status"] = "removed"
        self.assertIn("BLOB_DELETION_UNREVIEWED", self.verdict())

    def test_empty_blob_can_match_its_exact_git_sha(self):
        self.contents[self.paths[1]] = b""
        self.nodes[self.paths[1]]["sha"] = git_blob_id(b"")
        self.assertEqual(self.verdict(), ())

    def test_malformed_compare_snapshot_fails_closed(self):
        self.assertEqual(
            review_changed_blob_byte_identity(None, self.nodes, self.contents),
            ("BLOB_REVIEW_INPUT_UNREVIEWED",))

    def test_extra_duplicate_changed_path_fails_closed(self):
        self.files.append(dict(self.files[0]))
        self.assertIn("BLOB_SOURCE_INVENTORY_UNREVIEWED", self.verdict())

    def test_matching_bytes_are_not_an_annual_execution_gate(self):
        self.assertEqual(self.verdict(), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED", self.verdict())
