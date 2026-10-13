from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1040", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "requires Linux inotify")
class NativeDualMaskWriteRestoreBlackout(unittest.TestCase):
    def test_unchanged_final_bytes_and_inventory_hide_real_activity_under_both_reduced_masks(self):
        primary_fd = None
        alias_fd = None
        witness_fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            offset = 0
            output = []
            while offset < len(stream):
                self.assertGreaterEqual(len(stream) - offset, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(stream, offset)
                offset += module.EVENT.size
                self.assertLessEqual(nbytes, len(stream) - offset)
                name = stream[offset:offset + nbytes].split(b"\x00", 1)[0]
                offset += nbytes
                self.assertEqual(cookie, 0)
                output.append((wd, mask, name))
            self.assertEqual(offset, len(stream))
            return output

        def write(path, content):
            with path.open("r+b") as writer:
                self.assertEqual(writer.write(content), len(content))
                writer.truncate()
                writer.flush()
                os.fsync(writer.fileno())

        with tempfile.TemporaryDirectory(
            prefix="dec1040-public-write-restore-blackout-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first = os.lstat(sample)
            first_parent = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent), ("sample",))
            try:
                primary_fd, source_wd, parent_wd = module._start_watch(sample)
                alias_fd = os.dup(primary_fd)
                witness_fd, witness_source_wd, witness_parent_wd = (
                    module._start_watch(sample)
                )
                self.assertEqual(len({primary_fd, alias_fd, witness_fd}), 3)
                for fd in (primary_fd, alias_fd, witness_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32,
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                source_bytes = module._checked_watch_path_bytes(sample)
                parent_bytes = module._checked_watch_path_bytes(sample.parent)

                # Replace BOTH source and parent masks through alias,
                # without IN_MASK_ADD. Both original WDs stay unchanged
                # and no IN_IGNORED is emitted.
                self.assertEqual(libc.inotify_add_watch(
                    alias_fd, source_bytes,
                    module.IN_ATTRIB | module.IN_DONT_FOLLOW,
                ), source_wd)
                self.assertEqual(libc.inotify_add_watch(
                    alias_fd, parent_bytes,
                    module.IN_ATTRIB | module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                ), parent_wd)
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(module._read_receipt_pending(witness_fd), b"")

                # TWO real source writes, with original bytes restored
                # BEFORE either subscription is restored. A real public
                # ephemeral sibling is created and removed in the gap.
                write(sample, module.AFTER)
                self.assertEqual(sample.read_bytes(), module.AFTER)
                write(sample, module.BEFORE)
                transient = sample.parent / "public-write-restore-sibling"
                self.assertEqual(transient.write_bytes(b"PUBLIC-TEMP"),
                                 len(b"PUBLIC-TEMP"))
                os.unlink(transient)
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))

                # An actual native observer with TWO live WDs can be
                # completely quiet after both subscribed masks change.
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                empty_parse = module._classify_stream(b"", source_wd, parent_wd)
                self.assertTrue(empty_parse["well_formed"])
                self.assertEqual(empty_parse["source_modify_events"], 0)
                self.assertEqual(empty_parse["directory_changes"], 0)
                # Never mistake a superficially clean synthetic receipt
                # for independent OS-enforced no-write authorization.
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

                witnessed = module._read_receipt_pending(witness_fd)
                actual = records(witnessed)
                self.assertGreaterEqual(sum(
                    wd == witness_source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in actual
                ), 2)
                self.assertGreaterEqual(sum(
                    wd == witness_source_wd and mask == module.IN_CLOSE_WRITE
                    for wd, mask, name in actual
                ), 2)
                self.assertGreaterEqual(sum(
                    wd == witness_parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, name in actual
                ), 2)
                for mask in (module.IN_CREATE, module.IN_DELETE):
                    self.assertIn(
                        (witness_parent_wd, mask,
                         b"public-write-restore-sibling"), actual
                    )
                parsed = module._classify_stream(
                    witnessed, witness_source_wd, witness_parent_wd
                )
                self.assertTrue(parsed["well_formed"])
                self.assertFalse(parsed["invalidated"])
                self.assertGreaterEqual(parsed["source_modify_events"], 2)
                self.assertGreaterEqual(
                    parsed["transient_create_delete_pairs"], 1
                )
                true_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, witnessed,
                    witness_source_wd, True, False,
                    directory_watch=witness_parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(true_verdict["status"], "BLOCKED")
                self.assertIs(true_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    true_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(witness_fd), b"")

                # Reinstall BOTH full masks, retaining BOTH original
                # WDs. No native replay of the earlier real activity.
                self.assertEqual(libc.inotify_add_watch(
                    primary_fd, source_bytes,
                    module.MASK | module.IN_DONT_FOLLOW,
                ), source_wd)
                self.assertEqual(libc.inotify_add_watch(
                    primary_fd, parent_bytes,
                    module.DIRECTORY_MASK | module.IN_ONLYDIR |
                    module.IN_DONT_FOLLOW,
                ), parent_wd)
                for fd in (primary_fd, alias_fd, witness_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Real later public write and restore must be observable,
                # but cannot repair prior evidence-free interval.
                for content in (module.AFTER, module.BEFORE):
                    write(sample, content)
                    current = module._read_receipt_pending(alias_fd)
                    events = records(current)
                    self.assertTrue(any(
                        wd == source_wd and mask == module.IN_MODIFY
                        for wd, mask, name in events
                    ))
                    self.assertTrue(any(
                        wd == parent_wd and mask == module.IN_MODIFY
                        and name == b"sample"
                        for wd, mask, name in events
                    ))
                    self.assertTrue(module._classify_stream(
                        current, source_wd, parent_wd
                    )["well_formed"])
                    verdict = module._evaluate(
                        module.BEFORE, content, current, source_wd,
                        True, False, directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(
                        verdict["independent_os_proof_verified"], False
                    )
                    self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                    second = module._read_receipt_pending(witness_fd)
                    self.assertGreaterEqual(module._classify_stream(
                        second, witness_source_wd, witness_parent_wd
                    )["source_modify_events"], 1)
                    self.assertEqual(module._read_receipt_pending(witness_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                last = os.lstat(sample)
                last_parent = os.lstat(sample.parent)
                self.assertEqual(
                    (last.st_dev, last.st_ino, last.st_mode),
                    (first.st_dev, first.st_ino, first.st_mode),
                )
                self.assertEqual(
                    (last_parent.st_dev, last_parent.st_ino, last_parent.st_mode),
                    (first_parent.st_dev, first_parent.st_ino,
                     first_parent.st_mode),
                )
                self.assertEqual(
                    module._bounded_inventory_names(sample.parent), ("sample",)
                )
            finally:
                for fd in (witness_fd, alias_fd, primary_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
