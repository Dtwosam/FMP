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
IN_ACCESS=0x00000001
IN_MODIFY=0x00000002
IN_DELETE_SELF=0x00000400
IN_IGNORED=0x00008000


@unittest.skipUnless(
    sys.platform=="linux"
    and hasattr(os,"memfd_create")
    and hasattr(os,"copy_file_range")
    and all(hasattr(fcntl,field) for field in
        ("F_ADD_SEALS","F_GET_SEALS","F_SEAL_WRITE",
         "F_SEAL_GROW","F_SEAL_SHRINK","F_SEAL_SEAL")),
    "native Linux memfd seals, copy_file_range and inotify required")
class NativeMemfdCopyFileRangeSilentWriteRegression(unittest.TestCase):
    def test_copy_from_full_sealed_memfd_writes_unsealed_dest_without_modify(self):
        source_fd=destination_fd=watch_fd=None
        native=ctypes.CDLL(None,use_errno=True)
        native.inotify_init1.argtypes=[ctypes.c_int]
        native.inotify_init1.restype=ctypes.c_int
        native.inotify_add_watch.argtypes=[
            ctypes.c_int,ctypes.c_char_p,ctypes.c_uint32]
        native.inotify_add_watch.restype=ctypes.c_int

        def drain():
            try:
                raw=os.read(watch_fd,65536)
            except BlockingIOError:
                return []
            records=[];offset=0
            while offset<len(raw):
                self.assertGreaterEqual(len(raw)-offset,EVENT.size)
                wd,mask,cookie,length=EVENT.unpack_from(raw,offset)
                offset+=EVENT.size
                self.assertLessEqual(length,len(raw)-offset)
                name=raw[offset:offset+length].split(b"\x00",1)[0]
                offset+=length
                self.assertEqual(cookie,0)
                records.append((wd,mask,name))
            self.assertEqual(offset,len(raw))
            return records

        try:
            flags=os.MFD_ALLOW_SEALING|os.MFD_CLOEXEC
            source_fd=os.memfd_create(
                "dec1314-generated-public-copy-source",flags)
            destination_fd=os.memfd_create(
                "dec1314-generated-public-copy-destination",flags)
            initial_destination=b"?"*len(BEFORE)
            self.assertEqual(os.write(source_fd,BEFORE),len(BEFORE))
            self.assertEqual(
                os.write(destination_fd,initial_destination),len(BEFORE))
            self.assertNotEqual(BEFORE,initial_destination)
            source_stat=os.fstat(source_fd)
            destination_stat=os.fstat(destination_fd)
            self.assertEqual(source_stat.st_size,len(BEFORE))
            self.assertEqual(destination_stat.st_size,len(BEFORE))
            self.assertNotEqual(source_stat.st_ino,destination_stat.st_ino)

            watch_fd=native.inotify_init1(os.O_NONBLOCK|os.O_CLOEXEC)
            self.assertGreaterEqual(watch_fd,0)
            mask=IN_ACCESS|IN_MODIFY|IN_DELETE_SELF
            source_wd=native.inotify_add_watch(
                watch_fd,
                os.fsencode("/proc/self/fd/{}".format(source_fd)),mask)
            destination_wd=native.inotify_add_watch(
                watch_fd,
                os.fsencode("/proc/self/fd/{}".format(destination_fd)),mask)
            self.assertGreater(source_wd,0)
            self.assertGreater(destination_wd,0)
            self.assertNotEqual(source_wd,destination_wd)
            self.assertEqual(drain(),[])

            full_seals=(
                fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|
                fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL)
            self.assertEqual(
                fcntl.fcntl(source_fd,fcntl.F_ADD_SEALS,full_seals),0)
            self.assertEqual(
                fcntl.fcntl(source_fd,fcntl.F_GET_SEALS),full_seals)
            self.assertEqual(
                fcntl.fcntl(destination_fd,fcntl.F_GET_SEALS),0)
            self.assertEqual(drain(),[])

            # Source READ is allowed under full source seals.
            # In-kernel copy changes a different, unsealed inode.
            # On Linux tmpfs/memfd this does not emit IN_ACCESS
            # or IN_MODIFY on either original anonymous inode.
            copied=os.copy_file_range(
                source_fd,destination_fd,len(BEFORE),
                offset_src=0,offset_dst=0)
            self.assertEqual(copied,len(BEFORE))
            self.assertEqual(os.pread(source_fd,len(BEFORE),0),BEFORE)
            self.assertEqual(
                os.pread(destination_fd,len(BEFORE),0),BEFORE)
            self.assertEqual(
                (os.fstat(source_fd).st_size,
                 os.fstat(destination_fd).st_size),
                (len(BEFORE),len(BEFORE)))
            self.assertEqual(drain(),[])
            self.assertEqual(
                fcntl.fcntl(source_fd,fcntl.F_GET_SEALS),full_seals)
            self.assertEqual(
                fcntl.fcntl(destination_fd,fcntl.F_GET_SEALS),0)

            # With destination now sealed, identical copy is
            # genuinely rejected, without changing either inode.
            self.assertEqual(
                fcntl.fcntl(
                    destination_fd,fcntl.F_ADD_SEALS,full_seals),0)
            self.assertEqual(
                fcntl.fcntl(destination_fd,fcntl.F_GET_SEALS),full_seals)
            with self.assertRaises(OSError) as denied:
                os.copy_file_range(
                    source_fd,destination_fd,len(BEFORE),
                    offset_src=0,offset_dst=0)
            self.assertEqual(denied.exception.errno,errno.EPERM)
            self.assertEqual(os.pread(source_fd,len(BEFORE),0),BEFORE)
            self.assertEqual(
                os.pread(destination_fd,len(BEFORE),0),BEFORE)
            self.assertEqual(drain(),[])
            self.assertEqual(
                (os.fstat(source_fd).st_dev,os.fstat(source_fd).st_ino),
                (source_stat.st_dev,source_stat.st_ino))
            self.assertEqual(
                (os.fstat(destination_fd).st_dev,
                 os.fstat(destination_fd).st_ino),
                (destination_stat.st_dev,destination_stat.st_ino))

            os.close(source_fd);source_fd=None
            self.assertCountEqual(
                drain(),
                [(source_wd,IN_DELETE_SELF,b""),
                 (source_wd,IN_IGNORED,b"")])
            os.close(destination_fd);destination_fd=None
            self.assertCountEqual(
                drain(),
                [(destination_wd,IN_DELETE_SELF,b""),
                 (destination_wd,IN_IGNORED,b"")])
            self.assertEqual(drain(),[])
        finally:
            for fd in (source_fd,destination_fd,watch_fd):
                if fd is not None:
                    os.close(fd)
