from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/"scripts/dec677_disposable_inotify_events.py"
spec=importlib.util.spec_from_file_location("dec677_native_dec1287",SCRIPT)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
IN_ACCESS=0x00000001
IN_ONESHOT=0x80000000

@unittest.skipUnless(
    sys.platform=="linux" and hasattr(os,"copy_file_range"),
    "native Linux copy_file_range and inotify required")
class NativeCopyFileRangeReadVsDestWriteRegression(unittest.TestCase):
    def test_copy_file_range_reads_source_but_modifies_named_destination(self):
        normal_fd=original_fd=read_witness_fd=source_fd=dest_fd=writer_fd=None
        before=module.BEFORE
        changed=b"XXXXX"+before[5:]
        blank=b"?"*len(before)

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
            prefix="dec1287-public-copy-file-range-",dir="/tmp"
        ) as tmp:
            parent=Path(tmp);sample=parent/"sample";dest=parent/"dest"
            self.assertEqual(sample.write_bytes(before),len(before))
            self.assertEqual(dest.write_bytes(blank),len(blank))
            initial=(os.lstat(sample),os.lstat(dest),os.lstat(parent))
            try:
                normal_fd,source_wd,parent_wd=module._start_watch(sample)
                libc=ctypes.CDLL(None,use_errno=True)
                libc.inotify_init1.argtypes=[ctypes.c_int]
                libc.inotify_init1.restype=ctypes.c_int
                libc.inotify_add_watch.argtypes=[
                    ctypes.c_int,ctypes.c_char_p,ctypes.c_uint32]
                libc.inotify_add_watch.restype=ctypes.c_int
                original_fd=libc.inotify_init1(os.O_NONBLOCK|os.O_CLOEXEC)
                read_witness_fd=libc.inotify_init1(
                    os.O_NONBLOCK|os.O_CLOEXEC)
                self.assertEqual(
                    len({normal_fd,original_fd,read_witness_fd}),3)
                original_wd=libc.inotify_add_watch(
                    original_fd,module._checked_watch_path_bytes(sample),
                    module.IN_MODIFY|module.IN_CLOSE_WRITE|
                    module.IN_DONT_FOLLOW|IN_ONESHOT)
                read_source_wd=libc.inotify_add_watch(
                    read_witness_fd,
                    module._checked_watch_path_bytes(sample),
                    IN_ACCESS|module.IN_DONT_FOLLOW)
                read_parent_wd=libc.inotify_add_watch(
                    read_witness_fd,
                    module._checked_watch_path_bytes(parent),
                    IN_ACCESS|module.IN_ONLYDIR|module.IN_DONT_FOLLOW)
                self.assertGreater(original_wd,0)
                self.assertGreater(read_source_wd,0)
                self.assertGreater(read_parent_wd,0)
                self.assertNotEqual(read_source_wd,read_parent_wd)
                for fd in (normal_fd,original_fd,read_witness_fd):
                    self.assertEqual(module._read_receipt_pending(fd),b"")

                source_fd=os.open(sample,os.O_RDONLY|os.O_CLOEXEC)
                dest_fd=os.open(dest,os.O_WRONLY|os.O_CLOEXEC)
                self.assertEqual(os.fstat(source_fd).st_size,len(before))
                self.assertEqual(os.fstat(dest_fd).st_size,len(blank))
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(read_witness_fd),b"")

                # Native in-kernel copy obtains source bytes and
                # modifies a different inode, without writing source.
                self.assertEqual(
                    os.copy_file_range(source_fd,dest_fd,len(before)),
                    len(before))
                self.assertCountEqual(
                    rows(module._read_receipt_pending(read_witness_fd)),
                    [(read_source_wd,IN_ACCESS,b""),
                     (read_parent_wd,IN_ACCESS,b"sample")])
                copied_receipt=module._read_receipt_pending(normal_fd)
                self.assertEqual(
                    rows(copied_receipt),
                    [(parent_wd,module.IN_MODIFY,b"dest")])
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                copied=module._evaluate(
                    before,before,copied_receipt,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("dest","sample"))
                self.assertEqual(copied["status"],"BLOCKED")
                self.assertIs(copied["can_authorize_dispatch"],False)
                self.assertIs(
                    copied["independent_os_proof_verified"],False)
                self.assertEqual(os.fstat(source_fd).st_size,len(before))
                self.assertEqual(os.fstat(dest_fd).st_size,len(before))

                os.close(source_fd);source_fd=None
                os.close(dest_fd);dest_fd=None
                self.assertEqual(
                    rows(module._read_receipt_pending(normal_fd)),
                    [(parent_wd,module.IN_CLOSE_WRITE,b"dest")])
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                self.assertEqual(module._read_receipt_pending(read_witness_fd),b"")
                os.close(read_witness_fd);read_witness_fd=None
                self.assertEqual(dest.read_bytes(),before)
                self.assertEqual(sample.read_bytes(),before)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")

                # Real positive source-write controls distinguish
                # copying OUT of source from writing INTO source.
                writer_fd=os.open(sample,os.O_WRONLY|os.O_CLOEXEC)
                self.assertEqual(os.pwrite(writer_fd,b"XXXXX",0),5)
                positive=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    rows(positive),
                    [(source_wd,module.IN_MODIFY,b""),
                     (parent_wd,module.IN_MODIFY,b"sample")])
                self.assertEqual(
                    rows(module._read_receipt_pending(original_fd)),
                    [(original_wd,module.IN_MODIFY,b""),
                     (original_wd,module.IN_IGNORED,b"")])
                self.assertEqual(sample.read_bytes(),changed)
                result=module._evaluate(
                    before,changed,positive,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("dest","sample"))
                self.assertEqual(result["status"],"BLOCKED")
                self.assertIs(result["can_authorize_dispatch"],False)
                self.assertIs(
                    result["independent_os_proof_verified"],False)
                self.assertEqual(os.pwrite(writer_fd,before[:5],0),5)
                restored_receipt=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    rows(restored_receipt),
                    [(source_wd,module.IN_MODIFY,b""),
                     (parent_wd,module.IN_MODIFY,b"sample")])
                restored=module._evaluate(
                    changed,before,restored_receipt,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("dest","sample"))
                self.assertEqual(restored["status"],"BLOCKED")
                self.assertIs(restored["can_authorize_dispatch"],False)
                self.assertIs(
                    restored["independent_os_proof_verified"],False)
                os.close(writer_fd);writer_fd=None
                self.assertCountEqual(
                    rows(module._read_receipt_pending(normal_fd)),
                    [(source_wd,module.IN_CLOSE_WRITE,b""),
                     (parent_wd,module.IN_CLOSE_WRITE,b"sample")])
                for prior,current in zip(
                    initial,(os.lstat(sample),os.lstat(dest),os.lstat(parent))
                ):
                    self.assertEqual(
                        (prior.st_dev,prior.st_ino,prior.st_mode,prior.st_nlink),
                        (current.st_dev,current.st_ino,current.st_mode,current.st_nlink))
                self.assertEqual(sample.read_bytes(),before)
                self.assertEqual(dest.read_bytes(),before)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("dest","sample"))
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
            finally:
                for fd in (source_fd,dest_fd,writer_fd,read_witness_fd,
                           original_fd,normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):os.fstat(fd)
