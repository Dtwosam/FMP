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
# Kernel inotify watch descriptors are signed 32-bit integers. An arbitrary
# Python int is not evidence of a possible installed Linux watch identity.
MAX_WATCH_DESCRIPTOR = (1 << 31) - 1
# Linux UAPI limits.h NAME_MAX for a single directory-entry component.
MAX_EVENT_BASENAME = 255


def _outcome(findings: list[str], checks: dict[str, bool] | None = None) -> dict[str, Any]:
    return {"status": "BLOCKED" if findings else "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED",
            "findings": sorted(set(findings)), "observed_checks": checks or {},
            "can_authorize_dispatch": False, "independent_os_proof_verified": False}


def _classify_stream(data: bytes, watch: int,
                     directory_watch: int | None = None) -> dict[str, Any]:
    """Parse a bounded kernel event buffer, fail closed on bad identity/overflow."""
    if (not isinstance(data, bytes) or type(watch) is not int
            or not 0 <= watch <= MAX_WATCH_DESCRIPTOR):
        return {"well_formed": False, "overflow": True, "invalidated": True, "write_events": 0, "directory_changes": 0, "transient_create_delete_pairs": 0, "source_content_write_events": 0}
    if len(data) > 65536:
        return {"well_formed": False, "overflow": True, "invalidated": True, "write_events": 0, "directory_changes": 0, "transient_create_delete_pairs": 0, "source_content_write_events": 0}
    # The two watch identities come from distinct kernel registrations. An
    # untrusted caller must not alias the directory watch to the file watch,
    # or use a non-integer WD to make a fabricated observation appear quiet.
    if directory_watch is not None and (
        type(directory_watch) is not int
        or not 0 <= directory_watch <= MAX_WATCH_DESCRIPTOR
        or directory_watch == watch
    ):
        return {"well_formed": False, "overflow": True, "invalidated": True,
                "write_events": 0, "directory_changes": 0, "transient_create_delete_pairs": 0, "source_content_write_events": 0}
    pos = 0
    observed_writes = 0
    source_content_writes = 0
    observed_directory_changes = 0
    created_entries: set[bytes] = set()
    matched_transient_pairs = 0
    overflow = False
    invalidated = False
    okay = True
    while pos < len(data):
        if len(data) - pos < EVENT.size:
            okay = False
            break
        wd, mask, cookie, nbytes = EVENT.unpack_from(data, pos)
        pos += EVENT.size
        # A syntactically complete event with no known action or unexpected
        # flags must not be interpreted as a clean inotify observation.
        actions = mask & EVENT_ACTIONS
        # Linux emits one primary inotify action per record. IN_ISDIR is a
        # modifier, not permission to combine unrelated create/write/close
        # actions into a fabricated single event.
        if not actions or actions & (actions - 1) or mask & ~EVENT_ALLOWED:
            okay = False
        # The inotify cookie correlates rename/move records only. A cookie
        # on a file write, child create/delete, overflow or self event is
        # not a valid observation of that event's kernel layout.
        if cookie and not mask & (IN_MOVED_FROM | IN_MOVED_TO):
            okay = False
        if nbytes > 4096 or nbytes > len(data) - pos:
            okay = False
            break
        name_bytes = data[pos:pos + nbytes]
        pos += nbytes
        child_name: bytes | None = None
        # The fixed regular-file watch and the special overflow event must
        # not have a child filename. Directory child events require one
        # NUL-terminated, zero-padded, bounded single basename.
        if wd == watch or mask & IN_Q_OVERFLOW:
            if nbytes:
                okay = False
        elif directory_watch is not None and wd == directory_watch:
            if nbytes == 0 and mask & DIRECTORY_CHANGES:
                okay = False
            if nbytes:
                terminator = name_bytes.find(b"\x00")
                # Linux returns the *minimum* roundup(name_len + 1,
                # sizeof(struct inotify_event)) length, not any arbitrary
                # multiple of the header size with extra zero padding.
                padded_len = ((terminator + EVENT.size) // EVENT.size) * EVENT.size
                if (terminator <= 0 or terminator > MAX_EVENT_BASENAME
                        or nbytes != padded_len
                        or name_bytes[:terminator] in (b".", b"..")
                        or b"/" in name_bytes[:terminator]
                        or any(byte != 0 for byte in name_bytes[terminator:])):
                    okay = False
                else:
                    child_name = name_bytes[:terminator]
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
            # A transient create/remove witness needs the same valid basename
            # created before deletion. Two arbitrary entry events are not proof.
            if child_name is not None:
                change = mask & DIRECTORY_CHANGES
                if change == IN_CREATE:
                    created_entries.add(child_name)
                elif change == IN_DELETE and child_name in created_entries:
                    created_entries.remove(child_name)
                    matched_transient_pairs += 1
        if mask & (IN_IGNORED | IN_DELETE_SELF | IN_MOVE_SELF):
            invalidated = True
        if mask & (IN_MODIFY | IN_CLOSE_WRITE | IN_ATTRIB):
            observed_writes += 1
        # A deliberate rewrite of the watched source cannot be witnessed by
        # directory-only activity or file metadata IN_ATTRIB events.
        if wd == watch and mask & (IN_MODIFY | IN_CLOSE_WRITE):
            source_content_writes += 1
    return {"well_formed": okay and pos == len(data), "overflow": overflow,
            "invalidated": invalidated, "write_events": observed_writes,
            "directory_changes": observed_directory_changes,
            "transient_create_delete_pairs": matched_transient_pairs,
            "source_content_write_events": source_content_writes}


def _evaluate(before: bytes, after: bytes, data: bytes,
              watch: int, watcher_alive: bool, negative: bool,
              inode_stable: bool = True, replacement_negative: bool = False,
              directory_watch: int | None = None,
              directory_inventory_ok: bool = True,
              sibling_negative: bool = False,
              transient_sibling_negative: bool = False) -> dict[str, Any]:
    events = _classify_stream(data, watch, directory_watch)
    checks = {
        # An observer which now depends on two distinct kernel watches may
        # never call a file-only observation "complete" merely because the
        # file event queue was quiet. Missing watch identity is fail-closed.
        "both_watches_identified": (
            type(watch) is int and 0 <= watch <= MAX_WATCH_DESCRIPTOR
            and type(directory_watch) is int
            and 0 <= directory_watch <= MAX_WATCH_DESCRIPTOR
            and directory_watch != watch
        ),
        "final_digest_equal": before == after and hashlib.sha256(before).digest() == hashlib.sha256(after).digest(),
        "watched_inode_matches_final_path": inode_stable is True,
        "no_directory_entry_mutations": (events["directory_changes"] == 0
                                          and directory_inventory_ok is True),
        "transient_directory_control_detected": (
            events["well_formed"] and not events["overflow"]
            and not events["invalidated"] and watcher_alive is True
            and events["transient_create_delete_pairs"] >= 1
        ) if transient_sibling_negative else True,
        "event_stream_complete": events["well_formed"] and not events["overflow"] and not events["invalidated"] and watcher_alive is True,
        "no_observed_writes": events["write_events"] == 0,
        "negative_control_detected": (
            events["well_formed"] and not events["overflow"]
            and not events["invalidated"] and watcher_alive is True
            and events["source_content_write_events"] >= 2
        ) if negative else True,
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
        if checks["transient_directory_control_detected"] is not True:
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
        # select.poll.poll() promises a list. None, a malformed wrapper or
        # another falsely-empty value cannot stand in for kernel quietness.
        if type(readiness) is not list:
            raise OSError("synthetic inotify poll returned malformed readiness")
        if not readiness:
            return False
        # One fd is registered: the only acceptable readiness is one exact
        # POLLIN report. POLLPRI, zero/unknown bits or duplicate reports do
        # not establish that this inotify queue can be safely drained.
        if len(readiness) != 1 or readiness[0] != (fd, select.POLLIN):
            raise OSError("synthetic inotify event collector lost readable status")
        return True

    for _ in range(16):
        if not is_readable(250):
            break
        try:
            chunk = os.read(fd, 4096)
        except BlockingIOError as error:
            raise OSError("synthetic watch readiness raced an empty event queue") from error
        if type(chunk) is not bytes or len(chunk) > 4096:
            raise OSError("synthetic inotify read returned impossible chunk shape")
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
        if not stat.S_ISREG(st.st_mode) or not 0 <= st.st_size <= 4096:
            raise OSError("disposable sample is not a bounded regular inode")
        data = os.read(fd, st.st_size + 1)
        after = os.fstat(fd)
        # This detects a short read or some concurrent inode mutations. It
        # does NOT prove freedom from an adversarial write-and-restore race.
        if len(data) != st.st_size or (
            st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns
        ) != (
            after.st_dev, after.st_ino, after.st_size,
            after.st_mtime_ns, after.st_ctime_ns
        ):
            raise OSError("disposable inode changed or was read incompletely")
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
