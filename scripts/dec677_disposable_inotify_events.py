from __future__ import annotations

"""DEC-677 disposable Linux inotify negative event witness. NEVER authorization."""

import argparse
import ctypes
import hashlib
from itertools import islice
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
PERSISTENT_SIBLING_NAME = "unexpected-public-sibling"
TRANSIENT_SIBLING_NAME = "temporary-public-sibling"
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
# A Linux FD returned by int-valued libc/POSIX APIs cannot exceed INT_MAX.
MAX_FILE_DESCRIPTOR = (1 << 31) - 1
# Linux stat st_dev and st_ino are unsigned 64-bit kernel/ABI identities.
MAX_KERNEL_STAT_ID = (1 << 64) - 1
# Linux stat mode_t is an unsigned 32-bit value, not an arbitrary Python int.
MAX_KERNEL_STAT_MODE = (1 << 32) - 1
# Linux UAPI limits.h NAME_MAX for a single directory-entry component.
MAX_EVENT_BASENAME = 255


def _outcome(findings: list[str], checks: dict[str, bool] | None = None) -> dict[str, Any]:
    return {"status": "BLOCKED" if findings else "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED",
            "findings": sorted(set(findings)), "observed_checks": checks or {},
            "can_authorize_dispatch": False, "independent_os_proof_verified": False}


