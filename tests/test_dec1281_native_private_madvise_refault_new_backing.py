from __future__ import annotations

import ctypes
import importlib.util
import mmap
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/"scripts/dec677_disposable_inotify_events.py"
spec=importlib.util.spec_from_file_location("dec677_native_dec1281",SCRIPT)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
IN_ONESHOT=0x80000000


@unittest.skipUnless(
    sys.platform=="linux" and hasattr(mmap,"MADV_DONTNEED")
    and hasattr(mmap.mmap,"madvise"),
    "native Linux mmap.madvise and inotify required")
class NativePrivateMapRefaultAfterBackingMutation(unittest.TestCase):
    def test_madvise_dontneed_refaults_new_original_file_bytes_after_real_write(self):
        normal_fd=original_fd=reader_fd=writer_fd=None
        private=None
        before=module.BEFORE
        private_only=b"XXXXX"+before[5:]
        new_backing=b"YYYYY"+before[5:]
        self.assertNotEqual(before,private_only)
        self.assertNotEqual(before,new_backing)
        self.assertNotEqual(private_only,new_backing)

        def rows(data):
            self.assertIs(type(data),bytes)
            o=[];p=0
            while p<len(data):
                self.assertGreaterEqual(len(data)-p,module.EVENT.size)
                wd,mask,cookie,n=module.EVENT.unpack_from(data,p)
                p+=module.EVENT.size
                self.assertLessEqual(n,len(data)-p)
                name=data[p:p+n].split(b"\x00",1)[0];p+=n
                self.assertEqual(cookie,0)
                o.append((wd,mask,name))
            self.assertEqual(p,len(data))
            return o

        with tempfile.TemporaryDirectory(
            prefix="dec1281-public-cow-backing-refault-",dir="/tmp"
        ) as tmp:
            parent=Path(tmp);sample=parent/"sample"
            self.assertEqual(sample.write_bytes(before),len(before))
            old_file=os.lstat(sample);old_parent=os.lstat(parent)
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
                private=mmap.mmap(
                    reader_fd,len(before),access=mmap.ACCESS_COPY)
                self.assertEqual(private[:],before)
                private[:5]=b"XXXXX"
                private.flush()
                self.assertEqual(private[:],private_only)
                self.assertEqual(os.pread(reader_fd,len(before),0),before)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                # An actual independently writable description
                # changes the ORIGINAL inode from B to Y while the
                # private COW mapping continues showing X.
                writer_fd=os.open(sample,os.O_WRONLY|os.O_CLOEXEC)
                self.assertEqual(os.pwrite(writer_fd,b"YYYYY",0),5)
                receipt=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    rows(receipt),
                    [(source_wd,module.IN_MODIFY,b""),
                     (parent_wd,module.IN_MODIFY,b"sample")])
                self.assertEqual(
                    rows(module._read_receipt_pending(original_fd)),
                    [(original_wd,module.IN_MODIFY,b""),
                     (original_wd,module.IN_IGNORED,b"")])
                self.assertEqual(os.pread(reader_fd,len(before),0),new_backing)
                self.assertEqual(private[:],private_only)
                real_change=module._evaluate(
                    before,new_backing,receipt,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(real_change["status"],"BLOCKED")
                self.assertIs(real_change["can_authorize_dispatch"],False)
                self.assertIs(
                    real_change["independent_os_proof_verified"],False)

                # Discard COW pages. This is event-quiet: a private
                # memory remapping/refault, NOT another write.
                private.madvise(mmap.MADV_DONTNEED)
                self.assertEqual(private[:],new_backing)
                self.assertEqual(
                    module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                # Independently restore original generated PUBLIC
                # source via genuine write; another native MODIFY.
                self.assertEqual(os.pwrite(writer_fd,before[:5],0),5)
                restore_receipt=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    rows(restore_receipt),
                    [(source_wd,module.IN_MODIFY,b""),
                     (parent_wd,module.IN_MODIFY,b"sample")])
                self.assertEqual(os.pread(reader_fd,len(before),0),before)
                restored=module._evaluate(
                    new_backing,before,restore_receipt,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(restored["status"],"BLOCKED")
                self.assertIs(restored["can_authorize_dispatch"],False)
                self.assertIs(
                    restored["independent_os_proof_verified"],False)

                private.madvise(mmap.MADV_DONTNEED)
                self.assertEqual(private[:],before)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                private.close();private=None
                os.close(reader_fd);reader_fd=None
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                os.close(writer_fd);writer_fd=None
                self.assertCountEqual(
                    rows(module._read_receipt_pending(normal_fd)),
                    [(source_wd,module.IN_CLOSE_WRITE,b""),
                     (parent_wd,module.IN_CLOSE_WRITE,b"sample")])
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                for a,b in ((old_file,os.lstat(sample)),
                            (old_parent,os.lstat(parent))):
                    self.assertEqual(
                        (a.st_dev,a.st_ino,a.st_mode,a.st_nlink),
                        (b.st_dev,b.st_ino,b.st_mode,b.st_nlink))
                self.assertEqual(sample.read_bytes(),before)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
            finally:
                if private is not None:private.close()
                for fd in (reader_fd,writer_fd,original_fd,normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):os.fstat(fd)
