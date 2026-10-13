from __future__ import annotations

import array
import fcntl
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import termios
import ctypes
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1042", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "Linux native inotify FIONREAD only")
class NativeInotifyFionreadBlackoutRegression(unittest.TestCase):
    def test_zero_pending_bytes_on_aliased_dual_watches_cannot_prove_no_writes(self):
        primary_fd = None
        alias_fd = None
        independent_fd = None

        def pending_bytes(fd):
            size = array.array("i", [0])
            fcntl.ioctl(fd, termios.FIONREAD, size, True)
            self.assertGreaterEqual(size[0], 0)
            return size[0]

        def events(stream):
            self.assertIs(type(stream), bytes)
            result = []
            offset = 0
            while offset < len(stream):
                self.assertGreaterEqual(len(stream) - offset, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(stream, offset)
                offset += module.EVENT.size
                self.assertLessEqual(nbytes, len(stream) - offset)
                name = stream[offset:offset + nbytes].split(b"\x00", 1)[0]
                offset += nbytes
                self.assertEqual(cookie, 0)
                result.append((wd, mask, name))
            self.assertEqual(offset, len(stream))
            return result

        def write(path, content):
            with path.open("r+b") as writer:
                self.assertEqual(writer.write(content), len(content))
                writer.truncate()
                writer.flush()
                os.fsync(writer.fileno())

        with tempfile.TemporaryDirectory(
            prefix="dec1042-public-fionread-blackout-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first = os.lstat(sample)
            first_parent = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                primary_fd, source_wd, parent_wd = module._start_watch(sample)
                alias_fd = os.dup(primary_fd)
                independent_fd, other_source_wd, other_parent_wd = (
                    module._start_watch(sample)
                )
                self.assertEqual(len({primary_fd, alias_fd, independent_fd}), 3)
                for fd in (primary_fd, alias_fd, independent_fd):
                    self.assertEqual(pending_bytes(fd), 0)
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # With full masks, genuine public source writes enqueue
                # events for BOTH native instances, but duplicate FD
                # reads/counters describe one SHARED underlying queue.
                write(sample, module.AFTER)
                original_count = pending_bytes(primary_fd)
                self.assertGreaterEqual(original_count, module.EVENT.size)
                self.assertEqual(pending_bytes(alias_fd), original_count)
                independent_count = pending_bytes(independent_fd)
                self.assertGreaterEqual(independent_count, module.EVENT.size)
                original_events = module._read_receipt_pending(alias_fd)
                self.assertEqual(len(original_events), original_count)
                self.assertGreaterEqual(module._classify_stream(
                    original_events, source_wd, parent_wd
                )["source_modify_events"], 1)
                self.assertEqual(pending_bytes(primary_fd), 0)
                self.assertEqual(pending_bytes(alias_fd), 0)
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(pending_bytes(independent_fd), independent_count)
                independent_events = module._read_receipt_pending(independent_fd)
                self.assertEqual(len(independent_events), independent_count)
                self.assertGreaterEqual(module._classify_stream(
                    independent_events, other_source_wd, other_parent_wd
                )["source_modify_events"], 1)
                for stream, swd, pwd in (
                    (original_events, source_wd, parent_wd),
                    (independent_events, other_source_wd, other_parent_wd),
                ):
                    result = module._evaluate(
                        module.BEFORE, module.AFTER, stream, swd,
                        True, False, directory_watch=pwd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(result["status"], "BLOCKED")
                    self.assertIs(result["can_authorize_dispatch"], False)
                    self.assertIs(
                        result["independent_os_proof_verified"], False
                    )
                self.assertEqual(pending_bytes(independent_fd), 0)

                # Genuine alias-origin mask REPLACEMENT for both source
                # and parent leaves both WDs installed and FIONREAD=0.
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32,
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                src = module._checked_watch_path_bytes(sample)
                parent = module._checked_watch_path_bytes(sample.parent)
                self.assertEqual(libc.inotify_add_watch(
                    alias_fd, src, module.IN_ATTRIB | module.IN_DONT_FOLLOW,
                ), source_wd)
                self.assertEqual(libc.inotify_add_watch(
                    alias_fd, parent,
                    module.IN_ATTRIB | module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                ), parent_wd)
                self.assertEqual(pending_bytes(primary_fd), 0)
                self.assertEqual(pending_bytes(independent_fd), 0)

                # Actual changed-byte restoration AND transient sibling
                # create/delete occur with no source/parent events
                # in first instance. Independent observer sees both.
                write(sample, module.BEFORE)
                transient = sample.parent / "public-fionread-sibling"
                self.assertEqual(transient.write_bytes(b"PUBLIC-SIBLING"),
                                 len(b"PUBLIC-SIBLING"))
                os.unlink(transient)
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
                self.assertEqual(pending_bytes(primary_fd), 0)
                self.assertEqual(pending_bytes(alias_fd), 0)
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")

                actual_independent_count = pending_bytes(independent_fd)
                self.assertGreaterEqual(actual_independent_count,
                                        2 * module.EVENT.size)
                witness = module._read_receipt_pending(independent_fd)
                self.assertEqual(len(witness), actual_independent_count)
                native = events(witness)
                self.assertTrue(any(
                    wd == other_source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in native
                ))
                self.assertTrue(any(
                    wd == other_parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, name in native
                ))
                for mask in (module.IN_CREATE, module.IN_DELETE):
                    self.assertIn(
                        (other_parent_wd, mask, b"public-fionread-sibling"),
                        native,
                    )
                witness_parsed = module._classify_stream(
                    witness, other_source_wd, other_parent_wd
                )
                self.assertTrue(witness_parsed["well_formed"])
                self.assertGreaterEqual(witness_parsed["source_modify_events"], 1)
                self.assertGreaterEqual(
                    witness_parsed["transient_create_delete_pairs"], 1
                )
                witness_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, witness,
                    other_source_wd, True, False,
                    directory_watch=other_parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(witness_verdict["status"], "BLOCKED")
                self.assertIs(
                    witness_verdict["can_authorize_dispatch"], False
                )
                self.assertIs(
                    witness_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(pending_bytes(independent_fd), 0)
                apparent = module._evaluate(
                    module.BEFORE, module.BEFORE, b"",
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(apparent["status"], "BLOCKED")
                self.assertIs(apparent["can_authorize_dispatch"], False)
                self.assertIs(
                    apparent["independent_os_proof_verified"], False
                )

                # Restore full native masks at SAME source+parent WDs.
                # FIONREAD remains zero, with no retroactive events.
                self.assertEqual(libc.inotify_add_watch(
                    primary_fd, src, module.MASK | module.IN_DONT_FOLLOW,
                ), source_wd)
                self.assertEqual(libc.inotify_add_watch(
                    primary_fd, parent, module.DIRECTORY_MASK |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                ), parent_wd)
                for fd in (primary_fd, alias_fd, independent_fd):
                    self.assertEqual(pending_bytes(fd), 0)

                # Later real writes generate events again; sharing and
                # independence of pending-byte counters remains intact.
                for content in (module.AFTER, module.BEFORE):
                    write(sample, content)
                    original_bytes = pending_bytes(primary_fd)
                    self.assertGreater(original_bytes, 0)
                    self.assertEqual(original_bytes, pending_bytes(alias_fd))
                    second_bytes = pending_bytes(independent_fd)
                    self.assertGreater(second_bytes, 0)
                    resumed = module._read_receipt_pending(primary_fd)
                    self.assertEqual(len(resumed), original_bytes)
                    self.assertGreaterEqual(module._classify_stream(
                        resumed, source_wd, parent_wd
                    )["source_modify_events"], 1)
                    self.assertEqual(pending_bytes(alias_fd), 0)
                    separate = module._read_receipt_pending(independent_fd)
                    self.assertEqual(len(separate), second_bytes)
                    self.assertGreaterEqual(module._classify_stream(
                        separate, other_source_wd, other_parent_wd
                    )["source_modify_events"], 1)
                    for stream, swd, pwd in (
                        (resumed, source_wd, parent_wd),
                        (separate, other_source_wd, other_parent_wd),
                    ):
                        verdict = module._evaluate(
                            module.BEFORE, content, stream, swd,
                            True, False, directory_watch=pwd,
                            directory_inventory_names=("sample",),
                        )
                        self.assertEqual(verdict["status"], "BLOCKED")
                        self.assertIs(verdict["can_authorize_dispatch"], False)
                        self.assertIs(
                            verdict["independent_os_proof_verified"], False
                        )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = os.lstat(sample)
                final_parent = os.lstat(sample.parent)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (first.st_dev, first.st_ino, first.st_mode),
                )
                self.assertEqual(
                    (final_parent.st_dev, final_parent.st_ino, final_parent.st_mode),
                    (first_parent.st_dev, first_parent.st_ino,
                     first_parent.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                for fd in (independent_fd, alias_fd, primary_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
