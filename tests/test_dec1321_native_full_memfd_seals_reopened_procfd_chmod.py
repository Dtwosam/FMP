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

PUBLIC=b"PUBLIC-REOPENED-SEALED-INODE-ONLY"
EVENT=struct.Struct("iIII")
IN_ATTRIB=0x00000004
IN_MODIFY=0x00000002
IN_DELETE_SELF=0x00000400
IN_IGNORED=0x00008000

@unittest.skipUnless(
    sys.platform=="linux" and hasattr(os,"memfd_create")
    and os.path.isdir("/proc/self/fd")
    and all(hasattr(fcntl,n) for n in
        ("F_ADD_SEALS","F_GET_SEALS","F_SEAL_WRITE",
         "F_SEAL_GROW","F_SEAL_SHRINK","F_SEAL_SEAL")),
    "native Linux memfd sealing, procfs and inotify required")
class NativeFullySealedMemfdReopenedModeMutation(unittest.TestCase):
    def test_procfd_rdwr_after_original_close_changes_mode_not_bytes(self):
        fd=reopened=watch_fd=None
        libc=ctypes.CDLL(None,use_errno=True)
        libc.inotify_init1.argtypes=[ctypes.c_int]
        libc.inotify_init1.restype=ctypes.c_int
        libc.inotify_add_watch.argtypes=[
            ctypes.c_int,ctypes.c_char_p,ctypes.c_uint32]
        libc.inotify_add_watch.restype=ctypes.c_int

        def events():
            try:
                raw=os.read(watch_fd,65536)
            except BlockingIOError:
                return []
            observed=[];pos=0
            while pos<len(raw):
                self.assertGreaterEqual(len(raw)-pos,EVENT.size)
                wd,mask,cookie,n=EVENT.unpack_from(raw,pos)
                pos+=EVENT.size
                self.assertLessEqual(n,len(raw)-pos)
                name=raw[pos:pos+n].split(b"\x00",1)[0];pos+=n
                self.assertEqual(cookie,0)
                observed.append((wd,mask,name))
            self.assertEqual(pos,len(raw))
            return observed

        try:
            fd=os.memfd_create(
                "dec1321-generated-public-procfd-seal",
                os.MFD_ALLOW_SEALING|os.MFD_CLOEXEC)
            self.assertEqual(os.write(fd,PUBLIC),len(PUBLIC))
            original=os.fstat(fd)
            original_mode=stat.S_IMODE(original.st_mode)
            sealed=(
                fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|
                fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL)
            self.assertEqual(fcntl.fcntl(fd,fcntl.F_ADD_SEALS,sealed),0)
            self.assertEqual(fcntl.fcntl(fd,fcntl.F_GET_SEALS),sealed)
            watch_fd=libc.inotify_init1(os.O_NONBLOCK|os.O_CLOEXEC)
            self.assertGreaterEqual(watch_fd,0)
            wd=libc.inotify_add_watch(
                watch_fd,
                os.fsencode("/proc/self/fd/{}".format(fd)),
                IN_ATTRIB|IN_MODIFY|IN_DELETE_SELF)
            self.assertGreater(wd,0)
            self.assertEqual(events(),[])

            # Obtain separate native O_RDWR description BEFORE
            # closing original FD; full data seals survive this.
            reopened=os.open(
                "/proc/self/fd/{}".format(fd),
                os.O_RDWR|os.O_CLOEXEC)
            self.assertEqual(
                (os.fstat(reopened).st_dev,os.fstat(reopened).st_ino,
                 os.fstat(reopened).st_size),
                (original.st_dev,original.st_ino,len(PUBLIC)))
            self.assertEqual(fcntl.fcntl(reopened,fcntl.F_GET_SEALS),sealed)
            os.close(fd);fd=None
            self.assertEqual(events(),[])

            # The independently reopened description can still
            # change inode metadata even after original FD closes.
            target=0o444 if original_mode!=0o444 else 0o400
            os.fchmod(reopened,target)
            self.assertEqual(
                stat.S_IMODE(os.fstat(reopened).st_mode),target)
            self.assertEqual(events(),[(wd,IN_ATTRIB,b"")])
            self.assertEqual(os.pread(reopened,len(PUBLIC),0),PUBLIC)
            self.assertEqual(fcntl.fcntl(reopened,fcntl.F_GET_SEALS),sealed)

            # Full seals remain strong for CONTENT and SIZE despite
            # reopened O_RDWR and changed inode mode.
            with self.assertRaises(OSError) as denied:
                os.pwrite(reopened,b"XXXX",0)
            self.assertEqual(denied.exception.errno,errno.EPERM)
            with self.assertRaises(OSError) as denied:
                mmap.mmap(reopened,len(PUBLIC),access=mmap.ACCESS_WRITE)
            self.assertEqual(denied.exception.errno,errno.EPERM)
            for length in (len(PUBLIC)-1,len(PUBLIC)+1):
                with self.subTest(length=length):
                    with self.assertRaises(OSError) as denied:
                        os.ftruncate(reopened,length)
                    self.assertEqual(denied.exception.errno,errno.EPERM)
            self.assertEqual(events(),[])
            self.assertEqual(os.pread(reopened,len(PUBLIC),0),PUBLIC)

            os.fchmod(reopened,original_mode)
            final=os.fstat(reopened)
            self.assertEqual(events(),[(wd,IN_ATTRIB,b"")])
            self.assertEqual(
                (final.st_dev,final.st_ino,final.st_size,final.st_nlink,
                 stat.S_IMODE(final.st_mode)),
                (original.st_dev,original.st_ino,original.st_size,
                 original.st_nlink,original_mode))
            self.assertEqual(fcntl.fcntl(reopened,fcntl.F_GET_SEALS),sealed)
            self.assertEqual(os.pread(reopened,len(PUBLIC),0),PUBLIC)
            self.assertEqual(events(),[])

            os.close(reopened);reopened=None
            self.assertCountEqual(
                events(),
                [(wd,IN_DELETE_SELF,b""),(wd,IN_IGNORED,b"")])
            self.assertEqual(events(),[])
        finally:
            for handle in (fd,reopened,watch_fd):
                if handle is not None:
                    os.close(handle)