def _classify_stream(data: bytes, watch: int,
                     directory_watch: int | None = None) -> dict[str, Any]:
    """Parse a bounded kernel event buffer, fail closed on bad identity/overflow."""
    if (type(data) is not bytes or type(watch) is not int
            or not 0 <= watch <= MAX_WATCH_DESCRIPTOR):
        return {"well_formed": False, "overflow": True, "invalidated": True, "write_events": 0, "directory_changes": 0, "transient_create_delete_pairs": 0, "source_content_write_events": 0, "source_modify_events": 0, "expected_sibling_created": False, "expected_transient_pairs": 0, "pending_new_child_names": (), "source_attribute_events": 0}
    if len(data) > 65536:
        return {"well_formed": False, "overflow": True, "invalidated": True, "write_events": 0, "directory_changes": 0, "transient_create_delete_pairs": 0, "source_content_write_events": 0, "source_modify_events": 0, "expected_sibling_created": False, "expected_transient_pairs": 0, "pending_new_child_names": (), "source_attribute_events": 0}
    # The two watch identities come from distinct kernel registrations. An
    # untrusted caller must not alias the directory watch to the file watch,
    # or use a non-integer WD to make a fabricated observation appear quiet.
    if directory_watch is not None and (
        type(directory_watch) is not int
        or not 0 <= directory_watch <= MAX_WATCH_DESCRIPTOR
        or directory_watch == watch
    ):
        return {"well_formed": False, "overflow": True, "invalidated": True,
                "write_events": 0, "directory_changes": 0, "transient_create_delete_pairs": 0, "source_content_write_events": 0, "source_modify_events": 0, "expected_sibling_created": False, "expected_transient_pairs": 0, "pending_new_child_names": (), "source_attribute_events": 0}
    pos = 0
    observed_writes = 0
    source_content_writes = 0
    source_modifications = 0
    source_attribute_events = 0
    observed_directory_changes = 0
    created_entries: set[bytes] = set()
    # Names observed to enter after watch registration, as either regular
    # files or directories. This is not a full preexisting directory census.
    occupied_new_entries: set[bytes] = set()
    # For entries introduced since registration, record whether the name
    # referred to a directory. A regular file cannot disappear as a dir,
    # or vice versa, without an observable replacement/rename transition.
    observed_child_is_directory: dict[bytes, bool] = {}
    deleted_entries: set[bytes] = set()
    # Each rename cookie represents at most one move-from and one move-to
    # record in this bounded observation, even if other events intervene.
    rename_cookie_actions: dict[int, int] = {}
    matched_transient_pairs = 0
    expected_transient_pairs = 0
    expected_sibling_created = False
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
        # Linux pairs rename events with a nonzero cookie. A zero cookie
        # on a move record cannot prove a complete named move transition.
        move_action = mask & (IN_MOVED_FROM | IN_MOVED_TO)
        if move_action and cookie == 0:
            okay = False
        if move_action and cookie:
            prior = rename_cookie_actions.get(cookie, 0)
            # Repeating the same rename direction with the same cookie
            # cannot represent two independent kernel moves.
            if prior & move_action:
                okay = False
            rename_cookie_actions[cookie] = prior | move_action
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
            # The persistent sibling negative creates this exact regular file,
            # not just any unrelated entry or a similarly named directory.
            if child_name == PERSISTENT_SIBLING_NAME.encode("ascii"):
                action = mask & DIRECTORY_CHANGES
                if action == IN_CREATE and not mask & IN_ISDIR:
                    expected_sibling_created = True
                else:
                    # A later same-name deletion, move, or directory-kind
                    # replacement destroys the provenance of the expected
                    # persistent *regular* file from its earlier creation.
                    expected_sibling_created = False
            # A transient create/remove witness needs the same valid basename
            # created before deletion. Two arbitrary entry events are not proof.
            if child_name is not None:
                change = mask & DIRECTORY_CHANGES
                if change == IN_CREATE:
                    # Files and directories share one namespace. Creating a
                    # second child at an already observed occupied basename
                    # without a delete or move-out cannot be a complete log.
                    if child_name in occupied_new_entries:
                        okay = False
                    occupied_new_entries.add(child_name)
                    observed_child_is_directory[child_name] = bool(mask & IN_ISDIR)
                    # A new child clears any pending previous deletion for
                    # this basename, whether the child is a file or dir.
                    deleted_entries.discard(child_name)
                    # This negative control creates a regular-file sibling.
                    # IN_ISDIR denotes an actual directory, not that file.
                    if mask & IN_ISDIR:
                        created_entries.discard(child_name)
                    else:
                        # A second create for the exact same directory entry
                        # without an intervening delete/move contradicts a
                        # complete kernel event sequence. Do not interpret
                        # a later delete as trusted transient-file evidence.
                        if child_name in created_entries:
                            okay = False
                        created_entries.add(child_name)
                elif change == IN_DELETE:
                    if (child_name in observed_child_is_directory
                            and observed_child_is_directory[child_name] != bool(mask & IN_ISDIR)):
                        okay = False
                    observed_child_is_directory.pop(child_name, None)
                    occupied_new_entries.discard(child_name)
                    # Two consecutive same-name removals with no new child
                    # created or moved into that name contradict a complete
                    # directory-entry timeline. Reject the entire stream.
                    if child_name in deleted_entries:
                        okay = False
                    deleted_entries.add(child_name)
                    if not mask & IN_ISDIR and child_name in created_entries:
                        matched_transient_pairs += 1
                        if child_name == TRANSIENT_SIBLING_NAME.encode("ascii"):
                            expected_transient_pairs += 1
                    created_entries.discard(child_name)
                elif change in (IN_MOVED_FROM, IN_MOVED_TO):
                    if change == IN_MOVED_TO:
                        # An ordinary rename may replace an existing target
                        # of the SAME kind. A file-to-directory substitution
                        # requires the previous name to depart first (for
                        # example through renameat2 RENAME_EXCHANGE).
                        if (child_name in observed_child_is_directory
                                and observed_child_is_directory[child_name] != bool(mask & IN_ISDIR)):
                            okay = False
                        occupied_new_entries.add(child_name)
                        observed_child_is_directory[child_name] = bool(mask & IN_ISDIR)
                        deleted_entries.discard(child_name)
                    else:
                        # Like deletion, move-out leaves this basename known
                        # absent. Without a fresh create/move-in, a later
                        # delete or move-out cannot be the complete history.
                        if child_name in deleted_entries:
                            okay = False
                        deleted_entries.add(child_name)
                        if (child_name in observed_child_is_directory
                                and observed_child_is_directory[child_name] != bool(mask & IN_ISDIR)):
                            okay = False
                        observed_child_is_directory.pop(child_name, None)
                        occupied_new_entries.discard(child_name)
                    # After a move involving this basename, a previously
                    # created inode may have left or been replaced. A later
                    # IN_DELETE no longer proves create->unlink of that inode.
                    created_entries.discard(child_name)
        if mask & (IN_IGNORED | IN_DELETE_SELF | IN_MOVE_SELF):
            invalidated = True
        if mask & (IN_MODIFY | IN_CLOSE_WRITE | IN_ATTRIB):
            observed_writes += 1
        # A deliberate rewrite of the watched source cannot be witnessed by
        # directory-only activity or file metadata IN_ATTRIB events.
        if wd == watch and mask & (IN_MODIFY | IN_CLOSE_WRITE):
            source_content_writes += 1
        # IN_CLOSE_WRITE means an fd opened for writing was closed. It can
        # occur with no bytes written, so it cannot attest a modification.
        if wd == watch and mask & IN_MODIFY:
            source_modifications += 1
        if wd == watch and mask & IN_ATTRIB:
            source_attribute_events += 1
    return {"well_formed": okay and pos == len(data), "overflow": overflow,
            "invalidated": invalidated, "write_events": observed_writes,
            "directory_changes": observed_directory_changes,
            "transient_create_delete_pairs": matched_transient_pairs,
            "expected_transient_pairs": expected_transient_pairs,
            "source_content_write_events": source_content_writes,
            "source_modify_events": source_modifications,
            "source_attribute_events": source_attribute_events,
            "expected_sibling_created": expected_sibling_created,
            "pending_new_child_names": tuple(sorted(occupied_new_entries))}


