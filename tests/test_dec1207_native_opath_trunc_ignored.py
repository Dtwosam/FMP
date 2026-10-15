from __future__ import annotations

import ctypes
import errno
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1207", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_OPEN = 0x00000020
IN_CLOSE_NOWRITE = 0x00000010
IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux" and hasattr(os, "O_PATH"),
                     "Linux native inotify and O_PATH required")
class NativeOPathTruncIgnoredRegression(unittest.TestCase):
    def test_o_path_trunc_ignores_truncate_and_does_not_emit_mutation(self):
        original_fd = None
        read_witness_fd = None
        normal_fd = None
        reader_fd = None
        writer_fd = None

        def events(data):
            self.assertIs(type(data), bytes)
            rows = []
            off = 0
            while off < len(data):
                self.assertGreaterEqual(len(data) - off, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, off)
                off += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - off)
                name = data[off:off + nbytes].split(b"\x00", 1)[0]
                off += nbytes
                self.assertEqual(cookie, 0)
                rows.append((wd, mask, name))
            self.assertEqual(off, len(data))
            return rows

        def require_write_receipt(data, source_wd, parent_wd, before, after):
            received = events(data)
            allowed = {
                (source_wd, module.IN_MODIFY, b""),
                (parent_wd, module.IN_MODIFY, b"sample"),
                (source_wd, module.IN_CLOSE_WRITE, b""),
                (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
            }
            self.assertTrue(received)
            self.assertTrue(all(row in allowed for row in received))
            for required in allowed:
                self.assertIn(required, received)
            verdict = module._evaluate(
                before, after, data, source_wd, True, False,
                directory_watch=parent_wd,
                directory_inventory_names=("sample",),
            )
            self.assertEqual(verdict["status"], "BLOCKED")
            self.assertIs(verdict["can_authorize_dispatch"], False)
            self.assertIs(verdict["independent_os_proof_verified"], False)

        at = module.BEFORE.index(b"SOURCE")
        changed = module.BEFORE[:at] + b"X" + module.BEFORE[at + 1:]
        self.assertEqual(len(changed), len(module.BEFORE))
        self.assertNotEqual(changed, module.BEFORE)

        with tempfile.TemporaryDirectory(
            prefix="dec1207-public-opath-trunc-ignored-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE),
                             len(module.BEFORE))
            first = (os.lstat(sample), os.lstat(parent))
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
                original_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                read_witness_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                self.assertEqual(len({original_fd, read_witness_fd,
                                      normal_fd}), 3)
                original_wd = libc.inotify_add_watch(
                    original_fd,
                    module._checked_watch_path_bytes(sample),
                    module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                witness_wd = libc.inotify_add_watch(
                    read_witness_fd,
                    module._checked_watch_path_bytes(sample),
                    IN_OPEN | IN_CLOSE_NOWRITE | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(original_wd, 0)
                self.assertGreater(witness_wd, 0)
                for fd in (original_fd, read_witness_fd, normal_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Linux O_PATH deliberately ignores non-O_PATH flags
                # including O_TRUNC. This is a path-only descriptor:
                # no native READ OPEN, MODIFY, or CLOSE_NOWRITE event.
                reader_fd = os.open(
                    sample, os.O_PATH | os.O_TRUNC | os.O_CLOEXEC
                )
                self.assertEqual(os.fstat(reader_fd).st_size,
                                 len(module.BEFORE))
                for fd in (original_fd, read_witness_fd, normal_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # This O_PATH descriptor cannot write file data.
                with self.assertRaises(OSError) as rejected:
                    os.pwrite(reader_fd, b"X", 0)
                self.assertEqual(rejected.exception.errno, errno.EBADF)
                for fd in (original_fd, read_witness_fd, normal_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                os.close(reader_fd)
                reader_fd = None
                for fd in (original_fd, read_witness_fd, normal_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Close the read watcher BEFORE content-verification reads.
                os.close(read_witness_fd)
                with self.assertRaises(OSError):
                    os.fstat(read_witness_fd)
                read_witness_fd = None
                self.assertEqual(sample.read_bytes(), module.BEFORE)

                # Only a genuine later changed-byte write consumes the
                # original source-only MODIFY|CLOSE_WRITE|ONESHOT.
                writer_fd = os.open(
                    sample, os.O_WRONLY | os.O_CLOEXEC
                )
                self.assertEqual(os.pwrite(writer_fd, changed, 0),
                                 len(changed))
                os.fsync(writer_fd)
                os.close(writer_fd)
                writer_fd = None
                self.assertEqual(
                    events(module._read_receipt_pending(original_fd)),
                    [(original_wd, module.IN_MODIFY, b""),
                     (original_wd, module.IN_IGNORED, b"")],
                )
                require_write_receipt(
                    module._read_receipt_pending(normal_fd),
                    source_wd, parent_wd, module.BEFORE, changed
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
                require_write_receipt(
                    module._read_receipt_pending(normal_fd),
                    source_wd, parent_wd, changed, module.BEFORE
                )

                final = (os.lstat(sample), os.lstat(parent))
                for old, new in zip(first, final):
                    self.assertEqual(
                        (old.st_dev, old.st_ino, old.st_mode, old.st_nlink),
                        (new.st_dev, new.st_ino, new.st_mode, new.st_nlink),
                    )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
            finally:
                for fd in (reader_fd, writer_fd, original_fd,
                           read_witness_fd, normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
