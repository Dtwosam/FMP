from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1055", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux", "native Linux directory rename required")
class NativeOneShotDirectoryRenameRegression(unittest.TestCase):
    def test_one_shot_parent_sees_only_isdir_moved_from_with_ignored(self):
        one_fd = None
        witness_fd = None

        def records(raw):
            self.assertIs(type(raw), bytes)
            out = []
            pos = 0
            while pos < len(raw):
                self.assertGreaterEqual(len(raw) - pos, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(raw, pos)
                pos += module.EVENT.size
                self.assertLessEqual(nbytes, len(raw) - pos)
                name = raw[pos:pos + nbytes].split(b"\x00", 1)[0]
                pos += nbytes
                out.append((wd, mask, cookie, name))
            self.assertEqual(pos, len(raw))
            return out

        def paired(stream, parent_wd, old_name, new_name):
            native = records(stream)
            src = [(i, cookie) for i, (wd, mask, cookie, name)
                   in enumerate(native)
                   if (wd, mask, name) == (
                       parent_wd, module.IN_MOVED_FROM | module.IN_ISDIR,
                       old_name,
                   )]
            dst = [(i, cookie) for i, (wd, mask, cookie, name)
                   in enumerate(native)
                   if (wd, mask, name) == (
                       parent_wd, module.IN_MOVED_TO | module.IN_ISDIR,
                       new_name,
                   )]
            self.assertEqual(len(src), 1)
            self.assertEqual(len(dst), 1)
            self.assertGreater(src[0][1], 0)
            self.assertEqual(src[0][1], dst[0][1])
            self.assertLess(src[0][0], dst[0][0])
            return src[0][1]

        with tempfile.TemporaryDirectory(
            prefix="dec1055-public-oneshot-isdir-", dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            first_dir = parent / "public-alpha"
            second_dir = parent / "public-beta"
            self.assertEqual(sample.write_bytes(module.BEFORE), len(module.BEFORE))
            first_dir.mkdir()
            marker = first_dir / "public-marker"
            self.assertEqual(marker.write_bytes(b"PUBLIC-DIR-MARKER"),
                             len(b"PUBLIC-DIR-MARKER"))
            original = os.lstat(sample)
            original_parent = os.lstat(parent)
            original_dir = os.lstat(first_dir)
            marker_initial = os.lstat(marker)
            self.assertEqual(module._bounded_inventory_names(parent),
                             ("public-alpha", "sample"))
            try:
                witness_fd, source_wd, witness_parent_wd = (
                    module._start_watch(sample)
                )
                libc = ctypes.CDLL(None, use_errno=True)
                libc.inotify_init1.argtypes = [ctypes.c_int]
                libc.inotify_init1.restype = ctypes.c_int
                libc.inotify_add_watch.argtypes = [
                    ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32,
                ]
                libc.inotify_add_watch.restype = ctypes.c_int
                one_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreater(one_fd, 2)
                one_parent_wd = libc.inotify_add_watch(
                    one_fd, module._checked_watch_path_bytes(parent),
                    module.IN_MOVED_FROM | module.IN_ONLYDIR |
                    module.IN_DONT_FOLLOW | IN_ONESHOT,
                )
                self.assertGreater(one_parent_wd, 0)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                self.assertEqual(module._read_receipt_pending(witness_fd), b"")

                # A *directory* rename must carry IN_ISDIR on BOTH
                # independent native parent rename records. The one-
                # shot sees only its first matching MOVED_FROM action.
                os.rename(first_dir, second_dir)
                truncated = records(module._read_receipt_pending(one_fd))
                self.assertEqual(len(truncated), 2)
                self.assertEqual(
                    (truncated[0][0], truncated[0][1], truncated[0][3]),
                    (one_parent_wd,
                     module.IN_MOVED_FROM | module.IN_ISDIR,
                     b"public-alpha"),
                )
                self.assertGreater(truncated[0][2], 0)
                self.assertEqual(truncated[1],
                                 (one_parent_wd, module.IN_IGNORED, 0, b""))
                self.assertFalse(any(
                    mask & module.IN_MOVED_TO
                    for wd, mask, cookie, name in truncated
                ))
                self.assertEqual(module._read_receipt_pending(one_fd), b"")

                full = module._read_receipt_pending(witness_fd)
                original_cookie = paired(
                    full, witness_parent_wd, b"public-alpha", b"public-beta"
                )
                self.assertEqual(original_cookie, truncated[0][2])
                classified = module._classify_stream(
                    full, source_wd, witness_parent_wd
                )
                self.assertTrue(classified["well_formed"])
                self.assertFalse(classified["invalidated"])
                self.assertGreaterEqual(classified["directory_changes"], 2)
                verdict = module._evaluate(
                    module.BEFORE, module.BEFORE, full, source_wd,
                    True, False, directory_watch=witness_parent_wd,
                    directory_inventory_names=("public-beta", "sample"),
                )
                self.assertEqual(verdict["status"], "BLOCKED")
                self.assertIs(verdict["can_authorize_dispatch"], False)
                self.assertIs(
                    verdict["independent_os_proof_verified"], False
                )
                self.assertEqual(module._read_receipt_pending(witness_fd), b"")

                # Restore the same directory inode/name with a real
                # second rename. Disarmed one-shot remains silent.
                os.rename(second_dir, first_dir)
                self.assertEqual(module._read_receipt_pending(one_fd), b"")
                back = module._read_receipt_pending(witness_fd)
                paired(back, witness_parent_wd,
                       b"public-beta", b"public-alpha")
                self.assertTrue(module._classify_stream(
                    back, source_wd, witness_parent_wd
                )["well_formed"])
                self.assertEqual(module._read_receipt_pending(witness_fd), b"")

                self.assertEqual(sample.read_bytes(), module.BEFORE)
                self.assertEqual((first_dir / "public-marker").read_bytes(),
                                 b"PUBLIC-DIR-MARKER")
                final = os.lstat(sample)
                parent_final = os.lstat(parent)
                dir_final = os.lstat(first_dir)
                marker_final = os.lstat(first_dir / "public-marker")
                for before, after in (
                    (original, final),
                    (original_parent, parent_final),
                    (original_dir, dir_final),
                    (marker_initial, marker_final),
                ):
                    self.assertEqual(
                        (after.st_dev, after.st_ino, after.st_mode),
                        (before.st_dev, before.st_ino, before.st_mode),
                    )
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("public-alpha", "sample"))
            finally:
                for fd in (one_fd, witness_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
