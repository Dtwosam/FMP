from __future__ import annotations

import argparse
import json
import sys
# Stop project imports from generating checkout bytecode files.
sys.dont_write_bytecode = True
from pathlib import Path
from typing import Mapping, Sequence

from fmp.discovery.annual_pattern_catalogue_2023_dispatch_immutability_audit import (
    audit_2023_dispatch_main_immutability,
    validate_2023_dispatch_main_immutability_audit,
)


def _read(path: Path) -> Mapping[str, object]:
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON: {path}") from exc
    if not isinstance(result, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return result


def _cmd_audit(args: argparse.Namespace) -> int:
    source_checkout = Path(__file__).resolve().parents[1]
    target = args.out.resolve()
    if target.is_relative_to(source_checkout):
        raise ValueError("DEC-611 refuses audit output inside checkout")
    value = audit_2023_dispatch_main_immutability(
        _read(args.dec610_preflight_json),
        repository_root=Path("."),
        main_branch=_read(args.main_branch_json),
        annual_workflow_runs=_read(args.annual_workflow_runs_json),
        expected_head_sha=args.expected_head_sha,
    )
    validate_2023_dispatch_main_immutability_audit(value)
    payload = json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if target.exists():
        if target.read_text(encoding="utf-8") != payload:
            raise ValueError(f"conflicting existing output: {target}")
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload, encoding="utf-8")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only DEC-611 audit of exact 2023 annual-dispatch main immutability"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser("audit")
    audit.add_argument("--dec610-preflight-json", type=Path, required=True)
    audit.add_argument("--main-branch-json", type=Path, required=True)
    audit.add_argument("--annual-workflow-runs-json", type=Path, required=True)
    audit.add_argument("--expected-head-sha", required=True)
    audit.add_argument("--out", type=Path, required=True)
    audit.set_defaults(func=_cmd_audit)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
