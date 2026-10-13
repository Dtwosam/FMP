from __future__ import annotations

import ctypes
import fcntl
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1028", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(
    sys.platform == "linux" and hasattr(fcntl, "F_DUPFD_CLOEXEC"),
    "Linux native F_DUPFD_CLOEXEC required",
)
class NativeInotifyFcntlDuplicateVariants(unittest.TestCase):
    def test_dupfd_and_dupfd_cloexec_share_queue_with_different_fd_flags(self):
        original_fd = None
        inheritable_fd = None
        cloexec_fd = None
        independent_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            output = []
            offset = 0
            while offset < len(data):
                self.assertGreaterEqual(len(data) - offset, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, offset)
                offset += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - offset)
                name = data[offset:offset + nbytes].split(b"\x00", 1)[0]
                offset += nbytes
                self.assertEqual(cookie, 0)
                output.append((wd, mask, name))
            self.assertEqual(offset, len(data))
            return output

        with tempfile.TemporaryDirectory(
            prefix="dec1028-public-fcntl-inotify-dup-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = os.lstat(sample)
            parent_initial = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                original_fd, source_wd, parent_wd = module._start_watch(sample)
                inheritable_fd = fcntl.fcntl(
                    original_fd, fcntl.F_DUPFD, 0
                )
                cloexec_fd = fcntl.fcntl(
                    original_fd, fcntl.F_DUPFD_CLOEXEC, 0
                )
                independent_fd, independent_source, independent_parent = (
                    module._start_watch(sample)
                )
                self.assertEqual(
                    len({original_fd, inheritable_fd,
                         cloexec_fd, independent_fd}), 4
                )

                # F_DUPFD is the Linux non-CLOEXEC duplication variant;
                # F_DUPFD_CLOEXEC sets per-descriptor close-on-exec.
                # No subprocess or exec is ever invoked by this test.
                self.assertTrue(
                    fcntl.fcntl(original_fd, fcntl.F_GETFD)
                    & fcntl.FD_CLOEXEC
                )
                self.assertFalse(
                    fcntl.fcntl(inheritable_fd, fcntl.F_GETFD)
                    & fcntl.FD_CLOEXEC
                )
                self.assertTrue(
                    fcntl.fcntl(cloexec_fd, fcntl.F_GETFD)
                    & fcntl.FD_CLOEXEC
                )
                self.assertTrue(
                    fcntl.fcntl(independent_fd, fcntl.F_GETFD)
                    & fcntl.FD_CLOEXEC
                )
                # Restore the temporary inheritable flag immediately,
                # before ANY event read or other native filesystem work.
                fcntl.fcntl(
                    inheritable_fd, fcntl.F_SETFD,
                    fcntl.fcntl(inheritable_fd, fcntl.F_GETFD)
                    | fcntl.FD_CLOEXEC,
                )

                for fd in (original_fd, inheritable_fd,
                           cloexec_fd, independent_fd):
                    self.assertTrue(
                        fcntl.fcntl(fd, fcntl.F_GETFL) & os.O_NONBLOCK
                    )
                    self.assertTrue(
                        fcntl.fcntl(fd, fcntl.F_GETFD)
                        & fcntl.FD_CLOEXEC
                    )
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # All three FD numbers on the first instance share
                # ONE actual kernel event queue. The independent fourth
                # FD has its own source+parent event receipts.
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.AFTER), len(module.AFTER))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                first_stream = module._read_receipt_pending(inheritable_fd)
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in records(first_stream)
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, name in records(first_stream)
                ))
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(module._read_receipt_pending(cloexec_fd), b"")
                separate = module._read_receipt_pending(independent_fd)
                self.assertGreaterEqual(module._classify_stream(
                    separate, independent_source, independent_parent
                )["source_modify_events"], 1)
                for event_bytes, source, directory in (
                    (first_stream, source_wd, parent_wd),
                    (separate, independent_source, independent_parent),
                ):
                    parsed = module._classify_stream(
                        event_bytes, source, directory
                    )
                    self.assertTrue(parsed["well_formed"])
                    self.assertFalse(parsed["invalidated"])
                    self.assertGreaterEqual(parsed["source_modify_events"], 1)
                    verdict = module._evaluate(
                        module.BEFORE, module.AFTER, event_bytes,
                        source, True, False, directory_watch=directory,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(verdict["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Native removal via the CLOEXEC variant invalidates
                # the same original source WD. The F_DUPFD variant reads
                # its genuine IN_IGNORED while independent FD is intact.
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_rm_watch.argtypes = [ctypes.c_int, ctypes.c_int]
                libc.inotify_rm_watch.restype = ctypes.c_int
                self.assertEqual(
                    libc.inotify_rm_watch(cloexec_fd, source_wd), 0
                )
                ignored = module._read_receipt_pending(inheritable_fd)
                self.assertEqual(records(ignored), [
                    (source_wd, module.IN_IGNORED, b"")
                ])
                self.assertTrue(module._classify_stream(
                    ignored, source_wd, parent_wd
                )["invalidated"])
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(module._read_receipt_pending(cloexec_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.BEFORE),
                                     len(module.BEFORE))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                parent_only = module._read_receipt_pending(cloexec_fd)
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, name in records(parent_only)
                ))
                self.assertFalse(any(
                    wd == source_wd for wd, mask, name in records(parent_only)
                ))
                self.assertEqual(module._read_receipt_pending(inheritable_fd), b"")
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                restored = module._read_receipt_pending(independent_fd)
                self.assertGreaterEqual(module._classify_stream(
                    restored, independent_source, independent_parent
                )["source_modify_events"], 1)
                for event_bytes, source, directory in (
                    (ignored, source_wd, parent_wd),
                    (parent_only, source_wd, parent_wd),
                    (restored, independent_source, independent_parent),
                ):
                    verdict = module._evaluate(
                        module.BEFORE, module.BEFORE, event_bytes, source,
                        True, False, directory_watch=directory,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(verdict["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = os.lstat(sample)
                parent_final = os.lstat(sample.parent)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (initial.st_dev, initial.st_ino, initial.st_mode),
                )
                self.assertEqual(
                    (parent_final.st_dev, parent_final.st_ino, parent_final.st_mode),
                    (parent_initial.st_dev, parent_initial.st_ino,
                     parent_initial.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                for fd in (independent_fd, cloexec_fd,
                           inheritable_fd, original_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