def _evaluate(before: bytes, after: bytes, data: bytes,
              watch: int, watcher_alive: bool, negative: bool,
              inode_stable: bool = True, replacement_negative: bool = False,
              directory_watch: int | None = None,
              directory_inventory_ok: bool = True,
              directory_inventory_names: tuple[str, ...] | None = None,
              sibling_snapshot_stable: bool | None = None,
              sibling_negative: bool = False,
              transient_sibling_negative: bool = False,
              midpoint_snapshot_matches_expected: bool | None = None,
              transient_midpoint_verified: bool | None = None) -> dict[str, Any]:
    # The direct evaluator must not claim two incompatible deliberate
    # negative controls, even if called without the CLI/run_demo mode gate.
    controls = (negative, replacement_negative, sibling_negative,
                transient_sibling_negative)
    if any(type(control) is not bool for control in controls):
        return _outcome(["disposable evaluator negative controls must be booleans"])
    if sum(controls) > 1:
        return _outcome(["conflicting synthetic evaluator negative controls"])
    # Snapshot values reach hashlib below. A wrong type or oversized injected
    # snapshot cannot be accepted as a coherent bounded public fixture, nor
    # escape the fail-closed JSON verdict with an uncontrolled TypeError.
    if (type(before) is not bytes or type(after) is not bytes
            or len(before) > 4096 or len(after) > 4096):
        return _outcome(["disposable source snapshot must be bounded bytes"])
    events = _classify_stream(data, watch, directory_watch)
    both_watches_identified = (
        type(watch) is int and 0 <= watch <= MAX_WATCH_DESCRIPTOR
        and type(directory_watch) is int
        and 0 <= directory_watch <= MAX_WATCH_DESCRIPTOR
        and directory_watch != watch
    )
    # Only plain Path.name strings are valid inventory evidence. Tuple
    # element __eq__ implementations can otherwise forge exact-name matches.
    inventory_names_are_plain = (
        type(directory_inventory_names) is tuple
        # The disposable success contract only permits one source name or
        # source plus the one persistent sibling. Refuse longer injected
        # inventories before scanning their potentially many members.
        and 1 <= len(directory_inventory_names) <= 2
        and all(type(name) is str for name in directory_inventory_names)
    )
    directory_intact = (
        both_watches_identified and events["well_formed"]
        and not events["overflow"] and not events["invalidated"]
        and watcher_alive is True
        and events["directory_changes"] == 0
        and directory_inventory_ok is True
        and inventory_names_are_plain
        and directory_inventory_names == ("sample",)
    )
    checks = {
        # An observer which now depends on two distinct kernel watches may
        # never call a file-only observation "complete" merely because the
        # file event queue was quiet. Missing watch identity is fail-closed.
        "both_watches_identified": both_watches_identified,
        "final_digest_equal": before == after and hashlib.sha256(before).digest() == hashlib.sha256(after).digest(),
        "watched_inode_matches_final_path": inode_stable is True,
        "no_directory_entry_mutations": directory_intact,
        "sibling_creation_control_detected": (
            both_watches_identified
            and events["source_content_write_events"] == 0
            and events["source_attribute_events"] == 0
            and before == after and inode_stable is True
            and events["well_formed"] and not events["overflow"]
            and not events["invalidated"] and watcher_alive is True
            and directory_inventory_ok is False
            and inventory_names_are_plain
            and directory_inventory_names == tuple(sorted(("sample", PERSISTENT_SIBLING_NAME)))
            and sibling_snapshot_stable is True
            and events["expected_sibling_created"] is True
            and events["pending_new_child_names"] == (PERSISTENT_SIBLING_NAME.encode("ascii"),)
        ) if sibling_negative else False,
        "transient_midpoint_regular_file_verified": (
            transient_midpoint_verified is True
        ) if transient_sibling_negative else False,
        "transient_directory_control_detected": (
            both_watches_identified
            and events["source_content_write_events"] == 0
            and events["source_attribute_events"] == 0
            and transient_midpoint_verified is True
            and before == after and inode_stable is True
            and events["well_formed"] and not events["overflow"]
            and not events["invalidated"] and watcher_alive is True
            and directory_inventory_ok is True
            and inventory_names_are_plain
            and directory_inventory_names == ("sample",)
            and events["expected_transient_pairs"] >= 1
            and events["pending_new_child_names"] == ()
        ) if transient_sibling_negative else False,
        "event_stream_complete": (
            both_watches_identified and events["well_formed"]
            and not events["overflow"] and not events["invalidated"]
            and watcher_alive is True
        ),
        "no_observed_writes": (
            both_watches_identified and events["well_formed"]
            and not events["overflow"] and not events["invalidated"]
            and watcher_alive is True and events["write_events"] == 0
        ),
        "midpoint_source_snapshot_matches_expected": (
            midpoint_snapshot_matches_expected is True
        ) if negative else False,
        "negative_control_detected": (
            both_watches_identified and directory_intact
            and midpoint_snapshot_matches_expected is True
            and before == after
            and inode_stable is True
            and events["well_formed"] and not events["overflow"]
            and not events["invalidated"] and watcher_alive is True
            and events["source_modify_events"] >= 2
        ) if negative else False,
    }
    # Inactive negative-control fields must say False (not observed), not
    # True (detected). They are NOT requirements for another mode or a
    # clean quiet local experiment and must not create missing properties.
    gated_checks = {
        "sibling_creation_control_detected": sibling_negative,
        "transient_midpoint_regular_file_verified": transient_sibling_negative,
        "transient_directory_control_detected": transient_sibling_negative,
        "midpoint_source_snapshot_matches_expected": negative,
        "negative_control_detected": negative,
    }
    findings = [
        "synthetic inotify property missing: " + key
        for key, value in checks.items()
        if value is not True and gated_checks.get(key, True)
    ]
    if negative:
        findings.append("deliberate disposable write/restore must never be admitted")
    if replacement_negative:
        findings.append("deliberate disposable source inode substitution must never be admitted")
        if inode_stable is True:
            findings.append("synthetic inode-replacement negative control not detected")
    if sibling_negative:
        findings.append("deliberate disposable sibling creation must never be admitted")
        if checks["sibling_creation_control_detected"] is not True:
            findings.append("synthetic directory-event negative control not detected")
    if transient_sibling_negative:
        findings.append("deliberate create/remove cannot prove directory immutability")
        if checks["transient_directory_control_detected"] is not True:
            findings.append("synthetic transient directory negative control not observed")
    return _outcome(findings, checks)


