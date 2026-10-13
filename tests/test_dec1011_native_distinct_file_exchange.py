from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1011", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

AT_FDCWD = -100
RENAME_EXCHANGE = 2


@unittest.skipUnless(sys.platform == "linux", "Linux native regular-file exchange only")
class NativeDistinctFileExchangeRegression(unittest.TestCase):
    def test_distinct_file_exchange_swaps_names_not_watches_and_redirects_writes(self):
        fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            result = []
            offset = 0
            while offset < len(data):
                self.assertGreaterEqual(len(data) - offset, module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(data, offset)
                offset += module.EVENT.size
                self.assertLessEqual(length, len(data) - offset)
                name = data[offset:offset + length].split(b"\0", 1)[0]
                offset += length
                result.append((wd, mask, cookie, name))
            self.assertEqual(offset, len(data))
            return result

        with tempfile.TemporaryDirectory(
            prefix="dec1011-public-distinct-file-exchange-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            other = sample.parent / "public-other"
            other_before = b"PUBLIC_OTHER_START"
            other_after = b"PUBLIC_OTHER_WRITE"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            sample_stat = os.lstat(sample)
            parent_stat = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                self.assertEqual(other.write_bytes(other_before),
                                 len(other_before))
                other_stat = os.lstat(other)
                self.assertNotEqual(sample_stat.st_ino, other_stat.st_ino)
                created = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_CREATE, 0, b"public-other"), created
                )
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

                source_bytes = module._checked_watch_path_bytes(sample)
                other_bytes = module._checked_watch_path_bytes(other)

                def exchange():
                    module.ctypes.set_errno(0)
                    rc = lib.renameat2(
                        AT_FDCWD, source_bytes, AT_FDCWD, other_bytes,
                        RENAME_EXCHANGE,
                    )
                    self.assertEqual(
                        rc, 0,
                        f"renameat2 errno {module.ctypes.get_errno()}",
                    )
                    native = module._read_receipt_pending(fd)
                    ev = records(native)
                    self.assertEqual(len(ev), 6)
                    frm = [(cookie, name) for wd, mask, cookie, name in ev
                           if wd == parent_wd and mask == module.IN_MOVED_FROM]
                    to = [(cookie, name) for wd, mask, cookie, name in ev
                          if wd == parent_wd and mask == module.IN_MOVED_TO]
                    self.assertEqual(len(frm), 2)
                    self.assertEqual(len(to), 2)
                    self.assertEqual(
                        sorted(cookie for cookie, _ in frm),
                        sorted(cookie for cookie, _ in to),
                    )
                    self.assertEqual(len({cookie for cookie, _ in frm}), 2)
                    self.assertTrue(all(cookie > 0 for cookie, _ in frm))
                    for cookie, name in frm:
                        matched = [dest for c, dest in to if c == cookie]
                        self.assertEqual(len(matched), 1)
                        self.assertNotEqual(matched[0], name)
                    self.assertIn(
                        (source_wd, module.IN_MOVE_SELF, 0, b""), ev
                    )
                    self.assertIn(
                        (other_wd, module.IN_MOVE_SELF, 0, b""), ev
                    )
                    self.assertFalse(any(
                        mask & (module.IN_DELETE_SELF | module.IN_IGNORED)
                        for wd, mask, cookie, name in ev
                    ))
                    self.assertFalse(module._classify_stream(
                        native, source_wd, parent_wd
                    )["well_formed"])
                    verdict = module._evaluate(
                        module.BEFORE, module.BEFORE, native, source_wd,
                        True, False, directory_watch=parent_wd,
                        directory_inventory_names=("public-other", "sample"),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(
                        verdict["independent_os_proof_verified"], False
                    )
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                exchange()
                self.assertEqual(os.lstat(sample).st_ino, other_stat.st_ino)
                self.assertEqual(os.lstat(other).st_ino, sample_stat.st_ino)

                # The original sample PATH now names the OTHER inode.
                with sample.open("r+b") as writer:
                    self.assertEqual(writer.write(other_after), len(other_after))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                other_write = module._read_receipt_pending(fd)
                other_events = records(other_write)
                self.assertTrue(any(
                    wd == other_wd and mask == module.IN_MODIFY
                    for wd, mask, cookie, name in other_events
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, cookie, name in other_events
                ))
                self.assertFalse(any(
                    wd == source_wd for wd, mask, cookie, name in other_events
                ))
                self.assertFalse(module._classify_stream(
                    other_write, source_wd, parent_wd
                )["well_formed"])
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # The alternative PATH now names the ORIGINAL source inode.
                with other.open("r+b") as writer:
                    self.assertEqual(writer.write(module.AFTER),
                                     len(module.AFTER))
                    writer.truncate()
                    writer.flush()
                    os.fsync(writer.fileno())
                source_write = module._read_receipt_pending(fd)
                source_events = records(source_write)
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, cookie, name in source_events
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"public-other"
                    for wd, mask, cookie, name in source_events
                ))
                self.assertFalse(any(
                    wd == other_wd for wd, mask, cookie, name in source_events
                ))
                parsed = module._classify_stream(
                    source_write, source_wd, parent_wd
                )
                self.assertTrue(parsed["well_formed"])
                self.assertFalse(parsed["invalidated"])
                self.assertGreaterEqual(parsed["source_modify_events"], 1)
                verdict = module._evaluate(
                    module.BEFORE, module.AFTER, source_write, source_wd,
                    True, False, directory_watch=parent_wd,
                    directory_inventory_names=("public-other", "sample"),
                )
                self.assertEqual(verdict["status"], "BLOCKED")
                self.assertIs(verdict["can_authorize_dispatch"], False)
                self.assertIs(verdict["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # Atomic swap-back restores each original pathname/inode.
                # It cannot erase the two real writes observed mid-swap.
                exchange()
                self.assertEqual(os.lstat(sample).st_ino, sample_stat.st_ino)
                self.assertEqual(os.lstat(other).st_ino, other_stat.st_ino)

                for path, original_bytes, watched_wd in (
                    (sample, module.BEFORE, source_wd),
                    (other, other_before, other_wd),
                ):
                    with path.open("r+b") as writer:
                        self.assertEqual(writer.write(original_bytes),
                                         len(original_bytes))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    restored = records(module._read_receipt_pending(fd))
                    self.assertTrue(any(
                        wd == watched_wd and mask == module.IN_MODIFY
                        for wd, mask, cookie, name in restored
                    ))
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(other.read_bytes(), other_before)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                os.unlink(other)
                removed = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_DELETE, 0, b"public-other"),
                    removed,
                )
                self.assertIn((other_wd, module.IN_DELETE_SELF, 0, b""), removed)
                self.assertIn((other_wd, module.IN_IGNORED, 0, b""), removed)
                self.assertEqual(module._read_receipt_pending(fd), b"")

                after = os.lstat(sample)
                parent_after = os.lstat(sample.parent)
                self.assertEqual(
                    (after.st_dev, after.st_ino, after.st_mode),
                    (sample_stat.st_dev, sample_stat.st_ino, sample_stat.st_mode),
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
