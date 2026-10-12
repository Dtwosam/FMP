from __future__ import annotations

import errno
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec976", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(sys.platform == "linux", "native IN_ONLYDIR is Linux-only")
class NativeOnlyDirectoryGuardRegression(unittest.TestCase):
    def test_onlydir_rejects_regular_file_and_nofollow_directory_link(self):
        fd = None
        with tempfile.TemporaryDirectory(
            prefix="dec976-public-native-onlydir-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            directory_link = Path(tmp) / "public-parent-link"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            before = os.lstat(sample)
            before_parent = os.lstat(sample.parent)
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

                # A real file cannot satisfy IN_ONLYDIR. A symlink to a
                # directory cannot satisfy it when IN_DONT_FOLLOW is set.
                directory_link.symlink_to(sample.parent, target_is_directory=True)
                created = module._read_receipt_pending(fd)
                self.assertTrue(created)
                parsed_created = module._classify_stream(
                    created, source_wd, parent_wd
                )
                self.assertTrue(parsed_created["well_formed"])
                self.assertGreaterEqual(parsed_created["directory_changes"], 1)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                self.assertTrue(os.path.islink(directory_link))
                self.assertTrue(os.path.isdir(directory_link))
                self.assertNotEqual(os.lstat(directory_link).st_ino,
                                    os.lstat(sample.parent).st_ino)

                for candidate in (sample, directory_link):
                    module.ctypes.set_errno(0)
                    outcome = lib.inotify_add_watch(
                        fd, module._checked_watch_path_bytes(candidate),
                        module.IN_CREATE | module.IN_ONLYDIR |
                        module.IN_DONT_FOLLOW,
                    )
                    error = module.ctypes.get_errno()
                    self.assertEqual(outcome, -1)
                    self.assertEqual(error, errno.ENOTDIR)
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Remove the disposable alias and drain its real parent
                # event before checking the surviving original watches.
                os.unlink(directory_link)
                deleted = module._read_receipt_pending(fd)
                self.assertTrue(deleted)
                parsed_deleted = module._classify_stream(
                    deleted, source_wd, parent_wd
                )
                self.assertTrue(parsed_deleted["well_formed"])
                self.assertGreaterEqual(parsed_deleted["directory_changes"], 1)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))

                # Both failed registrations must leave the original source
                # and parent subscriptions observing real content writes.
                for content in (module.AFTER, module.BEFORE):
                    with sample.open("r+b") as writer:
                        self.assertEqual(writer.write(content), len(content))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    stream = module._read_receipt_pending(fd)
                    self.assertTrue(stream)
                    parsed = module._classify_stream(
                        stream, source_wd, parent_wd
                    )
                    self.assertTrue(parsed["well_formed"])
                    self.assertFalse(parsed["invalidated"])
                    self.assertGreaterEqual(parsed["source_modify_events"], 1)
                    self.assertGreaterEqual(
                        parsed["source_content_write_events"], 1
                    )
                    pos = 0
                    parent_writes = 0
                    while pos < len(stream):
                        wd, mask, cookie, length = module.EVENT.unpack_from(
                            stream, pos
                        )
                        pos += module.EVENT.size
                        name = stream[pos:pos + length].split(b"\x00", 1)[0]
                        pos += length
                        self.assertEqual(cookie, 0)
                        self.assertIn(wd, (source_wd, parent_wd))
                        if wd == parent_wd and mask & (
                            module.IN_MODIFY | module.IN_CLOSE_WRITE
                        ):
                            self.assertEqual(name, b"sample")
                            parent_writes += 1
                    self.assertEqual(pos, len(stream))
                    self.assertGreaterEqual(parent_writes, 1)
                    self.assertEqual(module._read_receipt_pending(fd), b"")
                    verdict = module._evaluate(
                        module.BEFORE, content, stream, source_wd,
                        True, False, directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(verdict["independent_os_proof_verified"], False)

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                after = os.lstat(sample)
                after_parent = os.lstat(sample.parent)
                self.assertEqual(
                    (after.st_dev, after.st_ino, after.st_mode),
                    (before.st_dev, before.st_ino, before.st_mode),
                )
                self.assertEqual(
                    (after_parent.st_dev, after_parent.st_ino,
                     after_parent.st_mode),
                    (before_parent.st_dev, before_parent.st_ino,
                     before_parent.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                if fd is not None:
                    os.close(fd)
                    with self.assertRaises(OSError):
                        os.fstat(fd)
