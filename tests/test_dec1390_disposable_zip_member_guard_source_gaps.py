"""DEC-1390: synthetic ZIP member safety review, never extract any archive.

All ZIPs are generated in memory with BytesIO. The annual workflow is read
from a committed Git blob only, and no GitHub artifact/annual data is fetched.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import PurePosixPath, Path
import hashlib
import re
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



def synthetic_unix_mode_zip(name: str, unix_mode: int) -> bytes:
    """One in-memory entry, no chmod, special files, extraction or host writes."""
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as dest:
        info = zipfile.ZipInfo(name)
        info.create_system = 3
        info.external_attr = unix_mode << 16
        dest.writestr(info, b"synthetic-only")
    return buffer.getvalue()


def member_problems(data: bytes) -> tuple[str, ...]:
    """Illustrative future *pre-extraction* denial logic, NOT installed guard."""
    problems = []
    observed: dict[str, bool] = {}
    with zipfile.ZipFile(BytesIO(data), "r") as archive:
        for info in archive.infolist():
            raw = info.filename
            elements = raw.split("/")
            name = PurePosixPath(raw)
            if (name.is_absolute() or ".." in elements or "\\" in raw
                    or re.match(r"^[A-Za-z]:", raw)
                    or str(name) == "."):
                problems.append("UNSAFE_MEMBER_PATH")
            canonical = str(name)
            if canonical in observed:
                problems.append("DUPLICATE_NORMALIZED_NAME")
            prefixes = canonical.split("/")
            if any("/".join(prefixes[:i]) in observed
                   and not observed["/".join(prefixes[:i])]
                   for i in range(1, len(prefixes))):
                problems.append("FILE_DIRECTORY_PREFIX_CONFLICT")
            if not info.is_dir() and any(
                existing.startswith(canonical + "/") for existing in observed
            ):
                problems.append("FILE_DIRECTORY_PREFIX_CONFLICT")
            observed[canonical] = info.is_dir()
            unix_mode = info.external_attr >> 16
            unix_type = stat.S_IFMT(unix_mode)
            if stat.S_ISLNK(unix_mode):
                problems.append("SYMLINK_ENTRY")
            if info.create_system == 3 and unix_type not in (
                0, stat.S_IFREG, stat.S_IFDIR, stat.S_IFLNK
            ):
                problems.append("UNSUPPORTED_UNIX_ENTRY_TYPE")
            if unix_mode & (stat.S_ISUID | stat.S_ISGID):
                problems.append("PRIVILEGED_MODE_BITS")
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

    def test_disposable_windows_drive_absolute_name_is_rejected(self):
        data = synthetic_zip([("C:/temp/destination.txt", b"test", False)])
        self.assertIn("UNSAFE_MEMBER_PATH", member_problems(data))

    def test_disposable_windows_drive_relative_name_is_rejected(self):
        data = synthetic_zip([("D:destination.txt", b"test", False)])
        self.assertIn("UNSAFE_MEMBER_PATH", member_problems(data))

    def test_disposable_root_dot_filename_is_rejected(self):
        data = synthetic_zip([(".", b"test", False)])
        self.assertIn("UNSAFE_MEMBER_PATH", member_problems(data))

    def test_normalized_duplicate_leading_dot_entry_is_rejected(self):
        data = synthetic_zip([
            ("./dir/manifest.json", b"first", False),
            ("dir/manifest.json", b"second", False),
        ])
        self.assertIn("DUPLICATE_NORMALIZED_NAME", member_problems(data))

    def test_file_then_descendant_member_collision_is_rejected(self):
        data = synthetic_zip([
            ("manifest", b"file", False),
            ("manifest/subfile.json", b"child", False),
        ])
        self.assertIn("FILE_DIRECTORY_PREFIX_CONFLICT",
                      member_problems(data))

    def test_descendant_then_parent_file_collision_is_rejected(self):
        data = synthetic_zip([
            ("manifest/subfile.json", b"child", False),
            ("manifest", b"file", False),
        ])
        self.assertIn("FILE_DIRECTORY_PREFIX_CONFLICT",
                      member_problems(data))

    def test_disposable_normal_directory_member_stays_distinct(self):
        data = synthetic_zip([
            ("safe/", b"", False),
            ("safe/manifest.json", b"{}", False),
        ])
        self.assertEqual(member_problems(data), ())

    def test_disposable_unix_character_device_entry_is_rejected(self):
        data = synthetic_unix_mode_zip(
            "synthetic-device", stat.S_IFCHR | 0o600
        )
        self.assertIn("UNSUPPORTED_UNIX_ENTRY_TYPE",
                      member_problems(data))

    def test_disposable_unix_fifo_entry_is_rejected(self):
        data = synthetic_unix_mode_zip(
            "synthetic-fifo", stat.S_IFIFO | 0o600
        )
        self.assertIn("UNSUPPORTED_UNIX_ENTRY_TYPE",
                      member_problems(data))

    def test_disposable_unix_setuid_mode_is_rejected(self):
        data = synthetic_unix_mode_zip(
            "synthetic-file", stat.S_IFREG | stat.S_ISUID | 0o755
        )
        self.assertIn("PRIVILEGED_MODE_BITS", member_problems(data))

    def test_disposable_unix_setgid_mode_is_rejected(self):
        data = synthetic_unix_mode_zip(
            "synthetic-file", stat.S_IFREG | stat.S_ISGID | 0o755
        )
        self.assertIn("PRIVILEGED_MODE_BITS", member_problems(data))

    def test_regular_unix_file_metadata_keeps_member_shape_clean(self):
        data = synthetic_unix_mode_zip(
            "safe/file.txt", stat.S_IFREG | 0o644
        )
        self.assertEqual(member_problems(data), ())
