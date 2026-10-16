from __future__ import annotations

import ctypes
import errno
import fcntl
import os
import struct
import sys
import unittest

BEFORE=b"PUBLIC-SEALED-DATA-1234"
EVENT=struct.Struct("iIII")
IN_MODIFY=0x00000002
IN_DELETE_SELF=0x00000400
IN_IGNORED=0x00008000


@unittest.skipUnless(
    sys.platform=="linux" and hasattr(os,"memfd_create")
    and hasattr(os,"splice") and hasattr(os,"pipe2")
    and all(hasattr(fcntl,n) for n in (
        "F_ADD_SEALS","F_GET_SEALS","F_SEAL_WRITE","F_SEAL_GROW",
        "F_SEAL_SHRINK","F_SEAL_SEAL")),
    "Linux memfd sealing, native splice and inotify required")
class NativeSealedMemfdSpliceDirectionRegression(unittest.TestCase):
    def test_full_seal_allows_reading_by_splice_but_denies_pipe_to_original(self):
        fd=watch_fd=pipe_r=pipe_w=None
        libc=ctypes.CDLL(None,use_errno=True)
        libc.inotify_init1.argtypes=[ctypes.c_int]
        libc.inotify_init1.restype=ctypes.c_int
        libc.inotify_add_watch.argtypes=[
            ctypes.c_int,ctypes.c_char_p,ctypes.c_uint32]
        libc.inotify_add_watch.restype=ctypes.c_int

        def drain():
            try:
                raw=os.read(watch_fd,65536)
            except BlockingIOError:
                return []
            out=[];offset=0
            while offset<len(raw):
                self.assertGreaterEqual(len(raw)-offset,EVENT.size)
                wd,mask,cookie,n=EVENT.unpack_from(raw,offset)
                offset+=EVENT.size
                self.assertLessEqual(n,len(raw)-offset)
                name=raw[offset:offset+n].split(b"\x00",1)[0]
                offset+=n
                self.assertEqual(cookie,0)
                out.append((wd,mask,name))
            self.assertEqual(offset,len(raw))
            return out

        try:
            fd=os.memfd_create(
                "dec1312-generated-public-memfd",
                os.MFD_ALLOW_SEALING|os.MFD_CLOEXEC)
            self.assertEqual(os.write(fd,BEFORE),len(BEFORE))
            watch_fd=libc.inotify_init1(os.O_NONBLOCK|os.O_CLOEXEC)
            self.assertGreaterEqual(watch_fd,0)
            wd=libc.inotify_add_watch(
                watch_fd,os.fsencode("/proc/self/fd/{}".format(fd)),
                IN_MODIFY|IN_DELETE_SELF)
            self.assertGreater(wd,0)
            self.assertEqual(drain(),[])
            seals=(fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|
                   fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL)
            self.assertEqual(
                fcntl.fcntl(fd,fcntl.F_ADD_SEALS,seals),0)
            self.assertEqual(fcntl.fcntl(fd,fcntl.F_GET_SEALS),seals)
            pipe_r,pipe_w=os.pipe2(os.O_CLOEXEC)

            # Full seals protect ORIGINAL DATA FROM WRITES, not
            # from being READ through an existing file handle.
            self.assertEqual(
                os.splice(fd,pipe_w,len(BEFORE),offset_src=0),
                len(BEFORE))
            self.assertEqual(os.read(pipe_r,len(BEFORE)),BEFORE)
            self.assertEqual(os.pread(fd,len(BEFORE),0),BEFORE)
            self.assertEqual(drain(),[])

            # The exact same kernel syscall with reversed direction
            # to this sealed inode is a genuine forbidden write.
            self.assertEqual(os.write(pipe_w,b"XXXX"),4)
            with self.assertRaises(OSError) as denied:
                os.splice(pipe_r,fd,4,offset_dst=0)
            self.assertEqual(denied.exception.errno,errno.EPERM)
            self.assertEqual(os.pread(fd,len(BEFORE),0),BEFORE)
            self.assertEqual(os.fstat(fd).st_size,len(BEFORE))
            self.assertEqual(fcntl.fcntl(fd,fcntl.F_GET_SEALS),seals)
            self.assertEqual(drain(),[])

            # Failed destination splice must not consume payload:
            # same bytes remain in pipe to be drained normally.
            self.assertEqual(os.read(pipe_r,4),b"XXXX")
            self.assertEqual(drain(),[])
            os.close(pipe_w);pipe_w=None
            os.close(pipe_r);pipe_r=None

            os.close(fd);fd=None
            self.assertCountEqual(
                drain(),
                [(wd,IN_DELETE_SELF,b""),
                 (wd,IN_IGNORED,b"")])
        finally:
            for x in (pipe_r,pipe_w,fd,watch_fd):
                if x is not None:os.close(x)
