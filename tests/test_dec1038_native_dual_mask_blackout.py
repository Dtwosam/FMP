from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1038", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "Linux inotify only")
class NativeDualMaskBlackoutRegression(unittest.TestCase):
    def test_both_masks_replaced_same_wds_silence_real_write_and_sibling(self):
        primary_fd = None
        duplicate_fd = None
        independent_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            result = []
            offset = 0
            while offset < len(data):
                self.assertGreaterEqual(len(data) - offset, module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(data, offset)
                offset += module.EVENT.size
                self.assertLessEqual(length, len(data) - offset)
                name = data[offset:offset + length].split(b"\x00", 1)[0]
                offset += length
                self.assertEqual(cookie, 0)
                result.append((wd, mask, name))
            self.assertEqual(offset, len(data))
            return result

        def write_sample(path, data):
            with path.open("r+b") as writer:
                self.assertEqual(writer.write(data), len(data))
                writer.truncate()
                writer.flush()
                os.fsync(writer.fileno())

        def sibling_cycle(parent, name):
            sibling = parent / name
            self.assertEqual(
                sibling.write_bytes(b"DISPOSABLE-PUBLIC"), len(b"DISPOSABLE-PUBLIC")
            )
            os.unlink(sibling)

        with tempfile.TemporaryDirectory(
            prefix="dec1038-public-dual-mask-blackout-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first = os.lstat(sample)
            parent_first = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                primary_fd, source_wd, parent_wd = module._start_watch(sample)
                duplicate_fd = os.dup(primary_fd)
                independent_fd, other_source_wd, other_parent_wd = (
                    module._start_watch(sample)
                )
                self.assertEqual(len({
                    primary_fd, duplicate_fd, independent_fd
                }), 3)
                for fd in (primary_fd, duplicate_fd, independent_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                source_bytes = module._checked_watch_path_bytes(sample)
                parent_bytes = module._checked_watch_path_bytes(sample.parent)

                # BOTH original subscriptions are degraded via an
                # aliased FD WITHOUT IN_MASK_ADD. Neither WD changes or
                # generates IN_IGNORED, yet content/census coverage ends.
                self.assertEqual(libc.inotify_add_watch(
                    duplicate_fd, source_bytes,
                    module.IN_ATTRIB | module.IN_DONT_FOLLOW,
                ), source_wd)
                self.assertEqual(libc.inotify_add_watch(
                    duplicate_fd, parent_bytes,
                    module.IN_ATTRIB | module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                ), parent_wd)
                for fd in (primary_fd, duplicate_fd, independent_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Make BOTH a true changed-byte source write and a real
                # transient sibling creation/deletion. First instance
                # reports no event whatsoever, although both WDs exist.
                write_sample(sample, module.AFTER)
                sibling_cycle(sample.parent, "public-hidden-sibling")
                self.assertEqual(sample.read_bytes(), module.AFTER)
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")
                self.assertEqual(module._read_receipt_pending(duplicate_fd), b"")
                true_events = module._read_receipt_pending(independent_fd)
                actual = records(true_events)
                self.assertTrue(any(
                    wd == other_source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in actual
                ))
                self.assertTrue(any(
                    wd == other_parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, name in actual
                ))
                for mask in (module.IN_CREATE, module.IN_DELETE):
                    self.assertIn(
                        (other_parent_wd, mask, b"public-hidden-sibling"), actual
                    )
                parsed = module._classify_stream(
                    true_events, other_source_wd, other_parent_wd
                )
                self.assertTrue(parsed["well_formed"])
                self.assertFalse(parsed["invalidated"])
                self.assertGreaterEqual(parsed["source_modify_events"], 1)
                self.assertGreaterEqual(parsed["directory_changes"], 2)
                blocked = module._evaluate(
                    module.BEFORE, module.AFTER, true_events,
                    other_source_wd, True, False,
                    directory_watch=other_parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(blocked["status"], "BLOCKED")
                self.assertIs(blocked["can_authorize_dispatch"], False)
                self.assertIs(blocked["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))

                # Restoring original masks retains SAME WD numbers and
                # produces no retrospective evidence of the blackout.
                self.assertEqual(libc.inotify_add_watch(
                    primary_fd, source_bytes,
                    module.MASK | module.IN_DONT_FOLLOW,
                ), source_wd)
                self.assertEqual(libc.inotify_add_watch(
                    primary_fd, parent_bytes,
                    module.DIRECTORY_MASK | module.IN_ONLYDIR |
                    module.IN_DONT_FOLLOW,
                ), parent_wd)
                for fd in (primary_fd, duplicate_fd, independent_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                sibling_cycle(sample.parent, "public-after-blackout")
                after_sibling = records(
                    module._read_receipt_pending(duplicate_fd)
                )
                for mask in (module.IN_CREATE, module.IN_DELETE):
                    self.assertIn(
                        (parent_wd, mask, b"public-after-blackout"),
                        after_sibling
                    )
                self.assertFalse(any(
                    name == b"public-hidden-sibling"
                    for wd, mask, name in after_sibling
                ))
                independently_later = records(
                    module._read_receipt_pending(independent_fd)
                )
                for mask in (module.IN_CREATE, module.IN_DELETE):
                    self.assertIn(
                        (other_parent_wd, mask, b"public-after-blackout"),
                        independently_later
                    )
                self.assertEqual(module._read_receipt_pending(primary_fd), b"")

                # Source restore only proves new post-gap observation.
                write_sample(sample, module.BEFORE)
                return_events = module._read_receipt_pending(primary_fd)
                native = records(return_events)
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in native
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, name in native
                ))
                self.assertFalse(any(
                    mask == module.IN_IGNORED for wd, mask, name in native
                ))
                return_parsed = module._classify_stream(
                    return_events, source_wd, parent_wd
                )
                self.assertTrue(return_parsed["well_formed"])
                self.assertFalse(return_parsed["invalidated"])
                self.assertGreaterEqual(return_parsed["source_modify_events"], 1)
                verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, return_events,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(verdict["status"], "BLOCKED")
                self.assertIs(verdict["can_authorize_dispatch"], False)
                self.assertIs(verdict["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(duplicate_fd), b"")
                independent_return = module._read_receipt_pending(independent_fd)
                self.assertGreaterEqual(module._classify_stream(
                    independent_return, other_source_wd, other_parent_wd
                )["source_modify_events"], 1)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                last = os.lstat(sample)
                parent_last = os.lstat(sample.parent)
                self.assertEqual(
                    (last.st_dev, last.st_ino, last.st_mode),
                    (first.st_dev, first.st_ino, first.st_mode),
                )
                self.assertEqual(
                    (parent_last.st_dev, parent_last.st_ino, parent_last.st_mode),
                    (parent_first.st_dev, parent_first.st_ino,
                     parent_first.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                for fd in (independent_fd, duplicate_fd, primary_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
