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
spec=importlib.util.spec_from_file_location("dec677_native_dec1267",SCRIPT)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
IN_ONESHOT=0x80000000

@unittest.skipUnless(
    sys.platform=="linux" and hasattr(os,"O_PATH")
    and os.path.isdir("/proc/self/fd"),
    "Linux native inotify, procfs and private mmap required")
class NativeUnlinkedPrivateMmapOutlivesAllDescriptors(unittest.TestCase):
    def test_private_map_outlives_all_fds_without_writing_original_inode(self):
        normal_fd=original_fd=holder_fd=reader_fd=None
        mapped=None
        before=module.BEFORE
        changed=b"XXXXX"+before[5:]
        late=b"YYYYY"+before[5:]
        self.assertEqual(len(before),len(changed))
        self.assertEqual(len(before),len(late))

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
            prefix="dec1267-public-detached-private-map-",dir="/tmp"
        ) as tmp:
            parent=Path(tmp);sample=parent/"sample"
            self.assertEqual(sample.write_bytes(before),len(before))
            prior_file=os.lstat(sample);prior_parent=os.lstat(parent)
            self.assertEqual(prior_file.st_nlink,1)
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

                holder_fd=os.open(sample,os.O_PATH|os.O_CLOEXEC)
                os.unlink(sample)
                self.assertFalse(sample.exists())
                self.assertEqual(os.fstat(holder_fd).st_nlink,0)
                self.assertEqual(module._bounded_inventory_names(parent),())
                receipt=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    rows(receipt),
                    [(source_wd,module.IN_ATTRIB,b""),
                     (parent_wd,module.IN_DELETE,b"sample")])
                result=module._evaluate(
                    before,before,receipt,source_wd,True,False,
                    directory_watch=parent_wd,directory_inventory_names=())
                self.assertEqual(result["status"],"BLOCKED")
                self.assertIs(result["can_authorize_dispatch"],False)
                self.assertIs(
                    result["independent_os_proof_verified"],False)
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                reader_fd=os.open(
                    "/proc/self/fd/{}".format(holder_fd),
                    os.O_RDONLY|os.O_CLOEXEC)
                self.assertEqual(
                    (os.fstat(reader_fd).st_dev,
                     os.fstat(reader_fd).st_ino,
                     os.fstat(reader_fd).st_nlink),
                    (prior_file.st_dev,prior_file.st_ino,0))
                mapped=mmap.mmap(
                    reader_fd,len(before),access=mmap.ACCESS_COPY)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                mapped[:5]=b"XXXXX"
                mapped.flush()
                self.assertEqual(mapped[:],changed)
                # Independent read of the REAL inode proves the
                # modified MAP_PRIVATE bytes were copy-on-write.
                self.assertEqual(
                    os.pread(reader_fd,len(before),0),before)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                mapped[:]=before

                # Both ordinary descriptors close while the PRIVATE
                # mapping keeps original detached inode alive.
                os.close(reader_fd);reader_fd=None
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                os.close(holder_fd);holder_fd=None
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                self.assertFalse(sample.exists())

                # Even after BOTH FDs closed, COW-mapped memory can
                # still change. This is NOT a source inode write.
                mapped[:5]=b"YYYYY"
                mapped.flush()
                self.assertEqual(mapped[:],late)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                quiet=module._evaluate(
                    before,before,b"",source_wd,True,False,
                    directory_watch=parent_wd,directory_inventory_names=())
                self.assertIn(
                    quiet["status"],
                    ("BLOCKED","LOCAL_DISPOSABLE_WITNESS_UNVERIFIED"))
                self.assertIs(quiet["can_authorize_dispatch"],False)
                self.assertIs(
                    quiet["independent_os_proof_verified"],False)

                # Last MAP_PRIVATE unmap retires the original inode
                # watch but emits no CLOSE_WRITE: only read-only
                # procfs fd and private COW mapped memory existed.
                mapped.close();mapped=None
                self.assertCountEqual(
                    rows(module._read_receipt_pending(normal_fd)),
                    [(source_wd,module.IN_DELETE_SELF,b""),
                     (source_wd,module.IN_IGNORED,b"")])
                self.assertEqual(
                    rows(module._read_receipt_pending(original_fd)),
                    [(original_wd,module.IN_IGNORED,b"")])
                self.assertFalse(sample.exists())
                self.assertEqual(module._bounded_inventory_names(parent),())
                now=os.lstat(parent)
                self.assertEqual(
                    (now.st_dev,now.st_ino,now.st_mode,now.st_nlink),
                    (prior_parent.st_dev,prior_parent.st_ino,
                     prior_parent.st_mode,prior_parent.st_nlink))
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
            finally:
                if mapped is not None:
                    mapped.close()
                for fd in (reader_fd,holder_fd,original_fd,normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
