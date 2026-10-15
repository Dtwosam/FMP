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
spec=importlib.util.spec_from_file_location("dec677_native_dec1273",SCRIPT)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
IN_ONESHOT=0x80000000

@unittest.skipUnless(sys.platform=="linux","native Linux inotify and mmap required")
class NativeAppendSharedMmapVsPositionalWriteRegression(unittest.TestCase):
    def test_oappend_shared_mmap_overwrites_prefix_while_pwrite_appends(self):
        normal_fd=original_fd=writer_fd=restore_fd=None
        mapped=None
        before=module.BEFORE
        changed=b"XXXXX"+before[5:]
        appended=changed+b"Z"
        after_map_restore=before+b"Z"
        self.assertEqual(len(before),len(changed))
        self.assertEqual(len(appended),len(before)+1)

        def rows(data):
            self.assertIs(type(data),bytes)
            result=[];pos=0
            while pos<len(data):
                self.assertGreaterEqual(len(data)-pos,module.EVENT.size)
                wd,mask,cookie,n=module.EVENT.unpack_from(data,pos)
                pos+=module.EVENT.size
                self.assertLessEqual(n,len(data)-pos)
                name=data[pos:pos+n].split(b"\x00",1)[0];pos+=n
                self.assertEqual(cookie,0)
                result.append((wd,mask,name))
            self.assertEqual(pos,len(data))
            return result

        with tempfile.TemporaryDirectory(
            prefix="dec1273-public-append-mmap-",dir="/tmp") as tmp:
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
                self.assertGreaterEqual(original_fd,0)
                original_wd=libc.inotify_add_watch(
                    original_fd,module._checked_watch_path_bytes(sample),
                    module.IN_MODIFY|module.IN_CLOSE_WRITE|
                    module.IN_DONT_FOLLOW|IN_ONESHOT)
                self.assertGreater(original_wd,0)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                writer_fd=os.open(
                    sample,os.O_RDWR|os.O_APPEND|os.O_CLOEXEC)
                self.assertEqual(os.fstat(writer_fd).st_size,len(before))
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                mapped=mmap.mmap(
                    writer_fd,len(before),access=mmap.ACCESS_WRITE)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")

                # O_APPEND on the FD does NOT redirect shared mmap
                # store to EOF. It mutates original fixed byte offsets.
                mapped[:5]=b"XXXXX"
                mapped.flush()
                self.assertEqual(os.pread(writer_fd,len(before),0),changed)
                self.assertEqual(os.fstat(writer_fd).st_size,len(before))
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                mmap_verdict=module._evaluate(
                    before,changed,b"",source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(mmap_verdict["status"],"BLOCKED")
                self.assertIs(mmap_verdict["can_authorize_dispatch"],False)
                self.assertIs(
                    mmap_verdict["independent_os_proof_verified"],False)

                # SAME O_APPEND FD makes Linux positional pwrite(0)
                # append at EOF, unlike the previous mapped store.
                self.assertEqual(os.pwrite(writer_fd,b"Z",0),1)
                self.assertEqual(os.fstat(writer_fd).st_size,len(before)+1)
                self.assertEqual(
                    os.pread(writer_fd,len(appended),0),appended)
                receipt=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    rows(receipt),
                    [(source_wd,module.IN_MODIFY,b""),
                     (parent_wd,module.IN_MODIFY,b"sample")])
                self.assertEqual(
                    rows(module._read_receipt_pending(original_fd)),
                    [(original_wd,module.IN_MODIFY,b""),
                     (original_wd,module.IN_IGNORED,b"")])
                pwrite_verdict=module._evaluate(
                    changed,appended,receipt,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(pwrite_verdict["status"],"BLOCKED")
                self.assertIs(pwrite_verdict["can_authorize_dispatch"],False)
                self.assertIs(
                    pwrite_verdict["independent_os_proof_verified"],False)

                # The mapped fixed prefix can still be restored with
                # no native IN_MODIFY; appended Z remains at EOF.
                mapped[:]=before
                mapped.flush()
                self.assertEqual(
                    os.pread(writer_fd,len(after_map_restore),0),
                    after_map_restore)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                unmap_verdict=module._evaluate(
                    appended,after_map_restore,b"",
                    source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(unmap_verdict["status"],"BLOCKED")
                self.assertIs(unmap_verdict["can_authorize_dispatch"],False)
                self.assertIs(
                    unmap_verdict["independent_os_proof_verified"],False)
                mapped.close();mapped=None
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")

                os.close(writer_fd);writer_fd=None
                self.assertCountEqual(
                    rows(module._read_receipt_pending(normal_fd)),
                    [(source_wd,module.IN_CLOSE_WRITE,b""),
                     (parent_wd,module.IN_CLOSE_WRITE,b"sample")])
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                # Genuine disposable fixture restore removes appended
                # byte with O_TRUNC then writes original public bytes.
                restore_fd=os.open(
                    sample,os.O_WRONLY|os.O_TRUNC|os.O_CLOEXEC)
                self.assertEqual(os.write(restore_fd,before),len(before))
                os.fsync(restore_fd)
                os.close(restore_fd);restore_fd=None
                restoring=module._read_receipt_pending(normal_fd)
                observed=rows(restoring)
                allowed={(source_wd,module.IN_MODIFY,b""),
                         (parent_wd,module.IN_MODIFY,b"sample"),
                         (source_wd,module.IN_CLOSE_WRITE,b""),
                         (parent_wd,module.IN_CLOSE_WRITE,b"sample")}
                self.assertTrue(observed)
                self.assertTrue(all(x in allowed for x in observed))
                self.assertTrue(allowed.issubset(set(observed)))
                ending=module._evaluate(
                    after_map_restore,before,restoring,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(ending["status"],"BLOCKED")
                self.assertIs(ending["can_authorize_dispatch"],False)
                self.assertIs(
                    ending["independent_os_proof_verified"],False)
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
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
                if mapped is not None:mapped.close()
                for fd in (restore_fd,writer_fd,original_fd,normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):os.fstat(fd)
