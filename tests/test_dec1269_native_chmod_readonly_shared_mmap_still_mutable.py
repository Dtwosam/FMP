from __future__ import annotations

import ctypes
import importlib.util
import mmap
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1269",SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT=0x80000000


@unittest.skipUnless(sys.platform=="linux", "native Linux inotify and mmap required")
class NativeMmapAfterReadOnlyChmodRegression(unittest.TestCase):
    def test_preexisting_shared_map_modifies_source_after_fchmod_readonly(self):
        normal_fd=original_fd=writer_fd=read_fd=None
        mapped=None
        before=module.BEFORE
        changed=b"XXXXX"+before[5:]
        self.assertEqual(len(before),len(changed))
        self.assertNotEqual(before,changed)

        def events(data):
            self.assertIs(type(data),bytes)
            found=[];pos=0
            while pos<len(data):
                self.assertGreaterEqual(len(data)-pos,module.EVENT.size)
                wd,mask,cookie,n=module.EVENT.unpack_from(data,pos)
                pos+=module.EVENT.size
                self.assertLessEqual(n,len(data)-pos)
                name=data[pos:pos+n].split(b"\x00",1)[0];pos+=n
                self.assertEqual(cookie,0)
                found.append((wd,mask,name))
            self.assertEqual(pos,len(data))
            return found

        with tempfile.TemporaryDirectory(
            prefix="dec1269-public-readonly-mmap-",dir="/tmp"
        ) as tmp:
            parent=Path(tmp)
            sample=parent/"sample"
            self.assertEqual(sample.write_bytes(before),len(before))
            start_file=os.lstat(sample)
            start_parent=os.lstat(parent)
            original_mode=stat.S_IMODE(start_file.st_mode)
            self.assertTrue(start_file.st_mode & stat.S_IFREG)
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
                writer_fd=os.open(sample,os.O_RDWR|os.O_CLOEXEC)
                mapped=mmap.mmap(
                    writer_fd,len(before),access=mmap.ACCESS_WRITE)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")

                # A permission downgrade after the mapping was
                # established does NOT retroactively revoke its
                # MAP_SHARED writable page permissions.
                os.fchmod(writer_fd,0o444)
                self.assertEqual(stat.S_IMODE(os.fstat(writer_fd).st_mode),0o444)
                chmod_receipt=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    events(chmod_receipt),
                    [(source_wd,module.IN_ATTRIB,b""),
                     (parent_wd,module.IN_ATTRIB,b"sample")])
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                chmod_verdict=module._evaluate(
                    before,before,chmod_receipt,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(chmod_verdict["status"],"BLOCKED")
                self.assertIs(chmod_verdict["can_authorize_dispatch"],False)
                self.assertIs(
                    chmod_verdict["independent_os_proof_verified"],False)

                # A new independent O_RDONLY description rejects
                # ftruncate, but that rejection does not constrain
                # the already writable MAP_SHARED mapping.
                read_fd=os.open(sample,os.O_RDONLY|os.O_CLOEXEC)
                with self.assertRaises(OSError):
                    os.ftruncate(read_fd,0)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                os.close(read_fd)
                read_fd=None
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")

                mapped[:5]=b"XXXXX"
                mapped.flush()
                self.assertEqual(os.pread(writer_fd,len(before),0),changed)
                self.assertEqual(
                    stat.S_IMODE(os.fstat(writer_fd).st_mode),0o444)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                changed_verdict=module._evaluate(
                    before,changed,b"",source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(changed_verdict["status"],"BLOCKED")
                self.assertIs(changed_verdict["can_authorize_dispatch"],False)
                self.assertIs(
                    changed_verdict["independent_os_proof_verified"],False)

                mapped[:]=before
                mapped.flush()
                self.assertEqual(os.pread(writer_fd,len(before),0),before)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                restored_verdict=module._evaluate(
                    changed,before,b"",source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(restored_verdict["status"],"BLOCKED")
                self.assertIs(restored_verdict["can_authorize_dispatch"],False)
                self.assertIs(
                    restored_verdict["independent_os_proof_verified"],False)
                mapped.close();mapped=None

                os.fchmod(writer_fd,original_mode)
                self.assertEqual(
                    stat.S_IMODE(os.fstat(writer_fd).st_mode),original_mode)
                chmod_back=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    events(chmod_back),
                    [(source_wd,module.IN_ATTRIB,b""),
                     (parent_wd,module.IN_ATTRIB,b"sample")])
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                back_verdict=module._evaluate(
                    before,before,chmod_back,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=("sample",))
                self.assertEqual(back_verdict["status"],"BLOCKED")
                self.assertIs(back_verdict["can_authorize_dispatch"],False)
                self.assertIs(
                    back_verdict["independent_os_proof_verified"],False)

                os.close(writer_fd);writer_fd=None
                close_receipt=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    events(close_receipt),
                    [(source_wd,module.IN_CLOSE_WRITE,b""),
                     (parent_wd,module.IN_CLOSE_WRITE,b"sample")])
                self.assertEqual(
                    events(module._read_receipt_pending(original_fd)),
                    [(original_wd,module.IN_CLOSE_WRITE,b""),
                     (original_wd,module.IN_IGNORED,b"")])
                final_file=os.lstat(sample)
                final_parent=os.lstat(parent)
                for a,b in ((start_file,final_file),(start_parent,final_parent)):
                    self.assertEqual(
                        (a.st_dev,a.st_ino,a.st_mode,a.st_nlink),
                        (b.st_dev,b.st_ino,b.st_mode,b.st_nlink))
                self.assertEqual(sample.read_bytes(),before)
                self.assertEqual(module._bounded_inventory_names(parent),
                                 ("sample",))
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
            finally:
                if mapped is not None: mapped.close()
                for fd in (read_fd,writer_fd,original_fd,normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):os.fstat(fd)
