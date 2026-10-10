from __future__ import annotations

"""DEC-674: disposable transient write/revert shows inventory digests miss events."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
from typing import Any

sys.dont_write_bytecode = True
BEFORE = b"DEC674_PUBLIC_FAKE_SOURCE\n"
TRANSIENT = b"DEC674_PUBLIC_TRANSIENT_CHANGE\n"


def assess(read_before: bytes, read_after: bytes, write_events: Any, observer_valid: bool) -> dict[str, Any]:
    """The event count is an offline synthetic hook, NOT OS audit evidence."""
    checks = {
        "final_bytes_equal": read_before == read_after,
        "digest_equal": hashlib.sha256(read_before).digest() == hashlib.sha256(read_after).digest(),
        "observer_record_present": type(write_events) is int and write_events >= 0 and observer_valid is True,
        "no_observed_writes": type(write_events) is int and write_events == 0 and observer_valid is True,
    }
    findings = ["disposable check missing or false: " + name for name, good in checks.items() if good is not True]
    return {
        "status": "BLOCKED" if findings else "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED",
        "findings": sorted(findings),
        "observed_checks": checks,
        "can_authorize_dispatch": False,
        "independent_os_proof_verified": False,
    }


def run_demo(inject_transient_write: bool = False) -> dict[str, Any]:
    if sys.platform != "linux" or not os.path.isdir("/tmp") or os.path.islink("/tmp"):
        return assess(BEFORE, BEFORE, None, False)
    try:
        with tempfile.TemporaryDirectory(prefix="dec674-public-", dir="/tmp") as directory:
            root = Path(directory)
            file = root / "sample"
            file.write_bytes(BEFORE)
            fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                source = os.open("sample", os.O_RDONLY | os.O_NOFOLLOW, dir_fd=fd)
                try:
                    info = os.fstat(source)
                    if not stat.S_ISREG(info.st_mode) or info.st_size > 256:
                        return assess(BEFORE, b"", None, False)
                    before = os.read(source, 257)
                finally:
                    os.close(source)
                events = 0
                if inject_transient_write:
                    # A disposable actor is deliberately given write authority.
                    # Two real writes occur; the final bytes are identical.
                    with open(file, "wb") as f:
                        f.write(TRANSIENT)
                        f.flush()
                        os.fsync(f.fileno())
                        events += 1
                    with open(file, "wb") as f:
                        f.write(BEFORE)
                        f.flush()
                        os.fsync(f.fileno())
                        events += 1
                source = os.open("sample", os.O_RDONLY | os.O_NOFOLLOW, dir_fd=fd)
                try:
                    after = os.read(source, 257)
                finally:
                    os.close(source)
                if sorted(os.listdir(fd)) != ["sample"]:
                    return assess(before, after, events, False)
                return assess(before, after, events, True)
            finally:
                os.close(fd)
    except (OSError, ValueError):
        return assess(BEFORE, BEFORE, None, False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False,
        description="DEC-674 offline transient-write digest blindness witness; NEVER dispatch")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--execute-disposable-control", action="store_true")
    modes.add_argument("--execute-reverted-write-negative", action="store_true")
    args = parser.parse_args(argv)
    result = (run_demo(inject_transient_write=args.execute_reverted_write_negative)
              if args.execute_disposable_control or args.execute_reverted_write_negative
              else assess(BEFORE, BEFORE, None, False))
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 3 if result["status"] == "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
