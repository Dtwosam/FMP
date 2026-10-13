from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1044", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify only")
class NativeInotifyModifyCoalescingRegression(unittest.TestCase):
    def test_six_real_writes_coalesce_to_one_source_only_modify_event(self):
        source_only_fd = None
        full_fd = None
        writer_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            events = []
            pos = 0
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - pos)
                name = data[pos:pos + nbytes].split(b"\x00", 1)[0]
                pos += nbytes
                events.append((wd, mask, cookie, name))
            self.assertEqual(pos, len(data))
            return events

        with tempfile.TemporaryDirectory(
            prefix="dec1044-public-modify-coalescing-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            source_first = os.lstat(sample)
            parent_first = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                full_fd, full_source_wd, parent_wd = module._start_watch(sample)
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                source_only_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                self.assertGreater(source_only_fd, 2)
                single_wd = libc.inotify_add_watch(
                    source_only_fd, module._checked_watch_path_bytes(sample),
                    module.IN_MODIFY | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(single_wd, 0)
                self.assertEqual(module._read_receipt_pending(full_fd), b"")
                self.assertEqual(
                    module._read_receipt_pending(source_only_fd), b""
                )

                # Keep ONE actual writer FD open throughout: no
                # IN_CLOSE_WRITE can interleave source-only IN_MODIFY.
                writer_fd = os.open(sample, os.O_RDWR | os.O_CLOEXEC)
                self.assertEqual(
                    module._read_receipt_pending(source_only_fd), b""
                )
                self.assertEqual(module._read_receipt_pending(full_fd), b"")

                # SIX separate successful kernel writes change the
                # first byte repeatedly, finally restoring it.
                for value in (b"A", b"B", b"C", b"E", b"F",
                              module.BEFORE[:1]):
                    self.assertEqual(os.lseek(writer_fd, 0, os.SEEK_SET), 0)
                    self.assertEqual(os.write(writer_fd, value), 1)
                self.assertEqual(sample.read_bytes(), module.BEFORE)

                # Linux coalesces identical successive unread events on
                # source-only watcher: SIX writes, ONE IN_MODIFY.
                source_only = module._read_receipt_pending(source_only_fd)
                self.assertEqual(
                    records(source_only),
                    [(single_wd, module.IN_MODIFY, 0, b"")],
                )
                self.assertEqual(
                    module._read_receipt_pending(source_only_fd), b""
                )
                source_only_parse = module._classify_stream(
                    source_only, single_wd
                )
                self.assertTrue(source_only_parse["well_formed"])
                self.assertFalse(source_only_parse["invalidated"])
                self.assertEqual(source_only_parse["source_modify_events"], 1)
                self.assertEqual(
                    source_only_parse["source_content_write_events"], 1
                )
                single_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, source_only,
                    single_wd, True, False,
                )
                self.assertEqual(single_verdict["status"], "BLOCKED")
                self.assertIs(single_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    single_verdict["independent_os_proof_verified"], False
                )

                # Separate TRUE source+parent inotify instance records
                # named parent and source modification events for
                # each write, preventing adjacent event coalescing.
                full = module._read_receipt_pending(full_fd)
                dual_records = records(full)
                source_mods = [
                    x for x in dual_records
                    if x == (full_source_wd, module.IN_MODIFY, 0, b"")
                ]
                parent_mods = [
                    x for x in dual_records
                    if x == (parent_wd, module.IN_MODIFY, 0, b"sample")
                ]
                self.assertGreaterEqual(len(source_mods), 6)
                self.assertGreaterEqual(len(parent_mods), 6)
                dual_parse = module._classify_stream(
                    full, full_source_wd, parent_wd
                )
                self.assertTrue(dual_parse["well_formed"])
                self.assertFalse(dual_parse["invalidated"])
                self.assertGreaterEqual(dual_parse["source_modify_events"], 6)
                self.assertGreaterEqual(
                    dual_parse["source_content_write_events"], 6
                )
                dual_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, full,
                    full_source_wd, True, False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(dual_verdict["status"], "BLOCKED")
                self.assertIs(dual_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    dual_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(full_fd), b"")

                # A contrasting genuine sequence DRAINS after every
                # write. The same source-only watch now reports a
                # separate IN_MODIFY for each successful native write.
                for value in (b"A", b"B", module.BEFORE[:1]):
                    self.assertEqual(os.lseek(writer_fd, 0, os.SEEK_SET), 0)
                    self.assertEqual(os.write(writer_fd, value), 1)
                    separately = module._read_receipt_pending(source_only_fd)
                    self.assertEqual(
                        records(separately),
                        [(single_wd, module.IN_MODIFY, 0, b"")],
                    )
                    full_single = module._read_receipt_pending(full_fd)
                    self.assertIn(
                        (full_source_wd, module.IN_MODIFY, 0, b""),
                        records(full_single),
                    )
                    self.assertIn(
                        (parent_wd, module.IN_MODIFY, 0, b"sample"),
                        records(full_single),
                    )
                    result = module._evaluate(
                        module.BEFORE, sample.read_bytes(), full_single,
                        full_source_wd, True, False,
                        directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(result["status"], "BLOCKED")
                    self.assertIs(result["can_authorize_dispatch"], False)
                    self.assertIs(
                        result["independent_os_proof_verified"], False
                    )
                    self.assertEqual(
                        module._read_receipt_pending(source_only_fd), b""
                    )
                    self.assertEqual(module._read_receipt_pending(full_fd), b"")

                os.close(writer_fd)
                writer_fd = None
                self.assertEqual(
                    module._read_receipt_pending(source_only_fd), b""
                )
                closing = records(module._read_receipt_pending(full_fd))
                self.assertIn(
                    (full_source_wd, module.IN_CLOSE_WRITE, 0, b""),
                    closing,
                )
                self.assertIn(
                    (parent_wd, module.IN_CLOSE_WRITE, 0, b"sample"),
                    closing,
                )
                self.assertEqual(module._read_receipt_pending(full_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                last = os.lstat(sample)
                last_parent = os.lstat(sample.parent)
                self.assertEqual(
                    (last.st_dev, last.st_ino, last.st_mode),
                    (source_first.st_dev, source_first.st_ino,
                     source_first.st_mode),
                )
                self.assertEqual(
                    (last_parent.st_dev, last_parent.st_ino,
                     last_parent.st_mode),
                    (parent_first.st_dev, parent_first.st_ino,
                     parent_first.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                for fd in (writer_fd, source_only_fd, full_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
