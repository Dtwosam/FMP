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
IN_MOVED_FROM = 0x00000040
IN_MOVED_TO = 0x00000080
IN_CREATE = 0x00000100
IN_DELETE = 0x00000200
IN_ISDIR = 0x40000000
IN_DELETE_SELF = 0x00000400
IN_MOVE_SELF = 0x00000800
IN_Q_OVERFLOW = 0x00004000
IN_IGNORED = 0x00008000
MASK = (IN_MODIFY | IN_CLOSE_WRITE | IN_ATTRIB | IN_DELETE_SELF |
        IN_MOVE_SELF | IN_Q_OVERFLOW | IN_IGNORED)
DIRECTORY_CHANGES = IN_MOVED_FROM | IN_MOVED_TO | IN_CREATE | IN_DELETE
EVENT_ACTIONS = MASK | DIRECTORY_CHANGES
EVENT_ALLOWED = EVENT_ACTIONS | IN_ISDIR
DIRECTORY_MASK = EVENT_ACTIONS
EVENT = struct.Struct("iIII")


def _outcome(findings: list[str], checks: dict[str, bool] | None = None) -> dict[str, Any]:
    return {"status": "BLOCKED" if findings else "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED",
            "findings": sorted(set(findings)), "observed_checks": checks or {},
            "can_authorize_dispatch": False, "independent_os_proof_verified": False}


def _classify_stream(data: bytes, watch: int,
                     directory_watch: int | None = None) -> dict[str, Any]:
    """Parse a bounded kernel event buffer, fail closed on bad identity/overflow."""
    if not isinstance(data, bytes) or type(watch) is not int or watch < 0:
        return {"well_formed": False, "overflow": True, "invalidated": True, "write_events": 0, "directory_changes": 0}
    if len(data) > 65536:
        return {"well_formed": False, "overflow": True, "invalidated": True, "write_events": 0, "directory_changes": 0}
    # The two watch identities come from distinct kernel registrations. An
    # untrusted caller must not alias the directory watch to the file watch,
    # or use a non-integer WD to make a fabricated observation appear quiet.
    if directory_watch is not None and (
        type(directory_watch) is not int or directory_watch < 0
        or directory_watch == watch
    ):
        return {"well_formed": False, "overflow": True, "invalidated": True,
                "write_events": 0, "directory_changes": 0}
    pos = 0
    observed_writes = 0
    observed_directory_changes = 0
    overflow = False
    invalidated = False
    okay = True
    while pos < len(data):
        if len(data) - pos < EVENT.size:
            okay = False
            break
        wd, mask, _cookie, nbytes = EVENT.unpack_from(data, pos)
        pos += EVENT.size
        # A syntactically complete event with no known action or unexpected
        # flags must not be interpreted as a clean inotify observation.
        if not (mask & EVENT_ACTIONS) or mask & ~EVENT_ALLOWED:
            okay = False
        if nbytes > 4096 or nbytes > len(data) - pos:
            okay = False
            break
        pos += nbytes
        if mask & IN_Q_OVERFLOW:
            overflow = True
            # Linux uses wd=-1 for queue overflow. Mixed flags are uncertain.
            if wd != -1 or mask != IN_Q_OVERFLOW:
                okay = False
        elif wd != watch and (directory_watch is None or wd != directory_watch):
            okay = False
        elif wd == watch and mask & (DIRECTORY_CHANGES | IN_ISDIR):
            # This watch belongs to a known *regular file*. An IN_CREATE,
            # IN_DELETE or move event on its WD is not a write to the file,
            # and must never silently pass as an empty directory observation.
            okay = False
        if directory_watch is not None and wd == directory_watch and mask & DIRECTORY_CHANGES:
            observed_directory_changes += 1
        if mask & (IN_IGNORED | IN_DELETE_SELF | IN_MOVE_SELF):
            invalidated = True
        if mask & (IN_MODIFY | IN_CLOSE_WRITE | IN_ATTRIB):
            observed_writes += 1
    return {"well_formed": okay and pos == len(data), "overflow": overflow,
            "invalidated": invalidated, "write_events": observed_writes,
            "directory_changes": observed_directory_changes}


