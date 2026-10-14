from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1052", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux rename one-shot required")
class NativeParentMovedFromOneshotRegression(unittest.TestCase):
    def test_moved_from_oneshot_drops_matching_to_while_independent_keeps_cookie(self):
        one_fd = None
        independent_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            result = []
            pos = 0
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - pos)
                name = data[pos:pos + nbytes].split(b"\x00", 1)[0]
                pos += nbytes
                result.append((wd, mask, cookie, name))
            self.assertEqual(pos, len(data))
            return result

        def paired(stream, wd, old, new):
            observed = records(stream)
            froms = [
                (index, cookie) for index, (event_wd, mask, cookie, name)
                in enumerate(observed)
                if event_wd == wd and mask == module.IN_MOVED_FROM
                and name == old
            ]
            tos = [
                (index, cookie) for index, (event_wd, mask, cookie, name)
                in enumerate(observed)
                if event_wd == wd and mask == module.IN_MOVED_TO
                and name == new
            ]
            self.assertEqual(len(froms), 1)
            self.assertEqual(len(tos), 1)
            self.assertGreater(froms[0][1], 0)
            self.assertEqual(froms[0][1], tos[0][1])
            self.assertLess(froms[0][0], tos[0][0])
            return froms[0][1]

        with tempfile.TemporaryDirectory(
            prefix="dec1052-public-oneshot-rename-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            first_name = Path(tmp) / "public-alpha"
            second_name = Path(tmp) / "public-beta"
            third_name = Path(tmp) / "public-gamma"
            self.assertEqual(sample.write_bytes(module.BEFORE),
                             len(module.BEFORE))
            self.assertEqual(first_name.write_bytes(b"PUBLIC-RENAMED"),
                             len(b"PUBLIC-RENAMED"))
            start = os.lstat(sample)
            parent_start = os.lstat(sample.parent)
            entry_start = os.lstat(first_name)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("public-alpha", "sample"))
            try:
                independent_fd, source_wd, parent_wd = (
                    module._start_watch(sample)
                )
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                one_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreater(one_fd, 2)
                one_parent_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(sample.parent),
                    module.IN_MOVED_FROM | module.IN_ONLYDIR |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_parent_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # In a same-directory rename, the first IN_MOVED_FROM
                # consumes the one-shot BEFORE it can see IN_MOVED_TO.
                os.rename(first_name, second_name)
                incomplete = records(module._read_receipt_pending(one_fd))
                self.assertEqual(len(incomplete), 2)
                self.assertEqual(
                    (incomplete[0][0], incomplete[0][1], incomplete[0][3]),
                    (one_parent_wd, module.IN_MOVED_FROM, b"public-alpha"),
                )
                self.assertGreater(incomplete[0][2], 0)
                self.assertEqual(
                    incomplete[1],
                    (one_parent_wd, module.IN_IGNORED, 0, b""),
                )
                self.assertFalse(any(
                    mask == module.IN_MOVED_TO
                    for wd, mask, cookie, name in incomplete
                ))
                self.assertEqual(module._read_receipt_pending(one_fd), b"")

                # Truly independent source+parent instance keeps BOTH
                # halves with matching nonzero native cookie.
                complete = module._read_receipt_pending(independent_fd)
                first_cookie = paired(
                    complete, parent_wd, b"public-alpha", b"public-beta"
                )
                self.assertEqual(first_cookie, incomplete[0][2])
                parsed = module._classify_stream(
                    complete, source_wd, parent_wd
                )
                self.assertTrue(parsed["well_formed"])
                self.assertFalse(parsed["invalidated"])
                self.assertGreaterEqual(parsed["directory_changes"], 2)
                decision = module._evaluate(
                    module.BEFORE, module.BEFORE, complete,
                    source_wd, True, False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("public-beta", "sample"),
                )
                self.assertEqual(decision["status"], "BLOCKED")
                self.assertIs(decision["can_authorize_dispatch"], False)
                self.assertIs(
                    decision["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Subsequent genuine renames are entirely invisible
                # to removed one-shot but remain complete on witness.
                os.rename(second_name, third_name)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                later = module._read_receipt_pending(independent_fd)
                paired(later, parent_wd, b"public-beta", b"public-gamma")
                self.assertTrue(module._classify_stream(
                    later, source_wd, parent_wd
                )["well_formed"])
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Restore initial public directory entry via real
                # rename and verify restored inode and final census.
                os.rename(third_name, first_name)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                restored_stream = module._read_receipt_pending(independent_fd)
                paired(
                    restored_stream, parent_wd,
                    b"public-gamma", b"public-alpha"
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")
                self.assertEqual(first_name.read_bytes(), b"PUBLIC-RENAMED")
                final_entry = os.lstat(first_name)
                final = os.lstat(sample)
                parent_final = os.lstat(sample.parent)
                self.assertEqual(
                    (final_entry.st_dev, final_entry.st_ino, final_entry.st_mode),
                    (entry_start.st_dev, entry_start.st_ino, entry_start.st_mode),
                )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (start.st_dev, start.st_ino, start.st_mode)
                )
                self.assertEqual(
                    (parent_final.st_dev, parent_final.st_ino,
                     parent_final.st_mode),
                    (parent_start.st_dev, parent_start.st_ino,
                     parent_start.st_mode)
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("public-alpha", "sample"))
            finally:
                for fd in (one_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
