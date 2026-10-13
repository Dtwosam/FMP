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
spec = importlib.util.spec_from_file_location("dec677_native_dec1050", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native one-shot event filters need Linux")
class NativeOneshotNonmatchingWriteThenAttribRegression(unittest.TestCase):
    def test_nonmatching_write_does_not_disarm_attrib_oneshot_until_chmod(self):
        oneshot_fd = None
        independent_fd = None

        def records(raw):
            self.assertIs(type(raw), bytes)
            parsed = []
            offset = 0
            while offset < len(raw):
                self.assertGreaterEqual(len(raw) - offset, module.EVENT.size)
                wd, mask, cookie, size = module.EVENT.unpack_from(raw, offset)
                offset += module.EVENT.size
                self.assertLessEqual(size, len(raw) - offset)
                name = raw[offset:offset + size].split(b"\x00", 1)[0]
                offset += size
                self.assertEqual(cookie, 0)
                parsed.append((wd, mask, name))
            self.assertEqual(offset, len(raw))
            return parsed

        def write_sample(path, value):
            with path.open("r+b") as writer:
                self.assertEqual(writer.write(value), len(value))
                writer.truncate()
                writer.flush()
                os.fsync(writer.fileno())

        with tempfile.TemporaryDirectory(
            prefix="dec1050-public-filtered-oneshot-", dir="/tmp"
        ) as tmp:
            sample = Path(tmp) / "sample"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            os.chmod(sample, 0o600)
            original = os.lstat(sample)
            parent_initial = os.lstat(sample.parent)
            self.assertEqual(stat.S_IMODE(original.st_mode), 0o600)
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
                oneshot_fd = libc.inotify_init1(
                    os.O_NONBLOCK | os.O_CLOEXEC
                )
                self.assertGreater(oneshot_fd, 2)
                oneshot_wd = libc.inotify_add_watch(
                    oneshot_fd, module._checked_watch_path_bytes(sample),
                    module.IN_ATTRIB | IN_ONESHOT | module.IN_DONT_FOLLOW,
                )
                self.assertGreater(oneshot_wd, 0)
                self.assertEqual(
                    module._read_receipt_pending(oneshot_fd), b""
                )
                self.assertEqual(
                    module._read_receipt_pending(independent_fd), b""
                )

                # A genuine content write does NOT match this source
                # watch's subscribed IN_ATTRIB-only one-shot action.
                # It must stay armed, emitting neither IN_ATTRIB nor
                # IN_IGNORED, while independent dual observer sees write.
                write_sample(sample, module.AFTER)
                self.assertEqual(module._read_receipt_pending(oneshot_fd), b"")
                independent_write = module._read_receipt_pending(independent_fd)
                native = records(independent_write)
                self.assertTrue(any(
                    wd == source_wd and mask == module.IN_MODIFY
                    for wd, mask, name in native
                ))
                self.assertTrue(any(
                    wd == parent_wd and mask == module.IN_MODIFY
                    and name == b"sample"
                    for wd, mask, name in native
                ))
                write_verdict = module._evaluate(
                    module.BEFORE, module.AFTER, independent_write,
                    source_wd, True, False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(write_verdict["status"], "BLOCKED")
                self.assertIs(write_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    write_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(
                    module._read_receipt_pending(independent_fd), b""
                )

                # The FIRST matching native chmod now triggers exactly
                # one source IN_ATTRIB and automatic IN_IGNORED. The
                # watch was NOT previously consumed by content writes.
                os.chmod(sample, 0o640)
                self.assertEqual(stat.S_IMODE(os.lstat(sample).st_mode),
                                 0o640)
                oneshot_attributes = module._read_receipt_pending(oneshot_fd)
                self.assertEqual(records(oneshot_attributes), [
                    (oneshot_wd, module.IN_ATTRIB, b""),
                    (oneshot_wd, module.IN_IGNORED, b""),
                ])
                one_parse = module._classify_stream(
                    oneshot_attributes, oneshot_wd
                )
                self.assertTrue(one_parse["invalidated"])
                self.assertEqual(one_parse["source_attribute_events"], 1)
                self.assertEqual(one_parse["source_modify_events"], 0)
                one_verdict = module._evaluate(
                    module.BEFORE, module.AFTER, oneshot_attributes,
                    oneshot_wd, True, False,
                )
                self.assertEqual(one_verdict["status"], "BLOCKED")
                self.assertIs(one_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    one_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(
                    module._read_receipt_pending(oneshot_fd), b""
                )

                full_attributes = module._read_receipt_pending(independent_fd)
                observed_attributes = records(full_attributes)
                self.assertIn(
                    (source_wd, module.IN_ATTRIB, b""),
                    observed_attributes
                )
                self.assertIn(
                    (parent_wd, module.IN_ATTRIB, b"sample"),
                    observed_attributes
                )
                self.assertFalse(any(
                    mask == module.IN_IGNORED
                    for wd, mask, name in observed_attributes
                ))
                attributes_verdict = module._evaluate(
                    module.BEFORE, module.AFTER, full_attributes,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(attributes_verdict["status"], "BLOCKED")
                self.assertIs(
                    attributes_verdict["can_authorize_dispatch"], False
                )
                self.assertIs(
                    attributes_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(
                    module._read_receipt_pending(independent_fd), b""
                )

                # After disarm, restoring chmod and public file bytes
                # cannot generate any new one-shot events; independent
                # native watcher still reports the real actions.
                os.chmod(sample, 0o600)
                self.assertEqual(module._read_receipt_pending(oneshot_fd), b"")
                restored_attributes = records(
                    module._read_receipt_pending(independent_fd)
                )
                self.assertIn(
                    (source_wd, module.IN_ATTRIB, b""),
                    restored_attributes
                )
                self.assertIn(
                    (parent_wd, module.IN_ATTRIB, b"sample"),
                    restored_attributes
                )
                write_sample(sample, module.BEFORE)
                self.assertEqual(module._read_receipt_pending(oneshot_fd), b"")
                restored_write = module._read_receipt_pending(independent_fd)
                self.assertGreaterEqual(module._classify_stream(
                    restored_write, source_wd, parent_wd
                )["source_modify_events"], 1)
                final_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, restored_write,
                    source_wd, True, False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",),
                )
                self.assertEqual(final_verdict["status"], "BLOCKED")
                self.assertIs(final_verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    final_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(
                    module._read_receipt_pending(independent_fd), b""
                )

                final = os.lstat(sample)
                parent_final = os.lstat(sample.parent)
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (original.st_dev, original.st_ino, original.st_mode),
                )
                self.assertEqual(
                    (parent_final.st_dev, parent_final.st_ino,
                     parent_final.st_mode),
                    (parent_initial.st_dev, parent_initial.st_ino,
                     parent_initial.st_mode),
                )
                self.assertEqual(
                    module._bounded_inventory_names(sample.parent),
                    ("sample",)
                )
            finally:
                if sample.exists():
                    os.chmod(sample, 0o600)
                for fd in (oneshot_fd, independent_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
