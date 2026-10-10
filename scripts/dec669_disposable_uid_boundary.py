from __future__ import annotations

"""DEC-669: disposable separate-UID permission witness; NEVER authorization.

Only an internally created /tmp tree is used. The opt-in tool requires an
already-root Linux sandbox and NEVER elevates privileges or accesses FMP data.
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

SAMPLE = b"DEC669_PUBLIC_SOURCE_ONLY\n"
REPORT = b"DEC669_PUBLIC_EXTERNAL_REPORT\n"
_CHILD = r'''
import json, os, sys
checkout, external, scratch = sys.argv[1:]
checks = {}
def denied(name, operation):
    try:
        operation()
    except PermissionError:
        checks[name] = True
    except OSError:
        checks[name] = False
    else:
        checks[name] = False
checks["synthetic_source_readable"] = open(os.path.join(checkout, "sample"), "rb").read() == b"DEC669_PUBLIC_SOURCE_ONLY\n"
denied("checkout_create", lambda: open(os.path.join(checkout, "injected"), "wb").close())
denied("checkout_truncate", lambda: open(os.path.join(checkout, "sample"), "wb").close())
denied("checkout_chmod", lambda: os.chmod(os.path.join(checkout, "sample"), 0o666))
denied("checkout_reparent", lambda: os.rename(os.path.join(scratch, "dummy"), os.path.join(checkout, "dummy")))
denied("external_create", lambda: open(os.path.join(external, "injected"), "wb").close())
denied("external_report_write", lambda: open(os.path.join(external, "report"), "wb").close())
denied("external_report_read", lambda: open(os.path.join(external, "report"), "rb").close())
checks["uid_is_restricted"] = os.geteuid() == 65534 and os.getegid() == 65534
checks["groups_cleared"] = os.getgroups() == []
state = {}
with open("/proc/self/status", "r", encoding="ascii") as handle:
    for line in handle:
        key, _, value = line.partition(":")
        if key in ("CapEff", "CapPrm", "CapBnd", "CapAmb", "NoNewPrivs"):
            state[key] = value.strip()
checks["capabilities_zero"] = all(state.get(k, "") and set(state[k]) == {"0"} for k in ("CapEff", "CapPrm", "CapBnd", "CapAmb"))
checks["no_new_privs"] = state.get("NoNewPrivs") == "1"
checks["cwd_is_scratch"] = os.getcwd() == scratch
print(json.dumps({"checks": checks}, sort_keys=True))
'''

REQUIRED = (
    "synthetic_source_readable", "checkout_create", "checkout_truncate",
    "checkout_chmod", "checkout_reparent", "external_create",
    "external_report_write", "external_report_read", "uid_is_restricted",
    "groups_cleared", "capabilities_zero", "no_new_privs", "cwd_is_scratch",
    "source_unchanged", "report_unchanged",
)


def _result(findings: list[str], checks: dict[str, bool] | None = None) -> dict[str, Any]:
    return {"status": "BLOCKED" if findings else "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED",
            "findings": sorted(set(findings)), "observed_checks": checks or {},
            "can_authorize_dispatch": False, "independent_os_proof_verified": False}


def _evaluate(observation: Any) -> dict[str, Any]:
    if not isinstance(observation, dict):
        return _result(["restricted child observation missing"])
    checks = observation.get("checks")
    if not isinstance(checks, dict):
        return _result(["restricted child checks missing"])
    missing = ["separate-UID denial not verified: " + key for key in REQUIRED if checks.get(key) is not True]
    return _result(missing, {key: checks.get(key) is True for key in REQUIRED})


def run_demo() -> dict[str, Any]:
    if (sys.platform != "linux" or os.geteuid() != 0
            or not shutil.which("setpriv") or not Path("/proc/self/status").is_file()):
        return _result(["opt-in root Linux setpriv prerequisites not met"])
    if not os.path.isdir("/tmp") or os.path.islink("/tmp"):
        return _result(["fixed public synthetic temporary root unavailable"])
    try:
        with tempfile.TemporaryDirectory(prefix="dec669-disposable-", dir="/tmp") as base:
            root = Path(base)
            checkout, external, scratch = root / "checkout", root / "external", root / "scratch"
            checkout.mkdir(mode=0o755)
            external.mkdir(mode=0o700)
            scratch.mkdir(mode=0o777)
            sample, report = checkout / "sample", external / "report"
            sample.write_bytes(SAMPLE)
            report.write_bytes(REPORT)
            sample.chmod(0o444)
            report.chmod(0o400)
            scratch.chmod(0o777)
            root.chmod(0o755)
            (scratch / "dummy").write_bytes(b"PUBLIC_DUMMY")
            (scratch / "dummy").chmod(0o666)
            before_source = hashlib.sha256(sample.read_bytes()).hexdigest()
            before_report = hashlib.sha256(report.read_bytes()).hexdigest()
            p = subprocess.run(
                ["setpriv", "--reuid=65534", "--regid=65534", "--clear-groups",
                 "--bounding-set=-all", "--inh-caps=-all", "--ambient-caps=-all",
                 "--no-new-privs", "--", sys.executable, "-B", "-c", _CHILD,
                 str(checkout), str(external), str(scratch)],
                cwd=scratch, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                close_fds=True, check=False, timeout=12,
                env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LANG": "C"},
            )
            if p.returncode != 0 or len(p.stdout) > 4096:
                return _result(["restricted child did not produce a bounded clean observation"])
            raw = json.loads(p.stdout)
            if not isinstance(raw, dict) or not isinstance(raw.get("checks"), dict):
                return _result(["restricted child data malformed"])
            checks = raw["checks"]
            checks["source_unchanged"] = (sample.read_bytes() == SAMPLE and
                  hashlib.sha256(sample.read_bytes()).hexdigest() == before_source and
                  sorted(p.name for p in checkout.iterdir()) == ["sample"])
            checks["report_unchanged"] = (report.read_bytes() == REPORT and
                  hashlib.sha256(report.read_bytes()).hexdigest() == before_report and
                  sorted(p.name for p in external.iterdir()) == ["report"])
            return _evaluate({"checks": checks})
    except (OSError, ValueError, subprocess.SubprocessError):
        return _result(["disposable UID boundary setup or observer failed"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False,
        description="DEC-669 disposable UID permission witness; NEVER annual authorization")
    parser.add_argument("--execute-disposable-demo", action="store_true")
    args = parser.parse_args(argv)
    result = run_demo() if args.execute_disposable_demo else _result(
        ["explicit separate-UID test opt-in missing"])
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 3 if result["status"] == "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
