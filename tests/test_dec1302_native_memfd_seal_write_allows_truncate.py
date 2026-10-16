from __future__ import annotations

import ctypes
import errno
import fcntl
import mmap
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
    and all(hasattr(fcntl,n) for n in
        ("F_ADD_SEALS","F_GET_SEALS","F_SEAL_WRITE")),
    "Linux memfd seals and native inotify required")
class NativeMemfdWriteSealDoesNotPreventTruncate(unittest.TestCase):
    def test_seal_write_denies_pwrite_but_size_changes_still_destroy_bytes(self):
        fd=watch_fd=None
        libc=ctypes.CDLL(None,use_errno=True)
        libc.inotify_init1.argtypes=[ctypes.c_int]
        libc.inotify_init1.restype=ctypes.c_int
        libc.inotify_add_watch.argtypes=[
            ctypes.c_int,ctypes.c_char_p,ctypes.c_uint32]
        libc.inotify_add_watch.restype=ctypes.c_int

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
                "dec1302-generated-public-memfd",
                os.MFD_ALLOW_SEALING|os.MFD_CLOEXEC)
            self.assertEqual(os.write(fd,BEFORE),len(BEFORE))
            watch_fd=libc.inotify_init1(os.O_NONBLOCK|os.O_CLOEXEC)
            self.assertGreaterEqual(watch_fd,0)
            wd=libc.inotify_add_watch(
                watch_fd,os.fsencode("/proc/self/fd/{}".format(fd)),
                IN_MODIFY|IN_DELETE_SELF)
            self.assertGreater(wd,0)
            self.assertEqual(drain(),[])
            self.assertEqual(
                fcntl.fcntl(fd,fcntl.F_ADD_SEALS,fcntl.F_SEAL_WRITE),0)
            self.assertEqual(
                fcntl.fcntl(fd,fcntl.F_GET_SEALS),fcntl.F_SEAL_WRITE)
            self.assertEqual(drain(),[])

            # F_SEAL_WRITE alone denies direct data writes and the
            # creation of a new writable shared mapping.
            with self.assertRaises(OSError) as denied:
                os.pwrite(fd,b"XXXX",0)
            self.assertEqual(denied.exception.errno,errno.EPERM)
            with self.assertRaises(OSError) as denied:
                mmap.mmap(fd,len(BEFORE),access=mmap.ACCESS_WRITE)
            self.assertEqual(denied.exception.errno,errno.EPERM)
            self.assertEqual(os.pread(fd,len(BEFORE),0),BEFORE)
            self.assertEqual(drain(),[])

            # Missing GROW/SHRINK seals is a real integrity gap:
            # ftruncate removes a byte, then regrowing to old length
            # yields a zero byte instead of the original final byte.
            os.ftruncate(fd,len(BEFORE)-1)
            self.assertEqual(
                drain(),[(wd,IN_MODIFY,b"")])
            self.assertEqual(os.fstat(fd).st_size,len(BEFORE)-1)
            self.assertEqual(
                os.pread(fd,len(BEFORE),0),BEFORE[:-1])
            os.ftruncate(fd,len(BEFORE))
            self.assertEqual(
                drain(),[(wd,IN_MODIFY,b"")])
            self.assertEqual(os.fstat(fd).st_size,len(BEFORE))
            self.assertEqual(
                os.pread(fd,len(BEFORE),0),BEFORE[:-1]+b"\x00")
            self.assertNotEqual(
                os.pread(fd,len(BEFORE),0),BEFORE)
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
