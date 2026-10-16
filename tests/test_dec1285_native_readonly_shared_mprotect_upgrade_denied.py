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
spec=importlib.util.spec_from_file_location("dec677_native_dec1285",SCRIPT)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
IN_ONESHOT=0x80000000


@unittest.skipUnless(sys.platform=="linux","Linux inotify and mmap required")
class NativeReadonlySharedMprotectWriteUpgradeDenial(unittest.TestCase):
    def test_readonly_shared_mapping_mprotect_upgrade_eacces_then_independent_writes(self):
        normal_fd=original_fd=reader_fd=writer_fd=None
        mapped_address=None
        page_size=mmap.PAGESIZE
        before=module.BEFORE
        changed=b"XXXXX"+before[5:]
        self.assertNotEqual(before,changed)

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
            prefix="dec1285-public-read-map-writer-",dir="/tmp"
        ) as tmp:
            parent=Path(tmp);sample=parent/"sample"
            self.assertEqual(sample.write_bytes(before),len(before))
            source_before=os.lstat(sample);parent_before=os.lstat(parent)
            try:
                normal_fd,source_wd,parent_wd=module._start_watch(sample)
                libc=ctypes.CDLL(None,use_errno=True)
                libc.inotify_init1.argtypes=[ctypes.c_int]
                libc.inotify_init1.restype=ctypes.c_int
                libc.inotify_add_watch.argtypes=[
                    ctypes.c_int,ctypes.c_char_p,ctypes.c_uint32]
                libc.inotify_add_watch.restype=ctypes.c_int
                original_fd=libc.inotify_init1(os.O_NONBLOCK|os.O_CLOEXEC)
                self.assertGreaterEqual(original_fd,0)
                original_wd=libc.inotify_add_watch(
                    original_fd,module._checked_watch_path_bytes(sample),
                    module.IN_MODIFY|module.IN_CLOSE_WRITE|
                    module.IN_DONT_FOLLOW|IN_ONESHOT)
                self.assertGreater(original_wd,0)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                reader_fd=os.open(sample,os.O_RDONLY|os.O_CLOEXEC)
                # Native MAP_SHARED read-only mapping of a true
                # O_RDONLY descriptor. mprotect cannot upgrade it
                # to writable, because the original FD lacks write.
                libc.mmap.argtypes=[
                    ctypes.c_void_p,ctypes.c_size_t,ctypes.c_int,
                    ctypes.c_int,ctypes.c_int,ctypes.c_longlong]
                libc.mmap.restype=ctypes.c_void_p
                libc.mprotect.argtypes=[
                    ctypes.c_void_p,ctypes.c_size_t,ctypes.c_int]
                libc.mprotect.restype=ctypes.c_int
                libc.munmap.argtypes=[ctypes.c_void_p,ctypes.c_size_t]
                libc.munmap.restype=ctypes.c_int
                ctypes.set_errno(0)
                mapped_address=libc.mmap(
                    None,page_size,mmap.PROT_READ,mmap.MAP_SHARED,
                    reader_fd,0)
                self.assertNotIn(
                    mapped_address,(None,ctypes.c_void_p(-1).value))
                self.assertEqual(
                    ctypes.string_at(mapped_address,len(before)),before)
                ctypes.set_errno(0)
                self.assertEqual(
                    libc.mprotect(mapped_address,page_size,
                                  mmap.PROT_READ|mmap.PROT_WRITE),-1)
                self.assertEqual(ctypes.get_errno(),errno.EACCES)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                with self.assertRaises(OSError) as denied:
                    os.ftruncate(reader_fd,0)
                self.assertEqual(denied.exception.errno,errno.EBADF)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")

                # An independent genuinely writable FD modifies the
                # original inode and existing read-only shared map
                # reflects the changed backing bytes WITHOUT remap.
                writer_fd=os.open(sample,os.O_WRONLY|os.O_CLOEXEC)
                self.assertEqual(os.pwrite(writer_fd,b"XXXXX",0),5)
                self.assertEqual(ctypes.string_at(mapped_address,len(before)),changed)
                self.assertEqual(os.pread(reader_fd,len(before),0),changed)
                real_receipt=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    rows(real_receipt),
                    [(source_wd,module.IN_MODIFY,b""),
                     (parent_wd,module.IN_MODIFY,b"sample")])
                self.assertEqual(
                    rows(module._read_receipt_pending(original_fd)),
                    [(original_wd,module.IN_MODIFY,b""),
                     (original_wd,module.IN_IGNORED,b"")])
                result=module._evaluate(
                    before,changed,real_receipt,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(result["status"],"BLOCKED")
                self.assertIs(result["can_authorize_dispatch"],False)
                self.assertIs(result["independent_os_proof_verified"],False)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")

                # Same already mapped read-only memory immediately
                # reflects restored actual original public bytes.
                self.assertEqual(os.pwrite(writer_fd,before[:5],0),5)
                self.assertEqual(ctypes.string_at(mapped_address,len(before)),before)
                self.assertEqual(os.pread(reader_fd,len(before),0),before)
                restore_receipt=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    rows(restore_receipt),
                    [(source_wd,module.IN_MODIFY,b""),
                     (parent_wd,module.IN_MODIFY,b"sample")])
                restored=module._evaluate(
                    changed,before,restore_receipt,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(restored["status"],"BLOCKED")
                self.assertIs(restored["can_authorize_dispatch"],False)
                self.assertIs(
                    restored["independent_os_proof_verified"],False)
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                self.assertEqual(libc.munmap(mapped_address,page_size),0)
                mapped_address=None
                os.close(reader_fd);reader_fd=None
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")

                os.close(writer_fd);writer_fd=None
                self.assertCountEqual(
                    rows(module._read_receipt_pending(normal_fd)),
                    [(source_wd,module.IN_CLOSE_WRITE,b""),
                     (parent_wd,module.IN_CLOSE_WRITE,b"sample")])
                for old,new in ((source_before,os.lstat(sample)),
                                (parent_before,os.lstat(parent))):
                    self.assertEqual(
                        (old.st_dev,old.st_ino,old.st_mode,old.st_nlink),
                        (new.st_dev,new.st_ino,new.st_mode,new.st_nlink))
                self.assertEqual(sample.read_bytes(),before)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
            finally:
                if mapped_address is not None:
                    self.assertEqual(libc.munmap(mapped_address,page_size),0)
                for fd in (reader_fd,writer_fd,original_fd,normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):os.fstat(fd)
