from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping, Sequence

from fmp.discovery.annual_pattern_catalogue_2023_runtime_authorization_install_preflight import (
    build_2023_runtime_authorization_install_preflight,
)


def _read_json(path: Path) -> Mapping[str, object]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        dict(value),
        sort_keys=True,
        indent=2,
        allow_nan=False,
    ) + "\n"
    if destination.exists() and destination.read_text(encoding="utf-8") != payload:
        raise ValueError(f"conflicting existing output: {destination}")
    destination.write_text(payload, encoding="utf-8")


def _cmd_plan(args: argparse.Namespace) -> int:
    value = build_2023_runtime_authorization_install_preflight(
        _read_json(args.authorization_json),
        _read_json(args.plan_json),
        repository_root=Path("."),
        main_branch=_read_json(args.main_branch_json),
        expected_head_sha=args.expected_head_sha,
    )
    _write_json(args.out, value)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the read-only DEC-605 2023 runtime install preflight.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan = subparsers.add_parser("plan")
    plan.add_argument("--authorization-json", type=Path, required=True)
    plan.add_argument("--plan-json", type=Path, required=True)
    plan.add_argument("--main-branch-json", type=Path, required=True)
    plan.add_argument("--expected-head-sha", required=True)
    plan.add_argument("--out", type=Path, required=True)
    plan.set_defaults(func=_cmd_plan)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