def _start_watch(path: Path) -> tuple[int, int, int]:
    # Until inotify_init1 yields an integer FD, no descriptor is owned here.
    # Unexpected injected loader/signature/init errors must still produce a
    # handled BLOCKED result rather than escaping as RuntimeError.
    try:
        lib = ctypes.CDLL(None, use_errno=True)
        lib.inotify_init1.argtypes = [ctypes.c_int]
        lib.inotify_init1.restype = ctypes.c_int
        lib.inotify_add_watch.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32]
        lib.inotify_add_watch.restype = ctypes.c_int
        fd = lib.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
    except Exception as error:
        if isinstance(error, OSError):
            raise
        raise OSError("disposable inotify initialization raised unexpectedly") from error
    if type(fd) is not int:
        raise OSError("disposable inotify_init1 returned a noninteger descriptor")
    if fd > MAX_FILE_DESCRIPTOR:
        raise OSError("disposable inotify_init1 returned an oversized descriptor")
    if fd < 0:
        raise OSError(ctypes.get_errno(), "disposable inotify_init1 failed")
    if fd <= 2:
        # A host whose standard descriptors are closed may allocate the new
        # observer on fd 0, 1 or 2. Refuse that uncertain stdio boundary.
        os.close(fd)
        raise OSError("disposable inotify watcher used a standard descriptor")
    # After successful nonstdio allocation, this function owns fd until it
    # returns the complete dual-watch tuple. A ctypes call that raises (not
    # just one returning -1) must not leak the observer descriptor.
    try:
        wd = lib.inotify_add_watch(fd, os.fsencode(path), MASK)
        if type(wd) is not int or not 0 <= wd <= MAX_WATCH_DESCRIPTOR:
            error = ctypes.get_errno()
            raise OSError(error or 22, "disposable inotify_add_watch failed")
        directory_wd = lib.inotify_add_watch(fd, os.fsencode(path.parent), DIRECTORY_MASK)
        if (type(directory_wd) is not int
                or not 0 <= directory_wd <= MAX_WATCH_DESCRIPTOR
                or directory_wd == wd):
            error = ctypes.get_errno()
            raise OSError(error or 22, "disposable directory inotify_add_watch failed")
    except Exception as error:
        os.close(fd)
        if isinstance(error, OSError):
            raise
        raise OSError("disposable inotify watch registration raised unexpectedly") from error
    return fd, wd, directory_wd


