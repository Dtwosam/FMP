from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1037", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "Linux native inotify required")
class NativeQueuedSiblingParentMaskReplacementRegression(unittest.TestCase):
    def test_queued_siblings_survive_mask_change_but_later_siblings_are_lost(self):
        original_fd = None
        alias_fd = None
        independent_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            result = []
            pos = 0
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, size = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(size, len(data) - pos)
                name = data[pos:pos + size].split(b"\x00", 1)[0]
                pos += size
                self.assertEqual(cookie, 0)
                result.append((wd, mask, name))
            self.assertEqual(pos, len(data))
            return result

        def sibling_cycle(parent, name):
            path = parent / name
            self.assertEqual(path.write_bytes(b"PUBLIC-SIBLING"), 14)
            os.unlink(path)

        def verify_pair(events, wd, basename):
            self.assertIn((wd, module.IN_CREATE, basename), events)
            self.assertIn((wd, module.IN_DELETE, basename), events)
            before = events.index((wd, module.IN_CREATE, basename))
            after = events.index((wd, module.IN_DELETE, basename))
            self.assertLess(before, after)

        with tempfile.TemporaryDirectory(
            prefix="dec1037-public-queued-parent-mask-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = os.lstat(sample)
            initial_parent = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                original_fd, source_wd, parent_wd = module._start_watch(sample)
                alias_fd = os.dup(original_fd)
                independent_fd, separate_source_wd, separate_parent_wd = (
                    module._start_watch(sample)
                )
                self.assertEqual(len({original_fd, alias_fd, independent_fd}), 3)
                for fd in (original_fd, alias_fd, independent_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Queue real sibling events under original directory
                # mask. Neither the alias nor original has drained them.
                sibling_cycle(sample.parent, "public-before-mask")
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))

                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32,
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                parent_bytes = module._checked_watch_path_bytes(sample.parent)
                replacement = libc.inotify_add_watch(
                    alias_fd, parent_bytes,
                    module.IN_ATTRIB | module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                self.assertEqual(replacement, parent_wd)

                # SAME WD, no IN_IGNORED. Queued old CREATE/DELETE
                # records remain available even after changing the mask.
                prior = module._read_receipt_pending(original_fd)
                prior_events = records(prior)
                verify_pair(prior_events, parent_wd, b"public-before-mask")
                self.assertFalse(any(
                    mask == module.IN_IGNORED
                    for wd, mask, name in prior_events
                ))
                self.assertTrue(module._classify_stream(
                    prior, source_wd, parent_wd
                )["well_formed"])
                first_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, prior,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(first_verdict["status"], "BLOCKED")
                self.assertIs(first_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    first_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                separate_prior = records(
                    module._read_receipt_pending(independent_fd)
                )
                verify_pair(
                    separate_prior, separate_parent_wd, b"public-before-mask"
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Subsequent real sibling cycle under IN_ATTRIB-only
                # parent mask produces NO original/alias event at all,
                # while the independent instance proves it happened.
                sibling_cycle(sample.parent, "public-during-mask")
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                independent_gap = records(
                    module._read_receipt_pending(independent_fd)
                )
                verify_pair(
                    independent_gap, separate_parent_wd, b"public-during-mask"
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))

                # The original SOURCE watch remains active, and real
                # changed-byte writes still reach it. Parent activity
                # remains silent under reduced mask.
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.AFTER),
                                     len(module.AFTER))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                source_only = module._read_receipt_pending(alias_fd)
                source_events = records(source_only)
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in source_events
                ))
                self.assertFalse(any(
                    wd == parent_wd for wd, mask, name in source_events
                ))
                independent_write = module._read_receipt_pending(independent_fd)
                independent_write_events = records(independent_write)
                self.assertTrue(any(
                    wd == separate_source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in independent_write_events
                ))
                self.assertTrue(any(
                    wd == separate_parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, name in independent_write_events
                ))
                for data, swd, pwd in (
                    (source_only, source_wd, parent_wd),
                    (independent_write, separate_source_wd, separate_parent_wd),
                ):
                    verdict = module._evaluate(
                        module.BEFORE, module.AFTER, data, swd, True, False,
                        directory_watch=pwd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(
                        verdict["independent_os_proof_verified"], False
                    )
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                restored_wd = libc.inotify_add_watch(
                    original_fd, parent_bytes,
                    module.DIRECTORY_MASK | module.IN_ONLYDIR |
                    module.IN_DONT_FOLLOW,
                )
                self.assertEqual(restored_wd, parent_wd)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                sibling_cycle(sample.parent, "public-after-mask")
                final_events = records(module._read_receipt_pending(alias_fd))
                verify_pair(final_events, parent_wd, b"public-after-mask")
                self.assertFalse(any(
                    name == b"public-during-mask"
                    for wd, mask, name in final_events
                ))
                verify_pair(
                    records(module._read_receipt_pending(independent_fd)),
                    separate_parent_wd, b"public-after-mask"
                )
                self.assertEqual(module._read_receipt_pending(original_fd), b"")

                # Final byte restoration is a NEW observed write and
                # cannot supply missing sibling history retroactively.
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.BEFORE),
                                     len(module.BEFORE))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                restored = module._read_receipt_pending(original_fd)
                restored_events = records(restored)
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in restored_events
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample" for wd, mask, name in restored_events
                ))
                parsed_restored = module._classify_stream(
                    restored, source_wd, parent_wd
                )
                self.assertTrue(parsed_restored["well_formed"])
                self.assertFalse(parsed_restored["invalidated"])
                self.assertGreaterEqual(parsed_restored["source_modify_events"], 1)
                final_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, restored,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(final_verdict["status"], "BLOCKED")
                self.assertIs(final_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    final_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                final_independent = module._read_receipt_pending(independent_fd)
                self.assertGreaterEqual(module._classify_stream(
                    final_independent, separate_source_wd, separate_parent_wd
                )["source_modify_events"], 1)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                end = os.lstat(sample)
                parent_end = os.lstat(sample.parent)
                self.assertEqual(
                    (end.st_dev, end.st_ino, end.st_mode),
                    (initial.st_dev, initial.st_ino, initial.st_mode),
                )
                self.assertEqual(
                    (parent_end.st_dev, parent_end.st_ino, parent_end.st_mode),
                    (initial_parent.st_dev, initial_parent.st_ino,
                     initial_parent.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                for fd in (independent_fd, alias_fd, original_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
