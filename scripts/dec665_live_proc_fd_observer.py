from __future__ import annotations

"""DEC-665: disposable live /proc FD observer, source-only and NEVER authorizing.

There is NO caller-supplied filesystem path and NO annual-runner integration.
The watched child waits for a byte on a private pipe while the parent observes
its live descriptor targets. No credential values or absolute paths are emitted.
"""

import argparse
import json
import os
import select
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

sys.dont_write_bytecode = True

_CHILD = ("import sys;sys.stdout.buffer.write(b'R');"
          "sys.stdout.buffer.flush();sys.stdin.buffer.read(1)")
_REQUIRED = ("stdio_pipes", "safe_cwd", "no_checkout_fd", "no_extra_fd", "child_exited")


def _result(findings: list[str], checks: dict[str, bool] | None = None) -> dict[str, Any]:
    return {
        "status": "BLOCKED" if findings else "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED",
        "findings": sorted(set(findings)),
        "observed_checks": checks or {},
        "can_authorize_dispatch": False,
        "independent_os_proof_verified": False,
    }


def _evaluate(raw: Any, injected: bool) -> dict[str, Any]:
    """Untrusted observation classification; never actual isolation approval."""
    if not isinstance(raw, dict):
        return _result(["live synthetic process observation missing"])
    missing = [field for field in _REQUIRED if raw.get(field) is not True]
    findings = ["live observer check missing or false: " + field for field in missing]
    if injected:
        findings.append("synthetic checkout descriptor injection is a negative control")
        if raw.get("no_checkout_fd") is True:
            findings.append("expected synthetic leaked checkout FD was not observed")
    return _result(findings, {field: raw.get(field) is True for field in _REQUIRED})


def _read_fd_targets(fd_directory: int) -> dict[int, str]:
    """Bounded FD-relative read of procfs symlinks, without opening FD targets."""
    names = os.listdir(fd_directory)
    if len(names) > 128:
        raise OSError("synthetic child has an unexpectedly large FD table")
    targets: dict[int, str] = {}
    for name in names:
        if not name.isdecimal():
            raise OSError("unexpected proc fd entry")
        targets[int(name)] = os.readlink(name, dir_fd=fd_directory)
    return targets


def _require_stable_snapshot(before: dict[int, str], after: dict[int, str],
                             cwd_before: str, cwd_after: str) -> tuple[dict[int, str], str]:
    """Reject changed FD topology or cwd even across two immediate scans."""
    if before != after:
        raise OSError("live child descriptor targets changed between snapshots")
    if cwd_before != cwd_after:
        raise OSError("live child cwd changed between snapshots")
    return after, cwd_after


def _snapshot(pid: int, checkout: Path, expected_cwd: Path) -> dict[str, bool]:
    """Take two consistent FD snapshots while the paused fake child is alive.

    A stable pair is NOT continuous confinement or independently attested
    safety on an actual runner.
    """
    proc_root = Path("/proc") / str(pid)
    fd_dir = os.open(proc_root / "fd", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        first = _read_fd_targets(fd_dir)
        cwd_first = os.readlink(proc_root / "cwd")
        second = _read_fd_targets(fd_dir)
        cwd_second = os.readlink(proc_root / "cwd")
    finally:
        os.close(fd_dir)
    targets, cwd = _require_stable_snapshot(first, second, cwd_first, cwd_second)
    checkout_prefix = str(checkout) + os.sep
    checkout_fd = any(t == str(checkout) or t.startswith(checkout_prefix)
                      for t in targets.values())
    return {
        "stdio_pipes": all(targets.get(fd, "").startswith("pipe:[") for fd in (0, 1, 2)),
        "safe_cwd": cwd == str(expected_cwd),
        "no_checkout_fd": not checkout_fd,
        "no_extra_fd": set(targets) == {0, 1, 2},
    }


def run_demo(inject_checkout_fd: bool = False) -> dict[str, Any]:
    if sys.platform != "linux" or not Path("/proc/self/fd").is_dir():
        return _result(["Linux live procfd observer is unavailable"])
    if not os.path.isdir("/tmp") or os.path.islink("/tmp"):
        return _result(["fixed synthetic temporary root unavailable"])
    try:
        with tempfile.TemporaryDirectory(prefix="dec665-observer-", dir="/tmp") as directory:
            base = Path(directory)
            checkout, scratch = base / "checkout", base / "scratch"
            checkout.mkdir(mode=0o700)
            scratch.mkdir(mode=0o700)
            sample = checkout / "sample"
            sample.write_bytes(b"DEC665_PUBLIC_SYNTHETIC_FILE\n")
            original = sample.read_bytes()
            fake_fd = os.open(sample, os.O_WRONLY | os.O_CLOEXEC)
            child = None
            try:
                child = subprocess.Popen(
                    [sys.executable, "-B", "-c", _CHILD],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, cwd=scratch,
                    close_fds=True, pass_fds=(fake_fd,) if inject_checkout_fd else (),
                    env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LANG": "C"},
                )
            finally:
                os.close(fake_fd)
            raw: dict[str, bool] = {}
            exit_ok = False
            try:
                # Verify the interpreter is actually at its paused read, not
                # still transiently opening bootstrap descriptors pre-exec.
                ready, _, _ = select.select([child.stdout], [], [], 5)
                if not ready or os.read(child.stdout.fileno(), 1) != b"R":
                    raise OSError("synthetic child did not reach observer barrier")
                raw = _snapshot(child.pid, checkout, scratch)
            finally:
                try:
                    stdout, stderr = child.communicate(input=b"X", timeout=8)
                    exit_ok = (child.returncode == 0 and not stdout and not stderr)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.communicate(timeout=3)
            raw["child_exited"] = exit_ok
            if sample.read_bytes() != original or sorted(x.name for x in checkout.iterdir()) != ["sample"]:
                raw["no_checkout_fd"] = False
            return _evaluate(raw, inject_checkout_fd)
    except (OSError, ValueError, subprocess.SubprocessError):
        return _result(["live disposable process observation failed"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="DEC-665 offline live procfd observation; NEVER authorization",
        add_help=False,
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--execute-disposable-demo", action="store_true")
    mode.add_argument("--execute-fd-negative-control", action="store_true")
    args = parser.parse_args(argv)
    if args.execute_disposable_demo or args.execute_fd_negative_control:
        outcome = run_demo(inject_checkout_fd=args.execute_fd_negative_control)
    else:
        outcome = _result(["no disposable live observer demonstration requested"])
    print(json.dumps(outcome, sort_keys=True, separators=(",", ":")))
    return 3 if outcome["status"] == "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
