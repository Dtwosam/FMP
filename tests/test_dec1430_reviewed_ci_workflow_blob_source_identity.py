"""DEC-1430: source-only CI workflow definition byte identity inventory.

Pure local Git object reads; no GitHub API, workflow dispatch, historical
artifact reads, production code, original data, or trading.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
REVIEWED_CI_BLOBS = {
    ".github/workflows/tests.yml": "e80c05a17b00311640fb96bc8aa09b01f2f3425e",
    ".github/workflows/phase3-acceptance.yml":
        "969240049d434b30ea52f089710d7e0d511d9072",
}


def git_blob_id(data: object) -> str | None:
    """Calculate SHA-1 Git blob ID, without invoking a live GitHub endpoint."""
    if type(data) is not bytes:
        return None
    header = ("blob " + str(len(data))).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def review_ci_workflow_blobs(contents: object) -> tuple[str, ...]:
    """Explicitly pin exact reviewed CI YAML bytes, not just workflow names."""
    if type(contents) is not dict:
        return ("CI_SOURCE_INVENTORY_UNREVIEWED",)
    if set(contents) != set(REVIEWED_CI_BLOBS):
        return ("CI_SOURCE_INVENTORY_UNREVIEWED",)
    issues = []
    for path, expected in REVIEWED_CI_BLOBS.items():
        actual = git_blob_id(contents[path])
        if actual != expected:
            issues.append(path + "_BLOB_IDENTITY_UNREVIEWED")
    return tuple(sorted(set(issues)))


def checked_in_ci_sources() -> dict[str, bytes]:
    return {
        path: subprocess.check_output(
            ["git", "show", "HEAD:" + path],
            cwd=ROOT,
        )
        for path in REVIEWED_CI_BLOBS
    }


class GitHubCIResultNeedsReviewedCIWorkflowDefinitions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = checked_in_ci_sources()

    def test_both_checked_in_ci_workflow_blobs_have_reviewed_identity(self):
        self.assertEqual(review_ci_workflow_blobs(self.sources), ())

    def test_pinned_definition_scope_has_exactly_two_workflows(self):
        self.assertEqual(set(REVIEWED_CI_BLOBS), {
            ".github/workflows/tests.yml",
            ".github/workflows/phase3-acceptance.yml",
        })

    def test_git_blob_function_handles_binary_bytes_as_exact_identity(self):
        self.assertEqual(git_blob_id(b""), hashlib.sha1(b"blob 0\0").hexdigest())

    def test_git_blob_function_refuses_strings_instead_of_bytes(self):
        self.assertIsNone(git_blob_id("text"))

    def test_one_byte_historical_ci_workflow_change_is_rejected(self):
        changed = dict(self.sources)
        key = ".github/workflows/tests.yml"
        changed[key] = changed[key] + b"\n"
        self.assertIn(key + "_BLOB_IDENTITY_UNREVIEWED",
                      review_ci_workflow_blobs(changed))

    def test_one_byte_phase3_ci_workflow_change_is_rejected(self):
        changed = dict(self.sources)
        key = ".github/workflows/phase3-acceptance.yml"
        changed[key] = changed[key].replace(b"name: phase3-acceptance",
                                          b"name: phase3-acceptance-altered", 1)
        self.assertIn(key + "_BLOB_IDENTITY_UNREVIEWED",
                      review_ci_workflow_blobs(changed))

    def test_missing_tests_workflow_is_rejected(self):
        changed = dict(self.sources)
        changed.pop(".github/workflows/tests.yml")
        self.assertEqual(review_ci_workflow_blobs(changed),
                         ("CI_SOURCE_INVENTORY_UNREVIEWED",))

    def test_unreviewed_third_workflow_is_rejected(self):
        changed = dict(self.sources)
        changed[".github/workflows/altered.yml"] = b"on: push\n"
        self.assertEqual(review_ci_workflow_blobs(changed),
                         ("CI_SOURCE_INVENTORY_UNREVIEWED",))

    def test_workflow_bytes_replaced_by_string_are_rejected(self):
        changed = dict(self.sources)
        changed[".github/workflows/tests.yml"] = "unreviewed"
        self.assertIn(
            ".github/workflows/tests.yml_BLOB_IDENTITY_UNREVIEWED",
            review_ci_workflow_blobs(changed),
        )

    def test_workflow_blob_ids_are_lowercase_forty_hex_digits(self):
        import re
        for blob in REVIEWED_CI_BLOBS.values():
            self.assertIsNotNone(re.fullmatch(r"[0-9a-f]{40}", blob))

    def test_exact_source_bytes_not_file_name_alone_are_required(self):
        changed = {name: b"" for name in self.sources}
        verdict = review_ci_workflow_blobs(changed)
        self.assertEqual(len(verdict), 2)

    def test_invalid_container_is_not_accepted(self):
        self.assertEqual(review_ci_workflow_blobs(None),
                         ("CI_SOURCE_INVENTORY_UNREVIEWED",))

    def test_source_identity_is_not_original_no_write_proof(self):
        self.assertEqual(review_ci_workflow_blobs(self.sources), ())
        self.assertNotIn("ORIGINAL_OS_NO_WRITE_PROVEN",
                         review_ci_workflow_blobs(self.sources))

    def test_source_identity_is_not_run385_dispatch_consent(self):
        self.assertEqual(review_ci_workflow_blobs(self.sources), ())
        self.assertNotIn("ANNUAL_DISPATCH_AUTHORIZED",
                         review_ci_workflow_blobs(self.sources))
