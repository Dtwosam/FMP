from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1010", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

AT_FDCWD = -100
RENAME_EXCHANGE = 2


@unittest.skipUnless(sys.platform == "linux", "renameat2 is Linux-only")
class NativeSameInodeExchangeNoopRegression(unittest.TestCase):
    def test_exchange_hardlink_names_same_inode_returns_zero_with_no_move_events(self):
        fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            pos = 0
            output = []
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(length, len(data) - pos)
                name = data[pos:pos + length].split(b"\x00", 1)[0]
                pos += length
                output.append((wd, mask, cookie, name))
            self.assertEqual(pos, len(data))
            return output

        with tempfile.TemporaryDirectory(
            prefix="dec1010-public-same-inode-exchange-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            alias = sample.parent / "public-hardlink-alias"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first = os.lstat(sample)
            parent_first = os.lstat(sample.parent)
            self.assertEqual(first.st_nlink, 1)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                os.link(sample, alias)
                linked = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_CREATE, 0, b"public-hardlink-alias"),
                    linked,
                )
                self.assertIn(
                    (source_wd, module.IN_ATTRIB, 0, b""), linked
                )
                self.assertEqual(os.lstat(sample).st_nlink, 2)
                self.assertEqual(
                    (os.lstat(alias).st_dev, os.lstat(alias).st_ino),
                    (first.st_dev, first.st_ino),
                )
                self.assertEqual(module._read_receipt_pending(fd), b"")

                lib = module.ctypes.CDLL(None, use_errno=True)
                if not hasattr(lib, "renameat2"):
                    self.skipTest("libc renameat2 unavailable")
                lib.renameat2.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint,
                ]
                lib.renameat2.restype = module.ctypes.c_int
                source_bytes = module._checked_watch_path_bytes(sample)
                alias_bytes = module._checked_watch_path_bytes(alias)

                # Two different pathnames designate ONE inode. A native
                # atomic exchange returns success without a true move.
                module.ctypes.set_errno(0)
                exchange = lib.renameat2(
                    AT_FDCWD, source_bytes, AT_FDCWD, alias_bytes,
                    RENAME_EXCHANGE,
                )
                self.assertEqual(
                    exchange, 0,
                    f"native exchange errno {module.ctypes.get_errno()}",
                )
                self.assertEqual(module._read_receipt_pending(fd), b"")
                self.assertEqual(
                    (os.lstat(sample).st_dev, os.lstat(sample).st_ino),
                    (first.st_dev, first.st_ino),
                )
                self.assertEqual(
                    (os.lstat(alias).st_dev, os.lstat(alias).st_ino),
                    (first.st_dev, first.st_ino),
                )
                self.assertEqual(os.lstat(sample).st_nlink, 2)
                self.assertEqual(
                    module._bounded_inventory_names(sample.parent),
                    ("public-hardlink-alias", "sample"),
                )

                # The absence of move events is NOT an absence of writes:
                # both source/parent watches still see real modifications
                # performed separately through either hardlink name.
                for path, content, entry in (
                    (alias, module.AFTER, b"public-hardlink-alias"),
                    (sample, module.BEFORE, b"sample"),
                ):
                    with path.open("r+b") as writer:
                        self.assertEqual(writer.write(content), len(content))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    native = module._read_receipt_pending(fd)
                    self.assertTrue(native)
                    parsed = module._classify_stream(native, source_wd, parent_wd)
                    self.assertTrue(parsed["well_formed"])
                    self.assertFalse(parsed["invalidated"])
                    self.assertGreaterEqual(parsed["source_modify_events"], 1)
                    self.assertGreaterEqual(
                        parsed["source_content_write_events"], 1
                    )
                    self.assertTrue(any(
                        wd == source_wd and mask == module.IN_MODIFY
                        for wd, mask, cookie, name in records(native)
                    ))
                    self.assertTrue(any(
                        wd == parent_wd and mask == module.IN_MODIFY
                        and name == entry
                        for wd, mask, cookie, name in records(native)
                    ))
                    verdict = module._evaluate(
                        module.BEFORE, content, native, source_wd,
                        True, False, directory_watch=parent_wd,
                        directory_inventory_names=(
                            "public-hardlink-alias", "sample"
                        ),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(verdict["independent_os_proof_verified"], False)
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                os.unlink(alias)
                removal = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_DELETE, 0, b"public-hardlink-alias"),
                    removal,
                )
                self.assertIn((source_wd, module.IN_ATTRIB, 0, b""), removal)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                final = os.lstat(sample)
                final_parent = os.lstat(sample.parent)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode, final.st_nlink),
                    (first.st_dev, first.st_ino, first.st_mode, first.st_nlink),
                )
                self.assertEqual(
                    (final_parent.st_dev, final_parent.st_ino, final_parent.st_mode),
                    (parent_first.st_dev, parent_first.st_ino,
                     parent_first.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                if fd is not None:
                    os.close(fd)
                    with self.assertRaises(OSError):
                        os.fstat(fd)
