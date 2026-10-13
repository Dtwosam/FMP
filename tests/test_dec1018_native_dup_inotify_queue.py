from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1018", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "native inotify FD aliases need Linux")
class NativeDuplicatedInotifyFDRegression(unittest.TestCase):
    def test_dup_shares_queue_and_watch_lifetime_unlike_independent_fd(self):
        primary_fd = None
        alias_fd = None
        independent_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            offset = 0
            parsed = []
            while offset < len(data):
                self.assertGreaterEqual(len(data) - offset, module.EVENT.size)
                wd, mask, cookie, n = module.EVENT.unpack_from(data, offset)
                offset += module.EVENT.size
                self.assertLessEqual(n, len(data) - offset)
                name = data[offset:offset + n].split(b"\x00", 1)[0]
                offset += n
                self.assertEqual(cookie, 0)
                parsed.append((wd, mask, name))
            self.assertEqual(offset, len(data))
            return parsed

        with tempfile.TemporaryDirectory(
            prefix="dec1018-public-shared-inotify-queue-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = os.lstat(sample)
            parent_initial = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                primary_fd, source_wd, parent_wd = module._start_watch(sample)
                alias_fd = os.dup(primary_fd)
                independent_fd, other_source_wd, other_parent_wd = (
                    module._start_watch(sample)
                )
                self.assertEqual(len({primary_fd, alias_fd, independent_fd}), 3)
                self.assertNotEqual(source_wd, parent_wd)
                self.assertNotEqual(other_source_wd, other_parent_wd)
                for fd in (primary_fd, alias_fd, independent_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # An alias FD is NOT a separate observer: draining via
                # the duplicate consumes the ORIGINAL's shared queue.
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.AFTER), len(module.AFTER))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                shared_stream = module._read_receipt_pending(alias_fd)
                self.assertTrue(shared_stream)
                original = module._classify_stream(
                    shared_stream, source_wd, parent_wd
                )
                self.assertTrue(original["well_formed"])
                self.assertFalse(original["invalidated"])
                self.assertGreaterEqual(original["source_modify_events"], 1)
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample" for wd, mask, name in records(shared_stream)
                ))
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                independent_stream = module._read_receipt_pending(independent_fd)
                second = module._classify_stream(
                    independent_stream, other_source_wd, other_parent_wd
                )
                self.assertTrue(second["well_formed"])
                self.assertGreaterEqual(second["source_modify_events"], 1)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")
                for data, wd, dir_wd in (
                    (shared_stream, source_wd, parent_wd),
                    (independent_stream, other_source_wd, other_parent_wd),
                ):
                    verdict = module._evaluate(
                        module.BEFORE, module.AFTER, data, wd, True,
                        False, directory_watch=dir_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(verdict["independent_os_proof_verified"], False)

                # Removing source watch through dup modifies the SAME
                # inotify instance. Its original FD reads IN_IGNORED;
                # the independent observer has not lost any watch.
                lib = ctypes.CDLL(None, use_errno=True)
                lib.inotify_rm_watch.argtypes = [ctypes.c_int, ctypes.c_int]
                lib.inotify_rm_watch.restype = ctypes.c_int
                self.assertEqual(lib.inotify_rm_watch(alias_fd, source_wd), 0)
                source_ignored = module._read_receipt_pending(primary_fd)
                self.assertEqual(records(source_ignored), [
                    (source_wd, module.IN_IGNORED, b"")
                ])
                self.assertTrue(module._classify_stream(
                    source_ignored, source_wd, parent_wd
                )["invalidated"])
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Source restore still reaches the shared-instance
                # PARENT but not its removed source WD; independent FD
                # retains genuine source + named parent write evidence.
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.BEFORE),
                                     len(module.BEFORE))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                parent_only = module._read_receipt_pending(primary_fd)
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample" for wd, mask, name in records(parent_only)
                ))
                self.assertFalse(any(
                    wd == source_wd for wd, mask, name in records(parent_only)
                ))
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                independently_restored = module._read_receipt_pending(independent_fd)
                self.assertGreaterEqual(module._classify_stream(
                    independently_restored, other_source_wd, other_parent_wd
                )["source_modify_events"], 1)
                for data, wd, dir_wd in (
                    (source_ignored, source_wd, parent_wd),
                    (parent_only, source_wd, parent_wd),
                    (independently_restored, other_source_wd, other_parent_wd),
                ):
                    result = module._evaluate(
                        module.BEFORE, module.BEFORE, data, wd, True,
                        False, directory_watch=dir_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(result["status"], "BLOCKED")
                    self.assertIs(result["can_authorize_dispatch"], False)
                    self.assertIs(result["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Remove remaining parent through alias. The original
                # FD receives IN_IGNORED and shares the now-empty queue.
                self.assertEqual(lib.inotify_rm_watch(alias_fd, parent_wd), 0)
                parent_ignored = module._read_receipt_pending(primary_fd)
                self.assertEqual(records(parent_ignored), [
                    (parent_wd, module.IN_IGNORED, b"")
                ])
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # A third real write is quiet on both ALIASED descriptors.
                # The unrelated instance remains a valid independent
                # witness of the public source mutation.
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.AFTER), len(module.AFTER))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                untouched = module._read_receipt_pending(independent_fd)
                self.assertGreaterEqual(module._classify_stream(
                    untouched, other_source_wd, other_parent_wd
                )["source_modify_events"], 1)
                verdict = module._evaluate(
                    module.BEFORE, module.AFTER, untouched,
                    other_source_wd, True, False,
                    directory_watch=other_parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(verdict["status"], "BLOCKED")
                self.assertIs(verdict["can_authorize_dispatch"], False)
                self.assertIs(verdict["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Closing the duplicate does not close the original
                # native inotify FD or make it an independent instance.
                os.close(alias_fd)
                alias_fd = None
                os.fstat(primary_fd)
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.BEFORE),
                                     len(module.BEFORE))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                fresh = module._read_receipt_pending(independent_fd)
                self.assertGreaterEqual(module._classify_stream(
                    fresh, other_source_wd, other_parent_wd
                )["source_modify_events"], 1)
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
                for fd in (alias_fd, independent_fd, primary_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
