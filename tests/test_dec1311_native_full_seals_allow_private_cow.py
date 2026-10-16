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
        ("F_ADD_SEALS","F_GET_SEALS","F_SEAL_WRITE",
         "F_SEAL_GROW","F_SEAL_SHRINK","F_SEAL_SEAL",
         "F_SEAL_FUTURE_WRITE")),
    "Linux memfd seals and native inotify required")
class NativeFullySealedMemfdPrivateCowStillWritable(unittest.TestCase):
    def test_full_seals_reject_original_writes_but_permit_private_cow(self):
        fd=watch_fd=None
        private_map=None
        read_map=None
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
                "dec1311-generated-public-memfd",
                os.MFD_ALLOW_SEALING|os.MFD_CLOEXEC)
            self.assertEqual(os.write(fd,BEFORE),len(BEFORE))
            watch_fd=libc.inotify_init1(os.O_NONBLOCK|os.O_CLOEXEC)
            self.assertGreaterEqual(watch_fd,0)
            wd=libc.inotify_add_watch(
                watch_fd,os.fsencode("/proc/self/fd/{}".format(fd)),
                IN_MODIFY|IN_DELETE_SELF)
            self.assertGreater(wd,0)
            self.assertEqual(drain(),[])
            full_seals=(
                fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|
                fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL)
            self.assertEqual(
                fcntl.fcntl(fd,fcntl.F_ADD_SEALS,full_seals),0)
            self.assertEqual(
                fcntl.fcntl(fd,fcntl.F_GET_SEALS),full_seals)
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

            # Even a fully sealed ORIGINAL memfd can be privately
            # mapped writable. This mutates COW memory only, not
            # the sealed original inode data.
            private_map=mmap.mmap(
                fd,len(BEFORE),access=mmap.ACCESS_COPY)
            self.assertEqual(private_map[:],BEFORE)
            private_map[:4]=b"XXXX"
            private_map.flush()
            self.assertEqual(private_map[:],b"XXXX"+BEFORE[4:])
            self.assertEqual(os.pread(fd,len(BEFORE),0),BEFORE)
            self.assertEqual(fcntl.fcntl(fd,fcntl.F_GET_SEALS),full_seals)
            self.assertEqual(drain(),[])
            private_map.close();private_map=None
            self.assertEqual(os.pread(fd,len(BEFORE),0),BEFORE)
            self.assertEqual(drain(),[])

            read_map=mmap.mmap(
                fd,len(BEFORE),access=mmap.ACCESS_READ)
            self.assertEqual(read_map[:],BEFORE)
            read_map.close();read_map=None
            self.assertEqual(drain(),[])

            # Unlike F_SEAL_WRITE by itself, the combined GROW
            # and SHRINK seals deny both size changes. F_SEAL_SEAL
            # also makes the precise seal set irreversible.
            for size in (len(BEFORE)-1,len(BEFORE)+1):
                with self.subTest(size=size):
                    with self.assertRaises(OSError) as denied:
                        os.ftruncate(fd,size)
                    self.assertEqual(denied.exception.errno,errno.EPERM)
                    self.assertEqual(os.fstat(fd).st_size,len(BEFORE))
                    self.assertEqual(os.pread(fd,len(BEFORE),0),BEFORE)
                    self.assertEqual(drain(),[])
            with self.assertRaises(OSError) as denied:
                fcntl.fcntl(fd,fcntl.F_ADD_SEALS,fcntl.F_SEAL_FUTURE_WRITE)
            self.assertEqual(denied.exception.errno,errno.EPERM)
            self.assertEqual(
                fcntl.fcntl(fd,fcntl.F_GET_SEALS),full_seals)
            self.assertEqual(os.pread(fd,len(BEFORE),0),BEFORE)
            self.assertEqual(drain(),[])

            # Disposable anonymous object is retired without any
            # protected annual path, evidence or production source.
            os.close(fd);fd=None
            self.assertCountEqual(
                drain(),
                [(wd,IN_DELETE_SELF,b""),
                 (wd,IN_IGNORED,b"")])
        finally:
            if private_map is not None:private_map.close()
            if read_map is not None:read_map.close()
            if fd is not None:os.close(fd)
            if watch_fd is not None:os.close(watch_fd)
