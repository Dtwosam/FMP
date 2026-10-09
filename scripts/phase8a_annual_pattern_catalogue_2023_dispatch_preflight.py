from __future__ import annotations

import argparse
import json
import sys
# Stop project imports from generating checkout bytecode files.
sys.dont_write_bytecode = True
from pathlib import Path
from typing import Mapping, Sequence

from fmp.discovery.annual_pattern_catalogue_2023_external_report_create import write_once_external_report

from fmp.discovery.annual_pattern_catalogue_2023_dispatch_preflight import (
    build_2023_dispatch_preflight,
    validate_2023_dispatch_preflight,
)


def _read_json(path: Path) -> Mapping[str, object]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _write_json(path: Path, value: Mapping[str, object]) -> None:
    destination = Path(path)
    payload = json.dumps(
        dict(value),
        sort_keys=True,
        indent=2,
        allow_nan=False,
    ) + "\n"
    write_once_external_report(destination, payload, f"conflicting existing output: {destination}")


def _cmd_plan(args: argparse.Namespace) -> int:
    source_checkout = Path(__file__).resolve().parents[1]
    target = args.out.resolve()
    if target.is_relative_to(source_checkout):
        raise ValueError("DEC-608 refuses audit output inside checkout")
    value = build_2023_dispatch_preflight(
        _read_json(args.install_receipt_json),
        repository_root=Path("."),
        main_branch=_read_json(args.main_branch_json),
        annual_workflow_runs=_read_json(args.annual_workflow_runs_json),
        expected_head_sha=args.expected_head_sha,
    )
    validate_2023_dispatch_preflight(value)
    _write_json(target, value)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the read-only DEC-608 2023 annual dispatch preflight."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan = subparsers.add_parser("plan")
    plan.add_argument("--install-receipt-json", type=Path, required=True)
    plan.add_argument("--main-branch-json", type=Path, required=True)
    plan.add_argument("--annual-workflow-runs-json", type=Path, required=True)
    plan.add_argument("--expected-head-sha", required=True)
    plan.add_argument("--out", type=Path, required=True)
    plan.set_defaults(func=_cmd_plan)
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
