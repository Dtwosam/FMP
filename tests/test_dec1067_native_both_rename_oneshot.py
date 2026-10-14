from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1067", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "Linux inotify rename cookie required")
class NativeBothRenameMaskOneshotRegression(unittest.TestCase):
    def test_from_disarms_before_to_even_when_both_rename_masks_subscribed(self):
        one_fd = None
        independent_fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            result = []
            offset = 0
            while offset < len(stream):
                self.assertGreaterEqual(len(stream) - offset, module.EVENT.size)
                wd, mask, cookie, size = module.EVENT.unpack_from(stream, offset)
                offset += module.EVENT.size
                self.assertLessEqual(size, len(stream) - offset)
                name = stream[offset:offset + size].split(b"\x00", 1)[0]
                offset += size
                result.append((wd, mask, cookie, name))
            self.assertEqual(offset, len(stream))
            return result

        def full_pair(stream, wd, old, new):
            stream_events = records(stream)
            from_events = [(i, cookie)
                           for i, (xwd, mask, cookie, name)
                           in enumerate(stream_events)
                           if xwd == wd and mask == module.IN_MOVED_FROM
                           and name == old]
            to_events = [(i, cookie)
                         for i, (xwd, mask, cookie, name)
                         in enumerate(stream_events)
                         if xwd == wd and mask == module.IN_MOVED_TO
                         and name == new]
            self.assertEqual(len(from_events), 1)
            self.assertEqual(len(to_events), 1)
            self.assertGreater(from_events[0][1], 0)
            self.assertEqual(from_events[0][1], to_events[0][1])
            self.assertLess(from_events[0][0], to_events[0][0])
            return from_events[0][1]

        with tempfile.TemporaryDirectory(
            prefix="dec1067-public-both-rename-oneshot-", dir="/tmp"
        ) as tmp:
            root = Path(tmp)
            sample = root / "sample"
            alpha = root / "public-alpha"
            beta = root / "public-beta"
            gamma = root / "public-gamma"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            self.assertEqual(alpha.write_bytes(b"PUBLIC-RENAME"),
                             len(b"PUBLIC-RENAME"))
            initial = os.lstat(sample)
            initial_entry = os.lstat(alpha)
            initial_parent = os.lstat(root)
            self.assertEqual(module._bounded_inventory_names(root),
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
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(root),
                    module.IN_MOVED_FROM | module.IN_MOVED_TO |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # FIRST actual event of the same-directory rename is
                # MOVED_FROM. It auto-removes one-shot BEFORE MOVED_TO,
                # despite BOTH types explicitly in its initial mask.
                os.rename(alpha, beta)
                truncated = records(module._read_receipt_pending(one_fd))
                self.assertEqual(len(truncated), 2)
                self.assertEqual(
                    (truncated[0][0], truncated[0][1], truncated[0][3]),
                    (one_wd, module.IN_MOVED_FROM, b"public-alpha"),
                )
                self.assertGreater(truncated[0][2], 0)
                self.assertEqual(
                    truncated[1],
                    (one_wd, module.IN_IGNORED, 0, b""),
                )
                self.assertFalse(any(
                    mask == module.IN_MOVED_TO
                    for wd, mask, cookie, name in truncated
                ))
                self.assertEqual(module._read_receipt_pending(one_fd), b"")

                original_pair = module._read_receipt_pending(independent_fd)
                full_cookie = full_pair(
                    original_pair, parent_wd,
                    b"public-alpha", b"public-beta",
                )
                self.assertEqual(full_cookie, truncated[0][2])
                classified = module._classify_stream(
                    original_pair, source_wd, parent_wd
                )
                self.assertTrue(classified["well_formed"])
                self.assertFalse(classified["invalidated"])
                self.assertGreaterEqual(classified["directory_changes"], 2)
                verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, original_pair,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("public-beta", "sample"),
                )
                self.assertEqual(verdict["status"], "BLOCKED")
                self.assertIs(verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # The disarmed original cannot observe later rename
                # operations, but the witness retains full cookie pairs.
                for old, new, old_name, new_name in (
                    (beta, gamma, b"public-beta", b"public-gamma"),
                    (gamma, alpha, b"public-gamma", b"public-alpha"),
                ):
                    os.rename(old, new)
                    self.assertEqual(module._read_receipt_pending(one_fd), b"")
                    observed = module._read_receipt_pending(independent_fd)
                    full_pair(observed, parent_wd, old_name, new_name)
                    self.assertEqual(
                        module._read_receipt_pending(independent_fd), b""
                    )

                self.assertEqual(alpha.read_bytes(), b"PUBLIC-RENAME")
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = os.lstat(sample)
                final_entry = os.lstat(alpha)
                final_parent = os.lstat(root)
                for before, after in (
                    (initial, final),
                    (initial_entry, final_entry),
                    (initial_parent, final_parent),
                ):
                    self.assertEqual(
                        (before.st_dev, before.st_ino, before.st_mode),
                        (after.st_dev, after.st_ino, after.st_mode),
                    )
                self.assertEqual(module._bounded_inventory_names(root),
                                 ("public-alpha", "sample"))
            finally:
                for fd in (one_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
