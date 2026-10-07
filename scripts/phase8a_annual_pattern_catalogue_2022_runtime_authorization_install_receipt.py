from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping, Sequence

from fmp.discovery.annual_pattern_catalogue_2022_runtime_authorization_install_receipt import (
    review_2022_runtime_authorization_install,
    validate_2022_runtime_authorization_install_receipt,
)


def _read_json(path: Path) -> Mapping[str, object]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _read_lines(path: Path) -> list[str]:
    return [
        line.strip()
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    destination = Path(path)
    payload = json.dumps(
        dict(value),
        sort_keys=True,
        indent=2,
        allow_nan=False,
    ) + "\n"
    if destination.exists() and destination.read_text(encoding="utf-8") != payload:
        raise ValueError(f"conflicting existing output: {destination}")
    destination.write_text(payload, encoding="utf-8")


def _cmd_review(args: argparse.Namespace) -> int:
    value = review_2022_runtime_authorization_install(
        _read_json(args.action_json),
        repository_root=Path("."),
        install_commit_sha=args.install_commit_sha,
        changed_files=_read_lines(args.changed_files),
        installed_gate_blob_sha=args.installed_gate_blob_sha,
        installed_runtime_blob_sha=args.installed_runtime_blob_sha,
    )
    validate_2022_runtime_authorization_install_receipt(value)
    _write_json(args.out, value)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Review the exact DEC-596 2022 runtime authorization installation."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    review = subparsers.add_parser("review")
    review.add_argument("--action-json", type=Path, required=True)
    review.add_argument("--install-commit-sha", required=True)
    review.add_argument("--changed-files", type=Path, required=True)
    review.add_argument("--installed-gate-blob-sha", required=True)
    review.add_argument("--installed-runtime-blob-sha", required=True)
    review.add_argument("--out", type=Path, required=True)
    review.set_defaults(func=_cmd_review)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except ValueError as exc:
        parser.exit(2, f"{exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
