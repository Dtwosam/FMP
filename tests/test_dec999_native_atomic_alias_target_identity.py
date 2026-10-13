from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec999", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

RENAME_EXCHANGE = 2
AT_FDCWD = -100


@unittest.skipUnless(sys.platform == "linux", "native rename exchange requires Linux")
class NativeAtomicAliasTargetIdentityRegression(unittest.TestCase):
    def test_exchange_pathnames_redirects_writes_to_distinct_existing_inodes(self):
        fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            pos = 0
            result = []
            while pos < len(stream):
                self.assertGreaterEqual(len(stream) - pos, module.EVENT.size)
                wd, mask, cookie, n = module.EVENT.unpack_from(stream, pos)
                pos += module.EVENT.size
                self.assertLessEqual(n, len(stream) - pos)
                name = stream[pos:pos + n].split(b"\x00", 1)[0]
                pos += n
                result.append((wd, mask, cookie, name))
            self.assertEqual(pos, len(stream))
            return result

        with tempfile.TemporaryDirectory(
            prefix="dec999-public-exchanged-targets-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            other = sample.parent / "public-other"
            first_alias = sample.parent / "public-first-alias"
            second_alias = sample.parent / "public-second-alias"
            other_original = b"PUBLIC-OTHER-ORIGINAL"
            other_changed = b"PUBLIC-OTHER-MODIFIED"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            self.assertEqual(other.write_bytes(other_original),
                             len(other_original))
            original_sample = os.lstat(sample)
            original_other = os.lstat(other)
            original_parent = os.lstat(sample.parent)
            self.assertNotEqual(original_sample.st_ino, original_other.st_ino)
            try:
                fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                first_alias.symlink_to("sample")
                second_alias.symlink_to("public-other")
                created = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_CREATE, 0, b"public-first-alias"),
                    created,
                )
                self.assertIn(
                    (parent_wd, module.IN_CREATE, 0, b"public-second-alias"),
                    created,
                )
                self.assertEqual(module._read_receipt_pending(fd), b"")

                lib = module.ctypes.CDLL(None, use_errno=True)
                lib.inotify_add_watch.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = module.ctypes.c_int
                if not hasattr(lib, "renameat2"):
                    self.skipTest("libc renameat2 unavailable")
                lib.renameat2.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint,
                ]
                lib.renameat2.restype = module.ctypes.c_int

                other_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(other),
                    module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_DONT_FOLLOW,
                )
                self.assertGreater(other_wd, 0)
                self.assertNotIn(other_wd, (source_wd, parent_wd))
                self.assertEqual(module._read_receipt_pending(fd), b"")

                before_first_link = os.lstat(first_alias)
                before_second_link = os.lstat(second_alias)
                module.ctypes.set_errno(0)
                exchange = lib.renameat2(
                    AT_FDCWD, module._checked_watch_path_bytes(first_alias),
                    AT_FDCWD, module._checked_watch_path_bytes(second_alias),
                    RENAME_EXCHANGE,
                )
                self.assertEqual(
                    exchange, 0,
                    f"native exchange failed: {module.ctypes.get_errno()}",
                )
                self.assertEqual(os.lstat(first_alias).st_ino,
                                 before_second_link.st_ino)
                self.assertEqual(os.lstat(second_alias).st_ino,
                                 before_first_link.st_ino)
                self.assertEqual(os.stat(first_alias).st_ino,
                                 original_other.st_ino)
                self.assertEqual(os.stat(second_alias).st_ino,
                                 original_sample.st_ino)

                move_stream = records(module._read_receipt_pending(fd))
                self.assertEqual(len(move_stream), 4)
                from_moves = [
                    (cookie, name) for wd, mask, cookie, name in move_stream
                    if wd == parent_wd and mask == module.IN_MOVED_FROM
                ]
                to_moves = [
                    (cookie, name) for wd, mask, cookie, name in move_stream
                    if wd == parent_wd and mask == module.IN_MOVED_TO
                ]
                self.assertEqual(len(from_moves), 2)
                self.assertEqual(len(to_moves), 2)
                self.assertEqual(
                    sorted(cookie for cookie, name in from_moves),
                    sorted(cookie for cookie, name in to_moves),
                )
                self.assertEqual(len({cookie for cookie, name in from_moves}), 2)
                self.assertTrue(all(cookie > 0 for cookie, name in from_moves))
                for cookie, name in from_moves:
                    paired = [dest for c, dest in to_moves if c == cookie]
                    self.assertEqual(len(paired), 1)
                    self.assertNotEqual(name, paired[0])
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # The FIRST alias now follows the OTHER regular-file inode.
                # The original source WD must NOT acquire that write.
                with first_alias.open("r+b") as writer:
                    self.assertEqual(writer.write(other_changed),
                                     len(other_changed))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                other_stream = module._read_receipt_pending(fd)
                other_records = records(other_stream)
                self.assertTrue(any(
                    wd == other_wd and mask == module.IN_MODIFY
                    for wd, mask, cookie, name in other_records
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"public-other"
                    for wd, mask, cookie, name in other_records
                ))
                self.assertFalse(any(
                    wd == source_wd or
                    (wd == parent_wd and mask == module.IN_MODIFY
                     and name == b"public-first-alias")
                    for wd, mask, cookie, name in other_records
                ))
                self.assertFalse(module._classify_stream(
                    other_stream, source_wd, parent_wd
                )["well_formed"])
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # The SECOND alias now follows the ORIGINAL watched sample.
                with second_alias.open("r+b") as writer:
                    self.assertEqual(writer.write(module.AFTER), len(module.AFTER))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                sample_stream = module._read_receipt_pending(fd)
                sample_records = records(sample_stream)
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, cookie, name in sample_records
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, cookie, name in sample_records
                ))
                self.assertFalse(any(
                    wd == other_wd for wd, mask, cookie, name in sample_records
                ))
                self.assertTrue(module._classify_stream(
                    sample_stream, source_wd, parent_wd
                )["well_formed"])
                verdict = module._evaluate(
                    module.BEFORE, module.AFTER, sample_stream, source_wd,
                    True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(verdict["status"], "BLOCKED")
                self.assertIs(verdict["can_authorize_dispatch"], False)
                self.assertIs(verdict["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # Restore through the exchanged aliases, proving the same
                # two registered regular-file inodes remain distinct.
                for alias, expected_wd, original_bytes in (
                    (first_alias, other_wd, other_original),
                    (second_alias, source_wd, module.BEFORE),
                ):
                    with alias.open("r+b") as writer:
                        self.assertEqual(writer.write(original_bytes),
                                         len(original_bytes))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    restored = records(module._read_receipt_pending(fd))
                    self.assertTrue(any(
                        wd == expected_wd and mask == module.IN_MODIFY
                        for wd, mask, cookie, name in restored
                    ))
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(other.read_bytes(), other_original)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                os.unlink(first_alias)
                os.unlink(second_alias)
                os.unlink(other)
                removals = records(module._read_receipt_pending(fd))
                for entry in (
                    b"public-first-alias", b"public-second-alias", b"public-other"
                ):
                    self.assertIn(
                        (parent_wd, module.IN_DELETE, 0, entry), removals
                    )
                self.assertEqual(module._read_receipt_pending(fd), b"")
                final = os.lstat(sample)
                parent_final = os.lstat(sample.parent)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (original_sample.st_dev, original_sample.st_ino,
                     original_sample.st_mode),
                )
                self.assertEqual(
                    (parent_final.st_dev, parent_final.st_ino,
                     parent_final.st_mode),
                    (original_parent.st_dev, original_parent.st_ino,
                     original_parent.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                if fd is not None:
                    os.close(fd)
                    with self.assertRaises(OSError):
                        os.fstat(fd)
