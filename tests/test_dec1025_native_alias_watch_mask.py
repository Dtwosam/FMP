from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1025", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_OPEN = 0x00000020
IN_MASK_ADD = 0x20000000  # Native registration option, not event action.


@unittest.skipUnless(sys.platform == "linux", "native inotify mask sharing is Linux-only")
class NativeDupMaskMutationRegression(unittest.TestCase):
    def test_mask_add_via_duplicate_changes_original_instance_not_independent(self):
        original_fd = None
        alias_fd = None
        independent_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            result = []
            pos = 0
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - pos)
                name = data[pos:pos + nbytes].split(b"\x00", 1)[0]
                pos += nbytes
                self.assertEqual(cookie, 0)
                result.append((wd, mask, name))
            self.assertEqual(pos, len(data))
            return result

        with tempfile.TemporaryDirectory(
            prefix="dec1025-public-alias-mask-mutation-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            sample_before = os.lstat(sample)
            parent_before = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                original_fd, source_wd, parent_wd = module._start_watch(sample)
                alias_fd = os.dup(original_fd)
                independent_fd, other_source_wd, other_parent_wd = (
                    module._start_watch(sample)
                )
                self.assertEqual(len({original_fd, alias_fd, independent_fd}), 3)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # The numeric alias_fd is a DIFFERENT descriptor but
                # operates on EXACTLY the SAME registered source WD.
                lib = ctypes.CDLL(None, use_errno=True)
                lib.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32
                ]
                lib.inotify_add_watch.restype = ctypes.c_int
                ctypes.set_errno(0)
                result_wd = lib.inotify_add_watch(
                    alias_fd, module._checked_watch_path_bytes(sample),
                    IN_MASK_ADD | IN_OPEN,
                )
                self.assertEqual(result_wd, source_wd)
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Real sample write now generates OPEN only for ORIGINAL
                # native instance. The untouched independent observer
                # remains on its source+parent well-formed event mask.
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.AFTER), len(module.AFTER))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                augmented = module._read_receipt_pending(original_fd)
                native = records(augmented)
                self.assertIn((source_wd, IN_OPEN, b""), native)
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in native
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample" for wd, mask, name in native
                ))
                self.assertFalse(module._classify_stream(
                    augmented, source_wd, parent_wd
                )["well_formed"])
                blocked = module._evaluate(
                    module.BEFORE, module.AFTER, augmented,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(blocked["status"], "BLOCKED")
                self.assertIs(blocked["can_authorize_dispatch"], False)
                self.assertIs(blocked["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                self.assertEqual(module._read_receipt_pending(original_fd), b"")

                independently_observed = module._read_receipt_pending(independent_fd)
                independent_native = records(independently_observed)
                self.assertFalse(any(
                    mask == IN_OPEN for wd, mask, name in independent_native
                ))
                parsed = module._classify_stream(
                    independently_observed,
                    other_source_wd, other_parent_wd
                )
                self.assertTrue(parsed["well_formed"])
                self.assertFalse(parsed["invalidated"])
                self.assertGreaterEqual(parsed["source_modify_events"], 1)
                other_verdict = module._evaluate(
                    module.BEFORE, module.AFTER, independently_observed,
                    other_source_wd, True, False,
                    directory_watch=other_parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(other_verdict["status"], "BLOCKED")
                self.assertIs(other_verdict["can_authorize_dispatch"], False)
                self.assertIs(other_verdict["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # Closing the alias cannot undo the mutation already
                # made to the surviving original kernel instance.
                os.close(alias_fd)
                alias_fd = None
                os.fstat(original_fd)
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(module.BEFORE), len(module.BEFORE))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                again = module._read_receipt_pending(original_fd)
                again_native = records(again)
                self.assertIn((source_wd, IN_OPEN, b""), again_native)
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in again_native
                ))
                self.assertFalse(module._classify_stream(
                    again, source_wd, parent_wd
                )["well_formed"])
                return_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, again,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(return_verdict["status"], "BLOCKED")
                self.assertIs(return_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    return_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(original_fd), b"")

                independent_restore = module._read_receipt_pending(independent_fd)
                self.assertTrue(module._classify_stream(
                    independent_restore, other_source_wd, other_parent_wd
                )["well_formed"])
                self.assertFalse(any(
                    mask == IN_OPEN for wd, mask, name in records(independent_restore)
                ))
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = os.lstat(sample)
                parent_final = os.lstat(sample.parent)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (sample_before.st_dev, sample_before.st_ino,
                     sample_before.st_mode),
                )
                self.assertEqual(
                    (parent_final.st_dev, parent_final.st_ino, parent_final.st_mode),
                    (parent_before.st_dev, parent_before.st_ino,
                     parent_before.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                for fd in (alias_fd, independent_fd, original_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
