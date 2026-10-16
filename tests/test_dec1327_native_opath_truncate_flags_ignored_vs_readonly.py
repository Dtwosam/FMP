from __future__ import annotations

import ctypes
import errno
import fcntl
import os
import struct
import sys
import unittest

BEFORE=b"GENERATED-PUBLIC-PATH-ONLY-TRUNC"
EVENT=struct.Struct("iIII")
IN_MODIFY=0x00000002
IN_DELETE_SELF=0x00000400
IN_IGNORED=0x00008000

@unittest.skipUnless(
    sys.platform=="linux" and hasattr(os,"O_PATH")
    and hasattr(os,"memfd_create")
    and all(hasattr(fcntl,x) for x in
        ("F_ADD_SEALS","F_GET_SEALS","F_SEAL_WRITE",
         "F_SEAL_GROW","F_SEAL_SHRINK","F_SEAL_SEAL")),
    "Linux O_PATH and memfd sealing required")
class NativeOPathOpenTruncIgnored(unittest.TestCase):
    def test_opath_truncate_flag_is_ignored_under_weak_and_full_seals(self):
        native=ctypes.CDLL(None,use_errno=True)
        native.inotify_init1.argtypes=[ctypes.c_int]
        native.inotify_init1.restype=ctypes.c_int
        native.inotify_add_watch.argtypes=[
            ctypes.c_int,ctypes.c_char_p,ctypes.c_uint32]
        native.inotify_add_watch.restype=ctypes.c_int

        for label,seals,allows_truncate in (
            ("write-only",fcntl.F_SEAL_WRITE,True),
            ("full",fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|
             fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL,False)):
            with self.subTest(seal_case=label):
                fd=watch_fd=path_fd=read_fd=None
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
                        "dec1327-public-"+label,
                        os.MFD_CLOEXEC|os.MFD_ALLOW_SEALING)
                    self.assertEqual(os.write(fd,BEFORE),len(BEFORE))
                    old=os.fstat(fd)
                    watch_fd=native.inotify_init1(
                        os.O_NONBLOCK|os.O_CLOEXEC)
                    self.assertGreaterEqual(watch_fd,0)
                    wd=native.inotify_add_watch(
                        watch_fd,
                        os.fsencode("/proc/self/fd/{}".format(fd)),
                        IN_MODIFY|IN_DELETE_SELF)
                    self.assertGreater(wd,0)
                    self.assertEqual(drain(),[])
                    self.assertEqual(
                        fcntl.fcntl(fd,fcntl.F_ADD_SEALS,seals),0)
                    self.assertEqual(
                        fcntl.fcntl(fd,fcntl.F_GET_SEALS),seals)
                    self.assertEqual(drain(),[])

                    # O_PATH changes open semantics: O_TRUNC (and
                    # even O_WRONLY) is ignored in path-only mode.
                    # Open succeeds, but no file size/data change.
                    for access in (0,os.O_WRONLY):
                        path_fd=os.open(
                            "/proc/self/fd/{}".format(fd),
                            os.O_PATH|access|os.O_TRUNC|os.O_CLOEXEC)
                        self.assertEqual(
                            (os.fstat(path_fd).st_dev,
                             os.fstat(path_fd).st_ino,
                             os.fstat(path_fd).st_size),
                            (old.st_dev,old.st_ino,len(BEFORE)))
                        with self.assertRaises(OSError) as denied:
                            os.pread(path_fd,1,0)
                        self.assertEqual(denied.exception.errno,errno.EBADF)
                        self.assertEqual(os.pread(fd,len(BEFORE),0),BEFORE)
                        self.assertEqual(drain(),[])
                        os.close(path_fd);path_fd=None
                        self.assertEqual(drain(),[])

                    # Real O_RDONLY|O_TRUNC has entirely different
                    # kernel behavior on the SAME original inode:
                    # weak seal erases data; full size seals deny.
                    if allows_truncate:
                        read_fd=os.open(
                            "/proc/self/fd/{}".format(fd),
                            os.O_RDONLY|os.O_TRUNC|os.O_CLOEXEC)
                        self.assertEqual(os.fstat(fd).st_size,0)
                        self.assertEqual(os.pread(fd,len(BEFORE),0),b"")
                        self.assertEqual(drain(),[(wd,IN_MODIFY,b"")])
                        os.close(read_fd);read_fd=None
                        self.assertEqual(drain(),[])
                    else:
                        with self.assertRaises(OSError) as denied:
                            os.open(
                                "/proc/self/fd/{}".format(fd),
                                os.O_RDONLY|os.O_TRUNC|os.O_CLOEXEC)
                        self.assertEqual(denied.exception.errno,errno.EPERM)
                        self.assertEqual(os.pread(fd,len(BEFORE),0),BEFORE)
                        self.assertEqual(os.fstat(fd).st_size,len(BEFORE))
                        self.assertEqual(drain(),[])

                    self.assertEqual(
                        fcntl.fcntl(fd,fcntl.F_GET_SEALS),seals)
                    self.assertEqual(
                        (os.fstat(fd).st_dev,os.fstat(fd).st_ino),
                        (old.st_dev,old.st_ino))
                    os.close(fd);fd=None
                    self.assertCountEqual(
                        drain(),
                        [(wd,IN_DELETE_SELF,b""),
                         (wd,IN_IGNORED,b"")])
                    self.assertEqual(drain(),[])
                finally:
                    for handle in (path_fd,read_fd,fd,watch_fd):
                        if handle is not None:
                            os.close(handle)
