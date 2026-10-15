from __future__ import annotations

import ctypes
import errno
import importlib.util
import mmap
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/"scripts/dec677_disposable_inotify_events.py"
spec=importlib.util.spec_from_file_location("dec677_native_dec1277",SCRIPT)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
IN_ONESHOT=0x80000000


@unittest.skipUnless(sys.platform=="linux","Linux native inotify and mmap required")
class NativeWriteOnlyMmapRejectedButFallocateMutates(unittest.TestCase):
    def test_writeonly_fd_rejects_three_mmap_modes_but_zero_range_is_mutating(self):
        normal_fd=original_fd=writer_fd=None
        before=module.BEFORE
        zeroed=b"\x00"*5+before[5:]
        self.assertNotEqual(before,zeroed)

        def rows(data):
            self.assertIs(type(data),bytes)
            out=[];pos=0
            while pos<len(data):
                self.assertGreaterEqual(len(data)-pos,module.EVENT.size)
                wd,mask,cookie,n=module.EVENT.unpack_from(data,pos)
                pos+=module.EVENT.size
                self.assertLessEqual(n,len(data)-pos)
                name=data[pos:pos+n].split(b"\x00",1)[0];pos+=n
                self.assertEqual(cookie,0)
                out.append((wd,mask,name))
            self.assertEqual(pos,len(data))
            return out

        with tempfile.TemporaryDirectory(
            prefix="dec1277-public-writeonly-mmap-denied-",dir="/tmp"
        ) as tmp:
            parent=Path(tmp);sample=parent/"sample"
            self.assertEqual(sample.write_bytes(before),len(before))
            original_source=os.lstat(sample)
            original_parent=os.lstat(parent)
            try:
                normal_fd,source_wd,parent_wd=module._start_watch(sample)
                libc=ctypes.CDLL(None,use_errno=True)
                libc.inotify_init1.argtypes=[ctypes.c_int]
                libc.inotify_init1.restype=ctypes.c_int
                libc.inotify_add_watch.argtypes=[
                    ctypes.c_int,ctypes.c_char_p,ctypes.c_uint32]
                libc.inotify_add_watch.restype=ctypes.c_int
                libc.fallocate.argtypes=[
                    ctypes.c_int,ctypes.c_int,
                    ctypes.c_longlong,ctypes.c_longlong]
                libc.fallocate.restype=ctypes.c_int
                original_fd=libc.inotify_init1(os.O_NONBLOCK|os.O_CLOEXEC)
                self.assertGreaterEqual(original_fd,0)
                original_wd=libc.inotify_add_watch(
                    original_fd,module._checked_watch_path_bytes(sample),
                    module.IN_MODIFY|module.IN_CLOSE_WRITE|
                    module.IN_DONT_FOLLOW|IN_ONESHOT)
                self.assertGreater(original_wd,0)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                writer_fd=os.open(sample,os.O_WRONLY|os.O_CLOEXEC)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                for access in (
                    mmap.ACCESS_READ,mmap.ACCESS_COPY,mmap.ACCESS_WRITE
                ):
                    with self.assertRaises(OSError) as rejected:
                        mmap.mmap(writer_fd,len(before),access=access)
                    self.assertEqual(rejected.exception.errno,errno.EACCES)
                    self.assertEqual(os.fstat(writer_fd).st_size,len(before))
                    self.assertEqual(sample.read_bytes(),before)
                    self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                    self.assertEqual(module._read_receipt_pending(original_fd),b"")

                # Rejected mmap requests prove only mmap requires
                # access including read permission; genuine native
                # fallocate can still modify through O_WRONLY.
                self.assertEqual(
                    libc.fallocate(writer_fd,0x11,0,5),0,
                    os.strerror(ctypes.get_errno()))
                self.assertEqual(os.fstat(writer_fd).st_size,len(before))
                self.assertEqual(sample.read_bytes(),zeroed)
                modified_receipt=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    rows(modified_receipt),
                    [(source_wd,module.IN_MODIFY,b""),
                     (parent_wd,module.IN_MODIFY,b"sample")])
                self.assertEqual(
                    rows(module._read_receipt_pending(original_fd)),
                    [(original_wd,module.IN_MODIFY,b""),
                     (original_wd,module.IN_IGNORED,b"")])
                result=module._evaluate(
                    before,zeroed,modified_receipt,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(result["status"],"BLOCKED")
                self.assertIs(result["can_authorize_dispatch"],False)
                self.assertIs(result["independent_os_proof_verified"],False)

                # Repeat exact zero-range: byte-equal yet another
                # genuine native source+parent IN_MODIFY.
                self.assertEqual(
                    libc.fallocate(writer_fd,0x11,0,5),0,
                    os.strerror(ctypes.get_errno()))
                repeated_receipt=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    rows(repeated_receipt),
                    [(source_wd,module.IN_MODIFY,b""),
                     (parent_wd,module.IN_MODIFY,b"sample")])
                repeated=module._evaluate(
                    zeroed,zeroed,repeated_receipt,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(repeated["status"],"BLOCKED")
                self.assertIs(repeated["can_authorize_dispatch"],False)
                self.assertIs(
                    repeated["independent_os_proof_verified"],False)
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                # Restore generated PUBLIC bytes with actual write,
                # separately observed by the continuing helper.
                self.assertEqual(os.pwrite(writer_fd,before[:5],0),5)
                self.assertEqual(sample.read_bytes(),before)
                restore_receipt=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    rows(restore_receipt),
                    [(source_wd,module.IN_MODIFY,b""),
                     (parent_wd,module.IN_MODIFY,b"sample")])
                restore_verdict=module._evaluate(
                    zeroed,before,restore_receipt,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(restore_verdict["status"],"BLOCKED")
                self.assertIs(restore_verdict["can_authorize_dispatch"],False)
                self.assertIs(
                    restore_verdict["independent_os_proof_verified"],False)
                os.close(writer_fd);writer_fd=None
                self.assertCountEqual(
                    rows(module._read_receipt_pending(normal_fd)),
                    [(source_wd,module.IN_CLOSE_WRITE,b""),
                     (parent_wd,module.IN_CLOSE_WRITE,b"sample")])
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                for old,new in ((original_source,os.lstat(sample)),
                                (original_parent,os.lstat(parent))):
                    self.assertEqual(
                        (old.st_dev,old.st_ino,old.st_mode,old.st_nlink),
                        (new.st_dev,new.st_ino,new.st_mode,new.st_nlink))
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(sample.read_bytes(),before)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
            finally:
                for fd in (writer_fd,original_fd,normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):os.fstat(fd)
