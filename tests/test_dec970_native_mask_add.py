from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec970", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# These flags are native Linux inotify registration/event UAPI values.
# The observer deliberately does not accept IN_OPEN as an observed write.
IN_OPEN = 0x00000020
IN_MASK_ADD = 0x20000000


@unittest.skipUnless(sys.platform == "linux", "native inotify mask-add is Linux-only")
class NativeMaskAddRegression(unittest.TestCase):
    def test_real_mask_add_preserves_source_writes_but_extra_open_blocks(self):
        fd = None
        with tempfile.TemporaryDirectory(
            prefix="dec970-public-native-mask-add-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first_stat = os.lstat(sample)
            parent_stat = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertNotEqual(source_wd, parent_wd)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                lib = module.ctypes.CDLL(None, use_errno=True)
                lib.inotify_add_watch.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = module.ctypes.c_int

                # IN_MASK_ADD keeps the original source subscriptions and
                # adds IN_OPEN. This is NOT DEC-965's replacement case.
                same_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(sample),
                    IN_OPEN | IN_MASK_ADD | module.IN_DONT_FOLLOW,
                )
                self.assertEqual(same_wd, source_wd)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                for next_bytes in (module.AFTER, module.BEFORE):
                    with sample.open("r+b") as writer:
                        self.assertEqual(writer.write(next_bytes), len(next_bytes))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    stream = module._read_receipt_pending(fd)
                    self.assertTrue(stream)
                    pos = 0
                    records = []
                    while pos < len(stream):
                        wd, mask, cookie, length = module.EVENT.unpack_from(
                            stream, pos
                        )
                        pos += module.EVENT.size
                        name = stream[pos:pos + length].split(b"\x00", 1)[0]
                        pos += length
                        self.assertEqual(cookie, 0)
                        records.append((wd, mask, name))
                    self.assertEqual(pos, len(stream))

                    source_masks = [
                        mask for wd, mask, name in records if wd == source_wd
                    ]
                    self.assertIn(IN_OPEN, source_masks)
                    self.assertIn(module.IN_MODIFY, source_masks)
                    self.assertIn(module.IN_CLOSE_WRITE, source_masks)
                    self.assertTrue(any(
                        wd == parent_wd and mask & module.IN_MODIFY
                        and name == b"sample" for wd, mask, name in records
                    ))
                    self.assertFalse(any(
                        mask & module.IN_IGNORED for wd, mask, name in records
                    ))

                    # The native IN_OPEN record is outside the evaluator's
                    # supported masks. It must NOT be quietly discarded or
                    # reinterpreted as a complete no-write witness.
                    parsed = module._classify_stream(
                        stream, source_wd, parent_wd
                    )
                    self.assertFalse(parsed["well_formed"])
                    self.assertGreaterEqual(parsed["source_modify_events"], 1)
                    self.assertEqual(module._read_receipt_pending(fd), b"")
                    verdict = module._evaluate(
                        module.BEFORE, next_bytes, stream, source_wd,
                        True, False, directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(verdict["independent_os_proof_verified"], False)

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                # Reading the real inode now also creates genuine IN_OPEN;
                # an empty queue BEFORE read was not a no-write guarantee.
                read_stream = module._read_receipt_pending(fd)
                self.assertTrue(read_stream)
                self.assertFalse(module._classify_stream(
                    read_stream, source_wd, parent_wd
                )["well_formed"])
                self.assertEqual(module._read_receipt_pending(fd), b"")

                after = os.lstat(sample)
                parent_after = os.lstat(sample.parent)
                self.assertEqual(
                    (after.st_dev, after.st_ino, after.st_mode),
                    (first_stat.st_dev, first_stat.st_ino, first_stat.st_mode),
                )
                self.assertEqual(
                    (parent_after.st_dev, parent_after.st_ino, parent_after.st_mode),
                    (parent_stat.st_dev, parent_stat.st_ino, parent_stat.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                if fd is not None:
                    os.close(fd)
                    with self.assertRaises(OSError):
                        os.fstat(fd)
