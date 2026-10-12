from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec973", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Linux inotify.h per-directory registration modifier.
IN_EXCL_UNLINK = 0x04000000


@unittest.skipUnless(sys.platform == "linux", "native IN_EXCL_UNLINK is Linux-only")
class NativeExcludeUnlinkedChildrenRegression(unittest.TestCase):
    def test_real_parent_instances_differ_for_unlinked_open_child(self):
        normal_fd = None
        filtered_fd = None
        sibling_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            pos = 0
            result = []
            while pos < len(data):
                self.assertGreaterEqual(len(data) - pos, module.EVENT.size)
                wd, mask, cookie, length = module.EVENT.unpack_from(data, pos)
                pos += module.EVENT.size
                self.assertLessEqual(length, len(data) - pos)
                name = data[pos:pos + length].split(b"\x00", 1)[0]
                pos += length
                result.append((wd, mask, cookie, name))
            self.assertEqual(pos, len(data))
            return result

        with tempfile.TemporaryDirectory(
            prefix="dec973-public-exclude-unlink-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            start_file = os.lstat(sample)
            start_parent = os.lstat(sample.parent)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                normal_fd, source_wd, parent_wd = module._start_watch(sample)
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
                lib = module.ctypes.CDLL(None, use_errno=True)
                lib.inotify_init1.argtypes = [module.ctypes.c_int]
                lib.inotify_init1.restype = module.ctypes.c_int
                lib.inotify_add_watch.argtypes = [
                    module.ctypes.c_int, module.ctypes.c_char_p,
                    module.ctypes.c_uint32,
                ]
                lib.inotify_add_watch.restype = module.ctypes.c_int

                filtered_fd = lib.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreaterEqual(filtered_fd, 0)
                filtered_parent_wd = lib.inotify_add_watch(
                    filtered_fd, module._checked_watch_path_bytes(sample.parent),
                    module.IN_MODIFY | module.IN_CLOSE_WRITE |
                    module.IN_CREATE | module.IN_DELETE |
                    IN_EXCL_UNLINK | module.IN_DONT_FOLLOW | module.IN_ONLYDIR,
                )
                self.assertGreater(filtered_parent_wd, 0)
                self.assertEqual(module._read_receipt_pending(filtered_fd), b"")

                sibling = sample.parent / "public-open-unlinked-child"
                self.assertEqual(sibling.write_bytes(b"PUBLIC-START"),
                                 len(b"PUBLIC-START"))
                normal_create = module._read_receipt_pending(normal_fd)
                filtered_create = module._read_receipt_pending(filtered_fd)
                self.assertTrue(normal_create)
                self.assertTrue(filtered_create)
                self.assertTrue(module._classify_stream(
                    normal_create, source_wd, parent_wd
                )["well_formed"])
                self.assertTrue(any(
                    wd == parent_wd and mask & module.IN_CREATE
                    and name == b"public-open-unlinked-child"
                    for wd, mask, cookie, name in records(normal_create)
                ))
                self.assertTrue(any(
                    wd == filtered_parent_wd and mask & module.IN_CREATE
                    and name == b"public-open-unlinked-child"
                    for wd, mask, cookie, name in records(filtered_create)
                ))

                # Keep a real child descriptor live across actual unlink.
                sibling_fd = os.open(sibling, os.O_RDWR | os.O_CLOEXEC)
                os.unlink(sibling)
                normal_unlink = module._read_receipt_pending(normal_fd)
                filtered_unlink = module._read_receipt_pending(filtered_fd)
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_DELETE
                    and name == b"public-open-unlinked-child"
                    for wd, mask, cookie, name in records(normal_unlink)
                ))
                self.assertTrue(any(
                    wd == filtered_parent_wd and mask == module.IN_DELETE
                    and name == b"public-open-unlinked-child"
                    for wd, mask, cookie, name in records(filtered_unlink)
                ))
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))

                # Both directory watches remain installed. By native Linux
                # design only IN_EXCL_UNLINK suppresses subsequent child
                # writes via the still-open but now unlinked descriptor.
                self.assertEqual(os.write(sibling_fd, b"PUBLIC-CHANGED"),
                                 len(b"PUBLIC-CHANGED"))
                os.fsync(sibling_fd)
                normal_write = module._read_receipt_pending(normal_fd)
                self.assertTrue(normal_write)
                self.assertTrue(any(
                    wd == parent_wd and mask & module.IN_MODIFY
                    and name == b"public-open-unlinked-child"
                    for wd, mask, cookie, name in records(normal_write)
                ))
                self.assertEqual(module._read_receipt_pending(filtered_fd), b"")
                self.assertTrue(module._classify_stream(
                    normal_write, source_wd, parent_wd
                )["well_formed"])
                os.close(sibling_fd)
                sibling_fd = None
                normal_close = module._read_receipt_pending(normal_fd)
                self.assertTrue(any(
                    wd == parent_wd and mask & module.IN_CLOSE_WRITE
                    and name == b"public-open-unlinked-child"
                    for wd, mask, cookie, name in records(normal_close)
                ))
                self.assertEqual(module._read_receipt_pending(filtered_fd), b"")
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")

                # The filtered watch is NOT dead: the still-linked sample
                # continues to trigger both source and directory events.
                for content in (module.AFTER, module.BEFORE):
                    with sample.open("r+b") as writer:
                        self.assertEqual(writer.write(content), len(content))
                        writer.truncate()
                        writer.flush()
                        os.fsync(writer.fileno())
                    normal = module._read_receipt_pending(normal_fd)
                    filtered = module._read_receipt_pending(filtered_fd)
                    self.assertTrue(normal)
                    self.assertTrue(filtered)
                    native = module._classify_stream(normal, source_wd, parent_wd)
                    self.assertTrue(native["well_formed"])
                    self.assertFalse(native["invalidated"])
                    self.assertGreaterEqual(native["source_modify_events"], 1)
                    self.assertTrue(any(
                        wd == filtered_parent_wd and mask & module.IN_MODIFY
                        and name == b"sample"
                        for wd, mask, cookie, name in records(filtered)
                    ))
                    self.assertEqual(module._read_receipt_pending(normal_fd), b"")
                    self.assertEqual(module._read_receipt_pending(filtered_fd), b"")
                    verdict = module._evaluate(
                        module.BEFORE, content, normal, source_wd,
                        True, False, directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(verdict["independent_os_proof_verified"], False)

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                last_file = os.lstat(sample)
                last_parent = os.lstat(sample.parent)
                self.assertEqual(
                    (last_file.st_dev, last_file.st_ino, last_file.st_mode),
                    (start_file.st_dev, start_file.st_ino, start_file.st_mode),
                )
                self.assertEqual(
                    (last_parent.st_dev, last_parent.st_ino, last_parent.st_mode),
                    (start_parent.st_dev, start_parent.st_ino,
                     start_parent.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                for fd in (sibling_fd, filtered_fd, normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
