from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1063", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "real native Linux inotify only")
class NativeParentBothMaskDeleteFirstOneShot(unittest.TestCase):
    def test_rmdir_first_disarms_create_delete_oneshot_before_recreate(self):
        one_fd = None
        independent_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            pos = 0
            seen = []
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - pos)
                name = data[pos:pos + nbytes].split(b"\x00", 1)[0]
                pos += nbytes
                self.assertEqual(cookie, 0)
                seen.append((wd, mask, name))
            self.assertEqual(pos, len(data))
            return seen

        with tempfile.TemporaryDirectory(
            prefix="dec1063-public-both-mask-delete-first-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            sibling = parent / "public-existing-dir"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            sibling.mkdir()
            sample_initial = os.lstat(sample)
            parent_initial = os.lstat(parent)
            sibling_initial = os.lstat(sibling)
            self.assertEqual(
                module._bounded_inventory_names(parent),
                ("public-existing-dir", "sample"),
            )
            try:
                independent_fd, source_wd, independent_parent_wd = (
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
                    one_fd, module._checked_watch_path_bytes(parent),
                    module.IN_CREATE | module.IN_DELETE |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_parent_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # The actual first event is DELETE, despite BOTH CREATE
                # and DELETE being in this watch's initial native mask.
                # Do not drain either kernel queue until after rmdir
                # AND recreation of a disposable PUBLIC directory.
                sibling.rmdir()
                self.assertFalse(sibling.exists())
                sibling.mkdir()
                self.assertTrue(sibling.is_dir())
                self.assertEqual(
                    module._bounded_inventory_names(parent),
                    ("public-existing-dir", "sample"),
                )
                truncated = records(module._read_receipt_pending(one_fd))
                self.assertEqual(truncated, [
                    (one_parent_wd, module.IN_DELETE | module.IN_ISDIR,
                     b"public-existing-dir"),
                    (one_parent_wd, module.IN_IGNORED, b""),
                ])
                self.assertFalse(any(
                    mask & module.IN_CREATE
                    for wd, mask, name in truncated
                ))
                self.assertEqual(module._read_receipt_pending(one_fd), b"")

                observed = module._read_receipt_pending(independent_fd)
                events = records(observed)
                delete = (
                    independent_parent_wd,
                    module.IN_DELETE | module.IN_ISDIR,
                    b"public-existing-dir",
                )
                create = (
                    independent_parent_wd,
                    module.IN_CREATE | module.IN_ISDIR,
                    b"public-existing-dir",
                )
                self.assertIn(delete, events)
                self.assertIn(create, events)
                self.assertLess(events.index(delete), events.index(create))
                parsed = module._classify_stream(
                    observed, source_wd, independent_parent_wd
                )
                self.assertTrue(parsed["well_formed"])
                self.assertFalse(parsed["invalidated"])
                self.assertGreaterEqual(parsed["directory_changes"], 2)
                decision = module._evaluate(
                    module.BEFORE, module.BEFORE, observed,
                    source_wd, True, False,
                    directory_watch=independent_parent_wd,
                    directory_inventory_names=("public-existing-dir", "sample"),
                )
                self.assertEqual(decision["status"], "BLOCKED")
                self.assertIs(decision["can_authorize_dispatch"], False)
                self.assertIs(
                    decision["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # A second genuine rmdir/mkdir lifecycle remains
                # invisible on disarmed one-shot, but the independent
                # parent continues to observe both named operations.
                sibling.rmdir()
                sibling.mkdir()
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                subsequent = records(
                    module._read_receipt_pending(independent_fd)
                )
                self.assertIn(delete, subsequent)
                self.assertIn(create, subsequent)
                self.assertLess(
                    subsequent.index(delete), subsequent.index(create)
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                sample_final = os.lstat(sample)
                parent_final = os.lstat(parent)
                sibling_final = os.lstat(sibling)
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                for old, new in (
                    (sample_initial, sample_final),
                    (parent_initial, parent_final),
                ):
                    self.assertEqual(
                        (old.st_dev, old.st_ino, old.st_mode),
                        (new.st_dev, new.st_ino, new.st_mode),
                    )
                self.assertEqual(
                    module._bounded_inventory_names(parent),
                    ("public-existing-dir", "sample"),
                )
                # The recreated sibling has the same PUBLIC name/type;
                # no assertion of its inode identity is permitted.
                self.assertEqual(sibling_initial.st_mode, sibling_final.st_mode)
            finally:
                for fd in (one_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
