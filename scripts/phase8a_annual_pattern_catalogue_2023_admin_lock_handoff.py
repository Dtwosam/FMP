from __future__ import annotations

import argparse
import json
import sys
# Stop project imports from generating checkout bytecode files.
sys.dont_write_bytecode = True
from pathlib import Path
from typing import Mapping, Sequence

from fmp.discovery.annual_pattern_catalogue_2023_external_report_create import write_once_external_report

from fmp.discovery.annual_pattern_catalogue_2023_admin_lock_handoff import (
    build_2023_admin_lock_handoff,
    validate_2023_admin_lock_handoff,
)


def _read_object(path: Path) -> Mapping[str, object]:
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"DEC-613 cannot read JSON: {path}") from exc
    if not isinstance(result, dict):
        raise ValueError(f"DEC-613 expected JSON object: {path}")
    return result


def _prepare(args: argparse.Namespace) -> int:
    source_checkout = Path(__file__).resolve().parents[1]
    target = args.out.resolve()
    if target.is_relative_to(source_checkout):
        raise ValueError("DEC-613 refuses audit output inside checkout")
    value = build_2023_admin_lock_handoff(
        readiness=_read_object(args.dec612_readiness_json),
        repository_root=Path("."),
        main_branch=_read_object(args.main_branch_json),
        annual_runs=_read_object(args.annual_workflow_runs_json),
        expected_head_sha=args.expected_head_sha,
    )
    validate_2023_admin_lock_handoff(value)
    payload = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    write_once_external_report(target, payload, f"DEC-613 conflicting output: {target}")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="DEC-613 offline read-only 2023 admin lock evidence handoff; no dispatch"
    )
    sub = p.add_subparsers(dest="command", required=True)
    cmd = sub.add_parser("prepare")
    cmd.add_argument("--dec612-readiness-json", type=Path, required=True)
    cmd.add_argument("--main-branch-json", type=Path, required=True)
    cmd.add_argument("--annual-workflow-runs-json", type=Path, required=True)
    cmd.add_argument("--expected-head-sha", required=True)
    cmd.add_argument("--out", type=Path, required=True)
    cmd.set_defaults(func=_prepare)
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return int(args.func(args))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