def _read_pending(fd: int) -> bytes:
    """Bounded event drain; never present an unreadable/pending queue as quiet."""
    try:
        return _read_pending_checked(fd)
    except Exception as error:
        if isinstance(error, OSError):
            raise
        raise OSError("synthetic inotify collector wrapper raised unexpectedly") from error


def _read_pending_checked(fd: int) -> bytes:
    if type(fd) is not int or not 3 <= fd <= MAX_FILE_DESCRIPTOR:
        raise OSError("synthetic inotify collector requires a nonstdio integer fd")
    chunks: list[bytes] = []
    size = 0
    poller = select.poll()
    registered = poller.register(
        fd, select.POLLIN | select.POLLERR | select.POLLHUP | select.POLLNVAL)
    # CPython poll.register mutates the poll set and returns None. An
    # injected non-void result is not evidence of a successful registration.
    if registered is not None:
        raise OSError("synthetic inotify poll registration returned malformed status")

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
        if len(readiness) != 1:
            raise OSError("synthetic inotify event collector lost readable status")
        record = readiness[0]
        # A patched or malformed object must not masquerade as a real
        # kernel-ready (int fd, int events) pair via a forged __eq__ method.
        if (type(record) is not tuple or len(record) != 2
                or type(record[0]) is not int or type(record[1]) is not int
                or record != (fd, select.POLLIN)):
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


def _bounded_inventory_names(folder: Path) -> tuple[str, ...]:
    """Read at most two admissible children plus one over-limit witness.

    os.scandir is lazy; Path.iterdir may materialize a full directory before
    callers slice the results. The third child is enough to refuse a clean
    synthetic inventory without examining an unbounded number of names.
    """
    try:
        with os.scandir(folder) as entries:
            names = tuple(entry.name for entry in islice(entries, 3))
    except Exception as error:
        if isinstance(error, OSError):
            raise
        raise OSError("disposable inventory scan raised unexpectedly") from error
    # Do not sort injected custom name objects with attacker-defined __lt__.
    if any(type(name) is not str for name in names):
        raise OSError("disposable inventory returned a malformed entry name")
    return tuple(sorted(names))


def _checked_snapshot_metadata(st: Any) -> tuple[int, int, int, int, int]:
    """Reject patched fstat metadata before size arithmetic or comparisons."""
    fields = ("st_mode", "st_dev", "st_ino", "st_size",
              "st_mtime_ns", "st_ctime_ns")
    try:
        values = tuple(getattr(st, field) for field in fields)
    except Exception as error:
        raise OSError("disposable fstat returned unreadable metadata") from error
    if any(type(value) is not int for value in values):
        raise OSError("disposable fstat returned noninteger metadata")
    mode, dev, ino, size, mtime_ns, ctime_ns = values
    if (not 0 <= mode <= MAX_KERNEL_STAT_MODE or not stat.S_ISREG(mode)
            or not 0 <= dev <= MAX_KERNEL_STAT_ID
            or not 0 <= ino <= MAX_KERNEL_STAT_ID or not 0 <= size <= 4096):
        raise OSError("disposable sample is not a bounded regular inode")
    return dev, ino, size, mtime_ns, ctime_ns


