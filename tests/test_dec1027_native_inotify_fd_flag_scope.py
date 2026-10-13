from __future__ import annotations

import fcntl
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1027", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "native inotify descriptor flags need Linux")
class NativeInotifyDuplicatedDescriptorFlags(unittest.TestCase):
    def test_nonblock_shared_with_dup_but_cloexec_is_per_descriptor(self):
        original_fd = None
        duplicate_fd = None
        independent_fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            pos = 0
            output = []
            while pos < len(stream):
                self.assertGreaterEqual(len(stream) - pos, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(stream, pos)
                pos += module.EVENT.size
                self.assertLessEqual(nbytes, len(stream) - pos)
                name = stream[pos:pos + nbytes].split(b"\x00", 1)[0]
                pos += nbytes
                self.assertEqual(cookie, 0)
                output.append((wd, mask, name))
            self.assertEqual(pos, len(stream))
            return output

        with tempfile.TemporaryDirectory(
            prefix="dec1027-public-inotify-fd-flags-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = os.lstat(sample)
            parent_initial = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                original_fd, source_wd, parent_wd = module._start_watch(sample)
                duplicate_fd = os.dup(original_fd)
                independent_fd, other_source_wd, other_parent_wd = (
                    module._start_watch(sample)
                )
                self.assertEqual(
                    len({original_fd, duplicate_fd, independent_fd}), 3
                )
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(module._read_receipt_pending(duplicate_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Source and its dup share a file DESCRIPTION (F_GETFL),
                # but independent instance has different description.
                for fd in (original_fd, duplicate_fd, independent_fd):
                    self.assertTrue(
                        fcntl.fcntl(fd, fcntl.F_GETFL) & os.O_NONBLOCK
                    )
                    self.assertTrue(
                        fcntl.fcntl(fd, fcntl.F_GETFD) & fcntl.FD_CLOEXEC
                    )

                # FD_CLOEXEC is a descriptor flag: clearing it only on
                # duplicate leaves original and independent unchanged.
                dup_flags = fcntl.fcntl(duplicate_fd, fcntl.F_GETFD)
                try:
                    fcntl.fcntl(
                        duplicate_fd, fcntl.F_SETFD,
                        dup_flags & ~fcntl.FD_CLOEXEC,
                    )
                    self.assertFalse(
                        fcntl.fcntl(duplicate_fd, fcntl.F_GETFD)
                        & fcntl.FD_CLOEXEC
                    )
                    for fd in (original_fd, independent_fd):
                        self.assertTrue(
                            fcntl.fcntl(fd, fcntl.F_GETFD)
                            & fcntl.FD_CLOEXEC
                        )
                finally:
                    fcntl.fcntl(duplicate_fd, fcntl.F_SETFD, dup_flags)
                for fd in (original_fd, duplicate_fd, independent_fd):
                    self.assertTrue(
                        fcntl.fcntl(fd, fcntl.F_GETFD) & fcntl.FD_CLOEXEC
                    )

                # O_NONBLOCK is a STATUS flag on the shared description.
                # Do NOT call any receipt reader during this brief block-
                # mode probe. Always restore nonblock in finally.
                original_status = fcntl.fcntl(original_fd, fcntl.F_GETFL)
                try:
                    fcntl.fcntl(
                        duplicate_fd, fcntl.F_SETFL,
                        original_status & ~os.O_NONBLOCK,
                    )
                    self.assertFalse(
                        fcntl.fcntl(original_fd, fcntl.F_GETFL)
                        & os.O_NONBLOCK
                    )
                    self.assertFalse(
                        fcntl.fcntl(duplicate_fd, fcntl.F_GETFL)
                        & os.O_NONBLOCK
                    )
                    self.assertTrue(
                        fcntl.fcntl(independent_fd, fcntl.F_GETFL)
                        & os.O_NONBLOCK
                    )
                finally:
                    fcntl.fcntl(original_fd, fcntl.F_SETFL, original_status)
                for fd in (original_fd, duplicate_fd, independent_fd):
                    self.assertTrue(
                        fcntl.fcntl(fd, fcntl.F_GETFL) & os.O_NONBLOCK
                    )
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Restored nonblocking native instances continue to
                # record genuine source writes. Reading original queue
                # drains duplicate, not the independent observer.
                for payload in (module.AFTER, module.BEFORE):
                    with sample.open("r+b") as writer:
                        self.assertEqual(writer.write(payload), len(payload))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    original = module._read_receipt_pending(original_fd)
                    self.assertTrue(any(
                        wd == source_wd and mask == module.IN_MODIFY
                        for wd, mask, name in records(original)
                    ))
                    self.assertTrue(any(
                        wd == parent_wd and mask == module.IN_MODIFY
                        and name == b"sample"
                        for wd, mask, name in records(original)
                    ))
                    self.assertEqual(
                        module._read_receipt_pending(duplicate_fd), b""
                    )
                    independent = module._read_receipt_pending(independent_fd)
                    for stream, swd, pwd in (
                        (original, source_wd, parent_wd),
                        (independent, other_source_wd, other_parent_wd),
                    ):
                        classified = module._classify_stream(
                            stream, swd, pwd
                        )
                        self.assertTrue(classified["well_formed"])
                        self.assertFalse(classified["invalidated"])
                        self.assertGreaterEqual(
                            classified["source_modify_events"], 1
                        )
                        self.assertGreaterEqual(
                            classified["source_content_write_events"], 1
                        )
                        verdict = module._evaluate(
                            module.BEFORE, payload, stream, swd,
                            True, False, directory_watch=pwd,
                            directory_inventory_names=("sample",),
                        )
                        self.assertEqual(verdict["status"], "BLOCKED")
                        self.assertIs(
                            verdict["can_authorize_dispatch"], False
                        )
                        self.assertIs(
                            verdict["independent_os_proof_verified"], False
                        )
                    self.assertEqual(
                        module._read_receipt_pending(original_fd), b""
                    )
                    self.assertEqual(
                        module._read_receipt_pending(independent_fd), b""
                    )

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                last = os.lstat(sample)
                parent_last = os.lstat(sample.parent)
                self.assertEqual(
                    (last.st_dev, last.st_ino, last.st_mode),
                    (initial.st_dev, initial.st_ino, initial.st_mode),
                )
                self.assertEqual(
                    (parent_last.st_dev, parent_last.st_ino,
                     parent_last.st_mode),
                    (parent_initial.st_dev, parent_initial.st_ino,
                     parent_initial.st_mode),
                )
                self.assertEqual(
                    module._bounded_inventory_names(sample.parent), ("sample",)
                )
            finally:
                for fd in (independent_fd, duplicate_fd, original_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
