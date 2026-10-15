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

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1276", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
IN_ONESHOT=0x80000000


@unittest.skipUnless(sys.platform=="linux","Linux native mmap/inotify required")
class NativeReadOnlySharedMmapDeniedPrivateCowRegression(unittest.TestCase):
    def test_readonly_fd_denies_shared_writable_map_but_allows_private_cow(self):
        normal_fd=original_fd=reader_fd=writer_fd=None
        private=None
        before=module.BEFORE
        changed=b"XXXXX"+before[5:]
        self.assertNotEqual(before,changed)
        self.assertEqual(len(before),len(changed))

        def rows(data):
            self.assertIs(type(data),bytes)
            seen=[];off=0
            while off<len(data):
                self.assertGreaterEqual(len(data)-off,module.EVENT.size)
                wd,mask,cookie,n=module.EVENT.unpack_from(data,off)
                off+=module.EVENT.size
                self.assertLessEqual(n,len(data)-off)
                name=data[off:off+n].split(b"\x00",1)[0]
                off+=n
                self.assertEqual(cookie,0)
                seen.append((wd,mask,name))
            self.assertEqual(off,len(data))
            return seen

        with tempfile.TemporaryDirectory(
            prefix="dec1276-public-readonly-mmap-access-",dir="/tmp"
        ) as tmp:
            parent=Path(tmp);sample=parent/"sample"
            self.assertEqual(sample.write_bytes(before),len(before))
            old_source=os.lstat(sample)
            old_parent=os.lstat(parent)
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
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                with self.assertRaises(OSError) as denied:
                    mmap.mmap(
                        reader_fd,len(before),access=mmap.ACCESS_WRITE)
                self.assertEqual(denied.exception.errno,errno.EACCES)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                self.assertEqual(os.fstat(reader_fd).st_size,len(before))
                self.assertEqual(sample.read_bytes(),before)

                # Same O_RDONLY descriptor may create MAP_PRIVATE COW:
                # mutable mapping bytes are NOT mutated source bytes.
                private=mmap.mmap(
                    reader_fd,len(before),access=mmap.ACCESS_COPY)
                private[:5]=b"XXXXX"
                self.assertEqual(private[:],changed)
                private.flush()
                self.assertEqual(os.pread(reader_fd,len(before),0),before)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                no_source_write=module._evaluate(
                    before,before,b"",source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertIs(no_source_write["can_authorize_dispatch"],False)
                self.assertIs(
                    no_source_write["independent_os_proof_verified"],False)
                private.close();private=None
                os.close(reader_fd);reader_fd=None
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                # Independent writer can still mutate original source;
                # failure to map O_RDONLY does not prove OS no-write
                # denial for ALL file descriptions/processes.
                writer_fd=os.open(sample,os.O_WRONLY|os.O_CLOEXEC)
                self.assertEqual(os.pwrite(writer_fd,b"XXXXX",0),5)
                actual=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    rows(actual),
                    [(source_wd,module.IN_MODIFY,b""),
                     (parent_wd,module.IN_MODIFY,b"sample")])
                self.assertEqual(
                    rows(module._read_receipt_pending(original_fd)),
                    [(original_wd,module.IN_MODIFY,b""),
                     (original_wd,module.IN_IGNORED,b"")])
                self.assertEqual(sample.read_bytes(),changed)
                modified=module._evaluate(
                    before,changed,actual,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(modified["status"],"BLOCKED")
                self.assertIs(modified["can_authorize_dispatch"],False)
                self.assertIs(
                    modified["independent_os_proof_verified"],False)

                self.assertEqual(os.pwrite(writer_fd,before[:5],0),5)
                restoring=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    rows(restoring),
                    [(source_wd,module.IN_MODIFY,b""),
                     (parent_wd,module.IN_MODIFY,b"sample")])
                restored=module._evaluate(
                    changed,before,restoring,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(restored["status"],"BLOCKED")
                self.assertIs(restored["can_authorize_dispatch"],False)
                self.assertIs(
                    restored["independent_os_proof_verified"],False)
                os.close(writer_fd);writer_fd=None
                self.assertCountEqual(
                    rows(module._read_receipt_pending(normal_fd)),
                    [(source_wd,module.IN_CLOSE_WRITE,b""),
                     (parent_wd,module.IN_CLOSE_WRITE,b"sample")])
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                for old,new in ((old_source,os.lstat(sample)),
                                (old_parent,os.lstat(parent))):
                    self.assertEqual(
                        (old.st_dev,old.st_ino,old.st_mode,old.st_nlink),
                        (new.st_dev,new.st_ino,new.st_mode,new.st_nlink))
                self.assertEqual(sample.read_bytes(),before)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
            finally:
                if private is not None: private.close()
                for fd in (reader_fd,writer_fd,original_fd,normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):os.fstat(fd)
