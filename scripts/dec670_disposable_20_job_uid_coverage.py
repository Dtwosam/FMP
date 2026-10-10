from __future__ import annotations

"""DEC-670: disposable 20-job UID isolation composition; NEVER authorizes runs."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
from typing import Any

sys.dont_write_bytecode = True

UID_WITNESS = Path(__file__).resolve().with_name("dec669_disposable_uid_boundary.py")
JOBS = ("annual_preflight",) + tuple(f"annual_cell:{n:02d}" for n in range(1, 19)) + ("annual_freeze",)
UNVERIFIED = "LOCAL_DISPOSABLE_WITNESS_UNVERIFIED"


def _result(findings: list[str], count: int = 0) -> dict[str, Any]:
    return {
        "status": "BLOCKED" if findings else UNVERIFIED,
        "findings": sorted(set(findings))[:22],
        "covered_synthetic_jobs": count,
        "required_synthetic_jobs": 20,
        "can_authorize_dispatch": False,
        "independent_os_proof_verified": False,
    }


def assess(receipts: Any, required_checks: tuple[str, ...]) -> dict[str, Any]:
    """Treat every individual process record as untrusted nonauthorizing JSON."""
    if not isinstance(receipts, dict) or set(receipts) != set(JOBS):
        return _result(["exact 20-job synthetic identity coverage not demonstrated"])
    if len(JOBS) != 20 or len(set(JOBS)) != 20:
        return _result(["internal synthetic job identity definition invalid"])
    findings: list[str] = []
    covered = 0
    for job in JOBS:
        result = receipts[job]
        if not isinstance(result, dict):
            findings.append("missing or malformed synthetic witness: " + job)
            continue
        checks = result.get("observed_checks")
        if (result.get("status") != UNVERIFIED
                or result.get("can_authorize_dispatch") is not False
                or result.get("independent_os_proof_verified") is not False
                or result.get("findings") != []
                or not isinstance(checks, dict)
                or set(checks) != set(required_checks)
                or any(checks[name] is not True for name in required_checks)):
            findings.append("synthetic OS restriction not evidenced: " + job)
            continue
        covered += 1
    return _result(findings, covered)


def run_demo() -> dict[str, Any]:
    """Run the *same* fake-UID experiment 20 times, with no annual inputs."""
    spec = importlib.util.spec_from_file_location("dec669_uid_witness", UID_WITNESS)
    if spec is None or spec.loader is None:
        return _result(["synthetic UID witness source unavailable"])
    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except (OSError, ImportError, AttributeError):
        return _result(["synthetic UID witness cannot be loaded"])
    checks = getattr(module, "REQUIRED", None)
    demo = getattr(module, "run_demo", None)
    if not isinstance(checks, tuple) or not callable(demo):
        return _result(["synthetic UID witness API invalid"])
    receipts: dict[str, Any] = {}
    for job in JOBS:
        try:
            record = demo()
        except (OSError, ValueError):
            record = {"status": "BLOCKED"}
        receipts[job] = record
        if not isinstance(record, dict) or record.get("status") != UNVERIFIED:
            break
    return assess(receipts, checks)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False,
        description="DEC-670 offline 20-disposable-UID-job rehearsal; NEVER dispatch")
    parser.add_argument("--execute-disposable-20", action="store_true")
    args = parser.parse_args(argv)
    outcome = run_demo() if args.execute_disposable_20 else _result(
        ["explicit synthetic 20-job OS demo opt-in missing"])
    print(json.dumps(outcome, sort_keys=True, separators=(",", ":")))
    return 3 if outcome["status"] == UNVERIFIED else 2


if __name__ == "__main__":
    raise SystemExit(main())
