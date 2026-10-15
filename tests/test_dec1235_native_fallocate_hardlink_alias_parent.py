from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1235", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000
IN_MASK = module.IN_MODIFY | module.IN_CLOSE_WRITE


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeFallocateHardlinkAliasRouting(unittest.TestCase):
    def test_alias_fallocate_routes_named_events_to_alias_parent_only(self):
        normal_fd = original_fd = alias_fd = writer_fd = restore_fd = None
        before = b"A" * 16 + b"B" * 16 + b"C" * 16
        changed = b"A" * 16 + b"\x00" * 16 + b"C" * 16

        def parse(data):
            self.assertIs(type(data), bytes)
            observed = []
            offset = 0
            while offset < len(data):
                self.assertGreaterEqual(len(data)-offset, module.EVENT.size)
                wd, mask, cookie, n = module.EVENT.unpack_from(data, offset)
                offset += module.EVENT.size
                self.assertLessEqual(n, len(data)-offset)
                name = data[offset:offset+n].split(b"\x00", 1)[0]
                offset += n
                self.assertEqual(cookie, 0)
                observed.append((wd, mask, name))
            self.assertEqual(offset, len(data))
            return observed

        with tempfile.TemporaryDirectory(
            prefix="dec1235-public-hardlink-fallocate-", dir="/tmp"
        ) as tmp:
            root = Path(tmp)
            original_parent = root / "original"
            alias_parent = root / "alias"
            original_parent.mkdir()
            alias_parent.mkdir()
            source = original_parent / "sample"
            alias = alias_parent / "link"
            self.assertEqual(source.write_bytes(before), len(before))
            os.link(source, alias)
            start_source = os.lstat(source)
            start_alias = os.lstat(alias)
            start_parent = os.lstat(original_parent)
            start_alias_parent = os.lstat(alias_parent)
            self.assertEqual((start_source.st_dev, start_source.st_ino),
                             (start_alias.st_dev, start_alias.st_ino))
            self.assertEqual(module._bounded_inventory_names(original_parent),
                             ("sample",))
            self.assertEqual(module._bounded_inventory_names(alias_parent),
                             ("link",))
            try:
                normal_fd, source_wd, parent_wd = module._start_watch(source)
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                libc.fallocate.argtypes = [
                    ctypes.c_int, ctypes.c_int,
                    ctypes.c_longlong, ctypes.c_longlong,
                ]
                libc.fallocate.restype = ctypes.c_int
                original_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                alias_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertEqual(len({normal_fd, original_fd, alias_fd}), 3)
                original_wd = libc.inotify_add_watch(
                    original_fd, module._checked_watch_path_bytes(source),
                    IN_MASK | module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                alias_wd = libc.inotify_add_watch(
                    alias_fd, module._checked_watch_path_bytes(alias_parent),
                    IN_MASK | module.IN_ONLYDIR | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(original_wd, 0)
                self.assertGreater(alias_wd, 0)
                for fd in (normal_fd, original_fd, alias_fd):
                    self.assertEqual(module._read_receipt_pending(fd), b"")

                writer_fd = os.open(alias, os.O_WRONLY | os.O_CLOEXEC)
                for step in (1, 2):
                    self.assertEqual(
                        libc.fallocate(writer_fd, 0x11, 16, 16), 0,
                        os.strerror(ctypes.get_errno()),
                    )
                    self.assertEqual(os.fstat(writer_fd).st_size, len(before))
                    # Same inode: source MODIFY is real. Path provenance:
                    # only the hardlink alias's parent gets named MODIFY.
                    real_receipt = module._read_receipt_pending(normal_fd)
                    self.assertEqual(parse(real_receipt),
                                     [(source_wd, module.IN_MODIFY, b"")])
                    self.assertEqual(
                        parse(module._read_receipt_pending(alias_fd)),
                        [(alias_wd, module.IN_MODIFY, b"link")],
                    )
                    if step == 1:
                        self.assertEqual(
                            parse(module._read_receipt_pending(original_fd)),
                            [(original_wd, module.IN_MODIFY, b""),
                             (original_wd, module.IN_IGNORED, b"")],
                        )
                    else:
                        self.assertEqual(module._read_receipt_pending(original_fd),
                                         b"")
                    prior = before if step == 1 else changed
                    result = module._evaluate(
                        prior, changed, real_receipt, source_wd, True, False,
                        directory_watch=parent_wd,
                        directory_inventory_names=("sample",),
                    )
                    self.assertEqual(result["status"], "BLOCKED")
                    self.assertIs(result["can_authorize_dispatch"], False)
                    self.assertIs(result["independent_os_proof_verified"], False)
                    self.assertEqual(source.read_bytes(), changed)
                    self.assertEqual(alias.read_bytes(), changed)
                    self.assertEqual(module._read_receipt_pending(normal_fd), b"")
                os.close(writer_fd)
                writer_fd = None
                self.assertEqual(
                    parse(module._read_receipt_pending(normal_fd)),
                    [(source_wd, module.IN_CLOSE_WRITE, b"")],
                )
                self.assertEqual(
                    parse(module._read_receipt_pending(alias_fd)),
                    [(alias_wd, module.IN_CLOSE_WRITE, b"link")],
                )
                self.assertEqual(module._read_receipt_pending(original_fd), b"")

                # Restoration through ORIGINAL name routes the parent
                # receipt back to original_parent, not alias_parent.
                restore_fd = os.open(source, os.O_WRONLY | os.O_TRUNC |
                                     os.O_CLOEXEC)
                self.assertEqual(os.write(restore_fd, before), len(before))
                os.fsync(restore_fd)
                os.close(restore_fd)
                restore_fd = None
                receipt = module._read_receipt_pending(normal_fd)
                entries = parse(receipt)
                allowed = {
                    (source_wd, module.IN_MODIFY, b""),
                    (parent_wd, module.IN_MODIFY, b"sample"),
                    (source_wd, module.IN_CLOSE_WRITE, b""),
                    (parent_wd, module.IN_CLOSE_WRITE, b"sample"),
                }
                self.assertTrue(entries)
                self.assertTrue(all(x in allowed for x in entries))
                self.assertTrue(allowed.issubset(set(entries)))
                self.assertEqual(module._read_receipt_pending(alias_fd), b"")
                result = module._evaluate(
                    changed, before, receipt, source_wd, True, False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(result["status"], "BLOCKED")
                self.assertIs(result["can_authorize_dispatch"], False)
                self.assertIs(result["independent_os_proof_verified"], False)
                self.assertEqual(module._read_receipt_pending(normal_fd), b"")
                self.assertEqual(module._read_receipt_pending(original_fd), b"")
                for path, old in ((source, start_source),
                                  (alias, start_alias),
                                  (original_parent, start_parent),
                                  (alias_parent, start_alias_parent)):
                    now = os.lstat(path)
                    self.assertEqual(
                        (now.st_dev, now.st_ino, now.st_mode, now.st_nlink),
                        (old.st_dev, old.st_ino, old.st_mode, old.st_nlink),
                    )
                self.assertEqual(source.read_bytes(), before)
                self.assertEqual(alias.read_bytes(), before)
                self.assertEqual(module._bounded_inventory_names(original_parent),
                                 ("sample",))
                self.assertEqual(module._bounded_inventory_names(alias_parent),
                                 ("link",))
            finally:
                for fd in (writer_fd, restore_fd, original_fd,
                           alias_fd, normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
