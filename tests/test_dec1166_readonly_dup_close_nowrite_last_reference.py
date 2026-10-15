from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1166", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ACCESS = 0x00000001
IN_OPEN = 0x00000020
IN_CLOSE_NOWRITE = 0x00000010
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeReadOnlyDupLastCloseNowriteRegression(unittest.TestCase):
    def test_dup_readonly_file_first_close_quiet_then_last_close_nowrite(self):
        one_fd = None
        read_witness_fd = None
        normal_fd = None
        first_reader_fd = None
        second_reader_fd = None
        writer_fd = None

        def events(data):
            self.assertIs(type(data), bytes)
            seen = []
            off = 0
            while off < len(data):
                self.assertGreaterEqual(len(data) - off, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, off)
                off += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - off)
                name = data[off:off + nbytes].split(b"\x00", 1)[0]
                off += nbytes
                self.assertEqual(cookie, 0)
                seen.append((wd, mask, name))
            self.assertEqual(off, len(data))
            return seen

        def assert_read_stage(data, source_wd, parent_wd, mask):
            self.assertCountEqual(
                events(data),
                [(source_wd, mask, b""),
                 (parent_wd, mask, b"sample")],
            )

        def actual_write(path, payload):
            fd = os.open(path, os.O_WRONLY | os.O_TRUNC | os.O_CLOEXEC)
            try:
                self.assertEqual(os.write(fd, payload), len(payload))
                os.fsync(fd)
            finally:
                os.close(fd)

        def verify_normal_write(raw, source_wd, parent_wd, after):
            seen = events(raw)
            expected = {
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            }
            self.assertTrue(seen)
            self.assertTrue(all(x in expected for x in seen))
            for required in expected:
                self.assertIn(required, seen)
            verdict = module._evaluate(
                module.BEFORE, after, raw, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(verdict["status"], "BLOCKED")
            self.assertIs(verdict["can_authorize_dispatch"], False)
            self.assertIs(verdict["independent_os_proof_verified"], False)

        changed_at = module.BEFORE.index(b"SOURCE")
        changed = (module.BEFORE[:changed_at] + b"X" +
                   module.BEFORE[changed_at + 1:])
        self.assertNotEqual(changed, module.BEFORE)
        self.assertEqual(len(changed), len(module.BEFORE))

        with tempfile.TemporaryDirectory(
            prefix="dec1166-public-dup-readonly-last-close-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE),
                             len(module.BEFORE))
            first_stat = (os.lstat(sample), os.lstat(parent))
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("sample",))
            try:
                normal_fd, source_wd, parent_wd = module._start_watch(sample)
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32,
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                one_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                read_witness_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                self.assertEqual(len({one_fd, read_witness_fd, normal_fd}),
                                 3)
                one_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(sample),
                    IN_CLOSE_NOWRITE | module.IN_MODIFY |
                    module.IN_CLOSE_WRITE | module.IN_DONT_FOLLOW |
                    IN_ONESHOT,
                )
                witness_source_wd = libc.inotify_add_watch(
                    read_witness_fd,
                    module._checked_watch_path_bytes(sample),
                    IN_OPEN | IN_ACCESS | IN_CLOSE_NOWRITE |
                    module.IN_DONT_FOLLOW,
                )
                witness_parent_wd = libc.inotify_add_watch(
                    read_witness_fd,
                    module._checked_watch_path_bytes(parent),
                    IN_OPEN | IN_ACCESS | IN_CLOSE_NOWRITE |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                for wd in (one_wd, witness_source_wd, witness_parent_wd):
                    self.assertGreater(wd, 0)
                self.assertNotEqual(witness_source_wd, witness_parent_wd)
                for fd in (one_fd, read_witness_fd, normal_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                first_reader_fd = os.open(
                    sample, os.O_RDONLY | os.O_CLOEXEC
                )
                assert_read_stage(
                    module._read_receipt_pending(read_witness_fd),
                    witness_source_wd, witness_parent_wd, IN_OPEN,
                )
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Dup creates another integer FD referring to the SAME
                # open file description, not a second independently
                # opened file. First close must not emit CLOSE_NOWRITE.
                second_reader_fd = os.dup(first_reader_fd)
                self.assertEqual(os.fstat(first_reader_fd).st_ino,
                                 os.fstat(second_reader_fd).st_ino)
                os.close(first_reader_fd)
                first_reader_fd = None
                for fd in (one_fd, read_witness_fd, normal_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Actual positive byte read on surviving duplicate emits
                # source ACCESS and named original-parent ACCESS, but
                # original CLOSE_NOWRITE one-shot stays registered.
                self.assertEqual(os.read(second_reader_fd, 6),
                                 module.BEFORE[:6])
                assert_read_stage(
                    module._read_receipt_pending(read_witness_fd),
                    witness_source_wd, witness_parent_wd, IN_ACCESS,
                )
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Only LAST duplicate close generates native source
                # CLOSE_NOWRITE, consuming original test-only ONESHOT.
                os.close(second_reader_fd)
                second_reader_fd = None
                self.assertEqual(
                    events(module._read_receipt_pending(one_fd)),
                    [(one_wd, IN_CLOSE_NOWRITE, b""),
                     (one_wd, module.IN_IGNORED, b"")],
                )
                assert_read_stage(
                    module._read_receipt_pending(read_witness_fd),
                    witness_source_wd, witness_parent_wd, IN_CLOSE_NOWRITE,
                )
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # Close separate read-event watcher before ordinary content
                # verifications; they would otherwise generate more true
                # source OPEN/ACCESS/NOWRITE events.
                os.close(read_witness_fd)
                with self.assertRaises(OSError):
                    os.fstat(read_witness_fd)
                read_witness_fd = None
                self.assertEqual(sample.read_bytes(), module.BEFORE)

                actual_write(sample, changed)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                verify_normal_write(
                    module._read_receipt_pending(normal_fd),
                    source_wd, parent_wd, changed,
                )
                self.assertEqual(sample.read_bytes(), changed)

                actual_write(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                verify_normal_write(
                    module._read_receipt_pending(normal_fd),
                    source_wd, parent_wd, module.BEFORE,
                )
                self.assertEqual(sample.read_bytes(), module.BEFORE)

                final_stat = (os.lstat(sample), os.lstat(parent))
                for before, after in zip(first_stat, final_stat):
                    self.assertEqual(
                        (before.st_dev, before.st_ino, before.st_mode,
                         before.st_nlink),
                        (after.st_dev, after.st_ino, after.st_mode,
                         after.st_nlink),
                    )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
            finally:
                for fd in (first_reader_fd, second_reader_fd, writer_fd,
                           one_fd, read_witness_fd, normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
