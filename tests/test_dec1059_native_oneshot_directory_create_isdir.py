from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1059", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeParentDirectoryCreateOneShotRegression(unittest.TestCase):
    def test_one_shot_create_directory_has_isdir_then_ignored_and_misses_rmdir(self):
        one_fd = None
        witness_fd = None

        def records(stream):
            self.assertIs(type(stream), bytes)
            pos = 0
            result = []
            while pos < len(stream):
                self.assertGreaterEqual(len(stream) - pos, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(stream, pos)
                pos += module.EVENT.size
                self.assertLessEqual(nbytes, len(stream) - pos)
                name = stream[pos:pos + nbytes].split(b"\x00", 1)[0]
                pos += nbytes
                self.assertEqual(cookie, 0)
                result.append((wd, mask, name))
            self.assertEqual(pos, len(stream))
            return result

        def sample_write(path, payload):
            with path.open("r+b") as writer:
                self.assertEqual(writer.write(payload), len(payload))
                writer.truncate()
                writer.flush()
                os.fsync(writer.fileno())

        with tempfile.TemporaryDirectory(
            prefix="dec1059-public-parent-mkdir-oneshot-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            directory = parent / "public-created-dir"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            initial = os.lstat(sample)
            parent_initial = os.lstat(parent)
            self.assertEqual(module._bounded_inventory_names(parent), ("sample",))
            try:
                witness_fd, source_wd, parent_wd = module._start_watch(sample)
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                one_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreater(one_fd, 2)
                oneshot_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(parent),
                    module.IN_CREATE | module.IN_ONLYDIR |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(oneshot_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(witness_fd), b"")

                # Genuine sample writes do not match parent CREATE.
                # Original one-shot stays armed until first mkdir.
                for content in (module.AFTER, module.BEFORE):
                    sample_write(sample, content)
                    self.assertEqual(module._read_receipt_pending(one_fd), b"")
                    observed = module._read_receipt_pending(witness_fd)
                    events = records(observed)
                    self.assertTrue(any(
                        wd == source_wd and mask == module.IN_MODIFY
                        for wd, mask, name in events
                    ))
                    self.assertTrue(any(
                        wd == parent_wd and mask == module.IN_MODIFY
                        and name == b"sample"
                        for wd, mask, name in events
                    ))
                    verdict = module._evaluate(
                        module.BEFORE, content, observed, source_wd,
                        True, False, directory_watch=parent_wd,
                        directory_inventory_names=("sample",)
                    )
                    self.assertEqual(verdict["status"], "BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"], False)
                    self.assertIs(
                        verdict["independent_os_proof_verified"], False
                    )
                    self.assertEqual(module._read_receipt_pending(witness_fd), b"")

                # A real mkdir is the first MATCHING parent action.
                # Kernel reports IN_ISDIR on the event and then
                # auto-destroys the one-shot watch with IN_IGNORED.
                directory.mkdir()
                self.assertTrue(directory.is_dir())
                self.assertEqual(records(
                    module._read_receipt_pending(one_fd)
                ), [
                    (oneshot_wd, module.IN_CREATE | module.IN_ISDIR,
                     b"public-created-dir"),
                    (oneshot_wd, module.IN_IGNORED, b""),
                ])
                self.assertEqual(module._read_receipt_pending(one_fd), b"")

                create_stream = module._read_receipt_pending(witness_fd)
                create_events = records(create_stream)
                self.assertIn(
                    (parent_wd, module.IN_CREATE | module.IN_ISDIR,
                     b"public-created-dir"),
                    create_events
                )
                self.assertFalse(any(
                    mask == module.IN_IGNORED
                    for wd, mask, name in create_events
                ))
                parsed = module._classify_stream(
                    create_stream, source_wd, parent_wd
                )
                self.assertTrue(parsed["well_formed"])
                self.assertFalse(parsed["invalidated"])
                self.assertGreaterEqual(parsed["directory_changes"], 1)
                create_verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, create_stream,
                    source_wd, True, False, directory_watch=parent_wd,
                    directory_inventory_names=("public-created-dir", "sample"),
                )
                self.assertEqual(create_verdict["status"], "BLOCKED")
                self.assertIs(
                    create_verdict["can_authorize_dispatch"], False
                )
                self.assertIs(
                    create_verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(witness_fd), b"")

                # The original directory creation is undone, but
                # the disarmed CREATE one-shot cannot see the rmdir.
                directory.rmdir()
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                delete_events = records(
                    module._read_receipt_pending(witness_fd)
                )
                self.assertIn(
                    (parent_wd, module.IN_DELETE | module.IN_ISDIR,
                     b"public-created-dir"),
                    delete_events
                )
                self.assertEqual(module._read_receipt_pending(witness_fd), b"")

                # A second genuine mkdir/rmdir is also invisible to
                # the dead one-shot, not to the independent parent.
                directory.mkdir()
                directory.rmdir()
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                later = records(module._read_receipt_pending(witness_fd))
                self.assertIn(
                    (parent_wd, module.IN_CREATE | module.IN_ISDIR,
                     b"public-created-dir"),
                    later
                )
                self.assertIn(
                    (parent_wd, module.IN_DELETE | module.IN_ISDIR,
                     b"public-created-dir"),
                    later
                )
                self.assertEqual(module._read_receipt_pending(witness_fd), b"")

                final = os.lstat(sample)
                parent_final = os.lstat(parent)
                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual(
                    (final.st_dev, final.st_ino, final.st_mode),
                    (initial.st_dev, initial.st_ino, initial.st_mode),
                )
                self.assertEqual(
                    (parent_final.st_dev, parent_final.st_ino,
                     parent_final.st_mode),
                    (parent_initial.st_dev, parent_initial.st_ino,
                     parent_initial.st_mode),
                )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
            finally:
                for fd in (one_fd, witness_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
