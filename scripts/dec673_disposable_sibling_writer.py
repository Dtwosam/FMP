from __future__ import annotations

"""DEC-673: privileged sibling writer invalidates restricted-UID-only proof."""

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
ORIGINAL = b"DEC673_PUBLIC_SYNTHETIC_SOURCE\n"
REPLACED = b"DEC673_PRIVILEGED_SIBLING_CHANGE\n"
CHILD = r'''
import json, os, sys
source = sys.argv[1]
sys.stdout.buffer.write(b"R")
sys.stdout.buffer.flush()
if sys.stdin.buffer.read(1) != b"X":
    raise SystemExit(9)
try:
    with open(os.path.join(source, "sample"), "wb") as writer:
        writer.write(b"NOT_ALLOWED")
except PermissionError:
    denied = True
else:
    denied = False
print(json.dumps({"write_denied": denied, "uid_restricted": os.geteuid() == 65534}))
'''


def _result(observed: Any, sibling_injected: bool) -> dict[str, Any]:
    if not isinstance(observed, dict):
        return {"status": "BLOCKED", "findings": ["synthetic observation invalid"],
                "can_authorize_dispatch": False, "independent_os_proof_verified": False}
    required = ("restricted_write_denied", "restricted_uid", "source_unchanged",
                "source_inventory_unchanged", "child_exited_cleanly")
    findings = ["synthetic boundary missing or false: " + name
                for name in required if observed.get(name) is not True]
    if sibling_injected:
        findings.append("privileged sibling writer was deliberately allowed to mutate fake source")
        if observed.get("source_unchanged") is True:
            findings.append("synthetic sibling-write negative control not detected")
    return {
        "status": "BLOCKED" if findings else "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED",
        "findings": sorted(set(findings)),
        "observed_checks": {name: observed.get(name) is True for name in required},
        "can_authorize_dispatch": False,
        "independent_os_proof_verified": False,
    }


def run_demo(inject_privileged_sibling: bool = False) -> dict[str, Any]:
    if (sys.platform != "linux" or os.geteuid() != 0 or not shutil.which("setpriv")
            or not os.path.isdir("/tmp") or os.path.islink("/tmp")):
        return _result(None, inject_privileged_sibling)
    try:
        with tempfile.TemporaryDirectory(prefix="dec673-disposable-", dir="/tmp") as directory:
            root = Path(directory)
            source, scratch = root / "checkout", root / "scratch"
            source.mkdir(mode=0o755)
            scratch.mkdir(mode=0o777)
            sample = source / "sample"
            sample.write_bytes(ORIGINAL)
            sample.chmod(0o444)
            root.chmod(0o755)
            scratch.chmod(0o777)
            before = hashlib.sha256(sample.read_bytes()).hexdigest()
            child = subprocess.Popen(
                ["setpriv", "--reuid=65534", "--regid=65534", "--clear-groups",
                 "--bounding-set=-all", "--inh-caps=-all", "--ambient-caps=-all",
                 "--no-new-privs", "--", sys.executable, "-B", "-c", CHILD, str(source)],
                cwd=scratch, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, close_fds=True,
                env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LANG": "C"},
            )
            result = None
            clean_exit = False
            try:
                ready, _, _ = select.select([child.stdout], [], [], 5)
                if not ready or os.read(child.stdout.fileno(), 1) != b"R":
                    raise OSError("restricted toy child did not reach barrier")
                # A separate host principal with root-level write authority
                # remains able to modify the same synthetic file, despite
                # the child's denied write attempts and read-only file mode.
                if inject_privileged_sibling:
                    with open(sample, "wb") as writer:
                        writer.write(REPLACED)
                stdout, stderr = child.communicate(input=b"X", timeout=9)
                if child.returncode == 0 and not stderr and len(stdout) < 1024:
                    result = json.loads(stdout)
                    clean_exit = isinstance(result, dict)
            finally:
                if child.poll() is None:
                    child.kill()
                    child.communicate(timeout=3)
            return _result({
                "restricted_write_denied": isinstance(result, dict) and result.get("write_denied") is True,
                "restricted_uid": isinstance(result, dict) and result.get("uid_restricted") is True,
                "source_unchanged": hashlib.sha256(sample.read_bytes()).hexdigest() == before,
                "source_inventory_unchanged": sorted(x.name for x in source.iterdir()) == ["sample"],
                "child_exited_cleanly": clean_exit,
            }, inject_privileged_sibling)
    except (OSError, ValueError, subprocess.SubprocessError):
        return _result(None, inject_privileged_sibling)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(add_help=False,
        description="DEC-673 disposable host-sibling writer counterexample; NEVER dispatch")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--execute-disposable-control", action="store_true")
    group.add_argument("--execute-privileged-sibling-negative", action="store_true")
    args = p.parse_args(argv)
    if args.execute_disposable_control or args.execute_privileged_sibling_negative:
        verdict = run_demo(inject_privileged_sibling=args.execute_privileged_sibling_negative)
    else:
        verdict = _result(None, False)
    print(json.dumps(verdict, sort_keys=True, separators=(",", ":")))
    return 3 if verdict["status"] == "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
