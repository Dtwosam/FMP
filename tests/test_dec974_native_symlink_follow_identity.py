from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec974", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "native symlink inotify identity is Linux-only")
class NativeSymlinkWatchIdentityRegression(unittest.TestCase):
    def test_real_symlink_nofollow_watch_is_not_target_watch(self):
        normal_fd = None
        following_fd = None
        link_fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            pos = 0
            result = []
            while pos < len(stream):
                self.assertGreaterEqual(len(stream) - pos, module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(stream, pos)
                pos += module.EVENT.size
                self.assertLessEqual(length, len(stream) - pos)
                name = stream[pos:pos + length].split(b"\x00", 1)[0]
                pos += length
                self.assertEqual(cookie, 0)
                result.append((wd, mask, name))
            self.assertEqual(pos, len(stream))
            return result

        with tempfile.TemporaryDirectory(
            prefix="dec974-public-symlink-identity-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            alias = Path(tmp) / "public-alias"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            start = os.lstat(sample)
            start_parent = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                normal_fd, sample_wd, parent_wd = module._start_watch(sample)
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                alias.symlink_to("sample")
                self.assertTrue(stat.S_ISLNK(os.lstat(alias).st_mode))
                self.assertNotEqual(os.lstat(alias).st_ino, os.lstat(sample).st_ino)
                new_entry = module._read_receipt_pending(normal_fd)
                self.assertTrue(module._classify_stream(
                    new_entry, sample_wd, parent_wd
                )["well_formed"])
                self.assertTrue(any(
                    wd == parent_wd and mask & module.IN_CREATE
                    and name == b"public-alias"
                    for wd, mask, name in records(new_entry)
                ))
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                lib = module.ctypes.CDLL(None, use_errno=True)
                lib.inotify_init1.argtypes = [module.ctypes.c_int]
                lib.inotify_init1.restype = module.ctypes.c_int
                lib.inotify_add_watch.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = module.ctypes.c_int
                mask = (module.IN_MODIFY | module.IN_CLOSE_WRITE |
                        module.IN_DELETE_SELF | module.IN_MOVE_SELF |
                        module.IN_IGNORED)

                following_fd = lib.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                link_fd = lib.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreaterEqual(following_fd, 0)
                self.assertGreaterEqual(link_fd, 0)
                # Without IN_DONT_FOLLOW the kernel watches the target inode.
                # With IN_DONT_FOLLOW it watches the symlink inode itself.
                target_wd = lib.inotify_add_watch(
                    following_fd, module._checked_watch_path_bytes(alias), mask
                )
                link_wd = lib.inotify_add_watch(
                    link_fd, module._checked_watch_path_bytes(alias),
                    mask | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(target_wd, 0)
                self.assertGreater(link_wd, 0)
                for fd in (following_fd, link_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.AFTER), len(module.AFTER))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                target_stream = module._read_receipt_pending(following_fd)
                link_stream = module._read_receipt_pending(link_fd)
                main_stream = module._read_receipt_pending(normal_fd)
                self.assertEqual(link_stream, b"")
                self.assertTrue(target_stream)
                self.assertTrue(any(
                    wd == target_wd and mask & module.IN_MODIFY
                    for wd, mask, name in records(target_stream)
                ))
                self.assertTrue(all(
                    wd == target_wd and not name and
                    mask & (module.IN_MODIFY | module.IN_CLOSE_WRITE)
                    for wd, mask, name in records(target_stream)
                ))
                parsed = module._classify_stream(
                    main_stream, sample_wd, parent_wd
                )
                self.assertTrue(parsed["well_formed"])
                self.assertGreaterEqual(parsed["source_modify_events"], 1)
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                os.unlink(alias)
                symlink_removed = module._read_receipt_pending(link_fd)
                self.assertEqual(records(symlink_removed), [
                    (link_wd, module.IN_DELETE_SELF, b""),
                    (link_wd, module.IN_IGNORED, b""),
                ])
                self.assertEqual(module._read_receipt_pending(following_fd), b"")
                parent_deleted = module._read_receipt_pending(normal_fd)
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_DELETE
                    and name == b"public-alias"
                    for wd, mask, name in records(parent_deleted)
                ))
                self.assertEqual(module._read_receipt_pending(link_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Target watch survives unlinking a different symlink inode.
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.BEFORE), len(module.BEFORE))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                target_after_alias_removal = module._read_receipt_pending(
                    following_fd
                )
                source_after_alias_removal = module._read_receipt_pending(
                    normal_fd
                )
                self.assertTrue(any(
                    wd == target_wd and mask & module.IN_MODIFY
                    for wd, mask, name in records(target_after_alias_removal)
                ))
                self.assertEqual(module._read_receipt_pending(link_fd), b"")
                self.assertTrue(module._classify_stream(
                    source_after_alias_removal, sample_wd, parent_wd
                )["well_formed"])
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
                self.assertEqual(module._read_receipt_pending(following_fd), b"")

                for content, stream in (
                    (module.AFTER, main_stream),
                    (module.BEFORE, source_after_alias_removal),
                ):
                    verdict = module._evaluate(
                        module.BEFORE, content, stream, sample_wd,
                        True, False, directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(verdict["independent_os_proof_verified"], False)

                final = os.lstat(sample)
                final_parent = os.lstat(sample.parent)
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (start.st_dev, start.st_ino, start.st_mode),
                )
                self.assertEqual(
                    (final_parent.st_dev, final_parent.st_ino,
                     final_parent.st_mode),
                    (start_parent.st_dev, start_parent.st_ino,
                     start_parent.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                for fd in (link_fd, following_fd, normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
