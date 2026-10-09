from __future__ import annotations

import argparse
import json
import sys
# The audit CLI is read-only even when environment bytecode suppression is off.
# Set this before importing the project package, not after argument parsing.
sys.dont_write_bytecode = True
from pathlib import Path
from typing import Sequence

from fmp.discovery.annual_pattern_catalogue_2023_external_report_create import write_once_external_report

from fmp.discovery.annual_pattern_catalogue_2023_tag_ruleset_static_review import (
    inspect_2023_tag_ruleset_snapshot,
    validate_2023_tag_ruleset_static_review,
)


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"DEC-616 cannot read JSON input: {path}") from exc


def _assess(args: argparse.Namespace) -> int:
    # Anchor containment to the actual source checkout, not the caller's cwd.
    # Invoking this CLI from scripts/ must not permit writing into repo root.
    checkout = Path(__file__).resolve().parents[1]
    target = args.out.resolve()
    # Reject output targets inside the checkout before reading any input JSON.
    if target.is_relative_to(checkout):
        raise ValueError("DEC-616 refuses audit output inside checkout")
    report = inspect_2023_tag_ruleset_snapshot(
        tag_ref=args.tag_ref,
        reviewed_commit_sha=args.reviewed_commit_sha,
        git_ref_response=_read_json(args.git_ref_json),
        rulesets=_read_json(args.rulesets_json),
        includes_inherited_rulesets=args.includes_inherited_rulesets,
        enumeration_complete=args.enumeration_complete,
    )
    validate_2023_tag_ruleset_static_review(report)
    data = json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n"
    write_once_external_report(target, data, f"DEC-616 refuses to overwrite conflicting report: {target}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="DEC-616 untrusted offline static tag ruleset review; never dispatch"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("assess")
    command.add_argument("--tag-ref", required=True)
    command.add_argument("--reviewed-commit-sha", required=True)
    command.add_argument("--git-ref-json", type=Path, required=True)
    command.add_argument("--rulesets-json", type=Path, required=True)
    command.add_argument("--includes-inherited-rulesets", action="store_true")
    command.add_argument("--enumeration-complete", action="store_true")
    command.add_argument("--out", type=Path, required=True)
    command.set_defaults(func=_assess)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
