from __future__ import annotations

import ctypes
import errno
import errno
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1189", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "requires real native Linux inotify")
class NativePunchHolePastEofModifyRegression(unittest.TestCase):
    def test_punch_hole_beyond_eof_emits_modify_without_byte_delta(self):
        original_fd = None
        normal_fd = None
        writer_fd = None

        def unpack(data):
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
                self.assertEqual(cookie, 0)
                result.append((wd, mask, name))
            self.assertEqual(pos, len(data))
            return result

        def assert_blocked(data, source_wd, parent_wd, before, after,
                           has_close):
            actual = unpack(data)
            allowed = {
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
            }
            if has_close:
                allowed.update({
                    (source_wd, module.IN_CLOSE_WRITE, b""),
                    (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
                })
            self.assertTrue(actual)
            self.assertTrue(all(event in allowed for event in actual))
            for event in allowed:
                self.assertIn(event, actual)
            result = module._evaluate(
                before, after, data, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(result["status"], "BLOCKED")
            self.assertIs(result["can_authorize_dispatch"], False)
            self.assertIs(result["independent_os_proof_verified"], False)

        changed_at = module.BEFORE.index(b"SOURCE")
        changed = (module.BEFORE[:changed_at] + b"X" +
                   module.BEFORE[changed_at + 1:])
        self.assertEqual(len(changed), len(module.BEFORE))
        self.assertNotEqual(changed, module.BEFORE)

        with tempfile.TemporaryDirectory(
            prefix="dec1189-public-punch-past-eof-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE),
                             len(module.BEFORE))
            start = (os.lstat(sample), os.lstat(parent))
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("sample",))
            try:
                normal_fd, source_wd, parent_wd = module._start_watch(sample)
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                original_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreater(original_fd, 2)
                self.assertNotEqual(original_fd, normal_fd)
                one_wd = libc.inotify_add_watch(
                    original_fd, module._checked_watch_path_bytes(sample),
                    module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_wd, 0)
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # PUNCH_HOLE|KEEP_SIZE targets only a region BEYOND EOF.
                # The existing file content is untouched, but this real
                # Linux operation still produces native IN_MODIFY.
                libc.fallocate.argtypes = [
                    ctypes.c_int, ctypes.c_int, ctypes.c_longlong,
                    ctypes.c_longlong,
                ]
                libc.fallocate.restype = ctypes.c_int
                unchanged = module.BEFORE
                writer_fd = os.open(sample, os.O_WRONLY | os.O_CLOEXEC)
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
                rc = libc.fallocate(writer_fd, 0x03, 4096, 4096)
                if rc != 0:
                    error = ctypes.get_errno()
                    if error in (errno.EOPNOTSUPP, errno.ENOSYS, errno.EINVAL):
                        self.skipTest("filesystem lacks PUNCH_HOLE|KEEP_SIZE")
                    raise OSError(error, os.strerror(error))

                self.assertEqual(
                    unpack(module._read_receipt_pending(original_fd)),
                    [(one_wd, module.IN_MODIFY, b""),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                hole_receipt = module._read_receipt_pending(normal_fd)
                assert_blocked(hole_receipt, source_wd, parent_wd,
                               module.BEFORE, unchanged, False)
                self.assertEqual(os.fstat(writer_fd).st_size,
                                 len(module.BEFORE))
                self.assertEqual(sample.read_bytes(), unchanged)
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Writable descriptor close emits its own CLOSE_WRITE on
                # the still-continuing source+original-parent helper.
                os.close(writer_fd)
                writer_fd = None
                self.assertCountEqual(
                    unpack(module._read_receipt_pending(normal_fd)),
                    [(source_wd, module.IN_CLOSE_WRITE, b""),
                     (parent_wd, module.IN_CLOSE_WRITE, b"sample")],
                )
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")

                # A real changed-byte write is an independent positive
                # control: the normal continuous watcher still observes
                # source+parent MODIFY and CLOSE_WRITE after the no-op
                # already consumed the unsafe one-shot.
                writer_fd = os.open(
                    sample, os.O_WRONLY | os.O_CLOEXEC
                )
                self.assertEqual(os.pwrite(writer_fd, changed, 0),
                                 len(changed))
                os.fsync(writer_fd)
                os.close(writer_fd)
                writer_fd = None
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                assert_blocked(
                    module._read_receipt_pending(normal_fd),
                    source_wd, parent_wd, unchanged, changed, True
                )
                self.assertEqual(sample.read_bytes(), changed)

                writer_fd = os.open(
                    sample, os.O_WRONLY | os.O_TRUNC | os.O_CLOEXEC
                )
                self.assertEqual(os.write(writer_fd, module.BEFORE),
                                 len(module.BEFORE))
                os.fsync(writer_fd)
                os.close(writer_fd)
                writer_fd = None
                self.assertEqual(module._read_receipt_pending(original_fd),
                                 b"")
                assert_blocked(
                    module._read_receipt_pending(normal_fd),
                    source_wd, parent_wd, changed, module.BEFORE, True
                )

                finish = (os.lstat(sample), os.lstat(parent))
                for before, after in zip(start, finish):
                    self.assertEqual(
                        (before.st_dev, before.st_ino, before.st_mode,
                         before.st_nlink),
                        (after.st_dev, after.st_ino, after.st_mode,
                         after.st_nlink),
                    )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
            finally:
                for fd in (writer_fd, original_fd, normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
