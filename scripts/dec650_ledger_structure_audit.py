from __future__ import annotations

"""DEC-652: offline STRUCTURAL audit of DEC-650 evidence, never authorization.

This module has no network, subprocess, GitHub, protected-data, or output-file
operations. Both the policy and the ledger are untrusted until independently
attested; a complete shape cannot demonstrate that OS measurements are true.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import re
import sys
from typing import Any, Mapping, Sequence

sys.dont_write_bytecode = True

SCHEMA = "dec650-structural-ledger-v1"
MAX_JSON_BYTES = 1024 * 1024  # Reject oversized untrusted inputs before decoding.
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
SYMBOLS = ("EURUSD", "GBPUSD", "USDJPY")
TIMEFRAMES = ("5m", "15m", "1h")
HORIZONS = (60, 240)
REQUIRED_CHECKS = frozenset((
    "source_mount_enforced_readonly", "checkout_path_write_denied",
    "chmod_or_privilege_recovery_denied", "directory_reparent_denied",
    "writable_alias_denied", "inherited_fd_contained",
    "stdio_fd_0_1_2_contained", "credential_leak_denied",
    "checkout_inventory_unchanged", "exclusive_external_publication",
    "concurrent_publication_conflict_denied", "failure_cleanup_clean",
))
JOB_TYPES = frozenset(("preflight", "cell", "freeze"))
IDENTITY_FIELDS = (
    "repository", "source_commit", "source_tree", "workflow_blob",
    "workflow_ref", "segment", "run_number", "run_attempt",
    "previous_freeze_run_id",
)


def _sha40(value: Any) -> bool:
    return isinstance(value, str) and HEX40.fullmatch(value) is not None


def _sha64(value: Any) -> bool:
    return isinstance(value, str) and HEX64.fullmatch(value) is not None


def _positive_int(value: Any) -> bool:
    return type(value) is int and value > 0


def _job_key(job: Mapping[str, Any]) -> str:
    kind = job.get("kind")
    if kind != "cell":
        return str(kind)
    matrix = job.get("matrix")
    if not isinstance(matrix, dict):
        return "cell:invalid-matrix"
    return f"cell:{matrix.get('symbol')}:{matrix.get('timeframe')}:{matrix.get('horizon')}"


def _required_job_keys() -> set[str]:
    return {"preflight", "freeze"} | {
        f"cell:{s}:{t}:{h}" for s in SYMBOLS for t in TIMEFRAMES for h in HORIZONS
    }


def assess(policy: Any, ledger: Any) -> dict[str, Any]:
    """Reject incomplete/contradictory data; NEVER produce an authorizing PASS."""
    errors: list[str] = []
    if not isinstance(policy, dict) or not isinstance(ledger, dict):
        return _result(["policy and ledger must be JSON objects"])
    if policy.get("schema") != SCHEMA or ledger.get("schema") != SCHEMA:
        errors.append("schema version mismatch")
    if policy.get("repository") != "Dtwosam/FMP":
        errors.append("expected repository must be Dtwosam/FMP")
    for field in ("source_commit", "source_tree", "workflow_blob"):
        if not _sha40(policy.get(field)):
            errors.append(f"policy.{field} must be a lowercase 40-hex SHA")
    if not isinstance(policy.get("workflow_ref"), str) or not policy["workflow_ref"].startswith("refs/"):
        errors.append("policy.workflow_ref must be an explicit ref")
    if policy.get("segment") != "2023":
        errors.append("policy.segment must be 2023")
    if type(policy.get("run_number")) is not int or policy.get("run_number") != 385:
        errors.append("policy.run_number must be integer 385")
    if type(policy.get("previous_freeze_run_id")) is not int or policy.get("previous_freeze_run_id") != 37663157285:
        errors.append("policy.previous_freeze_run_id must be approved 2022 predecessor 37663157285")
    if policy.get("run_attempt") != 1 or type(policy.get("run_attempt")) is not int:
        errors.append("policy.run_attempt must be integer 1")
    for field in IDENTITY_FIELDS:
        if field not in policy or field not in ledger or ledger.get(field) != policy.get(field):
            errors.append(f"source/run identity mismatch: {field}")

    jobs = ledger.get("jobs")
    if not isinstance(jobs, list):
        return _result(errors + ["jobs must be an array of 20 individual job records"])
    if len(jobs) != 20:
        errors.append(f"expected 20 jobs, received {len(jobs)}")
    seen_keys: set[str] = set()
    job_ids: set[int] = set()
    for index, job in enumerate(jobs):
        prefix = f"jobs[{index}]"
        if not isinstance(job, dict):
            errors.append(f"{prefix} must be an object")
            continue
        key = _job_key(job)
        if key not in _required_job_keys():
            errors.append(f"{prefix}: unexpected job or matrix coordinate {key}")
        if key in seen_keys:
            errors.append(f"{prefix}: duplicate job {key}")
        seen_keys.add(key)
        if not isinstance(job.get("kind"), str) or job["kind"] not in JOB_TYPES:
            errors.append(f"{prefix}: unknown job kind")
        if job.get("kind") == "cell":
            m = job.get("matrix")
            if not isinstance(m, dict) or set(m) != {"symbol", "timeframe", "horizon"} or type(m.get("horizon")) is not int:
                errors.append(f"{prefix}: malformed cell coordinates")
        elif job.get("matrix") is not None:
            errors.append(f"{prefix}: non-cell job must have null matrix")
        jid = job.get("job_id")
        if not _positive_int(jid) or jid in job_ids:
            errors.append(f"{prefix}: invalid or reused job ID")
        else:
            job_ids.add(jid)
        # DEC-650 demands actor and observer provenance, not merely a mount
        # namespace label. These are still untrusted statements in JSON.
        for f in (
            "runner_identity", "runner_image", "kernel", "mount_namespace",
            "mountinfo_sha256", "source_mount_id", "input_mount_id",
            "output_mount_id", "observer_identity", "uid_map_sha256",
            "gid_map_sha256", "observer_manifest_sha256",
            "attempt_log_sha256", "race_replay_sha256",
            "external_report_receipt_sha256", "cleanup_receipt_sha256",
            "argv_sha256",
        ):
            v = job.get(f)
            if f.endswith("_sha256"):
                if not _sha64(v):
                    errors.append(f"{prefix}: missing valid {f}")
            elif not isinstance(v, str) or not v.strip():
                errors.append(f"{prefix}: missing {f}")
        if not _positive_int(job.get("restricted_uid")):
            errors.append(f"{prefix}: restricted UID must be nonroot integer")
        if not _positive_int(job.get("restricted_gid")):
            errors.append(f"{prefix}: restricted GID must be nonroot integer")
        if job.get("supplementary_groups") != []:
            errors.append(f"{prefix}: supplementary groups not demonstrated empty")
        for capability in ("permitted_capabilities", "ambient_capabilities"):
            if job.get(capability) != "0":
                errors.append(f"{prefix}: {capability} not recorded zero")
        if job.get("seccomp_mode") not in ("filter", "strict"):
            errors.append(f"{prefix}: restricted seccomp mode missing")
        for location in ("working_directory", "process_executable"):
            value = job.get(location)
            if not isinstance(value, str) or not value.startswith("/") or chr(0) in value:
                errors.append(f"{prefix}: {location} must be an explicit absolute path")
        env_keys = job.get("env_allowlist_keys")
        if (not isinstance(env_keys, list) or not env_keys
                or any(not isinstance(v, str) or re.fullmatch(r"[A-Z_][A-Z0-9_]*", v) is None
                       or any(secret in v for secret in ("TOKEN", "SECRET", "PASSWORD", "CREDENTIAL"))
                       for v in env_keys)
                or len(env_keys) != len(set(v for v in env_keys if isinstance(v, str)))):
            errors.append(f"{prefix}: missing, duplicate or credential-bearing env keys")
        for gate in ("cwd_outside_checkout", "input_mounts_readonly",
                     "output_mount_outside_checkout", "publisher_isolated"):
            if job.get(gate) is not True:
                errors.append(f"{prefix}: {gate} not established")
        for empty in ("privileged_skips", "unresolved_exceptions"):
            if job.get(empty) != []:
                errors.append(f"{prefix}: {empty} absent or nonempty")
        if job.get("no_new_privs") is not True:
            errors.append(f"{prefix}: no_new_privs must be true")
        if job.get("effective_capabilities") != "0":
            errors.append(f"{prefix}: capability set not recorded as zero")
        if job.get("checkout_mount_readonly") is not True:
            errors.append(f"{prefix}: checkout mount not recorded readonly")
        if job.get("writable_checkout_aliases") != []:
            errors.append(f"{prefix}: writable aliases present or unexamined")
        if job.get("unapproved_inherited_fds") != []:
            errors.append(f"{prefix}: unapproved inherited descriptors present or unexamined")
        streams = job.get("standard_streams")
        if not isinstance(streams, dict) or set(streams) != {"0", "1", "2"} or not all(isinstance(v, str) and v in ("devnull", "external-log") for v in streams.values()):
            errors.append(f"{prefix}: standard descriptors must have explicit safe targets")
        before, after = job.get("checkout_before_sha256"), job.get("checkout_after_sha256")
        if not _sha64(before) or not _sha64(after) or before != after:
            errors.append(f"{prefix}: checkout digest missing or changed")
        checks = job.get("checks")
        if not isinstance(checks, dict):
            errors.append(f"{prefix}: mandatory checks missing")
            continue
        if set(checks) != REQUIRED_CHECKS:
            errors.append(f"{prefix}: missing/extra mandatory checks")
        for name in REQUIRED_CHECKS:
            check = checks.get(name)
            if not isinstance(check, dict) or check.get("status") != "PASS" or check.get("skipped") is not False or check.get("privileged_test_executed") is not True or not _sha64(check.get("evidence_sha256")):
                errors.append(f"{prefix}: {name} missing/skipped/failed/unsubstantiated")
    missing = _required_job_keys() - seen_keys
    if missing:
        errors.append("missing job coordinates: " + ", ".join(sorted(missing)))
    return _result(errors)


def _result(errors: list[str]) -> dict[str, Any]:
    return {
        "status": "BLOCKED" if errors else "STRUCTURALLY_COMPLETE_UNVERIFIED",
        "can_authorize_dispatch": False,
        "independent_os_proof_verified": False,
        "findings": sorted(set(errors)),
    }


def _read_bounded(path: Path) -> bytes:
    # O_NONBLOCK prevents a FIFO from hanging the audit before its size check.
    # O_NOFOLLOW prevents the supplied leaf from becoming a symlink to an
    # unintended local source between inspection and open. No unsafe fallback.
    nofollow = getattr(os, "O_NOFOLLOW", None)
    nonblock = getattr(os, "O_NONBLOCK", None)
    if not isinstance(nofollow, int) or not isinstance(nonblock, int):
        raise ValueError("platform lacks nonblocking nofollow input reads")
    flags = os.O_RDONLY | nonblock | nofollow | getattr(os, "O_CLOEXEC", 0)
    with os.fdopen(os.open(path, flags), "rb") as handle:
        info = os.fstat(handle.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("JSON input must be a regular file")
        if info.st_size > MAX_JSON_BYTES:
            raise ValueError("JSON input exceeds one-megabyte limit")
        value = handle.read(MAX_JSON_BYTES + 1)
    if len(value) > MAX_JSON_BYTES:
        raise ValueError("JSON input exceeds one-megabyte limit")
    return value


def _unique_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> None:
    raise ValueError("nonstandard nonfinite JSON number")


def _strict_json(value: bytes) -> Any:
    return json.loads(
        value, object_pairs_hook=_unique_object_pairs,
        parse_constant=_reject_nonfinite,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline DEC-650 ledger structure audit (NEVER authorizes execution)")
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--policy-sha256", required=True, help="Reviewer-supplied SHA-256 of exact policy bytes")
    parser.add_argument("--ledger", type=Path, required=True)
    args = parser.parse_args(argv)
    if not _sha64(args.policy_sha256):
        result = _result(["policy digest must be 64 lowercase hex digits"])
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 2
    try:
        policy_bytes = _read_bounded(args.policy)
        if hashlib.sha256(policy_bytes).hexdigest() != args.policy_sha256:
            result = _result(["policy byte digest mismatch"])
        else:
            policy = _strict_json(policy_bytes)
            ledger = _strict_json(_read_bounded(args.ledger))
            result = assess(policy, ledger)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, RecursionError) as exc:
        result = _result(["cannot decode independent policy/ledger input: " + type(exc).__name__])
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["status"] == "STRUCTURALLY_COMPLETE_UNVERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
