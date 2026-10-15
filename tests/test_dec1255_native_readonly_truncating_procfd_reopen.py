from __future__ import annotations

import ctypes
import errno
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dec677_disposable_inotify_events.py"
spec = importlib.util.spec_from_file_location("dec677_native_dec1255", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IN_ONESHOT = 0x80000000


@unittest.skipUnless(sys.platform == "linux" and hasattr(os,"O_PATH") and os.path.isdir("/proc/self/fd"),
                     "Linux inotify and procfs required")
class NativeReadOnlyTruncatingProcFdOpenRegression(unittest.TestCase):
    def test_readonly_truncating_procfd_reopen_erases_before_rejected_allocations(self):
        normal_fd = original_fd = writer_fd = reopened_fd = readonly_fd = None
        before = module.BEFORE
        after = b"\x00" * 64

        def events(data):
            self.assertIs(type(data), bytes)
            output = []
            index = 0
            while index < len(data):
                self.assertGreaterEqual(len(data)-index, module.EVENT.size)
                wd, mask, cookie, n = module.EVENT.unpack_from(data,index)
                index += module.EVENT.size
                self.assertLessEqual(n,len(data)-index)
                name = data[index:index+n].split(b"\x00",1)[0]
                index += n
                self.assertEqual(cookie,0)
                output.append((wd,mask,name))
            self.assertEqual(index,len(data))
            return output

        with tempfile.TemporaryDirectory(
            prefix="dec1255-public-last-unlink-opath-procfd-readonly-trunc-",dir="/tmp"
        ) as tmp:
            parent = Path(tmp)
            sample = parent / "sample"
            self.assertEqual(sample.write_bytes(before),len(before))
            first = (os.lstat(sample),os.lstat(parent))
            self.assertEqual(first[0].st_nlink,1)
            try:
                normal_fd,source_wd,parent_wd=module._start_watch(sample)
                libc=ctypes.CDLL(None,use_errno=True)
                libc.inotify_init1.argtypes=[ctypes.c_int]
                libc.inotify_init1.restype=ctypes.c_int
                libc.inotify_add_watch.argtypes=[
                    ctypes.c_int,ctypes.c_char_p,ctypes.c_uint32
                ]
                libc.inotify_add_watch.restype=ctypes.c_int
                libc.inotify_rm_watch.argtypes=[ctypes.c_int,ctypes.c_int]
                libc.inotify_rm_watch.restype=ctypes.c_int
                libc.fallocate.argtypes=[
                    ctypes.c_int,ctypes.c_int,
                    ctypes.c_longlong,ctypes.c_longlong
                ]
                libc.fallocate.restype=ctypes.c_int
                original_fd=libc.inotify_init1(os.O_NONBLOCK|os.O_CLOEXEC)
                self.assertGreaterEqual(original_fd,0)
                original_wd=libc.inotify_add_watch(
                    original_fd,module._checked_watch_path_bytes(sample),
                    module.IN_MODIFY|module.IN_CLOSE_WRITE|
                    module.IN_DONT_FOLLOW|IN_ONESHOT
                )
                self.assertGreater(original_wd,0)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                # O_PATH itself has no read or write access and emits no
                # native IN_OPEN. Procfs can reopen the same detached
                # inode as a NEW independent writable file description.
                writer_fd=os.open(sample,os.O_PATH|os.O_CLOEXEC)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                os.unlink(sample)
                self.assertFalse(sample.exists())
                self.assertEqual(os.fstat(writer_fd).st_nlink,0)
                self.assertEqual(module._bounded_inventory_names(parent),())
                unlink_receipt=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    events(unlink_receipt),
                    [(source_wd,module.IN_ATTRIB,b""),
                     (parent_wd,module.IN_DELETE,b"sample")]
                )
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                result=module._evaluate(
                    before,before,unlink_receipt,source_wd,True,False,
                    directory_watch=parent_wd,directory_inventory_names=()
                )
                self.assertEqual(result["status"],"BLOCKED")
                self.assertIs(result["can_authorize_dispatch"],False)
                self.assertIs(result["independent_os_proof_verified"],False)

                proc_path="/proc/self/fd/{}".format(writer_fd)
                # This Linux READONLY|O_TRUNC procfs reopen is already
                # destructive at open time despite readonly access.
                readonly_fd=os.open(
                    proc_path,os.O_RDONLY|os.O_TRUNC|os.O_CLOEXEC
                )
                self.assertEqual(os.fstat(readonly_fd).st_nlink,0)
                self.assertEqual(os.fstat(readonly_fd).st_size,0)
                self.assertEqual(
                    (os.fstat(readonly_fd).st_dev,os.fstat(readonly_fd).st_ino),
                    (first[0].st_dev,first[0].st_ino))
                open_receipt=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    events(open_receipt),
                    [(source_wd,module.IN_MODIFY,b""),
                     (parent_wd,module.IN_MODIFY,b"sample")]
                )
                opening_verdict=module._evaluate(
                    before,b"",open_receipt,source_wd,True,False,
                    directory_watch=parent_wd,directory_inventory_names=()
                )
                self.assertEqual(opening_verdict["status"],"BLOCKED")
                self.assertIs(opening_verdict["can_authorize_dispatch"],False)
                self.assertIs(
                    opening_verdict["independent_os_proof_verified"],False)
                self.assertEqual(
                    events(module._read_receipt_pending(original_fd)),
                    [(original_wd,module.IN_MODIFY,b""),
                     (original_wd,module.IN_IGNORED,b"")]
                )
                for mode,offset,length in (
                    (0,0,5),(0x01,8192,4096),
                    (0x03,0,5),(0x11,0,5),
                ):
                    ctypes.set_errno(0)
                    self.assertEqual(
                        libc.fallocate(readonly_fd,mode,offset,length),-1)
                    self.assertEqual(ctypes.get_errno(),errno.EBADF)
                    self.assertEqual(os.fstat(readonly_fd).st_size,0)
                    self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                    self.assertEqual(module._read_receipt_pending(original_fd),b"")
                os.close(readonly_fd)
                readonly_fd=None
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")

                # A different, writable procfs reopen of the SAME
                # unlinked inode may succeed and mutate existing bytes.
                reopened_fd=os.open(proc_path,os.O_RDWR|os.O_CLOEXEC)
                self.assertNotEqual(reopened_fd,writer_fd)
                self.assertEqual(
                    (os.fstat(reopened_fd).st_dev,
                     os.fstat(reopened_fd).st_ino),
                    (first[0].st_dev,first[0].st_ino))
                self.assertEqual(os.fstat(reopened_fd).st_nlink,0)
                # Reopening via /proc/self/fd is not a source content
                # mutation even though the original path is absent.
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")

                # Original O_PATH cannot write/ftruncate at all.
                with self.assertRaises(OSError) as denied:
                    os.ftruncate(writer_fd,0)
                self.assertEqual(denied.exception.errno,errno.EBADF)
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                # Yet reopened O_RDWR FD can mutate the detached inode.

                for i in (1,2):
                    self.assertEqual(
                        libc.fallocate(reopened_fd,0x10,0,64),0,
                        os.strerror(ctypes.get_errno())
                    )
                    self.assertEqual(os.fstat(reopened_fd).st_nlink,0)
                    self.assertEqual(os.fstat(reopened_fd).st_size,64)
                    self.assertEqual(os.pread(reopened_fd,len(before),0),after)
                    receipt=module._read_receipt_pending(normal_fd)
                    self.assertCountEqual(
                        events(receipt),
                        [(source_wd,module.IN_MODIFY,b""),
                         (parent_wd,module.IN_MODIFY,b"sample")]
                    )
                    verdict=module._evaluate(
                        b"" if i==1 else after,
                        after,receipt,source_wd,True,False,
                        directory_watch=parent_wd,directory_inventory_names=()
                    )
                    self.assertEqual(verdict["status"],"BLOCKED")
                    self.assertIs(verdict["can_authorize_dispatch"],False)
                    self.assertIs(verdict["independent_os_proof_verified"],False)
                    # ONESHOT expired at O_RDONLY|O_TRUNC open time.
                    self.assertEqual(
                        module._read_receipt_pending(original_fd),b"")
                    self.assertEqual(module._read_receipt_pending(normal_fd),b"")

                os.close(reopened_fd)
                reopened_fd=None
                # The independent writable file description closed,
                # but the original O_PATH holder still preserves
                # the unlinked watched inode.
                self.assertCountEqual(
                    events(module._read_receipt_pending(normal_fd)),
                    [(source_wd,module.IN_CLOSE_WRITE,b""),
                     (parent_wd,module.IN_CLOSE_WRITE,b"sample")]
                )
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                self.assertEqual(os.fstat(writer_fd).st_nlink,0)
                os.close(writer_fd)
                writer_fd=None
                # Last reference is now the O_PATH procfs holder;
                # source DELETE_SELF/IGNORED only arrive on its close.
                final_receipt=module._read_receipt_pending(normal_fd)
                self.assertCountEqual(
                    events(final_receipt),
                    [(source_wd,module.IN_DELETE_SELF,b""),
                     (source_wd,module.IN_IGNORED,b"")]
                )
                final_verdict=module._evaluate(
                    after,after,final_receipt,source_wd,True,False,
                    directory_watch=parent_wd,directory_inventory_names=()
                )
                self.assertEqual(final_verdict["status"],"BLOCKED")
                self.assertIs(final_verdict["can_authorize_dispatch"],False)
                self.assertIs(final_verdict["independent_os_proof_verified"],False)
                ctypes.set_errno(0)
                self.assertEqual(libc.inotify_rm_watch(normal_fd,source_wd),-1)
                self.assertEqual(ctypes.get_errno(),errno.EINVAL)
                self.assertEqual(module._read_receipt_pending(original_fd),b"")
                self.assertEqual(module._read_receipt_pending(normal_fd),b"")
                self.assertFalse(sample.exists())
                self.assertEqual(module._bounded_inventory_names(parent),())
                now=os.lstat(parent)
                self.assertEqual(
                    (now.st_dev,now.st_ino,now.st_mode,now.st_nlink),
                    (first[1].st_dev,first[1].st_ino,
                     first[1].st_mode,first[1].st_nlink)
                )
            finally:
                for fd in (writer_fd,readonly_fd,reopened_fd,original_fd,normal_fd):
                    if fd is not None:
                        os.close(fd)
                        with self.assertRaises(OSError):
                            os.fstat(fd)
