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
import subprocess
import sys
import tempfile
from typing import Any

sys.dont_write_bytecode = True

# The setup process is privileged *only inside its disposable user namespace*.
# It creates a read-only bind mount of the disposable checkout and then runs
# a child with all capability sets empty. No host mount is changed.
_NAMESPACE_SETUP = r'''
import json, os, subprocess, sys
source, external, executable = sys.argv[1:]
def run(*argv):
    subprocess.run(argv, check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, timeout=8)
run("mount", "--make-rprivate", "/")
run("mount", "--bind", source, source)
run("mount", "-o", "remount,bind,ro", source)
args = ["setpriv", "--bounding-set=-all", "--inh-caps=-all",
        "--ambient-caps=-all", "--no-new-privs", "--", executable,
        "-B", "-c", "__ATTACK__", source, external]
p = subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True,
                   text=True, timeout=10, env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin",
                                               "LANG": "C"}, close_fds=True)
if p.returncode != 0:
    raise SystemExit(11)
print(p.stdout, end="")
'''

_RESTRICTED_ATTACK = r'''
import json, os, subprocess, sys
source, external = sys.argv[1:]
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
print(json.dumps({"checks": checks, "status": status}, sort_keys=True))
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


def run_demo() -> dict[str, Any]:
    """Run only against internally generated disposable data, never a supplied path."""
    if sys.platform != "linux" or not all(shutil.which(n) for n in ("unshare", "mount", "setpriv")):
        return _result("BLOCKED", ["Linux namespace prerequisites unavailable"])
    with tempfile.TemporaryDirectory(prefix="dec653-disposable-") as directory:
        source = Path(directory) / "checkout"
        external = Path(directory) / "external"
        source.mkdir(mode=0o700)
        external.mkdir(mode=0o700)
        sample = source / "sample"
        sample.write_bytes(b"DEC653_DISPOSABLE_ONLY\n")
        before = hashlib.sha256(sample.read_bytes()).hexdigest()
        setup = _NAMESPACE_SETUP.replace('"__ATTACK__"', repr(_RESTRICTED_ATTACK))
        try:
            p = subprocess.run(
                ["unshare", "--user", "--map-root-user", "--mount", "--",
                 sys.executable, "-B", "-c", setup, str(source), str(external), sys.executable],
                cwd=directory, stdin=subprocess.DEVNULL, capture_output=True,
                text=True, timeout=25, close_fds=True,
                env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LANG": "C"},
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return _result("BLOCKED", ["disposable namespace witness could not execute"])
        unchanged = (sample.exists() and hashlib.sha256(sample.read_bytes()).hexdigest() == before
                     and sorted(x.name for x in source.iterdir()) == ["sample"])
        if p.returncode != 0:
            return _result("BLOCKED", ["disposable namespace setup or child failed"])
        try:
            raw = json.loads(p.stdout)
        except (ValueError, TypeError):
            return _result("BLOCKED", ["disposable witness did not produce valid JSON"])
        return _evaluate(raw, unchanged)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DEC-653 disposable Linux OS-denial witness; NEVER annual authorization", add_help=False)
    parser.add_argument("--execute-disposable-demo", action="store_true")
    args = parser.parse_args(argv)
    result = run_demo() if args.execute_disposable_demo else _result(
        "BLOCKED", ["no local OS witness executed; explicit disposable demo opt-in required"])
    print(json.dumps(result, separators=(",", ":"), sort_keys=True))
    return 3 if result["status"] == "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
