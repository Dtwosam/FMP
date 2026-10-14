from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1126", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

PREFIX = b"DEC677_PUBLIC_"
AFTER_FIRST = b"DEC677_PUBLIC_CHORCE\n"
AFTER_SECOND = b"DEC677_PUBLIC_CHOICE\n"


@unittest.skipUnless(sys.platform == "linux", "requires real Linux inotify")
class NativeTwoPwriteOneCloseStagesRegression(unittest.TestCase):
    def test_two_separately_drained_pwrites_emit_modifies_before_one_close(self):
        watcher_fd = None
        writer_fd = None

        def records(receipt):
            self.assertIs(type(receipt), bytes)
            observed = []
            cursor = 0
            while cursor < len(receipt):
                self.assertGreaterEqual(len(receipt) - cursor,
                                        module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(
                    receipt, cursor,
                )
                cursor += module.EVENT.size
                self.assertLessEqual(length, len(receipt) - cursor)
                name = receipt[cursor:cursor + length].split(b"\x00", 1)[0]
                cursor += length
                self.assertEqual(cookie, 0)
                observed.append((wd, mask, name))
            self.assertEqual(cursor, len(receipt))
            return observed

        def assert_modify_pair(receipt, source_wd, parent_wd):
            observed = records(receipt)
            source = (source_wd, module.IN_MODIFY, b"")
            parent = (parent_wd, module.IN_MODIFY, b"sample")
            self.assertTrue(all(event in (source, parent)
                                for event in observed))
            self.assertGreaterEqual(observed.count(source), 1)
            self.assertGreaterEqual(observed.count(parent), 1)

        with tempfile.TemporaryDirectory(
            prefix="dec1126-public-two-pwrite-one-close-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(len(module.BEFORE), len(AFTER_FIRST))
            self.assertEqual(len(module.BEFORE), len(AFTER_SECOND))
            self.assertNotEqual(AFTER_FIRST, module.BEFORE)
            self.assertNotEqual(AFTER_SECOND, AFTER_FIRST)
            self.assertEqual(sample.write_bytes(module.BEFORE),
                             len(module.BEFORE))
            before = (os.lstat(sample), os.lstat(parent))
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("sample",))
            try:
                watcher_fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertEqual(module._read_receipt_pending(watcher_fd), b"")
                writer_fd = os.open(sample, os.O_WRONLY | os.O_CLOEXEC)
                self.assertEqual(module._read_receipt_pending(watcher_fd), b"")

                # First non-truncating pwrite changes only the first three
                # letters of the SOURCE suffix, without changing file size.
                self.assertEqual(os.pwrite(writer_fd, b"CHO", len(PREFIX)), 3)
                os.fsync(writer_fd)
                first_receipt = module._read_receipt_pending(watcher_fd)
                assert_modify_pair(first_receipt, source_wd, parent_wd)
                self.assertEqual(sample.read_bytes(), AFTER_FIRST)
                self.assertEqual(module._read_receipt_pending(watcher_fd), b"")

                # Second pwrite on the SAME OPEN descriptor changes another
                # three bytes. Draining the first stage prevents inotify
                # coalescing from collapsing the distinct mutation stages.
                self.assertEqual(
                    os.pwrite(writer_fd, b"ICE", len(PREFIX) + 3), 3,
                )
                os.fsync(writer_fd)
                second_receipt = module._read_receipt_pending(watcher_fd)
                assert_modify_pair(second_receipt, source_wd, parent_wd)
                self.assertEqual(sample.read_bytes(), AFTER_SECOND)
                self.assertEqual(module._read_receipt_pending(watcher_fd), b"")

                os.close(writer_fd)
                writer_fd = None
                close_receipt = module._read_receipt_pending(watcher_fd)
                self.assertCountEqual(records(close_receipt), [
                    (source_wd, module.IN_CLOSE_WRITE, b""),
                    (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
                ])
                self.assertEqual(module._read_receipt_pending(watcher_fd), b"")

                # Both pwrite syscalls generated positive source+parent
                # MODIFY receipts, but only ONE writable descriptor closed.
                complete = first_receipt + second_receipt + close_receipt
                native = records(complete)
                self.assertGreaterEqual(
                    native.count((source_wd, module.IN_MODIFY, b"")), 2,
                )
                self.assertGreaterEqual(
                    native.count((parent_wd, module.IN_MODIFY, b"sample")), 2,
                )
                self.assertEqual(
                    native.count((source_wd, module.IN_CLOSE_WRITE, b"")), 1,
                )
                self.assertEqual(
                    native.count((parent_wd, module.IN_CLOSE_WRITE, b"sample")),
                    1,
                )
                parsed = module._classify_stream(
                    complete, source_wd, parent_wd
                )
                self.assertTrue(parsed["well_formed"])
                self.assertFalse(parsed["invalidated"])
                self.assertGreaterEqual(parsed["source_content_write_events"],
                                        2)
                decision = module._evaluate(
                    module.BEFORE, AFTER_SECOND, complete, source_wd,
                    True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(decision["status"], "BLOCKED")
                self.assertIs(decision["can_authorize_dispatch"], False)
                self.assertIs(decision["independent_os_proof_verified"], False)

                # Second descriptor genuinely restores the original PUBLIC
                # bytes without replacing the source inode.
                writer_fd = os.open(sample, os.O_WRONLY | os.O_CLOEXEC)
                self.assertEqual(module._read_receipt_pending(watcher_fd), b"")
                self.assertEqual(
                    os.pwrite(writer_fd, module.BEFORE, 0),
                    len(module.BEFORE),
                )
                os.fsync(writer_fd)
                restore_receipt = module._read_receipt_pending(watcher_fd)
                assert_modify_pair(restore_receipt, source_wd, parent_wd)
                os.close(writer_fd)
                writer_fd = None
                self.assertCountEqual(
                    records(module._read_receipt_pending(watcher_fd)), [
                        (source_wd, module.IN_CLOSE_WRITE, b""),
                        (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
                    ],
                )
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                latest = (os.lstat(sample), os.lstat(parent))
                for old, new in zip(before, latest):
                    self.assertEqual(
                        (old.st_dev, old.st_ino, old.st_mode, old.st_nlink),
                        (new.st_dev, new.st_ino, new.st_mode, new.st_nlink),
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
