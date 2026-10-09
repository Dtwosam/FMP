from __future__ import annotations

import argparse
import json
import sys
# Stop project imports from generating checkout bytecode files.
sys.dont_write_bytecode = True
from pathlib import Path
from typing import Mapping, Sequence

from fmp.discovery.annual_pattern_catalogue_2023_dispatch_action_preflight import (
    build_2023_dispatch_action_preflight,
    validate_2023_dispatch_action_preflight,
)


def _read_json(path: Path) -> Mapping[str, object]:
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON: {path}") from exc
    if not isinstance(result, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return result


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    payload = json.dumps(dict(value), sort_keys=True, indent=2, allow_nan=False) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") != payload:
            raise ValueError(f"conflicting existing output: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def _cmd_plan(args: argparse.Namespace) -> int:
    source_checkout = Path(__file__).resolve().parents[1]
    target = args.out.resolve()
    if target.is_relative_to(source_checkout):
        raise ValueError("DEC-610 refuses audit output inside checkout")
    value = build_2023_dispatch_action_preflight(
        _read_json(args.authorization_json),
        repository_root=Path("."),
        main_branch=_read_json(args.main_branch_json),
        annual_workflow_runs=_read_json(args.annual_workflow_runs_json),
        expected_head_sha=args.expected_head_sha,
    )
    validate_2023_dispatch_action_preflight(value)
    _write_json(target, value)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only DEC-610 protected 2023 dispatch-action preflight"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    plan = sub.add_parser("plan")
    plan.add_argument("--authorization-json", type=Path, required=True)
    plan.add_argument("--main-branch-json", type=Path, required=True)
    plan.add_argument("--annual-workflow-runs-json", type=Path, required=True)
    plan.add_argument("--expected-head-sha", required=True)
    plan.add_argument("--out", type=Path, required=True)
    plan.set_defaults(func=_cmd_plan)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
