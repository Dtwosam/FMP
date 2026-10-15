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
spec=importlib.util.spec_from_file_location("dec677_native_dec1278",SCRIPT)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
IN_ONESHOT=0x80000000
IN_ACCESS=0x00000001
IN_OPEN=0x00000020
IN_CLOSE_NOWRITE=0x00000010


@unittest.skipUnless(sys.platform=="linux","Linux inotify and mmap required")
class NativeReadOnlyMmapAccessEventSilence(unittest.TestCase):
    def test_readonly_mapping_reads_no_access_event_but_pread_emits_access(self):
        normal_fd=original_fd=read_fd=reader_witness_fd=writer_fd=None
        mapped=None
        before=module.BEFORE
        changed=b"XXXXX"+before[5:]
        self.assertNotEqual(before,changed)

        def rows(data):
            self.assertIs(type(data),bytes)
            seen=[];pos=0
            while pos<len(data):
                self.assertGreaterEqual(len(data)-pos,module.EVENT.size)
                wd,mask,cookie,n=module.EVENT.unpack_from(data,pos)
                pos+=module.EVENT.size
                self.assertLessEqual(n,len(data)-pos)
                name=data[pos:pos+n].split(b"\x00",1)[0];pos+=n
                self.assertEqual(cookie,0)
                seen.append((wd,mask,name))
            self.assertEqual(pos,len(data))
            return seen

        with tempfile.TemporaryDirectory(
            prefix="dec1278-public-mmap-read-access-",dir="/tmp") as tmp:
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
                reader_witness_fd=libc.inotify_init1(
                    os.O_NONBLOCK|os.O_CLOEXEC)
                self.assertEqual(
                    len({normal_fd,original_fd,reader_witness_fd}),3)
                original_wd=libc.inotify_add_watch(
                    original_fd,module._checked_watch_path_bytes(sample),
                    module.IN_MODIFY|module.IN_CLOSE_WRITE|
                    module.IN_DONT_FOLLOW|IN_ONESHOT)
                read_mask=IN_ACCESS|IN_OPEN|IN_CLOSE_NOWRITE
                rw_source_wd=libc.inotify_add_watch(
                    reader_witness_fd,
                    module._checked_watch_path_bytes(sample),
                    read_mask|module.IN_DONT_FOLLOW)
                rw_parent_wd=libc.inotify_add_watch(
                    reader_witness_fd,
                    module._checked_watch_path_bytes(parent),
                    read_mask|module.IN_ONLYDIR|module.IN_DONT_FOLLOW)
                for wd in (original_wd,rw_source_wd,rw_parent_wd):
                    self.assertGreater(wd,0)
                self.assertNotEqual(rw_source_wd,rw_parent_wd)
                for fd in (normal_fd,original_fd,reader_witness_fd):
                    self.assertEqual(module._read_receipt_pending(fd),b"")

                read_fd=os.open(sample,os.O_RDONLY|os.O_CLOEXEC)
                self.assertCountEqual(
                    rows(module._read_receipt_pending(reader_witness_fd)),
                    [(rw_source_wd,IN_OPEN,b""),
                     (rw_parent_wd,IN_OPEN,b"sample")])
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                mapped=mmap.mmap(
                    read_fd,len(before),access=mmap.ACCESS_READ)
                self.assertEqual(mapped[:],before)
                self.assertEqual(bytes(mapped[0:5]),before[:5])
                # Reading a MAP_SHARED readonly memory mapping
                # does NOT generate kernel IN_ACCESS.
                self.assertEqual(
                    module._read_receipt_pending(reader_witness_fd),b"")
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                mapped.close();mapped=None
                self.assertEqual(
                    module._read_receipt_pending(reader_witness_fd),b"")

                # A real pread through same O_RDONLY FD DOES generate
                # source+named-parent native IN_ACCESS.
                self.assertEqual(os.pread(read_fd,len(before),0),before)
                self.assertCountEqual(
                    rows(module._read_receipt_pending(reader_witness_fd)),
                    [(rw_source_wd,IN_ACCESS,b""),
                     (rw_parent_wd,IN_ACCESS,b"sample")])
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                os.close(read_fd);read_fd=None
                self.assertCountEqual(
                    rows(module._read_receipt_pending(reader_witness_fd)),
                    [(rw_source_wd,IN_CLOSE_NOWRITE,b""),
                     (rw_parent_wd,IN_CLOSE_NOWRITE,b"sample")])
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")

                # Completely unsubscribe independent READ witness
                # before any fixture inventory scan, avoiding
                # unrelated IN_ISDIR self-access kernel receipts.
                os.close(reader_witness_fd);reader_witness_fd=None
                unchanged=module._evaluate(
                    before,before,b"",source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertIs(unchanged["can_authorize_dispatch"],False)
                self.assertIs(
                    unchanged["independent_os_proof_verified"],False)

                # Real subsequent write ensures the continuing
                # mutation watcher is genuinely armed throughout.
                writer_fd=os.open(sample,os.O_WRONLY|os.O_CLOEXEC)
                self.assertEqual(os.pwrite(writer_fd,b"XXXXX",0),5)
                receipt=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    rows(receipt),
                    [(source_wd,module.IN_MODIFY,b""),
                     (parent_wd,module.IN_MODIFY,b"sample")])
                self.assertEqual(
                    rows(module._read_receipt_pending(original_fd)),
                    [(original_wd,module.IN_MODIFY,b""),
                     (original_wd,module.IN_IGNORED,b"")])
                self.assertEqual(sample.read_bytes(),changed)
                verdict=module._evaluate(
                    before,changed,receipt,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(verdict["status"],"BLOCKED")
                self.assertIs(verdict["can_authorize_dispatch"],False)
                self.assertIs(
                    verdict["independent_os_proof_verified"],False)

                self.assertEqual(os.pwrite(writer_fd,before[:5],0),5)
                restore_receipt=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    rows(restore_receipt),
                    [(source_wd,module.IN_MODIFY,b""),
                     (parent_wd,module.IN_MODIFY,b"sample")])
                restoring=module._evaluate(
                    changed,before,restore_receipt,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(restoring["status"],"BLOCKED")
                self.assertIs(restoring["can_authorize_dispatch"],False)
                self.assertIs(
                    restoring["independent_os_proof_verified"],False)
                os.close(writer_fd);writer_fd=None
                self.assertCountEqual(
                    rows(module._read_receipt_pending(normal_fd)),
                    [(source_wd,module.IN_CLOSE_WRITE,b""),
                     (parent_wd,module.IN_CLOSE_WRITE,b"sample")])
                for old,new in ((old_source,os.lstat(sample)),
                                (old_parent,os.lstat(parent))):
                    self.assertEqual(
                        (old.st_dev,old.st_ino,old.st_mode,old.st_nlink),
                        (new.st_dev,new.st_ino,new.st_mode,new.st_nlink))
                self.assertEqual(sample.read_bytes(),before)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
            finally:
                if mapped is not None:mapped.close()
                for fd in (read_fd,writer_fd,reader_witness_fd,
                           original_fd,normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):os.fstat(fd)
