from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1232", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
IN_ONESHOT = 0x80000000
FALLOC_FL_COLLAPSE_RANGE = 0x08

@unittest.skipUnless(sys.platform == "linux", "native Linux inotify required")
class NativeCollapsePrefixTwice(unittest.TestCase):
    def test_two_collapse_prefix_operations_delete_first_two_pages(self):
        original_fd = normal_fd = writer_fd = restore_fd = None
        before = b"A"*4096 + b"B"*4096 + b"C"*4096
        after_one = b"B"*4096 + b"C"*4096
        after_two = b"C"*4096
        after = after_two

        def parse(data):
            self.assertIs(type(data), bytes)
            result=[]
            offset=0
            while offset<len(data):
                self.assertGreaterEqual(len(data)-offset,module.EVENT.size)
                wd,mask,cookie,nbytes=module.EVENT.unpack_from(data,offset)
                offset+=module.EVENT.size
                self.assertLessEqual(nbytes,len(data)-offset)
                name=data[offset:offset+nbytes].split(b"\x00",1)[0]
                offset+=nbytes
                self.assertEqual(cookie,0)
                result.append((wd,mask,name))
            self.assertEqual(offset,len(data))
            return result

        with tempfile.TemporaryDirectory(prefix="dec1232-public-collapse-range-at-offset-zero-",dir="/tmp") as tmp:
            parent=Path(tmp)
            sample=parent/"sample"
            self.assertEqual(sample.write_bytes(before),len(before))
            first=(os.lstat(sample),os.lstat(parent))
            self.assertEqual(module._bounded_inventory_names(parent),("sample",))
            try:
                normal_fd,source_wd,parent_wd=module._start_watch(sample)
                libc=ctypes.CDLL(None,use_errno=True)
                libc.inotify_init1.argtypes=[ctypes.c_int]
                libc.inotify_init1.restype=ctypes.c_int
                libc.inotify_add_watch.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_uint32]
                libc.inotify_add_watch.restype=ctypes.c_int
                libc.fallocate.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_longlong,ctypes.c_longlong]
                libc.fallocate.restype=ctypes.c_int
                original_fd=libc.inotify_init1(os.O_NONBLOCK|os.O_CLOEXEC)
                self.assertGreaterEqual(original_fd,0)
                original_wd=libc.inotify_add_watch(
                    original_fd,module._checked_watch_path_bytes(sample),
                    module.IN_MODIFY|module.IN_CLOSE_WRITE|module.IN_DONT_FOLLOW|IN_ONESHOT)
                self.assertGreater(original_wd,0)
                self.assertNotEqual(original_fd,normal_fd)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                writer_fd=os.open(sample,os.O_WRONLY|os.O_CLOEXEC)
                for iteration in (1,2):
                    self.assertEqual(libc.fallocate(
                        writer_fd,FALLOC_FL_COLLAPSE_RANGE,
                        0,4096),0,os.strerror(ctypes.get_errno()))
                    self.assertEqual(os.fstat(writer_fd).st_size,
                        len(after_one) if iteration==1 else len(after_two))
                    receipt=module._read_receipt_pending(normal_fd)
                    self.assertCountEqual(
                        parse(receipt),
                        [(source_wd,module.IN_MODIFY,b""),
                         (parent_wd,module.IN_MODIFY,b"sample")])
                    verdict=module._evaluate(
                        before if iteration==1 else after_one,
                        after_one if iteration==1 else after_two,
                        receipt,source_wd,True,False,
                        directory_watch=parent_wd,
                        directory_inventory_names=("sample",))
                    self.assertEqual(verdict["status"],"BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"],False)
                    self.assertIs(verdict["independent_os_proof_verified"],False)
                    if iteration==1:
                        self.assertEqual(parse(module._read_receipt_pending(original_fd)),
                            [(original_wd,module.IN_MODIFY,b""),
                             (original_wd,module.IN_IGNORED,b"")])
                    else:
                        self.assertEqual(module._read_receipt_pending(original_fd),b"")
                    self.assertEqual(sample.read_bytes(),
                        after_one if iteration==1 else after_two)
                    self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                os.close(writer_fd)
                writer_fd=None
                self.assertCountEqual(parse(module._read_receipt_pending(normal_fd)),
                    [(source_wd,module.IN_CLOSE_WRITE,b""),
                     (parent_wd,module.IN_CLOSE_WRITE,b"sample")])
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                restore_fd=os.open(sample,os.O_WRONLY|os.O_TRUNC|os.O_CLOEXEC)
                self.assertEqual(os.write(restore_fd,before),len(before))
                os.fsync(restore_fd)
                os.close(restore_fd)
                restore_fd=None
                receipt=module._read_receipt_pending(normal_fd)
                observed=parse(receipt)
                required={(source_wd,module.IN_MODIFY,b""),
                          (parent_wd,module.IN_MODIFY,b"sample"),
                          (source_wd,module.IN_CLOSE_WRITE,b""),
                          (parent_wd,module.IN_CLOSE_WRITE,b"sample")}
                self.assertTrue(observed)
                self.assertTrue(all(row in required for row in observed))
                self.assertTrue(required.issubset(set(observed)))
                result=module._evaluate(after,before,receipt,source_wd,True,False,
                    directory_watch=parent_wd,directory_inventory_names=("sample",))
                self.assertEqual(result["status"],"BLOCKED")
                self.assertIs(result["can_authorize_dispatch"],False)
                self.assertIs(result["independent_os_proof_verified"],False)
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                final=(os.lstat(sample),os.lstat(parent))
                for old,new in zip(first,final):
                    self.assertEqual((old.st_dev,old.st_ino,old.st_mode,old.st_nlink),
                                     (new.st_dev,new.st_ino,new.st_mode,new.st_nlink))
                self.assertEqual(sample.read_bytes(),before)
                self.assertEqual(module._bounded_inventory_names(parent),("sample",))
            finally:
                for fd in (writer_fd,restore_fd,original_fd,normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
