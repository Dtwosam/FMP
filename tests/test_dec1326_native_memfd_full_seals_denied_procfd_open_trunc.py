from __future__ import annotations

import ctypes
import errno
import fcntl
import mmap
import os
import struct
import sys
import unittest

BEFORE=b"GENERATED-PUBLIC-SEAL-TRUNC-ABCD"
EVENT=struct.Struct("iIII")
IN_MODIFY=0x00000002
IN_DELETE_SELF=0x00000400
IN_IGNORED=0x00008000


@unittest.skipUnless(
    sys.platform=="linux" and hasattr(os,"memfd_create")
    and os.path.isdir("/proc/self/fd")
    and all(hasattr(fcntl,key) for key in
        ("F_ADD_SEALS","F_GET_SEALS","F_SEAL_WRITE",
         "F_SEAL_GROW","F_SEAL_SHRINK","F_SEAL_SEAL",
         "F_SEAL_FUTURE_WRITE")),
    "Linux memfd seals and native inotify required")
class NativeFullSealsAllProcfdTruncateDenied(unittest.TestCase):
    def test_full_seals_reject_readonly_writeonly_rdwr_truncate_and_writes(self):
        fd=watch_fd=trunc_fd=None
        native=ctypes.CDLL(None,use_errno=True)
        native.inotify_init1.argtypes=[ctypes.c_int]
        native.inotify_init1.restype=ctypes.c_int
        native.inotify_add_watch.argtypes=[
            ctypes.c_int,ctypes.c_char_p,ctypes.c_uint32]
        native.inotify_add_watch.restype=ctypes.c_int

        def receipts():
            try:
                raw=os.read(watch_fd,65536)
            except BlockingIOError:
                return []
            result=[];offset=0
            while offset<len(raw):
                self.assertGreaterEqual(len(raw)-offset,EVENT.size)
                wd,mask,cookie,n=EVENT.unpack_from(raw,offset)
                offset+=EVENT.size
                self.assertLessEqual(n,len(raw)-offset)
                name=raw[offset:offset+n].split(b"\x00",1)[0]
                offset+=n
                self.assertEqual(cookie,0)
                result.append((wd,mask,name))
            self.assertEqual(offset,len(raw))
            return result

        try:
            fd=os.memfd_create(
                "dec1326-generated-public-truncate",
                os.MFD_ALLOW_SEALING|os.MFD_CLOEXEC)
            self.assertEqual(os.write(fd,BEFORE),len(BEFORE))
            original=os.fstat(fd)
            watch_fd=native.inotify_init1(os.O_NONBLOCK|os.O_CLOEXEC)
            self.assertGreaterEqual(watch_fd,0)
            wd=native.inotify_add_watch(
                watch_fd,os.fsencode("/proc/self/fd/{}".format(fd)),
                IN_MODIFY|IN_DELETE_SELF)
            self.assertGreater(wd,0)
            self.assertEqual(receipts(),[])
            seals=(fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|
                   fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL)
            self.assertEqual(fcntl.fcntl(fd,fcntl.F_ADD_SEALS,seals),0)
            self.assertEqual(fcntl.fcntl(fd,fcntl.F_GET_SEALS),seals)
            self.assertEqual(receipts(),[])
            with self.assertRaises(OSError) as denied:
                os.pwrite(fd,b"XXXX",0)
            self.assertEqual(denied.exception.errno,errno.EPERM)
            with self.assertRaises(OSError) as denied:
                mmap.mmap(fd,len(BEFORE),access=mmap.ACCESS_WRITE)
            self.assertEqual(denied.exception.errno,errno.EPERM)
            self.assertEqual(receipts(),[])
            for access in (os.O_RDONLY,os.O_WRONLY,os.O_RDWR):
                with self.subTest(access=access):
                    with self.assertRaises(OSError) as denied:
                        trunc_fd=os.open("/proc/self/fd/{}".format(fd),
                            access|os.O_TRUNC|os.O_CLOEXEC)
                    self.assertEqual(denied.exception.errno,errno.EPERM)
                    self.assertIsNone(trunc_fd)
                    self.assertEqual(os.fstat(fd).st_size,len(BEFORE))
                    self.assertEqual(os.pread(fd,len(BEFORE),0),BEFORE)
                    self.assertEqual(receipts(),[])
            self.assertEqual(fcntl.fcntl(fd,fcntl.F_GET_SEALS),seals)

            self.assertEqual(
                (os.fstat(fd).st_dev,os.fstat(fd).st_ino,
                 os.fstat(fd).st_nlink),
                (original.st_dev,original.st_ino,original.st_nlink))
            os.close(fd);fd=None
            self.assertCountEqual(
                receipts(),
                [(wd,IN_DELETE_SELF,b""),(wd,IN_IGNORED,b"")])
            self.assertEqual(receipts(),[])
        finally:
            for handle in (trunc_fd,fd,watch_fd):
                if handle is not None:
                    os.close(handle)
