from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1119", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeParentRenameFirstHalfOneShotRegression(unittest.TestCase):
    def test_rename_first_moved_from_disarms_parent_before_paired_to_and_writes(self):
        one_fd = None
        independent_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            out = []
            pos = 0
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - pos)
                name = data[pos:pos + nbytes].split(b"\x00", 1)[0]
                pos += nbytes
                out.append((wd, mask, cookie, name))
            self.assertEqual(pos, len(data))
            return out

        def actual_write(path, contents):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, contents), len(contents))
                os.fsync(fd)
            finally:
                os.close(fd)

        def verify_change(data, source_wd, parent_wd, after):
            native = records(data)
            # O_TRUNC can emit a genuine MODIFY before the subsequent
            # write(), yielding more than one source/parent MODIFY.
            # Every native record must still be one of the four expected
            # source/parent mutation identities. Enforce both writes and
            # exactly one writable close per descriptor, but do not forge
            # an arbitrary "exactly one MODIFY" kernel guarantee.
            source_modify = (source_wd, module.IN_MODIFY, 0, b"")
            parent_modify = (parent_wd, module.IN_MODIFY, 0, b"sample")
            source_close = (source_wd, module.IN_CLOSE_WRITE, 0, b"")
            parent_close = (parent_wd, module.IN_CLOSE_WRITE, 0, b"sample")
            permitted = (source_modify, parent_modify, source_close,
                         parent_close)
            self.assertTrue(all(event in permitted for event in native))
            self.assertGreaterEqual(native.count(source_modify), 1)
            self.assertGreaterEqual(native.count(parent_modify), 1)
            self.assertEqual(native.count(source_close), 1)
            self.assertEqual(native.count(parent_close), 1)
            parsed = module._classify_stream(data, source_wd, parent_wd)
            self.assertTrue(parsed["well_formed"])
            self.assertFalse(parsed["invalidated"])
            self.assertGreaterEqual(parsed["source_content_write_events"], 1)
            verdict = module._evaluate(
                module.BEFORE, after, data, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(verdict["status"], "BLOCKED")
            self.assertIs(verdict["can_authorize_dispatch"], False)
            self.assertIs(verdict["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1119-public-parent-first-rename-event-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            renamed = parent / "alternate"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = (os.lstat(sample), os.lstat(parent))
            self.assertEqual(initial[0].st_nlink, 1)
            self.assertEqual(module._bounded_inventory_names(parent), ("sample",))
            try:
                independent_fd, source_wd, parent_wd = module._start_watch(sample)
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32,
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                one_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreater(one_fd, 2)
                self.assertNotEqual(one_fd, independent_fd)
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(parent),
                    module.IN_MOVED_FROM | module.IN_MOVED_TO |
                    module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                os.rename(sample, renamed)
                self.assertFalse(sample.exists())
                self.assertTrue(renamed.is_file())
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("alternate",))
                # Parent ONESHOT subscribes to BOTH rename halves. The
                # first named MOVED_FROM consumes it BEFORE MOVED_TO is
                # emitted with the matching kernel rename cookie.
                original_oneshot = records(
                    module._read_receipt_pending(one_fd)
                )
                self.assertEqual(len(original_oneshot), 2)
                self.assertEqual(
                    original_oneshot[0][:2],
                    (one_wd, module.IN_MOVED_FROM),
                )
                self.assertGreater(original_oneshot[0][2], 0)
                self.assertEqual(original_oneshot[0][3], b"sample")
                self.assertEqual(
                    original_oneshot[1],
                    (one_wd, module.IN_IGNORED, 0, b""),
                )
                outward = module._read_receipt_pending(independent_fd)
                original = records(outward)
                self.assertEqual(len(original), 3)
                self.assertIn((source_wd, module.IN_MOVE_SELF, 0, b""), original)
                entries = [e for e in original if e[0] == parent_wd]
                self.assertEqual(len(entries), 2)
                rename_cookies = {e[2] for e in entries}
                self.assertEqual(len(rename_cookies), 1)
                cookie = rename_cookies.pop()
                self.assertGreater(cookie, 0)
                self.assertEqual(original_oneshot[0][2], cookie)
                self.assertCountEqual(entries, [
                    (parent_wd, module.IN_MOVED_FROM, cookie, b"sample"),
                    (parent_wd, module.IN_MOVED_TO, cookie, b"alternate"),
                ])
                parsed = module._classify_stream(
                    outward, source_wd, parent_wd
                )
                self.assertTrue(parsed["well_formed"])
                self.assertTrue(parsed["invalidated"])
                blocked = module._evaluate(
                    module.BEFORE, module.BEFORE, outward, source_wd, True,
                    False, directory_watch=parent_wd,
                    directory_inventory_names=("alternate",),
                )
                self.assertEqual(blocked["status"], "BLOCKED")
                self.assertIs(blocked["can_authorize_dispatch"], False)
                self.assertIs(blocked["independent_os_proof_verified"], False)

                os.rename(renamed, sample)
                self.assertTrue(sample.is_file())
                self.assertFalse(renamed.exists())
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                returned = module._read_receipt_pending(independent_fd)
                restored_events = records(returned)
                self.assertEqual(len(restored_events), 3)
                self.assertIn(
                    (source_wd, module.IN_MOVE_SELF, 0, b""),
                    restored_events,
                )
                entries = [e for e in restored_events if e[0] == parent_wd]
                self.assertEqual(len(entries), 2)
                rename_cookies = {e[2] for e in entries}
                self.assertEqual(len(rename_cookies), 1)
                cookie = rename_cookies.pop()
                self.assertGreater(cookie, 0)
                self.assertCountEqual(entries, [
                    (parent_wd, module.IN_MOVED_FROM, cookie, b"alternate"),
                    (parent_wd, module.IN_MOVED_TO, cookie, b"sample"),
                ])
                parsed = module._classify_stream(
                    returned, source_wd, parent_wd
                )
                self.assertTrue(parsed["well_formed"])
                self.assertTrue(parsed["invalidated"])
                blocked = module._evaluate(
                    module.BEFORE, module.BEFORE, returned, source_wd, True,
                    False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(blocked["status"], "BLOCKED")
                self.assertIs(blocked["can_authorize_dispatch"], False)
                self.assertIs(blocked["independent_os_proof_verified"], False)

                actual_write(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                verify_change(module._read_receipt_pending(independent_fd),
                              source_wd, parent_wd, module.AFTER)
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                actual_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                verify_change(module._read_receipt_pending(independent_fd),
                              source_wd, parent_wd, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                final = (os.lstat(sample), os.lstat(parent))
                for before, after in zip(initial, final):
                    self.assertEqual(
                        (before.st_dev, before.st_ino, before.st_mode,
                         before.st_nlink),
                        (after.st_dev, after.st_ino, after.st_mode,
                         after.st_nlink),
                    )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
            finally:
                if renamed.exists() and not sample.exists():
                    os.rename(renamed, sample)
                for fd in (one_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
