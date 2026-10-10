from __future__ import annotations

"""DEC-653 disposable Linux mount witness, NEVER annual-runner authorization.

Runs only against a newly created temporary checkout. No GitHub, network,
protected data, workflow dispatch or production paths are accepted as inputs.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import Any

sys.dont_write_bytecode = True

# The setup process is privileged *only inside its disposable user namespace*.
# It creates a read-only bind mount of the disposable checkout and then runs
# a child with all capability sets empty. No host mount is changed.
_NAMESPACE_SETUP = r'''
import fcntl, json, os, subprocess, sys
source, external, executable, inject = sys.argv[1:]
# In both modes, open a writable FD before remount, to test closure.
original = os.open(os.path.join(source, "sample"), os.O_WRONLY)
preopened = fcntl.fcntl(original, fcntl.F_DUPFD_CLOEXEC, 200)
os.close(original)
# A PUBLIC fake credential is created only in our disposable external directory.
# The negative control passes a read-only handle as child FD0.
fake_canary = b"DEC658_PUBLIC_FAKE_CREDENTIAL\n"
canary_path = os.path.join(external, "synthetic-canary")
with open(canary_path, "wb") as handle:
    handle.write(fake_canary)
canary_fd = os.open(canary_path, os.O_RDONLY | os.O_CLOEXEC) if inject == "3" else None
def run(*argv):
    subprocess.run(argv, check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, timeout=8)
run("mount", "--make-rprivate", "/")
run("mount", "--bind", source, source)
run("mount", "-o", "remount,bind,ro", source)
args = ["setpriv", "--bounding-set=-all", "--inh-caps=-all",
        "--ambient-caps=-all", "--no-new-privs", "--", executable,
        "-B", "-c", "__ATTACK__", source, external,
        str(preopened), inject]
child_env = {"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LANG": "C"}
if inject == "4":
    # PUBLIC test marker, never any real repository credential or token.
    child_env["DEC659_SYNTHETIC_ACCESS_TOKEN"] = "DEC659_PUBLIC_FAKE_CANARY"
try:
    p = subprocess.run(args,
                       stdin=canary_fd if inject == "3" else subprocess.DEVNULL,
                       stdout=preopened if inject == "2" else subprocess.PIPE,
                       stderr=subprocess.PIPE,
                       text=True, timeout=10, env=child_env, close_fds=True,
                       pass_fds=(preopened,) if inject == "1" else ())
finally:
    os.close(preopened)
    if canary_fd is not None:
        os.close(canary_fd)
if p.returncode != 0:
    raise SystemExit(11)
print(p.stderr if inject == "2" else p.stdout, end="")
'''

_RESTRICTED_ATTACK = r'''
import json, os, subprocess, sys
source, external, inherited_fd, inject = sys.argv[1:]
probe = "unknown"
try:
    os.write(int(inherited_fd), b"INHERITED_FD_BYPASS\n")
except OSError as exc:
    probe = "closed_before_consumer" if exc.errno == 9 else "other_write_error"
else:
    probe = "write_succeeded"
# All modes explicitly probe FD0. /dev/null gives EOF in clean modes;
# a malicious inherited fake credential handle exposes only a public canary.
stdin_bytes = os.read(0, 64)
if stdin_bytes == b"":
    stdin_probe = "safe_eof"
elif stdin_bytes == b"DEC658_PUBLIC_FAKE_CREDENTIAL\n":
    stdin_probe = "canary_received"
else:
    stdin_probe = "unexpected_input"
environment_value = os.environ.get("DEC659_SYNTHETIC_ACCESS_TOKEN")
if environment_value is None:
    env_probe = "absent"
elif environment_value == "DEC659_PUBLIC_FAKE_CANARY":
    env_probe = "canary_present"
else:
    env_probe = "unexpected_value"
stdio_probe = "not_provided"
if inject == "2":
    try:
        os.write(1, b"STDIO_FD_BYPASS\n")
    except OSError:
        stdio_probe = "write_denied"
    else:
        stdio_probe = "write_succeeded"
status = {}
for line in open("/proc/self/status", encoding="ascii"):
    key = line.split(":", 1)[0]
    if key in ("CapEff", "CapPrm", "CapBnd", "CapAmb", "NoNewPrivs"):
        status[key] = line.split(":", 1)[1].strip()
checks = {}
def denied(label, action):
    try:
        action()
    except OSError:
        checks[label] = True
    else:
        checks[label] = False
denied("create", lambda: open(os.path.join(source, "injected"), "wb").close())
denied("truncate", lambda: open(os.path.join(source, "sample"), "wb").close())
denied("chmod", lambda: os.chmod(os.path.join(source, "sample"), 0o666))
os.makedirs(os.path.join(external, "reparent"), exist_ok=True)
denied("reparent", lambda: os.rename(os.path.join(external, "reparent"), os.path.join(source, "reparent")))
p = subprocess.run(["mount", "-o", "remount,bind,rw", source],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                   timeout=5, check=False)
checks["remount"] = p.returncode != 0
mounts = open("/proc/self/mountinfo", encoding="utf-8").read().splitlines()
checks["readonly_mount"] = any((len(f := line.split()) >= 6 and
                                  f[4] == source and "ro" in f[5].split(","))
                                 for line in mounts)
print(json.dumps({"checks": checks, "status": status,
                  "inherited_fd_probe": probe,
                  "stdio_probe": stdio_probe,
                  "stdin_probe": stdin_probe,
                  "env_probe": env_probe}, sort_keys=True),
      file=sys.stderr if inject == "2" else sys.stdout)
'''

CHECKS = ("create", "truncate", "chmod", "reparent", "remount", "readonly_mount")
CAPS = ("CapEff", "CapPrm", "CapBnd", "CapAmb")


def _result(status: str, findings: list[str], checks: dict[str, bool] | None = None) -> dict[str, Any]:
    return {
        "status": status,
        "findings": sorted(set(findings)),
        "observed_checks": checks or {},
        "can_authorize_dispatch": False,
        "independent_os_proof_verified": False,
    }


def _evaluate(raw: Any, unchanged: bool) -> dict[str, Any]:
    """Interpret *untrusted* local witness output; never certify isolation."""
    if not isinstance(raw, dict) or not isinstance(raw.get("checks"), dict) or not isinstance(raw.get("status"), dict):
        return _result("BLOCKED", ["synthetic witness output is malformed"])
    checks, proc = raw["checks"], raw["status"]
    findings = []
    if raw.get("inherited_fd_probe") != "closed_before_consumer":
        findings.append("writable checkout descriptor inherited or unaccounted for")
    if raw.get("stdio_probe") != "not_provided":
        findings.append("checkout-writable standard stream inherited or unaccounted for")
    if raw.get("stdin_probe") != "safe_eof":
        findings.append("standard input descriptor exposed data or lacks safe provenance")
    if raw.get("env_probe") != "absent":
        findings.append("synthetic credential environment reached restricted process")
    for name in CHECKS:
        if checks.get(name) is not True:
            findings.append("OS denial not demonstrated: " + name)
    for name in CAPS:
        val = proc.get(name)
        if not isinstance(val, str) or not val or set(val) != {"0"}:
            findings.append("restricted capability field not zero: " + name)
    if proc.get("NoNewPrivs") != "1":
        findings.append("no_new_privs is not observed true")
    if not unchanged:
        findings.append("disposable checkout inventory changed")
    return _result("BLOCKED" if findings else "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED", findings,
                   {name: checks.get(name) is True for name in CHECKS})


def _sample_snapshot(directory_fd: int) -> tuple[int, int, str] | None:
    """Snapshot synthetic file by anchored FD, never follow a swapped symlink."""
    flags = os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    fd = os.open("sample", flags, dir_fd=directory_fd)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size > 4096:
            return None
        data = os.read(fd, 4097)
        if len(data) > 4096:
            return None
        return (info.st_dev, info.st_ino, hashlib.sha256(data).hexdigest())
    finally:
        os.close(fd)


def _unchanged_disposable_source(source: Path, directory_fd: int,
                                 original_dir: os.stat_result,
                                 original_snapshot: tuple[int, int, str] | None) -> bool:
    """Check pinned synthetic inode and directory, with no path-following reads."""
    try:
        now = os.stat(source, follow_symlinks=False)
        if (now.st_dev, now.st_ino) != (original_dir.st_dev, original_dir.st_ino):
            return False
        return (original_snapshot is not None
                and _sample_snapshot(directory_fd) == original_snapshot
                and sorted(os.listdir(directory_fd)) == ["sample"])
    except OSError:
        return False


def run_demo(inject_checkout_fd: bool = False, inject_stdout_fd: bool = False,
             inject_stdin_fd: bool = False, inject_env_canary: bool = False) -> dict[str, Any]:
    """Run only against internally generated disposable data, never a supplied path."""
    if sum((inject_checkout_fd, inject_stdout_fd, inject_stdin_fd, inject_env_canary)) > 1:
        return _result("BLOCKED", ["conflicting synthetic descriptor-injection modes"])
    if sys.platform != "linux" or not all(shutil.which(n) for n in ("unshare", "mount", "setpriv")):
        return _result("BLOCKED", ["Linux namespace prerequisites unavailable"])
    # Fixed trusted scratch root: caller-controlled TMPDIR must never route
    # our synthetic writes into an arbitrary repository or protected tree.
    if not os.path.isdir("/tmp") or os.path.islink("/tmp"):
        return _result("BLOCKED", ["fixed disposable temporary root is unavailable"])
    with tempfile.TemporaryDirectory(prefix="dec653-disposable-", dir="/tmp") as directory:
        source = Path(directory) / "checkout"
        external = Path(directory) / "external"
        source.mkdir(mode=0o700)
        external.mkdir(mode=0o700)
        sample = source / "sample"
        sample.write_bytes(b"DEC653_DISPOSABLE_ONLY\n")
        directory_fd = os.open(source, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            original_dir = os.fstat(directory_fd)
            before = _sample_snapshot(directory_fd)
            setup = _NAMESPACE_SETUP.replace('"__ATTACK__"', repr(_RESTRICTED_ATTACK))
            try:
                p = subprocess.run(
                    ["unshare", "--user", "--map-root-user", "--mount", "--",
                     sys.executable, "-B", "-c", setup, str(source), str(external), sys.executable,
                     "4" if inject_env_canary else ("3" if inject_stdin_fd else ("2" if inject_stdout_fd else ("1" if inject_checkout_fd else "0")))],
                    cwd=directory, stdin=subprocess.DEVNULL, capture_output=True,
                    text=True, timeout=25, close_fds=True,
                    env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LANG": "C"},
                    check=False,
                )
            except (OSError, subprocess.TimeoutExpired):
                return _result("BLOCKED", ["disposable namespace witness could not execute"])
            unchanged = _unchanged_disposable_source(source, directory_fd, original_dir, before)
            if p.returncode != 0:
                return _result("BLOCKED", ["disposable namespace setup or child failed"])
            try:
                raw = json.loads(p.stdout)
            except (ValueError, TypeError):
                return _result("BLOCKED", ["disposable witness did not produce valid JSON"])
            return _evaluate(raw, unchanged)
        finally:
            os.close(directory_fd)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DEC-653 disposable Linux OS-denial witness; NEVER annual authorization", add_help=False)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--execute-disposable-demo", action="store_true")
    modes.add_argument("--execute-fd-counterexample", action="store_true")
    modes.add_argument("--execute-stdio-counterexample", action="store_true")
    modes.add_argument("--execute-stdin-counterexample", action="store_true")
    modes.add_argument("--execute-env-counterexample", action="store_true")
    args = parser.parse_args(argv)
    if (args.execute_disposable_demo or args.execute_fd_counterexample
            or args.execute_stdio_counterexample or args.execute_stdin_counterexample
            or args.execute_env_counterexample):
        result = run_demo(inject_checkout_fd=args.execute_fd_counterexample,
                          inject_stdout_fd=args.execute_stdio_counterexample,
                          inject_stdin_fd=args.execute_stdin_counterexample,
                          inject_env_canary=args.execute_env_counterexample)
    else:
        result = _result("BLOCKED", ["explicit disposable demo opt-in required"])
    print(json.dumps(result, separators=(",", ":"), sort_keys=True))
    return 3 if result["status"] == "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
