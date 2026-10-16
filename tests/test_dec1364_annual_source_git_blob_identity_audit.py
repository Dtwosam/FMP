"""Source-fidelity audit only: Git object hashes are NOT dispatch authorization.

These tests never dispatch workflows or open the protected annual dataset.
They ensure the SOURCE text being characterized in the draft regression
lineage is the reviewed checked-in Git blob, not a mutated checkout file.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


def committed_blob_sha(path: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD:" + path],
        cwd=ROOT, text=True, stderr=subprocess.PIPE,
    ).strip()


class TrackedAnnualSourceBlobFingerprintsAreNotAdmission(unittest.TestCase):
    def test_actual_annual_workflow_blob_is_reviewed_source_version(self):
        self.assertEqual(
            committed_blob_sha(".github/workflows/phase8a-annual-pattern-catalogue.yml"),
            "09b3a8f5ace25f9bf316827b9f4f82df7f72d4e1",
        )

    def test_annual_cli_blob_matches_output_path_source_review(self):
        self.assertEqual(
            committed_blob_sha("scripts/phase8a_annual_pattern_catalogue.py"),
            "030bf98df2d5ffb50821bd0403f205c7c09f20f3",
        )

    def test_2023_runtime_gate_blob_matches_sha_shape_source_review(self):
        self.assertEqual(
            committed_blob_sha(
                "src/fmp/discovery/annual_pattern_catalogue_2023_runtime_authorization.py"
            ),
            "cb4d32507dc93fa8a7a1296e630ce3bc9ee9c191",
        )

    def test_source_order_audit_blob_matches_non_authorizing_diagnostic(self):
        self.assertEqual(
            committed_blob_sha("scripts/dec1356_annual_workflow_source_order_audit.py"),
            "348dce13adf26734ed6139f11d7ba46d6c145546",
        )

    def test_missing_tracked_source_fails_instead_of_falling_back_to_worktree(self):
        with self.assertRaises(subprocess.CalledProcessError):
            committed_blob_sha("tests/this-dec1364-file-will-never-exist.py.missing")
