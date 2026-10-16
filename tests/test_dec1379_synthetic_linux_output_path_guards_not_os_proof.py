"""DEC-1379: Linux tempdir-only positive and negative path guard probes.

Every created original, hardlink, symlink and child path is synthetic and
resides inside a TemporaryDirectory. No protected annual file or module,
network access, GitHub workflow dispatch or production path is involved.
"""
from __future__ import annotations

import errno
import mmap
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest

LINUX = sys.platform.startswith("linux")


@unittest.skipUnless(LINUX, "Linux/POSIX descriptor semantics only")
class LinuxTempOnlyOutputGuardsAreNotFullOriginalNoWriteProof(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(
            prefix="dec1379-synthetic-output-guards-"
        )
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.scratch = self.root / "scratch"
        self.target_dir = self.root / "synthetic-original"
        self.scratch.mkdir()
        self.target_dir.mkdir()

    def test_nofollow_refuses_existing_file_symlink(self):
        target = self.target_dir / "literal.txt"
        target.write_text("original", encoding="utf-8")
        alias = self.scratch / "alias.txt"
        alias.symlink_to(target)
        with self.assertRaises(OSError) as err:
            os.open(alias, os.O_WRONLY | os.O_NOFOLLOW)
        self.assertEqual(err.exception.errno, errno.ELOOP)
        self.assertEqual(target.read_text(encoding="utf-8"), "original")

    def test_nofollow_refuses_dangling_file_symlink(self):
        target = self.target_dir / "missing.txt"
        alias = self.scratch / "alias.txt"
        alias.symlink_to(target)
        with self.assertRaises(OSError) as err:
            os.open(alias, os.O_WRONLY | os.O_NOFOLLOW)
        self.assertEqual(err.exception.errno, errno.ELOOP)
        self.assertFalse(target.exists())

    def test_create_exclusive_refuses_existing_plain_output(self):
        output = self.scratch / "existing.txt"
        output.write_text("before", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        self.assertEqual(output.read_text(encoding="utf-8"), "before")

    def test_dirfd_anchored_plain_basename_creates_only_scratch_child(self):
        directory_fd = os.open(self.scratch, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, directory_fd)
        fd = os.open(
            "new.txt", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600, dir_fd=directory_fd,
        )
        try:
            os.write(fd, b"synthetic")
        finally:
            os.close(fd)
        self.assertEqual((self.scratch / "new.txt").read_bytes(), b"synthetic")
        self.assertFalse((self.target_dir / "new.txt").exists())

    def test_dirfd_without_parent_filter_allows_dotdot_escape_in_temp_root(self):
        directory_fd = os.open(self.scratch, os.O_RDONLY | os.O_DIRECTORY)
        self.addCleanup(os.close, directory_fd)
        fd = os.open(
            "../synthetic-original/escaped.txt",
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600, dir_fd=directory_fd,
        )
        try:
            os.write(fd, b"synthetic-only")
        finally:
            os.close(fd)
        self.assertEqual((self.target_dir / "escaped.txt").read_bytes(),
                         b"synthetic-only")

    def test_nofollow_does_not_prevent_hardlink_alias_write(self):
        original = self.target_dir / "original.txt"
        original.write_text("before", encoding="utf-8")
        alias = self.scratch / "hardlink.txt"
        os.link(original, alias)
        self.assertEqual(original.stat().st_ino, alias.stat().st_ino)
        self.assertGreaterEqual(original.stat().st_nlink, 2)
        fd = os.open(alias, os.O_WRONLY | os.O_NOFOLLOW)
        try:
            os.write(fd, b"after!")
        finally:
            os.close(fd)
        self.assertEqual(original.read_text(encoding="utf-8"), "after!")

    def test_symlink_is_detectable_even_when_exists_returns_false(self):
        dangling = self.scratch / "missing.json"
        dangling.symlink_to(self.target_dir / "missing.json")
        self.assertFalse(dangling.exists())
        self.assertTrue(dangling.is_symlink())
        self.assertTrue(stat.S_ISLNK(os.lstat(dangling).st_mode))

    def test_readonly_descriptor_rejects_write_without_claiming_os_isolation(self):
        original = self.target_dir / "source.txt"
        original.write_text("unchanged", encoding="utf-8")
        fd = os.open(original, os.O_RDONLY)
        try:
            with self.assertRaises(OSError) as err:
                os.write(fd, b"blocked")
            self.assertEqual(err.exception.errno, errno.EBADF)
        finally:
            os.close(fd)
        self.assertEqual(original.read_text(encoding="utf-8"), "unchanged")

    def test_truncating_open_can_modify_synthetic_original_without_write_call(self):
        original = self.target_dir / "original.txt"
        original.write_text("do not touch", encoding="utf-8")
        fd = os.open(original, os.O_WRONLY | os.O_TRUNC)
        os.close(fd)
        self.assertEqual(original.read_bytes(), b"")

    def test_synthetic_scratch_and_original_paths_share_only_temp_root(self):
        self.assertEqual(self.scratch.parent, self.root)
        self.assertEqual(self.target_dir.parent, self.root)
        self.assertNotEqual(self.scratch, self.target_dir)

    def test_nofollow_final_component_still_follows_synthetic_parent_symlink(self):
        target = self.target_dir / "original.txt"
        target.write_text("before", encoding="utf-8")
        parent_alias = self.scratch / "parent"
        parent_alias.symlink_to(self.target_dir, target_is_directory=True)
        fd = os.open(parent_alias / "original.txt", os.O_WRONLY | os.O_NOFOLLOW)
        try:
            os.write(fd, b"after!")
        finally:
            os.close(fd)
        self.assertEqual(target.read_text(encoding="utf-8"), "after!")

    def test_dirfd_nofollow_final_component_does_not_lock_parent_alias(self):
        target = self.target_dir / "original.txt"
        target.write_bytes(b"before")
        (self.scratch / "linked_parent").symlink_to(
            self.target_dir, target_is_directory=True
        )
        directory_fd = os.open(self.scratch, os.O_RDONLY | os.O_DIRECTORY)
        try:
            fd = os.open(
                "linked_parent/original.txt",
                os.O_WRONLY | os.O_NOFOLLOW,
                dir_fd=directory_fd,
            )
            try:
                os.pwrite(fd, b"after!", 0)
            finally:
                os.close(fd)
        finally:
            os.close(directory_fd)
        self.assertEqual(target.read_bytes(), b"after!")

    def test_open_write_descriptor_survives_synthetic_path_rename(self):
        original = self.target_dir / "synthetic-original.txt"
        moved = self.target_dir / "synthetic-moved.txt"
        original.write_bytes(b"before")
        fd = os.open(original, os.O_RDWR)
        try:
            os.rename(original, moved)
            os.pwrite(fd, b"after!", 0)
        finally:
            os.close(fd)
        self.assertFalse(original.exists())
        self.assertEqual(moved.read_bytes(), b"after!")

    def test_writable_mmap_survives_closing_original_descriptor(self):
        original = self.target_dir / "synthetic-original.txt"
        original.write_bytes(b"before")
        fd = os.open(original, os.O_RDWR)
        try:
            mapped = mmap.mmap(fd, 6, access=mmap.ACCESS_WRITE)
        finally:
            os.close(fd)
        try:
            mapped[:6] = b"after!"
            mapped.flush()
        finally:
            mapped.close()
        self.assertEqual(original.read_bytes(), b"after!")

    def test_exclusive_create_refuses_synthetic_dangling_symlink(self):
        target = self.target_dir / "not-created.txt"
        alias = self.scratch / "symlink-output.txt"
        alias.symlink_to(target)
        with self.assertRaises(FileExistsError):
            os.open(alias, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        self.assertFalse(target.exists())
