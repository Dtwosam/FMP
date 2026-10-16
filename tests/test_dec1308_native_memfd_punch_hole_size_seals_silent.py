from __future__ import annotations

import ctypes
import errno
import fcntl
import mmap
import os
import struct
import sys
import unittest

BEFORE=b"A"*4096+b"B"*4096+b"C"*4096
EVENT=struct.Struct("iIII")
IN_MODIFY=0x00000002
IN_DELETE_SELF=0x00000400
IN_IGNORED=0x00008000


@unittest.skipUnless(
    sys.platform=="linux" and hasattr(os,"memfd_create")
    and all(hasattr(fcntl,n) for n in
        ("F_ADD_SEALS","F_GET_SEALS","F_SEAL_GROW",
         "F_SEAL_SHRINK","F_SEAL_WRITE")),
    "Linux memfd seals and native inotify required")
class NativeMemfdPunchHoleSizeSealsSilentDataLoss(unittest.TestCase):
    def test_size_seals_allow_silent_hole_punch_but_write_seal_denies(self):
        fd=watch_fd=None
        libc=ctypes.CDLL(None,use_errno=True)
        libc.inotify_init1.argtypes=[ctypes.c_int]
        libc.inotify_init1.restype=ctypes.c_int
        libc.inotify_add_watch.argtypes=[
            ctypes.c_int,ctypes.c_char_p,ctypes.c_uint32]
        libc.inotify_add_watch.restype=ctypes.c_int
        libc.fallocate.argtypes=[
            ctypes.c_int,ctypes.c_int,
            ctypes.c_longlong,ctypes.c_longlong]
        libc.fallocate.restype=ctypes.c_int

        def drain():
            try:
                data=os.read(watch_fd,65536)
            except BlockingIOError:
                return []
            result=[];pos=0
            while pos<len(data):
                self.assertGreaterEqual(len(data)-pos,EVENT.size)
                wd,mask,cookie,n=EVENT.unpack_from(data,pos)
                pos+=EVENT.size
                self.assertLessEqual(n,len(data)-pos)
                name=data[pos:pos+n].split(b"\x00",1)[0]
                pos+=n
                self.assertEqual(cookie,0)
                result.append((wd,mask,name))
            self.assertEqual(pos,len(data))
            return result

        try:
            fd=os.memfd_create(
                "dec1308-generated-public-memfd",
                os.MFD_ALLOW_SEALING|os.MFD_CLOEXEC)
            self.assertEqual(os.write(fd,BEFORE),len(BEFORE))
            watch_fd=libc.inotify_init1(os.O_NONBLOCK|os.O_CLOEXEC)
            self.assertGreaterEqual(watch_fd,0)
            wd=libc.inotify_add_watch(
                watch_fd,os.fsencode("/proc/self/fd/{}".format(fd)),
                IN_MODIFY|IN_DELETE_SELF)
            self.assertGreater(wd,0)
            self.assertEqual(drain(),[])
            # Size seals reject ftruncate but do NOT protect
            # existing page contents against native hole punching.
            only_size=fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK
            self.assertEqual(
                fcntl.fcntl(fd,fcntl.F_ADD_SEALS,only_size),0)
            self.assertEqual(fcntl.fcntl(fd,fcntl.F_GET_SEALS),only_size)
            for length in (len(BEFORE)-1,len(BEFORE)+1):
                with self.assertRaises(OSError) as denied:
                    os.ftruncate(fd,length)
                self.assertEqual(denied.exception.errno,errno.EPERM)
            self.assertEqual(os.pread(fd,len(BEFORE),0),BEFORE)
            self.assertEqual(drain(),[])

            # Actual tmpfs anonymous backing middle page B is
            # HOLE-PUNCHED through libc fallocate(PUNCH|KEEP_SIZE).
            # Size is unchanged, data becomes zeros and Linux
            # native inotify IN_MODIFY remains SILENT.
            punched=BEFORE[:4096]+b"\x00"*4096+BEFORE[8192:]
            ctypes.set_errno(0)
            self.assertEqual(
                libc.fallocate(fd,0x03,4096,4096),0,
                os.strerror(ctypes.get_errno()))
            self.assertEqual(os.fstat(fd).st_size,len(BEFORE))
            self.assertEqual(os.pread(fd,len(BEFORE),0),punched)
            self.assertNotEqual(punched,BEFORE)
            self.assertEqual(drain(),[])
            ctypes.set_errno(0)
            self.assertEqual(
                libc.fallocate(fd,0x03,4096,4096),0,
                os.strerror(ctypes.get_errno()))
            self.assertEqual(os.pread(fd,len(BEFORE),0),punched)
            self.assertEqual(drain(),[])

            # Add strong WRITE seal after the changes. A fresh
            # hole punch over untouched C is now truly EPERM,
            # proving the change in effective data protection.
            guarded=only_size|fcntl.F_SEAL_WRITE
            self.assertEqual(
                fcntl.fcntl(fd,fcntl.F_ADD_SEALS,fcntl.F_SEAL_WRITE),0)
            self.assertEqual(fcntl.fcntl(fd,fcntl.F_GET_SEALS),guarded)
            ctypes.set_errno(0)
            self.assertEqual(libc.fallocate(fd,0x03,8192,4096),-1)
            self.assertEqual(ctypes.get_errno(),errno.EPERM)
            self.assertEqual(os.pread(fd,len(BEFORE),0),punched)
            self.assertEqual(os.pread(fd,4096,8192),b"C"*4096)
            self.assertEqual(os.fstat(fd).st_size,len(BEFORE))
            self.assertEqual(drain(),[])

            # Disposable anonymous object is retired without any
            # protected annual path, evidence or production source.
            os.close(fd);fd=None
            self.assertCountEqual(
                drain(),
                [(wd,IN_DELETE_SELF,b""),
                 (wd,IN_IGNORED,b"")])
        finally:
            if fd is not None:os.close(fd)
            if watch_fd is not None:os.close(watch_fd)
