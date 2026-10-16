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
spec=importlib.util.spec_from_file_location("dec677_native_dec1292",SCRIPT)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
IN_ONESHOT=0x80000000


@unittest.skipUnless(sys.platform=="linux","Linux inotify and mmap required")
class NativeSharedMprotectReupgradeAfterFdCloseRegression(unittest.TestCase):
    def test_shared_mprotect_reupgrade_after_closing_original_fd_mutates_inode(self):
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
            prefix="dec1292-public-read-map-writer-",dir="/tmp"
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

                # Native writable MAP_SHARED is established before
                # a page-only mprotect downgrade. This does NOT
                # change the file's on-disk inode permission mode.
                reader_fd=os.open(sample,os.O_RDWR|os.O_CLOEXEC)
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
                    None,page_size,mmap.PROT_READ|mmap.PROT_WRITE,
                    mmap.MAP_SHARED,reader_fd,0)
                self.assertNotIn(
                    mapped_address,(None,ctypes.c_void_p(-1).value))
                self.assertEqual(
                    ctypes.string_at(mapped_address,len(before)),before)
                self.assertEqual(
                    libc.mprotect(mapped_address,page_size,mmap.PROT_READ),0)
                self.assertEqual(
                    ctypes.string_at(mapped_address,len(before)),before)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                # Close original O_RDWR FD before re-upgrading.
                # Native CLOSE_WRITE is DEFERRED while the shared
                # mapping still owns the backing-file reference.
                os.close(reader_fd);reader_fd=None
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                # Re-upgrading remains possible after the writer FD
                # has closed: the mapping retained writable capability
                # from when it was originally established.
                self.assertEqual(
                    libc.mprotect(mapped_address,page_size,
                                  mmap.PROT_READ|mmap.PROT_WRITE),0)
                ctypes.memmove(mapped_address,b"XXXXX",5)
                self.assertEqual(
                    ctypes.string_at(mapped_address,len(before)),changed)
                self.assertEqual(sample.read_bytes(),changed)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                first=module._evaluate(
                    before,changed,b"",source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(first["status"],"BLOCKED")
                self.assertIs(first["can_authorize_dispatch"],False)
                self.assertIs(first["independent_os_proof_verified"],False)

                ctypes.memmove(mapped_address,before[:5],5)
                self.assertEqual(
                    ctypes.string_at(mapped_address,len(before)),before)
                self.assertEqual(sample.read_bytes(),before)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                restored=module._evaluate(
                    changed,before,b"",source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(restored["status"],"BLOCKED")
                self.assertIs(restored["can_authorize_dispatch"],False)
                self.assertIs(
                    restored["independent_os_proof_verified"],False)

                # Final shared-mapping unmap, not earlier os.close,
                # now releases the LAST backing writable reference.
                # It produces source+parent CLOSE_WRITE and expires
                # isolated unsafe test-only ONESHOT only at the end.
                self.assertEqual(libc.munmap(mapped_address,page_size),0)
                mapped_address=None
                self.assertCountEqual(
                    rows(module._read_receipt_pending(normal_fd)),
                    [(source_wd,module.IN_CLOSE_WRITE,b""),
                     (parent_wd,module.IN_CLOSE_WRITE,b"sample")])
                self.assertEqual(
                    rows(module._read_receipt_pending(original_fd)),
                    [(original_wd,module.IN_CLOSE_WRITE,b""),
                     (original_wd,module.IN_IGNORED,b"")])

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
