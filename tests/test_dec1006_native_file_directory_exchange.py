from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1006", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

RENAME_EXCHANGE = 2
AT_FDCWD = -100


@unittest.skipUnless(sys.platform == "linux", "Linux native mixed-type exchange only")
class NativeFileDirectoryExchangeRegression(unittest.TestCase):
    def test_atomic_file_directory_exchange_swaps_path_types_not_watched_inodes(self):
        fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            offset = 0
            result = []
            while offset < len(stream):
                self.assertGreaterEqual(len(stream) - offset, module.EVENT.size)
                wd, mask, cookie, size = module.EVENT.unpack_from(stream, offset)
                offset += module.EVENT.size
                self.assertLessEqual(size, len(stream) - offset)
                name = stream[offset:offset + size].split(b"\x00", 1)[0]
                offset += size
                result.append((wd, mask, cookie, name))
            self.assertEqual(offset, len(stream))
            return result

        with tempfile.TemporaryDirectory(
            prefix="dec1006-public-mixed-exchange-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            other_dir = Path(tmp) / "public-other-dir"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial_file = os.lstat(sample)
            initial_parent = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertNotEqual(source_wd, parent_wd)
                self.assertEqual(module._read_receipt_pending(fd), b"")
                other_dir.mkdir()
                first_dir = os.lstat(other_dir)
                self.assertTrue(stat.S_ISDIR(first_dir.st_mode))
                made = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_CREATE | module.IN_ISDIR, 0,
                     b"public-other-dir"), made
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
                dir_wd = lib.inotify_add_watch(
                    fd, module._checked_watch_path_bytes(other_dir),
                    module.IN_MOVE_SELF | module.IN_DELETE_SELF |
                    module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(dir_wd, 0)
                self.assertNotIn(dir_wd, (source_wd, parent_wd))
                self.assertEqual(module._read_receipt_pending(fd), b"")

                sample_bytes = module._checked_watch_path_bytes(sample)
                other_bytes = module._checked_watch_path_bytes(other_dir)

                for iteration in range(2):
                    module.ctypes.set_errno(0)
                    result = lib.renameat2(
                        AT_FDCWD, sample_bytes,
                        AT_FDCWD, other_bytes, RENAME_EXCHANGE,
                    )
                    self.assertEqual(
                        result, 0,
                        f"renameat2 errno: {module.ctypes.get_errno()}",
                    )
                    if iteration == 0:
                        self.assertEqual(os.lstat(sample).st_ino,
                                         first_dir.st_ino)
                        self.assertEqual(os.lstat(other_dir).st_ino,
                                         initial_file.st_ino)
                        self.assertTrue(stat.S_ISDIR(os.lstat(sample).st_mode))
                        self.assertTrue(stat.S_ISREG(os.lstat(other_dir).st_mode))
                    else:
                        self.assertEqual(os.lstat(sample).st_ino,
                                         initial_file.st_ino)
                        self.assertEqual(os.lstat(other_dir).st_ino,
                                         first_dir.st_ino)
                        self.assertTrue(stat.S_ISREG(os.lstat(sample).st_mode))
                        self.assertTrue(stat.S_ISDIR(os.lstat(other_dir).st_mode))

                    stream = module._read_receipt_pending(fd)
                    events = records(stream)
                    self.assertEqual(len(events), 6)
                    file_from = [
                        (cookie, name) for wd, mask, cookie, name in events
                        if wd == parent_wd and mask == module.IN_MOVED_FROM
                    ]
                    file_to = [
                        (cookie, name) for wd, mask, cookie, name in events
                        if wd == parent_wd and mask == module.IN_MOVED_TO
                    ]
                    dir_from = [
                        (cookie, name) for wd, mask, cookie, name in events
                        if wd == parent_wd and
                        mask == (module.IN_MOVED_FROM | module.IN_ISDIR)
                    ]
                    dir_to = [
                        (cookie, name) for wd, mask, cookie, name in events
                        if wd == parent_wd and
                        mask == (module.IN_MOVED_TO | module.IN_ISDIR)
                    ]
                    self.assertEqual(len(file_from), 1)
                    self.assertEqual(len(file_to), 1)
                    self.assertEqual(len(dir_from), 1)
                    self.assertEqual(len(dir_to), 1)
                    self.assertEqual(file_from[0][0], file_to[0][0])
                    self.assertEqual(dir_from[0][0], dir_to[0][0])
                    self.assertGreater(file_from[0][0], 0)
                    self.assertGreater(dir_from[0][0], 0)
                    self.assertNotEqual(file_from[0][0], dir_from[0][0])
                    self.assertEqual(
                        (file_from[0][1], file_to[0][1]),
                        (b"sample", b"public-other-dir")
                        if iteration == 0 else
                        (b"public-other-dir", b"sample"),
                    )
                    self.assertEqual(
                        (dir_from[0][1], dir_to[0][1]),
                        (b"public-other-dir", b"sample")
                        if iteration == 0 else
                        (b"sample", b"public-other-dir"),
                    )
                    self.assertIn(
                        (source_wd, module.IN_MOVE_SELF, 0, b""), events
                    )
                    self.assertIn(
                        (dir_wd, module.IN_MOVE_SELF, 0, b""), events
                    )
                    self.assertFalse(any(
                        mask & (module.IN_DELETE_SELF | module.IN_IGNORED)
                        for wd, mask, cookie, name in events
                    ))
                    # No aliasing or trimming the genuine extra directory WD.
                    self.assertFalse(module._classify_stream(
                        stream, source_wd, parent_wd
                    )["well_formed"])
                    verdict = module._evaluate(
                        module.BEFORE, module.BEFORE, stream,
                        source_wd, True, False, directory_watch=parent_wd,
                        directory_inventory_names=(
                            "public-other-dir", "sample",
                        ),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(
                        verdict["independent_os_proof_verified"], False
                    )
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                # Directory is restored to its initial separate path. Its
                # original WD invalidates when the real inode is removed.
                other_dir.rmdir()
                removed = records(module._read_receipt_pending(fd))
                self.assertIn(
                    (parent_wd, module.IN_DELETE | module.IN_ISDIR, 0,
                     b"public-other-dir"), removed
                )
                self.assertIn(
                    (dir_wd, module.IN_DELETE_SELF, 0, b""), removed
                )
                self.assertIn(
                    (dir_wd, module.IN_IGNORED, 0, b""), removed
                )
                self.assertEqual(module._read_receipt_pending(fd), b"")

                # Original regular-file source and parent subscriptions
                # still detect changed bytes and a true byte restoration.
                for content in (module.AFTER, module.BEFORE):
                    with sample.open("r+b") as writer:
                        self.assertEqual(writer.write(content), len(content))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    stream = module._read_receipt_pending(fd)
                    parsed = module._classify_stream(
                        stream, source_wd, parent_wd
                    )
                    self.assertTrue(parsed["well_formed"])
                    self.assertFalse(parsed["invalidated"])
                    self.assertGreaterEqual(parsed["source_modify_events"], 1)
                    self.assertGreaterEqual(
                        parsed["source_content_write_events"], 1
                    )
                    final_verdict = module._evaluate(
                        module.BEFORE, content, stream,
                        source_wd, True, False, directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(final_verdict["status"], "BLOCKED")
                    self.assertIs(
                        final_verdict["can_authorize_dispatch"], False
                    )
                    self.assertIs(
                        final_verdict["independent_os_proof_verified"], False
                    )
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                file_after = os.lstat(sample)
                parent_after = os.lstat(sample.parent)
                self.assertEqual(
                    (file_after.st_dev, file_after.st_ino, file_after.st_mode),
                    (initial_file.st_dev, initial_file.st_ino,
                     initial_file.st_mode),
                )
                self.assertEqual(
                    (parent_after.st_dev, parent_after.st_ino, parent_after.st_mode),
                    (initial_parent.st_dev, initial_parent.st_ino,
                     initial_parent.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                if fd is not None:
                    os.close(fd)
                    with self.assertRaises(OSError):
                        os.fstat(fd)
