from __future__ import annotations

import ctypes
import errno
import fcntl
import mmap
import os
import stat
import struct
import sys
import unittest

PUBLIC=b"PUBLIC-SEALED-INODE-METADATA-CHECK"
EVENT=struct.Struct("iIII")
IN_ATTRIB=0x00000004
IN_MODIFY=0x00000002
IN_DELETE_SELF=0x00000400
IN_IGNORED=0x00008000


@unittest.skipUnless(
    sys.platform=="linux" and hasattr(os,"memfd_create")
    and all(hasattr(fcntl,x) for x in
        ("F_ADD_SEALS","F_GET_SEALS","F_SEAL_WRITE","F_SEAL_GROW",
         "F_SEAL_SHRINK","F_SEAL_SEAL")),
    "Linux native memfd full seals and inotify required")
class NativeFullSealedMemfdMetadataStillMutable(unittest.TestCase):
    def test_full_seals_deny_byte_writes_but_allow_fchmod_attrib(self):
        fd=watch_fd=None
        libc=ctypes.CDLL(None,use_errno=True)
        libc.inotify_init1.argtypes=[ctypes.c_int]
        libc.inotify_init1.restype=ctypes.c_int
        libc.inotify_add_watch.argtypes=[
            ctypes.c_int,ctypes.c_char_p,ctypes.c_uint32]
        libc.inotify_add_watch.restype=ctypes.c_int

        def receipt():
            try:
                raw=os.read(watch_fd,65536)
            except BlockingIOError:
                return []
            result=[];offset=0
            while offset<len(raw):
                self.assertGreaterEqual(len(raw)-offset,EVENT.size)
                wd,mask,cookie,count=EVENT.unpack_from(raw,offset)
                offset+=EVENT.size
                self.assertLessEqual(count,len(raw)-offset)
                name=raw[offset:offset+count].split(b"\x00",1)[0]
                offset+=count
                self.assertEqual(cookie,0)
                result.append((wd,mask,name))
            self.assertEqual(offset,len(raw))
            return result

        try:
            fd=os.memfd_create(
                "dec1319-public-anonymous-permission-test",
                os.MFD_ALLOW_SEALING|os.MFD_CLOEXEC)
            self.assertEqual(os.write(fd,PUBLIC),len(PUBLIC))
            before=os.fstat(fd)
            original_mode=stat.S_IMODE(before.st_mode)
            target_mode=0o444 if original_mode!=0o444 else 0o400
            watch_fd=libc.inotify_init1(os.O_NONBLOCK|os.O_CLOEXEC)
            self.assertGreaterEqual(watch_fd,0)
            wd=libc.inotify_add_watch(
                watch_fd,os.fsencode("/proc/self/fd/{}".format(fd)),
                IN_ATTRIB|IN_MODIFY|IN_DELETE_SELF)
            self.assertGreater(wd,0)
            self.assertEqual(receipt(),[])

            full=(
                fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|
                fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL)
            self.assertEqual(
                fcntl.fcntl(fd,fcntl.F_ADD_SEALS,full),0)
            self.assertEqual(fcntl.fcntl(fd,fcntl.F_GET_SEALS),full)
            self.assertEqual(receipt(),[])

            # Full seals protect bytes and length; they do NOT
            # permanently freeze permission metadata. Existing FD
            # may still change inode mode and issue native ATTRIB.
            os.fchmod(fd,target_mode)
            self.assertEqual(
                stat.S_IMODE(os.fstat(fd).st_mode),target_mode)
            self.assertEqual(receipt(),[(wd,IN_ATTRIB,b"")])
            self.assertEqual(fcntl.fcntl(fd,fcntl.F_GET_SEALS),full)
            self.assertEqual(os.pread(fd,len(PUBLIC),0),PUBLIC)

            # Despite old O_RDWR FD and changed mode, byte/length
            # writes remain denied by actual strong kernel seals.
            with self.assertRaises(OSError) as denied:
                os.pwrite(fd,b"XXXX",0)
            self.assertEqual(denied.exception.errno,errno.EPERM)
            with self.assertRaises(OSError) as denied:
                mmap.mmap(fd,len(PUBLIC),access=mmap.ACCESS_WRITE)
            self.assertEqual(denied.exception.errno,errno.EPERM)
            for size in (len(PUBLIC)-1,len(PUBLIC)+1):
                with self.subTest(size=size):
                    with self.assertRaises(OSError) as denied:
                        os.ftruncate(fd,size)
                    self.assertEqual(denied.exception.errno,errno.EPERM)
            self.assertEqual(os.pread(fd,len(PUBLIC),0),PUBLIC)
            self.assertEqual(receipt(),[])

            os.fchmod(fd,original_mode)
            restored=os.fstat(fd)
            self.assertEqual(
                (restored.st_dev,restored.st_ino,restored.st_size,
                 restored.st_nlink,stat.S_IMODE(restored.st_mode)),
                (before.st_dev,before.st_ino,before.st_size,
                 before.st_nlink,original_mode))
            self.assertEqual(receipt(),[(wd,IN_ATTRIB,b"")])
            self.assertEqual(fcntl.fcntl(fd,fcntl.F_GET_SEALS),full)
            self.assertEqual(os.pread(fd,len(PUBLIC),0),PUBLIC)
            self.assertEqual(receipt(),[])

            os.close(fd);fd=None
            self.assertCountEqual(
                receipt(),
                [(wd,IN_DELETE_SELF,b""),(wd,IN_IGNORED,b"")])
            self.assertEqual(receipt(),[])
        finally:
            for handle in (fd,watch_fd):
                if handle is not None:
                    os.close(handle)
