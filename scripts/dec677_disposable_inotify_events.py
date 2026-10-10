from __future__ import annotations

"""DEC-677 disposable Linux inotify negative event witness. NEVER authorization."""

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import select
import stat
import struct
import sys
import tempfile
from typing import Any

sys.dont_write_bytecode = True

BEFORE = b"DEC677_PUBLIC_SOURCE\n"
AFTER = b"DEC677_PUBLIC_CHANGED\n"
IN_MODIFY = 0x00000002
IN_CLOSE_WRITE = 0x00000008
IN_ATTRIB = 0x00000004
IN_DELETE_SELF = 0x00000400
IN_MOVE_SELF = 0x00000800
IN_Q_OVERFLOW = 0x00004000
IN_IGNORED = 0x00008000
MASK = (IN_MODIFY | IN_CLOSE_WRITE | IN_ATTRIB | IN_DELETE_SELF |
        IN_MOVE_SELF | IN_Q_OVERFLOW | IN_IGNORED)
EVENT = struct.Struct("iIII")


def _outcome(findings: list[str], checks: dict[str, bool] | None = None) -> dict[str, Any]:
    return {"status": "BLOCKED" if findings else "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED",
            "findings": sorted(set(findings)), "observed_checks": checks or {},
            "can_authorize_dispatch": False, "independent_os_proof_verified": False}


def _classify_stream(data: bytes, watch: int) -> dict[str, Any]:
    """Parse a bounded kernel event buffer, fail closed on bad identity/overflow."""
    if not isinstance(data, bytes) or type(watch) is not int or watch < 0:
        return {"well_formed": False, "overflow": True, "invalidated": True, "write_events": 0}
    if len(data) > 65536:
        return {"well_formed": False, "overflow": True, "invalidated": True, "write_events": 0}
    pos = 0
    observed_writes = 0
    overflow = False
    invalidated = False
    okay = True
    while pos < len(data):
        if len(data) - pos < EVENT.size:
            okay = False
            break
        wd, mask, _cookie, nbytes = EVENT.unpack_from(data, pos)
        pos += EVENT.size
        if nbytes > 4096 or nbytes > len(data) - pos:
            okay = False
            break
        pos += nbytes
        if mask & IN_Q_OVERFLOW:
            overflow = True
        elif wd != watch:
            okay = False
        if mask & (IN_IGNORED | IN_DELETE_SELF | IN_MOVE_SELF):
            invalidated = True
        if mask & (IN_MODIFY | IN_CLOSE_WRITE | IN_ATTRIB):
            observed_writes += 1
    return {"well_formed": okay and pos == len(data), "overflow": overflow,
            "invalidated": invalidated, "write_events": observed_writes}


def _evaluate(before: bytes, after: bytes, data: bytes,
              watch: int, watcher_alive: bool, negative: bool,
              inode_stable: bool = True, replacement_negative: bool = False) -> dict[str, Any]:
    events = _classify_stream(data, watch)
    checks = {
        "final_digest_equal": before == after and hashlib.sha256(before).digest() == hashlib.sha256(after).digest(),
        "watched_inode_matches_final_path": inode_stable is True,
        "event_stream_complete": events["well_formed"] and not events["overflow"] and not events["invalidated"] and watcher_alive is True,
        "no_observed_writes": events["write_events"] == 0,
        "negative_control_detected": (events["write_events"] >= 2) if negative else True,
    }
    findings = ["synthetic inotify property missing: " + k for k, v in checks.items() if v is not True]
    if negative:
        findings.append("deliberate disposable write/restore must never be admitted")
    if replacement_negative:
        findings.append("deliberate disposable source inode substitution must never be admitted")
        if inode_stable is True:
            findings.append("synthetic inode-replacement negative control not detected")
    return _outcome(findings, checks)