def _evaluate(before: bytes, after: bytes, data: bytes,
              watch: int, watcher_alive: bool, negative: bool,
              inode_stable: bool = True, replacement_negative: bool = False,
              directory_watch: int | None = None,
              directory_inventory_ok: bool = True,
              sibling_negative: bool = False,
              transient_sibling_negative: bool = False) -> dict[str, Any]:
    events = _classify_stream(data, watch, directory_watch)
    checks = {
        "final_digest_equal": before == after and hashlib.sha256(before).digest() == hashlib.sha256(after).digest(),
        "watched_inode_matches_final_path": inode_stable is True,
        "no_directory_entry_mutations": (events["directory_changes"] == 0
                                          and directory_inventory_ok is True),
        "transient_directory_control_detected": (
            events["directory_changes"] >= 2 if transient_sibling_negative else True
        ),
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
    if sibling_negative:
        findings.append("deliberate disposable sibling creation must never be admitted")
        if events["directory_changes"] == 0 and directory_inventory_ok is True:
            findings.append("synthetic directory-event negative control not detected")
    if transient_sibling_negative:
        findings.append("deliberate create/remove cannot prove directory immutability")
        if events["directory_changes"] < 2:
            findings.append("synthetic transient directory negative control not observed")
    return _outcome(findings, checks)


def _start_watch(path: Path) -> tuple[int, int, int]:
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
    directory_wd = lib.inotify_add_watch(fd, os.fsencode(path.parent), DIRECTORY_MASK)
    if directory_wd < 0 or directory_wd == wd:
        error = ctypes.get_errno()
        os.close(fd)
        raise OSError(error or 22, "disposable directory inotify_add_watch failed")
    return fd, wd, directory_wd


def _read_pending(fd: int) -> bytes:
    """Bounded event drain; never present an unreadable/pending queue as quiet."""
    chunks: list[bytes] = []
    size = 0
    poller = select.poll()
    poller.register(fd, select.POLLIN | select.POLLERR | select.POLLHUP | select.POLLNVAL)

    def is_readable(timeout_ms: int) -> bool:
        readiness = poller.poll(timeout_ms)
        if any(descriptor != fd or flags & (select.POLLERR | select.POLLHUP | select.POLLNVAL)
               for descriptor, flags in readiness):
            raise OSError("synthetic inotify event collector lost readable status")
        return bool(readiness)

    for _ in range(16):
        if not is_readable(250):
            break
        try:
            chunk = os.read(fd, 4096)
        except BlockingIOError as error:
            raise OSError("synthetic watch readiness raced an empty event queue") from error
        if not chunk:
            raise OSError("synthetic watch became EOF after readiness")
        chunks.append(chunk)
        size += len(chunk)
        if size > 65536:
            raise OSError("synthetic event queue exceeds bounded observation")
    else:
        # A bounded collector may not silently truncate a still-readable
        # queue, hiding later IN_Q_OVERFLOW or directory event records.
        if is_readable(0):
            raise OSError("synthetic inotify event queue still pending after drain limit")
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


def run_demo(negative: bool = False, replace_watched_inode: bool = False,
             create_sibling: bool = False, transient_sibling: bool = False) -> dict[str, Any]:
    if sum((negative, replace_watched_inode, create_sibling, transient_sibling)) > 1:
        return _outcome(["conflicting synthetic negative-control modes"])
    if sys.platform != "linux" or not os.path.isdir("/tmp") or os.path.islink("/tmp"):
        return _outcome(["Linux disposable kernel event monitor unavailable"])
    try:
        with tempfile.TemporaryDirectory(prefix="dec677-disposable-", dir="/tmp") as folder:
            path = Path(folder) / "sample"
            path.write_bytes(BEFORE)
            original_inode, original_bytes = _snapshot_regular(path)
            fd, wd, dir_wd = _start_watch(path)
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
                if create_sibling:
                    (Path(folder) / "unexpected-public-sibling").write_bytes(b"PUBLIC-EXTRA")
                if transient_sibling:
                    transient = Path(folder) / "temporary-public-sibling"
                    transient.write_bytes(b"PUBLIC-TEMPORARY")
                    transient.unlink()
                raw = _read_pending(fd)
                final_inode, end = _snapshot_regular(path)
                inventory_ok = sorted(p.name for p in Path(folder).iterdir()) == ["sample"]
                return _evaluate(original_bytes, end, raw, wd, True, negative,
                                 inode_stable=(original_inode == final_inode),
                                 replacement_negative=replace_watched_inode,
                                 directory_watch=dir_wd,
                                 directory_inventory_ok=inventory_ok,
                                 sibling_negative=create_sibling,
                                 transient_sibling_negative=transient_sibling)
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
    choices.add_argument("--execute-sibling-creation-negative", action="store_true")
    choices.add_argument("--execute-transient-directory-negative", action="store_true")
    args = p.parse_args(argv)
    result = (run_demo(negative=args.execute_reverted_write_negative,
                       replace_watched_inode=args.execute_inode_replacement_negative,
                       create_sibling=args.execute_sibling_creation_negative,
                       transient_sibling=args.execute_transient_directory_negative)
              if (args.execute_disposable_control or args.execute_reverted_write_negative
                  or args.execute_inode_replacement_negative
                  or args.execute_sibling_creation_negative
                  or args.execute_transient_directory_negative)
              else _outcome(["explicit synthetic observer opt-in required"]))
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 3 if result["status"] == "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
