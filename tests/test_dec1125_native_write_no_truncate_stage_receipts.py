from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1125", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Exactly equal length to the module's public initial file. This isolates
# a real changed-byte overwrite from truncation, size growth or rename.
CHANGED_SAME_SIZE = b"DEC677_PUBLIC_CHOICE\n"


@unittest.skipUnless(sys.platform == "linux", "requires real Linux inotify")
class NativeNoTruncateWriteStageReceiptRegression(unittest.TestCase):
    def test_write_without_truncate_only_modifies_when_actual_write_occurs(self):
        watcher_fd = None
        writer_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            found = []
            pos = 0
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - pos)
                name = data[pos:pos + nbytes].split(b"\x00", 1)[0]
                pos += nbytes
                self.assertEqual(cookie, 0)
                found.append((wd, mask, name))
            self.assertEqual(pos, len(data))
            return found

        def assert_write_only_events(data, source_wd, parent_wd,
                                     expected_action):
            native = records(data)
            source = (source_wd, expected_action, b"")
            parent = (parent_wd, expected_action, b"sample")
            self.assertTrue(native)
            self.assertTrue(all(event in (source, parent) for event in native))
            self.assertGreaterEqual(native.count(source), 1)
            self.assertGreaterEqual(native.count(parent), 1)

        with tempfile.TemporaryDirectory(
            prefix="dec1125-public-write-no-truncate-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(len(CHANGED_SAME_SIZE), len(module.BEFORE))
            self.assertNotEqual(CHANGED_SAME_SIZE, module.BEFORE)
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = (os.lstat(sample), os.lstat(parent))
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("sample",))
            try:
                watcher_fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertEqual(module._read_receipt_pending(watcher_fd), b"")

                # O_WRONLY without O_TRUNC opens an unchanged inode. Unlike
                # DEC-1124, it does not itself truncate or emit MODIFY.
                writer_fd = os.open(sample, os.O_WRONLY | os.O_CLOEXEC)
                self.assertEqual(os.fstat(writer_fd).st_size, len(module.BEFORE))
                self.assertEqual(module._read_receipt_pending(watcher_fd), b"")
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(module._read_receipt_pending(watcher_fd), b"")

                # Exactly one actual write of equal-length but changed bytes.
                # Linux emits genuine source and parent MODIFY events.
                self.assertEqual(os.write(writer_fd, CHANGED_SAME_SIZE),
                                 len(CHANGED_SAME_SIZE))
                os.fsync(writer_fd)
                changed_receipt = module._read_receipt_pending(watcher_fd)
                assert_write_only_events(
                    changed_receipt, source_wd, parent_wd, module.IN_MODIFY,
                )
                self.assertEqual(os.fstat(writer_fd).st_size,
                                 len(module.BEFORE))

                # One writable close emits CLOSE_WRITE on both watches.
                os.close(writer_fd)
                writer_fd = None
                close_receipt = module._read_receipt_pending(watcher_fd)
                self.assertCountEqual(records(close_receipt), [
                    (source_wd, module.IN_CLOSE_WRITE, b""),
                    (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
                ])
                self.assertEqual(module._read_receipt_pending(watcher_fd), b"")
                self.assertEqual(sample.read_bytes(), CHANGED_SAME_SIZE)
                stream = changed_receipt + close_receipt
                classification = module._classify_stream(
                    stream, source_wd, parent_wd
                )
                self.assertTrue(classification["well_formed"])
                self.assertFalse(classification["invalidated"])
                self.assertGreaterEqual(
                    classification["source_content_write_events"], 1
                )
                outcome = module._evaluate(
                    module.BEFORE, CHANGED_SAME_SIZE, stream, source_wd,
                    True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(outcome["status"], "BLOCKED")
                self.assertIs(outcome["can_authorize_dispatch"], False)
                self.assertIs(outcome["independent_os_proof_verified"], False)

                # Restore same-size original bytes through a second real
                # O_WRONLY write, again without an intervening truncation.
                writer_fd = os.open(sample, os.O_WRONLY | os.O_CLOEXEC)
                self.assertEqual(module._read_receipt_pending(watcher_fd), b"")
                self.assertEqual(os.write(writer_fd, module.BEFORE),
                                 len(module.BEFORE))
                os.fsync(writer_fd)
                restore = module._read_receipt_pending(watcher_fd)
                assert_write_only_events(
                    restore, source_wd, parent_wd, module.IN_MODIFY,
                )
                os.close(writer_fd)
                writer_fd = None
                self.assertCountEqual(
                    records(module._read_receipt_pending(watcher_fd)), [
                        (source_wd, module.IN_CLOSE_WRITE, b""),
                        (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
                    ],
                )
                self.assertEqual(module._read_receipt_pending(watcher_fd), b"")
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                latest = (os.lstat(sample), os.lstat(parent))
                for before, after in zip(initial, latest):
                    self.assertEqual(
                        (before.st_dev, before.st_ino, before.st_mode,
                         before.st_nlink),
                        (after.st_dev, after.st_ino, after.st_mode,
                         after.st_nlink),
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
