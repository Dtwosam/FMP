from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1054", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "Linux native one-shot rename required")
class NativeParentMovedToOneshotRegression(unittest.TestCase):
    def test_moved_to_only_watch_emits_cookie_and_ignored_without_source_half(self):
        one_fd = None
        independent_fd = None

        def records(raw):
            self.assertIs(type(raw), bytes)
            parsed = []
            offset = 0
            while offset < len(raw):
                self.assertGreaterEqual(len(raw) - offset, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(raw, offset)
                offset += module.EVENT.size
                self.assertLessEqual(nbytes, len(raw) - offset)
                name = raw[offset:offset + nbytes].split(b"\x00", 1)[0]
                offset += nbytes
                parsed.append((wd, mask, cookie, name))
            self.assertEqual(offset, len(raw))
            return parsed

        def pair(stream, wd, old, new):
            events = records(stream)
            froms = [
                (i, cookie) for i, (source, mask, cookie, name)
                in enumerate(events) if source == wd
                and mask == module.IN_MOVED_FROM and name == old
            ]
            tos = [
                (i, cookie) for i, (source, mask, cookie, name)
                in enumerate(events) if source == wd
                and mask == module.IN_MOVED_TO and name == new
            ]
            self.assertEqual(len(froms), 1)
            self.assertEqual(len(tos), 1)
            self.assertGreater(froms[0][1], 0)
            self.assertEqual(froms[0][1], tos[0][1])
            self.assertLess(froms[0][0], tos[0][0])
            return tos[0][1]

        with tempfile.TemporaryDirectory(
            prefix="dec1054-public-moved-to-oneshot-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            source_entry = sample.parent / "public-alpha"
            moved_entry = sample.parent / "public-beta"
            self.assertEqual(sample.write_bytes(module.BEFORE),
                             len(module.BEFORE))
            self.assertEqual(source_entry.write_bytes(b"PUBLIC-ENTRY"),
                             len(b"PUBLIC-ENTRY"))
            original = os.lstat(sample)
            original_parent = os.lstat(sample.parent)
            original_entry = os.lstat(source_entry)
            self.assertEqual(
                module._bounded_inventory_names(sample.parent),
                ("public-alpha", "sample"),
            )
            try:
                independent_fd, source_wd, parent_wd = (
                    module._start_watch(sample)
                )
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32,
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                one_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreater(one_fd, 2)
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(sample.parent),
                    module.IN_MOVED_TO | module.IN_ONLYDIR |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # The one-shot filters OUT the real MOVED_FROM half.
                # First matching MOVED_TO consumes the watch, with its
                # real positive cookie followed by auto IN_IGNORED.
                os.rename(source_entry, moved_entry)
                to_only = records(module._read_receipt_pending(one_fd))
                self.assertEqual(len(to_only), 2)
                self.assertEqual(
                    (to_only[0][0], to_only[0][1], to_only[0][3]),
                    (one_wd, module.IN_MOVED_TO, b"public-beta"),
                )
                self.assertGreater(to_only[0][2], 0)
                self.assertEqual(
                    to_only[1],
                    (one_wd, module.IN_IGNORED, 0, b""),
                )
                self.assertFalse(any(
                    mask == module.IN_MOVED_FROM
                    for wd, mask, cookie, name in to_only
                ))
                self.assertEqual(module._read_receipt_pending(one_fd), b"")

                real = module._read_receipt_pending(independent_fd)
                cookie = pair(
                    real, parent_wd,
                    b"public-alpha", b"public-beta"
                )
                self.assertEqual(to_only[0][2], cookie)
                parsed = module._classify_stream(
                    real, source_wd, parent_wd
                )
                self.assertTrue(parsed["well_formed"])
                self.assertFalse(parsed["invalidated"])
                self.assertGreaterEqual(parsed["directory_changes"], 2)
                verdict = module._evaluate(
                    module.BEFORE, module.BEFORE,
                    real, source_wd, True, False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("public-beta", "sample"),
                )
                self.assertEqual(verdict["status"], "BLOCKED")
                self.assertIs(verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Restoring the original entry via a genuine second
                # rename is invisible to the already disarmed one-shot.
                os.rename(moved_entry, source_entry)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                restored_stream = module._read_receipt_pending(independent_fd)
                pair(
                    restored_stream, parent_wd,
                    b"public-beta", b"public-alpha"
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Finally verify original public bytes, inode roles,
                # directory inventory and unchanged sample identity.
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(source_entry.read_bytes(), b"PUBLIC-ENTRY")
                after = os.lstat(sample)
                entry_after = os.lstat(source_entry)
                parent_after = os.lstat(sample.parent)
                self.assertEqual(
                    (after.st_dev, after.st_ino, after.st_mode),
                    (original.st_dev, original.st_ino, original.st_mode),
                )
                self.assertEqual(
                    (entry_after.st_dev, entry_after.st_ino, entry_after.st_mode),
                    (original_entry.st_dev, original_entry.st_ino,
                     original_entry.st_mode),
                )
                self.assertEqual(
                    (parent_after.st_dev, parent_after.st_ino,
                     parent_after.st_mode),
                    (original_parent.st_dev, original_parent.st_ino,
                     original_parent.st_mode),
                )
                self.assertEqual(
                    module._bounded_inventory_names(sample.parent),
                    ("public-alpha", "sample"),
                )
            finally:
                for fd in (one_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
