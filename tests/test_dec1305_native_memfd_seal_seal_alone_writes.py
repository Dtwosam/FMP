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
        ("F_ADD_SEALS","F_GET_SEALS","F_SEAL_WRITE","F_SEAL_SEAL")),
    "Linux memfd seals and native inotify required")
class NativeMemfdSealSealAlonePermitsDataMutation(unittest.TestCase):
    def test_seal_seal_only_prevents_new_seals_not_file_writes(self):
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
                "dec1305-generated-public-memfd",
                os.MFD_ALLOW_SEALING|os.MFD_CLOEXEC)
            self.assertEqual(os.write(fd,BEFORE),len(BEFORE))
            watch_fd=libc.inotify_init1(os.O_NONBLOCK|os.O_CLOEXEC)
            self.assertGreaterEqual(watch_fd,0)
            wd=libc.inotify_add_watch(
                watch_fd,os.fsencode("/proc/self/fd/{}".format(fd)),
                IN_MODIFY|IN_DELETE_SELF)
            self.assertGreater(wd,0)
            self.assertEqual(drain(),[])
            # F_SEAL_SEAL irreversibly blocks ADDING seals, but
            # says nothing about modifying the data right now.
            self.assertEqual(
                fcntl.fcntl(fd,fcntl.F_ADD_SEALS,fcntl.F_SEAL_SEAL),0)
            self.assertEqual(
                fcntl.fcntl(fd,fcntl.F_GET_SEALS),fcntl.F_SEAL_SEAL)
            with self.assertRaises(OSError) as denied:
                fcntl.fcntl(fd,fcntl.F_ADD_SEALS,fcntl.F_SEAL_WRITE)
            self.assertEqual(denied.exception.errno,errno.EPERM)
            self.assertEqual(drain(),[])

            # Ordinary pwrite changes ORIGINAL anonymous inode
            # bytes and emits real native IN_MODIFY even though
            # the memfd seal set can no longer be extended.
            changed=b"XXXX"+BEFORE[4:]
            self.assertEqual(os.pwrite(fd,b"XXXX",0),4)
            self.assertEqual(os.pread(fd,len(BEFORE),0),changed)
            self.assertEqual(drain(),[(wd,IN_MODIFY,b"")])
            self.assertEqual(os.pwrite(fd,BEFORE[:4],0),4)
            self.assertEqual(os.pread(fd,len(BEFORE),0),BEFORE)
            self.assertEqual(drain(),[(wd,IN_MODIFY,b"")])

            # Data can also be destroyed by truncation, then
            # subsequently restored because NO write/size seal
            # exists. Each true mutation has a native receipt.
            os.ftruncate(fd,len(BEFORE)-1)
            self.assertEqual(drain(),[(wd,IN_MODIFY,b"")])
            self.assertEqual(
                os.pread(fd,len(BEFORE),0),BEFORE[:-1])
            os.ftruncate(fd,len(BEFORE))
            self.assertEqual(drain(),[(wd,IN_MODIFY,b"")])
            self.assertEqual(
                os.pread(fd,len(BEFORE),0),BEFORE[:-1]+b"\x00")
            self.assertEqual(os.pwrite(fd,BEFORE[-1:],len(BEFORE)-1),1)
            self.assertEqual(drain(),[(wd,IN_MODIFY,b"")])
            self.assertEqual(os.pread(fd,len(BEFORE),0),BEFORE)
            self.assertEqual(os.fstat(fd).st_size,len(BEFORE))
            self.assertEqual(
                fcntl.fcntl(fd,fcntl.F_GET_SEALS),fcntl.F_SEAL_SEAL)
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
