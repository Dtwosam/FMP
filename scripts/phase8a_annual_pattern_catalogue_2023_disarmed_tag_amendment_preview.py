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

from fmp.discovery.annual_pattern_catalogue_2023_disarmed_tag_amendment_preview import (
    build_2023_disarmed_tag_amendment_preview,
    validate_2023_disarmed_tag_amendment_preview,
)


def _assess(args: argparse.Namespace) -> int:
    source_checkout = Path(__file__).resolve().parents[1]
    target = args.out.resolve()
    if target.is_relative_to(source_checkout):
        raise ValueError("DEC-618 preview report must be written outside the checkout")
    result = build_2023_disarmed_tag_amendment_preview(repository_root=Path("."))
    validate_2023_disarmed_tag_amendment_preview(result)
    output = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    write_once_external_report(target, output, f"DEC-618 refusing conflicting output: {target}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="DEC-618 disarmed read-only annual workflow diff preview, never installed"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    assess = sub.add_parser("assess")
    assess.add_argument("--out", required=True, type=Path)
    assess.set_defaults(func=_assess)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, UnicodeError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())
