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
    and os.path.isdir("/proc/self/fd")
    and all(hasattr(fcntl,n) for n in (
        "F_ADD_SEALS","F_GET_SEALS","F_SEAL_WRITE",
        "F_SEAL_GROW","F_SEAL_SHRINK","F_SEAL_SEAL",
        "F_SEAL_FUTURE_WRITE")),
    "Linux memfd seals, procfs and native inotify required")
class NativeFullySealedMemfdIndependentO_RDWRReopen(unittest.TestCase):
    def test_full_seals_still_deny_new_rdwr_description_after_original_closes(self):
        fd=reopened=watch_fd=None
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
            records=[];at=0
            while at<len(raw):
                self.assertGreaterEqual(len(raw)-at,EVENT.size)
                wd,mask,cookie,n=EVENT.unpack_from(raw,at)
                at+=EVENT.size
                self.assertLessEqual(n,len(raw)-at)
                name=raw[at:at+n].split(b"\x00",1)[0];at+=n
                self.assertEqual(cookie,0)
                records.append((wd,mask,name))
            self.assertEqual(at,len(raw))
            return records

        try:
            fd=os.memfd_create(
                "dec1316-generated-public-memfd",
                os.MFD_ALLOW_SEALING|os.MFD_CLOEXEC)
            self.assertEqual(os.write(fd,BEFORE),len(BEFORE))
            initial=os.fstat(fd)
            watch_fd=libc.inotify_init1(os.O_NONBLOCK|os.O_CLOEXEC)
            self.assertGreaterEqual(watch_fd,0)
            wd=libc.inotify_add_watch(
                watch_fd,os.fsencode("/proc/self/fd/{}".format(fd)),
                IN_MODIFY|IN_DELETE_SELF)
            self.assertGreater(wd,0)
            self.assertEqual(drain(),[])
            complete=(
                fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|
                fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL)
            self.assertEqual(
                fcntl.fcntl(fd,fcntl.F_ADD_SEALS,complete),0)
            self.assertEqual(fcntl.fcntl(fd,fcntl.F_GET_SEALS),complete)

            # A NEW O_RDWR description of the same sealed inode
            # can be opened via procfs. Its O_RDWR bits do NOT
            # override kernel enforced seals.
            reopened=os.open(
                "/proc/self/fd/{}".format(fd),
                os.O_RDWR|os.O_CLOEXEC)
            after=os.fstat(reopened)
            self.assertEqual(
                (initial.st_dev,initial.st_ino,initial.st_size),
                (after.st_dev,after.st_ino,after.st_size))
            self.assertEqual(
                fcntl.fcntl(reopened,fcntl.F_GET_SEALS),complete)
            self.assertEqual(os.pread(reopened,len(BEFORE),0),BEFORE)
            self.assertEqual(drain(),[])

            # Close the ORIGINAL FD first. The reopened FD pins
            # the same anonymous inode and its active watch.
            os.close(fd);fd=None
            self.assertEqual(drain(),[])
            self.assertEqual(os.pread(reopened,len(BEFORE),0),BEFORE)
            for attempt in (
                lambda:os.pwrite(reopened,b"XXXX",0),
                lambda:os.ftruncate(reopened,len(BEFORE)-1),
                lambda:os.ftruncate(reopened,len(BEFORE)+1),
                lambda:mmap.mmap(
                    reopened,len(BEFORE),access=mmap.ACCESS_WRITE),
                lambda:fcntl.fcntl(
                    reopened,fcntl.F_ADD_SEALS,
                    fcntl.F_SEAL_FUTURE_WRITE),
            ):
                with self.assertRaises(OSError) as denied:
                    attempt()
                self.assertEqual(denied.exception.errno,errno.EPERM)
                self.assertEqual(os.fstat(reopened).st_size,len(BEFORE))
                self.assertEqual(os.pread(reopened,len(BEFORE),0),BEFORE)
                self.assertEqual(drain(),[])
            self.assertEqual(
                fcntl.fcntl(reopened,fcntl.F_GET_SEALS),complete)

            # The last FD, not the original descriptor, actually
            # retires the watched anonymous inode.
            os.close(reopened);reopened=None
            self.assertCountEqual(
                drain(),
                [(wd,IN_DELETE_SELF,b""),
                 (wd,IN_IGNORED,b"")])
        finally:
            for descriptor in (reopened,fd,watch_fd):
                if descriptor is not None:os.close(descriptor)
