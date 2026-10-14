from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1113", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeSourceHardlinkCreateAttributeOneShotRegression(unittest.TestCase):
    def test_new_hardlink_name_disarms_source_oneshot_before_source_write(self):
        one_fd = None
        independent_fd = None

        def events(data):
            self.assertIs(type(data), bytes)
            answer = []
            pos = 0
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - pos)
                name = data[pos:pos + nbytes].split(b"\x00", 1)[0]
                pos += nbytes
                self.assertEqual(cookie, 0)
                answer.append((wd, mask, name))
            self.assertEqual(pos, len(data))
            return answer

        def genuine_write(path, content):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC)
            try:
                self.assertEqual(os.write(fd, content), len(content))
                os.fsync(fd)
            finally:
                os.close(fd)

        def verify_real_write(data, source_wd, parent_wd, after):
            actual = events(data)
            for expected in (
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            ):
                self.assertIn(expected, actual)
            parsed = module._classify_stream(data, source_wd, parent_wd)
            self.assertTrue(parsed["well_formed"])
            self.assertFalse(parsed["invalidated"])
            self.assertGreaterEqual(parsed["source_content_write_events"], 1)
            outcome = module._evaluate(
                module.BEFORE, after, data, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(outcome["status"], "BLOCKED")
            self.assertIs(outcome["can_authorize_dispatch"], False)
            self.assertIs(outcome["independent_os_proof_verified"], False)

        with tempfile.TemporaryDirectory(
            prefix="dec1113-public-hardlink-create-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            alias = parent / "alias"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first = (os.lstat(sample), os.lstat(parent))
            self.assertEqual(first[0].st_nlink, 1)
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
                    one_fd, module._checked_watch_path_bytes(sample),
                    module.IN_ATTRIB | module.IN_MODIFY |
                    module.IN_CLOSE_WRITE | module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                # Real hard-link CREATE supplies a second basename for the
                # existing watched source inode, without modifying bytes.
                os.link(sample, alias)
                self.assertEqual(os.lstat(sample).st_nlink, 2)
                self.assertEqual(os.lstat(sample).st_ino,
                                 os.lstat(alias).st_ino)
                self.assertEqual(
                    events(module._read_receipt_pending(one_fd)),
                    [(one_wd, module.IN_ATTRIB, b""),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                self.assertCountEqual(
                    events(module._read_receipt_pending(independent_fd)),
                    [(source_wd, module.IN_ATTRIB, b""),
                     (parent_wd, module.IN_CREATE, b"alias")],
                )
                self.assertEqual(module._read_receipt_pending(one_fd), b"")

                # Removing the alias restores initial nlink and inventory,
                # but source one-shot remains removed after IN_IGNORED.
                os.unlink(alias)
                self.assertEqual(os.lstat(sample).st_nlink, 1)
                self.assertFalse(alias.exists())
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertCountEqual(
                    events(module._read_receipt_pending(independent_fd)),
                    [(source_wd, module.IN_ATTRIB, b""),
                     (parent_wd, module.IN_DELETE, b"alias")],
                )
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                genuine_write(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                verify_real_write(
                    module._read_receipt_pending(independent_fd),
                    source_wd, parent_wd, module.AFTER,
                )
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                genuine_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                verify_real_write(
                    module._read_receipt_pending(independent_fd),
                    source_wd, parent_wd, module.BEFORE,
                )
                self.assertEqual(module._read_receipt_pending(independent_fd),
                                 b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = (os.lstat(sample), os.lstat(parent))
                for old, new in zip(first, final):
                    self.assertEqual(
                        (old.st_dev, old.st_ino, old.st_mode, old.st_nlink),
                        (new.st_dev, new.st_ino, new.st_mode, new.st_nlink),
                    )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertFalse(alias.exists())
            finally:
                for fd in (one_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
