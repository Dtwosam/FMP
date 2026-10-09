from __future__ import annotations

"""DEC-645: read-only filesystem observations, never an authorization gate."""

import argparse
import json
import os
from pathlib import Path
import re
import stat
import sys

sys.dont_write_bytecode = True

_OCTAL = re.compile(r"\\([0-7]{3})")


def _mount_path(value: str) -> Path:
    decoded = _OCTAL.sub(lambda m: chr(int(m.group(1), 8)), value)
    path = Path(decoded)
    if not path.is_absolute():
        raise ValueError("mount point is not absolute")
    return path


def parse_mountinfo(content: str) -> list[dict[str, object]]:
    """Parse a strictly bounded Linux mountinfo snapshot; no kernel changes."""
    if len(content) > 2_000_000:
        raise ValueError("mountinfo exceeds diagnostic size budget")
    entries: list[dict[str, object]] = []
    for line in content.splitlines():
        parts = line.split(" - ", 1)
        if len(parts) != 2:
            raise ValueError("invalid mountinfo separator")
        left = parts[0].split()
        right = parts[1].split()
        if len(left) < 6 or len(right) < 3:
            raise ValueError("invalid mountinfo fields")
        entries.append({
            "mount_id": int(left[0]),
            "mount_point": _mount_path(left[4]),
            "vfs_readonly": "ro" in left[5].split(","),
            "filesystem_type": right[0],
        })
    if not entries:
        raise ValueError("mountinfo empty")
    return entries


def _covering_mount(path: Path, entries: list[dict[str, object]]) -> dict[str, object] | None:
    matches = [
        entry for entry in entries
        if path == entry["mount_point"] or entry["mount_point"] in path.parents
    ]
    if not matches:
        return None
    longest = max(len(entry["mount_point"].parts) for entry in matches)
    candidates = [entry for entry in matches if len(entry["mount_point"].parts) == longest]
    return candidates[0] if len(candidates) == 1 else None


def inspect_checkout_boundary(
    checkout: Path, output_parent: Path, mountinfo_content: str,
) -> dict[str, object]:
    """Advisory observations only; no scenario is allowed to authorize work."""
    result: dict[str, object] = {
        "protocol": "fmp-dec645-mount-boundary-observation-v1",
        "authorized": False,
        "classification": "NOT_AN_AUTHORIZATION",
        "confidence": "advisory_current_namespace_only",
        "reason": "Mount/permission observations cannot prove immutable checkout integrity or authorize annual dispatch.",
    }
    try:
        checkout = checkout.resolve(strict=True)
        output_parent = output_parent.resolve(strict=True)
        if not checkout.is_dir() or not output_parent.is_dir():
            raise ValueError("both paths must be existing directories")
        mounts = parse_mountinfo(mountinfo_content)
        left = _covering_mount(checkout, mounts)
        right = _covering_mount(output_parent, mounts)
        if left is None or right is None:
            raise ValueError("mount identity missing or ambiguous")
        checkout_stat = checkout.stat()
        output_stat = output_parent.stat()
        statvfs = os.statvfs(checkout)
        readonly_flag = getattr(os, "ST_RDONLY", None)
        result["observation"] = {
            "checkout_mount_id": left["mount_id"],
            "output_mount_id": right["mount_id"],
            "distinct_mount_ids": left["mount_id"] != right["mount_id"],
            "distinct_st_dev": checkout_stat.st_dev != output_stat.st_dev,
            "checkout_vfs_mount_readonly": left["vfs_readonly"],
            "checkout_statvfs_readonly": None if readonly_flag is None else bool(statvfs.f_flag & readonly_flag),
            "output_parent_resolves_into_checkout": output_parent == checkout or checkout in output_parent.parents,
        }
        result["reason"] = (
            "These are point-in-time observations, not a proof against bind-mount aliases, "
            "mount changes, privileged actors or concurrent rename."
        )
    except (OSError, ValueError) as exc:
        result["observation_error"] = type(exc).__name__
        result["reason"] = "Filesystem evidence unavailable or ambiguous; fail closed."
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only mount boundary advisory; always denies authorization")
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--output-parent", type=Path, required=True)
    parser.add_argument("--mountinfo", type=Path, default=Path("/proc/self/mountinfo"))
    args = parser.parse_args(argv)
    try:
        flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(args.mountinfo, flags)
        with os.fdopen(fd, "r", encoding="utf-8") as stream:
            mountinfo = stream.read(2_000_001) if stat.S_ISREG(os.fstat(stream.fileno()).st_mode) else ""
    except (OSError, UnicodeError):
        mountinfo = ""
    print(json.dumps(inspect_checkout_boundary(args.checkout, args.output_parent, mountinfo), sort_keys=True))
    return 2  # Deliberate nonzero: observations NEVER grant workflow/merge permission.


if __name__ == "__main__":
    raise SystemExit(main())
