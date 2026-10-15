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
spec = importlib.util.spec_from_file_location("dec677_native_dec1266", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(
    sys.platform == "linux" and hasattr(os,"O_PATH")
    and os.path.isdir("/proc/self/fd"),
    "native Linux inotify, procfs and shared mmap required")
class NativeUnlinkedMmapOutlivesDescriptorsRegression(unittest.TestCase):
    def test_shared_map_mutates_after_all_descriptors_close_and_delays_close(self):
        normal_fd = original_fd = holder_fd = writer_fd = None
        mapped = None
        before = module.BEFORE
        changed = b"XXXXX" + before[5:]
        late = b"YYYYY" + before[5:]
        self.assertEqual(len(before),len(changed))
        self.assertEqual(len(before),len(late))

        def rows(data):
            self.assertIs(type(data),bytes)
            observed=[];pos=0
            while pos<len(data):
                self.assertGreaterEqual(len(data)-pos,module.EVENT.size)
                wd,mask,cookie,n=module.EVENT.unpack_from(data,pos)
                pos+=module.EVENT.size
                self.assertLessEqual(n,len(data)-pos)
                name=data[pos:pos+n].split(b"\x00",1)[0];pos+=n
                self.assertEqual(cookie,0)
                observed.append((wd,mask,name))
            self.assertEqual(pos,len(data))
            return observed

        with tempfile.TemporaryDirectory(
            prefix="dec1266-public-orphaned-shared-map-",dir="/tmp"
        ) as tmp:
            parent=Path(tmp);sample=parent/"sample"
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
                initial=module._evaluate(
                    before,before,unlink_receipt,source_wd,True,False,
                    directory_watch=parent_wd,
                    directory_inventory_names=())
                self.assertEqual(initial["status"],"BLOCKED")
                self.assertIs(initial["can_authorize_dispatch"],False)
                self.assertIs(
                    initial["independent_os_proof_verified"],False)
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                writer_fd=os.open(
                    "/proc/self/fd/{}".format(holder_fd),
                    os.O_RDWR|os.O_CLOEXEC)
                self.assertEqual(
                    (os.fstat(writer_fd).st_dev,
                     os.fstat(writer_fd).st_ino,
                     os.fstat(writer_fd).st_nlink),
                    (original_file.st_dev,original_file.st_ino,0))
                mapped=mmap.mmap(
                    writer_fd,len(before),access=mmap.ACCESS_WRITE)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")

                # Prove this MAP_SHARED mapping changes the ORIGINAL
                # inode, not only a private userspace COW buffer.
                mapped[:5]=b"XXXXX"
                mapped.flush()
                self.assertEqual(
                    os.pread(writer_fd,len(before),0),changed)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                first=module._evaluate(
                    before,changed,b"",source_wd,True,False,
                    directory_watch=parent_wd,directory_inventory_names=())
                self.assertEqual(first["status"],"BLOCKED")
                self.assertIs(first["can_authorize_dispatch"],False)
                self.assertIs(first["independent_os_proof_verified"],False)

                mapped[:]=before
                mapped.flush()
                self.assertEqual(os.pread(writer_fd,len(before),0),before)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                # Close BOTH live file descriptors while MAP_SHARED
                # mapping still exists. Neither close emits CLOSE_WRITE
                # or removes the original inode watch yet.
                os.close(writer_fd)
                writer_fd=None
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                os.close(holder_fd)
                holder_fd=None
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                self.assertFalse(sample.exists())

                # With no surviving ordinary Python FD to the source,
                # existing writable shared mapping can STILL change
                # the backing original inode, event-quiet.
                mapped[:5]=b"YYYYY"
                mapped.flush()
                self.assertEqual(mapped[:],late)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                second=module._evaluate(
                    before,late,b"",source_wd,True,False,
                    directory_watch=parent_wd,directory_inventory_names=())
                self.assertEqual(second["status"],"BLOCKED")
                self.assertIs(second["can_authorize_dispatch"],False)
                self.assertIs(second["independent_os_proof_verified"],False)

                mapped[:]=before
                mapped.flush()
                self.assertEqual(mapped[:],before)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                # Final mapping release, not either prior os.close,
                # emits deferred CLOSE_WRITE plus DELETE_SELF/IGNORED.
                mapped.close()
                mapped=None
                final_receipt=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    rows(final_receipt),
                    [(source_wd,module.IN_CLOSE_WRITE,b""),
                     (parent_wd,module.IN_CLOSE_WRITE,b"sample"),
                     (source_wd,module.IN_DELETE_SELF,b""),
                     (source_wd,module.IN_IGNORED,b"")])
                self.assertEqual(
                    rows(module._read_receipt_pending(original_fd)),
                    [(original_wd,module.IN_CLOSE_WRITE,b""),
                     (original_wd,module.IN_IGNORED,b"")])
                retired=module._evaluate(
                    before,before,final_receipt,source_wd,True,False,
                    directory_watch=parent_wd,directory_inventory_names=())
                self.assertEqual(retired["status"],"BLOCKED")
                self.assertIs(retired["can_authorize_dispatch"],False)
                self.assertIs(
                    retired["independent_os_proof_verified"],False)
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