def _snapshot_regular(path: Path) -> tuple[tuple[int, int], bytes]:
    """Read only a bounded regular inode through a non-following FD."""
    flags = os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    try:
        fd = os.open(path, flags)
    except Exception as error:
        if isinstance(error, OSError):
            raise
        raise OSError("disposable snapshot open raised unexpectedly") from error
    # The temporary observer can be invoked in a process with closed stdio.
    # Refuse snapshot handles allocated onto fd 0-2 (or malformed patched
    # handles); never close a standard I/O descriptor as an afterthought.
    if type(fd) is not int or not 0 <= fd <= MAX_FILE_DESCRIPTOR:
        raise OSError("disposable regular snapshot requires a valid integer fd")
    if fd <= 2:
        os.close(fd)
        raise OSError("disposable regular snapshot used a standard descriptor")
    try:
        initial = _checked_snapshot_metadata(os.fstat(fd))
        data = os.read(fd, initial[2] + 1)
        # A real os.read() is bounded by the requested size and yields
        # plain immutable bytes. Malformed mock/injected data must become a
        # controlled blocked snapshot, not TypeError or forged completeness.
        if type(data) is not bytes or len(data) > initial[2] + 1:
            raise OSError("disposable regular snapshot read returned impossible bytes")
        final = _checked_snapshot_metadata(os.fstat(fd))
        # This detects a short read or some concurrent inode mutations. It
        # does NOT prove freedom from an adversarial write-and-restore race.
        if len(data) != initial[2] or initial != final:
            raise OSError("disposable inode changed or was read incompletely")
        return (initial[0], initial[1]), data
    except Exception as error:
        if isinstance(error, OSError):
            raise
        raise OSError("disposable snapshot syscall raised unexpectedly") from error
    finally:
        os.close(fd)


def _checked_snapshot_result(value: Any) -> tuple[tuple[int, int], bytes]:
    """Do not trust an injected snapshot helper's identity or payload."""
    if type(value) is not tuple or len(value) != 2:
        raise OSError("disposable snapshot result has invalid shape")
    identity, data = value
    if (type(identity) is not tuple or len(identity) != 2
            or any(type(part) is not int or not 0 <= part <= MAX_KERNEL_STAT_ID
                   for part in identity)
            or type(data) is not bytes or len(data) > 4096):
        raise OSError("disposable snapshot result has invalid identity or bytes")
    return identity, data


