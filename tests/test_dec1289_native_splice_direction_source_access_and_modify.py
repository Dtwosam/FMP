from __future__ import annotations

import ctypes
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/"scripts/dec677_disposable_inotify_events.py"
spec=importlib.util.spec_from_file_location("dec677_native_dec1289",SCRIPT)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
IN_ACCESS=0x00000001
IN_ONESHOT=0x80000000

@unittest.skipUnless(
    sys.platform=="linux" and hasattr(os,"splice"),
    "native Linux splice and inotify required")
class NativeSpliceReadAndWriteDirectionRegression(unittest.TestCase):
    def test_splice_file_to_pipe_is_read_but_pipe_to_file_is_real_mutation(self):
        normal_fd=original_fd=read_witness_fd=source_fd=pipe_r=pipe_w=writer_fd=None
        before=module.BEFORE
        changed=b"XXXXX"+before[5:]

        def rows(data):
            self.assertIs(type(data),bytes)
            res=[];pos=0
            while pos<len(data):
                self.assertGreaterEqual(len(data)-pos,module.EVENT.size)
                wd,mask,cookie,n=module.EVENT.unpack_from(data,pos)
                pos+=module.EVENT.size
                self.assertLessEqual(n,len(data)-pos)
                name=data[pos:pos+n].split(b"\x00",1)[0];pos+=n
                self.assertEqual(cookie,0)
                res.append((wd,mask,name))
            self.assertEqual(pos,len(data))
            return res

        with tempfile.TemporaryDirectory(
            prefix="dec1289-public-sendfile-pipe-",dir="/tmp"
        ) as tmp:
            parent=Path(tmp);sample=parent/"sample"
            self.assertEqual(sample.write_bytes(before),len(before))
            old_source=os.lstat(sample);old_parent=os.lstat(parent)
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
                rswd=libc.inotify_add_watch(
                    read_witness_fd,
                    module._checked_watch_path_bytes(sample),
                    IN_ACCESS|module.IN_DONT_FOLLOW)
                rpwd=libc.inotify_add_watch(
                    read_witness_fd,
                    module._checked_watch_path_bytes(parent),
                    IN_ACCESS|module.IN_ONLYDIR|module.IN_DONT_FOLLOW)
                self.assertGreater(original_wd,0)
                self.assertGreater(rswd,0)
                self.assertGreater(rpwd,0)
                self.assertNotEqual(rswd,rpwd)
                for fd in (normal_fd,original_fd,read_witness_fd):
                    self.assertEqual(module._read_receipt_pending(fd),b"")

                source_fd=os.open(sample,os.O_RDONLY|os.O_CLOEXEC)
                pipe_r,pipe_w=os.pipe2(os.O_CLOEXEC)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(read_witness_fd),b"")

                # Native source-file -> pipe splice is a READ:
                # original source IN_ACCESS but no native MODIFY.
                self.assertEqual(
                    os.splice(source_fd,pipe_w,len(before)),
                    len(before))
                self.assertCountEqual(
                    rows(module._read_receipt_pending(read_witness_fd)),
                    [(rswd,IN_ACCESS,b""),
                     (rpwd,IN_ACCESS,b"sample")])
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                self.assertEqual(os.fstat(source_fd).st_size,len(before))
                # The read-direction splice delivered the exact
                # PUBLIC file bytes, with no source inode mutation.
                self.assertEqual(os.read(pipe_r,len(before)),before)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                no_write=module._evaluate(
                    before,before,b"",source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertIs(no_write["can_authorize_dispatch"],False)
                self.assertIs(
                    no_write["independent_os_proof_verified"],False)
                os.close(source_fd);source_fd=None
                self.assertEqual(module._read_receipt_pending(read_witness_fd),b"")
                os.close(read_witness_fd);read_witness_fd=None

                # Reverse splice direction: pipe -> original O_WRONLY
                # FD really modifies original bytes, without a
                # userspace file write() or pwrite() call.
                writer_fd=os.open(sample,os.O_WRONLY|os.O_CLOEXEC)
                self.assertEqual(os.write(pipe_w,b"XXXXX"),5)
                self.assertEqual(
                    os.splice(pipe_r,writer_fd,5,offset_dst=0),5)
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
                    directory_inventory_names=("sample",))
                self.assertEqual(result["status"],"BLOCKED")
                self.assertIs(result["can_authorize_dispatch"],False)
                self.assertIs(result["independent_os_proof_verified"],False)

                # A second pipe -> source splice restores original
                # disposable PUBLIC bytes with separate true MODIFY.
                self.assertEqual(os.write(pipe_w,before[:5]),5)
                self.assertEqual(
                    os.splice(pipe_r,writer_fd,5,offset_dst=0),5)
                restoring=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    rows(restoring),
                    [(source_wd,module.IN_MODIFY,b""),
                     (parent_wd,module.IN_MODIFY,b"sample")])
                verdict=module._evaluate(
                    changed,before,restoring,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(verdict["status"],"BLOCKED")
                self.assertIs(verdict["can_authorize_dispatch"],False)
                self.assertIs(
                    verdict["independent_os_proof_verified"],False)
                os.close(writer_fd);writer_fd=None
                self.assertCountEqual(
                    rows(module._read_receipt_pending(normal_fd)),
                    [(source_wd,module.IN_CLOSE_WRITE,b""),
                     (parent_wd,module.IN_CLOSE_WRITE,b"sample")])
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                os.close(pipe_w);pipe_w=None
                os.close(pipe_r);pipe_r=None
                for a,b in ((old_source,os.lstat(sample)),
                            (old_parent,os.lstat(parent))):
                    self.assertEqual(
                        (a.st_dev,a.st_ino,a.st_mode,a.st_nlink),
                        (b.st_dev,b.st_ino,b.st_mode,b.st_nlink))
                self.assertEqual(sample.read_bytes(),before)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
            finally:
                for fd in (pipe_r,pipe_w,source_fd,writer_fd,
                           read_witness_fd,original_fd,normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):os.fstat(fd)