def _start_watch(path: Path) -> tuple[int, int]:
    lib = ctypes.CDLL(None, use_errno=True)
    lib.inotify_init1.argtypes = [ctypes.c_int]
    lib.inotify_init1.restype = ctypes.c_int
    lib.inotify_add_watch.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32]
    lib.inotify_add_watch.restype = ctypes.c_int
    fd = lib.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
    if fd < 0:
        raise OSError(ctypes.get_errno(), "disposable inotify_init1 failed")
    wd = lib.inotify_add_watch(fd, os.fsencode(path), MASK)
    if wd < 0:
        error = ctypes.get_errno()
        os.close(fd)
        raise OSError(error, "disposable inotify_add_watch failed")
    return fd, wd


def _read_pending(fd: int) -> bytes:
    chunks: list[bytes] = []
    size = 0
    poller = select.poll()
    poller.register(fd, select.POLLIN | select.POLLERR | select.POLLHUP)
    for _ in range(16):
        if not poller.poll(250):
            break
        chunk = os.read(fd, 4096)
        if not chunk:
            break
        chunks.append(chunk)
        size += len(chunk)
        if size > 65536:
            raise OSError("synthetic event queue exceeds bounded observation")
    return b"".join(chunks)


def _snapshot_regular(path: Path) -> tuple[tuple[int, int], bytes]:
    """Read only a bounded regular inode through a non-following FD."""
    flags = os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    fd = os.open(path, flags)
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_size > 4096:
            raise OSError("disposable sample is not a bounded regular inode")
        data = os.read(fd, 4097)
        if len(data) > 4096:
            raise OSError("disposable source snapshot exceeds bound")
        return (st.st_dev, st.st_ino), data
    finally:
        os.close(fd)


def run_demo(negative: bool = False, replace_watched_inode: bool = False) -> dict[str, Any]:
    if negative and replace_watched_inode:
        return _outcome(["conflicting synthetic negative-control modes"])
    if sys.platform != "linux" or not os.path.isdir("/tmp") or os.path.islink("/tmp"):
        return _outcome(["Linux disposable kernel event monitor unavailable"])
    try:
        with tempfile.TemporaryDirectory(prefix="dec677-disposable-", dir="/tmp") as folder:
            path = Path(folder) / "sample"
            path.write_bytes(BEFORE)
            original_inode, original_bytes = _snapshot_regular(path)
            fd, wd = _start_watch(path)
            try:
                if negative:
                    for value in (AFTER, BEFORE):
                        with open(path, "wb") as f:
                            f.write(value)
                            f.flush()
                            os.fsync(f.fileno())
                if replace_watched_inode:
                    # An inode-targeted watch is not an identity proof for a
                    # mutable pathname. Substitute a precreated identical file.
                    replacement = Path(folder) / "public-replacement"
                    replacement.write_bytes(BEFORE)
                    os.replace(replacement, path)
                raw = _read_pending(fd)
                final_inode, end = _snapshot_regular(path)
                return _evaluate(original_bytes, end, raw, wd, True, negative,
                                 inode_stable=(original_inode == final_inode),
                                 replacement_negative=replace_watched_inode)
            finally:
                os.close(fd)
    except (OSError, AttributeError, ValueError):
        return _outcome(["disposable inotify setup, read or cleanup failed"])


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(add_help=False,
        description="DEC-677 disposable inotify observation, NEVER real runner acceptance")
    choices = p.add_mutually_exclusive_group()
    choices.add_argument("--execute-disposable-control", action="store_true")
    choices.add_argument("--execute-reverted-write-negative", action="store_true")
    choices.add_argument("--execute-inode-replacement-negative", action="store_true")
    args = p.parse_args(argv)
    result = (run_demo(negative=args.execute_reverted_write_negative,
                       replace_watched_inode=args.execute_inode_replacement_negative)
              if (args.execute_disposable_control or args.execute_reverted_write_negative
                  or args.execute_inode_replacement_negative)
              else _outcome(["explicit synthetic observer opt-in required"]))
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 3 if result["status"] == "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
