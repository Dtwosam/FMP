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
spec = importlib.util.spec_from_file_location("dec677_native_dec1264", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(
    sys.platform == "linux" and hasattr(os, "O_PATH") and
    os.path.isdir("/proc/self/fd"),
    "native Linux inotify, mmap and procfs required"
)
class NativeProcFdUnlinkedSharedMapSilentMutationRegression(unittest.TestCase):
    def test_mmap_mutates_and_restores_unlinked_inode_without_modify_events(self):
        normal_fd = original_fd = holder_fd = writer_fd = None
        mapped = None
        before = module.BEFORE
        changed = b"XXXXX" + before[5:]
        self.assertNotEqual(before, changed)
        self.assertEqual(len(before), len(changed))

        def rows(data):
            self.assertIs(type(data), bytes)
            found = []
            offset = 0
            while offset < len(data):
                self.assertGreaterEqual(len(data)-offset, module.EVENT.size)
                wd, mask, cookie, count = module.EVENT.unpack_from(data, offset)
                offset += module.EVENT.size
                self.assertLessEqual(count, len(data)-offset)
                name = data[offset:offset+count].split(b"\x00",1)[0]
                offset += count
                self.assertEqual(cookie, 0)
                found.append((wd,mask,name))
            self.assertEqual(offset,len(data))
            return found

        with tempfile.TemporaryDirectory(
            prefix="dec1264-public-unlinked-procfd-mmap-",dir="/tmp"
        ) as tmp:
            parent=Path(tmp)
            sample=parent/"sample"
            self.assertEqual(sample.write_bytes(before),len(before))
            original_file=os.lstat(sample)
            original_parent=os.lstat(parent)
            self.assertEqual(original_file.st_nlink,1)
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
                unlink_verdict=module._evaluate(
                    before,before,unlink_receipt,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=())
                self.assertEqual(unlink_verdict["status"],"BLOCKED")
                self.assertIs(unlink_verdict["can_authorize_dispatch"],False)
                self.assertIs(
                    unlink_verdict["independent_os_proof_verified"],False)
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                # This is a new independently writable file description
                # even though the original source pathname is absent.
                writer_fd=os.open(
                    "/proc/self/fd/{}".format(holder_fd),
                    os.O_RDWR|os.O_CLOEXEC)
                self.assertEqual(
                    (os.fstat(writer_fd).st_dev,
                     os.fstat(writer_fd).st_ino,
                     os.fstat(writer_fd).st_nlink),
                    (original_file.st_dev,original_file.st_ino,0))
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                # MAP_SHARED writable mapping can mutate and restore
                # original inode bytes without native IN_MODIFY.
                mapped=mmap.mmap(writer_fd,len(before),access=mmap.ACCESS_WRITE)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                mapped[:5]=b"XXXXX"
                mapped.flush()
                self.assertEqual(os.pread(writer_fd,len(before),0),changed)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                first_verdict=module._evaluate(
                    before,changed,b"",source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=())
                self.assertEqual(first_verdict["status"],"BLOCKED")
                self.assertIs(first_verdict["can_authorize_dispatch"],False)
                self.assertIs(
                    first_verdict["independent_os_proof_verified"],False)

                mapped[:]=before
                mapped.flush()
                self.assertEqual(os.pread(writer_fd,len(before),0),before)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                second_verdict=module._evaluate(
                    changed,before,b"",source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=())
                self.assertEqual(second_verdict["status"],"BLOCKED")
                self.assertIs(second_verdict["can_authorize_dispatch"],False)
                self.assertIs(
                    second_verdict["independent_os_proof_verified"],False)
                mapped.close()
                mapped=None
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")

                # Writable FD closing reports native CLOSE_WRITE
                # even though both mmap transitions lacked MODIFY.
                os.close(writer_fd)
                writer_fd=None
                close_receipt=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    rows(close_receipt),
                    [(source_wd,module.IN_CLOSE_WRITE,b""),
                     (parent_wd,module.IN_CLOSE_WRITE,b"sample")])
                self.assertEqual(
                    rows(module._read_receipt_pending(original_fd)),
                    [(original_wd,module.IN_CLOSE_WRITE,b""),
                     (original_wd,module.IN_IGNORED,b"")])
                close_verdict=module._evaluate(
                    before,before,close_receipt,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=())
                self.assertEqual(close_verdict["status"],"BLOCKED")
                self.assertIs(close_verdict["can_authorize_dispatch"],False)
                self.assertIs(
                    close_verdict["independent_os_proof_verified"],False)

                os.close(holder_fd)
                holder_fd=None
                final_receipt=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    rows(final_receipt),
                    [(source_wd,module.IN_DELETE_SELF,b""),
                     (source_wd,module.IN_IGNORED,b"")])
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                self.assertFalse(sample.exists())
                self.assertEqual(module._bounded_inventory_names(parent),())
                now=os.lstat(parent)
                self.assertEqual(
                    (now.st_dev,now.st_ino,now.st_mode,now.st_nlink),
                    (original_parent.st_dev,original_parent.st_ino,
                     original_parent.st_mode,original_parent.st_nlink))
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
            finally:
                if mapped is not None:
                    mapped.close()
                for fd in (writer_fd,holder_fd,original_fd,normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
