from __future__ import annotations

import argparse
import json
import sys
# The audit CLI is read-only even when environment bytecode suppression is off.
# Set this before importing the project package, not after argument parsing.
sys.dont_write_bytecode = True
from pathlib import Path
from typing import Mapping, Sequence

from fmp.discovery.annual_pattern_catalogue_2023_immutable_tag_feasibility import (
    build_2023_immutable_tag_feasibility,
    validate_2023_immutable_tag_feasibility,
)


def _read_object(path: Path) -> Mapping[str, object]:
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"DEC-615 cannot read input: {path}") from exc
    if not isinstance(result, dict):
        raise ValueError(f"DEC-615 input must be a JSON object: {path}")
    return result


def _assess(args: argparse.Namespace) -> int:
    checkout = Path.cwd().resolve()
    target = args.out.resolve()
    # Reject output targets inside the checkout before reading any input JSON.
    if target.is_relative_to(checkout):
        raise ValueError("DEC-615 refuses audit output inside checkout")
    result = build_2023_immutable_tag_feasibility(
        repository_root=Path("."),
        handoff=_read_object(args.dec614_handoff_json),
        main_branch=_read_object(args.main_branch_json),
        annual_workflow_runs=_read_object(args.annual_workflow_runs_json),
        expected_head_sha=args.expected_head_sha,
    )
    validate_2023_immutable_tag_feasibility(result)
    output = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if target.exists() and target.read_text(encoding="utf-8") != output:
        raise ValueError(f"DEC-615 existing output conflicts: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(output, encoding="utf-8")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only DEC-615 static feasibility assessment; cannot dispatch"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    assess = sub.add_parser("assess")
    assess.add_argument("--dec614-handoff-json", type=Path, required=True)
    assess.add_argument("--main-branch-json", type=Path, required=True)
    assess.add_argument("--annual-workflow-runs-json", type=Path, required=True)
    assess.add_argument("--expected-head-sha", required=True)
    assess.add_argument("--out", type=Path, required=True)
    assess.set_defaults(func=_assess)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
