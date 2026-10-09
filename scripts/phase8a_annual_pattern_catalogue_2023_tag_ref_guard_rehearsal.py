from __future__ import annotations

import argparse
import json
import sys
# The audit CLI is read-only even when environment bytecode suppression is off.
# Set this before importing the project package, not after argument parsing.
sys.dont_write_bytecode = True
from pathlib import Path
from typing import Sequence

from fmp.discovery.annual_pattern_catalogue_2023_tag_ref_guard_rehearsal import (
    build_2023_tag_ref_guard_rehearsal,
    validate_2023_tag_ref_guard_rehearsal,
)


def _assess(args: argparse.Namespace) -> int:
    # Anchor containment to the actual source checkout, not the caller's cwd.
    # Invoking this CLI from scripts/ must not permit writing into repo root.
    checkout = Path(__file__).resolve().parents[1]
    target = args.out.resolve()
    # Reject output targets inside the checkout before reading any input JSON.
    if target.is_relative_to(checkout):
        raise ValueError("DEC-617 refuses audit output inside checkout")
    result = build_2023_tag_ref_guard_rehearsal(
        repository_root=Path("."),
        candidate_tag_ref=args.candidate_tag_ref,
        reviewed_commit_sha=args.reviewed_commit_sha,
    )
    validate_2023_tag_ref_guard_rehearsal(result)
    text = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if target.exists():
        if target.read_text(encoding="utf-8") != text:
            raise ValueError(f"DEC-617 refuses to overwrite conflicting rehearsal: {target}")
        # Do not rewrite identical reports: hard links may share checkout inodes.
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="DEC-617 inert offline annual tag guard rehearsal; cannot dispatch"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    assess = sub.add_parser("assess")
    assess.add_argument("--candidate-tag-ref", required=True)
    assess.add_argument("--reviewed-commit-sha", required=True)
    assess.add_argument("--out", required=True, type=Path)
    assess.set_defaults(func=_assess)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (ValueError, OSError, UnicodeError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
