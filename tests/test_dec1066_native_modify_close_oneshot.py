from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1066", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeModifyCloseCombinedOneshotRegression(unittest.TestCase):
    def test_modify_disarms_before_close_write_despite_combined_mask(self):
        one_fd = None
        independent_fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            pos = 0
            output = []
            while pos < len(stream):
                self.assertGreaterEqual(len(stream) - pos, module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(stream, pos)
                pos += module.EVENT.size
                self.assertLessEqual(length, len(stream) - pos)
                name = stream[pos:pos + length].split(b"\x00", 1)[0]
                pos += length
                self.assertEqual(cookie, 0)
                output.append((wd, mask, name))
            self.assertEqual(pos, len(stream))
            return output

        def write_real(path, payload):
            with path.open("r+b") as writer:
                self.assertEqual(writer.write(payload), len(payload))
                writer.truncate()
                writer.flush()
                os.fsync(writer.fileno())

        with tempfile.TemporaryDirectory(
            prefix="dec1066-public-oneshot-modify-close-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = os.lstat(sample)
            parent_initial = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                independent_fd, other_source_wd, other_parent_wd = (
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
                    one_fd, module._checked_watch_path_bytes(sample),
                    module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Both MODIFY and CLOSE_WRITE are explicitly
                # subscribed, but first true MODIFY destroys watch.
                # Do not drain one-shot until real write AND close.
                write_real(sample, module.AFTER)
                first = records(module._read_receipt_pending(one_fd))
                self.assertEqual(first, [
                    (one_wd, module.IN_MODIFY, b""),
                    (one_wd, module.IN_IGNORED, b""),
                ])
                self.assertFalse(any(
                    mask == module.IN_CLOSE_WRITE
                    for wd, mask, name in first
                ))
                self.assertEqual(module._read_receipt_pending(one_fd), b"")

                separate = module._read_receipt_pending(independent_fd)
                native = records(separate)
                for expected in (
                    (other_source_wd, module.IN_MODIFY, b""),
                    (other_source_wd, module.IN_CLOSE_WRITE, b""),
                    (other_parent_wd, module.IN_MODIFY, b"sample"),
                    (other_parent_wd, module.IN_CLOSE_WRITE, b"sample"),
                ):
                    self.assertIn(expected, native)
                classified = module._classify_stream(
                    separate, other_source_wd, other_parent_wd
                )
                self.assertTrue(classified["well_formed"])
                self.assertFalse(classified["invalidated"])
                self.assertGreaterEqual(classified["source_modify_events"], 1)
                self.assertGreaterEqual(
                    classified["source_content_write_events"], 1
                )
                blocked = module._evaluate(
                    module.BEFORE, module.AFTER, separate,
                    other_source_wd, True, False,
                    directory_watch=other_parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(blocked["status"], "BLOCKED")
                self.assertIs(blocked["can_authorize_dispatch"], False)
                self.assertIs(
                    blocked["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # The one-shot cannot see a SECOND real write/close
                # restoring initial bytes, while independent watcher
                # has both event categories and remains registered.
                write_real(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                restored = module._read_receipt_pending(independent_fd)
                native_restored = records(restored)
                for expected in (
                    (other_source_wd, module.IN_MODIFY, b""),
                    (other_source_wd, module.IN_CLOSE_WRITE, b""),
                    (other_parent_wd, module.IN_MODIFY, b"sample"),
                    (other_parent_wd, module.IN_CLOSE_WRITE, b"sample"),
                ):
                    self.assertIn(expected, native_restored)
                restored_decision = module._evaluate(
                    module.BEFORE, module.BEFORE, restored,
                    other_source_wd, True, False,
                    directory_watch=other_parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(restored_decision["status"], "BLOCKED")
                self.assertIs(
                    restored_decision["can_authorize_dispatch"], False
                )
                self.assertIs(
                    restored_decision["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                final = os.lstat(sample)
                parent_final = os.lstat(sample.parent)
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                for before, after in (
                    (initial, final), (parent_initial, parent_final)
                ):
                    self.assertEqual(
                        (before.st_dev, before.st_ino, before.st_mode),
                        (after.st_dev, after.st_ino, after.st_mode),
                    )
                self.assertEqual(
                    module._bounded_inventory_names(sample.parent),
                    ("sample",),
                )
            finally:
                for fd in (one_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
