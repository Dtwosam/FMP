from __future__ import annotations

import ctypes
import importlib.util
import mmap
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1265", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(
    sys.platform == "linux" and hasattr(os,"O_PATH")
    and os.path.isdir("/proc/self/fd"),
    "Linux procfs, inotify and mmap required")
class NativeUnlinkedProcFdPrivateMmapCowRegression(unittest.TestCase):
    def test_private_mmap_cow_changes_mapping_but_not_original_unlinked_inode(self):
        normal_fd = original_fd = holder_fd = reader_fd = None
        mapped = None
        before = module.BEFORE
        private = b"XXXXX" + before[5:]
        self.assertNotEqual(private,before)

        def rows(data):
            self.assertIs(type(data),bytes)
            out=[]; offset=0
            while offset<len(data):
                self.assertGreaterEqual(len(data)-offset,module.EVENT.size)
                wd,mask,cookie,n=module.EVENT.unpack_from(data,offset)
                offset+=module.EVENT.size
                self.assertLessEqual(n,len(data)-offset)
                name=data[offset:offset+n].split(b"\x00",1)[0]
                offset+=n
                self.assertEqual(cookie,0)
                out.append((wd,mask,name))
            self.assertEqual(offset,len(data))
            return out

        with tempfile.TemporaryDirectory(
            prefix="dec1265-public-unlinked-procfd-private-map-",dir="/tmp"
        ) as tmp:
            parent=Path(tmp)
            sample=parent/"sample"
            self.assertEqual(sample.write_bytes(before),len(before))
            before_file=os.lstat(sample)
            before_parent=os.lstat(parent)
            self.assertEqual(before_file.st_nlink,1)
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
                unlink_receipt=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    rows(unlink_receipt),
                    [(source_wd,module.IN_ATTRIB,b""),
                     (parent_wd,module.IN_DELETE,b"sample")])
                verdict=module._evaluate(
                    before,before,unlink_receipt,source_wd,True,False,
                    directory_watch=parent_wd,directory_inventory_names=())
                self.assertEqual(verdict["status"],"BLOCKED")
                self.assertIs(verdict["can_authorize_dispatch"],False)
                self.assertIs(
                    verdict["independent_os_proof_verified"],False)
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                # Independent O_RDONLY procfs reopened description is
                # sufficient for MAP_PRIVATE COW. MAP_SHARED writable
                # would need O_RDWR, as covered in the companion test.
                reader_fd=os.open(
                    "/proc/self/fd/{}".format(holder_fd),
                    os.O_RDONLY|os.O_CLOEXEC)
                self.assertEqual(
                    (os.fstat(reader_fd).st_dev,
                     os.fstat(reader_fd).st_ino,
                     os.fstat(reader_fd).st_nlink),
                    (before_file.st_dev,before_file.st_ino,0))
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                mapped=mmap.mmap(
                    reader_fd,len(before),access=mmap.ACCESS_COPY)
                self.assertEqual(bytes(mapped[:]),before)
                mapped[:5]=b"XXXXX"
                self.assertEqual(bytes(mapped[:]),private)
                mapped.flush()
                # COW mapping's private visible bytes have changed,
                # but the actual original inode has not.
                self.assertEqual(
                    os.pread(reader_fd,len(before),0),before)
                self.assertEqual(os.fstat(reader_fd).st_size,len(before))
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

                mapped.close()
                mapped=None
                os.close(reader_fd)
                reader_fd=None
                # O_RDONLY procfs descriptor's CLOSE_NOWRITE is
                # not subscribed by either mutation-only watch.
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                os.close(holder_fd)
                holder_fd=None
                self.assertCountEqual(
                    rows(module._read_receipt_pending(normal_fd)),
                    [(source_wd,module.IN_DELETE_SELF,b""),
                     (source_wd,module.IN_IGNORED,b"")])
                # The deliberately unsafe source ONESHOT stayed armed
                # through all COW-only reads/writes and is invalidated
                # at inode retirement, without ever reporting MODIFY.
                self.assertEqual(
                    rows(module._read_receipt_pending(original_fd)),
                    [(original_wd,module.IN_IGNORED,b"")])
                self.assertFalse(sample.exists())
                self.assertEqual(module._bounded_inventory_names(parent),())
                final_parent=os.lstat(parent)
                self.assertEqual(
                    (final_parent.st_dev,final_parent.st_ino,
                     final_parent.st_mode,final_parent.st_nlink),
                    (before_parent.st_dev,before_parent.st_ino,
                     before_parent.st_mode,before_parent.st_nlink))
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
            finally:
                if mapped is not None:
                    mapped.close()
                for fd in (reader_fd,holder_fd,original_fd,normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
