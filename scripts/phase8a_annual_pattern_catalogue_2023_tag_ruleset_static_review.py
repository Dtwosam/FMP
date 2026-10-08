from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

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
    if args.out.exists() and args.out.read_text(encoding="utf-8") != data:
        raise ValueError(f"DEC-616 refuses to overwrite conflicting report: {args.out}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(data, encoding="utf-8")
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
