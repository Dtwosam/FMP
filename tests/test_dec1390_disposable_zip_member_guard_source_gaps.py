"""DEC-1390: synthetic ZIP member safety review, never extract any archive.

All ZIPs are generated in memory with BytesIO. The annual workflow is read
from a committed Git blob only, and no GitHub artifact/annual data is fetched.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import PurePosixPath, Path
import hashlib
import stat
import subprocess
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def synthetic_zip(rows: list[tuple[str, bytes, bool]]) -> bytes:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as dest:
        for name, data, symlink in rows:
            info = zipfile.ZipInfo(name)
            if symlink:
                info.create_system = 3
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
            dest.writestr(info, data)
    return buffer.getvalue()


def member_problems(data: bytes) -> tuple[str, ...]:
    """Illustrative future *pre-extraction* denial logic, NOT installed guard."""
    problems = []
    observed = set()
    with zipfile.ZipFile(BytesIO(data), "r") as archive:
        for info in archive.infolist():
            raw = info.filename
            elements = raw.split("/")
            name = PurePosixPath(raw)
            if name.is_absolute() or ".." in elements or "\\" in raw:
                problems.append("UNSAFE_MEMBER_PATH")
            canonical = str(name)
            if canonical in observed:
                problems.append("DUPLICATE_NORMALIZED_NAME")
            observed.add(canonical)
            if stat.S_ISLNK(info.external_attr >> 16):
                problems.append("SYMLINK_ENTRY")
    return tuple(sorted(set(problems)))


class SyntheticZipMembersAreNotRealProtectedArtifactAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = subprocess.check_output(
            ["git", "show",
             "HEAD:.github/workflows/phase8a-annual-pattern-catalogue.yml"],
            cwd=ROOT, text=True,
        )
        cls.preflight = cls.workflow.split("  annual_preflight:\n", 1)[1].split(
            "  annual_cell:\n", 1
        )[0]
        cls.cell = cls.workflow.split("  annual_cell:\n", 1)[1].split(
            "  annual_freeze:\n", 1
        )[0]

    def test_current_cell_has_four_unzip_operations(self):
        self.assertEqual(self.cell.count("unzip -q .downloads/"), 4)

    def test_prior_freeze_is_extracted_after_archive_hash_comparison(self):
        s = self.preflight
        self.assertLess(s.index('test "$actual_sha" = "$expected_sha"'),
                        s.index("unzip -q .prior-freeze/freeze.zip"))

    def test_cell_archive_checks_checksum_before_first_unzip(self):
        self.assertLess(
            self.cell.index('test "$actual_sha" = "$expected_sha"'),
            self.cell.index("unzip -q .downloads/feature.zip"),
        )

    def test_current_cell_shell_has_no_explicit_member_listing_before_unzip(self):
        self.assertNotIn("zipinfo ", self.cell)
        self.assertNotIn("unzip -Z ", self.cell)
        self.assertNotIn("unzip -l ", self.cell)

    def test_current_prior_shell_has_no_explicit_member_listing_before_unzip(self):
        self.assertNotIn("zipinfo ", self.preflight)
        self.assertNotIn("unzip -Z ", self.preflight)
        self.assertNotIn("unzip -l ", self.preflight)

    def test_disposable_safe_member_shape_has_no_diagnostics(self):
        data = synthetic_zip([("dir/manifest.json", b"{}", False)])
        self.assertEqual(member_problems(data), ())

    def test_disposable_parent_traversal_member_is_rejected(self):
        data = synthetic_zip([("../outside.txt", b"synthetic", False)])
        self.assertIn("UNSAFE_MEMBER_PATH", member_problems(data))

    def test_disposable_absolute_and_backslash_names_are_rejected(self):
        for name in ("/absolute.txt", r"folder\escape.txt"):
            with self.subTest(name=name):
                data = synthetic_zip([(name, b"synthetic", False)])
                self.assertIn("UNSAFE_MEMBER_PATH", member_problems(data))

    def test_disposable_zip_symlink_entry_is_rejected(self):
        data = synthetic_zip([("link", b"../outside", True)])
        self.assertIn("SYMLINK_ENTRY", member_problems(data))

    def test_disposable_duplicate_normalized_member_is_rejected(self):
        data = synthetic_zip([
            ("a/./same.txt", b"first", False),
            ("a/same.txt", b"second", False),
        ])
        self.assertIn("DUPLICATE_NORMALIZED_NAME", member_problems(data))

    def test_matching_synthetic_sha256_does_not_constrain_member_structure(self):
        data = synthetic_zip([("../escape.txt", b"synthetic", False)])
        expected = hashlib.sha256(data).hexdigest()
        self.assertEqual(hashlib.sha256(data).hexdigest(), expected)
        self.assertIn("UNSAFE_MEMBER_PATH", member_problems(data))
