from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1031", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "native Linux watch masks only")
class NativeDuplicateParentMaskReplacementGap(unittest.TestCase):
    def test_parent_mask_replacement_misses_sibling_lifecycle_despite_same_wd(self):
        original_fd = None
        alias_fd = None
        independent_fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            parsed = []
            pos = 0
            while pos < len(stream):
                self.assertGreaterEqual(len(stream) - pos, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(stream, pos)
                pos += module.EVENT.size
                self.assertLessEqual(nbytes, len(stream) - pos)
                name = stream[pos:pos + nbytes].split(b"\x00", 1)[0]
                pos += nbytes
                self.assertEqual(cookie, 0)
                parsed.append((wd, mask, name))
            self.assertEqual(pos, len(stream))
            return parsed

        with tempfile.TemporaryDirectory(
            prefix="dec1031-public-parent-mask-gap-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            sample.write_bytes(module.BEFORE)
            before = os.lstat(sample)
            parent_before = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent), ("sample",))
            try:
                original_fd, source_wd, parent_wd = module._start_watch(sample)
                alias_fd = os.dup(original_fd)
                independent_fd, other_source_wd, other_parent_wd = (
                    module._start_watch(sample)
                )
                self.assertEqual(len({original_fd, alias_fd, independent_fd}), 3)
                for fd in (original_fd, alias_fd, independent_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                lib = ctypes.CDLL(None, use_errno=True)
                lib.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32
                ]
                lib.inotify_add_watch.restype = ctypes.c_int
                parent_path = module._checked_watch_path_bytes(sample.parent)

                # Without IN_MASK_ADD the alias replaces the ORIGINAL
                # parent mask with IN_ATTRIB only. The parent WD integer
                # stays identical, but CREATE/DELETE coverage vanishes.
                replacement_wd = lib.inotify_add_watch(
                    alias_fd, parent_path,
                    module.IN_ATTRIB | module.IN_ONLYDIR | module.IN_DONT_FOLLOW
                )
                self.assertEqual(replacement_wd, parent_wd)
                for fd in (original_fd, independent_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                sibling = sample.parent / "public-mask-gap-sibling"
                self.assertEqual(sibling.write_bytes(b"PUBLIC-TRANSIENT"),
                                 len(b"PUBLIC-TRANSIENT"))
                os.unlink(sibling)
                # Empty original queue is NOT an independent census.
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                gap = module._read_receipt_pending(independent_fd)
                gap_records = records(gap)
                self.assertIn(
                    (other_parent_wd, module.IN_CREATE,
                     b"public-mask-gap-sibling"), gap_records
                )
                self.assertIn(
                    (other_parent_wd, module.IN_DELETE,
                     b"public-mask-gap-sibling"), gap_records
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))

                # Original SOURCE mask stays intact and sees a real file
                # write while original PARENT remains blind to its name.
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.AFTER), len(module.AFTER))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                source_only = module._read_receipt_pending(original_fd)
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in records(source_only)
                ))
                self.assertFalse(any(
                    wd == parent_wd for wd, mask, name in records(source_only)
                ))
                other_write = module._read_receipt_pending(independent_fd)
                self.assertTrue(any(
                    wd == other_source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in records(other_write)
                ))
                self.assertTrue(any(
                    wd == other_parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, name in records(other_write)
                ))
                for stream, swd, pwd in (
                    (source_only, source_wd, parent_wd),
                    (other_write, other_source_wd, other_parent_wd),
                ):
                    result = module._evaluate(
                        module.BEFORE, module.AFTER, stream, swd,
                        True, False, directory_watch=pwd,
                        directory_inventory_names=("sample",)
                    )
                    self.assertEqual(result["status"], "BLOCKED")
                    self.assertIs(result["can_authorize_dispatch"], False)
                    self.assertIs(result["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Reinstall old parent mask on SAME WD. Neither native FD
                # can retroactively report the vanished transient sibling.
                original_wd_again = lib.inotify_add_watch(
                    original_fd, parent_path,
                    module.DIRECTORY_MASK | module.IN_ONLYDIR |
                    module.IN_DONT_FOLLOW
                )
                self.assertEqual(original_wd_again, parent_wd)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                later = sample.parent / "public-mask-restored-sibling"
                self.assertEqual(later.write_bytes(b"PUBLIC-LATER"),
                                 len(b"PUBLIC-LATER"))
                os.unlink(later)
                later_stream = module._read_receipt_pending(alias_fd)
                later_events = records(later_stream)
                self.assertIn(
                    (parent_wd, module.IN_CREATE,
                     b"public-mask-restored-sibling"), later_events
                )
                self.assertIn(
                    (parent_wd, module.IN_DELETE,
                     b"public-mask-restored-sibling"), later_events
                )
                self.assertFalse(any(
                    name == b"public-mask-gap-sibling"
                    for wd, mask, name in later_events
                ))
                separate_later = records(
                    module._read_receipt_pending(independent_fd)
                )
                self.assertIn(
                    (other_parent_wd, module.IN_CREATE,
                     b"public-mask-restored-sibling"), separate_later
                )
                self.assertIn(
                    (other_parent_wd, module.IN_DELETE,
                     b"public-mask-restored-sibling"), separate_later
                )
                self.assertEqual(module._read_receipt_pending(original_fd), b"")

                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.BEFORE),
                                     len(module.BEFORE))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                restored = module._read_receipt_pending(original_fd)
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in records(restored)
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, name in records(restored)
                ))
                restored_parse = module._classify_stream(
                    restored, source_wd, parent_wd
                )
                self.assertTrue(restored_parse["well_formed"])
                self.assertFalse(restored_parse["invalidated"])
                restored_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, restored,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",)
                )
                self.assertEqual(restored_verdict["status"], "BLOCKED")
                self.assertIs(restored_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    restored_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                full_restore = module._read_receipt_pending(independent_fd)
                self.assertGreaterEqual(module._classify_stream(
                    full_restore, other_source_wd, other_parent_wd
                )["source_modify_events"], 1)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = os.lstat(sample)
                parent_final = os.lstat(sample.parent)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (before.st_dev, before.st_ino, before.st_mode)
                )
                self.assertEqual(
                    (parent_final.st_dev, parent_final.st_ino, parent_final.st_mode),
                    (parent_before.st_dev, parent_before.st_ino,
                     parent_before.st_mode)
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                for fd in (independent_fd, alias_fd, original_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
