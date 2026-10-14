from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1064", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "Linux native IN_ONESHOT required")
class NativeSourceModifyAttribCombinedOneShot(unittest.TestCase):
    def test_first_attribute_then_first_modify_each_disarm_combined_mask(self):
        first_fd = None
        second_fd = None
        independent_fd = None

        def records(data):
            self.assertIs(type(data), bytes)
            offset = 0
            parsed = []
            while offset < len(data):
                self.assertGreaterEqual(len(data) - offset, module.EVENT.size)
                wd, mask, cookie, size = module.EVENT.unpack_from(data, offset)
                offset += module.EVENT.size
                self.assertLessEqual(size, len(data) - offset)
                name = data[offset:offset + size].split(b"\x00", 1)[0]
                offset += size
                self.assertEqual(cookie, 0)
                parsed.append((wd, mask, name))
            self.assertEqual(offset, len(data))
            return parsed

        def changed_bytes(path, content):
            with path.open("r+b") as writer:
                self.assertEqual(writer.write(content), len(content))
                writer.truncate()
                writer.flush()
                os.fsync(writer.fileno())

        with tempfile.TemporaryDirectory(
            prefix="dec1064-public-dual-mask-source-oneshot-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            os.chmod(sample, 0o600)
            initial = os.lstat(sample)
            parent_initial = os.lstat(sample.parent)
            self.assertEqual(stat.S_IMODE(initial.st_mode), 0o600)
            self.assertEqual(module._bounded_inventory_names(sample.parent),
                             ("sample",))
            try:
                independent_fd, source_wd, parent_wd = (
                    module._start_watch(sample)
                )
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32
                ]
                libc.inotify_add_watch.restype = ctypes.c_int

                def create_oneshot():
                    fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                    self.assertGreater(fd, 2)
                    wd = libc.inotify_add_watch(
                        fd, module._checked_watch_path_bytes(sample),
                        module.IN_MODIFY | module.IN_ATTRIB |
                        module.IN_DONT_FOLLOW | IN_ONESHOT,
                    )
                    self.assertGreater(wd, 0)
                    self.assertEqual(module._read_receipt_pending(fd), b"")
                    return fd, wd

                first_fd, first_wd = create_oneshot()
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # BOTH event types were subscribed. First matching
                # real chmod disarms watch BEFORE later content write.
                os.chmod(sample, 0o640)
                self.assertEqual(stat.S_IMODE(os.lstat(sample).st_mode),
                                 0o640)
                self.assertEqual(records(
                    module._read_receipt_pending(first_fd)
                ), [
                    (first_wd, module.IN_ATTRIB, b""),
                    (first_wd, module.IN_IGNORED, b""),
                ])
                witnessed_attributes = module._read_receipt_pending(independent_fd)
                self.assertIn(
                    (source_wd, module.IN_ATTRIB, b""),
                    records(witnessed_attributes),
                )
                self.assertIn(
                    (parent_wd, module.IN_ATTRIB, b"sample"),
                    records(witnessed_attributes),
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                changed_bytes(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(first_fd), b"")
                full_write = module._read_receipt_pending(independent_fd)
                self.assertIn(
                    (source_wd, module.IN_MODIFY, b""), records(full_write)
                )
                self.assertIn(
                    (parent_wd, module.IN_MODIFY, b"sample"),
                    records(full_write),
                )
                decision = module._evaluate(
                    module.BEFORE, module.AFTER, full_write,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(decision["status"], "BLOCKED")
                self.assertIs(decision["can_authorize_dispatch"], False)
                self.assertIs(
                    decision["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                # A freshly registered, SEPARATE one-shot with exactly
                # the same BOTH-event mask is triggered by real MODIFY.
                # It is then unable to observe mode restoration.
                second_fd, second_wd = create_oneshot()
                changed_bytes(sample, module.BEFORE)
                self.assertEqual(records(
                    module._read_receipt_pending(second_fd)
                ), [
                    (second_wd, module.IN_MODIFY, b""),
                    (second_wd, module.IN_IGNORED, b""),
                ])
                independent_restore_write = module._read_receipt_pending(independent_fd)
                self.assertIn(
                    (source_wd, module.IN_MODIFY, b""),
                    records(independent_restore_write),
                )
                self.assertIn(
                    (parent_wd, module.IN_MODIFY, b"sample"),
                    records(independent_restore_write),
                )
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                os.chmod(sample, 0o600)
                self.assertEqual(module._read_receipt_pending(first_fd), b"")
                self.assertEqual(module._read_receipt_pending(second_fd), b"")
                mode_restore = module._read_receipt_pending(independent_fd)
                self.assertIn(
                    (source_wd, module.IN_ATTRIB, b""),
                    records(mode_restore),
                )
                self.assertIn(
                    (parent_wd, module.IN_ATTRIB, b"sample"),
                    records(mode_restore),
                )
                self.assertFalse(any(
                    mask == module.IN_IGNORED
                    for wd, mask, name in records(mode_restore)
                ))
                self.assertEqual(module._read_receipt_pending(independent_fd), b"")

                last = os.lstat(sample)
                parent_last = os.lstat(sample.parent)
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(
                    (last.st_dev, last.st_ino, last.st_mode),
                    (initial.st_dev, initial.st_ino, initial.st_mode),
                )
                self.assertEqual(
                    (parent_last.st_dev, parent_last.st_ino,
                     parent_last.st_mode),
                    (parent_initial.st_dev, parent_initial.st_ino,
                     parent_initial.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(sample.parent),
                                 ("sample",))
            finally:
                if sample.exists():
                    os.chmod(sample, 0o600)
                for fd in (second_fd, first_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
