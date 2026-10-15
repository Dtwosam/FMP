from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1214", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
IN_ONESHOT = 0x80000000
FALLOC_FL_KEEP_SIZE = 0x01

@unittest.skipUnless(sys.platform == "linux", "Linux native inotify required")
class NativeFallocateKeepSizeFarBeyondEof(unittest.TestCase):
    def test_two_keep_size_allocations_beyond_eof_emit_modify_but_preserve_size(self):
        original_fd = normal_fd = writer_fd = restore_fd = None

        def rows(data):
            self.assertIs(type(data), bytes)
            output = []
            offset = 0
            while offset < len(data):
                self.assertGreaterEqual(len(data)-offset, module.EVENT.size)
                wd, mask, cookie, nbytes = module.EVENT.unpack_from(data, offset)
                offset += module.EVENT.size
                self.assertLessEqual(nbytes, len(data)-offset)
                name = data[offset:offset+nbytes].split(b"\x00", 1)[0]
                offset += nbytes
                self.assertEqual(cookie, 0)
                output.append((wd,mask,name))
            self.assertEqual(offset, len(data))
            return output

        before = module.BEFORE
        at = before.index(b"SOURCE")
        changed = before[:at] + b"X" + before[at+1:]
        with tempfile.TemporaryDirectory(prefix="dec1214-public-keep-size-",dir="/tmp") as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(before),len(before))
            first = (os.lstat(sample),os.lstat(parent))
            self.assertEqual(module._bounded_inventory_names(parent),("sample",))
            try:
                normal_fd, source_wd, parent_wd = module._start_watch(sample)
                libc = ctypes.CDLL(None,use_errno=True)
                libc.inotify_init1.argtypes=[ctypes.c_int]
                libc.inotify_init1.restype=ctypes.c_int
                libc.inotify_add_watch.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_uint32]
                libc.inotify_add_watch.restype=ctypes.c_int
                libc.fallocate.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_longlong,ctypes.c_longlong]
                libc.fallocate.restype=ctypes.c_int
                original_fd = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
                self.assertGreaterEqual(original_fd,0)
                original_wd = libc.inotify_add_watch(
                    original_fd,module._checked_watch_path_bytes(sample),
                    module.IN_MODIFY | module.IN_CLOSE_WRITE | module.IN_DONT_FOLLOW | IN_ONESHOT)
                self.assertGreater(original_wd,0)
                self.assertNotEqual(normal_fd,original_fd)
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                writer_fd = os.open(sample,os.O_WRONLY | os.O_CLOEXEC)

                for iteration in (1,2):
                    self.assertEqual(
                        libc.fallocate(writer_fd,FALLOC_FL_KEEP_SIZE,8192,4096),
                        0,os.strerror(ctypes.get_errno()))
                    self.assertEqual(os.fstat(writer_fd).st_size,len(before))
                    receipt = module._read_receipt_pending(normal_fd)
                    self.assertCountEqual(
                        rows(receipt),
                        [(source_wd,module.IN_MODIFY,b""),
                         (parent_wd,module.IN_MODIFY,b"sample")])
                    verdict=module._evaluate(
                        before,before,receipt,source_wd,True,False,
                        directory_watch=parent_wd,
                        directory_inventory_names=("sample",))
                    self.assertEqual(verdict["status"],"BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"],False)
                    self.assertIs(verdict["independent_os_proof_verified"],False)
                    if iteration == 1:
                        self.assertEqual(
                            rows(module._read_receipt_pending(original_fd)),
                            [(original_wd,module.IN_MODIFY,b""),
                             (original_wd,module.IN_IGNORED,b"")])
                    else:
                        self.assertEqual(module._read_receipt_pending(original_fd),b"")
                    self.assertEqual(sample.read_bytes(),before)
                    self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                os.close(writer_fd)
                writer_fd = None
                self.assertCountEqual(
                    rows(module._read_receipt_pending(normal_fd)),
                    [(source_wd,module.IN_CLOSE_WRITE,b""),
                     (parent_wd,module.IN_CLOSE_WRITE,b"sample")])
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                # Genuine changed and restoring writes prove continuation.
                for payload,old in ((changed,before),(before,changed)):
                    restore_fd=os.open(sample,os.O_WRONLY | os.O_TRUNC | os.O_CLOEXEC)
                    self.assertEqual(os.write(restore_fd,payload),len(payload))
                    os.fsync(restore_fd)
                    os.close(restore_fd)
                    restore_fd=None
                    receipt=module._read_receipt_pending(normal_fd)
                    observed=rows(receipt)
                    allowed={(source_wd,module.IN_MODIFY,b""),
                             (parent_wd,module.IN_MODIFY,b"sample"),
                             (source_wd,module.IN_CLOSE_WRITE,b""),
                             (parent_wd,module.IN_CLOSE_WRITE,b"sample")}
                    self.assertTrue(observed)
                    self.assertTrue(all(x in allowed for x in observed))
                    self.assertTrue(allowed.issubset(set(observed)))
                    verdict=module._evaluate(old,payload,receipt,source_wd,True,False,
                         directory_watch=parent_wd,directory_inventory_names=("sample",))
                    self.assertEqual(verdict["status"],"BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"],False)
                    self.assertIs(verdict["independent_os_proof_verified"],False)
                    self.assertEqual(module._read_receipt_pending(original_fd),b"")
                    self.assertEqual(sample.read_bytes(),payload)
                    self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                final=(os.lstat(sample),os.lstat(parent))
                for a,b in zip(first,final):
                    self.assertEqual((a.st_dev,a.st_ino,a.st_mode,a.st_nlink),
                                     (b.st_dev,b.st_ino,b.st_mode,b.st_nlink))
                self.assertEqual(sample.read_bytes(),before)
                self.assertEqual(module._bounded_inventory_names(parent),("sample",))
            finally:
                for fd in (writer_fd,restore_fd,original_fd,normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
