from __future__ import annotations

import ctypes
import errno
import fcntl
import os
import struct
import sys
import unittest

BEFORE=b"GENERATED-PUBLIC-MINIMAL-SEAL-BYTES"
EVENT=struct.Struct("iIII")
IN_MODIFY=0x00000002
IN_DELETE_SELF=0x00000400
IN_IGNORED=0x00008000

@unittest.skipUnless(
    sys.platform=="linux" and hasattr(os,"memfd_create")
    and os.path.isdir("/proc/self/fd")
    and all(hasattr(fcntl,n) for n in
        ("F_ADD_SEALS","F_GET_SEALS","F_SEAL_WRITE",
         "F_SEAL_FUTURE_WRITE","F_SEAL_GROW","F_SEAL_SHRINK")),
    "native Linux memfd sealing and procfd O_TRUNC required")
class NativeMinimalShrinkSealOpenTruncateBoundary(unittest.TestCase):
    def test_shrink_seal_not_write_or_grow_is_decisive_for_open_trunc(self):
        libc=ctypes.CDLL(None,use_errno=True)
        libc.inotify_init1.argtypes=[ctypes.c_int]
        libc.inotify_init1.restype=ctypes.c_int
        libc.inotify_add_watch.argtypes=[
            ctypes.c_int,ctypes.c_char_p,ctypes.c_uint32]
        libc.inotify_add_watch.restype=ctypes.c_int
        cases=(
            ("grow-only",fcntl.F_SEAL_GROW,True),
            ("write-grow",fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW,True),
            ("shrink-only",fcntl.F_SEAL_SHRINK,False),
            ("write-shrink",fcntl.F_SEAL_WRITE|fcntl.F_SEAL_SHRINK,False),
            ("future-shrink",
             fcntl.F_SEAL_FUTURE_WRITE|fcntl.F_SEAL_SHRINK,False),
        )
        for label,seal,allows in cases:
            with self.subTest(case=label):
                fd=watch_fd=trunc_fd=None
                def read_events():
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
                        "dec1328-generated-public-"+label,
                        os.MFD_CLOEXEC|os.MFD_ALLOW_SEALING)
                    self.assertEqual(os.write(fd,BEFORE),len(BEFORE))
                    original=os.fstat(fd)
                    watch_fd=libc.inotify_init1(
                        os.O_NONBLOCK|os.O_CLOEXEC)
                    self.assertGreaterEqual(watch_fd,0)
                    wd=libc.inotify_add_watch(
                        watch_fd,
                        os.fsencode("/proc/self/fd/{}".format(fd)),
                        IN_MODIFY|IN_DELETE_SELF)
                    self.assertGreater(wd,0)
                    self.assertEqual(read_events(),[])
                    self.assertEqual(
                        fcntl.fcntl(fd,fcntl.F_ADD_SEALS,seal),0)
                    self.assertEqual(fcntl.fcntl(fd,fcntl.F_GET_SEALS),seal)
                    self.assertEqual(read_events(),[])

                    if allows:
                        # Even F_SEAL_WRITE together with GROW
                        # does not stop destructive shrink at open.
                        trunc_fd=os.open(
                            "/proc/self/fd/{}".format(fd),
                            os.O_RDONLY|os.O_TRUNC|os.O_CLOEXEC)
                        self.assertEqual(os.fstat(fd).st_size,0)
                        self.assertEqual(os.pread(fd,len(BEFORE),0),b"")
                        self.assertEqual(
                            read_events(),[(wd,IN_MODIFY,b"")])
                        os.close(trunc_fd);trunc_fd=None
                        self.assertEqual(read_events(),[])
                    else:
                        # Any tested combination with SHRINK
                        # denies the very same O_RDONLY|O_TRUNC.
                        with self.assertRaises(OSError) as denied:
                            os.open(
                                "/proc/self/fd/{}".format(fd),
                                os.O_RDONLY|os.O_TRUNC|os.O_CLOEXEC)
                        self.assertEqual(denied.exception.errno,errno.EPERM)
                        self.assertEqual(os.fstat(fd).st_size,len(BEFORE))
                        self.assertEqual(os.pread(fd,len(BEFORE),0),BEFORE)
                        self.assertEqual(read_events(),[])

                    self.assertEqual(fcntl.fcntl(fd,fcntl.F_GET_SEALS),seal)
                    self.assertEqual(
                        (os.fstat(fd).st_dev,os.fstat(fd).st_ino),
                        (original.st_dev,original.st_ino))
                    os.close(fd);fd=None
                    self.assertCountEqual(
                        read_events(),
                        [(wd,IN_DELETE_SELF,b""),
                         (wd,IN_IGNORED,b"")])
                    self.assertEqual(read_events(),[])
                finally:
                    for handle in (trunc_fd,fd,watch_fd):
                        if handle is not None:
                            os.close(handle)
