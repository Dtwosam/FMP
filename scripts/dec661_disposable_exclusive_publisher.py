from __future__ import annotations

"""DEC-661: disposable exclusive external report witness; NEVER authorization."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import stat
import sys
import tempfile
from typing import Any, Callable

sys.dont_write_bytecode = True

MAX_BYTES = 1024 * 1024
REPORT_NAME = "synthetic-report.json"
PAYLOAD = b'{"disposable":true,"never_authorize":true}\n'


def _result(findings: list[str], checks: dict[str, bool] | None = None) -> dict[str, Any]:
    return {
        "status": "BLOCKED" if findings else "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED",
        "findings": sorted(set(findings)),
        "observed_checks": checks or {},
        "can_authorize_dispatch": False,
        "independent_os_proof_verified": False,
    }


def _write_all(fd: int, payload: bytes, writer: Callable[[int, bytes], int]) -> None:
    position = 0
    while position < len(payload):
        written = writer(fd, payload[position:])
        if type(written) is not int or written <= 0 or written > len(payload) - position:
            raise OSError("writer did not make bounded forward progress")
        position += written


def _publish_once(directory_fd: int, payload: bytes,
                  writer: Callable[[int, bytes], int] = os.write) -> None:
    """Create externally with O_EXCL; link completed bytes into final name.

    Requires a trusted single-writer *synthetic* directory; this does not prove
    security against concurrent privileged namespace writers or a real runner.
    """
    if not isinstance(payload, bytes) or not payload or len(payload) > MAX_BYTES:
        raise ValueError("invalid synthetic report payload")
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW |
             getattr(os, "O_CLOEXEC", 0))
    pending = ".pending-" + secrets.token_hex(16)
    fd = os.open(pending, flags, 0o600, dir_fd=directory_fd)
    try:
        _write_all(fd, payload, writer)
        os.fsync(fd)
        os.link(pending, REPORT_NAME, src_dir_fd=directory_fd,
                dst_dir_fd=directory_fd, follow_symlinks=False)
        # No rename-overwrite. An existing regular file, symlink, or FIFO
        # at REPORT_NAME raises FileExistsError rather than being replaced.
        os.fsync(directory_fd)
    finally:
        os.close(fd)
        os.unlink(pending, dir_fd=directory_fd)


def _read_report(directory_fd: int) -> bytes:
    fd = os.open(REPORT_NAME, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW,
                 dir_fd=directory_fd)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_BYTES:
            raise ValueError("synthetic report not a bounded regular file")
        data = os.read(fd, MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError("synthetic report bytes unbounded")
        return data
    finally:
        os.close(fd)


def run_demo() -> dict[str, Any]:
    if sys.platform != "linux" or not os.path.isdir("/tmp") or os.path.islink("/tmp"):
        return _result(["disposable Linux temporary root unavailable"])
    if (not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY")
            or any(fn not in os.supports_dir_fd for fn in (os.open, os.link, os.unlink))):
        return _result(["anchored exclusive publication primitives unavailable"])
    checks: dict[str, bool] = {}
    try:
        with tempfile.TemporaryDirectory(prefix="dec661-disposable-", dir="/tmp") as base:
            parent = Path(base)
            checkout, external, alias = (parent / "checkout", parent / "external", parent / "alias")
            checkout.mkdir()
            external.mkdir()
            alias.mkdir()
            sample = checkout / "sample"
            sample.write_bytes(b"DEC661_PUBLIC_SYNTHETIC_SOURCE\n")
            before = hashlib.sha256(sample.read_bytes()).hexdigest()
            dir_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
            external_fd = os.open(external, dir_flags)
            alias_fd = os.open(alias, dir_flags)
            try:
                _publish_once(external_fd, PAYLOAD)
                checks["external_bytes_exact"] = _read_report(external_fd) == PAYLOAD
                collision_denied = False
                try:
                    _publish_once(external_fd, b"collision")
                except FileExistsError:
                    collision_denied = True
                checks["existing_result_denied"] = collision_denied
                checks["collision_did_not_mutate_report"] = _read_report(external_fd) == PAYLOAD
                (alias / REPORT_NAME).symlink_to(checkout / "sample")
                alias_denied = False
                try:
                    _publish_once(alias_fd, b"symlink overwrite")
                except FileExistsError:
                    alias_denied = True
                checks["symlink_result_denied"] = alias_denied
                checks["symlink_target_unchanged"] = hashlib.sha256(sample.read_bytes()).hexdigest() == before
                failure = parent / "failed"
                failure.mkdir()
                failure_fd = os.open(failure, dir_flags)
                try:
                    def fail_writer(_fd: int, _data: bytes) -> int:
                        raise OSError("disposable simulated failure")
                    failed = False
                    try:
                        _publish_once(failure_fd, PAYLOAD, writer=fail_writer)
                    except OSError:
                        failed = True
                    checks["failed_write_denied"] = failed
                    checks["failed_write_no_final_or_temp"] = os.listdir(failure_fd) == []
                finally:
                    os.close(failure_fd)
                checks["pending_files_removed"] = sorted(os.listdir(external_fd)) == [REPORT_NAME]
                checks["checkout_unchanged"] = (hashlib.sha256(sample.read_bytes()).hexdigest() == before
                                                 and sorted(x.name for x in checkout.iterdir()) == ["sample"])
            finally:
                os.close(alias_fd)
                os.close(external_fd)
    except (OSError, ValueError):
        return _result(["disposable external publication setup or inspection failed"])
    failed_checks = ["disposable check not demonstrated: " + key
                     for key, passed in checks.items() if passed is not True]
    return _result(failed_checks, checks)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False,
        description="DEC-661 synthetic exclusive external publish audit; NEVER dispatch authority")
    parser.add_argument("--execute-disposable-demo", action="store_true")
    args = parser.parse_args(argv)
    result = run_demo() if args.execute_disposable_demo else _result(
        ["no disposable publication demonstration requested"])
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 3 if result["status"] == "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
