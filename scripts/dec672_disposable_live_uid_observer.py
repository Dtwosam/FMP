from __future__ import annotations

"""DEC-672: parent-observed live synthetic UID boundary; NEVER authorize dispatch."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import select
import shutil
import subprocess
import sys
import tempfile
from typing import Any

sys.dont_write_bytecode = True

SOURCE_BYTES = b"DEC672_PUBLIC_FAKE_CHECKOUT\n"
REPORT_BYTES = b"DEC672_PUBLIC_FAKE_REPORT\n"
CAP_FIELDS = ("CapEff", "CapPrm", "CapBnd", "CapAmb")
PARENT_CHECKS = (
    "live_uid", "live_gid", "live_groups_empty", "live_capabilities_zero",
    "live_no_new_privs", "live_safe_stdio", "live_scratch_cwd",
    "live_no_unexpected_fd", "live_no_checkout_or_report_fd", "live_stable_observation",
    "live_fd_targets_readable", "live_cwd_readable",
)
CHILD_CHECKS = (
    "source_readable", "source_create_denied", "source_truncate_denied",
    "source_chmod_denied", "source_reparent_denied", "report_create_denied",
    "report_read_denied", "report_write_denied",
)
POST_CHECKS = ("source_unchanged", "report_unchanged", "child_exited_cleanly")

_CHILD = r'''
import json, os, sys
checkout, external, scratch = sys.argv[1:]
sys.stdout.buffer.write(b"R")
sys.stdout.buffer.flush()
if sys.stdin.buffer.read(1) != b"X":
    raise SystemExit(10)
checks = {}
checks["source_readable"] = open(os.path.join(checkout, "sample"), "rb").read() == b"DEC672_PUBLIC_FAKE_CHECKOUT\n"
def denial(label, op):
    try:
        op()
    except PermissionError:
        checks[label] = True
    except OSError:
        checks[label] = False
    else:
        checks[label] = False
denial("source_create_denied", lambda: open(os.path.join(checkout, "injected"), "wb").close())
denial("source_truncate_denied", lambda: open(os.path.join(checkout, "sample"), "wb").close())
denial("source_chmod_denied", lambda: os.chmod(os.path.join(checkout, "sample"), 0o666))
denial("source_reparent_denied", lambda: os.rename(os.path.join(scratch, "dummy"), os.path.join(checkout, "dummy")))
denial("report_create_denied", lambda: open(os.path.join(external, "injected"), "wb").close())
denial("report_read_denied", lambda: open(os.path.join(external, "report"), "rb").close())
denial("report_write_denied", lambda: open(os.path.join(external, "report"), "wb").close())
print(json.dumps({"checks": checks}, sort_keys=True))
'''


def _result(findings: list[str], checks: dict[str, bool] | None = None) -> dict[str, Any]:
    return {
        "status": "BLOCKED" if findings else "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED",
        "findings": sorted(set(findings)),
        "observed_checks": checks or {},
        "can_authorize_dispatch": False,
        "independent_os_proof_verified": False,
    }


def _evaluate(checks: Any, injected: bool = False) -> dict[str, Any]:
    if not isinstance(checks, dict):
        return _result(["parent and child observations malformed"])
    required = PARENT_CHECKS + CHILD_CHECKS + POST_CHECKS
    missing = ["observation missing or false: " + name for name in required
               if checks.get(name) is not True]
    if injected:
        missing.append("deliberately inherited writable checkout FD must BLOCK")
        if checks.get("live_no_unexpected_fd") is True or checks.get("live_no_checkout_or_report_fd") is True:
            missing.append("injected descriptor failed to appear in independent observer")
    return _result(missing, {name: checks.get(name) is True for name in required})


def _parse_status(data: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in data.splitlines():
        key, colon, value = line.partition(":")
        if colon and key not in parsed:
            parsed[key] = value.strip()
    return parsed


def _read_live(pid: int, checkout: Path, external: Path, scratch: Path) -> dict[str, bool]:
    """Two parent-side snapshots while a fixed, still-running child is paused."""
    root = Path("/proc") / str(pid)
    fd_dir = os.open(root / "fd", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        def capture():
            names = os.listdir(fd_dir)
            if len(names) > 32 or any(not x.isdecimal() for x in names):
                raise OSError("unexpected synthetic descriptor table")
            # Root in an unprivileged container may NOT have permission to
            # dereference another UID's /proc/PID/fd or cwd (ptrace access).
            # This is a hard fail-closed blocker, not a successful snapshot.
            readable_fds = True
            try:
                targets = {int(name): os.readlink(name, dir_fd=fd_dir) for name in names}
            except PermissionError:
                targets = {}
                readable_fds = False
            with open(root / "status", "r", encoding="ascii") as f:
                status = _parse_status(f.read(16385))
            readable_cwd = True
            try:
                cwd = os.readlink(root / "cwd")
            except PermissionError:
                cwd = None
                readable_cwd = False
            return targets, status, cwd, readable_fds, readable_cwd
        before = capture()
        after = capture()
    finally:
        os.close(fd_dir)
    targets, status, cwd, readable_fds, readable_cwd = after
    prefixes = (str(checkout), str(external))
    leaked = any(t == prefix or t.startswith(prefix + os.sep)
                 for t in targets.values() for prefix in prefixes)
    def ids_match(key: str):
        fields = status.get(key, "").split()
        return len(fields) == 4 and all(x == "65534" for x in fields)
    def zero_caps():
        try:
            return all(status.get(k) and int(status[k], 16) == 0 for k in CAP_FIELDS)
        except ValueError:
            return False
    return {
        "live_uid": ids_match("Uid"),
        "live_gid": ids_match("Gid"),
        "live_groups_empty": status.get("Groups") == "",
        "live_capabilities_zero": zero_caps(),
        "live_no_new_privs": status.get("NoNewPrivs") == "1",
        "live_safe_stdio": all(targets.get(i, "").startswith("pipe:[") for i in (0, 1, 2)),
        "live_scratch_cwd": cwd == str(scratch),
        "live_no_unexpected_fd": set(targets) == {0, 1, 2},
        "live_no_checkout_or_report_fd": readable_fds and not leaked,
        "live_stable_observation": readable_fds and readable_cwd and before == after,
        "live_fd_targets_readable": readable_fds,
        "live_cwd_readable": readable_cwd,
    }


def run_demo(inject_checkout_fd: bool = False) -> dict[str, Any]:
    if (sys.platform != "linux" or os.geteuid() != 0 or not shutil.which("setpriv")
            or not Path("/proc/self/status").is_file()):
        return _result(["root Linux setpriv and procfs prerequisites unavailable"])
    if not os.path.isdir("/tmp") or os.path.islink("/tmp"):
        return _result(["fixed temporary root unavailable"])
    try:
        with tempfile.TemporaryDirectory(prefix="dec672-fake-", dir="/tmp") as base:
            root = Path(base)
            checkout, external, scratch = (root / "checkout", root / "external", root / "scratch")
            checkout.mkdir(mode=0o755)
            external.mkdir(mode=0o700)
            scratch.mkdir(mode=0o777)
            sample, report = checkout / "sample", external / "report"
            sample.write_bytes(SOURCE_BYTES)
            report.write_bytes(REPORT_BYTES)
            sample.chmod(0o444)
            report.chmod(0o400)
            (scratch / "dummy").write_bytes(b"DEC672_PUBLIC_DUMMY")
            (scratch / "dummy").chmod(0o666)
            scratch.chmod(0o777)
            root.chmod(0o755)
            src_before = hashlib.sha256(sample.read_bytes()).hexdigest()
            report_before = hashlib.sha256(report.read_bytes()).hexdigest()
            opened = os.open(sample, os.O_WRONLY | os.O_CLOEXEC)
            child = None
            try:
                child = subprocess.Popen(
                    ["setpriv", "--reuid=65534", "--regid=65534", "--clear-groups",
                     "--bounding-set=-all", "--inh-caps=-all", "--ambient-caps=-all",
                     "--no-new-privs", "--", sys.executable, "-B", "-c", _CHILD,
                     str(checkout), str(external), str(scratch)],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    cwd=scratch, close_fds=True,
                    pass_fds=(opened,) if inject_checkout_fd else (),
                    env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LANG": "C"},
                )
            finally:
                os.close(opened)
            observed = {}
            success = False
            try:
                ready, _, _ = select.select([child.stdout], [], [], 5)
                if not ready or os.read(child.stdout.fileno(), 1) != b"R":
                    raise OSError("paused restricted child readiness not observed")
                observed = _read_live(child.pid, checkout, external, scratch)
                stdout, stderr = child.communicate(input=b"X", timeout=10)
                if child.returncode == 0 and not stderr and len(stdout) <= 4096:
                    try:
                        raw = json.loads(stdout)
                    except ValueError:
                        raw = None
                    if isinstance(raw, dict) and isinstance(raw.get("checks"), dict):
                        observed.update({name: raw["checks"].get(name) is True
                                         for name in CHILD_CHECKS})
                        success = True
            finally:
                if child.poll() is None:
                    child.kill()
                    child.communicate(timeout=3)
            observed["child_exited_cleanly"] = success
            observed["source_unchanged"] = (
                hashlib.sha256(sample.read_bytes()).hexdigest() == src_before
                and sorted(x.name for x in checkout.iterdir()) == ["sample"])
            observed["report_unchanged"] = (
                hashlib.sha256(report.read_bytes()).hexdigest() == report_before
                and sorted(x.name for x in external.iterdir()) == ["report"])
            return _evaluate(observed, injected=inject_checkout_fd)
    except (OSError, ValueError, subprocess.SubprocessError):
        return _result(["disposable live UID observation failed"])


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(add_help=False,
        description="DEC-672 disposable live UID observer, NEVER annual authorization")
    options = p.add_mutually_exclusive_group()
    options.add_argument("--execute-disposable-demo", action="store_true")
    options.add_argument("--execute-leaked-fd-control", action="store_true")
    args = p.parse_args(argv)
    result = (run_demo(inject_checkout_fd=args.execute_leaked_fd_control)
              if (args.execute_disposable_demo or args.execute_leaked_fd_control)
              else _result(["explicit disposable live UID observation opt-in missing"]))
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 3 if result["status"] == "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
