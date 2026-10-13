from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec998", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_MASK_CREATE = 0x10000000  # Registration only, never an event record action.
RENAME_EXCHANGE = 2
AT_FDCWD = -100


@unittest.skipUnless(sys.platform == "linux", "native rename exchange is Linux-only")
class NativeAtomicSymlinkExchangeRegression(unittest.TestCase):
    def test_real_exchange_swaps_names_but_not_two_symlink_watch_inodes(self):
        fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            result = []
            offset = 0
            while offset < len(stream):
                self.assertGreaterEqual(len(stream) - offset, module.EVENT.size)
                wd, mask, cookie, count = module.EVENT.unpack_from(stream, offset)
                offset += module.EVENT.size
                self.assertLessEqual(count, len(stream) - offset)
                name = stream[offset:offset + count].split(b"\x00", 1)[0]
                offset += count
                result.append((wd, mask, cookie, name))
            self.assertEqual(offset, len(stream))
            return result

        with tempfile.TemporaryDirectory(
            prefix="dec998-public-atomic-link-exchange-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            first_alias = sample.parent / "public-first-alias"
            second_alias = sample.parent / "public-second-alias"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first_stat = os.lstat(sample)
            first_parent_stat = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                first_alias.symlink_to("sample")
                second_alias.symlink_to("sample")
                created = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_CREATE, 0, b"public-first-alias"),
                    created,
                )
                self.assertIn(
                    (parent_wd, module.IN_CREATE, 0, b"public-second-alias"),
                    created,
                )
                original_first_inode = os.lstat(first_alias).st_ino
                original_second_inode = os.lstat(second_alias).st_ino
                self.assertNotEqual(original_first_inode, original_second_inode)
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

                mask = (IN_MASK_CREATE | module.IN_DONT_FOLLOW
                        | module.IN_MOVE_SELF | module.IN_DELETE_SELF)
                first_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(first_alias), mask
                )
                second_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(second_alias), mask
                )
                self.assertGreater(first_wd, 0)
                self.assertGreater(second_wd, 0)
                self.assertEqual(
                    len({source_wd, parent_wd, first_wd, second_wd}), 4
                )
                self.assertEqual(module._read_receipt_pending(fd), b"")

                module.ctypes.set_errno(0)
                exchanged = lib.renameat2(
                    AT_FDCWD, module._checked_watch_path_bytes(first_alias),
                    AT_FDCWD, module._checked_watch_path_bytes(second_alias),
                    RENAME_EXCHANGE,
                )
                self.assertEqual(
                    exchanged, 0,
                    f"renameat2 exchange failed: {module.ctypes.get_errno()}",
                )
                self.assertEqual(os.lstat(first_alias).st_ino,
                                 original_second_inode)
                self.assertEqual(os.lstat(second_alias).st_ino,
                                 original_first_inode)

                native = module._read_receipt_pending(fd)
                self.assertTrue(native)
                exchange_events = records(native)
                parent_moves = [
                    (mask_value, cookie, name)
                    for wd, mask_value, cookie, name in exchange_events
                    if wd == parent_wd
                ]
                self.assertEqual(len(parent_moves), 4)
                from_moves = [
                    (cookie, name) for mask_value, cookie, name in parent_moves
                    if mask_value == module.IN_MOVED_FROM
                ]
                to_moves = [
                    (cookie, name) for mask_value, cookie, name in parent_moves
                    if mask_value == module.IN_MOVED_TO
                ]
                self.assertEqual(len(from_moves), 2)
                self.assertEqual(len(to_moves), 2)
                self.assertEqual(
                    sorted(name for cookie, name in from_moves),
                    [b"public-first-alias", b"public-second-alias"],
                )
                self.assertEqual(
                    sorted(name for cookie, name in to_moves),
                    [b"public-first-alias", b"public-second-alias"],
                )
                self.assertEqual(len({cookie for cookie, name in from_moves}), 2)
                self.assertTrue(all(cookie > 0 for cookie, name in from_moves))
                self.assertEqual(
                    sorted(cookie for cookie, name in from_moves),
                    sorted(cookie for cookie, name in to_moves),
                )
                for cookie, old_name in from_moves:
                    paired_to = [
                        new_name for match, new_name in to_moves
                        if match == cookie
                    ]
                    self.assertEqual(len(paired_to), 1)
                    self.assertNotEqual(paired_to[0], old_name)
                self.assertIn(
                    (first_wd, module.IN_MOVE_SELF, 0, b""),
                    exchange_events,
                )
                self.assertIn(
                    (second_wd, module.IN_MOVE_SELF, 0, b""),
                    exchange_events,
                )
                self.assertFalse(any(
                    mask_value & (module.IN_IGNORED | module.IN_DELETE_SELF)
                    for wd, mask_value, cookie, name in exchange_events
                ))
                self.assertFalse(module._classify_stream(
                    native, source_wd, parent_wd
                )["well_formed"])
                swapped_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, native, source_wd,
                    True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(swapped_verdict["status"], "BLOCKED")
                self.assertIs(swapped_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    swapped_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # After exchange, deleting the FIRST pathname must
                # invalidate the SECOND inode's original native WD.
                os.unlink(first_alias)
                first_deleted = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_DELETE, 0, b"public-first-alias"),
                    first_deleted,
                )
                self.assertIn(
                    (second_wd, module.IN_DELETE_SELF, 0, b""),
                    first_deleted,
                )
                self.assertIn(
                    (second_wd, module.IN_IGNORED, 0, b""),
                    first_deleted,
                )
                self.assertFalse(any(
                    wd == first_wd for wd, mask_value, cookie, name
                    in first_deleted
                ))
                os.unlink(second_alias)
                second_deleted = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_DELETE, 0, b"public-second-alias"),
                    second_deleted,
                )
                self.assertIn(
                    (first_wd, module.IN_DELETE_SELF, 0, b""),
                    second_deleted,
                )
                self.assertIn(
                    (first_wd, module.IN_IGNORED, 0, b""),
                    second_deleted,
                )
                self.assertEqual(module._read_receipt_pending(fd), b"")
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))

                # The original watched regular file never left its inode;
                # real distinct-byte writes remain observable and BLOCKED.
                for content in (module.AFTER, module.BEFORE):
                    with sample.open("r+b") as writer:
                        self.assertEqual(writer.write(content), len(content))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    source_stream = module._read_receipt_pending(fd)
                    parsed = module._classify_stream(
                        source_stream, source_wd, parent_wd
                    )
                    self.assertTrue(parsed["well_formed"])
                    self.assertFalse(parsed["invalidated"])
                    self.assertGreaterEqual(parsed["source_modify_events"], 1)
                    self.assertGreaterEqual(
                        parsed["source_content_write_events"], 1
                    )
                    verdict = module._evaluate(
                        module.BEFORE, content, source_stream,
                        source_wd, True, False, directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(verdict["independent_os_proof_verified"], False)
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = os.lstat(sample)
                parent_final = os.lstat(sample.parent)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (first_stat.st_dev, first_stat.st_ino, first_stat.st_mode),
                )
                self.assertEqual(
                    (parent_final.st_dev, parent_final.st_ino,
                     parent_final.st_mode),
                    (first_parent_stat.st_dev, first_parent_stat.st_ino,
                     first_parent_stat.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                if fd is not None:
                    os.close(fd)
                    with self.assertRaises(OSError):
                        os.fstat(fd)
