from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping, Sequence

from fmp.discovery.annual_pattern_catalogue_2021_runtime_authorization_install_action import (
    compile_2021_runtime_authorization_install_action,
    validate_2021_runtime_authorization_install_action,
)


def _read_json(path: Path) -> Mapping[str, object]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        json.dumps(dict(value), sort_keys=True, indent=2, allow_nan=False) + "\n"
    )
    if destination.exists() and destination.read_text(encoding="utf-8") != payload:
        raise ValueError(f"conflicting existing output: {destination}")
    destination.write_text(payload, encoding="utf-8")


def _cmd_compile(args: argparse.Namespace) -> int:
    value = compile_2021_runtime_authorization_install_action(
        _read_json(args.preflight_json),
        repository_root=Path("."),
        main_branch=_read_json(args.main_branch_json),
        expected_head_sha=args.expected_head_sha,
    )
    validate_2021_runtime_authorization_install_action(value)
    _write_json(args.out, value)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compile the exact two-file DEC-584 2021 runtime install action."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    compile_parser = subparsers.add_parser("compile")
    compile_parser.add_argument("--preflight-json", type=Path, required=True)
    compile_parser.add_argument("--main-branch-json", type=Path, required=True)
    compile_parser.add_argument("--expected-head-sha", required=True)
    compile_parser.add_argument("--out", type=Path, required=True)
    compile_parser.set_defaults(func=_cmd_compile)
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
