from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1012", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

AT_FDCWD = -100
RENAME_EXCHANGE = 2


@unittest.skipUnless(sys.platform == "linux", "native rename exchange is Linux-only")
class NativeEqualByteFileExchangeRegression(unittest.TestCase):
    def test_equal_byte_file_exchange_changes_path_inode_and_blocks_authorization(self):
        fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            parsed = []
            offset = 0
            while offset < len(data):
                self.assertGreaterEqual(len(data) - offset, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, offset)
                offset += module.EVENT.size
                self.assertLessEqual(nbytes, len(data) - offset)
                name = data[offset:offset + nbytes].split(b"\x00", 1)[0]
                offset += nbytes
                parsed.append((wd, mask, cookie, name))
            self.assertEqual(offset, len(data))
            return parsed

        with tempfile.TemporaryDirectory(
            prefix="dec1012-public-equal-bytes-exchange-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            other = sample.parent / "public-same-bytes"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first = os.lstat(sample)
            first_parent = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                # A SECOND distinct regular-file inode deliberately has
                # EXACTLY the same public byte contents as watched source.
                self.assertEqual(other.write_bytes(module.BEFORE),
                                 len(module.BEFORE))
                other_before = os.lstat(other)
                self.assertNotEqual(
                    (first.st_dev, first.st_ino),
                    (other_before.st_dev, other_before.st_ino),
                )
                self.assertIn(
                    (parent_wd, module.IN_CREATE, 0, b"public-same-bytes"),
                    records(module._read_receipt_pending(fd)),
                )
                self.assertEqual(module._read_receipt_pending(fd), b"")
                self.assertEqual(other.read_bytes(), sample.read_bytes())
                self.assertEqual(module._read_receipt_pending(fd), b"")

                lib = module.ctypes.CDLL(None, use_errno=True)
                if not hasattr(lib, "renameat2"):
                    self.skipTest("libc renameat2 unavailable")
                lib.inotify_add_watch.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = module.ctypes.c_int
                lib.renameat2.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint,
                ]
                lib.renameat2.restype = module.ctypes.c_int
                other_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(other),
                    module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_MOVE_SELF | module.IN_DELETE_SELF |
                    module.IN_DONT_FOLLOW,
                )
                self.assertGreater(other_wd, 0)
                self.assertNotIn(other_wd, (source_wd, parent_wd))
                self.assertEqual(module._read_receipt_pending(fd), b"")

                source_name = module._checked_watch_path_bytes(sample)
                other_name = module._checked_watch_path_bytes(other)

                for turn in range(2):
                    module.ctypes.set_errno(0)
                    rc = lib.renameat2(
                        AT_FDCWD, source_name, AT_FDCWD, other_name,
                        RENAME_EXCHANGE,
                    )
                    self.assertEqual(
                        rc, 0,
                        f"native exchange errno {module.ctypes.get_errno()}",
                    )
                    expected_source_path_inode = (
                        other_before.st_ino if turn == 0 else first.st_ino
                    )
                    expected_other_path_inode = (
                        first.st_ino if turn == 0 else other_before.st_ino
                    )
                    self.assertEqual(os.lstat(sample).st_ino,
                                     expected_source_path_inode)
                    self.assertEqual(os.lstat(other).st_ino,
                                     expected_other_path_inode)

                    # Both snapshots remain IDENTICAL, even though the
                    # watched pathname refers to a different inode on the
                    # first exchange. Never trust byte equality alone.
                    self.assertEqual(sample.read_bytes(), module.BEFORE)
                    self.assertEqual(other.read_bytes(), module.BEFORE)
                    native = module._read_receipt_pending(fd)
                    events = records(native)
                    self.assertEqual(len(events), 6)
                    from_moves = [
                        (cookie, name) for wd, mask, cookie, name in events
                        if wd == parent_wd and mask == module.IN_MOVED_FROM
                    ]
                    to_moves = [
                        (cookie, name) for wd, mask, cookie, name in events
                        if wd == parent_wd and mask == module.IN_MOVED_TO
                    ]
                    self.assertEqual(len(from_moves), 2)
                    self.assertEqual(len(to_moves), 2)
                    self.assertEqual(
                        sorted(cookie for cookie, _ in from_moves),
                        sorted(cookie for cookie, _ in to_moves),
                    )
                    self.assertEqual(
                        len({cookie for cookie, _ in from_moves}), 2
                    )
                    self.assertTrue(all(cookie > 0 for cookie, _ in from_moves))
                    for cookie, basename in from_moves:
                        matching = [
                            to_name for c, to_name in to_moves if c == cookie
                        ]
                        self.assertEqual(len(matching), 1)
                        self.assertNotEqual(matching[0], basename)
                    self.assertIn(
                        (source_wd, module.IN_MOVE_SELF, 0, b""), events
                    )
                    self.assertIn(
                        (other_wd, module.IN_MOVE_SELF, 0, b""), events
                    )
                    self.assertFalse(any(
                        mask & (module.IN_MODIFY | module.IN_CLOSE_WRITE)
                        for wd, mask, cookie, name in events
                    ))
                    parsed = module._classify_stream(
                        native, source_wd, parent_wd
                    )
                    self.assertFalse(parsed["well_formed"])
                    self.assertTrue(parsed["invalidated"])
                    self.assertEqual(parsed["source_modify_events"], 0)
                    self.assertEqual(
                        parsed["source_content_write_events"], 0
                    )
                    verdict = module._evaluate(
                        module.BEFORE, module.BEFORE, native,
                        source_wd, True, False, directory_watch=parent_wd,
                        directory_inventory_names=(
                            "public-same-bytes", "sample"
                        ),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(
                        verdict["independent_os_proof_verified"], False
                    )
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # The original pathname and original inode return, but
                # the native observed swaps are still historical evidence.
                os.unlink(other)
                removed = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_DELETE, 0, b"public-same-bytes"),
                    removed,
                )
                self.assertIn(
                    (other_wd, module.IN_DELETE_SELF, 0, b""), removed
                )
                self.assertIn(
                    (other_wd, module.IN_IGNORED, 0, b""), removed
                )
                self.assertEqual(module._read_receipt_pending(fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = os.lstat(sample)
                final_parent = os.lstat(sample.parent)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (first.st_dev, first.st_ino, first.st_mode),
                )
                self.assertEqual(
                    (final_parent.st_dev, final_parent.st_ino, final_parent.st_mode),
                    (first_parent.st_dev, first_parent.st_ino,
                     first_parent.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                if fd is not None:
                    os.close(fd)
                    with self.assertRaises(OSError):
                        os.fstat(fd)