def run_demo(negative: bool = False, replace_watched_inode: bool = False,
             create_sibling: bool = False, transient_sibling: bool = False) -> dict[str, Any]:
    # The direct helper is also exercised by synthetic callers, not only the
    # argparse Boolean switches. Reject injected truthy/non-numeric values
    # before arithmetic or any generated filesystem operation.
    modes = (negative, replace_watched_inode, create_sibling, transient_sibling)
    if any(type(mode) is not bool for mode in modes):
        return _outcome(["disposable negative-control modes must be booleans"])
    if sum(modes) > 1:
        return _outcome(["conflicting synthetic negative-control modes"])
    if sys.platform != "linux" or not os.path.isdir("/tmp") or os.path.islink("/tmp"):
        return _outcome(["Linux disposable kernel event monitor unavailable"])
    try:
        with tempfile.TemporaryDirectory(prefix="dec677-disposable-", dir="/tmp") as folder:
            path = Path(folder) / "sample"
            path.write_bytes(BEFORE)
            # Start observing both the inode and parent directory *before*
            # taking the baseline. A prewatch snapshot would leave an
            # unobserved gap before kernel watch registration.
            # Guard the helper return again at the runner boundary. A
            # patched registration must not close stdio, install a one-watch
            # "quiet" result, or reach filesystem reads with forged WDs.
            registered = _start_watch(path)
            if type(registered) is not tuple or len(registered) != 3:
                raise OSError("disposable watch registration has invalid shape")
            fd, wd, dir_wd = registered
            if type(fd) is not int or not 3 <= fd <= MAX_FILE_DESCRIPTOR:
                raise OSError("disposable watch registration has invalid file descriptor")
            try:
                if (type(wd) is not int or not 0 <= wd <= MAX_WATCH_DESCRIPTOR
                        or type(dir_wd) is not int
                        or not 0 <= dir_wd <= MAX_WATCH_DESCRIPTOR
                        or wd == dir_wd):
                    raise OSError("disposable watch registration has invalid watch identities")
                original_inode, original_bytes = _checked_snapshot_result(_snapshot_regular(path))
                if original_bytes != BEFORE:
                    raise OSError("disposable generated source baseline differs from fixture")
                midpoint_matches_expected = None
                if negative:
                    # This is generated public data; observe the intermediate
                    # changed inode/bytes rather than inferring a revert from
                    # a matching final digest plus event counts alone.
                    with open(path, "wb") as f:
                        f.write(AFTER)
                        f.flush()
                        os.fsync(f.fileno())
                    midpoint_inode, midpoint_bytes = _checked_snapshot_result(_snapshot_regular(path))
                    midpoint_matches_expected = (
                        midpoint_inode == original_inode and midpoint_bytes == AFTER
                    )
                    with open(path, "wb") as f:
                        f.write(BEFORE)
                        f.flush()
                        os.fsync(f.fileno())
                if replace_watched_inode:
                    # An inode-targeted watch is not an identity proof for a
                    # mutable pathname. Substitute a precreated identical file.
                    replacement = Path(folder) / "public-replacement"
                    replacement.write_bytes(BEFORE)
                    os.replace(replacement, path)
                sibling_path = Path(folder) / PERSISTENT_SIBLING_NAME
                sibling_initial_inode = None
                sibling_initial_bytes = None
                if create_sibling:
                    sibling_path.write_bytes(b"PUBLIC-EXTRA")
                    sibling_initial_inode, sibling_initial_bytes = _checked_snapshot_result(_snapshot_regular(sibling_path))
                transient_midpoint_verified = None
                if transient_sibling:
                    transient = Path(folder) / TRANSIENT_SIBLING_NAME
                    transient.write_bytes(b"PUBLIC-TEMPORARY")
                    # Prove this toy control really had the expected bounded
                    # regular file on disk before removing its directory entry.
                    transient_inode, transient_payload = _checked_snapshot_result(_snapshot_regular(transient))
                    transient_midpoint_verified = (
                        type(transient_inode) is tuple
                        and len(transient_inode) == 2
                        and transient_payload == b"PUBLIC-TEMPORARY"
                    )
                    transient.unlink()
                final_inode, end = _checked_snapshot_result(_snapshot_regular(path))
                if end != BEFORE:
                    raise OSError("disposable generated source final bytes differ from fixture")
                inventory_names = _bounded_inventory_names(Path(folder))
                inventory_ok = inventory_names == ("sample",)
                sibling_snapshot_stable = None
                if create_sibling:
                    # Open without following symlinks; type, inode and exact
                    # generated bytes must still match the earlier snapshot.
                    sibling_final_inode, sibling_final_bytes = _checked_snapshot_result(_snapshot_regular(sibling_path))
                    sibling_snapshot_stable = (
                        sibling_final_inode == sibling_initial_inode
                        and sibling_final_bytes == sibling_initial_bytes == b"PUBLIC-EXTRA"
                    )
                # Drain after final snapshots and directory enumeration, so
                # events emitted *during* those reads are not silently left
                # outside the disposable observer's sampled interval.
                raw = _read_pending(fd)
                return _evaluate(original_bytes, end, raw, wd, True, negative,
                                 inode_stable=(original_inode == final_inode),
                                 replacement_negative=replace_watched_inode,
                                 directory_watch=dir_wd,
                                 directory_inventory_ok=inventory_ok,
                                 directory_inventory_names=inventory_names,
                                 sibling_snapshot_stable=sibling_snapshot_stable,
                                 sibling_negative=create_sibling,
                                 transient_sibling_negative=transient_sibling,
                                 midpoint_snapshot_matches_expected=midpoint_matches_expected,
                                 transient_midpoint_verified=transient_midpoint_verified)
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
