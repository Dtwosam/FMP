from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from fmp.discovery.exp062_historical_one_shot_executor_workflow_preflight import (
    build_one_shot_historical_executor_workflow_preflight,
    validate_one_shot_historical_executor_workflow_preflight,
)


def _read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _plan(args: argparse.Namespace) -> int:
    value = build_one_shot_historical_executor_workflow_preflight(
        repository_root=Path("."),
        main_branch=_read_json(args.main_json),
        workflow_runs=_read_json(args.runs_json),
        expected_head_sha=args.expected_head,
    )
    validate_one_shot_historical_executor_workflow_preflight(value)
    print(json.dumps(value, sort_keys=True, indent=2, allow_nan=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only EXP-062 one-shot historical executor workflow preflight"
        )
    )
    sub = parser.add_subparsers(dest="command", required=True)
    plan = sub.add_parser("plan")
    plan.add_argument("--main-json", type=Path, required=True)
    plan.add_argument("--runs-json", type=Path, required=True)
    plan.add_argument("--expected-head", required=True)
    plan.set_defaults(func=_plan)
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
