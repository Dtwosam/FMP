from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1048", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "Linux native one-shot inotify only")
class NativeOneshotSixWritesRegression(unittest.TestCase):
    def test_oneshot_disarms_on_first_of_six_writes_while_dual_witness_sees_all(self):
        oneshot_fd = None
        dual_fd = None
        writer_fd = None

        def records(raw):
            self.assertIs(type(raw), bytes)
            offset = 0
            parsed = []
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

        with tempfile.TemporaryDirectory(
            prefix="dec1048-public-oneshot-six-writes-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = os.lstat(sample)
            parent_initial = os.lstat(sample.parent)
            self.assertEqual(
                module._bounded_inventory_names(sample.parent), ("sample",)
            )
            try:
                dual_fd, source_wd, parent_wd = module._start_watch(sample)
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32,
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                oneshot_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                self.assertGreater(oneshot_fd, 2)
                one_wd = libc.inotify_add_watch(
                    oneshot_fd, module._checked_watch_path_bytes(sample),
                    module.IN_MODIFY | IN_ONESHOT | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(one_wd, 0)
                self.assertNotEqual(dual_fd, oneshot_fd)
                self.assertEqual(module._read_receipt_pending(dual_fd), b"")
                self.assertEqual(module._read_receipt_pending(oneshot_fd), b"")

                # Six genuine successful writes to one public inode
                # while ONE writer FD stays open. Source-only one-shot
                # registration disarms on FIRST IN_MODIFY; later writes
                # cannot contribute events to that removed subscription.
                writer_fd = os.open(sample, os.O_RDWR | os.O_CLOEXEC)
                self.assertEqual(module._read_receipt_pending(dual_fd), b"")
                for byte in (b"A", b"B", b"C", b"E", b"F",
                             module.BEFORE[:1]):
                    self.assertEqual(os.lseek(writer_fd, 0, os.SEEK_SET), 0)
                    self.assertEqual(os.write(writer_fd, byte), 1)
                self.assertEqual(sample.read_bytes(), module.BEFORE)

                # Real Linux kernel buffer contains first modification
                # followed by explicit auto-disarm IN_IGNORED.
                oneshot_stream = module._read_receipt_pending(oneshot_fd)
                self.assertEqual(records(oneshot_stream), [
                    (one_wd, module.IN_MODIFY, 0, b""),
                    (one_wd, module.IN_IGNORED, 0, b""),
                ])
                one_parse = module._classify_stream(
                    oneshot_stream, one_wd
                )
                self.assertTrue(one_parse["invalidated"])
                self.assertEqual(one_parse["source_modify_events"], 1)
                self.assertEqual(
                    one_parse["source_content_write_events"], 1
                )
                one_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE,
                    oneshot_stream, one_wd, True, False,
                )
                self.assertEqual(one_verdict["status"], "BLOCKED")
                self.assertIs(one_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    one_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(oneshot_fd), b"")

                # The truly separate dual source+parent instance sees
                # native source and named-parent events for every write.
                dual_stream = module._read_receipt_pending(dual_fd)
                native = records(dual_stream)
                self.assertGreaterEqual(sum(
                    (wd, mask, cookie, name) ==
                    (source_wd, module.IN_MODIFY, 0, b"")
                    for wd, mask, cookie, name in native
                ), 6)
                self.assertGreaterEqual(sum(
                    (wd, mask, cookie, name) ==
                    (parent_wd, module.IN_MODIFY, 0, b"sample")
                    for wd, mask, cookie, name in native
                ), 6)
                classified = module._classify_stream(
                    dual_stream, source_wd, parent_wd
                )
                self.assertTrue(classified["well_formed"])
                self.assertFalse(classified["invalidated"])
                self.assertGreaterEqual(classified["source_modify_events"], 6)
                full_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, dual_stream,
                    source_wd, True, False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(full_verdict["status"], "BLOCKED")
                self.assertIs(full_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    full_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(dual_fd), b"")

                # Close shared writer. One-shot queue remains empty;
                # only live dual subscriptions observe CLOSE_WRITE.
                os.close(writer_fd)
                writer_fd = None
                self.assertEqual(module._read_receipt_pending(oneshot_fd), b"")
                close_stream = module._read_receipt_pending(dual_fd)
                closing = records(close_stream)
                self.assertIn(
                    (source_wd, module.IN_CLOSE_WRITE, 0, b""), closing
                )
                self.assertIn(
                    (parent_wd, module.IN_CLOSE_WRITE, 0, b"sample"),
                    closing,
                )
                self.assertEqual(module._read_receipt_pending(dual_fd), b"")

                # Even an additional real public write is unseen by
                # disarmed one-shot, but remains independently observed.
                with sample.open("r+b") as writer:
                    self.assertEqual(
                        writer.write(module.AFTER), len(module.AFTER)
                    )
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                self.assertEqual(module._read_receipt_pending(oneshot_fd), b"")
                later = module._read_receipt_pending(dual_fd)
                self.assertGreaterEqual(module._classify_stream(
                    later, source_wd, parent_wd
                )["source_modify_events"], 1)
                later_verdict = module._evaluate(
                    module.BEFORE, module.AFTER, later,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(later_verdict["status"], "BLOCKED")
                self.assertIs(later_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    later_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(dual_fd), b"")

                with sample.open("r+b") as writer:
                    self.assertEqual(
                        writer.write(module.BEFORE), len(module.BEFORE)
                    )
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                self.assertEqual(module._read_receipt_pending(oneshot_fd), b"")
                restore = module._read_receipt_pending(dual_fd)
                self.assertGreaterEqual(module._classify_stream(
                    restore, source_wd, parent_wd
                )["source_modify_events"], 1)
                self.assertEqual(module._read_receipt_pending(dual_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                last = os.lstat(sample)
                last_parent = os.lstat(sample.parent)
                self.assertEqual(
                    (last.st_dev, last.st_ino, last.st_mode),
                    (initial.st_dev, initial.st_ino, initial.st_mode),
                )
                self.assertEqual(
                    (last_parent.st_dev, last_parent.st_ino,
                     last_parent.st_mode),
                    (parent_initial.st_dev, parent_initial.st_ino,
                     parent_initial.st_mode),
                )
                self.assertEqual(
                    module._bounded_inventory_names(sample.parent), ("sample",)
                )
            finally:
                for fd in (writer_fd, oneshot_fd, dual_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
