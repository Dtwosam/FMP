from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1124", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "requires actual native Linux inotify")
class NativeTruncateWriteCloseStageReceiptRegression(unittest.TestCase):
    def test_open_truncate_write_and_close_are_distinct_native_mutation_stages(self):
        watcher_fd = None
        writer_fd = None

        def records(receipt):
            self.assertIs(type(receipt), bytes)
            seen = []
            offset = 0
            while offset < len(receipt):
                self.assertGreaterEqual(len(receipt) - offset,
                                        module.EVENT.size)
                wd, mask, cookie, count = module.EVENT.unpack_from(
                    receipt, offset
                )
                offset += module.EVENT.size
                self.assertLessEqual(count, len(receipt) - offset)
                name = receipt[offset:offset + count].split(b"\x00", 1)[0]
                offset += count
                self.assertEqual(cookie, 0)
                seen.append((wd, mask, name))
            self.assertEqual(offset, len(receipt))
            return seen

        with tempfile.TemporaryDirectory(
            prefix="dec1124-public-staged-trunc-write-close-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            self.assertGreater(len(module.BEFORE), 0)
            original_source = os.lstat(sample)
            original_parent = os.lstat(parent)
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("sample",))
            try:
                watcher_fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertEqual(module._read_receipt_pending(watcher_fd), b"")

                # Stage 1: O_TRUNC is a real content modification even BEFORE
                # any explicit write() occurs. Drain it separately so the
                # kernel need not preserve multiple identical queued events.
                writer_fd = os.open(
                    sample, os.O_WRONLY | os.O_TRUNC | os.O_CLOEXEC,
                )
                self.assertEqual(os.fstat(writer_fd).st_size, 0)
                truncate = module._read_receipt_pending(watcher_fd)
                self.assertCountEqual(records(truncate), [
                    (source_wd, module.IN_MODIFY, b""),
                    (parent_wd, module.IN_MODIFY, b"sample"),
                ])

                # Stage 2: genuine write() modifies the SAME already-open
                # inode and yields another pair of native MODIFY receipts.
                self.assertEqual(os.write(writer_fd, module.AFTER),
                                 len(module.AFTER))
                os.fsync(writer_fd)
                write = module._read_receipt_pending(watcher_fd)
                self.assertCountEqual(records(write), [
                    (source_wd, module.IN_MODIFY, b""),
                    (parent_wd, module.IN_MODIFY, b"sample"),
                ])

                # Stage 3: CLOSE_WRITE is a single close of the genuinely
                # writable FD, not a promise there was only one MODIFY.
                os.close(writer_fd)
                writer_fd = None
                closed = module._read_receipt_pending(watcher_fd)
                self.assertCountEqual(records(closed), [
                    (source_wd, module.IN_CLOSE_WRITE, b""),
                    (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
                ])
                self.assertEqual(module._read_receipt_pending(watcher_fd),
                                 b"")

                self.assertEqual(sample.read_bytes(), module.AFTER)
                complete = truncate + write + closed
                native = records(complete)
                self.assertEqual(native.count(
                    (source_wd, module.IN_MODIFY, b"")), 2)
                self.assertEqual(native.count(
                    (parent_wd, module.IN_MODIFY, b"sample")), 2)
                self.assertEqual(native.count(
                    (source_wd, module.IN_CLOSE_WRITE, b"")), 1)
                self.assertEqual(native.count(
                    (parent_wd, module.IN_CLOSE_WRITE, b"sample")), 1)
                parsed = module._classify_stream(
                    complete, source_wd, parent_wd
                )
                self.assertTrue(parsed["well_formed"])
                self.assertFalse(parsed["invalidated"])
                self.assertGreaterEqual(parsed["source_content_write_events"],
                                        2)
                result = module._evaluate(
                    module.BEFORE, module.AFTER, complete, source_wd,
                    True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(result["status"], "BLOCKED")
                self.assertIs(result["can_authorize_dispatch"], False)
                self.assertIs(result["independent_os_proof_verified"], False)

                # Restore original PUBLIC bytes using a second genuine write.
                # This separate operation may itself generate multiple
                # MODIFY events; require positive provenance, not one count.
                restore_fd = os.open(sample, os.O_WRONLY | os.O_TRUNC)
                try:
                    self.assertEqual(os.write(restore_fd, module.BEFORE),
                                     len(module.BEFORE))
                    os.fsync(restore_fd)
                finally:
                    os.close(restore_fd)
                restored = records(
                    module._read_receipt_pending(watcher_fd)
                )
                for event in (
                    (source_wd, module.IN_MODIFY, b""),
                    (parent_wd, module.IN_MODIFY, b"sample"),
                    (source_wd, module.IN_CLOSE_WRITE, b""),
                    (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
                ):
                    self.assertIn(event, restored)
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                new_source = os.lstat(sample)
                new_parent = os.lstat(parent)
                for earlier, later in (
                    (original_source, new_source),
                    (original_parent, new_parent),
                ):
                    self.assertEqual(
                        (earlier.st_dev, earlier.st_ino, earlier.st_mode),
                        (later.st_dev, later.st_ino, later.st_mode),
                    )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
            finally:
                if writer_fd is not None:
                    os.close(writer_fd)
                if watcher_fd is not None:
                    os.close(watcher_fd)
                    with self.assertRaises(OSError):
                        os.fstat(watcher_fd)
